// Render poster.html to a 2160x2700 JPG (and a 1080x1350 copy for quick posting).
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2160, height: 2700 } });
  await p.goto('file://' + path.join(__dirname, 'poster.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForFunction(() => [...document.images].every((i) => i.complete && i.naturalWidth));
  await p.evaluate(() => window.layout());
  await p.waitForTimeout(300);
  const out = path.join(__dirname, 'imak-mk-king-of-heavy-duty.jpg');
  await p.screenshot({ path: out, type: 'jpeg', quality: 94 });
  console.log('wrote', out);
  await b.close();
})();
