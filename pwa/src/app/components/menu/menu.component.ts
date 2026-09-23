import { Component, computed, inject } from "@angular/core";
import { toSignal } from "@angular/core/rxjs-interop";
import { map } from "rxjs";
import {
  IonButton,
  IonHeader,
  IonIcon,
  IonItem,
  IonLabel,
  IonList,
  IonToolbar,
} from '@ionic/angular';
import { TranslatePipe } from '@ngx-translate/core';
import { environment } from '../../../environments/environment';
import { Miscellaneous } from '../../classes/misc';
import { Auth } from '../../classes/auth';
import { Crud } from '../../classes/crud';

@Component({
  selector: 'app-menu',
  imports: [IonHeader, IonToolbar, IonList, IonItem, IonLabel, IonButton, IonIcon, TranslatePipe],
  templateUrl: './menu.component.html',
  styleUrl: './menu.component.scss',
})
export class MenuComponent {
  misc = inject(Miscellaneous);
  private auth = inject(Auth);
  private crud = inject(Crud);

  public version = environment.appVersion;
  public release = environment.release;
  public companyName = environment.companyName;
  readonly collections_ = toSignal(this.crud.collections.pipe(map((res: any) => (res && res.data ? res.data : []))), { initialValue: [] as any[] });
  readonly user_ = toSignal(this.auth.user, { initialValue: null as any });
  readonly perm_ = computed(() => !!(this.user_() && this.user_().perm));
  readonly segmentsadm = computed(() => (this.perm_() ? environment.segmentsadm : []));

  sign_out() {
    this.auth.sign_out().catch((error: any) => console.error('signout error', error?.msg ?? error));
  }
}
