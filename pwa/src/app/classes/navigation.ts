import { Injectable } from "@angular/core";
import { NavController } from "@ionic/angular";

@Injectable({
    providedIn: "root"
})

export class Navigation {
    constructor(
        private nav: NavController
    ) { }
    navigateRoot(p: string) {
        return new Promise((resolve, reject) => {
            this.nav.navigateRoot([p]).then(() => {
                resolve(true);
            }).catch((error: any) => {
                reject(error);
            });
        });
    }
    navigateRootWithParams(p: any, params: any) {
        return new Promise((resolve, reject) => {
            this.nav.navigateRoot([p, params]).then(() => {
                resolve(true);
            }).catch((error: any) => {
                reject(error);
            });
        });
    }
}