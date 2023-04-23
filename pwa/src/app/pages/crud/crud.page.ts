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

@Component({
  selector: "app-crud",
  templateUrl: "./crud.page.html",
  styleUrls: ["./crud.page.scss"],
})
export class CrudPage implements OnInit {
  @Input() shuttle: any = {};
  @Input() modified: boolean = false;
  @ViewChild("barcodefocus", { static: false }) barcodefocus: any;
  public crudForm: FormGroup;

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
  public dataprev: any = {};
  public filterops: any = environment.filterops;
  public pivotvalueops: any = environment.pivotvalueops;
  public loadingText: string = environment.misc.loadingText;
  public timeout: number = environment.misc.default_delay;
  public selected_: any = [];
  public fieldsupd: any = [];
  public fields: any = [];
  public isInProgress: boolean = false;
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
  public barcoded_: boolean = false;
  public istrue_: boolean = true;
  public visible: string = "hide";
  public parent: any = {};
  public aktions: any = [];
  public properties_: any = {};
  private sweeped: any;
  private filter: any = [];
  private file: any = null;
  private relatedx: any = []
  private collections: any = [];
  private views: any = [];
  private view: any = null;
  private structure__: any = {};

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

  ngOnDestroy() {
    this.storage.remove("LSOP").then(() => { });
  }

