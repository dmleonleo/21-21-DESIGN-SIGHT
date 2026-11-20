// scene.js — renderer, sky, model loading, model fixes, render loop.
// Split from the single inline script of docs/index.html
// (merged14: #9-#14 serial chain + round-2 review fixes).
// Behaviour unchanged: only the module boundary is new.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { isNight, currentEnvIntensity, stepMomentAnim, setMoment, moment } from './lighting.js';
import { labelSprite, exhibits, labelSprites } from './labels.js';
import { mode, exteriorCamPos, EXT_TARGET, extDefault, camAnimBox, opening, endOpening, beginOpening, applyDeepLink, setMode } from './camera.js';
import { updateWalk, walk, canStand, focusState, ray, ptr } from './walk.js';
import { updateTour, tour } from './tour.js';
import { currentEx } from './ui.js';

export let controls;
const errBox = document.getElementById('err');
function showErr(m){ errBox.style.display='block'; errBox.textContent=m; }
/* ================= Renderer / Scene ================= */
const stage = document.getElementById('stage');
export let renderer;
/* Software rasterizers (SwiftShader/llvmpipe — headless browsers, VMs,
   blocklisted GPUs) render this scene seconds-per-frame at full settings;
   detect them and degrade gracefully instead of appearing frozen. */
let isSoftwareGL = false;

export const scene = new THREE.Scene();
/* ---- Procedural sky with clouds (equirect canvas) ----
   The v14 GLB carries no sky — the clouds lived only in the Blender world —
   so the page paints its own: one equirect canvas used as the background
   AND, through PMREM, as the image-based light source, so the glass facade
   and the folded steel roof pick up real sky reflections. */
function makeSkyTexture(){
  var W=2048,H=1024;
  var c=document.createElement('canvas'); c.width=W/2; c.height=H/2;
  var x=c.getContext('2d');
  x.scale(0.5,0.5); /* paint at half resolution: a quarter of the pixels */
  var g=x.createLinearGradient(0,0,0,H);
  /* #7: Tokyo thin-haze grey-blue — the old postcard blue is gone */
  g.addColorStop(0.00,'#4d6478');
  g.addColorStop(0.30,'#7f96a9');
  g.addColorStop(0.46,'#b6c6cf');
  g.addColorStop(0.52,'#dfe6e8');
  g.addColorStop(0.58,'#c3cbcc');
  g.addColorStop(1.00,'#a3adae');
  x.fillStyle=g; x.fillRect(0,0,W,H);
  var seed=1234567;
  function rnd(){ seed=(seed*16807)%2147483647; return seed/2147483647; }
  function blob(cx,cy,rx,ry,alpha,grey){
    var col=grey?'110,126,142':'255,255,255';
    /* wrap copies only near the seam — most blobs are drawn once, which
       keeps this synchronous paint cheap on throttled CPUs */
    var offs=(cx<280||cx>W-280)?[-W,0,W]:[0];
    for(var k=0;k<offs.length;k++){
      var off=offs[k];
      var rg=x.createRadialGradient(cx+off,cy,0,cx+off,cy,rx);
      rg.addColorStop(0,'rgba('+col+','+alpha+')');
      rg.addColorStop(0.55,'rgba('+col+','+(alpha*0.5)+')');
      rg.addColorStop(1,'rgba('+col+',0)');
      x.fillStyle=rg;
      x.beginPath(); x.ellipse(cx+off,cy,rx,ry,0,0,6.2832); x.fill();
    }
  }
  /* cloud clusters: shaded underside first, then bright overlapping puffs */
  for(var i=0;i<20;i++){
    var cx=rnd()*W, cy=H*(0.14+rnd()*0.30), s=0.6+rnd()*0.9;
    blob(cx,cy+16*s,120*s,26*s,0.20,true);
    var n=5+Math.floor(rnd()*6);
    for(var j=0;j<n;j++){
      blob(cx+(rnd()-0.5)*190*s, cy+(rnd()-0.5)*26*s, (46+rnd()*62)*s, (15+rnd()*13)*s, 0.30+rnd()*0.30,false);
    }
    blob(cx,cy-8*s,58*s,17*s,0.5,false);
  }
  /* thin high wisps */
  for(var w=0;w<10;w++){
    blob(rnd()*W, H*(0.05+rnd()*0.12), 150+rnd()*190, 7+rnd()*6, 0.13+rnd()*0.10,false);
  }
  /* haze at the horizon line */
  var hz=x.createLinearGradient(0,H*0.44,0,H*0.56);
  hz.addColorStop(0,'rgba(255,255,255,0)');
  hz.addColorStop(0.5,'rgba(255,255,255,0.34)');
  hz.addColorStop(1,'rgba(255,255,255,0)');
  x.fillStyle=hz; x.fillRect(0,H*0.44,W,H*0.12);
  var t=new THREE.CanvasTexture(c);
  t.mapping=THREE.EquirectangularReflectionMapping;
  if('colorSpace' in t) t.colorSpace=THREE.SRGBColorSpace; else t.encoding=THREE.sRGBEncoding;
  return t;
}

/* #7: night sky as a gradient, not a flat colour — deep blue-grey with a
   faint warm band at the horizon, so the folded roof's outline stays
   readable against the sky instead of sinking into black. Built lazily
   like the day sky. #4's MOMENTS night bg should use nightSkyTex at
   rebase (same pattern as the day sky texture). */
function makeNightSkyTexture(){
  var W=1024,H=512;
  var c=document.createElement('canvas'); c.width=W; c.height=H;
  var x=c.getContext('2d');
  var g=x.createLinearGradient(0,0,0,H);
  g.addColorStop(0.00,'#1d2632');
  g.addColorStop(0.45,'#2c3947');
  g.addColorStop(0.52,'#3d4c5a');
  g.addColorStop(0.58,'#4a5a66');
  g.addColorStop(1.00,'#232c36');
  x.fillStyle=g; x.fillRect(0,0,W,H);
  var wg=x.createLinearGradient(0,H*0.46,0,H*0.58);
  wg.addColorStop(0,'rgba(214,164,110,0)');
  wg.addColorStop(0.5,'rgba(214,164,110,0.10)');
  wg.addColorStop(1,'rgba(214,164,110,0)');
  x.fillStyle=wg; x.fillRect(0,H*0.46,W,H*0.12);
  var t=new THREE.CanvasTexture(c);
  t.mapping=THREE.EquirectangularReflectionMapping;
  if('colorSpace' in t) t.colorSpace=THREE.SRGBColorSpace; else t.encoding=THREE.sRGBEncoding;
  return t;
}
export let nightSkyTex = null;
export function buildNightSky(){
  if(nightSkyTex) return;
  try{ nightSkyTex=makeNightSkyTexture(); }catch(e){ return; }
}
/* The sky is NOT painted during startup: painting hundreds of gradient
   blobs on the main thread before the model fetch even began was enough
   to stall first paint / DOMContentLoaded on slow CPUs and made the page
   look stuck on the loading screen. Start from a flat sky colour, build
   the real sky a moment later (see the deferred call below). */
export let skyTex = null;
scene.background=new THREE.Color(0x9db1bd);
export function buildSky(){
  if(skyTex) return;
  try{ skyTex=makeSkyTexture(); }catch(e){ return; }
  if(!isNightRef()) scene.background=skyTex;
}
scene.fog=new THREE.Fog(0xc8d3d6,120,280);
/* Environment (IBL) is generated AFTER window load, from a downscaled copy
   of the sky: PMREM generation is GPU work that must not block first paint. */
