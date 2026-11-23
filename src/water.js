// Still Water: an independent homage to "water" (21_21 DESIGN SIGHT, 2007, directed by Taku Satoh).
// No works from that show are reproduced: only still water, falling drops and light, made here from plain geometry.
import * as THREE from 'three';
import { M, B1, label, onWall, onFloor } from './exhibit.js';

const SERIF = '"Bella Gothic",Arial,sans-serif';
const MAXD = 12;
const rimM = new THREE.MeshStandardMaterial({ color: 0x5e5c58, roughness: 0.85 });
const dropM = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.05, metalness: 0, transparent: true, opacity: 0.7, envMapIntensity: 1.4 });

// water: a dark dielectric mirror whose normal is bent by expanding rings (horizontal surfaces only)
function waterMat(env = 1) {
  const drops = { value: [...Array(MAXD)].map(() => new THREE.Vector4(0, 0, -99, 0)) };
  const time = { value: 0 };
  const m = new THREE.MeshStandardMaterial({ color: 0x07090a, roughness: 0.035, metalness: 0, envMapIntensity: env });
  m.onBeforeCompile = (sh) => {
    sh.uniforms.uDrops = drops; sh.uniforms.uTime = time;
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vW;')
      .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvW = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
varying vec3 vW; uniform vec4 uDrops[${MAXD}]; uniform float uTime;
vec2 ripple(vec2 p) {
  vec2 g = vec2(0.0);
  for (int i = 0; i < ${MAXD}; i++) {
    vec4 d = uDrops[i]; float age = uTime - d.z;
    if (age < 0.0 || age > 7.0) continue;
    vec2 v = p - d.xy; float r = length(v) + 1e-4; float k = r - age * 0.42;
    float e = exp(-k * k * 18.0) * exp(-age * 0.55) * d.w / (1.0 + r * 2.5);
    g += (v / r) * sin(k * 34.0) * e;
  }
  return g;
}`).replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
{ vec2 gr = ripple(vec2(vW.x, -vW.z)) * 0.55; normal = normalize((viewMatrix * vec4(-gr.x, 1.0, gr.y, 0.0)).xyz); }`);
  };
  m.customProgramCacheKey = () => 'water';
  m.userData = { drops, time, next: 0 };
  m.drop = (x, y, amp = 1) => { const d = drops.value[m.userData.next++ % MAXD]; d.set(x, y, time.value, amp); };
  return m;
}

// a round basin set into the floor: thin concrete lip, water a few millimetres below it
function basin(g, x, y, z, r, env) {
  const w = waterMat(env);
  const rim = new THREE.Mesh(new THREE.RingGeometry(r, r + 0.035, 72), rimM); onFloor(rim, x, y, z + 0.004); rim.receiveShadow = true; g.add(rim);
  const water = new THREE.Mesh(new THREE.CircleGeometry(r, 72), w); onFloor(water, x, y, z + 0.002); water.receiveShadow = true; g.add(water);
  return w;
}

// one small text, set quietly in serif and grotesk
function caption(title, lines, w = 1.2) {
  return label([
    { t: title, size: 40, weight: 280, font: SERIF },
    { t: ' ', size: 10 },
    ...lines.map((t) => ({ t, size: 19, color: '#b8b4ac' })),
  ], { w, px: 900 });
}

