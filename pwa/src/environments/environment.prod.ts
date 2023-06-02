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

export const environment = {
  animated: false,
  sanitizerEnabled: true,
  production: true,
  appVersion: require("../../package.json").version,
  release: "Brezel Edition",
  apiPort: "8443",
  support_url: "#",
  misc: {
    logo: "logo-electron",
    default_sort: '{"_modified_at": -1}',
    default_collation: '{"locale": "tr"}',
    default_page: 1,
    default_icon: "medical-outline",
    limit: 30,
    limits: [20, 50, 100],
    loadingText: "Bitte warten Sie",
    defaultColumnWidth: 140,
    default_delay: 500
  },
  import_structure: {
    "properties": {
      "sto_id": {
        "bsonType": "string",
        "minLength": 3,
        "maxLength": 32,
        "pattern": "^[a-z0-9-]{3,32}$",
        "title": "ID",
        "description": "Upload ID",
        "permanent": true,
        "required": true
      },
      "sto_collection_id": {
        "bsonType": "string",
        "minLength": 3,
        "maxLength": 32,
        "pattern": "^[a-z0-9-_]{3,32}$",
        "title": "Collection",
        "description": "ID of the target Collection",
        "collection": true,
        "permanent": true,
        "required": true
      },
      "sto_file": {
        "bsonType": "string",
        "minLength": 0,
        "maxLength": 64,
        "file": true,
        "title": "File",
        "description": "Excel, CSV or JSON File"
      }
    },
    "required": [
      "sto_id",
      "sto_collection_id",
      "sto_file"
    ]
  },
  pivotvalueops: [
    { "key": "sum", "value": "sum" },
    { "key": "count", "value": "count" },
    { "key": "size", "value": "size" },
    { "key": "unique", "value": "unique" },
    { "key": "mean", "value": "mean" },
    { "key": "std", "value": "std" },
    { "key": "max", "value": "max" },
    { "key": "min", "value": "min" }
  ],
  filterops: [
    { "key": "=", "op": "=", "value": "eq" },
    { "key": "not =", "op": "!=", "value": "ne" },
    { "key": ">", "op": ">", "value": "gt" },
    { "key": ">=", "op": ">=", "value": "gte" },
    { "key": "<", "op": "<", "value": "lt" },
    { "key": "<=", "op": "<=", "value": "lte" },
    { "key": "contains", "op": "", "value": "contains" },
    { "key": "not contains", "op": "", "value": "nc" },
    { "key": "in", "op": "", "value": "in" },
    { "key": "not in", "op": "", "value": "nin" },
    { "key": "null", "op": "", "value": "null" },
    { "key": "not null", "op": "", "value": "nnull" },
    { "key": "true", "op": "", "value": "true" },
    { "key": "false", "op": "", "value": "false" }
  ],
  admin_collections: {
    "_collection": {
      "title": "Collections",
      "description": "User defined database collections."
    },
    "_announcement": {
      "title": "Announcements",
      "description": "Data announcements log of the shared views."
    },
    "_user": {
      "title": "Users",
      "description": "Internal users, data subscribers and hashtags."
    },
    "_permission": {
      "title": "Permissions",
      "description": "User permissions of the database collections."
    },
    "_firewall": {
      "title": "Firewall",
      "description": "IP Firewall"
    },
    "_token": {
      "title": "API Tokens",
      "description": "Access tokens of the built-in API functions."
    },
    "_backup": {
      "title": "Backups",
      "description": "Database backups and restoring."
    },
    "_log": {
      "title": "Logs",
      "description": "Transaction logs in detail."
    },
    "_kv": {
      "title": "Key:Value",
      "description": "Basic environment variables defined as KEY:VALUE pairs."
    }
  },
  segmentsadm: [
    { "id": "_announcement", "title": "Announcements", "description": "Data announcements of shared views." },
    { "id": "_user", "title": "Users", "description": "Internal users and data subscribers." },
    { "id": "_permission", "title": "Permissions", "description": "Database collection permissions." },
    { "id": "_firewall", "title": "Firewall", "description": "IP Firewall" },
    { "id": "_token", "title": "API Tokens", "description": "Access tokens of built-in API functions." },
    { "id": "_backup", "title": "Backups", "description": "Database backup and restore." },
    { "id": "_log", "title": "Logs", "description": "Transaction logs in detail" },
    { "id": "_kv", "title": "Key:Value", "description": "Basic environment variables defined as KEY:VALUE pairs." }
  ],
  themes: [
    { "name": "Dark", "color": "#111111" },
    { "name": "Cobalt", "color": "#0047AB" },
    { "name": "Grün", "color": "#008000" },
    { "name": "Glaucous", "color": "#6082B6" },
    { "name": "Marine", "color": "#3A62FA" },
    { "name": "Iris", "color": "#5D3FD3" },
    { "name": "Sunshine", "color": "#FF5733" },
    { "name": "Rot", "color": "#AA0000" }
  ]
}