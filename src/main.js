// 21_21 DESIGN SIGHT · digital experience
// Model frame: X east, Y north, Z up (metres, GL = 0). glTF/three frame: x = X, y = Z, z = -Y.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import * as BufferGeometryUtils from 'three/addons/utils/BufferGeometryUtils.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
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
scene.fog = new THREE.Fog(0x2a2c2e, 90, 420);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.22;

const camera = new THREE.PerspectiveCamera(42, innerWidth / innerHeight, 0.05, 1500);
camera.position.copy(M(30, -50, 24));

// sky: a quiet gradient dome. dark zenith, a low glow toward the sun
const sky = new THREE.Mesh(new THREE.SphereGeometry(1200, 32, 16), new THREE.ShaderMaterial({
  side: THREE.BackSide, depthWrite: false, fog: false,
  uniforms: { sunPosition: { value: new THREE.Vector3(0, 1, 0) }, day: { value: 1 } },
  vertexShader: 'varying vec3 vDir; void main(){ vDir = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
  fragmentShader: `uniform vec3 sunPosition; uniform float day; varying vec3 vDir;
    void main(){
      vec3 d = normalize(vDir); float h = max(d.y, 0.0);
      vec3 zen = mix(vec3(0.010,0.012,0.018), vec3(0.16,0.20,0.26), day);
      vec3 hor = mix(vec3(0.05,0.045,0.05), vec3(0.42,0.43,0.43), day);
      vec3 c = mix(hor, zen, pow(h, 0.45));
      float s = max(dot(d, normalize(sunPosition)), 0.0);
      vec3 warm = vec3(1.0,0.62,0.34) * (1.0 - day * 0.6);
      c += warm * (pow(s, 6.0) * 0.35 + pow(s, 64.0) * 0.5) * (1.0 - h * 0.6);
      c = mix(c, hor * 0.6, smoothstep(0.0, -0.15, d.y));
      gl_FragColor = vec4(c, 1.0);
    }`,
}));
sky.material.uniforms.rayleigh = { value: 0 };
scene.add(sky);
const realList = [sky];

const hemi = new THREE.HemisphereLight(0xc9d3dc, 0x2b2a24, 0.6);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffffff, 3.2);
sun.castShadow = true;
sun.shadow.mapSize.set(TEST ? 1024 : 4096, TEST ? 1024 : 4096);
const sc = sun.shadow.camera; sc.left = -70; sc.right = 70; sc.top = 50; sc.bottom = -50; sc.near = 1; sc.far = 400;
sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.07; sun.shadow.radius = 2.5;
scene.add(sun, sun.target);
sun.target.position.copy(M(28, 3, 0));
const fill = new THREE.AmbientLight(0xfff1de, 0);           // raised underground
scene.add(fill);
// warm interior lamps: they carry the building at dusk and underground
const lamps = [[28, 11, 1.8], [38, 9.5, 1.6], [6, -1.5, 1.3], [36, 2, -4.2], [52, 1, -4.2], [64, 4, -4.2], [50, 12, -3.6]]
  .map(([x, y, z]) => { const l = new THREE.PointLight(0xffd7a8, 0, 16, 2); l.position.copy(M(x, y, z)); scene.add(l); return l; });
let lampLevel = 0, baseExposure = 0.8, underK = 0;

