/*
Technoplatz BI

Copyright (C) 2019-2023 Technoplatz IT Solutions GmbH, Mustafa Mat

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General private License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General private License for more details.

You should have received a copy of the GNU Affero General private License
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

import { Component, OnInit, ViewChild } from "@angular/core";
import { ModalController, AlertController, IonSelect, NavController } from "@ionic/angular";
import { Router } from "@angular/router";
import { Storage } from "@ionic/storage";
import { Crud } from "../../classes/crud";
import { Miscellaneous } from "../../classes/miscellaneous";
import { environment } from "../../../environments/environment";
import { CrudPage } from "../crud/crud.page";
import { JsonEditorComponent, JsonEditorOptions } from "ang-jsoneditor";

@Component({
  selector: "app-collection",
  templateUrl: "./collection.page.html",
  styleUrls: ["./collection.page.scss"]
})

export class CollectionPage implements OnInit {
  @ViewChild(JsonEditorComponent, { static: false }) private strcutureEditor?: JsonEditorComponent;
  @ViewChild("select0") selectRef?: IonSelect;
  public header: string = "";
  public loadingText: string = environment.misc.loadingText;
  private submenu: string = "";
  private segment = "data";
  public user: any = null;
  public perm: boolean = false;
  public is_crud: boolean = false;
  public paget: any = [];
  public id: string = "";
  private template_showed: boolean = false;
  public reconfig: boolean = false;
  public filter: any = [];
  public searched: any = null;
  public data: any = [];
  private structure: any = [];
  public selected: any = [];
  private views: any = [];
  private viewsx: any = [];
  public pages: any = [];
  public limit: number = environment.misc.limit;
  public page: number = 1;
  private page_start: number = 1;
  public count: number = 0;
  public is_loaded: boolean = true;
  private is_selected: boolean = false;
  public multicheckbox: boolean = false;
  private master: any = {};
  private collections: any = [];
  private collections_: any = {};
  public is_initialized: boolean = false;
  public is_pane_ok: boolean = false;
  public barcoded_: boolean = false;
  public is_samecol: boolean = false;
  private view: any = null;
  public actions: any = [];
  public columns_: any;
  private menu_toggle: boolean = false;
  public view_mode: any = {};
  private options?: JsonEditorOptions;
  private sweeped: any = [];
  private sort: any = {};
  private properites_: any = {};
  private actionix: number = -1;
  private views_structure: any;
  private collections_structure: any;
  private menu: string = "";
  private saved_filter: string = "";
  private page_end: number = 1;
  private clonok: number = -1;
  private collectionso: any;
  private usero: any;

  constructor(
    private storage: Storage,
    private crud: Crud,
    private misc: Miscellaneous,
    private modal: ModalController,
    private alert: AlertController,
    private router: Router
  ) {
    this.collectionso = this.crud.collections.subscribe((res: any) => {
      this.collections = res && res.data ? res.data : [];
      this.collections_structure = res.structure;
      this.collections_ = {};
      for (let item_ in res.data) {
        this.collections_[res.data[item_].col_id] = true;
      }
    });
  }

  ngOnDestroy() {
    this.collectionso = null;
    this.usero = null;
  }

  ngOnInit() {
    this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
      this.user = LSUSERMETA;
      this.perm = LSUSERMETA && LSUSERMETA.perm ? true : false;
      this.menu = this.router.url.split("/")[1];
      this.id = this.submenu = this.router.url.split("/")[2];
      this.crud.getCollection(this.id).then((res: any) => {
        this.header = res && res.data ? res.data.col_title : this.id;
        this.storage.set("LSID", this.id).then(() => {
          this.is_crud = this.id.charAt(0) === "_" ? false : true;
          this.storage.get("LSFILTER_" + this.id).then((LSFILTER_: any) => {
            this.storage.get("LSSEARCHED_" + this.id).then((LSSEARCHED_: any) => {
              // this.filter = LSFILTER_ && LSFILTER_.length > 0 ? LSFILTER_ : [];
              LSSEARCHED_ ? this.searched = LSSEARCHED_ : null;
              this.actions = [];
              this.filter = [];
              this.RefreshData(0).then(() => { }).catch((error: any) => {
                console.error(error);
                this.misc.doMessage(error, "error");
              }).finally(() => {
                this.is_initialized = true;
              });
            });
          });
        });
      }).catch((error: any) => {
        console.error(error);
        this.misc.doMessage(error, "error");
      });
    });
  }

  getColumns() {
    return new Promise((resolve, reject) => {
      let p_ = 0;
      for (let [key, value] of Object.entries(this.properites_)) {
        this.properites_[key]["index"] = p_;
        if (p_ === Object.keys(this.properites_).length - 1) {
          resolve(true);
        } else {
          p_++;
        }
      }
    });
  }

  RefreshData(p: number) {
    return new Promise((resolve, reject) => {
      this.is_loaded = this.is_selected = false;
      this.storage.get("LSSEARCHED_" + this.id).then((LSSEARCHED_: any) => {
        this.storage.get("LSSAVEDFILTER").then((LSSAVEDFILTER: any) => {
          this.searched = LSSEARCHED_ ? LSSEARCHED_ : null;
          this.saved_filter = LSSAVEDFILTER ? LSSAVEDFILTER : null;
          this.storage.get("LSFILTER_" + this.id).then((LSFILTER_: any) => {
            this.filter = LSFILTER_ && LSFILTER_.length > 0 ? LSFILTER_ : [];
            this.count = 0;
            this.page = p === 0 ? 1 : p;
            this.crud.Find(
              "read",
              this.id,
              null,
              this.filter && this.filter.length > 0 ? this.filter : [],
              this.sort,
              this.page,
              this.limit).then((res: any) => {
                this.data = res.data;
                this.reconfig = res.reconfig;
                this.structure = res.structure;
                this.actions = this.structure && this.structure.actions ? this.structure.actions : [];
                this.properites_ = res.structure && res.structure.properties ? res.structure.properties : null;
                this.columns_ = [];
                if (this.properites_) {
                  this.getColumns().then(() => {
                    this.barcoded_ = true ? Object.keys(this.structure.properties).filter((key: any) => this.structure.properties[key].barcoded).length > 0 : false;
                    this.columns_ = Object.keys(this.structure.properties).filter((key: any) => !this.structure.properties[key].hidden).reduce((obj: any, key) => { obj[key] = this.structure.properties[key]; return obj; }, {});
                    this.count = res.count;
                    this.multicheckbox = false;
                    this.multicheckbox ? this.multicheckbox = false : null;
                    this.selected = new Array(res.data.length).fill(false);
                    this.pages = this.count > 0 ? Math.ceil(this.count / this.limit) : environment.misc.default_page;
                    const lmt = this.pages >= 10 ? 10 : this.pages;
                    this.paget = new Array(lmt);
                    this.page_start = this.page > 10 ? this.page - 10 + 1 : 1;
                    this.page_end = this.page_start + 10;
                    this.is_loaded = true;
                    this.is_samecol = true;
                    this.is_pane_ok = true;
                    this.searched === null ? this.doResetSearch(true) : this.doResetSearch(false);
                    for (let p = 0; p < this.paget.length; p++) {
                      this.paget[p] = this.page_start + p;
                    }
                    resolve(true);
                  });
                } else {
                  console.error("*** no structure found");
                  this.is_loaded = true;
                  this.is_samecol = true;
                }
              }).catch((error: any) => {
                console.error(error);
                this.misc.doMessage(error, "error");
                this.is_loaded = true;
                this.is_samecol = true;
                reject(error);
              });
          });
        });
      });
    });
  }

  doImport(type_: string) {
    const import_structure_ = environment.import_structure;
    const upload_structure_ = environment.upload_structure;
    this.modal.create({
      component: CrudPage,
      backdropDismiss: false,
      cssClass: "crud-modal",
      componentProps: {
        shuttle: {
          op: type_ === "import" ? "import" : "upload",
          collection: "_storage",
          collections: this.collections ? this.collections : [],
          views: this.views ? this.views : [],
          user: this.user,
          data: {
            "sto_id": type_ === "import" ? "data-import" : "data-upload",
            "sto_collection_id": this.id,
            "sto_prefix": type_ === "import" ? null : null,
            "sto_file": null
          },
          structure: type_ === "import" ? import_structure_ : upload_structure_,
          sweeped: [],
          filter: { "sto_collection_id": type_ === "import" ? this.id : null },
          actions: [],
          direct: -1
        }
      }
    }).then((modal: any) => {
      modal.present();
      modal.onDidDismiss().then((res: any) => {
        this.RefreshData(0);
      });
    });
  }

  doAction(ix: any) {
    if (this.perm) {
      this.actionix = ix;
      if (this.actions[ix] && this.actions[ix].filter && this.actions[ix].filter.length > 0 && (!this.sweeped[this.segment] || this.sweeped[this.segment].length === 0)) {
        this.storage.set("LSFILTER_" + this.id, this.actions[ix].filter).then(() => {
          this.filter = this.actions[ix].filter;
          this.RefreshData(0).then(() => {
            this.data && this.data.length > 0 ? this.goCrud(null, "action") : null;
          }).catch((error: any) => {
            console.error(error);
            this.misc.doMessage(error, "error");
          });
        }).catch((error: any) => {
          console.error(error);
          this.misc.doMessage(error, "error");
        });
      } else {
        this.goCrud(null, "action");
      }
    } else {
      console.error("no permission");
      this.misc.doMessage("no permission", "error");
    }
  }

  async Settings(collection_: any, op: string, data_: any, ix_: number) {
    if (!this.perm) {
      console.error("*** no permission");
    } else {
      const modal = await this.modal.create({
        component: CrudPage,
        backdropDismiss: false,
        cssClass: "crud-modal",
        componentProps: {
          shuttle: {
            op: op,
            collection: collection_,
            collections: this.collections ? this.collections : [],
            views: this.views ? this.views : [],
            user: this.user,
            data: data_,
            structure: collection_ === "_view" && this.views && this.views_structure ? this.views_structure : collection_ === "_collection" && this.collections_structure ? this.collections_structure : [],
            direct: -1
          }
        }
      });
      modal.onDidDismiss().then((res: any) => {
        if (res.data.modified) {
          this.crud.getAll().then(() => { }).catch((error: any) => {
            console.error(error);
            this.misc.doMessage(error, "error");
          });
        }
      });
      return await modal.present();
    }
  }

  MultiCrud(op: string) {
    if (this.data.length > 0 && this.is_selected) {
      if (op === "action") {
        if (this.structure && this.structure.actions && this.structure.actions.length > 0) {
          this.goCrud(null, op);
        } else {
          this.misc.doMessage("no action defined for the collection", "error");
        }
      } else {
        this.alert.create({
          header: "Confirm",
          message: "Please confirm this " + op,
          buttons: [
            {
              text: "Cancel",
              role: "cancel",
              cssClass: "secondary",
              handler: () => { }
            }, {
              text: "OKAY",
              handler: () => {
                this.is_loaded = this.is_selected = false;
                this.crud.MultiCrud(
                  op,
                  this.id,
                  this.sweeped[this.segment],
                  true).then(() => {
                    this.page = environment.misc.default_page;
                    this.RefreshData(0);
                  }).catch((error: any) => {
                    console.error(error);
                    this.misc.doMessage(error, "error");
                  }).finally(() => {
                    this.is_loaded = true;
                    this.is_samecol = true;
                  });
              }
            }
          ]
        }).then((alert: any) => {
          alert.style.cssText = "--backdrop-opacity: 0 !important; z-index: 99999 !important; box-shadow: none !important;";
          alert.present();
        });
      }
    } else {
      this.misc.doMessage("you must select record(s) prior to " + op, "error");
      console.error("*** you must select record(s) prior to update");
    }
  }

  async goCrud(rec: any, op: string) {
    const modal = await this.modal.create({
      component: CrudPage,
      backdropDismiss: false,
      cssClass: "crud-modal",
      componentProps: {
        shuttle: {
          op: op,
          collection: this.id,
          collections: this.collections ? this.collections : [],
          views: this.views ? this.views : [],
          user: this.user,
          data: rec,
          structure: this.structure,
          sweeped: this.sweeped[this.segment] && op === "action" ? this.sweeped[this.segment] : [],
          filter: op === "action" ? this.filter : null,
          actions: this.actions && this.actions.length > 0 ? this.actions : [],
          actionix: op === "action" && this.actionix >= 0 ? this.actionix : -1,
          view: this.view,
          barcoded: this.barcoded_
        }
      }
    });
    modal.onDidDismiss().then((res: any) => {
      if (res.data.modified) {
        this.crud.getAll().then(() => {
          this.RefreshData(0);
        }).catch((error: any) => {
          console.error(error);
          this.misc.doMessage(error, "error");
        });

      }
      if (res.data.filters) {
        this.storage.set("LSFILTER_" + this.id, res.data.filters).then(() => {
          this.filter = res.data.filters;
          this.RefreshData(0);
        });
      }
    });
    return await modal.present();
  }

  doCollectionSettings() {
    if (this.perm && this.is_crud) {
      this.crud.Find("read", "_collection", null, [{
        key: "col_id",
        op: "eq",
        value: this.id
      }], null, 1, 1).then((res: any) => {
        this.master = {
          collection: "_collection",
          structure: res.structure,
          data: res.data[0]
        }
        this.modal.create({
          component: CrudPage,
          backdropDismiss: false,
          cssClass: "crud-modal",
          componentProps: {
            shuttle: {
              op: "update",
              collection: this.master.collection,
              collections: this.collections ? this.collections : [],
              views: this.views ? this.views : [],
              user: this.user,
              data: this.master.data,
              structure: this.master.structure,
              direct: -1
            }
          }
        }).then((modal: any) => {
          modal.present();
          modal.onDidDismiss().then((res: any) => {
            if (res.data.modified) {
              this.RefreshData(0);
            } else {
              if (res.data.filters) {
                this.storage.set("LSFILTER_" + this.id, res.data.filters).then(() => {
                  this.filter = res.data.filters;
                  this.RefreshData(0);
                });
              }
            }
          });
        });
      }).catch((error: any) => {
        console.error(error);
        this.misc.doMessage(error, "error");
      });
    }
  }

  async GetIsSelectData() {
    this.sweeped[this.segment] = [];
    const q = await this.selected.findIndex((obj: boolean) => obj === true);
    this.clonok = q;
    q >= 0 ? (this.is_selected = true) : (this.is_selected = false);
    const r = await this.selected.reduce((acc: any, val: any, index: number) => {
      const q = val === true ? this.sweeped[this.segment].push(this.data[index]._id) : null;
    }, []);
  }

  doSaveAsView() {
    if (this.perm && this.data.length > 0 && this.is_crud) {
      this.crud.SaveAsView(this.id, this.filter).then((res: any) => {
        // goto view
      }).catch((error: any) => {
        this.misc.doMessage("filter not saved", "error");
        console.error(error);
      });
    } else {
      console.error("*** you must apply a filter prior to save");
      this.misc.doMessage("you must apply a filter prior to save", "error");
    }
  }

  doPurge() {
    if (this.perm && this.filter.length > 0 && this.data.length > 0 && this.is_crud) {
      this.alert.create({
        cssClass: "my-custom-class",
        header: "Delete ALL Filtered!",
        subHeader: "This operation will remove ALL data has been filtered. Lots of records can be affected. Please enter your OTP to approve this operation.",
        inputs: [
          {
            name: "id",
            value: null,
            type: "text",
            placeholder: "Enter your OTP"
          }
        ],
        buttons: [
          {
            text: "Cancel",
            role: "cancel",
            cssClass: "primary",
            handler: () => {
              console.warn("Confirm cancel");
            }
          }, {
            text: "OK",
            handler: (purgeData: any) => {
              this.crud.PurgeFiltered(this.id, purgeData && purgeData.id ? purgeData.id : null, this.filter).then((res: any) => {
                this.misc.doMessage("bulk delete completed successfully", "success");
                this.RefreshData(0);
              }).catch((error: any) => {
                this.misc.doMessage(error, "error");
                console.error(error);
              });
            }
          }
        ]
      }).then((alert: any) => {
        alert.present();
      });
    } else {
      console.error("*** you must apply a filter prior to purge");
      this.misc.doMessage("you must apply a filter prior to purge", "error");
    }
  }

  SwitchSelectData(event: any) {
    this.selected = new Array(this.data.length).fill(event);
    this.GetIsSelectData();
  }

  SetSelectData(i: number, event: any) {
    if (this.segment !== "_log" && this.segment !== "_backup") {
      this.selected[i] = event.detail.checked;
      this.GetIsSelectData();
    }
  }

  orderByIndex = (a: any, b: any): number => {
    return a.value.index < b.value.index ? -1 : (b.value.index > a.value.index ? 1 : 0);
  }

  setSort(key: string, d: number) {
    this.sort = {};
    this.sort[key] = d;
    this.RefreshData(0);
  }

  doSetSearch(k: string) {
    this.searched[k].setmode = false;
    let i = 0;
    for (let key_ in this.structure.properties) {
      k !== key_ ? this.searched[key_].actived = false : this.searched[key_].actived = !this.searched[key_].actived;
    }
  }

  doResetSearch(full: boolean) {
    full ? this.searched = {} : null;
    for (let key_ in this.structure.properties) {
      this.searched[key_] = full ? { actived: false, kw: null, f: false, op: "eq", setmode: false } : { actived: false, kw: this.searched[key_] && this.searched[key_].kw ? this.searched[key_].kw : null, f: this.searched[key_] && this.searched[key_].f ? this.searched[key_].f : null, op: this.searched[key_] && this.searched[key_].op ? this.searched[key_].op : null, setmode: this.searched[key_] && this.searched[key_].setmode ? this.searched[key_].setmode : null };
    }
  }

  doResetSearchItem(k: string) {
    const n_ = this.filter.length;
    this.searched[k].actived = false;
    for (let d = 0; d < n_; d++) {
      if (this.filter[d] && this.filter[d]["key"] === k) {
        this.filter.splice(d, 1);
        this.searched[k].f = false;
        this.searched[k].kw = null;
        this.searched[k].op = "eq";
        this.searched[k].setmode = false;
      }
      if (d === n_ - 1) {
        this.storage.set("LSFILTER_" + this.id, this.filter).then(() => {
          this.storage.set("LSSEARCHED_" + this.id, this.searched).then(() => {
            this.RefreshData(0);
          });
        });
      }
    }
  }

  doSearch(k: string, v: string) {
    this.searched[k].setmode = false;
    if (!this.filter || this.filter.length === 0) {
      if (v === "true" || v === "false") {
        this.filter.push({
          key: k,
          op: v,
          value: null
        });
      } else {
        this.filter.push({
          key: k,
          op: this.searched[k].op,
          value: v
        });
      }
      this.searched[k].f = true;
      this.storage.set("LSFILTER_" + this.id, this.filter).then(() => {
        this.storage.set("LSSEARCHED_" + this.id, this.searched).then(() => {
          this.RefreshData(0);
        });
      });
    } else {
      let found = false;
      const n_ = this.filter.length;
      for (let d = 0; d < n_; d++) {
        if (this.filter[d] && this.filter[d]["key"] === k) {
          found = true;
          this.filter[d]["op"] = this.searched[k].op;
          this.filter[d]["value"] = v;
        }
        if (d === n_ - 1) {
          !found ? this.filter.push({
            key: k,
            op: this.searched[k].op,
            value: v
          }) : null;
          this.searched[k].f = true;
          this.storage.set("LSFILTER_" + this.id, this.filter).then(() => {
            this.storage.set("LSSEARCHED_" + this.id, this.searched).then(() => {
              this.RefreshData(0);
            });
          });
        }
      }
    }
  }

  doSetSearchItemOp(k: string, op: string) {
    this.searched[k].op = op;
  }

  doMenuToggle() {
    this.menu_toggle = !this.menu_toggle;
  }

  goField(f_: string) {
    console.log("*** f_", this.id, f_);
  }

  goFields() {
    const id_ = "_field";
    this.storage.set("LSFILTER_" + id_, [{
      "key": "fie_collection_id",
      "op": "eq",
      "value": this.id
    }]).then(() => {
      // admin fields'e git
    });
  }

  doReconfigure() {
    if (this.perm) {
      this.crud.Reconfigure(this.id).then((res: any) => {
        if (res && res.result) {
          this.RefreshData(0);
          this.misc.doMessage("structure updated successfully", "success");
        } else {
          this.misc.doMessage("structure not updated", "error");
        }
      }).catch((error: any) => {
        console.error(error);
        this.misc.doMessage(error, "error");
      });
    }
  }

  doTemplateShow() {
    this.template_showed = !this.template_showed;
  }

  doStartSearch(e: any) {
    this.viewsx = this.views;
    this.viewsx = this.viewsx.filter((obj: any) => (obj["vie_id"] + obj["vie_title"]).toLowerCase().indexOf(e.toLowerCase()) > -1);
  }

}
