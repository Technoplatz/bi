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

import { Component, OnInit, HostListener, Input, ViewChild } from "@angular/core";
import { UntypedFormBuilder, UntypedFormGroup } from "@angular/forms";
import { AlertController } from "@ionic/angular";
import { TranslateService } from "@ngx-translate/core";
import { Storage } from "@ionic/storage";
import { Miscellaneous } from "../../classes/misc";
import { Crud } from "./../../classes/crud";
import { environment } from "./../../../environments/environment";

@Component({
  selector: "app-crud",
  templateUrl: "./crud.page.html",
  styleUrls: ["./crud.page.scss"],
})
export class CrudPage implements OnInit {
  @Input() shuttle: any = {};
  @Input() modified: boolean = false;
  @ViewChild("barcodefocus", { static: false }) barcodefocus: any;
  public crudForm: UntypedFormGroup;
  public novalue: any = null;
  public required: any = [];
  public property_list: any = [];
  public tab: string = "data";
  public op: string = "";
  public saved_filter: string = "";
  public saved_filters: any = [];
  public collection: string = "";
  public user: any;
  public data_: any = {};
  public filterops: any = environment.filterops;
  public pivotvalueops: any = environment.pivotvalueops;
  public loadingText: string = environment.misc.loadingText;
  public timeout: number = environment.misc.default_delay;
  public timeZone = environment.timeZone;
  public selected_: any = [];
  public fieldsupd: any = [];
  public fields: any = [];
  public in_progress: boolean = false;
  public is_ready: boolean = false;
  public _id: string = "";
  public arrayitem: any = {};
  public error: string = "";
  public arrays: any = [];
  public parentkey: number = 0;
  public localfield: string = "";
  public field_parents: any;
  public parents: any;
  public relact: boolean = false;
  public reloading: boolean = false;
  public related: any = [];
  public actionix: number = -1;
  public is_token_copied: boolean = false;
  public scan_: boolean = false;
  public scanned_: any = [];
  public istrue_: boolean = true;
  public isnoninteractive_: boolean = false;
  public visible: string = "hide";
  public parent: any = {};
  public aktions: any = [];
  public properties_: any = {};
  public links: any = [];
  public counter: number = 0;
  public scan_result: string = "";
  private sweeped: any;
  public link_text: string = "";
  public link_: any = {};
  public linked_: any = [];
  public date_format: string = "DD.MM.YYYY HH:mm";
  public locale_: string = "en-US";
  public link_limit_: number = 100;
  private counters: any = {};
  private filter: any = [];
  private actions: any = [];
  private file: any = null;
  private relatedx: any = [];
  private collections: any = [];
  private structure__: any = {};
  private link_projection_: any = {};
  private input_: string = "";

  @HostListener("document:keydown", ["$event"]) loginWithEnter(event: any) {
    if (event.key === "Enter") {
      this.input_ = this.crudForm.get(event.target.name)?.value;
      if (event.target.getAttribute("name") === "arrayitem") {
        this.doAddItemToArray(event).then(() => {
        }).catch((error: any) => {
          this.misc.doMessage(error, "error");
        });
      } else {
        this.crudForm.get(event.target.name)?.setValue(this.input_.replace(/NAVIGATEPREVIOUS|NAVIGATENEXT|UNIDENTIFIED|NULL|CUT|COPY|SHIFT|TAB|CAPSLOCK|METAV|ARROWDOWN|ARROWUP|ARROWLEFT|ARROWRIGHT|BACKSPACE/gi, "").toUpperCase());
        this.submit_f();
      }
    } else {
      this.input_ += event.key;
    }
  }

  constructor(
    private formBuilder: UntypedFormBuilder,
    public misc: Miscellaneous,
    private storage: Storage,
    private crud: Crud,
    private alert: AlertController,
    public translate: TranslateService
  ) {
    this.crudForm = this.formBuilder.group({}, {});
    this.misc.localization.subscribe((l_: any) => {
      this.locale_ = l_;
    });
  }

  customCounterFormatter(inputLength: number, maxLength: number) {
    return `${maxLength - inputLength} characters remaining`;
  }

  ngOnDestroy() {
    this.storage.remove("LSOP").then(() => { });
  }

