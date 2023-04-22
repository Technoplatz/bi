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
import * as shape from "d3-shape";

@Component({
  selector: "app-chart",
  templateUrl: './chart.component.html',
  styleUrls: ['./chart.component.scss']
})

export class ChartComponent implements OnInit {
  @Input() item: any;
  @Input() width: any;
  public series: any = [];
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
  public dimension: any[] = [0, 0];
  public colorSchema: any = [];
  public curve: any;
  public ok: boolean = false;
  private minWidth: number = 16;

  constructor() { }

  ngOnInit() {
    this.ok = false;
  }

  ngOnChanges() {
    const view_ = this.item.self;
    this.series = this.item.series;
    this.chartStyle = view_.chart_type;
    this.showXAxis = view_.chart_xaxis;
    this.showYAxis = view_.chart_yaxis;
    this.showXAxisLabel = view_.chart_xaxis_label;
    this.showYAxisLabel = view_.chart_yaxis_label;
    this.showLegend = view_.chart_legend;
    // this.xAxisLabel = this.showXAxisLabel && view_.xaxis_label ? view_.xaxis_label : view_.xaxis;
    // this.yAxisLabel = this.showYAxisLabel && view_.yaxis_label ? view_.yaxis_label :  view_.yaxis;
    // this.legendTitle = this.showLegend && view_.legend_title ? view_.legend_title : view_.legend;
    this.showDataLabel = view_.chart_label;
    this.showGridLines = view_.chart_grid;
    this.gradient = view_.chart_gradient;
    this.curve = shape.curveCardinal;
    this.colorSchema = view_.chart_colors && view_.chart_colors.length > 0 ? {
      domain: view_.chart_colors
    } : null;
    this.dimension = this.width > this.minWidth ? [this.width - 16, this.width * 0.75] : [];
    this.ok = true;
  }

  onSelect(event: any) {
    console.log("*** event", event);
  }
}