export let skyEnvTex = null;
export function setupEnvironment(){
  if(skyEnvTex) return;
  if(isSoftwareGL) return; /* PMREM in a software rasterizer stalls for many seconds; the direct lights carry the scene there */
  buildSky();
  if(!skyTex) return;
  try{
    var small=document.createElement('canvas'); small.width=512; small.height=256;
    small.getContext('2d').drawImage(skyTex.image,0,0,512,256);
    var et=new THREE.CanvasTexture(small);
    et.mapping=THREE.EquirectangularReflectionMapping;
    if('colorSpace' in et) et.colorSpace=THREE.SRGBColorSpace; else et.encoding=THREE.sRGBEncoding;
    var pm=new THREE.PMREMGenerator(renderer);
    skyEnvTex=pm.fromEquirectangular(et).texture;
    pm.dispose();
    if(!isNightRef()) scene.environment=skyEnvTex;
    if('environmentIntensity' in scene) scene.environmentIntensity=isNightRef()?0.1:0.5;
  }catch(e){ /* IBL is an enhancement; direct lights still carry the scene */ }
}
/* #4: real-HDRI environment — Overcast Soil (Pure Sky), Poly Haven,
   CC0 1.0 (no attribution required), 1K, 1024x512 Radiance .hdr.
   No Tokyo overcast/dusk HDRI exists on Poly Haven (all 998 screened;
   the only japan-tagged one is a Nagoya garden at sunrise), so a
   location-neutral pure sky is used for scene.environment ONLY — the
   visible sky stays the painted canvas (day) / solid colours (dusk,
   night), so one HDRI serves all four moments. 39% of its pixels are
   above 1.0, so an 8-bit PNG conversion would clip the dynamic range;
   the true .hdr is decoded at runtime with this small RGBE decoder. */
export let hdriEnvTex = null;
function decodeRGBE(buf){
  var b=new Uint8Array(buf), pos=0;
  function readLine(){
    var s=pos;
    while(pos<b.length&&b[pos]!==10) pos++;
    var line='';
    for(var i=s;i<pos;i++) line+=String.fromCharCode(b[i]);
    pos++;
    return line;
  }
  var w=0,h=0,line;
  /* header lines run until the blank line; the resolution line
     ("-Y 512 +X 1024") follows AFTER that blank line, not before it */
  while((line=readLine())!==''){ /* skip header lines */ }
  line=readLine();
  var m=line.match(/-Y\s+(\d+)\s+\+X\s+(\d+)/);
  if(m){ h=parseInt(m[1],10); w=parseInt(m[2],10); }
  if(!w||!h) throw new Error('bad hdr header');
  var data=new Float32Array(w*h*3), p=pos;
  for(var y=0;y<h;y++){
    if(b[p]!==2||b[p+1]!==2) throw new Error('hdr is not RLE');
    p+=4;
    var chs=[];
    for(var c=0;c<4;c++){
      var ch=new Uint8Array(w), x=0;
      while(x<w){
        var n=b[p++];
        if(n>128){ var v=b[p++]; for(var k=0;k<n-128;k++) ch[x++]=v; }
        else { for(var k2=0;k2<n;k2++) ch[x++]=b[p++]; }
      }
      chs.push(ch);
    }
    for(var x2=0;x2<w;x2++){
      var e=chs[3][x2], f=(e===0)?0:Math.pow(2,e-136);
      var idx=(y*w+x2)*3;
      data[idx]=chs[0][x2]*f; data[idx+1]=chs[1][x2]*f; data[idx+2]=chs[2][x2]*f;
    }
  }
  return {width:w,height:h,data:data};
}
export function loadHDRIEnv(){
  if(isSoftwareGL) return; /* PMREM in software GL stalls for many seconds */
  fetch('assets/overcast_soil_puresky_1k.hdr').then(function(r){
    if(!r.ok) throw new Error('hdr '+r.status);
    return r.arrayBuffer();
  }).then(function(buf){
    var hdr=decodeRGBE(buf);
    /* #11 review (Hark 2026-11-19): RGBFormat + FloatType is a
       float-linear-filtered texture, which many iOS devices do not
       support. Convert the decoded RGB floats to RGBA half-floats
       (alpha 1): half-float linear filtering IS supported on iOS,
       and RGBA is the filterable HDR layout. decodeRGBE is untouched
       (its output was validated in Node during #4). */
    var half=new Uint16Array(hdr.width*hdr.height*4);
    for(var i=0,j=0;i<hdr.data.length;i+=3,j+=4){
      half[j]=THREE.DataUtils.toHalfFloat(hdr.data[i]);
      half[j+1]=THREE.DataUtils.toHalfFloat(hdr.data[i+1]);
      half[j+2]=THREE.DataUtils.toHalfFloat(hdr.data[i+2]);
      half[j+3]=THREE.DataUtils.toHalfFloat(1);
    }
    var tex=new THREE.DataTexture(half,hdr.width,hdr.height,THREE.RGBAFormat,THREE.HalfFloatType);
    tex.mapping=THREE.EquirectangularReflectionMapping;
    tex.needsUpdate=true;
    var pm=new THREE.PMREMGenerator(renderer);
    hdriEnvTex=pm.fromEquirectangular(tex).texture;
    pm.dispose(); tex.dispose();
    scene.environment=hdriEnvTex;
    if('environmentIntensity' in scene) scene.environmentIntensity=currentEnvIntensity();
  }).catch(function(){ setupEnvironment(); /* fallback: painted-sky env */ });
}
function isNightRef(){ return typeof isNight!=='undefined'&&isNight; }
/* Sky painting + PMREM are deferred until AFTER the model has loaded
   (onModelLoaded calls them): they compete for the same main thread as
   the GLB parse, and the opaque loading overlay covers the screen until
   then, so building them earlier only delayed the model itself. */

export const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 500); /* #7: architectural 38° (was 50°) */
camera.position.set(20,14.5,-81); /* #7: matches exteriorCamPos */



/* lights — strong directional sun with sharp shadows, sky IBL (scene.environment)
   for ambient/reflections; low fills so the contrast stays photographic */
export const hemi = new THREE.HemisphereLight(0xdde3e6, 0x8a8a80, 0.35); /* #7: greyer sky/ground */ scene.add(hemi);
export const sun = new THREE.DirectionalLight(0xfff2dd, 3.0);
export const fill = new THREE.DirectionalLight(0xc3d2d8, 0.3); /* #7: greyer fill */ fill.position.set(-40,24,-36); scene.add(fill);
scene.add(new THREE.AmbientLight(0xffffff,0.08)); /* #4: 0.06 -> 0.08, kept
   after the #11 review: the baked atlas moved from aoMap to lightMap
   (see onModelLoaded), so the 0.08 is now a brightness floor under the
   lightMap + fill lights, not an aoMap compensation; if real-device
   shots show washout, this is the first knob to turn down. */
/* #11 review (Hark 2026-11-19): the nine PointLights are NOT all gone
   any more. The baked lightmap (second UV, now on material.lightMap)
   carries the indirect light — skylight wash, court light spilling
   underground, G2 wall washing — but until the lightMap is confirmed
   on a real device (SwiftShader skips the HDRI env path), 4 low-intensity
   interior PointLights stay as fill so the basement galleries are not
   dark on a real GPU. No shadows on them — the sun already casts them.
   They join intLights, so the moment system scales them x1.6 at night
   like the SpotLights. Intensities are ~half the originals (main
   @62eeaac6): enough to lift the floor, not enough to flatten the baked
   gradient. (This supersedes the #4 acceptance "PointLight <= 2".) */
export const intLights = [];
function addIntLight(x,y,z,color,intensity,dist){
  var pl=new THREE.PointLight(color,intensity,dist); pl.position.set(x,y,z); scene.add(pl); intLights.push(pl); return pl;
}
function addSpotLight(x,y,z,tx,ty,tz,color,intensity,angle,dist){
  var sp=new THREE.SpotLight(color,intensity,dist,angle,0.5,1.2);
  sp.position.set(x,y,z);
  sp.target.position.set(tx,ty,tz);
  scene.add(sp); scene.add(sp.target);
  intLights.push(sp); return sp;
}

/* #14 review (Hark 2026-11-19) + Leon's decision (#7, 2026-11-19):
   cherry petals REMOVED — drifting sakura all year round reads like a
   postcard and breaks Ando's restraint; it also saves a per-frame
   particle update. (Creation code + animate update deleted, not hidden.) */
export let reducedMotion = false;
/* ================= Blender model (GLB) =================
   design2121.glb — flat hierarchy under WEB_ROOT, objects named SM_*.
   glTF space: x east, y up, z south-ish; ground y=0, basement floor y=-4.8. */
export let model = null;
export let modelReady = false;
export const pickMeshes = [];
/* item 2: every mesh of the loaded GLB. The raycast collision guard,
   the landing ring and the ground snap read colliderMeshes instead
   (see below) — solidMeshes stays as the complete list for reference. */
