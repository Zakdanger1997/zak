// i.Mak Drive Handbook – an open book on a drafting mat; each lesson's mechanism pops up from the page.
import * as THREE from 'three';
import { RoomEnvironment } from '../vendor/environments/RoomEnvironment.js';
import { LESSONS, preload } from './lessons.js';
import { PW, PH, drawLeft, drawRight, leftLayout } from './pages.js';
import { badge, leader } from './parts.js';

const Q = new URLSearchParams(location.search);
const RECORD = Q.has('record');
const PAGE_W = 21, PAGE_D = 28, HP = 1.5;         // page size (cm) and paper stack height

/* ---------------------------------------------------------------- renderer */
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: RECORD });
renderer.setPixelRatio(RECORD ? 1 : Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.toneMapping = THREE.NeutralToneMapping;
renderer.toneMappingExposure = 1.0;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1f25);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.35;
const camera = new THREE.PerspectiveCamera(30, 1, 1, 600);

scene.add(new THREE.HemisphereLight(0xfff4e2, 0x20262d, 0.9));
const key = new THREE.DirectionalLight(0xfff1dc, 2.3);
key.position.set(-22, 46, 20);
key.castShadow = true;
key.shadow.mapSize.set(RECORD ? 4096 : 2048, RECORD ? 4096 : 2048);
Object.assign(key.shadow.camera, { left: -30, right: 30, top: 24, bottom: -24, near: 10, far: 110 });
key.shadow.bias = -0.0004;
key.shadow.normalBias = 0.02;
scene.add(key);
const fill = new THREE.DirectionalLight(0xdbe7ff, 0.45);
fill.position.set(30, 20, 30);
scene.add(fill);
const lamp = new THREE.PointLight(0xffd29a, 260, 120, 1.6);
lamp.position.set(26, 30, -26);
scene.add(lamp);

/* --------------------------------------------------------------- the desk */
function deskTexture() {
  const c = document.createElement('canvas');
  c.width = c.height = 1024;
  const x = c.getContext('2d');
  x.fillStyle = '#262d34';
  x.fillRect(0, 0, 1024, 1024);
  const img = x.getImageData(0, 0, 1024, 1024), d = img.data;
  for (let i = 0; i < d.length; i += 4) { const n = (Math.random() - 0.5) * 10; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
  x.putImageData(img, 0, 0);
  for (let i = 0; i <= 20; i++) {
    const v = (i / 20) * 1024;
    x.strokeStyle = i % 5 === 0 ? 'rgba(170,200,220,0.16)' : 'rgba(170,200,220,0.07)';
    x.lineWidth = i % 5 === 0 ? 2 : 1;
    x.beginPath(); x.moveTo(v, 0); x.lineTo(v, 1024); x.stroke();
    x.beginPath(); x.moveTo(0, v); x.lineTo(1024, v); x.stroke();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(12, 12);
  t.anisotropy = 8;
  return t;
}
const desk = new THREE.Mesh(new THREE.PlaneGeometry(240, 240), new THREE.MeshStandardMaterial({ map: deskTexture(), roughness: 0.9 }));
desk.rotation.x = -Math.PI / 2;
desk.receiveShadow = true;
scene.add(desk);

// steel rule and pencil beside the book
{
  const rc = document.createElement('canvas');
  rc.width = 64; rc.height = 1024;
  const x = rc.getContext('2d');
  x.fillStyle = '#c3c8cd'; x.fillRect(0, 0, 64, 1024);
  x.fillStyle = '#2a2f35';
  for (let i = 0; i <= 320; i++) {
    const y = 12 + i * 3.125, w = i % 10 === 0 ? 30 : i % 5 === 0 ? 20 : 11;
    x.fillRect(0, y, w, 1.2);
  }
  const rt = new THREE.CanvasTexture(rc);
  rt.colorSpace = THREE.SRGBColorSpace;
  const rule = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.08, 33), [
    new THREE.MeshStandardMaterial({ color: 0xb8bdc2, metalness: 0.9, roughness: 0.3 }),
    new THREE.MeshStandardMaterial({ color: 0xb8bdc2, metalness: 0.9, roughness: 0.3 }),
    new THREE.MeshStandardMaterial({ map: rt, metalness: 0.7, roughness: 0.35 }),
    new THREE.MeshStandardMaterial({ color: 0xb8bdc2 }),
    new THREE.MeshStandardMaterial({ color: 0xb8bdc2 }),
    new THREE.MeshStandardMaterial({ color: 0xb8bdc2 }),
  ]);
  rule.position.set(26.5, 0.04, 1);
  rule.rotation.y = -0.06;
  rule.castShadow = rule.receiveShadow = true;
  scene.add(rule);
  const pencil = new THREE.Group();
  const body = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, 15, 6), new THREE.MeshStandardMaterial({ color: 0xcc0605, roughness: 0.5 }));
  pencil.add(body);
  const wood = new THREE.Mesh(new THREE.ConeGeometry(0.42, 1.6, 6), new THREE.MeshStandardMaterial({ color: 0xe2c49a, roughness: 0.8 }));
  wood.position.y = 8.3;
  pencil.add(wood);
  const lead = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.45, 6), new THREE.MeshStandardMaterial({ color: 0x222222 }));
  lead.position.y = 9.1;
  pencil.add(lead);
  pencil.rotation.set(Math.PI / 2, 0, -1.25);
  pencil.position.set(-12, 0.42, 19.5);
  pencil.traverse((o) => (o.castShadow = true));
  scene.add(pencil);
}

