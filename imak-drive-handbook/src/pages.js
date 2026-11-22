// Draws the printed pages of the handbook onto canvases (60 px per cm, page 21 x 28 cm).
export const PW = 1260, PH = 1680;
const INK = '#1f2a36', GREY = '#5d6b78', RED = '#cc0605', RED_DK = '#9e0a08', PAPER = '#f4efe4';
const F = (w, s, cond = false) => `${w} ${s}px "${cond ? 'Barlow Condensed' : 'Barlow'}"`;

let paperTile = null;
function paper(x, right) {
  if (!paperTile) {
    paperTile = document.createElement('canvas');
    paperTile.width = PW; paperTile.height = PH;
    const p = paperTile.getContext('2d');
    p.fillStyle = PAPER;
    p.fillRect(0, 0, PW, PH);
    const img = p.getImageData(0, 0, PW, PH), d = img.data;
    let seed = 7;
    const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
    for (let i = 0; i < d.length; i += 4) {
      const n = (rnd() - 0.5) * 9;
      d[i] += n; d[i + 1] += n; d[i + 2] += n * 0.9;
    }
    p.putImageData(img, 0, 0);
  }
  x.drawImage(paperTile, 0, 0);
  // faint 5 mm engineering grid
  x.strokeStyle = 'rgba(80,110,140,0.10)';
  x.lineWidth = 1;
  for (let v = 30; v < PW; v += 30) { x.beginPath(); x.moveTo(v, 0); x.lineTo(v, PH); x.stroke(); }
  for (let v = 30; v < PH; v += 30) { x.beginPath(); x.moveTo(0, v); x.lineTo(PW, v); x.stroke(); }
  // gutter shading towards the spine
  const g = right ? x.createLinearGradient(0, 0, 160, 0) : x.createLinearGradient(PW, 0, PW - 160, 0);
  g.addColorStop(0, 'rgba(60,45,25,0.22)');
  g.addColorStop(1, 'rgba(60,45,25,0)');
  x.fillStyle = g;
  x.fillRect(0, 0, PW, PH);
}

function wrap(x, text, maxW) {
  const words = text.split(' '), lines = [];
  let line = '';
  for (const w of words) {
    const t = line ? line + ' ' + w : w;
    if (x.measureText(t).width > maxW && line) { lines.push(line); line = w; } else line = t;
  }
  if (line) lines.push(line);
  return lines;
}

function para(x, text, left, top, maxW, lh) {
  const lines = wrap(x, text, maxW);
  lines.forEach((l, i) => x.fillText(l, left, top + i * lh));
  return top + lines.length * lh;
}

function footer(x, n, right, logo) {
  x.fillStyle = GREY;
  x.font = F(500, 24);
  x.textBaseline = 'alphabetic';
  if (right) {
    x.textAlign = 'right';
    x.fillText(`${n}`, PW - 90, PH - 70);
    x.textAlign = 'left';
    if (logo) x.drawImage(logo, 120, PH - 104, 100, 100 * logo.height / logo.width);
  } else {
    x.textAlign = 'left';
    x.fillText(`${n}`, 90, PH - 70);
    x.textAlign = 'right';
    x.fillText('i.Mak Drive Handbook', PW - 130, PH - 70);
    x.textAlign = 'left';
  }
  x.fillStyle = RED;
  x.fillRect(right ? PW - 230 : 90, PH - 110, 140, 4);
}

/** Layout of the interactive regions on a lesson's left page (canvas px). */
export function leftLayout(lesson) {
  const opts = (lesson.options || []).map((_, i) => ({ x: 90, y: 905 + i * 70, w: 1000, h: 60 }));
  return {
    options: opts,
    flap: { x: 90, y: 1130, w: 1080, h: 230 },
    dial: { x: 150, y: 1470, w: 960, h: 70 },
  };
}

