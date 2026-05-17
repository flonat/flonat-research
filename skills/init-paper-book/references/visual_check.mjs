#!/usr/bin/env node
/**
 * Visual smoke-test for paper-book chapters via Playwright.
 *
 * Invariants (per chapter):
 *   1. Single H1 in main content
 *   2. No raw mystmd syntax leaking through (`` ```{X} ``, `:::`, `{cite:t}`, `$$`)
 *   3. Math rendering: ≥1 MathJax container if chapter had `$...$` source
 *   4. Callout rendering: source ` ```{X} ` callouts become `<aside>`/`<div class="callout-*">`
 *   5. Figures resolve: every <img> in DOM returns HTTP 200
 *   6. Citation links: every `{cite:t}` in source becomes an <a> in DOM
 *   7. Sidebar chapter list has 8 chapters + references = 9 entries
 *   8. No console errors
 *
 * Usage:
 *   node visual_check.mjs --slug <slug> --base-url http://localhost:8770 --output /tmp/visual-<slug>.json
 *
 * Requires: npx playwright (auto-installs chromium on first run)
 */
import { chromium } from 'playwright';
import { readFile, writeFile } from 'fs/promises';
import { existsSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
import { parseArgs } from 'node:util';

const CHAPTERS = ['intro', 'background', 'setup', 'method', 'results',
                  'limitations', 'extend', 'appendix', 'references'];

const RAW_MYSTMD_PATTERNS = [
    /```\{(important|tip|note|warning|caution|seealso)\}/,
    /:::\s*\{\.callout/,
    /\{cite:[tp]\}`/,
    /\$\$[^$]+\$\$/,
];

async function checkChapter(browser, baseUrl, slug, chapter, vaultDir) {
    const url = `${baseUrl}/book/${slug}/${chapter}`;
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    const consoleErrors = [];
    page.on('console', msg => {
        if (msg.type() === 'error') consoleErrors.push(msg.text());
    });

    const failures = [];
    let sourceText = '';
    // The 'references' chapter is auto-generated from references.bib — no source .md file.
    // Skip source-driven assertions for it.
    if (chapter !== 'references') {
        try {
            sourceText = await readFile(join(vaultDir, `${chapter}.md`), 'utf-8');
        } catch { /* fall through with empty source */ }
    }

    try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 10000 });
        await page.waitForSelector('article, main, .book-chapter', { timeout: 5000 }).catch(() => {});

        const html = await page.content();

        // 1. Single H1
        const h1Count = await page.locator('main h1, article h1').count();
        if (h1Count !== 1) failures.push(`H1 count=${h1Count} (expected 1)`);

        // 2. No raw mystmd in rendered HTML
        for (const pat of RAW_MYSTMD_PATTERNS) {
            const visibleText = await page.locator('main, article').first().innerText().catch(() => '');
            if (pat.test(visibleText)) {
                failures.push(`Raw mystmd leaking: ${pat.source}`);
            }
        }

        // 3. Math rendering (only if source has math)
        if (sourceText.includes('$') && chapter !== 'references') {
            const mathCount = await page.locator('mjx-container, span.MathJax, .katex').count();
            if (mathCount === 0) failures.push('Math source present but no MathJax/KaTeX container in DOM');
        }

        // 4. Callout rendering
        if (sourceText.match(/```\{(important|tip|note|warning|caution|seealso)\}/)) {
            const calloutCount = await page.locator('aside.callout, div.callout, .admonition').count();
            if (calloutCount === 0) failures.push('Callout source present but no .callout/.admonition in DOM');
        }

        // 5. Figures resolve (probe each img src)
        const imgSrcs = await page.locator('main img, article img').evaluateAll(els => els.map(e => e.src));
        for (const src of imgSrcs) {
            try {
                const r = await page.request.get(src);
                if (r.status() !== 200) failures.push(`Image ${src} returned ${r.status()}`);
            } catch (e) {
                failures.push(`Image probe failed for ${src}: ${e.message}`);
            }
        }

        // 6. Citation links: source cites must render as <a>
        const sourceCiteCount = (sourceText.match(/\{cite:[tp]\}`[^`]+`/g) || []).length;
        if (sourceCiteCount > 0 && chapter !== 'references') {
            const linkCount = await page.locator('main a[href*="/paper/"], main a[href*="/references#"], article a[href*="/paper/"], article a[href*="/references#"]').count();
            if (linkCount === 0) failures.push(`Source has ${sourceCiteCount} cites but no /paper/ or /references# links in DOM`);
        }

        // 7. Sidebar chapter list (atlas renders 9 chapter links in an <aside>)
        if (chapter === 'intro') {
            const navItems = await page.locator('aside a').count();
            if (navItems < 9) failures.push(`Sidebar has ${navItems} entries (expected ≥9)`);
        }

        // 8. Console errors
        if (consoleErrors.length > 0) {
            failures.push(`${consoleErrors.length} console error(s): ${consoleErrors.slice(0, 2).join(' | ')}`);
        }
    } catch (e) {
        failures.push(`Page navigation failed: ${e.message}`);
    }

    // Screenshot regardless of pass/fail
    const screenshotPath = `/tmp/init-paper-book-${slug}-${chapter}.png`;
    await page.screenshot({ path: screenshotPath, fullPage: false }).catch(() => {});
    await page.close();

    return { chapter, pass: failures.length === 0, failures, screenshot: screenshotPath };
}

async function main() {
    const { values } = parseArgs({
        options: {
            slug: { type: 'string' },
            'base-url': { type: 'string', default: 'http://localhost:8770' },
            output: { type: 'string' },
        },
    });

    if (!values.slug || !values.output) {
        console.error('Usage: node visual_check.mjs --slug <slug> --base-url <url> --output <path>');
        process.exit(2);
    }

    const vaultDir = join(homedir(), 'Research-Vault', 'books', values.slug);
    if (!existsSync(vaultDir)) {
        console.error(`Vault dir not found: ${vaultDir}`);
        process.exit(2);
    }

    const browser = await chromium.launch({ headless: true });
    const results = {};
    for (const ch of CHAPTERS) {
        results[ch] = await checkChapter(browser, values['base-url'], values.slug, ch, vaultDir);
    }
    await browser.close();

    const failed = Object.values(results).filter(r => !r.pass);
    const summary = {
        verdict: failed.length === 0 ? 'PASS' : 'BLOCK',
        chapters_checked: CHAPTERS.length,
        chapters_failed: failed.length,
        results,
    };

    await writeFile(values.output, JSON.stringify(summary, null, 2));
    console.log(JSON.stringify({
        verdict: summary.verdict,
        chapters_failed: summary.chapters_failed,
        details_at: values.output,
    }, null, 2));

    process.exit(failed.length === 0 ? 0 : 1);
}

main().catch(e => { console.error(e); process.exit(2); });
