// Read the Building: an independent homage to "Rules?" (21_21 DESIGN SIGHT, 2021).
// Tags pinned to the building's own rules (facts from the 2021 exhibition document, restated in our words),
// a floor vote and a field of squares that follow whatever rule you give them. All objects and texts are original.
import * as THREE from 'three';
import { G1E, M, B1, label, wallText, onWall, onFloor, box, strip } from './exhibit.js';

const BLUE = '#4d6bff';
const blue = new THREE.MeshBasicMaterial({ color: 0x4d6bff, toneMapped: false });
const leadM = new THREE.LineBasicMaterial({ color: 0x4d6bff, toneMapped: false, transparent: true, opacity: 0.9 });

// a numbered tag that always faces you, a leader line and a dot on the thing it describes
function tag(g, n, title, anchor, at, info) {
  const cv = document.createElement('canvas'); cv.width = 768; cv.height = 128;
  const c = cv.getContext('2d');
  c.fillStyle = BLUE; c.beginPath(); c.arc(64, 64, 44, 0, Math.PI * 2); c.fill();
  c.fillStyle = '#fff'; c.font = '1000 40px "Bella Gothic",Arial'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(String(n).padStart(2, '0'), 64, 66);
  c.textAlign = 'left'; c.fillStyle = '#f2f0ea'; c.font = '1000 30px "Bella Gothic",Arial'; c.letterSpacing = '3px'; c.fillText(title.toUpperCase(), 128, 66);
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, sizeAttenuation: false, toneMapped: false }));
  sp.center.set(64 / 768, 0.5); sp.scale.set(0.39, 0.065, 1); sp.position.copy(M(...at)); sp.renderOrder = 20; sp.userData.info = info; g.add(sp);
  const ln = new THREE.Line(new THREE.BufferGeometry().setFromPoints([M(...at), M(...anchor)]), leadM); ln.renderOrder = 19; g.add(ln);
  const dot = new THREE.Mesh(new THREE.SphereGeometry(0.035, 12, 8), blue); dot.position.copy(M(...anchor)); dot.userData.info = info; g.add(dot);
  return sp;
}

