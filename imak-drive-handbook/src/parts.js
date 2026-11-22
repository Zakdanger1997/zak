// Geometry and materials for the pop-up mechanisms.
// Everything is drawn as a "technical drawing come to life": warm white matte parts with
// ink outlines, i.Mak red for the part that matters. Units: centimetres (the book is 42 x 28 cm).
import * as THREE from 'three';

export const INK = 0x1f2a36;
export const RED = 0xcc0605;      // RAL 3020 traffic red, sRGB #CC0605
export const BLUE = 0x2f7fd8;

const matCache = {};
export function mat(kind) {
  if (matCache[kind]) return matCache[kind];
  const m = {
    paper: () => new THREE.MeshStandardMaterial({ color: 0xf3efe6, roughness: 0.92, metalness: 0 }),
    part: () => new THREE.MeshStandardMaterial({ color: 0xf6f3ec, roughness: 0.78, metalness: 0 }),
    shade: () => new THREE.MeshStandardMaterial({ color: 0xd9d4ca, roughness: 0.85, metalness: 0 }),
    red: () => new THREE.MeshStandardMaterial({ color: RED, roughness: 0.55, metalness: 0 }),
    steel: () => new THREE.MeshStandardMaterial({ color: 0xc9ced4, roughness: 0.32, metalness: 0.85 }),
    blue: () => new THREE.MeshStandardMaterial({ color: BLUE, roughness: 0.4, emissive: 0x1a5fb8, emissiveIntensity: 0.6 }),
    rope: () => new THREE.MeshStandardMaterial({ color: 0x8a7a62, roughness: 0.9 }),
  }[kind]();
  matCache[kind] = m;
  return m;
}
const lineMat = new THREE.LineBasicMaterial({ color: INK, transparent: true, opacity: 0.85 });

/** Mesh + ink outline. */
export function inked(geo, material, threshold = 28) {
  const g = new THREE.Group();
  const m = new THREE.Mesh(geo, material);
  m.castShadow = true;
  m.receiveShadow = true;
  g.add(m);
  const e = new THREE.LineSegments(new THREE.EdgesGeometry(geo, threshold), lineMat);
  g.add(e);
  g.userData.mesh = m;
  return g;
}

const inv = (a) => Math.tan(a) - a;
const PA = (20 * Math.PI) / 180;

/** Outline points of an involute spur gear (external), tooth 0 centred on angle 0. */
export function gearOutline(z, m, steps = 5) {
  const r = (m * z) / 2, rb = r * Math.cos(PA), ra = r + m, rf = r - 1.25 * m;
  const pts = [];
  const half = (R) => {
    const Rc = Math.max(R, rb);
    return Math.PI / (2 * z) + inv(PA) - inv(Math.acos(rb / Rc));
  };
  const r0 = Math.max(rf, rb * 0.999);
  for (let k = 0; k < z; k++) {
    const c = (2 * Math.PI * k) / z;
    // rising flank (angle c - half), tip, falling flank (c + half), then root to the next tooth
    const flank = [];
    for (let i = 0; i <= steps; i++) {
      const R = r0 + ((ra - r0) * i) / steps;
      flank.push([R, half(R)]);
    }
    const start = c - half(r0) - 0.0001;
    pts.push([rf * Math.cos(start), rf * Math.sin(start)]);
    for (const [R, h] of flank) pts.push([R * Math.cos(c - h), R * Math.sin(c - h)]);
    for (let i = flank.length - 1; i >= 0; i--) {
      const [R, h] = flank[i];
      pts.push([R * Math.cos(c + h), R * Math.sin(c + h)]);
    }
    const end = c + half(r0) + 0.0001;
    pts.push([rf * Math.cos(end), rf * Math.sin(end)]);
    const next = c + (2 * Math.PI) / z - half(r0);
    const mid = (end + next) / 2;
    pts.push([rf * Math.cos(mid), rf * Math.sin(mid)]);
  }
  return pts;
}

function holePath(radius, n = 40) {
  const p = new THREE.Path();
  p.absarc(0, 0, radius, 0, Math.PI * 2, true);
  return p;
}

/** Extruded spur gear lying in the XZ plane (axis = Y), thickness t, bore radius. */
export function gearGeo(z, m, t, bore = 0, spokes = 0, upright = false) {
  const s = new THREE.Shape();
  gearOutline(z, m).forEach(([x, y], i) => (i ? s.lineTo(x, y) : s.moveTo(x, y)));
  s.closePath();
  if (bore) s.holes.push(holePath(bore));
  const r = (m * z) / 2;
  if (spokes && r > bore * 3.2) {
    // lightening holes between hub and rim
    const rin = bore * 1.9, rout = r - 2.6 * m;
    for (let k = 0; k < spokes; k++) {
      const a0 = (2 * Math.PI * k) / spokes + 0.22, a1 = (2 * Math.PI * (k + 1)) / spokes - 0.22;
      const h = new THREE.Path();
      h.moveTo(rin * Math.cos(a0), rin * Math.sin(a0));
      h.absarc(0, 0, rout, a0, a1, false);
      h.absarc(0, 0, rin, a1, a0, true);
      s.holes.push(h);
    }
  }
  const g = new THREE.ExtrudeGeometry(s, { depth: t, bevelEnabled: true, bevelSize: m * 0.06, bevelThickness: m * 0.06, bevelSegments: 1, curveSegments: 18 });
  g.translate(0, 0, -t / 2);
  if (!upright) g.rotateX(-Math.PI / 2);   // upright: gear in the XY plane, spins about Z
  return g;
}

