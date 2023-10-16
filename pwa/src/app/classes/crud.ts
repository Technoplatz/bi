/*
Technoplatz BI

Copyright (C) 2019-2023 Technoplatz IT Solutions GmbH, Mustafa Mat

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

If your software can interact with users remotely through a computer
network, you should also make sure that it provides a way for users to
get its source.  For example, if your program is a web application, its
interface could display a "Source" link that leads users to an archive
of the code.  There are many ways you could offer source, and different
solutions will be better for different programs; see section 13 for the
specific requirements.

You should also get your employer (if you work as a programmer) or school,
if any, to sign a "copyright disclaimer" for the program, if necessary.
For more information on this, and how to apply and follow the GNU AGPL, see
https://www.gnu.org/licenses.
*/

import { Injectable } from "@angular/core";
import { Subject, BehaviorSubject } from "rxjs";
import { Validators, UntypedFormControl } from "@angular/forms";
import { Miscellaneous } from "./misc";

@Injectable({
  providedIn: "root"
})

export class Crud {
  public cartitems = [];
  public productList: any = [];
  public fields: any = [];
  public modalSubmitListener = new Subject<any>();
  public updateListener = new Subject<any>();
  public objectsListener = new BehaviorSubject([]);
  public objects = this.objectsListener.asObservable();
  public collections = new BehaviorSubject<any>([]);
  public views = new BehaviorSubject<any>([]);
  public queries = new BehaviorSubject<any>([]);
  public charts = new BehaviorSubject<any>([]);
  public visuals = new BehaviorSubject<any>([]);
  public announcements = new BehaviorSubject<any>([]);

  constructor(
    private misc: Miscellaneous
  ) { }

  init_form(op: string, structure: any, form: any, data: any, collections: any, views: any, counters: any, actionix_: number) {
    return new Promise((resolve, reject) => {
      let i = 0;
      let init: any = {};
      this.fields = [];
      delete structure.properties["col_structure"];
      for (let item in structure.properties) {
        const p: any = structure.properties[item];
        const bsonType_ = p.bsonType;
        let enums_ = p.enum;
        const arrayInc_ = bsonType_ === "array" ? true : false;
        const objectInc_ = bsonType_ === "object" ? true : false;
        const title_ = p.title;
        const required_ = structure.required && structure.required.indexOf(item) !== -1 ? true : actionix_ && actionix_ > 0 && structure.actions[actionix_].required?.indexOf(item) !== -1 ? true : false;
        const description_ = p.description ? p.description : null;
        const minLength_ = p.minLength > 0 ? p.minLength : null;
        const maxLength_ = p.maxLength > 0 ? p.maxLength : null;
        const minimum_ = p.minimum > 0 ? p.minimum : null;
        const maximum_ = p.maximum > 0 ? p.maximum : null;
        const minItems_ = p.minItems && p.minItems >= 0 ? p.minItems : null;
        const maxItems_ = p.maxItems && p.maxItems >= 0 ? p.maxItems : null;
        const caseType_ = p.caseType ? p.caseType : null;
        const timestamp_ = p.timestamp && ["action", "insert"].includes(op) ? true : false;
        const items_ = p.items ? p.items : null;
        const password_ = p.password ? true : false;
        const pattern_ = p.pattern ? p.pattern : null;
        const placeholder_ = p.placeholder ? p.placeholder : null;
        const subType_ = p.subType ? p.subType : null;
        const tzoffset = new Date().getTimezoneOffset() * 60000;
        const default_ = p.default ? p.default === '$CURRENT_DATE' ? new Date(Date.now() - tzoffset).toISOString().substring(0, 19) : p.default : null;
        const file_ = p.file ? true : false;
        const filter_ = p.filter ? true : false;
        const property_ = p.property ? true : false;
        const kv_ = p.subType === "keyvalue" ? true : false;
        const ko_ = p.subType === "keyop" ? true : false;
        const permanent_ = p.permanent && op == "update" && data && data[item] ? true : false;
        const readonly_ = p.readonly ? true : actionix_ && actionix_ > 0 && structure.actions[actionix_].readonly?.indexOf(item) !== -1 ? true : false;
        const dateOnly_ = p.dateOnly ? true : false;
        const collection_ = p.collection ? true : false;
        const textarea_ = p.textarea ? true : false;
        const disabled_ = p.disabled || permanent_ ? true : false;
        const hashtag_ = p.hashtag ? true : false;
        const chips_ = p.chips ? true : false;
        const view_ = p.view ? true : false;
        const decimals_ = p.decimals && p.decimals > 0 ? p.decimals : null;
        const manualAdd_ = p.manualAdd ? true : false;
        const counter_ = p.counter && p.counter === true ? true : false;
        view_ ? enums_ = (() => { let arr_ = []; for (let v = 0; v < views.length; v++) { arr_.push(views[v].record.vie_id) } return arr_; })() : null;
        collection_ ? enums_ = (() => { let arr_ = []; for (let v = 0; v < collections.length; v++) { arr_.push(collections[v].col_id) } return arr_; })() : null;
        const parents_ = structure.parents ? structure.parents.find((obj: any) => obj.match[0]?.key === item) : null;
        const v = [];
        required_ ? v.push(Validators.required) : null;
        minLength_ && bsonType_ !== "array" ? v.push(Validators.minLength(minLength_)) : null;
        maxLength_ && bsonType_ !== "array" ? v.push(Validators.maxLength(maxLength_)) : null;
        minimum_ ? v.push(Validators.min(minimum_)) : null;
        maximum_ ? v.push(Validators.max(maximum_)) : null;
        pattern_ && !p.file ? v.push(Validators.pattern(pattern_)) : null;
        this.fields.push({
          name: item,
          title: title_,
          enum: enums_,
          required: required_,
          bsonType: bsonType_,
          description: description_,
          password: password_,
          maxLength: maxLength_,
          minLength: minLength_,
          minItems: minItems_,
          maxItems: maxItems_,
          parents: parents_,
          items: items_,
          file: file_,
          filter: filter_,
          kv: kv_,
          ko: ko_,
          permanent: permanent_,
          readonly: readonly_,
          collection: collection_,
          view: view_,
          property: property_,
          textarea: textarea_,
          decimals: decimals_,
          hashtag: hashtag_,
          chips: chips_,
          subType: subType_,
          manualAdd: manualAdd_,
          placeholder: placeholder_,
          counter: counter_,
          dateOnly: dateOnly_,
          caseType: caseType_,
          timestamp: timestamp_
        });
        const kvval_: any = [{
          key: null,
          value: null
        }];
        init[item] = timestamp_ ? new Date(Date.now() - tzoffset).toISOString().replace(/-|:|T/gi, '').substring(0, 14) : counters && counters[item] ? counters[item] : default_ ? default_ : arrayInc_ ? kv_ ? kvval_ : [] : objectInc_ ? {} : null;
        form.addControl(item, new UntypedFormControl({ "value": data && data[item] ? data[item] : init[item], "disabled": disabled_ || (item === "id" && op === "update" && (data[item] || init[item])) ? true : false }, Validators.compose(v)));
        if (i === Object.keys(structure.properties).length - 1) {
          resolve({
            form: form,
            fields: this.fields,
            init: init
          });
        } else {
          i++;
        }
      }
    });
  }

