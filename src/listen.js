// Room Tone: a show you hear. Made for this model; not an homage to, or a copy of, any past exhibition.
// Seven rooms, seven instruments. Each room plays on its own while you are in it, and every sound is drawn:
// wavefronts on the floor, rays to the walls that answered, light on the stair, columns over the voices,
// a playhead that crosses the long room, rings on the glass, one slow ring at the end.
import * as THREE from 'three';
import { M, B1, label, onWall, onFloor } from './exhibit.js';

const C = 343, SLOW = 100;                              // m/s; floor rings and rays move at C / SLOW = 3.43 m/s
const SERIF = '"Bella Gothic",Arial,sans-serif';
const ink = new THREE.MeshBasicMaterial({ color: 0xece9e2, toneMapped: false, transparent: true, depthWrite: false, side: THREE.DoubleSide });
const glow = new THREE.MeshBasicMaterial({ color: 0xfff3e0, toneMapped: false, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide });
const black = new THREE.MeshStandardMaterial({ color: 0x0d0e10, roughness: 0.5, metalness: 0.4 });
const PENT = [0, 2, 4, 7, 9];
const pentF = (i) => 146.83 * 2 ** ((PENT[((i % 5) + 5) % 5] + 12 * Math.floor(i / 5)) / 12);   // D pentatonic from D3
const rnd = (a, b) => a + Math.random() * (b - a);

function caption(title, lines, w = 1.2) {
  return label([{ t: title, size: 40, weight: 280, font: SERIF }, { t: ' ', size: 10 }, ...lines.map((t) => ({ t, size: 19, color: '#b8b4ac' }))], { w, px: 900 });
}
const DIRS = [];
for (let i = 0; i < 16; i++) { const a = (i / 16) * Math.PI * 2; DIRS.push(new THREE.Vector3(Math.cos(a), 0.04, Math.sin(a)).normalize()); }
for (let i = 0; i < 6; i++) { const a = (i / 6) * Math.PI * 2 + 0.3; DIRS.push(new THREE.Vector3(Math.cos(a) * 0.7, 0.71, Math.sin(a) * 0.7).normalize()); }
DIRS.push(new THREE.Vector3(0, 1, 0));

// the stair, measured off the model: upper flight runs west to east down to a landing, lower flight back west to Gallery 2
const UPPER = { y0: 16.05, y1: 17.2, r: [42.9, 43.2, 43.6, 44.0, 44.3, 44.7, 45.1, 45.4, 45.8, 46.2, 46.6, 46.9, 47.3, 47.7, 48.0, 48.4, 48.8, 49.1] };
const LOWER = { y0: 14.1, y1: 15.6, r: [49.0, 48.7, 48.3, 47.9, 47.6, 47.2, 46.8, 46.5, 46.1, 45.7, 45.4, 45.0] };
// a melody that walks down the stair (degrees of D pentatonic), one note a tread
const MELODY = [14, 13, 12, 13, 11, 10, 11, 9, 8, 9, 10, 8, 7, 6, 7, 5, 6, 4, 9, 8, 7, 8, 6, 5, 6, 4, 3, 2, 0];

// rooms, in model coordinates; first match wins
const ZONES = [
  ['stair', (X, Y, Z) => X > 42 && X < 54 && Y > 13.6 && Y < 17.6 && Z > B1 + 0.5 && Z < 2.4],
  ['glass', (X, Y, Z) => X > 49 && X < 60 && Y > 0 && Y < 12 && Z < -1.2],
  ['long', (X, Y, Z) => X > 39 && X < 70 && Y > -8.5 && Y < 6 && Z < -1.2],
  ['voices', (X, Y, Z) => X > 28 && X < 39.2 && Y > -3 && Y < 11 && Z < -1.2],
  ['lobby', (X, Y, Z) => X > 21 && X < 33 && Y > 7 && Y < 17 && Z > -1 && Z < 4],
  ['minute', (X, Y, Z) => X > -7 && X < 12 && Y > -7 && Y < 9 && Z > -1 && Z < 5],
  ['plaza', (X, Y, Z) => Z > -1.2],
];
const PAD = { plaza: 0.7, lobby: 0.45, stair: 0.3, voices: 0.12, long: 0.25, glass: 0.3, minute: 0 };

