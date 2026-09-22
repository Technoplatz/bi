// Drives the sign-in flow of the interface in a headless browser: opens the sign-in modal, submits the
// credentials, waits for the second-factor form, reads the code from /probe/otp.txt (written by the
// wrapper script from the local database), submits it and expects the dashboard route with the menu.
import { chromium } from "playwright";
import { existsSync, readFileSync, writeFileSync } from "node:fs";

const [url, email, password] = process.argv.slice(2);
const browser = await chromium.launch({ args: ["--no-sandbox"] });
const page = await browser.newPage();
const logs = [];
// serialize error objects inside the page before they reach the console, so the text survives
// even when the page navigates away before the message can be inspected
await page.addInitScript(() => {
  const serialize = (v) => {
    if (v instanceof Error) return `${v.name}: ${v.message} @ ${(v.stack || "").split("\n").slice(1, 4).join(" ").trim()}`;
    if (v && typeof v === "object") {
      const picked = {};
      for (const k of ["name", "message", "status", "statusText", "url", "error", "rejection", "code"]) if (k in v) picked[k] = v[k] instanceof Error ? serialize(v[k]) : v[k];
      try { return `${v.constructor?.name ?? "object"} ${JSON.stringify(picked).slice(0, 400)}`; } catch { return String(v); }
    }
    return v;
  };
  const original = console.error;
  console.error = (...args) => original(...args.map(serialize));
  window.addEventListener("unhandledrejection", (e) => original("UNHANDLED", serialize(e.reason)));
});
page.on("console", async (m) => {
  if (!["error", "warning"].includes(m.type())) return;
  // resolve error objects to their message and first stack frames; the production bundle minifies class names
  const parts = [];
  for (const arg of m.args()) {
    try { parts.push(await arg.evaluate((v) => v instanceof Error ? `${v.message} @ ${(v.stack || "").split("\n").slice(1, 3).join(" ").trim()}` : String(v))); }
    catch { parts.push(null); }
  }
  const text = parts.every((x) => x !== null) ? parts.join(" ") : m.text();
  logs.push(`[console.${m.type()}] ${text} (${m.location()?.url?.split("/").pop() ?? ""}:${m.location()?.lineNumber ?? ""})`.slice(0, 700));
});
page.on("pageerror", (e) => logs.push(`[pageerror] ${e.message}`.slice(0, 300)));
page.on("response", (r) => { if (r.url().includes("/api/")) logs.push(`[api ${r.status()}] ${r.request().postData()?.slice(0, 60) ?? ""}`); });

