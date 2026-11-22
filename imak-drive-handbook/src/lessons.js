// The five lessons of the i.Mak Drive Handbook.
// Each lesson: printed text for the left page, a dial (discrete values), a predict-then-lift-the-flap
// question, and build() which returns the pop-up mechanism for the right page.
// Every number is either plain physics or taken from the i.Mak catalogue (service factors).
import * as THREE from 'three';
import { GLTFLoader } from '../vendor/loaders/GLTFLoader.js';
import { mat, inked, gearGeo, ringGeo, meshAngle, cyl, box, arcArrow, badge, leader, RED, BLUE, INK } from './parts.js';

const TAU = Math.PI * 2;
const lerp = (a, b, t) => a + (b - a) * t;
const fmt = (v, d = 0) => v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });

/* ------------------------------------------------------------------ 1. ratio */
function buildRatio() {
  // upright gear pair in the XY plane (axes along Z), motor behind, hoist drum in front
  const group = new THREE.Group();
  const M = 0.25, Z1 = 14, CY = 8.8, X1 = -6.6, RD = 1.5, DZ = 2.4;
  const P = 4, N1 = 1450, ETA = 0.98, DRUM_M = 0.10;   // physics uses a 10 cm hoist drum
  const T1 = (9550 * P) / N1;
  const zc = (r, h, m, z0, seg = 32) => {         // cylinder along Z from z0 to z0 + h
    const g = new THREE.CylinderGeometry(r, r, h, seg);
    g.rotateX(Math.PI / 2);
    g.translate(0, 0, z0 + h / 2);
    return inked(g, m, 20);
  };
  const base = box(19.5, 0.6, 9, mat('shade'));
  base.position.set(-0.4, 0, -1);
  group.add(base);
  const plate = box(18.5, CY + 1.4, 0.4, mat('part'));
  plate.position.set(-0.6, 0.6, -1.3);
  group.add(plate);
  const motor = zc(2.3, 5.0, mat('part'), -6.6, 40);
  motor.position.set(X1, CY, 0);
  group.add(motor);
  const foot = box(4.2, CY - 2.3, 4.2, mat('part'));
  foot.position.set(X1, 0.6, -4.1);
  group.add(foot);
  for (let k = 0; k < 12; k++) {
    const a = (k / 12) * TAU;
    const fin = new THREE.BoxGeometry(0.16, 0.5, 4.6);
    fin.translate(0, 2.45, -4.0);
    const f = inked(fin, mat('part'));
    f.rotation.z = a;
    f.position.set(X1, CY, 0);
    group.add(f);
  }
  const pinion = inked(gearGeo(Z1, M, 1.0, 0.35, 0, true), mat('shade'), 20);
  pinion.position.set(X1, CY, 0);
  group.add(pinion);
  const pShaft = zc(0.35, 2.0, mat('steel'), -1.2, 16);
  pShaft.position.set(X1, CY, 0);
  group.add(pShaft);
  const out = new THREE.Group();
  out.position.y = CY;
  group.add(out);
  const drum = new THREE.Group();
  drum.add(zc(RD, 1.6, mat('steel'), DZ - 0.8, 32));
  drum.add(zc(RD * 1.4, 0.16, mat('part'), DZ - 0.95, 32));
  drum.add(zc(RD * 1.4, 0.16, mat('part'), DZ + 0.8, 32));
  drum.add(zc(0.38, 5.0, mat('steel'), -1.4, 16));
  out.add(drum);
  let wheel = null, z2 = 28, theta1 = 0, liftDir = 1, lift = 0;
  const rope = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 1, 8), mat('rope'));
  rope.castShadow = true;
  group.add(rope);
  const load = new THREE.Group();
  const loadBox = box(1, 1, 1, mat('red'));
  load.add(loadBox);
  const hook = cyl(0.14, 0.7, mat('steel'), 8);
  load.add(hook);
  group.add(load);
  const tag = badge('kg', RED);
  tag.scale.set(3.6, 1.8, 1);
  group.add(tag);
  const tagCanvas = tag.material.map.image;
  function drawTag(kg) {
    const c = tagCanvas, x = c.getContext('2d');
    c.width = 256; c.height = 128;
    x.clearRect(0, 0, 256, 128);
    x.fillStyle = '#cc0605';
    roundRect(x, 6, 18, 244, 92, 16); x.fill();
    x.fillStyle = '#fff';
    x.font = '700 64px "Barlow Condensed"';
    x.textAlign = 'center'; x.textBaseline = 'middle';
    x.fillText(`${fmt(kg)} kg`, 128, 66);
    tag.material.map.needsUpdate = true;
  }
  const arrowIn = arcArrow(2.6, 2.4, 0.9, 0.32, INK);
  arrowIn.rotation.x = Math.PI / 2;
  arrowIn.position.set(X1, CY, 0.7);
  group.add(arrowIn);
  const arrowOut = new THREE.Group();
  group.add(arrowOut);
  const ratio = () => z2 / Z1;
  const torque = () => T1 * ratio() * ETA;
  const mass = () => torque() / DRUM_M / 9.81;
  function setValue(z) {
    z2 = z;
    if (wheel) out.remove(wheel);
    wheel = inked(gearGeo(z2, M, 1.0, 0.38, z2 > 30 ? 5 : 0, true), mat('red'), 20);
    out.add(wheel);
    const x2 = X1 + (M * (Z1 + z2)) / 2;
    out.position.x = x2;
    arrowOut.clear();
    const r2 = (M * z2) / 2;
    const w = 0.22 + 0.5 * (ratio() / 4);          // thicker arrow = more torque
    const a = arcArrow(r2 + 1.0, 0.7, 2.3, w, RED);
    a.rotation.x = Math.PI / 2;
    arrowOut.add(a);
    arrowOut.position.set(x2, CY, 0.7);
    drawTag(mass());
    const s = 1.2 + 1.4 * Math.cbrt(mass() / 105);
    loadBox.scale.set(s, s, s);
    hook.position.y = s;
    lift = 0;
    liftDir = 1;
  }
  function update(dt) {
    // pinion clockwise (seen from the front) -> wheel anticlockwise -> right side of the drum winds up
    const w1 = -0.55 * TAU * liftDir;
    theta1 += w1 * dt;
    pinion.rotation.z = theta1;
    const th2 = meshAngle(0, theta1, Z1, z2);
    if (wheel) wheel.rotation.z = th2;
    drum.rotation.z = th2;
    lift += ((0.55 * TAU) / ratio()) * RD * dt * liftDir;
    const top = 3.2;
    if (lift > top) { lift = top; liftDir = -1; }
    if (lift < 0) { lift = 0; liftDir = 1; }
    const xr = out.position.x + RD, s = loadBox.scale.y;
    load.position.set(xr, 0.6 + lift, DZ);
    const yTop = CY, yBot = 0.6 + lift + s + 0.7;
    rope.position.set(xr, (yTop + yBot) / 2, DZ);
    rope.scale.y = Math.max(0.01, yTop - yBot);
    tag.position.set(xr + s * 0.5 + 2.3, 0.6 + lift + s * 0.55, DZ);
  }
  setValue(28);
  return {
    group, setValue, update,
    readouts: () => [
      ['Ratio  i = Z₂ / Z₁', `${fmt(ratio(), ratio() % 1 ? 1 : 0)} : 1`],
      ['Output speed', `${fmt(N1 / ratio())} rpm`],
      ['Output torque', `${fmt(torque())} Nm`],
      ['Load on a 10 cm drum', `${fmt(mass())} kg`],
    ],
    badges: [
      { n: 1, at: new THREE.Vector3(X1 - 1.2, CY + 3.4, -4.5), label: 'Motor 4 kW, 1450 rpm' },
      { n: 2, at: new THREE.Vector3(X1 - 2.6, CY - 1.4, 0.8), label: 'Pinion, 14 teeth' },
      { n: 3, at: () => new THREE.Vector3(out.position.x, CY + (M * z2) / 2 + 1.3, 0.6), label: 'Wheel – set by the dial' },
      { n: 4, at: () => new THREE.Vector3(out.position.x + RD - 2.2, 1.8 + lift, DZ + 1.2), label: 'Load' },
    ],
  };
}

