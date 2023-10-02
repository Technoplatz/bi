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
import { ModalController, ToastController } from "@ionic/angular";
import { Subject, BehaviorSubject } from "rxjs";
import { Storage } from "@ionic/storage";
import { TranslateService } from "@ngx-translate/core";
import { environment } from "../../environments/environment";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { CrudPage } from "../pages/crud/crud.page";
import { SignPage } from "../pages/sign/sign.page";
import { ClipboardService } from "ngx-clipboard";

@Injectable({
  providedIn: "root"
})

export class Miscellaneous {
  public collections = new BehaviorSubject<any>([]);
  public session_ = new BehaviorSubject<any>([]);
  public navi = new Subject<any>();
  public menutoggle = new BehaviorSubject<boolean>(false);
  public version = new BehaviorSubject<any>(null);
  public saas = new BehaviorSubject<any>(null);
  public screen_size = new BehaviorSubject<any>(null);
  public toggle: boolean = true;
  private collections_: any;

  constructor(
    private storage: Storage,
    private translate: TranslateService,
    private modal: ModalController,
    private toast: ToastController,
    private cb: ClipboardService,
    private http: HttpClient
  ) {
    this.collections.subscribe((res: any) => {
      this.collections_ = res && res.data ? res.data : [];
    });
  }

  getAPIUrl() {
    return new Promise((resolve) => {
      const ipaddrregx_ = /^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/gi;
      const domain_ = window.location.host.split(":")[0];
      resolve(window.location.protocol + "//" + (ipaddrregx_.test(domain_) || domain_ === "localhost" ? domain_ + ":" + environment.apiPort : "api." + domain_));
    });
  }

  apiCall(url: string, posted: any) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        this.getAPIUrl().then((apiHost) => {
          const token_: string = LSUSERMETA && LSUSERMETA.token ? LSUSERMETA.token : "";
          const api_key_: string = LSUSERMETA && LSUSERMETA.api_key ? LSUSERMETA.api_key : "";
          let hdr_: any = {
            headers: new HttpHeaders({
              "Content-Type": "application/json",
              "Authorization": "Bearer " + token_,
              "X-Api-Key": api_key_
            }),
            observe: "response"
          }
          if (posted.responseType) {
            hdr_.responseType = posted.responseType;
          }
          this.http.post<any>(apiHost + "/" + url, posted, hdr_).subscribe((res: any) => {
            const res_ = res.body;
            if (posted.responseType) {
              resolve(res_);
            } else {
              if (res_?.result) {
                resolve(res_);
              } else {
                console.error("*** api negative", res_);
                reject(res_ && res_.msg ? res_.msg : res_);
              }
            }
          }, (res: any) => {
            const res_ = res;
            if (res_.error && res_.status) {
              if (res_.status === 403) {
                this.session_.next("ended");
                this.doMessage(res_.error.msg, "error");
              }
              reject(res_.error.msg ? res_.error.msg : res_.error);
            } else {
              reject(res_);
            }
          });
        });
      });
    });
  }

  upload_modal_f(id: any) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        this.modal.create({
          component: CrudPage,
          backdropDismiss: false,
          cssClass: "crud-modal",
          componentProps: {
            shuttle: {
              op: "import",
              collection: "_storage",
              collections: this.collections_ ? this.collections_ : [],
              views: [],
              user: LSUSERMETA,
              data: {
                "sto_id": "data-import",
                "sto_collection_id": id,
                "sto_file": null
              },
              structure: environment.import_structure,
              sweeped: [],
              filter: {},
              actions: [],
              direct: -1
            }
          }
        }).then((modal: any) => {
          modal.present().then(() => {
            modal.onDidDismiss().then((res: any) => {
              if (res.data && res.data.modified) {
                this.doMessage("file imported successfully", "success");
                resolve(res.data.cid);
              } else {
                reject(res);
              }
            });
          });
        });
      });
    });
  }

  apiFileCall(url: string, posted: any) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        const token_: string = LSUSERMETA && LSUSERMETA.token ? LSUSERMETA.token : "";
        const api_key_: string = LSUSERMETA && LSUSERMETA.api_key ? LSUSERMETA.api_key : "";
        posted.append("email", LSUSERMETA.email);
        this.getAPIUrl().then((apiHost) => {
          this.http.post<any>(apiHost + "/" + url, posted, {
            headers: new HttpHeaders({
              "Authorization": "Bearer " + token_,
              "X-Api-Key": api_key_
            }),
            observe: "response" as "response"
          }).subscribe((res: any) => {
            const res_ = res.body;
            if (res_ && res_.result) {
              resolve(res_);
            } else {
              console.error("*** file api negative", res_);
              reject(res_ && res_.msg ? res_.msg : res_);
            }
          }, (res: any) => {
            const res_ = res;
            if (res_.error && res_.status) {
              if (res_.status === 403) {
                this.session_.next("ended");
                this.doMessage(res_.error.msg, "error");
              }
              reject(res_.error.msg ? res_.error.msg : res_.error);
            } else {
              reject(res_);
            }
          });
        });
      });
    });
  }

  setLanguage(l: string) {
    return new Promise((resolve, reject) => {
      if (l) {
        this.storage.set("LSLANG", l).then(() => {
          this.translate.setDefaultLang(l);
          this.translate.use(l);
          resolve(true);
        }).catch((error: any) => {
          reject("storage lang set error");
        });
      } else {
        reject("language code not valid");
      }
    });
  }

  getLanguage() {
    return new Promise((resolve, reject) => {
      this.storage.get("LSLANG").then((LSLANG: any) => {
        resolve(LSLANG ? LSLANG : "en");
      }).catch(() => {
        resolve("en");
      });
    });
  }

  dismissModal(obj: any) {
    return new Promise((resolve, reject) => {
      if (this.modal) {
        setTimeout(() => {
          this.modal.dismiss(obj).then((res: any) => {
            resolve(res);
          }).catch((error: any) => {
            reject(error);
          });
        }, 200);
      } else {
        resolve(true);
      }
    });
  }

  async doMessage(msg: string, type: string) {
    type === "error" ? console.error("*** err msg", msg) : null;
    if (msg) {
      const typed: any = {
        message: msg.toLowerCase(),
        duration: type === "success" ? 3000 : 10000,
        cssClass: type === "success" ? "toast-class-success" : type === "error" ? "toast-class-error" : "toast-class-warning",
        buttons: [{
          side: "end",
          icon: "close-outline",
          role: "cancel",
          handler: () => { }
        }]
      };
      const toast = await this.toast.create(typed);
      toast.present();
    }
  }

  getFormattedDate(val: any) {
    const tzoffset = new Date().getTimezoneOffset() * 60000;
    let date_ = val ? val : new Date(Date.now() - tzoffset).toISOString();
    return date_.substring(0, 19) + "Z";
  }

  copyToClipboard(s: string) {
    return new Promise((resolve, reject) => {
      this.cb.copy(s)
      resolve(true);
    });
  }

  async doSign(op: string) {
    const modal = await this.modal.create({
      component: SignPage,
      backdropDismiss: false,
      cssClass: "signin-modal",
      componentProps: {
        op: op,
        user: null
      }
    });
    return await modal.present();
  }

}