var solidMeshes=[];
/* #12 review (Hark 2026-11-19): collision-only list. rayWallBlocked,
   floorHitAt and the ground snap used to raycast solidMeshes (every
   mesh: hidden trees, the 55k-tri steel roof, glass, exhibits) with
   no BVH — slow on phones. The #10/#11 compression merged the 637
   v16 objects into 125 meshes, so wall/column/ground geometry can no
   longer be picked out by node name; the filter uses MATERIAL names
   (the discriminator that survived the merge) plus the visible flag.
   On the baked GLB: 131,624 tris -> ~32,880 (25%); roof, trees,
   glass and exhibits are out. The zone tables (canStand) stay the
   first layer; this ray guard is the second. */
var COLLIDER_MATS=['MAT_Concrete','MAT_Concrete_Board','MAT_Concrete_Dark','MAT_White_Wall','MAT_Floor_Concrete','MAT_Granite','MAT_Wood_Floor','MAT_Grass','MAT_Paving','MAT_Dark_Door'  /* #18: MAT_Paving_Dark deleted in the GLB */,'MAT_G3_Frosted','MAT_FarGround'];
export const colliderMeshes = [];
var exhibitMeshes={};   /* '01'..'12' -> [meshes] (all twelve are real objects in the v16 GLB) */
var spinnerPivot=null, lampMeshes=[];

export function canvasTexture(w,h,draw){
  var c=document.createElement('canvas'); c.width=w; c.height=h;
  draw(c.getContext('2d'),w,h);
  var t=new THREE.CanvasTexture(c); t.anisotropy=4; return t;
}



/* Texture decode path — IMPORTANT: GLTFLoader picks its image decoder
   when the GLB is PARSED (in the parser, after the file downloads), not
   when the loader is constructed. When createImageBitmap exists (and
   the UA is not old Safari/Firefox) it decodes the GLB's embedded PNGs
   through createImageBitmap(blob, {premultiplyAlpha:'none',
   colorSpaceConversion:'none'}). On Apple WebKit (Safari / app
   webviews on macOS & iOS) that call can resolve with blank bitmaps:
   every textured material then renders as its default white base
   colour — grass, steel roof, concrete, paving and the tree cards all
   turn into a white clay model, while untextured materials keep their
   colours. Hiding createImageBitmap for the whole load (startLoad →
   onModelLoaded / final loadFailed) forces the classic <img> /
   blob-URL decoder — the path three.js itself uses for Safari < 17 —
   which decodes these PNGs correctly in every engine. Nothing else on
   this page uses createImageBitmap, and the global is restored as soon
   as the parse finishes. */
var _hiddenCIB=null;
function hideCreateImageBitmap(){
  if(_hiddenCIB||!window.createImageBitmap) return;
  _hiddenCIB=window.createImageBitmap;
  try{ window.createImageBitmap=undefined; }catch(e){}
}
function restoreCreateImageBitmap(){
  if(!_hiddenCIB) return;
  try{ window.createImageBitmap=_hiddenCIB; }catch(e){}
  _hiddenCIB=null;
}
/* Asset architecture: the model is NOT embedded in this page. The
   ~1.99 MB Meshopt-compressed GLB ships as its own file,
   assets/design2121.glb, and is fetched by the relative path in
   fetchModel() below; three.module.min.js is likewise an external file,
   as is the Meshopt decoder it needs (assets/meshopt_decoder.js,
   registered on the loader in parseModel). This HTML therefore
   stays ~120 KB — no base64 model blob, no data-URI geometry.
   (The single-file 11 MB HTML that the platform's export produces
   inlines these assets at export time; that is an export packaging
   choice, not how this page is written or served.)

   Robust loading — final architecture, after the failure was finally
   reproduced end-to-end (headless Chromium against a gateway simulator
   that delivers 2.5 MB bursts separated by 100 s of silence and ignores
   Range requests — the delivery profile the artifact gateway shows
   under load, confirmed by its own audit captures stalling at ~7 KB
   delivered in 15 s):

   THE BUG THAT KEPT COMING BACK ("一直加载失败 / 载入中断" on the
   visitor's iPhone AND Mac, while every local test passed): the old
   loader aborted any attempt that made no progress for 90 s. On the
   gateway's bursty delivery, pauses longer than that are NORMAL, so
   nearly every attempt was aborted mid-download; because the gateway
   ignores Range, each retry restarted from byte zero, reached the
   same pause, and was aborted again — an infinite "载入中断，正在
   自动重试…" loop on a connection that would have finished if it
   had simply been left alone. Local tests never reproduced it
   because local servers answer fast and honour Range.

   THE RULE THAT FOLLOWS, AND MUST NOT BE REGRESSED: page code NEVER
   aborts a download — no stall watchdog, no attempt age cap, no
   AbortController. A pending read is left pending for as long as the
   network takes; the browser's own network stack is the only
   watchdog, and it ends an attempt only when the connection truly
   dies (error / close). Only THEN does retry logic run:
   - Bytes already received are KEPT, and the retry resumes with an
     HTTP Range request. A server that ignores Range resends the
     whole body, which is handled as a fresh download — and that
     attempt, too, is given unlimited time, so even a from-zero
     restart on a bursty link now finishes.
   - Retries are unbounded (backoff capped at 10 s): a retry only
     ever follows a real network failure, so there is no loop to
     protect against — the old MAX_LOAD_ATTEMPTS existed only
     because the watchdog manufactured failures.
   - The asset URL never changes (no cache-busting query strings —
     a gateway matching exact paths can 404 those); cache bypass
     uses fetch's cache mode on from-scratch restarts only.
   - The manual 「重新加载」 button (shown after 45 s) abandons the
     pending attempt by sequence number — its late callbacks become
     no-ops — and starts a fresh one, resuming from the held bytes.
     A network 'online' event does the same after a failure.
   - Before parsing, the assembled bytes are verified against the
     HTTP length (when known) and against the GLB's own declared
     length in its header, so a silently truncated body is resumed,
     not parsed.
   - The parse step keeps its own 90 s timeout (parsing is local CPU
     work; a hang there is a decoder deadlock, not patience), runs on
     a fresh loader each time, works on a copy of the bytes, and is
     retried once with the OTHER texture decoder (createImageBitmap
     restored), so a decoder-specific hang cannot stick either. If
     both decoders fail, the manual button restarts the parse.
   The GLB itself was also shrunk 10.46 MB → 7.55 MB (duplicate
   bufferViews merged, opaque PNG textures re-encoded as JPEG, UVs
   dropped from untextured materials; verified pixel-identical
   renders), so a patient download has less wire time to survive. */
