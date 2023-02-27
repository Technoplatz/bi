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

import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import { Subject } from "rxjs";
import { Crud } from "./crud";
import { Navigation } from "./navigation";
import { Miscellaneous } from "./miscellaneous";
import { HttpClient, HttpHeaders } from "@angular/common/http";
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
  stateChange = new Subject<any>();
  saas_ = new Subject<any>();

  constructor(
    private storage: Storage,
    private navigation: Navigation,
    private misc: Miscellaneous,
    private crud: Crud,
    private http: HttpClient
  ) {
    this.misc.getAPIHost().then((apiHost: any) => {
      this.apiHost = apiHost;
    });
  }

  Saas() {
    return new Promise((resolve, reject) => {
      this.http.post<any>(this.apiHost + "/auth", JSON.stringify({
        "op": "saas"
      }), {
        headers: new HttpHeaders(this.authHeaders)
      }).subscribe((res: any) => {
        if (res && res.result) {
          resolve(res.saas);
        } else {
          reject(res.msg);
        }
      }, (error: any) => {
        reject(error.message);
      });
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
      }, (error: any) => {
        console.error("*** error", error);
        reject(error.message);
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
      }, (error: any) => {
        reject(error.message);
      });
    });
  }

  TFAC(creds: any) {
    return new Promise((resolve, reject) => {
      creds.op = "tfac";
      this.http.post<any>(this.apiHost + "/auth", JSON.stringify(creds), {
        headers: new HttpHeaders(this.authHeaders)
      }).subscribe((res: any) => {
        if (res && res.result) {
          this.storage.set("LSUSERMETA", res.user).then(() => {
            this.crud.getAll().then(() => {
              this.stateChange.next(res.user);
              this.navigation.navigateRoot("/dashboard").then(() => {
                resolve(true);
              }).catch((error: any) => {
                reject(error);
              });
            }).catch((error: any) => {
              console.error(error);
              this.misc.doMessage(error, "error");
            });
          }).catch((error: any) => {
            reject(error);
          });
        } else {
          reject(res.msg);
        }
      }, (error: any) => {
        reject(error);
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
          this.navigation.navigateRoot("/").then(() => {
            resolve(true);
          }).catch((error: any) => {
            reject(error);
          });
        } else {
          reject(res.msg);
        }
      }, (error: any) => {
        reject(error);
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
        }, (error: any) => {
          reject(error);
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
        }, (error: any) => {
          reject(error);
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
            this.storage.remove("LSID").then(() => {
              this.http.post<any>(this.apiHost + "/auth", JSON.stringify({
                email: email,
                op: "signout"
              }), {
                headers: new HttpHeaders(this.authHeaders)
              }).subscribe((res: any) => {
                if (res && res.result) {
                  this.stateChange.next(null);
                } else {
                  reject(res.msg);
                }
              }, () => {
                reject("could not connected to the server");
              });
            });
          });
        } else {
          this.navigation.navigateRoot("/").then(() => {
            resolve(true);
          }).catch((error: any) => {
            reject(error);
          });
        }
      });
    });
  }

  Session() {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        if (LSUSERMETA && LSUSERMETA.email && LSUSERMETA.token) {
          this.stateChange.next(LSUSERMETA);
          const email_ = LSUSERMETA.email;
          const token_ = LSUSERMETA.token;
          const jdate_ = LSUSERMETA.jdate;
          const creds_ = {
            email: email_,
            token: token_,
            op: "session",
            jdate: jdate_
          };
          this.http.post<any>(this.apiHost + "/auth", JSON.stringify(creds_), {
            headers: new HttpHeaders(this.authHeaders)
          }).subscribe((res: any) => {
            if (res && res.result) {
              resolve(true);
            } else {
              this.storage.remove("LSUSERMETA").then(() => {
                this.stateChange.next(null);
                reject(res.msg);
              }).catch((error: any) => {
                reject(error);
              });
            }
          }, () => {
            reject("could not connect to the server");
          });
        } else {
          reject("user session closed");
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
            this.stateChange.next(null);
            resolve(true);
          } else {
            reject(res.msg);
          }
        }, (error: any) => {
          reject(error.message);
        });
      }).catch((error: any) => {
        reject(error);
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
            this.stateChange.next(null);
            resolve({ message: res.msg });
          } else {
            reject({ message: res.msg });
          }
        } else {
          reject({ message: "no api response" });
        }
      }, (error: any) => {
        reject({ message: error.message });
      });
    });
  }
}
