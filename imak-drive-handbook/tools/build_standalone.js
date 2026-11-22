// Build one self-contained HTML file (code, i.Mak model, fonts and logo inlined) that also works
// when opened by double-click (file://), where browsers block ES modules and fetches.
//   node tools/build_standalone.js            -> dist/imak-drive-handbook.html
// Needs esbuild (npm i esbuild).
const fs = require('fs');
const path = require('path');
const esbuild = require('esbuild');

const root = path.join(__dirname, '..');
const rd = (f) => fs.readFileSync(path.join(root, f));
const b64 = (f) => rd(f).toString('base64');

const js = esbuild.buildSync({
  entryPoints: [path.join(root, 'src/main.js')],
  bundle: true, format: 'iife', minify: true, write: false, target: 'es2020',
  alias: { three: path.join(root, 'vendor/three.module.js') },
}).outputFiles[0].text;

let html = rd('index.html').toString();
const logo = 'data:image/png;base64,' + b64('img/logo.png');
html = html.replace(/url\((fonts\/[^)]+\.woff2)\)/g, (_, f) => `url(data:font/woff2;base64,${b64(f)})`);
html = html.replace('src="img/logo.png"', `src="${logo}"`);
html = html.replace(/<script type="importmap">.*?<\/script>\n/s, '');
const assets = `<script>window.HB_ASSETS={logo:${JSON.stringify(logo)},irkm:${JSON.stringify(b64('models/irkm.glb'))}};</script>`;
html = html.replace('<script type="module" src="src/main.js"></script>', () => `${assets}\n<script>${js.replace(/<\/script/g, '<\\/script')}</script>`);
fs.mkdirSync(path.join(root, 'dist'), { recursive: true });
const out = path.join(root, 'dist/imak-drive-handbook.html');
fs.writeFileSync(out, html);
console.log('wrote', out, (html.length / 1e6).toFixed(1), 'MB');
