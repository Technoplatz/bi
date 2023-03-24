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
import { environment } from "../../../environments/environment";
import { Miscellaneous } from "../../classes/misc";
import { Auth } from "../../classes/auth";
import { Crud } from "../../classes/crud";

@Component({
  selector: "app-menu",
  templateUrl: "./menu.component.html",
  styleUrls: ["./menu.component.scss"],
})

export class MenuComponent implements OnInit {
  public version = environment.appVersion;
  public release = environment.release;
  public collections_: any;
  public collections: any = [];
  public views_: any;
  public views: any = [];
  public segmentsadm: any;
  public saas_: any;
  public user_: any;

  constructor(
    public misc: Miscellaneous,
    private auth: Auth,
    private crud: Crud
  ) { }

  ngOnInit() {
    this.collections_ = this.crud.collections.subscribe((res: any) => {
      res && res.data ? this.collections = res.data : null;
    });
    this.views_ = this.crud.views.subscribe((res: any) => {
      res && res.data ? this.views = res.data : null;
    });
    this.crud.saas.subscribe((res: any) => {
      this.saas_ = res;
    });
    this.auth.user.subscribe((res: any) => {
      this.user_ = res;
      this.segmentsadm = res && res.perm ? environment.segmentsadm : [];
    });
  }

  ngOnDestroy() {
    this.collections_ = null;
    this.views_ = null;
  }

  Signout() {
    this.auth.Signout().then(() => {
      console.log("*** signed out");
    }).catch((error: any) => {
      console.error(error);
    });
  }

}
