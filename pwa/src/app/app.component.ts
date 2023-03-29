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
import { NavController } from "@ionic/angular";
import { Router, Event, NavigationError, NavigationEnd, NavigationStart } from "@angular/router";
import { Storage } from "@ionic/storage";
import { Miscellaneous } from "./classes/misc";
import { Auth } from "./classes/auth";
import { Crud } from "./classes/crud";
import { Plugins } from "@capacitor/core";
import { environment } from "../environments/environment";

const { Network } = Plugins;

@Component({
  selector: "app-root",
  templateUrl: "app.component.html",
  styleUrls: ["app.component.scss"]
})

export class AppComponent implements OnInit {
  public user_: any = null;
  public swu_: boolean = false;
  public net_: boolean = true;
  public menutoggle: boolean = true;

  constructor(
    private translate: TranslateService,
    private router: Router,
    private auth: Auth,
    private crud: Crud,
    private misc: Miscellaneous,
    private storage: Storage,
    private nav: NavController
  ) { }

  ngOnInit() {
    this.misc.menutoggle.subscribe((res: any) => {
      this.menutoggle = res === undefined ? true : res;
      this.storage.set("LSMENUTOGGLE", res).then(() => { });
    });

    this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
      this.auth.user.next(LSUSERMETA);
      this.misc.user.next(LSUSERMETA);
      if (LSUSERMETA) {
        this.crud.getSaas().then((saas: any) => {
          this.misc.saas.next(saas);
          this.crud.getAll().then(() => { }).catch((error: any) => {
            this.misc.doMessage(error, "error");
          });
        });
      }
    });

    this.auth.user.subscribe((user: any) => {
      this.user_ = user;
      if (!user) {
        this.misc.navi.next("");
      }
    });

    this.misc.navi.subscribe((path: any) => {
      this.nav.navigateRoot(path).then(() => { }).catch((error: any) => {
        console.error(error);
      });
    });

    this.storage.get("LSTHEME").then((res: any) => {
      if (res) {
        document.documentElement.style.setProperty("--ion-color-primary", res.color);
      } else {
        this.storage.set("LSTHEME", environment.themes[0]).then(() => {
          document.documentElement.style.setProperty("--ion-color-primary", environment.themes[0].color);
        });
      }
    });

    this.router.events.subscribe((event: Event) => {
      if (event instanceof NavigationError) {
        console.error("*** navigation error", event.url, event.error);
      } else if (event instanceof NavigationStart) {
      } else if (event instanceof NavigationEnd) {
        const urlpart1_ = event.url.split("/")[1];
        if (!urlpart1_) {
          this.menutoggle = false;
        }
      }
    });

    Network.addListener("networkStatusChange", (status: any) => {
      if (!status.connected) {
        this.net_ = false;
        console.error("*** internet connection is lost");
      } else {
        setTimeout(() => {
          console.log("*** internet connection is back again");
          this.net_ = true;
          location.reload();
        }, 3000);
      }
    });

    this.misc.getLanguage().then((res: any) => {
      this.translate.setDefaultLang(res ? res : "en");
      this.translate.use(res ? res : "en");
    }).catch((error: any) => {
      console.error(error);
    });

    this.storage.get("LSMENUTOGGLE").then((res: any) => {
      this.misc.menutoggle.next(res);
    });

  }

}
