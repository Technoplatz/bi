export const environment = {
  production: true,
  appVersion: require("../../package.json").version,
  release: "Brezel",
  apiPort: "5001",
  apiKey: "61c09da62f1f9ca9357796c9",
  misc: {
    logo: "logo-electron",
    default_sort: '{"_modified_at": -1}',
    default_collation: '{"locale": "tr"}',
    default_page: 1,
    default_icon: "medical-outline",
    limit: 30,
    limits: [20, 50, 100],
    loadingText: "Bitte warten Sie"
  },
  import_structure: {
    "properties": {
      "sto_id": {
        "bsonType": "string",
        "minLength": 3,
        "maxLength": 32,
        "pattern": "^[a-z0-9-]{3,32}$",
        "title": "ID",
        "description": "Storage ID",
        "permanent": true,
        "required": true,
        "width": 160
      },
      "sto_collection_id": {
        "bsonType": "string",
        "minLength": 3,
        "maxLength": 32,
        "pattern": "^[a-z0-9-_]{3,32}$",
        "title": "Collection",
        "description": "Collection ID",
        "collection": true,
        "required": true,
        "width": 110
      },
      "sto_file": {
        "bsonType": "string",
        "minLength": 0,
        "maxLength": 64,
        "file": true,
        "title": "Excel File",
        "description": "Excel File",
        "width": 100
      }
    },
    "required": [
      "sto_id",
      "sto_collection_id",
      "sto_file"
    ],
    "unique": [
      [
        "sto_id"
      ],
      [
        "sto_collection_id"
      ]
    ],
    "index": [
      [
        "sto_collection_id"
      ]
    ],
    "sort": {
      "_modified_at": -1
    }
  },
  upload_structure: {
    "properties": {
      "sto_id": {
        "bsonType": "string",
        "minLength": 3,
        "maxLength": 32,
        "pattern": "^[a-z0-9-]{3,32}$",
        "title": "ID",
        "description": "Storage ID",
        "permanent": true,
        "required": true,
        "width": 160
      },
      "sto_collection_id": {
        "bsonType": "string",
        "minLength": 3,
        "maxLength": 32,
        "pattern": "^[a-z0-9-_]{3,32}$",
        "title": "Collection",
        "description": "Collection ID",
        "required": true,
        "width": 110
      },
      "sto_prefix": {
        "bsonType": "string",
        "minLength": 3,
        "maxLength": 3,
        "pattern": "^[a-z]{3,3}$",
        "title": "Column Prefix",
        "description": "Column Prefix",
        "required": true,
        "width": 90
      },
      "sto_file": {
        "bsonType": "string",
        "minLength": 0,
        "maxLength": 64,
        "file": true,
        "title": "Excel File",
        "description": "Excel File",
        "width": 100
      }
    },
    "required": [
      "sto_id",
      "sto_collection_id",
      "sto_prefix",
      "sto_file"
    ],
    "unique": [
      [
        "sto_id"
      ],
      [
        "sto_collection_id"
      ],
      [
        "sto_prefix"
      ]
    ],
    "index": [
      [
        "sto_collection_id"
      ],
      [
        "sto_prefix"
      ]
    ],
    "sort": {
      "_modified_at": -1
    }
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
  segmentsadm: [
    { "id": "_collection", "title": "Collections" },
    { "id": "_field", "title": "Data Fields" },
    { "id": "_view", "title": "Views" },
    { "id": "_action", "title": "Actions" },
    { "id": "_automation", "title": "Automation" },
    { "id": "_user", "title": "Users" },
    { "id": "_permission", "title": "Permissions" },
    { "id": "_token", "title": "API Tokens" },
    { "id": "_firewall", "title": "Firewall" },
    { "id": "_backup", "title": "Backups" },
    { "id": "_log", "title": "Logs" }
  ],
  charts: {
    colorScheme: {
      domain: ['#5AA454', '#A10A28', '#C7B42C', '#AAAAAA']
    }
  },
  themes: [
    { "name": "Dark", "color": "#111111" },
    { "name": "Cobalt", "color": "#0047AB" },
    { "name": "Grün", "color": "#008000" },
    { "name": "Glaucous", "color": "#6082B6" },
    { "name": "Marine", "color": "#3A62FA" },
    { "name": "Iris", "color": "#5D3FD3" },
    { "name": "Sunshine", "color": "#FF5733" },
    { "name": "Rot", "color": "#CC0000" }
  ]
}