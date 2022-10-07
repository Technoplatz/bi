import { Injectable } from "@angular/core";
import { ModalController, ToastController, LoadingController, AlertController } from "@ionic/angular";
import { Storage } from "@ionic/storage";
import { TranslateService } from "@ngx-translate/core";
import { Navigation } from "./navigation";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { environment } from "../../environments/environment";
import { ClipboardPluginWeb } from "@capacitor/core";

@Injectable({
  providedIn: "root"
})

export class Miscellaneous {
  private loadin: any;
  private filter: any = [];
  private apiHost: string;
  private miscHeaders: any = {
    "Content-Type": "application/json",
    "X-Api-Key": environment.apiKey
  }

  constructor(
    private storage: Storage,
    private translate: TranslateService,
    private modal: ModalController,
    private toast: ToastController,
    private loading: LoadingController,
    private nav: Navigation,
    private alert: AlertController,
    private http: HttpClient,
    private cb: ClipboardPluginWeb
  ) { }

  go(p: string) {
    return new Promise((resolve, reject) => {
      this.nav.navigateRoot(p).then(() => {
        resolve(true);
      }).catch((error: any) => {
        reject(error);
      });
    });
  }

  getAPIHost() {
    return new Promise((resolve) => {
      this.apiHost = environment.apiHost;
      resolve(environment.apiHost);
    });
  }

  getRandomString(length: number) {
    return new Promise((resolve, reject) => {
      let result = "";
      const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
      const charactersLength = characters.length;
      for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
        const q = i === length - 1 ? resolve(result) : null;
      }
    });
  }

  getVersion() {
    return new Promise((resolve, reject) => {
      this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
        const posted: any = {
          op: "version",
          user: LSUSERMETA
        }
        this.http.post<any>(this.apiHost + "/crud", posted, {
          headers: new HttpHeaders(this.miscHeaders)
        }).subscribe((res: any) => {
          if (res && res.result) {
            resolve(res);
          } else {
            reject(res.msg);
          }
        }, (error: any) => {
          reject(error);
        });
      }).catch((error: any) => {
        reject(error);
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

  isJson(j: any) {
    try {
      JSON.parse(j);
    } catch (e) {
      return false;
    }
    return true;
  }

  async presentLoading(message: string) {
    this.loadin = await this.loading.create({
      spinner: "crescent",
      duration: 5000,
      message: message,
      translucent: true,
      cssClass: "custom-loading",
      backdropDismiss: false,
      showBackdrop: true,
      mode: "md",
      keyboardClose: false,
    });
    await this.loadin.present();
  }

  dismissLoading(loadin) {
    loadin ? loadin.dismiss().then(() => { }) : null;
  }

  async doMessage(msg: string, type: string) {
    const typed: any = {
      message: msg,
      duration: type === "success" ? 5000 : 10000,
      position: "top",
      cssClass: type === "success" ? "toast-class-success" : "toast-class-error",
      buttons: [
        {
          side: "end",
          icon: "close-outline",
          role: "cancel",
          handler: () => {
            console.info("alert canceled");
          }
        }
      ]
    };
    this.toast.dismiss().then(() => { }).catch((error: any) => { });
    const toast = await this.toast.create(typed);
    toast.present();
  }

  getFilterString(id: string) {
    return new Promise((resolve, reject) => {
      let filterstr = "";
      this.storage.get("LSFILTER_" + id).then((LSFILTER: any) => {
        this.filter = LSFILTER ? LSFILTER : [];
        if (this.filter && this.filter.length > 0) {
          for (let f = 0; f <= this.filter.length - 1; f++) {
            filterstr += f > 0 ? " and " : "";
            filterstr += this.filter[f].key + " ";
            filterstr += environment.filterops.filter((obj: any) => this.filter[f].op === obj.value)[0].value + " ";
            filterstr += this.filter[f].value + " ";
            if (f === this.filter.length - 1) {
              resolve(filterstr);
            }
          }
        } else {
          resolve(filterstr);
        }
      });
    });
  }

  async doInfoAlert(d: any) {
    const alert = await this.alert.create({
      header: "Info",
      message: d + ".",
      buttons: ["OK"],
    });
    alert.style.cssText = "--backdrop-opacity: 0 !important; z-index: 99999 !important; box-shadow: none !important;";
    await alert.present();
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
