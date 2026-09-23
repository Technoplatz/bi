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

import { Component, OnInit, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { Router } from '@angular/router';
import { IonApp, IonRouterOutlet, IonSplitPane } from '@ionic/angular';
import { Storage } from '@ionic/storage-angular';
import { TranslateService } from '@ngx-translate/core';
import { environment } from '../environments/environment';
import { Auth } from './classes/auth';
import { Crud } from './classes/crud';
import { Miscellaneous } from './classes/misc';
import { Su } from './classes/su';
import { MenuComponent } from './components/menu/menu.component';
import { ToolsComponent } from './components/tools/tools.component';
import { SignPage } from './pages/sign/sign.page';
import { CrudPage } from './pages/crud/crud.page';

@Component({
  selector: 'app-root',
  imports: [IonApp, IonSplitPane, IonRouterOutlet, MenuComponent, ToolsComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {
  private translate = inject(TranslateService);
  private router = inject(Router);
  private auth = inject(Auth);
  private crud = inject(Crud);
  private misc = inject(Miscellaneous);
  private storage = inject(Storage);
  private su = inject(Su);

  readonly user_ = toSignal(this.auth.user, { initialValue: null as any });
  public companyName = environment.companyName;
  private paginations_ = environment.paginations;

  constructor() {
    document.title = this.companyName ? this.companyName : 'BI';
    this.misc.register_modal('sign', SignPage);
    this.misc.register_modal('crud', CrudPage);
    this.storage.get('LSPAGINATION').then((LSPAGINATION: any) => {
      if (!LSPAGINATION) {
        this.storage.set('LSPAGINATION', this.paginations_[1]);
      }
    });
    this.misc.navi.subscribe((path: any) => {
      this.router.navigateByUrl(path).catch((error: any) => console.error(error));
    });
    this.storage.get('LSTHEME').then((LSTHEME: any) => {
      document.documentElement.style.setProperty(
        '--ion-color-primary',
        LSTHEME ? LSTHEME.color : environment.themes[0].color,
      );
    });
    this.su.check_for_updates();
  }

  ngOnInit() {
    this.storage.get('LSUSERMETA').then((LSUSERMETA_: any) => {
      this.misc
        .locale()
        .then((locale_: any) => {
          locale_ = locale_ ? locale_ : LSUSERMETA_?.locale ? LSUSERMETA_.locale : 'de';
          this.storage.set('LSLOCALE', locale_).then(() => {
            this.translate.setFallbackLang(locale_);
            this.translate.use(locale_);
            this.auth.user.next(LSUSERMETA_);
            if (LSUSERMETA_) {
              this.crud.get_all().catch((error: any) => this.misc.doMessage(error, 'error'));
            }
          });
        })
        .catch((error: any) => console.error(error));
    });
  }
}
