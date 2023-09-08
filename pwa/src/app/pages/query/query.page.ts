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
import { Router } from "@angular/router";
import { Storage } from "@ionic/storage";
import { Crud } from "../../classes/crud";
import { Auth } from "../../classes/auth";
import { Miscellaneous } from "../../classes/misc";
import { environment } from "../../../environments/environment";
import { JsonEditorOptions, JsonEditorComponent } from "ang-jsoneditor";

@Component({
  selector: "app-query",
  templateUrl: "./query.page.html",
  styleUrls: ["./query.page.scss"]
})

export class QueryPage implements OnInit {
  @ViewChild(JsonEditorComponent, { static: false }) editor: JsonEditorComponent = new JsonEditorComponent;
  public jeoptions: JsonEditorOptions;
  public default_width: number = environment.misc.defaultColumnWidth;
  public header: string = "QUERIES";
  public subheader: string = "";
  public loadingText: string = environment.misc.loadingText;
  private submenu: string = "";
  public user: any = null;
  public perm: boolean = false;
  public id: string = "";
  public data_: any = [];
  public pages: any = [];
  public limit_: number = environment.misc.limit;
  public count_: number = 0;
  public is_loaded: boolean = true;
  public is_initialized: boolean = false;
  public status_: any = {};
  public columns_: any;
  public view_mode: any = {};
  private menu: string = "";
  public schema_key: any = null;
  public fields_: any = {};
  public is_saving: boolean = false;
  public is_deleting: boolean = false;
  public sort: any = {};
  public schemevis: any = "hide";
  public aggregate_: any = [];
  private aggregated_: any = [];
  public is_key_copied: boolean = false;
  public is_key_copying: boolean = false;
  public templates: any = [];
  public is_inprogress: boolean = false;
  public menutoggle: boolean = false;
  public is_url_copied: boolean = false;
  public query_url_: string = "";
  public pages_: number = 1;
  private page_start_: number = 1;
  private page_end_: number = 1;
  public page_: number = 1;
  public paget_: any = [];

  constructor(
    private storage: Storage,
    private auth: Auth,
    private crud: Crud,
    private router: Router,
    public misc: Miscellaneous
  ) {
    this.jeoptions = new JsonEditorOptions();
    this.jeoptions.modes = ["tree", "code", "text"]
    this.jeoptions.mode = "code";
    this.jeoptions.statusBar = true;
    this.jeoptions.enableSort = false;
    this.jeoptions.expandAll = false;
    this.jeoptions.navigationBar = true;
    this.jeoptions.name = "aggregate";
  }

  ngOnDestroy() {
    this.auth.user.unsubscribe;
  }

  ngOnInit() {
    this.misc.getAPIUrl().then((apiHost: any) => {
      this.menu = this.router.url.split("/")[1];
      this.id = this.submenu = this.router.url.split("/")[2];
      this.query_url_ = apiHost + "/get/query/" + this.id;
      this.RefreshData(1).then(() => {
        this.is_initialized = true;
      });
    });
  }

  RefreshData(page_: number) {
    return new Promise((resolve, reject) => {
      this.is_loaded = false;
      this.page_ = page_ === 0 ? 1 : page_;
      this.crud.getQuery(this.id, this.page_, this.limit_).then((res: any) => {
        if (res && res.query) {
          this.subheader = res.query.que_title;
          this.aggregate_ = res.query.que_aggregate;
          this.fields_ = res.fields;
          this.data_ = res.data;
          this.count_ = res.count;
          this.pages_ = this.count_ > 0 ? Math.ceil(this.count_ / this.limit_) : environment.misc.default_page;
          const lmt = this.pages_ >= 10 ? 10 : this.pages_;
          this.paget_ = new Array(lmt);
          this.page_start_ = this.page_ > 10 ? this.page_ - 10 + 1 : 1;
          this.page_end_ = this.page_start_ + 10;
          for (let p = 0; p < this.paget_.length; p++) {
            this.paget_[p] = this.page_start_ + p;
          }
          resolve(true);
        } else {
          this.misc.doMessage("no data found", "error");
          reject();
        }
      }).finally(() => {
        this.is_loaded = true;
        this.is_initialized = true;
      });
    });
  }

  orderByIndex = (a: any, b: any): number => {
    return a.value.index < b.value.index ? -1 : (b.value.index > a.value.index ? 1 : 0);
  }

  show_aggregation(shw: boolean) {
    if (shw) {
      this.editor.setMode(this.jeoptions.mode);
      this.schemevis = "show";
      this.editor.focus();
    } else {
      this.RefreshData(0).then(() => {
        this.schemevis = "hide"
        this.aggregated_ ? this.misc.doMessage("changes were discarded", "warning") : null;
        this.aggregated_ = null;
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

  save_query() {
    if (this.aggregated_) {
      this.is_saving = true;
      this.misc.apiCall("/crud", {
        op: "savequery",
        id: this.id,
        aggregate: this.aggregated_
      }).then(() => {
        this.misc.doMessage("query saved successfully", "success");
        this.RefreshData(0).then(() => {
          this.schemevis = "hide"
        });
      }).catch((error: any) => {
        this.misc.doMessage(error, "error");
      }).finally(() => {
        this.aggregated_ = null;
        this.is_saving = false;
      });
    } else {
      this.misc.doMessage("no changes detected in query", "warning");
    }
  }

  aggregate_changed(ev: any) {
    if (!ev.isTrusted) {
      this.aggregated_ = ev;
    } else {
      console.error("*** event", ev);
    }
  }

  copy_url(tocopy_: string) {
    this.is_url_copied = ["view", "collection"].includes(tocopy_) ? true : false;
    this.misc.copyToClipboard(this.query_url_).then(() => { }).catch((error: any) => {
      console.error("*** copy error", error);
    }).finally(() => {
      this.is_url_copied = false;
    });
  }

}