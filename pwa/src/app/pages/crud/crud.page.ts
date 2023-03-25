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
import { FormBuilder, FormGroup } from "@angular/forms";
import { AlertController } from "@ionic/angular";
import { Storage } from "@ionic/storage";
import { Miscellaneous } from "../../classes/misc";
import { Crud } from "./../../classes/crud";
import { environment } from "./../../../environments/environment";
import { JsonEditorComponent, JsonEditorOptions } from "ang-jsoneditor";
import { ItemReorderEventDetail } from '@ionic/core';

@Component({
  selector: "app-crud",
  templateUrl: "./crud.page.html",
  styleUrls: ["./crud.page.scss"],
})
export class CrudPage implements OnInit {
  @Input() shuttle: any = {};
  @Input() modified: boolean = false;
  @ViewChild(JsonEditorComponent, { static: false }) public editor?: JsonEditorComponent;
  @ViewChild("barcodefocus", { static: false }) barcodefocus: any;
  public novalue: any = null;
  public properties: any = {};
  public required: any = [];
  public property_list: any = [];
  public data_properties: any = [];
  public tab: string = "data";
  public op: string = "";
  public saved_filter: string = "";
  public saved_filters: any = [];
  public collection: string = "";
  public user: any;
  public data: any = {};
  public dataprev: any = {};
  public filterops: any = environment.filterops;
  public pivotvalueops: any = environment.pivotvalueops;
  public loadingText: string = environment.misc.loadingText;
  public timeout: number = environment.misc.default_delay;
  public selected_: any = [];
  public crudForm: FormGroup;
  public fieldsupd: any = [];
  public fields: any = [];
  public isInProgress: boolean = false;
  public is_ready: boolean = false;
  public _id: string = "";
  public arrayitem: any = {};
  public error: string = "";
  public options?: JsonEditorOptions;
  public arrays: any = [];
  public parentkey: number = 0;
  public aktions: any = [];
  public localfield: string = "";
  public parents: any;
  public relact: boolean = false;
  public reloading: boolean = false;
  public related: any = [];
  public actionix: number = -1;
  public is_token_copied: boolean = false;
  public barcoded_: boolean = false;
  public istrue_: boolean = true;
  public visible: string = "hide";
  public filters: any = [{
    key: null,
    op: null,
    value: null
  }];
  private structure: any = {};
  private sweeped: any;
  private filter: any = [];
  private file: any = null;
  private relatedx: any = []
  private collections: any = [];
  private views: any = [];
  private view: any = null;

  @HostListener("document:keydown", ["$event"]) loginWithEnter(event: any) {
    if (event.key === "Enter") {
      if (event.target.getAttribute("name") === "arrayitem") {
        this.doAddItemToArray(event).then(() => {
        }).catch((error: any) => {
          this.misc.doMessage(error, "error");
        });
      }
    }
  }

  constructor(
    private formBuilder: FormBuilder,
    public misc: Miscellaneous,
    private storage: Storage,
    private crud: Crud,
    private alert: AlertController
  ) {
    this.crudForm = this.formBuilder.group({}, {});
  }

  ngOnInit() {
    this.modified = false;
    this.collection = this.shuttle.collection ? this.shuttle.collection : null;
    this.user = this.shuttle.user;
    this.op = this.shuttle.op;
    this.dataprev = this.shuttle.data;
    this.structure = this.shuttle.structure;
    this.sweeped = this.shuttle.sweeped;
    this.filter = this.shuttle.filter;
    this.collections = this.shuttle.collections;
    this.views = this.shuttle.views;
    this.actionix = this.shuttle.actionix;
    this.view = this.shuttle.view;
    this.barcoded_ = this.shuttle.barcoded;
    this.properties = this.structure.properties;
    this.options = new JsonEditorOptions();
    this.options.modes = ["code", "tree"];
    this.options.mode = "code";
    this.options.statusBar = true;
    this.doGetAllAktions(this.op).then((res: any) => {
      this.aktions = res;
      this.doGetFilters().then(() => {
        this.doInitForm();
      }).catch((error: any) => {
        this.misc.doMessage(error, "error");
      });
    });
  }

