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

import { Injectable, inject } from '@angular/core';
import { Subject, BehaviorSubject } from 'rxjs';
import { Validators, UntypedFormControl } from '@angular/forms';
import { Miscellaneous } from './misc';

@Injectable({ providedIn: 'root' })
export class Crud {
  private misc = inject(Miscellaneous);

  public fields: any = [];
  public modalSubmitListener = new Subject<any>();
  public updateListener = new Subject<any>();
  public objectsListener = new BehaviorSubject([]);
  public objects = this.objectsListener.asObservable();
  public collections = new BehaviorSubject<any>([]);
  public queries = new BehaviorSubject<any>([]);
  public visuals = new BehaviorSubject<any>([]);

  init_form(
    op: string,
    structure: any,
    form: any,
    data: any,
    collections: any,
    counters: any,
    actionix_: number,
  ) {
    return new Promise((resolve) => {
      const init: any = {};
      this.fields = [];
      delete structure.properties['col_structure'];
      const names_ = Object.keys(structure.properties);
      for (const item of names_) {
        const p: any = structure.properties[item];
        const bsonType_ = p.bsonType;
        let enums_ = p.enum;
        const arrayInc_ = bsonType_ === 'array';
        const objectInc_ = bsonType_ === 'object';
        const required_ =
          structure.required && structure.required.indexOf(item) !== -1
            ? true
            : actionix_ &&
                actionix_ > 0 &&
                structure.actions[actionix_].required?.indexOf(item) !== -1
              ? true
              : false;
        const minLength_ = p.minLength > 0 ? p.minLength : null;
        const maxLength_ = p.maxLength > 0 ? p.maxLength : null;
        const minimum_ = p.minimum > 0 ? p.minimum : null;
        const maximum_ = p.maximum > 0 ? p.maximum : null;
        const timestamp_ = p.timestamp && ['action', 'insert'].includes(op) ? true : false;
        const pattern_ = p.pattern ? p.pattern : null;
        const tzoffset = new Date().getTimezoneOffset() * 60000;
        const default_ = p.default
          ? p.default === '$CURRENT_DATE'
            ? new Date(Date.now() - tzoffset).toISOString().substring(0, 19)
            : p.default
          : null;
        const kv_ = p.subType === 'keyvalue';
        const permanent_ = p.permanent && data?._modified_count >= 0 ? true : false;
        const collection_ = p.collection ? true : false;
        const disabled_ = p.disabled || permanent_ ? true : false;
        if (collection_) {
          enums_ = (collections || []).map((c: any) => c.col_id);
        }
        const parents_ = structure.parents
          ? structure.parents.find((obj: any) => obj.match[0]?.key === item)
          : null;
        const v = [];
        if (required_) {
          v.push(Validators.required);
        }
        if (minLength_ && bsonType_ !== 'array') {
          v.push(Validators.minLength(minLength_));
        }
        if (maxLength_ && bsonType_ !== 'array') {
          v.push(Validators.maxLength(maxLength_));
        }
        if (minimum_) {
          v.push(Validators.min(minimum_));
        }
        if (maximum_) {
          v.push(Validators.max(maximum_));
        }
        if (pattern_ && !p.file) {
          v.push(Validators.pattern(pattern_));
        }
        this.fields.push({
          name: item,
          title: p.title,
          enum: enums_,
          required: required_,
          bsonType: bsonType_,
          description: p.description ? p.description : null,
          password: !!p.password,
          maxLength: maxLength_,
          minLength: minLength_,
          minItems: p.minItems && p.minItems >= 0 ? p.minItems : null,
          maxItems: p.maxItems && p.maxItems >= 0 ? p.maxItems : null,
          parents: parents_,
          items: p.items ? p.items : null,
          file: !!p.file,
          filter: !!p.filter,
          kv: kv_,
          ko: p.subType === 'keyop',
          permanent: permanent_,
          readonly: !!p.readonly,
          collection: collection_,
          view: !!p.view,
          property: !!p.property,
          textarea: !!p.textarea,
          decimals: p.decimals && p.decimals > 0 ? p.decimals : null,
          hashtag: !!p.hashtag,
          chips: !!p.chips,
          subType: p.subType ? p.subType : null,
          manualAdd: !!p.manualAdd,
          placeholder: p.placeholder ? p.placeholder : null,
          counter: p.counter === true,
          dateOnly: !!p.dateOnly,
          caseType: p.caseType ? p.caseType : null,
          timestamp: timestamp_,
          selection: !!p.selection,
          reminder: !!p.reminder,
        });
        const kvval_: any = [{ key: null, value: null }];
        init[item] = timestamp_
          ? new Date(Date.now() - tzoffset).toISOString().replace(/-|:|T/gi, '').substring(0, 14)
          : counters && counters[item]
            ? counters[item]
            : default_
              ? default_
              : arrayInc_
                ? kv_
                  ? kvval_
                  : []
                : objectInc_
                  ? {}
                  : null;
        form.addControl(
          item,
          new UntypedFormControl(
            {
              value: data && data[item] ? data[item] : init[item],
              disabled:
                disabled_ || (item === 'id' && op === 'update' && (data[item] || init[item]))
                  ? true
                  : false,
            },
            Validators.compose(v),
          ),
        );
      }
      resolve({ form: form, fields: this.fields, init: init });
    });
  }

