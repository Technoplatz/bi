import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { TranslateModule } from "@ngx-translate/core";
import { IonicModule } from "@ionic/angular";
import { ConsolePageRoutingModule } from "./console-routing.module";
import { ConsolePage } from "./console.page";
import { PageComponentsModule } from "../../components/page-components.module";
import { CapitalizePipe } from "./../../pipes/capitalize-pipe";
import { QRCodeModule } from 'angularx-qrcode';
import { NgJsonEditorModule } from "ang-jsoneditor";

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    IonicModule,
    ConsolePageRoutingModule,
    TranslateModule.forChild(),
    PageComponentsModule,
    QRCodeModule,
    NgJsonEditorModule
  ],
  declarations: [
    ConsolePage,
    CapitalizePipe
  ],
  exports: [
    ConsolePage
  ]
})
export class ConsolePageModule { }
