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
*/

import { inject } from "@angular/core";
import { CanActivateFn, ResolveFn, Routes } from "@angular/router";
import { Storage } from "@ionic/storage-angular";
import { Auth } from "./classes/auth";

export const sessionGuard: CanActivateFn = async () => {
  try {
    await inject(Auth).Session();
    return true;
  } catch (error) {
    console.error(error);
    return false;
  }
};

export const userResolver: ResolveFn<boolean> = async () => {
  const meta = await inject(Storage).get("LSUSERMETA");
  return !!meta;
};

export const adminResolver: ResolveFn<boolean> = async () => {
  const meta = await inject(Storage).get("LSUSERMETA");
  return !!meta?.perm;
};

// pages are ported one by one; unported paths lead to the "not yet available" page until then
export const routes: Routes = [
  { path: "", loadComponent: () => import("./pages/home/home.page").then((m) => m.HomePage), resolve: { user: userResolver } },
  { path: "dashboard", canActivate: [sessionGuard], loadComponent: () => import("./pages/pending/pending.page").then((m) => m.PendingPage), resolve: { user: userResolver } },
  { path: "settings/account", canActivate: [sessionGuard], loadComponent: () => import("./pages/pending/pending.page").then((m) => m.PendingPage), resolve: { user: userResolver } },
  { path: "settings/profile-settings", canActivate: [sessionGuard], loadComponent: () => import("./pages/pending/pending.page").then((m) => m.PendingPage), resolve: { user: userResolver } },
  { path: "collection/:p", canActivate: [sessionGuard], loadComponent: () => import("./pages/pending/pending.page").then((m) => m.PendingPage), resolve: { user: userResolver } },
  { path: "query/:p", canActivate: [sessionGuard], loadComponent: () => import("./pages/pending/pending.page").then((m) => m.PendingPage), resolve: { user: userResolver } },
  { path: "job/:p", canActivate: [sessionGuard], loadComponent: () => import("./pages/pending/pending.page").then((m) => m.PendingPage), resolve: { user: userResolver } },
  { path: "admin/:p", canActivate: [sessionGuard], loadComponent: () => import("./pages/pending/pending.page").then((m) => m.PendingPage), resolve: { user: adminResolver } },
  { path: "404", canActivate: [sessionGuard], loadComponent: () => import("./pages/pending/pending.page").then((m) => m.PendingPage), resolve: { user: userResolver } },
  { path: "**", redirectTo: "404", pathMatch: "full" }
];
