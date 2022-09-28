import { Component, OnInit } from "@angular/core";
import { Miscellaneous } from "./../../classes/miscellaneous";
import { environment } from "./../../../environments/environment";

@Component({
  selector: "app-footer",
  templateUrl: "./footer.component.html",
  styleUrls: ["./footer.component.scss"],
})
export class FooterComponent implements OnInit {
  public version = environment.appVersion;
  public ok = false;
  public proc = false;
  public langcss: string = "lang-passive";
  public lang: string = "de";
  public langs: any = [];
  public langsoriginal: any = [
    { id: "en", name: "EN", class: "lang-passive" },
    { id: "de", name: "DE", class: "lang-passive" },
    { id: "tr", name: "TR", class: "lang-passive" },
  ];

  constructor(
    private misc: Miscellaneous
  ) { }

  ngOnInit() {
    this.langs = this.langsoriginal;
    this.misc.getLanguage().then((LSLANG) => {
      const index = this.langs.findIndex((obj: any) => obj["id"] === LSLANG);
      this.langs[index].class = "lang-active";
      setTimeout(() => {
        this.ok = true;
      }, 10);
    });
  }

  goSetLang(i: number, l: string) {
    this.proc = true;
    for (let j = 0; j < this.langsoriginal.length; j++) {
      this.langs[j].class = "lang-passive";
      const setLang =
        j === this.langsoriginal.length - 1
          ? this.misc.setLanguage(l).then(() => {
            this.langs[i].class = "lang-active";
            setTimeout(() => {
              this.proc = false;
            }, 500);
          })
          : null;
    }
  }

}
