/*
Technoplatz BI

Copyright ©Technoplatz IT Solutions GmbH, Mustafa Mat

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
import { Auth } from "../../classes/auth";

@Component({
  selector: "app-tools",
  templateUrl: "./tools.component.html",
  styleUrls: ["./tools.component.scss"]
})

export class ToolsComponent implements OnInit {
  public user_: any = null;
  public ready_: boolean = false;
  public detected_: boolean = false;

  constructor(
    private auth: Auth,
    public misc: Miscellaneous
  ) {
    this.misc.version.subscribe((version_: any) => {
      this.ready_ = version_.ready ? true : false;
      this.detected_ = version_.detected ? true : false;
    });
  }

  ngOnDestroy() {
    this.auth.user.unsubscribe;
  }

  ngOnInit() {
    this.auth.user.subscribe((user_: any) => {
      this.user_ = user_;
    });
  }

  reload_app() {
    window.location.reload();
  }

}
