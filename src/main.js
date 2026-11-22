// 21_21 DESIGN SIGHT · digital experience
// Model frame: X east, Y north, Z up (metres, GL = 0). glTF/three frame: x = X, y = Z, z = -Y.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { Sky } from 'three/addons/objects/Sky.js';
import * as BufferGeometryUtils from 'three/addons/utils/BufferGeometryUtils.js';
import { MeshBVH } from 'three-mesh-bvh';

const $ = (s) => document.querySelector(s);
const M = (x, y, z) => new THREE.Vector3(x, z, -y);          // model -> three
const toModel = (v) => ({ x: v.x, y: -v.z, z: v.y });        // three -> model
const EYE = 1.6;
const MAP = { x0: -12, x1: 78, y0: -14, y1: 22 };            // plan image extent (m)

// ---------- renderer / scene ----------
const canvas = $('#view');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
const TEST = location.search.includes('test');
renderer.setPixelRatio(TEST ? 1 : Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.9;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xdfe3e6, 140, 520);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.35;

const camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.05, 1500);
camera.position.copy(M(30, -50, 24));

const sky = new Sky();
sky.scale.setScalar(4000);
Object.assign(sky.material.uniforms.turbidity, { value: 6 });
sky.material.uniforms.rayleigh.value = 1.4;
sky.material.uniforms.mieCoefficient.value = 0.004;
sky.material.uniforms.mieDirectionalG.value = 0.8;
scene.add(sky);

const hemi = new THREE.HemisphereLight(0xdfe9f3, 0x6f7a5a, 1.1);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffffff, 3.2);
sun.castShadow = true;
sun.shadow.mapSize.set(TEST ? 1024 : 4096, TEST ? 1024 : 4096);
const sc = sun.shadow.camera; sc.left = -70; sc.right = 70; sc.top = 50; sc.bottom = -50; sc.near = 1; sc.far = 400;
sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.04;
scene.add(sun, sun.target);
sun.target.position.copy(M(28, 3, 0));
const fill = new THREE.AmbientLight(0xfff4e6, 0);           // raised underground
scene.add(fill);

// garden context: far ground + cedars (stylised; not part of the measured model)
{
  const g = new THREE.Mesh(new THREE.CircleGeometry(600, 64).rotateX(-Math.PI / 2),
    new THREE.MeshStandardMaterial({ color: 0x86a85e, roughness: 1 }));
  g.position.y = -0.45; g.receiveShadow = true; scene.add(g);
  let s = 7; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const trunk = new THREE.CylinderGeometry(0.18, 0.28, 1, 6).translate(0, 0.5, 0);
  const crown = new THREE.ConeGeometry(1, 1, 8).translate(0, 0.5, 0);
  const pts = [];
  for (let i = 0; i < 48; i++) pts.push([-14 + rnd() * 104, 34 + rnd() * 26]);          // north grove (Midtown garden)
  for (let i = 0; i < 10; i++) pts.push([88 + rnd() * 18, -10 + rnd() * 40]);            // east edge
  const tI = new THREE.InstancedMesh(trunk, new THREE.MeshStandardMaterial({ color: 0x4a3c30, roughness: 1 }), pts.length);
  const cI = new THREE.InstancedMesh(crown, new THREE.MeshStandardMaterial({ color: 0x3e5a3c, roughness: 1 }), pts.length);
  const m = new THREE.Matrix4(), q = new THREE.Quaternion();
  pts.forEach(([x, y], i) => {
    const h = 11 + rnd() * 10, r = 2.2 + rnd() * 1.6, p = M(x, y, -0.4);
    m.compose(p, q, new THREE.Vector3(1, h * 0.35, 1)); tI.setMatrixAt(i, m);
    m.compose(p.clone().add(new THREE.Vector3(0, h * 0.25, 0)), q, new THREE.Vector3(r, h * 0.8, r)); cI.setMatrixAt(i, m);
  });
  tI.castShadow = cI.castShadow = true;
  scene.add(tI, cI);
}