/* -------------------------------------------------------------- 2. planetary */
function buildPlanetary() {
  const group = new THREE.Group();
  const M = 0.2, ZR = 72, T = 0.9, H = 1.4;
  const base = cyl(8.9, 0.5, mat('shade'), 64, 20);
  group.add(base);
  const ring = inked(ringGeo(ZR, M, T, 8.3), mat('part'), 20);
  ring.position.y = H;
  group.add(ring);
  const posts = [];
  for (let k = 0; k < 4; k++) {
    const p = cyl(0.35, H - 0.4, mat('part'), 12);
    const a = (k / 4) * TAU + 0.4;
    p.position.set(Math.cos(a) * 7.9, 0.5, Math.sin(a) * 7.9);
    group.add(p);
    posts.push(p);
  }
  const moving = new THREE.Group();
  moving.position.y = H;
  group.add(moving);
  const sunShaft = cyl(0.4, 3.0, mat('steel'), 16);
  let zs = 18, zp = 27, sun, planets = [], carrier, ths = 0;
  function setValue(z) {
    zs = z; zp = (ZR - zs) / 2;
    moving.clear();
    sun = inked(gearGeo(zs, M, T, 0.3), mat('steel'), 20);
    moving.add(sun);
    sunShaft.position.y = 0;
    moving.add(sunShaft);
    planets = [];
    carrier = new THREE.Group();
    const a = (M * (zs + zp)) / 2;
    // three-armed carrier plate (red, the output)
    for (let k = 0; k < 3; k++) {
      const p = new THREE.Group();
      const g = inked(gearGeo(zp, M, T, 0.32, zp > 20 ? 4 : 0), mat('part'), 20);
      p.add(g);
      p.userData.phi0 = (k / 3) * TAU;
      planets.push(p);
      moving.add(p);
    }
    const pts = [0, 1, 2].map((k) => [Math.cos((k / 3) * TAU) * a, Math.sin((k / 3) * TAU) * a]);
    // carrier: three slim arms and a hub ring (red, the output); the sun shaft passes through the hub
    const tz = T / 2 + 0.25;
    for (let k = 0; k < 3; k++) {
      const [px, py] = pts[k], len = Math.hypot(px, py), ang = Math.atan2(py, px);
      const arm = new THREE.Shape();
      arm.moveTo(1.2, -0.42);
      arm.lineTo(len, -0.42);
      arm.absarc(len, 0, 0.75, -Math.PI / 2, Math.PI / 2, false);
      arm.lineTo(1.2, 0.42);
      arm.closePath();
      const g = new THREE.ExtrudeGeometry(arm, { depth: 0.35, bevelEnabled: false, curveSegments: 16 });
      g.rotateZ(ang);
      g.rotateX(-Math.PI / 2);
      g.translate(0, tz, 0);
      carrier.add(inked(g, mat('red'), 20));
    }
    const hub = new THREE.Shape();
    hub.absarc(0, 0, 1.55, 0, TAU, false);
    const hh = new THREE.Path();
    hh.absarc(0, 0, 0.62, 0, TAU, true);
    hub.holes.push(hh);
    const hg = new THREE.ExtrudeGeometry(hub, { depth: 0.6, bevelEnabled: false, curveSegments: 32 });
    hg.rotateX(-Math.PI / 2);
    hg.translate(0, tz, 0);
    carrier.add(inked(hg, mat('red'), 20));
    for (let k = 0; k < 3; k++) {
      const pin = cyl(0.3, 0.9, mat('steel'), 12);
      pin.position.set(pts[k][0], T / 2 - 0.1, -pts[k][1]);
      carrier.add(pin);
    }
    moving.add(carrier);
    // arrows: input on the sun, output on the carrier
    const ain = arcArrow((M * zs) / 2 + 0.2, 0.3, 2.0, 0.22, INK);
    ain.position.y = T / 2 + 0.8;
    moving.add(ain);
    const aout = arcArrow(a + 1.6, 0.4, 1.6, 0.3, RED);
    aout.position.y = T / 2 + 0.9;
    moving.add(aout);
    ringPhase = null;
  }
  let ringPhase = null;
  const ratio = () => 1 + ZR / zs;
  function update(dt) {
    ths += 0.6 * TAU * dt;
    const thc = ths / ratio();
    sun.rotation.y = ths;
    carrier.rotation.y = thc;
    planets.forEach((p) => {
      const phi = p.userData.phi0 + thc;
      const a = (M * (zs + zp)) / 2;
      p.position.set(Math.cos(phi) * a, 0, -Math.sin(phi) * a);
      p.rotation.y = meshAngle(phi, ths, zs, zp);
    });
    if (ringPhase === null) {
      // turn the ring so its teeth sit in planet 0's gaps (internal mesh)
      const p = planets[0], phi = p.userData.phi0 + thc, thp = p.rotation.y;
      ringPhase = phi - (((phi - thp) * zp) / TAU - 0.5) * (TAU / ZR) + Math.PI / ZR;
      ring.rotation.y = ringPhase;
    }
  }
  setValue(18);
  return {
    group, setValue, update,
    readouts: () => [
      ['Sun / planet / ring', `${zs} / ${zp} / ${ZR} teeth`],
      ['Ratio  1 + Zring / Zsun', `${fmt(ratio(), ratio() % 1 ? 1 : 0)} : 1`],
      ['Carrier speed at 1450 rpm in', `${fmt(1450 / ratio())} rpm`],
      ['Torque shared by', '3 planets'],
    ],
    badges: [
      { n: 1, at: new THREE.Vector3(0, H + 3.4, 0), label: 'Sun – input' },
      { n: 2, at: () => planets[1] ? planets[1].position.clone().add(new THREE.Vector3(0, H + 1.6, 0)) : new THREE.Vector3(), label: 'Planets' },
      { n: 3, at: new THREE.Vector3(-6.2, H + 1.6, 4.6), label: 'Ring – held' },
      { n: 4, at: () => { const c = carrier ? carrier.rotation.y : 0; const a = (M * (zs + zp)) / 2; return new THREE.Vector3(Math.cos(c + 1.05) * a * 0.5, H + 2.2, -Math.sin(c + 1.05) * a * 0.5); }, label: 'Carrier – output' },
    ],
  };
}