  ngOnInit() {
    this.modified = false;
    this.collection = this.shuttle.collection;
    this.user = this.shuttle.user;
    this.op = this.shuttle.op;
    this.structure__ = this.shuttle.structure;
    this.properties_ = this.shuttle.structure.properties;
    this.sweeped = this.shuttle.sweeped;
    this.counters = this.shuttle.counters;
    this.filter = this.shuttle.filter;
    this.collections = this.shuttle.collections;
    this.actionix = this.shuttle.actionix;
    this.scan_ = this.shuttle.scan;
    this.links = this.shuttle.structure.links;
    this.link_ = this.links ? this.links[0] : null;
    this.parents = this.structure__?.parents ? this.structure__.parents : [];
    this.actions = this.shuttle.actions && this.shuttle.actions.length > 0 ? this.shuttle.actions : [];
    this.isnoninteractive_ = this.actions[this.actionix]?.noninteractive === true ? true : false;
    this.storage.get("LSSCANNED").then((LSSCANNED: any) => {
      this.scanned_ = LSSCANNED ? LSSCANNED : [];
      this.doGetAllAktions(this.op).then((res: any) => {
        this.aktions = res;
        this.crud.init_form(this.op, this.structure__, this.crudForm, this.shuttle.data, this.collections, this.counters, this.actionix).then((res: any) => {
          this.tab = "data";
          this.crudForm = res.form;
          this.fields = res.fields;
          this.fieldsupd = this.op === "insert" && this.collection === "_collection" ? res.fields.filter((obj: any) => obj.name !== "col_structure") : res.fields;
          this.data_ = this.shuttle.data ? this.shuttle.data : res.init;
          this._id = this.op === "update" ? this.shuttle.data && this.shuttle.data._id ? this.shuttle.data._id : null : null;
          this.get_sub_properties(this.collection).then(() => {
            if (this.actionix >= 0) {
              this.doAktionChange(this.actionix).then(() => { }).catch((error: any) => {
                this.misc.doMessage(error, "error");
              });
            }
          }).catch((error: any) => {
            this.misc.doMessage(error, "error");
          }).finally(() => {
            this.visible = "show";
            this.scan_ ? setInterval(() => { this.barcodefocus.setFocus(); }, 1000) : null;
            for (let i in this.crudForm.controls) {
              this.crudForm.controls[i].markAsTouched();
            }
          });
        }).catch((error: any) => {
          this.misc.doMessage(error, "error");
        });
      });
    });
  }

  doGetAllAktions(op: string) {
    return new Promise((resolve) => {
      if (op !== "action") {
        resolve([]);
      } else {
        resolve(this.shuttle.actions && this.shuttle.actions.length > 0 ? this.shuttle.actions : []);
      }
    });
  }

  async propertiesAktionFilter(action_: any) {
    return Object.entries(this.properties_).filter((obj: any) => action_.set.some((f: any) => obj[0] === f.key));
  }

  doAktionChange(ix: number) {
    return new Promise((resolve) => {
      const action_ = this.aktions[ix];
      const struc_: any = this.structure__;
      let controls_: any = {};
      let fields_: any = {};
      this.fieldsupd = this.fields.filter((obj: any) => action_.set.some((f: any) => obj.name === f.key));
      this.propertiesAktionFilter(action_).then((props_: any) => {
        for (let j = 0; j < props_.length; j++) {
          fields_[props_[j][0]] = props_[j][1];
          if (j === props_.length - 1) {
            struc_.properties = fields_;
            struc_.required = struc_.required ? struc_.required.filter((obj: any) => action_.set.some((f: any) => obj.name === f.key)) : [];
            const form_ctrl_filter_ = Object.entries(this.crudForm.controls).filter((obj: any) => action_.set.some((f: any) => obj[0] === f.key));
            for (let k = 0; k < form_ctrl_filter_.length; k++) {
              controls_[form_ctrl_filter_[k][0]] = form_ctrl_filter_[k][1];
              if (k === form_ctrl_filter_.length - 1) {
                for (let f = 0; f < action_.set.length; f++) {
                  const ndate_ = new Date(Date.now() - ((new Date()).getTimezoneOffset() * 60000));
                  action_.set[f].value === "$CURRENT_DATE" ? action_.set[f].value = ndate_.toISOString().substring(0, 19) : action_.set[f].value === "$TIMESTAMP" ? action_.set[f].value = ndate_.toISOString().replace(/-|:|T/gi, '').substring(0, 14) : null;
                  this.data_[action_.set[f].key] = !action_.set[f].value ? this.data_[action_.set[f].key] : action_.set[f].value;
                  this.crudForm.get(action_.set[f].key)?.setValue(!action_.set[f].value ? this.data_[action_.set[f].key] : action_.set[f].value);
                  if (f === action_.set.length - 1) {
                    this.crudForm.controls = controls_;
                    this.visible = "show";
                    resolve(true);
                  }
                }
              }
            }
          }
        }
      });
    });
  }

