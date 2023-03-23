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
import { Auth } from "../../classes/auth";
import { Miscellaneous } from "../../classes/miscellaneous";
import { environment } from "../../../environments/environment";
import { CrudPage } from "../crud/crud.page";
import { JsonEditorOptions } from "ang-jsoneditor";

@Component({
  selector: "app-collection",
  templateUrl: "./collection.page.html",
  styleUrls: ["./collection.page.scss"]
})

export class CollectionPage implements OnInit {
  @ViewChild("select0") selectRef?: IonSelect;
  public defaultColumnWidth: number = environment.misc.defaultColumnWidth;
  public header: string = "Collections";
  public subheader: string = "";
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
  public structure: any = {};
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
  public collections: any = [];
  public is_initialized: boolean = false;
  public is_pane_ok: boolean = false;
  public barcoded_: boolean = false;
  public is_samecol: boolean = false;
  private view: any = null;
  public actions: any = [];
  public columns_: any;
  private menu_toggle: boolean = false;
  public view_mode: any = {};
  private sweeped: any = [];
  private sort: any = {};
  private properites_: any = {};
  private actionix: number = -1;
  private views_structure: any;
  private collections_structure: any;
  private menu: string = "";
  private page_end: number = 1;
  private clonok: number = -1;
  private collections_: any;
  private user_: any;
  public jeoptions?: JsonEditorOptions;
  public jeopen: boolean = false;
  public is_saving: boolean = false;
  public is_viewsaving: boolean = false;

  constructor(
    private storage: Storage,
    private auth: Auth,
    private crud: Crud,
    private modal: ModalController,
    private alert: AlertController,
    private router: Router,
    public misc: Miscellaneous
  ) {
    this.collections_ = this.crud.collections.subscribe((res: any) => {
      this.collections = res && res.data ? res.data : [];
      this.collections_structure = res.structure;
    });
    this.user_ = this.auth.user.subscribe((res: any) => {
      this.user = res;
      this.perm = res && res.perm ? true : false;
    });
  }

  ngOnDestroy() {
    this.collections_ = null;
    this.user_ = null;
  }

