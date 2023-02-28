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

import { Component, OnInit, Input } from "@angular/core";
import { environment } from "../../../environments/environment";
import * as shape from "d3-shape";

@Component({
  selector: "app-charts",
  templateUrl: './charts.component.html',
  styleUrls: ['./charts.component.scss']
})

export class ChartsComponent implements OnInit {
  @Input() visual: any;
  @Input() width: any;
  public data: any = [];
  public chartStyle: string = "";
  public publicshowXAxis: boolean = false;
  public showXAxis: boolean = false;
  public showYAxis: boolean = false;
  public showXAxisLabel: boolean = false;
  public showYAxisLabel: boolean = false;
  public gradient: boolean = false;
  public showLegend: boolean = false;
  public showDataLabel: boolean = false;
  public showGridLines: boolean = false;
  public noBarWhenZero: boolean = true;
  public roundDomains: boolean = false;
  public xAxisLabel: string = "";
  public yAxisLabel: string = "";
  public legendTitle: string = "";
  public legendPosition: string = "right";
  public tooltipDisabled: boolean = false;
  public view: any[] = [0, 0];
  public colorScheme: any = environment.charts.colorScheme;
  public curve: any;
  public ok: boolean = false;
  private minWidth: number = 16;

  constructor() { }

  ngOnInit() {
    this.ok = false;
  }

  ngOnChanges() {
    this.data = this.visual.data;
    this.chartStyle = this.visual.style;
    this.showXAxis = this.visual.xaxis_show;
    this.showYAxis = this.visual.yaxis_show;
    this.showXAxisLabel = this.visual.xaxis_label_show;
    this.showYAxisLabel = this.visual.yaxis_label_show;
    this.showLegend = this.visual.legend_show;
    this.xAxisLabel = this.showXAxisLabel && this.visual.xaxis_label ? this.visual.xaxis_label : this.visual.xaxis;
    this.yAxisLabel = this.showYAxisLabel && this.visual.yaxis_label ? this.visual.yaxis_label :  this.visual.yaxis;
    this.legendTitle = this.showLegend && this.visual.legend_title ? this.visual.legend_title : this.visual.legend;
    this.showDataLabel = this.visual.datalabel_show;
    this.showGridLines = this.visual.grid_show;
    this.gradient = this.visual.gradient;
    this.curve = shape.curveCardinal;
    this.colorScheme = {
      domain: this.visual.color_scheme
    }
    this.view = this.width > this.minWidth ? [this.width - 16, this.width * 0.55] : [];
    this.ok = true;
  }

  onSelect(event: any) {
    console.log("*** event", event);
  }
}
