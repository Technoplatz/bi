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
  selector: 'app-job',
  templateUrl: './job.page.html',
  styleUrl: './job.page.scss',
})
export class JobPage implements OnInit {
  misc = inject(Miscellaneous);
  private storage = inject(Storage);
  private auth = inject(Auth);
  private crud = inject(Crud);
  private router = inject(Router);
  private modal = inject(ModalController);

  readonly editor = viewChild<JsonEditorComponent>('editor');
  readonly jeoptions = signal<JsonEditorOptions>(new JsonEditorOptions());
  public default_width: number = environment.misc.defaultColumnWidth;
  public header: string = 'JOBS';
  readonly subheader = signal<string>('');
  public loadingText: string = environment.misc.loadingText;
  readonly user = toSignal(this.auth.user, { initialValue: null as any });
  public perm: boolean = false;
  public id: string = '';
  public data_: any = [];
  public pages: any = [];
  public limit_: number = environment.misc.limit;
  readonly count_ = signal<number>(0);
  public status_: any = {};
  public columns_: any;
  readonly _saving = signal<boolean>(false);
  public is_deleting: boolean = false;
  public sort: any = {};
  readonly schemavis_ = signal<boolean>(false);
  readonly aggregate_ = signal<any>([]);
  public is_key_copied: boolean = false;
  public is_key_copying: boolean = false;
  public templates: any = [];
  public is_inprogress: boolean = false;
  public is_url_copied: boolean = false;
  readonly running_ = signal<boolean>(false);
  public job_scheduled_cron_: string = '';
  private menu: string = '';
  private submenu: string = '';
  private job_: any = {};
  readonly perma_ = computed(() => !!this.user()?.perma);
  private readonly collections_ = toSignal(this.crud.collections.pipe(map((res: any) => (res && res.data ? res.data : []))), { initialValue: [] as any[] });
  public json_content_: any = null;
  public col_: string = '';
  private schema_: any = {};

  ngOnInit() {}

  ionViewDidEnter() {
    this.storage.get('LSPAGINATION').then((LSPAGINATION: any) => {
      this.limit_ = LSPAGINATION * 1;
      this.storage.get('LSJOB').then((LSJOB_: any) => {
        this.col_ = LSJOB_?.job_collection_id;
        this.job_ = LSJOB_;
        this.menu = this.router.url.split('/')[1];
        this.id = this.submenu = this.router.url.split('/')[2];
        this.subheader.set(this.id);
        this.refresh_data(false).then(() => {});
      });
    });
  }

  refresh_data(run_: boolean) {
    return new Promise((resolve, reject) => {
      this.running_.set(true);
      this.schemavis_.set(false);
      this.crud
        .get_query_job('job', this.id, this.limit_, run_)
        .then((res: any) => {
          if (res && res.job) {
            this.schema_ = res.schema;
            this.job_scheduled_cron_ = res.job?.job_scheduled_cron;
            this.subheader.set(res.job.job_name);
            this.json_content_ = res.job.job_aggregate;
            this.aggregate_.set(res.job.job_aggregate);
            this.count_.set(res.count);
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
    return new Promise((resolve, reject) => {
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

  save_job_json_f(approved_: boolean) {
    if (this.json_content_ && this.json_content_.length > 0) {
      this._saving.set(true);
      this.aggregate_.set(this.json_content_);
      this.misc
        .api_call('crud', {
          op: 'savejob',
          collection: '_job',
          id: this.id,
          aggregate: this.aggregate_(),
          approved: approved_,
        })
        .then(() => {
          this.misc.doMessage('job saved successfully', 'success');
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

  run_job() {
    this.refresh_data(true).then(() => {});
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
            collection: '_job',
            collections: this.collections_(),
            views: [],
            user: this.user(),
            data: this.job_,
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
            this.misc.doMessage('job settings updated successfully', 'success');
            this.refresh_data(true);
          }
        });
        modal_.present();
      });
  }
}
