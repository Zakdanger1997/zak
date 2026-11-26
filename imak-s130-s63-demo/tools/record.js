// Record demo.html frame by frame -> MP4 (H.264, 30 fps), optional audio track. Same pattern as stat-twins/tools/compose.js.
// Usage: node tools/record.js video/out.mp4 [--audio audio/mix.wav] [--stills 3,8,15]
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process');
const ROOT = path.join(__dirname, '..');
const A = process.argv.slice(2), out = A[0];
const audio = A.includes('--audio') ? A[A.indexOf('--audio') + 1] : null;
const stills = A.includes('--stills') ? A[A.indexOf('--stills') + 1].split(',').map(Number) : null;
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.woff2': 'font/woff2', '.stl': 'application/octet-stream' };
(async () => {
  const srv = http.createServer((q, r) => {
    const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
    if (!f.startsWith(ROOT) || !fs.existsSync(f)) { r.writeHead(404); return r.end(); }
    r.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r);
  }).listen(0);
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', (e) => console.error('page error:', e.message));
  await page.goto(`http://localhost:${srv.address().port}/demo.html`);
  await page.waitForFunction(() => window.ready && window.setup);
  await page.evaluate(() => document.fonts.ready);
  const total = await page.evaluate(() => window.setup());
  const fps = 30, n = Math.round(total * fps);
  let ff = null;
  if (!stills) {
    const args = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-'];
    if (audio) args.push('-i', audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k');
    args.push('-t', total.toFixed(3), '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out);
    ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
  }
  const want = stills ? stills.map((s) => Math.round(s * fps)) : null;
  for (let i = 0; i < n; i++) {
    if (want && !want.includes(i)) continue;
    await page.evaluate((t) => window.renderAt(t), i / fps);
    if (ff) { const buf = await page.screenshot({ type: 'jpeg', quality: 92 }); if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r)); }
    else await page.screenshot({ path: `/tmp/claude-0/demo_${(i / fps).toFixed(1)}.jpg`, type: 'jpeg', quality: 85 });
    if (i % 150 === 0) console.log('frame', i, '/', n);
  }
  if (ff) { ff.stdin.end(); await new Promise((r) => ff.on('close', r)); console.log('wrote', out, total.toFixed(1), 's'); }
  await browser.close(); srv.close();
})();
