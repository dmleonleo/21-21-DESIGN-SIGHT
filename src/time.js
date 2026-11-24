// One Big Clock: an independent homage to "Time" (2027) at 21_21 DESIGN SIGHT. Not affiliated with it.
// The whole building keeps one day, 10:00 to 19:00, a frame every five minutes. Eleven places, eleven ways of looking
// at ordinary time. Everything moves in steps, like stop-motion, and every object here is our own.
import * as THREE from 'three';
import * as BufferGeometryUtils from 'three/addons/utils/BufferGeometryUtils.js';
import { M, B1, label, onWall, onFloor } from './exhibit.js';

const SERIF = '"Bella Gothic",Arial,sans-serif';
const FPS = 12;                                          // the show's own frame rate: everything steps, never glides
const NIGHT = (() => { const d = new Date(), h = d.getHours() + d.getMinutes() / 60; return !(h >= 6 && h < 18.5); })();   // the visitor's own clock (Leon 2026-11-25)
const OPEN = 10, CLOSE = 19, ARRIVE = NIGHT ? 20 : 8.5, STEP = 5 / 60, FRAME = 5;   // a frame is five site minutes, shown for five seconds: one site hour a minute
const ink = new THREE.MeshBasicMaterial({ color: 0xece9e2, toneMapped: false, transparent: true, depthWrite: false, side: THREE.DoubleSide });
const inkS = () => { const m = ink.clone(); m.userData.st = 1; return m; };   // fixed lines, merged into a few meshes once built
function mergeStatic(g) {
  const buckets = new Map();
  for (const o of [...g.children]) {
    if (!o.isMesh || !o.material.userData || !o.material.userData.st || !o.visible) continue;
    o.updateMatrix(); const geo = o.geometry.clone().applyMatrix4(o.matrix); const k = o.material.opacity.toFixed(3) + '|' + o.renderOrder;
    if (!buckets.has(k)) buckets.set(k, { m: o.material, r: o.renderOrder, gs: [] });
    buckets.get(k).gs.push(geo.index ? geo.toNonIndexed() : geo); g.remove(o); o.geometry.dispose();
  }
  for (const { m, r, gs } of buckets.values()) { const mm = new THREE.Mesh(BufferGeometryUtils.mergeGeometries(gs, false), m); mm.renderOrder = r; g.add(mm); }
}
const glow = new THREE.MeshBasicMaterial({ color: 0xfff3e0, toneMapped: false, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide });
const shade = new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.5, depthWrite: false, side: THREE.DoubleSide });
const black = new THREE.MeshStandardMaterial({ color: 0x111214, roughness: 0.55, metalness: 0.35 });
const ORANGE = '#ff5a1f', PALE = '#e4f2e8';
const PENT = [0, 2, 4, 7, 9];
const pentF = (i) => 146.83 * 2 ** ((PENT[((i % 5) + 5) % 5] + 12 * Math.floor(i / 5)) / 12);   // D pentatonic from D3
const hhmm = (h) => { const m = Math.round(h * 60); return `${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`; };

function caption(title, lines, w = 1.2) {
  return label([{ t: title, size: 40, weight: 280, font: SERIF }, { t: ' ', size: 10 }, ...lines.map((t) => ({ t, size: 19, color: '#b8b4ac' }))], { w, px: 900 });
}
// a plane that carries a canvas we redraw ourselves
function sheet(w, h, px, { add = false } = {}) {
  const cv = document.createElement('canvas'); cv.width = px; cv.height = Math.round(px * h / w);
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, toneMapped: false, side: THREE.DoubleSide });
  if (add) mat.blending = THREE.AdditiveBlending;
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat); mesh.userData.label = true;
  return { mesh, cv, g: cv.getContext('2d'), tex, W: cv.width, H: cv.height };
}
// the sun over Tokyo (same sums as the site's sundial), model frame
const LAT = 35.6674 * Math.PI / 180;
function sunDir(hour) {
  const now = new Date(), doy = Math.floor((now - new Date(now.getFullYear(), 0, 0)) / 864e5);
  const decl = 23.44 * Math.PI / 180 * Math.sin(2 * Math.PI * (284 + doy) / 365);
  const H = (hour + (139.7301 - 135) / 15 - 12) * 15 * Math.PI / 180;
  const alt = Math.asin(Math.sin(LAT) * Math.sin(decl) + Math.cos(LAT) * Math.cos(decl) * Math.cos(H));
  const az = Math.atan2(-Math.sin(H), Math.tan(decl) * Math.cos(LAT) - Math.sin(LAT) * Math.cos(H));
  return { x: Math.sin(az) * Math.cos(alt), y: Math.cos(az) * Math.cos(alt), z: Math.sin(alt), alt };
}

const ZONES = [
  ['visit', (X, Y, Z) => Z > -1.2 && Math.hypot(X - 16.8, Y - 6.6) < 2.6],
  ['read', (X, Y, Z) => X > 31 && X < 39.2 && Y > -2.4 && Y < 1.8 && Z < -1.2],
  ['rice', (X, Y, Z) => X > 34.4 && X < 39.2 && Y > 6.4 && Y < 11 && Z < -1.2],
  ['cal', (X, Y, Z) => X > 57 && X < 70 && Y > -8.5 && Y < -4.4 && Z < -1.2],
  ['stair', (X, Y, Z) => X > 42 && X < 54 && Y > 13.6 && Y < 17.6 && Z > B1 + 0.5 && Z < 2.4],
  ['light', (X, Y, Z) => X > 49 && X < 60 && Y > 4.5 && Y < 12 && Z < -1.2],
  ['line', (X, Y, Z) => X > 39 && X < 70 && Y > -8.5 && Y < 6 && Z < -1.2],
  ['rings', (X, Y, Z) => X > 28 && X < 39.2 && Y > -3 && Y < 11 && Z < -1.2],
  ['board', (X, Y, Z) => X > 21 && X < 33 && Y > 7 && Y < 17 && Z > -1 && Z < 4],
  ['stone', (X, Y, Z) => X > -3 && X < 7.2 && Y > -6.2 && Y < 6.6 && Z > -1 && Z < 4.5],
  ['plaza', (X, Y, Z) => Z > -1.2],
];
const PAD = { visit: 0.5, read: 0.15, rice: 0.35, cal: 0.3, plaza: 0.6, board: 0.4, stair: 0.25, rings: 0.2, line: 0.1, light: 0.25, stone: 0 };

