import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { TranslateModule } from "@ngx-translate/core";
import { IonicModule } from "@ionic/angular";
import { MainPageRoutingModule } from "./main-routing.module";
import { MainPage } from "./main.page";
import { PageComponentsModule } from "../../components/page-components.module";

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    IonicModule,
    MainPageRoutingModule,
    TranslateModule.forChild(),
    PageComponentsModule
  ],
  declarations: [MainPage]
})
export class MainPageModule { }