/* ----------------------------------------------------------------- 3. motor */
function buildMotor() {
  const group = new THREE.Group();
  const H = 0.6;
  // stator ring, cut open on top so the coils show
  const ringShape = new THREE.Shape();
  ringShape.absarc(0, 0, 8.0, 0, TAU, false);
  const hole = new THREE.Path();
  hole.absarc(0, 0, 6.4, 0, TAU, true);
  ringShape.holes.push(hole);
  const sg = new THREE.ExtrudeGeometry(ringShape, { depth: 3.2, bevelEnabled: false, curveSegments: 64 });
  sg.rotateX(-Math.PI / 2);
  const stator = inked(sg, mat('part').clone(), 20);
  stator.position.y = H;
  group.add(stator);
  const foot = box(14, H, 9, mat('shade'));
  group.add(foot);
  // cooling fins on the outside
  for (let k = 0; k < 36; k++) {
    const a = (k / 36) * TAU;
    const f = box(0.5, 3.0, 0.16, mat('part'));
    f.position.set(Math.cos(a) * 8.2, H + 0.1, Math.sin(a) * 8.2);
    f.rotation.y = -a;
    group.add(f);
  }
  // six coils: A+ C- B+ A- C+ B- (2-pole, three-phase)
  const coils = [];
  const phase = [0, -2, 1, -0, 2, -1];
  const sign = [1, -1, 1, -1, 1, -1];
  for (let k = 0; k < 6; k++) {
    const a = (k / 6) * TAU;
    const g = new THREE.BoxGeometry(1.5, 2.6, 2.6);
    g.translate(0, 1.3, 0);
    const cm = new THREE.MeshStandardMaterial({ color: 0xb87333, roughness: 0.45, metalness: 0.6, emissive: 0x000000 });
    const c = inked(g, cm, 30);
    c.position.set(Math.cos(a) * 5.6, H + 0.3, -Math.sin(a) * 5.6);
    c.rotation.y = a;
    c.userData = { ph: Math.abs(phase[k]), sign: sign[k], mat: cm };
    group.add(c);
    coils.push(c);
    const lbl = badge(['A', 'C', 'B', 'A', 'C', 'B'][k], k % 3 === 0 ? RED : INK);
    lbl.scale.set(1.1, 1.1, 1);
    lbl.position.set(Math.cos(a) * 7.2, H + 3.9, -Math.sin(a) * 7.2);
    group.add(lbl);
  }
  // rotor with skewed bars + shaft + fan
  const rotor = new THREE.Group();
  rotor.position.y = H + 0.4;
  group.add(rotor);
  const rc = cyl(3.9, 2.8, mat('shade'), 48, 30);
  rotor.add(rc);
  for (let k = 0; k < 18; k++) {
    const a = (k / 18) * TAU;
    const bar = box(0.34, 2.9, 0.5, mat('steel'));
    bar.position.set(Math.cos(a) * 3.85, -0.05, Math.sin(a) * 3.85);
    bar.rotation.y = -a;
    rotor.add(bar);
  }
  const sh = cyl(0.55, 6.0, mat('steel'), 16);
  rotor.add(sh);
  const fan = new THREE.Group();
  fan.position.y = 5.3;
  for (let k = 0; k < 8; k++) {
    const b = box(2.6, 0.12, 0.9, mat('part'));
    b.children.forEach((c) => (c.position.x = 1.6));
    b.rotation.y = (k / 8) * TAU;
    b.rotation.z = 0.0;
    b.children[0].rotation.x = 0.5;
    fan.add(b);
  }
  fan.add(cyl(0.9, 0.5, mat('part'), 16));
  rotor.add(fan);
  // field arrow across the rotor
  const arrow = new THREE.Group();
  const shaftG = new THREE.CylinderGeometry(0.28, 0.28, 6.4, 12);
  shaftG.rotateZ(Math.PI / 2);
  const am = new THREE.MeshBasicMaterial({ color: RED });
  arrow.add(new THREE.Mesh(shaftG, am));
  const headG = new THREE.ConeGeometry(0.75, 1.5, 16);
  headG.rotateZ(-Math.PI / 2);
  const head = new THREE.Mesh(headG, am);
  head.position.x = 3.8;
  arrow.add(head);
  arrow.position.y = H + 3.6;
  group.add(arrow);
  // air particles blown by the fan along the fins
  const N = 70;
  const air = new THREE.InstancedMesh(new THREE.SphereGeometry(0.16, 8, 6), mat('blue'), N);
  const airP = Array.from({ length: N }, (_, i) => ({ a: (i / N) * TAU * 7.3, s: (i * 0.618) % 1 }));
  group.add(air);
  const dummy = new THREE.Object3D();
  let f = 50, th = 0, thr = 0, heat = 0;
  const setValue = (v) => (f = v);
  const SLIP = 0.04;
  function update(dt) {
    const we = (f / 50) * 0.45 * TAU;          // visual: 50 Hz -> 0.45 rev/s of the field
    th += we * dt;
    thr += we * (1 - SLIP) * dt;
    arrow.rotation.y = th;
    rotor.rotation.y = thr;
    coils.forEach((c) => {
      const i = Math.cos(th - (c.userData.ph * TAU) / 3) * c.userData.sign;
      const col = c.userData.mat.emissive;
      if (i > 0) col.setRGB(0.9 * i, 0.05 * i, 0.03 * i);
      else col.setRGB(0.05 * -i, 0.25 * -i, 0.85 * -i);
      c.userData.mat.emissiveIntensity = 0.9;
    });
    // cooling air ~ speed; heat at full torque stays ~ the same -> glow on the frame grows
    const cool = f / 50;
    heat = lerp(heat, Math.max(0, 1 - cool) ** 1.3, Math.min(1, dt * 2));
    stator.userData.mesh.material.emissive.setRGB(0.75 * heat, 0.12 * heat, 0.02 * heat);
    airP.forEach((p, i) => {
      p.s += dt * 0.55 * cool;
      if (p.s > 1) p.s -= 1;
      const r = 8.9 + 0.3 * Math.sin(i);
      const y = H + 6.0 - p.s * 6.3;
      dummy.position.set(Math.cos(p.a) * r, y, Math.sin(p.a) * r);
      const vis = cool < 0.02 ? 0 : (i / N < 0.25 + 0.75 * cool ? 1 : 0);
      dummy.scale.setScalar(vis);
      dummy.updateMatrix();
      air.setMatrixAt(i, dummy.matrix);
    });
    air.instanceMatrix.needsUpdate = true;
  }
  return {
    group, setValue, update,
    readouts: () => [
      ['Supply frequency (VFD)', `${fmt(f)} Hz`],
      ['Field speed  120 · f / p  (p = 2)', `${fmt((120 * f) / 2)} rpm`],
      ['Shaft-fan cooling air', `${fmt(Math.min(100, (f / 50) * 100))} %`],
      ['Heat to remove at full torque', '≈ 100 %'],
    ],
    badges: [
      { n: 1, at: new THREE.Vector3(0, H + 7.4, 0), label: 'Shaft fan – turns with the motor' },
      { n: 2, at: new THREE.Vector3(6.4, H + 5.2, -3.2), label: 'Stator coils, three phases' },
      { n: 3, at: new THREE.Vector3(-2.4, H + 4.6, 2.4), label: 'Rotating field' },
      { n: 4, at: new THREE.Vector3(-9.6, H + 3.4, 1.0), label: 'Cooling air over the fins' },
    ],
    heat: () => heat,
  };
}

