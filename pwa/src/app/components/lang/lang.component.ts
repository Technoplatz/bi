/*
Technoplatz BI

Copyright ©Technoplatz IT Solutions GmbH, Mustafa Mat

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
import { environment } from "../../../environments/environment";

@Component({
  selector: "app-lang",
  templateUrl: "./lang.component.html",
  styleUrls: ["./lang.component.scss"],
})
export class LangComponent implements OnInit {
  public version_ = environment.appVersion;
  public langcss: string = "selection-passive";
  public lang: string = "de";
  public langs_: any = [];
  public lang_proc_ = false;
  public langsoriginal: any = [
    { id: "en", name: "EN", class: "selection-passive" },
    { id: "de", name: "DE", class: "selection-passive" },
    { id: "tr", name: "TR", class: "selection-passive" },
  ];

  constructor(
    private misc: Miscellaneous,
  ) {
    this.langs_ = this.langsoriginal;
    this.misc.locale().then((LSLOCALE_: any) => {
      const index = this.langs_.findIndex((obj: any) => obj["id"] === LSLOCALE_);
      this.langs_[index].class = "selection-active";
    });
  }

  ngOnInit() { }

  do_set_locale(i: number, lang_: string) {
    this.lang_proc_ = true;
    for (let j = 0; j < this.langsoriginal.length; j++) {
      this.langs_[j].class = "selection-passive";
      j === this.langsoriginal.length - 1
        ? this.misc.set_locale(lang_).then(() => {
          this.langs_[i].class = "selection-active";
          setTimeout(() => {
            this.lang_proc_ = false;
          }, 500);
        })
        : null;
    }
  }
}