export async function buildRules(scene) {
  const g = new THREE.Group(); g.name = 'rules'; g.userData.colliders = [];
  const anim = [];

  // 01 the door handle
  tag(g, 1, 'The Ando handle', [18.86, 11.2, 1.0], [18.2, 10.3, 1.7],
    'The lever on this door is a stock model by Union (T215). Ando has used it since his early buildings, so often that the maker came to call it the Ando model.');

  // 02 formwork panels and separator holes, drawn on the Gallery 1 wall
  {
    const y0 = 0.6, z0 = B1 + 0.9, w = 1.8, h = 0.9, X = (y) => G1E.x(y) - 0.008;
    const x = X(y0 + 0.9);
    const bar = (b) => { b.rotation.y = G1E.rot; b.castShadow = false; g.add(b); };
    for (let k = 0; k < 2; k++) {
      const zz = z0 + k * h;
      bar(box(0.004, w, 0.012, blue, X(y0 + w / 2), y0 + w / 2, zz - 0.006)); bar(box(0.004, w, 0.012, blue, X(y0 + w / 2), y0 + w / 2, zz + h - 0.006));
      bar(box(0.004, 0.012, h, blue, X(y0), y0, zz)); bar(box(0.004, 0.012, h, blue, X(y0 + w), y0 + w, zz));
      for (const dy of [0.3, 0.9, 1.5]) for (const dz of [0.225, 0.675]) {
        const r = new THREE.Mesh(new THREE.RingGeometry(0.03, 0.042, 20), blue);
        r.position.copy(M(X(y0 + dy) - 0.002, y0 + dy, zz + dz)); r.rotation.y = -Math.PI / 2 - 0.0477; g.add(r);
      }
    }
    tag(g, 2, '900 × 1800, six holes', [X(y0 + 0.9), y0 + 0.9, z0 + 1.35], [38.0, 2.7, B1 + 2.15],
      'Japanese formwork plywood is 900 × 1800 mm, and every panel here leaves six tie holes on a 450 × 600 mm grid. Count them across any wall: the grid is the building\'s rhythm.');
    g.add(onWall(wallText('Rules you can read', 'formwork, ties, treads', 'Concrete remembers its moulds. A standard plywood sheet sets the size of every panel; the ties that hold the moulds apart leave six holes in each. Joints, stairs and openings are counted in the same 450 and 600 mm steps.', 1.4), G1E.x(-1.3) - 0.012, -1.3, B1 + 1.7, G1E.yaw));
  }

  // 03 stair: treads and risers
  tag(g, 3, 'Tread 300, rise 150', [50.4, 15.6, -2.33], [49.4, 15.0, -1.75],
    'The rule: each tread is 300 mm, matching the tie-hole pitch, and each rise 150 mm, a sixth of a 900 mm panel. Our reconstruction rises about 171 mm per step; the drawings we had were not that precise.');

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
        const l = label([{ t: String(v[k]), size: 96, weight: 1000 }], { w: 0.6, px: 256, align: 'center', pad: 0.01 });
        onFloor(l, pads[k].x, pads[k].y - 0.25, B1 + 0.01); g.add(l); pads[k].count = l;
      }
    };
    for (const [k, x] of [['yes', 32.4], ['no', 35.4]]) {
      const pad = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1.6), new THREE.MeshStandardMaterial({ color: k === 'yes' ? 0x4d6bff : 0x26272a, roughness: 0.7 }));
      onFloor(pad, x, 6.6, B1); g.add(pad);
      const t = label([{ t: k.toUpperCase(), size: 80, weight: 1000, track: 8, color: '#f2f0ea' }], { w: 0.8, px: 320, align: 'center', pad: 0.01 });
      onFloor(t, x, 6.95, B1 + 0.005); g.add(t);
      pads[k] = { x, y: 6.6, mesh: pad };
      pad.userData.onTap = () => { v = load(); v[k]++; localStorage.setItem(KEY, JSON.stringify(v)); draw(); return `Counted: ${k.toUpperCase()}. ${v.yes} yes, ${v.no} no on this device.`; };
      pad.userData.info = 'Tap to vote.';
    }
    draw();
    g.add(onFloor(label([{ t: 'SHOULD EVERY RULE BE WRITTEN DOWN?', size: 34, weight: 1000, track: 3 }, { t: 'Step on a square to vote. Tallies stay on this device.', size: 20, color: '#bdb9b0' }], { w: 2.6, px: 1024 }), 33.9, 8.1, B1));
  }

  // 07 squares that follow a rule, in Gallery 2 (our own small simulation)
  {
    const N = 42, AREA = { x0: 43.0, x1: 65.5, y0: -5.6, y1: 3.6 }, S = 0.42;
    const inst = new THREE.InstancedMesh(new THREE.BoxGeometry(S, S, S), new THREE.MeshStandardMaterial({ color: 0x1d1e21, roughness: 0.5, metalness: 0.3 }), N);
    inst.castShadow = true; inst.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    const col = new THREE.Color();
    for (let i = 0; i < N; i++) inst.setColorAt(i, col.set(i === 0 ? 0x4d6bff : 0xe9e6df));
    g.add(inst);
    const rules = [
      { name: 'No rules', text: 'Everyone goes where they like. Watch how often they bump.' },
      { name: 'Keep left', text: 'Eastbound on the north side, westbound on the south: the Japanese road rule. Lanes appear by themselves.' },
      { name: 'Follow the one ahead', text: 'Each square follows the next one round a loop, keeping a gap. One rule, one queue.' },
    ];
    let rule = 1;
    const A = [...Array(N)].map((_, i) => ({ x: AREA.x0 + Math.random() * (AREA.x1 - AREA.x0), y: AREA.y0 + Math.random() * (AREA.y1 - AREA.y0), vx: 0, vy: 0, dir: i % 2 ? 1 : -1, s: Math.random() * 1000, h: Math.random() * 6.28 }));
    const signs = rules.map((r, i) => { const l = label([{ t: `RULE: ${r.name.toUpperCase()}`, size: 40, weight: 1000, track: 4, color: '#8ea0ff' }, { t: 'tap a square to change it', size: 22, color: '#bdb9b0' }], { w: 2.6, px: 1024 }); onFloor(l, 54.2, -6.6, B1); l.visible = i === rule; g.add(l); return l; });
    const cx = (AREA.x0 + AREA.x1) / 2, cy = (AREA.y0 + AREA.y1) / 2, rx = (AREA.x1 - AREA.x0) / 2 - 1, ry = (AREA.y1 - AREA.y0) / 2 - 1;
    const loopPt = (s) => { const t = s % (Math.PI * 2); return [cx + rx * Math.cos(t), cy + ry * Math.sin(t)]; };
    inst.userData.onTap = () => { rule = (rule + 1) % rules.length; signs.forEach((l, i) => (l.visible = i === rule)); A.forEach((a, i) => (a.s = (i / N) * Math.PI * 2)); return `Rule: ${rules[rule].name}. ${rules[rule].text}`; };
    inst.userData.info = 'Tap to change the rule.';
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), up = new THREE.Vector3(0, 1, 0), sc = new THREE.Vector3(1, 1, 1);
    let last = 0;
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
        if (d < S * 1.5 && d > 1e-4) { const k = (S * 1.5 - d) * 0.5 / d; a.x -= dx * k; a.y -= dy * k; b.x += dx * k; b.y += dy * k; }
      }
      A.forEach((a, i) => {
        a.x += a.vx * dt; a.y += a.vy * dt;
        if (rule === 1) { if (a.x > AREA.x1) a.x = AREA.x0; if (a.x < AREA.x0) a.x = AREA.x1; }
        if (a.x < AREA.x0) { a.x = AREA.x0; a.h = 0; } if (a.x > AREA.x1) { a.x = AREA.x1; a.h = Math.PI; }
        if (a.y < AREA.y0) { a.y = AREA.y0; a.h = Math.PI / 2; } if (a.y > AREA.y1) { a.y = AREA.y1; a.h = -Math.PI / 2; }
        q.setFromAxisAngle(up, Math.atan2(-a.vy, a.vx));
        m4.compose(M(a.x, a.y, B1 + S / 2), q, sc); inst.setMatrixAt(i, m4);
      });
      inst.instanceMatrix.needsUpdate = true;
    });
    g.add(onWall(wallText('Square goes, our way', 'one rule at a time', 'Rules make behaviour visible. Give these squares one rule and the room organises itself; take it away and they collide. Tap a square to switch between no rules, keep left, and follow the one ahead.', 1.8), 54.2, -7.26, B1 + 1.7, Math.PI / 2));
  }

  const credit = label([{ t: 'READ THE BUILDING', size: 30, weight: 1000, track: 4 }, { t: 'An independent homage to "Rules?" (21_21 DESIGN SIGHT, 2021).', size: 18, color: '#bdb9b0' }, { t: 'Not affiliated. Facts restated from its public document; objects and texts original.', size: 18, color: '#bdb9b0' }], { w: 1.4, px: 900 });
  g.add(onFloor(credit, 29.9, 10.55, 0));

  scene.add(g);
  return { group: g, update: (t) => anim.forEach((f) => f(t)), colliders: g.userData.colliders };
}
