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

import { Component, OnInit, ViewChild } from "@angular/core";
import { ModalController, AlertController, IonSelect } from "@ionic/angular";
import { Router } from "@angular/router";
import { Storage } from "@ionic/storage";
import { Crud } from "../../classes/crud";
import { Auth } from "../../classes/auth";
import { Miscellaneous } from "../../classes/misc";
import { environment } from "../../../environments/environment";
import { CrudPage } from "../crud/crud.page";

@Component({
  selector: "app-view",
  templateUrl: "./view.page.html",
  styleUrls: ["./view.page.scss"]
})

export class ViewPage implements OnInit {
  @ViewChild("select0") selectRef?: IonSelect;
  public loadingText: string = environment.misc.loadingText;
  public defaultColumnWidth: number = environment.misc.defaultColumnWidth;
  public header: string = "Views";
  public subheader: string = "";
  public user: any = null;
  public is_crud: boolean = false;
  public paget: any = [];
  public id: string = "";
  public reconfig: boolean = false;
  public searched: any = null;
  public data: any = [];
  public selected: any = [];
  public pages: any = [];
  public limit: number = environment.misc.limit;
  public page: number = 1;
  public count: number = 0;
  public is_loaded: boolean = true;
  public multicheckbox: boolean = false;
  public is_initialized: boolean = false;
  public is_pane_ok: boolean = false;
  public actions: any = [];
  public columns_: any;
  public view_mode: any = {};
  public otp_show: boolean = false;
  public otp_qr: string = "";
  public in_otp_process: boolean = false;
  public in_otp_process_test: boolean = false;
  public pivot_: string = "";
  public statistics_key_: string = "";
  public statistics_: any = null;
  public view_id: string = "";
  public view_count: number = 0;
  public view_properties: any = {};
  public view_properties_: any = {};
  public subscribers: string = "";
  public view: any = null;
  public is_url_copied: boolean = false;
  public is_apikey_enabled: boolean = false;
  public accountf_apikey: string = "";
  public viewurl_: string = "";
  public viewurl_masked_: string = "";
  public is_apikey_copied: boolean = false;
  private segment = "data";
  private page_start: number = 1;
  private is_selected: boolean = false;
  private views: any = [];
  private submenu: string = "";
  private collections: any = [];
  private apiHost: string = "";
  private sweeped: any = [];
  private view_structure: any;
  private menu: string = "";
  private page_end: number = 1;

  private col_structure: any = {};
  public col_id: string = "";
  public collections_: any;
  public user_: any;

  constructor(
    private storage: Storage,
    private crud: Crud,
    private auth: Auth,
    private modal: ModalController,
    private alert: AlertController,
    private router: Router,
    public misc: Miscellaneous
  ) {
    this.misc.getAPIHost().then((apiHost: any) => {
      this.apiHost = apiHost;
    });
    this.collections_ = this.crud.collections.subscribe((res: any) => {
      this.collections = res && res.data ? res.data : [];
    });
    this.user_ = this.auth.user.subscribe((res: any) => {
      this.user = res ? res : null;
      this.accountf_apikey = res && res.apikey ? res.apikey : null;
    });
  }

  ngOnDestroy() {
    this.collections_ = null;
    this.user_ = null;
  }

  ngOnInit() {
    this.menu = this.router.url.split("/")[1];
    this.id = this.submenu = this.router.url.split("/")[2];
    this.RefreshData(0).then(() => { }).finally(() => {
      this.is_initialized = true;
    });
  }

  RefreshData(p: number) {
    return new Promise((resolve, reject) => {
      this.is_loaded = this.is_selected = false;
      this.misc.apiCall("crud", {
        op: "view",
        _id: "",
        vie_id: this.id,
        source: "internal",
        page: p,
        limit: this.limit
      }).then((res: any) => {
        this.col_structure = res && res.col_structure ? res.col_structure : null;
        this.col_id = res && res.col_id ? res.col_id : null;
        this.view = res && res.record ? res.record : null;
        this.data = res && res.data ? res.data : [];
        this.view_count = res && res.count ? res.count : 0;
        this.view_properties = res.properties;
        this.view_properties_ = Object.keys(res.properties);
        this.view_structure = res.structure;
        this.subheader = this.view.vie_title;
        this.viewurl_ = this.apiHost + "/get/view/" + this.view._id + "?k=" + this.accountf_apikey;
        this.storage.set("LSVIEW-" + this.id, this.view).then(() => {
          this.crud.Pivot(this.view._id, this.accountf_apikey).then((res: any) => {
            this.pivot_ = res && res.pivot ? res.pivot : null;
            const statistics_ = res && res.statistics ? res.statistics : null;
            this.statistics_key_ = this.view.vie_pivot_values ? this.view.vie_pivot_values[0].key : null;
            this.statistics_ = statistics_ && this.statistics_key_ ? statistics_[this.statistics_key_] : null;
          }).catch((error: any) => {
            console.error("*** view mode", error);
            this.misc.doMessage(error.error.msg, "error");
          }).finally(() => {
            resolve(true);
          });
        });
      }).finally(() => {
        this.is_loaded = true;
      });
    });
  }

