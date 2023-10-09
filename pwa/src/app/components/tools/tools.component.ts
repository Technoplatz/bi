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
import { Miscellaneous } from "../../classes/misc";
import { Storage } from "@ionic/storage";
import { Auth } from "../../classes/auth";

@Component({
  selector: "app-tools",
  templateUrl: "./tools.component.html",
  styleUrls: ["./tools.component.scss"]
})

export class ToolsComponent implements OnInit {
  public name: string = "";
  public is_new_version: boolean = false;
  public new_version_: string = "";

  constructor(
    private auth: Auth,
    public misc: Miscellaneous,
    private storage: Storage
  ) {
    this.misc.version.subscribe((version_: any) => {
      if (version_ && version_.is_new_version) {
        this.is_new_version = true;
        this.new_version_ = version_.version;
      }
    });
  }

  ngOnDestroy() {
    this.misc.version.unsubscribe;
    this.auth.user.unsubscribe;
  }

  ngOnInit() {
    this.auth.user.subscribe((user: any) => {
      this.name = user ? user.name : "";
    });
  }

  set_version() {
    this.storage.set("LSVERSION", this.new_version_).then(() => {
      window.location.replace("/dashboard");
    });
  }

  sign_out() {
    this.auth.sign_out().then(() => { }).catch((error: any) => {
      console.error("signout error", error.msg);
    });
  }

}