// ---------- sun position (Tokyo) ----------
const LAT = 35.6674 * Math.PI / 180;
function setSun(hour) {
  const now = new Date();
  const doy = Math.floor((now - new Date(now.getFullYear(), 0, 0)) / 864e5);
  const decl = 23.44 * Math.PI / 180 * Math.sin(2 * Math.PI * (284 + doy) / 365);
  const solar = hour + (139.7301 - 135) / 15;                    // JST -> local solar time
  const H = (solar - 12) * 15 * Math.PI / 180;
  const alt = Math.asin(Math.sin(LAT) * Math.sin(decl) + Math.cos(LAT) * Math.cos(decl) * Math.cos(H));
  const az = Math.atan2(-Math.sin(H), Math.tan(decl) * Math.cos(LAT) - Math.sin(LAT) * Math.cos(H)); // from north, clockwise
  const dir = M(Math.sin(az) * Math.cos(alt), Math.cos(az) * Math.cos(alt), Math.sin(alt));
  sky.material.uniforms.sunPosition.value.copy(dir);
  sun.position.copy(sun.target.position).addScaledVector(dir, 200);
  const day = THREE.MathUtils.smoothstep(alt, -0.05, 0.25);
  sun.intensity = 3.4 * day;
  sun.color.setHSL(0.09, 0.55 * (1 - day) + 0.1, 0.62 + 0.3 * day);
  hemi.intensity = 0.25 + 0.9 * day;
  renderer.toneMappingExposure = 0.55 + 0.4 * day;
  const hh = Math.floor(hour), mm = Math.round((hour - hh) * 60);
  $('#sunOut').value = `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`;
}
$('#sunRange').addEventListener('input', (e) => setSun(+e.target.value));
setSun(14);

// ---------- controls ----------
const orbit = new OrbitControls(camera, canvas);
orbit.enableDamping = true;
orbit.target.copy(M(28, 3, 0));
orbit.maxPolarAngle = Math.PI * 0.495;
orbit.minDistance = 6; orbit.maxDistance = 260;

// look controller for tour + walk: camera position is ours, drag rotates yaw/pitch
const look = { yaw: 0, pitch: 0, drag: null };
function lookAtPoint(target) {
  const d = target.clone().sub(camera.position);
  look.yaw = Math.atan2(-d.x, -d.z);
  look.pitch = Math.atan2(d.y, Math.hypot(d.x, d.z));
}
function applyLook() {
  camera.quaternion.setFromEuler(new THREE.Euler(look.pitch, look.yaw, 0, 'YXZ'));
}
canvas.addEventListener('pointerdown', (e) => {
  if (mode === 'orbit') return;
  look.drag = { x: e.clientX, y: e.clientY, id: e.pointerId };
  canvas.setPointerCapture(e.pointerId);
});
canvas.addEventListener('pointermove', (e) => {
  if (!look.drag || look.drag.id !== e.pointerId) return;
  const k = 0.0042 * (55 / camera.fov);
  look.yaw += (e.clientX - look.drag.x) * k;
  look.pitch = THREE.MathUtils.clamp(look.pitch + (e.clientY - look.drag.y) * k, -1.35, 1.35);
  look.drag.x = e.clientX; look.drag.y = e.clientY;
  if (fly) fly = null;
});
canvas.addEventListener('pointerup', () => (look.drag = null));
canvas.addEventListener('pointercancel', () => (look.drag = null));

// ---------- collision (BVH over the whole building) ----------
let bvh = null;
const ray = new THREE.Ray();
function hit(origin, dir, far) {
  if (!bvh) return null;
  ray.origin.copy(origin); ray.direction.copy(dir);
  const h = bvh.raycastFirst(ray, THREE.DoubleSide);
  return h && h.distance <= far ? h : null;
}
const DOWN = new THREE.Vector3(0, -1, 0);
function floorBelow(p, from = 0.6) {               // p = eye position (three)
  const o = p.clone(); o.y = p.y - EYE + from;
  const h = hit(o, DOWN, 30);
  return h ? h.point.y : null;
}

