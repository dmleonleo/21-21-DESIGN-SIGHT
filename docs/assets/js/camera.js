// camera.js — current mode, preset cameras, fly-to, mode switching,
// deep links, opening glide.
// Split from the single inline script of docs/index.html
// (merged14: #9-#14 serial chain + round-2 review fixes).
// Behaviour unchanged: only the module boundary is new.
import * as THREE from 'three';
import { scene, camera, controls, reducedMotion, modelReady } from './scene.js';
import { MOMENTS, moment, setMoment } from './lighting.js';
import { startTour, setTourFolded, tourGoTo, tourStops, tour } from './tour.js';
import { enterWalk, goNearExhibit } from './walk.js';
import { showG3Spot, g3Spots, g3Idx, captionDismissed, flashVertical, updateWalkTip, armIntro, verticalEl, currentEx, showExhibit } from './ui.js';
import { exhibits, applyLabels } from './labels.js';

export const EXT_TARGET = new THREE.Vector3(7, 1.5, -1);
export let extDefault = true;
export function exteriorCamPos(){
  /* #7: pulled back along the same sightline so both wings still fit
     at the 38° lens (distance x1.35 vs the 50° position) */
  if(camera.aspect>=0.85) return new THREE.Vector3(20,14.5,-81);
  /* Portrait: the two wings span ~85 m along x, which overflows the narrow
     horizontal FOV of a portrait screen at any fixed distance. Solve the
     camera distance from the projected corners of the buildings' bounding
     box (museum wing + cafe wing, ground slab excluded) so both wings fit
     fully in frame with margin on both sides, at any portrait aspect. */
  var dir=new THREE.Vector3(101,53.5,-141).normalize();
  var box=new THREE.Box3(new THREE.Vector3(-44,0,-21),new THREE.Vector3(49,7,9));
  var center=box.getCenter(new THREE.Vector3());
  var right=new THREE.Vector3().crossVectors(new THREE.Vector3(0,1,0),dir).normalize();
  var upv=new THREE.Vector3().crossVectors(dir,right).normalize();
  var vTan=Math.tan(camera.fov*Math.PI/360);
  var hTan=vTan*camera.aspect;
  var d=0;
  for(var xi=0;xi<2;xi++) for(var yi=0;yi<2;yi++) for(var zi=0;zi<2;zi++){
    var c=new THREE.Vector3(xi?box.max.x:box.min.x, yi?box.max.y:box.min.y, zi?box.max.z:box.min.z).sub(center);
    var z=c.dot(dir);
    d=Math.max(d, z+Math.abs(c.dot(right))/hTan, z+Math.abs(c.dot(upv))/vTan);
  }
  d*=1.1; /* side margins */
  if(scene.fog){ if(scene.fog.near<140) scene.fog.near=140; if(scene.fog.far<430) scene.fog.far=430; }
  return EXT_TARGET.clone().add(dir.multiplyScalar(d));
}
export let mode = 'exterior';
const badge = document.getElementById('modeBadge');
const modeNames={exterior:'外观 · 环视',lobby:'入口大堂',g3:'Gallery 3 · 西翼',gallery:'展厅 · 全景',walk:'展厅 · 步行中',tour:'自动游览 · 进行中'};
export const camAnimBox = { current: null };
const exhibitCard = document.getElementById('exhibitCard');
const caption = document.getElementById('caption');
const walkHud = document.getElementById('walkHud');
const walkTip = document.getElementById('walkTip');
const cross = document.getElementById('cross');
const tourHud = document.getElementById('tourHud');
export function flyTo(pos,tgt,dur){
  camAnimBox.current={p0:camera.position.clone(),p1:pos.clone(),t0:controls.target.clone(),t1:tgt.clone(),s:performance.now(),d:(dur||1100)};
}
export function setMode(next,keepCam){
  mode=next;
  document.body.dataset.mode=next;
  flashVertical();
  var activeBtn=document.querySelector('#modebar button[data-mode="'+next+'"]');
  if(activeBtn&&window.innerWidth<=760){ try{ activeBtn.scrollIntoView({inline:'center',block:'nearest'}); }catch(e){} }
  /* item 5: a fresh mode entry drops any preset view; the hash
     follows the new state (a view button sets currentView after). */
  currentView=null;
  document.querySelectorAll('#modebar button').forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.mode===next?'true':'false'); });
  badge.textContent=modeNames[next];
  var inside=(next!=='exterior');
  scene.fog=inside? null : new THREE.Fog(MOMENTS[moment].fog,120,280); /* #4: fog follows the current light moment */
  applyLabels();
  walkHud.classList.toggle('show',next==='walk');
  document.body.classList.toggle('walking',next==='walk');
  walkTip.classList.toggle('show',next==='walk');
  cross.classList.toggle('show',next==='walk');
  tourHud.classList.toggle('show',next==='tour');
  if(next!=='g3'&&next!=='walk') exhibitCard.classList.remove('show'); /* #6.1: the exhibit/spot card belongs to one mode only — a G3 spot must not linger into the gallery panorama (and vice versa); g3 re-shows it via showG3Spot(), walk via showExhibit()/proximity */
  caption.style.display=(next==='exterior'&&!captionDismissed)?'block':'none';
  controls.enabled=(next!=='walk'&&next!=='tour');
  controls.maxPolarAngle=(next==='exterior')?Math.PI*0.52:Math.PI*0.65;
  controls.maxDistance=(next==='exterior')?260:60;
  if(next==='exterior'&&!keepCam){ extDefault=true; flyTo(exteriorCamPos(),EXT_TARGET.clone()); }
  /* FIX [1] lobby camera: the #21B position (-6,1.9,2) sat INSIDE the
     slanted entrance wall (1.2 m thick; camera 0.20 m from its centreline
     — GLB raycast, see fix/STATUS.md), which is why Hark's lobby.png was
     all grey wall. New: stands on the open ground just inside the
     entrance, looking east-southeast along the south glass toward the
     court mullions and the stair; shop counter in the foreground, hall
     columns and sloped soffit in frame. Three candidates screenshotted;
     this one (E2) reads cleanly in SwiftShader. */
  if(next==='lobby') flyTo(new THREE.Vector3(-3.5,1.9,0.0),new THREE.Vector3(14,0.4,-1.0));
  if(next==='g3'){ var gs=g3Spots[g3Idx]; flyTo(gs.cam,gs.tgt,1400); showG3Spot(g3Idx); }
  /* #21B Gallery 2: x 15.08..48.56, z -17.24..-3.25, ceiling -1.95; camera inside the SW corner */
  if(next==='gallery') flyTo(new THREE.Vector3(18,-1.2,-15),new THREE.Vector3(45,-4.5,-6)); /* #21B: same reframe as tour stop 6 */
  if(next==='walk'){ updateWalkTip(); enterWalk(); }
  if(next==='tour'){ setTourFolded(true); startTour(); }
  syncHash();
}
/* ================= Deep links (item 5) =================
   The URL hash carries the visit state so a shared link (or a
   refresh) lands back in the same place: #exhibit-07, #tour-5,
   #g3-2, #view-aerial, or a plain mode (#lobby, #gallery, #walk,
   #exterior). The hash is written with replaceState — no history
   spam as the tour advances — and read once the model is on screen
   (see the applyDeepLink() call at the end of onModelLoaded). */
