// Print a rendered Reveal.js deck (HTML) to PDF with the installed Chrome.
//
// Usage: node print-pdf.mjs <deck.html> <out.pdf> [width height]
//   CHROME=/path/to/chrome overrides the browser (default: macOS Google Chrome).
//
// Adapted from the PB130 handout builder (2026-10). Why not
// `chrome --headless --print-to-pdf`: that fires on the load event, and Reveal
// builds its print pages (.pdf-page) afterwards, so many exports came out blank.
// Here we wait until Reveal reports ready AND every slide has its print page.

import puppeteer from "puppeteer-core";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import { statSync } from "node:fs";

const [htmlArg, outArg, widthArg, heightArg] = process.argv.slice(2);
if (!htmlArg || !outArg) {
  console.error("usage: node print-pdf.mjs <deck.html> <out.pdf> [width height]");
  process.exit(2);
}

const chrome =
  process.env.CHROME ||
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const url = pathToFileURL(resolve(htmlArg)).href + "?print-pdf";
const out = resolve(outArg);
const width = Number(widthArg) || 1280;
const height = Number(heightArg) || 720;

const browser = await puppeteer.launch({
  executablePath: chrome,
  headless: true,
  args: ["--allow-file-access-from-files"],
});

try {
  const page = await browser.newPage();
  page.on("pageerror", (e) => console.error("page error:", e.message));
  await page.setViewport({ width, height });
  await page.goto(url, { waitUntil: "networkidle0", timeout: 120000 });

  // Slide count comes from Reveal itself: counting <section> elements before
  // Reveal initialises gives 0 and would make this wait vacuous.
  await page.waitForFunction(
    () =>
      window.Reveal &&
      window.Reveal.isReady() &&
      window.Reveal.getTotalSlides() > 0 &&
      document.querySelectorAll(".pdf-page").length >=
        window.Reveal.getTotalSlides(),
    { timeout: 90000 }
  );
  await page.evaluate(() => document.fonts.ready);
  const slides = await page.evaluate(() => window.Reveal.getTotalSlides());
  const pages = await page.evaluate(
    () => document.querySelectorAll(".pdf-page").length
  );
  await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true });

  const kb = Math.round(statSync(out).size / 1024);
  console.log(`${slides} slides, ${pages} print pages, ${kb} KB -> ${out}`);
} finally {
  await browser.close();
}