var loadDone=false, loadAttempts=0, parseAttempts=0, loadExhausted=false, loadSlowTimer=null, loadRetryTimer=null;
var PARSE_TIMEOUT_MS=90000;
var asmChunks=[], asmLoaded=0, asmTotal=0, asmBuffer=null;
var fetchInFlight=false; /* guards startLoad against a second concurrent download (e.g. the manual button tapped while an attempt is still streaming) — two pumps appending to asmChunks would corrupt the assembly */
var loadSeq=0; /* attempt sequence: bumping it abandons the pending attempt — every callback of an older attempt becomes a no-op */
var loadMsgEl=document.getElementById('loadMsg');
var loadBarWrap=document.getElementById('loadBarWrap');
var loadBar=document.getElementById('loadBar');
var loadRetryBtn=document.getElementById('loadRetry');
function restartLoad(){
  loadExhausted=false;
  loadRetryBtn.style.display='none';
  errBox.style.display='none';
  loadAttempts=0; parseAttempts=0;
  loadSeq++; /* abandon any attempt still pending */
  fetchInFlight=false;
  if(loadRetryTimer){ clearTimeout(loadRetryTimer); loadRetryTimer=null; }
  startLoad();
}
function startLoad(){
  if(loadDone) return;
  if(loadRetryTimer){ clearTimeout(loadRetryTimer); loadRetryTimer=null; }
  loadBarWrap.style.display='block';
  onLoadProgress({loaded:asmLoaded,total:asmTotal});
  /* Purely a UI timer: after 45 s, say the load is still running and
     offer the manual restart. It NEVER touches the download itself —
     a slow gateway is waited out, not aborted. */
  clearTimeout(loadSlowTimer);
  loadSlowTimer=setTimeout(function(){
    if(!loadDone){
      loadMsgEl.textContent='载入时间较长（模型约 7.5 MB），仍在自动继续…也可点「重新加载」再试一次。';
      loadRetryBtn.style.display='inline-block';
    }
  },45000);
  if(asmBuffer){ parseModel(); return; } /* bytes already complete: go straight to parsing */
  if(fetchInFlight) return; /* an attempt is already streaming — let it finish */
  loadAttempts++;
  fetchModel();
}
function fetchModel(){
  var mySeq=++loadSeq;
  var resumeFrom=asmLoaded;
  if(loadAttempts>1){
    loadMsgEl.textContent=resumeFrom>0
      ?('连接中断，正在从 '+Math.round(resumeFrom/Math.max(asmTotal,1)*100)+'% 处继续载入…（第 '+loadAttempts+' 次尝试）')
      :('正在重新载入建筑模型…（第 '+loadAttempts+' 次尝试）');
  }else{
    loadMsgEl.textContent='正在载入建筑模型…';
  }
  fetchInFlight=true;
  var settled=false;
  function alive(){ return !settled&&mySeq===loadSeq&&!loadDone; }
  function cleanup(){ settled=true; if(mySeq===loadSeq) fetchInFlight=false; }
  function fail(err){
    if(!alive()) return;
    cleanup();
    loadFailed(err);
  }
  var headers={};
  if(resumeFrom>0) headers['Range']='bytes='+resumeFrom+'-';
  var fetchOpts={headers:headers};
  if(resumeFrom===0&&loadAttempts>1) fetchOpts.cache='no-store';
  var req;
  try{ req=fetch('assets/design2121.glb',fetchOpts); }catch(e){ fail(e); return; }
  req.then(function(res){
    if(!alive()) return;
    if(res.status===416){
      /* Range starts past the end of the file: we already hold every
         byte (or the server disagrees about the size — start over). */
      cleanup();
      if(asmTotal>0&&asmLoaded>=asmTotal) finishDownload();
      else{ asmChunks=[]; asmLoaded=0; asmTotal=0; loadFailed(new Error('HTTP 416')); }
      return;
    }
    if(!res.ok&&res.status!==206){ fail(new Error('HTTP '+res.status)); return; }
    var appending=false;
    if(resumeFrom>0&&res.status===206){
      var cr=res.headers.get('Content-Range')||'';
      var m=cr.match(/bytes\s+(\d+)-(\d+)\/(\d+|\*)/);
      if(m&&parseInt(m[1],10)===resumeFrom){
        appending=true;
        if(m[3]!=='*') asmTotal=parseInt(m[3],10);
      }else{
        /* The partial body does not line up with what we hold: drop
           it and let the next attempt fetch the file fresh. */
        asmChunks=[]; asmLoaded=0; asmTotal=0;
        fail(new Error('续传响应不匹配'));
        return;
      }
    }
    if(!appending){
      /* First attempt, or the server ignored Range and is sending the
         whole file again: this body replaces whatever was held. */
      asmChunks=[]; asmLoaded=0;
      asmTotal=parseInt(res.headers.get('Content-Length')||'0',10)||0;
    }else if(!asmTotal){
      var cl2=parseInt(res.headers.get('Content-Length')||'0',10)||0;
      if(cl2) asmTotal=resumeFrom+cl2;
    }
    onLoadProgress({loaded:asmLoaded,total:asmTotal});
    var reader=null;
    if(res.body&&typeof res.body.getReader==='function'){
      try{ reader=res.body.getReader(); }catch(e){ reader=null; }
    }
    if(reader){
      (function pump(){
        reader.read().then(function(r){
          if(!alive()) return; /* abandoned or finished: stop quietly */
          if(r.done){ cleanup(); finishDownload(); }
          else{
            asmChunks.push(r.value); asmLoaded+=r.value.length;
            onLoadProgress({loaded:asmLoaded,total:asmTotal});
            pump();
          }
        },fail);
      })();
    }else{
      /* No streamable body (older engines): a plain whole-body read —
         it resolves when the body is complete, however long the
         network takes, and rejects only on a real failure. */
      res.arrayBuffer().then(function(ab){
        if(!alive()) return;
        var u8=new Uint8Array(ab);
        asmChunks.push(u8); asmLoaded+=u8.length;
        onLoadProgress({loaded:asmLoaded,total:asmTotal});
        cleanup(); finishDownload();
      },fail);
    }
  }).catch(fail);
}
function finishDownload(){
  if(loadDone) return;
  /* A stream that ends early is resumed, never parsed. */
  if(asmTotal>0&&asmLoaded<asmTotal){ loadFailed(new Error('下载不完整')); return; }
  var buf=new Uint8Array(asmLoaded), off=0;
  for(var i=0;i<asmChunks.length;i++){ buf.set(asmChunks[i],off); off+=asmChunks[i].length; }
  /* GLB self-check: magic 'glTF' and the total length the file
     declares for itself at bytes 8–11. This also catches truncation
     when the server sent no Content-Length at all. */
  var declared=0;
  if(buf.length>=12&&buf[0]===0x67&&buf[1]===0x6C&&buf[2]===0x54&&buf[3]===0x46){
    declared=(buf[8]|(buf[9]<<8)|(buf[10]<<16)|(buf[11]<<24))>>>0;
  }
  if(!declared||declared<buf.length){
    asmChunks=[]; asmLoaded=0; asmTotal=0;
    loadFailed(new Error('模型文件校验失败'));
    return;
  }
  if(declared>buf.length){
    asmTotal=declared;
    loadFailed(new Error('下载不完整'));
    return;
  }
  asmChunks=[];
  asmBuffer=buf.buffer;
  parseModel();
}
function parseModel(){
  if(loadDone||!asmBuffer) return;
  parseAttempts++;
  /* First parse hides createImageBitmap (the WebKit blank-bitmap
     guard); a retry parses with the native decoder instead, so one
     decoder's failure cannot be the end of the road. Each attempt
     gets a fresh loader and its own copy of the bytes. */
  if(parseAttempts>1) restoreCreateImageBitmap(); else hideCreateImageBitmap();
  var settled=false;
  var timer=setTimeout(function(){
    if(settled||loadDone) return;
    settled=true;
    loadFailed(new Error('模型解析超时'));
  },PARSE_TIMEOUT_MS);
  var ld=new GLTFLoader();
  /* #4: the shipped GLB is Meshopt-compressed (EXT_meshopt_compression,
     via #3's pipeline); the decoder ships as assets/meshopt_decoder.js
     (self-contained, wasm inlined). Without it the parse fails. */
  if(window.MeshoptDecoder) ld.setMeshoptDecoder(MeshoptDecoder);
  try{
    ld.parse(asmBuffer.slice(0),'',function(gltf){
      if(settled) return;
      settled=true; clearTimeout(timer);
      onModelLoaded(gltf);
    },function(err){
      if(settled) return;
      settled=true; clearTimeout(timer);
      loadFailed(err||new Error('模型解析失败'));
    });
  }catch(e){
    if(!settled){ settled=true; clearTimeout(timer); loadFailed(e); }
  }
}
function onLoadProgress(xhr){
  if(xhr.total){
    var p=Math.round(xhr.loaded/xhr.total*100);
    loadBar.style.width=p+'%';
    loadMsgEl.textContent='正在载入建筑模型… '+p+'%';
  }else if(xhr.loaded){
    loadMsgEl.textContent='正在载入建筑模型… '+(xhr.loaded/1048576).toFixed(1)+' MB';
  }
}
function loadFailed(err){
  if(loadDone) return;
  clearTimeout(loadSlowTimer);
  var parsePhase=!!asmBuffer;
  /* Download failures retry forever: a retry only ever follows a
     REAL network failure now (page code aborts nothing), and each
     retry resumes from the held bytes, so persistence is the whole
     strategy — there is no attempt budget to exhaust. Parse
     failures get exactly one retry, with the other texture decoder;
     after that the manual button restarts the parse. */
  if(parsePhase&&parseAttempts>=2){
    loadExhausted=true;
    restoreCreateImageBitmap();
    loadMsgEl.textContent='建筑模型解析失败，请点「重新加载」再试一次。';
    loadRetryBtn.style.display='inline-block';
    showErr('建筑模型解析失败：'+(err&&err.message||err));
    return;
  }
  loadMsgEl.textContent=parsePhase?'解析中断，正在换一种解码方式重试…':'载入中断，正在自动重试…';
  var delay=parsePhase?600:Math.min(1200*Math.max(1,loadAttempts),10000);
  loadRetryTimer=setTimeout(function(){
    loadRetryTimer=null;
    if(parsePhase) parseModel(); else startLoad();
  },delay);
}

