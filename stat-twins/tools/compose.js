// Record one stat-twin short: node tools/compose.js data/story_ronaldo.json video/out.mp4 [--stills 1,5,30]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const http = require('http'); const path = require('path'); const fs = require('fs');
const ROOT = path.join(__dirname, '..');
const types = { '.html': 'text/html', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.woff2': 'font/woff2', '.json': 'application/json' };
const srv = http.createServer((req, res) => {
  const f = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(f, (e, d) => { if (e) { res.writeHead(404); res.end(); return; } res.writeHead(200, { 'Content-Type': types[path.extname(f).toLowerCase()] || 'application/octet-stream' }); res.end(d); });
}).listen(0);
(async () => {
  const a = process.argv.slice(2);
  const story = JSON.parse(fs.readFileSync(path.join(ROOT, a[0])));
  const stills = a.includes('--stills') ? a[a.indexOf('--stills') + 1].split(',').map(Number) : null;
  const out = stills ? null : path.join(ROOT, a[1]);
  const audio = path.join(ROOT, 'audio', (story.audio || 'music.wav'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', (e) => console.log('pageerror', e.message));
  await page.goto(`http://localhost:${srv.address().port}/compose.html`);
  await page.evaluate(() => document.fonts.ready);
  const total = await page.evaluate((s) => window.setup(s), story);
  const fps = 30, n = Math.round(total * fps);
  let ff = null;
  if (out) {
    fs.mkdirSync(path.dirname(out), { recursive: true });
    const args = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-'];
    if (fs.existsSync(audio)) args.push('-i', audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k', '-t', total.toFixed(3)); // not -shortest: it can cut the last ~2 s while x264 still buffers frames
    args.push('-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out);
    ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
  }
  const want = stills ? stills.map((s) => Math.round(s * fps)) : null;
  for (let i = 0; i < n; i++) {
    if (want && !want.includes(i)) continue;
    await page.evaluate((t) => window.renderAt(t), i / fps);
    if (ff) { const buf = await page.screenshot({ type: 'jpeg', quality: 92 }); if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r)); }
    else await page.screenshot({ path: `/tmp/claude-0/st_${(i / fps).toFixed(1)}.jpg`, type: 'jpeg', quality: 85 });
  }
  if (ff) { ff.stdin.end(); await new Promise((r) => ff.on('close', r)); console.log('wrote', out, total.toFixed(1), 's'); }
  await browser.close(); srv.close();
})();
