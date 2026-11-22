// Render brochure.html to an A4 PDF (and optional page PNGs for review).
// Usage: node tools/build_pdf.js [out.pdf] [--png DIR]
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const root = path.resolve(__dirname, '..');
  const args = process.argv.slice(2);
  const out = path.resolve(args.find((a) => a.endsWith('.pdf')) || path.join(root, 'imak-mixing-agitating-brochure-EN.pdf'));
  const pngIdx = args.indexOf('--png');
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(root, 'brochure.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: out, printBackground: true, preferCSSPageSize: true });
  console.log('PDF:', out);
  if (pngIdx >= 0) {
    const dir = path.resolve(args[pngIdx + 1]);
    require('fs').mkdirSync(dir, { recursive: true });
    await page.setViewportSize({ width: 794, height: 1123 });
    const n = await page.$$eval('.page', (p) => p.length);
    for (let i = 0; i < n; i++) {
      const el = (await page.$$('.page'))[i];
      await el.screenshot({ path: path.join(dir, `p${String(i + 1).padStart(2, '0')}.png`) });
    }
    console.log('PNGs:', dir);
  }
  await browser.close();
})();