// ---------- modes ----------
let mode = 'orbit', fly = null;
const stations = await (await fetch('data/stations.json')).json();
let tIdx = 0, tAuto = null;

function setMode(m) {
  mode = m;
  document.querySelectorAll('#modes [data-mode]').forEach((b) => b.classList.toggle('on', b.dataset.mode === m));
  orbit.enabled = m === 'orbit';
  $('#tourCard').hidden = m !== 'tour';
  $('#walkHelp').hidden = m !== 'walk';
  $('#stick').hidden = !(m === 'walk' && matchMedia('(hover:none)').matches);
  stopAuto();
  if (m === 'orbit') {
    const fwd = new THREE.Vector3(); camera.getWorldDirection(fwd);
    const tgt = M(28, 3, 0);
    if (camera.position.y < 3) { flyTo(M(30, -50, 24), tgt, () => orbit.target.copy(tgt)); }
    else orbit.target.copy(tgt);
  } else if (m === 'tour') {
    goStation(tIdx);
  } else if (m === 'walk') {
    const s = stations.find((x) => x.id === 'plaza');
    flyTo(M(...s.cam), M(...s.look));
    toast('漫游模式：从广场出发');
  }
}
document.querySelectorAll('#modes [data-mode]').forEach((b) => b.addEventListener('click', () => setMode(b.dataset.mode)));

function flyTo(pos, target, done) {
  const from = camera.position.clone();
  const q0 = camera.quaternion.clone();
  const tmp = new THREE.Object3D(); tmp.position.copy(pos); tmp.lookAt(target);
  const dist = from.distanceTo(pos);
  fly = { from, to: pos, q0, q1: tmp.quaternion.clone(), t: 0, dur: TEST ? 0.05 : THREE.MathUtils.clamp(dist / 18, 1.2, 3.2), target, done };
}
function stepFly(dt) {
  if (!fly) return;
  fly.t += dt / fly.dur;
  const k = fly.t >= 1 ? 1 : 0.5 - 0.5 * Math.cos(Math.PI * fly.t);
  // arc up over the roof when travelling far
  const lift = Math.sin(Math.PI * k) * Math.min(18, fly.from.distanceTo(fly.to) * 0.25);
  camera.position.lerpVectors(fly.from, fly.to, k); camera.position.y += lift;
  camera.quaternion.slerpQuaternions(fly.q0, fly.q1, k);
  if (fly.t >= 1) { const f = fly; fly = null; lookAtPoint(f.target); applyLook(); f.done && f.done(); }
}

// tour
function goStation(i) {
  tIdx = (i + stations.length) % stations.length;
  const s = stations[tIdx];
  $('#tIdx').textContent = `${String(tIdx + 1).padStart(2, '0')} / ${String(stations.length).padStart(2, '0')}`;
  $('#tTitle').textContent = s.title; $('#tEn').textContent = s.en; $('#tText').textContent = s.text;
  flyTo(M(...s.cam), M(...s.look));
}
function stopAuto() { if (tAuto) { clearInterval(tAuto); tAuto = null; $('#tPlay').textContent = '自动播放'; } }
$('#tPrev').onclick = () => { stopAuto(); goStation(tIdx - 1); };
$('#tNext').onclick = () => { stopAuto(); goStation(tIdx + 1); };
$('#tPlay').onclick = () => {
  if (tAuto) return stopAuto();
  $('#tPlay').textContent = '暂停'; goStation(tIdx + 1);
  tAuto = setInterval(() => goStation(tIdx + 1), 9000);
};

