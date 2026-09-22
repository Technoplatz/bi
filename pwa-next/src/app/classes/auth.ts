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

import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage-angular";
import { BehaviorSubject } from "rxjs";
import { Crud } from "./crud";
import { Miscellaneous } from "./misc";

@Injectable({ providedIn: "root" })
export class Auth {
  public user = new BehaviorSubject<any>(null);

  constructor(
    private storage: Storage,
    private misc: Miscellaneous,
    private crud: Crud
  ) {
    this.misc.session_.subscribe((session_: any) => {
      if (session_ === "ended") {
        this.setUserOut();
      }
    });
  }

  setUserOut() {
    // clear the stored session first; the redirect would otherwise abort the IndexedDB delete
    return new Promise((resolve) => {
      this.storage.remove("LSUSERMETA").then(() => {
        this.user.next(null);
        window.location.replace("/");
        resolve(true);
      }).catch(() => {
        window.location.replace("/");
        resolve(true);
      });
    });
  }

  private auth_call(creds: any, op: string, endpoint = "auth") {
    return new Promise((resolve, reject) => {
      creds.op = op;
      this.misc.api_call(endpoint, JSON.stringify(creds)).then((res: any) => {
        if (res && res.result) {
          resolve(res);
        } else {
          this.misc.doMessage(res?.msg, "error");
          reject(res?.msg);
        }
      }).catch((res: any) => {
        this.misc.doMessage(res, "error");
        reject(res);
      });
    });
  }

  sign_in(creds: any) {
    return this.auth_call(creds, "signin").then(() => true);
  }

  Forgot(creds: any) {
    return this.auth_call(creds, "forgot").then(() => true);
  }

  TFAC(creds: any) {
    return new Promise((resolve, reject) => {
      this.auth_call(creds, "tfac").then((res: any) => {
        this.user.next(res.user);
        this.storage.set("LSUSERMETA", res.user).then(() => {
          resolve(true);
          this.misc.navi.next("/dashboard");
          this.crud.get_all().catch((error: any) => {
            this.misc.doMessage(error, "error");
          });
        });
      }).catch((error: any) => reject(error));
    });
  }

  Reset(creds: any) {
    return this.auth_call(creds, "reset").then(() => true);
  }

  OTP(obj: any) {
    return new Promise((resolve, reject) => {
      this.misc.api_call("otp", JSON.stringify({ request: obj })).then((res: any) => {
        if (res && res.result) {
          resolve(res);
        } else {
          reject(res.msg);
        }
      }).catch((res: any) => {
        this.misc.doMessage(res, "error");
        reject(res);
      });
    });
  }

  sign_out() {
    // invalidate the server session while the token is still available, then clear and redirect
    return new Promise((resolve, reject) => {
      this.misc.api_call("auth", JSON.stringify({ op: "signout" })).then((res: any) => {
        this.setUserOut().then(() => {
          res && res.result ? resolve(true) : reject(res?.msg);
        });
      }).catch((res: any) => {
        this.misc.doMessage(res, "error");
        this.setUserOut().then(() => reject(res));
      });
    });
  }

  Session() {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        if (LSUSERMETA && LSUSERMETA?.token) {
          resolve(true);
        } else {
          this.setUserOut().then(() => {
            reject("session closed");
          });
        }
      });
    });
  }

  sign_up(creds: any) {
    return this.auth_call(creds, "signup");
  }
}