/* ================= G3 roof clip fix — REMOVED in v17 (#17) =================
   The v16 GLB's sloped G3 ceiling rose through the folded cafe roof along
   its north band, and a load-time function used to pull its vertices back
   under the roof. The v17 model clamps the ceiling to roof-0.30 m in
   Blender (probe: 0 ceiling-above-roof violations across the whole G3
   quad) and rebuilds the roof as a folded plate, so the page-side
   correction is deleted — the model is correct on its own now. */
/* ================= Exterior trees: keep only three =================
   The v19 GLB plants 21 trees on the grounds (each one a trunk plus
   four side cards and two top cards, named SM_Tree_Trunk_<key>,
   SM_Tree_Card_<key>_<n>, SM_Tree_TopCard_<key>_<n>). At Leon's
   request only three stay — a single calm, evenly spaced row along
   the north lawn belt, west / centre / east, so the folded roofs read
   against open grass instead of a thicket of leaf cards:
     west   x -20.5, z 22.9
     centre x  11.6, z 22.1
     east   x  34.6, z 24.8
   (#21B: the belt moved 9 m north in the rebuild, so the kept keys
   are the same three trunks with y -9; the old keys no longer exist
   in the GLB and keeping them would hide all three.)
   The other eighteen grounds trees are hidden (visible=false, so
   they neither render nor cast shadows). The one tree inside the
   sunken courtyard planter (key 31.3_-0.56, trunk base at basement
   level) is not a grounds tree and is left untouched. */
var KEEP_TREE_KEYS={
  '-20.506536543695546_-22.861288898608986':true,
  '11.640643481283298_-22.104740129882714':true,
  '34.563058939808485_-24.770751238658896':true,
  '31.3_-0.56':true /* sunken-courtyard planter tree — not a grounds tree */
};
function pruneExteriorTrees(){
  model.traverse(function(o){
    var nm=o.name||'';
    var key=null;
    if(nm.indexOf('SM_Tree_Trunk_')===0) key=nm.slice('SM_Tree_Trunk_'.length);
    else if(nm.indexOf('SM_Tree_Card_')===0) key=nm.slice('SM_Tree_Card_'.length).replace(/_\d+$/,'');
    else if(nm.indexOf('SM_Tree_TopCard_')===0) key=nm.slice('SM_Tree_TopCard_'.length).replace(/_\d+$/,'');
    if(key!==null&&!KEEP_TREE_KEYS[key]) o.visible=false;
  });
}

/* #7: mute a texture's saturation in place (draw -> mix toward luma ->
   re-upload). Used for the turf / flower-bed maps: their baked colours
   are postcard-saturated and no colour multiplier can desaturate a
   texture (multiplication can only darken). Runs once at load. */
function desaturateTexture(tex,amount){
  if(!tex||!tex.image||amount<=0) return;
  try{
    var img=tex.image, w=img.width, h=img.height;
    if(!w||!h||w>1024||h>1024) return;
    var c=document.createElement('canvas'); c.width=w; c.height=h;
    var x=c.getContext('2d',{willReadFrequently:true});
    x.drawImage(img,0,0);
    var d=x.getImageData(0,0,w,h), px=d.data;
    for(var i=0;i<px.length;i+=4){
      var l=0.299*px[i]+0.587*px[i+1]+0.114*px[i+2];
      px[i]+=(l-px[i])*amount; px[i+1]+=(l-px[i+1])*amount; px[i+2]+=(l-px[i+2])*amount;
    }
    x.putImageData(d,0,0);
    tex.image=c; tex.needsUpdate=true;
  }catch(e){ /* unreadable texture: leave it alone */ }
}
/* #7: page-side material pass (see issue #7 for what stays model-side).
   - Steel roof -> matte dark grey (roughness up, metalness down, tone deepened).
   - Turf / far ground / flower beds -> desaturated (texture-level for the
     two maps; colour factor for the untextured far ground). The flower
     beds drop from signal red to dusty rose: red stays with the G2 sphere.
   - Concrete is already neutral grey in the baked textures: left alone.
     Template grid, tie-hole alignment and tiling repetition need the model.
   - Exhibits: geometry is the limiter; ceramic/lacquer/bamboo/paper params
     are already differentiated in the GLB. Left alone. */
