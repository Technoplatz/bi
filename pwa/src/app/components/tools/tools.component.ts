import { Component, computed, inject } from "@angular/core";
import { toSignal } from "@angular/core/rxjs-interop";
import { IonButton, IonIcon, IonLabel } from '@ionic/angular';
import { TranslatePipe } from '@ngx-translate/core';
import { Miscellaneous } from '../../classes/misc';
import { Auth } from '../../classes/auth';

@Component({
  selector: 'app-tools',
  imports: [IonButton, IonIcon, IonLabel, TranslatePipe],
  template: `
    <div class="top-tools">
      @if (ready_()) {
        <ion-button color="danger" (click)="reload_app()" size="small" class="new-version">{{
          'New Version is Ready' | translate
        }}</ion-button>
      }
      @if (detected_()) {
        <ion-button
          color="success"
          (click)="reload_app()"
          size="small"
          class="new-version-downloading"
          >{{ 'New Version Detected' | translate }}</ion-button
        >
      }
      @if (user_()) {
        <ion-button fill="clear" (click)="misc.navi.next('settings/account')">
          <ion-label>{{ user_().name }}&nbsp;</ion-label>
          <ion-icon name="person-circle-sharp" color="primary"></ion-icon>
        </ion-button>
      }
    </div>
  `,
  styleUrl: './tools.component.scss',
})
export class ToolsComponent {
  private auth = inject(Auth);
  misc = inject(Miscellaneous);

  private readonly version_ = toSignal(this.misc.version, { initialValue: {} as any });
  readonly ready_ = computed(() => !!this.version_()?.ready);
  readonly detected_ = computed(() => !!this.version_()?.detected);
  readonly user_ = toSignal(this.auth.user, { initialValue: null as any });

  reload_app() {
    window.location.reload();
  }
}
