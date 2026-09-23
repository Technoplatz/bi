import { Component, } from "@angular/core";
import { IonCol, IonFooter, IonGrid, IonRow } from "@ionic/angular";
import { TranslatePipe } from "@ngx-translate/core";
import { environment } from "../../../environments/environment";

@Component({
  selector: "app-footer",
  imports: [IonFooter, IonGrid, IonRow, IonCol, TranslatePipe],
  templateUrl: "./footer.component.html",
  styleUrl: "./footer.component.scss"
})
export class FooterComponent {
  public version_ = environment.appVersion;
}
