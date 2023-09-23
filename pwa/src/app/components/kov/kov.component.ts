/*
Technoplatz BI

Copyright (C) 2019-2023 Technoplatz IT Solutions GmbH, Mustafa Mat

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

import { Component, OnInit, Input } from "@angular/core";
import { environment } from "./../../../environments/environment";
import { ItemReorderEventDetail } from '@ionic/core';

@Component({
  selector: "app-kov",
  templateUrl: "./kov.component.html",
  styleUrls: ["./kov.component.scss"]
})

export class KovComponent implements OnInit {
  @Input() properties: any;
  @Input() data: any;
  @Input() field: any;
  @Input() op: string = "";
  public kovs: any = null;
  public type: string = "key";
  public ok: boolean = false;
  public filterops: any = environment.filterops;
  public fname: string = "";
  private hours_: any = [];
  private minutes_: any = [];
  private days_: any = [
    { "key": "mon" },
    { "key": "tue" },
    { "key": "wed" },
    { "key": "thu" },
    { "key": "fri" },
    { "key": "sat" },
    { "key": "sun" }
  ]
  private tags_ = [
    { "key": "#Managers" },
    { "key": "#Administrators" }
  ];
  private empty_ = [
    { "key": null }
  ];
  private dual_ = [
    { "key": null, "value": null }
  ];
  public keyop_ = [
    { key: "x-axis" },
    { key: "y-axis" },
    { key: "group" },
    { key: "data[count]" },
    { key: "data[sum]" }
  ];

  constructor() { }

  ngOnInit() {
    for (let h_ = 0; h_ < 24; h_++) {
      this.hours_.push({ "key": h_ });
    }
    for (let m_ = 0; m_ < 60; m_++) {
      this.minutes_.push({ "key": m_ });
    }
  }

  ngOnChanges() {
    this.ok = false;
    this.fname = this.field.name;
    if (["keyop", "keyvalue", "emptyfield"].includes(this.field.subType)) {
      this.type = this.field.subType;
    } else if (this.field.subType === "filter") {
      this.type = "keyopvalue";
    }
    if (["keyop", "keyvalue", "filter", "property"].includes(this.field.subType)) {
      this.kovs = this.properties;
    } else if (this.field.subType === "hour") {
      this.kovs = this.hours_;
    } else if (this.field.subType === "minute") {
      this.kovs = this.minutes_;
    } else if (this.field.subType === "day") {
      this.kovs = this.days_;
    } else if (this.field.subType === "tag") {
      this.kovs = this.tags_;
    } else if (this.field.subType === "string") {
      this.kovs = this.empty_;
    } else if (this.field.subType === "emptyfield") {
      this.kovs = this.dual_;
    }
    setTimeout(() => {
      this.ok = true;
    }, 1000);
  }

  doLineAdd(i: number) {
    if (i === -1 || !this.data[this.fname]) {
      this.data[this.fname] = [{ "key": null }];
    } else {
      if (this.type === "keyopvalue") {
        this.data[this.fname].push({
          key: null,
          op: null,
          value: null
        });
      } else if (this.type === "keyop") {
        this.data[this.fname].push({
          key: null,
          op: null
        });
      } else if (this.type === "keyvalue" || this.type === "emptyfield") {
        this.data[this.fname].push({
          key: null,
          value: null
        });
      } else if (this.type === "key") {
        this.data[this.fname].push({
          key: null
        });
      } else if (this.type === "other") {
        this.data[this.fname].push(null);
      }
    }
  }

  doLineRemove(i: number) {
    this.data[this.fname].splice(i, 1);
  }

  doReorder(ev: CustomEvent<ItemReorderEventDetail>, fn: string) {
    this.data[fn] = ev.detail.complete(this.data[fn]);
  }

}
