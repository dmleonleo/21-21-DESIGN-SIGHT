// scene.js — renderer, sky, model loading, model fixes, render loop.
// Split from the single inline script of docs/index.html (main @62eeaac6).
// Behaviour unchanged: only the module boundary is new.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { isNight } from './lighting.js';
import { labelSprite, exhibits } from './labels.js';
import { mode, exteriorCamPos, EXT_TARGET, extDefault, camAnimBox } from './camera.js';
import { updateWalk } from './walk.js';
import { updateTour } from './tour.js';

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
  g.addColorStop(0.00,'#3565a6');
  g.addColorStop(0.30,'#6f9fd2');
  g.addColorStop(0.46,'#bcd6ee');
  g.addColorStop(0.52,'#e2ecf4');
  g.addColorStop(0.58,'#ccd6da');
  g.addColorStop(1.00,'#aeb9bc');
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
/* The sky is NOT painted during startup: painting hundreds of gradient
   blobs on the main thread before the model fetch even began was enough
   to stall first paint / DOMContentLoaded on slow CPUs and made the page
   look stuck on the loading screen. Start from a flat sky colour, build
   the real sky a moment later (see the deferred call below). */
export let skyTex = null;
scene.background=new THREE.Color(0xa9c2dc);
export function buildSky(){
  if(skyTex) return;
  try{ skyTex=makeSkyTexture(); }catch(e){ return; }
  if(!isNightRef()) scene.background=skyTex;
}
scene.fog=new THREE.Fog(0xd8e6f0,120,280);
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
function isNightRef(){ return typeof isNight!=='undefined'&&isNight; }
/* Sky painting + PMREM are deferred until AFTER the model has loaded
   (onModelLoaded calls them): they compete for the same main thread as
   the GLB parse, and the opaque loading overlay covers the screen until
   then, so building them earlier only delayed the model itself. */

export const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 500);
camera.position.set(16,11,-60);



/* lights — strong directional sun with sharp shadows, sky IBL (scene.environment)
   for ambient/reflections; low fills so the contrast stays photographic */
export const hemi = new THREE.HemisphereLight(0xdfeaf5, 0x8a9077, 0.35);
export const sun = new THREE.DirectionalLight(0xfff2dd, 3.0);
const fill = new THREE.DirectionalLight(0xbfd4e6, 0.3);
/* interior lights for the basement galleries (the model is enclosed) */
export const intLights = [];
function addIntLight(x,y,z,color,intensity,dist){
  var pl=new THREE.PointLight(color,intensity,dist); pl.position.set(x,y,z); scene.add(pl); intLights.push(pl); return pl;
}
/* ================= Drifting sakura petals (exterior only) =================
   After Sakura River Valley: the scene should feel alive and seasonal.
   ~130 soft petals drift over the Midtown lawn, swaying as they fall.
   They fade in only in exterior mode and vanish indoors; skipped for
   software rasterizers and for visitors who prefer reduced motion. */
let petals = null, petalData = null;
let reducedMotion = false;
/* ================= Blender model (GLB) =================
   design2121.glb — flat hierarchy under WEB_ROOT, objects named SM_*.
   glTF space: x east, y up, z south-ish; ground y=0, basement floor y=-4.8. */
export let model = null;
let modelReady = false;
export const pickMeshes = [];
const exhibitMeshes = {};   /* '01'..'12' -> [meshes] (all twelve are real objects in the v16 GLB) */
let spinnerPivot = null;
const lampMeshes = [];

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
   7.55 MB GLB ships as its own file, assets/design2121.glb, and is
   fetched by the relative path in fetchModel() below; three.module.min.js
   is likewise an external file. This HTML therefore stays ~117 KB —
   no base64 model blob, no data-URI geometry. (The single-file
   11 MB HTML that the platform's export produces inlines these
   assets at export time; that is an export packaging choice, not
   how this page is written or served.)

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
/* ================= G3 ceiling / cafe-roof clip fix =================
   In the v16 GLB the west wing's sloped white ceiling (SM_G3_Ceiling)
   rises through the folded cafe roof along its north band (measured
   against the roof surface: up to 0.46 m proud, x −24…−15.5, z 2.4…5.0),
   and its two downlights (SM_G3_Downlight_1/2) poke through with it —
   from outside they read as a big white wedge and two white shards
   lying on the roof. The GLB is a baked asset, so the correction is
   applied here at load: build a height field of SM_Cafe_Roof, pull
   every ceiling vertex that crosses it to just under the roof surface
   (the ceiling then hugs the roof underside, as built ceilings do),
   and drop each rigid downlight by its own worst penetration. Only
   vertices above the roof move; the interior — including the low
   ceiling edge at the south glass — is untouched. */