const step = (name, ok) => console.log(`${ok ? "ok  " : "FAIL"} ${name}`);
let failed = false;
try {
  await page.goto(url, { waitUntil: "networkidle" });
  await page.getByText(/Sign in|Einloggen|Giriş/).first().click();
  await page.waitForSelector("app-sign form", { timeout: 10000 });
  step("sign-in modal opened", true);
  await page.locator("app-sign ion-input[formcontrolname=email] input").fill(email);
  await page.locator("app-sign ion-input[formcontrolname=password] input").fill(password);
  await page.locator("app-sign ion-button.sign-button").first().click();
  await page.waitForSelector("app-sign ion-input[formcontrolname=tfac] input", { timeout: 15000 });
  step("password accepted, second factor form shown", true);
  writeFileSync("/probe/otp-requested.txt", String(Date.now()));
  let code = null;
  for (let i = 0; i < 60 && !code; i++) {
    await page.waitForTimeout(500);
    if (existsSync("/probe/otp.txt")) {
      code = readFileSync("/probe/otp.txt", "utf8").trim();
    }
  }
  if (!code) throw new Error("no otp delivered by the wrapper");
  await page.locator("app-sign ion-input[formcontrolname=tfac] input").fill(code);
  await page.locator("app-sign ion-button.sign-button").first().click();
  await page.waitForURL(/\/dashboard/, { timeout: 15000 });
  step("signed in, navigated to /dashboard", true);
  await page.waitForSelector("app-menu", { timeout: 10000 });
  const menu = await page.evaluate(() => [...document.querySelectorAll("app-menu p")].map((p) => p.textContent.trim()).slice(0, 12));
  step(`menu rendered with ${menu.length} entries`, menu.length > 0);
  const meta = await page.evaluate(() => new Promise((res) => {
    const req = indexedDB.open("__bidb");
    req.onsuccess = () => { const db = req.result; const tx = db.transaction(db.objectStoreNames[0]); const g = tx.objectStore(db.objectStoreNames[0]).get("LSUSERMETA"); g.onsuccess = () => res(g.result ? Object.keys(g.result) : null); g.onerror = () => res(null); };
    req.onerror = () => res(null);
  }));
  step(`session stored in IndexedDB (${meta ? meta.join(",") : "none"})`, !!meta && meta.includes("token"));
  // let the dashboard finish its own requests before the tour reloads it; a fetch aborted by the
  // navigation is otherwise reported as an HttpErrorResponse with status 0
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  // tour: every ported route must render content without page errors or console errors
  const firstCollection = await page.evaluate(() => [...document.querySelectorAll("app-menu p")].map((p) => p.textContent.trim())[0]);
  const collections = await page.evaluate(() => fetch("/assets/env.js").then(() => null));
  const routes = ["/dashboard", "/admin/_collection", "/admin/_query", "/admin/_job", "/admin/_user", "/settings/account", "/settings/profile-settings", "/404"];
  const colId = await page.evaluate(async () => {
    const meta = await new Promise((res) => { const r = indexedDB.open("__bidb"); r.onsuccess = () => { const db = r.result; const g = db.transaction(db.objectStoreNames[0]).objectStore(db.objectStoreNames[0]).get("LSUSERMETA"); g.onsuccess = () => res(g.result); g.onerror = () => res(null); }; r.onerror = () => res(null); });
    const env = window.env || {};
    const r = await fetch(env.API_URL + "/crud", { method: "POST", headers: { "Content-Type": "application/json", Authorization: "Bearer " + meta.token, "X-Api-Key": meta.api_key }, body: JSON.stringify({ op: "collections", collection: "_collection" }) });
    const j = await r.json(); return j?.data?.[0]?.col_id ?? null;
  });
  if (colId) routes.splice(1, 0, `/collection/${colId}`);
  for (const route of routes) {
    const before = logs.length;
    await page.goto(new URL(route, url).href, { waitUntil: "networkidle" });
    await page.waitForTimeout(2500);
    const info = await page.evaluate(() => {
      const content = document.querySelector("ion-router-outlet ion-content, ion-router-outlet");
      return { text: (content?.innerText || "").replace(/\s+/g, " ").trim().slice(0, 70), spinners: document.querySelectorAll("ion-spinner").length, url: location.pathname };
    });
    const errors = logs.slice(before).filter((l) => l.startsWith("[pageerror]") || l.startsWith("[console.error]"));
    step(`${route} -> ${info.url} "${info.text}"${errors.length ? " ERRORS: " + errors.join(" | ") : ""}`, errors.length === 0 && info.text.length > 0);
    if (errors.length) failed = true;
  }
  // schema editor: the text view must show the schema with CodeMirror's own layout applied
  if (colId) {
    const before = logs.length;
    await page.goto(new URL(`/collection/${colId}`, url).href, { waitUntil: "networkidle" });
    await page.waitForTimeout(1500);
    await page.getByText(/Edit Schema|Schema bearbeiten|Şema/i).first().click();
    await page.waitForSelector("json-editor .cm-content", { timeout: 10000 }).catch(() => null);
    await page.waitForTimeout(1500);
    const schema = await page.evaluate(() => {
      const content = document.querySelector("json-editor .cm-content");
      const scroller = document.querySelector("json-editor .cm-scroller");
      const host = document.querySelector("json-editor");
      return { text: content?.textContent.slice(0, 40) ?? "", flex: scroller ? getComputedStyle(scroller).display : "", height: host ? Math.round(host.getBoundingClientRect().height) : 0, top: content ? Math.round(content.getBoundingClientRect().top - scroller.getBoundingClientRect().top) : -1 };
    });
    const errors = logs.slice(before).filter((l) => l.startsWith("[pageerror]") || l.startsWith("[console.error]"));
    const ok = schema.text.includes("properties") && schema.flex === "flex" && schema.height > 300 && schema.height < 2000 && schema.top === 0 && errors.length === 0;
    step(`schema editor on ${colId} shows the schema (${JSON.stringify(schema)})${errors.length ? " ERRORS: " + errors.join(" | ") : ""}`, ok);
    if (!ok) failed = true;
  }
  // record editor modal: open "new record" on a data collection and expect the crud form
  if (colId) {
    const before = logs.length;
    await page.goto(new URL(`/collection/${colId}`, url).href, { waitUntil: "networkidle" });
    await page.waitForTimeout(2000);
    await page.getByText(/Neuer Datensatz|New Record|Yeni Kayıt/).first().click();
    await page.waitForSelector("app-crud form, app-crud ion-content", { timeout: 10000 });
    const crud = await page.evaluate(() => ({ inputs: document.querySelectorAll("app-crud ion-input, app-crud ion-select, app-crud ion-textarea, app-crud ion-checkbox").length, kov: document.querySelectorAll("app-crud app-kov").length }));
    const errors = logs.slice(before).filter((l) => l.startsWith("[pageerror]") || l.startsWith("[console.error]"));
    step(`crud modal opened for ${colId} with ${crud.inputs} inputs${errors.length ? " ERRORS: " + errors.join(" | ") : ""}`, crud.inputs > 0 && errors.length === 0);
    if (errors.length) failed = true;
    await page.evaluate(() => document.querySelector("ion-modal")?.dismiss());
    await page.waitForTimeout(800);
  }
  await page.getByText(/Sign Out|Abmelden|Çıkış/).first().click();
  await page.waitForURL((u) => !u.pathname.startsWith("/dashboard"), { timeout: 10000 });
  step("signed out", true);
} catch (e) {
  failed = true;
  step(e.message.split("\n")[0], false);
  const dom = await page.evaluate(() => ({
    url: location.href,
    modal: document.querySelector("ion-modal")?.outerHTML.slice(0, 200) ?? null,
    sign: document.querySelector("app-sign")?.outerHTML.slice(0, 200) ?? null,
    signinTexts: [...document.querySelectorAll("ion-button")].map((b) => b.textContent.trim()),
    body: document.body.innerText.slice(0, 300)
  }));
  console.log(JSON.stringify(dom, null, 1));
}
console.log(logs.join("\n"));
await browser.close();
process.exit(failed ? 1 : 0);
