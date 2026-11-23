// Measure the Sight: an independent homage to "Measuring" (21_21 DESIGN SIGHT, 2015).
// Everything here is original: plain geometry, our own type and our own texts.
import * as THREE from 'three';

const M = (x, y, z) => new THREE.Vector3(x, z, -y);   // model (X east, Y north, Z up) -> three
const B1 = -6.0;                                       // basement floor level
// Gallery 1's east wall is not on a grid line: it leans 2.7° (probed: X 38.779 at Y 0.6, 38.989 at Y 5.0)
const G1E = { x: (y) => 38.751 + 0.0477 * y, yaw: Math.PI - 0.0477, rot: -0.0477 };

const ply = new THREE.MeshStandardMaterial({ color: 0xcdb48e, roughness: 0.78, metalness: 0 });
const plyEdge = new THREE.MeshStandardMaterial({ color: 0xa88c62, roughness: 0.8 });
const white = new THREE.MeshStandardMaterial({ color: 0xf2f0ea, roughness: 0.6 });
const tape = new THREE.MeshBasicMaterial({ color: 0xf4f2ec });
const signal = new THREE.MeshBasicMaterial({ color: 0xff5a1f });           // the one unit colour
const steel = new THREE.MeshStandardMaterial({ color: 0x1b1c1e, metalness: 0.8, roughness: 0.35 });
const brass = new THREE.MeshStandardMaterial({ color: 0xb8955a, metalness: 0.9, roughness: 0.3 });
const glassM = new THREE.MeshPhysicalMaterial({ color: 0xffffff, transparent: true, opacity: 0.18, roughness: 0.05, metalness: 0, depthWrite: false });
const waterM = new THREE.MeshStandardMaterial({ color: 0x6f9fb0, transparent: true, opacity: 0.55, roughness: 0.1 });
const bagM = new THREE.MeshStandardMaterial({ color: 0xe9e4d8, roughness: 0.95 });
const discM = new THREE.MeshStandardMaterial({ color: 0xbfc3c6, metalness: 0.7, roughness: 0.4 });

// ---------- type on canvas ----------
const FONT = '"Bella Gothic","Helvetica Neue",Arial,sans-serif';
function label(lines, { w = 1, px = 512, size = 40, weight = 400, color = '#f2f0ea', bg = null, align = 'left', lead = 1.35, pad = 0.06 } = {}) {
  const L = lines.map((l) => (typeof l === 'string' ? { t: l } : l));
  const scale = px / w;                                  // canvas px per metre
  const hs = L.map((l) => (l.size || size) * lead);
  const H = Math.ceil(hs.reduce((a, b) => a + b, 0) + pad * scale * 2);
  const cv = document.createElement('canvas'); cv.width = px; cv.height = H;
  const g = cv.getContext('2d');
  if (bg) { g.fillStyle = bg; g.fillRect(0, 0, px, H); }
  let y = pad * scale;
  L.forEach((l, i) => {
    g.font = `${l.weight || weight} ${l.size || size}px ${FONT}`; g.fillStyle = l.color || color; g.textBaseline = 'top';
    g.textAlign = align; const x = align === 'center' ? px / 2 : align === 'right' ? px - pad * scale : pad * scale;
    if (l.track) g.letterSpacing = `${l.track}px`;
    g.fillText(l.t, x, y + (hs[i] - (l.size || size)) / 2);
    g.letterSpacing = '0px';
    y += hs[i];
  });
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, H / scale), new THREE.MeshBasicMaterial({ map: tex, transparent: !bg, depthWrite: !!bg, toneMapped: false, color: 0xd9d6cf }));
  m.userData.label = true;
  return m;
}
// wrap a paragraph to lines of roughly n characters
const wrap = (s, n) => { const out = []; let cur = ''; for (const w of s.split(' ')) { if ((cur + ' ' + w).trim().length > n) { out.push(cur.trim()); cur = w; } else cur += ' ' + w; } if (cur.trim()) out.push(cur.trim()); return out; };