  submit_f() {
    if (!this.in_progress) {
      this.input_ = "";
      this.crudForm.updateValueAndValidity();
      if (!["remove"].includes(this.op) && !this.crudForm.valid && !this.isnoninteractive_) {
        const msg_ = this.op === "action" ? "form is not valid or action is not non-interactive" : "form is not valid";
        this.misc.doMessage(msg_, "error");
      } else {
        this.linked_ = this.link_text ? this.link_text.trim().split('\n').filter((e: any) => { return e }) : [];
        this.modified = true;
        this.in_progress = true;
        this.crud.submit_f(this.data_, this.collection, this.structure__, this.crudForm, this._id, this.op, this.file, this.sweeped, this.filter, this.actionix, this.link_, this.linked_).then((res_: any) => {
          res_ && res_?.result === true ? this.misc.doMessage(`${this.op} completed successfully`, "success") : null;
          this.crud.modalSubmitListener.next({ result: true });
          if (res_ && res_.token) {
            this.alert.create({
              subHeader: "A new API Token has been generated. This is the only chance to copy!",
              message: res_.token,
              buttons: [{
                text: "COPY",
                handler: () => {
                  this.misc.copy_to_clipboard(`Bearer ${res_.token}`).then(() => { }).catch((error: any) => {
                    this.misc.doMessage(error, "error");
                  }).finally(() => {
                    this.dismiss_modal({ op: this.op, modified: this?.modified, filter: [], cid: res_ && res_.cid ? res_.cid : null, res: res_ });
                  });
                }
              }]
            }).then((alert: any) => {
              alert.present();
            });
          } else {
            this.scan_result = "";
            const iot_input_ = "bar_input";
            if (this.scan_) {
              this.scan_result = `<div class="scan-ok">&#10003; OK ${this.crudForm.get(iot_input_)?.value}<br /><span>Read at ${new Date(Date.now()).toISOString()}</span></div>`;
              this.scanned_.unshift({ input: this.crudForm.get(iot_input_)?.value, date: new Date(Date.now()).toISOString() });
              this.storage.set("LSSCANNED", this.scanned_).then(() => {
                this.data_[iot_input_] = "";
                this.crudForm.get(iot_input_)?.setValue(this.data_[iot_input_]);
              });
            } else {
              this.dismiss_modal({ op: this.op, modified: this?.modified, filter: [], cid: res_ && res_.cid ? res_.cid : null, res: res_ });
            }
          }
        }).catch((error_: any) => {
          this.misc.doMessage(error_, "error");
        }).finally(() => {
          this.in_progress = false;
        });
      }
    }
  }

  dump(op_: string) {
    this.in_progress = true;
    this.misc.api_call("crud", {
      op: op_,
      collection: "_dump",
      dumpid: this.data_.dmp_id,
      type: this.data_.dmp_type,
      responseType: "blob" as "json"
    }).then((res_: any) => {
      if (op_ === "dumpd") {
        const fn_ = res_.filename;
        let binaryData = [];
        binaryData.push(res_.binary);
        let downloadLink = document.createElement("a");
        downloadLink.href = window.URL.createObjectURL(new Blob(binaryData, { type: "application/octet-strem" }));
        downloadLink.setAttribute("download", fn_);
        document.body.appendChild(downloadLink);
        downloadLink.click();
      }
      this.misc.doMessage(`${op_} completed successfully`, "success");
    }).catch((error: any) => {
      this.misc.doMessage(error, "error");
    }).finally(() => {
      this.dismiss_modal({ op: op_, modified: true, filter: [] });
      this.in_progress = false;
    });
  }

