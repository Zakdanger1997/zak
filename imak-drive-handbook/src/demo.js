// Scripted walkthrough used for the LinkedIn video (?record=1, frame by frame) and ?demo=1 (live).
// Times in seconds. The script follows the research brief: motion + a question in the first
// seconds, predict-then-reveal on every lesson, captions for sound-off viewing, logo only at the end.

const hookEl = () => document.getElementById('hook');
const capEl = () => document.getElementById('cap');
const curEl = () => document.getElementById('cursor');
const endEl = () => document.getElementById('endcard');

export function script(hb) {
  const ev = [];
  const at = (t, fn) => ev.push({ t, fn });
  const hook = (t, html) => at(t, () => (hookEl().innerHTML = html));
  const cap = (t, text) => at(t, () => (capEl().innerHTML = text ? `<span>${text}</span>` : ''));
  const view = (t, v, d = 1.0) => at(t, () => hb.view(v, d));
  const dial = (t, i) => at(t, () => hb.setDial(i));
  const turn = (t, i) => at(t, () => hb.goTo(i));
  // cursor: glide to a page target 0.6 s before the tap
  const tap = (t, target, fn) => {
    at(t - 0.65, () => cursor.go(target));
    at(t, () => { cursor.tap(); fn(); });
  };
  const opt = (i) => () => { const r = hb.layoutOf().options[i]; return [r.x + 22, r.y + 30]; };
  const flap = () => { const r = hb.layoutOf().flap; return [r.x + r.w * 0.55, r.y + r.h * 0.5]; };

  // 1 · ratio
  hook(0, 'Double the gear ratio.<br>What happens to the <em>torque?</em>');
  dial(0.9, 3);
  dial(1.7, 4);
  cap(1.7, '2 : 1 → 4 : 1 · same 4 kW motor');
  view(3.0, 'left', 1.0);
  hook(3.0, '');
  cap(3.4, 'Guess before the book answers.');
  tap(4.6, opt(1), () => hb.pick(1));
  tap(5.8, flap, () => hb.toggleFlap(true));
  cap(5.9, 'Torque × 2, speed ÷ 2 – minus ~2 % loss per stage.');
  at(7.4, () => cursor.hide());
  view(7.6, 'book', 0.9);
  hook(7.6, '');
  cap(7.7, '');
  turn(8.2, 2);
  // 2 · planetary
  view(9.3, 'mech', 1.0);
  hook(9.4, 'A <em>7 : 1</em> ratio<br>inside one ring gear.');
  dial(10.6, 4);
  cap(10.6, 'Smaller sun → bigger ratio: 1 + 72 / 12 = 7');
  cap(12.4, 'Three planets share the torque.');
  view(13.4, 'book', 0.9);
  hook(13.4, '');
  cap(13.5, '');
  turn(14.0, 3);
  // 3 · motor on a VFD
  view(15.1, 'mech', 1.0);
  hook(15.2, 'You slowed the motor to protect it.<br><em>That’s why it overheated.</em>');
  dial(16.0, 2);
  dial(16.6, 3);
  dial(17.2, 4);
  dial(17.8, 5);
  cap(16.2, '50 Hz → 15 Hz: its own fan slows down too');
  view(19.2, 'left', 1.0);
  hook(19.2, '');
  cap(19.4, 'Predict the risk.');
  tap(20.6, opt(1), () => hb.pick(1));
  tap(21.8, flap, () => hb.toggleFlap(true));
  cap(21.9, 'Full torque = full heat, a fraction of the air. Long low-speed duty → forced-ventilation fan.');
  at(24.2, () => cursor.hide());
  view(24.4, 'book', 0.9);
  hook(24.4, '');
  cap(24.5, '');
  turn(25.0, 4);
  // 4 · pump
  view(26.1, 'mech', 1.0);
  hook(26.2, 'Run a pump <em>20 % slower.</em><br>How much power do you save?');
  dial(27.1, 1);
  dial(27.8, 2);
  cap(27.3, 'Flow ∝ n · head ∝ n² · power ∝ n³');
  view(29.0, 'left', 1.0);
  hook(29.0, '');
  tap(30.4, opt(1), () => hb.pick(1));
  tap(31.6, flap, () => hb.toggleFlap(true));
  cap(31.7, 'About half: 0.8³ = 0.51 (less with high static head).');
  at(33.8, () => cursor.hide());
  view(34.0, 'book', 0.9);
  hook(34.0, '');
  cap(34.1, '');
  turn(34.6, 5);
  // 5 · the real unit
  view(35.7, 'mech', 1.2);
  hook(35.8, 'Then the drawing becomes<br><em>the real i.Mak unit.</em>');
  cap(36.2, 'IRKM helical-bevel geared motor – our official 3D model');
  dial(38.4, 1);
  dial(39.2, 2);
  cap(38.6, 'Mixer 400 Nm · 24 h/day → fs 1.5 → 600 Nm gear unit');
  at(41.2, () => end.show());
  const duration = 45.0;
  ev.sort((a, b) => a.t - b.t);
  return { ev, duration };
}

// cursor glides in page coordinates and is projected every frame (the camera keeps moving)
const cursor = {
  hb: null, from: null, to: null, t: 1, vis: false, tapT: 1,
  go(target) {
    const p = typeof target === 'function' ? target() : target;
    const start = this.vis && this.pos ? this.pos : [p[0] + 260, p[1] + 220];
    this.from = start; this.to = p; this.t = 0; this.vis = true;
  },
  tap() { this.tapT = 0; },
  hide() { this.vis = false; },
  step(dt) {
    const el = curEl();
    if (!this.vis || !this.to) { el.style.display = 'none'; return; }
    this.t = Math.min(1, this.t + dt / 0.6);
    const k = this.t < 0.5 ? 2 * this.t * this.t : 1 - (-2 * this.t + 2) ** 2 / 2;
    this.pos = [this.from[0] + (this.to[0] - this.from[0]) * k, this.from[1] + (this.to[1] - this.from[1]) * k];
    const s = this.hb.leftPagePoint(this.pos[0], this.pos[1]);
    el.style.display = 'block';
    el.style.left = s.x + 'px';
    el.style.top = s.y + 'px';
    this.tapT += dt;
    el.classList.toggle('tap', this.tapT < 0.3);
    el.style.transform = `scale(${this.tapT < 0.3 ? 0.8 : 1})`;
  },
};

const end = {
  t: -1,
  show() {
    const e = endEl();
    e.querySelector('h1').textContent = 'The Drive Handbook';
    e.querySelector('p').innerHTML = 'Five machines you can turn, guess and check.<br>Which one should we explain next?';
    this.t = 0;
  },
  step(dt) {
    if (this.t < 0) return;
    this.t += dt;
    const e = endEl();
    e.style.display = 'flex';
    e.style.opacity = Math.min(1, this.t / 0.6);
    hookEl().style.opacity = capEl().style.opacity = Math.max(0, 1 - this.t / 0.4);
  },
};

export function runDemo(hb, live) {
  cursor.hb = hb;
  const { ev, duration } = script(hb);
  let t = 0, next = 0;
  function frame(dt, render = true) {
    t += dt;
    while (next < ev.length && ev[next].t <= t) ev[next++].fn();
    hb.step(dt, render);
    cursor.step(dt);
    end.step(dt);
  }
  hb.view('mech', 0.01);
  if (live) {
    let last = performance.now();
    const loop = (now) => {
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      frame(dt);
      if (t < duration + 2) requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }
  return { frame, duration };
}
