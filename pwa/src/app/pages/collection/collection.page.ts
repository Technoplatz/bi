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
import { FormsModule } from '@angular/forms';
import { TranslatePipe } from '@ngx-translate/core';
import { InnerFooterComponent } from '../../components/inner-footer/inner-footer.component';
import { PaginationComponent } from '../../components/pagination/pagination.component';
import { Component, OnInit, ElementRef, viewChild, inject, signal, computed } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import {
  AlertController,
  IonButton,
  IonCheckbox,
  IonCol,
  IonContent,
  IonGrid,
  IonIcon,
  IonInput,
  IonLabel,
  IonRow,
  IonSpinner,
  IonText,
  IonTextarea,
  ModalController,
} from '@ionic/angular';
import { Router } from '@angular/router';
import { Storage } from '@ionic/storage-angular';
import { map } from 'rxjs';
import { Crud } from '../../classes/crud';
import { Auth } from '../../classes/auth';
import { Miscellaneous } from '../../classes/misc';
import { environment } from '../../../environments/environment';
import { CrudPage } from '../crud/crud.page';
import {
  JsonEditorOptions,
  JsonEditorComponent,
} from '../../components/json-editor/json-editor.component';

@Component({
  imports: [
    CommonModule,
    FormsModule,
    TranslatePipe,
    IonButton,
    IonCheckbox,
    IonCol,
    IonContent,
    IonGrid,
    IonIcon,
    IonInput,
    IonLabel,
    IonRow,
    IonSpinner,
    IonText,
    IonTextarea,
    InnerFooterComponent,
    PaginationComponent,
    JsonEditorComponent,
  ],
  selector: 'app-collection',
  templateUrl: './collection.page.html',
  styleUrl: './collection.page.scss',
})
export class CollectionPage implements OnInit {
  private storage = inject(Storage);
  private auth = inject(Auth);
  private crud = inject(Crud);
  private modal = inject(ModalController);
  private alert = inject(AlertController);
  private router = inject(Router);
  misc = inject(Miscellaneous);

  readonly editor = viewChild<JsonEditorComponent>('editor');
  readonly searchfocus = viewChild<any>('searchfocus');
  readonly svg = viewChild<any>('svg');
  private json_content_: any = null;
  private sweeped: any = [];
  private actionix: number = -1;
  private menu: string = '';
  private clonok: number = -1;
  private view: any = null;
  private is_selected: boolean = false;
  private counters_: any = {};
  private segment = 'data';
  private page_start: number = 1;
  private key_: any = null;
  private record_: any = [];
  readonly jeoptions = signal<JsonEditorOptions>(new JsonEditorOptions());
  readonly header = signal<string>('Collections');
  readonly subheader = signal<string>('');
  public loadingText: string = environment.misc.loadingText;
  readonly user = toSignal(this.auth.user, { initialValue: null as any });
  readonly perm_ = computed(() => !!(this.user() && this.user().perm));
  readonly perma_ = computed(() => !!(this.user() && this.user().perma));
  readonly is_crud = signal<boolean>(false);
  readonly paget_ = signal<any>([]);
  readonly id = signal<string>('');
  readonly filter_ = signal<any>([]);
  readonly searched = signal<any>(null);
  readonly data = signal<any>([]);
  readonly selected = signal<any>([]);
  readonly pages_ = signal<any>([]);
  readonly limit_ = signal<number>(environment.misc.limit);
  public page_: number = 1;
  readonly pager_ = signal<number>(1);
  readonly count = signal<number>(0);
  readonly is_loaded = signal<boolean>(true);
  readonly multicheckbox = signal<boolean>(false);
  readonly collections_ = toSignal(
    this.crud.collections.pipe(map((res: any) => (res && res.data ? res.data : []))),
    { initialValue: [] as any[] },
  );
  readonly title_ = computed(
    () => this.collections_()?.find((obj_: any) => obj_.col_id === this.subheader())?.col_title,
  );
  readonly links_ = signal<any>([]);
  readonly is_initialized = signal<boolean>(false);
  readonly scan_ = signal<boolean>(false);
  readonly actions = signal<any>([]);
  readonly properties_ = signal<any>({});
  readonly is_saving = signal<boolean>(false);
  public is_deleting: boolean = false;
  public sort: any = {};
  readonly structure_ = signal<any>({});
  readonly schemavis_ = signal<boolean>(false);
  readonly importvis_ = signal<boolean>(false);
  readonly is_key_copied = signal<boolean>(false);
  readonly is_key_copying = signal<boolean>(false);
  public is_inprogress: boolean = false;
  readonly flashcards_ = signal<any>([]);
  readonly propkeys_ = signal<string>('');
  readonly is_copied = signal<boolean>(false);
  readonly colvis_activated_ = signal<boolean>(false);
  readonly colvised_ = signal<boolean>(false);
  readonly colvis_ = signal<any>({});
  readonly selections_ = signal<any>({});
  readonly pagination_ = signal<any>([]);
  public fixedcols_: any = [
    { key: '_created_at', title: 'Created At' },
    { key: '_created_by', title: 'Created By' },
    { key: '_modified_at', title: 'Modified At' },
    { key: '_modified_by', title: 'Modified By' },
    { key: '_id', title: 'ID' },
  ];

