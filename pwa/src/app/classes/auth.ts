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
import { HttpClient, HttpHeaders, HttpResponse } from "@angular/common/http";
import { environment } from "../../environments/environment";

@Injectable({
  providedIn: "root"
})

export class Auth {
  private apiHost: string = "";
  private authHeaders: any = {
    "Content-Type": "application/json",
    "X-Api-Key": environment.apiKey
  }
  public user = new BehaviorSubject<any>(null);

  constructor(
    private storage: Storage,
    private misc: Miscellaneous,
    private crud: Crud,
    private http: HttpClient
  ) {
    this.misc.getAPIHost().then((apiHost: any) => {
      this.apiHost = apiHost;
    });
  }

  Signin(creds: any) {
    return new Promise((resolve, reject) => {
      creds.op = "signin";
      this.http.post<any>(this.apiHost + "/auth", JSON.stringify(creds), {
        headers: new HttpHeaders(this.authHeaders)
      }).subscribe((res: any) => {
        if (res && res.result) {
          resolve(true);
        } else {
          reject(res.msg);
        }
      }, (res: any) => {
        reject(res.error && res.error.msg ? res.error.msg : res);
      });
    });
  }

  Forgot(creds: any) {
    return new Promise((resolve, reject) => {
      creds.op = "forgot";
      this.http.post<any>(this.apiHost + "/auth", JSON.stringify(creds), {
        headers: new HttpHeaders(this.authHeaders)
      }).subscribe((res: any) => {
        if (res && res.result) {
          resolve(true);
        } else {
          reject(res.msg);
        }
      }, (res: any) => {
        reject(res.error && res.error.msg ? res.error.msg : res);
      });
    });
  }

  TFAC(creds: any) {
    return new Promise((resolve, reject) => {
      creds.op = "tfac";
      this.http.post<any>(this.apiHost + "/auth", JSON.stringify(creds), {
        headers: new HttpHeaders(this.authHeaders)
      }).subscribe((res: any) => {
        if (res.result) {
          this.storage.set("LSUSERMETA", res.user).then(() => {
            this.crud.getAll().then(() => {
              this.user.next(res.user);
              setTimeout(() => {
                this.misc.navi.next("/dashboard");
                this.misc.menutoggle.next(true);
              }, 1000);
              resolve(true);
            }).catch((error: any) => {
              console.error(error);
              this.misc.doMessage(error, "error");
            });
          })
        } else {
          reject(res.msg);
        }
      }, (res: any) => {
        reject(res.error && res.error.msg ? res.error.msg : res);
      });
    });
  }

  Reset(creds: any) {
    return new Promise((resolve, reject) => {
      creds.op = "reset";
      this.http.post<any>(this.apiHost + "/auth", JSON.stringify(creds), {
        headers: new HttpHeaders(this.authHeaders)
      }).subscribe((res: any) => {
        if (res && res.result) {
          this.misc.navi.next("/");
          resolve(true);
        } else {
          reject(res.msg);
        }
      }, (res: any) => {
        reject(res.error && res.error.msg ? res.error.msg : res);
      });
    });
  }

  Account(op: any) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        this.http.post<any>(this.apiHost + "/auth", JSON.stringify({
          op: op,
          user: LSUSERMETA
        }), {
          headers: new HttpHeaders(this.authHeaders)
        }).subscribe((res: any) => {
          if (res && res.result) {
            resolve(res);
          } else {
            reject(res.msg);
          }
        }, (res: any) => {
          reject(res.error && res.error.msg ? res.error.msg : res);
        });
      });
    });
  }

  OTP(obj: any) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        this.http.post<any>(this.apiHost + "/otp", JSON.stringify({
          request: obj,
          user: LSUSERMETA
        }), {
          headers: new HttpHeaders(this.authHeaders)
        }).subscribe((res: any) => {
          if (res && res.result) {
            resolve(res);
          } else {
            reject(res.msg);
          }
        }, (res: any) => {
          reject(res.error && res.error.msg ? res.error.msg : res);
        });
      });
    });
  }

  Signout() {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        if (LSUSERMETA && LSUSERMETA.email) {
          const email = LSUSERMETA.email;
          this.storage.remove("LSUSERMETA").then(() => {
            this.http.post<any>(this.apiHost + "/auth", JSON.stringify({
              email: email,
              op: "signout"
            }), {
              headers: new HttpHeaders(this.authHeaders)
            }).subscribe((res: any) => {
              if (res && res.result) {
                this.user.next(null);
              } else {
                reject(res.msg);
              }
            }, (res: any) => {
              reject(res.error && res.error.msg ? res.error.msg : res);
            });
          });
        } else {
          this.misc.navi.next("/");
          resolve(true);
        }
      });
    });
  }

  Session() {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        if (LSUSERMETA && LSUSERMETA?.email && LSUSERMETA.token) {
          resolve(true);
        } else {
          this.user.next(null);
          reject("session closed");
        }
      });
    });
  }

  Signup(creds: any) {
    return new Promise((resolve, reject) => {
      this.storage.remove("LSUSERMETA").then(() => {
        creds.op = "signup";
        this.http.post<any>(this.apiHost + "/auth", JSON.stringify(creds), {
          headers: new HttpHeaders(this.authHeaders)
        }).subscribe((res: any) => {
          if (res && res.result) {
            this.user.next(null);
            resolve(true);
          } else {
            reject(res.msg);
          }
        }, (error: any) => {
          reject(error.msg);
        });
      }, (res: any) => {
        reject(res.error && res.error.msg ? res.error.msg : res);
      });
    });
  }

  forgotPassword(creds: any) {
    return new Promise((resolve, reject) => {
      this.http.post<any>(this.apiHost + "/auth", JSON.stringify(creds), {
        headers: new HttpHeaders(this.authHeaders)
      }).subscribe((res: any) => {
        if (res) {
          if (res.successful) {
            this.user.next(null);
            resolve({ message: res.msg });
          } else {
            reject({ message: res.msg });
          }
        } else {
          reject({ message: "no api response" });
        }
      }, (res: any) => {
        reject(res.error && res.error.msg ? res.error.msg : res);
      });
    });
  }
}