  ngOnInit() {
    this.modified = false;
    this.collection = this.shuttle.collection;
    this.user = this.shuttle.user;
    this.op = this.shuttle.op;
    this.dataprev = this.shuttle.data;
    this.structure__ = this.shuttle.structure;
    this.properties_ = this.shuttle.structure.properties;
    this.sweeped = this.shuttle.sweeped;
    this.filter = this.shuttle.filter;
    this.collections = this.shuttle.collections;
    this.views = this.shuttle.views;
    this.actionix = this.shuttle.actionix;
    this.view = this.shuttle.view;
    this.barcoded_ = this.shuttle.barcoded;

    this.parents = this.structure__?.parents ? this.structure__.parents : [];
    this.doGetAllAktions(this.op).then((res: any) => {
      this.aktions = res;
      this.crud.initForm(this.op, this.structure__, this.crudForm, this.shuttle.data, this.collections, this.views).then((res: any) => {
        this.tab = "data";
        this.crudForm = res.form;
        this.fields = res.fields;
        this.fieldsupd = this.op === "insert" && this.collection === "_collection" ? res.fields.filter((obj: any) => obj.name !== "col_structure") : res.fields;
        this.data_ = this.shuttle.data ? this.shuttle.data : res.init;
        this._id = this.op === "update" ? this.shuttle.data && this.shuttle.data._id ? this.shuttle.data._id : null : null;
        this.doGetSubProperties(this.collection).then(() => {
          if (this.actionix >= 0) {
            this.doAktionChange(this.actionix).then(() => { }).catch((error: any) => {
              this.misc.doMessage(error, "error");
            });
          }
        }).catch((error: any) => {
          this.misc.doMessage(error, "error");
        }).finally(() => {
          this.visible = "show";
          this.barcoded_ ? setTimeout(() => { this.barcodefocus.setFocus(); }, this.timeout) : null;
        });
      }).catch((error: any) => {
        this.misc.doMessage(error, "error");
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
                  action_.set[f].value === "$CURRENT_DATE" ? action_.set[f].value = new Date(Date.now() - ((new Date()).getTimezoneOffset() * 60000)).toISOString().substring(0, 19) : null;
                  this.data_[action_.set[f].key] = action_.set[f].value;
                  this.crudForm.get(action_.set[f].key)?.setValue(action_.set[f].value);
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

  doSubmit() {
    if (!this.isInProgress) {
      if (!["remove", "action"].includes(this.op) && !this.crudForm.valid) {
        this.misc.doMessage("form is not valid", "error");
      } else {
        this.modified = true;
        this.isInProgress = true;
        this.crud.Submit(this.collection, this.structure__, this.crudForm, this._id, this.op, this.file, this.sweeped, this.filter, this.view, this.actionix).then((res: any) => {
          this.crud.modalSubmitListener.next({ "result": true });
          if (this.barcoded_) {
            console.log("*** barcode is staying alive");
          } else {
            this.doDismissModal({ op: this.op, modified: this.modified, filter: [], cid: res && res.cid ? res.cid : null, res: res });
          }
        }).catch((res: any) => {
          this.misc.doMessage(res, "error");
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
      "id": this.data_.bak_id,
      "type": this.data_.bak_type
    }).then(() => {
      this.misc.doMessage(op_ + " completed successfully", "success");
      this.doDismissModal({ op: op_, modified: this.modified, filter: [] });
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
      "id": this.data_.bak_id,
      "type": this.data_.bak_type
    }).then(() => {
      this.doDismissModal({ op: this.op, modified: this.modified, filter: [] });
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

  doDismissModal(obj: any) {
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

  doGetSubProperties(coll_: string) {
    return new Promise((resolve, reject) => {
      this.misc.apiCall("crud", {
        op: "read",
        collection: "_collection",
        projection: null,
        match: [{
          key: "col_id",
          op: "eq",
          value: coll_ === "_collection" ? this.data_["col_id"] : coll_ === "_permission" ? this.data_["per_collection_id"] : coll_ === "_action" ? this.data_["act_collection_id"] : coll_ === "_action" ? this.data_["act_collection_id"] : coll_
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

  doChangeEnum(field_: any, coll_: any) {
    if (field_.collection) {
      this.doGetSubProperties(coll_).then((props_: any) => {
        this.property_list = props_;
      }).catch((res: any) => {
        this.misc.doMessage(res, "error");
      });
    }
  }

  doParent(parent_: any) {
    this.parent = parent_;
    let projection_: any = {};
    this.relact = true;
    this.tab = "relation";
    let filter_ = this.parent.filter ? this.parent.filter : [];
    let matchkeys_: any = [];
    this.parent.match.forEach((m: any) => matchkeys_.push(m.key));
    if (this.parent.get && this.parent.get.length > 0) {
      this.reloading = true;
      for (let p = 0; p < this.parent.get.length; p++) {
        projection_[this.parent.get[p]] = 1;
        if (p === this.parent.get.length - 1) {
          this.related = [];
          this.misc.apiCall("crud", {
            op: "read",
            collection: this.parent.collection,
            projection: projection_,
            match: filter_,
            sort: null,
            page: 1,
            limit: 1000
          }).then((res: any) => {
            if (res && res.data) {
              this.related = res.data;
              for (let k = 0; k < this.related.length; k++) {
                this.related[k].selected = true;
                if (k === this.related.length - 1) {
                  this.relatedx = this.related = this.related.sort((a: any, b: any) => (a.selected ? -1 : 1));
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

  doSetRelated(item_: any) {
    for (let k = 0; k < this.field_parents.match.length; k++) {
      if (this.field_parents.match[k].key) {
        this.data_[this.field_parents.match[k].key] = item_[this.field_parents.match[k].value];
        this.crudForm.get(this.field_parents.match[k].key)?.setValue(item_[this.field_parents.match[k].value]);
      }
      if (k === this.field_parents.match.length - 1) {
        this.tab = "data";
      }
    }
  }

  doStartSearch(e: any) {
    this.related = this.relatedx;
    this.related = this.related.filter((obj: any) => (obj[this.field_parents.get[0]] + obj[this.field_parents.get[1]] + obj[this.field_parents.get[2]]).toLowerCase().indexOf(e.toLowerCase()) > -1);
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
    this.data_[fn] = date_;
    this.crudForm.get(fn)?.setValue(date_);
  }

  doInitDate(fn: string) {
    const date_ = this.misc.getFormattedDate(null);
    this.data_[fn] = date_;
    this.crudForm.get(fn)?.setValue(date_);
  }

  doCancelDate(fn: string) {
    this.data_[fn] = null;
    this.crudForm.get(fn)?.setValue(null);
  }

}
