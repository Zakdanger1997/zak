// node render.js test [t1 t2 ...]   -> check frames in test/
// node render.js full [worker nworkers] -> frames piped into ffmpeg, video-only segment(s) in parts/
const { chromium } = require('playwright'); const serve = require('./serve');
const fs = require('fs'); const { spawn } = require('child_process');
const mode = process.argv[2] || 'test';
(async () => {
  const port = 8200 + Math.floor(Math.random() * 500);
  const srv = await serve(__dirname, port);
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 600, height: 1000 } });
  p.on('pageerror', e => console.log('pageerror', e.message));
  p.on('console', m => { if (m.type() === 'error') console.log('console', m.text()); });
  await p.goto(`http://localhost:${port}/scene.html`);
  await p.waitForFunction(() => window.__ready, null, { timeout: 300000 });
  const info = await p.evaluate(() => window.__info);
  console.log('total', info.total.toFixed(2), 'frames', info.frames);
  if (mode === 'test') {
    fs.mkdirSync('test', { recursive: true });
    let times = process.argv.slice(3).map(Number);
    if (!times.length) times = info.scenes.flatMap(([s, d]) => [s + d * 0.35, s + d * 0.85]);
    for (const t of times) {
      const t0 = Date.now(); await p.evaluate(t => window.__seek(t), t);
      const url = await p.evaluate(() => window.__frame(0.9));
      fs.writeFileSync(`test/t${t.toFixed(2).padStart(6, '0')}.jpg`, Buffer.from(url.split(',')[1], 'base64'));
      console.log('t', t.toFixed(2), Date.now() - t0, 'ms');
    }
  } else {
    const wi = +(process.argv[3] || 0), wn = +(process.argv[4] || 1);
    const per = Math.ceil(info.frames / wn), f0 = wi * per, f1 = Math.min(info.frames, f0 + per);
    fs.mkdirSync('parts', { recursive: true });
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(info.fps), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', `parts/part${wi}.mp4`], { stdio: ['pipe', 'inherit', 'inherit'] });
    const st = Date.now();
    for (let f = f0; f < f1; f++) {
      await p.evaluate(t => window.__seek(t), f / info.fps);
      const url = await p.evaluate(() => window.__frame(0.93));
      if (!ff.stdin.write(Buffer.from(url.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
      if ((f - f0) % 60 === 0) console.log(`w${wi} frame ${f}/${f1} ${((Date.now() - st) / 1000 / Math.max(1, f - f0)).toFixed(2)} s/frame`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
    console.log(`w${wi} done`);
  }
  await b.close(); srv.close();
})();
