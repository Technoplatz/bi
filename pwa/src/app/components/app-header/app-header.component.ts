import { Component, OnInit, Input, SimpleChanges } from "@angular/core";
import { ModalController } from "@ionic/angular";
import { environment } from "../../../environments/environment";
import { SignPage } from "../../pages/sign/sign.page";
import { Auth } from "../../classes/auth";

@Component({
  selector: "app-header",
  templateUrl: "./app-header.component.html",
  styleUrls: ["./app-header.component.scss"],
})

export class AppHeaderComponent implements OnInit {
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
    private auth: Auth
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

  Signout() {
    this.auth.Signout().then(() => {
      console.log("*** signed out");
    }).catch((error: any) => {
      console.error("signout error", error.message);
    });
  }

}