  ngOnInit() {
    this.menu = this.router.url.split('/')[1];
    const id = this.router.url.split('/')[2];
    this.id.set(id);
    this.subheader.set(id);
    const is_crud = id.charAt(0) === '_' ? false : true;
    this.is_crud.set(is_crud);
    this.header.set(
      is_crud
        ? 'COLLECTIONS'
        : id === '_collection'
          ? 'DATA COLLECTIONS'
          : id === '_query'
            ? 'QUERIES'
            : id === '_job'
              ? 'JOBS'
              : id === '_visual'
                ? 'VISUALIZATION'
                : 'ADMINISTRATION',
    );
  }

  ionViewDidEnter() {
    this.is_initialized.set(false);
    this.colvis_activated_.set(false);
    this.storage.get('LSPAGINATION_' + this.id()).then((LSPAGINATION: any) => {
      this.limit_.set(LSPAGINATION ? LSPAGINATION * 1 : 50);
      this.storage.get('LSCOLVIS_' + this.id()).then((LSCOLVIS_: any) => {
        this.colvis_.set(LSCOLVIS_ ? LSCOLVIS_ : {});
        this.storage.get('LSFILTER_' + this.id()).then((LSFILTER_: any) => {
          this.storage.get('LSSEARCHED_' + this.id()).then((LSSEARCHED_: any) => {
            this.filter_.set(LSFILTER_ && LSFILTER_.length > 0 ? LSFILTER_ : []);
            LSSEARCHED_ ? this.searched.set(LSSEARCHED_) : null;
            this.actions.set([]);
            this.crud
              .get_collection(this.id())
              .then((res: any) => {
                this.counters_ = res && res.counters ? res.counters : {};
                this.refresh_data(0, false)
                  .then(() => {})
                  .catch((error: any) => {
                    this.misc.doMessage(error, 'error');
                  })
                  .finally(() => {
                    this.is_initialized.set(true);
                  });
              })
              .catch((error: any) => {
                this.misc.doMessage(error, 'error');
              });
          });
        });
      });
    });
  }

  get_links(res: any) {
    // counts the linked documents on the records of the response before they become the data signal
    return new Promise((resolve, reject) => {
      const links_ = res.structure.links
        ? res.structure.links.filter((lnk_: any) => lnk_.listed === true)
        : [];
      this.links_.set(links_);
      const data_ = res.data;
      for (let l_: number = 0; l_ < links_.length; l_++) {
        data_.forEach((record_: any, index_: number) => {
          data_[index_]['_link_' + links_[l_].collection].count = 0;
          data_[index_]['_link_' + links_[l_].collection].sum = 0;
          data_[index_]['_link_' + links_[l_].collection].forEach((item_: any) => {
            data_[index_]['_link_' + links_[l_].collection].count += 1;
            data_[index_]['_link_' + links_[l_].collection].sum += item_.sum;
          });
        });
      }
      resolve(true);
    });
  }

