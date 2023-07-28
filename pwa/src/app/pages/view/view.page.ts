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
import { AlertController } from "@ionic/angular";
import { Router } from "@angular/router";
import { Crud } from "../../classes/crud";
import { Auth } from "../../classes/auth";
import { Miscellaneous } from "../../classes/misc";
import { environment } from "../../../environments/environment";

@Component({
  selector: "app-view",
  templateUrl: "./view.page.html",
  styleUrls: ["./view.page.scss"]
})

export class ViewPage implements OnInit {
  public loadingText: string = environment.misc.loadingText;
  public defaultColumnWidth: number = environment.misc.defaultColumnWidth;
  public header: string = "SHARED VIEWS";
  public subheader: string = "";
  public user: any = null;
  public id: string = "";
  public reconfig: boolean = false;
  public data: any = [];
  public limit: number = environment.misc.limit;
  public count: number = 0;
  public multicheckbox: boolean = false;
  public is_initialized: boolean = false;
  public columns_: any;
  public view_mode: any = {};
  public otp_show: boolean = false;
  public otp_qr: string = "";
  public in_otp_process: boolean = false;
  public in_otp_process_test: boolean = false;
  public pivot_: string = "";
  public view_id: string = "";
  public view_count: number = 0;
  public view_properties: any = {};
  public view_properties_: any = {};
  public is_url_copied: boolean = false;
  public accountf_api_key: string = "";
  public viewurl_: string = "";
  public is_api_key_copied: boolean = false;
  private segment = "data";
  private is_selected: boolean = false;
  private views: any = [];
  private submenu: string = "";
  private collections: any = [];
  private apiHost: string = "";
  private sweeped: any = [];
  private view_structure: any;
  private menu: string = "";
  private col_structure: any = {};
  private user_: any;
  public col_id: string = "";
  public collections_: any;
  public charts_: any = null;
  public is_saving: boolean = false;
  public jeopen: boolean = false;
  public schemevis: any = "hide";
  public view: any = null;
  public view_: any = {};
  public cron_: string = "";

  constructor(
    private crud: Crud,
    private auth: Auth,
    private alert: AlertController,
    private router: Router,
    public misc: Miscellaneous
  ) {
    this.user_ ? null : this.user_ = this.auth.user.subscribe((res: any) => {
      this.user = res ? res : null;
      this.accountf_api_key = res && res.api_key ? res.api_key : null;
    });
    this.crud.charts.subscribe((res: any) => {
      if (res && res.views) {
        this.charts_ = res.views;
        console.log("*** this.charts_", this.charts_);
      }
    });
    this.misc.getAPIUrl().then((apiHost: any) => {
      this.apiHost = apiHost;
    });
  }

  ngOnDestroy() {
    this.auth.user.unsubscribe;
  }

  ngOnInit() {
    this.menu = this.router.url.split("/")[1];
    this.id = this.submenu = this.router.url.split("/")[2];
    this.view = this.charts_.filter((obj: any) => obj.id === this.id)[0];
    if(this.view) {
      this.view_ = this.view.view;
      this.subheader = this.view.view.title;
      this.data = this.view.data ? this.view.data : [];
      const crontab_ = this.view_.scheduled_cron ? this.view_.scheduled_cron.split(' ') : null;
      this.cron_ = crontab_ ? "min=" + crontab_[0] + " hour=" + crontab_[1] + " day=" + crontab_[2] + " month=" + crontab_[3] + " week_days=" + crontab_[4] : "";
      this.view_properties = this.view.properties;
      this.view_properties_ = Object.keys(this.view.properties);
      this.view_count = this.data && this.data.length > 0 ? this.data.length : 0;
      this.col_id = this.view.collection;
      this.pivot_ = this.view && this.view.pivot ? this.view.pivot : null;
      this.viewurl_ = this.apiHost + "/get/view/" + this.view.id + "?k=" + this.accountf_api_key;
    }
    this.is_initialized = true;
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
              if (["reset", "show"].includes(op_)) {
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
                this.misc.doMessage("Backup OTP has been sent by email", "success");
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

  async doAnnounceNow(scope: string) {
    if (!this.in_otp_process) {
      scope === "live" ? this.in_otp_process = true : this.in_otp_process_test = true;
      this.doOTP({
        op: "request"
      }).then(() => {
        this.in_otp_process = this.in_otp_process_test = false;
        this.alert.create({
          cssClass: "alert-class",
          header: scope === "live" ? "LIVE Announcement!" : "TEST Announcement",
          subHeader: "Please enter your Two-Factor Authorization Code",
          inputs: [
            {
              name: "id",
              value: null,
              type: "text",
              placeholder: "000000"
            }
          ],
          buttons: [
            {
              text: "Cancel",
              role: "cancel",
              cssClass: "primary",
              handler: () => { }
            }, {
              text: "CONFIRM",
              handler: (announceData: any) => {
                this.misc.apiCall("crud", {
                  op: "announce",
                  collection: this.view.collection,
                  id: this.view.id,
                  tfac: announceData && announceData.id ? announceData.id : null,
                  scope: scope
                }).then(() => {
                  this.misc.doMessage("view has been announced successfully", "success");
                }).catch((error: any) => {
                  this.misc.doMessage(error, "error");
                  console.error(error);
                });
              }
            }
          ]
        }).then((alert: any) => {
          alert.present();
        });
      }).catch((error: any) => {
        this.in_otp_process = this.in_otp_process_test = false;
        console.error(error);
        this.misc.doMessage(error, "error");
      });
    }
  }

  doCopy(tocopy_: string) {
    const copied_ = tocopy_ === "api_key" ? this.accountf_api_key : tocopy_ === "view" ? this.viewurl_ : "";
    this.is_api_key_copied = tocopy_ === "api_key" ? true : false;
    this.is_url_copied = ["view", "collection"].includes(tocopy_) ? true : false;
    this.misc.copyToClipboard(copied_).then(() => { }).catch((error: any) => {
      console.error("not copied", error);
    }).finally(() => {
      this.is_api_key_copied = false;
      this.is_url_copied = false;
    });
  }

  doSaveView() {
    this.is_saving = true;
    this.misc.apiCall("/crud", {
      op: "saveview",
      id: this.id,
      view: this.view_,
      collection: this.col_id
    }).then(() => {
      window.location.reload();
    }).catch((error: any) => {
      this.misc.doMessage(error, "error");
    }).finally(() => {
      this.is_saving = false;
    });
  }

}
