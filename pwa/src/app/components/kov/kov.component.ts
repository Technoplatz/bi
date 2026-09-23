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

import { FormsModule } from '@angular/forms';
import { TranslatePipe } from '@ngx-translate/core';
import {
  IonButton,
  IonCol,
  IonGrid,
  IonIcon,
  IonInput,
  IonItem,
  IonReorder,
  IonReorderGroup,
  IonRow,
  IonSelect,
  IonSelectOption,
  IonSpinner,
} from '@ionic/angular';
import { Component, OnInit, SimpleChanges, input, model, signal } from '@angular/core';
import { environment } from './../../../environments/environment';
import { ItemReorderEventDetail } from '@ionic/core';

@Component({
  imports: [
    FormsModule,
    TranslatePipe,
    IonButton,
    IonCol,
    IonGrid,
    IonIcon,
    IonInput,
    IonItem,
    IonReorder,
    IonReorderGroup,
    IonRow,
    IonSelect,
    IonSelectOption,
    IonSpinner,
  ],
  selector: 'app-kov',
  templateUrl: './kov.component.html',
  styleUrl: './kov.component.scss',
})
export class KovComponent implements OnInit {
  readonly properties = input<any>(undefined);
  // the parent's data object; every edit replaces the array inside it and hands the new object back
  readonly data = model<any>({});
  readonly field = input<any>({});
  readonly op = input<string>('');
  readonly kovs = signal<any>(null);
  readonly type = signal<string>('key');
  readonly ok = signal<boolean>(false);
  public filterops: any = environment.filterops;
  readonly fname = signal<string>('');
  private hours_: any = [];
  private minutes_: any = [];
  private days_: any = [
    { key: 'mon' },
    { key: 'tue' },
    { key: 'wed' },
    { key: 'thu' },
    { key: 'fri' },
    { key: 'sat' },
    { key: 'sun' },
  ];
  private tags_ = [{ key: '#Managers' }, { key: '#Administrators' }];
  private empty_ = [{ key: null }];
  private dual_ = [{ key: null, value: null }];
  public keyop_ = [
    { key: 'x-axis' },
    { key: 'y-axis' },
    { key: 'group' },
    { key: 'data[count]' },
    { key: 'data[sum]' },
  ];

  constructor() {}

  ngOnInit() {
    for (let h_ = 0; h_ < 24; h_++) {
      this.hours_.push({ key: h_ });
    }
    for (let m_ = 0; m_ < 60; m_++) {
      this.minutes_.push({ key: m_ });
    }
  }

  ngOnChanges(changes: SimpleChanges) {
    // the data object is replaced on every edit; only a new field or property list resets the rows
    if (!changes['field'] && !changes['properties']) {
      return;
    }
    const field_ = this.field();
    this.ok.set(false);
    this.fname.set(field_.name);
    if (['keyop', 'keyvalue', 'emptyfield'].includes(field_.subType)) {
      this.type.set(field_.subType);
    } else if (field_.subType === 'filter') {
      this.type.set('keyopvalue');
    }
    if (['keyop', 'keyvalue', 'filter', 'property'].includes(field_.subType)) {
      this.kovs.set(this.properties());
    } else if (field_.subType === 'hour') {
      this.kovs.set(this.hours_);
    } else if (field_.subType === 'minute') {
      this.kovs.set(this.minutes_);
    } else if (field_.subType === 'day') {
      this.kovs.set(this.days_);
    } else if (field_.subType === 'tag') {
      this.kovs.set(this.tags_);
    } else if (field_.subType === 'string') {
      this.kovs.set(this.empty_);
    } else if (field_.subType === 'emptyfield') {
      this.kovs.set(this.dual_);
    }
    setTimeout(() => {
      this.ok.set(true);
    }, 1000);
  }

  private set_lines(lines: any[]) {
    this.data.update((d: any) => ({ ...d, [this.fname()]: lines }));
  }

  // a value typed or selected in a row: the row and the array are replaced, never mutated
  doLineChange(i: number, key: string | null, value: any) {
    const lines_ = this.data()[this.fname()] ? [...this.data()[this.fname()]] : [];
    lines_[i] = key === null ? value : { ...lines_[i], [key]: value };
    this.set_lines(lines_);
  }

  doLineAdd(i: number) {
    const lines_ = this.data()[this.fname()];
    if (i === -1 || !lines_) {
      this.set_lines([{ key: null }]);
    } else {
      if (this.type() === 'keyopvalue') {
        this.set_lines([...lines_, { key: null, op: null, value: null }]);
      } else if (this.type() === 'keyop') {
        this.set_lines([...lines_, { key: null, op: null }]);
      } else if (this.type() === 'keyvalue' || this.type() === 'emptyfield') {
        this.set_lines([...lines_, { key: null, value: null }]);
      } else if (this.type() === 'key') {
        this.set_lines([...lines_, { key: null }]);
      } else if (this.type() === 'other') {
        this.set_lines([...lines_, null]);
      }
    }
  }

  doLineRemove(i: number) {
    this.set_lines(this.data()[this.fname()].filter((_: any, j: number) => j !== i));
  }

  doReorder(ev: CustomEvent<ItemReorderEventDetail>, fn: string) {
    // complete() reorders the copy it is given and leaves the DOM to the @for loop
    const lines_ = ev.detail.complete([...this.data()[fn]]);
    this.data.update((d: any) => ({ ...d, [fn]: lines_ }));
  }
}
