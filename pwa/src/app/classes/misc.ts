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
import { ClipboardPluginWeb } from "@capacitor/core";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { CrudPage } from "../pages/crud/crud.page";

@Injectable({
  providedIn: "root"
})

export class Miscellaneous {
  public user = new BehaviorSubject<any>(null);
  public collections = new BehaviorSubject<any>([]);
  public navi = new Subject<any>();
  public menutoggle = new Subject<any>();
  public version = new BehaviorSubject<boolean>(false);
  public toggle: boolean = true;

  private user_: any;
  private collections_: any;

  constructor(
    private storage: Storage,
    private translate: TranslateService,
    private modal: ModalController,
    private toast: ToastController,
    private cb: ClipboardPluginWeb,
    private http: HttpClient
  ) {
    this.user.subscribe((user: any) => {
      this.user_ = user;
    });
    this.collections.subscribe((res: any) => {
      this.collections_ = res && res.data ? res.data : [];
    });
  }

  getAPIHost() {
    return new Promise((resolve) => {
      const ipaddrregx_ = /^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/gi;
      const domain_ = window.location.host.split(":")[0];
      resolve(window.location.protocol + "//" + (ipaddrregx_.test(domain_) || domain_ === "localhost" ? domain_ + ":" + environment.apiPort : "api." + domain_));
    });
  }

  apiCall(url: string, posted: any) {
    return new Promise((resolve, reject) => {
      const collection_ = posted.collection ? posted.collection : "";
      this.storage.get("LSVIEW-" + collection_).then((LSVIEW: any) => {
        posted.user = this.user_;
        posted.email = this.user_.email;
        posted.view = LSVIEW ? LSVIEW : null;
        this.getAPIHost().then((apiHost) => {
          this.http.post<any>(apiHost + "/" + url, posted, {
            headers: new HttpHeaders({
              "Content-Type": "application/json",
              "X-Api-Key": environment.apiKey
            })
          }).subscribe((res: any) => {
            if (res && res.result) {
              resolve(res);
            } else {
              reject(res.msg);
            }
          }, (error: any) => {
            reject(error.msg);
          });
        });
      });
    });
  }

  doImport(id: any) {
    return new Promise((resolve, reject) => {
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
            user: this.user_,
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
  }

  apiFileCall(url: string, posted: any) {
    return new Promise((resolve, reject) => {
      posted.append("email", this.user_.email);
      posted.append("token", this.user_.token);
      this.getAPIHost().then((apiHost) => {
        this.http.post<any>(apiHost + "/" + url, posted, {
          headers: new HttpHeaders({
            "X-Api-Key": environment.apiKey
          })
        }).subscribe((res: any) => {
          if (res && res.result) {
            resolve(res);
          } else {
            reject(res);
          }
        }, (error: any) => {
          reject(error);
        });
      });
    });
  }

  doMenuToggle() {
    this.storage.get("LSMENUTOGGLE").then((LSMENUTOGGLE: boolean) => {
      this.toggle = !LSMENUTOGGLE;
      this.menutoggle.next(this.toggle);
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
      this.storage.get("LSLANG").then((LSLANG) => {
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
    type === "error" ? console.error(msg) : null;
    const typed: any = {
      message: msg,
      duration: type === "success" ? 5000 : 10000,
      position: "top",
      cssClass: type === "success" ? "toast-class-success" : "toast-class-error",
      buttons: [{
        side: "end",
        icon: "close-outline",
        role: "cancel",
        handler: () => { }
      }]
    };
    this.toast.dismiss().then(() => { }).catch((error: any) => { });
    const toast = await this.toast.create(typed);
    toast.present();
  }

  getFormattedDate(val: any) {
    const tzoffset = new Date().getTimezoneOffset() * 60000;
    let date_ = val ? val : new Date(Date.now() - tzoffset).toISOString();
    return date_.substring(0, 19) + "Z";
  }

  copyToClipboard(s: string) {
    return new Promise((resolve, reject) => {
      this.cb.write({ string: s }).then(() => {
        setTimeout(() => {
          resolve(true);
        }, 1000);
      }).catch((error: any) => {
        reject(error);
      });
    });
  }

}
