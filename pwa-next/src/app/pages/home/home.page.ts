import { Component, OnInit, ChangeDetectionStrategy } from "@angular/core";
import { IonButton, IonCol, IonContent, IonGrid, IonHeader, IonIcon, IonRow, IonToolbar } from "@ionic/angular";
import { Storage } from "@ionic/storage-angular";
import { TranslatePipe } from "@ngx-translate/core";
import { Miscellaneous } from "../../classes/misc";
import { FooterComponent } from "../../components/footer/footer.component";
import { LangComponent } from "../../components/lang/lang.component";

@Component({
  // ported code updates plain fields in promise callbacks; angular 22 components are OnPush by default
  changeDetection: ChangeDetectionStrategy.Eager,
  selector: "app-home",
  imports: [IonHeader, IonToolbar, IonGrid, IonRow, IonCol, IonContent, IonIcon, IonButton, TranslatePipe, FooterComponent, LangComponent],
  templateUrl: "./home.page.html",
  styleUrl: "./home.page.scss"
})
export class HomePage implements OnInit {
  public user: any;

  constructor(public misc: Miscellaneous, private storage: Storage) { }

  ngOnInit() {
    this.storage.get("LSUSERMETA").then((LSUSERMETA: any) => {
      this.user = LSUSERMETA ? LSUSERMETA : null;
    });
  }
}
