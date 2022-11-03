import { Component, OnInit, Input } from "@angular/core";
import { environment } from "../../../environments/environment";
import * as shape from "d3-shape";

@Component({
  selector: "app-charts",
  templateUrl: './charts.component.html',
  styleUrls: ['./charts.component.scss']
})

export class ChartsComponent implements OnInit {
  @Input() chart: any;
  @Input() width: any;
  public data: any = [];
  public chartStyle: string = "";
  public publicshowXAxis: boolean = false;
  public showXAxis: boolean = false;
  public showYAxis: boolean = false;
  public gradient: boolean = false;
  public showLegend: boolean = false;
  public showXAxisLabel: boolean = false;
  public showYAxisLabel: boolean = false;
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
    this.data = this.chart.data;
    this.chartStyle = this.chart.style;
    this.showXAxis = this.chart.xaxis_show;
    this.showYAxis = this.chart.yaxis_show;
    this.showLegend = this.chart.legend_show;
    this.xAxisLabel = this.chart.xaxis_label ? this.chart.xaxis_label : this.chart.xaxis;
    this.yAxisLabel = this.chart.yaxis_label ? this.chart.yaxis_label :  this.chart.yaxis;
    this.legendTitle = this.chart.legend_title ? this.chart.legend_title : this.chart.legend;
    this.showDataLabel = this.chart.datalabel_show;
    this.showGridLines = this.chart.grid_show;
    this.showXAxisLabel = this.chart.xaxis_label ? true : false;
    this.showYAxisLabel = this.chart.yaxis_label ? true : false;
    this.gradient = this.chart.gradient;
    this.curve = shape.curveCardinal;
    this.colorScheme = {
      domain: this.chart.color_scheme
    }
    this.view = this.width > this.minWidth ? [this.width - 16, this.width * 0.55] : [];
    this.ok = true;
  }

  onSelect(event: any) {
    console.log("*** event", event);
  }
}
