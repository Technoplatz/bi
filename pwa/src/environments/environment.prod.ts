export const environment = {
  production: true,
  appVersion: require("../../package.json").version,
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
    { "id": "_collection", "title": "Collections", "description": "Collections" },
    { "id": "_field", "title": "Data Fields", "description": "Field is the core element of a data collection. Here's where you can manage them." },
    { "id": "_view", "title": "Views", "description": "Views" },
    { "id": "_action", "title": "Actions", "description": "Actions" },
    { "id": "_user", "title": "Users", "description": "Users" },
    { "id": "_permission", "title": "Permissions", "description": "Permissions" },
    { "id": "_token", "title": "Access Tokens", "description": "Access Tokens" },
    { "id": "_firewall", "title": "Firewall", "description": "Firewall" },
    { "id": "_backup", "title": "Backups", "description": "Backups" },
    { "id": "_log", "title": "Log", "description": "Log" }
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
    { "name": "Sunshine", "color": "#FF5733" }
  ]
}