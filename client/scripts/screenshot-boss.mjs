// Dev-only visual verification tool — not part of the app or a test suite.
// Logs in through the real UI (JWT lives in-memory only, so we can't fake
// auth via localStorage), navigates to a boss's detail page, optionally
// clicks a tab and any number of buttons by their visible text, then saves
// a screenshot. Reusable for the rest of #19 (placement mode, export button).
//
// Usage:
//   SCREENSHOT_EMAIL=... SCREENSHOT_PASSWORD=... node scripts/screenshot-boss.mjs \
//     <bossId> <outputFile> [--tab "Raid Plan"] [--click "Phase 2"] [--click "..."]
//
// SCREENSHOT_BASE_URL defaults to http://localhost:5173.

import { chromium } from "playwright";

const args = process.argv.slice(2);
const [bossId, outputFile] = args;
let tab = null;
const clicks = [];

for (let i = 2; i < args.length; i++) {
  if (args[i] === "--tab") tab = args[++i];
  else if (args[i] === "--click") clicks.push(args[++i]);
}

if (!bossId || !outputFile) {
  console.error("Usage: node scripts/screenshot-boss.mjs <bossId> <outputFile> [--tab NAME] [--click TEXT]...");
  process.exit(1);
}

const BASE_URL = process.env.SCREENSHOT_BASE_URL || "http://localhost:5173";
const EMAIL = process.env.SCREENSHOT_EMAIL;
const PASSWORD = process.env.SCREENSHOT_PASSWORD;

if (!EMAIL || !PASSWORD) {
  console.error("Set SCREENSHOT_EMAIL and SCREENSHOT_PASSWORD env vars first.");
  process.exit(1);
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

// The JWT lives in memory only (never localStorage — see api/authToken.ts),
// so page.goto() after login would trigger a full reload and wipe it.
// Navigate the rest of the way via client-side <Link> clicks instead.
await page.goto(`${BASE_URL}/login`);
await page.fill('input[type="email"]', EMAIL);
await page.fill('input[type="password"]', PASSWORD);
await page.click('button[type="submit"]');
await page.waitForURL(`${BASE_URL}/`);

await page.click('a[href="/bosses"]');
await page.click(`a[href="/bosses/${bossId}"]`);
await page.waitForSelector("h1");

if (tab) {
  await page.click(`button:has-text("${tab}")`);
}
for (const label of clicks) {
  await page.click(`button:has-text("${label}")`);
  await page.waitForTimeout(200);
}

await page.waitForTimeout(500); // let images/layout settle
await page.screenshot({ path: outputFile });
await browser.close();
console.log(`Saved ${outputFile}`);
