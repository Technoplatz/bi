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

import { TranslatePipe } from '@ngx-translate/core';
import { IonButton, IonContent } from '@ionic/angular';
import { InnerFooterComponent } from '../../components/inner-footer/inner-footer.component';
import { Component, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { Miscellaneous } from '../../classes/misc';
import { Storage } from '@ionic/storage-angular';

@Component({
  // ported code updates plain fields in promise callbacks; angular 22 components are OnPush by default
  changeDetection: ChangeDetectionStrategy.Eager,
  imports: [TranslatePipe, IonButton, IonContent, InnerFooterComponent],
  selector: 'app-404',
  templateUrl: './_404.page.html',
  styleUrl: './_404.page.scss',
})
export class _404Page implements OnInit {
  public header: string = 'Sorry!';

  constructor(
    public misc: Miscellaneous,
    private storage: Storage,
  ) {}

  ngOnDestroy() {}

  ngOnInit() {}
}
