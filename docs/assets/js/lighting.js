// lighting.js — the four moments of light (interface palette + scene
// light together), atmosphere tint, day/night shim.
// Split from the single inline script of docs/index.html
// (merged14: #9-#14 serial chain + round-2 review fixes).
// Behaviour unchanged: only the module boundary is new.
import * as THREE from 'three';
import { scene, renderer, sun, hemi, intLights, skyEnvTex, skyTex, buildSky, buildNightSky, nightSkyTex, hdriEnvTex } from './scene.js';
import { mode } from './camera.js';

/* exterior preset views — framed on the real two-wing model */
/* #4: the four moments of light. One switch for the whole page: the
   interface palette (body.day) and the scene's light change together.
   The baked indoor lightmap does NOT change with the moment (indoor
   light is moment-independent by design); only the outdoor sun, sky,
   fog and exposure move. Morning+noon use the paper UI, dusk+night
   the dark UI. Night is the default — the page opens on the black
   version. Switching lerps every value over 2.5 s in the render loop
   (stepMomentAnim, called from animate). */
export const MOMENTS={
  morning:{label:'清晨',sunPos:[62,26,-18],sunColor:0xffd9a8,sun:2.2,hemi:0.30,exp:1.02,fog:0xe8e2d4,env:0.55,bg:'sky',dark:false},
  noon:{label:'正午',sunPos:[50,62,30],sunColor:0xfff2dd,sun:3.0,hemi:0.35,exp:1.05,fog:0xc8d3d6,env:0.6,bg:'sky',dark:false},
  dusk:{label:'黄昏',sunPos:[-58,14,20],sunColor:0xff9a5c,sun:1.6,hemi:0.20,exp:1.0,fog:0xe8c9a8,env:0.35,bg:0x3a2f28,dark:true},
  night:{label:'夜',sunPos:[-40,30,-24],sunColor:0xbfd0e8,sun:0.55,hemi:0.14,exp:0.95,fog:0x39434e,env:0.12,bg:0x39434e,dark:true}
};
var MOMENT_ORDER=['morning','noon','dusk','night'];
export let moment = 'night';
export let isNight = true; /* derived: dusk or night — kept for isNightRef()/setMode */
var themeBtn=document.getElementById('themeToggle');
var nightViewBtn=document.querySelector('#side .views button[data-view="night"]');
var momentAnim=null;
export function currentEnvIntensity(){ return MOMENTS[moment].env; }
function applyMomentValues(m){
  var sp=m.sunPos;
  sun.position.set(sp[0],sp[1],sp[2]);
  sun.color.setHex(m.sunColor);
  sun.intensity=m.sun;
  hemi.intensity=m.hemi;
  renderer.toneMappingExposure=m.exp;
  if(m.bg==='sky'){
    buildSky();
    scene.background=skyTex||new THREE.Color(0xa9c2dc);
  }else{
    scene.background=new THREE.Color(m.bg);
  }
  if(m===MOMENTS.night){ buildNightSky(); if(nightSkyTex) scene.background=nightSkyTex; } /* #14-2: gradient night sky */
  if(mode==='exterior') scene.fog=new THREE.Fog(m.fog,120,280);
  if(hdriEnvTex) scene.environment=hdriEnvTex;
  else if(skyEnvTex) scene.environment=skyEnvTex;
  if('environmentIntensity' in scene) scene.environmentIntensity=m.env;
}
function applyMomentUI(m){
  document.body.classList.toggle('day',!m.dark);
  var mc=document.querySelector('meta[name="color-scheme"]');
  if(mc) mc.setAttribute('content',m.dark?'dark':'light');
  var next=MOMENT_ORDER[(MOMENT_ORDER.indexOf(moment)+1)%MOMENT_ORDER.length];
  themeBtn.setAttribute('aria-label','切换到'+MOMENTS[next].label);
  themeBtn.setAttribute('aria-pressed',m.dark?'true':'false');
  if(nightViewBtn) nightViewBtn.textContent=(moment==='dusk')?'回到夜晚':'黄昏灯光';
}
export function setMoment(name,instant){
  if(!MOMENTS[name]) return;
  var from=MOMENTS[moment], to=MOMENTS[name];
  var wasDark=from.dark, nowDark=to.dark;
  moment=name;
  isNight=nowDark;
  applyMomentUI(to);
  applyAtmosphereTint(name); /* #14-2: tint follows the moment */
  /* interior SpotLights are scaled only when crossing the light/dark
     boundary, so repeated moment switches never drift them apart */
  if(wasDark!==nowDark){
    var f=nowDark?1.6:1/1.6;
    intLights.forEach(function(l){ l.intensity*=f; });
  }
  if(instant){
    momentAnim=null;
    applyMomentValues(to);
  }else{
    /* leaving the painted sky for a solid-colour moment: swap the sky
       texture for its average colour first, so the 2.5 s lerp has a
       colour to start from instead of snapping at the end */
    if(to.bg!=='sky'&&scene.background&&!scene.background.isColor){
      scene.background=new THREE.Color(0xa9c2dc);
    }
    momentAnim={from:from,to:to,t0:performance.now(),d:2500,
      sunPos0:sun.position.clone(),sunCol0:sun.color.clone(),
      sun0:sun.intensity,hemi0:hemi.intensity,exp0:renderer.toneMappingExposure,
      env0:('environmentIntensity' in scene)?scene.environmentIntensity:to.env,
      fog0:(scene.fog&&mode==='exterior')?scene.fog.color.clone():new THREE.Color(to.fog),
      bg0:(scene.background&&scene.background.isColor)?scene.background.clone():new THREE.Color(to.bg)};
  }
  renderer.shadowMap.needsUpdate=true; /* sun moved — re-bake shadows */
}
/* One switch for the whole page: the interface palette (body.day)
   and the scene's light change together, so the sheet and the
   building are never in different times of day. Night is the
   default — the page opens on the black version. Interior lights
   are scaled only on an actual change, so the two entry points
   (the header's sun/moon button and the archive's dusk view) can
   never drift the intensities apart. (After the #11 rebase the
   switch is setMoment(name); fog follows MOMENTS[moment].fog.) */