/* ------------------------------------------------------------------ 4. pump */
function buildPump() {
  const group = new THREE.Group();
  const H = 0.5, R2 = 4.6;
  const base = box(17, H, 13, mat('shade'));
  group.add(base);
  // volute: spiral wall that opens into the discharge pipe
  const vol = new THREE.Shape();
  const rv = (a) => 5.3 + 1.9 * (a / TAU);
  const n = 90;
  for (let i = 0; i <= n; i++) {
    const a = (i / n) * TAU;
    const r = rv(a) + 0.7;
    i ? vol.lineTo(Math.cos(a) * r, Math.sin(a) * r) : vol.moveTo(Math.cos(a) * r, Math.sin(a) * r);
  }
  vol.lineTo(rv(TAU) + 0.7, 9.5 * 0 + 0);
  const outerEnd = rv(TAU) + 0.7;
  vol.lineTo(outerEnd, -0.01);
  vol.lineTo(outerEnd, 5.6);        // discharge pipe (shape +y = away from the reader)
  vol.lineTo(rv(0) - 0.0, 5.6);
  vol.lineTo(rv(0), 0.4);
  for (let i = n; i >= 0; i--) {
    const a = (i / n) * TAU;
    const r = rv(a);
    vol.lineTo(Math.cos(a) * r, Math.sin(a) * r);
  }
  const vg = new THREE.ExtrudeGeometry(vol, { depth: 2.6, bevelEnabled: false, curveSegments: 8 });
  vg.rotateX(-Math.PI / 2);
  const volute = inked(vg, mat('part'), 35);
  volute.position.y = H;
  group.add(volute);
  const floor = cyl(rv(TAU) + 0.6, 0.2, mat('paper'), 64, 30);
  floor.position.y = H;
  group.add(floor);
  // impeller: back plate + backward-curved vanes, i.Mak red
  const imp = new THREE.Group();
  imp.position.y = H + 0.2;
  group.add(imp);
  imp.add(cyl(R2, 0.3, mat('red'), 48, 30));
  const eye = cyl(1.2, 1.0, mat('steel'), 24);
  imp.add(eye);
  for (let k = 0; k < 6; k++) {
    const s = new THREE.Shape();
    const pts = [];
    for (let i = 0; i <= 12; i++) {
      const r = 1.3 + ((R2 - 1.4) * i) / 12;
      const a = -0.9 * ((r - 1.3) / (R2 - 1.3)) ** 1.1;      // backward curve
      pts.push([r, a]);
    }
    pts.forEach(([r, a], i) => (i ? s.lineTo(r * Math.cos(a), r * Math.sin(a)) : s.moveTo(r * Math.cos(a), r * Math.sin(a))));
    for (let i = pts.length - 1; i >= 0; i--) {
      const [r, a] = pts[i];
      const aa = a + 0.16 / r * 2.2;
      s.lineTo(r * Math.cos(aa), r * Math.sin(aa));
    }
    const g = new THREE.ExtrudeGeometry(s, { depth: 1.5, bevelEnabled: false });
    g.rotateX(-Math.PI / 2);
    const v = inked(g, mat('red'), 30);
    v.rotation.y = (k / 6) * TAU;
    v.position.y = 0.3;
    imp.add(v);
  }
  // water particles
  const N = 160;
  const water = new THREE.InstancedMesh(new THREE.SphereGeometry(0.2, 8, 6), mat('blue'), N);
  group.add(water);
  const ps = Array.from({ length: N }, (_, i) => ({ s: i / N, k: i % 6, j: ((i * 7919) % 100) / 100 }));
  const dummy = new THREE.Object3D();
  let sp = 1, th = 0;
  const setValue = (v) => (sp = v / 100);
  function pos(p, out) {
    // 0..0.4 along the vane (rotating with the impeller), 0.4..0.8 round the volute, 0.8..1 out of the pipe
    const s = p.s;
    if (s < 0.4) {
      const u = s / 0.4, r = 1.3 + (R2 - 1.3) * u;
      const a = th + (p.k / 6) * TAU + 0.35 - 0.9 * u ** 1.1;
      out.set(Math.cos(a) * r, H + 1.2, -Math.sin(a) * r);
    } else if (s < 0.82) {
      const u = (s - 0.4) / 0.42;
      const a0 = th + (p.k / 6) * TAU + 0.35 - 0.9;
      const aw = ((a0 % TAU) + TAU) % TAU;           // where it left the impeller
      const a = aw + u * (TAU - aw) * 0.999;         // then round the volute to the outlet at 2π
      const r = lerp(R2 + 0.2, rv(a) - 0.45 - 0.4 * p.j, Math.min(1, u * 3));
      out.set(Math.cos(a) * r, H + 1.2, -Math.sin(a) * r);
    } else {
      const u = (s - 0.82) / 0.18;
      const x = lerp(rv(0) + 0.3, outerEnd - 0.3, p.j);
      out.set(x, H + 1.2, -u * 5.4);
    }
  }
  function update(dt) {
    th += sp * 0.5 * TAU * dt;
    imp.rotation.y = th;
    const v = new THREE.Vector3();
    ps.forEach((p, i) => {
      p.s += dt * 0.28 * sp;
      if (p.s > 1) p.s -= 1;
      pos(p, v);
      dummy.position.copy(v);
      dummy.scale.setScalar(i / N < sp ? 1 : 0);    // fewer particles at lower flow
      dummy.updateMatrix();
      water.setMatrixAt(i, dummy.matrix);
    });
    water.instanceMatrix.needsUpdate = true;
  }
  return {
    group, setValue, update,
    readouts: () => [
      ['Pump speed', `${fmt(sp * 100)} %  (${fmt(1450 * sp)} rpm)`],
      ['Flow  Q ∝ n', `${fmt(sp * 100)} %`],
      ['Head  H ∝ n²', `${fmt(sp * sp * 100)} %`],
      ['Power  P ∝ n³', `${fmt(sp ** 3 * 100)} %`],
    ],
    bars: () => [['Q', sp], ['H', sp * sp], ['P', sp ** 3]],
    badges: [
      { n: 1, at: new THREE.Vector3(0, H + 3.2, 0), label: 'Eye – water enters here' },
      { n: 2, at: new THREE.Vector3(2.6, H + 3.0, -2.6), label: 'Impeller, backward-curved vanes' },
      { n: 3, at: new THREE.Vector3(-6.4, H + 3.4, 2.4), label: 'Volute turns speed into pressure' },
      { n: 4, at: new THREE.Vector3(6.4, H + 3.6, -5.0), label: 'Discharge' },
    ],
  };
}