// walk input
const keys = new Set();
addEventListener('keydown', (e) => {
  if (e.target.tagName === 'INPUT') return;
  keys.add(e.code);
  if (mode === 'tour' && e.code === 'ArrowRight') { stopAuto(); goStation(tIdx + 1); }
  if (mode === 'tour' && e.code === 'ArrowLeft') { stopAuto(); goStation(tIdx - 1); }
});
addEventListener('keyup', (e) => keys.delete(e.code));
addEventListener('blur', () => keys.clear());
const stick = { x: 0, y: 0, id: null };
{
  const el = $('#stick'), knob = el.querySelector('i');
  const upd = (e) => {
    const r = el.getBoundingClientRect(); let x = (e.clientX - r.left - r.width / 2) / (r.width / 2), y = (e.clientY - r.top - r.height / 2) / (r.height / 2);
    const l = Math.hypot(x, y); if (l > 1) { x /= l; y /= l; }
    stick.x = x; stick.y = y; knob.style.transform = `translate(${x * 38}px,${y * 38}px)`;
  };
  el.addEventListener('pointerdown', (e) => { stick.id = e.pointerId; el.setPointerCapture(e.pointerId); upd(e); e.stopPropagation(); });
  el.addEventListener('pointermove', (e) => { if (stick.id === e.pointerId) upd(e); });
  const end = () => { stick.id = null; stick.x = stick.y = 0; knob.style.transform = ''; };
  el.addEventListener('pointerup', end); el.addEventListener('pointercancel', end);
}

const vel = new THREE.Vector3();
function stepWalk(dt) {
  if (fly) return;
  let f = 0, r = 0;
  if (keys.has('KeyW') || keys.has('ArrowUp')) f += 1;
  if (keys.has('KeyS') || keys.has('ArrowDown')) f -= 1;
  if (keys.has('KeyD') || keys.has('ArrowRight')) r += 1;
  if (keys.has('KeyA') || keys.has('ArrowLeft')) r -= 1;
  f -= stick.y; r += stick.x;
  const speed = (keys.has('ShiftLeft') || keys.has('ShiftRight') ? 4.2 : 1.9);
  const fwd = new THREE.Vector3(-Math.sin(look.yaw), 0, -Math.cos(look.yaw));
  const right = new THREE.Vector3(-fwd.z, 0, fwd.x);
  const want = fwd.multiplyScalar(f).add(right.multiplyScalar(r));
  if (want.lengthSq() > 1) want.normalize();
  vel.lerp(want.multiplyScalar(speed), 1 - Math.exp(-dt * 10));
  const step = vel.clone().multiplyScalar(dt);
  const p = camera.position;
  const tryMove = (d) => {
    const len = d.length(); if (len < 1e-5) return;
    const dir = d.clone().divideScalar(len);
    const feet = p.y - EYE;
    for (const h of [0.45, 1.0, 1.55]) {
      const o = new THREE.Vector3(p.x, feet + h, p.z);
      if (hit(o, dir, len + 0.3)) return false;
    }
    p.add(d); return true;
  };
  if (tryMove(step) === false) {                       // slide along walls
    tryMove(new THREE.Vector3(step.x, 0, 0)); tryMove(new THREE.Vector3(0, 0, step.z));
  }
  const fl = floorBelow(p, 0.5);                       // steps up to 0.5 m
  if (fl !== null) {
    const target = fl + EYE;
    p.y += (target - p.y) * (target < p.y ? 1 - Math.exp(-dt * 9) : 1 - Math.exp(-dt * 14));
  }
}

