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

import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { HttpClientModule, HttpClient } from "@angular/common/http";
import { RouteReuseStrategy } from "@angular/router";
import { IonicModule, IonicRouteStrategy } from "@ionic/angular";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { SplashScreen } from "@ionic-native/splash-screen/ngx";
import { StatusBar } from "@ionic-native/status-bar/ngx";
import { AppComponent } from "./app.component";
import { AppRoutingModule } from "./app-routing.module";
import { TranslateModule, TranslateLoader } from "@ngx-translate/core";
import { TranslateHttpLoader } from "@ngx-translate/http-loader";
import { IonicStorageModule } from "@ionic/storage";
import { enableProdMode } from "@angular/core";
import { PageComponentsModule } from "./components/page-components.module";
import { SignPage } from "./pages/sign/sign.page";
import { CrudPage } from "./pages/crud/crud.page";
import { NgJsonEditorModule } from "ang-jsoneditor";
import { ServiceWorkerModule } from "@angular/service-worker";
import { DatePipe } from "@angular/common";
import { ClipboardPluginWeb } from "@capacitor/core";
import { environment } from "./../environments/environment";

if (environment.production) {
  enableProdMode();
}

export function createTranslateLoader(http: HttpClient) {
  return new TranslateHttpLoader(http, "./assets/i18n/", ".json");
}

@NgModule({
    declarations: [
        AppComponent,
        SignPage,
        CrudPage
    ],
    imports: [
        PageComponentsModule,
        BrowserModule,
        HttpClientModule,
        IonicModule.forRoot({
            animated: environment.animated,
            sanitizerEnabled: environment.sanitizerEnabled
        }),
        FormsModule,
        ReactiveFormsModule,
        IonicStorageModule.forRoot({
            name: "__bretzeldb",
            driverOrder: ["indexeddb", "sqlite", "websql"]
        }),
        AppRoutingModule,
        TranslateModule.forRoot({
            defaultLanguage: "en",
            loader: {
                provide: TranslateLoader,
                useFactory: (createTranslateLoader),
                deps: [HttpClient]
            }
        }),
        ServiceWorkerModule.register("ngsw-worker.js", {
            enabled: environment.production
            // registrationStrategy: "registerImmediately"
        }),
        NgJsonEditorModule
    ],
    providers: [
        StatusBar,
        SplashScreen,
        DatePipe,
        ClipboardPluginWeb,
        {
            provide: RouteReuseStrategy,
            useClass: IonicRouteStrategy
        }
        // { provide: LocationStrategy, useClass: HashLocationStrategy }
    ],
    bootstrap: [
        AppComponent
    ]
})
export class AppModule { }
