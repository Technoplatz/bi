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

@Injectable({
  providedIn: "root"
})

export class Miscellaneous {
  private apiHost: string = "";
  public toggle: boolean = true;

  constructor(
    private storage: Storage,
    private translate: TranslateService,
    private modal: ModalController,
    private toast: ToastController,
    private cb: ClipboardPluginWeb
  ) { }

  navi = new Subject<any>();
  menutoggle = new Subject<any>();
  version = new BehaviorSubject<any>([]);

  doMenuToggle() {
    this.storage.get("LSMENUTOGGLE").then((LSMENUTOGGLE: boolean) => {
      this.toggle = !LSMENUTOGGLE;
      this.menutoggle.next(this.toggle);
    });
  }

  getAPIHost() {
    return new Promise((resolve) => {
      this.apiHost = window.location.host.includes("8100") ? window.location.protocol + "//" + window.location.host.replace(/8100/gi, environment.apiPort) : window.location.protocol + "//api." + window.location.hostname;
      resolve(this.apiHost);
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
