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

import { Component, OnInit } from "@angular/core";
import { ModalController } from "@ionic/angular";
import { Router } from "@angular/router";
import { Storage } from "@ionic/storage";
import { Crud } from "../../classes/crud";
import { Auth } from "../../classes/auth";
import { Miscellaneous } from "../../classes/misc";
import { environment } from "../../../environments/environment";
import { JsonEditorOptions } from "ang-jsoneditor";
import { CrudPage } from "../crud/crud.page";

@Component({
  selector: "app-job",
  templateUrl: "./job.page.html",
  styleUrls: ["./job.page.scss"]
})

export class JobPage implements OnInit {
  public jeoptions: JsonEditorOptions = new JsonEditorOptions();
  public default_width: number = environment.misc.defaultColumnWidth;
  public header: string = "JOBS";
  public subheader: string = "";
  public loadingText: string = environment.misc.loadingText;
  public user: any = null;
  public perm: boolean = false;
  public id: string = "";
  public data_: any = [];
  public pages: any = [];
  public limit_: number = environment.misc.limit;
  public count_: number = 0;
  public status_: any = {};
  public columns_: any;
  public _saving: boolean = false;
  public is_deleting: boolean = false;
  public sort: any = {};
  public schemavis_: boolean = false;
  public aggregate_: any = [];
  public is_key_copied: boolean = false;
  public is_key_copying: boolean = false;
  public templates: any = [];
  public is_inprogress: boolean = false;
  public is_url_copied: boolean = false;
  public running_: boolean = false;
  public job_scheduled_cron_: string = "";
  private menu: string = "";
  private submenu: string = "";
  private job_: any = {};
  public perma_: boolean = false;
  private collections_: any = [];
  public json_content_: any = null;
  public col_: string = "";
  private schema_: any = {};

  constructor(
    public misc: Miscellaneous,
    private storage: Storage,
    private auth: Auth,
    private crud: Crud,
    private router: Router,
    private modal: ModalController
  ) {
    this.auth.user.subscribe((res: any) => {
      this.user = res;
      this.perma_ = res.perma;
    });
    this.crud.collections.subscribe((res: any) => {
      this.collections_ = res && res.data ? res.data : [];
    });
  }

  ngOnDestroy() {
    this.auth.user.unsubscribe;
    this.crud.collections.unsubscribe;
  }

  ngOnInit() { }

  ionViewDidEnter() {
    this.storage.get("LSPAGINATION").then((LSPAGINATION: any) => {
      this.limit_ = LSPAGINATION * 1;
      this.storage.get("LSJOB").then((LSJOB_: any) => {
        this.col_ = LSJOB_?.job_collection_id;
        this.job_ = LSJOB_;
        this.menu = this.router.url.split("/")[1];
        this.id = this.subheader = this.submenu = this.router.url.split("/")[2];
        this.refresh_data(false).then(() => { });
      });
    });
  }

  refresh_data(run_: boolean) {
    return new Promise((resolve, reject) => {
      this.running_ = true;
      this.schemavis_ = false;
      this.crud.get_query_job("job", this.id, this.limit_, run_).then((res: any) => {
        if (res && res.job) {
          this.schema_ = res.schema;
          this.job_scheduled_cron_ = res.job?.job_scheduled_cron;
          this.subheader = res.job.job_name;
          this.json_content_ = res.job.job_aggregate;
          this.aggregate_ = res.job.job_aggregate;
          this.count_ = res.count;
          resolve(true);
        } else {
          this.misc.doMessage("no data found", "error");
          reject();
        }
        if (res.err) {
          this.misc.doMessage(res.err, "error");
          reject();
        }
      }).catch((res: any) => {
        this.misc.doMessage(res, "error");
        reject();
      }).finally(() => {
        this.running_ = false;
      });
    });
  }

  json_editor_init() {
    return new Promise((resolve, reject) => {
      this.jeoptions = new JsonEditorOptions();
      this.jeoptions.modes = ["tree", "code", "text"]
      this.jeoptions.mode = "code";
      this.jeoptions.statusBar = this.jeoptions.navigationBar = true;
      this.jeoptions.enableSort = this.jeoptions.expandAll = false;
      resolve(true);
    });
  }

  set_editor(set_: boolean) {
    this.schemavis_ = !this.schemavis_ && set_ && !this.running_;
    set_ ? this.json_editor_init().then(() => { }) : null;
  }

  save_job_json_f(approved_: boolean) {
    if (this.json_content_ && this.json_content_.length > 0) {
      this._saving = true;
      this.aggregate_ = this.json_content_;
      this.misc.api_call("crud", {
        op: "savejob",
        collection: "_job",
        id: this.id,
        aggregate: this.aggregate_,
        approved: approved_
      }).then(() => {
        this.misc.doMessage("job saved successfully", "success");
      }).catch((error: any) => {
        this.misc.doMessage(error, "error");
      }).finally(() => {
        this._saving = false;
      });
    } else {
      this.misc.doMessage("invalid aggregation", "error");
    }
  }

  json_changed(event_: any) {
    !event_.isTrusted ? this.json_content_ = event_ : null;
  }

  run_job() {
    this.refresh_data(true).then(() => {
      console.log("*** jub run");
    });
  }

  async edit_query() {
    const modal = await this.modal.create({
      component: CrudPage,
      backdropDismiss: true,
      cssClass: "crud-modal",
      componentProps: {
        shuttle: {
          op: "update",
          collection: "_job",
          collections: this.collections_,
          views: [],
          user: this.user,
          data: this.job_,
          counters: null,
          structure: this.schema_,
          sweeped: [],
          filter: null,
          actions: [],
          actionix: -1,
          view: null,
          scan: null
        }
      }
    });
    modal.onDidDismiss().then((res: any) => {
      if (res.data.modified && res.data.res.result) {
        this.misc.doMessage("query settings updated successfully", "success");
        this.refresh_data(true);
      }
    });
    return await modal.present();
  }

}