// a wall text: title, a Japanese/aside line, body
function wallText(title, aside, body, w = 1.6) {
  return label([
    { t: title.toUpperCase(), size: 34, weight: 1000, track: 3 },
    { t: aside, size: 22, color: '#a9a59d', track: 2 },
    { t: ' ', size: 14 },
    ...wrap(body, 52).map((t) => ({ t, size: 22 })),
  ], { w, px: 1024 });
}
// place a flat thing on a wall: p = model point on the wall, yaw = direction the face looks (radians, model frame)
function onWall(o, x, y, z, faceYaw) { o.position.copy(M(x, y, z)); o.rotation.y = faceYaw + Math.PI / 2; return o; }
// lay a flat thing on the floor, reading towards +Y unless rot says otherwise
function onFloor(o, x, y, z, rot = 0) { o.position.copy(M(x, y, z + 0.004)); o.rotation.set(-Math.PI / 2, 0, rot); return o; }

function box(w, d, h, mat, x, y, z) {                  // w along X, d along Y, h up; (x,y,z) = centre of the base
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
  m.position.copy(M(x, y, z + h / 2)); m.castShadow = m.receiveShadow = true; return m;
}
function plinth(g, w, d, h, x, y, z = B1) {             // ply box with a darker 18 mm edge line at the top
  const p = box(w, d, h, ply, x, y, z); g.add(p);
  g.add(box(w + 0.004, d + 0.004, 0.018, plyEdge, x, y, z + h - 0.018));
  g.userData.colliders.push(p);
  return z + h;
}
function strip(g, x0, y0, x1, y1, z, wdt = 0.05, mat = tape) {   // floor line
  const len = Math.hypot(x1 - x0, y1 - y0);
  const m = new THREE.Mesh(new THREE.PlaneGeometry(len, wdt), mat);
  m.position.copy(M((x0 + x1) / 2, (y0 + y1) / 2, z + 0.003));
  m.rotation.set(-Math.PI / 2, 0, Math.atan2(y1 - y0, x1 - x0));
  m.receiveShadow = true; g.add(m); return m;
}