  refresh_data(page_: number, outfile_: boolean) {
    return new Promise((resolve, reject) => {
      this.is_selected = false;
      this.is_loaded.set(false);
      this.schemavis_.set(false);
      this.storage.get('LSSEARCHED_' + this.id()).then((LSSEARCHED_: any) => {
        this.storage.get('LSFILTER_' + this.id()).then((LSFILTER_: any) => {
          this.storage.get('LSSELECTIONS_' + this.id()).then((LSSELECTIONS_: any) => {
            this.storage.get('LSCOLVIS_' + this.id()).then((LSCOLVIS_: any) => {
              const colvis_ = LSCOLVIS_ ? LSCOLVIS_ : {};
              this.colvis_.set(colvis_);
              this.colvised_.set(Object.keys(colvis_).some((key_) => colvis_[key_] === true));
              this.searched.set(LSSEARCHED_ ? LSSEARCHED_ : null);
              this.filter_.set(LSFILTER_ && LSFILTER_.length > 0 ? LSFILTER_ : []);
              this.selections_.set(LSSELECTIONS_ ? LSSELECTIONS_ : {});
              this.count.set(0);
              this.page_ = page_ === 0 ? 1 : page_;
              this.misc
                .api_call('crud', {
                  op: 'read',
                  collection: this.id(),
                  projection: null,
                  match: this.filter_() && this.filter_().length > 0 ? this.filter_() : [],
                  sort: this.sort,
                  page: this.page_,
                  limit: this.limit_(),
                  selections: this.selections_(),
                  outfile: outfile_,
                })
                .then((res: any) => {
                  this.selections_.set(res.selected);
                  this.pager_.set(this.page_);
                  this.structure_.set(res.structure);
                  this.get_links(res).then(() => {
                    this.data.set(res.data);
                    this.json_content_ = res.structure;
                    this.actions.set(res.actions);
                    const properties_ = res.structure.properties;
                    this.properties_.set(properties_);
                    this.importvis_.set(res.structure.import?.enabled);
                    this.pagination_.set(res.structure.pagination ? res.structure.pagination : []);
                    this.scan_.set(
                      true
                        ? Object.keys(properties_).filter((key: any) => properties_[key].scan)
                            .length > 0
                        : false,
                    );
                    this.count.set(res.count);
                    this.multicheckbox.set(false);
                    this.selected.set(new Array(res.data.length).fill(false));
                    const pages_ =
                      this.count() > 0
                        ? Math.ceil(this.count() / this.limit_())
                        : environment.misc.default_page;
                    this.pages_.set(pages_);
                    const lmt = pages_ >= 10 ? 10 : pages_;
                    const paget_ = new Array(lmt);
                    this.page_start = this.page_ > 10 ? this.page_ - 10 + 1 : 1;
                    this.searched() === null ? this.init_search(true) : this.init_search(false);
                    for (let p = 0; p < paget_.length; p++) {
                      paget_[p] = this.page_start + p;
                    }
                    this.paget_.set(paget_);
                    resolve(true);
                  });
                })
                .catch((error: any) => {
                  this.misc.doMessage(error, 'error');
                  reject(error);
                })
                .finally(() => {
                  this.crud
                    .get_all()
                    .then(() => {
                      let propkeys_ = '';
                      Object.keys(this.properties_()).forEach((key_: string) => {
                        propkeys_ += `${key_}\t`;
                      });
                      this.propkeys_.set(propkeys_);
                    })
                    .catch((err_: any) => {
                      console.error('get_all', err_);
                    })
                    .finally(() => {
                      this.is_loaded.set(true);
                    });
                });
            });
          });
        });
      });
    });
  }

  action(ix_: any) {
    if (this.actions()[ix_]?.one_click || this.sweeped[this.segment]?.length > 0) {
      this.actionix = ix_;
      this.go_crud(this.record_, 'action');
    } else {
      this.misc.doMessage('please select the rows to be processed', 'error');
    }
  }

  multi_crud(op_: string) {
    if (this.data().length > 0 && this.is_loaded()) {
      if (this.is_selected) {
        if (op_ === 'action') {
          if (this.structure_() && this.structure_().actions && this.structure_().actions.length > 0) {
            this.go_crud(null, op_);
          } else {
            this.misc.doMessage('no action defined for the collection', 'error');
          }
        } else {
          this.alert
            .create({
              header: 'Confirm',
              message: 'Please confirm this ' + op_,
              buttons: [
                {
                  text: 'Cancel',
                  role: 'cancel',
                  cssClass: 'secondary',
                  handler: () => {},
                },
                {
                  text: 'OKAY',
                  handler: () => {
                    this.is_deleting = true;
                    this.is_selected = false;
                    this.is_loaded.set(false);
                    this.misc
                      .api_call('crud', {
                        op: op_,
                        collection: this.id(),
                        match: this.sweeped[this.segment],
                        doc: null,
                        is_crud: true,
                      })
                      .then(() => {
                        this.refresh_data(0, false);
                      })
                      .catch((res: any) => {
                        this.misc.doMessage(res && res.msg ? res.msg : res, 'error');
                      })
                      .finally(() => {
                        this.is_loaded.set(true);
                        this.is_deleting = false;
                      });
                  },
                },
              ],
            })
            .then((alert: any) => {
              alert.style.cssText =
                '--backdrop-opacity: 0 !important; z-index: 99999 !important; box-shadow: none !important;';
              alert.present();
            });
        }
      } else {
        this.misc.doMessage('please select the rows to be processed', 'warning');
      }
    }
  }

