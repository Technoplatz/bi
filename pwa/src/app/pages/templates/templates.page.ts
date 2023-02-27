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
import { Miscellaneous } from "../../classes/miscellaneous";
import { Crud } from "../../classes/crud";

@Component({
  selector: "app-templates",
  templateUrl: "./templates.page.html",
  styleUrls: ["./templates.page.scss"]
})

export class TemplatesPage implements OnInit {
  public header: string = "Templates";
  public templates: any = [];
  public is_initialized: boolean = false;
  public user: any = null;

  constructor(
    private misc: Miscellaneous,
    private crud: Crud,
    private storage: Storage
  ) { }

  ngOnDestroy() { }

  ngOnInit() {
    this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
      this.user = LSUSERMETA;
      this.crud.Template("list", null).then((res: any) => {
        this.templates = res && res.data ? res.data : [];
        this.is_initialized = true;
      }).catch((error: any) => {
        console.error(error);
        this.misc.doMessage(error, "error");
      });
    });
  }

  doNavi(s: string, sub: any) {
    this.misc.navi.next({
      s: s,
      sub: sub,
    });
  }

  doInstallTemplate(item_: any, ix: number) {
    if (!this.templates[ix].processing) {
      this.templates[ix].processing = true;
      this.crud.Template("install", item_).then(() => {
        this.misc.doMessage("template installed successfully", "success");
      }).catch((error: any) => {
        console.error(error);
        this.misc.doMessage(error, "error");
      }).finally(() => {
        this.templates[ix].processing = false;
      });
    }
  }

}
