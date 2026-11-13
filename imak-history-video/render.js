// Deterministic renderer: drives window.__seek(t) and captures the canvas.
// Usage: node render.js test   (stills at key beats)
//        node render.js full   (all frames -> frames/)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const dir = __dirname;
const mode = process.argv[2] || 'test';

(async () => {
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1080 }, deviceScaleFactor: 1 });
  await page.addInitScript(() => { window.__headless = true; });
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  await page.goto('file://' + path.join(dir, 'animation.html'));
  await page.evaluate(() => window.__ready);
  await page.waitForTimeout(200);
  const meta = await page.evaluate(() => window.__meta);
  console.log('meta', JSON.stringify(meta), 'errors:', errs.length ? errs : 'none');

  const grab = async (t) => page.evaluate((t) => { window.__seek(t);
    return document.getElementById('c').toDataURL(window.__fmt || 'image/png').split(',')[1]; }, t);

  if (mode === 'test') {
    await page.evaluate(() => { window.__fmt = 'image/png'; });
    fs.mkdirSync(path.join(dir, 'test'), { recursive: true });
    // sample 2 beats inside each scene
    const starts = await page.evaluate(() => { const s=[],SC=window.__meta; return window.__dump ? window.__dump() : null; });
    // just sample evenly + a few key times
    const total = meta.total;
    const times = [];
    // scene-aware sampling: use known starts by stepping
    for (let t = 0.6; t < total; t += 1.4) times.push(+t.toFixed(2));
    times.push(total - 0.2);
    let idx = 0;
    for (const t of times) {
      const b64 = await grab(t);
      fs.writeFileSync(path.join(dir, 'test', `t${String(Math.round(t*100)).padStart(5,'0')}.png`), Buffer.from(b64, 'base64'));
      idx++;
    }
    console.log('wrote', idx, 'stills to test/');
  } else {
    await page.evaluate(() => { window.__fmt = 'image/jpeg'; });
    const fps = meta.fps, n = Math.ceil(meta.total * fps);
    const fdir = path.join(dir, 'frames'); fs.rmSync(fdir, { recursive: true, force: true }); fs.mkdirSync(fdir, { recursive: true });
    const t0 = Date.now();
    for (let k = 0; k < n; k++) {
      const b64 = await page.evaluate((t) => { window.__seek(t);
        return document.getElementById('c').toDataURL('image/jpeg', 0.95).split(',')[1]; }, k / fps);
      fs.writeFileSync(path.join(fdir, `f${String(k).padStart(5, '0')}.jpg`), Buffer.from(b64, 'base64'));
      if (k % 150 === 0) console.log('frame', k, '/', n, ((Date.now()-t0)/1000).toFixed(0)+'s');
    }
    console.log('frames done', n, 'errors:', errs.length ? errs : 'none');
  }
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