/** Internal ring gear (tooth material at angle 0), outer radius ro. */
export function ringGeo(z, m, t, ro) {
  const s = new THREE.Shape();
  s.absarc(0, 0, ro, 0, Math.PI * 2, false);
  // the tooth spaces of an internal gear have the shape of external teeth of the same gear
  const r = (m * z) / 2;
  const h = new THREE.Path();
  const pts = gearOutline(z, m).map(([x, y]) => {
    const R = Math.hypot(x, y), a = Math.atan2(y, x) + Math.PI / z;   // spaces between ring teeth
    const Ri = 2 * r - R + 0.25 * m;                                   // mirror tip/root about the pitch circle
    return [Ri * Math.cos(a), Ri * Math.sin(a)];
  });
  pts.reverse().forEach(([x, y], i) => (i ? h.lineTo(x, y) : h.moveTo(x, y)));
  h.closePath();
  s.holes.push(h);
  const g = new THREE.ExtrudeGeometry(s, { depth: t, bevelEnabled: false, curveSegments: 48 });
  g.translate(0, 0, -t / 2);
  g.rotateX(-Math.PI / 2);
  return g;
}

/** Spur gear meshing phase: rotation of a gear (zp teeth) whose centre sits at world angle phi
 *  from a driving gear (zs teeth) turned to angle ths. Works for any pair of external gears. */
export function meshAngle(phi, ths, zs, zp) {
  return phi + Math.PI + ((phi - ths) * zs - Math.PI) / zp;
}

export function cyl(r, h, mtl = mat('part'), seg = 32, th = 28) {
  const g = new THREE.CylinderGeometry(r, r, h, seg);
  g.translate(0, h / 2, 0);
  return inked(g, mtl, th);
}

export function box(w, h, d, mtl = mat('part')) {
  const g = new THREE.BoxGeometry(w, h, d);
  g.translate(0, h / 2, 0);
  return inked(g, mtl);
}

/** Flat curved arrow (torque / rotation sign) in the XZ plane. */
export function arcArrow(radius, a0, a1, width, color = RED) {
  const s = new THREE.Shape();
  const n = 32, ri = radius - width / 2, ro = radius + width / 2;
  for (let i = 0; i <= n; i++) {
    const a = a0 + ((a1 - a0) * i) / n;
    i ? s.lineTo(ro * Math.cos(a), ro * Math.sin(a)) : s.moveTo(ro * Math.cos(a), ro * Math.sin(a));
  }
  const dir = Math.sign(a1 - a0), ah = width * 1.9, tip = a1 + dir * (ah / radius);
  s.lineTo((radius + ah * 0.75) * Math.cos(a1), (radius + ah * 0.75) * Math.sin(a1));
  s.lineTo(radius * Math.cos(tip), radius * Math.sin(tip));
  s.lineTo((radius - ah * 0.75) * Math.cos(a1), (radius - ah * 0.75) * Math.sin(a1));
  for (let i = n; i >= 0; i--) {
    const a = a0 + ((a1 - a0) * i) / n;
    s.lineTo(ri * Math.cos(a), ri * Math.sin(a));
  }
  const g = new THREE.ShapeGeometry(s);
  g.rotateX(-Math.PI / 2);
  const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.9, side: THREE.DoubleSide, depthWrite: false }));
  return m;
}

/** Small numbered callout that floats in 3D and always faces the camera (sprite). */
export function badge(text, color = INK) {
  const c = document.createElement('canvas');
  c.width = c.height = 128;
  const x = c.getContext('2d');
  x.fillStyle = '#f6f2e9';
  x.strokeStyle = typeof color === 'number' ? '#' + color.toString(16).padStart(6, '0') : color;
  x.lineWidth = 7;
  x.beginPath();
  x.arc(64, 64, 52, 0, Math.PI * 2);
  x.fill();
  x.stroke();
  x.fillStyle = x.strokeStyle;
  x.font = '600 66px "Barlow Condensed"';
  x.textAlign = 'center';
  x.textBaseline = 'middle';
  x.fillText(text, 64, 68);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: t, depthTest: false, transparent: true }));
  s.scale.set(1.5, 1.5, 1);
  s.renderOrder = 10;
  return s;
}

/** Dashed ink leader from a badge to a point. */
export function leader(a, b) {
  const g = new THREE.BufferGeometry().setFromPoints([a, b]);
  const l = new THREE.Line(g, new THREE.LineDashedMaterial({ color: INK, dashSize: 0.25, gapSize: 0.18, transparent: true, opacity: 0.7 }));
  l.computeLineDistances();
  return l;
}