// ---------- minimap ----------
const you = $('#you');
let level = '1F';
function updateMap() {
  const m = toModel(camera.position);
  const lv = m.z < -1.3 ? 'B1' : '1F';
  if (lv !== level) { level = lv; $('#planimg').src = lv === 'B1' ? 'plan_b1.png' : 'plan_f1.png'; $('#lvlname').textContent = lv === 'B1' ? 'B1 地下一层' : '1F 地面层'; }
  const px = (m.x - MAP.x0) / (MAP.x1 - MAP.x0), py = (MAP.y1 - m.y) / (MAP.y1 - MAP.y0);
  you.style.display = px < -0.05 || px > 1.05 || py < -0.1 || py > 1.1 ? 'none' : '';
  you.style.left = `${px * 100}%`; you.style.top = `${py * 100}%`;
  const d = new THREE.Vector3(); camera.getWorldDirection(d);
  you.style.setProperty('--rot', `${Math.atan2(d.x, -d.z) * 180 / Math.PI}deg`);
}
$('#lvlname').textContent = '1F 地面层';
$('#map').addEventListener('click', (e) => {
  const r = $('#map .frame').getBoundingClientRect();
  const x = MAP.x0 + (e.clientX - r.left) / r.width * (MAP.x1 - MAP.x0);
  const y = MAP.y1 - (e.clientY - r.top) / r.height * (MAP.y1 - MAP.y0);
  if (mode === 'orbit') { orbit.target.copy(M(x, y, level === 'B1' ? -4 : 0)); return; }
  if (mode === 'tour') setMode('walk');
  const top = level === 'B1' ? -1.6 : 6;
  const h = hit(M(x, y, top), DOWN, 12);
  if (!h) return toast('那里没有可以站的地面');
  const pos = h.point.clone(); pos.y += EYE;
  const fwd = new THREE.Vector3(); camera.getWorldDirection(fwd); fwd.y = 0; fwd.normalize();
  flyTo(pos, pos.clone().add(fwd.multiplyScalar(5)));
});

// ---------- info / toast ----------
$('#infoBtn').onclick = () => $('#info').showModal();
$('#infoClose').onclick = () => $('#info').close();
let toastT;
function toast(t) { const el = $('#toast'); el.textContent = t; el.hidden = false; clearTimeout(toastT); toastT = setTimeout(() => (el.hidden = true), 2600); }

// ---------- load model ----------
const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
loader.load('model/2121.glb', (gltf) => {
  const root = gltf.scene;
  const geos = [];
  root.updateMatrixWorld(true);
  root.traverse((o) => {
    if (!o.isMesh) return;
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    const name = mats[0].name || '';
    const isGlass = /glass|frosted/.test(name);
    const isLight = /light/.test(name);
    o.castShadow = !isGlass && !isLight;
    o.receiveShadow = !isLight;
    mats.forEach((m) => {
      if (isGlass) { m.transparent = true; m.depthWrite = false; m.envMapIntensity = 1.2; }
      if (isLight) { m.emissive = new THREE.Color(1, 0.94, 0.82); m.emissiveIntensity = 2.2; }
      if (m.map) m.map.anisotropy = renderer.capabilities.getMaxAnisotropy();
    });
    if (!isLight) {
      const g = o.geometry.clone();
      for (const k of Object.keys(g.attributes)) if (k !== 'position') g.deleteAttribute(k);
      g.applyMatrix4(o.matrixWorld);
      geos.push(g.index ? g.toNonIndexed() : g);
    }
  });
  scene.add(root);
  const merged = BufferGeometryUtils.mergeGeometries(geos, false);
  bvh = new MeshBVH(merged);
  $('#loader').classList.add('done');
  setTimeout(() => $('#loader').remove(), 1000);
  orbit.update();
}, (e) => {
  if (e.total) $('#loadbar').style.width = `${(e.loaded / e.total) * 100}%`;
}, (err) => { $('#loadtext').textContent = '模型载入失败：' + err.message; });

// ---------- loop ----------
const clock = new THREE.Timer();
function frame() {
  clock.update(); const dt = Math.min(clock.getDelta(), 0.05);
  if (fly) stepFly(dt);
  if (mode === 'orbit' && !fly) orbit.update();
  else if (!fly) { if (mode === 'walk') stepWalk(dt); applyLook(); }
  const under = toModel(camera.position).z < -1.2;
  fill.intensity += ((under ? 0.9 : 0) - fill.intensity) * 0.08;
  updateMap();
  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}
frame();
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
// debug hook for automated checks
window.__2121 = { setMode, goStation, camera, setSun, ready: () => !!bvh };
