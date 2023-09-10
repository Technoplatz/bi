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
  public default_width: number = environment.misc.defaultColumnWidth;
  public header: string = "Collections";
  public subheader: string = "";
  public description: string = "";
  public loadingText: string = environment.misc.loadingText;
  private submenu: string = "";
  private segment = "data";
  public user: any = null;
  public perm: boolean = false;
  public is_crud: boolean = false;
  public paget: any = [];
  public id: string = "";
  public filter_: any = [];
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
  private counters_: any = {};
  public collections: any = [];
  public is_initialized: boolean = false;
  public scan_: boolean = false;
  public status_: any = {};
  public action_: any = {};
  private view: any = null;
  public actions: any = [];
  public columns_: any;
  private sweeped: any = [];
  private actionix: number = -1;
  private menu: string = "";
  private page_end: number = 1;
  private clonok: number = -1;
  private collections_: any;
  private user_: any;
  public schema_key: any = null;
  public properties_: any = {};
  public is_saving: boolean = false;
  public is_deleting: boolean = false;
  public sort: any = {};
  public structure: any = {};
  public schemevis: any = "hide";
  private structure_ori_: any = null;
  private structured_: any = null;
  public is_key_copied: boolean = false;
  public is_key_copying: boolean = false;
  private segmentsadm_: any = environment.segmentsadm;
  public templates: any = [];
  public is_inprogress: boolean = false;
  public flashcards_: any = [];
  public menutoggle: boolean = false;
  public schema_: any = {
    "properties": { "title": "Properties", "count": 0 },
    "required": { "title": "Required", "count": 0 },
    "index": { "title": "Indexes", "count": 0 },
    "actions": { "title": "Actions", "count": 0 },
    "parents": { "title": "Parents", "count": 0 },
    "triggers": { "title": "Triggers", "count": 0 },
    "views": { "title": "Views", "count": 0 },
    "unique": { "title": "Unique", "count": 0 },
    "sort": { "title": "Sort", "count": 0 },
    "links": { "title": "Links", "count": 0 },
    "fetchers": { "title": "Fetchers", "count": 0 }
  }

  constructor(
    private storage: Storage,
    private auth: Auth,
    private crud: Crud,
    private modal: ModalController,
    private alert: AlertController,
    private router: Router,
    public misc: Miscellaneous
  ) {
    this.jeoptions = new JsonEditorOptions();
    this.jeoptions.modes = ["tree", "code", "text"]
    this.jeoptions.mode = "tree";
    this.jeoptions.statusBar = true;
    this.jeoptions.enableSort = false;
    this.jeoptions.expandAll = false;
    this.jeoptions.navigationBar = true;
    this.jeoptions.name = "schema-structure";
    this.crud.views.subscribe((res: any) => {
      this.flashcards_ = res ? res.filter((obj: any) => obj.collection === this.id && obj.view.flashcard === true) : [];
    });
    this.collections_ = this.crud.collections.subscribe((res: any) => {
      this.collections = res && res.data ? res.data : [];
    });
    this.user_ = this.auth.user.subscribe((res: any) => {
      this.user = res;
    });
  }

  ngOnDestroy() {
    this.auth.user.unsubscribe;
    this.crud.collections.unsubscribe;
    this.crud.views.unsubscribe;
    this.collections_ = null;
    this.user_ = null;
  }

  ngOnInit() {
    this.menu = this.router.url.split("/")[1];
    this.id = this.submenu = this.router.url.split("/")[2];
    this.is_crud = this.id.charAt(0) === "_" ? false : true;
    this.header = this.is_crud ? "COLLECTIONS" : ["_collection", "_query"].includes(this.id) ? "STUDIO" : "ADMINISTRATION";
    this.crud.getCollection(this.id).then((res: any) => {
      this.counters_ = res && res.counters ? res.counters : {};
      this.subheader = res && res.data ? res.data.col_title : this.id;
      this.description = res && res.data ? res.data.col_description : this.segmentsadm_.find((obj: any) => obj.id === this.id)?.description;
    }).catch((error: any) => {
      this.misc.doMessage(error, "error");
    });
  }

  ionViewDidEnter() {
    this.is_initialized = false;
    this.storage.get("LSFILTER_" + this.id).then((LSFILTER_: any) => {
      this.storage.get("LSSEARCHED_" + this.id).then((LSSEARCHED_: any) => {
        this.storage.get("LSSTATUS_" + this.id).then((LSSTATUS: any) => {
          this.status_ = LSSTATUS;
          this.filter_ = LSFILTER_ && LSFILTER_.length > 0 ? LSFILTER_ : [];
          LSSEARCHED_ ? this.searched = LSSEARCHED_ : null;
          this.actions = [];
          this.RefreshData(0).then(() => {
            if (this.id === "_collection") {
              this.misc.apiCall("crud", {
                op: "template",
                proc: "list",
                template: null
              }).then((res: any) => {
                this.templates = res && res.templates ? res.templates : [];
              }).catch((error: any) => {
                this.misc.doMessage(error, "error");
              });
            }
          }).catch((error: any) => {
            this.misc.doMessage(error, "error");
          }).finally(() => {
            this.is_initialized = true;
          });
        });
      });
    });
  }

  doBuildSchema(prop_: any) {
    for (let p_ in prop_) {
      if (this.schema_[p_]) {
        this.schema_[p_].count = ["properties", "sort", "views"].includes(p_) ? Object.keys(prop_[p_]).length : prop_[p_].length;
      }
    }
  }

  RefreshData(p: number) {
    return new Promise((resolve, reject) => {
      this.is_loaded = this.is_selected = false;
      this.doSetSchemaKey(null);
      this.storage.get("LSSEARCHED_" + this.id).then((LSSEARCHED_: any) => {
        this.searched = LSSEARCHED_ ? LSSEARCHED_ : null;
        this.storage.get("LSFILTER_" + this.id).then((LSFILTER_: any) => {
          this.filter_ = LSFILTER_ && LSFILTER_.length > 0 ? LSFILTER_ : [];
          this.count = 0;
          this.page = p === 0 ? 1 : p;
          this.misc.apiCall("crud", {
            op: "read",
            collection: this.id,
            projection: null,
            match: this.filter_ && this.filter_.length > 0 ? this.filter_ : [],
            sort: this.sort,
            page: this.page,
            limit: this.limit
          }).then((res: any) => {
            this.editor?.setMode(this.jeoptions.mode);
            this.doBuildSchema(res.structure);
            this.data = res.data;
            this.structure_ori_ = res.structure;
            this.structure = res.structure;
            this.actions = this.structure.actions;
            this.properties_ = res.structure.properties;
            this.scan_ = true ? Object.keys(this.properties_).filter((key: any) => this.properties_[key].scan).length > 0 : false;
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
          }).catch((error: any) => {
            this.misc.doMessage(error, "error");
            reject(error);
          }).finally(() => {
            this.is_loaded = true;
            this.crud.getAll().then(() => { });
          });
        });
      });
    });
  }

  doAction(ix_: any) {
    if (this.actions[ix_]?.one_click || this.sweeped[this.segment]?.length > 0) {
      this.actionix = ix_;
      this.go_crud(null, "action");
    } else {
      this.misc.doMessage("please make a selection to run this action", "error");
    }
  }

  MultiCrud(op_: string) {
    if (this.data.length > 0 && this.is_selected) {
      if (op_ === "action") {
        if (this.structure && this.structure.actions && this.structure.actions.length > 0) {
          this.go_crud(null, op_);
        } else {
          this.misc.doMessage("no action defined for the collection", "error");
        }
      } else {
        this.alert.create({
          header: "Confirm",
          message: "Please confirm this " + op_,
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
                op: op_,
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
      this.misc.doMessage("you must select record(s) prior to " + op_, "error");
    }
  }

  async go_crud(rec: any, op: string) {
    if (this.id === "_query") { this.go_query(rec) } else {
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
            counters: this.counters_,
            structure: this.editor ? this.editor.get() : this.structure,
            sweeped: this.sweeped[this.segment] && op === "action" ? this.sweeped[this.segment] : [],
            filter: op === "action" ? this.filter_ : null,
            actions: this.actions && this.actions.length > 0 ? this.actions : [],
            actionix: op === "action" && this.actionix >= 0 ? this.actionix : -1,
            view: this.view,
            scan: this.scan_
          }
        }
      });
      modal.onDidDismiss().then((res: any) => {
        if (res.data.modified || this.scan_) {
          if (op === "action" && res.data.res) {
            this.misc.doMessage(res.data.res.content, "success");
          }
          this.RefreshData(0);
        }
      });
      return await modal.present();
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
    this.storage.set("LSFILTER_" + this.id, this.filter_).then(() => {
      for (let key_ in this.structure.properties) {
        if (this.searched) {
          this.searched[key_] = full ? { actived: false, kw: null, f: false, op: "contains", setmode: false } : { actived: false, kw: this.searched[key_].kw ? this.searched[key_].kw : null, f: this.searched[key_].f ? this.searched[key_].f : null, op: this.searched[key_].op ? this.searched[key_].op : null, setmode: this.searched[key_].setmode ? this.searched[key_].setmode : null };
        }
      }
    });
  }

  doClearFilter() {
    return new Promise((resolve, reject) => {
      this.filter_ = [];
      this.status_ = null;
      this.storage.set("LSFILTER_" + this.id, this.filter_).then(() => {
        this.storage.set("LSSEARCHED_" + this.id, null).then(() => {
          this.storage.remove("LSSTATUS_" + this.id).then(() => {
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
    });
  }

  doResetSearchItem(k: string) {
    const n_ = this.filter_.length;
    this.searched[k].actived = false;
    for (let d = 0; d < n_; d++) {
      if (this.filter_[d] && this.filter_[d]["key"] === k) {
        this.filter_.splice(d, 1);
        this.searched[k].f = false;
        this.searched[k].kw = null;
        this.searched[k].op = "contains";
        this.searched[k].setmode = false;
      }
      if (d === n_ - 1) {
        this.storage.set("LSFILTER_" + this.id, this.filter_).then(() => {
          this.storage.set("LSSEARCHED_" + this.id, this.searched).then(() => {
            this.RefreshData(0);
          });
        });
      }
    }
  }

  doSearch(k: string, v: string) {
    this.searched[k].setmode = false;
    if (!this.filter_ || this.filter_.length === 0) {
      if (["true", "false"].includes(v)) {
        this.filter_.push({
          key: k,
          op: v,
          value: null
        });
      } else {
        this.filter_.push({
          key: k,
          op: this.searched[k].op,
          value: v
        });
      }
      this.searched[k].f = true;
      this.storage.set("LSFILTER_" + this.id, this.filter_).then(() => {
        this.storage.set("LSSEARCHED_" + this.id, this.searched).then(() => {
          this.storage.remove("LSSTATUS_" + this.id).then(() => {
            this.status_ = null;
            this.RefreshData(0);
          });
        });
      });
    } else {
      let found = false;
      const n_ = this.filter_.length;
      for (let d = 0; d < n_; d++) {
        if (this.filter_[d] && this.filter_[d]["key"] === k) {
          found = true;
          this.filter_[d]["op"] = this.searched[k].op;
          this.filter_[d]["value"] = v;
        }
        if (d === n_ - 1) {
          !found ? this.filter_.push({
            key: k,
            op: this.searched[k].op,
            value: v
          }) : null;
          this.searched[k].f = true;
          this.storage.set("LSFILTER_" + this.id, this.filter_).then(() => {
            this.storage.set("LSSEARCHED_" + this.id, this.searched).then(() => {
              this.storage.remove("LSSTATUS_" + this.id).then(() => {
                this.status_ = null;
                this.RefreshData(0);
              });
            });
          });
        }
      }
    }
  }

  doSetSearchItemOp(k: string, op: string) {
    this.searched[k].op = op;
  }

  doShowSchema(shw: boolean) {
    if (shw) {
      this.editor.setMode(this.jeoptions.mode);
      this.schemevis = "show";
      this.editor.focus();
    } else {
      this.RefreshData(0).then(() => {
        this.schemevis = "hide"
        this.structured_ ? this.misc.doMessage("changes were discarded", "warning") : null;
        this.structured_ = null;
      });
    }
  }

  doSetSchemaKey(key: any) {
    this.schema_key = key ? key : "schema-structure";
    this.editor?.setName(key ? key : "schema-structure");
  }

  doShowSchemaKey(key: string) {
    this.structured_ ? this.misc.doMessage("the latest change was discarded", "warning") : null;
    this.doSetSchemaKey(key);
    this.structured_ = null;
    this.structure = this.structure_ori_[key];
    this.editor.setMode(this.jeoptions.mode);
    this.schemevis = "show";
    this.editor.focus();
  }

  doFlashcard(item_: any) {
    if (item_ !== "") {
      this.status_ = item_;
      this.filter_ = item_.view.data_filter;
      this.storage.set("LSSTATUS_" + this.id, this.status_).then(() => {
        this.storage.set("LSFILTER_" + this.id, this.filter_).then(() => {
          this.RefreshData(0).then(() => { }).catch((res: any) => {
            this.misc.doMessage(res, "error");
          });
        });
      });
    }
  }

  doMenuToggle() {
    this.storage.get("LSMENUTOGGLE").then((LSMENUTOGGLE: boolean) => {
      this.menutoggle = !LSMENUTOGGLE ? true : false;
      this.storage.set("LSMENUTOGGLE", this.menutoggle).then(() => {
        this.misc.menutoggle.next(this.menutoggle);
      });
    });
  }

  compareWith(o1: any, o2: any) {
    return o1 && o2 ? o1.id === o2.id : o1 === o2;
  }

  doClearAttr() {
    this.status_ = null;
    this.action_ = null;
  }

  doSaveView() {
    this.alert.create({
      cssClass: "my-custom-class",
      subHeader: "Save Filter as View",
      message: "Please enter a view name to save the current filter.",
      inputs: [
        {
          name: "title",
          id: "title",
          value: null,
          type: "text",
          placeholder: "Enter a title for the new view"
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
          text: "SAVE VIEW",
          handler: (data: any) => {
            this.misc.apiCall("/crud", {
              op: "saveview",
              collection: this.id,
              filter: this.filter_,
              title: data.title
            }).then((res: any) => {
              this.misc.doMessage("view saved successfully", "success");
              this.crud.getAll().then(() => { });
              this.misc.navi.next("view/" + res.id);
            }).catch((error: any) => {
              this.misc.doMessage(error, "error");
            });
          }
        }
      ]
    }).then((alert: any) => {
      alert.present();
      const viewfocus: HTMLElement = document.getElementById("title")!;
      setTimeout(() => viewfocus.focus(), 600);
    });
  }

  doSaveSchema() {
    if (this.structured_) {
      this.is_saving = true;
      this.misc.apiCall("/crud", {
        op: "saveschema",
        collection: this.id,
        schema_key: this.schema_key,
        structure: this.structured_
      }).then(() => {
        this.misc.doMessage("schema saved successfully", "success");
        this.RefreshData(0).then(() => {
          this.schemevis = "hide"
        });
      }).catch((error: any) => {
        this.misc.doMessage(error, "error");
      }).finally(() => {
        this.structured_ = null;
        this.is_saving = false;
      });
    } else {
      this.misc.doMessage("no changes detected in the schema", "warning");
    }

  }

  doUploadModal() {
    this.misc.doUploadModal(this.id).then(() => {
      this.RefreshData(0).then(() => { });
    });
  }

  setCopy(key: any) {
    this.is_key_copying = true;
    this.is_key_copied = false;
    this.misc.apiCall("crud", {
      op: "copykey",
      collection: this.id,
      properties: this.structure.properties,
      match: this.filter_,
      sweeped: this.sweeped[this.segment],
      key: key
    }).then((res: any) => {
      this.misc.copyToClipboard(res.copied).then(() => {
        this.is_key_copying = false;
        this.is_key_copied = true;
      }).catch((error: any) => {
        console.error("not copied", key, error);
      }).finally(() => {
        setTimeout(() => {
          this.is_key_copied = false;
          this.is_key_copying = false;
          this.searched[key].actived = false;
        }, 1000);
      });
    }).catch((error: any) => {
      this.is_key_copied = false;
      this.is_key_copying = false;
      this.searched[key].actived = false;
      this.misc.doMessage(error, "error");
    });
  }

  doChangeSchema(ev: any) {
    if (!ev.isTrusted) {
      this.structured_ = ev;
    } else {
      console.error("*** event", ev);
    }
  }

  doInstallTemplate(item_: any, ix: number) {
    if (!this.templates[ix].processing) {
      this.templates[ix].processing = true;
      this.misc.apiCall("crud", {
        op: "template",
        proc: "install",
        id: item_._id
      }).then((res: any) => {
        this.misc.doMessage(res.msg, "success");
        this.misc.navi.next("dashboard");
      }).catch((error: any) => {
        this.misc.doMessage(error, "error");
      }).finally(() => {
        this.RefreshData(0).then(() => {
          this.templates[ix].processing = false;
        });
      });
    }
  }

  go_query(record_: any) {
    this.storage.set("LSQUERY", record_).then(() => {
      this.misc.navi.next("/query/" + record_.que_id);
    });
  }

}