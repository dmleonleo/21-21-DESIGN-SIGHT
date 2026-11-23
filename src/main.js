// 21_21 DESIGN SIGHT · digital experience
// Model frame: X east, Y north, Z up (metres, GL = 0). glTF/three frame: x = X, y = Z, z = -Y.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import * as BufferGeometryUtils from 'three/addons/utils/BufferGeometryUtils.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { buildExhibit } from './exhibit.js';
import { buildRules } from './rules.js';
import { FullScreenQuad } from 'three/addons/postprocessing/Pass.js';
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
renderer.setPixelRatio(TEST ? 1 : Math.min(devicePixelRatio, matchMedia('(hover:none)').matches ? 1.5 : 2));   // phones: 1.5x keeps the frame rate
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
let envK = 1;   // real sky light (Poly Haven CC0 HDRI) replaces the studio env once loaded
new RGBELoader().load('env/kloofendal_48d_partly_cloudy_puresky.hdr', (t) => {
  t.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = pmrem.fromEquirectangular(t).texture; t.dispose();
  envK = 0.35; setSun(+$('#sunRange').value);
});

const camera = new THREE.PerspectiveCamera(42, innerWidth / innerHeight, 0.05, 1500);
const TOUCH = matchMedia('(hover:none)').matches;
const HOME = () => (innerWidth < innerHeight ? M(29, -92, 52) : M(30, -50, 24));   // portrait phones need to stand further back
camera.position.copy(HOME());

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
const nightMats = [];
const realList = [sky];
let groundMat = null; const trees = [];

const hemi = new THREE.HemisphereLight(0xc9d3dc, 0x2b2a24, 0.6);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffffff, 3.2);
sun.castShadow = true;
{ const sm = TEST ? 1024 : matchMedia('(hover:none)').matches ? 2048 : 4096; sun.shadow.mapSize.set(sm, sm); }
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
    new THREE.MeshStandardMaterial({ color: 0x30352a, roughness: 1 }));
  g.position.y = -0.45; g.receiveShadow = true; scene.add(g); realList.push(g); groundMat = g.material;
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
  scene.add(tI, cI); realList.push(tI, cI); trees.push(tI, cI);
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
  sun.intensity = 2.8 * lit * (0.6 + 0.4 * day);
  sun.color.setHSL(0.075, 0.75 * (1 - day) + 0.08, 0.55 + 0.3 * day);
  hemi.intensity = 0.16 + 0.14 * day;   // night floor: Roppongi city glow
  hemi.color.setHSL(0.6, 0.25, 0.35 + 0.4 * day);
  scene.fog.color.setHSL(0.6, 0.08, 0.04 + 0.14 * day);
  scene.environmentIntensity = (0.22 + 0.3 * day) * envK;
  sky.material.uniforms.day.value = day;
  baseExposure = 0.62 + 0.9 * (1 - day) * (1 - day);   // eye adapts at night
  lampLevel = 1 - day;
  for (const m of nightMats) m.color.copy(m.userData.night).multiplyScalar(0.45 + 0.55 * day);   // surfaces sink at night
  const hh = Math.floor(hour), mm = Math.round((hour - hh) * 60);
  $('#sunOut').value = `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`;
}
$('#sunRange').addEventListener('input', (e) => setSun(+e.target.value));
setSun(23);

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

// ---------- ruler and exhibit notes (Journey stops and Walk) ----------
const rulerG = new THREE.Group(); scene.add(rulerG);
const dotG = new THREE.SphereGeometry(0.035, 16, 12), dotM = new THREE.MeshBasicMaterial({ color: 0xff5a1f, depthTest: false, toneMapped: false });
const lineM = new THREE.LineBasicMaterial({ color: 0xff5a1f, depthTest: false, toneMapped: false });
let rulerOn = false, rulerPts = [];
const SHAKU = 10 / 33;
function rulerClear() { rulerPts = []; rulerG.clear(); }
function rulerShow(t) { const o = $('#rulerOut'); o.textContent = t; o.hidden = !t; }
function setRuler(on) {
  rulerOn = on; $('#rulerBtn').classList.toggle('on', on); rulerClear();
  rulerShow(on ? (matchMedia('(hover:none)').matches ? 'Tap two points' : 'Click two points') : '');
}
$('#rulerBtn').addEventListener('click', () => setRuler(!rulerOn));
function note(t) { const el = $('#note'); el.textContent = t; el.hidden = !t; clearTimeout(note.t); if (t) note.t = setTimeout(() => (el.hidden = true), 7000); }
const pickRay = new THREE.Raycaster(), ndc = new THREE.Vector2();
function pick(e) {
  const r = canvas.getBoundingClientRect();
  ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  pickRay.setFromCamera(ndc, camera);
  return pickRay;
}
let tapStart = null;
canvas.addEventListener('pointerdown', (e) => { tapStart = { x: e.clientX, y: e.clientY, t: performance.now() }; });
canvas.addEventListener('pointerup', (e) => {
  if (!tapStart || (mode !== 'tour' && mode !== 'walk')) return;
  const moved = Math.hypot(e.clientX - tapStart.x, e.clientY - tapStart.y), dt = performance.now() - tapStart.t; tapStart = null;
  if (moved > 6 || dt > 600) return;
  const rc = pick(e), h = hit(rc.ray.origin, rc.ray.direction, 200);
  if (rulerOn) {
    if (!h) return;
    if (rulerPts.length === 2) rulerClear();
    const p = h.point.clone(); rulerPts.push(p);
    const d = new THREE.Mesh(dotG, dotM); d.position.copy(p); d.renderOrder = 10; rulerG.add(d);
    if (rulerPts.length === 2) {
      const ln = new THREE.Line(new THREE.BufferGeometry().setFromPoints(rulerPts), lineM); ln.renderOrder = 10; rulerG.add(ln);
      const m = rulerPts[0].distanceTo(rulerPts[1]);
      rulerShow(`${m < 1 ? (m * 100).toFixed(1) + ' cm' : m.toFixed(2) + ' m'}   ·   ${(m / SHAKU).toFixed(m / SHAKU < 10 ? 2 : 1)} shaku`);
    } else rulerShow('And the second point');
    return;
  }
  if (!exhibit) return;
  const hs = rc.intersectObject(exhibit.group, true);
  for (const x of hs) {
    if (h && x.distance > h.distance + 0.08) break;              // behind a wall
    let o = x.object; while (o && !o.userData.info && !o.userData.onTap) o = o.parent;
    if (o) { note(o.userData.onTap ? o.userData.onTap() : o.userData.info); return; }
  }
});

