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

import { Component, OnInit, ViewChild } from "@angular/core";
import { ModalController, IonSelect } from "@ionic/angular";
import { Storage } from "@ionic/storage";
import { Crud } from "../../classes/crud";
import { Miscellaneous } from "../../classes/miscellaneous";
import { environment } from "../../../environments/environment";
import { CrudPage } from "../crud/crud.page";
import { JsonEditorComponent, JsonEditorOptions } from "ang-jsoneditor";

@Component({
  selector: "app-dashboard",
  templateUrl: "./dashboard.page.html",
  styleUrls: ["./dashboard.page.scss"]
})

export class DashboardPage implements OnInit {
  @ViewChild(JsonEditorComponent, { static: false }) public strcutureEditor?: JsonEditorComponent;
  @ViewChild("select0") selectRef?: IonSelect;
  public header: string = "Dashboard";
  public now: any = Date.now();
  public version = environment.appVersion;
  public release = environment.release;
  public loadingText: string = environment.misc.loadingText;
  public menu: string = "";
  public submenu: string = "";
  public segment = "data";
  public user: any = null;
  public themes: any = environment.themes;
  public limits: any = environment.misc.limits;
  public perm: boolean = false;
  public is_crud: boolean = false;
  public in_otp_process: boolean = false;
  public in_otp_process_test: boolean = false;
  public paget: any = [];
  public id: string = "";
  public sortstr: any;
  public ok: boolean = false;
  public template_showed: boolean = false;
  public reconfig: boolean = false;
  public filter: any = [];
  public saved_filter: string = "";
  public selected_view: any;
  public searched: any = null;
  public data: any = [];
  public structure: any = [];
  public selected: any = [];
  public announcements: any = [];
  public views: any = [];
  public viewsx: any = [];
  public views_dash: any = [];
  public views_pane: any = [];
  public flashcards: any = [];
  public visuals: any = [];
  public kpis: any = [];
  public metrics: any = [];
  public pages: any = [];
  public limit: number = environment.misc.limit;
  public page: number = 1;
  public page_start: number = 1;
  public page_end: number = 1;
  public count: number = 0;
  public chart_size: string = "small";
  public chart_css: string = "";
  public flash_css: string = "";
  public is_loaded: boolean = true;
  public is_refreshing: boolean = false;
  public is_selected: boolean = false;
  public is_show_resize: boolean = false;
  public is_pivot_loading: boolean = false;
  public pivot_: string = "";
  public statistics_key_: string = "";
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
  public accountf_apikey: string = "";
  public accountf_apikeydate: any = null;
  public accountf_description: string = "";
  public accountf_qrurl: string = "";
  public is_processing_account: boolean = false;
  public is_visuals_loading: boolean = false;
  public barcoded_: boolean = false;
  public is_samecol: boolean = false;
  public qr_exists: boolean = false;
  public qr_show: boolean = false;
  public otp_show: boolean = false;
  public otp_qr: string = "";
  public dashmode: string = "card";
  public viewurl_: string = "";
  public viewurl_masked_: string = "";
  public view: any = null;
  public visual: any = null;
  public view_id: string = "";
  public visual_id: string = "";
  public view_data: any = [];
  public view_df: any = [];
  public view_count: number = 0;
  public view_properties: any = [];
  public view_properties_: any = [];
  public subscribers: string = "";
  public scheduled: boolean = false;
  public viewtab: string = "pivot";
  public actions: any = [];
  public vie_projection: any = [];
  public columns_: any;
  public chart: any = null;
  public class_left_side: string = "console-left-side hide-scrollbar";
  public menu_toggle: boolean = false;
  public view_mode: any = {};
  public pane_segval_colls: string = "collection";
  public pane_segval_dash: string = "dash";
  public options?: JsonEditorOptions;
  public options2?: JsonEditorOptions;
  public announcementso: any;
  private views_structure: any;
  private collections_structure: any;
  private apiHost: string = "";
  public viewso: any;
  private collectionso: any;

