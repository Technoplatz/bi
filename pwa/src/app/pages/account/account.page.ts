/*
Technoplatz BI

Copyright (C) 2019-2023 Technoplatz IT Solutions GmbH, Mustafa Mat

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
import { Miscellaneous } from "../../classes/miscellaneous";
import { environment } from "../../../environments/environment";
import { Router } from "@angular/router";

@Component({
  selector: "app-account",
  templateUrl: "./account.page.html",
  styleUrls: ["./account.page.scss"]
})

export class AccountPage implements OnInit {
  public header: string = "Account";
  public user: any = null;
  public is_initialized: boolean = false;
  public menu: string = "";
  public submenu: string = "";
  public themes: any = environment.themes;
  public perm: boolean = false;
  public accountf_apikey: string = "";
  public is_apikey_copied: boolean = false;
  public is_apikey_enabled: boolean = false;
  public accountf_apikeydate: any = null;
  public is_processing_account: boolean = false;
  public is_url_copied: boolean = false;
  public viewurl_: string = "";
  public viewurl_masked_: string = "";
  public qr_exists: boolean = false;
  public otp_show: boolean = false;
  public otp_qr: string = "";

  constructor(
    private storage: Storage,
    private auth: Auth,
    private router: Router,
    private misc: Miscellaneous,
    private alert: AlertController
  ) { }

  ngOnDestroy() { }

  ngOnInit() {
    this.menu = this.router.url.split("/")[1];
    this.submenu = this.router.url.split("/")[2];
    this.header = this.submenu === "apikey" ? "API Key" : this.submenu === "preferences" ? "Preferences" : this.submenu === "signout" ? "Sign Out" : this.submenu === "security" ? "Security" : this.submenu;
    this.is_initialized = false;
    this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
      this.user = LSUSERMETA;
      this.perm = LSUSERMETA && LSUSERMETA.perm ? true : false;
      this.accountf_apikey = LSUSERMETA.apikey;
      this.is_initialized = true;
    });
  }

  doTheme(LSTHEME: any) {
    this.storage.set("LSTHEME", LSTHEME).then(() => {
      document.documentElement.style.setProperty("--ion-color-primary", LSTHEME.color);
    });
  }

  doSignout() {
    this.auth.Signout().then(() => {
      console.log("*** signed out");
    }).catch((error: any) => {
      console.error("signout error", error.message);
    });
  }

  doCopy(w: string) {
    const s = w === "apikey" ? this.accountf_apikey : w === "view" ? this.viewurl_ : "";
    this.is_apikey_copied = w === "apikey" ? true : false;
    this.is_url_copied = w === "view" || w === "collection" ? true : false;
    this.misc.copyToClipboard(s).then(() => { }).catch((error: any) => {
      console.error("not copied", error);
    }).finally(() => {
      this.is_apikey_copied = false;
      this.is_url_copied = false;
    });
  }

  doAccount(s: string) {
    return new Promise((resolve) => {
      this.auth.Account(s).then((res: any) => {
        if (s === "apikeygen" || s === "apikeyget") {
          this.accountf_apikey = res && res.user && res.user.apikey ? res.user.apikey : null;
          this.accountf_apikeydate = res && res.user && res.user.apikey_modified_at ? res.user.apikey_modified_at.$date : null;
          s === "apikeygen" ? this.doApiKeyEnabled() : null;
        }
        resolve(true);
      }).catch((error: any) => {
        this.qr_exists = false;
        console.error(error);
        this.misc.doMessage(error, "error");
      });
    });
  }

  doApiKeyEnabled() {
    if (!this.is_apikey_enabled) {
      this.is_apikey_enabled = true;
      setTimeout(() => {
        this.is_apikey_enabled = false;
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
      subHeader: "Validate One-Time Password",
      message: "Please enter the current one time password generated by App",
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
          this.auth.OTP(obj).then((res: any) => {
            if (res && res.result) {
              this.otp_qr = res.qr;
              if (op_ === "reset" || op_ === "show") {
                this.otp_show = true;
                resolve(true);
              } else if (op_ === "validate") {
                if (res.success) {
                  this.otp_show = false;
                  this.misc.doMessage("OTP validated successfully", "success");
                  resolve(true);
                } else {
                  this.otp_show = false;
                  const err_ = "OTP does not match";
                  this.misc.doMessage(err_, "error");
                  console.error(err_);
                  reject(err_);
                }
              } else if (op_ === "request") {
                this.misc.doMessage("Backup OTP was sent by email", "success");
                resolve(true);
              } else {
                const err_ = "invalid operation";
                console.error(err_);
                this.misc.doMessage(err_, "error");
                reject(err_);
              }
            } else {
              this.misc.doMessage(res.msg, "error");
              reject(res.msg);
            }
          }).catch((error: any) => {
            this.otp_show = false;
            console.error(error);
            this.misc.doMessage(error, "error");
            reject(error);
          });
        }
      }
    });
  }

}