function applyAestheticMaterials(){
  if(!model) return;
  var done={};
  model.traverse(function(o){
    if(!o.isMesh||!o.material||Array.isArray(o.material)) return;
    var m=o.material, mn=m.name||'';
    if(mn==='MAT_Steel_Roof'&&!done.roof){
      done.roof=true;
      m.roughness=0.88; m.metalness=0.05;
      if(m.color) m.color.multiplyScalar(0.72);
    }
    if(mn==='MAT_Grass'&&m.map&&!done.grass){ done.grass=true; desaturateTexture(m.map,0.45); }
    if(mn==='MAT_FarGround'&&!done.far){
      done.far=true;
      if(m.color) m.color.setRGB(1,1,1); /* #18: MAT_FarGround now carries a radial-gradient texture — keep the colour white so the texture is not multiplied down */
    }
  });
}
function onModelLoaded(gltf){
  if(loadDone) return;
  loadDone=true;
  restoreCreateImageBitmap(); /* parse finished — the texture decoder choice is locked in */
  clearTimeout(loadSlowTimer);
  model=gltf.scene; scene.add(model);
  model.traverse(function(o){ if(o.isMesh){ solidMeshes.push(o); if(o.visible!==false&&o.material&&!Array.isArray(o.material)&&COLLIDER_MATS.indexOf(o.material.name)>=0) colliderMeshes.push(o); } });
  model.traverse(function(o){
    if(o.isMesh){
      o.castShadow=true; o.receiveShadow=true;
      if(o.name&&o.name.indexOf('SM_Tree_')===0) o.castShadow=false; /* #18: background tree belt casts no shadow */
      var mn=o.material&&o.material.name;
      if(mn==='MAT_Glass'){
        /* #4: the baked GLB carries plain transparent glass (transmission
           0, base alpha 0.18) — normalise to opacity 0.32 so the facade
           reads as glass: visible and reflective, neither a solid wall
           nor invisible. The GLB JSON is verified to contain no
           KHR_materials_transmission (see the #4 PR; the #21A web
           pipeline strips it in build_join_21A.mjs — the Blender
           source GLB keeps it, the web GLB does not). */
        o.material=o.material.clone();
        o.material.transparent=true;
        o.material.opacity=0.32;
        o.material.depthWrite=false;
      }else if(o.material&&!Array.isArray(o.material)&&'transmission' in o.material&&o.material.transmission>0){
        /* safety net: no transmission material may survive in the scene —
           KHR transmission forces a second full-scene render every frame */
        o.material=o.material.clone();
        o.material.transmission=0;
        o.material.transparent=true;
        o.material.opacity=0.38;
        o.material.depthWrite=false;
      }
      var mn=o.material&&o.material.name;
      /* #11 review (Hark 2026-11-19): the baked atlas was attached as
         aoMap (glTF occlusionTexture), which in three.js only DARKENS
         the indirect/env light — "skylight wash, court light spilling
         underground" never appears as light. At runtime the atlas is
         moved to material.lightMap (channel 1 = the second UV set the
         bake used), so it ADDS the baked indirect light; aoMap is
         cleared (the atlas is a light map, not an occlusion map — a
         separate soft AO would need a new bake). lightMapIntensity 1.0
         keeps the atlas as authored. Idempotent: shared materials are
         moved once, later meshes see aoMap already null and skip. */
      if(o.material&&!Array.isArray(o.material)&&o.material.aoMap){
        var lm=o.material.aoMap;
        o.material.lightMap=lm;
        if('channel' in lm) lm.channel=1;
        o.material.lightMapIntensity=1.0;
        o.material.aoMap=null;
        o.material.needsUpdate=true;
      }
      /* Meshopt-quantized GLB bakes each mesh's half-extent into its node scale
         (lamps 0.15, downlights 0.07); the pulse must multiply that base scale,
         not overwrite it — overwriting inflates lamps ~6.7x / downlights ~14x. */
      if(mn==='MAT_Pendant_Light'&&o.material.emissive){ o.material=o.material.clone(); o.material.emissive=new THREE.Color(0xffc98a); o.material.emissiveIntensity=0.9; o.userData.baseScale=o.scale.x; lampMeshes.push(o); }
      if((mn==='MAT_LightStrip'||mn==='MAT_Skylight')&&o.material.emissive){ o.material=o.material.clone(); o.material.emissive=new THREE.Color(0xfff3d0); o.material.emissiveIntensity=0.55; }
      /* capture group must keep the leading zero: exhibitMeshes is keyed
         '01'..'12' to match the exhibits data (key:'01'…). Capturing only
         the digit ('1'…'9') silently orphaned every mesh — tap-picking
         found nothing. The v16 GLB contains all twelve exhibits as real
         objects (07–12 are distinct works, not copies of 01–06). */
      var m=o.name.match(/^SM_EXHIBIT_(0[1-9]|1[0-2])_/);
      if(m){ (exhibitMeshes[m[1]]=exhibitMeshes[m[1]]||[]).push(o); }
    }
  });
  /* The model is in the scene: let the visitor in NOW. Everything
     below this line is enhancement (texture health check, spinner,
     roof / stair corrections, labels) — none of it may hold the
     loading screen hostage if it throws, so the overlay is dismissed
     here and each step below runs under its own guard. (Previously
     the overlay only came down at the very end of this function, so
     one throwing enhancement read as "the model failed to load".) */
  modelReady=true;
  renderer.shadowMap.needsUpdate=true; /* bake the sun shadow map once */
  document.getElementById('loading').classList.add('hide');
  document.body.classList.add('scene-blur'); /* #6.2: the scene starts blurred, sharpens as deferred work finishes */
  /* Texture health check: sample every unique base-colour map. If one
     decoded to a blank white image (the WebKit failure guarded against
     at the loader above), say so on screen instead of silently showing
     a white clay model. A real texture — even pale concrete — never
     averages to uniform near-white at this scale. */
  try{ (function(){
    var seen=[], broken=0;
    model.traverse(function(o){
      if(o.isMesh&&o.material&&o.material.map&&seen.indexOf(o.material.map)<0) seen.push(o.material.map);
    });
    var c=document.createElement('canvas'); c.width=4; c.height=4;
    var x=c.getContext('2d',{willReadFrequently:true});
    seen.forEach(function(tex){
      var img=tex.image;
      if(!img||!img.width||!img.height){ broken++; return; }
      try{
        x.clearRect(0,0,4,4); x.drawImage(img,0,0,4,4);
        var d=x.getImageData(0,0,4,4).data, allWhite=true;
        for(var i=0;i<d.length;i+=4){ if(d[i]<248||d[i+1]<248||d[i+2]<248){ allWhite=false; break; } }
        if(allWhite) broken++;
      }catch(e){ /* an unreadable image cannot be judged here; rendering is the test */ }
    });
    if(broken>0) showErr('模型贴图有 '+broken+' 张未能正确解码，画面会发白。请刷新页面重试；若仍如此，请换用最新版 Safari / Chrome 打开。');
  })(); }catch(e){ /* the health check is advisory only */ }
  /* The v16 GLB is used exactly as exported — no procedural stretching,
     no cloned exhibits. Its basement outline (floor x -10..52, z -16..7,
     ~1,336 m²) extends EAST to x=52, and all twelve exhibits are real
     objects in the file at their v16 positions. */
  /* rotating centrepiece: pivot on Exhibit 06 ring + core (v16: at x=36, z=-2.5) */
  try{
    var ring=model.getObjectByName('SM_EXHIBIT_06_Ring');
    var core=model.getObjectByName('SM_EXHIBIT_06_Core');
    if(ring){
      spinnerPivot=new THREE.Group();
      spinnerPivot.position.set(36,-2.7,-2.5);
      model.add(spinnerPivot);
      spinnerPivot.attach(ring);
      if(core) spinnerPivot.attach(core);
    }
  }catch(e){ /* spinner is decorative */ }
  try{ pruneExteriorTrees(); }catch(e){ /* tree pruning is an enhancement */ }
  try{ applyAestheticMaterials(); }catch(e){ /* aesthetic material pass is an enhancement */ }
  /* exhibit labels */
  try{
    labelSprite('01 · 一块布 A-POC',32,-0.5,-9.5);
    labelSprite('02 · 光的织物',35,-0.4,-7.0);
    labelSprite('03 · 坐的设计',42,-3.2,-8.2);
    labelSprite('04 · 字与形',38,-0.6,-15.5);
    labelSprite('05 · 器物',46,-2.2,-10.0);
    labelSprite('06 · 转动的圆',36,-0.9,-2.5);
    labelSprite('07 · Akari 纸灯',48,-3.0,-4.5);
    labelSprite('08 · 急须与茶杯',47,-3.4,-13.5);
    labelSprite('09 · 暖帘',29.5,-2.2,1.0);
    labelSprite('10 · 漆器便当盒',15,-3.4,3.5);
    labelSprite('11 · 竹篮',28,-3.6,-4.0);
    labelSprite('12 · 茶碗与茶筅',6,-3.4,5.5);
    labelSprite('G3 · Gallery 3（西翼）',-20,1.2,0.5,true);
  }catch(e){ /* labels are an enhancement */ }
  /* register exhibits for picking */
  exhibits.forEach(function(ex){
    (exhibitMeshes[ex.key]||[]).forEach(function(mesh){
      mesh.userData.exhibit=ex; pickMeshes.push(mesh);
    });
  });
  /* now that the model is on screen, build the cloudy sky + IBL */
  setTimeout(function(){ buildSky(); setupEnvironment(); loadHDRIEnv(); beginOpening(); },60); /* #4: real-HDRI env + #6.2: opening glide */
  /* item 5: a shared link (#exhibit-07, #tour-5, ...) lands here */
  try{ applyDeepLink(); }catch(e){ /* a bad hash must not break the page */ }
}
/* #7: keep verticals vertical — a shift-lens. Architectural photography
   does not tilt the camera: it keeps the film level and shifts the lens.
   After the frame's camera orientation is set, level the camera to its
   yaw and shift the film window vertically so the aim point stays
   centred. The framing (centre + FOV) is unchanged; only the
   convergence is gone. Skipped in walk mode (first-person pitch is the
   visitor's own) and when looking steeply down (aerial: no verticals
   to keep). #5's raycast picking reads the same projection matrix, so
   click-to-move keeps working through the offset at rebase. */
var SHIFT_MAX_PITCH=0.44; /* ~25 degrees */
function applyShiftLens(){
  if(mode==='walk'||!camera){ camera.clearViewOffset(); return; }
  var fwd=new THREE.Vector3(); camera.getWorldDirection(fwd);
  var pitch=Math.asin(Math.max(-1,Math.min(1,fwd.y)));
  if(Math.abs(pitch)<0.01||Math.abs(pitch)>SHIFT_MAX_PITCH){ camera.clearViewOffset(); return; }
  var yaw=Math.atan2(-fwd.x,-fwd.z);
  camera.rotation.set(0,yaw,0,'YXZ');
  var rel=controls.target.clone().sub(camera.position);
  var dist=Math.hypot(rel.x,rel.z);
  if(dist<0.1){ camera.clearViewOffset(); return; }
  var ndcY=(rel.y/dist)/Math.tan(camera.fov*Math.PI/360);
  var w=renderer.domElement.width, h=renderer.domElement.height;
  camera.setViewOffset(w,h,0,-ndcY*h/2,w,h);
  camera.updateProjectionMatrix();
}
/* ================= Resize & loop ================= */
function resize(){
  var w=stage.clientWidth||window.innerWidth, h=stage.clientHeight||window.innerHeight;
  renderer.setSize(w,h); camera.aspect=w/h;
  camera.fov=camera.aspect<0.85?60:38; /* #7: 38° landscape; portrait 60° so the two wings still fit */
  camera.updateProjectionMatrix();
  /* keep the default exterior framing fitted when the viewport changes
     (rotation, webview resize) — unless the user has orbited or picked a
     preset view, in which case their framing is left alone */
  if(mode==='exterior'&&extDefault&&!camAnimBox.current&&!opening){ camera.position.copy(exteriorCamPos()); controls.target.copy(EXT_TARGET); }
}

