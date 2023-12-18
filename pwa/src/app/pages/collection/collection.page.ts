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

import { Component, OnInit, ViewChild, ElementRef, HostListener } from "@angular/core";
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
  @ViewChild("editor", { static: false }) editor: any = new JsonEditorComponent();
  @ViewChild("searchfocus", { static: false }) searchfocus: any = [];
  @ViewChild("svg") svg: any = ElementRef;
  private json_content_: any = null;
  private sweeped: any = [];
  private actionix: number = -1;
  private menu: string = "";
  private clonok: number = -1;
  private view: any = null;
  private is_selected: boolean = false;
  private counters_: any = {};
  private segment = "data";
  private page_start: number = 1;
  private key_: any = null;
  public jeoptions: JsonEditorOptions = new JsonEditorOptions();
  public header: string = "Collections";
  public subheader: string = "";
  public loadingText: string = environment.misc.loadingText;
  public user: any = null;
  public perm_: boolean = false;
  public perma_: boolean = false;
  public is_crud: boolean = false;
  public paget_: any = [];
  public id: string = "";
  public filter_: any = [];
  public searched: any = null;
  public data: any = [];
  public selected: any = [];
  public record_: any = [];
  public pages_: any = [];
  public limit_: number = environment.misc.limit;
  public page_: number = 1;
  public pager_: number = 1;
  public count: number = 0;
  public is_loaded: boolean = true;
  public multicheckbox: boolean = false;
  public collections_: any = [];
  public title_: any = [];
  public links_: any = [];
  public is_initialized: boolean = false;
  public scan_: boolean = false;
  public actions: any = [];
  public properties_: any = {};
  public is_saving: boolean = false;
  public is_deleting: boolean = false;
  public sort: any = {};
  public structure_: any = {};
  public schemavis_: boolean = false;
  public importvis_: boolean = false;
  public is_key_copied: boolean = false;
  public is_key_copying: boolean = false;
  public is_inprogress: boolean = false;
  public flashcards_: any = [];
  public propkeys_: string = "";
  public is_copied: boolean = false;
  public selections_: any = {};

  constructor(
    private storage: Storage,
    private auth: Auth,
    private crud: Crud,
    private modal: ModalController,
    private alert: AlertController,
    private router: Router,
    public misc: Miscellaneous
  ) {
    this.crud.collections.subscribe((res: any) => {
      this.collections_ = res && res.data ? res.data : [];
      this.title_ = this.collections_?.find((obj_: any) => obj_.col_id === this.subheader)?.col_title;
    });
    this.auth.user.subscribe((res: any) => {
      this.perm_ = res && res.perm;
      this.perma_ = res && res.perma;
      this.user = res;
    });
  }

  ngOnDestroy() {
    this.auth.user.unsubscribe;
    this.crud.collections.unsubscribe;
  }

  ngOnInit() {
    this.menu = this.router.url.split("/")[1];
    this.subheader = this.id = this.router.url.split("/")[2];
    this.is_crud = this.id.charAt(0) === "_" ? false : true;
    this.header = this.is_crud ? "COLLECTIONS" : this.id === "_collection" ? "DATA COLLECTIONS" : this.id === "_query" ? "QUERIES" : this.id === "_job" ? "JOBS" : this.id === "_visual" ? "VISUALIZATION" : "ADMINISTRATION";
  }

  ionViewDidEnter() {
    this.is_initialized = false;
    this.storage.get("LSPAGINATION").then((LSPAGINATION: any) => {
      this.limit_ = LSPAGINATION * 1;
      this.storage.get("LSFILTER_" + this.id).then((LSFILTER_: any) => {
        this.storage.get("LSSEARCHED_" + this.id).then((LSSEARCHED_: any) => {
          this.filter_ = LSFILTER_ && LSFILTER_.length > 0 ? LSFILTER_ : [];
          LSSEARCHED_ ? this.searched = LSSEARCHED_ : null;
          this.actions = [];
          this.crud.get_collection(this.id).then((res: any) => {
            this.counters_ = res && res.counters ? res.counters : {};
            this.refresh_data(0, false).then(() => { }).catch((error: any) => {
              this.misc.doMessage(error, "error");
            }).finally(() => {
              this.is_initialized = true;
            });
          }).catch((error: any) => {
            this.misc.doMessage(error, "error");
          });
        });
      });
    });
  }

  get_links(res: any) {
    return new Promise((resolve, reject) => {
      this.links_ = res.structure.links ? res.structure.links.filter((lnk_: any) => lnk_.listed === true) : [];
      for (let l_: number = 0; l_ < this.links_.length; l_++) {
        this.data.forEach((data_: any, index_: number) => {
          this.data[index_]["_link_" + this.links_[l_].collection].count = 0;
          this.data[index_]["_link_" + this.links_[l_].collection].sum = 0;
          this.data[index_]["_link_" + this.links_[l_].collection].forEach((item_: any) => {
            this.data[index_]["_link_" + this.links_[l_].collection].count += 1;
            this.data[index_]["_link_" + this.links_[l_].collection].sum += item_.sum;
          });
        });
      }
      resolve(true);
    });
  }

  refresh_data(page_: number, outfile_: boolean) {
    return new Promise((resolve, reject) => {
      this.is_loaded = this.is_selected = false;
      this.schemavis_ = false;
      this.storage.get("LSSEARCHED_" + this.id).then((LSSEARCHED_: any) => {
        this.storage.get("LSFILTER_" + this.id).then((LSFILTER_: any) => {
          this.storage.get("LSSELECTIONS_" + this.id).then((LSSELECTIONS_: any) => {
            this.searched = LSSEARCHED_ ? LSSEARCHED_ : null;
            this.filter_ = LSFILTER_ && LSFILTER_.length > 0 ? LSFILTER_ : [];
            this.selections_ = LSSELECTIONS_ ? LSSELECTIONS_ : {};
            this.count = 0;
            this.page_ = page_ === 0 ? 1 : page_;
            this.misc.api_call("crud", {
              op: "read",
              collection: this.id,
              projection: null,
              match: this.filter_ && this.filter_.length > 0 ? this.filter_ : [],
              sort: this.sort,
              page: this.page_,
              limit: this.limit_,
              selections: this.selections_,
              outfile: outfile_
            }).then((res: any) => {
              this.selections_ = res.selected;
              this.pager_ = this.page_;
              this.data = res.data;
              this.structure_ = res.structure;
              this.get_links(res).then(() => {
                this.json_content_ = res.structure;
                this.actions = res.actions;
                this.properties_ = res.structure.properties;
                this.importvis_ = res.structure.import?.enabled;
                this.scan_ = true ? Object.keys(this.properties_).filter((key: any) => this.properties_[key].scan).length > 0 : false;
                this.count = res.count;
                this.multicheckbox = false;
                this.multicheckbox ? this.multicheckbox = false : null;
                this.selected = new Array(res.data.length).fill(false);
                this.pages_ = this.count > 0 ? Math.ceil(this.count / this.limit_) : environment.misc.default_page;
                const lmt = this.pages_ >= 10 ? 10 : this.pages_;
                this.paget_ = new Array(lmt);
                this.page_start = this.page_ > 10 ? this.page_ - 10 + 1 : 1;
                this.searched === null ? this.init_search(true) : this.init_search(false);
                for (let p = 0; p < this.paget_.length; p++) {
                  this.paget_[p] = this.page_start + p;
                }
                resolve(true);
              });
            }).catch((error: any) => {
              this.misc.doMessage(error, "error");
              reject(error);
            }).finally(() => {
              this.crud.get_all().then(() => {
                this.propkeys_ = "";
                Object.keys(this.properties_).forEach((key_: string) => { this.propkeys_ += `${key_}\t`; });
              }).catch((err_: any) => {
                console.error("get_all", err_);
              }).finally(() => {
                this.is_loaded = true;
              });
            });
          });
        });
      });
    });
  }

  action(ix_: any) {
    if (this.actions[ix_]?.one_click || this.sweeped[this.segment]?.length > 0) {
      this.actionix = ix_;
      this.go_crud(this.record_, "action");
    } else {
      this.misc.doMessage("please select the rows to be processed", "error");
    }
  }

  multi_crud(op_: string) {
    if (this.data.length > 0 && this.is_loaded) {
      if (this.is_selected) {
        if (op_ === "action") {
          if (this.structure_ && this.structure_.actions && this.structure_.actions.length > 0) {
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
                this.misc.api_call("crud", {
                  op: op_,
                  collection: this.id,
                  match: this.sweeped[this.segment],
                  doc: null,
                  is_crud: true
                }).then(() => {
                  this.refresh_data(0, false);
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
        this.misc.doMessage("please select the rows to be processed", "warning");
      }
    }
  }

  async go_crud(record_: any, op: string) {
    if (this.id === "_query" && !this.perm_) { } else {
      const modal = await this.modal.create({
        component: CrudPage,
        backdropDismiss: true,
        cssClass: "crud-modal",
        componentProps: {
          shuttle: {
            op: op,
            collection: this.id ? this.id : null,
            collections: this.collections_ ? this.collections_ : [],
            user: this.user,
            data: record_,
            counters: this.counters_,
            structure: this.structure_,
            sweeped: this.sweeped[this.segment] && op === "action" ? this.sweeped[this.segment] : [],
            filter: op === "action" ? this.filter_ : null,
            actions: this.actions && this.actions.length > 0 ? this.actions : [],
            actionix: op === "action" && this.actionix >= 0 ? this.actionix : -1,
            view: this.view,
            scan: this.scan_
          }
        }
      });
      modal.onDidDismiss().then((res_: any) => {
        if (op === "action" || res_.data?.modified || this.scan_) {
          this.refresh_data(0, false);
        }
      });
      return await modal.present();
    }
  }

  async get_is_select_data() {
    this.sweeped[this.segment] = [];
    const q = await this.selected.findIndex((obj: boolean) => obj === true);
    this.clonok = q;
    q >= 0 ? (this.is_selected = true) : (this.is_selected = false);
    const r = await this.selected.reduce((acc: any, val: any, index: number) => {
      const q = val === true ? this.sweeped[this.segment].push(this.data[index]._id) : null;
    }, []);
  }

  switch_select_data(event: any) {
    this.selected = new Array(this.data.length).fill(event);
    this.get_is_select_data();
  }

  set_select_data(i: number, event: any) {
    if (!["_log", "_backup", "_announcement"].includes(this.segment)) {
      this.selected[i] = event.detail.checked;
      this.get_is_select_data();
    }
  }

  orderByIndex = (a: any, b: any): number => {
    return a.value.index < b.value.index ? -1 : (b.value.index > a.value.index ? 1 : 0);
  }

  do_sort(key: string, d: number) {
    this.sort = {};
    this.sort[key] = d ? d * -1 : 1;
    this.refresh_data(0, false);
  }

  set_search(k_: string) {
    setTimeout(() => {
      this.searchfocus?.setFocus();
      this.searched[k_].kw = this.searched[k_]?.kw?.trim().replace(/^\s*\n/gm, "");
      this.key_ = k_;
    }, 500);
    for (let key_ in this.structure_.properties) {
      this.searched[key_].actived = k_ === key_ ? !this.searched[key_]?.actived : false;
    }
  }

  init_search(full: boolean) {
    full ? this.searched = {} : null;
    this.storage.set("LSFILTER_" + this.id, this.filter_).then(() => {
      if (this.searched) {
        for (let key_ in this.structure_.properties) {
          this.searched[key_] = full ? { actived: false, kw: null, f: false, op: "contains" } : { actived: false, kw: this.searched[key_]?.kw ? this.searched[key_]?.kw : null, f: this.searched[key_]?.f, op: this.searched[key_]?.op };
        }
      }
    });
  }

  clear_filter() {
    return new Promise((resolve, reject) => {
      this.filter_ = [];
      this.storage.remove("LSFILTER_" + this.id).then(() => {
        this.storage.remove("LSSEARCHED_" + this.id).then(() => {
          this.storage.remove("LSSELECTIONS_" + this.id).then(() => {
            this.init_search(true);
            this.searched = null;
            this.sweeped[this.segment] = [];
            this.sort = {};
            this.refresh_data(0, false).then(() => {
              resolve(true);
            }).catch((error: any) => {
              this.misc.doMessage(error, "error");
              reject(error);
            });
          });
        });
      });
    });
  }

  init_search_item(key_: string) {
    const n_ = this.filter_.length;
    this.searched[key_].actived = false;
    for (let d = 0; d < n_; d++) {
      if (this.filter_[d] && this.filter_[d]["key"] === key_) {
        this.filter_.splice(d, 1);
        this.searched[key_].f = false;
        this.searched[key_].kw = null;
        this.searched[key_].op = "contains";
      }
      if (d === n_ - 1) {
        this.storage.set("LSFILTER_" + this.id, this.filter_).then(() => {
          this.storage.set("LSSEARCHED_" + this.id, this.searched).then(() => {
            this.storage.set("LSSELECTIONS_" + this.id, this.selections_).then(() => {
              this.refresh_data(0, false);
            });
          });
        });
      }
    }
  }

  search(key_: string, value_: string) {
    this.searched[key_].actived = false;
    if (!this.filter_ || this.filter_.length === 0) {
      if (["true", "false"].includes(value_)) {
        this.filter_.push({
          key: key_,
          op: value_,
          value: null
        });
      } else {
        this.filter_.push({
          key: key_,
          op: this.searched[key_]?.op,
          value: value_
        });
      }
      this.searched[key_].f = true;
      this.storage.set("LSFILTER_" + this.id, this.filter_).then(() => {
        this.storage.set("LSSEARCHED_" + this.id, this.searched).then(() => {
          this.storage.set("LSSELECTIONS_" + this.id, this.selections_).then(() => {
            this.refresh_data(0, false);
          });
        });
      });
    } else {
      let found_ = false;
      const n_ = this.filter_.length;
      for (let d = 0; d < n_; d++) {
        if (this.filter_[d] && this.filter_[d]["key"] === key_) {
          found_ = true;
          this.filter_[d]["op"] = this.searched[key_]?.op;
          this.filter_[d]["value"] = value_;
        }
        if (d === n_ - 1) {
          !found_ ? this.filter_.push({
            key: key_,
            op: this.searched[key_]?.op,
            value: value_
          }) : null;
          this.searched[key_].f = true;
          this.storage.set("LSFILTER_" + this.id, this.filter_).then(() => {
            this.storage.set("LSSEARCHED_" + this.id, this.searched).then(() => {
              this.storage.set("LSSELECTIONS_" + this.id, this.selections_).then(() => {
                this.refresh_data(0, false);
              });
            });
          });
        }
      }
    }
  }

  set_search_item(key_: string, op: string) {
    this.searched[key_].op = op;
  }

  json_editor_init() {
    return new Promise((resolve) => {
      this.jeoptions = new JsonEditorOptions();
      this.jeoptions.modes = ["tree", "code", "text"]
      this.jeoptions.mode = "code";
      this.jeoptions.mainMenuBar = true;
      this.jeoptions.statusBar = false;
      this.jeoptions.navigationBar = true;
      this.jeoptions.enableSort = false;
      this.jeoptions.expandAll = false;
      resolve(true);
    });
  }

  set_editor(set_: boolean) {
    this.schemavis_ = !this.schemavis_ && set_ && this.is_loaded;
    set_ ? this.json_editor_init().then(() => { }) : null;
  }

  do_flashcard(item_: any) {
    this.filter_ = item_.view.data_filter;
    this.storage.set("LSFILTER_" + this.id, this.filter_).then(() => {
      this.refresh_data(0, false).then(() => { }).catch((res: any) => {
        this.misc.doMessage(res, "error");
      });
    });
  }

  save_schema_f() {
    if (this.json_content_) {
      this.is_saving = true;
      this.structure_ = this.json_content_;
      this.misc.api_call("crud", {
        op: "saveschema",
        collection: this.id,
        structure: this.json_content_
      }).then(() => {
        this.misc.doMessage("schema saved successfully", "success");
        this.refresh_data(0, false).then(() => {
          this.schemavis_ = false;
        });
      }).catch((error: any) => {
        this.misc.doMessage(error, "error");
      }).finally(() => {
        this.is_saving = false;
      });
    } else {
      this.misc.doMessage("invalid structure", "error");
    }
  }

  import_modal() {
    this.misc.import_modal(this.id).then(() => {
      this.misc.doMessage("file imported successfully", "success");
      this.refresh_data(0, false).then(() => { });
    }).catch((error: any) => {
      console.error(error);
    }).finally(() => { });
  }

  copy_column(key: any) {
    this.is_key_copying = true;
    this.is_key_copied = false;
    this.misc.api_call("crud", {
      op: "copykey",
      collection: this.id,
      properties: this.structure_.properties,
      match: this.filter_,
      sweeped: this.sweeped[this.segment],
      key: key
    }).then((res: any) => {
      this.misc.copy_to_clipboard(res.copied).then(() => {
        this.is_key_copied = true;
        this.searched[key].actived = false;
        this.misc.doMessage(`${res.copied?.split("\n")?.length} items copied`, "success")
      }).catch((error: any) => {
        this.misc.doMessage(`${key} not copied: ${error}`, "error");
      }).finally(() => {
        setTimeout(() => {
          this.is_key_copying = false;
          this.is_key_copied = false;
        }, 1000);
      });
    }).catch((error: any) => {
      this.is_key_copying = false;
      this.misc.doMessage(error, "error");
    });
  }

  copy_headers() {
    this.is_copied = false;
    this.misc.copy_to_clipboard(this.propkeys_).then(() => {
      this.is_copied = true;
    }).catch((error: any) => {
      console.error("copy_headers", error);
    }).finally(() => {
      setTimeout(() => {
        this.is_copied = false;
      }, 1000);
    });
  }

  json_changed(event_: any) {
    !event_.isTrusted ? this.json_content_ = event_ : null;
  }

  go_query_job(record_: any, event_: any) {
    event_.stopPropagation();
    this.id === "_query" ? this.storage.set("LSQUERY", record_).then(() => {
      this.misc.navi.next("/query/" + record_._id);
    }) : this.storage.set("LSJOB", record_).then(() => {
      this.misc.navi.next("/job/" + record_._id);
    });
  }

  tdc(event_: any, record_: any) {
    this.record_ = record_;
    event_.stopPropagation();
  }

  selection_changed(item_: string, s_: number) {
    this.selections_[item_][s_].value = !this.selections_[item_][s_].value;
  }

}