import { Component, OnInit, Input } from "@angular/core";
import { environment } from "./../../../environments/environment";

@Component({
  selector: "app-filter",
  templateUrl: "./filter.component.html",
  styleUrls: ["./filter.component.scss"]
})

export class FilterComponent implements OnInit {
  @Input() property_list: any;
  @Input() filters: any;
  public filterops: any = environment.filterops;

  constructor() { }

  ngOnInit() {
    this.property_list.push({key: "_id", value: "Record ID"});
    if (!this.filters || this.filters.length === 0) {
      this.filters = [{ "key": null, "op": null, "value": null }]
    }
  }

  doLineAdd(i: number) {
    this.filters[i].key && this.filters[i].op ? this.filters.push({
      key: null,
      op: null,
      value: null
    }) : null;
  }

  doLineRemove(i: number) {
    this.filters.splice(i, 1);
  }

}
