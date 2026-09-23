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
import { InnerFooterComponent } from '../../components/inner-footer/inner-footer.component';
import { Component, OnInit, viewChild, inject, signal, computed } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
import {
  IonButton,
  IonCol,
  IonContent,
  IonGrid,
  IonIcon,
  IonRow,
  IonSpinner,
  IonText,
  ModalController,
} from '@ionic/angular';
import { Router } from '@angular/router';
import { Storage } from '@ionic/storage-angular';
import { Crud } from '../../classes/crud';
import { Auth } from '../../classes/auth';
import { Miscellaneous } from '../../classes/misc';
import { TranslateService } from '@ngx-translate/core';
import { environment } from '../../../environments/environment';
import {
  JsonEditorOptions,
  JsonEditorComponent,
} from '../../components/json-editor/json-editor.component';
import { CrudPage } from '../crud/crud.page';

@Component({
  imports: [
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
    JsonEditorComponent,
  ],
  selector: 'app-query',
  templateUrl: './query.page.html',
  styleUrl: './query.page.scss',
})
export class QueryPage implements OnInit {
  misc = inject(Miscellaneous);
  private storage = inject(Storage);
  private auth = inject(Auth);
  private crud = inject(Crud);
  private router = inject(Router);
  private modal = inject(ModalController);
  private translate = inject(TranslateService);

  readonly editor = viewChild<JsonEditorComponent>('editor');
  readonly jeoptions = signal<JsonEditorOptions>(new JsonEditorOptions());
  public default_width: number = environment.misc.defaultColumnWidth;
  public header: string = 'QUERIES';
  readonly subheader = signal<string>('');
  public loadingText: string = environment.misc.loadingText;
  readonly user = toSignal(this.auth.user, { initialValue: null as any });
  public perm: boolean = false;
  public id: string = '';
  readonly data_ = signal<any>([]);
  public pages: any = [];
  readonly limit_ = signal<number>(environment.misc.limit);
  public count_: number = 0;
  readonly fields_ = signal<any>({});
  readonly _saving = signal<boolean>(false);
  public sort: any = {};
  readonly schemavis_ = signal<boolean>(false);
  readonly aggregate_ = signal<any>([]);
  public is_key_copied: boolean = false;
  public is_key_copying: boolean = false;
  public templates: any = [];
  public is_inprogress: boolean = false;
  readonly is_url_copied = signal<boolean>(false);
  readonly running_ = signal<boolean>(false);
  readonly running_test_ = signal<boolean>(false);
  readonly running_live_ = signal<boolean>(false);
  public query_url_: string = '';
  readonly que_scheduled_cron_ = signal<string>('');
  readonly _tags = signal<any>([]);
  readonly collections_ = toSignal(this.crud.collections.pipe(map((res: any) => (res && res.data ? res.data : []))), { initialValue: [] as any[] });
  private menu: string = '';
  private submenu: string = '';
  private query_: any = {};
  readonly perm_ = computed(() => !!this.user()?.perm);
  readonly perma_ = computed(() => !!this.user()?.perma);
  readonly permqa_ = computed(() => !!this.user()?.permqa);
  private schema_: any = {};
  public json_content_: any = null;
  public col_: string = '';
  readonly pivot_ = signal<string>('');

  ngOnInit() {}

  ionViewDidEnter() {
    this.storage.get('LSPAGINATION').then((LSPAGINATION: any) => {
      this.limit_.set(LSPAGINATION * 1);
      this.storage.get('LSQUERY').then((LSQUERY_: any) => {
        this.col_ = LSQUERY_?.que_collection_id;
        this.query_ = LSQUERY_;
        this.menu = this.router.url.split('/')[1];
        this.id = this.submenu = this.router.url.split('/')[2];
        this.subheader.set(this.id);
        this.query_url_ = `${environment.apiUrl}/get/query/${this.id}`;
        this.refresh_data(false).then(() => {});
      });
    });
  }

  refresh_data(run_: boolean) {
    return new Promise((resolve, reject) => {
      this.running_.set(true);
      this.schemavis_.set(false);
      this.crud
        .get_query_job('query', this.id, this.limit_(), run_)
        .then((res: any) => {
          if (res.query && res.data) {
            this.pivot_.set(res.pivot !== '' ? res.pivot : null);
            this.schema_ = res.schema;
            this.que_scheduled_cron_.set(res.query?.que_scheduled_cron);
            this._tags.set(res.query?._tags);
            this.subheader.set(res.query.que_title);
            this.json_content_ = res.query.que_aggregate;
            this.aggregate_.set(res.query.que_aggregate);
            this.fields_.set(res.fields);
            this.data_.set(res.data);
            this.count_ = res.count;
            resolve(true);
          } else {
            this.misc.doMessage('no data found', 'error');
            reject();
          }
          if (res.err) {
            this.misc.doMessage(res.err, 'error');
            reject();
          }
        })
        .catch((res: any) => {
          this.misc.doMessage(res.err, 'error');
          reject();
        })
        .finally(() => {
          this.running_.set(false);
        });
    });
  }

