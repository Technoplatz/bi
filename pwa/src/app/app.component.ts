import { Component, OnInit } from "@angular/core";
import { TranslateService } from "@ngx-translate/core";
import { Router, Event, NavigationError, NavigationEnd } from "@angular/router";
import { Storage } from "@ionic/storage";
import { Miscellaneous } from "./classes/miscellaneous";
import { Auth } from "./classes/auth";
import { Plugins } from "@capacitor/core";
import { environment } from "../environments/environment";

const { Network } = Plugins;

@Component({
  selector: "app-root",
  templateUrl: "app.component.html",
  styleUrls: ["app.component.scss"]
})

export class AppComponent implements OnInit {
  public user_: any;
  public console_: boolean = false;
  public index_: boolean = false;
  public swu_: boolean = false;
  public net_: boolean = true;
  private version_app = environment.appVersion;
  private version_global: string = "";

  constructor(
    private translate: TranslateService,
    private router: Router,
    private auth: Auth,
    private misc: Miscellaneous,
    private storage: Storage
  ) { }

  ngOnInit() {
    this.storage.get("LSTHEME").then((LSTHEME: any) => {
      if (LSTHEME) {
        document.documentElement.style.setProperty("--ion-color-primary", LSTHEME.color);
      } else {
        const LSTHEME = environment.themes[2];
        this.storage.set("LSTHEME", LSTHEME).then(() => {
          document.documentElement.style.setProperty("--ion-color-primary", LSTHEME.color);
        });
      }
    });

    setInterval(() => {
      this.doSwUpdateCheck();
    }, 15 * 60 * 1000);

    // get user
    this.storage.get("LSUSERMETA").then((LSUSERMETA) => {
      this.user_ = LSUSERMETA;
      this.doSwUpdateCheck();
    });

    // listen auth changes
    this.auth.authStateChange.subscribe((user: any) => {
      if (user) {
        this.user_ = user;
      } else {
        this.user_ = null;
        this.misc.go("/").then(() => {
        }).catch((error: any) => {
          console.error(error);
        });
      }
    });

    // listen page changes
    this.router.events.subscribe((event: Event) => {
      if (event instanceof NavigationError) {
        console.error("*** navigation error", event.url, event.error);
      } else if (event instanceof NavigationEnd) {
        this.index_ = event.url === "/" ? true : false;
        this.console_ = ["/console"].includes(event.url.substring(0, 8)) ? true : false;
      }
    });

    // listen internet connection
    Network.addListener("networkStatusChange", (status: any) => {
      if (!status.connected) {
        this.net_ = false;
        console.error("*** internet connection is lost");
      } else {
        setTimeout(() => {
          console.log("*** internet connection is back again");
          this.net_ = true;
          location.reload();
        }, 3000);
      }
    });

    // set default language
    this.misc.getLanguage().then((LSLANG: any) => {
      this.translate.setDefaultLang(LSLANG ? LSLANG : "en");
      this.translate.use(LSLANG ? LSLANG : "en");
    }).catch((error: any) => {
      console.error(error);
    });

  }

  doSwUpdateCheck() {
    this.misc.getVersion().then((res: any) => {
      if (res && res.result && res.versions) {
        this.version_global = res.versions[0].version;
        const version_local_ = this.version_app.replace("-dev", "").replace("-prod", "");
        if (this.version_global !== version_local_ && this.version_global > version_local_) {
          this.swu_ = true;
        }
      } else {
        console.error("no version checked");
      }
    }).catch((error: any) => {
      console.error(error);
    });
  }

}
