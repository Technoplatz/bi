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
import { TranslateService } from "@ngx-translate/core";
import { Router } from "@angular/router";
import { Storage } from "@ionic/storage";
import { Miscellaneous } from "./classes/misc";
import { Auth } from "./classes/auth";
import { Crud } from "./classes/crud";
import { Su } from "./classes/su";
import { environment } from "../environments/environment";

@Component({
  selector: "app-root",
  templateUrl: "app.component.html",
  styleUrls: ["app.component.scss"]
})

export class AppComponent implements OnInit {
  public user_: any = null;
  public net_: boolean = true;
  private paginations_ = environment.paginations;

  constructor(
    private translate: TranslateService,
    private router: Router,
    private auth: Auth,
    private crud: Crud,
    private misc: Miscellaneous,
    private storage: Storage,
    private su: Su
  ) {
    // auth
    this.auth.user.subscribe((user: any) => {
      this.user_ = user;
    });
    // version check
    this.su.checkForUpdates();
    // pagination
    this.storage.get("LSPAGINATION").then((LSPAGINATION: any) => {
      !LSPAGINATION ? this.storage.set("LSPAGINATION", this.paginations_[1]).then(() => { }) : null;
    });
    // navi
    this.misc.navi.subscribe((path: any) => {
      this.router.navigateByUrl(path).then(() => { }).catch((error: any) => {
        console.error(error);
      });
    });
    // theme
    this.storage.get("LSTHEME").then((LSTHEME: any) => {
      document.documentElement.style.setProperty("--ion-color-primary", LSTHEME ? LSTHEME.color : environment.themes[0].color);
    });
  }

  ngOnInit() {
    "serviceWorker" in navigator ? navigator.serviceWorker.getRegistrations().then((regs_: any) => {
      if (regs_.length) {
        for (let reg_ of regs_) { reg_.unregister(); }
      }
    }) : null;
    this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
      this.auth.user.next(LSUSERMETA);
      LSUSERMETA ? this.crud.get_all().then(() => { }).catch((error: any) => {
        this.misc.doMessage(error, "error");
      }) : null;
      this.misc.getLanguage().then((res: any) => {
        this.translate.setDefaultLang(res ? res : "en");
        this.translate.use(res ? res : "en");
      }).catch((error: any) => {
        console.error(error);
      });
    });
  }

}