  async go_crud(record_: any, op: string) {
    if (this.id() === '_query' && !this.perm_()) {
    } else {
      const modal = await this.modal.create({
        component: CrudPage,
        backdropDismiss: true,
        cssClass: 'crud-modal',
        componentProps: {
          shuttle: {
            op: op,
            collection: this.id() ? this.id() : null,
            collections: this.collections_() ? this.collections_() : [],
            user: this.user(),
            data: record_,
            counters: this.counters_,
            structure: this.structure_(),
            sweeped:
              this.sweeped[this.segment] && op === 'action' ? this.sweeped[this.segment] : [],
            filter: op === 'action' ? this.filter_() : null,
            actions: this.actions() && this.actions().length > 0 ? this.actions() : [],
            actionix: op === 'action' && this.actionix >= 0 ? this.actionix : -1,
            view: this.view,
            scan: this.scan_(),
          },
        },
      });
      modal.onDidDismiss().then((res_: any) => {
        if (op === 'action' || res_.data?.modified || this.scan_()) {
          this.refresh_data(0, false);
        }
      });
      return await modal.present();
    }
  }

  async get_is_select_data() {
    this.sweeped[this.segment] = [];
    const q = await this.selected().findIndex((obj: boolean) => obj === true);
    this.clonok = q;
    q >= 0 ? (this.is_selected = true) : (this.is_selected = false);
    const r = await this.selected().reduce((acc: any, val: any, index: number) => {
      const q = val === true ? this.sweeped[this.segment].push(this.data()[index]._id) : null;
    }, []);
  }

  switch_select_data(event: any) {
    this.selected.set(new Array(this.data().length).fill(event));
    this.get_is_select_data();
  }

  set_select_data(i: number, event: any) {
    if (!['_log', '_backup', '_announcement'].includes(this.segment)) {
      this.selected.update((selected: any) =>
        selected.map((val: boolean, index: number) => (index === i ? event.detail.checked : val)),
      );
      this.get_is_select_data();
    }
  }

  orderByIndex = (a: any, b: any): number => {
    return a.value.index < b.value.index ? -1 : b.value.index > a.value.index ? 1 : 0;
  };

  do_sort(key: any, d: number) {
    this.sort = {};
    this.sort[key] = d ? d * -1 : 1;
    this.refresh_data(0, false);
  }

  // replaces the search state of one column with a new object, so the template notices the change
  set_searched(key_: any, patch_: any) {
    this.searched.update((searched: any) => ({
      ...searched,
      [key_]: { ...(searched ? searched[key_] : {}), ...patch_ },
    }));
  }

  set_search_kw(key_: any, kw_: any) {
    this.set_searched(key_, { kw: kw_ });
  }

  set_search(k_: any) {
    this.colvis_activated_.set(false);
    setTimeout(() => {
      this.searchfocus()?.setFocus();
      this.set_searched(k_, {
        kw: this.searched()[k_]?.kw?.trim().replace(/^\s*\n/gm, ''),
      });
      this.key_ = k_;
    }, 500);
    const searched: any = { ...this.searched() };
    for (let key_ in this.structure_().properties) {
      searched[key_] = {
        ...searched[key_],
        actived: k_ === key_ ? !searched[key_]?.actived : false,
      };
    }
    this.searched.set(searched);
  }

  init_search(full: boolean) {
    full ? this.searched.set({}) : null;
    this.storage.set('LSFILTER_' + this.id(), this.filter_()).then(() => {
      const searched_ = this.searched();
      if (searched_) {
        const searched: any = { ...searched_ };
        for (let key_ in this.structure_().properties) {
          searched[key_] = full
            ? { actived: false, kw: null, f: false, op: 'contains' }
            : {
                actived: false,
                kw: searched_[key_]?.kw ? searched_[key_]?.kw : null,
                f: searched_[key_]?.f,
                op: searched_[key_]?.op,
              };
        }
        this.searched.set(searched);
      }
    });
  }

