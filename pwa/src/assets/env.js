(function (window) {
  window["env"] = window["env"] || {};
  window["env"]["TZ"] = "Europe/Berlin";
  window["env"]["API_URL"] = "/api"; // the dev server proxies /api to the local stack (proxy.conf.json)
  window["env"]["COMPANY_NAME"] = "Acme Inc.";
})(this);