export async function buildListen(scene, { fx = () => {}, sound = () => null, hit = () => null, listener = () => null, ground = () => null } = {}) {
  try { await document.fonts.load(`280 40px ${SERIF}`); } catch (e) {}
  const g = new THREE.Group(); g.name = 'listen'; g.userData.colliders = [];
  const anim = [];
  let now = 0, zone = null, zoneT = 0;
  const DOWN = new THREE.Vector3(0, -1, 0), o3 = new THREE.Vector3(), v3 = new THREE.Vector3();
  const floorAt = (X, Y, Z) => { const h = hit(M(X, Y, Z + 0.4), DOWN, 6); return h ? -0 + h.point.y : M(0, 0, Z).y; };   // three y

  // ---------- drawn sound: floor rings, echo rays, dots where echoes return ----------
  const ringG = new THREE.RingGeometry(0.975, 1, 128);
  const rings = [...Array(16)].map(() => { const r = new THREE.Mesh(ringG, ink.clone()); r.rotation.x = -Math.PI / 2; r.visible = false; r.renderOrder = 18; g.add(r); return { m: r, t0: -1, max: 1, sp: 1, a: 0.85 }; });
  let ri = 0;
  function ring(p, max = 14, sp = C / SLOW, a = 0.85, vertical = false) {
    const r = rings[ri++ % rings.length]; r.t0 = now; r.max = max; r.sp = sp; r.a = a; r.m.position.copy(p);
    if (vertical) r.m.rotation.set(0, 0, 0); else r.m.rotation.set(-Math.PI / 2, 0, 0);
    return r;
  }
  const rayMats = [];
  const rays = [...Array(64)].map(() => {
    const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.Float32BufferAttribute(new Float32Array(6), 3));
    const m = ink.clone(); m.opacity = 0; rayMats.push(m);
    const l = new THREE.Line(geo, new THREE.LineBasicMaterial({ color: 0xece9e2, transparent: true, opacity: 0, depthWrite: false, toneMapped: false }));
    l.visible = false; l.renderOrder = 19; l.frustumCulled = false; g.add(l); return { l, t0: -1, a: 1 };
  });
  let yi = 0;
  const dotG = new THREE.CircleGeometry(0.06, 20);
  const dots = [...Array(64)].map(() => { const d = new THREE.Mesh(dotG, ink.clone()); d.visible = false; d.renderOrder = 18; g.add(d); return { m: d, t0: -1 }; });
  let di = 0;
  anim.push(() => {
    for (const r of rings) {
      if (r.t0 < 0) continue; const rad = 0.05 + (now - r.t0) * r.sp;
      if (rad > r.max) { r.t0 = -1; r.m.visible = false; continue; }
      r.m.visible = true; r.m.scale.setScalar(rad); r.m.material.opacity = r.a * (1 - rad / r.max) ** 1.4;
    }
    for (const y of rays) {
      if (y.t0 < 0) continue; const age = now - y.t0;
      if (age < 0) { y.l.visible = false; continue; }
      if (age > 1.8) { y.t0 = -1; y.l.visible = false; continue; }
      y.l.visible = true; y.l.material.opacity = y.a * (1 - age / 1.8) ** 2;
    }
    for (const d of dots) {
      if (d.t0 < 0) continue; const age = now - d.t0;
      if (age < 0) { d.m.visible = false; continue; }
      if (age > 2.4) { d.t0 = -1; d.m.visible = false; continue; }
      d.m.visible = true; d.m.material.opacity = Math.max(0, 1 - age / 2.4) * (age < 0.08 ? age / 0.08 : 1); d.m.scale.setScalar(1 + age * 1.2);
    }
  });

  // a clap at a point (three.js coordinates): direct sound, first echoes off the real surfaces, drawn as they happen
  function clapAt(p, { kind = 'clap', a = 1, f, quietEcho = 1 } = {}) {
    const mp = { x: p.x, y: -p.z, z: p.y };
    fx(kind, mp.x, mp.y, mp.z, { a, f });
    const fh = hit(o3.copy(p).add(v3.set(0, 0.3, 0)), DOWN, 8);
    ring(new THREE.Vector3(p.x, (fh ? fh.point.y : p.y) + 0.012, p.z), 16);
    const L = listener(); const src = new THREE.Vector3().copy(p).add(v3.set(0, 0.25, 0));
    let n = 0;
    for (const d of DIRS) {
      const h = hit(src, d, 60); if (!h || h.distance < 0.6) continue;
      const q = h.point, dist = h.distance;
      const back = L ? Math.hypot(q.x - L.x, q.y - L.y, q.z - L.z) : dist;
      const delay = (dist + back) / C, amp = Math.min(0.55, 2.4 / (dist + back)) * quietEcho;
      if (amp < 0.025) continue;
      fx(kind, q.x, -q.z, q.y, { delay, a: amp * a, f, wet: 0.3 });
      const at = now + dist / (C / SLOW);
      const y = rays[yi++ % rays.length]; const pa = y.l.geometry.attributes.position.array;
      pa[0] = src.x; pa[1] = src.y; pa[2] = src.z; pa[3] = q.x; pa[4] = q.y; pa[5] = q.z; y.l.geometry.attributes.position.needsUpdate = true;
      y.t0 = at; y.a = Math.min(0.7, 0.25 + amp);
      const dd = dots[di++ % dots.length]; dd.t0 = at; dd.m.position.copy(q).addScaledVector(d, -0.02); dd.m.lookAt(o3.copy(q).sub(d));
      n++;
    }
    return n;
  }

  // ======================= 01 plaza: call and answer =======================
  let wind = null;
  {
    const x = 8.0, y = -1.6, z = (ground(x, y) ?? -0.08) + 0.01;
    const c = new THREE.Mesh(new THREE.RingGeometry(0.58, 0.6, 96), ink); onFloor(c, x, y, z); g.add(c);
    g.add(onFloor(caption('Call and answer', ['Wooden clappers walk the plaza. Watch the walls reply.', 'Tap anywhere to clap back.'], 1.0), x - 0.5, y - 1.1, z));
    // a pair of wooden clappers circles the plaza, a slow call, then a roll that speeds up
    const ROLL = [0, 1.4, 2.4, 2.95, 3.35, 3.62, 3.84, 4.02, 4.17, 4.29, 4.39, 4.47, 4.54];
    let next = 0, k = 0, cx = 0, cy = 0;
    anim.push(() => {
      if (zone !== 'plaza') { next = now + 1.2; k = 0; return; }
      const s = sound(); if (s && s.ready && !wind) { wind = s.drone(M(30, 34, 9), 520, 'wind'); }
      if (now < next) return;
      if (k === 0) { const a = rnd(0, Math.PI * 2); cx = 11 + Math.cos(a) * 3.4; cy = -2.6 + Math.sin(a) * 2.4; }
      const gz = (ground(cx, cy) ?? -0.08) + 1.2;
      clapAt(M(cx, cy, gz), { kind: 'block', a: 0.9 - k * 0.03, f: k % 2 ? 1620 : 1720, quietEcho: 1.4 });
      k++;
      if (k >= ROLL.length) { k = 0; next = now + 6; } else next = now + (ROLL[k] - ROLL[k - 1]);
    });
  }
  // ======================= 02 lobby: footsteps =======================
  {
    const c = new THREE.Mesh(new THREE.RingGeometry(0.58, 0.6, 96), ink); onFloor(c, 28.2, 12.2, 0.01); g.add(c);
    g.add(onFloor(caption('Footsteps', ['Someone you cannot see is walking.', 'Concrete hands every step back. Tap to clap.'], 1.0), 27.6, 11.0, 0.01));
    const PATH = [[23.5, 14.6], [27.5, 15.2], [31.0, 13.6], [30.4, 10.2], [26.8, 9.4], [24.0, 11.4]];
    const prints = [...Array(14)].map(() => { const m = new THREE.Mesh(new THREE.CircleGeometry(0.07, 18).scale(1, 1.9, 1), ink.clone()); m.visible = false; m.renderOrder = 17; g.add(m); return { m, t0: -1 }; });
    let pi = 0, s0 = 0, nextStep = 0, foot = 0;
    const per = PATH.reduce((acc, p, i) => acc + Math.hypot(PATH[(i + 1) % PATH.length][0] - p[0], PATH[(i + 1) % PATH.length][1] - p[1]), 0);
    function at(d) {
      d = ((d % per) + per) % per;
      for (let i = 0; i < PATH.length; i++) { const a = PATH[i], b = PATH[(i + 1) % PATH.length], l = Math.hypot(b[0] - a[0], b[1] - a[1]); if (d <= l) { const u = d / l; return [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, Math.atan2(b[1] - a[1], b[0] - a[0])]; } d -= l; }
      return PATH[0];
    }
    anim.push(() => {
      for (const p of prints) { if (p.t0 < 0) continue; const age = now - p.t0; if (age > 5) { p.t0 = -1; p.m.visible = false; continue; } p.m.visible = true; p.m.material.opacity = 0.55 * (1 - age / 5); }
      if (zone !== 'lobby' || now < nextStep) return;
      nextStep = now + 0.56; s0 += 0.72; foot ^= 1;
      const [x, y, h] = at(s0), side = foot ? 0.13 : -0.13, X = x - Math.sin(h) * side, Y = y + Math.cos(h) * side;
      fx('step', X, Y, 0.05, { a: 0.9, wet: 1.3 });
      const p = prints[pi++ % prints.length]; p.t0 = now; onFloor(p.m, X, Y, 0.012, h - Math.PI / 2);
      ring(M(X, Y, 0.014), 2.2, 1.6, 0.4);
    });
  }
  // ======================= 03 the stair: a tuned stair =======================
  const treads = [];
  {
    const add = (F, i, x0, x1) => {
      const z = (() => { const h = hit(M((x0 + x1) / 2, (F.y0 + F.y1) / 2, 2.4), DOWN, 10); return h ? h.point.y : null; })();
      if (z === null) return;
      const w = F.y1 - F.y0, nose = x0;
      const bar = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.006, w * 0.94), glow.clone()); bar.position.set(nose, z + 0.004, -(F.y0 + F.y1) / 2); bar.material.opacity = 0.08; bar.renderOrder = 18; g.add(bar);
      treads.push({ x0: Math.min(x0, x1), x1: Math.max(x0, x1), y0: F.y0, y1: F.y1, z, bar, lit: -10 });
    };
    for (let i = 0; i < UPPER.r.length - 1; i++) add(UPPER, i, UPPER.r[i], UPPER.r[i + 1]);
    for (let i = 0; i < LOWER.r.length; i++) add(LOWER, i, LOWER.r[i], i + 1 < LOWER.r.length ? LOWER.r[i + 1] : 44.6);
    const playTread = (k, a = 0.7) => {
      const t = treads[k]; if (!t) return; t.lit = now;
      const X = (t.x0 + t.x1) / 2, Y = (t.y0 + t.y1) / 2, Z = -(-t.z);
      fx(k < UPPER.r.length - 1 ? 'marimba' : 'pluck', X, Y, Z + 0.2, { f: pentF(MELODY[k % MELODY.length] + 2), a, d: 3.2 });
    };
    g.userData.playTread = playTread;
    // a walker you cannot see goes down the stair, waits, and comes back up a little faster
    let k = -1, dir = 1, next = 0, lastL = null;
    anim.push(() => {
      for (const t of treads) { const age = now - t.lit; t.bar.material.opacity = 0.08 + 0.9 * Math.max(0, 1 - age / 1.4) ** 2; }
      const L = listener();
      if (L) {                                                              // your own steps, in Walk
        const X = L.x, Y = -L.z, idx = treads.findIndex((t) => X >= t.x0 && X < t.x1 && Y >= t.y0 && Y <= t.y1 && Math.abs(L.y - 1.6 - t.z) < 0.6);
        if (idx >= 0 && idx !== lastL) playTread(idx, 0.6); lastL = idx >= 0 ? idx : lastL;
      }
      if (zone !== 'stair' || now < next) return;
      k += dir;
      if (k >= treads.length) { dir = -1; k = treads.length; next = now + 2.6; return; }
      if (k < 0) { dir = 1; k = -1; next = now + 3.2; return; }
      playTread(k, 0.65); const t = treads[k]; fx('step', (t.x0 + t.x1) / 2, (t.y0 + t.y1) / 2, t.z, { a: 0.35 });
      next = now + (dir > 0 ? 0.36 : 0.3) * (k === UPPER.r.length - 2 ? 2.2 : 1);
    });
    g.add(onWall(caption('A tuned stair', ['Every tread is a note. Someone is playing it.', 'Tap a step, or walk it yourself in Walk.'], 1.0), 45.0, 16.95, -2.2, -Math.PI / 2));
  }
  // ======================= 04 Gallery 1: twelve voices =======================
  const field = [];
  {
    const NOTES = [146.83, 164.81, 185.0, 207.65, 220.0, 246.94, 277.18, 293.66, 329.63, 369.99, 440.0, 554.37];   // D lydian, low to high
    const CHORDS = [[0, 4, 7, 9], [2, 5, 8, 10], [1, 4, 6, 9, 11], [0, 3, 7, 10], [2, 4, 6, 8, 11], [0, 5, 7, 9]];
    let k = 0;
    for (let j = 0; j < 4; j++) for (let i = 0; i < 3; i++) {
      const x = 30.8 + i * 3.0 + (j % 2) * 0.9, y = -0.6 + j * 2.9, hang = B1 + 2.05;
      const up = hit(M(x, y, hang), new THREE.Vector3(0, 1, 0), 8), top = up ? up.point.y : hang + 2.5;
      const thread = new THREE.Mesh(new THREE.CylinderGeometry(0.0012, 0.0012, top - M(0, 0, hang).y, 4), ink); thread.position.copy(M(x, y, hang)); thread.position.y = (top + M(0, 0, hang).y) / 2; g.add(thread);
      const spk = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.075, 0.11, 32), black); spk.position.copy(M(x, y, hang - 0.055)); spk.castShadow = true; g.add(spk);
      const col = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.11, 2.0, 32, 1, true), glow.clone()); col.position.copy(M(x, y, B1 + 1.0)); col.material.opacity = 0; col.renderOrder = 17; g.add(col);
      const pool = new THREE.Mesh(new THREE.CircleGeometry(0.42, 40), glow.clone()); onFloor(pool, x, y, B1 + 0.006); pool.material.opacity = 0; g.add(pool);
      const hitT = new THREE.Mesh(new THREE.SphereGeometry(0.34, 8, 6), new THREE.MeshBasicMaterial({ visible: false })); hitT.position.copy(spk.position); g.add(hitT);
      const v = { x, y, z: hang - 0.06, f: NOTES[k], idx: k, held: false, lvl: 0, d: null, col, pool };
      const tap = () => { v.held = !v.held; fx('bell', x, y, hang, { f: v.f * 2, a: 0.25, d: 4 }); return v.held ? `Held: ${Math.round(v.f)} Hz. It sings through every chord.` : `Released: ${Math.round(v.f)} Hz.`; };
      spk.userData.onTap = hitT.userData.onTap = tap; spk.userData.noClap = hitT.userData.noClap = true;
      field.push(v); k++;
    }
    let ci = 0, nextChord = 0;
    anim.push(() => {
      const s = sound(); const on = zone === 'voices';
      if (on && now > nextChord) { ci = (ci + 1) % CHORDS.length; nextChord = now + 8; }
      const chord = CHORDS[ci];
      for (const v of field) {
        if (s && s.ready && !v.d && on) v.d = s.drone(M(v.x, v.y, v.z), v.f, 'voice');
        const want = on && (v.held || chord.includes(v.idx)) ? 1 : 0;
        v.lvl += (want - v.lvl) * 0.025;
        if (v.d) { v.d.set(on ? 0.085 * want : 0, 1.4); v.d.vowel(0.5 + 0.5 * Math.sin(now * 0.13 + v.idx), 3); }
        const breathe = 0.75 + 0.25 * Math.sin(now * (1.1 + v.idx * 0.07) + v.idx);
        v.col.material.opacity = 0.16 * v.lvl * breathe + (v.held ? 0.05 : 0);
        v.pool.material.opacity = 0.22 * v.lvl * breathe;
      }
    });
    g.add(onWall(caption('Twelve voices', ['A slow choir, one note a speaker. The light is the sound.', 'Tap a speaker to hold its note.'], 1.2), 30.0, 3.2, B1 + 1.55, 0));
  }
  // ======================= 05 Gallery 2: the long room plays back =======================
  const marks = [];
  let head = null;
  {
    const X0 = 40.0, X1 = 68.6, LAP = 4.0;                 // the echo, slowed about 24x: there and back in four seconds
    const markG = new THREE.CircleGeometry(0.16, 32), markR = new THREE.RingGeometry(0.2, 0.215, 48);
    const noteAt = (Y) => pentF(Math.round((Y + 6.0) / 10.0 * 11) + 3);
    function addMark(X, Y) {
      if (marks.length >= 28) { const m = marks.shift(); g.remove(m.d, m.r); }
      const d = new THREE.Mesh(markG, glow.clone()), r = new THREE.Mesh(markR, ink.clone());
      onFloor(d, X, Y, B1 + 0.008); onFloor(r, X, Y, B1 + 0.009); d.material.opacity = 0.35; g.add(d, r);
      const m = { X, Y, d, r, f: noteAt(Y), lit: -10 }; marks.push(m); return m;
    }
    function tapFloor(X, Y) {
      const i = marks.findIndex((m) => Math.hypot(m.X - X, m.Y - Y) < 0.55);
      if (i >= 0) { const m = marks.splice(i, 1)[0]; g.remove(m.d, m.r); fx('tick', X, Y, B1, { a: 0.5 }); return; }
      const m = addMark(X, Y); fx('pluck', X, Y, B1 + 0.2, { f: m.f, a: 0.6, d: 2.6 }); m.lit = now;
    }
    g.userData.tapLong = tapFloor;
    [[43.5, -3.0], [47.0, 1.0], [51.2, -1.2], [55.0, 2.4], [58.8, -4.0], [62.0, 0.2], [65.5, -2.0]].forEach(([x, y]) => addMark(x, y));
    // the playhead: a thin sheet of light that crosses the room and comes back
    head = new THREE.Mesh(new THREE.PlaneGeometry(10.6, 2.6), glow.clone()); head.material.opacity = 0; head.rotation.y = Math.PI / 2; head.renderOrder = 17; g.add(head);
    const line = new THREE.Mesh(new THREE.PlaneGeometry(0.035, 10.6), glow.clone()); line.rotation.x = -Math.PI / 2; line.material.opacity = 0; g.add(line);
    let lastX = X0, lastDir = 1;
    anim.push(() => {
      const on = zone === 'long';
      const ph = (now % LAP) / LAP, X = ph < 0.5 ? X0 + (X1 - X0) * ph * 2 : X1 - (X1 - X0) * (ph - 0.5) * 2, dir = ph < 0.5 ? 1 : -1;
      head.position.copy(M(X, -1.2, B1 + 1.3)); line.position.copy(M(X, -1.2, B1 + 0.01));
      head.material.opacity += ((on ? 0.05 : 0) - head.material.opacity) * 0.05; line.material.opacity = head.material.opacity * 9;
      if (on) {
        for (const m of marks) if ((m.X - lastX) * (m.X - X) <= 0 && lastX !== X) { m.lit = now; fx('pluck', m.X, m.Y, B1 + 0.2, { f: m.f, a: 0.55, d: 2.4, bright: 0.3 + 0.5 * (m.X - X0) / (X1 - X0) }); ring(M(m.X, m.Y, B1 + 0.012), 1.6, 2.2, 0.6); }
        if (dir !== lastDir) fx('block', dir < 0 ? X1 + 0.4 : X0 - 0.4, -1.2, B1 + 1.2, { f: dir < 0 ? 980 : 1170, a: 0.45 });
      }
      for (const m of marks) { const age = now - m.lit; m.d.material.opacity = 0.3 + 0.7 * Math.max(0, 1 - age / 0.6); m.d.scale.setScalar(1 + 0.6 * Math.max(0, 1 - age / 0.4)); }
      lastX = X; lastDir = dir;
    });
    g.add(onWall(caption('The long room plays back', ['The light is the far wall\'s echo, slowed about', 'twenty-four times. It plays every mark it crosses.', 'Tap the floor to add a note, tap a mark to remove it.'], 1.3), 54.2, -7.24, B1 + 1.6, Math.PI / 2));
  }
  // ======================= 06 the court glass: rain on glass =======================
  const GL = { x0: 45.6, x1: 63.6, y: 11.97, z0: B1 + 0.3, z1: B1 + 9.5 };
  const glassNote = (Z) => pentF(5 + Math.round(Math.max(0, Math.min(1, (Z - GL.z0) / (GL.z1 - GL.z0))) * 11));
  function ringGlass(X, Z, a = 0.5, big = false) {
    fx('glass', X, GL.y, Z, { f: glassNote(Z), a, d: big ? 8 : 4.5 });
    ring(M(X, GL.y - 0.02, Z), big ? 3.2 : 1.7, big ? 1.6 : 1.1, big ? 0.95 : 0.8, true);
  }
  {
    g.add(onFloor(caption('Rain on glass', ['Each drop rings the glass, higher towards the roof.', 'Tap the glass to strike it.'], 1.0), 53.6, 10.6, B1 + 0.01));
    let next = 0;
    anim.push(() => {
      if (zone !== 'glass' || now < next) return;
      next = now + rnd(0.18, 0.9) * (Math.random() < 0.15 ? 3 : 1);
      ringGlass(rnd(GL.x0 + 0.5, Math.min(GL.x1, 58.5)), rnd(GL.z0 + 0.4, B1 + 4.8), rnd(0.18, 0.4));
    });
  }
  // ======================= 07 Gallery 3: one minute =======================
  let city = null;
  {
    g.add(onFloor(caption('One minute', ['The music steps back. A slow pulse, the city', 'through the walls, and a bell when the minute is up.'], 1.0), 0.2, -1.2, 0.01));
    const breath = new THREE.Mesh(new THREE.RingGeometry(0.985, 1, 128), ink.clone()); onFloor(breath, 1.2, -3.2, 0.012); breath.material.opacity = 0; g.add(breath);
    const arcM = ink.clone(); arcM.opacity = 0; let arc = null, arcK = -1;
    let start = -1, beat = 0;
    anim.push(() => {
      const on = zone === 'minute', s = sound();
      if (s && s.ready && !city && on) city = s.drone(M(-14, -2, 2), 210, 'city');
      if (city) city.set(on ? 0.06 : 0, 2.5);
      if (!on) { start = -1; breath.material.opacity *= 0.9; arcM.opacity *= 0.9; return; }
      if (start < 0) { start = now; beat = now + 1.2; }
      const t = now - start, el = t % 60;
      const b = (now % 1.0); breath.scale.setScalar(1.25 + 0.12 * Math.exp(-b * 4)); breath.material.opacity = 0.25 + 0.35 * Math.exp(-b * 3);
      const kk = Math.floor(el * 2);
      if (kk !== arcK) { arcK = kk; if (arc) { g.remove(arc); arc.geometry.dispose(); } arc = new THREE.Mesh(new THREE.RingGeometry(1.55, 1.565, 128, 1, Math.PI / 2, -Math.max(0.001, el / 60) * Math.PI * 2), arcM); onFloor(arc, 1.2, -3.2, 0.012); g.add(arc); }
      arcM.opacity = 0.6;
      if (now > beat) { beat += 1.0; const L = listener(); if (L) { fx('thud', L.x + 0.6, -L.z, L.y - 1.2, { f: 46, a: 0.45, wet: 0.2 }); fx('thud', L.x + 0.6, -L.z, L.y - 1.2, { f: 42, a: 0.26, delay: 0.24, wet: 0.2 }); } }
      if (el < 0.02 && t > 1) fx('bell', 1.2, -3.2, 2.0, { f: 293.66, a: 0.5, d: 12 });
    });
  }

  // ---------- which room the listener is in ----------
  anim.push(() => {
    const L = listener(), s = sound();
    let z = null;
    if (L) {
      const X = L.x, Y = -L.z, Z = L.y; for (const [n, f] of ZONES) if (f(X, Y, Z)) { z = n; break; }
      if (z === 'minute') { const h = hit(M(X, Y, 12), DOWN, 20); if (!h || h.point.y < Z + 0.4) z = 'plaza'; }   // Gallery 3 only under its roof
    }
    if (z !== zone) { zone = z; zoneT = now; if (s && s.quiet) s.quiet(z ? PAD[z] : 1, 2.0); }
    if (wind) wind.set(zone === 'plaza' ? 0.05 : 0, 2);
  });

  const credit = label([
    { t: 'Room Tone', size: 44, weight: 280, font: SERIF }, { t: ' ', size: 8 },
    { t: 'Seven rooms, seven instruments. Every sound you hear is drawn.', size: 18, color: '#bdb9b0' },
    { t: 'Our own show. Not affiliated with 21_21 DESIGN SIGHT. Sound on, headphones best.', size: 18, color: '#bdb9b0' },
  ], { w: 1.5, px: 1000 });
  g.add(onFloor(credit, 25.4, 15.6, 0));

  // a tap: the stair plays its tread, the long-room floor takes a note, the glass rings, anything else claps
  function clap(p) {
    const X = p.x, Y = -p.z, Z = p.y;
    const t = treads.findIndex((q) => X >= q.x0 - 0.05 && X < q.x1 + 0.05 && Y >= q.y0 - 0.1 && Y <= q.y1 + 0.1 && Math.abs(Z - q.z) < 0.25);
    if (t >= 0) { g.userData.playTread(t, 0.8); return 0; }
    if (Math.abs(Y - 12.0) < 0.25 && X > GL.x0 && X < GL.x1 && Z < GL.z1) { ringGlass(X, Z, 0.7, true); return 0; }
    if (Z < B1 + 0.08 && X > 39.4 && X < 69 && Y > -7.6 && Y < 4.4) { g.userData.tapLong(X, Y); return 0; }
    return clapAt(p);
  }

  scene.add(g);
  return {
    group: g, colliders: g.userData.colliders, clap,
    update: (t) => { now = t; anim.forEach((f) => f(t)); },
    leave: () => {
      const s = sound(); if (s && s.quiet) s.quiet(1); zone = null;
      for (const v of field) if (v.d) { v.d.stop(); v.d = null; }
      for (const d of [wind, city]) if (d) d.stop(); wind = city = null;
    },
  };
}