/* --------------------------------------------------------------- the book */
const book = new THREE.Group();
scene.add(book);
const cover = new THREE.Mesh(new THREE.BoxGeometry(2 * PAGE_W + 1.6, 0.3, PAGE_D + 1.2), new THREE.MeshStandardMaterial({ color: 0x8f100d, roughness: 0.75 }));
cover.position.y = 0.15;
cover.castShadow = cover.receiveShadow = true;
book.add(cover);
function edgeTexture() {
  const c = document.createElement('canvas');
  c.width = 16; c.height = 256;
  const x = c.getContext('2d');
  x.fillStyle = '#efe8d8'; x.fillRect(0, 0, 16, 256);
  for (let y = 0; y < 256; y += 2) { x.fillStyle = `rgba(120,100,70,${0.08 + Math.random() * 0.1})`; x.fillRect(0, y, 16, 1); }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
const edgeMat = new THREE.MeshStandardMaterial({ map: edgeTexture(), roughness: 0.95 });
const dip = (d) => 0.95 * Math.exp(-d / 1.3);     // pages curve down into the spine
const pageY = (d) => HP - dip(d);
for (const s of [-1, 1]) {
  // paper block whose top follows the page curve
  const sh = new THREE.Shape();
  sh.moveTo(0, 0.3);
  for (let i = 0; i <= 40; i++) { const d = (i / 40) * (PAGE_W - 0.15); sh.lineTo(d, pageY(d) - 0.04); }
  sh.lineTo(PAGE_W - 0.15, 0.3);
  const g = new THREE.ExtrudeGeometry(sh, { depth: PAGE_D - 0.3, bevelEnabled: false });
  g.translate(0, 0, -(PAGE_D - 0.3) / 2);
  const blk = new THREE.Mesh(g, edgeMat);
  blk.scale.x = s;
  blk.castShadow = blk.receiveShadow = true;
  book.add(blk);
}

function pageGeometry(side) {
  const g = new THREE.PlaneGeometry(PAGE_W, PAGE_D, 48, 1);
  g.rotateX(-Math.PI / 2);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const lx = p.getX(i) + PAGE_W / 2;            // 0 at the left edge of the plane
    const x = side < 0 ? lx - PAGE_W : lx;        // left page spans -21..0, right 0..21
    p.setX(i, x);
    p.setY(i, pageY(Math.abs(x)));
  }
  g.computeVertexNormals();
  return g;
}
function pageCanvas() {
  const c = document.createElement('canvas');
  c.width = PW; c.height = PH;
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = renderer.capabilities.getMaxAnisotropy();
  return { c, x: c.getContext('2d'), t };
}
const cvL = pageCanvas(), cvR = pageCanvas(), cvFront = pageCanvas(), cvBack = pageCanvas();
const leftPage = new THREE.Mesh(pageGeometry(-1), new THREE.MeshStandardMaterial({ map: cvL.t, roughness: 0.95 }));
const rightPage = new THREE.Mesh(pageGeometry(1), new THREE.MeshStandardMaterial({ map: cvR.t, roughness: 0.95 }));
leftPage.receiveShadow = rightPage.receiveShadow = true;
book.add(leftPage, rightPage);

