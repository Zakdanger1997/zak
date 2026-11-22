// Compose the IRC video: compose.html driven frame by frame (Playwright), audio/mix.wav muxed in.
//   node tools/compose.js [out.mp4] [--stills 1,20,40]
// Uses whatever render frames exist (nearest earlier frame), so it also works mid-render as an animatic.
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
    res.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream', 'Cache-Control': 'max-age=3600' });
    res.end(d);
  });
}).listen(0);

(async () => {
  const a = process.argv.slice(2);
  const stills = a.includes('--stills') ? a[a.indexOf('--stills') + 1].split(',').map(Number) : null;
  const out = stills ? null : a.find((x) => x.endsWith('.mp4')) || path.join(ROOT, 'video', 'imak-irc-9x16.mp4');
  const tl = JSON.parse(fs.readFileSync(path.join(ROOT, 'timeline.json')));
  const frames = {};
  for (const d of fs.readdirSync(path.join(ROOT, 'render'))) {
    const p = path.join(ROOT, 'render', d);
    if (fs.statSync(p).isDirectory()) frames[d] = fs.readdirSync(p).filter((f) => /^\d{4}\.png$/.test(f)).map((f) => +f.slice(0, 4)).sort((x, y) => x - y);
  }
  // prefer interpolated full-rate sequences (render/<shot>_i) over the raw renders
  const dirs = {};
  for (const k of Object.keys(frames)) if (k.endsWith('_i') && frames[k].length) { const b = k.slice(0, -2); frames[b] = frames[k]; dirs[b] = k; }
  const photos = JSON.parse(fs.readFileSync(path.join(ROOT, 'assets', 'photos.json')));
  let lineup = { w: 3200, h: 1800 };
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', (e) => console.log('pageerror', e.message));
  await page.goto(`http://localhost:${srv.address().port}/compose.html`);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(([t, f, p, l, d]) => window.setup(t, f, p, l, d), [tl, frames, photos, lineup, dirs]);
  const fps = tl.fps, n = Math.round(tl.total * fps);
  let ff = null;
  if (out) {
    fs.mkdirSync(path.dirname(out), { recursive: true });
    ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
      '-i', path.join(ROOT, 'audio', 'mix.wav'), '-map', '0:v', '-map', '1:a',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k',
      '-movflags', '+faststart', '-shortest', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  }
  const want = stills ? stills.map((s) => Math.round(s * fps)) : null;
  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    if (want && !want.includes(i)) continue;
    await page.evaluate((t) => window.renderAt(t), i / fps);
    if (ff) {
      const buf = await page.screenshot({ type: 'jpeg', quality: 94 });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      if (i % 300 === 0) console.log(`frame ${i}/${n} ${((Date.now() - t0) / 1000).toFixed(0)} s`);
    } else {
      await page.screenshot({ path: `/tmp/claude-0/irc/comp_${(i / fps).toFixed(1)}.png` });
    }
  }
  if (ff) { ff.stdin.end(); await new Promise((r) => ff.on('close', r)); console.log('wrote', out); }
  await browser.close();
  srv.close();
})();