/* ------------------------------------------------- 5. the real i.Mak unit */
let gltfCache = null;
/** Load the i.Mak model before the first page turn so lesson 5 pops up complete. */
export function preload() {
  const done = (res) => (g) => { gltfCache = g.scene; res(); };
  const packed = window.HB_ASSETS && window.HB_ASSETS.irkm;     // single-file build: model inlined as base64
  if (packed) {
    const bin = Uint8Array.from(atob(packed), (c) => c.charCodeAt(0)).buffer;
    return new Promise((res) => new GLTFLoader().parse(bin, '', done(res), () => res()));
  }
  return new Promise((res) => new GLTFLoader().load('models/irkm.glb', done(res), undefined, () => res()));
}
function buildReal() {
  const group = new THREE.Group();
  const turntable = cyl(8.6, 0.5, mat('shade'), 64, 30);
  group.add(turntable);
  const spin = new THREE.Group();
  spin.position.y = 0.5;
  group.add(spin);
  const paint = new THREE.MeshPhysicalMaterial({ color: RED, roughness: 0.42, metalness: 0, clearcoat: 0.35, clearcoatRoughness: 0.3 });
  const steel = new THREE.MeshStandardMaterial({ color: 0xd6dade, roughness: 0.22, metalness: 1 });
  const bore = new THREE.MeshStandardMaterial({ color: 0x8b9096, roughness: 0.4, metalness: 0.8 });
  const place = (scene) => {
    const m = scene.clone(true);
    m.traverse((o) => {
      if (!o.isMesh) return;
      o.castShadow = o.receiveShadow = true;
      const n = (o.material && o.material.name) || o.name;
      o.material = n.includes('steel') ? steel : n.includes('bore') ? bore : paint;
    });
    const bb = new THREE.Box3().setFromObject(m);
    const size = bb.getSize(new THREE.Vector3());
    const s = 15.5 / Math.max(size.x, size.z);
    m.scale.setScalar(s);
    const bb2 = new THREE.Box3().setFromObject(m);
    const c = bb2.getCenter(new THREE.Vector3());
    m.position.set(-c.x, -bb2.min.y, -c.z);
    spin.add(m);
  };
  if (gltfCache) place(gltfCache);
  else new GLTFLoader().load('models/irkm.glb', (g) => { gltfCache = g.scene; place(g.scene); });
  let hours = 2, a = 0.6;
  const FS = [1.0, 1.25, 1.5];
  const setValue = (v) => (hours = v);
  function update(dt) {
    a += dt * 0.32;
    spin.rotation.y = a;
  }
  const need = 400;
  return {
    group, setValue, update,
    readouts: () => [
      ['Mixer torque (load class M)', `${need} Nm`],
      ['Running time', ['0 – 3 h / day', '3 – 10 h / day', '10 – 24 h / day'][hours]],
      ['Service factor fs (i.Mak table)', fmt(FS[hours], 2)],
      ['Gear unit rated at least', `${fmt(need * FS[hours])} Nm`],
    ],
    badges: [],
    real: true,
  };
}

