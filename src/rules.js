// Read the Building: an independent homage to "Rules?" (21_21 DESIGN SIGHT, 2021).
// Tags pinned to the building's own rules (facts from the 2021 exhibition document, restated in our words),
// a floor vote and a field of squares that follow whatever rule you give them. All objects and texts are original.
import * as THREE from 'three';
import { G1E, M, B1, label, wallText, onWall, onFloor, box, strip } from './exhibit.js';

// Ando's restraint: no colour, no badges. A hairline, a small number, a few words, and only when you are near.
const INK = '#ece9e2';
const inkM = new THREE.MeshBasicMaterial({ color: 0xece9e2, toneMapped: false });
const lineInk = new THREE.MeshBasicMaterial({ color: 0xece9e2, toneMapped: false, transparent: true, opacity: 0.55 });
const NEAR = 8, FAR = 15;                                  // tags fade in between these distances (m)
const fade = (o, base) => { o.onBeforeRender = (r, s, cam) => { const d = cam.position.distanceTo(o.userData.at || o.position); o.material.opacity = base * THREE.MathUtils.smoothstep(FAR - d, 0, FAR - NEAR); }; };

function tag(g, n, title, anchor, at, info) {
  const W = 1024, H = 64;
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const c = cv.getContext('2d');
  c.fillStyle = INK; c.textBaseline = 'middle';
  c.font = '280 30px "Bella Gothic",Arial'; c.fillText(String(n).padStart(2, '0'), 0, H / 2 + 1);
  c.fillRect(52, H / 2, 56, 1);
  c.font = '560 19px "Bella Gothic",Arial'; c.letterSpacing = '5px'; c.fillText(title.toUpperCase(), 124, H / 2 + 1);
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, sizeAttenuation: false, toneMapped: false, transparent: true, depthWrite: false }));
  sp.center.set(0, 0.5); sp.scale.set(0.026 * W / H, 0.026, 1); sp.position.copy(M(...at)); sp.renderOrder = 20; sp.userData.info = info; fade(sp, 0.92); g.add(sp);
  const ln = new THREE.Line(new THREE.BufferGeometry().setFromPoints([M(...at), M(...anchor)]), new THREE.LineBasicMaterial({ color: 0xece9e2, toneMapped: false, transparent: true, depthWrite: false }));
  ln.userData.at = M(...anchor); fade(ln, 0.5); ln.renderOrder = 19; g.add(ln);
  const dot = new THREE.Mesh(new THREE.SphereGeometry(0.012, 10, 6), new THREE.MeshBasicMaterial({ color: 0xece9e2, toneMapped: false, transparent: true }));
  dot.position.copy(M(...anchor)); dot.userData.info = info; fade(dot, 1); g.add(dot);
  // a larger invisible target so the tag is easy to tap
  const hitT = new THREE.Mesh(new THREE.SphereGeometry(0.18, 8, 6), new THREE.MeshBasicMaterial({ visible: false })); hitT.position.copy(M(...anchor)); hitT.userData.info = info; g.add(hitT);
  return sp;
}