// ---------- modes ----------
const fovFor = (m) => { const base = { orbit: 38, tour: 50, walk: 62, diagram: 38 }[m]; const a = innerWidth / innerHeight;
  return a < 1 ? Math.min(base * THREE.MathUtils.clamp(0.8 / a, 1, 1.75), 88) : base; };
const realThings = [];
let mode = 'orbit', fly = null, fovTarget = fovFor('orbit');
camera.fov = fovTarget; camera.updateProjectionMatrix();
const PROGRAMS = { building: await (await fetch('data/stations.json')).json(), measure: await (await fetch('data/exhibit.json')).json(), rules: await (await fetch('data/rules.json')).json() };
const SHOWS = { measure: 'Measure the Sight', rules: 'Read the Building' };
let program = 'building', stations = PROGRAMS.building;
let show = (() => { try { return SHOWS[localStorage.getItem('2121.show')] ? localStorage.getItem('2121.show') : 'measure'; } catch (e) { return 'measure'; } })();
const shows = {}, bvhs = {};
function setShow(name) {                      // one exhibition is installed at a time: its objects, its collisions
  show = name; try { localStorage.setItem('2121.show', name); } catch (e) {}
  exhibit = shows[name] || null;
  if (bvhs[name]) bvh = bvhs[name];
  showVis();
  if (rulerOn) rulerClear();
}
function showVis() { for (const [k, v] of Object.entries(shows)) v.group.visible = k === show && mode !== 'diagram'; }
function openChooser() { $('#chooser').hidden = false; $('#chooser').querySelectorAll('button[data-show]').forEach((b) => b.classList.toggle('on', b.dataset.show === show)); }
$('#chooser').addEventListener('click', (e) => {
  const b = e.target.closest('button[data-show]');
  if (b) { $('#chooser').hidden = true; setMode('show:' + b.dataset.show); return; }
  if (e.target.id === 'chooser' || e.target.closest('.x')) $('#chooser').hidden = true;
});
function setProgram(p) {
  if (p === program) return;
  program = p; stations = PROGRAMS[p]; J.reach = null; J.t = J.p = 0; J.chapter = -1;
  $('#rail').querySelectorAll('button').forEach((b) => b.remove());
  $('#tKick').textContent = SHOWS[p] || '';
}

let tIdx = 0, tAuto = null;