  action_f() {
    const op_ = "action";
    this.in_progress = true;
    const properties_ = this.structure__.properties;
    let doc_: any = {};
    let i = 0;
    for (let item in properties_) {
      doc_[item] = properties_[item].bsonType === "date" && this.crudForm.get(item)?.value ? new Date(this.crudForm.get(item)?.value) : this.crudForm.get(item)?.value;
      if (i === Object.keys(properties_).length - 1) {
        const posted_: any = {
          op: op_,
          collection: this.collection,
          doc: doc_,
          data: this.data_,
          match: this.sweeped,
          filter: this.filter,
          _id: this._id,
          actionix: this.actionix
        }
        const download_by_ = this.actions[this.actionix]["download_by"];
        download_by_ && this.data_ && this.data_[download_by_] ? posted_.responseType = "blob" : null;
        this.misc.api_call("crud", posted_).then((res_: any) => {
          if (res_.filename) {
            const fn_ = res_.filename;
            let binaryData = [];
            binaryData.push(res_.binary);
            let downloadLink = document.createElement("a");
            downloadLink.href = window.URL.createObjectURL(new Blob(binaryData, { type: "application/octet-strem" }));
            downloadLink.setAttribute("download", fn_);
            document.body.appendChild(downloadLink);
            downloadLink.click();
            this.misc.doMessage(`action completed successfully`, "success");
          } else {
            if (res_.result) {
              this.misc.doMessage(res_.msg ? res_.msg : `action completed successfully`, "success");
            } else {
              this.misc.doMessage(res_.msg ? res_.msg : "action error", "error");
            }
          }
        }).catch((error_: any) => {
          console.error("!!! E1", error_);
          this.misc.doMessage(error_, "error");
        }).finally(() => {
          this.dismiss_modal({ op: op_, modified: true, filter: [] });
          this.in_progress = false;
        });
      } else {
        i++;
      }
    }
  }

  async doRemove() {
    const alert = await this.alert.create({
      header: "Deleting",
      message: "Please confirm this deletion.",
      buttons: [
        {
          text: "CANCEL",
          role: "cancel",
          cssClass: "secondary",
          handler: () => { }
        }, {
          text: "OKAY",
          handler: () => {
            this.op = "remove";
            this.submit_f();
          }
        }
      ]
    });
    alert.style.cssText = "--backdrop-opacity: 0 !important; z-index: 99999 !important; box-shadow: none !important;";
    await alert.present();
  }

  doDeleteItemFromArray(name: any, item: any) {
    this.data_[name] = this.data_[name].filter((e: any) => e !== item);
    this.crudForm.controls[name].setValue(this.data_[name]);
  }

  doAddItemToArray(event: any) {
    return new Promise((resolve, reject) => {
      const field_ = this.fields.filter((obj: any) => obj.name === event.target.getAttribute("title"));
      const maxItems = field_[0] && field_[0].maxItems ? field_[0].maxItems : 32;
      const chipEl = document.createElement("ion-chip");
      chipEl.slot = "start";
      chipEl.outline = true;
      !this.data_[event.target.getAttribute("title")] ? this.data_[event.target.getAttribute("title")] = [] : null;
      if (event.target.value && this.data_[event.target.getAttribute("title")].length < maxItems) {
        this.data_[event.target.getAttribute("title")] ? null : this.data_[event.target.getAttribute("title")] = [];
        this.data_[event.target.getAttribute("title")].push(event.target.getAttribute("type") === "number" ? Number(event.target.value) : event.target.value);
        this.arrayitem[event.target.getAttribute("title")] = null;
        this.crudForm.controls[event.target.getAttribute("title")].setValue(this.data_[event.target.getAttribute("title")]);
        resolve(true);
      } else {
        this.misc.doMessage("maximum number of items exceeds", "error");
        reject("array item is invalid");
      }
    });
  }

  goTab(tab: any) {
    this.tab = tab;
    this.localfield = tab.local_field ? tab.local_field : null;
  }

