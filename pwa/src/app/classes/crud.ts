/*
Technoplatz BI

Copyright (C) 2020-2023 Technoplatz IT Solutions GmbH, Mustafa Mat

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see https://www.gnu.org/licenses.

If your software can interact with users remotely through a computer
network, you should also make sure that it provides a way for users to
get its source.  For example, if your program is a web application, its
interface could display a "Source" link that leads users to an archive
of the code.  There are many ways you could offer source, and different
solutions will be better for different programs; see section 13 for the
specific requirements.

You should also get your employer (if you work as a programmer) or school,
if any, to sign a "copyright disclaimer" for the program, if necessary.
For more information on this, and how to apply and follow the GNU AGPL, see
https://www.gnu.org/licenses.
*/

import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import { Subject, BehaviorSubject } from "rxjs";
import { Validators, FormControl } from "@angular/forms";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Miscellaneous } from "./miscellaneous";
import { environment } from "../../environments/environment";

@Injectable({
  providedIn: "root"
})

export class Crud {
  public cartitems = [];
  public productList: any = [];
  public fields: any = [];
  public objectsListener = new BehaviorSubject([]);
  public objects = this.objectsListener.asObservable();
  private apiHost: string = "";
  private crudHeaders: any = {
    "Content-Type": "application/json",
    "X-Api-Key": environment.apiKey
  }
  private uploadHeaders: any = {
    "X-Api-Key": environment.apiKey
  }
  announcements: any = new Subject<any>();

  constructor(
    private storage: Storage,
    private misc: Miscellaneous,
    private http: HttpClient
  ) {
    this.misc.getAPIHost().then((apiHost: any) => {
      this.apiHost = apiHost;
    });
  }

  initForm(op: string, structure: any, form: any, data: any, collections: any, views: any) {
    return new Promise((resolve, reject) => {
      let i = 0;
      let init: any = {};
      this.fields = [];
      for (let item in structure.properties) {
        const p: any = structure.properties[item];
        const bsonType_ = p.bsonType;
        let enums_ = p.enum;
        const arrayInc_ = bsonType_ === "array" ? true : false;
        const objectInc_ = bsonType_ === "object" ? true : false;
        const title_ = p.title;
        const required_ = structure.required && structure.required.indexOf(item) !== -1 ? true : false;
        const description_ = p.description ? p.description : null;
        const minLength_ = p.minLength > 0 ? p.minLength : null;
        const maxLength_ = p.maxLength > 0 ? p.maxLength : null;
        const minimum_ = p.minimum > 0 ? p.minimum : null;
        const maximum_ = p.maximum > 0 ? p.maximum : null;
        const minItems_ = p.minItems && p.minItems >= 0 ? p.minItems : null;
        const maxItems_ = p.maxItems && p.maxItems >= 0 ? p.maxItems : null;
        const items_ = p.items ? p.items : null;
        const password_ = p.password ? true : false;
        const pattern_ = p.pattern ? p.pattern : null;
        const subType_ = p.subType ? p.subType : null;
        const tzoffset = new Date().getTimezoneOffset() * 60000;
        const default_ = p.default ? p.default === '$CURRENT_DATE' ? new Date(Date.now() - tzoffset).toISOString().substring(0, 19) : p.default : null;
        const file_ = p.file ? true : false;
        const filter_ = p.filter ? true : false;
        const property_ = p.property ? true : false;
        const kv_ = p.kv ? true : false;
        const permanent_ = p.permanent ? true : false;
        const collection_ = p.collection ? true : false;
        const textarea_ = p.textarea ? true : false;
        const hashtag_ = p.hashtag ? true : false;
        const chips_ = p.chips ? true : false;
        const view_ = p.view ? true : false;
        const manualAdd_ = p.manualAdd ? true : false;
        view_ ? enums_ = (() => { let arr_ = []; for (let v = 0; v < views.length; v++) { arr_.push(views[v].record.vie_id) } return arr_; })() : null;
        collection_ ? enums_ = (() => { let arr_ = []; for (let v = 0; v < collections.length; v++) { arr_.push(collections[v].col_id) } return arr_; })() : null;
        const parents = structure.parents ? structure.parents.find((obj: any) => obj.key && obj.key === item) : null;
        const v = [];
        required_ ? v.push(Validators.required) : null;
        minLength_ && bsonType_ !== "array" ? v.push(Validators.minLength(minLength_)) : null;
        maxLength_ && bsonType_ !== "array" ? v.push(Validators.maxLength(maxLength_)) : null;
        minimum_ ? v.push(Validators.min(minimum_)) : null;
        maximum_ ? v.push(Validators.max(maximum_)) : null;
        pattern_ && !p.file ? v.push(Validators.pattern(pattern_)) : null;
        this.fields.push({
          name: item,
          title: title_,
          enum: enums_,
          required: required_,
          bsonType: bsonType_,
          description: description_,
          password: password_,
          maxLength: maxLength_,
          minLength: minLength_,
          minItems: minItems_,
          maxItems: maxItems_,
          parents: parents,
          items: items_,
          file: file_,
          filter: filter_,
          kv: kv_,
          permanent: permanent_,
          collection: collection_,
          view: view_,
          property: property_,
          textarea: textarea_,
          hashtag: hashtag_,
          chips: chips_,
          subType: subType_,
          manualAdd: manualAdd_
        });
        const kvval_: any = [{
          key: null,
          value: null
        }];
        init[item] = default_ ? default_ : arrayInc_ ? kv_ ? kvval_ : [] : objectInc_ ? {} : null;
        form.addControl(item, new FormControl({ "value": data && data[item] ? data[item] : init[item], "disabled": item === "id" && op === "update" && (data[item] || init[item]) ? true : false }, Validators.compose(v)));
        if (i === Object.keys(structure.properties).length - 1) {
          resolve({
            form: form,
            fields: this.fields,
            init: init
          });
        } else {
          i++;
        }
      }
    });
  }

