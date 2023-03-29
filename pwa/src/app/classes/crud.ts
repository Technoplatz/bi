/*
Technoplatz BI

Copyright (C) 2019-2023 Technoplatz IT Solutions GmbH, Mustafa Mat

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
import { Miscellaneous } from "./misc";
import { environment } from "../../environments/environment";

@Injectable({
  providedIn: "root"
})

export class Crud {
  public cartitems = [];
  public productList: any = [];
  public fields: any = [];
  private apiHost: string = "";
  public modalSubmitListener = new Subject<any>();
  public updateListener = new Subject<any>();
  public objectsListener = new BehaviorSubject([]);
  public objects = this.objectsListener.asObservable();
  public collections = new BehaviorSubject<any>([]);
  public views = new BehaviorSubject<any>([]);
  public visuals = new BehaviorSubject<any>([]);
  public saas = new BehaviorSubject(null);
  public announcements = new BehaviorSubject<any>([]);
  private crudHeaders: any = {
    "Content-Type": "application/json",
    "X-Api-Key": environment.apiKey
  }

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
      delete structure.properties["col_structure"];
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
        const parents_ = structure.parents ? structure.parents.find((obj: any) => obj.lookup[0]?.local === item) : null;
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
          parents: parents_,
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

  Reconfigure(collection_: string) {
    return new Promise((resolve, reject) => {
      this.misc.apiCall("crud", {
        op: "reconfigure",
        collection: collection_
      }).then((res: any) => {
        this.storage.remove("LSFILTER_" + collection_).then(() => {
          resolve(res);
        });
      }).catch((error: any) => {
        reject(error);
      });
    });
  }

  Submit(collection: string, structure: any, form: any, _id: string, op: string, file: any, match: any, filter: any, view: any) {
    return new Promise((resolve, reject) => {
      const properties = structure.properties;
      let doc_: any = {};
      let i = 0;
      for (let item in properties) {
        doc_[item] = properties[item].bsonType === "date" && form.get(item).value ? new Date(form.get(item).value) : form.get(item).value;
        if (i === Object.keys(properties).length - 1) {
          _id ? (doc_["_id"] = _id) : null;
          if (file) {
            let posted_: FormData = new FormData();
            const sto_collection_id_ = doc_["sto_collection_id"];
            posted_.append("file", file, file.name);
            posted_.append("collection", sto_collection_id_);
            this.misc.apiFileCall("import", posted_).then((res: any) => {
              res.cid = sto_collection_id_;
              resolve(res);
            }).catch((error: any) => {
              reject(error.msg);
            });
          } else {
            this.misc.apiCall("crud", {
              op: op,
              collection: collection,
              doc: doc_,
              match: match && match.length > 0 ? match : null,
              filter: filter ? filter : null,
              _id: _id ? _id : null,
              view: view
            }).then((res: any) => {
              resolve(res);
            }).catch((error: any) => {
              reject(error);
            });
          }
        } else {
          i++;
        }
      }
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
          resolve(res.visual);
        } else {
          reject(res.msg);
        }
      }, (error: any) => {
        console.error("*** error", error);
        reject(error);
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

  getCollections(LSUSERMETA: any) {
    return new Promise((resolve, reject) => {
      const posted: any = {
        op: "collections",
        user: LSUSERMETA
      }
      this.http.post<any>(this.apiHost + "/crud", posted, {
        headers: new HttpHeaders(this.crudHeaders)
      }).subscribe((res: any) => {
        if (res && res.result) {
          this.misc.collections.next(res);
          resolve(this.collections.next(res));
        } else {
          reject(res.msg);
        }
      }, (error: any) => {
        reject(error);
      });
    });
  }

  getCollection(id: string) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        const posted: any = {
          collection: id,
          op: "collection",
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

  getViews(LSUSERMETA: any) {
    return new Promise((resolve, reject) => {
      const posted: any = {
        op: "views",
        user: LSUSERMETA,
        dashboard: false
      }
      this.http.post<any>(this.apiHost + "/crud", posted, {
        headers: new HttpHeaders(this.crudHeaders)
      }).subscribe((res: any) => {
        if (res && res.result) {
          resolve(this.views.next(res));
        } else {
          reject(res.msg);
        }
      }, (error: any) => {
        reject(error);
      });
    });
  }

  getAnnouncements(LSUSERMETA: any) {
    return new Promise((resolve, reject) => {
      this.misc.apiCall("crud", {
        op: "read",
        collection: "_announcement",
        projection: null,
        match: [{
          key: "ano_to",
          op: "eq",
          value: LSUSERMETA.email
        }],
        sort: { "log_date": -1 },
        page: 1,
        limit: 10
      }).then((res: any) => {
        resolve(this.announcements.next(res));
      }).catch((error: any) => {
        console.error("*** announcements error", error);
        reject(error);
      });
    });
  }

  getAll() {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        this.getSaas().then(() => {
          this.getCollections(LSUSERMETA).then(() => {
            this.getViews(LSUSERMETA).then(() => {
              this.getAnnouncements(LSUSERMETA).then(() => {
                resolve(true);
              });
            }).catch((error: any) => {
              reject(error);
            });
          }).catch((error: any) => {
            reject(error);
          });
        });
      });
    });
  }

  getSaas() {
    return new Promise((resolve, reject) => {
      const posted: any = {
        op: "saas"
      }
      this.http.post<any>(this.apiHost + "/auth", posted, {
        headers: new HttpHeaders(this.crudHeaders)
      }).subscribe((res: any) => {
        if (res && res.result) {
          this.saas.next(res.saas);
          resolve(res.saas);
        } else {
          reject(res.msg);
        }
      }, (error: any) => {
        reject(error);
      });
    });
  }

}
