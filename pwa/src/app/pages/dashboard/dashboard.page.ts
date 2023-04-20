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

import { Component, OnInit } from "@angular/core";
import { Storage } from "@ionic/storage";
import { Crud } from "../../classes/crud";
import { Miscellaneous } from "../../classes/misc";

@Component({
  selector: "app-dashboard",
  templateUrl: "./dashboard.page.html",
  styleUrls: ["./dashboard.page.scss"]
})

export class DashboardPage implements OnInit {
  public id: string = "";
  public data: any = [];
  public flashcards: any = [];
  public chart_size: string = "small";
  public chart_css: string = "chart-sq small";
  public is_refreshing: boolean = false;
  public view: any = null;
  public chart: any = null;
  public announcements: any = [];
  public announcements_: any = null;
  public charts_: any = null;
  public charts: any = [];

  constructor(
    private storage: Storage,
    private crud: Crud,
    public misc: Miscellaneous
  ) {
    this.charts_ ? null : this.charts_ = this.crud.charts.subscribe((res: any) => {
      this.charts = res && res.views ? res.views.filter((obj: any) => obj.view.chart_type !== "Flashcard") : [];
      this.flashcards = res && res.views ? res.views.filter((obj: any) => obj.view.chart_type === "Flashcard") : [];
      console.log("*** charts", this.charts);
    });
    this.announcements_ ? null : this.crud.announcements.subscribe((res: any) => {
      this.announcements = res && res.data ? res.data : [];
    });
  }

  ngOnInit() {
    this.storage.get("LSCHARTSIZE").then((LSCHARTSIZE: any) => {
      this.chart_size = LSCHARTSIZE ? LSCHARTSIZE : "small";
      this.chart_css = "chart-sq " + this.chart_size;
    });
  }

  doRefresh() {
    this.is_refreshing = true;
    this.crud.getAll().then(() => { }).catch((error: any) => {
      this.misc.doMessage(error, "error");
    }).finally(() => {
      this.is_refreshing = false;
    });
  }

  doResizeCharts() {
    this.chart_size = this.chart_size === "small" ? "medium" : this.chart_size === "medium" ? "large" : this.chart_size === "large" ? "small" : "small";
    this.storage.set("LSCHARTSIZE", this.chart_size).then(() => {
      this.chart_css = "chart-sq " + this.chart_size;
    });
  }

  doImport() {
    this.misc.doImport(null).then((id: any) => {
      this.misc.navi.next("collection/" + id);
    });
  }

}
