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
import { Router } from "@angular/router";
import { Storage } from "@ionic/storage";
import { Crud } from "../../classes/crud";
import { Auth } from "../../classes/auth";
import { Miscellaneous } from "../../classes/misc";
import { environment } from "../../../environments/environment";
import { JsonEditorOptions } from "ang-jsoneditor";

@Component({
  selector: "app-query",
  templateUrl: "./query.page.html",
  styleUrls: ["./query.page.scss"]
})

export class QueryPage implements OnInit {
  public jeoptions: JsonEditorOptions = new JsonEditorOptions();
  public default_width: number = environment.misc.defaultColumnWidth;
  public header: string = "QUERIES";
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
  public fields_: any = {};
  public _saving: boolean = false;
  public is_deleting: boolean = false;
  public sort: any = {};
  public schemavis_: boolean = false;
  public type_: string = "aggregate";
  public aggregate_: any = [];
  public is_key_copied: boolean = false;
  public is_key_copying: boolean = false;
  public templates: any = [];
  public is_inprogress: boolean = false;
  public is_url_copied: boolean = false;
  public running_: boolean = false;
  public query_url_: string = "";
  public que_scheduled_cron_: string = "";
  public _tags: any = [];
  private menu: string = "";
  private submenu: string = "";
  private query_: any = {};
  private uri_: string = "";
  public perma_: boolean = false;
  private collections_: any = [];
  private schema_: any = {};
  public json_content_: any = null;
  public col_: string = "";

  constructor(
    public misc: Miscellaneous,
    private storage: Storage,
    private auth: Auth,
    private crud: Crud,
    private router: Router
  ) {
    this.misc.api.subscribe((api_: any) => {
      this.uri_ = api_.uri;
    });
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
    this.misc.api.unsubscribe;
    this.crud.collections.unsubscribe;
  }

  ngOnInit() { }

  ionViewDidEnter() {
    this.storage.get("LSPAGINATION").then((LSPAGINATION: any) => {
      this.limit_ = LSPAGINATION * 1;
      this.storage.get("LSQUERY").then((LSQUERY_: any) => {
        this.col_ = LSQUERY_?.que_collection_id;
        this.query_ = LSQUERY_;
        this.type_ = LSQUERY_?.que_type;
        this.menu = this.router.url.split("/")[1];
        this.id = this.subheader = this.submenu = this.router.url.split("/")[2];
        this.query_url_ = `${this.uri_}/get/query/${this.id}`;
        this.refresh_data(false).then(() => { });
      });
    });
  }

  refresh_data(run_: boolean) {
    return new Promise((resolve, reject) => {
      this.running_ = true;
      this.schemavis_ = false;
      this.crud.get_query_job("query", this.id, this.limit_, run_).then((res: any) => {
        if (res.query && res.data) {
          this.schema_ = res.schema;
          this.que_scheduled_cron_ = res.query?.que_scheduled_cron;
          this._tags = res.query?._tags;
          this.subheader = res.query.que_title;
          this.json_content_ = res.query.que_aggregate;
          this.aggregate_ = res.query.que_aggregate;
          this.type_ = res.query.que_type;
          this.fields_ = res.fields;
          this.data_ = res.data;
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
        this.misc.doMessage(res.err, "error");
        reject();
      }).finally(() => {
        this.running_ = false;
      });
    });
  }

  json_editor_init() {
    return new Promise((resolve) => {
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

  save_json_f(approved_: boolean) {
    if (this.json_content_ && this.json_content_.length > 0) {
      this._saving = true;
      this.aggregate_ = this.json_content_;
      this.misc.api_call("crud", {
        op: "savequery",
        collection: "_query",
        id: this.id,
        aggregate: this.aggregate_,
        approved: approved_
      }).then(() => {
        this.misc.doMessage("query saved successfully", "success");
        this.refresh_data(false).then(() => {
          this.schemavis_ = false;
        });
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

  copy_url() {
    this.is_url_copied = false;
    this.misc.copy_to_clipboard(this.query_url_).then(() => {
      this.is_url_copied = true;
    }).catch((error: any) => {
      console.error("*** copy error", error);
    }).finally(() => {
      setTimeout(() => {
        this.is_url_copied = false;
      }, 1000);
    });
  }

  run_query() {
    if (!this.running_) {
      this.running_ = true;
      this.refresh_data(true).then(() => { }).finally(() => {
        this.running_ = false;
      });
    }
  }

}