export async function buildExhibit(scene, root) {
  try { await Promise.all([document.fonts.load(`400 40px ${FONT}`), document.fonts.load(`1000 40px ${FONT}`)]); } catch (e) {}
  const g = new THREE.Group(); g.name = 'exhibit'; g.userData.colliders = [];
  const anim = [];

  // ===== 1. Lobby: your metre =====
  {
    const z = 0, x = 29.2, y = 11.2;
    strip(g, x, y, x + 1, y, z, 0.03); strip(g, x, y + 1, x + 1, y + 1, z, 0.03); strip(g, x, y, x, y + 1, z, 0.03); strip(g, x + 1, y, x + 1, y + 1, z, 0.03);
    const s = 10 / 33, xs = x + 1.35;
    strip(g, xs, y, xs + s, y, z, 0.02, signal); strip(g, xs, y + s, xs + s, y + s, z, 0.02, signal); strip(g, xs, y, xs, y + s, z, 0.02, signal); strip(g, xs + s, y, xs + s, y + s, z, 0.02, signal);
    g.add(onFloor(label([{ t: '1 m', size: 44, weight: 1000 }, { t: 'one metre, 1793', size: 22, color: '#bdb9b0' }], { w: 0.6 }), x + 0.32, y + 0.55, z));
    g.add(onFloor(label([{ t: '1 SHAKU', size: 44, weight: 1000, track: 2 }, { t: '10/33 m, 30.3 cm', size: 22, color: '#bdb9b0' }], { w: 0.6 }), xs + 0.3, y - 0.22, z));
  }

  // ===== 2. Sunken court: the tall pane and the sun clock =====
  {
    const gx = 55.0, gy = 8.4;
    // gnomon: a triangular steel plate on a north-south line; its real shadow comes from the scene's sun
    const sh = new THREE.Shape(); sh.moveTo(0, 0); sh.lineTo(1.4, 0); sh.lineTo(1.4, 1.4 * Math.tan(35.67 * Math.PI / 180)); sh.lineTo(0, 0);   // the style rises northwards at the latitude
    const gn = new THREE.Mesh(new THREE.ExtrudeGeometry(sh, { depth: 0.016, bevelEnabled: false }), steel);
    gn.position.copy(M(gx - 0.008, gy - 0.7, B1)); gn.rotation.y = Math.PI / 2; gn.castShadow = true; g.add(gn);
    gn.userData.info = 'The style leans at 35.67°, Tokyo\'s latitude, so it points at the celestial pole. Move the time slider and read the hour from its shadow.';
    g.userData.colliders.push(gn);
    // hour lines, 6:00 to 18:00, as a horizontal sundial for Tokyo (35.67 N)
    const lat = 35.67 * Math.PI / 180;
    for (let h = 6; h <= 18; h++) {
      const a = Math.atan(Math.sin(lat) * Math.tan((h - 12) * Math.PI / 12));
      const ang = h < 6.01 ? -Math.PI / 2 : h > 17.99 ? Math.PI / 2 : a;
      const r0 = 0.15, r1 = h % 3 ? 1.35 : 1.6, ox = gx, oy = gy - 0.7;
      strip(g, ox + Math.sin(ang) * r0, oy + Math.cos(ang) * r0, ox + Math.sin(ang) * r1, oy + Math.cos(ang) * r1, B1, h % 3 ? 0.012 : 0.02, h === 12 ? signal : tape);
      if (!(h % 3)) g.add(onFloor(label([{ t: String(h), size: 40, weight: 1000 }], { w: 0.2, px: 128, align: 'center', pad: 0.01 }), ox + Math.sin(ang) * 1.8, oy + Math.cos(ang) * 1.8, B1));
    }
    g.add(onFloor(label([{ t: 'SUN CLOCK', size: 30, weight: 1000, track: 3 }, { t: 'Tokyo, 35.67° N. The shadow is the hour.', size: 20, color: '#bdb9b0' }], { w: 1.2 }), gx - 0.1, gy - 1.25, B1));
    // a tape up the court glass, in metres
    const tx = 52.6, ty = 11.97, top = 2.6;           // just inside the court glass (Y 12.03); the roof steel starts at about +2.7 here
    const t = new THREE.Mesh(new THREE.PlaneGeometry(0.03, top - B1), tape); t.position.copy(M(tx, ty, (top + B1) / 2)); g.add(t);
    for (let m = 0; m <= 8; m++) {
      const tick = new THREE.Mesh(new THREE.PlaneGeometry(m % 5 ? 0.12 : 0.24, 0.012), m === 0 ? signal : tape);
      tick.position.copy(M(tx + (m % 5 ? 0.06 : 0.12), ty, B1 + m)); g.add(tick);
      const l = label([{ t: `${m} m`, size: 36, weight: m % 5 ? 400 : 1000 }], { w: 0.34, px: 160, pad: 0.01 });
      l.position.copy(M(tx + 0.42, ty - 0.01, B1 + m + 0.02)); g.add(l);
    }
    const l = label([{ t: 'FLOOR TO ROOF', size: 34, weight: 1000, track: 3 }, { t: 'about 8.6 m of glass here', size: 20, color: '#bdb9b0' }], { w: 1.0 });
    l.position.copy(M(tx + 0.75, ty - 0.01, B1 + 2.2)); g.add(l);
  }

  // ===== 3. Gallery 1: basic units =====
  {
    // (a) one litre
    let top = plinth(g, 0.5, 0.5, 0.95, 34.6, 7.0);
    const c = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.1, 0.1), glassM); c.position.copy(M(34.6, 7.0, top + 0.05)); g.add(c);
    c.userData.info = 'One litre: a 10 cm cube. Filled with water it weighs one kilogram, which is how the kilogram was first defined in 1795.';
    const wv = new THREE.Mesh(new THREE.BoxGeometry(0.096, 0.094, 0.096), waterM); wv.position.copy(M(34.6, 7.0, top + 0.049)); g.add(wv);
    g.add(onFloor(label([{ t: '1 L = 1 kg', size: 30, weight: 1000 }, { t: 'a 10 cm cube of water', size: 18, color: '#bdb9b0' }], { w: 0.4, px: 400 }), 34.6, 6.84, top));
    // (b) six bags, one size, six weights
    top = plinth(g, 2.4, 0.55, 0.75, 34.6, 4.2);
    const bags = [['1 kan', '3.75 kg'], ['500 monme', '1.875 kg'], ['1 lb', '454 g'], ['8 oz', '227 g'], ['1 kg', '1,000 g'], ['500 g', '500 g']];
    const bagG = new THREE.SphereGeometry(0.11, 24, 16); bagG.scale(1, 0.62, 0.8);
    bags.forEach(([u, v], i) => {
      const x = 34.6 - 1.0 + i * 0.4;
      const b = new THREE.Mesh(bagG, bagM); b.position.copy(M(x, 4.25, top + 0.065)); b.castShadow = true; g.add(b);
      b.userData.info = `${u}: ${v}. Same bag, same size. ` + ['Lift it and your arm drops: the heaviest of the six.', 'Half a kan, still the second heaviest.', 'The pound, from the Roman libra.', 'Eight ounces, half a pound.', 'The kilogram, a litre of water.', 'Half a kilogram.'][i];
      g.add(onFloor(label([{ t: u.toUpperCase(), size: 30, weight: 1000, track: 2 }, { t: v, size: 24, color: '#bdb9b0' }], { w: 0.3, px: 300, align: 'center', pad: 0.01 }), x, 4.04, top));
    });
    // (c) 1,000 discs of 3.75 g make one kan: ten stacks of a hundred
    top = plinth(g, 0.7, 0.5, 0.9, 34.6, 1.0);
    const dg = new THREE.CylinderGeometry(0.022, 0.022, 0.0012, 20);
    const inst = new THREE.InstancedMesh(dg, discM, 1000); const mtx = new THREE.Matrix4();
    for (let s = 0; s < 10; s++) for (let k = 0; k < 100; k++) {
      const x = 34.6 - 0.24 + (s % 5) * 0.12, y = 1.0 + (s < 5 ? 0.08 : -0.08);
      mtx.makeTranslation(...M(x, y, top + 0.0006 + k * 0.00125).toArray()); inst.setMatrixAt(s * 100 + k, mtx);
    }
    inst.castShadow = true; g.add(inst);
    inst.userData.info = 'One thousand discs of 3.75 g each, one monme apiece: together they weigh one kan, 3.75 kg.';
    g.add(onFloor(label([{ t: '1,000 × 3.75 g = 1 KAN', size: 26, weight: 1000, track: 1 }], { w: 0.6, px: 600, pad: 0.01 }), 34.6, 0.82, top));
    // wall text on the east wall
    g.add(onWall(wallText('Basic units', '1 litre, 1 kan, 1 second', 'Same size, different weight: units only mean something when we can feel them. One litre of water weighs one kilogram. One kan, the old Japanese weight, is 3.75 kilograms, a thousand monme.'), G1E.x(4.2) - 0.012, 4.2, B1 + 1.75, G1E.yaw));
    // (d) from 1 to 100: ten plywood cubes, 10 cm to 1 m, along the west wall
    let y = -1.5;
    for (let i = 1; i <= 10; i++) {
      const s = i / 10;
      const cb = box(s, s, s, i === 10 ? white : ply, 29.25 + s / 2, y + s / 2, B1); g.add(cb); g.userData.colliders.push(cb);
      cb.userData.info = `${i * 10} cm cube. ` + (i === 10 ? 'One cubic metre: a thousand litres, a tonne of water.' : `${(Math.pow(i / 10, 3) * 1000).toFixed(i < 3 ? 0 : 0)} litres inside.`);
      g.add(onFloor(label([{ t: `${i * 10}`, size: 44, weight: 1000 }, { t: 'cm', size: 22, color: '#bdb9b0' }], { w: 0.22, px: 160, pad: 0.01 }), 29.25 + s + 0.16, y + s / 2, B1, Math.PI / 2));
      y += s + 0.42;
    }
    strip(g, 29.2, -1.6, 29.2, y, B1, 0.02, signal);
  }

  // ===== 4. Gallery 2: how big is this building? A full doubles tennis court =====
  {
    const x0 = 42.3, L = 23.77, W = 10.97, y0 = -6.52,   // 6 cm clear of the slanting south wall at the west end, just short of the columns
      z = B1, sx = 1.37, sv = 6.40, cx = x0 + L / 2;
    const ln = (a, b, c, d) => strip(g, a, b, c, d, z, 0.05);
    ln(x0, y0, x0 + L, y0); ln(x0, y0 + W, x0 + L, y0 + W);                                  // doubles sidelines
    ln(x0, y0 + sx, x0 + L, y0 + sx); ln(x0, y0 + W - sx, x0 + L, y0 + W - sx);              // singles sidelines
    ln(x0, y0, x0, y0 + W); ln(x0 + L, y0, x0 + L, y0 + W);                                  // baselines
    ln(cx - sv, y0 + sx, cx - sv, y0 + W - sx); ln(cx + sv, y0 + sx, cx + sv, y0 + W - sx);  // service lines
    ln(cx - sv, y0 + W / 2, cx + sv, y0 + W / 2);                                            // centre service line
    ln(x0, y0 + W / 2, x0 + 0.1, y0 + W / 2); ln(x0 + L - 0.1, y0 + W / 2, x0 + L, y0 + W / 2);
    // the net
    for (const yy of [y0 + 0.03, y0 + W - 0.03]) { const p = box(0.06, 0.06, 1.07, steel, cx, yy, z); g.add(p); }   // posts on the doubles lines: the hall leaves no more room
    // the floor lines are informative too
    const net = new THREE.Mesh(new THREE.PlaneGeometry(W, 0.914), new THREE.MeshBasicMaterial({ color: 0x0c0c0c, transparent: true, opacity: 0.55, side: THREE.DoubleSide, depthWrite: false }));
    net.position.copy(M(cx, y0 + W / 2, z + 0.46)); net.rotation.y = Math.PI / 2; g.add(net);
    net.userData.info = 'A doubles court, 23.77 × 10.97 m. Use the ruler on the baseline to check it.';
    const band = new THREE.Mesh(new THREE.PlaneGeometry(W, 0.05), new THREE.MeshBasicMaterial({ color: 0xf4f2ec, side: THREE.DoubleSide }));
    band.position.copy(M(cx, y0 + W / 2, z + 0.9)); band.rotation.y = Math.PI / 2; g.add(band);
    g.add(onFloor(label([{ t: '23.77 × 10.97 m', size: 56, weight: 1000 }, { t: 'a doubles court, 260.8 m², inside a 443 m² hall', size: 26, color: '#bdb9b0' }], { w: 2.4, px: 1024 }), cx - 3.8, y0 + 2.6, z));
    g.add(onWall(wallText('How big is this building?', 'Gallery 2, 443 m²', 'Gallery 2 is 443 square metres: about 134 tsubo, or some 273 tatami mats, and big enough to hold a full tennis court. From the garden the building is a low folded roof. Underground, it opens into this hall.', 1.8), 54.2, -7.26, B1 + 1.7, Math.PI / 2));
    // the building at 1:100 on a table by the east wall
    const top = plinth(g, 1.0, 0.6, 0.9, 67.7, -1.2);
    if (root) {
      const mini = root.clone(true);
      const drop = []; mini.traverse((o) => { if (o.isMesh) { if (/lawn/.test(o.name)) drop.push(o); o.castShadow = true; o.receiveShadow = true; } }); drop.forEach((o) => o.removeFromParent());
      mini.scale.setScalar(0.01); mini.userData.info = 'The building at 1:100, the same model you are standing in. Only the roof and the glass show above the lawn.';
      // model origin (0,0,0) -> sits so its centre (~X 32, Y 3) lands on the table
      mini.position.copy(M(67.7 - 0.32, -1.2 - 0.03, top + 0.06));
      g.add(mini);
    }
    g.add(onFloor(label([{ t: '1:100', size: 40, weight: 1000 }, { t: 'the whole building, 80 per cent underground', size: 18, color: '#bdb9b0' }], { w: 0.5, px: 500, pad: 0.01 }), 67.7, -1.42, top));
  }

  // ===== 5. Gallery 2 west bay: bodies and tools, the seconds pendulum =====
  {
    const px = 40.5, py = -3.6, z = B1, H = 2.3;
    for (const dy of [-0.35, 0.35]) g.add(box(0.04, 0.04, H, steel, px, py + dy, z));
    g.add(box(0.04, 0.74, 0.04, steel, px, py, z + H - 0.04));
    g.add(box(0.5, 0.9, 0.02, ply, px, py, z));
    const arm = new THREE.Group(); arm.position.copy(M(px, py, z + H - 0.06));
    const rod = new THREE.Mesh(new THREE.CylinderGeometry(0.005, 0.005, 0.994, 8), steel); rod.position.y = -0.497; arm.add(rod);
    const bob = new THREE.Mesh(new THREE.SphereGeometry(0.045, 24, 16), brass); bob.position.y = -0.994; bob.castShadow = true; arm.add(bob);
    bob.userData.info = arm.userData.info = 'A seconds pendulum: 0.994 m from pivot to bob, one swing per second. Compare it with the one-metre bar beside it.';
    g.add(arm);
    anim.push((t) => { arm.rotation.x = 0.22 * Math.cos(Math.PI * t); });   // T = 2 s: one beat each second
    // a 1 m bar beside it, from the pivot down
    const bar = box(0.012, 0.012, 1.0, white, px, py + 0.55, z + H - 1.06); g.add(bar);
    const bl = label([{ t: '0.994 m', size: 30, weight: 1000 }, { t: 'beats once a second', size: 18, color: '#bdb9b0' }], { w: 0.42, px: 420 });
    g.add(onWall(bl, px + 0.02, py - 0.75, z + 1.6, 0));
    g.add(onWall(wallText('Bodies and tools', 'the seconds pendulum', 'In the 1790s the metre was nearly defined by a pendulum that beats once a second. That pendulum is just short of one metre long. Bodies, swings and shadows were our first rulers.', 1.4), 39.24, -1.2, B1 + 1.7, 0));
  }

  // ===== 6. Gallery 3: 54 metres of steel, at 1:10 =====
  {
    const z = 0, x = -2.6, y = -3.0;
    const top = plinth(g, 5.6, 0.32, 0.45, x + 2.7, y, z);
    const plate = box(5.4, 0.26, 0.016, steel, x + 2.7, y, top);   // 1:10 in length, 1:1 in thickness
    plate.userData.info = 'The roof plate: 5.4 m here stands for 54 m. The thickness, 16 mm, is real. Steel this long grows by about 30 mm from winter to summer.'; g.add(plate);
    const t = label([{ t: '54 m AT 1:10, 16 mm AT 1:1', size: 32, weight: 1000, track: 2 }, { t: 'one folded steel plate; it moves about 30 mm between winter and summer', size: 20, color: '#bdb9b0' }], { w: 2.2, px: 1024 });
    g.add(onFloor(t, x + 1.25, y - 0.3, z));
  }

  // credit
  const credit = label([{ t: 'MEASURE THE SIGHT', size: 30, weight: 1000, track: 4 }, { t: 'An independent homage to "Measuring" (21_21 DESIGN SIGHT, 2015).', size: 18, color: '#bdb9b0' }, { t: 'Not affiliated. All objects and texts are original.', size: 18, color: '#bdb9b0' }], { w: 1.2, px: 800 });
  g.add(onFloor(credit, 29.85, 10.55, 0));

  g.traverse((o) => { if (o.isMesh && !o.userData.label && o.castShadow === false) o.receiveShadow = true; });
  scene.add(g);
  return { group: g, update: (t) => anim.forEach((f) => f(t)), colliders: g.userData.colliders };
}

export { G1E, M, B1, label, wallText, onWall, onFloor, box, strip, wrap, steel, white, ply };