/* ------------------------------------------------------------------ cover */
function buildCover() {
  const group = new THREE.Group();
  const M = 0.3;
  const zs = [18, 30, 12];
  const gears = [];
  const rig = new THREE.Group();
  rig.position.set(0, 0.6, 0);
  group.add(rig);
  const plinth = cyl(8.4, 0.6, mat('shade'), 64, 30);
  group.add(plinth);
  let x = -6.2;
  const pos = [];
  zs.forEach((z, i) => {
    if (i) x += (M * (zs[i - 1] + z)) / 2;
    pos.push(x);
  });
  zs.forEach((z, i) => {
    const g = inked(gearGeo(z, M, 1.1, 0.4, z > 20 ? 5 : 0), i === 1 ? mat('red') : i === 2 ? mat('steel') : mat('part'), 20);
    g.position.set(pos[i], 0.6, i === 1 ? 0 : 0);
    rig.add(g);
    const sh = cyl(0.4, 2.6, mat('steel'), 16);
    sh.position.set(pos[i], 0, 0);
    rig.add(sh);
    gears.push(g);
  });
  let th = 0;
  function update(dt) {
    th += dt * 0.5 * TAU * 0.5;
    gears[0].rotation.y = th;
    const t1 = meshAngle(0, th, zs[0], zs[1]);
    gears[1].rotation.y = t1;
    gears[2].rotation.y = meshAngle(0, t1, zs[1], zs[2]);
  }
  return { group, setValue() {}, update, readouts: () => [], badges: [] };
}