  json_editor_init() {
    return new Promise((resolve) => {
      const jeoptions_ = new JsonEditorOptions();
      jeoptions_.modes = ['tree', 'code', 'text'];
      jeoptions_.mode = 'code';
      jeoptions_.statusBar = false;
      jeoptions_.navigationBar = false;
      jeoptions_.mainMenuBar = true;
      jeoptions_.enableSort = false;
      jeoptions_.expandAll = false;
      this.jeoptions.set(jeoptions_);
      resolve(true);
    });
  }

  set_editor(set_: boolean) {
    this.schemavis_.set(!this.schemavis_() && set_ && !this.running_());
    set_ ? this.json_editor_init().then(() => {}) : null;
  }

  save_query_json_f(approved_: boolean) {
    if (this.json_content_ && this.json_content_.length > 0) {
      this._saving.set(true);
      this.aggregate_.set(this.json_content_);
      this.misc
        .api_call('crud', {
          op: 'savequery',
          collection: '_query',
          id: this.id,
          aggregate: this.aggregate_(),
          approved: approved_,
        })
        .then(() => {
          this.misc.doMessage(
            approved_ ? 'query approved successfully' : 'query saved successfully',
            'success',
          );
          this.refresh_data(false).then(() => {
            this.schemavis_.set(false);
          });
        })
        .catch((error: any) => {
          this.misc.doMessage(error, 'error');
        })
        .finally(() => {
          this._saving.set(false);
        });
    } else {
      this.misc.doMessage('invalid aggregation', 'error');
    }
  }

  json_changed(event_: any) {
    !event_.isTrusted ? (this.json_content_ = event_) : null;
  }

  copy_url() {
    this.is_url_copied.set(false);
    this.misc
      .copy_to_clipboard(this.query_url_)
      .then(() => {
        this.is_url_copied.set(true);
      })
      .catch((error: any) => {
        console.error('copy error', error);
      })
      .finally(() => {
        setTimeout(() => {
          this.is_url_copied.set(false);
        }, 1000);
      });
  }

  run_query() {
    if (!this.running_()) {
      this.running_.set(true);
      this.refresh_data(true)
        .then(() => {})
        .finally(() => {
          this.running_.set(false);
        });
    }
  }

  do_announce(type_: string) {
    if (!this.running_test_() && !this.running_live_()) {
      this.running_test_.set(type_ === 'test' ? true : false);
      this.running_live_.set(type_ === 'live' ? true : false);
      this.misc
        .api_call('crud', {
          op: 'reqotp',
          collection: '_query',
          id: this.id,
        })
        .then(() => {
          this.misc
            .validateOTP(type_)
            .then((otp_: any) => {
              this.crud
                .announce(this.id, type_, otp_)
                .then((res_: any) => {
                  if (res_?.err) {
                    this.misc.doMessage(this.translate.instant(res_.err), 'error');
                  } else {
                    this.misc.doMessage(
                      this.translate.instant(`${type_} announcement has made successfully`),
                      'success',
                    );
                  }
                })
                .catch((error: any) => {
                  this.misc.doMessage(error, 'error');
                })
                .finally(() => {
                  this.running_test_.set(false);
                  this.running_live_.set(false);
                });
            })
            .catch(() => {
              this.running_test_.set(false);
              this.running_live_.set(false);
            });
        })
        .catch((err_: any) => {
          this.misc.doMessage(err_, 'error');
          this.running_test_.set(false);
          this.running_live_.set(false);
        })
        .finally(() => {
          this._saving.set(false);
        });
    }
  }

  edit_query() {
    this.modal
      .create({
        component: CrudPage,
        backdropDismiss: true,
        cssClass: 'crud-modal',
        componentProps: {
          shuttle: {
            op: 'update',
            collection: '_query',
            collections: this.collections_(),
            views: [],
            user: this.user(),
            data: this.query_,
            counters: null,
            structure: this.schema_,
            sweeped: [],
            filter: null,
            actions: [],
            actionix: -1,
            view: null,
            scan: null,
          },
        },
      })
      .then((modal_: any) => {
        modal_.onDidDismiss().then((res: any) => {
          if (res.data.modified && res.data.res.result) {
            this.misc.doMessage('query settings updated successfully', 'success');
            this.refresh_data(true);
          }
        });
        modal_.present();
      });
  }
}