function fixG3RoofClip(){
  var roof=model.getObjectByName('SM_Cafe_Roof');
  var ceil=model.getObjectByName('SM_G3_Ceiling');
  if(!roof||!ceil||!roof.geometry||!ceil.geometry) return;
  model.updateWorldMatrix(true,true);
  /* height field of the cafe roof: topmost roof Y per 0.2 m XZ cell */
  var CELL=0.2, GX0=-34.6, GZ0=-6.6, GNX=128, GNZ=66;
  var grid=new Float32Array(GNX*GNZ); for(var gi=0;gi<grid.length;gi++) grid[gi]=-1e9;
  (function(){
    var pos=roof.geometry.attributes.position, idx=roof.geometry.index;
    var m=roof.matrixWorld, v=[new THREE.Vector3(),new THREE.Vector3(),new THREE.Vector3()];
    var nTri=idx?idx.count/3:pos.count/3;
    for(var t=0;t<nTri;t++){
      for(var k=0;k<3;k++){
        var vi=idx?idx.getX(t*3+k):t*3+k;
        v[k].fromBufferAttribute(pos,vi).applyMatrix4(m);
      }
      var mnx=Math.min(v[0].x,v[1].x,v[2].x), mxx=Math.max(v[0].x,v[1].x,v[2].x);
      var mnz=Math.min(v[0].z,v[1].z,v[2].z), mxz=Math.max(v[0].z,v[1].z,v[2].z);
      var ix0=Math.max(0,Math.floor((mnx-GX0)/CELL)), ix1=Math.min(GNX-1,Math.floor((mxx-GX0)/CELL));
      var iz0=Math.max(0,Math.floor((mnz-GZ0)/CELL)), iz1=Math.min(GNZ-1,Math.floor((mxz-GZ0)/CELL));
      var d=v[1].clone().sub(v[0]), e=v[2].clone().sub(v[0]);
      var den=d.x*e.z-e.x*d.z; if(Math.abs(den)<1e-12) continue;
      for(var ix=ix0;ix<=ix1;ix++) for(var iz=iz0;iz<=iz1;iz++){
        var px=GX0+(ix+0.5)*CELL, pz=GZ0+(iz+0.5)*CELL;
        var rx=px-v[0].x, rz=pz-v[0].z;
        var bu=(rx*e.z-rz*e.x)/den, bv=(d.x*rz-d.z*rx)/den, bw=1-bu-bv;
        if(bu<-0.02||bv<-0.02||bw<-0.02) continue;
        var y=bw*v[0].y+bu*v[1].y+bv*v[2].y, cell=iz*GNX+ix;
        if(y>grid[cell]) grid[cell]=y;
      }
    }
  })();
  function roofY(x,z){
    var ix=Math.floor((x-GX0)/CELL), iz=Math.floor((z-GZ0)/CELL), best=null;
    for(var r=0;r<=2;r++){
      for(var dx=-r;dx<=r;dx++) for(var dz=-r;dz<=r;dz++){
        if(r>0&&Math.max(Math.abs(dx),Math.abs(dz))!==r) continue;
        var cx=ix+dx, cz=iz+dz;
        if(cx<0||cz<0||cx>=GNX||cz>=GNZ) continue;
        var val=grid[cz*GNX+cx];
        if(val>-1e8&&(best===null||val<best)) best=val;
      }
      if(best!==null) return best;
    }
    return null;
  }
  var MARGIN=0.05, tmp=new THREE.Vector3();
  function clampMesh(mesh){
    if(!mesh||!mesh.geometry) return;
    mesh.updateWorldMatrix(true,false);
    var pos=mesh.geometry.attributes.position;
    var inv=new THREE.Matrix4().copy(mesh.matrixWorld).invert(), hit=false;
    for(var i=0;i<pos.count;i++){
      tmp.fromBufferAttribute(pos,i).applyMatrix4(mesh.matrixWorld);
      var rh=roofY(tmp.x,tmp.z);
      if(rh!==null&&tmp.y>rh-MARGIN){
        tmp.y=rh-MARGIN; tmp.applyMatrix4(inv); pos.setXYZ(i,tmp.x,tmp.y,tmp.z); hit=true;
      }
    }
    if(hit){ pos.needsUpdate=true; mesh.geometry.computeBoundingSphere(); }
  }
  function lowerFixture(obj){
    if(!obj||!obj.geometry) return;
    obj.updateWorldMatrix(true,false);
    var pos=obj.geometry.attributes.position, worst=0;
    for(var i=0;i<pos.count;i++){
      tmp.fromBufferAttribute(pos,i).applyMatrix4(obj.matrixWorld);
      var rh=roofY(tmp.x,tmp.z);
      if(rh!==null) worst=Math.max(worst,tmp.y-(rh-MARGIN));
    }
    if(worst>0){
      obj.getWorldPosition(tmp); tmp.y-=worst;
      if(obj.parent){ obj.parent.updateWorldMatrix(true,false); obj.parent.worldToLocal(tmp); }
      obj.position.copy(tmp); obj.updateWorldMatrix(true,false);
    }
  }
  clampMesh(ceil);
  ['SM_G3_CoveStrip','SM_G3_PR_Ceiling','SM_G3_Kit_WallS'].forEach(function(nm){
    clampMesh(model.getObjectByName(nm));
  });
  lowerFixture(model.getObjectByName('SM_G3_Downlight_1'));
  lowerFixture(model.getObjectByName('SM_G3_Downlight_2'));
}
/* ================= Stair-foot wall fix =================
   In the v16 GLB the x=8 atrium wall line runs straight across the
   foot of the 30-step stair: SM_Atrium_Wall_East_A (x 7.85-8.15,
   z 3.4-5.0, full height y -4.8..0, its eight form-tie discs
   SM_Atrium_TieHole_00..07 on its west face) stands across most of
   the stair's width (z 3-5) exactly where the flight lands — the
   tour's stair stop looks straight into it, the walk-mode stair
   ride and the enter-walk descent fly through it, and on foot the
   only way past was a 0.4 m sliver at z 3.0-3.4 between the wall's
   north edge and the balustrade. The segment belongs one bay
   further north, continuing the Gallery 1 west wall
   (SM_G1_Wall_West_North, x 7.9-8.1, z 5-7, same concrete, same
   height). The GLB is a baked asset, so at load the segment and
   its tie discs are shifted +1.6 m in z: it then spans z 5.0-6.6,
   merged into the G1 wall run, and the stair foot (z 3.4-5.0)
   opens onto the landing. BASE_BLOCKERS below matches the shift. */
