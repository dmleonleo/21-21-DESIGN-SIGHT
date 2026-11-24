// Room Tone: a show you hear. Made for this model; not an homage to, or a copy of, any past exhibition.
// Every tap is a clap: real first echoes are traced off the model (BVH rays, speed of sound 343 m/s) and played from
// where they bounce; the same wavefront is drawn on the floor a hundred times slower, so you can watch what you hear.
import * as THREE from 'three';
import { M, B1, label, onWall, onFloor } from './exhibit.js';

const C = 343, SLOW = 100;                              // m/s; the drawn ring moves at C / SLOW = 3.43 m/s
const SERIF = '"Bella Gothic",Arial,sans-serif';
const ink = new THREE.MeshBasicMaterial({ color: 0xece9e2, toneMapped: false, transparent: true, depthWrite: false, side: THREE.DoubleSide });
const black = new THREE.MeshStandardMaterial({ color: 0x0d0e10, roughness: 0.5, metalness: 0.4 });

function caption(title, lines, w = 1.2) {
  return label([{ t: title, size: 40, weight: 280, font: SERIF }, { t: ' ', size: 10 }, ...lines.map((t) => ({ t, size: 19, color: '#b8b4ac' }))], { w, px: 900 });
}
// directions for the first echoes: around the horizon, up, down and four diagonals
const DIRS = [];
for (let i = 0; i < 12; i++) { const a = (i / 12) * Math.PI * 2; DIRS.push(new THREE.Vector3(Math.cos(a), 0, Math.sin(a))); }
for (let i = 0; i < 6; i++) { const a = (i / 6) * Math.PI * 2 + 0.3; DIRS.push(new THREE.Vector3(Math.cos(a) * 0.7, 0.71, Math.sin(a) * 0.7).normalize()); }
DIRS.push(new THREE.Vector3(0, 1, 0), new THREE.Vector3(0, -1, 0));
const STAIR = { x0: 42, x1: 54.5, y0: 12.4, y1: 17.2 };
const PENT = [0, 2, 4, 7, 9];
const pentF = (i) => 146.83 * 2 ** ((PENT[((i % 5) + 5) % 5] + 12 * Math.floor(i / 5)) / 12);

