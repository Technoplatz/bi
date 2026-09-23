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
*/

import { NgxChartsModule } from '@swimlane/ngx-charts';
import { Component, computed, input } from '@angular/core';
import * as shape from 'd3-shape';
import { LegendPosition } from '@swimlane/ngx-charts';

@Component({
  imports: [NgxChartsModule],
  selector: 'app-chart',
  templateUrl: './chart.component.html',
  styleUrl: './chart.component.scss',
})
export class ChartComponent {
  readonly item = input<any>(undefined);
  readonly width = input<any>(undefined);
  private minWidth: number = 16;
  // everything the template reads derives from the two inputs
  private readonly view_ = computed(() => (this.item() && this.item().view ? this.item().view : {}));
  readonly series = computed(() => (this.item() && this.item().series ? this.item().series : []));
  readonly chartStyle = computed<string>(() => this.view_().chart_type ?? '');
  readonly showXAxis = computed<boolean>(() => !!this.view_().chart_xaxis);
  readonly showYAxis = computed<boolean>(() => !!this.view_().chart_yaxis);
  readonly showXAxisLabel = computed<boolean>(() => !!this.view_().chart_xaxis_label);
  readonly showYAxisLabel = computed<boolean>(() => !!this.view_().chart_yaxis_label);
  readonly showLegend = computed<boolean>(() => !!this.view_().chart_legend);
  // this.xAxisLabel = this.showXAxisLabel && view_.xaxis_label ? view_.xaxis_label : view_.xaxis;
  // this.yAxisLabel = this.showYAxisLabel && view_.yaxis_label ? view_.yaxis_label :  view_.yaxis;
  // this.legendTitle = this.showLegend && view_.legend_title ? view_.legend_title : view_.legend;
  readonly showDataLabel = computed<boolean>(() => !!this.view_().chart_label);
  readonly showGridLines = computed<boolean>(() => !!this.view_().chart_grid);
  readonly gradient = computed<boolean>(() => !!this.view_().chart_gradient);
  readonly colorSchema = computed<any>(() =>
    this.view_().chart_colors && this.view_().chart_colors.length > 0
      ? { domain: this.view_().chart_colors }
      : null,
  );
  readonly dimension = computed<[number, number] | undefined>(() =>
    this.width() > this.minWidth ? [this.width() - 16, this.width() * 0.75] : undefined,
  );
  readonly ok = computed<boolean>(() => !!this.item());
  public publicshowXAxis: boolean = false;
  public noBarWhenZero: boolean = true;
  public roundDomains: boolean = false;
  public xAxisLabel: string = '';
  public yAxisLabel: string = '';
  public legendTitle: string = '';
  public legendPosition: LegendPosition = LegendPosition.Right;
  public tooltipDisabled: boolean = false;
  public curve: any = shape.curveCardinal;

  onSelect(event: any) {
    console.log('*** event', event);
  }
}