  submit_f(
    data_: any,
    collection: string,
    structure: any,
    form: any,
    _id: string,
    op: string,
    file: any,
    match: any,
    filter: any,
    actionix: any,
    link_: any,
    linked_: any,
  ) {
    return new Promise((resolve, reject) => {
      const properties = structure.properties;
      const doc_: any = {};
      for (const item in properties) {
        doc_[item] =
          properties[item].bsonType === 'date' && form.get(item).value
            ? new Date(form.get(item).value)
            : form.get(item).value;
      }
      if (_id) {
        doc_['_id'] = _id;
      }
      if (file) {
        const posted_: FormData = new FormData();
        posted_.append('file', file, file.name);
        posted_.append('collection', doc_['sto_collection_id']);
        posted_.append('process', doc_['sto_process']);
        this.misc
          .api_call_file('import', posted_)
          .then((res_: any) => {
            res_.cid = doc_['sto_collection_id'];
            resolve(res_);
          })
          .catch((err: any) => reject(err));
      } else {
        this.misc
          .api_call('crud', {
            op: op,
            collection: collection,
            doc: doc_,
            data: data_,
            match: match && match.length > 0 ? match : null,
            filter: filter ? filter : null,
            _id: _id ? _id : null,
            actionix: actionix,
            link: link_,
            linked: linked_,
          })
          .then((res_: any) => resolve(res_))
          .catch((error_: any) => reject(error_));
      }
    });
  }

  get_collections() {
    return this.misc
      .api_call('crud', { op: 'collections', collection: '_collection' })
      .then((res: any) => {
        this.misc.collections.next(res);
        this.collections.next(res);
        return true;
      });
  }

  get_visuals(scope_: any) {
    return this.misc.api_call('crud', { op: 'visuals', collection: '_query', scope: scope_ });
  }

  get_visual(id_: any) {
    return this.misc.api_call('crud', { op: 'visual', collection: '_query', id: id_ });
  }

  get_otp(id_: any) {
    return this.misc.api_call('crud', { op: 'reqotp', collection: '_query', id: id_ });
  }

  get_collection(id: string) {
    return this.misc.api_call('crud', { collection: id, op: 'collection' });
  }

  get_query_job(type_: string, id_: string, limit_: number, run_: boolean) {
    return this.misc.api_call('crud', {
      id: id_,
      op: type_,
      collection: type_ === 'job' ? '_job' : '_query',
      limit: limit_,
      run: run_,
    });
  }

  announce(id_: string, type_: string, otp_: number) {
    return this.misc.api_call('crud', {
      id: id_,
      op: 'announce',
      collection: '_query',
      tfac: otp_,
      type: type_,
    });
  }

  get_announcements() {
    return this.misc.api_call('crud', { op: 'announcements', collection: '_announcement' });
  }

  get_all() {
    return this.get_collections()
      .catch((error: any) => {
        console.error('*** collections error', error);
      })
      .then(() => true);
  }
}
