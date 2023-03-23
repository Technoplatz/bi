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

import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { TranslateModule } from "@ngx-translate/core";
import { RouterModule } from "@angular/router";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { MenuComponent } from "./menu/menu.component";
import { FooterComponent } from "./footer/footer.component";
import { FilterComponent } from "./filter/filter.component";
import { ToolsComponent } from "./tools/tools.component";
import { KovComponent } from "./kov/kov.component";
import { InnerFooterComponent } from "./inner-footer/inner-footer.component";
import { ModalFooterComponent } from "./modal-footer/modal-footer.component";
import { ChartsComponent } from "./charts/charts.component";
import { IonicModule } from "@ionic/angular";
import { NgxChartsModule } from "@swimlane/ngx-charts";

@NgModule({
    declarations: [
        MenuComponent,
        FooterComponent,
        FilterComponent,
        ToolsComponent,
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
        MenuComponent,
        FooterComponent,
        FilterComponent,
        ToolsComponent,
        KovComponent,
        InnerFooterComponent,
        ModalFooterComponent,
        ChartsComponent
    ]
})

export class PageComponentsModule { }