export async function buildListen(scene, { fx = () => {}, sound = () => null, hit = () => null, listener = () => null, ground = () => null } = {}) {
  try { await document.fonts.load(`280 40px ${SERIF}`); } catch (e) {}
  const g = new THREE.Group(); g.name = 'listen'; g.userData.colliders = [];
  const anim = [];
  let now = 0;

  // ---------- wavefronts on the floor + dots where echoes return ----------
  const ringG = new THREE.RingGeometry(0.985, 1, 128);
  const rings = [...Array(10)].map(() => { const r = new THREE.Mesh(ringG, ink.clone()); r.rotation.x = -Math.PI / 2; r.visible = false; r.renderOrder = 18; g.add(r); return { m: r, t0: -1, max: 1 }; });
  const dotG = new THREE.CircleGeometry(0.05, 16);
  const dots = [...Array(40)].map(() => { const d = new THREE.Mesh(dotG, ink.clone()); d.visible = false; d.renderOrder = 18; g.add(d); return { m: d, t0: -1 }; });
  let ri = 0, di = 0;
  anim.push(() => {
    for (const r of rings) {
      if (r.t0 < 0) continue; const age = now - r.t0, rad = 0.05 + age * C / SLOW;
      if (rad > r.max) { r.t0 = -1; r.m.visible = false; continue; }
      r.m.visible = true; r.m.scale.setScalar(rad); r.m.material.opacity = 0.85 * (1 - rad / r.max) ** 1.5;
    }
    for (const d of dots) {
      if (d.t0 < 0) continue; const age = now - d.t0;
      if (age < 0) { d.m.visible = false; continue; }
      if (age > 2.2) { d.t0 = -1; d.m.visible = false; continue; }
      d.m.visible = true; d.m.material.opacity = Math.max(0, 1 - age / 2.2) * (age < 0.08 ? age / 0.08 : 1); d.m.scale.setScalar(1 + age * 0.8);
    }
  });

  const o3 = new THREE.Vector3(), nrm = new THREE.Vector3();
  // a clap at a point (three.js coordinates): direct sound, first echoes from the real surfaces, rings and dots
  function clap(p) {
    const s = sound(); const mp = { x: p.x, y: -p.z, z: p.y };
    const glass = Math.abs(mp.y - 12.03) < 0.2 && mp.x > 45 && mp.x < 64 && mp.z < -0.5;    // the court glass sings instead
    if (glass) {
      const h = Math.max(0, Math.min(1, (mp.z - B1) / 8));
      fx('glass', mp.x, mp.y, mp.z, { f: pentF(5 + Math.round(h * 9)), a: 0.55, d: 7 });
    } else fx('clap', mp.x, mp.y, mp.z, { a: 1 });
    // the floor under the clap carries the ring
    const fh = hit(o3.copy(p).add(nrm.set(0, 0.3, 0)), new THREE.Vector3(0, -1, 0), 8);
    const floorY = fh ? fh.point.y + 0.012 : p.y;
    const r = rings[ri++ % rings.length]; r.t0 = now; r.max = 16; r.m.position.set(p.x, floorY, p.z);
    // first-order echoes: one ray per direction from just off the surface
    const L = listener(); const src = o3.copy(p).add(nrm.set(0, 0.25, 0));
    if (L) { const toL = new THREE.Vector3(L.x - p.x, L.y - p.y, L.z - p.z); if (toL.length() > 0.5) src.addScaledVector(toL.normalize(), 0.2); }
    let n = 0;
    for (const d of DIRS) {
      const h = hit(src, d, 70); if (!h || h.distance < 0.6) continue;
      const q = h.point, dist = h.distance;
      // path: clap -> wall -> listener
      const back = L ? Math.hypot(q.x - L.x, q.y - L.y, q.z - L.z) : dist;
      const delay = (dist + back) / C, a = Math.min(0.55, 2.2 / (dist + back));
      if (a < 0.03) continue;
      if (!glass) fx('clap', q.x, -q.z, q.y, { delay, a, wet: 0.25 });
      const dd = dots[di++ % dots.length]; dd.t0 = now + dist / (C / SLOW); dd.m.position.copy(q).addScaledVector(d, -0.02);
      dd.m.lookAt(o3.copy(q).sub(d)); n++;
    }
    return n;
  }

  // ---------- 01 plaza: a white circle to clap in ----------
  {
    const x = 8.0, y = -1.6, z = (ground(x, y) ?? -0.08) + 0.01;
    const c = new THREE.Mesh(new THREE.RingGeometry(0.58, 0.6, 96), ink); onFloor(c, x, y, z); g.add(c);
    g.add(onFloor(caption('Clap', ['Tap anywhere. Every surface answers.', 'Out here, the garden barely does.'], 0.9), x - 0.45, y - 1.05, z));
  }
  // ---------- 02 lobby: the same, indoors ----------
  {
    const c = new THREE.Mesh(new THREE.RingGeometry(0.58, 0.6, 96), ink); onFloor(c, 28.2, 12.2, 0.01); g.add(c);
    g.add(onFloor(caption('Again, inside', ['Concrete, glass, a low ceiling.', 'The white dots show where the echoes came from.'], 1.0), 27.6, 11.0, 0.01));
  }
  // ---------- 03 the stair: every step a note ----------
  {
    let lastStep = null;
    anim.push(() => {
      const L = listener(); if (!L) return; const X = L.x, Y = -L.z, Z = L.y;
      if (X < STAIR.x0 || X > STAIR.x1 || Y < STAIR.y0 || Y > STAIR.y1 || Z > 2.2 || Z < B1 + 1) { lastStep = null; return; }
      const step = Math.round((Z - 1.6 - B1) / 0.15);                       // the eye is 1.6 m above the tread
      if (lastStep !== null && step !== lastStep) fx('note', X, Y, Z - 1.5, { f: pentF(Math.max(0, Math.min(19, Math.round(step / 2)))), a: 0.5, d: 2.2 });
      lastStep = step;
    });
    g.add(onWall(caption('A scale of steps', ['In Walk, each step plays the next note.', 'Down the stair, down the scale.'], 1.0), 45.0, 16.95, -2.2, -Math.PI / 2));
  }
  // ---------- 04 Gallery 1: twelve voices ----------
  const field = [];
  {
    const NOTES = [146.83, 164.81, 185.0, 207.65, 220.0, 246.94, 277.18, 293.66, 329.63, 369.99, 440.0, 554.37];   // D lydian
    let k = 0;
    for (let j = 0; j < 4; j++) for (let i = 0; i < 3; i++) {
      const x = 30.8 + i * 3.0 + (j % 2) * 0.9, y = -0.6 + j * 2.9, hang = B1 + 2.05;
      const up = hit(M(x, y, hang), new THREE.Vector3(0, 1, 0), 8), top = up ? up.point.y : hang + 2.5;
      const thread = new THREE.Mesh(new THREE.CylinderGeometry(0.0012, 0.0012, top - M(0, 0, hang).y, 4), ink); thread.position.copy(M(x, y, hang)); thread.position.y = (top + M(0, 0, hang).y) / 2; g.add(thread);
      const spk = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.075, 0.11, 32), black); spk.position.copy(M(x, y, hang - 0.055)); spk.castShadow = true; g.add(spk);
      const ring = new THREE.Mesh(new THREE.RingGeometry(0.08, 0.088, 48), ink.clone()); ring.rotation.x = Math.PI / 2; ring.position.copy(M(x, y, hang - 0.115)); g.add(ring);
      const hitT = new THREE.Mesh(new THREE.SphereGeometry(0.32, 8, 6), new THREE.MeshBasicMaterial({ visible: false })); hitT.position.copy(spk.position); g.add(hitT);
      const v = { x, y, z: hang - 0.06, f: NOTES[k], on: true, d: null, ring, ph: Math.random() * 6 };
      const tap = () => { v.on = !v.on; fx('click', x, y, hang, { f: v.f * 4, a: 0.4 }); return v.on ? `Back on: ${Math.round(v.f)} Hz.` : `Silenced: ${Math.round(v.f)} Hz. Tap again to bring it back.`; };
      spk.userData.onTap = hitT.userData.onTap = tap; spk.userData.noClap = hitT.userData.noClap = true;
      field.push(v); k++;
    }
    anim.push(() => {
      const s = sound(); const L = listener();
      const near = L && L.y < -1.2 && L.x > 28 && L.x < 40 && -L.z > -3 && -L.z < 11;
      for (const v of field) {
        if (s && s.ready && !v.d && L && L.y < 0) v.d = s.drone(M(v.x, v.y, v.z), v.f, 'sine');
        if (v.d) v.d.set(near && v.on ? 0.07 : 0, 0.6);
        v.ring.material.opacity = v.on ? 0.45 + 0.4 * Math.sin(now * (1.2 + v.f / 400) + v.ph) ** 2 : 0.12;
      }
    });
    g.add(onWall(caption('Twelve voices', ['Each speaker holds one note. Walk between them.', 'Tap one to silence it. Headphones help.'], 1.2), 30.0, 3.2, B1 + 1.55, 0));
  }
  // ---------- 05 Gallery 2: the long room ----------
  {
    const c = new THREE.Mesh(new THREE.RingGeometry(0.58, 0.6, 96), ink); onFloor(c, 44.5, -1.0, B1 + 0.01); g.add(c);
    g.add(onWall(caption('The long room', ['About thirty metres. Clap: the far wall answers', 'under two tenths of a second later. The ring is', 'the same sound, slowed a hundred times.'], 1.3), 54.2, -7.24, B1 + 1.6, Math.PI / 2));
  }
  // ---------- 06 the court glass ----------
  g.add(onFloor(caption('Tall glass', ['Tap the glass. It rings higher towards the roof.'], 1.0), 53.6, 10.6, B1 + 0.01));
  // ---------- 07 Gallery 3: one minute ----------
  let quiet = false, beat = 0;
  {
    g.add(onFloor(caption('One minute', ['The music steps back. Only a slow pulse stays.', 'Stay as long as you like.'], 1.0), 0.2, -1.2, 0.01));
    anim.push(() => {
      const s = sound(), L = listener(); if (!s) return;
      const inG3 = L && L.x > -7 && L.x < 12 && -L.z > -7 && -L.z < 9 && L.y > -1 && L.y < 5;
      if (inG3 !== quiet) { quiet = inG3; s.quiet(inG3 ? 0 : 1, inG3 ? 2.5 : 1.2); }
      if (quiet && now > beat) { beat = now + 1.0; fx('thud', L.x + 0.6, -L.z, L.y - 1.2, { f: 46, a: 0.5, wet: 0.2 }); fx('thud', L.x + 0.6, -L.z, L.y - 1.2, { f: 42, a: 0.3, delay: 0.24, wet: 0.2 }); }
    });
  }

  const credit = label([
    { t: 'Room Tone', size: 44, weight: 280, font: SERIF }, { t: ' ', size: 8 },
    { t: 'A show you hear, made for this model. Echoes are traced off the building itself.', size: 18, color: '#bdb9b0' },
    { t: 'Not affiliated with 21_21 DESIGN SIGHT. Sound on, headphones best.', size: 18, color: '#bdb9b0' },
  ], { w: 1.5, px: 1000 });
  g.add(onFloor(credit, 25.4, 15.6, 0));

  scene.add(g);
  return {
    group: g, colliders: g.userData.colliders, clap,
    update: (t) => { now = t; anim.forEach((f) => f(t)); },
    leave: () => { const s = sound(); if (s) s.quiet(1); quiet = false; for (const v of field) if (v.d) v.d.set(0, 0.3); },
  };
}
