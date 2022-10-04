import { Component, OnInit, ViewChild } from "@angular/core";
import { ModalController, AlertController, IonSelect, NavController } from "@ionic/angular";
import { Router } from "@angular/router";
import { Location } from "@angular/common";
import { Storage } from "@ionic/storage";
import { Crud } from "../../classes/crud";
import { Auth } from "../../classes/auth";
import { Miscellaneous } from "../../classes/miscellaneous";
import { environment } from "../../../environments/environment";
import { CrudPage } from "../crud/crud.page";
import { JsonEditorComponent, JsonEditorOptions } from "ang-jsoneditor";

@Component({
  selector: "app-console",
  templateUrl: "./console.page.html",
  styleUrls: ["./console.page.scss"]
})

export class ConsolePage implements OnInit {
  @ViewChild(JsonEditorComponent, { static: false }) public strcutureEditor: JsonEditorComponent;
  @ViewChild("select0") selectRef: IonSelect;
  public now: any = Date.now();
  public version = environment.appVersion;
  public loadingText: string = environment.misc.loadingText;
  public menu: string;
  public submenu: string;
  public header: string;
  public header_desc: string;
  public segment = "data";
  public user: any = null;
  public segmentsadm: any;
  public themes: any = environment.themes;
  public limits: any = environment.misc.limits;
  public perm: boolean;
  public is_crud: boolean;
  public in_otp_process: boolean = false;
  public in_otp_process_test: boolean = false;
  public paget: any = [];
  public id: string = null;
  public sortstr: any;
  public ok: boolean = false;
  public filter: any = [];
  public saved_filter: string = null;
  public selected_view: any;
  public searched: any = null;
  public data: any = [];
  public structure: any = [];
  public selected: any = [];
  public announcements: any = [];
  public views: any = [];
  public views_dash: any = [];
  public views_pane: any = [];
  public visuals: any = [];
  public kpis: any = [];
  public metrics: any = [];
  public templates: any = [];
  public pages: any = [];
  public limit: number = environment.misc.limit;
  public page: number = 1;
  public page_start: number = 1;
  public page_end: number = 1;
  public count: number = 0;
  public chart_size: string = "small";
  public chart_css: string = "";
  public is_loaded: boolean = true;
  public is_dash_ok: boolean = false;
  public is_selected: boolean = false;
  public is_show_resize: boolean = false;
  public is_pivot_showed: boolean = true;
  public is_pivot_loading: boolean = false;
  public pivot_: string = null;
  public statistics_key_: string = null;
  public statistics_: any = null;
  public multicheckbox: boolean = false;
  public clonok: number = -1;
  public show_select: boolean = true;
  public master: any = {};
  public view_active: boolean = true;
  public collections: any = [];
  public collections_: any = {};
  public is_initialized: boolean = false;
  public is_pane_ok: boolean = false;
  public is_url_copied: boolean = false;
  public is_apikey_copied: boolean = false;
  public is_apikey_enabled: boolean = false;
  public accountf_apikey: string = null;
  public accountf_apikeydate: any = null;
  public accountf_description: string = null;
  public accountf_qrurl: string = null;
  public is_processing_account: boolean = false;
  public is_visuals_loading: boolean = false;
  public qr_exists: boolean = false;
  public qr_show: boolean = false;
  public otp_show: boolean = false;
  public otp_qr: string = null;
  public dashmode: string = "card";
  public viewurl_: string = null;
  public viewurl_masked_: string = null;
  public view: any = null;
  public visual: any = null;
  public view_id: string = null;
  public visual_id: string = null;
  public view_data: any = [];
  public view_df: any = [];
  public view_count: number = 0;
  public view_properties: any = [];
  public view_properties_: any = [];
  public subscribers: string;
  public scheduled: boolean;
  public sched_days: string;
  public sched_hours: string;
  public sched_minutes: string;
  public sched_timezone: string;
  public viewtab: string = "pivot";
  public saas_: any;
  public actions: any = [];
  public vie_projection: any = [];
  public columns_: any;
  public chart: any = null;
  public class_left_side: string = "console-left-side hide-scrollbar";
  public menu_toggle: boolean = false;
  public view_mode: any = {};
  public show_banners: boolean = false;
  public dummy_id: string = "f00000000000000000000000";
  public pane_segval_colls: string = "collection";
  public pane_segval_dash: string = "dash";
  public options: JsonEditorOptions;
  public options2: JsonEditorOptions;
  public structure_array: any =
    {
      name: "tes_order_no",
      bsonType: "string",
      title: "Title1",
      description: "Description1"
    };
  public structure_new: any = {
    "properties": {
      "_tags": {
        "bsonType": "array",
        "uniqueItems": true,
        "minItems": 0,
        "maxItems": 100,
        "items": {
          "bsonType": "string",
          "pattern": "^[#@][a-zA-Z0-9ÜĞİŞÖÇüğışçöß]{0,32}$"
        },
        "title": "Tags",
        "description": "Tags",
        "subType": "tag",
        "manualAdd": true,
        "chips": true,
        "width": 300
      }
    },
    "required": [],
    "unique": [],
    "index": [
      [
        "_tags"
      ]
    ],
    "parents": [
      {
        "key": "act_account_id",
        "collection": "accounts",
        "lookup": [
          {
            "local": "act_account_id",
            "remote": "acc_id"
          }
        ]
      }
    ],
    "sort": {
      "act_id": 1
    },
    "actions": []
  }
  public customPopoverOptions: any = {
    cssClass: "popover-select"
  };
  public structure1: any = {
    "name": "tes_order_no",
    "bsonType": "string",
    "title": "Title1",
    "description": "Description1",
    "price": 0
  };
  public structure2: any;
  private sweeped: any = [];
  private sort: any = {};
  private properites_: any = {};
  private actionix: number = -1;
  private visuals_structure: any;
  private views_structure: any;
  private apiHost: string;