var lastNow=performance.now(), elapsed=0;
/* ================= Debug HUD (issue #3) =================
   Shows renderer.info (draw calls / triangles) for the model-
   compression work. Hidden by default; enable with ?debug=1 in
   the URL, #debug, or Shift+D. Updated at most twice a
   second so it never costs a layout per frame. */
var dbgHud=document.getElementById('dbgHud');
var dbgLast=0;
function setDebug(on){
  document.body.classList.toggle('debug',!!on);
  if(dbgHud&&!on) dbgHud.textContent='';
}
if(/[?&]debug=1/.test(location.search)||location.hash==='#debug') setDebug(true);
/* #10 review (Hark 2026-11-19): bare D clashed with walk-mode WASD
   (walk.keys['d'] = move right), so the panel no longer listens to
   it. Shift+D still toggles (repeat-guarded); ?debug=1 / #debug
   in the URL work as before. */
window.addEventListener('keydown',function(e){
  if(e.repeat) return;
  if(e.key&&e.key.toLowerCase()==='d'&&e.shiftKey&&!e.metaKey&&!e.ctrlKey&&!e.altKey) setDebug(!document.body.classList.contains('debug'));
});
function updateDbgHud(nowMs){
  if(!document.body.classList.contains('debug')||!dbgHud||!renderer) return;
  if(nowMs-dbgLast<500) return;
  dbgLast=nowMs;
  var r=renderer.info.render, m=renderer.info.memory;
  dbgHud.textContent='calls '+r.calls+' · tris '+r.triangles+' · geo '+m.geometries+' · tex '+m.textures;
}
var renderCount=0; /* frames actually drawn — the debug handle reads this */
function animate(){
  requestAnimationFrame(animate);
  try{
    var nowMs=performance.now();
    var dt=Math.min((nowMs-lastNow)/1000,0.05); lastNow=nowMs; elapsed+=dt;
    var t=elapsed;
    stepMomentAnim(nowMs); /* #4: 2.5 s light-moment transition */
    if(opening){
      /* #6.2 opening glide: ease along the roof edge, then hand over */
      var ok=(nowMs-opening.s)/opening.d;
      if(ok>=1){ endOpening(false); }
      else{
        var oe=ok<0.5?4*ok*ok*ok:1-Math.pow(-2*ok+2,3)/2;
        camera.position.lerpVectors(opening.p0,opening.p1,oe);
        controls.target.lerpVectors(opening.t0,opening.t1,oe);
      }
    }else if(camAnimBox.current&&mode!=='walk'&&mode!=='tour'){
      var k=Math.min(1,(performance.now()-camAnimBox.current.s)/camAnimBox.current.d);
      var e=1-Math.pow(1-k,3);
      camera.position.lerpVectors(camAnimBox.current.p0,camAnimBox.current.p1,e);
      controls.target.lerpVectors(camAnimBox.current.t0,camAnimBox.current.t1,e);
      if(k>=1) camAnimBox.current=null;
    }
    if(!opening){
      if(mode==='walk') updateWalk(dt,nowMs);
      else if(mode==='tour'){ updateTour(nowMs); camera.lookAt(controls.target); }
      else controls.update();
      applyShiftLens(); /* #7: keep verticals vertical (shift-lens) */
    }
    /* #12 review (Hark 2026-11-19): on-demand rendering +
       adaptive DPR are removed from this PR into a separate PR
       (extracted code: review-round2/chain/extracted-on-demand-dpr.md)
       — the page now renders every frame, as before #5. */
    if(spinnerPivot) spinnerPivot.rotation.y=t*0.45;
    lampMeshes.forEach(function(o,i){ var s=1+Math.sin(t*2+i)*0.08; var b=o.userData.baseScale||1; o.scale.set(b*s,b*s,b*s); });
    /* In-scene labels: cap their screen size at close range and fade
       them out when the camera is right on top of them (issue #2.3).
       A sprite's screen size grows as 1/distance, so standing at an
       exhibit's stand point (2.6 m from its label) used to fill the
       frame with a clipped fragment of the text. Below 8 m the sprite
       is shrunk in proportion to distance, holding its angular size
       at the value it has at 8 m; below 2 m it fades out, gone at 1 m. */
    for(var li=0;li<labelSprites.length;li++){
      var sp=labelSprites[li];
      if(!sp.visible) continue;
      var ld=camera.position.distanceTo(sp.position);
      var ls=Math.min(1,ld/8);
      sp.scale.set(2.7*ls,0.55*ls,1);
      sp.material.opacity=0.96*Math.max(0,Math.min(1,(ld-1)/1));
    }
    renderCount++;
    renderer.render(scene,camera);
    updateDbgHud(nowMs);
  }catch(err){
    showErr('渲染出错：'+err.message);
  }
}
/* debug handle for testing and review (not part of the UI): read-only
   snapshots of the interaction state — mode, walk position, tour stop,
   focus, pixel ratio and renderer.info. A review can drive the page
   through the normal UI and read the state back here. */
window.__2121={
  get mode(){ return mode; },
  get walkPos(){ return walk.pos.toArray(); },
  get walkLevel(){ return walk.level; },
  get walkTarget(){ return walk.clickTarget; },
  get tourIdx(){ return tour.idx; },
  get tourDwell(){ return tour.dwellDur; },
  get tourPhase(){ return tour.phase; },
  get exhibit(){ return currentEx?currentEx.key:null; },
  get focus(){ return focusState?(focusState.mode+':'+(focusState.ex?focusState.ex.key:'')):null; },
  get pixelRatio(){ return renderer.getPixelRatio(); },
  get renderInfo(){ var i=renderer.info.render; return {calls:i.calls,triangles:i.triangles}; },
  get frames(){ return renderCount; },
  get colliders(){ return colliderMeshes.length; },
  get hash(){ return location.hash; },
  get clickBlocked(){ return walk.clickBlocked; },
  /* read-only collision probes (debug only) */
  canStandAt: function(x,z){ return canStand(x,z); },
  wallGuard: function(fx,fz,tx,tz){
    var dx=tx-fx, dz=tz-fz, dist=Math.hypot(dx,dz);
    if(dist<0.01||!colliderMeshes.length) return {blocked:false};
    ray.set(new THREE.Vector3(fx,walk.pos.y-0.45,fz),new THREE.Vector3(dx/dist,0,dz/dist));
    ray.far=dist+0.4;
    var hits=ray.intersectObjects(colliderMeshes,false);
    ray.far=Infinity;
    return {blocked:hits.length>0, hit: hits.length?{name:hits[0].object.name,dist:+hits[0].distance.toFixed(2)}:null};
  },
  project: function(x,y,z){
    var v=new THREE.Vector3(x,y,z).project(camera);
    return {x:(v.x*0.5+0.5)*window.innerWidth, y:(-v.y*0.5+0.5)*window.innerHeight, behind:v.z>1};
  },
  /* read-only pick probe: what would a tap at (sx,sy) hit? (debug only)
     floor mirrors floorHitAt: the first hit whose world normal faces up. */
  debugPick: function(sx,sy){
    var r=renderer.domElement.getBoundingClientRect();
    ptr.x=((sx-r.left)/r.width)*2-1; ptr.y=-((sy-r.top)/r.height)*2+1;
    ray.setFromCamera(ptr,camera);
    var eh=ray.intersectObjects(pickMeshes,false);
    var sh=ray.intersectObjects(colliderMeshes,false);
    var fl=null;
    for(var i=0;i<sh.length;i++){
      var n=sh[i].face?sh[i].face.normal:null;
      var wn=n?n.clone().transformDirection(sh[i].object.matrixWorld):null;
      if(wn&&wn.y>0.5){ fl={name:sh[i].object.name,point:sh[i].point.toArray().map(function(v){ return +v.toFixed(2); })}; break; }
    }
    return {
      ex: eh.length?{name:eh[0].object.name,ex:eh[0].object.userData.exhibit?eh[0].object.userData.exhibit.key:null,dist:+eh[0].distance.toFixed(2)}:null,
      solid: sh.length?{name:sh[0].object.name,dist:+sh[0].distance.toFixed(2)}:null,
      floor: fl
    };
  }
};
/* #4: read-only debug hook for automated verification (does not affect the
   UI). Lets a test drive moments/modes and read renderer state without
   reaching into the closure. */