export function drawLeft(x, lesson, st, n, logo) {
  paper(x, false);
  x.textBaseline = 'alphabetic';
  if (lesson.cover) return drawCoverLeft(x, logo);
  const L = 90, W = 1080;
  x.fillStyle = RED;
  x.font = F(600, 30, true);
  x.letterSpacing = '3px';
  x.fillText(lesson.kicker.toUpperCase(), L, 140);
  x.letterSpacing = '0px';
  x.fillStyle = INK;
  x.font = F(700, 88, true);
  x.fillText(lesson.title, L, 235);
  x.fillStyle = RED;
  x.fillRect(L, 262, 120, 6);
  // formula card
  x.fillStyle = 'rgba(255,255,255,0.55)';
  x.fillRect(L, 300, W, 150);
  x.strokeStyle = 'rgba(31,42,54,0.35)';
  x.lineWidth = 2;
  x.strokeRect(L, 300, W, 150);
  x.fillStyle = INK;
  x.font = F(600, 62, true);
  x.fillText(lesson.formula, L + 34, 382);
  x.fillStyle = GREY;
  x.font = F(500, 27);
  x.fillText(lesson.note, L + 36, 428);
  x.fillStyle = INK;
  x.font = F(400, 34);
  para(x, lesson.body, L, 520, W, 47);
  // predict
  x.fillStyle = RED;
  x.font = F(700, 30, true);
  x.letterSpacing = '3px';
  x.fillText('PREDICT', L, 800);
  x.letterSpacing = '0px';
  x.fillStyle = INK;
  x.font = F(600, 37);
  para(x, lesson.question, L, 850, W, 46);
  const lay = leftLayout(lesson);
  lesson.options.forEach((o, i) => {
    const r = lay.options[i], cy = r.y + 30;
    const chosen = st.pick === i, right = st.open && i === lesson.answer;
    x.lineWidth = 3;
    x.strokeStyle = INK;
    x.beginPath();
    x.arc(r.x + 22, cy, 17, 0, Math.PI * 2);
    x.stroke();
    if (chosen) {
      x.fillStyle = INK;
      x.beginPath();
      x.arc(r.x + 22, cy, 9, 0, Math.PI * 2);
      x.fill();
    }
    x.fillStyle = right ? RED_DK : INK;
    x.font = F(right ? 700 : 500, 35);
    x.fillText(o, r.x + 60, cy + 12);
    if (right) {
      // hand-drawn check mark
      x.strokeStyle = RED;
      x.lineWidth = 6;
      x.lineCap = 'round';
      x.beginPath();
      const tx = r.x + 60 + x.measureText(o).width + 24;
      x.moveTo(tx, cy);
      x.lineTo(tx + 14, cy + 15);
      x.lineTo(tx + 42, cy - 18);
      x.stroke();
      x.lineCap = 'butt';
    }
  });
  // flap
  const f = lay.flap;
  if (!st.open) {
    x.fillStyle = '#e6d6b6';
    x.fillRect(f.x, f.y, f.w, f.h);
    x.strokeStyle = 'rgba(31,42,54,0.45)';
    x.setLineDash([12, 9]);
    x.lineWidth = 2;
    x.strokeRect(f.x + 12, f.y + 12, f.w - 24, f.h - 24);
    x.setLineDash([]);
    // folded corner
    x.fillStyle = '#cdb88f';
    x.beginPath();
    x.moveTo(f.x + f.w - 70, f.y + f.h);
    x.lineTo(f.x + f.w, f.y + f.h - 70);
    x.lineTo(f.x + f.w, f.y + f.h);
    x.fill();
    x.fillStyle = INK;
    x.font = F(700, 44, true);
    x.fillText('Lift the flap to see the answer', f.x + 44, f.y + 105);
    x.fillStyle = GREY;
    x.font = F(500, 28);
    x.fillText('…after you have made your prediction', f.x + 46, f.y + 152);
    x.strokeStyle = RED;
    x.lineWidth = 4;
    x.beginPath();
    x.moveTo(f.x + f.w - 150, f.y + 175);
    x.quadraticCurveTo(f.x + f.w - 100, f.y + 175, f.x + f.w - 95, f.y + 130);
    x.stroke();
  } else {
    x.fillStyle = 'rgba(204,6,5,0.07)';
    x.fillRect(f.x, f.y, f.w, f.h);
    x.fillStyle = RED;
    x.fillRect(f.x, f.y, 8, f.h);
    x.fillStyle = INK;
    x.font = F(600, 33);
    para(x, lesson.reveal, f.x + 36, f.y + 56, f.w - 70, 44);
    // the lifted flap seen edge-on at the top
    x.fillStyle = '#d9c7a2';
    x.fillRect(f.x, f.y - 22, f.w, 22);
  }
  // dial
  const d = lay.dial, vals = lesson.dial.values, idx = st.dial;
  x.fillStyle = RED;
  x.font = F(700, 30, true);
  x.letterSpacing = '3px';
  x.fillText('TURN THE DIAL', L, 1440);
  x.letterSpacing = '0px';
  x.fillStyle = GREY;
  x.font = F(500, 28);
  x.textAlign = 'right';
  x.fillText(lesson.dial.label, L + W, 1440);
  x.textAlign = 'left';
  const cy = d.y + d.h / 2;
  x.strokeStyle = INK;
  x.lineWidth = 4;
  x.beginPath(); x.moveTo(d.x, cy); x.lineTo(d.x + d.w, cy); x.stroke();
  const pos = (i) => d.x + (d.w * i) / (vals.length - 1);
  vals.forEach((v, i) => {
    x.lineWidth = 3;
    x.beginPath(); x.moveTo(pos(i), cy - 16); x.lineTo(pos(i), cy + 16); x.stroke();
  });
  const kx = d.x + (d.w * st.dialPos) / (vals.length - 1);
  x.fillStyle = RED;
  x.beginPath(); x.arc(kx, cy, 26, 0, Math.PI * 2); x.fill();
  x.fillStyle = '#fff';
  x.beginPath(); x.arc(kx, cy, 9, 0, Math.PI * 2); x.fill();
  x.fillStyle = INK;
  x.font = F(700, 40, true);
  x.textAlign = 'center';
  x.fillText(lesson.dial.fmt(vals[idx]), Math.min(Math.max(kx, d.x + 90), d.x + d.w - 90), cy + 78);
  x.textAlign = 'left';
  footer(x, n * 2, false, logo);
}

