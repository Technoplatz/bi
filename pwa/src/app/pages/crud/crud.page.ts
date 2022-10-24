import { Component, OnInit, HostListener, Input, ViewChild, ChangeDetectorRef } from "@angular/core";
import { FormBuilder, FormGroup } from "@angular/forms";
import { AlertController } from "@ionic/angular";
import { Storage } from "@ionic/storage";
import { Miscellaneous } from "./../../classes/miscellaneous";
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
  @ViewChild(JsonEditorComponent, { static: false }) public editor: JsonEditorComponent;
  public novalue: any = null;
  public properties: any = {};
  public required: any = [];
  public property_list: any = [];
  public data_properties: any = [];
  public tab: string = "data";
  public op: string;
  public saved_filter: string;
  public saved_filters: any = [];
  public collection: string;
  public user: any;
  public data: any = {};
  public dataprev: any = {};
  public filterops: any = environment.filterops;
  public pivotvalueops: any = environment.pivotvalueops;
  public loadingText: string = environment.misc.loadingText;
  public selected_: any = [];
  public crudForm: FormGroup;
  public fieldsupd: any = [];
  public fields: any = [];
  public isInProgress: boolean = false;
  public is_ready: boolean = false;
  public _id: string;
  public arrayitem: any = {};
  public error: string = null;
  public options: JsonEditorOptions;
  public arrays: any = [];
  public visibility: string = "ion-padding-start ion-padding-end ion-hide";
  public parentkey: number = 0;
  public aktions: any = [];
  public localfield: string = null;
  public showhide: string = "show-segment";
  public parents: any;
  public relact: boolean = false;
  public reloading: boolean = false;
  public related: any = [];
  public actionix: number = -1;
  public is_token_copied: boolean = false;
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
        this.doAddItemToArray(event).then((item: string) => {
        }).catch((error: any) => {
          console.error(error);
        });
      }
    }
  }

  constructor(
    private formBuilder: FormBuilder,
    public misc: Miscellaneous,
    private storage: Storage,
    private crud: Crud,
    private alert: AlertController,
    private cd: ChangeDetectorRef
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
    this.properties = this.structure.properties;
    this.doGetAllAktions(this.op).then((res: any) => {
      this.aktions = res;
      this.options = new JsonEditorOptions();
      this.options.modes = ["code", "tree"];
      this.options.mode = "code";
      this.options.statusBar = true;
      this.doGetFilters().then(() => {
        this.crud.initForm(this.op, this.structure, this.crudForm, this.shuttle.data, this.collections, this.views).then((res: any) => {
          this.crudForm = res.form;
          this.fields = res.fields;
          this.fieldsupd = res.fields;
          this.data = this.shuttle.data ? this.shuttle.data : res.init;
          this._id = this.op === "update" ? this.shuttle.data && this.shuttle.data._id ? this.shuttle.data._id : null : null;
          this.visibility = "ion-padding-start ion-padding-end";
          const view_ = this.collection === "_view" && this.data ? this.data.vie_id : null;
          this.doGetViewProperties(view_).then(() => {
            this.doGetCollectionProperties(this.collection).then(() => {
              this.tab = "data";
              this.showhide = this.op === "action" ? "hide-segment" : "show-segment";
              if (this.actionix >= 0) {
                this.doAktionChange(this.actionix).then(() => {
                  setTimeout(() => {
                    this.is_ready = true;
                    this.cd.detectChanges();
                  }, 500);
                }).catch((error: any) => {
                  console.error(error);
                  this.misc.doMessage(error, "error");
                  this.is_ready = true;
                });
              } else {
                setTimeout(() => {
                  this.is_ready = true;
                  this.cd.detectChanges();
                }, 500);
              }
            }).catch((error: any) => {
              console.error(error);
              this.misc.doMessage(error, "error");
              this.is_ready = true;
            });
          }).catch((error: any) => {
            console.error(error);
            this.misc.doMessage(error, "error");
            this.is_ready = true;
          });
        }).catch((error: any) => {
          console.error(error);
          this.misc.doMessage(error, "error");
          this.is_ready = true;
        });
      }).catch((error: any) => {
        console.error(error);
        this.misc.doMessage(error, "error");
        this.is_ready = true;
      });
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
    return Object.entries(this.properties).filter((obj: any) => v.fields.some((f: any) => obj[0] === f.key));
  }

  doAktionChange(ix: number) {
    return new Promise((resolve, reject) => {
      const v = this.aktions[ix];
      let structure_ = this.structure;
      let controls_ = {};
      let fields_ = {};
      this.fieldsupd = this.fields.filter((obj: any) => v.fields.some((f: any) => obj.name === f.key));
      this.propertiesAktionFilter(v).then((properties_filter_: any) => {
        for (let j = 0; j < properties_filter_.length; j++) {
          fields_[properties_filter_[j][0]] = properties_filter_[j][1];
          if (j === properties_filter_.length - 1) {
            structure_.properties = fields_;
            structure_.required = structure_.required ? structure_.required.filter((obj: any) => v.fields.some((f: any) => obj.name === f.key)) : [];
            const form_ctrl_filter_ = Object.entries(this.crudForm.controls).filter((obj: any) => v.fields.some((f: any) => obj[0] === f.key));
            for (let k = 0; k < form_ctrl_filter_.length; k++) {
              controls_[form_ctrl_filter_[k][0]] = form_ctrl_filter_[k][1];
              if (k === form_ctrl_filter_.length - 1) {
                for (let f = 0; f < v.fields.length; f++) {
                  v.fields[f].value === "$CURRENT_DATE" ? v.fields[f].value = new Date(Date.now() - ((new Date()).getTimezoneOffset() * 60000)).toISOString().substring(0, 10) : null;
                  this.data[v.fields[f].key] = v.fields[f].value;
                  this.crudForm.get(v.fields[f].key).setValue(v.fields[f].value);
                  if (f === v.fields.length - 1) {
                    this.crudForm.controls = controls_;
                    this.showhide = "show-segment";
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
    this.storage.remove("LSOP").then(() => {
    });
  }

  doSubmit() {
    this.error = null;
    if (!this.isInProgress) {
      if (this.op !== "remove" && !this.crudForm.valid) {
        this.doShowError("form is not valid");
        this.misc.doMessage("form is not valid", "error");
      } else {
        this.modified = true;
        this.isInProgress = true;
        this.crud.Submit(this.collection, this.structure, this.crudForm, this._id, this.op, this.file, this.sweeped, this.filter, this.view).then(() => {
          setTimeout(() => {
            this.doCancel({ op: this.op, modified: this.modified, filter: [] });
          }, 500);
        }).catch((error: any) => {
          this.doShowError(error);
          console.error(error);
          this.misc.doMessage(error, "error");
        }).finally(() => {
          this.isInProgress = false;
        });
      }
    }
  }

  doDump() {
    this.error = null;
    this.modified = true;
    this.isInProgress = true;
    this.crud.Dump().then(() => {
      setTimeout(() => {
        this.doCancel({ op: this.op, modified: this.modified, filter: [] });
      }, 500);
    }).catch((error: any) => {
      this.doShowError(error);
      console.error(error);
    }).finally(() => {
      this.isInProgress = false;
    });
  }

  doDownload() {
    this.error = null;
    this.modified = true;
    this.isInProgress = true;
    this.crud.Download({
      "id": this.data.bak_id,
      "type": this.data.bak_type
    }).then(() => {
      setTimeout(() => {
        this.doCancel({ op: this.op, modified: this.modified, filter: [] });
      }, 500);
    }).catch((error: any) => {
      this.doShowError(error);
      console.error(error);
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
          text: "Cancel",
          role: "cancel",
          cssClass: "secondary",
          handler: () => { }
        }, {
          text: "Okay",
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
      this.doCancel({ modified: false, filters: this.filters && this.filters.length > 0 ? this.filters : null });
    }, 500);
  }

  doDeleteItemFromArray(name: any, item: any) {
    this.data[name] = this.data[name].filter((e: any) => e !== item);
    this.crudForm.controls[name].setValue(this.data[name]);
  }

  doAddItemToArray(event: any) {
    return new Promise((resolve, reject) => {
      const field_ = this.fields.filter((obj: any) => obj.name === event.target.getAttribute("title"));
      const minItems = field_[0] && field_[0].minItems ? field_[0].minItems : 0;
      const maxItems = field_[0] && field_[0].maxItems ? field_[0].maxItems : 32;
      const input = document.querySelector(".chips-input");
      const chipGroup = document.querySelector(".brz-visual-group");
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
        this.doShowError("maximum number of items exceeds");
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
        this.crudForm.get(this.parents.lookup[0].local).setValue(this.data[this.parents.lookup[0].local]);
      }
    }
  }

  doJsonChangeLog(event: any) {
    event ? null : null;
  }

  doAfterError() {
    this.storage.get("LSOP").then((LSOP: string) => { }).catch((error: any) => {
      console.error(error);
      this.misc.doMessage(error, "error");
    });
  }

  doCancel(obj: any) {
    this.misc.dismissModal(obj ? obj : { modified: false, filter: [] }).then(() => { }).catch((error: any) => {
      console.error(error);
      this.misc.doMessage(error, "error");
      this.doShowError(error);
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

  doGetViewProperties(view_: string) {
    return new Promise((resolve, reject) => {
      this.data_properties = [];
      if (!view_) {
        resolve(true);
      } else {
        this.crud.View(null, view_, "propsonly").then((res: any) => {
          if (res && res.properties) {
            let i = 0;
            for (let item in res.properties) {
              this.data_properties.push(item);
              if (i < Object.keys(res.properties).length - 1) {
                resolve(true);
              } else {
                i++;
              }
            }
          } else {
            reject("view properties not found");
          }
        }).catch((error: any) => {
          reject(error);
        });
      }
    });
  }

  doGetCollectionProperties(collection_: string) {
    return new Promise((resolve, reject) => {
      const cid_ = collection_ === "_action" ? this.data["act_collection_id"] : collection_ === "_field" ? this.data["fie_collection_id"] : collection_ === "_view" ? this.data["vie_collection_id"] : collection_;
      this.crud.Find("find", "_collection", null, [{
        key: "col_id",
        op: "eq",
        value: cid_
      }], null, 1, 1).then((res: any) => {
        const properties = res && res.data && res.data[0] && res.data[0].col_structure && res.data[0].col_structure.properties ? res.data[0].col_structure.properties : this.properties;
        this.property_list = [];
        let i = 0;
        for (let property in properties) {
          const key = property;
          const val = properties[property].title;
          if (i < Object.keys(properties).length - 1) {
            this.property_list.push({ key: key, value: val });
            i++;
          } else {
            this.property_list.push({ key: key, value: val });
            this.property_list.push({ key: "_id", value: null });
            resolve(true);
          }
        }
      }).catch((error: any) => {
        this.doShowError(error);
        console.error(error);
        reject(error);
      });
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
            this.crud.Find("find", "_view", null, [{
              key: "vie_collection_id",
              op: "eq",
              value: this.collection
            }], null, 1, 100).then((res: any) => {
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
              this.doShowError(error);
              console.error(error);
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
    if (field_.collection) {
      this.doGetCollectionProperties(value_);
    } else if (field_.view) {
      this.doGetViewProperties(value_);
    }
  }

  doShowError(error: any) {
    this.error = error;
    setTimeout(() => {
      this.error = null;
    }, 7000);
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
        this.crud.Find("find", collection_, null, match_, null, 1, 1000).then((res: any) => {
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
          this.doShowError(error);
          console.error(error);
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
              this.crudForm.get(this.parents.lookup[k].local).setValue(this.data[this.parents.lookup[k].local]);
            }
          } else {
            this.data[this.parents.lookup[k].local] = item[this.parents.lookup[k].remote];
            this.crudForm.get(this.parents.lookup[k].local).setValue(item[this.parents.lookup[k].remote]);
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
    this.crudForm.get(fn).setValue(this.data[fn]);
  }

  doFieldReset(fn: string) {
    this.crudForm.get(fn).setValue(null);
    this.data[fn] = null;
  }

  doCopyToken() {
    this.is_token_copied = true;
    this.misc.copyToClipboard(btoa(this._id)).then(() => { }).catch((error: any) => {
      console.error("not copied", error);
    }).finally(() => {
      this.is_token_copied = false;
    });
  }

}
