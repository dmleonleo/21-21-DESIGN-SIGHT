// lighting.js — day/night switch (interface palette + scene light together).
// Split from the single inline script of docs/index.html (main @62eeaac6).
// Behaviour unchanged: only the module boundary is new.
import * as THREE from 'three';
import { scene, renderer, sun, hemi, intLights, skyEnvTex, skyTex, buildSky } from './scene.js';
import { mode } from './camera.js';

/* exterior preset views — framed on the real two-wing model */
var sunDay={pos:new THREE.Vector3(50,62,30),exp:1.05,sun:3.0,hemi:0.35};
export let isNight = false;
var themeBtn=document.getElementById('themeToggle');
var nightViewBtn=document.querySelector('#side .views button[data-view="night"]');
/* One switch for the whole page: the interface palette (body.day)
   and the scene's light change together, so the sheet and the
   building are never in different times of day. Night is the
   default — the page opens on the black version. Interior lights
   are scaled only on an actual change, so the two entry points
   (the header's sun/moon button and the archive's dusk view) can
   never drift the intensities apart. Fog follows the mode: there
   is none indoors, and setMode re-derives it from isNight when
   the visitor steps back outside. */
export function setNight(n){
  n=!!n;
  var changed=(n!==isNight);
  isNight=n;
  document.body.classList.toggle('day',!n);
  themeBtn.setAttribute('aria-pressed',n?'true':'false');
  themeBtn.setAttribute('aria-label',n?'切换到白天':'切换到夜晚');
  if(nightViewBtn) nightViewBtn.textContent=n?'回到白天':'黄昏灯光';
  var mc=document.querySelector('meta[name="color-scheme"]');
  if(mc) mc.setAttribute('content',n?'dark':'light');
  if(n){
    scene.background=new THREE.Color(0x2b3442);
    if(mode==='exterior') scene.fog=new THREE.Fog(0x2b3442,120,280);
    sun.intensity=0.55; sun.position.set(-40,30,-24); hemi.intensity=0.14;
    renderer.toneMappingExposure=0.95;
    if(skyEnvTex) scene.environment=skyEnvTex;
    if('environmentIntensity' in scene) scene.environmentIntensity=0.1;
    if(changed) intLights.forEach(function(l){ l.intensity*=1.6; });
  }else{
    buildSky(); /* the day background is restored from the sky texture */
    scene.background=skyTex||new THREE.Color(0xa9c2dc);
    if(mode==='exterior') scene.fog=new THREE.Fog(0xd8e6f0,120,280);
    sun.intensity=sunDay.sun; sun.position.copy(sunDay.pos); hemi.intensity=sunDay.hemi;
    renderer.toneMappingExposure=sunDay.exp;
    if(skyEnvTex) scene.environment=skyEnvTex;
    if('environmentIntensity' in scene) scene.environmentIntensity=0.5;
    if(changed) intLights.forEach(function(l){ l.intensity/=1.6; });
  }
  renderer.shadowMap.needsUpdate=true; /* sun moved — re-bake shadows */
}

export function initLighting(){
  themeBtn.addEventListener('click',function(){ setNight(!isNight); });
  setNight(true); /* night is the default */
}
