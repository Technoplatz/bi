import { Component } from "@angular/core";
import { Miscellaneous } from "../../classes/misc";
import { environment } from "../../../environments/environment";

@Component({
  selector: "app-lang",
  template: `
    <div class="flex-container">
      @for (item of langs_; track item.id; let i = $index) {
        <div [class]="item.class" (click)="do_set_locale(i, item.id)">{{ item.name }}</div>
      }
    </div>
  `,
  styleUrl: "./lang.component.scss"
})
export class LangComponent {
  public version_ = environment.appVersion;
  public lang_proc_ = false;
  public langs_ = [
    { id: "en", name: "EN", class: "selection-passive" },
    { id: "de", name: "DE", class: "selection-passive" },
    { id: "tr", name: "TR", class: "selection-passive" }
  ];

  constructor(private misc: Miscellaneous) {
    this.misc.locale().then((LSLOCALE_: any) => {
      const index = this.langs_.findIndex((obj) => obj.id === LSLOCALE_);
      if (index >= 0) {
        this.langs_[index].class = "selection-active";
      }
    });
  }

  do_set_locale(i: number, lang_: string) {
    this.lang_proc_ = true;
    this.langs_.forEach((l) => (l.class = "selection-passive"));
    this.misc.set_locale(lang_).then(() => {
      this.langs_[i].class = "selection-active";
      setTimeout(() => (this.lang_proc_ = false), 500);
    });
  }
}