  ngOnInit() {
    this.menu = this.router.url.split("/")[1];
    this.id = this.submenu = this.router.url.split("/")[2];
    this.is_crud = this.id.charAt(0) === "_" ? false : true;
    this.jeoptions = new JsonEditorOptions();
    this.jeoptions.mode = "code";
    this.jeoptions.statusBar = true;
    this.crud.getCollection(this.id).then((res: any) => {
      this.header = this.is_crud ? "COLLECTIONS" : "ADMINISTRATION";
      this.subheader = res && res.data ? res.data.col_title : this.id;
      this.storage.set("LSID", this.id).then(() => {
        this.storage.get("LSFILTER_" + this.id).then((LSFILTER_: any) => {
          this.storage.get("LSSEARCHED_" + this.id).then((LSSEARCHED_: any) => {
            this.filter = LSFILTER_ && LSFILTER_.length > 0 ? LSFILTER_ : [];
            LSSEARCHED_ ? this.searched = LSSEARCHED_ : null;
            this.actions = [];
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
  }

  RefreshData(p: number) {
    return new Promise((resolve, reject) => {
      this.is_loaded = this.is_selected = false;
      this.storage.get("LSSEARCHED_" + this.id).then((LSSEARCHED_: any) => {
        this.searched = LSSEARCHED_ ? LSSEARCHED_ : null;
        this.storage.get("LSFILTER_" + this.id).then((LSFILTER_: any) => {
          this.filter = LSFILTER_ && LSFILTER_.length > 0 ? LSFILTER_ : [];
          this.count = 0;
          this.page = p === 0 ? 1 : p;
          this.misc.apiCall("crud", {
            op: "read",
            collection: this.id,
            projection: null,
            match: this.filter && this.filter.length > 0 ? this.filter : [],
            sort: this.sort,
            page: this.page,
            limit: this.limit
          }).then((res: any) => {
            this.data = res.data;
            this.reconfig = res.reconfig;
            this.structure = res.structure;
            this.actions = this.structure && this.structure.actions ? this.structure.actions : [];
            this.properites_ = res.structure && res.structure.properties ? res.structure.properties : null;
            this.columns_ = [];
            if (this.properites_) {
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
              this.searched === null ? this.doResetSearch(true) : this.doResetSearch(false);
              for (let p = 0; p < this.paget.length; p++) {
                this.paget[p] = this.page_start + p;
              }
              resolve(true);
            } else {
              console.error("*** no structure found");
            }
          }).catch((error: any) => {
            console.error(error);
            this.misc.doMessage(error, "error");
            reject(error);
          }).finally(() => {
            this.is_pane_ok = true;
            this.is_loaded = true;
            this.is_samecol = true;
          });
        });
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
      backdropDismiss: true,
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
        this.RefreshData(0).then(() => {
          ["_collection", "_view", "_backup"].includes(this.id) ? this.crud.getAll().then(() => {
            if (["remove", "restore"].includes(res.data.op)) {
              this.misc.navi.next("dashboard");
            }
          }).catch((error: any) => {
            console.error(error);
            this.misc.doMessage(error, "error");
          }) : null;
        });
      } else {
        if (res.data.filters && res.data.filters.length > 0) {
          this.storage.set("LSFILTER_" + this.id, res.data.filters).then(() => {
            this.filter = res.data.filters;
            this.RefreshData(0);
          });
        }
      }
    });
    return await modal.present();
  }

  doCollectionSettings() {
    if (this.perm && this.is_crud) {
      this.misc.apiCall("crud", {
        op: "read",
        collection: "_collection",
        projection: null,
        match: [{
          key: "col_id",
          op: "eq",
          value: this.id
        }],
        sort: null,
        page: 1,
        limit: 1
      }).then((res: any) => {
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
              this.crud.getAll().then(() => {
                if (res.data.op === "remove") {
                  this.misc.navi.next("dashboard");
                } else {
                  this.misc.navi.next("dashboard");
                }
              }).catch((error: any) => {
                console.error(error);
                this.misc.doMessage(error, "error");
              });
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
      this.is_viewsaving = true;
      this.misc.apiCall("crud", {
        op: "saveasview",
        collection: this.id,
        match: this.filter
      }).then((res: any) => {
        this.crud.getAll().then(() => {
          this.is_viewsaving = false;
          this.misc.navi.next("view/" + res.id);
        });
      }).catch((error: any) => {
        this.is_viewsaving = false;
        this.misc.doMessage("filter not saved", "error");
        console.error(error);
      });
    } else {
      console.error("*** you must apply a filter prior to save");
      this.misc.doMessage("you must apply a filter prior to save", "error");
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
    this.storage.set("LSFILTER_" + this.id, this.filter).then(() => {
      for (let key_ in this.structure.properties) {
        this.searched[key_] = full ? { actived: false, kw: null, f: false, op: "eq", setmode: false } : { actived: false, kw: this.searched[key_] && this.searched[key_].kw ? this.searched[key_].kw : null, f: this.searched[key_] && this.searched[key_].f ? this.searched[key_].f : null, op: this.searched[key_] && this.searched[key_].op ? this.searched[key_].op : null, setmode: this.searched[key_] && this.searched[key_].setmode ? this.searched[key_].setmode : null };
      }
    });
  }

  doClearFilter() {
    this.filter = [];
    this.storage.set("LSSFILTER_" + this.id, this.filter).then(() => {
      this.storage.set("LSSEARCHED_" + this.id, null).then(() => {
        this.storage.set("LSSAVEDFILTER", "").then(() => {
          this.doResetSearch(true);
          this.searched = {};
          this.RefreshData(0);
        });
      });
    });
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
      this.misc.navi.next("admin/_field");
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

  doShowCode() {
    this.jeopen = !this.jeopen;
  }

  doSaveCode() {
    if (this.perm) {
      this.is_saving = true;
      this.misc.apiCall("/crud", {
        op: "savecode",
        collection: this.id,
        structure: this.structure
      }).then(() => {
        window.location.reload();
      }).catch((error: any) => {
        console.error(error);
        this.misc.doMessage(error, "error");
      }).finally(() => {
        this.is_saving = false;
      });
    }
  }

  doImport() {
    this.misc.doImport(this.id).then(() => {
      this.RefreshData(0).then(() => { });
    });
  }

}
