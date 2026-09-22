import { Component, OnDestroy, OnInit } from "@angular/core";
import { IonButton, IonHeader, IonIcon, IonItem, IonLabel, IonList, IonToolbar } from "@ionic/angular";
import { TranslatePipe } from "@ngx-translate/core";
import { Subscription } from "rxjs";
import { environment } from "../../../environments/environment";
import { Miscellaneous } from "../../classes/misc";
import { Auth } from "../../classes/auth";
import { Crud } from "../../classes/crud";

@Component({
  selector: "app-menu",
  imports: [IonHeader, IonToolbar, IonList, IonItem, IonLabel, IonButton, IonIcon, TranslatePipe],
  templateUrl: "./menu.component.html",
  styleUrl: "./menu.component.scss"
})
export class MenuComponent implements OnInit, OnDestroy {
  public version = environment.appVersion;
  public release = environment.release;
  public companyName = environment.companyName;
  public segmentsadm: any = [];
  public user_: any;
  public perm_ = false;
  public collections_: any = [];
  private subs_: Subscription[] = [];

  constructor(public misc: Miscellaneous, private auth: Auth, private crud: Crud) { }

  ngOnInit() {
    this.subs_.push(this.crud.collections.subscribe((res: any) => {
      this.collections_ = res && res.data ? res.data : [];
    }));
    this.subs_.push(this.auth.user.subscribe((res: any) => {
      this.user_ = res;
      this.perm_ = !!(res && res.perm);
      this.segmentsadm = res && res.perm ? environment.segmentsadm : [];
    }));
  }

  ngOnDestroy() {
    this.subs_.forEach((s) => s.unsubscribe());
  }

  sign_out() {
    this.auth.sign_out().catch((error: any) => console.error("signout error", error?.msg ?? error));
  }
}
