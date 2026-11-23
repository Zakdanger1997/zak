// Record the collage company video: story.html driven frame by frame (Playwright), audio/mix.wav muxed in.
//   node tools/compose.js [out.mp4] [--stills 1,20,40]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const http = require('http');
const path = require('path');
const fs = require('fs');

const ROOT = path.join(__dirname, '..');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2', '.json': 'application/json', '.svg': 'image/svg+xml' };
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
  const out = stills ? null : a.find((x) => x.endsWith('.mp4')) || path.join(ROOT, 'video', 'imak-story-16x9.mp4');
  const tl = JSON.parse(fs.readFileSync(path.join(ROOT, 'timeline.json')));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', (e) => console.log('pageerror', e.message));
  await page.goto(`http://localhost:${srv.address().port}/story.html`);
  await page.evaluate(async (t) => { await window.setup(t); }, tl);
  const fps = tl.fps, n = Math.round(tl.total * fps);
  let ff = null;
  if (out) {
    fs.mkdirSync(path.dirname(out), { recursive: true });
    ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
      '-i', path.join(ROOT, 'audio', 'mix.wav'), '-map', '0:v', '-map', '1:a',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-tune', 'stillimage', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k',
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
      await page.screenshot({ path: `/tmp/claude-0/story_${(i / fps).toFixed(1)}.png` });
    }
  }
  if (ff) { ff.stdin.end(); await new Promise((r) => ff.on('close', r)); console.log('wrote', out); }
  await browser.close();
  srv.close();
})();