  doInitForm() {
    this.crud.initForm(this.op, this.structure, this.crudForm, this.shuttle.data, this.collections, this.views).then((res: any) => {
      this.tab = "data";
      this.visible = this.op === "action" ? "hide" : "show";
      this.crudForm = res.form;
      this.fields = res.fields;
      this.fieldsupd = this.op === "insert" && this.collection === "_collection" ? this.fields.filter((obj: any) => obj.name !== "col_structure") : res.fields;
      this.data = this.shuttle.data ? this.shuttle.data : res.init;
      this._id = this.op === "update" ? this.shuttle.data && this.shuttle.data._id ? this.shuttle.data._id : null : null;
      this.doGetProperties().then(() => {
        if (this.actionix >= 0) {
          this.doAktionChange(this.actionix).then(() => { }).catch((error: any) => {
            this.misc.doMessage(error, "error");
          });
        }
      }).catch((error: any) => {
        this.misc.doMessage(error, "error");
      }).finally(() => {
        setTimeout(() => { this.visible = "show"; }, this.timeout);
        this.barcoded_ ? setTimeout(() => { this.barcodefocus.setFocus(); }, this.timeout) : null;
      });
    }).catch((error: any) => {
      this.misc.doMessage(error, "error");
    });
  }

  doGetAllAktions(op: string) {
    return new Promise((resolve, reject) => {
      if (op !== "action") {
        resolve([]);
      } else {
        resolve(this.shuttle.actions && this.shuttle.actions.length > 0 ? this.shuttle.actions : []);
      }
    });
  }

  async propertiesAktionFilter(v: any) {
    return Object.entries(this.properties).filter((obj: any) => v.set.some((f: any) => obj[0] === f.key));
  }