// garden context: far ground + cedars (stylised; not part of the measured model)
{
  const g = new THREE.Mesh(new THREE.CircleGeometry(600, 64).rotateX(-Math.PI / 2),
    new THREE.MeshStandardMaterial({ color: 0x262b21, roughness: 1 }));
  g.position.y = -0.45; g.receiveShadow = true; scene.add(g); realList.push(g);
  let s = 7; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const trunk = new THREE.CylinderGeometry(0.18, 0.28, 1, 6).translate(0, 0.5, 0);
  // crown: a loose cluster of low-poly blobs, read as silhouette at dusk
  const crown = BufferGeometryUtils.mergeGeometries([[0, 0.55, 0, 0.62], [0.32, 0.4, 0.1, 0.45], [-0.28, 0.35, -0.12, 0.44], [0.05, 0.8, 0.05, 0.4], [-0.1, 0.22, 0.3, 0.36]]
    .map(([x, y, z, r]) => new THREE.IcosahedronGeometry(r, 1).translate(x, y, z)));
  const pts = [];
  for (let i = 0; i < 48; i++) pts.push([-14 + rnd() * 104, 34 + rnd() * 26]);          // north grove (Midtown garden)
  for (let i = 0; i < 10; i++) pts.push([88 + rnd() * 18, -10 + rnd() * 40]);            // east edge
  const tI = new THREE.InstancedMesh(trunk, new THREE.MeshStandardMaterial({ color: 0x1d1814, roughness: 1 }), pts.length);
  const cI = new THREE.InstancedMesh(crown, new THREE.MeshStandardMaterial({ color: 0x1b2419, roughness: 1, flatShading: true }), pts.length);
  const m = new THREE.Matrix4(), q = new THREE.Quaternion();
  pts.forEach(([x, y], i) => {
    const h = 11 + rnd() * 10, r = 2.2 + rnd() * 1.6, p = M(x, y, -0.4);
    m.compose(p, q, new THREE.Vector3(1, h * 0.35, 1)); tI.setMatrixAt(i, m);
    q.setFromAxisAngle(new THREE.Vector3(0, 1, 0), rnd() * 6.28);
    m.compose(p.clone().add(new THREE.Vector3(0, h * 0.3, 0)), q, new THREE.Vector3(r * 1.5, h * 0.75, r * 1.5)); cI.setMatrixAt(i, m); q.identity();
  });
  tI.castShadow = cI.castShadow = true;
  scene.add(tI, cI); realList.push(tI, cI);
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
  const day = THREE.MathUtils.smoothstep(alt, -0.04, 0.35);
  const lit = THREE.MathUtils.smoothstep(alt, -0.02, 0.05);
  sun.intensity = 4.6 * lit * (0.6 + 0.4 * day);
  sun.color.setHSL(0.075, 0.75 * (1 - day) + 0.08, 0.55 + 0.3 * day);
  hemi.intensity = 0.1 + 0.55 * day;
  hemi.color.setHSL(0.6, 0.25, 0.35 + 0.4 * day);
  scene.fog.color.setHSL(0.6, 0.08, 0.04 + 0.14 * day);
  scene.environmentIntensity = 0.1 + 0.3 * day;
  sky.material.uniforms.day.value = day;
  baseExposure = 0.55 + 0.25 * day;
  lampLevel = 1 - day;
  const hh = Math.floor(hour), mm = Math.round((hour - hh) * 60);
  $('#sunOut').value = `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`;
}
$('#sunRange').addEventListener('input', (e) => setSun(+e.target.value));
setSun(14.5);

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
const fovFor = (m) => { const base = { orbit: 38, tour: 50, walk: 62, diagram: 38 }[m]; const a = innerWidth / innerHeight;
  return a < 1 ? Math.min(base * THREE.MathUtils.clamp(0.8 / a, 1, 1.75), 88) : base; };
const realThings = [];
let mode = 'orbit', fly = null, fovTarget = fovFor('orbit');
camera.fov = fovTarget; camera.updateProjectionMatrix();
const stations = await (await fetch('data/stations.json')).json();
let tIdx = 0, tAuto = null;