// ---------- Journey: one continuous take, driven by scroll ----------
const J = { p: 0, t: 0, pos: null, look: null, chapter: -1, on: false, input: 0 };
function buildJourney() {
  J.reach = stations.map((st) => {                       // how far each shot may dolly forward before meeting a wall
    const c = M(...st.cam), d = M(...st.look).sub(c).normalize();
    const h = bvh ? hit(c, d, 6) : null;
    return h ? Math.max(0, Math.min(1.8, h.distance - 2.2)) : 1.8;
  });
  const rail = $('#rail');
  if (!rail.children.length || rail.children.length < 2) stations.forEach((s, i) => { const b = document.createElement('button'); b.style.top = `${(i / (stations.length - 1)) * 100}%`; b.title = s.title; b.dataset.t = s.title; b.onclick = () => { stopAuto(); J.t = i; }; rail.appendChild(b); });
}
function chapterText(i) {
  const s = stations[i];
  $('#tIdx').textContent = String(i + 1).padStart(2, '0');
  $('#tOf').textContent = `/ ${String(stations.length).padStart(2, '0')}`;
  $('#tTitle').textContent = s.title; $('#tText').textContent = s.text;
  const last = i === stations.length - 1;
  $('#tPrev').disabled = i === 0;
  $('#tNext').textContent = last ? 'Walk on' : 'Next'; $('#tNext').classList.toggle('end', last);
  if (!tAuto) $('#tPlay').textContent = last ? 'Again' : 'Play';
}
const jA = new THREE.Vector3(), jB = new THREE.Vector3(), jTmp = new THREE.PerspectiveCamera();
const camB = new THREE.PerspectiveCamera();          // the incoming shot during a dissolve
const XF = 0.22;                                     // half-width of a dissolve, in chapters
let xfadeK = 0;
function shotPose(i, u, out) {                       // u: 0..1 within shot i, runs past both ends during dissolves
  const st = stations[i];
  jA.copy(M(...st.cam)); jB.copy(M(...st.look));
  const dir = jB.clone().sub(jA).normalize();
  out.position.copy(jA).addScaledVector(dir, THREE.MathUtils.clamp(u, -0.2, 1.22) * J.reach[i]);   // slow push-in that never stops at the cut
  jTmp.position.copy(out.position); jTmp.lookAt(jB.clone().addScaledVector(dir, 4));
  jTmp.rotateY(-(u - 0.5) * 0.07);                  // every shot drifts the same way, so the motion carries across
  out.quaternion.copy(jTmp.quaternion);
}
function stepJourney(dt) {
  if (!J.on) return;
  const N = stations.length - 1;
  J.t = THREE.MathUtils.clamp(J.t, 0, N);
  if (!tAuto && performance.now() - J.input > 900) J.t += (Math.round(J.t) - J.t) * Math.min(1, dt * 2.2);   // come to rest on a shot, never mid-dissolve
  J.p += (J.t - J.p) * Math.min(1, dt * (TEST ? 60 : 2.4));
  document.querySelectorAll('#rail button').forEach((b, i) => b.classList.toggle('on', i === Math.round(J.p)));
  if (!J.reach || (!J.bvhOK && bvh)) { J.bvhOK = !!bvh; buildJourney(); }
  const c = THREE.MathUtils.clamp(Math.round(J.p), 0, N);
  const f = THREE.MathUtils.clamp(J.p - c, -0.5, 0.5);
  // the shot pair around the nearest boundary: a dissolves into a + 1
  const a = THREE.MathUtils.clamp(Math.floor(J.p), 0, Math.max(0, N - 1));
  const k = N > 0 ? THREE.MathUtils.smoothstep(J.p, a + 0.5 - XF, a + 0.5 + XF) : 0;
  shotPose(a, J.p - a + 0.5, camera);
  if (k > 0.001 && k < 0.999) { shotPose(a + 1, J.p - a - 0.5, camB); xfadeK = k; }
  else { if (k >= 0.999) shotPose(a + 1, J.p - a - 0.5, camera); xfadeK = 0; }
  if (c !== J.chapter) { J.chapter = c; tIdx = c; chapterText(c); }
  $('#cut2').style.opacity = 0;
  $('#tourCard').style.opacity = 1 - THREE.MathUtils.smoothstep(Math.abs(f), 0.08, 0.3);
  $('#railDot').style.top = `${(J.p / N) * 100}%`;
}
addEventListener('wheel', (e) => {
  if (mode !== 'tour' || !J.on) return;
  stopAuto(); J.input = performance.now(); J.t += (Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY) * 0.0016;
}, { passive: true });
{ let ty = null;
  let tx = null;
  canvas.addEventListener('touchstart', (e) => { if (mode === 'tour') { ty = e.touches[0].clientY; tx = e.touches[0].clientX; } }, { passive: true });
  canvas.addEventListener('touchmove', (e) => {                  // swipe up or left: forward
    if (mode !== 'tour' || ty === null) return; stopAuto(); J.input = performance.now();
    const dy = ty - e.touches[0].clientY, dx = tx - e.touches[0].clientX;
    J.t += (Math.abs(dx) > Math.abs(dy) ? dx : dy) * 0.006; ty = e.touches[0].clientY; tx = e.touches[0].clientX;
  }, { passive: true });
  canvas.addEventListener('touchend', () => (ty = null));
}

// ---------- Section: cut the building open, run the day ----------
const cutPlane = new THREE.Plane();
let cutKind = 'none';
const CUT = { plan: { min: -5.6, max: 4.8, def: 1.4, label: (v) => `Z ${v >= 0 ? '+' : ''}${v.toFixed(1)}` }, long: { min: -12, max: 22, def: 10, label: (v) => `Y ${v.toFixed(1)}` } };
function setCut(kind, v) {
  cutKind = kind;
  document.querySelectorAll('#cut [data-cut]').forEach((b) => b.classList.toggle('on', b.dataset.cut === kind));
  const on = kind !== 'none', r = $('#cutRange');
  r.hidden = !on; $('#cutOut').hidden = !on;
  if (on) {
    const c = CUT[kind];
    if (v === undefined) { r.min = c.min; r.max = c.max; r.step = 0.1; r.value = c.def; v = c.def; }
    if (kind === 'plan') cutPlane.set(new THREE.Vector3(0, -1, 0), v);       // keep below v
    else cutPlane.set(new THREE.Vector3(0, 0, -1), -v);                      // keep model Y > v (north half), seen from the south
    $('#cutOut').value = c.label(v);
  }
  const planes = on ? [cutPlane] : null;
  for (const m of clipMats) { m.clippingPlanes = planes; m.needsUpdate = true; }
  if (groundMat) { groundMat.clippingPlanes = planes; groundMat.needsUpdate = true; }
  coverU.cutOn.value = on ? 1 : 0;
  earthMat.clippingPlanes = planes; earthMat.needsUpdate = true; earth.visible = on;
  trees.forEach((t) => (t.visible = !on && mode !== 'diagram'));
}
renderer.localClippingEnabled = true;
// earth mass: only its inside shows, and only when the cut opens it
const earthMat = new THREE.MeshBasicMaterial({ color: 0x141413, side: THREE.BackSide, fog: false });
const earth = new THREE.Mesh(new THREE.BoxGeometry(600, 120, 600), earthMat);
earth.position.copy(M(32, 4, -60.5)); earth.visible = false; scene.add(earth);
const CUTVIEW = { plan: [[30, -26, 74], [30, 4, -1]], long: [[30, -58, 9], [30, 10, -2.5]] };
document.querySelectorAll('#cut [data-cut]').forEach((b) => (b.onclick = () => {
  setCut(b.dataset.cut);
  const v = CUTVIEW[b.dataset.cut];
  if (v) { const t = M(...v[1]); flyTo(M(...v[0]), t, () => orbit.target.copy(t)); }
}));
$('#cutRange').addEventListener('input', (e) => setCut(cutKind, +e.target.value));
let dayRun = null;
$('#dayBtn').onclick = () => {
  if (dayRun) { dayRun = null; $('#dayBtn').textContent = 'Day'; return; }
  dayRun = { h: Math.max(5, +$('#sunRange').value >= 23 ? 5 : +$('#sunRange').value) }; $('#dayBtn').textContent = 'Stop';
};
function stepDay(dt) {
  if (!dayRun) return;
  dayRun.h += dt * 0.9;                     // a day in ~20 s
  if (dayRun.h > 23.5) dayRun.h = 5;
  $('#sunRange').value = dayRun.h; setSun(dayRun.h);
}

