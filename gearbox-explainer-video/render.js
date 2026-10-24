const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const dir = __dirname;
const TL = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json'), 'utf8'));
const mode = process.argv[2] || 'test';
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.addInitScript((tl) => { window.TIMELINE = tl; window.__headless = true; }, TL);
  await page.goto('file://' + path.join(dir, 'animation.html'));
  await page.evaluate(() => window.__ready.catch((e) => "fontfail:" + e)).then((r) => console.log("fonts", r));
  await page.waitForTimeout(300);
  if (mode === 'test') {
    fs.mkdirSync(path.join(dir, 'test'), { recursive: true });
    let acc = 0;
    for (let i = 0; i < TL.scenes.length; i++) {
      for (const f of [0.35, 0.8]) {
        const t = acc + TL.scenes[i].dur * f;
        const b64 = await page.evaluate((t) => { window.__seek(t); return document.getElementById('c').toDataURL('image/png').split(',')[1]; }, t);
        fs.writeFileSync(path.join(dir, 'test', `s${i + 1}_${Math.round(f * 100)}.png`), Buffer.from(b64, 'base64'));
      }
      acc += TL.scenes[i].dur;
    }
  } else {
    const fps = TL.fps, n = Math.ceil(TL.total * fps);
    const fdir = path.join(dir, 'frames'); fs.mkdirSync(fdir, { recursive: true });
    const t0 = Date.now();
    for (let k = 0; k < n; k++) {
      const b64 = await page.evaluate((t) => { window.__seek(t); return document.getElementById('c').toDataURL('image/jpeg', 0.92).split(',')[1]; }, k / fps);
      fs.writeFileSync(path.join(fdir, `f${String(k).padStart(5, '0')}.jpg`), Buffer.from(b64, 'base64'));
      if (k % 300 === 0) console.log('frame', k, '/', n, ((Date.now() - t0) / 1000).toFixed(0) + 's');
    }
    console.log('frames done', n);
  }
  await browser.close();
})();