function fixStairFootWall(){
  var wall=model.getObjectByName('SM_Atrium_Wall_East_A');
  if(wall) wall.position.z+=1.6;
  for(var i=0;i<8;i++){
    var th=model.getObjectByName('SM_Atrium_TieHole_0'+i);
    if(th) th.position.z+=1.6;
  }
}
/* ================= Exterior trees: keep only three =================
   The v16 GLB plants 18 trees on the grounds (each one a trunk plus
   four side cards and two top cards, named SM_Tree_Trunk_<key>,
   SM_Tree_Card_<key>_<n>, SM_Tree_TopCard_<key>_<n>). At Leon's
   request only three stay — a single calm, evenly spaced row along
   the south lawn, west / centre / east, so the folded roofs read
   against open grass instead of a thicket of leaf cards:
     west   x -20.5, z 13.9
     centre x  11.6, z 13.1
     east   x  34.6, z 15.8
   The other fifteen grounds trees are hidden (visible=false, so
   they neither render nor cast shadows). The one tree inside the
   sunken courtyard planter (key 15_1.5, trunk base at basement
   level) is not a grounds tree and is left untouched. */
var KEEP_TREE_KEYS={
  '-20.506536543695546_-13.861288898608986':true,
  '11.640643481283298_-13.104740129882714':true,
  '34.563058939808485_-15.770751238658896':true,
  '15_1.5':true /* sunken-courtyard planter tree — not a grounds tree */
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
function onModelLoaded(gltf){
  if(loadDone) return;
  loadDone=true;
  restoreCreateImageBitmap(); /* parse finished — the texture decoder choice is locked in */
  clearTimeout(loadSlowTimer);
  model=gltf.scene; scene.add(model);
  model.traverse(function(o){
    if(o.isMesh){
      o.castShadow=true; o.receiveShadow=true;
      if(o.material&&!Array.isArray(o.material)&&'transmission' in o.material&&o.material.transmission>0){
        /* KHR transmission forces a second full-scene render every frame —
           measured here as the main thread blocking for ~70 s after the
           download hit 100% under software GL, and a heavy per-frame cost
           on phones. Replace it with plain transparent glass that still
           picks up the sky environment reflection. */
        o.material=o.material.clone();
        o.material.transmission=0;
        o.material.transparent=true;
        o.material.opacity=0.38;
        o.material.depthWrite=false;
      }
      var mn=o.material&&o.material.name;
      if(mn==='MAT_Pendant_Light'&&o.material.emissive){ o.material=o.material.clone(); o.material.emissive=new THREE.Color(0xffc98a); o.material.emissiveIntensity=0.9; lampMeshes.push(o); }
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
  try{ fixG3RoofClip(); }catch(e){ /* roof correction is an enhancement */ }
  try{ fixStairFootWall(); }catch(e){ /* stair correction is an enhancement */ }
  try{ pruneExteriorTrees(); }catch(e){ /* tree pruning is an enhancement */ }
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
    labelSprite('G3 · Gallery 3（西翼）',-23,2.4,1.6);
  }catch(e){ /* labels are an enhancement */ }
  /* register exhibits for picking */
  exhibits.forEach(function(ex){
    (exhibitMeshes[ex.key]||[]).forEach(function(mesh){
      mesh.userData.exhibit=ex; pickMeshes.push(mesh);
    });
  });
  /* now that the model is on screen, build the cloudy sky + IBL */
  setTimeout(function(){ buildSky(); setupEnvironment(); },60);
}
/* ================= Resize & loop ================= */
function resize(){
  var w=stage.clientWidth||window.innerWidth, h=stage.clientHeight||window.innerHeight;
  renderer.setSize(w,h); camera.aspect=w/h;
  camera.fov=camera.aspect<0.85?70:50; /* wider FOV in portrait so the two wings can fit */
  camera.updateProjectionMatrix();
  /* keep the default exterior framing fitted when the viewport changes
     (rotation, webview resize) — unless the user has orbited or picked a
     preset view, in which case their framing is left alone */
  if(mode==='exterior'&&extDefault&&!camAnimBox.current){ camera.position.copy(exteriorCamPos()); controls.target.copy(EXT_TARGET); }
}

var lastNow=performance.now(), elapsed=0;
function animate(){
  requestAnimationFrame(animate);
  try{
    var nowMs=performance.now();
    var dt=Math.min((nowMs-lastNow)/1000,0.05); lastNow=nowMs; elapsed+=dt;
    var t=elapsed;
    var ca = camAnimBox.current;
    if(ca&&mode!=='walk'&&mode!=='tour'){
      var k=Math.min(1,(performance.now()-ca.s)/ca.d);
      var e=1-Math.pow(1-k,3);
      camera.position.lerpVectors(ca.p0,ca.p1,e);
      controls.target.lerpVectors(ca.t0,ca.t1,e);
      if(k>=1) camAnimBox.current=null;
    }
    if(mode==='walk') updateWalk(dt,nowMs);
    else if(mode==='tour'){ updateTour(nowMs); camera.lookAt(controls.target); }
    else controls.update();
    if(spinnerPivot) spinnerPivot.rotation.y=t*0.45;
    if(petals){
      var pTarget=(mode==='exterior')?0.75:0;
      petals.material.opacity+=(pTarget-petals.material.opacity)*Math.min(1,dt*2);
      petals.visible=petals.material.opacity>0.02;
      if(petals.visible){
        var pArr=petals.geometry.attributes.position.array;
        for(var qi=0;qi<petalData.length;qi++){
          var pd=petalData[qi];
          pd.y-=pd.sp*dt;
          pd.x+=Math.sin(t*pd.sw+pd.ph)*dt*0.55;
          pd.z+=Math.cos(t*pd.sw*0.8+pd.ph)*dt*0.3;
          if(pd.y<0.15){ pd.y=12+Math.random()*3; pd.x=-48+Math.random()*105; pd.z=-26+Math.random()*42; }
          pArr[qi*3]=pd.x; pArr[qi*3+1]=pd.y; pArr[qi*3+2]=pd.z;
        }
        petals.geometry.attributes.position.needsUpdate=true;
      }
    }
    lampMeshes.forEach(function(o,i){ var s=1+Math.sin(t*2+i)*0.08; o.scale.set(s,s,s); });
    renderer.render(scene,camera);
  }catch(err){
    showErr('渲染出错：'+err.message);
  }
}

/* Runs the page's original top-level statements, in their original order:
   error handlers -> renderer -> controls -> lights -> petals -> loader.
   Returns false only when WebGL is unavailable (the original script
   returned early in that case, before any listener was attached); the
   entry script then skips the remaining inits, exactly as before. */
export function initScene(){
  window.onerror=function(m,s,l){ showErr('页面出错：'+m+'（行 '+l+'）'); return false; };
  window.addEventListener('unhandledrejection',function(e){ showErr('页面出错：'+(e.reason&&e.reason.message||e.reason)); });
  try{
    renderer = new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
  }catch(e){
    /* No WebGL (old webview, GPU blocklist, software fallback removed):
       say so on the loading screen instead of spinning on it forever. */
    document.getElementById('loadMsg').textContent='无法启动 3D：此浏览器或设备未提供 WebGL。请换用最新版 Safari / Chrome 打开本页。';
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
  renderer.toneMapping=THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure=1.05;
  stage.appendChild(renderer.domElement);
  controls = new OrbitControls(camera,renderer.domElement);
  controls.enableDamping=true; controls.dampingFactor=0.06;
  controls.maxPolarAngle=Math.PI*0.52; controls.minDistance=4; controls.maxDistance=260;
  controls.target.set(4,1.5,-1);
  scene.add(hemi);
  fill.position.set(-40,24,-36); scene.add(fill);
  sun.position.set(50,62,30); sun.castShadow=true;
  sun.shadow.mapSize.set(2048,2048);
  if(isSoftwareGL) sun.shadow.mapSize.set(1024,1024);
  sun.shadow.camera.left=-70; sun.shadow.camera.right=70; sun.shadow.camera.top=70; sun.shadow.camera.bottom=-70;
  sun.shadow.camera.far=220; sun.shadow.bias=-0.0004; sun.shadow.normalBias=0.03;
  scene.add(sun);
  scene.add(new THREE.AmbientLight(0xffffff,0.06));
  addIntLight(24,-1.1,-5.5,0xfff1da,0.85,36);   /* Gallery 2 west (v16: hall is the east rectangle) */
  addIntLight(38,-1.1,-7.5,0xfff1da,0.7,34);     /* Gallery 2 centre */
  addIntLight(47,-1.1,-9.5,0xfff1da,0.65,32);    /* Gallery 2 east end, to x=52 */
  addIntLight(38,-1.1,-13.5,0xfff1da,0.6,30);    /* Gallery 2 south band (04 panel wall) */
  addIntLight(28,-1.1,4.0,0xf2f6ff,0.7,32);     /* Gallery 1 skylight hall */
  addIntLight(15,-0.8,-2.0,0xffe9bb,0.65,24);   /* sunken courtyard (open pit, floor -4.8) */
  addIntLight(4,-0.4,1.5,0xfff1da,0.6,26);      /* atrium void (open -4.8 to +6.24) */
  addIntLight(2,2.4,-4.2,0xfff4e0,0.55,24);     /* entrance lobby: reception / elevator */
  addIntLight(-23,2.4,1.2,0xfff4e0,0.6,28);     /* Gallery 3 — west (cafe) wing */
  try{ reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)').matches; }catch(e){ reducedMotion=false; }
  if(!reducedMotion&&!isSoftwareGL){
    var pCount=130;
    var pGeo=new THREE.BufferGeometry();
    var pPos=new Float32Array(pCount*3); petalData=[];
    for(var pi=0;pi<pCount;pi++){
      var px=-48+Math.random()*105, py=0.4+Math.random()*13, pz=-26+Math.random()*42;
      pPos[pi*3]=px; pPos[pi*3+1]=py; pPos[pi*3+2]=pz;
      petalData.push({x:px,y:py,z:pz,ph:Math.random()*6.283,sp:0.22+Math.random()*0.45,sw:0.4+Math.random()*0.8});
    }
    pGeo.setAttribute('position',new THREE.BufferAttribute(pPos,3));
    var pTex=canvasTexture(64,64,function(ctx){
      ctx.translate(32,32); ctx.rotate(0.6);
      var grd=ctx.createRadialGradient(0,0,2,0,0,20);
      grd.addColorStop(0,'rgba(250,231,237,0.95)');
      grd.addColorStop(0.7,'rgba(244,199,212,0.7)');
      grd.addColorStop(1,'rgba(244,199,212,0)');
      ctx.fillStyle=grd;
      ctx.beginPath(); ctx.ellipse(0,0,17,10,0,0,6.2832); ctx.fill();
    });
    petals=new THREE.Points(pGeo,new THREE.PointsMaterial({size:0.85,map:pTex,transparent:true,opacity:0,depthWrite:false,sizeAttenuation:true}));
    petals.frustumCulled=false; petals.visible=false;
    scene.add(petals);
  }
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
