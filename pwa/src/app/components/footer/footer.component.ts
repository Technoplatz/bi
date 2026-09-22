import { Component, ChangeDetectionStrategy } from "@angular/core";
import { IonCol, IonFooter, IonGrid, IonRow } from "@ionic/angular";
import { TranslatePipe } from "@ngx-translate/core";
import { environment } from "../../../environments/environment";

@Component({
  // ported code updates plain fields in promise callbacks; angular 22 components are OnPush by default
  changeDetection: ChangeDetectionStrategy.Eager,
  selector: "app-footer",
  imports: [IonFooter, IonGrid, IonRow, IonCol, TranslatePipe],
  templateUrl: "./footer.component.html",
  styleUrl: "./footer.component.scss"
})
export class FooterComponent {
  public version_ = environment.appVersion;
}
