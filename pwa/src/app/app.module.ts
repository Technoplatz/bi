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
            animated: false,
            sanitizerEnabled: false
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