export async function buildWater(scene, { ground = () => null } = {}) {
  try { await Promise.all([document.fonts.load(`280 40px ${SERIF}`), document.fonts.load('560 19px "Bella Gothic"')]); } catch (e) {}
  const g = new THREE.Group(); g.name = 'water'; g.userData.colliders = [];
  const anim = [], mats = [];
  const rnd = (a, b) => a + Math.random() * (b - a);

  // 01 Plaza: a line of water, about 10 m long and 120 mm wide, cut into the paving beside the path
  {
    const x0 = 5.84, y0 = -4.85, x1 = 12.0, y1 = 3.6, len = Math.hypot(x1 - x0, y1 - y0);
    const w = waterMat(1.2); mats.push(w);
    // the ground here is not level: lay the strip on it, 40 pieces, each a few millimetres proud
    const N = 48, nx = -(y1 - y0) / len, ny = (x1 - x0) / len;
    const strip2 = (half, dz) => {
      const pos = [], idx = [];
      for (let i = 0; i <= N; i++) {
        const k = i / N, x = x0 + (x1 - x0) * k, y = y0 + (y1 - y0) * k, z = (ground(x, y) ?? -0.08) + dz;
        const a = M(x + nx * half, y + ny * half, z), b = M(x - nx * half, y - ny * half, z);
        pos.push(a.x, a.y, a.z, b.x, b.y, b.z);
        if (i < N) { const j = i * 2; idx.push(j, j + 1, j + 2, j + 1, j + 3, j + 2); }
      }
      const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); geo.setIndex(idx); geo.computeVertexNormals();
      return geo;
    };
    const m = new THREE.Mesh(strip2(0.06, 0.012), w); m.material.side = THREE.DoubleSide; g.add(m);
    const lip = new THREE.Mesh(strip2(0.095, 0.008), rimM); g.add(lip);
    let t0 = 0;
    anim.push((t) => { if (t > t0) { t0 = t + rnd(2.5, 5); const k = Math.random(); w.drop(x0 + (x1 - x0) * k, y0 + (y1 - y0) * k, 0.6); } });
    g.add(onFloor(caption('A line', ['Ten metres of water, one hand wide.', 'It points the way in.'], 0.9), 7.2, -0.2, (ground(7.2, -0.2) ?? -0.08), Math.atan2(y1 - y0, x1 - x0) - Math.PI / 2));
  }

  // 02 Lobby: one drop, every few seconds, into a black basin
  {
    const x = 29.0, y = 11.7, r = 0.85;
    const w = basin(g, x, y, 0, r, 0.9); mats.push(w);
    // the thread it falls from: a hairline from the ceiling
    const top = 3.2, thread = new THREE.Mesh(new THREE.CylinderGeometry(0.0015, 0.0015, top - 1.2, 4), new THREE.MeshBasicMaterial({ color: 0xd9d6cf, transparent: true, opacity: 0.35 }));
    thread.position.copy(M(x, y, (top + 1.2) / 2)); g.add(thread);
    const d = new THREE.Mesh(new THREE.SphereGeometry(0.012, 12, 8), dropM); d.scale.set(1, 1.6, 1); g.add(d);
    let t0 = 1, falling = -1;
    anim.push((t) => {
      if (falling < 0 && t > t0) falling = t;
      if (falling >= 0) {
        const s = t - falling, z = 1.2 - 4.9 * s * s;
        if (z <= 0) { w.drop(x, y, 1.4); falling = -1; t0 = t + 4.5; d.visible = false; }
        else { d.visible = true; d.position.copy(M(x, y, z)); }
      } else { d.visible = true; d.position.copy(M(x, y, 1.2 - Math.min(1, (t0 - t) < 1 ? 1 - (t0 - t) : 0) * 0.004)); }
    });
    d.userData.info = 'One drop every four and a half seconds. Wait for the rings to reach the rim before the next one falls.';
    g.add(onFloor(caption('One drop', ['Wait for it.'], 0.6), x - 0.3, y - 1.35, 0));
  }

  // 03 The void by the stair: seven threads of falling water, 8.6 m from the roof to the basement
  {
    const cx = 47.6, cy = 12.0, w = basin(g, cx, cy, B1, 1.15, 0.6); mats.push(w);
    const N = 7, threads = [...Array(N)].map((_, i) => { const a = i / N * Math.PI * 2; return { x: cx + Math.cos(a) * 0.62 * (i % 2 ? 1 : 0.45), y: cy + Math.sin(a) * 0.62 * (i % 2 ? 1 : 0.45) }; });
    const PER = 5, DROPS = N * PER, top = 2.6;
    const inst = new THREE.InstancedMesh(new THREE.SphereGeometry(0.016, 8, 6), dropM, DROPS); inst.instanceMatrix.setUsage(THREE.DynamicDrawUsage); g.add(inst);
    const st = [...Array(DROPS)].map((_, i) => ({ th: threads[i % N], t: -rnd(0, 6) }));
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), sc = new THREE.Vector3(1, 3.2, 1);
    let last = 0;
    anim.push((t) => {
      const dt = Math.min(0.05, t - last || 0.016); last = t;
      st.forEach((s, i) => {
        s.t += dt;
        const z = top - 4.9 * Math.max(0, s.t) ** 2;
        if (z <= B1) { w.drop(s.th.x, s.th.y, 0.8); s.t = -rnd(0.4, 3.5); }
        sc.y = 1 + Math.min(9, Math.max(0, s.t) * 7);
        m4.compose(M(s.th.x, s.th.y, s.t < 0 ? top + 50 : z), q, sc); inst.setMatrixAt(i, m4);
      });
      inst.instanceMatrix.needsUpdate = true;
    });
    for (const th of threads) { const l = new THREE.Mesh(new THREE.CylinderGeometry(0.004, 0.004, 0.02, 6), rimM); l.position.copy(M(th.x, th.y, top + 0.01)); g.add(l); }
    g.add(onFloor(caption('Falling', ['Seven drops let go from the roof.', 'Eight and a half metres: about 1.3 seconds.'], 0.95), cx - 2.0, cy + 1.5, B1, -0.2));
  }

  // 04 Gallery 1: rain on nine still basins
  {
    const ws = [];
    for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) { const w = basin(g, 34.3 + i * 0.95, 2.0 + j * 0.95, B1, 0.36, 0.5); ws.push({ w, x: 34.3 + i * 0.95, y: 2.0 + j * 0.95 }); mats.push(w); }
    let t0 = 0;
    anim.push((t) => { if (t > t0) { t0 = t + rnd(0.08, 0.5); const b = ws[(Math.random() * ws.length) | 0], a = rnd(0, 6.28), r = Math.sqrt(Math.random()) * 0.3; b.w.drop(b.x + Math.cos(a) * r, b.y + Math.sin(a) * r, rnd(0.3, 0.8)); } });
    g.add(onWall(caption('Rain, indoors', ['Nine basins, one weather.', 'No two rings meet the same way twice.'], 1.0), 30.0, 3.2, B1 + 1.55, 0));
  }

  // 05 Gallery 2: one long still plane. Every so often, a single ring crosses it.
  {
    const x0 = 46.5, x1 = 60.5, y0 = -1.4, y1 = 2.1;
    const w = waterMat(0.75); mats.push(w);
    const pool = new THREE.Mesh(new THREE.PlaneGeometry(x1 - x0, y1 - y0), w); onFloor(pool, (x0 + x1) / 2, (y0 + y1) / 2, B1 + 0.002); g.add(pool);
    const edge = new THREE.Mesh(new THREE.PlaneGeometry(x1 - x0 + 0.08, y1 - y0 + 0.08), rimM); onFloor(edge, (x0 + x1) / 2, (y0 + y1) / 2, B1 + 0.001); g.add(edge);
    let t0 = 3;
    anim.push((t) => { if (t > t0) { t0 = t + rnd(6, 11); w.drop(rnd(x0 + 1, x1 - 1), rnd(y0 + 0.5, y1 - 0.5), 1.2); } });
    pool.userData.info = 'Fourteen metres of water a few millimetres deep. Stand at the end and the ceiling lights lie down in it.';
    g.add(onWall(caption('Still', ['Fourteen metres of water, millimetres deep.', 'The room, once more, upside down.'], 1.1), 54.2, -7.24, B1 + 1.6, Math.PI / 2));
  }

  // 06 Sunken court: a sheet of water over the whole court floor, the sky laid at your feet
  {
    const sh = new THREE.Shape([[45.0, 8.35], [63.3, 8.35], [68.3, 16.9], [66.0, 16.9], [45.0, 9.3]].map(([x, y]) => new THREE.Vector2(x, y)));
    const w = waterMat(2.2); mats.push(w);
    const sheet = new THREE.Mesh(new THREE.ShapeGeometry(sh), w); sheet.rotation.x = -Math.PI / 2; sheet.position.y = B1 + 0.012; g.add(sheet);
    let t0 = 0;
    anim.push((t) => { if (t > t0) { t0 = t + rnd(1.5, 4); const x = rnd(47, 64), y = rnd(8.8, 8.8 + (x - 45) * 0.36 - 0.4); w.drop(x, y, 0.7); } });
    sheet.userData.info = 'A few millimetres of water over the court. Look down and the glass, the roof edge and the sky are all there.';
  }

  const credit = label([
    { t: 'Still Water', size: 44, weight: 280, font: SERIF },
    { t: ' ', size: 8 },
    { t: 'An independent homage to "water" (21_21 DESIGN SIGHT, 2007).', size: 18, color: '#bdb9b0' },
    { t: 'Not affiliated. No works from that exhibition are shown; everything here is made for this model.', size: 18, color: '#bdb9b0' },
  ], { w: 1.5, px: 1000 });
  g.add(onFloor(credit, 25.4, 15.6, 0));

  scene.add(g);
  return { group: g, update: (t) => { for (const m of mats) m.userData.time.value = t; anim.forEach((f) => f(t)); }, colliders: g.userData.colliders };
}
