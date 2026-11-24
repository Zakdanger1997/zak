// Record the Anuga FoodTec teaser: compose.html driven frame by frame (Playwright), audio/music.wav muxed in.
//   node tools/compose.js [out.mp4] [--stills 1,4.2,9]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const http = require('http');
const path = require('path');
const fs = require('fs');

const ROOT = path.join(__dirname, '..');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2', '.json': 'application/json' };
const srv = http.createServer((req, res) => {
  const f = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(f, (e, d) => {
    if (e) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' });
    res.end(d);
  });
}).listen(0);

(async () => {
  const a = process.argv.slice(2);
  const stills = a.includes('--stills') ? a[a.indexOf('--stills') + 1].split(',').map(Number) : null;
  const out = stills ? null : a.find((x) => x.endsWith('.mp4')) || path.join(ROOT, 'video', 'imak-anuga-foodtec-2027.mp4');
  const sc = JSON.parse(fs.readFileSync(path.join(ROOT, 'scenes.json')));
  const map = JSON.parse(fs.readFileSync(path.join(ROOT, 'assets', 'map', 'europe_s2.json')));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', (e) => console.log('pageerror', e.message));
  await page.goto(`http://localhost:${srv.address().port}/compose.html`);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(([s, m]) => window.setup(s, m), [sc, map]);
  await page.waitForTimeout(500);
  const fps = sc.fps, n = Math.round(sc.total * fps);
  let ff = null;
  if (out) {
    fs.mkdirSync(path.dirname(out), { recursive: true });
    const audio = path.join(ROOT, 'audio', 'music.wav');
    const args = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-'];
    if (fs.existsSync(audio)) args.push('-i', audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '256k', '-shortest');
    args.push('-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out);
    ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
  }
  const want = stills ? stills.map((s) => Math.round(s * fps)) : null;
  for (let i = 0; i < n; i++) {
    if (want && !want.includes(i)) continue;
    await page.evaluate((t) => window.renderAt(t), i / fps);
    if (ff) {
      const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      if (i % 150 === 0) console.log(`frame ${i}/${n}`);
    } else {
      await page.screenshot({ path: `/tmp/claude-0/anuga/st_${(i / fps).toFixed(1)}.jpg`, type: 'jpeg', quality: 85 });
    }
  }
  if (ff) { ff.stdin.end(); await new Promise((r) => ff.on('close', r)); console.log('wrote', out); }
  await browser.close();
  srv.close();
})();
