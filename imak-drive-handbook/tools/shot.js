// Screenshot a lesson for review:  node tools/shot.js out.png [lesson] [view] [w] [h] [steps]
const { chromium } = require('playwright');
const path = require('path');
const http = require('http');
const fs = require('fs');

function serve(root) {
  const types = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.woff2': 'font/woff2', '.glb': 'model/gltf-binary', '.json': 'application/json' };
  return http.createServer((req, res) => {
    const f = path.join(root, decodeURIComponent(req.url.split('?')[0]));
    fs.readFile(f, (e, d) => {
      if (e) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' });
      res.end(d);
    });
  });
}
module.exports = { serve };

if (require.main === module) {
  (async () => {
    const [out = '/tmp/hb.png', lesson = '1', view = 'book', w = '1080', h = '1350', steps = '40'] = process.argv.slice(2);
    const srv = serve(path.join(__dirname, '..')).listen(0);
    const port = srv.address().port;
    const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
    const page = await browser.newPage({ viewport: { width: +w, height: +h } });
    page.on('console', (m) => (m.type() === 'error' || m.type() === 'warning') && console.log('console:', m.text()));
    page.on('pageerror', (e) => console.log('pageerror:', e.message));
    await page.goto(`http://localhost:${port}/index.html?record=1&lesson=${lesson}&view=${view}&w=${w}&h=${h}`);
    await page.waitForFunction(() => window.HB_READY, null, { timeout: 60000 });
    const t0 = Date.now();
    await page.evaluate((n) => { for (let i = 0; i < n; i++) window.HB.step(1 / 30, i === n - 1); }, +steps);
    console.log('ms/frame', ((Date.now() - t0) / +steps).toFixed(0));
    await page.screenshot({ path: out });
    await browser.close();
    srv.close();
  })();
}