// the turning page: a strip of columns bent around the spine
const NX = 32;
const flipGeo = new THREE.BufferGeometry();
{
  const pos = new Float32Array((NX + 1) * 2 * 3), uv = new Float32Array((NX + 1) * 2 * 2), idx = [];
  for (let i = 0; i <= NX; i++) for (let j = 0; j < 2; j++) {
    const k = i * 2 + j;
    uv[k * 2] = i / NX; uv[k * 2 + 1] = j;
  }
  for (let i = 0; i < NX; i++) {
    const a = i * 2, b = (i + 1) * 2, c = b + 1, d = a + 1;
    idx.push(a, b, c, a, c, d);
  }
  flipGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  flipGeo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  flipGeo.setIndex(idx);
}
cvBack.t.wrapS = THREE.RepeatWrapping;
cvBack.t.repeat.x = -1;
cvBack.t.offset.x = 1;
const flip = new THREE.Group();
const flipFront = new THREE.Mesh(flipGeo, new THREE.MeshStandardMaterial({ map: cvFront.t, roughness: 0.95, side: THREE.FrontSide }));
const flipBack = new THREE.Mesh(flipGeo, new THREE.MeshStandardMaterial({ map: cvBack.t, roughness: 0.95, side: THREE.BackSide }));
flipFront.castShadow = true;
flip.add(flipFront, flipBack);
flip.visible = false;
book.add(flip);
function bendFlip(theta) {
  const p = flipGeo.attributes.position;
  let X = 0, Y = 0;
  const step = PAGE_W / NX, lag = 0.75 * Math.sin(theta);
  for (let i = 0; i <= NX; i++) {
    const u = i / NX;
    if (i) {
      const a = theta - lag * u * u * (theta < Math.PI / 2 ? 1 : -1) * 0.9;
      X += Math.cos(a) * step;
      Y += Math.sin(a) * step;
    }
    for (let j = 0; j < 2; j++) {
      const k = i * 2 + j;
      p.setXYZ(k, X, HP + 0.04 + Y, j ? -PAGE_D / 2 : PAGE_D / 2);
    }
  }
  p.needsUpdate = true;
  flipGeo.computeVertexNormals();
  flipGeo.computeBoundingSphere();
}

/* -------------------------------------------------------------- the lessons */
const logo = new Image();
logo.src = 'img/logo.png';
const state = LESSONS.map((l) => ({ dial: l.dial ? l.dial.start : 0, dialPos: l.dial ? l.dial.start : 0, pick: null, open: false }));
let cur = 0, mech = null, mechRoot = null, turning = null, popT = 1, badges = [];
const MECH_POS = new THREE.Vector3(PAGE_W / 2 + 0.2, HP - 0.05, -6.0);

function makeMech(i) {
  const l = LESSONS[i];
  const m = l.build();
  m.badgesInfo = m.badges;
  if (l.dial) m.setValue(l.dial.values[state[i].dial]);
  const root = new THREE.Group();
  root.position.copy(MECH_POS);
  const s = l.cover ? 0.95 : 0.86;
  root.userData.s = s;
  root.add(m.group);
  m.group.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  return { m, root };
}
function setBadges(m) {
  badges.forEach((b) => mechRoot.remove(b.sprite, b.line));
  badges = [];
  (m.badges || []).forEach((b) => {
    const sp = badge(String(b.n));
    mechRoot.add(sp);
    badges.push({ sprite: sp, at: b.at, line: null });
  });
}
let lastRight = '';
function redraw(which = 'both') {
  const l = LESSONS[cur];
  if (which !== 'right') { drawLeft(cvL.x, l, state[cur], cur, logo.complete ? logo : null); cvL.t.needsUpdate = true; }
  if (which !== 'left') { drawRight(cvR.x, l, mech, cur, logo.complete ? logo : null, LESSONS); cvR.t.needsUpdate = true; }
}
function show(i) {
  if (mechRoot) book.remove(mechRoot);
  cur = i;
  const { m, root } = makeMech(i);
  mech = m; mechRoot = root;
  book.add(root);
  setBadges(m);
  redraw();
  updateUI();
}

