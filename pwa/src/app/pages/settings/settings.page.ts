/*
Technoplatz BI

Copyright ©Technoplatz IT Solutions GmbH, Mustafa Mat

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General private License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General private License for more details.

You should have received a copy of the GNU Affero General private License
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

import { Component, OnInit } from "@angular/core";
import { Storage } from "@ionic/storage";
import { Auth } from "../../classes/auth";
import { AlertController } from "@ionic/angular";
import { Miscellaneous } from "../../classes/misc";
import { environment } from "../../../environments/environment";
import { Router } from "@angular/router";

@Component({
  selector: "app-settings",
  templateUrl: "./settings.page.html",
  styleUrls: ["./settings.page.scss"]
})

export class SettingsPage implements OnInit {
  public version = environment.appVersion;
  public release = environment.release;
  public timeZone = environment.timeZone;
  public header: string = "SETTINGS";
  public subheader: string = "";
  public user: any = null;
  public is_initialized: boolean = false;
  public menu: string = "";
  public submenu: string = "";
  public themes: any = environment.themes;
  public perm: boolean = false;
  public accountf_api_key: string = "";
  public is_api_key_copied: boolean = false;
  public is_api_key_enabled: boolean = false;
  public is_api_gen_enabled: boolean = false;
  public accountf_api_key_date: any = null;
  public is_processing_account: boolean = false;
  public is_url_copied: boolean = false;
  public viewurl_: string = "";
  public viewurl_masked_: string = "";
  public qr_exists: boolean = false;
  public otp_show: boolean = false;
  public otp_process: boolean = false;
  public qr_show: boolean = false;
  public otp_qr: string = "";
  public saas: any = null;
  public pagination_: string = "25";

  constructor(
    private storage: Storage,
    private auth: Auth,
    private router: Router,
    private alert: AlertController,
    public misc: Miscellaneous
  ) { }

  ngOnInit() {
    this.menu = this.router.url.split("/")[1];
    this.submenu = this.router.url.split("/")[2];
    this.subheader = this.submenu === "account" ? "Account" : this.submenu === "profile-settings" ? "Profile Settings" : this.submenu;
    this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
      this.user = LSUSERMETA;
      this.perm = LSUSERMETA && LSUSERMETA.perm ? true : false;
      this.accountf_api_key = LSUSERMETA.api_key;
      this.is_initialized = true;
    });
  }

  doTheme(LSTHEME: any) {
    this.storage.set("LSTHEME", LSTHEME).then(() => {
      document.documentElement.style.setProperty("--ion-color-primary", LSTHEME.color);
    });
  }

  copy(w: string) {
    const s = w === "api_key" ? this.accountf_api_key : w === "view" ? this.viewurl_ : "";
    this.is_api_key_copied = w === "api_key" ? true : false;
    this.is_url_copied = w === "view" || w === "collection" ? true : false;
    this.misc.copy_to_clipboard(s).then(() => { }).catch((error: any) => {
      console.error("not copied", error);
    }).finally(() => {
      setTimeout(() => {
        this.is_api_key_copied = false;
        this.is_url_copied = false;
      }, 1000);
    });
  }

  doApiKeyEnabled() {
    if (!this.is_api_key_enabled) {
      this.is_api_key_enabled = true;
      setTimeout(() => {
        this.is_api_key_enabled = false;
      }, 5000);
    }
  }

  doResetOTP() {
    this.alert.create({
      header: "Warning",
      subHeader: "One-Time Password Reset",
      message: "Your current QR code will be removed and a new QR code will be generated. This means you will not be able to Login with the existing QR code until you activate the new code.",
      buttons: [
        {
          text: "CANCEL",
          role: "cancel",
          cssClass: "allert",
          handler: () => { }
        }, {
          text: "OKAY",
          handler: () => {
            this.doOTP({
              op: "reset"
            });
          }
        }
      ]
    }).then((alert: any) => {
      alert.present();
    });
  }

  doValidateOTP() {
    this.alert.create({
      cssClass: "my-custom-class",
      subHeader: "Validate 2FA Code",
      message: "Please enter the code generated from QR code",
      inputs: [
        {
          name: "id",
          value: null,
          type: "number",
          placeholder: "Enter current OTP"
        }
      ],
      buttons: [
        {
          text: "Cancel",
          role: "cancel",
          cssClass: "primary",
          handler: () => {
            console.warn("Confirm cancel");
          }
        }, {
          text: "OK",
          handler: (alertData: any) => {
            this.doOTP({
              op: "validate",
              otp: alertData.id
            });
          }
        }
      ]
    }).then((alert: any) => {
      alert.present();
    });
  }

  doOTP(obj: any) {
    return new Promise((resolve, reject) => {
      this.otp_qr = "";
      const op_ = obj && obj.op ? obj.op : null;
      if (op_) {
        if (op_ === "hide") {
          this.otp_show = false;
          resolve(true);
        } else {
          this.otp_process = true;
          this.otp_show = false;
          this.auth.OTP(obj).then((res: any) => {
            if (res && res.result) {
              this.otp_qr = res.qr;
              if (op_ === "reset" || op_ === "show") {
                this.otp_show = true;
                resolve(true);
              } else if (op_ === "validate") {
                if (res.success) {
                  this.misc.doMessage("OTP validated successfully", "success");
                  resolve(true);
                } else {
                  const err_ = "OTP does not match";
                  this.misc.doMessage(err_, "error");
                  reject(err_);
                }
              } else if (op_ === "request") {
                this.misc.doMessage("Backup OTP has been sent by email", "success");
                resolve(true);
              } else {
                const err_ = "invalid operation";
                this.misc.doMessage(err_, "error");
                reject(err_);
              }
            } else {
              this.misc.doMessage(res.msg, "error");
              reject(res.msg);
            }
          }).catch((error: any) => {
            this.misc.doMessage(error, "error");
            reject(error);
          }).finally(() => {
            this.otp_process = false;
          });
        }
      }
    });
  }

  set_pagination(event: any) {
    const val_ = event.target.value;
    this.storage.set("LSPAGINATION", val_).then(() => {
      this.pagination_ = val_;
    });
  }

}