  submit_f(collection: string, structure: any, form: any, _id: string, op: string, file: any, match: any, filter: any, view: any, actionix: any, link_: any, linked_: any) {
    return new Promise((resolve, reject) => {
      const properties = structure.properties;
      let doc_: any = {};
      let i = 0;
      for (let item in properties) {
        doc_[item] = properties[item].bsonType === "date" && form.get(item).value ? new Date(form.get(item).value) : form.get(item).value;
        if (i === Object.keys(properties).length - 1) {
          _id ? (doc_["_id"] = _id) : null;
          if (file) {
            let posted_: FormData = new FormData();
            const sto_collection_id_ = doc_["sto_collection_id"];
            const sto_process_ = doc_["sto_process"];
            posted_.append("file", file, file.name);
            posted_.append("collection", sto_collection_id_);
            posted_.append("process", sto_process_);
            this.misc.api_call_file("import", posted_).then((res: any) => {
              res.cid = sto_collection_id_;
              resolve(res);
            }).catch((err: any) => {
              reject(err);
            });
          } else {
            this.misc.api_call("crud", {
              op: op,
              collection: collection,
              doc: doc_,
              match: match && match.length > 0 ? match : null,
              filter: filter ? filter : null,
              _id: _id ? _id : null,
              view: view,
              actionix: actionix,
              link: link_,
              linked: linked_
            }).then((res: any) => {
              resolve(res);
            }).catch((err: any) => {
              reject(err);
            });
          }
        } else {
          i++;
        }
      }
    });
  }

  get_collections() {
    return new Promise((resolve, reject) => {
      this.misc.api_call("crud", {
        op: "collections",
        collection: "_collection"
      }).then((res: any) => {
        this.misc.collections.next(res);
        this.collections.next(res)
        resolve(true);
      }).catch((err: any) => {
        reject(err);
      });
    });
  }

  get_collection(id: string) {
    return new Promise((resolve, reject) => {
      this.misc.api_call("crud", {
        collection: id,
        op: "collection",
      }).then((res: any) => {
        resolve(res);
      }).catch((err: any) => {
        reject(err);
      });
    });
  }

  get_query(id_: string, page_: number, limit_: number, run_: boolean) {
    return new Promise((resolve, reject) => {
      this.misc.api_call("crud", {
        id: id_,
        op: "query",
        collection: "_query",
        page: page_,
        limit: limit_,
        run: run_
      }).then((res: any) => {
        resolve(res);
      }).catch((err: any) => {
        reject(err);
      });
    });
  }

  get_charts() {
    return new Promise((resolve, reject) => {
      this.misc.api_call("crud", {
        op: "charts",
        collection: "_query",
        source: "internal",
        dashboard: false
      }).then((res: any) => {
        resolve(this.charts.next(res));
      }).catch((err: any) => {
        reject(err);
      });
    });
  }

  get_views() {
    return new Promise((resolve, reject) => {
      this.misc.api_call("crud", {
        op: "views",
        collection: "_query"
      }).then((res: any) => {
        resolve(this.views.next(res.views));
      }).catch((err: any) => {
        reject(err);
      });
    });
  }

  get_announcements() {
    return new Promise((resolve, reject) => {
      this.misc.api_call("crud", {
        op: "announcements",
        collection: "_announcement"
      }).then((res: any) => {
        resolve(this.announcements.next(res));
      }).catch((err: any) => {
        reject(err);
      });
    });
  }

  get_all() {
    return new Promise((resolve, reject) => {
      // this.get_charts().then(() => { }).catch((error: any) => {
      //   console.error("*** charts error", error);
      // }).finally(() => {
      //   resolve(true);
      // });
      this.get_views().then(() => { }).catch((error: any) => {
        console.error("*** views error", error);
      }).finally(() => {
        resolve(true);
      });
      this.get_collections().then(() => { }).catch((error: any) => {
        console.error("*** collections error", error);
      }).finally(() => {
        resolve(true);
      });
    });
  }

}