/** Turn to lesson i with a page turn and a pop-up. */
function goTo(i) {
  if (turning || i === cur || i < 0 || i >= LESSONS.length) return;
  const dir = i > cur ? 1 : -1;
  const old = { m: mech, root: mechRoot };
  // new pages into spare canvases
  const { m, root } = makeMech(i);
  const nl = document.createElement('canvas'), nr = document.createElement('canvas');
  nl.width = nr.width = PW; nl.height = nr.height = PH;
  drawLeft(nl.getContext('2d'), LESSONS[i], state[i], i, logo);
  drawRight(nr.getContext('2d'), LESSONS[i], m, i, logo, LESSONS);
  if (dir > 0) {
    cvFront.x.drawImage(cvR.c, 0, 0);          // old right page lifts off
    cvBack.x.drawImage(nl, 0, 0);              // its back is the new left page
    cvR.x.drawImage(nr, 0, 0);                 // new right page is underneath
  } else {
    cvBack.x.drawImage(cvL.c, 0, 0);           // old left page lifts off (back face up)
    cvFront.x.drawImage(nr, 0, 0);
    cvL.x.drawImage(nl, 0, 0);
  }
  cvFront.t.needsUpdate = cvBack.t.needsUpdate = cvR.t.needsUpdate = cvL.t.needsUpdate = true;
  turning = { t: 0, dir, old, next: { m, root, i }, nl, nr, swapped: false };
  flip.visible = true;
  bendFlip(dir > 0 ? 0 : Math.PI);
}
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2);
const backOut = (t) => 1 + 2.2 * (t - 1) ** 3 + 1.2 * (t - 1) ** 2;
const TURN = 1.25;
function stepTurn(dt) {
  if (!turning) return;
  const tr = turning;
  tr.t += dt / TURN;
  const t = Math.min(1, tr.t);
  const th = tr.dir > 0 ? ease(t) * Math.PI : (1 - ease(t)) * Math.PI;
  bendFlip(th);
  // old mechanism folds down quickly, new one pops up once the page has passed
  if (tr.old.root) {
    const k = Math.max(0, 1 - t * 3.2);
    tr.old.root.scale.set(tr.old.root.userData.s, tr.old.root.userData.s * Math.max(0.001, k), tr.old.root.userData.s);
    if (k <= 0 && tr.old.root.parent) book.remove(tr.old.root);
  }
  if (!tr.swapped && t > 0.55) {
    tr.swapped = true;
    cur = tr.next.i; mech = tr.next.m; mechRoot = tr.next.root;
    mechRoot.scale.set(mechRoot.userData.s, 0.001, mechRoot.userData.s);
    book.add(mechRoot);
    setBadges(mech);
    popT = 0;
    updateUI();
  }
  if (tr.t >= 1) {
    if (tr.dir > 0) cvL.x.drawImage(tr.nl, 0, 0); else cvR.x.drawImage(tr.nr, 0, 0);
    cvL.t.needsUpdate = cvR.t.needsUpdate = true;
    flip.visible = false;
    turning = null;
    redraw();
  }
}

/* ------------------------------------------------------------- interaction */
const ray = new THREE.Raycaster();
const ndc = new THREE.Vector2();
let dragging = false;
function pageHit(clientX, clientY) {
  const r = canvas.getBoundingClientRect();
  ndc.set(((clientX - r.left) / r.width) * 2 - 1, -((clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(ndc, camera);
  const h = ray.intersectObject(leftPage)[0];
  if (!h) return null;
  return { x: h.uv.x * PW, y: (1 - h.uv.y) * PH };
}
const inR = (p, r, pad = 10) => p && p.x >= r.x - pad && p.x <= r.x + r.w + pad && p.y >= r.y - pad && p.y <= r.y + r.h + pad;
function dialFromX(px) {
  const l = LESSONS[cur], lay = leftLayout(l), n = l.dial.values.length;
  const f = Math.min(1, Math.max(0, (px - lay.dial.x) / lay.dial.w));
  return Math.round(f * (n - 1));
}
export function setDial(idx, animate = true) {
  const l = LESSONS[cur];
  if (!l.dial) return;
  idx = Math.max(0, Math.min(l.dial.values.length - 1, idx));
  const st = state[cur];
  st.dial = idx;
  if (!animate) st.dialPos = idx;
  mech.setValue(l.dial.values[idx]);
  if (l.id === 'ratio' || l.id === 'planetary') setBadges(mech);
  redraw();
}
export function pick(i) { state[cur].pick = i; redraw('left'); }
export function toggleFlap(open) { const st = state[cur]; st.open = open ?? !st.open; redraw('left'); }

if (!RECORD) {
  canvas.addEventListener('pointerdown', (e) => {
    if (turning) return;
    const l = LESSONS[cur];
    if (l.cover) { goTo(1); return; }
    const p = pageHit(e.clientX, e.clientY);
    if (!p) return;
    const lay = leftLayout(l);
    if (inR(p, lay.dial, 30)) { dragging = true; setDial(dialFromX(p.x)); canvas.setPointerCapture(e.pointerId); return; }
    lay.options.forEach((r, i) => inR(p, r) && pick(i));
    if (inR(p, lay.flap)) toggleFlap();
  });
  canvas.addEventListener('pointermove', (e) => {
    const p = pageHit(e.clientX, e.clientY);
    if (dragging && p) { const i = dialFromX(p.x); if (i !== state[cur].dial) setDial(i); }
    const l = LESSONS[cur];
    let hot = l.cover;
    if (p && !l.cover) { const lay = leftLayout(l); hot = inR(p, lay.dial, 30) || inR(p, lay.flap) || lay.options.some((r) => inR(p, r)); }
    canvas.style.cursor = hot ? 'pointer' : 'default';
  });
  canvas.addEventListener('pointerup', () => (dragging = false));
  addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === 'PageDown') goTo(cur + 1);
    if (e.key === 'ArrowLeft' || e.key === 'PageUp') goTo(cur - 1);
    if (e.key === 'ArrowUp') setDial(state[cur].dial + 1);
    if (e.key === 'ArrowDown') setDial(state[cur].dial - 1);
  });
}

