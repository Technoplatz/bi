import { Component, OnDestroy, OnInit, ChangeDetectionStrategy } from "@angular/core";
import { IonButton, IonIcon, IonLabel } from "@ionic/angular";
import { TranslatePipe } from "@ngx-translate/core";
import { Subscription } from "rxjs";
import { Miscellaneous } from "../../classes/misc";
import { Auth } from "../../classes/auth";

@Component({
  // ported code updates plain fields in promise callbacks; angular 22 components are OnPush by default
  changeDetection: ChangeDetectionStrategy.Eager,
  selector: "app-tools",
  imports: [IonButton, IonIcon, IonLabel, TranslatePipe],
  template: `
    <div class="top-tools">
      @if (ready_) {
        <ion-button color="danger" (click)="reload_app()" size="small" class="new-version">{{ 'New Version is Ready' | translate }}</ion-button>
      }
      @if (detected_) {
        <ion-button color="success" (click)="reload_app()" size="small" class="new-version-downloading">{{ 'New Version Detected' | translate }}</ion-button>
      }
      @if (user_) {
        <ion-button fill="clear" (click)="misc.navi.next('settings/account')">
          <ion-label>{{ user_.name }}&nbsp;</ion-label>
          <ion-icon name="person-circle-sharp" color="primary"></ion-icon>
        </ion-button>
      }
    </div>
  `,
  styleUrl: "./tools.component.scss"
})
export class ToolsComponent implements OnInit, OnDestroy {
  public user_: any = null;
  public ready_ = false;
  public detected_ = false;
  private subs_: Subscription[] = [];

  constructor(private auth: Auth, public misc: Miscellaneous) {
    this.subs_.push(this.misc.version.subscribe((version_: any) => {
      this.ready_ = !!version_.ready;
      this.detected_ = !!version_.detected;
    }));
  }

  ngOnInit() {
    this.subs_.push(this.auth.user.subscribe((user_: any) => (this.user_ = user_)));
  }

  ngOnDestroy() {
    this.subs_.forEach((s) => s.unsubscribe());
  }

  reload_app() {
    window.location.reload();
  }
}