function drawCoverLeft(x, logo) {
  const L = 110;
  x.fillStyle = RED;
  x.font = F(600, 32, true);
  x.letterSpacing = '4px';
  x.fillText('I.MAK GEARBOXES AND DRIVES', L, 260);
  x.letterSpacing = '0px';
  x.fillStyle = INK;
  x.font = F(700, 150, true);
  x.fillText('The Drive', L, 430);
  x.fillText('Handbook', L, 575);
  x.fillStyle = RED;
  x.fillRect(L, 620, 160, 8);
  x.fillStyle = INK;
  x.font = F(400, 42);
  para(x, 'Gearboxes, motors and pumps – explained by moving them. Turn the dial, make a prediction, lift the flap.', L, 720, 1000, 58);
  x.fillStyle = GREY;
  x.font = F(500, 30);
  x.fillText('Five lessons · every number checked against physics and the i.Mak catalogue', L, 1000);
  if (logo) x.drawImage(logo, L, 1330, 420, 420 * logo.height / logo.width);
  x.fillStyle = GREY;
  x.font = F(500, 26);
  x.fillText('Edition 2026', L, PH - 120);
}

export function drawRight(x, lesson, mech, n, logo, lessons) {
  paper(x, true);
  x.textBaseline = 'alphabetic';
  if (lesson.cover) return drawCoverRight(x, lessons, logo);
  const L = 110, W = 1060;
  // drawing frame for the pop-up
  x.strokeStyle = 'rgba(31,42,54,0.25)';
  x.lineWidth = 2;
  x.setLineDash([6, 8]);
  x.strokeRect(L - 10, 90, W + 10, 930);
  x.setLineDash([]);
  x.fillStyle = INK;
  x.font = F(500, 28);
  x.fillText(lesson.fig, L, 1080);
  // live readouts
  const rows = mech.readouts();
  let y = 1150;
  rows.forEach(([k, v], i) => {
    x.fillStyle = i % 2 ? 'rgba(255,255,255,0)' : 'rgba(255,255,255,0.5)';
    x.fillRect(L, y - 44, W, 62);
    x.fillStyle = GREY;
    x.font = F(500, 32);
    x.fillText(k, L + 18, y);
    x.fillStyle = i === rows.length - 1 || /torque|Power|least/i.test(k) ? RED_DK : INK;
    x.font = F(700, 46, true);
    x.textAlign = 'right';
    x.fillText(v, L + W - 18, y + 2);
    x.textAlign = 'left';
    y += 64;
  });
  x.strokeStyle = INK;
  x.lineWidth = 2;
  x.beginPath(); x.moveTo(L, 1106); x.lineTo(L + W, 1106); x.stroke();
  x.beginPath(); x.moveTo(L, y - 40); x.lineTo(L + W, y - 40); x.stroke();
  if (mech.bars) {
    const bars = mech.bars();
    bars.forEach(([k, v], i) => {
      const bx = L + 18, by = y + 10 + i * 46, bw = 900;
      x.fillStyle = GREY;
      x.font = F(700, 30, true);
      x.fillText(k, bx, by + 24);
      x.fillStyle = 'rgba(31,42,54,0.12)';
      x.fillRect(bx + 50, by, bw, 30);
      x.fillStyle = i === 2 ? RED : '#2f7fd8';
      x.fillRect(bx + 50, by, bw * v, 30);
    });
  } else if (mech.badgesInfo && mech.badgesInfo.length) {
    x.font = F(500, 30);
    mech.badgesInfo.forEach((b, i) => {
      const bx = L + (i % 2) * 540, by = y + 30 + Math.floor(i / 2) * 56;
      x.strokeStyle = INK;
      x.lineWidth = 3;
      x.beginPath(); x.arc(bx + 18, by - 10, 18, 0, Math.PI * 2); x.stroke();
      x.fillStyle = INK;
      x.font = F(700, 26, true);
      x.textAlign = 'center';
      x.fillText(String(b.n), bx + 18, by - 1);
      x.textAlign = 'left';
      x.font = F(500, 29);
      x.fillText(b.label, bx + 50, by);
    });
  } else if (mech.real) {
    x.fillStyle = GREY;
    x.font = F(500, 29);
    para(x, 'Geometry from the official i.Mak IRKM 93 / 160 L model, available for every size on iguide.imakreduktor.com.', L, y + 30, W, 42);
  }
  footer(x, n * 2 + 1, true, logo);
}

function drawCoverRight(x, lessons, logo) {
  const L = 120, W = 1020;
  x.fillStyle = RED;
  x.font = F(700, 30, true);
  x.letterSpacing = '3px';
  x.fillText('CONTENTS', L, 1090);
  x.letterSpacing = '0px';
  lessons.filter((l) => !l.cover).forEach((l, i) => {
    const y = 1160 + i * 78;
    x.fillStyle = RED;
    x.font = F(700, 44, true);
    x.fillText(String(i + 1), L, y);
    x.fillStyle = INK;
    x.font = F(600, 40, true);
    x.fillText(l.title, L + 60, y);
    x.fillStyle = GREY;
    x.font = F(500, 26);
    x.textAlign = 'right';
    x.fillText(l.kicker.split('·')[1].trim(), L + W, y);
    x.textAlign = 'left';
    x.strokeStyle = 'rgba(31,42,54,0.2)';
    x.lineWidth = 1;
    x.beginPath(); x.moveTo(L, y + 24); x.lineTo(L + W, y + 24); x.stroke();
  });
}
