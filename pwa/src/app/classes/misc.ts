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
import { ModalController, AlertController, ToastController } from "@ionic/angular";
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
  public version = new BehaviorSubject<any>({});
  public saas = new BehaviorSubject<any>(null);
  public localization = new BehaviorSubject<any>(null);
  public api = new BehaviorSubject<any>(null);
  private collections_: any;
  private uri_: string = "";
  private mopen_: boolean = false;

  constructor(
    private storage: Storage,
    private translate: TranslateService,
    private modal: ModalController,
    private alert: AlertController,
    private toast: ToastController,
    private cb: ClipboardService,
    private http: HttpClient
  ) {
    this.collections.subscribe((res: any) => {
      this.collections_ = res && res.data ? res.data : [];
    });
    const ipaddrregx_ = /^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/gi;
    const domain_ = window.location.host.split(":")[0];
    this.uri_ = `${window.location.protocol}//${ipaddrregx_.test(domain_) || domain_ === "localhost" ? domain_ + ":" + environment.apiPort : domain_}/api`;
    this.api.next({ uri: this.uri_ });
  }

  api_call(qstr_: string, posted_: any) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
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
        if (posted_["responseType"]) {
          hdr_.responseType = posted_["responseType"];
        }
        this.http.post<any>(`${this.uri_}/${qstr_}`, posted_, hdr_).subscribe((res: any) => {
          const res_ = res.body;
          const qt_ = res.headers.get("Content-Type");
          const filename_ = qt_.indexOf("filename=") > 0 ? qt_.substring(qt_.indexOf("filename=") + 9).trim() : null;
          if (posted_.responseType) {
            resolve({ "binary": res_, "filename": filename_ });
          } else {
            if (res_.result) {
              resolve(res_);
            } else {
              reject(res_ && res_.msg ? res_.msg : res_);
            }
          }
        }, (res__: any) => {
          if (res__.error && res__.status) {
            if (res__.status === 403) {
              this.session_.next("ended");
              this.doMessage(res__.error.msg, "error");
            }
            reject(res__.error.msg ? res__.error.msg : res__.error);
          } else {
            reject(res__);
          }
        });
      });
    });
  }

  import_modal(id: any) {
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
              user: LSUSERMETA,
              data: {
                "sto_id": "data-import",
                "sto_collection_id": id,
                "sto_process": "insert",
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

  api_call_file(qstr_: string, posted_: any) {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        const token_: string = LSUSERMETA && LSUSERMETA.token ? LSUSERMETA.token : "";
        const api_key_: string = LSUSERMETA && LSUSERMETA.api_key ? LSUSERMETA.api_key : "";
        posted_.append("email", LSUSERMETA.email);
        const uri_ = `${this.uri_}/${qstr_}`;
        this.http.post<any>(uri_, posted_, {
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
  }

  set_locale(LSLOCALE_: string) {
    return new Promise((resolve, reject) => {
      if (LSLOCALE_) {
        this.storage.set("LSLOCALE", LSLOCALE_).then(() => {
          this.translate.setDefaultLang(LSLOCALE_);
          this.translate.use(LSLOCALE_);
          this.localization.next(LSLOCALE_ === "tr" ? "tr-TR" : LSLOCALE_ === "de" ? "de-DE" : LSLOCALE_ === "en" ? "en-US" : null);
          resolve(true);
        });
      } else {
        reject("language code not valid");
      }
    });
  }

  locale() {
    return new Promise((resolve) => {
      this.storage.get("LSLOCALE").then((LSLOCALE_: any) => {
        this.localization.next(LSLOCALE_ === "tr" ? "tr-TR" : LSLOCALE_ === "de" ? "de-DE" : LSLOCALE_ === "en" ? "en-US" : null);
        resolve(LSLOCALE_);
      });
    });
  }

  doMessage(msg: string, type: string) {
    type === "error" ? console.error("!!! err", msg) : null;
    this.toast.create({
      message: `${this.translate.instant(msg?.toString())?.toLowerCase()}.`,
      duration: ["success", "warning"].includes(type) ? 3000 : 7000,
      cssClass: type === "success" ? "toast-class-success" : type === "error" ? "toast-class-error" : "toast-class-warning",
      buttons: [{
        side: "end",
        icon: "close-outline",
        role: "cancel",
        handler: () => { }
      }]
    }).then((toast_: any) => {
      toast_.present();
    });
  }

  getFormattedDate(val: any) {
    const tzoffset = new Date().getTimezoneOffset() * 60000;
    let date_ = val ? val : new Date(Date.now() - tzoffset).toISOString();
    return date_.substring(0, 19) + "Z";
  }

  copy_to_clipboard(s: string) {
    return new Promise((resolve, reject) => {
      this.cb.copy(s)
      resolve(true);
    });
  }

  dismissModal(obj_: any) {
    return new Promise((resolve, reject) => {
      this.mopen_ = false;
      this.modal ? setTimeout(() => {
        this.modal.dismiss(obj_).then((dismiss_: any) => {
          resolve(dismiss_);
        }).catch((error: any) => {
          reject(error);
        });
      }, 200) : null;
    });
  }

  sign_modal(op: string) {
    return new Promise((resolve, reject) => {
      this.mopen_ ? null : this.modal.create({
        component: SignPage,
        backdropDismiss: false,
        cssClass: "sign-modal",
        componentProps: {
          op: op,
          user: null
        }
      }).then((modal_: any) => {
        modal_.present().then(() => {
          this.mopen_ = true;
          resolve(modal_);
        }).catch((error: any) => {
          reject(error);
        });
        modal_.onDidDismiss().then((dismiss_: any) => {
          this.mopen_ = false;
          resolve(dismiss_);
        }).catch((error: any) => {
          reject(error);
        });
      });
    });
  }

  show_note(reminder_: string, note_: string, event_: any) {
    event_.stopPropagation();
    this.alert.create({
      header: this.translate.instant("Reminder"),
      subHeader: reminder_,
      message: this.translate.instant(note_),
      buttons: [{
        text: this.translate.instant("Got It"),
        role: "cancel",
        handler: () => { }
      }],
    }).then((alert: any) => {
      alert.style.cssText = "--backdrop-opacity: 0 !important; z-index: 99999 !important; box-shadow: none !important;";
      alert.present();
    });
  }

}
