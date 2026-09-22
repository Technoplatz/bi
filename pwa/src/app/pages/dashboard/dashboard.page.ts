/*
Technoplatz BI

Copyright ©Technoplatz IT Solutions GmbH, Mustafa Mat

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
*/

import { CommonModule } from "@angular/common";
import { TranslatePipe } from "@ngx-translate/core";
import { IonButton, IonCol, IonContent, IonGrid, IonIcon, IonRow, IonSpinner, IonText } from "@ionic/angular";
import { InnerFooterComponent } from "../../components/inner-footer/inner-footer.component";
import { Component, OnInit, ChangeDetectionStrategy } from "@angular/core";
import { Crud } from "../../classes/crud";
import { Miscellaneous } from "../../classes/misc";
import { Auth } from "../../classes/auth";
import { environment } from "../../../environments/environment";

@Component({
  // ported code updates plain fields in promise callbacks; angular 22 components are OnPush by default
  changeDetection: ChangeDetectionStrategy.Eager,
  imports: [CommonModule, TranslatePipe, IonButton, IonCol, IonContent, IonGrid, IonIcon, IonRow, IonSpinner, IonText, InnerFooterComponent],
  selector: "app-dashboard",
  templateUrl: "./dashboard.page.html",
  styleUrl: "./dashboard.page.scss"
})

export class DashboardPage implements OnInit {
  public announcements_: any = [];
  public loadingText: string = environment.misc.loadingText;
  public flashsizes_: any = environment.flashsizes;
  public visuals_: any = [];
  public perm_: boolean = false;

  constructor(
    private crud: Crud,
    public misc: Miscellaneous,
    private auth: Auth
  ) {
    this.auth.user.subscribe((res: any) => {
      this.perm_ = res && res.perm;
    });
  }

  ngOnInit() {
    this.announcements_ = [];
    this.crud.get_announcements().then((res: any) => {
      this.announcements_ = res.data ? res.data.slice(0, 15) : [];
    }).catch((err_: any) => {
      console.warn("announcements not loaded", err_);
    });
  }

  ionViewDidEnter() {
    this.crud.get_visuals(null).then((visuals_: any) => {
      this.visuals_ = visuals_.visuals;
      for (let ix_: number = 0; ix_ < this.visuals_.length; ix_++) {
        this.visuals_[ix_].is_loaded = false;
        this.crud.get_visual(this.visuals_[ix_].id).then((visual_: any) => {
          this.visuals_[ix_].data = visual_.visual.data;
          this.visuals_[ix_].fields = visual_.visual.fields;
          this.visuals_[ix_].count = visual_.visual.count;
        }).catch((err_: any) => {
          this.visuals_[ix_].error = err_;
        }).finally(() => {
          this.visuals_[ix_].is_loaded = true;
        });
      }
    }).catch((err_: any) => {
      console.warn("visuals not loaded", err_);
    });
  }

  orderByIndex = (a: any, b: any): number => {
    return a.value.index < b.value.index ? -1 : (b.value.index > a.value.index ? 1 : 0);
  }

}
