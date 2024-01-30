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
import { Crud } from "../../classes/crud";
import { Miscellaneous } from "../../classes/misc";
import { Auth } from "../../classes/auth";
import { environment } from "../../../environments/environment";

@Component({
  selector: "app-dashboard",
  templateUrl: "./dashboard.page.html",
  styleUrls: ["./dashboard.page.scss"]
})

export class DashboardPage implements OnInit {
  public announcements_: any = [];
  public loadingText: string = environment.misc.loadingText;
  public flashsizes_: any = environment.flashsizes;
  public visuals_: any = [];
  public perm_: boolean = false;

  constructor(
    private crud: Crud,
    public misc: Miscellaneous,
    private auth: Auth
  ) {
    this.auth.user.subscribe((res: any) => {
      this.perm_ = res && res.perm;
    });
  }

  ngOnInit() {
    this.announcements_ = [];
    this.crud.get_announcements().then((res: any) => {
      this.announcements_ = res.data ? res.data.slice(0, 15) : [];
    });
  }

  ionViewDidEnter() {
    this.crud.get_visuals(null).then((visuals_: any) => {
      this.visuals_ = visuals_.visuals;
      for (let ix_: number = 0; ix_ < this.visuals_.length; ix_++) {
        this.visuals_[ix_].is_loaded = false;
        this.crud.get_visual(this.visuals_[ix_].id).then((visual_: any) => {
          this.visuals_[ix_].data = visual_.visual.data;
          this.visuals_[ix_].fields = visual_.visual.fields;
          this.visuals_[ix_].count = visual_.visual.count;
        }).catch((err_: any) => {
          this.visuals_[ix_].error = err_;
        }).finally(() => {
          this.visuals_[ix_].is_loaded = true;
        });
      }
    });
  }

  orderByIndex = (a: any, b: any): number => {
    return a.value.index < b.value.index ? -1 : (b.value.index > a.value.index ? 1 : 0);
  }

}