export async function buildTime(scene, { fx = () => {}, sound = () => null, hit = () => null, listener = () => null, ground = () => null, day = null } = {}) {
  try { await Promise.all([document.fonts.load(`280 40px ${SERIF}`), document.fonts.load(`600 40px ${SERIF}`)]); } catch (e) {}
  const g = new THREE.Group(); g.name = 'time'; g.userData.colliders = [];
  const anim = [];
  let now = 0, zone = null, frame = -1, newFrame = false;
  const DOWN = new THREE.Vector3(0, -1, 0);
  const floorZ = (X, Y, from = 2.4) => { const h = hit(M(X, Y, from), DOWN, 12); return h ? h.point.y : null; };
  const tap = (mesh, fn) => { mesh.userData.onTap = fn; mesh.userData.noClap = true; return mesh; };
  const hitBox = (w, h, d) => new THREE.Mesh(new THREE.BoxGeometry(w, h, d), new THREE.MeshBasicMaterial({ visible: false }));

  // ---------- floor rings, shared by every room ----------
  const ringG = new THREE.RingGeometry(0.975, 1, 96);
  const rings = [...Array(14)].map(() => { const r = new THREE.Mesh(ringG, ink.clone()); r.visible = false; r.renderOrder = 18; g.add(r); return { m: r, t0: -1, max: 1, sp: 1, a: 0.8 }; });
  let ri = 0;
  function ring(p, max = 3, sp = 2, a = 0.8, vertical = null) {
    const r = rings[ri++ % rings.length]; r.t0 = now; r.max = max; r.sp = sp; r.a = a; r.m.position.copy(p);
    if (vertical !== null) r.m.rotation.set(0, vertical, 0); else r.m.rotation.set(-Math.PI / 2, 0, 0);
  }
  anim.push(() => {
    if (!newFrame) return;                                // rings grow in steps too
    for (const r of rings) {
      if (r.t0 < 0) continue; const rad = 0.05 + (now - r.t0) * r.sp;
      if (rad > r.max) { r.t0 = -1; r.m.visible = false; continue; }
      r.m.visible = true; r.m.scale.setScalar(rad); r.m.material.opacity = r.a * (1 - rad / r.max) ** 1.3;
    }
  });

  // ======================= the site clock: one day, 10:00 to 19:00 =======================
  const C = { h: ARRIVE, next: 0, hold: 0, rew: -1, prevH: null, wait: 0, night: NIGHT };   // by night the doors stay shut until the visitor skips ahead
  function strike(h, at = 0) {                           // the hour, counted on a low bell at the gnomon
    const n = h % 12 || 12, X = DIAL.x, Y = DIAL.y, Z = DIAL.z + 2.4;
    for (let i = 0; i < n; i++) fx('bell', X, Y, Z, { f: 196, a: 0.55, d: 6, delay: at + i * 1.7, wet: 1.2 });
    for (let i = 0; i < n; i++) setTimeout(() => ring(M(X, Y, DIAL.z + 0.02), 7, 2.6, 0.7), (at + i * 1.7) * 1000);
  }
  function chime(up) {                                   // doors open (rising) and close (falling)
    const F = up ? [293.66, 369.99, 440, 587.33] : [587.33, 440, 369.99, 293.66];
    F.forEach((f, i) => fx('bell', DIAL.x, DIAL.y, DIAL.z + 2.4, { f, a: 0.6, d: 8, delay: i * 0.9, wet: 1.4 }));
  }
  function setH(h) { C.h = h; if (day) day.set(h); }
  function skipHour() {
    if (C.night) { C.night = false; setH(OPEN); C.next = now + FRAME; chime(true); return `The doors open: ${hhmm(OPEN)}.`; }
    if (C.rew >= 0 || C.hold) return 'The doors are closed. The day starts again in a moment.';
    const h = Math.min(CLOSE, Math.floor(C.h + 1e-6) + 1); setH(h); C.next = now + FRAME; frameTick(true);
    if (h >= CLOSE) { chime(false); C.hold = now + 12; } else strike(h);
    return `Skipped to ${hhmm(h)}.`;
  }
  function frameTick(loud) { fx('tick', DIAL.x, DIAL.y, DIAL.z + 0.3, { a: loud ? 0.6 : 0.22, f: 2400 }); }
  anim.push(() => {
    if (C.night) return;                                 // night visit: closed, the clock rests at 20:00
    if (day && day.busy()) { C.next = now + FRAME; return; }       // someone is running the sun by hand: the clock waits
    if (C.rew >= 0) {                                    // after closing: the day runs back, twelve frames a second
      if (newFrame) { C.rew++; setH(CLOSE - (CLOSE - OPEN) * Math.min(1, C.rew / 24)); frameTick(false); if (C.rew >= 24) { C.rew = -1; setH(OPEN); C.next = now + FRAME; chime(true); } }
      return;
    }
    if (C.hold) { if (now > C.hold) { C.hold = 0; C.rew = 0; } return; }
    if (now < C.next) return;
    C.next = now + FRAME;
    const before = C.h; let h = Math.round((C.h + STEP) * 12) / 12;
    if (h >= CLOSE) { h = CLOSE; C.hold = now + 12; chime(false); }
    setH(h); frameTick(false);
    if (Math.floor(h + 1e-6) > Math.floor(before + 1e-6) && h < CLOSE) strike(Math.floor(h + 1e-6));
    if (before < OPEN - 1e-6 && h >= OPEN - 1e-6) chime(true);      // the doors open on the first morning
  });

  // ======================= 01 plaza: the building is a clock =======================
  const DIAL = { x: 13.0, y: 1.4, z: 0 };
  let dialLbl = null;
  {
    DIAL.z = (ground(DIAL.x, DIAL.y) ?? -0.2) + 0.008;
    const rod = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.024, 2.4, 12), black); rod.position.copy(M(DIAL.x, DIAL.y, DIAL.z + 1.2)); rod.castShadow = true; g.add(rod);
    const foot = new THREE.Mesh(new THREE.RingGeometry(0.22, 0.24, 64), ink); onFloor(foot, DIAL.x, DIAL.y, DIAL.z); g.add(foot);
    // hour lines for today: where the tip of a 2.4 m rod throws its shadow at each opening hour
    for (let h = OPEN; h <= CLOSE; h++) {
      const s = sunDir(h); if (s.z < 0.06) continue;
      const len = Math.min(4.2, 2.4 / Math.tan(s.alt)), ang = Math.atan2(-s.y, -s.x);
      const ln = new THREE.Mesh(new THREE.PlaneGeometry(len, h === OPEN || h === CLOSE ? 0.018 : 0.01), inkS()); ln.material.opacity = 0.55;
      ln.geometry.translate(len / 2, 0, 0); onFloor(ln, DIAL.x, DIAL.y, DIAL.z, ang); g.add(ln);
      const n = label([{ t: String(h), size: 44, weight: 280, font: SERIF }], { w: 0.5, px: 240, align: 'center' });
      onFloor(n, DIAL.x + Math.cos(ang) * (len + 0.28), DIAL.y + Math.sin(ang) * (len + 0.28), DIAL.z, ang - Math.PI / 2); g.add(n);
    }
    // the rod's own shadow, drawn, jumping one frame at a time
    const sh = new THREE.Mesh(new THREE.PlaneGeometry(1, 0.05).translate(0.5, 0, 0), shade.clone()); sh.renderOrder = 17; g.add(sh);
    dialLbl = sheet(1.1, 0.28, 512); onFloor(dialLbl.mesh, DIAL.x - 0.2, DIAL.y - 0.75, DIAL.z, 0); g.add(dialLbl.mesh);
    let shownH = -1;
    anim.push(() => {
      if (C.h === shownH) return; shownH = C.h;
      const s = sunDir(C.h); const len = s.z > 0.02 ? Math.min(5, 2.4 / Math.tan(s.alt)) : 0;
      sh.visible = len > 0; sh.scale.set(Math.max(0.01, len), 1, 1); onFloor(sh, DIAL.x, DIAL.y, DIAL.z + 0.002, Math.atan2(-s.y, -s.x));
      const d = dialLbl; d.g.clearRect(0, 0, d.W, d.H); d.g.fillStyle = '#ece9e2'; d.g.font = `280 64px ${SERIF}`; d.g.textBaseline = 'middle'; d.g.fillText(hhmm(C.h), 4, d.H / 2);
      d.g.fillStyle = '#a9a59d'; d.g.font = `400 26px ${SERIF}`; d.g.fillText(C.h >= CLOSE ? 'CLOSED' : 'SITE TIME', 230, d.H / 2); d.tex.needsUpdate = true;
    });
    const hb = hitBox(0.9, 2.6, 0.9); hb.position.copy(M(DIAL.x, DIAL.y, DIAL.z + 1.3)); tap(hb, skipHour); tap(rod, skipHour); g.add(hb);
    g.add(onFloor(caption('The building is a clock', ['One day, ten to seven, a frame every five minutes.', 'Watch the shadow jump. Tap the rod to skip an hour.'], 1.15), DIAL.x + 0.5, DIAL.y - 1.7, DIAL.z));
  }

  // ======================= 02 lobby: timetable (a split-flap board) =======================
  {
    const CH = ' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:-~?.'.split('');
    const L = 16, R = 9, ROWS = 6, COLS = L + 1 + R;
    const PAGES = [
      ['EVERYDAY', [['READ ONE CAPTION', '~20 SEC'], ['CROSS THE STREET', '~30 SEC'], ['WAIT FOR GREEN', '~1 MIN'], ['MAKE AN ONIGRI', '~2 MIN'], ['WALK THE STAIR', '~30 SEC'], ['VISIT THIS SHOW', '~1 HR']]],
      ['THIS BUILDING', [['DOORS OPEN', '10:00'], ['DOORS CLOSE', '19:00'], ['CLOSED ON', 'TUESDAY'], ['OPEN FOR', '9 HR'], ['ONE FRAME HERE', '5 MIN'], ['ONE HOUR HERE', '1 MIN']]],
      ['FRAMES', [['ONE FILM SECOND', '24 FR'], ['STOP-MOTION SEC', '~12 FR'], ['ONE MINUTE', '60 SEC'], ['ONE HOUR', '3600 SEC'], ['ONE DAY', '24 HR'], ['ONE WEEK', '7 DAYS']]],
      ['SLOWER', [['A RICE SEASON', '~5 MONTHS'], ['ONE YEAR', '365 DAYS'], ['ONE GENERATION', '~30 YR'], ['THIS BUILDING', 'FROM 2007'], ['RICE IN JAPAN', '~3000 YR'], ['ONE STONE', '?']]],
    ];
    PAGES[0][1][3][0] = 'MAKE AN ONIGIRI';
    const cells = [...Array(ROWS * COLS)].map(() => ({ c: 0, to: 0 }));
    let page = -1, title = '';
    const W = 2.6, H = 1.3;
    const bd = sheet(W, H, 1536);
    const X = 31.25, Y = 12.3, Z = 1.0;
    const back = new THREE.Mesh(new THREE.BoxGeometry(W + 0.12, H + 0.12, 0.05), black); onWall(back, X - 0.03, Y, Z + H / 2, Math.PI); g.add(back);
    onWall(bd.mesh, X - 0.06, Y, Z + H / 2, Math.PI); bd.mesh.renderOrder = 16; g.add(bd.mesh);
    const cw = (bd.W - 80) / COLS, chh = (bd.H - 150) / ROWS;
    function draw() {
      const c = bd.g; c.fillStyle = '#0b0c0d'; c.fillRect(0, 0, bd.W, bd.H);
      c.fillStyle = '#ece9e2'; c.font = `600 34px ${SERIF}`; c.textBaseline = 'middle'; c.letterSpacing = '6px'; c.fillText('TIMETABLE', 40, 62);
      c.fillStyle = '#a9a59d'; c.textAlign = 'right'; c.fillText(title, bd.W - 40, 62); c.textAlign = 'left'; c.letterSpacing = '0px';
      c.font = `600 ${Math.round(chh * 0.6)}px ${SERIF}`; c.textAlign = 'center';
      for (let r = 0; r < ROWS; r++) for (let k = 0; k < COLS; k++) {
        if (k === L) continue;
        const x = 40 + k * cw, y = 120 + r * chh, cell = cells[r * COLS + k];
        c.fillStyle = cell.c !== cell.to ? '#202226' : '#16171a'; c.fillRect(x + 3, y + 5, cw - 6, chh - 10);
        c.fillStyle = k > L ? '#f2c9a0' : '#ece9e2'; c.fillText(CH[cell.c], x + cw / 2, y + chh / 2 + 2);
        c.fillStyle = '#000'; c.fillRect(x + 3, y + chh / 2 - 1, cw - 6, 2);
      }
      c.textAlign = 'left'; bd.tex.needsUpdate = true;
    }
    function setPage(p) {
      page = p; title = PAGES[p][0];
      PAGES[p][1].forEach(([a, b], r) => {
        const s = a.padEnd(L) + ' ' + b.padStart(R);
        for (let k = 0; k < COLS; k++) { const i = CH.indexOf(s[k]); cells[r * COLS + k].to = i < 0 ? 0 : i; }
      });
    }
    setPage(0); for (const c of cells) c.c = c.to; draw();
    let nextPage = 0, flips = 0;
    const flipAll = () => { setPage((page + 1) % PAGES.length); nextPage = now + 14; return `Timetable: ${title.toLowerCase()}.`; };
    tap(bd.mesh, flipAll); tap(back, flipAll);
    anim.push(() => {
      if (zone === 'board' && now > nextPage) flipAll();
      const fl = Math.floor(now * 25); if (fl === flips) return;               // the leaves fall at 25 a second
      const n = Math.min(8, Math.max(1, fl - flips)); flips = fl;               // a slow frame still drops every leaf it owes
      let moving = 0;
      for (const c of cells) if (c.c !== c.to) { for (let j = 0; j < n && c.c !== c.to; j++) c.c = (c.c + 1) % CH.length; moving++; }
      if (moving) {
        draw();
        const a = Math.min(1, 0.15 + moving / 40);
        fx('flap', X - 0.2, Y + (Math.random() - 0.5) * 2, Z + 0.7, { a });
        if (moving > 12) fx('flap', X - 0.2, Y + (Math.random() - 0.5) * 2, Z + 0.4, { a: a * 0.7, delay: 0.017 });
      }
    });
    g.add(onFloor(caption('Timetable', ['Ordinary days, timed. Watch the leaves fall', 'into place. Tap the board to turn the page.'], 1.0), 28.4, 11.0, 0.0));
  }

  // ======================= 03 the stair: twelve frames =======================
  {
    const N = 12, FR = [2, 12, 6, 24];
    let fi = 0, fps = 12, nextChange = 0, last = -1, cur = 0;
    const frames = [];
    const xs = [...Array(N)].map((_, i) => 43.4 + i * 0.48);
    for (let i = 0; i < N; i++) {
      const fz = floorZ(xs[i], 16.6); const Zm = (fz === null ? -2 : fz) + 1.45;
      const wh = hit(M(xs[i], 16.4, Zm), new THREE.Vector3(0, 0, -1), 3); const Yw = wh ? -wh.point.z - 0.012 : 17.36;
      const s = sheet(0.38, 0.38, 256);
      const c = s.g, u = i / N, bounce = Math.abs(Math.sin(Math.PI * u)), squash = i === 0 ? 0.6 : 1;
      c.fillStyle = '#0d0e10'; c.fillRect(0, 0, 256, 256); c.strokeStyle = '#3a3c40'; c.lineWidth = 3; c.strokeRect(2, 2, 252, 252);
      c.fillStyle = '#ece9e2'; c.fillRect(30, 210, 196, 3);
      const r = 22, cy = 210 - r * squash - bounce * 150, cx = 40 + u * 176;
      c.beginPath(); c.ellipse(cx, cy, r / squash ** 0.5, r * squash, 0, 0, Math.PI * 2); c.fill();
      c.fillStyle = '#7d7a74'; c.font = `400 22px ${SERIF}`; c.fillText(String(i + 1).padStart(2, '0'), 16, 34);
      s.tex.needsUpdate = true; s.mesh.material.transparent = false; s.mesh.material.depthWrite = true;
      onWall(s.mesh, xs[i], Yw, Zm, -Math.PI / 2); g.add(s.mesh);
      const set = () => { fi = (fi + 1) % FR.length; fps = FR[fi]; nextChange = now + 16; return `${fps} frames a second.`; };
      tap(s.mesh, set);
      const halo = new THREE.Mesh(new THREE.PlaneGeometry(0.44, 0.44), glow.clone()); halo.material.opacity = 0; onWall(halo, xs[i], Yw + 0.004, Zm, -Math.PI / 2); g.add(halo);
      frames.push({ m: s.mesh, halo, X: xs[i], Y: Yw, Z: Zm });
    }
    const fl = sheet(0.6, 0.16, 300); onWall(fl.mesh, xs[0] - 0.55, frames[0].Y - 0.002, frames[0].Z, -Math.PI / 2); g.add(fl.mesh);
    let shownFps = -1;
    anim.push(() => {
      if (zone === 'stair' && now > nextChange) { fi = (fi + 1) % FR.length; fps = FR[fi]; nextChange = now + 9; }
      if (fps !== shownFps) { shownFps = fps; const c = fl.g; c.clearRect(0, 0, fl.W, fl.H); c.fillStyle = '#ece9e2'; c.font = `600 44px ${SERIF}`; c.textBaseline = 'middle'; c.fillText(`${fps} FPS`, 6, fl.H / 2); fl.tex.needsUpdate = true; }
      const k = Math.floor(now * fps); if (k === last) return; last = k; cur = k % N;
      frames.forEach((f, i) => { f.m.material.color.setScalar(i === cur ? 1.3 : 0.12); f.halo.material.opacity = i === cur ? 0.55 : 0; });
      if (zone !== 'stair') return;
      const f = frames[cur];
      fx('shutter', f.X, f.Y - 0.3, f.Z, { a: fps >= 24 ? 0.18 : fps >= 12 ? 0.3 : 0.55 });
      if (cur === 0) fx('wood', f.X, f.Y - 0.3, f.Z - 0.4, { f: 150 + fps * 6, a: 0.7 });
    });
    g.add(onWall(caption('Twelve frames', ['One bounce, cut into twelve stills, lit one at a time.', 'Tap a frame to change the speed.'], 1.0), 47.6, frames[N - 1].Y - 0.004, frames[N - 1].Z - 0.55, -Math.PI / 2));
  }

  // ======================= 04 Gallery 1: a day, a week, a year =======================
  {
    const CX = 33.8, CY = 3.8, Z = B1 + 0.008;
    const add = (m) => { g.add(m); return m; };
    const tick = (r0, r1, a, w = 0.012, op = 0.6) => { const t = new THREE.Mesh(new THREE.PlaneGeometry(r1 - r0, w).translate((r0 + r1) / 2, 0, 0), inkS()); t.material.opacity = op; onFloor(t, CX, CY, Z, a); return add(t); };
    const RING = { year: 4.35, day: 3.2, week: 2.2 };
    for (const r of Object.values(RING)) { const c = new THREE.Mesh(new THREE.RingGeometry(r - 0.006, r + 0.006, 192), inkS()); c.material.opacity = 0.4; onFloor(c, CX, CY, Z); add(c); }
    const ang = (u) => Math.PI / 2 - u * Math.PI * 2;      // clockwise from north
    for (let i = 0; i < 24; i++) tick(RING.day - (i % 6 ? 0.12 : 0.3), RING.day, ang(i / 24), i % 6 ? 0.01 : 0.02);
    for (let i = 0; i < 7; i++) tick(RING.week - 0.25, RING.week, ang(i / 7), 0.02);
    { const pos = []; for (let i = 0; i < 365; i++) { const a = ang(i / 365), r0 = RING.year - 0.08; pos.push(CX + Math.cos(a) * r0, CY + Math.sin(a) * r0, CX + Math.cos(a) * RING.year, CY + Math.sin(a) * RING.year); }
      const v = []; for (let i = 0; i < pos.length; i += 2) v.push(...M(pos[i], pos[i + 1], Z + 0.002).toArray());
      const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.Float32BufferAttribute(v, 3));
      add(new THREE.LineSegments(geo, new THREE.LineBasicMaterial({ color: 0xece9e2, transparent: true, opacity: 0.35, toneMapped: false }))); }
    const MON = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334], ML = 'JFMAMJJASOND';
    MON.forEach((d, i) => { tick(RING.year - 0.3, RING.year, ang(d / 365), 0.02, 0.8); const a = ang((d + 15) / 365), r = RING.year + 0.22; const l = label([{ t: ML[i], size: 40, weight: 280, font: SERIF }], { w: 0.2, px: 100, align: 'center' }); onFloor(l, CX + Math.cos(a) * r, CY + Math.sin(a) * r, Z, a - Math.PI / 2); add(l); });
    ['00', '06', '12', '18'].forEach((t, i) => { const a = ang(i / 4), r = RING.day - 0.48; const l = label([{ t, size: 40, weight: 280, font: SERIF }], { w: 0.22, px: 110, align: 'center' }); onFloor(l, CX + Math.cos(a) * r, CY + Math.sin(a) * r, Z, a - Math.PI / 2); add(l); });
    'MTWTFSS'.split('').forEach((t, i) => { const a = ang((i + 0.5) / 7), r = RING.week - 0.4; const l = label([{ t, size: 40, weight: 280, font: SERIF }], { w: 0.16, px: 80, align: 'center' }); onFloor(l, CX + Math.cos(a) * r, CY + Math.sin(a) * r, Z, a - Math.PI / 2); add(l); });
    const hand = (len, w) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(len, w).translate(len / 2, 0, 0), glow.clone()); m.material.opacity = 0.9; m.renderOrder = 18; return add(m); };
    const H = { day: hand(RING.day - 0.05, 0.03), week: hand(RING.week - 0.05, 0.05), year: hand(RING.year - 0.05, 0.022) };
    const hub = new THREE.Mesh(new THREE.CircleGeometry(0.42, 48), glow.clone()); hub.material.opacity = 0.12; onFloor(hub, CX, CY, Z + 0.004); add(hub);
    const hubHit = hitBox(0.9, 0.3, 0.9); hubHit.position.copy(M(CX, CY, Z + 0.15)); add(hubHit);
    const lbl = sheet(1.6, 0.2, 800); onFloor(lbl.mesh, CX, CY - 0.75, Z + 0.003); add(lbl.mesh);
    // the modes: the building's own hour, a week in 14 s, a year in 24 s, then a held breath
    const MODES = [{ t: 'SITE TIME', len: 9 }, { t: 'A WEEK IN 14 SECONDS', len: 14 }, { t: 'A YEAR IN 24 SECONDS', len: 24 }, { t: ' ', len: 3 }];
    let mi = 0, t0 = 0, shown = -1, lastHour = -1, lastDay = -1, lastWeek = -1, lastMonth = -1;
    const today = new Date(), doy0 = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / 864e5) - 1, wd0 = (today.getDay() + 6) % 7;
    const next = () => { mi = (mi + 1) % MODES.length; t0 = now; lastHour = lastDay = lastWeek = lastMonth = -1; return MODES[mi].t.trim() ? MODES[mi].t.charAt(0) + MODES[mi].t.slice(1).toLowerCase() + '.' : 'Silence.'; };
    tap(hubHit, next); tap(hub, next);
    const setHand = (m, u) => onFloor(m, CX, CY, Z + 0.003, ang(u));
    anim.push(() => {
      if (zone === 'rings' && now - t0 > MODES[mi].len) next();
      if (mi !== shown) { shown = mi; const c = lbl.g; c.clearRect(0, 0, lbl.W, lbl.H); c.fillStyle = '#ece9e2'; c.font = `600 40px ${SERIF}`; c.letterSpacing = '5px'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(MODES[mi].t, lbl.W / 2, lbl.H / 2); c.letterSpacing = '0px'; c.textAlign = 'left'; lbl.tex.needsUpdate = true; }
      if (!newFrame) return;
      const on = zone === 'rings', el = Math.floor((now - t0) * FPS) / FPS;
      let dayU, d;                                        // d = days since the start of this year, fractional
      if (mi === 0) { d = doy0 + C.h / 24; }
      else if (mi === 1) d = doy0 + el / 2;                // a day every two seconds
      else if (mi === 2) d = (el / 24) * 365;              // the whole year
      else d = 365;
      dayU = d % 1; const wk = (wd0 + Math.floor(d - doy0 + 1e6)) % 7, wu = (wk + dayU) / 7, yu = (d % 365) / 365;
      setHand(H.day, dayU); H.day.material.opacity = mi === 2 ? 0.25 : 0.9;
      setHand(H.week, mi === 2 ? (Math.floor(d) % 7 + dayU) / 7 : wu); setHand(H.year, yu);
      hub.material.opacity = 0.1 + 0.1 * Math.max(0, 1 - (now - t0));
      if (!on) return;
      const hour = Math.floor(d * 24), dd = Math.floor(d), week = Math.floor(d / 7), month = MON.filter((m) => m <= (d % 365)).length;
      if (mi === 0) { if (lastHour !== hour && lastHour >= 0) fx('tick', CX, CY, B1 + 0.3, { a: 0.3 }); }
      else if (mi === 1) {
        if (hour !== lastHour && lastHour >= 0) fx('tick', CX + 1, CY, B1 + 0.2, { a: 0.12, f: 3000 });
        if (dd !== lastDay && lastDay >= 0) { const w = (wd0 + dd - doy0) % 7; fx('marimba', CX, CY + RING.week, B1 + 0.4, { f: pentF(5 + ((w % 7) + 7) % 7), a: 0.7 }); ring(M(CX, CY, Z + 0.01), RING.week, 3, 0.5); if (((w % 7) + 7) % 7 === 0) fx('bell', CX, CY, B1 + 2, { f: 293.66, a: 0.45, d: 5 }); }
      } else if (mi === 2) {
        if (week !== lastWeek && lastWeek >= 0) fx('tick', CX, CY + 2, B1 + 0.3, { a: 0.28 + 0.4 * yu, f: 1800 + 1200 * yu });
        if (month !== lastMonth && lastMonth >= 0) { fx('marimba', CX, CY, B1 + 0.6, { f: pentF(3 + month), a: 0.6 + 0.3 * yu }); ring(M(CX, CY, Z + 0.01), RING.year, 5, 0.5); }
      } else if (lastDay !== -2) {                       // the year is up: one low bell, then nothing
        fx('bell', CX, CY, B1 + 2.5, { f: 98, a: 0.9, d: 10 }); fx('thud', CX, CY, B1 + 0.2, { f: 44, a: 0.8 }); ring(M(CX, CY, Z + 0.01), 6, 4, 0.9);
        lastDay = -2; return;
      }
      if (mi !== 3) { lastHour = hour; lastDay = dd; lastWeek = week; lastMonth = month; }
    });
    g.add(onWall(caption('A day, a week, a year', ['Three hands. First the building\'s own hour, then faster.', 'Tap the centre to change the speed.'], 1.2), 28.86, 1.0, B1 + 1.55, 0));
  }

  // ======================= 05 Gallery 2: ten times longer =======================
  {
    const X0 = 40.8, X1 = 67.8, DEC = 11, LY = -2.2, Z = B1 + 0.008;
    const xAt = (lg) => X0 + (X1 - X0) * lg / DEC;
    const line = new THREE.Mesh(new THREE.PlaneGeometry(X1 - X0, 0.012).translate((X1 - X0) / 2, 0, 0), inkS()); line.material.opacity = 0.5; onFloor(line, X0, LY, Z, 0); g.add(line);
    const lit = new THREE.Mesh(new THREE.PlaneGeometry(1, 0.03).translate(0.5, 0, 0), glow.clone()); lit.material.opacity = 0.8; onFloor(lit, X0, LY, Z + 0.001, 0); lit.renderOrder = 18; g.add(lit);
    const DL = ['1 SECOND', '10 SECONDS', '1.7 MINUTES', '17 MINUTES', '2.8 HOURS', '1.2 DAYS', '12 DAYS', '4 MONTHS', '3.2 YEARS', '32 YEARS', '317 YEARS', '3,170 YEARS'];
    for (let n = 0; n <= DEC; n++) {
      const x = xAt(n), t = new THREE.Mesh(new THREE.PlaneGeometry(0.012, 0.5), inkS()); t.material.opacity = 0.7; onFloor(t, x, LY + 0.25, Z, 0); g.add(t);
      for (let k = 2; k < 10 && n < DEC; k++) { const xs = xAt(n + Math.log10(k)), s = new THREE.Mesh(new THREE.PlaneGeometry(0.008, 0.16), inkS()); s.material.opacity = 0.4; onFloor(s, xs, LY + 0.08, Z, 0); g.add(s); }
      const l = label([{ t: n === 0 ? '1 s' : `10^${n} s`.replace('10^1 s', '10 s'), size: 30, weight: 600, font: SERIF, track: 2 }, { t: DL[n], size: 22, color: '#a9a59d' }], { w: 1.0, px: 360 });
      onFloor(l, x + 0.52, LY + 0.85, Z, 0); g.add(l);
    }
    const EV = [
      [20, 'Read a caption', 'About twenty seconds, if you read every word.'],
      [120, 'Make an onigiri', 'About two minutes: wet hands, salt, rice, a strip of nori.'],
      [5400, 'One visit', 'About an hour and a half, start to finish.'],
      [86400, 'One day', 'Twenty-four hours. The site clock runs nine of them.'],
      [604800, 'One week', 'Seven days. This building rests one of them.'],
      [1.3e7, 'A rice season', 'Planting to harvest, roughly five months.'],
      [3.156e7, 'One year', 'Three hundred and sixty-five days, a little more.'],
      [6.3e8, 'This building', 'About twenty years since it opened in 2007.'],
      [9.5e10, 'Rice in Japan', 'Roughly three thousand years of planting.'],
    ];
    const dots = EV.map(([s, title, body]) => {
      const lg = Math.log10(s), x = xAt(lg);
      const d = new THREE.Mesh(new THREE.CircleGeometry(0.11, 32), glow.clone()); d.material.opacity = 0.35; onFloor(d, x, LY - 0.35, Z, 0); g.add(d);
      const l = label([{ t: title, size: 30, weight: 280, font: SERIF }], { w: 1.2, px: 420 }); onFloor(l, x + 0.6, LY - 0.72, Z, 0); g.add(l);
      const hb = hitBox(0.6, 0.2, 0.6); hb.position.copy(M(x, LY - 0.35, Z + 0.1)); g.add(hb);
      const o = { lg, x, d, lit: -10 };
      const fn = () => { o.lit = now; fx('marimba', x, LY - 0.35, Z + 0.3, { f: pentF(14 - Math.round(lg)), a: 0.7 }); ring(M(x, LY - 0.35, Z + 0.01), 1.2, 2, 0.6); return `${title}. ${body}`; };
      tap(hb, fn); tap(d, fn);
      return o;
    });
    // the pulse runs the line, a decade every two seconds: ticks at every 1..9 x 10^n, sparser and lower as it goes
    let pos = 0, rest = 0, lastK = 0;
    const lead = new THREE.Mesh(new THREE.CircleGeometry(0.09, 32), glow.clone()); lead.material.opacity = 1; lead.renderOrder = 19; g.add(lead);
    anim.push(() => {
      for (const o of dots) { const age = now - o.lit; o.d.material.opacity = 0.3 + 0.7 * Math.max(0, 1 - age / 1.2); o.d.scale.setScalar(1 + 0.8 * Math.max(0, 1 - age / 0.5)); }
      if (!newFrame) return;
      const on = zone === 'line';
      if (rest) { if (now > rest) { rest = 0; pos = 0; lastK = 0; } lead.visible = false; lit.scale.x = 0.001; return; }
      if (!on) { lead.visible = false; return; }
      pos += 1 / (2 * FPS);
      const x = xAt(Math.min(DEC, pos)); lead.visible = true; onFloor(lead, x, LY, Z + 0.002, 0); lit.scale.x = Math.max(0.001, x - X0);
      const k = Math.floor(10 ** (pos % 1)) + 9 * Math.floor(pos);            // index of the last 1..9 x 10^n mark passed
      if (k !== lastK) {
        const n = Math.floor(pos), first = k % 9 === 0, u = n / DEC;
        if (first) { fx('marimba', x, LY, Z + 0.4, { f: pentF(14 - n), a: 0.45 + 0.4 * u }); ring(M(x, LY, Z + 0.01), 1.5 + 2 * u, 2.4, 0.5 + 0.4 * u); }
        else fx('wood', x, LY, Z + 0.3, { f: 1400 * 2 ** (-n * 0.36), a: 0.18 + 0.5 * u });
        for (const o of dots) if (o.lg <= pos && o.lg > pos - 1 / (2 * FPS) - 0.15 && now - o.lit > 1) { o.lit = now; fx('glass', o.x, LY, Z + 0.5, { f: pentF(16 - Math.round(o.lg)) * 2, a: 0.25, d: 3 }); }
        lastK = k;
      }
      if (pos >= DEC) {                                   // three thousand years: the floor drops away, then silence
        fx('bell', X1, LY, Z + 2, { f: 73.42, a: 1, d: 12 }); fx('thud', X1, LY, Z + 0.2, { f: 38, a: 1 }); fx('glass', X1, LY, Z + 2, { f: 146.83, a: 0.5, d: 10 });
        ring(M(X1, LY, Z + 0.01), 12, 3.2, 0.9); rest = now + 7;
      }
    });
    g.add(onWall(caption('Ten times longer', ['Each step on the line is ten times the last. Listen', 'as the ticks slow and fall. Tap a dot to read it.'], 1.3), 52.0, -7.24, B1 + 1.6, Math.PI / 2));
  }

  // ======================= 06 court: waiting for the light =======================
  {
    const SX = 57.0, SY = 10.2, Z = B1;
    const face = Math.atan2(3.2 - SY, 53.0 - SX);           // towards the room
    const post = new THREE.Mesh(new THREE.BoxGeometry(0.07, 2.2, 0.07), black); post.position.copy(M(SX, SY, Z + 1.1)); post.castShadow = true; g.add(post);
    const head = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.78, 0.2), black); head.position.copy(M(SX, SY, Z + 2.55)); head.rotation.y = face + Math.PI / 2; head.castShadow = true; g.add(head);
    g.userData.colliders.push(post);
    const lamp = (stop) => {                              // our own pictograms: someone standing, someone walking
      const s = sheet(0.28, 0.28, 128, { add: true }), c = s.g, col = stop ? ORANGE : PALE;
      c.fillStyle = col; c.strokeStyle = col; c.lineWidth = 9; c.lineCap = 'round';
      c.beginPath(); c.arc(64, 28, 11, 0, 7); c.fill();
      if (stop) { c.beginPath(); c.moveTo(64, 46); c.lineTo(64, 84); c.moveTo(48, 50); c.lineTo(48, 78); c.moveTo(80, 50); c.lineTo(80, 78); c.moveTo(58, 84); c.lineTo(58, 116); c.moveTo(70, 84); c.lineTo(70, 116); c.stroke(); }
      else { c.beginPath(); c.moveTo(62, 46); c.lineTo(58, 84); c.moveTo(60, 54); c.lineTo(42, 72); c.moveTo(62, 54); c.lineTo(84, 66); c.moveTo(58, 84); c.lineTo(40, 114); c.moveTo(58, 84); c.lineTo(82, 112); c.stroke(); }
      s.tex.needsUpdate = true; return s.mesh;
    };
    const fwd = { x: Math.cos(face) * 0.105, y: Math.sin(face) * 0.105 };
    const red = lamp(true), green = lamp(false);
    onWall(red, SX + fwd.x, SY + fwd.y, Z + 2.74, face); onWall(green, SX + fwd.x, SY + fwd.y, Z + 2.38, face); g.add(red, green);
    const segs = [...Array(8)].map((_, i) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(0.05, 0.05), glow.clone()); const side = { x: -Math.sin(face) * 0.24, y: Math.cos(face) * 0.24 };
      onWall(m, SX + fwd.x + side.x, SY + fwd.y + side.y, Z + 2.25 + i * 0.075, face); g.add(m); return m; });
    // a crossing on the gallery floor
    for (let i = 0; i < 6; i++) { const b = new THREE.Mesh(new THREE.PlaneGeometry(0.42, 2.4), inkS()); b.material.opacity = 0.5; onFloor(b, 51.4 + i * 0.84, 8.6, Z + 0.006, 0); g.add(b); }
    const prints = [...Array(12)].map(() => { const m = new THREE.Mesh(new THREE.CircleGeometry(0.06, 16).scale(1, 1.9, 1), ink.clone()); m.visible = false; m.renderOrder = 17; g.add(m); return { m, t0: -1 }; });
    let pi = 0, phase = 'stop', until = 0, secT = 0, stepT = 0, sx = 0, foot = 0, chirpT = 0, pressed = false;
    const WAIT = 20, WALK = 9, BLINK = 3;
    const press = () => { if (phase !== 'stop') return 'Walk.'; if (!pressed) { pressed = true; until = Math.min(until, now + 3); fx('click', SX, SY, Z + 1.2, { a: 0.7, f: 1200 }); } return 'Button pressed. Not long now.'; };
    const hb = hitBox(0.6, 3, 0.6); hb.position.copy(M(SX, SY, Z + 1.5)); tap(hb, press); tap(post, press); tap(head, press); g.add(hb);
    anim.push(() => {
      for (const p of prints) { if (p.t0 < 0) continue; const age = now - p.t0; if (age > 4) { p.t0 = -1; p.m.visible = false; continue; } p.m.visible = true; p.m.material.opacity = 0.6 * (1 - age / 4); }
      const on = zone === 'light';
      if (!until) until = now + WAIT;
      if (now > until) {
        if (phase === 'stop') { phase = 'walk'; until = now + WALK; sx = 50.8; pressed = false; }
        else if (phase === 'walk') { phase = 'blink'; until = now + BLINK; }
        else { phase = 'stop'; until = now + WAIT; }
      }
      const left = Math.max(0, until - now);
      const blinkOn = phase !== 'blink' || Math.floor(now * 3) % 2 === 0;
      red.material.opacity = phase === 'stop' ? 1 : 0.08; green.material.opacity = phase === 'stop' ? 0.08 : blinkOn ? 1 : 0.1;
      const lit = phase === 'stop' ? Math.ceil(left / WAIT * 8) : phase === 'walk' ? Math.ceil(left / WALK * 8) : 0;
      segs.forEach((s, i) => { s.material.opacity = i < lit ? 0.9 : 0.06; s.material.color.set(phase === 'stop' ? ORANGE : PALE); });
      if (!on) return;
      if (phase === 'stop' && now > secT) { secT = now + 1; fx('tick', SX, SY, Z + 1.2, { a: left < 3.5 ? 0.5 : 0.12, f: left < 3.5 ? 2800 : 2000 }); }
      if (phase === 'walk' && now > chirpT) { chirpT = now + 0.55; fx('chirp', SX, SY, Z + 2.6, { a: 0.8, f: (Math.floor(now / 0.55) % 2) ? 2300 : 1900 }); }
      if (phase === 'blink' && now > chirpT) { chirpT = now + 0.33; fx('chirp', SX, SY, Z + 2.6, { a: 0.5, f: 2600 }); }
      if (phase !== 'stop' && now > stepT && sx < 56.4) {        // someone crosses
        stepT = now + 0.5; sx += 0.7; foot ^= 1; const Y = 8.6 + (foot ? 0.13 : -0.13);
        fx('step', sx, Y, Z + 0.05, { a: 0.8 }); const p = prints[pi++ % prints.length]; p.t0 = now; onFloor(p.m, sx, Y, Z + 0.01, -Math.PI / 2);
      }
    });
    g.add(onFloor(caption('Waiting for the light', ['Time we only spend waiting. It counts down, the room', 'goes quiet, then it all moves. Tap the post to press.'], 1.15), 51.6, 6.4, Z + 0.01));
  }

  // ======================= 07 Gallery 3: one stone =======================
  let city = null;
  {
    const SX = 2.2, SY = 0.4, Z = (ground(SX, SY) ?? 0) + 0.004;
    const mat = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1.6), new THREE.MeshStandardMaterial({ color: 0x15161a, roughness: 0.9 })); onFloor(mat, SX, SY, Z); mat.receiveShadow = true; g.add(mat);
    const geo = new THREE.IcosahedronGeometry(0.16, 4), p = geo.attributes.position, v = new THREE.Vector3();
    for (let i = 0; i < p.count; i++) { v.fromBufferAttribute(p, i); const n = 1 + 0.08 * Math.sin(v.x * 23 + 1.3) * Math.cos(v.z * 19) + 0.05 * Math.sin(v.y * 31 + v.x * 7); v.multiplyScalar(n); v.y *= 0.62; v.x *= 1.25; p.setXYZ(i, v.x, v.y, v.z); }
    geo.computeVertexNormals();
    const stone = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: 0x6e6b65, roughness: 0.95 })); stone.position.copy(M(SX, SY, Z + 0.09)); stone.rotation.y = 0.6; stone.castShadow = true; g.add(stone);
    const marks = [...Array(24)].map((_, i) => { const a = Math.PI / 2 - (i / 24) * Math.PI * 2, m = new THREE.Mesh(new THREE.PlaneGeometry(0.1, i % 6 ? 0.008 : 0.016), ink.clone()); m.material.opacity = 0.25; onFloor(m, SX + Math.cos(a) * 0.68, SY + Math.sin(a) * 0.68, Z + 0.003, a); g.add(m); return m; });
    const sh = new THREE.Mesh(new THREE.CircleGeometry(0.2, 40).scale(2.4, 0.9, 1).translate(0.4, 0, 0), shade.clone()); sh.material.opacity = 0.45; sh.renderOrder = 17; g.add(sh);
    const spot = new THREE.Mesh(new THREE.CircleGeometry(0.05, 20), glow.clone()); spot.renderOrder = 18; g.add(spot);
    let k = -1;
    const look = () => { fx('wood', SX, SY, Z + 0.1, { f: 130, a: 0.5 }); fx('note', SX, SY, Z + 0.4, { f: 146.83, a: 0.3, d: 4 }); return 'An ordinary stone. Look a little longer than you mean to.'; };
    tap(stone, look);
    anim.push(() => {
      const on = zone === 'stone', s = sound();
      if (s && s.ready && !city && on) city = s.drone(M(-14, -2, 2), 210, 'city');
      if (city) city.set(on ? 0.035 : 0, 2.5);
      const kk = Math.floor(now) % 24; if (kk === k) return; k = kk;     // one frame a second, a full turn in 24
      const a = Math.PI / 2 - (k / 24) * Math.PI * 2;
      marks.forEach((m, i) => (m.material.opacity = i === k ? 1 : 0.2));
      onFloor(spot, SX + Math.cos(a) * 0.68, SY + Math.sin(a) * 0.68, Z + 0.004);
      onFloor(sh, SX, SY, Z + 0.002, a + Math.PI);
      if (!on) return;
      if (k === 0) fx('bell', SX, SY, Z + 2, { f: 293.66, a: 0.35, d: 9 });
      else if (k % 6 === 0) fx('note', SX, SY, Z + 0.4, { f: 146.83 * (1 + k / 24), a: 0.08, d: 3 });
    });
    g.add(onFloor(caption('One stone', ['Almost silence. One ordinary stone, a light that', 'circles it a frame a second. Stay for one turn.'], 1.05), SX - 0.5, SY - 1.5, Z));
  }

  // ======================= 04 Gallery 1, south wall: reading time =======================
  {
    const WX = 34.6, WY = -2.39 + 0.16 * (34.6 - 33) + 0.03, ROT = 0.159, Z = B1, W = 3.6, H = 1.25;   // the south wall runs a little askew
    const TEXT = 'This is a caption. Read every word and it takes about twenty seconds. Most people read the title, glance at the first line, and walk on. That is fine. The building keeps its own time either way, and so do you.';
    const words = TEXT.split(' ');
    const sp = sheet(W, H, 1800); onWall(sp.mesh, WX, WY, Z + 1.55, Math.PI / 2 + ROT); g.add(sp.mesh);
    const c = sp.g, F = 56, LH = 84, PX = 90;
    c.font = `280 ${F}px ${SERIF}`;
    const pos = []; let x = PX, y = 150;
    for (const w of words) { const ww = c.measureText(w + ' ').width; if (x + ww > sp.W - PX) { x = PX; y += LH; } pos.push([x, y]); x += ww; }
    const SPEEDS = [['READING', 4], ['READING ALOUD', 2.4], ['SKIMMING', 12]];
    let si = 0, t0 = -1, shown = -2, rest = 0;
    function draw(k, el) {
      c.clearRect(0, 0, sp.W, sp.H);
      c.font = `600 26px ${SERIF}`; c.fillStyle = '#8f8b84'; c.fillText(SPEEDS[si][0] + `  ·  ${SPEEDS[si][1]} WORDS A SECOND`, PX, 70);
      c.font = `280 ${F}px ${SERIF}`;
      words.forEach((w, i) => { c.fillStyle = i < k ? '#f2efe8' : i === k ? ORANGE : '#5e5c57'; c.fillText(w, pos[i][0], pos[i][1]); });
      c.font = `280 64px ${SERIF}`; c.fillStyle = '#f2efe8'; c.fillText(el.toFixed(1) + ' s', PX, sp.H - 60);
      c.font = `600 24px ${SERIF}`; c.fillStyle = '#8f8b84'; c.fillText(`${Math.min(k, words.length)} OF ${words.length} WORDS`, PX + 260, sp.H - 72);
      sp.tex.needsUpdate = true;
    }
    draw(0, 0);
    const hb = hitBox(W, H, 0.3); hb.position.copy(M(WX, WY + 0.15, Z + 1.55)); hb.rotation.y = ROT; g.add(hb);
    const fn = () => { si = (si + 1) % SPEEDS.length; t0 = now; rest = 0; fx('flap', WX, WY, Z + 1.5, { a: 0.6 }); return `${SPEEDS[si][0].toLowerCase().replace(/^./, (m) => m.toUpperCase())}: ${SPEEDS[si][1]} words a second.`; };
    tap(hb, fn); tap(sp.mesh, fn);
    anim.push(() => {
      if (zone !== 'read') { t0 = -1; return; }
      if (!newFrame) return;
      if (rest) { if (now < rest) return; rest = 0; t0 = -1; }
      if (t0 < 0) { t0 = now; shown = -2; }
      const el = now - t0, k = Math.floor(el * SPEEDS[si][1]);
      if (k !== shown) {
        if (k < words.length) {
          const w = words[Math.max(0, k - 1)], end = /[.,]$/.test(w) && k > 0;
          const [px, py] = pos[Math.min(k, words.length - 1)];
          const xx = WX - W / 2 + W * px / sp.W, zz = Z + 1.55 + H / 2 - H * py / sp.H;
          fx(end ? 'wood' : 'tick', xx, WY, zz, end ? { f: /\.$/.test(w) ? 520 : 820, a: 0.35 } : { a: 0.09, f: 2600 + (k % 5) * 180 });
        } else { fx('flap', WX, WY, Z + 1.5, { a: 0.7 }); fx('note', WX, WY, Z + 1.6, { f: 293.66, a: 0.2, d: 3 }); rest = now + 4; }
        shown = k;
      }
      draw(k, Math.min(el, words.length / SPEEDS[si][1]));
    });
    g.add(onFloor(caption('Reading time', ['A caption, read one word at a time. Tap it to read', 'aloud, or to skim.'], 1.1), WX - 1.2, WY + 1.0, Z, ROT));
  }

  // ======================= 06 Gallery 1, north corner: one onigiri =======================
  {
    const RX = 36.6, RY = 8.4, Z = B1, TOP = Z + 0.78;
    const plinth = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.78, 0.9), new THREE.MeshStandardMaterial({ color: 0x1c1d20, roughness: 0.8 }));
    plinth.position.copy(M(RX, RY, Z + 0.39)); plinth.castShadow = plinth.receiveShadow = true; g.add(plinth); g.userData.colliders.push(plinth);
    const N = 560, S = 0.12;                                  // one rice ball, drawn about twice life size
    const grain = new THREE.SphereGeometry(1, 8, 6); grain.scale(0.0095, 0.0055, 0.0055);
    const rice = new THREE.InstancedMesh(grain, new THREE.MeshStandardMaterial({ color: 0xf2efe6, roughness: 0.55 }), N); rice.castShadow = true; g.add(rice);
    const HEAP = [], BALL = [], q = new THREE.Quaternion(), e = new THREE.Euler(), one = new THREE.Vector3(1, 1, 1), mtx = new THREE.Matrix4();
    const rnd = (a, b) => a + Math.random() * (b - a);
    for (let i = 0; i < N; i++) {
      const r = 0.1 * Math.sqrt(Math.random()), a = Math.random() * 7, hgt = 0.05 * (1 - r / 0.1) * Math.random();
      HEAP.push(M(RX - 0.2 + Math.cos(a) * r, RY + 0.18 + Math.sin(a) * r, TOP + 0.006 + hgt));
      // a rounded triangle standing up: sample the triangle, keep the grain near its skin
      let u, v; do { u = Math.random(); v = Math.random(); } while (u + v > 1);
      const px = (u - v) * S, pz = (1 - u - v) * S * 1.6 - (u + v) * 0.0;
      const d = rnd(-0.04, 0.04) * (1 - Math.abs(px) / S * 0.6);
      BALL.push(M(RX + 0.08 + px, RY - 0.05 + d, TOP + 0.01 + (1 - pz / (S * 1.6)) * S * 1.45 * 0.0 + pz * 0.9));
    }
    const ROT = [...Array(N)].map(() => new THREE.Quaternion().setFromEuler(e.set(rnd(0, 3), rnd(0, 3), rnd(0, 3))));
    const P = HEAP.map((p) => p.clone());
    const place = () => { for (let i = 0; i < N; i++) { mtx.compose(P[i], ROT[i], one); rice.setMatrixAt(i, mtx); } rice.instanceMatrix.needsUpdate = true; };
    place();
    const nori = new THREE.Mesh(new THREE.PlaneGeometry(0.11, 0.075), new THREE.MeshStandardMaterial({ color: 0x0d1410, roughness: 0.7, side: THREE.DoubleSide }));
    const nori2 = nori.clone(); [nori, nori2].forEach((n, i) => { n.position.copy(M(RX + 0.08, RY - 0.05 + (i ? 0.047 : -0.047), TOP + 0.045)); n.rotation.y = i ? Math.PI : 0; n.visible = false; g.add(n); });
    const tag = sheet(0.7, 0.22, 640); onFloor(tag.mesh, RX - 0.05, RY - 0.62, Z, 0); g.add(tag.mesh);
    function writeTag(a, b) { const c = tag.g; c.clearRect(0, 0, tag.W, tag.H); c.font = `600 34px ${SERIF}`; c.fillStyle = '#f2efe8'; c.fillText(a, 10, 70); c.font = `280 28px ${SERIF}`; c.fillStyle = '#a9a59d'; c.fillText(b, 10, 140); tag.tex.needsUpdate = true; }
    writeTag('TAP TO MAKE ONE', 'Rice, salt, nori. About two minutes.');
    let st = 'heap', f = 0, madeH = null, lastTag = '';
    const go = () => {
      if (st === 'make' || st === 'unmake') return 'Hold on, it is still being made.';
      if (st === 'heap') { st = 'make'; f = 0; return 'Making one: wet hands, salt, rice.'; }
      st = 'unmake'; f = 0; return 'Back to the bowl. Another one.';
    };
    const hb = hitBox(0.9, 1.2, 0.9); hb.position.copy(M(RX, RY, Z + 0.6)); g.add(hb); tap(hb, go); tap(rice, go); tap(plinth, go);
    anim.push(() => {
      if (!newFrame) return;
      if (st === 'heap' && zone === 'rice' && madeH === null) go();
      if (st === 'make') {
        f++;
        const k = Math.min(N, Math.floor(f / 30 * N));                     // three seconds of grains, a few dozen a frame
        for (let i = 0; i < k; i++) P[i].copy(BALL[i]);
        place();
        if (f <= 30) fx('tick', RX, RY, TOP + 0.1, { a: 0.12 + Math.random() * 0.12, f: rnd(3200, 5200) });
        if (f === 34 || f === 40 || f === 46) { fx('thud', RX, RY, TOP, { f: 90, a: 0.5 }); fx('wood', RX, RY, TOP + 0.1, { f: 240, a: 0.3 }); }
        if (f === 52) { nori.visible = nori2.visible = true; fx('shutter', RX, RY, TOP + 0.1, { a: 0.6 }); fx('flap', RX, RY, TOP + 0.1, { a: 0.4 }); }
        if (f === 60) { st = 'made'; madeH = C.h; fx('marimba', RX, RY, TOP + 0.3, { f: pentF(7), a: 0.6 }); ring(M(RX, RY, Z + 0.01), 1.6, 2, 0.6); }
      }
      if (st === 'unmake') {
        f++; nori.visible = nori2.visible = false;
        const k = Math.max(0, N - Math.floor(f / 8 * N));
        for (let i = k; i < N; i++) P[i].copy(HEAP[i]);
        place(); if (f % 2) fx('tick', RX, RY, TOP, { a: 0.2, f: rnd(1800, 2600) });
        if (k === 0) { st = 'make'; f = 0; madeH = null; }
      }
      // how old it is, on the site clock
      let a = 'TAP TO MAKE ONE', b = 'Rice, salt, nori. About two minutes.';
      if (st === 'make') { a = 'MAKING'; b = 'Wet hands, salt, rice, a strip of nori.'; }
      if (st === 'made' && madeH !== null) {
        let m = Math.round((C.h - madeH) * 60); if (m < 0) m += (CLOSE - OPEN) * 60;
        a = `MADE AT ${hhmm(madeH)}`; b = m < 5 ? 'Just now, on the site clock.' : `${Math.floor(m / 60) ? Math.floor(m / 60) + ' h ' : ''}${m % 60} min ago, on the site clock.${m > 240 ? ' Eat it soon.' : ''}`;
        const age = Math.min(1, m / 400); rice.material.color.setRGB(0.95 - 0.06 * age, 0.937 - 0.08 * age, 0.9 - 0.16 * age);
      } else rice.material.color.setRGB(0.95, 0.937, 0.9);
      if (a + b !== lastTag) { lastTag = a + b; writeTag(a, b); }
    });
    g.add(onFloor(caption('One onigiri', ['When was it made? Three hundred grains, three', 'presses, one strip of nori. Tap to make another.'], 1.1), RX - 1.6, RY - 1.2, Z));
  }

  // ======================= 07 Gallery 2, south wall: a year of days =======================
  {
    const WY = -7.24, WX = 62.8, Z = B1, W = 6.4, H = 1.5;
    const yr = new Date().getFullYear(), jan1 = new Date(yr, 0, 1), days = (new Date(yr + 1, 0, 1) - jan1) / 864e5;
    const today = Math.floor((new Date() - jan1) / 864e5), off = jan1.getDay();   // 0 = Sunday
    const cal = sheet(W, H, 2400); onWall(cal.mesh, WX, WY + 0.01, Z + 1.75, Math.PI / 2); g.add(cal.mesh);
    const c = cal.g, X0 = 150, Y0 = 110, CELL = 40;
    const cell = (d) => { const k = d + off; return [X0 + Math.floor(k / 7) * CELL, Y0 + (k % 7) * CELL]; };
    const MON = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
    const mStart = MON.map((_, m) => Math.round((new Date(yr, m, 1) - jan1) / 864e5));
    const SPEEDS = [[1, 'A DAY A FRAME'], [7, 'A WEEK A FRAME'], [30, 'A MONTH A FRAME']];
    let si = 0, d = 0, rest = 0;
    function draw(k) {
      c.clearRect(0, 0, cal.W, cal.H);
      c.font = `600 22px ${SERIF}`; c.fillStyle = '#8f8b84';
      ['S', 'M', 'T', 'W', 'T', 'F', 'S'].forEach((l, i) => c.fillText(l, X0 - 50, Y0 + i * CELL + 28));
      MON.forEach((m, i) => c.fillText(m, cell(mStart[i])[0], Y0 - 24));
      for (let i = 0; i < days; i++) {
        const [x, y] = cell(i), wd = (i + off) % 7;
        c.fillStyle = i === today ? ORANGE : i < k ? (wd === 2 ? '#6c6a66' : '#ece9e2') : (wd === 2 ? '#1f1f1f' : '#353432');
        c.fillRect(x, y, CELL - 8, CELL - 8);
      }
      c.font = `280 56px ${SERIF}`; c.fillStyle = '#f2efe8'; c.fillText(String(yr), X0, cal.H - 60);
      c.font = `600 22px ${SERIF}`; c.fillStyle = '#8f8b84'; c.fillText(`${Math.min(k, days)} OF ${days} DAYS  ·  ${SPEEDS[si][1]}  ·  DIMMER ROW: A DAY THE DOORS STAY SHUT`, X0 + 200, cal.H - 72);
      cal.tex.needsUpdate = true;
    }
    draw(0);
    const hb = hitBox(W, H, 0.3); hb.position.copy(M(WX, WY + 0.15, Z + 1.75)); g.add(hb);
    const fn = () => { si = (si + 1) % SPEEDS.length; d = 0; rest = 0; fx('flap', WX, WY, Z + 1.6, { a: 0.6 }); return SPEEDS[si][1].toLowerCase().replace(/^./, (m) => m.toUpperCase()) + '.'; };
    tap(hb, fn); tap(cal.mesh, fn);
    const sx = (k) => WX - W / 2 + W * cell(Math.min(k, days - 1))[0] / cal.W;
    anim.push(() => {
      if (zone !== 'cal' || !newFrame) return;
      if (rest) { if (now < rest) return; rest = 0; d = 0; }
      const was = d; d = Math.min(days, d + SPEEDS[si][0]);
      const a = Math.floor(was), b = Math.floor(d);
      for (let i = a; i < b; i++) {
        const m = mStart.indexOf(i);
        if (m >= 0) fx('marimba', sx(i), WY, Z + 1.8, { f: pentF(5 + m), a: 0.55 });
        else if (si === 0 && (i + off) % 7 === 2) fx('wood', sx(i), WY, Z + 1.6, { f: 300, a: 0.25 });
        else if (si === 0) fx('tick', sx(i), WY, Z + 1.7, { a: 0.08, f: 2400 + ((i + off) % 7) * 150 });
        if (i === today) { fx('bell', sx(i), WY, Z + 2, { f: 587.33, a: 0.6, d: 6 }); ring(M(sx(i), WY + 0.4, Z + 0.01), 2, 2, 0.7); }
      }
      if (b !== a || d === 0) draw(b);
      if (d >= days && !rest) { fx('bell', WX, WY, Z + 2, { f: 146.83, a: 0.7, d: 9 }); rest = now + 5; }
    });
    g.add(onWall(caption('A year of days', ['Every day this year, one square at a time. The orange', 'one is today. Tap the wall to change the speed.'], 1.3), WX - W / 2 - 0.9, WY + 0.01, Z + 1.6, Math.PI / 2));
  }

  // ======================= 11 plaza: your visit =======================
  {
    const VX = 16.8, VY = 6.6, VZ = (ground(VX, VY) ?? -0.18) + 0.006, MAX = 1500;
    const trail = new THREE.InstancedMesh(new THREE.CircleGeometry(0.045, 10), new THREE.MeshBasicMaterial({ color: 0xece9e2, transparent: true, opacity: 0.28, depthWrite: false, toneMapped: false }), MAX);
    trail.count = 0; trail.renderOrder = 16; trail.frustumCulled = false; g.add(trail);
    const PTS = [], mtx = new THREE.Matrix4(), q = new THREE.Quaternion().setFromEuler(new THREE.Euler(-Math.PI / 2, 0, 0)), one = new THREE.Vector3(1, 1, 1);
    const V = { start: -1, dist: 0, last: null, next: 0, rooms: new Set(), startH: null, replay: -1 };
    const pan = sheet(1.6, 0.62, 1100); onFloor(pan.mesh, VX, VY, VZ, 0); g.add(pan.mesh);
    let lastTxt = '';
    function write() {
      const s = V.start < 0 ? 0 : Math.floor(now - V.start), mm = String(Math.floor(s / 60)).padStart(2, '0'), ss = String(s % 60).padStart(2, '0');
      let sm = V.startH === null ? 0 : Math.round((C.h - V.startH) * 60); if (sm < 0) sm += (CLOSE - OPEN) * 60;
      const lines = [`${mm}:${ss}`, `${Math.round(V.dist)} M ON FOOT  ·  ${V.rooms.size} OF ${ZONES.length} PLACES  ·  ${Math.floor(sm / 60)} H ${sm % 60} MIN ON THE SITE CLOCK`];
      const txt = lines.join('|'); if (txt === lastTxt) return; lastTxt = txt;
      const c = pan.g; c.clearRect(0, 0, pan.W, pan.H);
      c.font = `600 26px ${SERIF}`; c.fillStyle = '#8f8b84'; c.fillText('YOUR VISIT', 30, 60);
      c.font = `280 150px ${SERIF}`; c.fillStyle = '#f2efe8'; c.fillText(lines[0], 24, 230);
      c.font = `600 24px ${SERIF}`; c.fillStyle = '#a9a59d'; c.fillText(lines[1], 30, 300);
      c.font = `280 24px ${SERIF}`; c.fillText('Tap to replay your route, one frame at a time.', 30, 360);
      pan.tex.needsUpdate = true;
    }
    const set = (i, p) => { mtx.compose(p, q, one); trail.setMatrixAt(i, mtx); };
    const replay = () => { if (PTS.length < 2) return 'Walk a little first. Your route is drawn as you go.'; V.replay = 0; trail.material.opacity = 0.8; fx('shutter', VX, VY, VZ + 0.3, { a: 0.6 }); return `Your route: ${Math.round(V.dist)} metres, replayed.`; };
    const hb = hitBox(1.6, 0.3, 0.62); hb.position.copy(M(VX, VY, VZ + 0.1)); g.add(hb); tap(hb, replay); tap(pan.mesh, replay);
    anim.push(() => {
      const L = listener();
      if (L && V.start >= 0 && now > V.next) {
        V.next = now + 0.8;
        const X = L.x, Y = -L.z, Zc = L.y, h = hit(M(X, Y, Zc), DOWN, 4);
        if (h) {
          const p = new THREE.Vector3(X, h.point.y + 0.012, -Y);
          if (!V.last || V.last.distanceTo(p) > 0.6) {
            if (V.last && V.last.distanceTo(p) < 6) V.dist += V.last.distanceTo(p);
            V.last = p;
            if (PTS.length < MAX) { PTS.push({ p, z: zone }); set(PTS.length - 1, p); trail.count = V.replay >= 0 ? trail.count : PTS.length; trail.instanceMatrix.needsUpdate = true; }
          }
        }
      }
      if (zone) V.rooms.add(zone);
      if (V.replay >= 0 && newFrame) {                       // the route redrawn, a few steps a frame, rising as it goes
        const step = Math.max(1, Math.ceil(PTS.length / 72)), a = V.replay; V.replay = Math.min(PTS.length, V.replay + step); trail.count = V.replay;
        const P = PTS[V.replay - 1], u = V.replay / PTS.length;
        fx('tick', -P.p.z * 0 + VX, VY, VZ + 0.3, { a: 0.15 + 0.2 * u, f: 1600 + 2400 * u });
        for (let i = a; i < V.replay; i++) if (i > 0 && PTS[i].z !== PTS[i - 1].z && PTS[i].z) fx('marimba', VX, VY, VZ + 0.6, { f: pentF(4 + ZONES.findIndex((zz) => zz[0] === PTS[i].z)), a: 0.45 });
        if (V.replay >= PTS.length) { V.replay = -1; trail.material.opacity = 0.28; trail.count = PTS.length; fx('bell', VX, VY, VZ + 2, { f: 293.66, a: 0.5, d: 6 }); ring(M(VX, VY, VZ), 4, 2.4, 0.7); }
      }
      if (zone === 'visit' && !V.seen && PTS.length > 4) { V.seen = true; replay(); }
      if (zone !== 'visit') V.seen = false;
      if (Math.floor(now * 2) !== V.w) { V.w = Math.floor(now * 2); write(); }
    });
    var visitStart = () => { if (V.start < 0) { V.start = now; V.startH = C.h; } };
  }

  // ---------- which room the visitor is in ----------
  let prevH = null;
  anim.push(() => {
    const L = listener(), s = sound(); let z = null;
    if (L) {
      const X = L.x, Y = -L.z, Z = L.y; for (const [n, f] of ZONES) if (f(X, Y, Z)) { z = n; break; }
      if (z === 'stone') { const h = hit(M(X, Y, 12), DOWN, 20); if (!h || h.point.y < Z + 0.4) z = 'plaza'; }
    }
    if (z !== zone) { zone = z; if (s && s.quiet) s.quiet(z ? PAD[z] : 1, 2.0); }
  });

  const credit = label([
    { t: 'One Big Clock', size: 44, weight: 280, font: SERIF }, { t: ' ', size: 8 },
    { t: 'The building keeps one day, ten to seven, one frame every five minutes.', size: 18, color: '#bdb9b0' },
    { t: 'An independent homage to "Time" (2027). Not affiliated with 21_21 DESIGN SIGHT.', size: 18, color: '#bdb9b0' },
  ], { w: 1.6, px: 1060 });
  g.add(onFloor(credit, 25.2, 15.6, 0));

  mergeStatic(g);
  scene.add(g);
  return {
    group: g, colliders: g.userData.colliders,
    get hour() { return C.h; },
    enter: () => { if (day) { prevH = day.get(); setH(C.h); } C.next = now + FRAME; visitStart(); },
    update: (t) => { now = t; const f = Math.floor(t * FPS); newFrame = f !== frame; frame = f; anim.forEach((fn) => fn(t)); },
    leave: () => {
      const s = sound(); if (s && s.quiet) s.quiet(1); zone = null;
      if (city) city.stop(); city = null;
      if (day && prevH !== null) day.set(prevH); prevH = null;
    },
  };
}