  async goCrud(rec: any, op: string) {
    const modal = await this.modal.create({
      component: CrudPage,
      backdropDismiss: false,
      cssClass: "crud-modal",
      componentProps: {
        shuttle: {
          op: op,
          collection: this.col_id,
          collections: this.collections ? this.collections : [],
          views: this.views ? this.views : [],
          user: this.user,
          data: rec,
          structure: this.col_structure,
          sweeped: this.sweeped[this.segment] && op === "action" ? this.sweeped[this.segment] : [],
          filter: [],
          actions: this.actions && this.actions.length > 0 ? this.actions : [],
          actionix: -1,
          view: this.view,
          barcoded: null
        }
      }
    });
    modal.onDidDismiss().then((res: any) => {
      if (res.data.modified) {
        this.RefreshData(0);
      }
    });
    return await modal.present();
  }

  async doViewSettings() {
    const modal = await this.modal.create({
      component: CrudPage,
      backdropDismiss: false,
      cssClass: "crud-modal",
      componentProps: {
        shuttle: {
          op: "update",
          collection: "_view",
          collections: this.collections ? this.collections : [],
          views: this.views ? this.views : [],
          user: this.user,
          data: this.view,
          structure: this.view_structure,
          direct: -1
        }
      }
    });
    modal.onDidDismiss().then((res: any) => {
      if (res.data.modified) {
        if (["remove", "restore"].includes(res.data.op)) {
          this.misc.navi.next("dashboard");
        } else {
          window.location.reload();
        }
      }
    });
    return await modal.present();
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

  async doAnnounceNow(view: any, scope: string) {
    if (!this.in_otp_process) {
      scope === "live" ? this.in_otp_process = true : this.in_otp_process_test = true;
      this.doOTP({
        op: "request"
      }).then(() => {
        this.in_otp_process = this.in_otp_process_test = false;
        this.alert.create({
          cssClass: "my-custom-class",
          header: scope === "live" ? "LIVE Announcement!" : "TEST Announcement",
          subHeader: "Please enter your Two-Factor Authorization Code",
          inputs: [
            {
              name: "id",
              value: null,
              type: "text",
              placeholder: "Enter your OTP"
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
                  collection: this.id,
                  view: view,
                  tfac: announceData && announceData.id ? announceData.id : null,
                  scope: scope
                }).then(() => {
                  this.misc.doMessage("view was announced successfully", "success");
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

  doCopy(v: string) {
    const s = v === "apikey" ? this.accountf_apikey : v === "view" ? this.viewurl_ : "";
    this.is_apikey_copied = v === "apikey" ? true : false;
    this.is_url_copied = ["view", "collection"].includes(v) ? true : false;
    this.misc.copyToClipboard(s).then(() => { }).catch((error: any) => {
      console.error("not copied", error);
    }).finally(() => {
      this.is_apikey_copied = false;
      this.is_url_copied = false;
    });
  }

  SwitchSelectData(event: any) {
    this.selected = new Array(this.data.length).fill(event);
    this.GetIsSelectData();
  }

  async GetIsSelectData() {
    this.sweeped[this.segment] = [];
    const q = await this.selected.findIndex((obj: boolean) => obj === true);
    q >= 0 ? (this.is_selected = true) : (this.is_selected = false);
    const r = await this.selected.reduce((acc: any, val: any, index: number) => {
      const q = val === true ? this.sweeped[this.segment].push(this.data[index]._id) : null;
    }, []);
  }

  SetSelectData(i: number, event: any) {
    this.selected[i] = event.detail.checked;
    this.GetIsSelectData();
  }

}