  SaveAsView(collection: string, filter: any) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        const posted: any = {
          op: "saveasview",
          user: LSUSERMETA,
          collection: collection,
          match: filter
        }
        this.http.post<any>(this.apiHost + "/crud", posted, {
          headers: new HttpHeaders(this.crudHeaders)
        }).subscribe((res: any) => {
          if (res && res.result) {
            resolve(res);
          } else {
            reject(res.msg);
          }
        }, (error: any) => {
          reject(error);
        });
      });
    });
  }

  SaveProperty(collection: string, properties: any, key: string) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        const posted: any = {
          op: "setprop",
          user: LSUSERMETA,
          collection: collection,
          properties: properties,
          key: key
        }
        this.http.post<any>(this.apiHost + "/crud", posted, {
          headers: new HttpHeaders(this.crudHeaders)
        }).subscribe((res: any) => {
          if (res && res.result) {
            resolve(res);
          } else {
            reject(res.msg);
          }
        }, (error: any) => {
          reject(error);
        });
      });
    });
  }

  Reconfigure(collection_: string) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        const posted: any = {
          op: "reconfigure",
          user: LSUSERMETA,
          collection: collection_
        }
        this.http.post<any>(this.apiHost + "/crud", posted, {
          headers: new HttpHeaders(this.crudHeaders)
        }).subscribe((res: any) => {
          if (res && res.result) {
            this.storage.remove("LSFILTER_" + collection_).then(() => {
              resolve(res);
            });
          } else {
            reject(res.msg);
          }
        }, (error: any) => {
          reject(error);
        });
      });
    });
  }

  AnnounceNow(view: string, tfac: string, scope: string, collection: string) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        const posted_: any = {
          op: "announce",
          user: LSUSERMETA,
          collection: collection,
          view: view,
          tfac: tfac,
          scope: scope
        }
        this.http.post<any>(this.apiHost + "/crud", posted_, {
          headers: new HttpHeaders(this.crudHeaders)
        }).subscribe((res: any) => {
          if (res && res.result) {
            resolve(res);
          } else {
            reject(res.msg);
          }
        }, (error: any) => {
          reject(error);
        });
      });
    });
  }

  PurgeFiltered(collection: string, tfac: string, match: any) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        const posted: any = {
          op: "purge",
          user: LSUSERMETA,
          collection: collection,
          match: match,
          tfac: tfac
        }
        this.http.post<any>(this.apiHost + "/crud", posted, {
          headers: new HttpHeaders(this.crudHeaders)
        }).subscribe((res: any) => {
          if (res && res.result) {
            resolve(res);
          } else {
            reject(res.msg);
          }
        }, (error: any) => {
          reject(error);
        });
      });
    });
  }

  Submit(collection: string, structure: any, form: any, _id: string, op: string, file: any, match: any, filter: any, view: any) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        const properties = structure.properties;
        let doc_: any = {};
        let i = 0;
        for (let item in properties) {
          doc_[item] = properties[item].bsonType === "date" && form.get(item).value ? new Date(form.get(item).value) : form.get(item).value;
          if (i === Object.keys(properties).length - 1) {
            _id ? (doc_["_id"] = _id) : null;
            let posted_: any = {
              op: op,
              user: LSUSERMETA,
              collection: collection,
              doc: doc_,
              match: match && match.length > 0 ? match : null,
              filter: filter ? filter : null,
              _id: _id ? _id : null,
              view: view
            }
            if (file) {
              let formData: FormData = new FormData();
              const sto_collection_id_ = doc_["sto_collection_id"];
              formData.append("op", op);
              formData.append("email", LSUSERMETA.email);
              formData.append("token", LSUSERMETA.token);
              formData.append("file", file, file.name);
              formData.append("collection", sto_collection_id_);
              formData.append("prefix", doc_["sto_prefix"]);
              formData.append("name", file.name);
              formData.append("size", file.size);
              formData.append("type", doc_["sto_file_type"]);
              this.http.post<any>(this.apiHost + "/import", formData, {
                headers: new HttpHeaders(this.uploadHeaders)
              }).subscribe((res: any) => {
                res.cid = sto_collection_id_;
                if (res && res.result) {
                  resolve(res);
                } else {
                  reject(res.msg);
                }
              }, (error: any) => {
                reject(error);
              });
            } else {
              this.http.post<any>(this.apiHost + "/crud", posted_, {
                headers: new HttpHeaders(this.crudHeaders)
              }).subscribe((res: any) => {
                if (res && res.result) {
                  resolve(res);
                } else {
                  reject(res.msg);
                }
              }, (error: any) => {
                reject(error);
              });
            }
          } else {
            i++;
          }
        }
      });
    });
  }

  Find(op: string, collection: string, projection: any, match: any, sort: any, page: number, limit: number) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        this.storage.get("LSVIEW-" + collection).then((LSVIEW: any) => {
          const posted: any = {
            op: op,
            user: LSUSERMETA,
            collection: collection,
            projection: projection,
            match: match,
            sort: sort,
            page: page,
            limit: limit,
            view: LSVIEW ? LSVIEW : null
          }
          this.http.post<any>(this.apiHost + "/crud", posted, {
            headers: new HttpHeaders(this.crudHeaders)
          }).subscribe((res: any) => {
            if (res && res.result) {
              resolve(res);
            } else {
              reject(res.msg);
            }
          }, (error: any) => {
            reject(error);
          });
        });
      });
    });
  }

  View(_id: string, vie_id_: string, source_: string) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        this.http.post<any>(this.apiHost + "/crud", {
          _id: _id,
          vie_id: vie_id_,
          op: "view",
          source: source_,
          user: LSUSERMETA
        }, {
          headers: new HttpHeaders(this.crudHeaders)
        }).subscribe((res: any) => {
          if (res && res.result) {
            resolve(res);
          } else {
            reject(res.msg);
          }
        }, (error: any) => {
          reject(error);
        });
      });
    });
  }

  Pivot(_id: any, apikey_: string) {
    return new Promise((resolve, reject) => {
      const __id = typeof _id === 'object' && "$oid" in _id && _id["$oid"] ? _id["$oid"] : _id;
      const url_ = this.apiHost + "/get/pivot" + "/" + __id + "?k=" + apikey_;
      this.http.get(url_, {
        headers: new HttpHeaders(this.crudHeaders)
      }).subscribe((res: any) => {
        if (res && res.result) {
          resolve(res);
        } else {
          reject(res.msg);
        }
      }, (error: any) => {
        console.error("*** error", error);
        reject(error);
      });
    });
  }

  Visual(_id: string, apikey_: string) {
    return new Promise((resolve, reject) => {
      const url_ = this.apiHost + "/get/visual" + "/" + _id + "?k=" + apikey_;
      this.http.get(url_, {
        headers: new HttpHeaders(this.crudHeaders)
      }).subscribe((res: any) => {
        if (res && res.result) {
          resolve(res.chart);
        } else {
          reject(res.msg);
        }
      }, (error: any) => {
        console.error("*** error", error);
        reject(error);
      });
    });
  }

  Match(id: string) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        this.http.post<any>(this.apiHost + "/crud", {
          op: "match",
          user: LSUSERMETA,
          collection: id
        }, {
          headers: new HttpHeaders(this.crudHeaders)
        }).subscribe((res: any) => {
          if (res && res.result) {
            if (res.result) {
              const resp = JSON.parse(res.result);
              resolve(resp);
            } else {
              resolve(true);
            }
          } else {
            reject(res.msg);
          }
        }, (error: any) => {
          reject(error);
        });
      });
    });
  }

  MultiCrud(op: string, collection: string, match: any, is_crud: boolean) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        this.http.post<any>(this.apiHost + "/crud", {
          op: op,
          user: LSUSERMETA,
          collection: collection,
          match: match,
          doc: null,
          is_crud: is_crud
        }, {
          headers: new HttpHeaders(this.crudHeaders)
        }).subscribe((res: any) => {
          if (res && res.result) {
            if (res.response) {
              const resp = JSON.parse(res.response);
              this.storage.set("LSRECORDID", resp._id).then(() => {
                this.updateListener.next(resp);
                resolve(resp);
              }).catch((error: any) => {
                reject(error);
              });
            } else {
              resolve(true);
            }
          } else {
            reject(res.msg);
          }
        }, (error: any) => {
          reject(error);
        });
      });
    });
  }

  getViews() {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        const posted: any = {
          op: "views",
          user: LSUSERMETA,
          dashboard: false
        }
        this.http.post<any>(this.apiHost + "/crud", posted, {
          headers: new HttpHeaders(this.crudHeaders)
        }).subscribe((res: any) => {
          if (res && res.result) {
            // this.views.next(res);
            resolve(res);
          } else {
            reject(res.msg);
          }
        }, (error: any) => {
          reject(error);
        });
      });
    });
  }

  Template(proc_: string, template_: any) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        const posted: any = {
          op: "template",
          proc: proc_,
          template: template_,
          user: LSUSERMETA
        }
        this.http.post<any>(this.apiHost + "/crud", posted, {
          headers: new HttpHeaders(this.crudHeaders)
        }).subscribe((res: any) => {
          if (res && res.result) {
            resolve(res);
          } else {
            reject(res.msg);
          }
        }, (error: any) => {
          reject(error);
        });
      });
    });
  }

  Dump() {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        this.http.post<any>(this.apiHost + "/crud", {
          op: "dump",
          user: LSUSERMETA
        }, {
          headers: new HttpHeaders(this.crudHeaders)
        }).subscribe((res: any) => {
          if (res && res.result) {
            resolve(true);
          } else {
            reject(res.msg);
          }
        }, (error: any) => {
          reject(error);
        });
      });
    });
  }

  Download(obj: any) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        this.http.post<any>(this.apiHost + "/get/dump", {
          user: LSUSERMETA,
          type: obj.type,
          id: obj.id
        }, {
          headers: new HttpHeaders(this.crudHeaders),
          responseType: "blob" as "json"
        }).subscribe((res: any) => {
          if (res) {
            const fn_ = obj.id + ".gz";
            let binaryData = [];
            binaryData.push(res);
            let downloadLink = document.createElement("a");
            downloadLink.href = window.URL.createObjectURL(new Blob(binaryData, { type: "application/octet-strem" }));
            downloadLink.setAttribute("download", fn_);
            document.body.appendChild(downloadLink);
            downloadLink.click();
            resolve(true);
          } else {
            reject(res.msg);
          }
        }, (error: any) => {
          reject(error);
        });
      });
    });
  }

  getCollections() {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        const posted: any = {
          op: "collections",
          user: LSUSERMETA
        }
        this.http.post<any>(this.apiHost + "/crud", posted, {
          headers: new HttpHeaders(this.crudHeaders)
        }).subscribe((res: any) => {
          if (res && res.result) {
            resolve(res);
          } else {
            reject(res.msg);
          }
        }, (error: any) => {
          reject(error);
        });
      });
    });
  }

  getAnnouncements() {
    this.Find(
      "read", "_log", null, [{
        key: "log_type",
        op: "eq",
        value: "Announcement"
      }], { "log_date": -1 }, 1, 10).then((res: any) => {
        this.announcements.next(res);
      }).catch((error: any) => {
        console.error("*** announcements error", error);
      });
  }

  getParents(obj: any) {
    return new Promise((resolve, reject) => {
      if (obj.parents) {
        let parents: any = [];
        for (let p = 0; p < obj.parents.length; p++) {
          let parent = obj.parents[p];
          const remote_fields = parent["remote_fields"];
          let data: any = [];
          this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
            this.http.post<any>(this.apiHost + "/crud", {
              op: "parent",
              user: LSUSERMETA,
              match: [],
              fields: parent["remote_fields"],
              collection: parent["collection"]
            }, {
              headers: new HttpHeaders(this.crudHeaders)
            }).subscribe((res: any) => {
              if (res && res.result && res.data) {
                for (let i = 0; i < res.data.length; i++) {
                  let id = "";
                  for (let j = 0; j < remote_fields.length; j++) {
                    id += res.data[i][remote_fields[j]] + " ";
                    if (j === remote_fields.length - 1) {
                      let data_line: any = {};
                      data_line["id"] = res.data[i]["_id"];
                      data_line[parent["local_field"]] = id.trim();
                      data.push(data_line);
                    }
                  }
                  if (i === res.data.length - 1) {
                    parents.push({ "title": parent["title"], "collection": parent["collection"], "local_field": parent["local_field"], "data": data });
                  }
                }
                if (p === obj.parents.length - 1) {
                  resolve(parents);
                }
              } else {
                reject(res.msg);
              }
            }, (error: any) => {
              reject(error);
            });
          });
        }
      } else {
        resolve([]);
      }
    });
  }

  modalSubmitListener = new Subject<any>();
  updateListener = new Subject<any>();
  views = new Subject<any>();
  subjects = new Subject<any>();
  visuals = new Subject<any>();
  collections = new Subject<any>();

}
