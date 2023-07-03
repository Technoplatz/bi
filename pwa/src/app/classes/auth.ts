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

import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import { BehaviorSubject } from "rxjs";
import { Crud } from "./crud";
import { Miscellaneous } from "./misc";

@Injectable({
  providedIn: "root"
})

export class Auth {
  public user = new BehaviorSubject<any>(null);

  constructor(
    private storage: Storage,
    private misc: Miscellaneous,
    private crud: Crud
  ) {
    this.misc.session_.subscribe((session_: any) => {
      session_ === "ended" ? this.setUserOut() : null;
    });
  }

  setUserOut() {
    this.storage.remove("LSUSERMETA").then(() => {
      this.user.next(null);
      window.location.replace("/");
    });
  }

  Signin(creds: any) {
    return new Promise((resolve, reject) => {
      creds.op = "signin";
      this.misc.apiCall("auth", JSON.stringify(creds)).then((res: any) => {
        if (res && res.result) {
          resolve(true);
        } else {
          this.misc.doMessage(res.msg, "error");
          reject(res.msg);
        }
      }).catch((res: any) => {
        this.misc.doMessage(res, "error");
        reject(res);
      });
    });
  }

  Forgot(creds: any) {
    return new Promise((resolve, reject) => {
      creds.op = "forgot";
      this.misc.apiCall("auth", JSON.stringify(creds)).then((res: any) => {
        if (res && res.result) {
          resolve(true);
        } else {
          reject(res.msg);
        }
      }).catch((res: any) => {
        this.misc.doMessage(res, "error");
        reject(res);
      });
    });
  }

  TFAC(creds: any) {
    return new Promise((resolve, reject) => {
      creds.op = "tfac";
      this.misc.apiCall("auth", JSON.stringify(creds)).then((res: any) => {
        if (res && res.result) {
          this.user.next(res.user);
          this.storage.set("LSUSERMETA", res.user).then(() => {
            resolve(true);
            this.misc.navi.next("/dashboard");
            this.crud.getAll().then(() => { }).catch((error: any) => {
              console.error(error);
              this.misc.doMessage(error, "error");
              reject(error);
            });
          });
        } else {
          this.misc.doMessage(res.msg, "error");
          reject(res.msg);
        }
      }).catch((res: any) => {
        this.misc.doMessage(res, "error");
        reject(res);
      });
    });
  }

  Reset(creds: any) {
    return new Promise((resolve, reject) => {
      creds.op = "reset";
      this.misc.apiCall("auth", JSON.stringify(creds)).then((res: any) => {
        if (res && res.result) {
          resolve(true);
        } else {
          reject(res.msg);
        }
      }).catch((res: any) => {
        this.misc.doMessage(res, "error");
        reject(res);
      });
    });
  }

  Account(op: any) {
    return new Promise((resolve, reject) => {
      this.misc.apiCall("auth", JSON.stringify({
        op: op
      })).then((res: any) => {
        if (res && res.result) {
          resolve(true);
        } else {
          reject(res.msg);
        }
      }).catch((res: any) => {
        this.misc.doMessage(res, "error");
        reject(res);
      });
    });
  }

  OTP(obj: any) {
    return new Promise((resolve, reject) => {
      this.misc.apiCall("otp", JSON.stringify({
        request: obj
      })).then((res: any) => {
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

  Signout() {
    return new Promise((resolve, reject) => {
      this.misc.apiCall("auth", JSON.stringify({
        op: "signout"
      })).then((res: any) => {
        if (res && res.result) {
          this.setUserOut();
          resolve(true);
        } else {
          reject(res.msg);
        }
      }).catch((res: any) => {
        this.misc.doMessage(res, "error");
        reject(res);
      });
    });
  }

  Session() {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        if (LSUSERMETA && LSUSERMETA?.token) {
          resolve(true);
        } else {
          this.setUserOut();
          reject("session closed");
        }
      });
    });
  }

  Signup(creds: any) {
    return new Promise((resolve, reject) => {
      creds.op = "signup";
      this.misc.apiCall("auth", JSON.stringify(creds)).then((res: any) => {
        if (res && res.result) {
          resolve(true);
        } else {
          reject(res.msg);
        }
      }).catch((res: any) => {
        this.misc.doMessage(res, "error");
        reject(res);
      });
    });
  }

  forgotPassword(creds: any) {
    return new Promise((resolve, reject) => {
      creds.op = "forgot";
      this.misc.apiCall("otp", JSON.stringify(creds)).then((res: any) => {
        if (res && res.result) {
          this.setUserOut();
          resolve(true);
        } else {
          reject(res.msg);
        }
      }).catch((res: any) => {
        this.misc.doMessage(res, "error");
        reject(res);
      });
    });
  }
}