/* ------------------------------------------------------------------- camera */
const VIEWS = {
  book: { target: new THREE.Vector3(0, 1.2, 0.6), width: 50, el: 58, az: 0 },
  left: { target: new THREE.Vector3(-10.5, 1.4, 1.6), width: 26.5, el: 66, az: 0 },
  right: { target: new THREE.Vector3(10.5, 4.0, -2.0), width: 25, el: 50, az: 0 },
  mech: { target: new THREE.Vector3(10.7, 5.0, -5.6), width: 24, el: 42, az: 8 },
  'mech:cover': { target: new THREE.Vector3(10.6, 2.0, -5.8), width: 26, el: 55, az: 0 },
  'mech:ratio': { target: new THREE.Vector3(10.2, 5.0, -5.4), width: 27, el: 26, az: 10 },
  'mech:planetary': { target: new THREE.Vector3(10.6, 1.8, -5.6), width: 23, el: 52, az: 0 },
  'mech:motor': { target: new THREE.Vector3(10.6, 2.6, -5.6), width: 25, el: 50, az: -6 },
  'mech:pump': { target: new THREE.Vector3(10.6, 1.4, -6.4), width: 23, el: 56, az: 0 },
  'mech:real': { target: new THREE.Vector3(10.6, 4.2, -5.8), width: 21, el: 30, az: 0 },
  cover: { target: new THREE.Vector3(0, 1.4, 0.2), width: 48, el: 62, az: 0 },
};
const camState = { target: VIEWS.book.target.clone(), width: 50, el: 58, az: 0 };
let camFrom = null, camTo = null, camT = 1, camDur = 1;
export function view(name, dur = 1.2) {
  camFrom = { ...camState, target: camState.target.clone() };
  camTo = VIEWS[name === 'mech' ? `mech:${LESSONS[cur].id}` : name] || VIEWS[name];
  camT = 0; camDur = dur;
}
function applyCamera() {
  const aspect = camera.aspect, vf = THREE.MathUtils.degToRad(camera.fov);
  const hf = 2 * Math.atan(Math.tan(vf / 2) * aspect);
  const dist = (camState.width / 2) / Math.tan(hf / 2);
  const el = THREE.MathUtils.degToRad(camState.el), az = THREE.MathUtils.degToRad(camState.az);
  const dir = new THREE.Vector3(Math.sin(az) * Math.cos(el), Math.sin(el), Math.cos(az) * Math.cos(el));
  camera.position.copy(camState.target).addScaledVector(dir, dist);
  camera.lookAt(camState.target);
  // in portrait recordings push the scene a little down, under the headline
  const w = renderer.domElement.width, h = renderer.domElement.height;
  if (RECORD && h > w) camera.setViewOffset(w, h, 0, -h * 0.06, w, h);
}
function stepCamera(dt) {
  if (camT < 1 && camTo) {
    camT = Math.min(1, camT + dt / camDur);
    const k = ease(camT);
    camState.target.lerpVectors(camFrom.target, camTo.target, k);
    camState.width = THREE.MathUtils.lerp(camFrom.width, camTo.width, k);
    camState.el = THREE.MathUtils.lerp(camFrom.el, camTo.el, k);
    camState.az = THREE.MathUtils.lerp(camFrom.az, camTo.az, k);
  }
  applyCamera();
}

