/*
Technoplatz BI

Copyright (C) 2020-2023 Technoplatz IT Solutions GmbH, Mustafa Mat

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see https://www.gnu.org/licenses.

If your software can interact with users remotely through a computer
network, you should also make sure that it provides a way for users to
get its source.  For example, if your program is a web application, its
interface could display a "Source" link that leads users to an archive
of the code.  There are many ways you could offer source, and different
solutions will be better for different programs; see section 13 for the
specific requirements.

You should also get your employer (if you work as a programmer) or school,
if any, to sign a "copyright disclaimer" for the program, if necessary.
For more information on this, and how to apply and follow the GNU AGPL, see
https://www.gnu.org/licenses.
*/

import { Component, OnInit } from "@angular/core";
import { Miscellaneous } from "../../classes/misc";
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
