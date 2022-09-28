import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { TranslateModule } from "@ngx-translate/core";
import { RouterModule } from "@angular/router";
import { AppHeaderComponent } from "./app-header/app-header.component";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { FooterComponent } from "./footer/footer.component";
import { FilterComponent } from "./filter/filter.component";
import { KovComponent } from "./kov/kov.component";
import { InnerFooterComponent } from "./inner-footer/inner-footer.component";
import { ModalFooterComponent } from "./modal-footer/modal-footer.component";
import { ChartsComponent } from "./charts/charts.component";
import { IonicModule } from "@ionic/angular";
import { NgxChartsModule } from "@swimlane/ngx-charts";

@NgModule({
  declarations: [
    AppHeaderComponent,
    FooterComponent,
    FilterComponent,
    KovComponent,
    InnerFooterComponent,
    ModalFooterComponent,
    ChartsComponent
  ],
  imports: [
    RouterModule,
    CommonModule,
    IonicModule,
    TranslateModule.forChild(),
    FormsModule,
    ReactiveFormsModule,
    NgxChartsModule
  ],
  exports: [
    AppHeaderComponent,
    FooterComponent,
    FilterComponent,
    KovComponent,
    InnerFooterComponent,
    ModalFooterComponent,
    ChartsComponent
  ],
  entryComponents: [
    AppHeaderComponent,
    FooterComponent,
    FilterComponent,
    KovComponent,
    InnerFooterComponent,
    ModalFooterComponent,
    ChartsComponent
  ]
})

export class PageComponentsModule { }