/* #7: vignette + grain tint follows the light moment — the old fixed
   green-grey is gone. The table covers all four moments so #4's
   setMoment(name) can call applyAtmosphereTint(name) directly at
   rebase; main's day/night toggle calls it with 'day'/'night'.
   (Round-2 fix: this table + function must live at top level, NOT
   inside setMoment's else branch — the first setMoment call during
   load referenced it before the block executed, throwing
   "applyAtmosphereTint is not defined" and killing the page.) */
var ATMOSPHERE_TINTS={
  morning:{vig:'rgba(56,48,38,0.12)',grain:0.030},
  noon:{vig:'rgba(28,30,32,0.12)',grain:0.030},
  day:{vig:'rgba(28,30,32,0.12)',grain:0.030},
  dusk:{vig:'rgba(64,44,30,0.15)',grain:0.036},
  night:{vig:'rgba(14,18,28,0.16)',grain:0.026}
};
function applyAtmosphereTint(name){
  var t=ATMOSPHERE_TINTS[name]||ATMOSPHERE_TINTS.night;
  var v=document.getElementById('vignette'), g=document.getElementById('grain');
  if(v) v.style.background='radial-gradient(ellipse at 50% 42%,transparent 52%,'+t.vig+' 100%)';
  if(g) g.style.opacity=t.grain;
}
export function stepMomentAnim(nowMs){
  if(!momentAnim) return;
  var a=momentAnim, k=Math.min(1,(nowMs-a.t0)/a.d);
  var e=k<0.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2; /* easeInOutCubic */
  var to=a.to;
  sun.position.lerpVectors(a.sunPos0,new THREE.Vector3(to.sunPos[0],to.sunPos[1],to.sunPos[2]),e);
  sun.color.copy(a.sunCol0).lerp(new THREE.Color(to.sunColor),e);
  sun.intensity=a.sun0+(to.sun-a.sun0)*e;
  hemi.intensity=a.hemi0+(to.hemi-a.hemi0)*e;
  renderer.toneMappingExposure=a.exp0+(to.exp-a.exp0)*e;
  if('environmentIntensity' in scene) scene.environmentIntensity=a.env0+(to.env-a.env0)*e;
  if(mode==='exterior'){
    var fogCol=a.fog0.clone().lerp(new THREE.Color(to.fog),e);
    scene.fog=new THREE.Fog(fogCol.getHex(),120,280);
  }
  if(to.bg==='sky'){
    /* lerp the flat colour toward the sky's average, then swap in the
       painted texture at the end (the colour already matches, so the
       swap is not a visible snap) */
    if(scene.background&&scene.background.isColor){
      scene.background.copy(a.bg0).lerp(new THREE.Color(0xa9c2dc),e);
    }
    if(e>=1){ buildSky(); scene.background=skyTex||new THREE.Color(0xa9c2dc); }
  }else if(scene.background&&scene.background.isColor){
    scene.background.copy(a.bg0).lerp(new THREE.Color(to.bg),e);
  }
  if(k>=1){ momentAnim=null; applyMomentValues(to); renderer.shadowMap.needsUpdate=true; }
}
/* setNight kept as a thin wrapper (the archive dusk view and the theme
   button used to call it); the moment system is the real switch. */
export function setNight(n){ setMoment(n?'night':'noon'); }

export function initLighting(){
  themeBtn.addEventListener('click',function(){
    var i=MOMENT_ORDER.indexOf(moment);
    setMoment(MOMENT_ORDER[(i+1)%MOMENT_ORDER.length]);
  });
  setMoment('night',true); /* night is the default */
}