function setMode(m) {
  mode = m;
  document.body.className = m;
  fovTarget = fovFor(m);
  document.querySelectorAll('#modes [data-mode]').forEach((b) => b.classList.toggle('on', b.dataset.mode === m));
  orbit.enabled = m === 'orbit';
  const D = m === 'diagram';
  diagCtl.enabled = D; diagRoot.visible = D; renderPass.camera = D ? diagCam : camera; bloom.enabled = !D;
  scene.background = D ? new THREE.Color(0x0e0f10) : null;
  for (const o of realThings) o.visible = !D;
  scene.fog.far = D ? 1e5 : 420;
  if (D) { explode = explodeTarget = 0; $('#explodeBtn').textContent = 'Explode'; }
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
    toast('Walk from the plaza');
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
  $('#tIdx').textContent = String(tIdx + 1).padStart(2, '0');
  $('#tOf').textContent = `/ ${String(stations.length).padStart(2, '0')}`;
  $('#tTitle').textContent = s.title; $('#tText').textContent = s.text;
  for (const el of [$('#tTitle'), $('#tText')]) { el.classList.remove('fade'); void el.offsetWidth; el.classList.add('fade'); }
  flyTo(M(...s.cam), M(...s.look));
}
function stopAuto() { if (tAuto) { clearInterval(tAuto); tAuto = null; $('#tPlay').textContent = 'Play'; } }
$('#tPrev').onclick = () => { stopAuto(); goStation(tIdx - 1); };
$('#tNext').onclick = () => { stopAuto(); goStation(tIdx + 1); };
$('#tPlay').onclick = () => {
  if (tAuto) return stopAuto();
  $('#tPlay').textContent = 'Pause'; goStation(tIdx + 1);
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
  if (lv !== level) { level = lv; $('#planimg').src = lv === 'B1' ? 'plan_b1.png' : 'plan_f1.png'; $('#lvlname').textContent = lv === 'B1' ? 'Basement' : 'Ground floor'; }
  const px = (m.x - MAP.x0) / (MAP.x1 - MAP.x0), py = (MAP.y1 - m.y) / (MAP.y1 - MAP.y0);
  you.style.display = px < -0.05 || px > 1.05 || py < -0.1 || py > 1.1 ? 'none' : '';
  you.style.left = `${px * 100}%`; you.style.top = `${py * 100}%`;
  const d = new THREE.Vector3(); camera.getWorldDirection(d);
  you.style.setProperty('--rot', `${Math.atan2(d.x, -d.z) * 180 / Math.PI}deg`);
}
$('#map').addEventListener('click', (e) => {
  const r = $('#map .frame').getBoundingClientRect();
  const x = MAP.x0 + (e.clientX - r.left) / r.width * (MAP.x1 - MAP.x0);
  const y = MAP.y1 - (e.clientY - r.top) / r.height * (MAP.y1 - MAP.y0);
  if (mode === 'orbit') { orbit.target.copy(M(x, y, level === 'B1' ? -4 : 0)); return; }
  if (mode === 'tour') setMode('walk');
  const top = level === 'B1' ? -1.6 : 6;
  const h = hit(M(x, y, top), DOWN, 12);
  if (!h) return toast('Nowhere to stand there');
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
const lightMats = [];
// ---------- sky cover: indoor fragments lose the open-sky ambient, so sunlight and lamps model the rooms ----------
const COVER = { w: 200, h: 80, x0: -14, x1: 86, y0: -16, y1: 24 };   // model metres, 0.5 m cells
const coverTex = new THREE.DataTexture(new Float32Array(COVER.w * COVER.h * 4).fill(-20), COVER.w, COVER.h, THREE.RGBAFormat, THREE.FloatType);
coverTex.magFilter = coverTex.minFilter = THREE.LinearFilter; coverTex.needsUpdate = true;
const coverU = { coverTex: { value: coverTex }, coverBox: { value: new THREE.Vector4(COVER.x0, COVER.x1, COVER.y0, COVER.y1) }, coverK: { value: 0.22 } };
function addCover(m) {
  m.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, coverU);
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vWPos;')
      .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvWPos = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
      varying vec3 vWPos; uniform sampler2D coverTex; uniform vec4 coverBox; uniform float coverK;
      float skyOpen(){
        vec2 uv = vec2((vWPos.x - coverBox.x) / (coverBox.y - coverBox.x), (-vWPos.z - coverBox.z) / (coverBox.w - coverBox.z));
        if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) return 1.0;
        vec4 c = texture2D(coverTex, uv);
        float roof = vWPos.y > -0.6 ? c.r : c.g;          // covering height above this level
        return smoothstep(-0.25, 0.05, vWPos.y - roof);   // 0 under cover, 1 in the open
      }`)
      .replace('#include <aomap_fragment>', `#include <aomap_fragment>
      { float k = mix(coverK, 1.0, skyOpen()); reflectedLight.indirectDiffuse *= k; reflectedLight.indirectSpecular *= k; }`);
  };
  m.needsUpdate = true;
}
function buildCover() {
  const d = coverTex.image.data, up = new THREE.Vector3(0, 1, 0);
  for (let j = 0; j < COVER.h; j++) for (let i = 0; i < COVER.w; i++) {
    const x = COVER.x0 + (i + 0.5) / COVER.w * (COVER.x1 - COVER.x0), y = COVER.y0 + (j + 0.5) / COVER.h * (COVER.y1 - COVER.y0);
    const a = hit(M(x, y, 0.3), up, 20), b = hit(M(x, y, -5.4), up, 6);
    const k = (j * COVER.w + i) * 4;
    d[k] = a ? a.point.y : -20; d[k + 1] = b ? b.point.y : -20;
  }
  coverTex.needsUpdate = true;
}
const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
loader.load('model/2121.glb', (gltf) => {
  const root = gltf.scene;
  const geos = [];
  root.updateMatrixWorld(true);
  root.traverse((o) => {
    if (!o.isMesh) return;
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    const name = (mats[0].name || '') + ' ' + o.name + ' ' + (o.parent ? o.parent.name : '');
    const isGlass = /glass|frosted/.test(name) || mats[0].transparent;
    const isLight = /light/.test(name) || (mats[0].emissive && mats[0].emissive.r > 0.5);
    if (/lawn/.test(mats[0].name)) mats.forEach((m) => m.color.setRGB(0.15, 0.13, 0.14));   // quiet the grass  // quiet the grass
    o.castShadow = !isGlass && !isLight;
    o.receiveShadow = !isLight;
    mats.forEach((m) => {
      if (isGlass) { m.transparent = true; m.depthWrite = false; m.envMapIntensity = 1.2; }
      if (isLight) { m.emissive = new THREE.Color(1, 0.9, 0.74); m.emissiveIntensity = 3.0; lightMats.push(m); }
      if (m.map) m.map.anisotropy = renderer.capabilities.getMaxAnisotropy();
      if (!isGlass && !isLight && !m.userData.cover) { m.userData.cover = true; addCover(m); }
    });
    if (!isLight) {
      const g = o.geometry.clone();
      for (const k of Object.keys(g.attributes)) if (k !== 'position') g.deleteAttribute(k);
      { // quantized (int16 normalized) positions would clamp to [-1,1] when transformed: expand to float first
        const src = g.attributes.position, f = new Float32Array(src.count * 3);
        for (let i = 0; i < src.count; i++) { f[i * 3] = src.getX(i); f[i * 3 + 1] = src.getY(i); f[i * 3 + 2] = src.getZ(i); }
        g.setAttribute('position', new THREE.BufferAttribute(f, 3));
      }
      g.applyMatrix4(o.matrixWorld);
      geos.push(g.index ? g.toNonIndexed() : g);
    }
  });
  scene.add(root); realThings.push(...realList, root);
  buildDiagram(root);
  const merged = BufferGeometryUtils.mergeGeometries(geos, false);
  bvh = new MeshBVH(merged);
  buildCover();
  $('#loader').classList.add('done');
  setTimeout(() => $('#loader').remove(), 1000);
  orbit.update();
}, (e) => {
  if (e.total) { const k = e.loaded / e.total; $('#loadbar').style.width = `${k * 100}%`; $('#loadpct').textContent = Math.round(k * 100); }
}, (err) => { $('#loadtext').textContent = 'Could not load the model. ' + err.message; });


// ---------- Diagram mode: an axonometric drawing on dark paper ----------
const DIAG = {
  roof:     { c: 0xd2a868, fill: 0.16, line: 0.85, label: 'Steel plate roof, 16 mm' },
  concrete: { c: 0x9fb2c6, fill: 0.07, line: 0.55, label: 'Exposed concrete' },
  glass:    { c: 0x76c0b2, fill: 0.14, line: 0.7,  label: 'Glazing and mullions' },
  b1:       { c: 0xa196e0, fill: 0.10, line: 0.6,  label: 'Basement, FL -6.0' },
  site:     { c: 0x8f9a86, fill: 0.0,  line: 0.22, label: 'Ground and lawn' },
};
const diagRoot = new THREE.Group(); diagRoot.visible = false; scene.add(diagRoot);
const diagParts = { up: new THREE.Group(), roof: new THREE.Group(), b1: new THREE.Group() };
Object.values(diagParts).forEach((g) => diagRoot.add(g));
let explode = 0, explodeTarget = 0;
function floatPositions(g) {
  const src = g.attributes.position, f = new Float32Array(src.count * 3);
  for (let i = 0; i < src.count; i++) { f[i * 3] = src.getX(i); f[i * 3 + 1] = src.getY(i); f[i * 3 + 2] = src.getZ(i); }
  const out = new THREE.BufferGeometry(); out.setAttribute('position', new THREE.BufferAttribute(f, 3)); return out;
}
function diagLayer(geo, key, parent) {
  const d = DIAG[key];
  if (d.fill > 0) parent.add(new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: d.c, transparent: true, opacity: d.fill, depthWrite: false, side: THREE.DoubleSide, fog: false })));
  const e = new THREE.LineSegments(new THREE.EdgesGeometry(geo, 20), new THREE.LineBasicMaterial({ color: d.c, transparent: true, opacity: d.line, fog: false }));
  parent.add(e);
}
function buildDiagram(root) {
  root.traverse((o) => {
    if (!o.isMesh || /ceiling|light|lawn/.test(o.name)) return;
    let g = o.geometry.index ? o.geometry.toNonIndexed() : o.geometry.clone();
    g = floatPositions(g); g.applyMatrix4(o.matrixWorld);
    const p = g.attributes.position.array, up = [], dn = [];
    for (let i = 0; i < p.length; i += 9) {
      const cy = (p[i + 1] + p[i + 4] + p[i + 7]) / 3;
      (cy < -0.7 ? dn : up).push(...p.subarray(i, i + 9));
    }
    const mk = (a) => { const b = new THREE.BufferGeometry(); b.setAttribute('position', new THREE.Float32BufferAttribute(a, 3)); return b; };
    const key = /__roof$/.test(o.name) ? 'roof' : /glass|steel|frosted/.test(o.name) ? 'glass' : 'concrete';
    if (up.length) diagLayer(mk(up), key, key === 'roof' ? diagParts.roof : diagParts.up);
    if (dn.length) diagLayer(mk(dn), 'b1', diagParts.b1);
  });
  // datum grid at GL, 3.6 m (two formwork panels) module
  const grid = new THREE.GridHelper(118.8, 33, 0x6a6f77, 0x3a3e44);
  grid.position.copy(M(32, 4, 0.01)); grid.material.transparent = true; grid.material.opacity = 0.7; grid.material.fog = false;
  diagParts.up.add(grid);
}
const diagCam = new THREE.OrthographicCamera(-1, 1, 1, -1, -500, 1000);
const diagCtl = new OrbitControls(diagCam, canvas);
diagCtl.enabled = false; diagCtl.enableDamping = true; diagCtl.target.copy(M(44, -6, -1.5));
diagCtl.minZoom = 0.6; diagCtl.maxZoom = 8; diagCtl.maxPolarAngle = Math.PI * 0.49;
diagCam.position.copy(M(44 + 60, -6 - 60, 58)); diagCam.zoom = 1;
function sizeDiag() {
  const a = innerWidth / innerHeight, half = a < 1 ? 40 / a : 54;
  diagCam.left = -half * a; diagCam.right = half * a; diagCam.top = half; diagCam.bottom = -half; diagCam.updateProjectionMatrix();
}
sizeDiag();
$('#explodeBtn').addEventListener('click', () => {
  explodeTarget = explodeTarget ? 0 : 1;
  $('#explodeBtn').textContent = explodeTarget ? 'Assemble' : 'Explode';
});
function stepDiagram() {
  explode += (explodeTarget - explode) * 0.06;
  diagParts.roof.position.y = explode * 9;
  diagParts.b1.position.y = -explode * 8;
  diagCtl.update();
  // level marks follow the drawing
  for (const [id, y, z] of [['#lvGL', 0, 0], ['#lvB1', -6, -explode * 8], ['#lvRF', 4.8, explode * 9]]) {
    const v = M(-12, -12, y).add(new THREE.Vector3(0, z, 0)).project(diagCam);
    const el = $(id); el.style.transform = `translate(${(v.x * 0.5 + 0.5) * innerWidth}px,${(-v.y * 0.5 + 0.5) * innerHeight}px)`;
  }
}

// ---------- post: AO, bloom, grade ----------
const composer = new EffectComposer(renderer);
const renderPass = new RenderPass(scene, camera);
composer.addPass(renderPass);
const bloom = window.__bloom = new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), 0.3, 0.5, 0.97);
composer.addPass(bloom);
composer.addPass(new OutputPass());
const grade = new ShaderPass({
  uniforms: { tDiffuse: { value: null }, time: { value: 0 }, grain: { value: 0.035 } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
  fragmentShader: `uniform sampler2D tDiffuse; uniform float time; uniform float grain; varying vec2 vUv;
    float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)) + time) * 43758.5453); }
    void main(){
      vec3 c = texture2D(tDiffuse, vUv).rgb;
      float l = dot(c, vec3(0.299,0.587,0.114));
      c = mix(vec3(l), c, 0.7);                                  // restrained saturation
      c = mix(c, c * vec3(0.92,0.98,1.06), 1.0 - smoothstep(0.0, 0.5, l));  // cool shadows
      c = mix(c, c * vec3(1.05,1.0,0.93), smoothstep(0.45, 1.0, l));       // warm highlights
      c = (c - 0.5) * 1.06 + 0.5;
      c += (h(vUv * 1000.0) - 0.5) * grain;
      gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0);
    }`,
});
composer.addPass(grade);

// ---------- loop ----------
const clock = new THREE.Timer();
function frame() {
  clock.update(); const dt = Math.min(clock.getDelta(), 0.05);
  if (fly) stepFly(dt);
  if (mode === 'diagram') stepDiagram();
  else if (mode === 'orbit' && !fly) orbit.update();
  else if (!fly) { if (mode === 'walk') stepWalk(dt); applyLook(); }
  const under = toModel(camera.position).z < -1.2;
  underK += ((under ? 1 : 0) - underK) * 0.08;
  renderer.toneMappingExposure = baseExposure * (1 - 0.28 * underK);
  fill.intensity += ((under ? 0.9 : 0.35 + 0.3 * lampLevel) - fill.intensity) * 0.08;
  const lampOn = Math.max(0.35, lampLevel, under ? 1 : 0);
  lamps.forEach((l, i) => { const k = i < 3 ? lampLevel * 0.6 : lampOn; l.intensity += (k * 7 - l.intensity) * 0.08; });
  for (const m of lightMats) m.emissiveIntensity = 1.6 + 2.4 * lampLevel;
  if (Math.abs(camera.fov - fovTarget) > 0.05) { camera.fov += (fovTarget - camera.fov) * 0.05; camera.updateProjectionMatrix(); }
  grade.uniforms.time.value = (grade.uniforms.time.value + 0.37) % 100;
  updateMap();
  composer.render(dt);
  requestAnimationFrame(frame);
}
frame();
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight; fovTarget = fovFor(mode); camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  composer.setSize(innerWidth, innerHeight); sizeDiag();
});
// debug hook for automated checks
window.__2121 = { get bvh() { return bvh; }, THREE, setMode, goStation, camera, setSun, ready: () => !!bvh, probe: (x, y, z) => { const h = hit(M(x, y, z), DOWN, 30); return h && toModel(h.point); } };
