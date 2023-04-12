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
import { ModalController, AlertController } from "@ionic/angular";
import { Router } from "@angular/router";
import { Storage } from "@ionic/storage";
import { Crud } from "../../classes/crud";
import { Auth } from "../../classes/auth";
import { Miscellaneous } from "../../classes/misc";
import { environment } from "../../../environments/environment";
import { CrudPage } from "../crud/crud.page";
import { JsonEditorOptions, JsonEditorComponent } from "ang-jsoneditor";

@Component({
  selector: "app-collection",
  templateUrl: "./collection.page.html",
  styleUrls: ["./collection.page.scss"]
})

export class CollectionPage implements OnInit {
  @ViewChild(JsonEditorComponent, { static: false }) editor: JsonEditorComponent = new JsonEditorComponent;
  public jeoptions: JsonEditorOptions;
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
  public selected: any = [];
  private views: any = [];
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
  private view: any = null;
  public actions: any = [];
  public columns_: any;
  private menu_toggle: boolean = false;
  public view_mode: any = {};
  private sweeped: any = [];
  private properites_: any = {};
  private actionix: number = -1;
  private views_structure: any;
  private collections_structure: any;
  private menu: string = "";
  private page_end: number = 1;
  private clonok: number = -1;
  private collections_: any;
  private user_: any;
  public jeopen: boolean = false;
  public is_saving: boolean = false;
  public is_deleting: boolean = false;
  public is_viewsaving: boolean = false;
  public sort: any = {};
  public structure: any = {};
  public schemevis: any = "hide";
  private structure_: any = {};

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
    this.jeoptions = new JsonEditorOptions();
    this.jeoptions.modes = ["code", "tree"]
    this.jeoptions.mode = "tree";
    this.jeoptions.statusBar = true;
    this.jeoptions.enableSort = false;
    this.jeoptions.expandAll = false;
    this.jeoptions.navigationBar = true;
    this.jeoptions.name = "schema-structure";
  }

  ngOnDestroy() {
    this.collections_ = null;
    this.user_ = null;
  }

  ngOnInit() {
    this.menu = this.router.url.split("/")[1];
    this.id = this.submenu = this.router.url.split("/")[2];
    this.is_crud = this.id.charAt(0) === "_" ? false : true;
    this.crud.getCollection(this.id).then((res: any) => {
      this.header = this.is_crud ? "COLLECTIONS" : "ADMINISTRATION";
      this.subheader = res && res.data ? res.data.col_title : this.id;
      this.storage.get("LSFILTER_" + this.id).then((LSFILTER_: any) => {
        this.storage.get("LSSEARCHED_" + this.id).then((LSSEARCHED_: any) => {
          this.filter = LSFILTER_ && LSFILTER_.length > 0 ? LSFILTER_ : [];
          LSSEARCHED_ ? this.searched = LSSEARCHED_ : null;
          this.actions = [];
          this.RefreshData(0).then(() => { }).catch((error: any) => {
            this.misc.doMessage(error, "error");
          }).finally(() => {
            this.is_initialized = true;
          });
        });
      });
    }).catch((res: any) => {
      this.is_initialized = true;
      this.misc.doMessage(res.error.msg, "error");
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
            this.structure_ = res.structure;
            this.actions = this.structure.actions;
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
              this.misc.doMessage("no structure found", "error");
              resolve(true);
            }
          }).catch((error: any) => {
            this.misc.doMessage(error, "error");
            reject(error);
          }).finally(() => {
            this.is_pane_ok = true;
            this.is_loaded = true;
          });
        });
      });
    });
  }

  doAction(ix: any) {
    if (this.perm && this.data?.length > 0) {
      if (this.actions[ix]?.one_click || this.sweeped[this.segment]?.length > 0) {
        this.actionix = ix;
        this.goCrud(null, "action");
      } else {
        this.misc.doMessage("please make a selection to run this action", "error");
      }
    } else {
      this.misc.doMessage("no permission to run this action", "error");
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
          buttons: [{
            text: "Cancel",
            role: "cancel",
            cssClass: "secondary",
            handler: () => { }
          }, {
            text: "OKAY",
            handler: () => {
              this.is_deleting = true;
              this.is_loaded = this.is_selected = false;
              this.misc.apiCall("crud", {
                op: op,
                collection: this.id,
                match: this.sweeped[this.segment],
                doc: null,
                is_crud: true
              }).then(() => {
                this.RefreshData(0);
              }).catch((res: any) => {
                this.misc.doMessage(res && res.msg ? res.msg : res, "error");
              }).finally(() => {
                this.is_loaded = true;
                this.is_deleting = false;
              });
            }
          }]
        }).then((alert: any) => {
          alert.style.cssText = "--backdrop-opacity: 0 !important; z-index: 99999 !important; box-shadow: none !important;";
          alert.present();
        });
      }
    } else {
      this.misc.doMessage("you must select record(s) prior to " + op, "error");
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
          collection: this.id ? this.id : null,
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
        if (op === "action" && res.data.res?.count > 0) {
          this.misc.doMessage("action completed successfully. " + res.data.res.count + " records affected", "success");
        }
        this.RefreshData(0);
      }
    });
    return await modal.present();
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
        this.misc.doMessage(error, "error");
      });
    } else {
      this.misc.doMessage("you must apply a filter prior to save", "error");
    }
  }

  SwitchSelectData(event: any) {
    this.selected = new Array(this.data.length).fill(event);
    this.GetIsSelectData();
  }

  SetSelectData(i: number, event: any) {
    if (!["_log", "_backup", "_announcement"].includes(this.segment)) {
      this.selected[i] = event.detail.checked;
      this.GetIsSelectData();
    }
  }

  orderByIndex = (a: any, b: any): number => {
    return a.value.index < b.value.index ? -1 : (b.value.index > a.value.index ? 1 : 0);
  }

  setSort(key: string, d: number) {
    this.sort = {};
    this.sort[key] = d ? d * -1 : 1;
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
        if (this.searched) {
          this.searched[key_] = full ? { actived: false, kw: null, f: false, op: "eq", setmode: false } : { actived: false, kw: this.searched[key_].kw ? this.searched[key_].kw : null, f: this.searched[key_].f ? this.searched[key_].f : null, op: this.searched[key_].op ? this.searched[key_].op : null, setmode: this.searched[key_].setmode ? this.searched[key_].setmode : null };
        }
      }
    });
  }

  doClearFilter() {
    return new Promise((resolve, reject) => {
      this.filter = [];
      this.storage.set("LSSFILTER_" + this.id, this.filter).then(() => {
        this.storage.set("LSSEARCHED_" + this.id, null).then(() => {
          this.doResetSearch(true);
          this.searched = null;
          this.sweeped[this.segment] = [];
          this.RefreshData(0).then(() => {
            resolve(true);
          }).catch((res: any) => {
            this.misc.doMessage(res, "error");
          });
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
      if (["true", "false"].includes(v)) {
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

  doTemplateShow() {
    this.template_showed = !this.template_showed;
  }

  doShowSchema() {
    if (this.jeopen) {
      this.jeopen = false;
      this.schemevis = "hide"
    } else {
      this.jeopen = true;
      this.schemevis = "show";
      this.editor.focus();
    }
  }

  doSaveSchema() {
    if (this.perm) {
      this.is_saving = true;
      this.misc.apiCall("/crud", {
        op: "saveschema",
        collection: this.id,
        structure: this.structure_
      }).then(() => {
        window.location.reload();
      }).catch((error: any) => {
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

  doChangeSchema(ev: any) {
    if (ev && ev.properties) {
      this.structure_ = ev;
    }
  }

}
