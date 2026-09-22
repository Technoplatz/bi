import { Component } from "@angular/core";
import { IonButton, IonContent, IonIcon } from "@ionic/angular";
import { TranslatePipe } from "@ngx-translate/core";
import { Miscellaneous } from "../../classes/misc";

@Component({
  selector: "app-pending",
  imports: [IonContent, IonButton, IonIcon, TranslatePipe],
  template: `
    <ion-content class="ion-padding">
      <h2>{{ 'This page is being rebuilt' | translate }}</h2>
      <p>{{ 'It will be available in the next release of the new interface' | translate }}.</p>
      <ion-button fill="outline" (click)="misc.navi.next('/')"><ion-icon name="arrow-back-sharp"></ion-icon>{{ 'Back' | translate }}</ion-button>
    </ion-content>
  `
})
export class PendingPage {
  constructor(public misc: Miscellaneous) { }
}