window.__2121={
  setMoment:function(n){ setMoment(n); },
  setMode:function(n,k){ setMode(n,k); },
  getMoment:function(){ return moment; },
  getState:function(){
    var ri=renderer.info?renderer.info.render:null;
    return {
      moment:moment,
      toneMapping:renderer.toneMapping,
      pointLights:scene.children.filter(function(o){ return o.isPointLight; }).length,
      spotLights:scene.children.filter(function(o){ return o.isSpotLight; }).length,
      hasEnv:!!scene.environment,
      loadDone:loadDone,
      drawCalls:ri?ri.calls:null,
      triangles:ri?ri.triangles:null
    };
  }
};

/* Runs the page's original top-level statements, in their original order:
   error handlers -> renderer -> controls -> lights -> loader.
   Returns false only when WebGL is unavailable (the original script
   returned early in that case, before any listener was attached); the
   entry script then skips the remaining inits, exactly as before. */
export function initScene(){
  window.onerror=function(m,s,l){ showErr('页面出错：'+m+'（行 '+l+'）'); return false; };
  window.addEventListener('unhandledrejection',function(e){ showErr('页面出错：'+(e.reason&&e.reason.message||e.reason)); });
  try{
    /* item 8: preserveDrawingBuffer — on-demand rendering freezes the
       frame when the exterior is idle, and without preserve the canvas
       reads back black in screenshots (and after a compositor surface
       loss) until the next interaction redraws it. Verified: with the
       freeze on, an idle exterior screenshotted black even 8 s after a
       fresh frame had rendered. The cost is one retained buffer; the
       power saving (no redraws while idle) is unaffected. */
    renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance',preserveDrawingBuffer:true});
  }catch(e){
    /* No WebGL (old webview, GPU blocklist, software fallback removed):
       show a DISTINCT error state, not the loading screen — different
       ground, error title, static line drawing, explanation, working
       reload (issue #2.9). The loading screen and the error screen
       used to be identical, so this read as "still loading", and every
       button was dead because the script returned before wiring them.
       The pure-interface controls (theme, archive, hide) are wired here
       with minimal handlers so the page is not dead without WebGL. */
    var loadingEl=document.getElementById('loading');
    loadingEl.classList.add('error');
    var errMark=loadingEl.querySelector('.mark'); if(errMark) errMark.textContent='3D 无法启动';
    var errMicro=loadingEl.querySelector('.lmicro'); if(errMicro) errMicro.textContent='WEBGL UNAVAILABLE';
    document.getElementById('loadMsg').textContent='此浏览器或设备未提供 WebGL，3D 展厅无法启动。请换用最新版 Safari / Chrome 打开本页，或在电脑上查看。';
    var retryBtn=document.getElementById('loadRetry');
    retryBtn.style.display='inline-block';
    retryBtn.textContent='重新加载';
    retryBtn.addEventListener('click',function(){ location.reload(); });
    (function(){
      var tb=document.getElementById('themeToggle');
      if(tb) tb.addEventListener('click',function(){
        var day=document.body.classList.toggle('day');
        tb.setAttribute('aria-pressed',day?'false':'true');
        tb.setAttribute('aria-label',day?'切换到夜晚':'切换到白天');
      });
      var st=document.getElementById('sideToggle'), sd=document.getElementById('side');
      if(st&&sd) st.addEventListener('click',function(){
        if(window.innerWidth<=760){ sd.classList.remove('closed'); sd.classList.toggle('open'); }
        else sd.classList.toggle('closed');
      });
      var sh=document.getElementById('sideHide');
      if(sh&&sd) sh.addEventListener('click',function(){ sd.classList.remove('open'); sd.classList.add('closed'); });
      var ut=document.getElementById('uiToggle');
      if(ut) ut.addEventListener('click',function(){
        var hidden=document.body.classList.toggle('ui-hidden');
        ut.textContent=hidden?'显示':'隐藏';
      });
    })();
    return false;
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.5));
  try{
    var glCtx=renderer.getContext();
    var dbgExt=glCtx.getExtension('WEBGL_debug_renderer_info');
    var rendererStr=dbgExt?String(glCtx.getParameter(dbgExt.UNMASKED_RENDERER_WEBGL)||''):'';
    isSoftwareGL=/swiftshader|llvmpipe|software rasterizer/i.test(rendererStr);
  }catch(e){ isSoftwareGL=false; }
  if(isSoftwareGL) renderer.setPixelRatio(1);
  renderer.shadowMap.enabled=true;
  renderer.shadowMap.type=THREE.PCFShadowMap;
  /* The sun and the architecture are static, so the shadow map is baked once
     (and re-baked only when the sun moves for dusk) instead of re-rendering
     500+ casters every frame — a large per-frame saving on weak GPUs. */
  renderer.shadowMap.autoUpdate=false;
  if('outputColorSpace' in renderer) renderer.outputColorSpace=THREE.SRGBColorSpace; else renderer.outputEncoding=THREE.sRGBEncoding;
  /* #4: AgX instead of ACES — ACES pushed the concrete warm and the G2 red
     sphere oversaturated; AgX keeps Ando's greys neutral and the red in
     gamut. A/B-tested against NeutralToneMapping (same cameras, same
     moments); AgX kept the sky and the steel roof closer to the reference
     photos, Neutral read slightly flat on the concrete. */
  renderer.toneMapping=THREE.AgXToneMapping;
  renderer.toneMappingExposure=1.05;
  stage.appendChild(renderer.domElement);
  controls = new OrbitControls(camera,renderer.domElement);
  controls.enableDamping=true; controls.dampingFactor=0.06;
  controls.maxPolarAngle=Math.PI*0.52; controls.minDistance=4; controls.maxDistance=260;
  controls.target.set(7,1.5,-1);
  sun.position.set(50,62,30); sun.castShadow=true;
  sun.shadow.mapSize.set(2048,2048);
  if(isSoftwareGL) sun.shadow.mapSize.set(1024,1024);
  sun.shadow.camera.left=-70; sun.shadow.camera.right=70; sun.shadow.camera.top=70; sun.shadow.camera.bottom=-70;
  sun.shadow.camera.far=220; sun.shadow.bias=-0.0004; sun.shadow.normalBias=0.03;
  scene.add(sun);
  addIntLight(31.8,-2.6,-10.2,0xfff1da,0.35,34); /* #21B Gallery 2 centre (was 0.7) */
  addIntLight(44,-2.6,-10,0xfff1da,0.3,32); /* #21B Gallery 2 east end (was 0.65) */
  addIntLight(9.5,-3.0,-6.5,0xf2f6ff,0.35,32); /* #21B Gallery 1 skylight hall (was 0.7) */
  addIntLight(6,-1.0,-4,0xfff1da,0.3,26); /* #21B lower lobby / atrium void (was 0.6) */
  addSpotLight(32,-2.6,-10, 32,-6.75,-10, 0xfff1da,66,0.88,30); /* #21B G2 spot (was 38,-1.1,-8 -> 38,-4.8,-8); #18 note: the spot must sit inside the gallery, not above the outdoor grass */
  addSpotLight(9.5,-1.0,-6.5,  9.5,-7.2,-6.5,  0xf2f6ff,120,0.5,25);  /* FIX [2]: was y=2.5, above ground OUTDOORS south of the glass — its cone painted the sharp white disc on the lawn (proven by experiment, see fix/STATUS.md). Now just above the G1 skylight panels (-1.1), below the ground slab (0.02); same target/intensity/angle, still lights the G1 floor. Same precedent as the #18 G2-spot move. */
  try{ reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)').matches; }catch(e){ reducedMotion=false; }
  loadRetryBtn.addEventListener('click',restartLoad);
  window.addEventListener('online',function(){ if(!loadDone&&loadExhausted) restartLoad(); });
  startLoad();
  return true;
}

/* Resize listener + first framing + render loop (the original script's
   final statements, in order). */
export function startLoop(){
  window.addEventListener('resize',resize); resize();
  camera.position.copy(exteriorCamPos());
  animate();
}