  clear_filter() {
    return new Promise((resolve, reject) => {
      this.filter_.set([]);
      this.storage.remove('LSFILTER_' + this.id()).then(() => {
        this.storage.remove('LSSEARCHED_' + this.id()).then(() => {
          this.storage.remove('LSSELECTIONS_' + this.id()).then(() => {
            this.init_search(true);
            this.searched.set(null);
            this.sweeped[this.segment] = [];
            this.sort = {};
            this.refresh_data(0, false)
              .then(() => {
                resolve(true);
              })
              .catch((error: any) => {
                this.misc.doMessage(error, 'error');
                reject(error);
              });
          });
        });
      });
    });
  }

  init_search_item(key_: any) {
    const n_ = this.filter_().length;
    this.set_searched(key_, { actived: false });
    if (n_ > 0) {
      const filter_ = this.filter_().filter((item_: any) => !(item_ && item_['key'] === key_));
      if (filter_.length !== n_) {
        this.set_searched(key_, { f: false, kw: null, op: 'contains' });
      }
      this.filter_.set(filter_);
      this.storage.set('LSFILTER_' + this.id(), this.filter_()).then(() => {
        this.storage.set('LSSEARCHED_' + this.id(), this.searched()).then(() => {
          this.storage.set('LSSELECTIONS_' + this.id(), this.selections_()).then(() => {
            this.refresh_data(0, false);
          });
        });
      });
    }
  }

  search(key_: any, value_: string) {
    this.set_searched(key_, { actived: false });
    const filter_ = this.filter_();
    if (!filter_ || filter_.length === 0) {
      if (['true', 'false'].includes(value_)) {
        this.filter_.set([
          {
            key: key_,
            op: value_,
            value: null,
          },
        ]);
      } else {
        this.filter_.set([
          {
            key: key_,
            op: this.searched()[key_]?.op,
            value: value_,
          },
        ]);
      }
      this.set_searched(key_, { f: true });
      this.storage.set('LSFILTER_' + this.id(), this.filter_()).then(() => {
        this.storage.set('LSSEARCHED_' + this.id(), this.searched()).then(() => {
          this.storage.set('LSSELECTIONS_' + this.id(), this.selections_()).then(() => {
            this.refresh_data(0, false);
          });
        });
      });
    } else {
      let found_ = false;
      const next_ = filter_.map((item_: any) => {
        if (item_ && item_['key'] === key_) {
          found_ = true;
          return { ...item_, op: this.searched()[key_]?.op, value: value_ };
        }
        return item_;
      });
      !found_
        ? next_.push({
            key: key_,
            op: this.searched()[key_]?.op,
            value: value_,
          })
        : null;
      this.filter_.set(next_);
      this.set_searched(key_, { f: true });
      this.storage.set('LSFILTER_' + this.id(), this.filter_()).then(() => {
        this.storage.set('LSSEARCHED_' + this.id(), this.searched()).then(() => {
          this.storage.set('LSSELECTIONS_' + this.id(), this.selections_()).then(() => {
            this.refresh_data(0, false);
          });
        });
      });
    }
  }

  set_search_item(key_: any, op: string) {
    this.set_searched(key_, { op: op });
  }

  json_editor_init() {
    return new Promise((resolve) => {
      const jeoptions = new JsonEditorOptions();
      jeoptions.modes = ['tree', 'code', 'text'];
      jeoptions.mode = 'code';
      jeoptions.mainMenuBar = true;
      jeoptions.statusBar = false;
      jeoptions.navigationBar = true;
      jeoptions.enableSort = false;
      jeoptions.expandAll = false;
      this.jeoptions.set(jeoptions);
      resolve(true);
    });
  }

  set_editor(set_: boolean) {
    this.schemavis_.set(!this.schemavis_() && set_ && this.is_loaded());
    set_ ? this.json_editor_init().then(() => {}) : null;
  }

  do_flashcard(item_: any) {
    this.filter_.set(item_.view.data_filter);
    this.storage.set('LSFILTER_' + this.id(), this.filter_()).then(() => {
      this.refresh_data(0, false)
        .then(() => {})
        .catch((res: any) => {
          this.misc.doMessage(res, 'error');
        });
    });
  }