export async function buildRules(scene, fx = () => {}) {
  try { await Promise.all(['280 30px "Bella Gothic"', '560 19px "Bella Gothic"'].map((f) => document.fonts.load(f))); } catch (e) {}
  const g = new THREE.Group(); g.name = 'rules'; g.userData.colliders = [];
  const anim = [];

  // 01 the door handle
  tag(g, 1, 'The Ando handle', [18.86, 11.2, 1.0], [18.2, 10.3, 1.7],
    'The lever on this door is a stock model by Union (T215). Ando has used it since his early buildings, so often that its maker came to call it the Ando model.');

  // 02 formwork panels and separator holes, drawn on the Gallery 1 wall
  {
    const y0 = 0.6, z0 = B1 + 0.9, w = 1.8, h = 0.9, X = (y) => G1E.x(y) - 0.008;
    const x = X(y0 + 0.9);
    const bar = (b) => { b.rotation.y = G1E.rot; b.castShadow = false; b.material = lineInk; g.add(b); };
    for (let k = 0; k < 2; k++) {
      const zz = z0 + k * h;
      bar(box(0.003, w, 0.006, lineInk, X(y0 + w / 2), y0 + w / 2, zz - 0.006)); bar(box(0.003, w, 0.006, lineInk, X(y0 + w / 2), y0 + w / 2, zz + h - 0.006));
      bar(box(0.003, 0.006, h, lineInk, X(y0), y0, zz)); bar(box(0.003, 0.006, h, lineInk, X(y0 + w), y0 + w, zz));
      for (const dy of [0.3, 0.9, 1.5]) for (const dz of [0.225, 0.675]) {
        const r = new THREE.Mesh(new THREE.RingGeometry(0.034, 0.04, 24), lineInk);
        r.position.copy(M(X(y0 + dy) - 0.002, y0 + dy, zz + dz)); r.rotation.y = -Math.PI / 2 - 0.0477; g.add(r);
      }
    }
    tag(g, 2, '900 × 1800, six holes', [X(y0 + 0.9), y0 + 0.9, z0 + 1.35], [38.0, 2.7, B1 + 2.15],
      'Japanese formwork plywood is 900 × 1800 mm, and every panel here leaves six tie holes on a 450 × 600 mm grid. Count them across any wall: the grid sets the building\'s rhythm.');
    g.add(onWall(wallText('Rules you can read', 'formwork, ties, treads', 'Concrete remembers its moulds. A standard plywood sheet sets the size of every panel; the ties that hold the moulds apart leave six holes in each. Joints, stairs and openings all follow the same 450 and 600 mm steps.', 1.4), G1E.x(-1.3) - 0.012, -1.3, B1 + 1.7, G1E.yaw));
  }

  // 03 stair: treads and risers
  tag(g, 3, 'Tread 300, rise 150', [50.4, 15.6, -2.33], [49.4, 15.0, -1.75],
    'The rule: each tread is 300 mm, matching the tie-hole pitch, and each rise 150 mm, a sixth of a 900 mm panel. Our model rises about 171 mm per step, because the drawings we had were not that precise.');

  // 04 the solid steel mullions
  tag(g, 4, 'Solid steel, 235 × 69', [52.28, 11.97, -3.0], [52.9, 11.2, -2.4],
    'These mullions carry part of the roof and resist wind. To keep the glass as wide as possible they are solid steel, only 235 × 69 mm in section, and the tallest reach about 11.7 m.');

  // 05 the roof
  tag(g, 5, '16 mm, 54 m, 30 mm', [38.5, 8.0, 1.2], [39.8, 6.4, 2.0],
    'The roof is clad in 16 mm steel plate, welded on site because a 54 m roof could not be shipped in one piece. It is built to move by up to 30 mm with the heat.');

  // 06 a floor vote in Gallery 1 (counts live on this device only)
  {
    const KEY = '2121.vote';
    const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || { yes: 0, no: 0 }; } catch (e) { return { yes: 0, no: 0 }; } };
    let v = load();
    const pads = {};
    const draw = () => {
      for (const k of ['yes', 'no']) {
        if (pads[k].count) { g.remove(pads[k].count); pads[k].count.material.map.dispose(); }
        const l = label([{ t: String(v[k]), size: 96, weight: 560 }], { w: 0.6, px: 256, align: 'center', pad: 0.01 });
        onFloor(l, pads[k].x, pads[k].y - 0.25, B1 + 0.01); g.add(l); pads[k].count = l;
      }
    };
    for (const [k, x] of [['yes', 32.4], ['no', 35.4]]) {
      const pad = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1.6), new THREE.MeshStandardMaterial({ color: k === 'yes' ? 0xbab6ae : 0x2a2b2e, roughness: 0.7 }));
      onFloor(pad, x, 6.6, B1); g.add(pad);
      const t = label([{ t: k.toUpperCase(), size: 80, weight: 560, track: 8, color: '#f2f0ea' }], { w: 0.8, px: 320, align: 'center', pad: 0.01 });
      onFloor(t, x, 6.95, B1 + 0.005); g.add(t);
      pads[k] = { x, y: 6.6, mesh: pad };
      pad.userData.onTap = () => { fx('note', x, 6.6, B1 + 0.05, { f: k === 'yes' ? 880 : 587.33, a: 0.45, d: 1.8 }); fx('click', x, 6.6, B1 + 0.05, { f: k === 'yes' ? 1760 : 1175, a: 0.6 }); v = load(); v[k]++; localStorage.setItem(KEY, JSON.stringify(v)); draw(); return `Counted: ${k.toUpperCase()}. ${v.yes} yes, ${v.no} no on this device.`; };
      pad.userData.info = 'Tap to vote.';
    }
    draw();
    g.add(onFloor(label([{ t: 'SHOULD EVERY RULE BE WRITTEN DOWN?', size: 34, weight: 560, track: 3 }, { t: 'Step on a square to vote. Tallies stay on this device.', size: 20, color: '#bdb9b0' }], { w: 2.6, px: 1024 }), 33.9, 8.1, B1));
  }

  // 07 squares that follow a rule, in Gallery 2 (our own small simulation)
  {
    const N = 42, AREA = { x0: 43.0, x1: 65.5, y0: -5.6, y1: 3.6 }, S = 0.42;
    const inst = new THREE.InstancedMesh(new THREE.BoxGeometry(S, S, S), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.5, metalness: 0.3 }), N);
    inst.castShadow = true; inst.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    const col = new THREE.Color();
    for (let i = 0; i < N; i++) inst.setColorAt(i, col.set(i === 0 ? 0x1d1e21 : 0xe9e6df));
    g.add(inst);
    const rules = [
      { name: 'No rules', text: 'Everyone goes where they like. Watch how often they bump.' },
      { name: 'Keep left', text: 'Eastbound on the north side, westbound on the south: the Japanese road rule. Lanes appear by themselves.' },
      { name: 'Follow the one ahead', text: 'Each square follows the one ahead around a loop, keeping its distance. One rule, one queue.' },
    ];
    let rule = 1;
    const A = [...Array(N)].map((_, i) => ({ x: AREA.x0 + Math.random() * (AREA.x1 - AREA.x0), y: AREA.y0 + Math.random() * (AREA.y1 - AREA.y0), vx: 0, vy: 0, dir: i % 2 ? 1 : -1, s: Math.random() * 1000, h: Math.random() * 6.28 }));
    const signs = rules.map((r, i) => { const l = label([{ t: `RULE: ${r.name.toUpperCase()}`, size: 40, weight: 560, track: 4, color: '#ece9e2' }, { t: 'tap a square to change it', size: 22, color: '#bdb9b0' }], { w: 2.6, px: 1024 }); onFloor(l, 54.2, -6.6, B1); l.visible = i === rule; g.add(l); return l; });
    const cx = (AREA.x0 + AREA.x1) / 2, cy = (AREA.y0 + AREA.y1) / 2, rx = (AREA.x1 - AREA.x0) / 2 - 1, ry = (AREA.y1 - AREA.y0) / 2 - 1;
    const loopPt = (s) => { const t = s % (Math.PI * 2); return [cx + rx * Math.cos(t), cy + ry * Math.sin(t)]; };
    inst.userData.onTap = () => { fx('glass', cx, cy, B1 + 1, { f: [392, 587.33, 880][(rule + 1) % 3], a: 0.5, d: 3 }); rule = (rule + 1) % rules.length; signs.forEach((l, i) => (l.visible = i === rule)); A.forEach((a, i) => (a.s = (i / N) * Math.PI * 2)); return `Rule: ${rules[rule].name}. ${rules[rule].text}`; };
    inst.userData.info = 'Tap to change the rule.';
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), up = new THREE.Vector3(0, 1, 0), sc = new THREE.Vector3(1, 1, 1);
    // sound: order becomes rhythm. Under a rule, each square ticks as it crosses the middle of the hall (its lane sets the pitch);
    // with no rule, you hear the bumps instead.
    let last = 0, bumpT = 0;
    anim.push((t) => {
      const dt = Math.min(0.05, t - last || 0.016); last = t;
      for (const a of A) {
        let tx = 0, ty = 0, sp = 1.1;
        if (rule === 0) { a.h += (Math.random() - 0.5) * 2.5 * dt; tx = Math.cos(a.h); ty = Math.sin(a.h); }
        else if (rule === 1) { tx = a.dir; const lane = a.dir > 0 ? cy + 2.3 : cy - 2.3; ty = (lane - a.y) * 0.6; sp = 1.3; }
        else { a.s += dt * 0.11; const [px, py] = loopPt(a.s); tx = px - a.x; ty = py - a.y; sp = Math.min(1.6, Math.hypot(tx, ty) * 1.5); }
        const L = Math.hypot(tx, ty) || 1; a.vx += ((tx / L) * sp - a.vx) * Math.min(1, dt * 2.5); a.vy += ((ty / L) * sp - a.vy) * Math.min(1, dt * 2.5);
      }
      for (let i = 0; i < N; i++) for (let j = i + 1; j < N; j++) {          // nobody walks through anybody
        const a = A[i], b = A[j], dx = b.x - a.x, dy = b.y - a.y, d = Math.hypot(dx, dy);
        if (d < S * 1.5 && d > 1e-4) { if (rule === 0 && d < S * 1.2 && t - bumpT > 0.09) { bumpT = t; fx('wood', (a.x + b.x) / 2, (a.y + b.y) / 2, B1 + S / 2, { f: 520 + Math.random() * 160, a: 0.22 }); } const k = (S * 1.5 - d) * 0.5 / d; a.x -= dx * k; a.y -= dy * k; b.x += dx * k; b.y += dy * k; }
      }
      A.forEach((a, i) => {
        const px0 = a.x; a.x += a.vx * dt; a.y += a.vy * dt;
        if (rule && (px0 - cx) * (a.x - cx) < 0 && Math.abs(a.x - px0) < 1) fx('click', a.x, a.y, B1 + S / 2, { f: rule === 1 ? (a.y > cy ? 1318.5 : 987.77) : 1174.7 + (i % 5) * 73, a: 0.3 });
        if (rule === 1) { if (a.x > AREA.x1) a.x = AREA.x0; if (a.x < AREA.x0) a.x = AREA.x1; }
        if (a.x < AREA.x0) { a.x = AREA.x0; a.h = 0; } if (a.x > AREA.x1) { a.x = AREA.x1; a.h = Math.PI; }
        if (a.y < AREA.y0) { a.y = AREA.y0; a.h = Math.PI / 2; } if (a.y > AREA.y1) { a.y = AREA.y1; a.h = -Math.PI / 2; }
        q.setFromAxisAngle(up, Math.atan2(-a.vy, a.vx));
        m4.compose(M(a.x, a.y, B1 + S / 2), q, sc); inst.setMatrixAt(i, m4);
      });
      inst.instanceMatrix.needsUpdate = true;
    });
    g.add(onWall(wallText('Forty-two squares', 'one rule at a time', 'Rules make behaviour visible. Give these squares a single rule and the room organises itself; take it away and they collide. Tap a square to switch between no rules, keep left, and follow the one ahead.', 1.8), 54.2, -7.26, B1 + 1.7, Math.PI / 2));
  }

  const credit = label([{ t: 'READ THE BUILDING', size: 30, weight: 560, track: 4 }, { t: 'An independent homage to "Rules?" (21_21 DESIGN SIGHT, 2021).', size: 18, color: '#bdb9b0' }, { t: 'Not affiliated. Facts are drawn from its public materials; objects and texts are our own.', size: 18, color: '#bdb9b0' }], { w: 1.4, px: 900 });
  g.add(onFloor(credit, 29.9, 10.55, 0));

  scene.add(g);
  return { group: g, update: (t) => anim.forEach((f) => f(t)), colliders: g.userData.colliders };
}
