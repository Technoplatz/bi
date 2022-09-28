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
