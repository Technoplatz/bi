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

import { ApplicationConfig, inject, isDevMode, provideAppInitializer, provideBrowserGlobalErrorListeners, provideZoneChangeDetection } from "@angular/core";
import { provideHttpClient } from "@angular/common/http";
import { PreloadAllModules, provideRouter, RouteReuseStrategy, withPreloading } from "@angular/router";
import { provideServiceWorker } from "@angular/service-worker";
import { provideIonicAngular, IonicRouteStrategy } from "@ionic/angular";
import { Storage } from "@ionic/storage-angular";
import { Drivers } from "@ionic/storage";
import { provideTranslateService } from "@ngx-translate/core";
import { provideTranslateHttpLoader } from "@ngx-translate/http-loader";
import { routes } from "./app.routes";
import { environment } from "../environments/environment";

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    // the ported code updates state inside promise callbacks; zone-based change detection keeps that
    // working until pages are moved to signals one by one
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideIonicAngular({ animated: environment.animated, sanitizerEnabled: environment.sanitizerEnabled }),
    { provide: RouteReuseStrategy, useClass: IonicRouteStrategy },
    provideRouter(routes, withPreloading(PreloadAllModules)),
    provideHttpClient(),
    provideTranslateService({
      fallbackLang: "en",
      loader: provideTranslateHttpLoader({ prefix: "./assets/i18n/", suffix: ".json" })
    }),
    // Ionic Storage 4 must be created before the first read; the old module did this implicitly
    { provide: Storage, useFactory: () => new Storage({ name: "__bidb", driverOrder: [Drivers.IndexedDB, Drivers.LocalStorage] }) },
    provideAppInitializer(() => inject(Storage).create().then(() => undefined)),
    provideServiceWorker("ngsw-worker.js", { enabled: !isDevMode(), registrationStrategy: "registerWhenStable:30000" })
  ]
};