  doSubmitRelated() {
    this.tab = "data";
    this.related = this.relatedx;
    this.data_[this.field_parents.match[0].key] = [];
    for (let k = 0; k < this.related.length; k++) {
      if (this.related[k].selected) {
        this.data_[this.field_parents.match[0].key].push(this.related[k][this.field_parents.match[0].value]);
      }
      if (k === this.related.length - 1) {
        this.crudForm.get(this.field_parents.match[0].key)?.setValue(this.data_[this.field_parents.match[0].key]);
      }
    }
  }

  dismiss_modal(obj: any) {
    this.misc.dismissModal(obj ? obj : { modified: false, filter: [] }).then(() => { }).catch((error: any) => {
      this.misc.doMessage(error, "error");
    });
  }

  onFileChange(ev: any) {
    const file: any = ev.target.files[0];
    if (file) {
      this.file = file;
      this.data_["sto_file_name"] = file.name;
      this.data_["sto_file_size"] = file.size;
    } else {
      this.file = null;
    }
  }

  get_sub_properties(coll_: string) {
    return new Promise((resolve, reject) => {
      this.misc.api_call("crud", {
        op: "read",
        collection: "_collection",
        projection: null,
        match: [{
          key: "col_id",
          op: "eq",
          value: coll_ === "_collection" ? this.data_["col_id"] : coll_ === "_visual" ? this.data_["vis_collection_id"] : coll_ === "_token" ? this.data_["tkn_collection_id"] : coll_ === "_permission" ? this.data_["per_collection_id"] : coll_
        }],
        sort: null,
        page: 1,
        limit: 1
      }).then((res: any) => {
        const properties = res && res.data && res.data[0] && res.data[0].col_structure && res.data[0].col_structure.properties ? res.data[0].col_structure.properties : this.properties_;
        let i = 0;
        let array_: any = [];
        for (let prop_ in properties) {
          if (i === Object.keys(properties).length - 1) {
            array_.push({ key: prop_, value: properties[prop_]?.title });
            this.property_list = array_;
            resolve(this.property_list);
          } else {
            array_.push({ key: prop_, value: properties[prop_]?.title });
            i++;
          }
        }
      }).catch((res: any) => {
        this.misc.doMessage(res, "error");
        reject(res);
      });
    });
  }

  change_enum(field_: any, coll_: any) {
    if (field_.collection) {
      this.get_sub_properties(coll_).then((props_: any) => {
        this.property_list = props_;
      }).catch((res: any) => {
        this.misc.doMessage(res, "error");
      });
    }
  }

  doGoLink(link_: any) {
    this.link_ = link_;
    this.link_text = "";
    let j_ = 0;
    this.data_["_link_" + link_.collection]?.length > 0 ? this.data_["_link_" + link_.collection].forEach((obj_: any) => {
      this.link_text += obj_[link_.get] ? (j_ > 0 ? "\n" : "") + obj_[link_.get] : "";
      j_++;
      j_ === this.data_["_link_" + link_.collection].length ? this.tab = "link" : null;
    }) : this.tab = "link";
  }

  get_linked() {
    let filter_ = [];
    this.link_text = "";
    const match_ = this.link_?.match;
    const collection_ = this.link_?.collection;
    const get_ = this.link_?.get;
    const autofill_ = this.link_?.autofill;
    if (match_ && collection_ && this.link_projection_ && get_ && autofill_) {
      this.reloading = true;
      this.link_projection_ = {};
      this.link_projection_[get_] = 1;
      for (let l = 0; l < match_.length; l++) {
        filter_.push({
          key: match_[l].key,
          op: match_[l].op,
          value: this.properties_[match_[l].value] ? this.data_[match_[l].value] !== "" ? this.data_[match_[l].value] : null : match_[l].value
        })
        if (l === match_.length - 1) {
          this.misc.api_call("crud", {
            op: "read",
            collection: collection_,
            projection: this.link_projection_,
            match: filter_,
            sort: this.link_projection_,
            group: true,
            page: 1,
            limit: this.link_limit_
          }).then((res: any) => {
            const data_ = res.data;
            if (data_) {
              for (let d = 0; d < data_.length; d++) {
                this.link_text += data_[d][get_];
                if (d === data_.length - 1) { } else {
                  this.link_text += "\n";
                }
              }
            }
          }).catch((error: any) => {
            this.misc.doMessage(error, "error");
          }).finally(() => {
            this.reloading = false;
          });
        }
      }
    }
  }

