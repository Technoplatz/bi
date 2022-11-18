import { Component, OnInit } from "@angular/core";
import { ActivatedRoute } from "@angular/router";
import { ModalController } from "@ionic/angular";
import { Auth } from "../../classes/auth";
import { SignPage } from "../sign/sign.page";

@Component({
  selector: "app-main",
  templateUrl: "./main.page.html",
  styleUrls: ["./main.page.scss"],
})
export class MainPage implements OnInit {
  public products: any = [];
  public user: any;

  constructor(
    private route: ActivatedRoute,
    private auth: Auth,
    private modal: ModalController
  ) { }

  ngOnInit() {
    this.route.data.subscribe((data: any) => {
      this.user = data.user;
    });
    this.auth.authStateChange.subscribe((user: any) => {
      this.user = user;
    });
  }

  async doSignup() {
    const modal = await this.modal.create({
      component: SignPage,
      backdropDismiss: false,
      cssClass: "signup-modal",
      componentProps: {
        op: "signup",
        user: this.user
      }
    });
    return await modal.present();
  }

}