function setMode(m) {
  const prev = mode;
  if (m === 'exhibit') { openChooser(); return; }
  if (m.startsWith('show:')) { const n = m.slice(5); setShow(n); setProgram(n); J.t = 0; m = 'tour'; } else if (m === 'tour') setProgram('building');
  mode = m; hideIntro();
  document.body.className = m + (document.body.classList.contains('light') ? ' light' : '') + (m === 'tour' && program !== 'building' ? ' exhibit' : '');
  fovTarget = fovFor(m);
  const shown = m === 'tour' && program !== 'building' ? 'exhibit' : m;
  if (rulerOn && m !== 'tour' && m !== 'walk') setRuler(false);
  note('');
  document.querySelectorAll('#modes [data-mode]').forEach((b) => b.classList.toggle('on', b.dataset.mode === shown));
  orbit.enabled = m === 'orbit';
  const D = m === 'diagram';
  diagCtl.enabled = D; diagRoot.visible = D; renderPass.camera = D ? diagCam : camera; bloom.enabled = !D;
  scene.background = D ? new THREE.Color(0x0e0f10) : null;
  for (const o of realThings) o.visible = !D;
  showVis();
  if (m !== 'orbit' && cutKind !== 'none') setCut('none');
  J.on = false; xfadeK = 0; $('#tourCard').style.opacity = ''; $('#cut2').style.opacity = 0;
  scene.fog.far = D ? 1e5 : 420;
  if (D) { explode = explodeTarget = 0; $('#explodeRange').value = 0; }
  $('#tourCard').hidden = m !== 'tour';
  $('#walkHelp').hidden = m !== 'walk';
  $('#stick').hidden = !(m === 'walk' && matchMedia('(hover:none)').matches);
  stopAuto();
  if (m === 'orbit') {
    const fwd = new THREE.Vector3(); camera.getWorldDirection(fwd);
    const tgt = M(28, 3, 0);
    if (camera.position.y < 3) { flyTo(HOME(), tgt, () => orbit.target.copy(tgt)); }
    else orbit.target.copy(tgt);
  } else if (m === 'tour') {
    const i = THREE.MathUtils.clamp(Math.round(J.t), 0, stations.length - 1), s = stations[i];
    J.t = J.p = i; J.chapter = -1;
    flyTo(M(...s.cam), M(...s.look), () => { J.on = true; });
    chapterText(i);
    if (!TEST) toast(TOUCH ? 'Swipe up to move through the building' : 'Scroll to move through the building');
  } else if (m === 'walk') {
    const fl = prev === 'tour' ? floorBelow(camera.position, 0.2) : null;
    if (fl !== null && Math.abs(camera.position.y - EYE - fl) < 1.2) {     // the journey ends indoors: walk on from that spot
      const fwd = new THREE.Vector3(); camera.getWorldDirection(fwd); fwd.y = 0; fwd.normalize();
      const pos = camera.position.clone(); pos.y = fl + EYE;
      flyTo(pos, pos.clone().add(fwd.multiplyScalar(5)));
      toast('Walk on from here');
    } else {
      const s = stations.find((x) => x.id === 'plaza');
      flyTo(M(...s.cam), M(...s.look));
      toast('Walk from the plaza');
    }
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
  if (J.on) { J.t = THREE.MathUtils.clamp(i, 0, stations.length - 1); if (TEST) J.p = J.t; return; }
  tIdx = (i + stations.length) % stations.length;
  const s = stations[tIdx];
  $('#tIdx').textContent = String(tIdx + 1).padStart(2, '0');
  $('#tOf').textContent = `/ ${String(stations.length).padStart(2, '0')}`;
  $('#tTitle').textContent = s.title; $('#tText').textContent = s.text;
  for (const el of [$('#tTitle'), $('#tText')]) { el.classList.remove('fade'); void el.offsetWidth; el.classList.add('fade'); }
  flyTo(M(...s.cam), M(...s.look));
}
function stopAuto() { if (tAuto) { clearInterval(tAuto); tAuto = null; $('#tPlay').textContent = Math.round(J.t) >= stations.length - 1 ? 'Again' : 'Play'; } }
$('#tPrev').onclick = () => { stopAuto(); goStation(Math.round(J.t) - 1); };
$('#tNext').onclick = () => { stopAuto(); if (Math.round(J.t) >= stations.length - 1) return setMode('walk'); goStation(Math.round(J.t) + 1); };
$('#tPlay').onclick = () => {
  if (tAuto) return stopAuto();
  if (Math.round(J.t) >= stations.length - 1) { J.t = J.p = 0; J.chapter = -1; }   // from the end: start over, no rewind blur
  $('#tPlay').textContent = 'Pause';
  tAuto = setInterval(() => { J.t += 0.0022; if (J.t >= stations.length - 1) stopAuto(); }, 16);
};

// walk input
const keys = new Set();
addEventListener('keydown', (e) => {
  if (e.target.tagName === 'INPUT') return;
  keys.add(e.code);
  if (mode === 'tour' && /ArrowRight|ArrowDown|Space/.test(e.code)) { stopAuto(); goStation(Math.round(J.t) + 1); }
  if (mode === 'tour' && /ArrowLeft|ArrowUp/.test(e.code)) { stopAuto(); goStation(Math.round(J.t) - 1); }
  const mk = { Digit1: 'tour', Digit2: 'orbit', Digit3: 'walk', Digit4: 'diagram' }[e.code];
  if (mk && !e.metaKey && !e.ctrlKey && !$('#info').open) setMode(mk);
  if (e.code === 'Escape') hideIntro();
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
// first visit: one quiet invitation, gone at the first touch
const intro = $('#intro');
let introOn = false;
function hideIntro() { if (!introOn) return; introOn = false; intro.classList.remove('on'); try { localStorage.setItem('2121.seen', '1'); } catch (e) {} }
function showIntro() {
  let seen = null; try { seen = localStorage.getItem('2121.seen'); } catch (e) {}
  if (TEST && !/intro/.test(location.search)) return;
  if (seen && !/intro/.test(location.search)) return;
  if (TOUCH) $('#introHint').textContent = 'Drag to turn. Pinch to zoom.';
  introOn = true; setTimeout(() => introOn && intro.classList.add('on'), 900);
  setTimeout(hideIntro, 16000);
}
$('#introGo').onclick = () => { J.t = 0; setMode('tour'); };
$('#introSkip').onclick = hideIntro;
canvas.addEventListener('pointerdown', () => setTimeout(hideIntro, 1200));
let toastT;
function toast(t) { const el = $('#toast'); el.textContent = t; el.hidden = false; clearTimeout(toastT); toastT = setTimeout(() => (el.hidden = true), 2600); }

// ---------- load model ----------
const lightMats = [], clipMats = [];
// ---------- sky cover: indoor fragments lose the open-sky ambient, so sunlight and lamps model the rooms ----------
const COVER = { w: 200, h: 80, x0: -14, x1: 86, y0: -16, y1: 24 };   // model metres, 0.5 m cells
const coverTex = new THREE.DataTexture(new Float32Array(COVER.w * COVER.h * 4).fill(-20), COVER.w, COVER.h, THREE.RGBAFormat, THREE.FloatType);
coverTex.magFilter = coverTex.minFilter = THREE.NearestFilter;   // linear blending of open(-20)/covered(+4.8) cells made dark wedges on walls coverTex.needsUpdate = true;
const openTex = new THREE.DataTexture(new Float32Array(COVER.w * COVER.h * 4).fill(1), COVER.w, COVER.h, THREE.RGBAFormat, THREE.FloatType);
openTex.magFilter = openTex.minFilter = THREE.LinearFilter;   // how much sky a covered spot still sees sideways (open sides of the forecourt, eaves)
const coverU = { openTex: { value: openTex }, coverTex: { value: coverTex }, coverBox: { value: new THREE.Vector4(COVER.x0, COVER.x1, COVER.y0, COVER.y1) }, coverK: { value: 0.22 }, cutOn: { value: 0 } };
function addCover(m) {
  m.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, coverU);
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vWPos;')
      .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvWPos = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    // normals always face the viewer: SketchUp export has triangles with reversed winding, which DoubleSide
    // shading flipped to the dark side (the black slivers on the walls)
    sh.fragmentShader = sh.fragmentShader.replace('#include <normal_fragment_begin>', THREE.ShaderChunk.normal_fragment_begin
      .replace('float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;', '\n#ifdef FLAT_SHADED\nfloat faceDirection = 1.0;\n#else\nfloat faceDirection = dot(vNormal, vViewPosition) >= 0.0 ? 1.0 : -1.0;\n#endif\n'));
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
      varying vec3 vWPos; uniform sampler2D coverTex; uniform sampler2D openTex; uniform vec4 coverBox; uniform float coverK; uniform float cutOn;
      float skyOpen(){
        // sample a little off the surface, on the viewer's side, so a wall under the eave reads as outside from outside
        vec3 gn = normalize(cross(dFdx(vWPos), dFdy(vWPos)));
        if (dot(gn, cameraPosition - vWPos) < 0.0) gn = -gn;
        vec3 sp = vWPos + gn * 0.35;
        vec2 uv = vec2((sp.x - coverBox.x) / (coverBox.y - coverBox.x), (-sp.z - coverBox.z) / (coverBox.w - coverBox.z));
        if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) return 1.0;
        vec4 c = texture2D(coverTex, uv);
        float up = vWPos.y > -0.6 ? 1.0 : 0.0;
        float roof = mix(c.g, c.r, up);                   // covering height above this level
        vec4 o = texture2D(openTex, uv);
        float side = mix(o.g, o.r, up);                   // sky seen past the open sides, traced on load
        return max(smoothstep(-0.25, 0.05, vWPos.y - roof), side);
      }`)
      .replace('#include <aomap_fragment>', `#include <aomap_fragment>
      { float k = mix(coverK, 1.0, skyOpen()); reflectedLight.indirectDiffuse *= k; reflectedLight.indirectSpecular *= k; }`)
      .replace('#include <dithering_fragment>', `#include <dithering_fragment>
      if (cutOn > 0.5 && !gl_FrontFacing) gl_FragColor = vec4(0.56, 0.55, 0.52, 1.0);`);
  };
  m.needsUpdate = true;
}
function retag(mesh, box, mat) {         // move the triangles inside a model-space box to another material
  const g = mesh.geometry, pos = g.attributes.position, v = new THREE.Vector3();
  const idx = g.index ? Array.from(g.index.array) : [...Array(pos.count).keys()];
  const inBox = (i) => { v.fromBufferAttribute(pos, i).applyMatrix4(mesh.matrixWorld); const m = toModel(v);
    return m.x > box[0][0] && m.x < box[1][0] && m.y > box[0][1] && m.y < box[1][1] && m.z > box[0][2] && m.z < box[1][2]; };
  const keep = [], move = [];
  for (let t = 0; t < idx.length; t += 3) (inBox(idx[t]) && inBox(idx[t + 1]) && inBox(idx[t + 2]) ? move : keep).push(idx[t], idx[t + 1], idx[t + 2]);
  if (!move.length) return 0;
  g.setIndex([...keep, ...move]); g.clearGroups(); g.addGroup(0, keep.length, 0); g.addGroup(keep.length, move.length, 1);
  mesh.material = [Array.isArray(mesh.material) ? mesh.material[0] : mesh.material, mat];
  return move.length / 3;
}
// F1 walls were modelled to stop at GL 0, but the forecourt paving falls away from the building, so their feet hover.
// Drop every wall-foot vertex that has open ground below it (within 1.2 m) down to that ground.
function groundWalls(root) {
  const ground = [], walls = [];
  root.traverse((o) => { if (!o.isMesh) return; if (/__(stone|lawn|paving|ground)$/.test(o.name) || /lawn/.test(o.name)) ground.push(o); if (/^F1_walls_RC__concrete/.test(o.name)) walls.push(o); });
  const rc = new THREE.Raycaster(); rc.far = 1.2; const v = new THREE.Vector3(), inv = new THREE.Matrix4();
  let moved = 0;
  for (const w of walls) {
    const src = w.geometry.attributes.position, f = new Float32Array(src.count * 3);
    for (let i = 0; i < src.count; i++) { f[i * 3] = src.getX(i); f[i * 3 + 1] = src.getY(i); f[i * 3 + 2] = src.getZ(i); }
    const pos = new THREE.BufferAttribute(f, 3); inv.copy(w.matrixWorld).invert();
    const cache = new Map();
    for (let i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i).applyMatrix4(w.matrixWorld);
      if (Math.abs(v.y) > 0.03) continue;                              // three y = model Z: only feet at GL 0
      const key = `${v.x.toFixed(3)},${v.z.toFixed(3)}`;
      let gy = cache.get(key);
      if (gy === undefined) {
        gy = null;
        rc.set(new THREE.Vector3(v.x, v.y - 0.02, v.z), DOWN);
        const h = rc.intersectObjects(ground, false)[0];
        if (h && h.point.y < v.y - 0.04) gy = h.point.y - 0.03;
        cache.set(key, gy);
      }
      if (gy === null) continue;
      v.y = gy; v.applyMatrix4(inv); pos.setXYZ(i, v.x, v.y, v.z); moved++;
    }
    if (moved) { w.geometry.setAttribute('position', pos); w.geometry.computeBoundingBox(); w.geometry.computeBoundingSphere(); }
  }
  return moved;
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
  // for each covered cell, the share of low and mid sky rays that escape: walls and glass block them
  const o = openTex.image.data, dirs = [];
  for (const el of [0.22, 0.6, 1.0]) for (let n = 0; n < 12; n++) { const az = n / 12 * Math.PI * 2; dirs.push(new THREE.Vector3(Math.cos(az) * Math.cos(el), Math.sin(el), Math.sin(az) * Math.cos(el))); }
  for (let j = 0; j < COVER.h; j++) for (let i = 0; i < COVER.w; i++) {
    const k = (j * COVER.w + i) * 4;
    const x = COVER.x0 + (i + 0.5) / COVER.w * (COVER.x1 - COVER.x0), y = COVER.y0 + (j + 0.5) / COVER.h * (COVER.y1 - COVER.y0);
    for (const [ch, z, roofH] of [[0, 1.4, d[k]], [1, -4.4, d[k + 1]]]) {
      if (roofH < -19) { o[k + ch] = 1; continue; }
      const p0 = M(x, y, z); let free = 0;
      for (const dv of dirs) if (!hit(p0, dv, 40)) free++;
      o[k + ch] = Math.min(1, (free / dirs.length) * 1.6);
    }
  }
  openTex.needsUpdate = true;
}
const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
let exhibit = null;
loader.load('model/2121.glb', async (gltf) => {
  const root = gltf.scene;
  const geos = [];
  root.updateMatrixWorld(true);
  groundWalls(root);
  root.traverse((o) => {
    if (!o.isMesh) return;
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    const name = (mats[0].name || '') + ' ' + o.name + ' ' + (o.parent ? o.parent.name : '');
    const isGlass = /glass|frosted/.test(name) || mats[0].transparent;
    const isLight = /light/.test(name) || (mats[0].emissive && mats[0].emissive.r > 0.5);
    if (/lawn/.test(mats[0].name)) mats.forEach((m) => m.color.setRGB(0.17, 0.18, 0.15));   // quiet the grass
    if (/__roof$/.test(o.name)) mats.forEach((m) => { if (!m.userData.roofed) { m.userData.roofed = true; m.color.multiplyScalar(0.28); m.metalness = 0.7; m.roughness = 0.38; } });
    if (/concrete/.test(o.name)) mats.forEach((m) => { if (!m.userData.dark) { m.userData.dark = true; m.color.multiplyScalar(0.5); m.roughness = 0.92; } });
    if (/__stone$/.test(o.name)) mats.forEach((m) => { if (!m.userData.dark) { m.userData.dark = true; m.color.multiplyScalar(0.42); m.roughness = 0.9; } });
    if (/__ceiling$/.test(o.name)) mats.forEach((m) => { if (!m.userData.dark) { m.userData.dark = true; m.color.multiplyScalar(0.72); } });
    if (/__steel$/.test(o.name)) mats.forEach((m) => { if (!m.userData.dark) { m.userData.dark = true; m.color.setRGB(0.07, 0.075, 0.08); m.metalness = 0.8; m.roughness = 0.35; } });
    mats.forEach((m) => { if (!isLight && !m.userData.night) { m.userData.night = m.color.clone(); nightMats.push(m); } });
    o.castShadow = !isGlass && !isLight;
    o.receiveShadow = !isLight;
    mats.forEach((m) => {
      if (isGlass) { m.transparent = true; m.depthWrite = false; m.envMapIntensity = 0.7; m.color.setRGB(0.80, 0.86, 0.88); m.opacity = 0.14; m.metalness = 0.0; m.roughness = 0.03; }
      if (isLight) { m.emissive = new THREE.Color(1, 0.9, 0.74); m.emissiveIntensity = 3.0; lightMats.push(m); }
      if (m.map) m.map.anisotropy = renderer.capabilities.getMaxAnisotropy();
      if (!isGlass && !isLight && !m.userData.cover) { m.userData.cover = true; addCover(m); }
      if (!m.userData.clip) { m.userData.clip = true; clipMats.push(m); if (!isGlass && !isLight) { m.side = THREE.DoubleSide; m.flatShading = true; } }   // planar architecture: geometric normals, ignores broken exported vertex normals
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
  { // the transom panel over the entrance door came in on the steel layer; it is the concrete band (station 3 text, photos)
    let steel = null, conc = null;
    root.traverse((o) => { if (o.isMesh && o.name === 'F1_mullions_frames__steel') steel = o; if (o.isMesh && o.name === 'F1_walls_RC__concrete_v') conc = o; });
    if (steel && conc) retag(steel, [[18.55, 10.3, 2.5], [19.3, 11.95, 3.45]], Array.isArray(conc.material) ? conc.material[0] : conc.material);
  }
  scene.add(root); realThings.push(...realList, root);
  buildDiagram(root); setSun(+$('#sunRange').value);
  // two exhibitions share the building; each gets its own collision tree with its own plinths
  for (const [name, build] of [['measure', () => buildExhibit(scene, root)], ['rules', () => buildRules(scene)]]) {
    try {
      const ex = await build(); shows[name] = ex;
      ex.group.traverse((o) => { if (o.isMesh && !o.userData.label) for (const m of [].concat(o.material)) if (!m.userData.clip) { m.userData.clip = true; clipMats.push(m); } });
      const extra = [];
      for (const c of ex.colliders) { c.updateMatrixWorld(true); const g = c.geometry.clone(); for (const k of Object.keys(g.attributes)) if (k !== 'position') g.deleteAttribute(k); g.applyMatrix4(c.matrixWorld); extra.push(g.index ? g.toNonIndexed() : g); }
      bvhs[name] = new MeshBVH(BufferGeometryUtils.mergeGeometries([...geos, ...extra], false));
    } catch (e) { console.error('exhibit', name, e); }
  }
  if (!bvhs.measure && !bvhs.rules) bvhs.base = new MeshBVH(BufferGeometryUtils.mergeGeometries(geos, false));
  bvh = bvhs[show] || bvhs.measure || bvhs.rules || bvhs.base;
  setShow(show);
  buildCover();
  $('#loader').classList.add('done');
  setTimeout(() => $('#loader').remove(), 1000);
  showIntro();
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
$('#explodeRange').addEventListener('input', (e) => { explodeTarget = +e.target.value; });   // a lever: the drawing follows the hand
addEventListener('keydown', (e) => {
  if (mode !== 'diagram' || e.target.tagName === 'INPUT') return;
  if (e.key === 'ArrowUp' || e.key === 'ArrowRight') explodeTarget = Math.min(1, explodeTarget + 0.1);
  else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') explodeTarget = Math.max(0, explodeTarget - 0.1);
  else return;
  $('#explodeRange').value = explodeTarget;
});
function stepDiagram() {
  explode += (explodeTarget - explode) * 0.14;
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
  uniforms: { tDiffuse: { value: null }, time: { value: 0 }, grain: { value: 0.035 }, paper: { value: 0 } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
  fragmentShader: `uniform sampler2D tDiffuse; uniform float time; uniform float grain; uniform float paper; varying vec2 vUv;
    float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)) + time) * 43758.5453); }
    void main(){
      vec3 c = texture2D(tDiffuse, vUv).rgb;
      float l = dot(c, vec3(0.299,0.587,0.114));
      c = mix(vec3(l), c, 0.7);                                  // restrained saturation
      c = mix(c, c * vec3(0.92,0.98,1.06), 1.0 - smoothstep(0.0, 0.5, l));  // cool shadows
      c = mix(c, c * vec3(1.05,1.0,0.93), smoothstep(0.45, 1.0, l));       // warm highlights
      c = (c - 0.25) * 1.05 + 0.25;
      c = mix(c, vec3(0.93,0.92,0.89) * (0.5 + 0.7 * c), paper);   // Light: morning haze, lifted paper blacks
      c += (h(vUv * 1000.0) - 0.5) * grain;
      gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0);
    }`,
});
composer.addPass(grade);
// cross-dissolve between Journey shots: the outgoing shot is rendered first into xfRT, then mixed under the incoming one
const xfRT = new THREE.WebGLRenderTarget(innerWidth * renderer.getPixelRatio(), innerHeight * renderer.getPixelRatio(), { type: THREE.HalfFloatType });
const xfade = new ShaderPass({
  uniforms: { tDiffuse: { value: null }, tPrev: { value: xfRT.texture }, k: { value: 0 } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
  fragmentShader: 'uniform sampler2D tDiffuse; uniform sampler2D tPrev; uniform float k; varying vec2 vUv; void main(){ gl_FragColor = vec4(mix(texture2D(tPrev, vUv).rgb, texture2D(tDiffuse, vUv).rgb, k), 1.0); }',
});
xfade.enabled = false; composer.addPass(xfade);
const xfCopy = new ShaderPass({ uniforms: { tDiffuse: { value: null } }, vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }', fragmentShader: 'uniform sampler2D tDiffuse; varying vec2 vUv; void main(){ gl_FragColor = texture2D(tDiffuse, vUv); }' });
const xfQuad = new FullScreenQuad(xfCopy.material);
function renderFrame(dt) {
  if (!(mode === 'tour' && xfadeK > 0)) { xfade.enabled = false; composer.render(dt); return; }
  // pass 1: outgoing shot, kept off screen
  xfade.enabled = false; composer.renderToScreen = false;
  composer.render(dt);
  xfCopy.uniforms.tDiffuse.value = composer.readBuffer.texture;
  renderer.setRenderTarget(xfRT); xfQuad.render(renderer);
  // pass 2: incoming shot, mixed over it
  const keep = camera.position.clone(), keepQ = camera.quaternion.clone();
  camera.position.copy(camB.position); camera.quaternion.copy(camB.quaternion); camera.updateMatrixWorld();
  composer.renderToScreen = true; xfade.enabled = true; xfade.uniforms.k.value = xfadeK;
  composer.render(dt);
  camera.position.copy(keep); camera.quaternion.copy(keepQ);
}

// ---------- light / dark: morning 08:00 vs late night 23:00 ----------
const THEME = { light: { h: 8.5, paper: 0.5 }, dark: { h: 23, paper: 0 } };
let themeRun = null, paperK = 0;
function setTheme(t, instant) {
  document.body.classList.toggle('light', t === 'light');
  document.querySelectorAll('#theme button').forEach((b) => b.classList.toggle('on', b.dataset.theme === t));
  dayRun = null; $('#dayBtn').textContent = 'Day';
  const to = THEME[t];
  if (instant) { paperK = to.paper; setSun(to.h); $('#sunRange').value = to.h; return; }
  themeRun = { h0: +$('#sunRange').value, h1: to.h, p0: paperK, p1: to.paper, k: 0 };
  try { localStorage.setItem('2121.theme', t); } catch (e) {}
}
document.querySelectorAll('#theme button').forEach((b) => (b.onclick = () => setTheme(b.dataset.theme)));
function stepTheme(dt) {
  if (!themeRun) return;
  themeRun.k = Math.min(1, themeRun.k + dt / 2.4);
  const e = themeRun.k * themeRun.k * (3 - 2 * themeRun.k);
  // always run forward in time: 08 -> 23 crosses the afternoon and dusk, 23 -> 08 crosses the night to dawn
  const h1 = themeRun.h1 < themeRun.h0 ? themeRun.h1 + 24 : themeRun.h1;
  const hh = (themeRun.h0 + (h1 - themeRun.h0) * e) % 24;
  paperK = themeRun.p0 + (themeRun.p1 - themeRun.p0) * e;
  const hs = hh < 5 ? 23.5 : Math.min(23.5, hh);
  $('#sunRange').value = hs; setSun(hs);
  if (themeRun.k >= 1) themeRun = null;
}
{ let t0 = 'dark'; try { t0 = localStorage.getItem('2121.theme') || 'dark'; } catch (e) {} setTheme(t0, true); }

// ---------- loop ----------
const clock = new THREE.Timer();
function frame() {
  clock.update(); const dt = Math.min(clock.getDelta(), 0.05);
  if (exhibit && mode !== 'diagram') exhibit.update(clock.getElapsed());
  if (fly) stepFly(dt);
  stepDay(dt); stepTheme(dt); grade.uniforms.paper.value = paperK;
  if (mode === 'diagram') stepDiagram();
  else if (mode === 'tour' && J.on && !fly) stepJourney(dt);
  else if (mode === 'orbit' && !fly) orbit.update();
  else if (!fly) { if (mode === 'walk') stepWalk(dt); applyLook(); }
  const under = toModel(camera.position).z < -1.2;
  underK += ((under ? 1 : 0) - underK) * 0.08;
  renderer.toneMappingExposure = baseExposure * (1 - 0.28 * underK);
  fill.intensity += ((under ? 0.9 : 0.35 + 0.3 * lampLevel) - fill.intensity) * 0.08;
  const lampOn = Math.max(0.35, lampLevel, under ? 1 : 0);
  lamps.forEach((l, i) => { const k = i < 3 ? lampLevel : lampOn; l.intensity += (k * (i < 3 ? 14 : 7) - l.intensity) * 0.08; });
  for (const m of lightMats) m.emissiveIntensity = 1.6 + 2.4 * lampLevel;
  if (Math.abs(camera.fov - fovTarget) > 0.05) { camera.fov += (fovTarget - camera.fov) * 0.05; camera.updateProjectionMatrix(); }
  grade.uniforms.time.value = (grade.uniforms.time.value + 0.37) % 100;
  updateMap();
  renderFrame(dt);
  requestAnimationFrame(frame);
}
frame();
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight; fovTarget = fovFor(mode); camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  composer.setSize(innerWidth, innerHeight); xfRT.setSize(innerWidth * renderer.getPixelRatio(), innerHeight * renderer.getPixelRatio()); sizeDiag();
});
// debug hook for automated checks
window.__2121 = { setShow, get show() { return show; }, view: (c, l) => { if (mode !== 'walk') setMode('walk'); fly = null; camera.position.copy(M(...c)); lookAtPoint(M(...l)); applyLook(); }, get exhibit() { return exhibit; }, get bvh() { return bvh; }, THREE, scene, setMode, goStation, setCut, J, camera, setSun, ready: () => !!bvh, probe: (x, y, z) => { const h = hit(M(x, y, z), DOWN, 30); return h && toModel(h.point); } };