/** Screen position (px) of a point on the left page given in canvas px – used by the demo cursor. */
export function leftPagePoint(px, py) {
  const x = -PAGE_W + (px / PW) * PAGE_W, z = -PAGE_D / 2 + (py / PH) * PAGE_D;
  const v = new THREE.Vector3(x, pageY(Math.abs(x)), z).project(camera);
  const r = canvas.getBoundingClientRect();
  return { x: (v.x * 0.5 + 0.5) * r.width, y: (-v.y * 0.5 + 0.5) * r.height };
}
export const layoutOf = () => leftLayout(LESSONS[cur]);

/* --------------------------------------------------------------------- loop */
function resize() {
  const w = RECORD ? +Q.get('w') || 1080 : innerWidth, h = RECORD ? +Q.get('h') || 1350 : innerHeight;
  renderer.setSize(w, h, !RECORD);
  if (RECORD) { canvas.style.width = w + 'px'; canvas.style.height = h + 'px'; }
  camera.aspect = w / h;
  // portrait screens: keep the book filling the width
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize);

const tmp = new THREE.Vector3();
let readKey = '';
export function step(dt, render = true) {
  stepTurn(dt);
  if (popT < 1 && mechRoot) {
    popT = Math.min(1, popT + dt / 0.7);
    const s = mechRoot.userData.s;
    mechRoot.scale.set(s, s * Math.max(0.001, backOut(popT)), s);
  }
  // dial knob glides to its value
  const st = state[cur];
  if (LESSONS[cur].dial && Math.abs(st.dialPos - st.dial) > 0.001) {
    st.dialPos += (st.dial - st.dialPos) * Math.min(1, dt * 9);
    if (Math.abs(st.dialPos - st.dial) < 0.01) st.dialPos = st.dial;
    if (!turning) redraw('left');
  }
  if (mech) {
    mech.update(dt);
    const k = mech.readouts().map((r) => r[1]).join('|');
    if (k !== readKey && !turning) { readKey = k; redraw('right'); }
  }
  badges.forEach((b, i) => {
    const at = typeof b.at === 'function' ? b.at() : b.at;
    b.sprite.position.copy(at);
    b.sprite.visible = popT > 0.9;
  });
  stepCamera(dt);
  if (render) renderer.render(scene, camera);
}

/* ---------------------------------------------------------------------- UI */
const ui = document.getElementById('ui');
function updateUI() {
  if (!ui) return;
  ui.querySelectorAll('button[data-i]').forEach((b) => b.classList.toggle('on', +b.dataset.i === cur));
}
if (ui && !RECORD) {
  const tabs = ui.querySelector('.tabs');
  LESSONS.forEach((l, i) => {
    const b = document.createElement('button');
    b.dataset.i = i;
    b.textContent = l.cover ? 'Cover' : `${i}  ${l.title}`;
    b.onclick = () => goTo(i);
    tabs.appendChild(b);
  });
} else if (ui) ui.style.display = 'none';

export const api = { goTo, setDial, pick, toggleFlap, view, step, leftPagePoint, layoutOf, get cur() { return cur; }, get turning() { return !!turning; }, state, LESSONS };
window.HB = api;

async function start() {
  await document.fonts.load('700 40px "Barlow Condensed"');
  await Promise.all(['400 30px Barlow', '500 30px Barlow', '600 30px Barlow', '500 30px "Barlow Condensed"', '600 30px "Barlow Condensed"'].map((f) => document.fonts.load(f)));
  await new Promise((r) => (logo.complete ? r() : (logo.onload = r)));
  await preload();
  resize();
  const startAt = +(Q.get('lesson') || 0);
  show(startAt);
  view(Q.get('view') || (startAt ? 'book' : 'cover'), 0.01);
  if (RECORD) { window.HB_READY = true; return; }
  if (Q.has('demo')) { const { runDemo } = await import('./demo.js'); runDemo(api, true); return; }
  let last = performance.now();
  renderer.setAnimationLoop((now) => {
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    step(dt);
  });
}
start();
