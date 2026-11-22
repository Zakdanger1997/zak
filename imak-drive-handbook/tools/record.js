// Record the scripted walkthrough frame by frame and encode an H.264 MP4.
//   node tools/record.js out.mp4 [w] [h] [fps]        full video
//   node tools/record.js --stills 2,5.5,12 [w] [h]    PNG stills at those times (for review)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const { serve } = require('./shot.js');

(async () => {
  const a = process.argv.slice(2);
  const stills = a[0] === '--stills' ? a[1].split(',').map(Number) : null;
  const out = stills ? null : a[0] || 'video/drive-handbook-4x5.mp4';
  const rest = stills ? a.slice(2) : a.slice(1);
  const [w = 1080, h = 1350, fps = 30] = rest.map(Number);
  const srv = serve(path.join(__dirname, '..')).listen(0);
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  page.on('pageerror', (e) => console.log('pageerror:', e.message));
  await page.goto(`http://localhost:${srv.address().port}/index.html?record=1&lesson=1&view=mech&w=${w}&h=${h}`);
  await page.waitForFunction(() => window.HB_READY, null, { timeout: 90000 });
  const duration = await page.evaluate(async () => {
    const { runDemo } = await import('./src/demo.js');
    window.D = runDemo(window.HB, false);
    return window.D.duration;
  });
  const n = Math.round(duration * fps);
  let ff = null;
  if (out) {
    fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
    ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  }
  const want = stills ? new Set(stills.map((t) => Math.round(t * fps))) : null;
  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    const shoot = !want || want.has(i);
    await page.evaluate(([dt, r]) => { window.D.frame(dt, r); }, [1 / fps, shoot]);
    if (!shoot) continue;
    if (ff) {
      const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    } else {
      await page.screenshot({ path: `/tmp/claude-0/still_${(i / fps).toFixed(1)}.png` });
    }
    if (i % 150 === 0) console.log(`frame ${i}/${n}  ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  }
  if (ff) { ff.stdin.end(); await new Promise((r) => ff.on('close', r)); console.log('wrote', out); }
  await browser.close();
  srv.close();
})();