function roundRect(x, l, t, w, h, r) {
  x.beginPath();
  x.moveTo(l + r, t);
  x.arcTo(l + w, t, l + w, t + h, r);
  x.arcTo(l + w, t + h, l, t + h, r);
  x.arcTo(l, t + h, l, t, r);
  x.arcTo(l, t, l + w, t, r);
  x.closePath();
}

export const LESSONS = [
  {
    id: 'cover', cover: true,
    title: 'The Drive Handbook',
    build: buildCover,
  },
  {
    id: 'ratio', kicker: 'Lesson 1 · Gear ratio',
    title: 'Speed for torque',
    formula: 'T₂ = T₁ · i · η     n₂ = n₁ / i',
    note: 'i = Z₂ / Z₁   ·   η ≈ 0.98 per helical stage',
    body: 'A gearbox does not make power. It trades speed for torque: the wheel has more teeth than the pinion, so it turns slower and pushes harder. Power in = power out, minus a little heat.',
    question: 'Double the ratio. What happens to the output torque?',
    options: ['It stays the same', 'It doubles', 'It halves'],
    answer: 1,
    reveal: 'It doubles – minus about 2 % loss per stage – and the output turns at half the speed. Watch the load: same 4 kW motor, much heavier lift, slower.',
    dial: { label: 'Wheel teeth', values: [14, 21, 28, 42, 56], start: 2, fmt: (v) => `Z₂ = ${v}` },
    fig: 'Fig. 1  A 4 kW motor lifting a load through one gear stage.',
    build: buildRatio,
  },
  {
    id: 'planetary', kicker: 'Lesson 2 · Planetary stage',
    title: 'A big ratio in a small ring',
    formula: 'i = 1 + Z_ring / Z_sun',
    note: 'ring held · sun drives · carrier is the output',
    body: 'Three planets share the load, so a planetary stage carries high torque in a compact, round housing. The smaller the sun, the bigger the ratio – that is why i.Mak IPR planetary units reach very high torques.',
    question: 'Ring held, sun turning clockwise. Which way does the carrier turn?',
    options: ['Clockwise, slower', 'Anticlockwise', 'It does not move'],
    answer: 0,
    reveal: 'Clockwise – the same way as the sun – but slower: 1 + 72 / Z_sun times. The planets roll inside the fixed ring and drag the carrier along.',
    dial: { label: 'Sun teeth', values: [36, 30, 24, 18, 12], start: 3, fmt: (v) => `Z_sun = ${v}` },
    fig: 'Fig. 2  Sun, three planets, held ring gear and carrier.',
    build: buildPlanetary,
  },
  {
    id: 'motor', kicker: 'Lesson 3 · Motor on a VFD',
    title: 'Slower is not always cooler',
    formula: 'n_s = 120 · f / p',
    note: 'f = supply frequency (Hz) · p = number of poles',
    body: 'Three coil pairs fed 120° apart make a magnetic field that rotates; the rotor follows a few percent behind (slip). A frequency inverter changes f, and with it the speed. But the cooling fan sits on the same shaft.',
    question: 'A standard motor runs at full torque at 15 Hz. What is the risk?',
    options: ['None – it runs cooler', 'It overheats', 'It runs backwards'],
    answer: 1,
    reveal: 'It overheats. Full torque still means full current and full losses, but its own fan now moves only a fraction of the air. For long low-speed running, add a forced-ventilation fan (i.Mak option CF).',
    dial: { label: 'Frequency', values: [60, 50, 40, 30, 20, 15, 10], start: 1, fmt: (v) => `f = ${v} Hz` },
    fig: 'Fig. 3  Two-pole induction motor, top cover removed.',
    build: buildMotor,
  },
  {
    id: 'pump', kicker: 'Lesson 4 · Centrifugal pump',
    title: 'The cube law',
    formula: 'Q ∝ n    H ∝ n²    P ∝ n³',
    note: 'affinity laws, same impeller, system without static head',
    body: 'The impeller flings water outwards; the volute slows it down and turns that speed into pressure. Flow follows speed, head follows speed squared – and power follows speed cubed.',
    question: 'Run the pump 20 % slower. Power drops by about…',
    options: ['20 %', 'about half', '80 %'],
    answer: 1,
    reveal: 'About half: 0.8³ = 0.51. That is why pumps on inverters save so much. With a high static lift the saving is smaller – always check the system curve.',
    dial: { label: 'Speed', values: [100, 90, 80, 70, 60, 50], start: 0, fmt: (v) => `n = ${v} %` },
    fig: 'Fig. 4  Volute casing with the cover removed.',
    build: buildPump,
  },
  {
    id: 'real', kicker: 'Lesson 5 · Sizing the gear unit',
    title: 'From drawing to the real unit',
    formula: 'T_rated ≥ T_load · fs',
    note: 'fs from the load class and the hours per day',
    body: 'The load decides the class – a mixer is M, moderate shocks. The running time decides how much margin it needs. This is an i.Mak IRKM helical-bevel geared motor, straight from our 3D model.',
    question: 'A mixer needs 400 Nm and runs 24 h a day. Which gear unit?',
    options: ['Rated 400 Nm', 'Rated 450 Nm', 'Rated 600 Nm'],
    answer: 2,
    reveal: '600 Nm. Class M at 10–24 h needs fs = 1.5 in the i.Mak table: 400 × 1.5 = 600 Nm. Shaft loads and heat are checked next.',
    dial: { label: 'Hours per day', values: [0, 1, 2], start: 0, fmt: (v) => ['0 – 3 h', '3 – 10 h', '10 – 24 h'][v] },
    fig: 'Fig. 5  i.Mak IRKM 93 geared motor, 160 L motor (official i.Mak 3D model).',
    build: buildReal,
  },
];
