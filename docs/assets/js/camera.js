// camera.js — current mode, preset cameras, fly-to, mode switching.
// Split from the single inline script of docs/index.html (main @62eeaac6).
// Behaviour unchanged: only the module boundary is new.
import * as THREE from 'three';
import { scene, camera, controls } from './scene.js';
import { isNight, setNight } from './lighting.js';
import { startTour, setTourFolded } from './tour.js';
import { enterWalk } from './walk.js';
import { showG3Spot, g3Spots, g3Idx, captionDismissed } from './ui.js';
import { applyLabels } from './labels.js';

export const EXT_TARGET = new THREE.Vector3(4, 1.5, -1);
export let extDefault = true;
export function exteriorCamPos(){
  if(camera.aspect>=0.85) return new THREE.Vector3(16,11,-60);
  /* Portrait: the two wings span ~85 m along x, which overflows the narrow
     horizontal FOV of a portrait screen at any fixed distance. Solve the
     camera distance from the projected corners of the buildings' bounding
     box (museum wing + cafe wing, ground slab excluded) so both wings fit
     fully in frame with margin on both sides, at any portrait aspect. */
  var dir=new THREE.Vector3(101,53.5,-141).normalize();
  var box=new THREE.Box3(new THREE.Vector3(-38,0,-10),new THREE.Vector3(47,12,10));
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
  document.querySelectorAll('#modebar button').forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.mode===next?'true':'false'); });
  badge.textContent=modeNames[next];
  var inside=(next!=='exterior');
  scene.fog=inside? null : new THREE.Fog(isNight?0x2b3442:0xd8e6f0,120,280);
  applyLabels();
  walkHud.classList.toggle('show',next==='walk');
  document.body.classList.toggle('walking',next==='walk');
  walkTip.classList.toggle('show',next==='walk');
  cross.classList.toggle('show',next==='walk');
  tourHud.classList.toggle('show',next==='tour');
  if(next==='tour') exhibitCard.classList.remove('show');
  caption.style.display=(next==='exterior'&&!captionDismissed)?'block':'none';
  controls.enabled=(next!=='walk'&&next!=='tour');
  controls.maxPolarAngle=(next==='exterior')?Math.PI*0.52:Math.PI*0.65;
  controls.maxDistance=(next==='exterior')?260:60;
  if(next==='exterior'&&!keepCam){ extDefault=true; flyTo(exteriorCamPos(),new THREE.Vector3(4,1.5,-1)); }
  /* Lobby camera stands on the solid west strip just inside the entrance
     (verified against the GLB: SM_Ground_Slab covers x -2..0.25 full depth).
     The previous viewpoint (7.6,1.9,-0.4) hovered over the atrium/stair
     opening in the slab (x 0.25..8, z -4.75..4.9), so the foreground was
     the open drop to the basement and the lobby floor read as missing.
     From the entrance the reception desk (0.5,-5.8) and the elevator door
     (-0.44,-3.6) face the camera across solid floor. */
  if(next==='lobby') flyTo(new THREE.Vector3(-1.15,1.85,1.15),new THREE.Vector3(0.9,0.6,-5.5));
  if(next==='g3'){ var gs=g3Spots[g3Idx]; flyTo(gs.cam,gs.tgt,1400); showG3Spot(g3Idx); }
  /* v16 Gallery 2: the east rectangle, x 24..52, z -15..1; camera inside the SW corner */
  if(next==='gallery') flyTo(new THREE.Vector3(27,-0.7,-14.8),new THREE.Vector3(46,-3.9,-2.5));
  if(next==='walk') enterWalk();
  if(next==='tour'){ setTourFolded(true); startTour(); }
}

export function initCamera(){
  document.querySelectorAll('#modebar button').forEach(function(b){
    b.addEventListener('click',function(){ setMode(b.dataset.mode); });
  });
  document.querySelectorAll('#side .views button').forEach(function(b){
    b.addEventListener('click',function(){
      if(mode!=='exterior') setMode('exterior',true);
      extDefault=false;
      var v=b.dataset.view;
      if(v==='front') flyTo(new THREE.Vector3(20,7,-44),new THREE.Vector3(19,2.2,-3));
      if(v==='aerial') flyTo(new THREE.Vector3(4,74,-34),new THREE.Vector3(4,0,-2));
      if(v==='court') flyTo(new THREE.Vector3(-13,3.4,-20),new THREE.Vector3(-5,1.2,1));
      if(v==='night'){
        setNight(!isNight);
        flyTo(new THREE.Vector3(28,8.5,-44),new THREE.Vector3(10,2,-2));
      }
    });
  });
  controls.addEventListener('start',function(){ if(mode==='exterior') extDefault=false; });
}