  get_parent(parent_: any) {
    this.parent = parent_;
    let projection_: any = {};
    this.relact = true;
    this.tab = "relation";
    let filter_ = this.parent.filter ? this.parent.filter : [];
    this.parent.filter.forEach((f: any) => f.value?.toString().substr(0, 1) === "$" ? f.value = this.data_[f.value?.toString().substr(1)] : Object.keys(this.properties_).includes(f.value) ? f.value = this.data_[f.value] : null);
    let matchkeys_: any = [];
    const group_ = this.parent.group ? this.parent.group : false;
    this.parent.match.forEach((m: any) => matchkeys_.push(m.key));
    if (this.parent.get && this.parent.get.length > 0) {
      this.reloading = true;
      for (let p = 0; p < this.parent.get.length; p++) {
        projection_[this.parent.get[p]] = 1;
        if (p === this.parent.get.length - 1) {
          this.related = [];
          this.misc.api_call("crud", {
            op: "read",
            collection: this.parent.collection,
            projection: projection_,
            match: filter_,
            sort: { "_modified_at": -1 },
            group: group_,
            page: 1,
            limit: 1000
          }).then((res: any) => {
            if (res && res.data) {
              this.related = res.data;
              for (let k = 0; k < this.related.length; k++) {
                this.related[k].selected = true;
                if (k === this.related.length - 1) {
                  this.relatedx = this.related;
                  this.reloading = false;
                }
              }
            }
          }).catch((error: any) => {
            this.misc.doMessage(error, "error");
          }).finally(() => {
            this.field_parents = parent_;
            this.reloading = false;
          });
        }
      }
    }
  }

  doStartSearch(e: any) {
    this.related = this.relatedx;
    this.related = this.related.filter((obj: any) => (obj[this.field_parents.get[0]] + obj[this.field_parents.get[1]] + obj[this.field_parents.get[2]]).toLowerCase().indexOf(e.toLowerCase()) > -1);
    if (this.related.length === 0 && this.scan_) {
      this.parent.filter = e !== "" ? () => {
        [{
          key: this.parent.match[0].value,
          op: "eq",
          value: e
        }]
      }
        : [];
      this.get_parent(this.parent);
    }
  }

  doSetRelated(item_: any) {
    for (let k = 0; k < this.field_parents.match.length; k++) {
      if (this.field_parents.match[k].key) {
        this.data_[this.field_parents.match[k].key] = item_[this.field_parents.match[k].value];
      }
      if (k === this.field_parents.match.length - 1) {
        this.tab = "data";
      }
    }
  }

  doTextManipulate(event: any, field: any) {
    const val_ = event.detail.value;
    if (field?.caseType === "lowercase") {
      this.data_[field.name] = val_.toLowerCase();
    } else if (field?.caseType === "uppercase") {
      this.data_[field.name] = val_.toUpperCase();
    } else if (field?.caseType === "capitalize") {
      this.data_[field.name] = val_.charAt(0).toUpperCase() + val_.slice(1)
    }
  }

  doDateAssign(event: any, fn: string) {
    const date_ = this.misc.getFormattedDate(event.detail.value);
    this.data_[fn] = date_;
    this.crudForm.get(fn)?.setValue(date_);
  }

  doInitDate(fn: string) {
    const date_ = this.misc.getFormattedDate(null);
    this.data_[fn] = date_;
    this.crudForm.get(fn)?.setValue(date_);
  }

  field_nulla(fn_: string) {
    this.data_[fn_] = null;
    this.crudForm.get(fn_)?.setValue(null);
  }

  filter_pipe_nulls(items_: any) {
    return items_.filter((item_: any) => item_ !== null);
  }

  unlock_field(fn_: string, index_: number) {
    this.crudForm.get(fn_)?.enable();
    this.fieldsupd[index_].permanent = false;
  }

}