  doAktionChange(ix: number) {
    return new Promise((resolve) => {
      const v = this.aktions[ix];
      let structure_: any = this.structure;
      let controls_: any = {};
      let fields_: any = {};
      this.fieldsupd = this.fields.filter((obj: any) => v.set.some((f: any) => obj.name === f.key));
      this.propertiesAktionFilter(v).then((properties_filter_: any) => {
        for (let j = 0; j < properties_filter_.length; j++) {
          fields_[properties_filter_[j][0]] = properties_filter_[j][1];
          if (j === properties_filter_.length - 1) {
            structure_.properties = fields_;
            structure_.required = structure_.required ? structure_.required.filter((obj: any) => v.set.some((f: any) => obj.name === f.key)) : [];
            const form_ctrl_filter_ = Object.entries(this.crudForm.controls).filter((obj: any) => v.set.some((f: any) => obj[0] === f.key));
            for (let k = 0; k < form_ctrl_filter_.length; k++) {
              controls_[form_ctrl_filter_[k][0]] = form_ctrl_filter_[k][1];
              if (k === form_ctrl_filter_.length - 1) {
                for (let f = 0; f < v.set.length; f++) {
                  v.set[f].value === "$CURRENT_DATE" ? v.set[f].value = new Date(Date.now() - ((new Date()).getTimezoneOffset() * 60000)).toISOString().substring(0, 19) : null;
                  this.data[v.set[f].key] = v.set[f].value;
                  this.crudForm.get(v.set[f].key)?.setValue(v.set[f].value);
                  if (f === v.set.length - 1) {
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

  ngOnDestroy() {
    this.storage.remove("LSOP").then(() => { });
  }

  doSubmit() {
    this.error = "";
    if (!this.isInProgress) {
      if (this.op !== "remove" && !this.crudForm.valid) {
        this.misc.doMessage("form is not valid", "error");
      } else {
        this.modified = true;
        this.isInProgress = true;
        this.crud.Submit(this.collection, this.structure, this.crudForm, this._id, this.op, this.file, this.sweeped, this.filter, this.view).then((res: any) => {
          this.crud.modalSubmitListener.next({ "result": true });
          if (!this.barcoded_ || this.op !== "insert") {
            setTimeout(() => {
              this.doDismissModal({ op: this.op, modified: this.modified, filter: [], cid: res && res.cid ? res.cid : null, res: res });
            }, this.timeout);
          } else {
            this.doInitForm();
          }
        }).catch((error: any) => {
          this.misc.doMessage(error, "error");
        }).finally(() => {
          this.isInProgress = false;
        });
      }
    }
  }

  doDump(op_: string) {
    this.modified = true;
    this.isInProgress = true;
    this.misc.apiCall("crud", {
      "op": op_,
      "id": this.data.bak_id,
      "type": this.data.bak_type
    }).then(() => {
      this.misc.doMessage(op_ + " completed successfully", "success");
      setTimeout(() => {
        this.doDismissModal({ op: op_, modified: this.modified, filter: [] });
      }, this.timeout);
    }).catch((error: any) => {
      this.misc.doMessage(error, "error");
    }).finally(() => {
      this.isInProgress = false;
    });
  }

  doDownload() {
    this.modified = true;
    this.isInProgress = true;
    this.crud.Download({
      "id": this.data.bak_id,
      "type": this.data.bak_type
    }).then(() => {
      setTimeout(() => {
        this.doDismissModal({ op: this.op, modified: this.modified, filter: [] });
      }, this.timeout);
    }).catch((error: any) => {
      this.misc.doMessage(error, "error");
    }).finally(() => {
      this.isInProgress = false;
    });
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
            this.doSubmit();
          }
        }
      ]
    });
    alert.style.cssText = "--backdrop-opacity: 0 !important; z-index: 99999 !important; box-shadow: none !important;";
    await alert.present();
  }

  doRunFilter() {
    setTimeout(() => {
      this.doDismissModal({ modified: false, filters: this.filters && this.filters.length > 0 ? this.filters : null });
    }, this.timeout);
  }

  doDeleteItemFromArray(name: any, item: any) {
    this.data[name] = this.data[name].filter((e: any) => e !== item);
    this.crudForm.controls[name].setValue(this.data[name]);
  }

  doAddItemToArray(event: any) {
    return new Promise((resolve, reject) => {
      const field_ = this.fields.filter((obj: any) => obj.name === event.target.getAttribute("title"));
      const maxItems = field_[0] && field_[0].maxItems ? field_[0].maxItems : 32;
      const chipEl = document.createElement("ion-chip");
      chipEl.slot = "start";
      chipEl.outline = true;
      !this.data[event.target.getAttribute("title")] ? this.data[event.target.getAttribute("title")] = [] : null;
      if (event.target.value && this.data[event.target.getAttribute("title")].length < maxItems) {
        this.data[event.target.getAttribute("title")] ? null : this.data[event.target.getAttribute("title")] = [];
        this.data[event.target.getAttribute("title")].push(event.target.getAttribute("type") === "number" ? Number(event.target.value) : event.target.value);
        this.arrayitem[event.target.getAttribute("title")] = null;
        this.crudForm.controls[event.target.getAttribute("title")].setValue(this.data[event.target.getAttribute("title")]);
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
    this.data[this.parents.lookup[0].local] = [];
    for (let k = 0; k < this.related.length; k++) {
      if (this.related[k].selected) {
        this.data[this.parents.lookup[0].local].push(this.related[k][this.parents.lookup[0].remote]);
      }
      if (k === this.related.length - 1) {
        this.crudForm.get(this.parents.lookup[0].local)?.setValue(this.data[this.parents.lookup[0].local]);
      }
    }
  }

  doJsonChangeLog(event: any) {
    event ? null : null;
  }

  doAfterError() {
    this.storage.get("LSOP").then((LSOP: string) => { }).catch((error: any) => {
      this.misc.doMessage(error, "error");
    });
  }

  doDismissModal(obj: any) {
    this.misc.dismissModal(obj ? obj : { modified: false, filter: [] }).then(() => { }).catch((error: any) => {
      this.misc.doMessage(error, "error");
    });
  }

  onFileChange(ev: any) {
    const file: any = ev.target.files[0];
    if (file) {
      this.file = file;
      this.data["sto_file_name"] = file.name;
      this.data["sto_file_size"] = file.size;
    } else {
      this.file = null;
    }
  }

  doGetProperties() {
    return new Promise((resolve, reject) => {
      this.property_list = [];
      let i = 0;
      for (let property in this.properties) {
        const key = property;
        const val = this.properties[property].title;
        if (i < Object.keys(this.properties).length - 1) {
          this.property_list.push({ key: key, value: val });
          i++;
        } else {
          this.property_list.push({ key: key, value: val });
          this.property_list.push({ key: "_upload_id", value: null });
          resolve(true);
        }
      };
    });
  }

  doGetFilters() {
    return new Promise((resolve, reject) => {
      if (this.op !== "filter") {
        resolve([]);
      } else {
        this.storage.get("LSFILTER_" + this.collection).then((LSFILTER_: any) => {
          LSFILTER_ && LSFILTER_.length > 0 ? this.filters = LSFILTER_ : null;
          this.storage.get("LSSAVEDFILTER").then((LSSAVEDFILTER: any) => {
            this.misc.apiCall("crud", {
              op: "read",
              collection: "_view",
              projection: null,
              match: [{
                key: "vie_collection_id",
                op: "eq",
                value: this.collection
              }],
              sort: null,
              page: 1,
              limit: 100
            }).then((res: any) => {
              this.saved_filters = res.data;
              const f = LSSAVEDFILTER ? res.data.filter((obj: any) => obj.vie_id === LSSAVEDFILTER) : [];
              f && f[0] ? this.filters = f[0].vie_filter : null;
              this.saved_filter = LSSAVEDFILTER ? LSSAVEDFILTER : null;
              let i = 0;
              for (let property in this.properties) {
                const key = property;
                const val = this.properties[property].title;
                if (i < Object.keys(this.properties).length - 1) {
                  this.property_list.push({ key: key, value: val });
                  i++;
                } else {
                  this.property_list.push({ key: key, value: val });
                  resolve(this.property_list);
                }
              }
            }).catch((error: any) => {
              this.misc.doMessage(error, "error");
            });
          });
        });
      }
    });
  }

  doTextAreaChanged(event: any) {
    const last_ = event.target.value.slice(-1);
    const n_ = event.target.value.split(" ");
    const lastw_ = n_[n_.length - 1];
  }

  doChangeFilter() {
    this.storage.set("LSSAVEDFILTER", this.saved_filter).then(() => {
      const f = this.saved_filters.filter((obj: any) => obj.vie_id === this.saved_filter);
      this.filters = f[0].vie_filter;
    });
  }

  doChangeEnum(field_: any, value_: any) {
    this.doGetProperties();
  }

  doRelated(f_: any) {
    this.reloading = true;
    this.relact = true;
    this.tab = "relation";
    this.parents = f_.parents;
    const collection_ = f_.parents.collection;
    let match_ = f_.parents.match ? f_.parents.match : [{
      "key": "_id",
      "op": "nnull",
      "value": null
    }];
    for (let m = 0; m < match_.length; m++) {
      f_.parents.match && f_.parents.match[m].lookup && this.crudForm.controls[f_.parents.match[m].lookup].value ? match_[m].value = this.crudForm.controls[f_.parents.match[m].lookup].value : null;
      if (m === match_.length - 1) {
        this.related = [];
        this.misc.apiCall("crud", {
          op: "read",
          collection: collection_,
          projection: null,
          match: match_,
          sort: null,
          page: 1,
          limit: 1000
        }).then((res: any) => {
          if (res && res.data) {
            this.related = res.data;
            for (let k = 0; k < this.related.length; k++) {
              if (this.data[f_.name]) {
                for (let b = 0; b < this.data[f_.name].length; b++) {
                  if (this.related[k][f_.parents.lookup[0].remote] === this.data[f_.name][b]) {
                    this.related[k].selected = true;
                  }
                }
              }
              if (k === this.related.length - 1) {
                this.relatedx = this.related = this.related.sort((a: any, b: any) => (a.selected ? -1 : 1));
                this.reloading = false;
              }
            }
          }
        }).catch((error: any) => {
          this.misc.doMessage(error, "error");
        });
      }
    }
  }

  doSetRelated(item: any) {
    if (this.properties[this.parents.lookup[0].local].bsonType != 'array') {
      for (let k = 0; k < this.parents.lookup.length; k++) {
        if (this.parents.lookup[k].local) {
          if (this.properties[this.parents.lookup[k].local].bsonType === "array") {
            !this.data[this.parents.lookup[k].local] || typeof this.data[this.parents.lookup[k].local] === "string" ? this.data[this.parents.lookup[k].local] = [] : null;
            if (!this.data[this.parents.lookup[k].local] || !this.data[this.parents.lookup[k].local].find((obj: any) => obj === item[this.parents.lookup[k].remote])) {
              this.data[this.parents.lookup[k].local].push(item[this.parents.lookup[k].remote]);
              this.crudForm.get(this.parents.lookup[k].local)?.setValue(this.data[this.parents.lookup[k].local]);
            }
          } else {
            this.data[this.parents.lookup[k].local] = item[this.parents.lookup[k].remote];
            this.crudForm.get(this.parents.lookup[k].local)?.setValue(item[this.parents.lookup[k].remote]);
          }
        }
        if (k === this.parents.lookup.length - 1) {
          this.tab = "data";
        }
      }
    }
  }

  doStartSearch(e: any) {
    this.related = this.relatedx;
    this.related = this.related.filter((obj: any) => (obj[this.parents.lookup[0].remote] + obj[this.parents.lookup[1]?.remote] + obj[this.parents.lookup[2]?.remote]).toLowerCase().indexOf(e.toLowerCase()) > -1);
  }

  doKvAdd(i: number, fn: string) {
    if (this.data[fn][i].key) {
      this.data[fn].push({
        key: null,
        value: null
      });
    }
  }

  doKvInit(fn: string) {
    this.data[fn].push({
      key: null,
      value: null
    });
  }

  doKvRemove(i: number, fn: string) {
    this.data[fn].splice(i, 1);
  }

  doReorder(ev: CustomEvent<ItemReorderEventDetail>, fn: string) {
    this.data[fn] = ev.detail.complete(this.data[fn]);
    this.crudForm.get(fn)?.setValue(this.data[fn]);
  }

  doFieldReset(fn: string) {
    this.crudForm.get(fn)?.setValue(null);
    this.data[fn] = null;
  }

  doCopyToken() {
    this.is_token_copied = true;
    this.misc.copyToClipboard(btoa(this._id)).then(() => { }).catch((error: any) => {
      this.misc.doMessage("not copied", "error");
    }).finally(() => {
      this.is_token_copied = false;
    });
  }

  doDateAssign(event: any, fn: string) {
    const date_ = this.misc.getFormattedDate(event.detail.value);
    this.data[fn] = date_;
    this.crudForm.get(fn)?.setValue(date_);
  }

  doInitDate(fn: string) {
    const date_ = this.misc.getFormattedDate(null);
    this.data[fn] = date_;
    this.crudForm.get(fn)?.setValue(date_);
  }

  doCancelDate(fn: string) {
    this.data[fn] = null;
    this.crudForm.get(fn)?.setValue(null);
  }

}
