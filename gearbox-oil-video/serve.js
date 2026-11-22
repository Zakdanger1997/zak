// Tiny static file server for the scene page (ES modules cannot load from file://).
const http = require('http'), fs = require('fs'), path = require('path');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json',
  '.glb': 'model/gltf-binary', '.woff2': 'font/woff2', '.png': 'image/png', '.jpg': 'image/jpeg' };
module.exports = function serve(root, port) {
  return new Promise(res => {
    const srv = http.createServer((req, rsp) => {
      const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
      fs.readFile(p, (err, data) => {
        if (err) { rsp.writeHead(404); rsp.end(); return; }
        rsp.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
        rsp.end(data);
      });
    }).listen(port, () => res(srv));
  });
};
