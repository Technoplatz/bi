import { Component, ChangeDetectionStrategy } from "@angular/core";
import { IonFooter } from "@ionic/angular";
import { TranslatePipe } from "@ngx-translate/core";
import { Miscellaneous } from "../../classes/misc";
import { LangComponent } from "../lang/lang.component";

@Component({
  // ported code updates plain fields in promise callbacks; angular 22 components are OnPush by default
  changeDetection: ChangeDetectionStrategy.Eager,
  selector: "app-inner-footer",
  imports: [IonFooter, TranslatePipe, LangComponent],
  templateUrl: "./inner-footer.component.html",
  styleUrl: "./inner-footer.component.scss"
})
export class InnerFooterComponent {
  constructor(public misc: Miscellaneous) { }
}
