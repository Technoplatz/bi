/*
Technoplatz BI

Copyright (C) 2019-2024 Technoplatz IT Solutions GmbH, Mustafa Mat

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
import { Storage } from "@ionic/storage";

@Injectable()
export class SessionGuard implements CanActivate {
  constructor(
    private auth: Auth
  ) { }
  async canActivate() {
    return await this.auth.Session().then(() => {
      return true;
    }).catch((error: any) => {
      console.error(error);
      return false;
    });
  }
}

@Injectable()
export class UserResolver implements Resolve<any> {
  constructor(private storage: Storage) { }
  resolve() {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA) => {
        resolve(LSUSERMETA ? true : false);
      }).catch((error: any) => {
        reject({ message: error.msg });
      });
    });
  }
}

@Injectable()
export class AdminResolver implements Resolve<any> {
  constructor(private storage: Storage) { }
  resolve() {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA) => {
        resolve(LSUSERMETA?.perm ? true : false);
      }).catch((error: any) => {
        reject({ message: error.msg });
      });
    });
  }
}

const routes: Routes = [
  {
    path: "",
    loadChildren: () => import("./pages/home/home.module").then((m) => m.HomePageModule),
    data: { preload: true },
    resolve: {
      user: UserResolver
    }
  },
  {
    path: "dashboard",
    canActivate: [SessionGuard],
    loadChildren: () => import("./pages/dashboard/dashboard.module").then((m) => m.DashboardPageModule),
    data: { preload: true },
    resolve: {
      user: UserResolver,
    }
  },
  {
    path: "settings/account",
    canActivate: [SessionGuard],
    loadChildren: () => import("./pages/settings/settings.module").then((m) => m.SettingsPageModule),
    data: { preload: true },
    resolve: {
      user: UserResolver,
    }
  },
  {
    path: "settings/profile-settings",
    canActivate: [SessionGuard],
    loadChildren: () => import("./pages/settings/settings.module").then((m) => m.SettingsPageModule),
    data: { preload: true },
    resolve: {
      user: UserResolver,
    }
  },
  {
    path: "collection/:p",
    canActivate: [SessionGuard],
    loadChildren: () => import("./pages/collection/collection.module").then((m) => m.CollectionPageModule),
    data: { preload: true },
    resolve: {
      user: UserResolver,
    }
  },
  {
    path: "query/:p",
    canActivate: [SessionGuard],
    loadChildren: () => import("./pages/query/query.module").then((m) => m.QueryPageModule),
    data: { preload: true },
    resolve: {
      user: UserResolver,
    }
  },
  {
    path: "job/:p",
    canActivate: [SessionGuard],
    loadChildren: () => import("./pages/job/job.module").then((m) => m.JobPageModule),
    data: { preload: true },
    resolve: {
      user: UserResolver,
    }
  },
  {
    path: "admin/:p",
    canActivate: [SessionGuard],
    loadChildren: () => import("./pages/collection/collection.module").then((m) => m.CollectionPageModule),
    data: { preload: true },
    resolve: {
      user: AdminResolver,
    }
  },
  {
    path: "404",
    canActivate: [SessionGuard],
    loadChildren: () => import("./pages/_404/_404.module").then((m) => m._404PageModule),
    data: { preload: true },
    resolve: {
      user: UserResolver,
    }
  },
  {
    path: "**",
    redirectTo: "404",
    pathMatch: "full",
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { preloadingStrategy: PreloadAllModules })],
  exports: [RouterModule],
  providers: [SessionGuard, UserResolver, AdminResolver],
})
export class AppRoutingModule { }
