// Loads the new interface, waits, and reports console messages, failed requests, router state and DOM markers.
import { chromium } from "playwright";

const url = process.argv[2] || "http://localhost:8100/";
const browser = await chromium.launch({ args: ["--no-sandbox"] });
const page = await browser.newPage();
const logs = [];
page.on("console", (m) => logs.push(`[console.${m.type()}] ${m.text()}`.slice(0, 400)));
page.on("pageerror", (e) => logs.push(`[pageerror] ${e.message}`.slice(0, 400)));
page.on("requestfailed", (r) => logs.push(`[requestfailed] ${r.url()} ${r.failure()?.errorText}`));
page.on("response", (r) => { if (r.status() >= 400) logs.push(`[http ${r.status()}] ${r.url()}`); });
await page.goto(url, { waitUntil: "networkidle" });
await page.waitForTimeout(3000);
const state = await page.evaluate(() => ({
  href: location.href,
  outlet: document.querySelector("ion-router-outlet")?.innerHTML.slice(0, 300) ?? null,
  appHome: !!document.querySelector("app-home"),
  buttons: [...document.querySelectorAll("ion-button")].map((b) => b.textContent.trim()).slice(0, 8),
  langs: [...document.querySelectorAll(".selection-active, .selection-passive")].map((e) => e.textContent.trim()),
  iconsRendered: [...document.querySelectorAll("ion-icon")].filter((i) => i.shadowRoot?.innerHTML.includes("<svg")).length,
  iconsTotal: document.querySelectorAll("ion-icon").length,
}));
console.log(JSON.stringify(state, null, 1));
console.log(logs.join("\n") || "(no console output)");
await browser.close();
