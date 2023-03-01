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

import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { ModalController } from "@ionic/angular";
import { environment } from "../../../environments/environment";
import { SignPage } from "../../pages/sign/sign.page";
import { Miscellaneous } from "../../classes/miscellaneous";

@Component({
  selector: "app-header",
  templateUrl: "./app-header.component.html",
  styleUrls: ["./app-header.component.scss"],
})

export class AppHeaderComponent implements OnInit {
  @Input() header: any;
  @Input() user: any;
  @Input() swu: boolean = false;
  @Input() net: boolean = false;
  private userData: any;
  public color: any = "primary";
  public colorContrast: any = "white";
  public isSignedIn: boolean = false;
  public name: any = null;
  public logo: string = environment.misc.logo;
  public swu_: boolean = false;
  public net_: boolean = false;
  public slideOpts = {
    initialSlide: 0,
    speed: 400,
    mode: "ios",
    autoplay: true,
  };

  constructor(
    private modal: ModalController,
    private misc: Miscellaneous
  ) { }

  ngOnInit() { }

  ngOnChanges(changes: SimpleChanges) {
    if (changes["user"]) {
      this.isSignedIn = changes["user"].currentValue ? true : false;
      this.userData = changes["user"].currentValue ? changes["user"].currentValue : null;
      this.name = changes["user"].currentValue ? changes["user"].currentValue["name"] : null;
    }
    if (changes["net"]) {
      this.net_ = changes["net"].currentValue ? true : false;
    }
    this.swu_ = changes["swu"] && changes["swu"].currentValue ? true : false;
  }

  async doSign(op: string) {
    const modal = await this.modal.create({
      component: SignPage,
      backdropDismiss: false,
      cssClass: "signin-modal",
      componentProps: {
        op: op,
        user: this.userData,
      }
    });
    return await modal.present();
  }

  doActivate() {
    window.location.reload();
  }

  doNavi(s: string, sub: any) {
    this.misc.navi.next({
      s: s,
      sub: sub,
    });
  }

  menuToggle() {
    this.misc.menutoggle.next();
  }

}