let currentView = null;
export function syncHash(){
  var h='';
  if(mode==='tour') h='#tour-'+(tour.idx+1);
  else if(mode==='g3') h='#g3-'+(g3Idx+1);
  else if(mode==='walk'&&currentEx) h='#exhibit-'+currentEx.key;
  else if(mode==='walk') h='#walk';
  else if(mode==='lobby') h='#lobby';
  else if(mode==='gallery') h='#gallery';
  else if(mode==='exterior'&&currentView) h='#view-'+currentView;
  else h='#exterior';
  try{ history.replaceState(null,'',h); }catch(e){}
}
export function applyDeepLink(){
  var h=(location.hash||'').replace(/^#/,'');
  if(!h||!modelReady) return;
  var m;
  if((m=h.match(/^exhibit-(\d{2})$/))){
    var ex=null;
    exhibits.forEach(function(e){ if(e.key===m[1]) ex=e; });
    if(ex){ showExhibit(ex); goNearExhibit(ex); }
    return;
  }
  if((m=h.match(/^tour-(\d+)$/))){
    var ti=Math.max(0,Math.min(tourStops.length-1,parseInt(m[1],10)-1));
    setMode('tour'); tourGoTo(ti,performance.now());
    return;
  }
  if((m=h.match(/^g3-(\d+)$/))){
    var gi=Math.max(0,Math.min(g3Spots.length-1,parseInt(m[1],10)-1));
    setMode('g3'); showG3Spot(gi); var gs=g3Spots[gi]; flyTo(gs.cam,gs.tgt,1200);
    return;
  }
  if((m=h.match(/^view-(aerial|front|court|night)$/))){
    setMode('exterior',true); extDefault=false; currentView=m[1];
    var v=m[1];
    if(v==='front') flyTo(new THREE.Vector3(20,7,-44),new THREE.Vector3(19,2.2,-3));
    if(v==='aerial') flyTo(new THREE.Vector3(7,74,-34),new THREE.Vector3(7,0,-4));
    if(v==='court') flyTo(new THREE.Vector3(-13,3.4,-20),new THREE.Vector3(-5,1.2,1));
    if(v==='night'){ setMoment('night'); flyTo(new THREE.Vector3(28,8.5,-44),new THREE.Vector3(10,2,-2)); } /* #12 review: a deep link must land on night, not toggle it */
    syncHash();
    return;
  }
  if(h==='lobby'||h==='gallery'||h==='walk'||h==='exterior'){ setMode(h); return; }
}
/* ================= Opening (#6.2) =================
   After the model is on screen: the Sugimoto blur sharpens as the
   deferred sky / IBL work finishes, then a 7 s glide runs along the
   54 m folded roof's south edge, west to east, settling on the
   standard exterior framing. Only the title + the vertical text are
   on screen during the glide; the full interface appears when it
   ends. Any input skips it. First visit only (localStorage), and
   never under reduced motion — returning visitors go straight to
   the exterior view. */
export let opening = null;
let openingDone = false;
export function beginOpening(){
  document.body.classList.remove('scene-blur');
  var seen=false;
  try{ seen=window.localStorage&&localStorage.getItem('2121-opening-seen')==='1'; }catch(e){}
  if(seen||reducedMotion){ endOpening(true); return; }
  opening={s:performance.now(),d:7000,
    p0:new THREE.Vector3(-14,8.5,-34), p1:exteriorCamPos(),
    t0:new THREE.Vector3(10,5,-2), t1:new THREE.Vector3(7,1.5,-1)};
  camera.position.copy(opening.p0); controls.target.copy(opening.t0);
  controls.enabled=false;
  document.body.classList.add('opening');
  if(verticalEl) verticalEl.classList.add('on');
  var skip=function(){ if(opening) endOpening(false); };
  window.addEventListener('pointerdown',skip,{once:true});
  window.addEventListener('keydown',skip,{once:true});
}
export function endOpening(instant){
  if(openingDone&&!opening) return;
  opening=null; openingDone=true;
  document.body.classList.remove('opening');
  if(verticalEl) verticalEl.classList.remove('on');
  controls.enabled=(mode!=='walk'&&mode!=='tour');
  camera.position.copy(exteriorCamPos()); controls.target.copy(EXT_TARGET);
  try{ if(window.localStorage) localStorage.setItem('2121-opening-seen','1'); }catch(e){}
  armIntro();
}

export function initCamera(){
  controls.addEventListener('start',function(){
    if(mode==='exterior'){ extDefault=false; if(currentView){ currentView=null; syncHash(); } }
  });
  document.querySelectorAll('#modebar button').forEach(function(b){
    b.addEventListener('click',function(){ setMode(b.dataset.mode); });
  });
  window.addEventListener('hashchange',function(){ applyDeepLink(); });
  document.querySelectorAll('#side .views button').forEach(function(b){
    b.addEventListener('click',function(){
      if(mode!=='exterior') setMode('exterior',true);
      extDefault=false;
      var v=b.dataset.view;
      currentView=v;
      if(v==='front') flyTo(new THREE.Vector3(20,7,-44),new THREE.Vector3(19,2.2,-3));
      if(v==='aerial') flyTo(new THREE.Vector3(7,74,-34),new THREE.Vector3(7,0,-4));
      if(v==='court') flyTo(new THREE.Vector3(-13,3.4,-20),new THREE.Vector3(-5,1.2,1));
      if(v==='night'){
        setMoment(moment==='dusk'?'night':'dusk'); /* archive dusk view: goes straight to dusk, not a toggle */
        flyTo(new THREE.Vector3(28,8.5,-44),new THREE.Vector3(10,2,-2));
      }
      syncHash();
    });
  });
}
