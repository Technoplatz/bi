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

import { Component, OnInit, Input, ChangeDetectionStrategy } from '@angular/core';
import { Storage } from '@ionic/storage-angular';
import { environment } from '../../../environments/environment';

@Component({
  // ported code updates plain fields in promise callbacks; angular 22 components are OnPush by default
  changeDetection: ChangeDetectionStrategy.Eager,
  imports: [],
  selector: 'app-pagination',
  templateUrl: './pagination.component.html',
  styleUrl: './pagination.component.scss',
})
export class PaginationComponent implements OnInit {
  @Input() id_: string = '';
  @Input() pagination_: any = [];
  public version_ = environment.appVersion;
  public css_: string = 'selection-passive';
  public default_: number = 25;
  public selections_: any = [];
  public set_proc_ = false;
  public selectionsoriginal_: any = [
    { id: 25, class: 'selection-passive' },
    { id: 50, class: 'selection-passive' },
    { id: 100, class: 'selection-passive' },
  ];

  constructor(private storage: Storage) {}

  ngOnInit() {
    this.get_selections().then((selections_: any) => {
      this.selections_ = selections_;
      this.storage.get('LSPAGINATION_' + this.id_).then((LSPAGINATION: any) => {
        if (LSPAGINATION) {
          this.default_ = LSPAGINATION ? LSPAGINATION : this.selections_[0].id;
          const index = this.selections_.findIndex((obj: any) => obj['id'] === this.default_);
          this.selections_[index].class = 'selection-active';
        }
      });
    });
  }

  get_selections() {
    return new Promise((resolve, reject) => {
      if (this.pagination_.length > 0) {
        let selections_: any = [];
        for (let j = 0; j < this.pagination_.length; j++) {
          selections_.push({ id: this.pagination_[j], class: 'selection-passive' });
          if (j === this.pagination_.length - 1) {
            resolve(selections_);
          }
        }
      } else {
        resolve(this.selectionsoriginal_);
      }
    });
  }

  set_pagination(i: number, limit_: number) {
    this.set_proc_ = true;
    for (let j = 0; j < this.selectionsoriginal_.length; j++) {
      this.selections_[j].class = 'selection-passive';
      j === this.selectionsoriginal_.length - 1
        ? this.storage.set('LSPAGINATION_' + this.id_, limit_).then(() => {
            this.selections_[i].class = 'selection-active';
            setTimeout(() => {
              this.set_proc_ = false;
              window.location.reload();
            }, 500);
          })
        : null;
    }
  }
}
