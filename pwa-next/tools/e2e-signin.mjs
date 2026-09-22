// Drives the sign-in flow of the interface in a headless browser: opens the sign-in modal, submits the
// credentials, waits for the second-factor form, reads the code from /probe/otp.txt (written by the
// wrapper script from the local database), submits it and expects the dashboard route with the menu.
import { chromium } from "playwright";
import { existsSync, readFileSync, writeFileSync } from "node:fs";

const [url, email, password] = process.argv.slice(2);
const browser = await chromium.launch({ args: ["--no-sandbox"] });
const page = await browser.newPage();
const logs = [];
page.on("console", (m) => { logs.push(`[console.${m.type()}] ${m.text()}`.slice(0, 300)); });
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