  save_schema_f() {
    if (this.json_content_) {
      this.is_saving.set(true);
      this.structure_.set(this.json_content_);
      this.misc
        .api_call('crud', {
          op: 'saveschema',
          collection: this.id(),
          structure: this.json_content_,
        })
        .then(() => {
          this.misc.doMessage('schema saved successfully', 'success');
          this.refresh_data(0, false).then(() => {
            this.schemavis_.set(false);
          });
        })
        .catch((error: any) => {
          this.misc.doMessage(error, 'error');
        })
        .finally(() => {
          this.is_saving.set(false);
        });
    } else {
      this.misc.doMessage('invalid structure', 'error');
    }
  }

  import_modal() {
    this.misc
      .import_modal(this.id())
      .then(() => {
        this.misc.doMessage('file imported successfully', 'success');
        this.refresh_data(0, false).then(() => {});
      })
      .catch((error: any) => {
        console.error(error);
      })
      .finally(() => {});
  }

  copy_column(key: any) {
    this.is_key_copying.set(true);
    this.is_key_copied.set(false);
    this.misc
      .api_call('crud', {
        op: 'copykey',
        collection: this.id(),
        properties: this.structure_().properties,
        match: this.filter_(),
        sweeped: this.sweeped[this.segment],
        key: key,
      })
      .then((res: any) => {
        this.misc
          .copy_to_clipboard(res.copied)
          .then(() => {
            this.is_key_copied.set(true);
            this.set_searched(key, { actived: false });
            this.misc.doMessage(`${res.copied?.split('\n')?.length} items copied`, 'success');
          })
          .catch((error: any) => {
            this.misc.doMessage(`${key} not copied: ${error}`, 'error');
          })
          .finally(() => {
            setTimeout(() => {
              this.is_key_copying.set(false);
              this.is_key_copied.set(false);
            }, 1000);
          });
      })
      .catch((error: any) => {
        this.is_key_copying.set(false);
        this.misc.doMessage(error, 'error');
      });
  }

  // marks one record as copied by replacing it, an in-place edit would not reach the template
  set_record_copied(indx_: number, is_copied_: boolean) {
    indx_ >= 0
      ? this.data.update((data: any) =>
          data.map((record_: any, index_: number) =>
            index_ === indx_ ? { ...record_, is_copied: is_copied_ } : record_,
          ),
        )
      : null;
  }

  copy(cpd_: any, event_: any, indx_: number) {
    event_.stopPropagation();
    this.is_copied.set(false);
    this.set_record_copied(indx_, false);
    this.misc
      .copy_to_clipboard(cpd_)
      .then(() => {
        this.is_copied.set(true);
        this.set_record_copied(indx_, true);
      })
      .catch((error: any) => {
        console.error('copy_headers', error);
      })
      .finally(() => {
        setTimeout(() => {
          this.is_copied.set(false);
          this.set_record_copied(indx_, false);
        }, 1000);
      });
  }

  json_changed(event_: any) {
    !event_.isTrusted ? (this.json_content_ = event_) : null;
  }

  go_query_job(record_: any, event_: any) {
    event_.stopPropagation();
    this.id() === '_query'
      ? this.storage.set('LSQUERY', record_).then(() => {
          this.misc.navi.next('/query/' + record_._id);
        })
      : this.storage.set('LSJOB', record_).then(() => {
          this.misc.navi.next('/job/' + record_._id);
        });
  }

  tdc(event_: any, record_: any) {
    this.record_ = record_;
    event_.stopPropagation();
  }

  selection_changed(item_: any, s_: number) {
    this.selections_.update((selections: any) => ({
      ...selections,
      [item_]: selections[item_].map((sel_: any, index_: number) =>
        index_ === s_ ? { ...sel_, value: !sel_.value } : sel_,
      ),
    }));
  }

  colvis_activate() {
    this.colvis_activated_.set(!this.colvis_activated_());
    const searched: any = { ...this.searched() };
    for (let key_ in this.structure_().properties) {
      searched[key_] = { ...searched[key_], actived: false };
    }
    this.searched.set(searched);
  }

  set_colvis_item(key_: any) {
    this.colvis_.update((colvis: any) => ({ ...colvis, [key_]: !colvis[key_] }));
  }

  set_colvis() {
    this.storage.set('LSCOLVIS_' + this.id(), this.colvis_()).then(() => {
      this.colvis_activated_.set(false);
      this.refresh_data(0, false);
    });
  }

  colvis_allon() {
    this.colvis_.set({});
  }

  colvis_alloff() {
    const colvis_: any = {};
    for (let key_ in this.structure_().properties) {
      colvis_[key_] = true;
    }
    this.colvis_.set(colvis_);
  }
}
