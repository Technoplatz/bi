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

import { CommonModule } from '@angular/common';
import { TranslatePipe } from '@ngx-translate/core';
import {
  IonButton,
  IonCol,
  IonContent,
  IonGrid,
  IonIcon,
  IonRow,
  IonSpinner,
  IonText,
} from '@ionic/angular';
import { InnerFooterComponent } from '../../components/inner-footer/inner-footer.component';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { Crud } from '../../classes/crud';
import { Miscellaneous } from '../../classes/misc';
import { Auth } from '../../classes/auth';
import { environment } from '../../../environments/environment';

@Component({
  imports: [
    CommonModule,
    TranslatePipe,
    IonButton,
    IonCol,
    IonContent,
    IonGrid,
    IonIcon,
    IonRow,
    IonSpinner,
    IonText,
    InnerFooterComponent,
  ],
  selector: 'app-dashboard',
  templateUrl: './dashboard.page.html',
  styleUrl: './dashboard.page.scss',
})
export class DashboardPage implements OnInit {
  private crud = inject(Crud);
  misc = inject(Miscellaneous);
  private auth = inject(Auth);

  readonly announcements_ = signal<any[]>([]);
  public loadingText: string = environment.misc.loadingText;
  public flashsizes_: any = environment.flashsizes;
  readonly visuals_ = signal<any[]>([]);
  private readonly user_ = toSignal(this.auth.user, { initialValue: null as any });
  readonly perm_ = computed(() => !!(this.user_() && this.user_().perm));

  ngOnInit() {
    this.announcements_.set([]);
    this.crud
      .get_announcements()
      .then((res: any) => {
        this.announcements_.set(res.data ? res.data.slice(0, 15) : []);
      })
      .catch((err_: any) => {
        console.warn('announcements not loaded', err_);
      });
  }

  ionViewDidEnter() {
    this.crud
      .get_visuals(null)
      .then((visuals_: any) => {
        const list_: any[] = visuals_.visuals.map((visual_: any) => ({ ...visual_, is_loaded: false }));
        this.visuals_.set(list_);
        for (let ix_: number = 0; ix_ < list_.length; ix_++) {
          this.crud
            .get_visual(list_[ix_].id)
            .then((visual_: any) => {
              this.patch_visual(ix_, {
                data: visual_.visual.data,
                fields: visual_.visual.fields,
                count: visual_.visual.count,
              });
            })
            .catch((err_: any) => {
              this.patch_visual(ix_, { error: err_ });
            })
            .finally(() => {
              this.patch_visual(ix_, { is_loaded: true });
            });
        }
      })
      .catch((err_: any) => {
        console.warn('visuals not loaded', err_);
      });
  }

  // replaces the visual at ix_ with a patched copy, so the list signal notifies the template
  private patch_visual(ix_: number, patch_: any) {
    this.visuals_.update((list_) =>
      list_.map((visual_, i_) => (i_ === ix_ ? { ...visual_, ...patch_ } : visual_)),
    );
  }

  orderByIndex = (a: any, b: any): number => {
    return a.value.index < b.value.index ? -1 : b.value.index > a.value.index ? 1 : 0;
  };
}