  constructor(
    private storage: Storage,
    private crud: Crud,
    private misc: Miscellaneous,
    private modal: ModalController
  ) { }

  ngOnDestroy() {
    this.announcementso = null;
    this.collectionso = null;
    this.viewso = null;
  }

  ngOnInit() {
    this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
      this.user = LSUSERMETA;
      this.perm = LSUSERMETA && LSUSERMETA.perm ? true : false;
      this.accountf_apikey = LSUSERMETA.apikey;

      // collections subscribe
      this.collectionso = this.crud.collections.subscribe((res: any) => {
        this.collections = res && res.data ? res.data : [];
        this.collections_structure = res.structure;
      });

      // announcements subscribe
      this.announcementso = this.crud.announcements.subscribe((res: any) => {
        this.announcements = res && res.data ? res.data : [];
      });

      // get announcements
      this.crud.getAnnouncements().then(() => {});

      this.viewso = this.crud.views.subscribe((res: any) => {
        this.views = this.viewsx = res && res.data ? res.data : [];
        this.views_structure = res && res.structure ? res.structure : null;
        if (this.views.length > 0) {
          this.views_dash = this.views.filter((obj: any) => obj.vie_dashboard && obj.vie_visual_style !== "Flashcard");
          this.flashcards = this.views.filter((obj: any) => obj.vie_dashboard && obj.vie_visual_style === "Flashcard");
          this.visuals = [];
          this.storage.get("LSCHARTSIZE").then((LSCHARTSIZE: any) => {
            this.chart_size = LSCHARTSIZE ? LSCHARTSIZE : "small";
            this.flash_css = "flash-sq";
            this.chart_css = "chart-sq " + this.chart_size;
            for (let v_ = 0; v_ < this.views.length; v_++) {
              this.doGetVisual(this.views[v_], v_);
            }
          });
        }
      });

    });
  }

  doRefresh() {
    this.is_refreshing = true;
    this.crud.getAll().then(() => { }).catch((error: any) => {
      console.error(error);
      this.misc.doMessage(error, "error");
    }).finally(() => {
      this.is_refreshing = false;
    });
  }

  doEnterViewMode(view_: any) {
    this.misc.navi.next({
      s: "view",
      sub: view_.vie_id,
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
        if (type_ === "upload") {
          // go collection
        }
      });
    });
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
            structure: collection_ === "_view" ? this.views_structure : collection_ === "_collection" ? this.collections_structure : this.collections_structure,
            direct: -1
          }
        }
      });
      modal.onDidDismiss().then((res: any) => {
        if (res.data.modified) {
          this.doRefresh();
        }
      });
      return await modal.present();
    }
  }

  doGetVisual(data: any, v_: number) {
    this.views[v_].loading = true;
    this.views[v_].error = null;
    if (this.accountf_apikey) {
      this.crud.Visual(data._id, this.accountf_apikey).then((chart: any) => {
        this.views[v_].visual = chart;
      }).catch((error: any) => {
        this.views[v_].visual = {};
        this.visuals[v_].error = error;
      }).finally(() => {
        this.views[v_].loading = false;
      });
    } else {
      const error_ = "Please create an API key in the Preferences section";
      this.views[v_].visual = {};
      this.views[v_].error = error_;
      console.error(error_);
      this.misc.doMessage(error_, "error");
    }
  }

  doStartSearch(e: any) {
    this.viewsx = this.views;
    this.viewsx = this.viewsx.filter((obj: any) => (obj["vie_id"] + obj["vie_title"]).toLowerCase().indexOf(e.toLowerCase()) > -1);
  }

  doResizeCharts() {
    this.storage.get("LSCHARTSIZE").then((LSCHARTSIZE: string) => {
      this.chart_size = LSCHARTSIZE === "small" ? "medium" : LSCHARTSIZE === "medium" ? "large" : LSCHARTSIZE === "large" ? "small" : "small";
      this.storage.set("LSCHARTSIZE", this.chart_size).then(() => {
        this.chart_css = "chart-sq " + this.chart_size;
        this.is_show_resize = false;
      });
    });
  }

}