  constructor(
    private storage: Storage,
    private auth: Auth,
    private crud: Crud,
    private misc: Miscellaneous,
    private modal: ModalController,
    private alert: AlertController,
    private nav: NavController,
    private router: Router,
    private location: Location
  ) {
    this.crud.announcements.subscribe((res: any) => {
      this.announcements = res && res.data ? res.data : [];
    });
    this.misc.getAPIHost().then((apiHost: string) => {
      this.apiHost = apiHost;
    });
  }

  ngOnInit() {
    const qstr1 = this.router.url.split("/")[2];
    const qstr2 = this.router.url.split("/")[3];
    this.storage.get("LSCHARTSIZE").then((LSCHARTSIZE: any) => {
      this.chart_size = LSCHARTSIZE ? LSCHARTSIZE : "small";
      this.chart_css = "chart-sq " + this.chart_size;
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        this.user = LSUSERMETA;
        this.perm = LSUSERMETA && LSUSERMETA.perm ? true : false;
        this.segmentsadm = this.perm ? environment.segmentsadm : [];
        this.collections = [];
        this.collections_ = {};
        this.visuals = [];
        this.views = this.views_dash = [];
        this.templates = [];
        this.filter = [];
        this.data = [];
        this.crud.getAnnouncements();
        this.doRefreshDash().then(() => {
          this.is_initialized = true;
          this.goSection(qstr1, qstr2, qstr2, null);
        }).catch(() => {
          this.is_initialized = true;
        });
      });
    });
  }

  doRefreshDash() {
    return new Promise((resolve, reject) => {
      this.is_dash_ok = false;
      this.auth.Saas().then((res: any) => {
        this.saas_ = res ? res : {};
        this.doAccount("apikeyget").then(() => {
          this.storage.get("LSDASHTOGGLE").then((LSDASHTOGGLE: boolean) => {
            this.show_banners = LSDASHTOGGLE === true || LSDASHTOGGLE === false ? LSDASHTOGGLE : true;
            this.crud.getCollections().then((res: any) => {
              if (res && res.data) {
                this.collections = res.data;
                for (let item_ in res.data) {
                  this.collections_[res.data[item_].col_id] = true;
                }
                this.doGetViews();
                this.crud.Template("list", null).then((res: any) => {
                  this.templates = res && res.data ? res.data : [];
                  this.is_dash_ok = true;
                  resolve(true);
                }).catch((error: any) => {
                  console.error(error);
                  this.misc.doMessage(error, "error");
                  this.is_dash_ok = true;
                  reject(error);
                });
              } else {
                const err_ = "no collection found";
                console.error(err_);
                this.misc.doMessage(err_, "error");
                this.is_dash_ok = true;
                reject(err_);
              }
            }).catch((error: any) => {
              console.error(error);
              this.misc.doMessage(error, "error");
              this.is_dash_ok = true;
              reject(error);
            });
          });
        });
      });
    });
  }

  doSetCollectionID(id: string) {
    return new Promise((resolve) => {
      this.storage.set("LSID", id).then(() => {
        this.id = id;
        resolve(true);
      });
    });
  }

  doEnterViewMode(view_: any) {
    return new Promise((resolve, reject) => {
      console.log("*** doEnterViewMode", view_);
      this.is_loaded = false;
      this.view = view_ ? view_ : this.views[0] ? this.views[0] : null;
      this.menu = "collections";
      this.submenu = this.header = this.view.vie_collection_id;
      this.doSetCollectionID(this.view.vie_collection_id).then(() => {
        this.view_mode[this.id] = true;
        this.view_mode["vie_title"] = this.view ? this.view.vie_title : null;
        this.view_mode["_tags"] = this.view ? this.view._tags : null;
        this.viewurl_ = this.apiHost + "/get/data/" + this.view._id + "?k=" + this.accountf_apikey;
        this.storage.set("LSVIEW-" + this.id, this.view).then(() => {
          this.RefreshData(0).then(() => {
            this.view = view_ ? view_ : this.views[0] ? this.views[0] : null;
            this.view_mode[this.id] = true;
            resolve(true);
          }).catch((error: any) => {
            console.error(error);
            this.misc.doMessage(error, "error");
            reject(error);
          });
        });
      });
    });
  }

  doGetViewMode() {
    return new Promise((resolve) => {
      this.storage.get("LSVIEW-" + this.id).then((LSVIEW: any) => {
        if (this.is_crud) {
          this.view = LSVIEW ? LSVIEW : this.views[0] ? this.views[0] : null;
          this.view_mode[this.id] = LSVIEW ? true : false;
          this.view_mode["vie_title"] = LSVIEW ? LSVIEW.vie_title : null;
          this.view_mode["_tags"] = LSVIEW ? LSVIEW._tags : null;
          this.crud.Pivot(this.view._id, this.accountf_apikey).then((res: any) => {
            this.pivot_ = res && res.pivot ? res.pivot : null;
            const statistics_ = res && res.statistics ? res.statistics : null;
            this.statistics_key_ = this.view.vie_pivot_values ? this.view.vie_pivot_values[0].key : null;
            this.statistics_ = statistics_ && this.statistics_key_ ? statistics_[this.statistics_key_] : null;
          }).catch((error: any) => {
            console.error("*** doGetViewMode", error);
            this.misc.doMessage(error.error.message, "error");
          }).finally(() => {
            resolve(true);
          });
        } else {
          this.view = null;
          this.view_mode[this.id] = false;
          resolve(true);
        }
      });
    });
  }

  doQuitViewMode() {
    return new Promise((resolve, reject) => {
      this.storage.remove("LSVIEW-" + this.id).then(() => {
        this.view_mode[this.id] = false;
        this.view = null;
        this.RefreshData(0).then(() => {
          resolve(true);
        }).catch((error: any) => {
          console.error(error);
          this.misc.doMessage(error, "error");
          reject(error);
        });
      });
    });
  }

  goSection(menu_: string, submenu_: any, header_: string, description_: string) {
    if (!submenu_ || submenu_ !== this.submenu) {
      this.menu = menu_;
      this.submenu = submenu_;
      this.header = header_ ? header_ : "dashboard";
      this.header_desc = description_ ? description_ : "Welcome to Technoplatz BI";
      this.pivot_ = null;
      this.submenu ? this.location.replaceState("/" + this.router.url.split("/")[1] + "/" + this.menu + "/" + this.submenu) : this.location.replaceState("/" + this.router.url.split("/")[1] + "/" + this.menu);
      if (menu_ === "collections" || menu_ === "admin") {
        menu_ === "admin" ? this.view_mode[this.id] = false : null;
        this.is_loaded = this.is_selected = false;
        if (submenu_ !== this.id) {
          this.doSetCollectionID(submenu_).then(() => {
            this.is_crud = this.id.charAt(0) === "_" ? false : true;
            this.storage.get("LSFILTER_" + this.id).then((LSFILTER_: any) => {
              this.storage.get("LSSEARCHED_" + this.id).then((LSSEARCHED_: any) => {
                this.filter = LSFILTER_ && LSFILTER_.length > 0 ? LSFILTER_ : [];
                LSSEARCHED_ ? this.searched = LSSEARCHED_ : null;
                this.actions = [];
                this.RefreshData(0).then(() => { }).catch((error: any) => {
                  console.error(error);
                  this.misc.doMessage(error, "error");
                });
              });
            });
          });
        } else {
          this.is_loaded = true;
        }
      } else if (menu_ === "dashboard") {
        this.is_loaded = true;
      } else if (menu_ === "setup") {
        this.options = new JsonEditorOptions();
        this.options.modes = ["code", "tree"];
        this.options.mode = "code";
        this.options.statusBar = true;
      }
    }
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
      this.is_crud = this.id.charAt(0) === "_" ? false : true;
      this.storage.get("LSSEARCHED_" + this.id).then((LSSEARCHED_: any) => {
        this.storage.get("LSSAVEDFILTER").then((LSSAVEDFILTER: any) => {
          this.doGetViewMode().then(() => {
            this.views_pane = this.views.filter((obj: any) => obj.vie_collection_id === this.id);
            this.searched = LSSEARCHED_ ? LSSEARCHED_ : null;
            this.saved_filter = LSSAVEDFILTER ? LSSAVEDFILTER : null;
            this.storage.get("LSFILTER_" + this.id).then((LSFILTER_: any) => {
              this.filter = LSFILTER_ && LSFILTER_.length > 0 ? LSFILTER_ : [];
              this.count = 0;
              this.page = p === 0 ? 1 : p;
              this.crud.Find(
                "find",
                this.id,
                null,
                this.filter && this.filter.length > 0 ? this.filter : [],
                this.sort,
                this.page,
                this.limit).then((res: any) => {
                  this.data = res.data;
                  this.structure = res.structure;
                  this.actions = this.structure && this.structure.actions ? this.structure.actions : [];
                  this.properites_ = res.structure && res.structure.properties ? res.structure.properties : null;
                  this.columns_ = [];
                  if (this.properites_) {
                    this.getColumns().then(() => {
                      this.columns_ = Object.keys(this.structure.properties).filter((key: any) => !this.structure.properties[key].hidden).reduce((obj, key) => { obj[key] = this.structure.properties[key]; return obj; }, {});
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
                  }
                }).catch((error: any) => {
                  console.error(error);
                  this.misc.doMessage(error, "error");
                  this.is_loaded = true;
                  reject(error);
                });
            });
          }).catch((error: any) => {
            console.error(error);
            this.misc.doMessage(error, "error");
            this.is_loaded = true;
            reject(error);
          });
        });
      });
    });
  }

  doImport() {
    const storage_structure_ = {
      "properties": {
        "sto_id": {
          "bsonType": "string",
          "minLength": 3,
          "maxLength": 32,
          "pattern": "^[a-z0-9-]{3,32}$",
          "title": "ID",
          "description": "Storage ID",
          "permanent": true,
          "required": true,
          "width": 160
        },
        "sto_collection_id": {
          "bsonType": "string",
          "minLength": 3,
          "maxLength": 32,
          "pattern": "^[a-z0-9-_]{3,32}$",
          "title": "Collection",
          "description": "Collection ID",
          "collection": true,
          "required": true,
          "width": 110
        },
        "sto_file": {
          "bsonType": "string",
          "minLength": 0,
          "maxLength": 64,
          "file": true,
          "title": "File",
          "description": "File name",
          "width": 100
        }
      },
      "required": [
        "sto_id",
        "sto_collection_id",
        "sto_file"
      ],
      "unique": [
        [
          "sto_id"
        ],
        [
          "sto_collection_id"
        ]
      ],
      "index": [
        [
          "sto_collection_id"
        ]
      ],
      "sort": {
        "_modified_at": -1
      }
    }
    this.doQuitViewMode();
    this.modal.create({
      component: CrudPage,
      backdropDismiss: false,
      cssClass: "crud-modal",
      componentProps: {
        shuttle: {
          op: "import",
          collection: "_storage",
          collections: this.collections ? this.collections : [],
          views: this.views ? this.views : [],
          user: this.user,
          data: {
            "sto_collection_id": this.id,
            "sto_file": null,
            "sto_id": "data-import",
            "sto_prefix": "ano"
          },
          structure: storage_structure_,
          sweeped: [],
          filter: { "sto_collection_id": this.id },
          actions: [],
          direct: -1
        }
      },
      swipeToClose: true,
    }).then((modal: any) => {
      modal.present();
      modal.onDidDismiss().then((res: any) => {
        if (res.data.modified) {
          this.RefreshData(0);
        }
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
        swipeToClose: true,
        componentProps: {
          shuttle: {
            op: op,
            collection: collection_,
            collections: this.collections ? this.collections : [],
            views: this.views ? this.views : [],
            user: this.user,
            data: data_,
            structure: collection_ === "_view" && this.views && this.views_structure ? this.views_structure : collection_ === "_visual" && this.visuals && this.visuals_structure ? this.visuals_structure : [],
            direct: -1
          }
        }
      });
      modal.onDidDismiss().then((res: any) => {
        if (res.data.modified) {
          if (collection_ === "_view") {
            if (this.menu !== "dashboard") {
              this.doEnterViewMode(data_).then(() => {
                this.doGetViews();
              });
            } else {
              this.doGetViews();
            }
          } else if (collection_ === "_visual") {
            if (data_) {
              this.doGetVisual(data_, ix_);
            }
          }
        }
      });
      return await modal.present();
    }
  }

  MultiCrud(op: string) {
    if (this.perm && this.data.length > 0 && this.is_selected) {
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
                    this.is_loaded = true;
                    this.page = environment.misc.default_page;
                    this.RefreshData(0);
                  }).catch((error: any) => {
                    this.is_loaded = true;
                    console.error(error);
                    this.misc.doMessage(error, "error");
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
          view: this.view
        }
      },
      swipeToClose: true,
    });
    modal.onDidDismiss().then((res: any) => {
      if (res.data.modified) {
        op === "action" ? this.doClearFilter() : this.RefreshData(0);
        if (this.id === "_collection") {
          this.crud.getCollections().then(() => { }).catch((error: any) => {
            console.error(error);
            this.misc.doMessage(error, "error");
          });
        } else if (this.id === "_view") {
          this.doRefreshDash().then(() => { }).catch((error: any) => { });
        }
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
      this.crud.Find("find", "_collection", null, [{
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
          },
          swipeToClose: true
        }).then((modal: any) => {
          modal.present();
          modal.onDidDismiss().then((res: any) => {
            if (res.data.modified) {
              if (this.master.collection === "_collection") {
                this.crud.getCollections().then(() => { }).catch((error: any) => {
                  console.error(error);
                  this.misc.doMessage(error, "error");
                });
              }
              res.data.op === "remove" ? this.nav.navigateRoot("/console").then(() => { }).catch((error: any) => {
                console.error(error);
                this.misc.doMessage(error, "error");
              }) : this.RefreshData(0);
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

  doSegmentChanged(ev: any) {
    this.menu === "collections" ? this.pane_segval_colls = ev.detail.value : this.pane_segval_dash = ev.detail.value;
  }

  doSaveAsView() {
    if (this.perm && this.data.length > 0) {
      this.crud.SaveAsView(this.id, this.filter).then((res: any) => {
        this.doEnterViewMode(res.view).then(() => {
          this.doGetViews();
          this.misc.doMessage("view saved successfully " + res.id, "success");
        });
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
    if (this.perm && this.filter.length > 0 && this.data.length > 0) {
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

  async doAnnounceNow(view: any, scope: string) {
    if (this.perm && !this.in_otp_process) {
      scope === "live" ? this.in_otp_process = true : this.in_otp_process_test = true;
      this.doOTP({
        op: "request"
      }).then(() => {
        this.in_otp_process = this.in_otp_process_test = false;
        this.alert.create({
          cssClass: "my-custom-class",
          header: scope === "live" ? "Announce Now!" : "TEST Announcement: This will be sent to internal Managers and Administrators only!",
          subHeader: scope === "live" ? "Please enter your OTP to confirm this announcement outside of the scheduled times." : "Please enter your OTP to confirm.",
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
              handler: () => { }
            }, {
              text: "CONFIRM",
              handler: (announceData: any) => {
                this.crud.AnnounceNow(view, announceData && announceData.id ? announceData.id : null, scope).then(() => {
                  this.crud.getAnnouncements();
                  this.misc.doMessage("view was announced successfully", "success");
                }).catch((error: any) => {
                  this.misc.doMessage(error, "error");
                  console.error(error);
                });
                // return false;
              }
            }
          ]
        }).then((alert: any) => {
          alert.present();
        });
      }).catch((error: any) => {
        this.in_otp_process = this.in_otp_process_test = false;
        console.error(error);
        this.misc.doMessage(error, "error");
      });
    }
  }

  doApiKeyEnabled() {
    if (!this.is_apikey_enabled) {
      this.is_apikey_enabled = true;
      setTimeout(() => {
        this.is_apikey_enabled = false;
      }, 5000);
    }
  }

  doAccount(s: string) {
    return new Promise((resolve, reject) => {
      this.auth.Account(s).then((res: any) => {
        if (s === "apikeygen" || s === "apikeyget") {
          this.accountf_apikey = res && res.user && res.user.apikey ? res.user.apikey : null;
          this.accountf_apikeydate = res && res.user && res.user.apikey_modified_at ? res.user.apikey_modified_at.$date : null;
          s === "apikeygen" ? this.doApiKeyEnabled() : null;
        }
        resolve(true);
      }).catch((error: any) => {
        this.qr_exists = false;
        console.error(error);
        this.misc.doMessage(error, "error");
      });
    });
  }

  doOTP(obj: any) {
    return new Promise((resolve, reject) => {
      this.otp_qr = null;
      const op_ = obj && obj.op ? obj.op : null;
      if (op_) {
        if (op_ === "hide") {
          this.otp_show = false;
          resolve(true);
        } else {
          this.auth.OTP(obj).then((res: any) => {
            if (res && res.result) {
              this.otp_qr = res.qr;
              if (op_ === "reset" || op_ === "show") {
                this.otp_show = true;
                resolve(true);
              } else if (op_ === "validate") {
                if (res.success) {
                  this.otp_show = false;
                  this.misc.doMessage("OTP validated successfully", "success");
                  resolve(true);
                } else {
                  this.otp_show = false;
                  const err_ = "OTP does not match";
                  this.misc.doMessage(err_, "error");
                  console.error(err_);
                  reject(err_);
                }
              } else if (op_ === "request") {
                this.misc.doMessage("Backup OTP was sent by email", "success");
                resolve(true);
              } else {
                const err_ = "invalid operation";
                console.error(err_);
                this.misc.doMessage(err_, "error");
                reject(err_);
              }
            } else {
              this.misc.doMessage(res.msg, "error");
              reject(res.msg);
            }
          }).catch((error: any) => {
            this.otp_show = false;
            console.error(error);
            this.misc.doMessage(error, "error");
            reject(error);
          });
        }
      }
    });
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

  doResetOTP() {
    this.alert.create({
      header: "Warning",
      subHeader: "One-Time Password Reset",
      message: "Your current QR code will be removed and a new QR code will be generated. This means you will not be able to Login with the existing QR code until you activate the new code.",
      buttons: [
        {
          text: "CANCEL",
          role: "cancel",
          cssClass: "allert",
          handler: () => { }
        }, {
          text: "OKAY",
          handler: () => {
            this.doOTP({
              op: "reset"
            });
          }
        }
      ]
    }).then((alert: any) => {
      alert.present();
    });
  }

  doValidateOTP() {
    this.alert.create({
      cssClass: "my-custom-class",
      subHeader: "Validate One-Time Password",
      message: "Please enter the current one time password generated by App",
      inputs: [
        {
          name: "id",
          value: null,
          type: "number",
          placeholder: "Enter current OTP"
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
          handler: (alertData: any) => {
            this.doOTP({
              op: "validate",
              otp: alertData.id
            });
          }
        }
      ]
    }).then((alert: any) => {
      alert.present();
    });
  }

  async doClearFilter() {
    this.storage.remove("LSFILTER_" + this.id).then(() => {
      this.storage.remove("LSSEARCHED_" + this.id).then(() => {
        this.storage.remove("LSSAVEDFILTER").then(() => {
          this.doResetSearch(true);
          this.sort = {};
          this.saved_filter = null;
          this.filter = [];
          this.sweeped[this.segment] = [];
          this.RefreshData(0);
        });
      });
    });
  }

  doCopy(w: string) {
    const s = w === "apikey" ? this.accountf_apikey : w === "view" ? this.viewurl_ : "";
    this.is_apikey_copied = w === "apikey" ? true : false;
    this.is_url_copied = w === "view" || w === "collection" ? true : false;
    this.misc.copyToClipboard(s).then(() => {
      console.log("*** copied");
    }).catch((error: any) => {
      console.error("not copied", error);
    }).finally(() => {
      this.is_apikey_copied = false;
      this.is_url_copied = false;
    });
  }

  setSort(key: string, d: number) {
    this.sort = {};
    this.sort[key] = d;
    this.RefreshData(0);
  }

  doInstallTemplate(item_: any, ix: number) {
    if (!this.templates[ix].processing) {
      this.templates[ix].processing = true;
      this.crud.Template("install", item_).then(() => {
        this.misc.doMessage("template installed successfully", "success");
        this.templates[ix].processing = false;
        this.doRefreshDash().then(() => { }).catch((error: any) => { });
      }).catch((error: any) => {
        this.templates[ix].processing = false;
        console.error(error);
        this.misc.doMessage(error, "error");
      });
    }
  }

  doGetVisual(data: any, v_: number) {
    this.views[v_].loading = true;
    this.crud.Visual("_visual", data._id, this.accountf_apikey).then((chart: any) => {
      this.views[v_].chart = chart;
    }).catch((error: any) => {
      this.views[v_].chart = {};
      this.visuals[v_].error = error;
    }).finally(() => {
      this.views[v_].loading = false;
    });
  }

  doGetViews() {
    this.crud.getViews().then((res: any) => {
      if (res && res.data && res.structure) {
        this.views = res.data;
        this.views_structure = res.structure;
        this.views_dash = this.views.filter((obj: any) => obj.vie_dashboard);
        this.views_pane = this.views.filter((obj: any) => obj.vie_collection_id === this.id);
        for (let v_ = 0; v_ < res.data.length; v_++) {
          this.doGetVisual(res.data[v_], v_);
        }
      }
    }).catch((error: any) => {
      console.error(error);
      this.misc.doMessage(error, "error");
    });
  }

  doShowPivot() {
    this.is_pivot_showed = this.is_pivot_showed ? false : true;
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

  doTheme(LSTHEME: any) {
    this.storage.set("LSTHEME", LSTHEME).then(() => {
      document.documentElement.style.setProperty("--ion-color-primary", LSTHEME.color);
    });
  }

  doSetSearchItemOp(k: string, op: string) {
    this.searched[k].op = op;
  }

  doMenuToggle() {
    this.menu_toggle = !this.menu_toggle;
  }

  doSetStructure() {
    if (this.perm) {
      this.crud.SetStructure(this.id).then((res: any) => {
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

  doResizeCharts(size: string) {
    this.chart_size = size === "S" ? "small" : size === "M" ? "medium" : size === "L" ? "large" : "small";
    this.storage.set("LSCHARTSIZE", this.chart_size).then(() => {
      this.chart_css = "chart-sq " + this.chart_size;
      this.is_show_resize = false;
    });
  }

}
