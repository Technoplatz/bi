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

import { Injectable, Type, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ModalController, AlertController, ToastController } from '@ionic/angular';
import { Storage } from '@ionic/storage-angular';
import { TranslateService } from '@ngx-translate/core';
import { Subject, BehaviorSubject } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class Miscellaneous {
  private storage = inject(Storage);
  private translate = inject(TranslateService);
  private modal = inject(ModalController);
  private alert = inject(AlertController);
  private toast = inject(ToastController);
  private http = inject(HttpClient);

  public collections = new BehaviorSubject<any>([]);
  public session_ = new BehaviorSubject<any>([]);
  public navi = new Subject<any>();
  public version = new BehaviorSubject<any>({});
  public saas = new BehaviorSubject<any>(null);
  public localization = new BehaviorSubject<any>(null);
  private collections_: any;
  private mopen_ = false;
  // the modal pages register themselves here so this service does not import them (no circular imports)
  private modalComponents_: { [key: string]: Type<any> } = {};

  constructor() {
    this.collections.subscribe((res: any) => {
      this.collections_ = res && res.data ? res.data : [];
    });
  }

  register_modal(name: string, component: Type<any>) {
    this.modalComponents_[name] = component;
  }

  private session_meta() {
    return this.storage.get('LSUSERMETA').then((LSUSERMETA: any) => ({
      meta: LSUSERMETA,
      token: LSUSERMETA && LSUSERMETA.token ? LSUSERMETA.token : '',
      api_key: LSUSERMETA && LSUSERMETA.api_key ? LSUSERMETA.api_key : '',
    }));
  }

  private on_http_error(res__: any, reject: (reason?: any) => void) {
    if (res__ && res__.error && res__.status) {
      if (res__.status === 403) {
        this.session_.next('ended');
        this.doMessage(res__.error.msg, 'error');
      }
      reject(res__.error.msg ? res__.error.msg : res__.error);
    } else {
      reject(res__);
    }
  }

  api_call(qstr_: string, posted_: any) {
    return new Promise((resolve, reject) => {
      this.session_meta().then(({ token, api_key }) => {
        const body_ = typeof posted_ === 'string' ? JSON.parse(posted_) : posted_;
        const hdr_: any = {
          headers: new HttpHeaders({
            'Content-Type': 'application/json',
            Authorization: 'Bearer ' + token,
            'X-Api-Key': api_key,
          }),
          observe: 'response',
        };
        if (body_['responseType']) {
          hdr_.responseType = body_['responseType'];
        }
        this.http.post<any>(`${environment.apiUrl}/${qstr_}`, body_, hdr_).subscribe({
          next: (res: any) => {
            const res_ = res.body;
            const qt_ = res.headers.get('Content-Type') || '';
            const filename_ =
              qt_.indexOf('filename=') > 0
                ? qt_.substring(qt_.indexOf('filename=') + 9).trim()
                : null;
            if (body_.responseType) {
              resolve({ binary: res_, filename: filename_ });
            } else if (res_ && res_.result) {
              resolve(res_);
            } else {
              reject(res_ && res_.msg ? res_.msg : res_);
            }
          },
          error: (res__: any) => this.on_http_error(res__, reject),
        });
      });
    });
  }

  api_call_file(qstr_: string, posted_: FormData) {
    return new Promise((resolve, reject) => {
      this.session_meta().then(({ token, api_key }) => {
        this.http
          .post<any>(`${environment.apiUrl}/${qstr_}`, posted_, {
            headers: new HttpHeaders({ Authorization: 'Bearer ' + token, 'X-Api-Key': api_key }),
            observe: 'response',
          })
          .subscribe({
            next: (res: any) => {
              const res_ = res.body;
              if (res_ && res_.result) {
                resolve(res_);
              } else {
                reject(res_ && res_.msg ? res_.msg : res_);
              }
            },
            error: (res__: any) => this.on_http_error(res__, reject),
          });
      });
    });
  }

  import_modal(id: any) {
    return new Promise((resolve, reject) => {
      const component_ = this.modalComponents_['crud'];
      if (!component_) {
        reject('the data editor is not available yet');
        return;
      }
      this.storage.get('LSUSERMETA').then((LSUSERMETA: any) => {
        this.modal
          .create({
            component: component_,
            backdropDismiss: false,
            cssClass: 'crud-modal',
            componentProps: {
              shuttle: {
                op: 'import',
                collection: '_storage',
                collections: this.collections_ ? this.collections_ : [],
                user: LSUSERMETA,
                data: {
                  sto_id: 'data-import',
                  sto_collection_id: id,
                  sto_process: 'insert',
                  sto_file: null,
                },
                structure: environment.import_structure,
                sweeped: [],
                filter: {},
                actions: [],
                direct: -1,
              },
            },
          })
          .then((modal: any) => {
            modal.present().then(() => {
              modal.onDidDismiss().then((res: any) => {
                if (res.data && res.data.modified) {
                  resolve(res.data.cid);
                } else {
                  reject(res);
                }
              });
            });
          });
      });
    });
  }

  set_locale(LSLOCALE_: string) {
    return new Promise((resolve, reject) => {
      if (LSLOCALE_) {
        this.storage.set('LSLOCALE', LSLOCALE_).then(() => {
          this.translate.setFallbackLang(LSLOCALE_);
          this.translate.use(LSLOCALE_);
          this.localization.next(
            LSLOCALE_ === 'tr'
              ? 'tr-TR'
              : LSLOCALE_ === 'de'
                ? 'de-DE'
                : LSLOCALE_ === 'en'
                  ? 'en-US'
                  : null,
          );
          resolve(true);
        });
      } else {
        reject('language code not valid');
      }
    });
  }

  locale() {
    return new Promise((resolve) => {
      this.storage.get('LSLOCALE').then((LSLOCALE_: any) => {
        this.localization.next(
          LSLOCALE_ === 'tr'
            ? 'tr-TR'
            : LSLOCALE_ === 'de'
              ? 'de-DE'
              : LSLOCALE_ === 'en'
                ? 'en-US'
                : null,
        );
        resolve(LSLOCALE_);
      });
    });
  }

  validateOTP(type_: any) {
    return new Promise((resolve, reject) => {
      this.alert
        .create({
          cssClass: 'my-custom-class',
          subHeader: this.translate.instant('OTP Validation') + ` [${type_}]`,
          message: this.translate.instant('Please enter your one-time password') + ':',
          backdropDismiss: false,
          inputs: [
            { name: 'id', value: null, type: 'number', cssClass: 'token', placeholder: '000000' },
          ],
          buttons: [
            {
              text: this.translate.instant('Cancel'),
              role: 'cancel',
              cssClass: 'primary',
              handler: () => {
                reject();
              },
            },
            {
              text: this.translate.instant('OK'),
              handler: (alertData: any) => {
                resolve(alertData.id);
              },
            },
          ],
        })
        .then((alert: any) => {
          alert.present().then(() => {
            const fnput_: any = document.querySelector('ion-alert input');
            fnput_?.focus();
          });
        })
        .catch((error_: any) => {
          reject(error_);
        });
    });
  }

  doMessage(msg: any, type: string) {
    if (type === 'error') {
      console.error('!!! err', msg);
    }
    const text_ = this.translate.instant(String(msg ?? '')) ?? '';
    this.toast
      .create({
        message: `${String(text_).toLowerCase()}.`,
        duration: ['success', 'warning'].includes(type) ? 3000 : 7000,
        cssClass:
          type === 'success'
            ? 'toast-class-success'
            : type === 'error'
              ? 'toast-class-error'
              : 'toast-class-warning',
        buttons: [{ side: 'end', icon: 'close-outline', role: 'cancel', handler: () => {} }],
      })
      .then((toast_: any) => {
        toast_.present();
      });
  }

  getFormattedDate(val: any) {
    const tzoffset = new Date().getTimezoneOffset() * 60000;
    const date_ = val ? val : new Date(Date.now() - tzoffset).toISOString();
    return date_.substring(0, 19) + 'Z';
  }

  copy_to_clipboard(s: string) {
    return navigator.clipboard.writeText(s).then(() => true);
  }

  dismissModal(obj_: any) {
    return new Promise((resolve, reject) => {
      this.mopen_ = false;
      setTimeout(() => {
        this.modal
          .dismiss(obj_)
          .then((dismiss_: any) => {
            resolve(dismiss_);
          })
          .catch((error: any) => {
            reject(error);
          });
      }, 200);
    });
  }

  sign_modal(op: string) {
    return new Promise((resolve, reject) => {
      const component_ = this.modalComponents_['sign'];
      if (this.mopen_ || !component_) {
        return;
      }
      this.modal
        .create({
          component: component_,
          backdropDismiss: false,
          cssClass: 'sign-modal',
          componentProps: { op: op, user: null },
        })
        .then((modal_: any) => {
          modal_
            .present()
            .then(() => {
              this.mopen_ = true;
              resolve(modal_);
            })
            .catch((error: any) => {
              reject(error);
            });
          modal_
            .onDidDismiss()
            .then((dismiss_: any) => {
              this.mopen_ = false;
              resolve(dismiss_);
            })
            .catch((error: any) => {
              reject(error);
            });
        });
    });
  }

  show_note(note_: string, event_: any) {
    event_.stopPropagation();
    this.alert
      .create({
        subHeader: this.translate.instant('Notes'),
        message: this.translate.instant(note_),
        buttons: [{ text: this.translate.instant('Got It'), role: 'cancel', handler: () => {} }],
      })
      .then((alert: any) => {
        alert.style.cssText =
          '--backdrop-opacity: 0 !important; z-index: 99999 !important; box-shadow: none !important;';
        alert.present();
      });
  }

  unique_array(value_: any, index_: number, self_: any) {
    return self_.indexOf(value_) === index_;
  }
}
