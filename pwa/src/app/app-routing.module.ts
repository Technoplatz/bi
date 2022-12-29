/*
Technoplatz BI

Copyright (C) 2020-2023 Technoplatz IT Solutions GmbH, Mustafa Mat

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

import { NgModule, Injectable } from "@angular/core";
import { PreloadAllModules, RouterModule, Routes, CanActivate, Resolve } from "@angular/router";
import { Auth } from "./classes/auth";
import { Miscellaneous } from "./classes/miscellaneous";
import { Storage } from "@ionic/storage";

@Injectable()
export class SessionGuard implements CanActivate {
  constructor(
    private auth: Auth,
    private misc: Miscellaneous
  ) { }
  async canActivate() {
    return await this.auth.Session().then(() => {
      return true;
    }).catch((error: any) => {
      console.error(error);
      this.misc.doMessage(error, "warning");
      this.misc.go("/").then(() => { }).catch((error: any) => {
        console.error(error);
      });
      return false;
    });
  }
}

@Injectable()
export class ModalAccessGuard implements CanActivate {
  constructor(
    private misc: Miscellaneous
  ) { }
  async canActivate() {
    this.misc.go("/").then(() => { }).catch((error: any) => { console.error(error); });
    return false;
  }
}

@Injectable()
export class UserResolver implements Resolve<any> {
  constructor(private storage: Storage) { }
  resolve() {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA) => {
        resolve(LSUSERMETA);
      }).catch((error: any) => {
        reject({ message: error.message });
      });
    });
  }
}

const routes: Routes = [
  {
    path: "",
    loadChildren: () => import("./pages/main/main.module").then((m) => m.MainPageModule),
    data: { preload: true },
    resolve: {
      user: UserResolver
    }
  },
  {
    path: "console",
    redirectTo: "console/dashboard",
    pathMatch: "full",
  },
  {
    path: "console/dashboard",
    canActivate: [SessionGuard],
    loadChildren: () => import("./pages/console/console.module").then((m) => m.ConsolePageModule),
    data: { preload: true },
    resolve: {
      user: UserResolver,
    }
  },
  {
    path: "console/dashboard/:p",
    canActivate: [SessionGuard],
    loadChildren: () => import("./pages/console/console.module").then((m) => m.ConsolePageModule),
    data: { preload: true },
    resolve: {
      user: UserResolver,
    }
  },
  {
    path: "console/setup/:p",
    canActivate: [SessionGuard],
    loadChildren: () => import("./pages/console/console.module").then((m) => m.ConsolePageModule),
    data: { preload: true },
    resolve: {
      user: UserResolver,
    }
  },
  {
    path: "console/collections/:p",
    canActivate: [SessionGuard],
    loadChildren: () => import("./pages/console/console.module").then((m) => m.ConsolePageModule),
    data: { preload: true },
    resolve: {
      user: UserResolver,
    }
  },
  {
    path: "console/view/:p",
    canActivate: [SessionGuard],
    loadChildren: () => import("./pages/console/console.module").then((m) => m.ConsolePageModule),
    data: { preload: true },
    resolve: {
      user: UserResolver,
    }
  },
  {
    path: "console/admin/:p",
    canActivate: [SessionGuard],
    loadChildren: () => import("./pages/console/console.module").then((m) => m.ConsolePageModule),
    data: { preload: true },
    resolve: {
      user: UserResolver,
    }
  },
  {
    path: "console/account/:p",
    canActivate: [SessionGuard],
    loadChildren: () => import("./pages/console/console.module").then((m) => m.ConsolePageModule),
    data: { preload: true },
    resolve: {
      user: UserResolver,
    }
  },
  {
    path: "**",
    redirectTo: "/",
    pathMatch: "full",
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { preloadingStrategy: PreloadAllModules })],
  exports: [RouterModule],
  providers: [ModalAccessGuard, SessionGuard, UserResolver],
})
export class AppRoutingModule { }
