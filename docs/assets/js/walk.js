// walk.js — walk mode: zones, collision, stair, picking, exhibit approach.
// Split from the single inline script of docs/index.html
// (merged14: #9-#14 serial chain + round-2 review fixes).
// Behaviour unchanged: only the module boundary is new.
import * as THREE from 'three';
import { camera, renderer, controls, scene, pickMeshes, colliderMeshes, modelReady } from './scene.js';
import { mode, setMode, camAnimBox, flyTo } from './camera.js';
import { showExhibit, currentEx, setExFolded } from './ui.js';
import { exhibits, EYE_Y } from './labels.js';

const exhibitCard = document.getElementById('exhibitCard');
export function goNearExhibit(ex){
  if(mode!=='walk'){ setMode('walk'); }
  /* a teleport cancels any in-progress tap-to-move, or the stale
     target drags the visitor away from the stand on arrival */
  walk.clickTarget=null; walk.clickBlocked=0; walk.focusEx=null; hideMoveRing();
  /* a teleport also ends any previous focus session: without this, a
     same-document hash navigation (e.g. a shared #exhibit-01 link
     opened while focused on 07) leaves focusState pointing at the
     old exhibit while the card shows the new one. */
  focusState=null;
  walk.intro=null;
  walk.level='base';
  walk.inStair=false; /* teleported to a stand point, outside the stair rects */
  walk.pos.copy(ex.stand);
  /* Hold this exhibit while the visitor stands at its stand point: the
     proximity auto-show in updateWalk otherwise immediately switches the
     card back to whichever exhibit's focus happens to be nearest (e.g.
     at 02's stand, 01's focus is closer), trapping 「下一件」 in a loop
     between two exhibits and making later exhibits unreachable. */
  walk.holdEx=ex;
  var dir=ex.focus.clone().sub(ex.stand);
  walk.yaw=Math.atan2(-dir.x,-dir.z);
  walk.pitch=-0.05;
}
/* picking + tap-to-move + exhibit focus (items 1, 2, 3) */
export const ray = new THREE.Raycaster(), ptr = new THREE.Vector2();
var downAt = null;
var pointerLocked=false;
export let focusState = null; /* the view before an exhibit focus, for Esc / empty-click exit */
var moveRing=null;
function initMoveRing(){
  moveRing=new THREE.Group();
  var ring=new THREE.Mesh(new THREE.RingGeometry(0.3,0.38,40),new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:0.85,side:THREE.DoubleSide,depthWrite:false}));
  ring.rotation.x=-Math.PI/2; moveRing.add(ring);
  var dot=new THREE.Mesh(new THREE.CircleGeometry(0.08,24),new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:0.9,side:THREE.DoubleSide,depthWrite:false}));
  dot.rotation.x=-Math.PI/2; dot.position.y=0.01; moveRing.add(dot);
  moveRing.visible=false; moveRing.renderOrder=6; scene.add(moveRing);
}
function showMoveRing(x,y,z,opacity){
  if(!moveRing) return;
  moveRing.position.set(x,y+0.03,z);
  moveRing.visible=true;
  moveRing.children.forEach(function(c){ c.material.opacity=opacity; });
}
function hideMoveRing(){ if(moveRing) moveRing.visible=false; }
function floorHitAt(cx,cy){
  /* the first upward-facing surface under the cursor, or null — the
     floor a tap-to-move target (or a hover ring) stands on */
  var r=renderer.domElement.getBoundingClientRect();
  ptr.x=((cx-r.left)/r.width)*2-1; ptr.y=-((cy-r.top)/r.height)*2+1;
  ray.setFromCamera(ptr,camera);
  var fh=ray.intersectObjects(colliderMeshes,false);
  for(var i=0;i<fh.length;i++){
    var n=fh[i].face?fh[i].face.normal:null;
    var wn=n?n.clone().transformDirection(fh[i].object.matrixWorld):null;
    if(wn&&wn.y>0.5) return fh[i].point;
  }
  return null;
}
function setClickTarget(x,y,z){
  walk.clickTarget={x:x,z:z}; walk.clickBlocked=0;
  showMoveRing(x,y,z,0.9);
}
function arriveClickTarget(){
  var ex=walk.focusEx; walk.clickTarget=null; walk.clickBlocked=0; hideMoveRing();
  if(ex){
    walk.focusEx=null;
    var dir=ex.focus.clone().sub(walk.pos);
    walk.yaw=Math.atan2(-dir.x,-dir.z); walk.pitch=-0.05;
    showExhibit(ex); setExFolded(false);
  }
}
function focusExhibit(ex){
  if(!ex) return;
  showExhibit(ex); setExFolded(false);
  if(mode==='walk'){
    /* walk to the exhibit's stand point, then face it */
    focusState={mode:'walk',ex:ex};
    walk.focusEx=ex;
    setClickTarget(ex.stand.x,ex.stand.y-1.62,ex.stand.z);
    return;
  }
  /* orbit modes: remember the view, fly to a viewpoint in front of it */
  focusState={mode:mode,ex:ex,pos:camera.position.clone(),tgt:controls.target.clone()};
  flyTo(ex.stand.clone(),ex.focus.clone(),1400);
}
function exitFocus(){
  if(!focusState) return;
  var fs=focusState; focusState=null;
  walk.focusEx=null; walk.clickTarget=null; hideMoveRing();
  exhibitCard.classList.remove('show');
  if(fs.mode==='walk') return; /* stay where you are; only the card closes */
  flyTo(fs.pos,fs.tgt,1200);
}
/* item 1: hover shows the landing ring where a tap would walk to */
var hoverTick=0;
/* ================= Walk mode (#21B layout, re-measured from the v19 GLB) =================
   Two walkable levels, tested as point-in-polygon zones + AABB blockers.
   Zone edges sit ~0.35-0.5 m inside the real wall faces; a horizontal
   ray at chest height (rayWallBlocked) guards against stale tables.
   Ground (eye y=1.62): west lobby (solid slab west of the atrium void;
   the void, court and stair openings cut the slab east of x=15.6) ->
   entrance door in the slanted west edge -> paved courtyard -> forecourt
   + walkway -> Gallery 3 hall (diagonal glass + diagonal west wall)
   and its terrace (reached from the courtyard around the terrace's
   east end, not through the glass). Basement (floor y=-6.75, eye
   -5.13): platform (-5.85) -> wide steps (6) -> lower lobby -> Gallery 1
   (inset quad, floor -7.20) -> noren doorway (x=15.08, z -8..-5) ->
   Gallery 2 (x 15.08..48.56, 6 columns) -> Z corridor (x 36..44).
   The court triangle and the atrium void are looked into, not entered.
   The 39-step main stair (x 15.63-27.26, z 3.29-6.16) links the levels
   via a 3-point ride (lobby top -> platform landing -> wide-steps
   bottom); its trigger is edge-latched (see checkStairTrigger). */
var GEYE=1.62;
export const walk={pos:new THREE.Vector3(-3.5,GEYE,0.5),yaw:-2.88,pitch:0,keys:{},press:{},intro:null,level:'ground',inStair:false, /* FIX [1]: spawn on the open ground just inside the entrance (was (-1.0,-1.8), a 0.35 m strip between the shop counter and the south glass) */
  clickTarget:null,clickBlocked:0,focusEx:null};
function rectPoly(x1,z1,x2,z2){ return [[x1,z1],[x2,z1],[x2,z2],[x1,z2]]; }
function inPoly(x,z,poly){
  var inside=false;
  for(var i=0,j=poly.length-1;i<poly.length;j=i++){
    var xi=poly[i][0],zi=poly[i][1],xj=poly[j][0],zj=poly[j][1];
    if(((zi>z)!==(zj>z))&&(x<(xj-xi)*(z-zi)/(zj-zi)+xi)) inside=!inside;
  }
  return inside;
}
var GROUND_ZONES=[
  rectPoly(-10,-2.33,15.6,7),            /* west lobby: solid slab west of the void / court / stair openings */
  rectPoly(-6,-1.6,-3,1.6),              /* entrance threshold (doorway in the slanted west edge) */
  rectPoly(-14,-7,-5,7),                 /* paved courtyard between the wings */
  rectPoly(-5,-15,25,-7),                /* forecourt paving south of the museum */
  rectPoly(-8.5,-31,-3.5,-13),           /* walkway south to the site edge */
  rectPoly(-10,-7,44,-2.33),             /* lawn apron along the south glass */
  [[-24.75,-3.17],[-10.5,0.4],[-10.5,5.5],[-31.85,5.5]],  /* Gallery 3 hall, inset from its diagonal west wall and plan-diagonal south glass */
  [[-25,-8.1],[-13.5,-8.1],[-13.5,-1.29],[-25,-4.16]],    /* G3 terrace, outside the glass line */
  rectPoly(-13.7,-2.4,-12.6,-1.3)        /* terrace <-> courtyard link at the terrace's east end */
];
var BASE_ZONES=[
  rectPoly(-1,3.29,15.63,7),             /* platform west (top -5.85) */
  rectPoly(15.63,6.16,27.26,7),          /* platform north strip (top -5.85) */
  rectPoly(27.26,5.39,29.44,6.16),       /* platform landing (top -5.85) */
  rectPoly(-10,-13.77,2.43,3.29),        /* lower lobby west strip (west of G1) */
  [[2.43,3.29],[15.08,3.29],[15.08,0.46],[2.43,-2.21]],  /* lower lobby north strip (platform edge -> G1 north edge) */
  [[-10,-17.24],[15.08,-17.24],[15.08,-12.04],[7.21,-13.77],[-10,-13.77]],  /* lower lobby south strip (south of G1) */
  [[7.48,-13.08],[3.18,-2.68],[14.57,-0.28],[14.57,-11.53]],  /* Gallery 1 inset quad (floor -7.20) */
  rectPoly(15.5,-16.8,48.1,-3.7),        /* Gallery 2 (6 columns, skylight slot) */
  rectPoly(36,-3,44,1),                  /* Z corridor */
  rectPoly(14.5,-8,15.7,-5),             /* noren doorway (exhibit 09), G1 <-> G2 */
  rectPoly(29.44,6.5,39.39,8.2)          /* lookout strip along the void's north edge */
];
var GROUND_BLOCKERS=[
  [-5.60,1.50,-2.40,2.50],   /* reception desk (measured from the v19 GLB) */
  [-2.50,-1.45,0.50,-0.55],  /* shop counter */
  [-1.51,3.68,0.40,5.79],    /* elevator shaft */
  [-13.4,5.78,-11.85,6.22],  /* cafe north wall, east tip (from the courtyard side) */
  [-18,2.8,-11.4,5.7],       /* Private Room + Kitchen block (G3 east end) */
  [-13.85,0.45,-12.15,2.55], /* WC block */
  [-22.05,4.62,-18.2,5.38],  /* G3 reception desks */
  [-28.85,2.68,-28.15,3.32],[-25.07,0.18,-24.43,0.82]  /* G3 square columns */
];
/* #21B hall columns (ground): 0.45 m square, x = 0/12/24/34, z = -1.2 */
[0,12,24,34].forEach(function(cx){ GROUND_BLOCKERS.push([cx-0.225,-1.425,cx+0.225,-0.975]); });
var BASE_BLOCKERS=[
  [-1.51,3.68,0.40,5.79],    /* elevator shaft */
  [15.63,3.29,27.26,6.16],   /* main stair flight (ride uses the trigger, not walking) */
  [11.72,-1.50,12.28,0.50],[11.72,-4.00,12.28,-2.00],  /* atrium benches */
  [5.65,-4.35,6.35,-3.65],[9.65,-3.35,10.35,-2.65],    /* atrium round tables */
  [6.39,-4.71,8.72,-4.24],   /* curved bookshelf arc (centre (8,-7), r 2.8) */
  /* #21B exhibit footprints (measured from the v19 GLB AABBs): 01,02,03,05,06,07,08,10,11.
     04 is a wall panel (zone inset keeps visitors off it); 09 is the noren
     curtain the visitor walks through; 12 sits on atrium table 0. */
  [22.15,-13.12,27.15,-11.94],[26.17,-12.25,30.23,-8.25],[34.50,-11.89,38.70,-10.69],
  [39.89,-13.47,43.60,-12.27],[28.33,-7.41,30.53,-5.21],[43.18,-8.66,44.38,-7.46],
  [41.93,-16.26,43.23,-15.61],[8.53,-6.30,9.47,-5.70],[19.41,-8.07,20.31,-7.17]
];
/* #21B Gallery 2 colonnade: 0.55 m columns at z=-5.55, x = 19.09/23.25/27.39/31.52/35.68/39.84 */
[19.09,23.25,27.39,31.52,35.68,39.84].forEach(function(cx){ BASE_BLOCKERS.push([cx-0.275,-5.83,cx+0.275,-5.275]); });
export function canStand(x,z){
  var zones=(walk.level==='ground')?GROUND_ZONES:BASE_ZONES;
  var ok=false;
  for(var i=0;i<zones.length;i++){ if(inPoly(x,z,zones[i])){ ok=true; break; } }
  if(!ok) return false;
  var bl=(walk.level==='ground')?GROUND_BLOCKERS:BASE_BLOCKERS, r=0.3;
  for(var k=0;k<bl.length;k++){ var b=bl[k]; if(x>b[0]-r&&x<b[2]+r&&z>b[1]-r&&z<b[3]+r) return false; }
  return true;
}
function rayWallBlocked(fx,fz,tx,tz){
  /* item 2: a geometry wall guard. Before a step, cast a short ray
     at chest height in the step direction against the loaded GLB —
     a wall (or glass, column, tall exhibit) inside the step plus a
     0.4 m margin blocks the step, even if the hand-written zone
     tables are stale. The ray is horizontal, so floors and ceilings
     never intersect it. */
  if(!colliderMeshes.length||!modelReady) return false;
  var dx=tx-fx, dz=tz-fz;
  var dist=Math.hypot(dx,dz);
  if(dist<0.01) return false;
  ray.set(new THREE.Vector3(fx,walk.pos.y-0.45,fz),new THREE.Vector3(dx/dist,0,dz/dist));
  ray.far=dist+0.4;
  var hits=ray.intersectObjects(colliderMeshes,false);
  ray.far=Infinity;
  return hits.length>0;
}
function attemptMove(nx,nz){
  if(canStand(nx,nz)&&!rayWallBlocked(walk.pos.x,walk.pos.z,nx,nz)){ walk.pos.x=nx; walk.pos.z=nz; return true; }
  if(canStand(nx,walk.pos.z)&&!rayWallBlocked(walk.pos.x,walk.pos.z,nx,walk.pos.z)){ walk.pos.x=nx; return true; }
  if(canStand(walk.pos.x,nz)&&!rayWallBlocked(walk.pos.x,walk.pos.z,walk.pos.x,nz)){ walk.pos.z=nz; return true; }
  return false;
}
function startStair(down){
  /* #21B 3-point ride: lobby top (stair head, GL) -> platform landing
     (-5.85) -> wide-steps bottom (B1 floor -6.75). Yaws are per leg. */
  var top=new THREE.Vector3(15.0,0.3,4.7),
      land=new THREE.Vector3(28.0,-5.85,5.8),
      bot=new THREE.Vector3(10.86,-6.75,1.0);
  walk.intro={s:performance.now(),d:4200,
    pts:down?[top,land,bot]:[bot,land,top],
    yaws:down?[-1.57,1.30]:[-1.84,1.49],
    endLevel:down?'base':'ground'};
  walk.pos.copy(walk.intro.pts[0]); walk.yaw=walk.intro.yaws[0]; walk.pitch=0;
}
function checkStairTrigger(){
  if(walk.intro) return;
  var p=walk.pos;
  var inRect=(walk.level==='ground')
    ? (p.x>14.5&&p.x<16.0&&p.z>3.5&&p.z<6.0)
    : (p.x>9.68&&p.x<12.04&&p.z>1.49&&p.z<3.29);
  if(!inRect){ walk.inStair=false; return; }
  /* Edge-latched: a descent ARRIVES inside the basement rect (10.86,1.0)
     and an ascent inside the ground rect (15.0,4.7), so the plain level
     test re-fired the stair on the arrival frame and ping-ponged the
     visitor between floors every 3 s with no input at all (verified by
     simulating updateWalk). Fire only on entering the rect; the latch
     is set on arrival (introPose) and clears once the visitor steps
     out of the rect. */
  if(walk.inStair) return;
  walk.inStair=true;
  startStair(walk.level==='ground');
}
export function enterWalk(){
  camAnimBox.current=null;
  walk.clickTarget=null; walk.clickBlocked=0; walk.focusEx=null; hideMoveRing();
  walk.level='ground';
  walk.intro={s:performance.now(),d:8000,
    pts:[new THREE.Vector3(-3.5,GEYE,0.5), new THREE.Vector3(15.0,0.3,4.7), new THREE.Vector3(28.0,-5.85,5.8), new THREE.Vector3(10.86,-6.75,1.0)], /* FIX [1]: intro starts at the new spawn */
    yaws:[-1.96,-1.57,1.30],
    endLevel:'base'};
  walk.pos.copy(walk.intro.pts[0]); walk.yaw=walk.intro.yaws[0]; walk.pitch=0;
  if(!currentEx) showExhibit(exhibits[0]);
}
function introPose(nowMs){
  var it=walk.intro; if(!it) return false;
  var k=(nowMs-it.s)/it.d;
  var last=it.pts[it.pts.length-1];
  if(k>=1){ walk.intro=null; if(it.endLevel) walk.level=it.endLevel; walk.inStair=true; /* arrivals stand inside a stair rect — don't let it re-fire */ walk.pos.copy(last); walk.yaw=it.yaws[it.yaws.length-1]; walk.pitch=0; return false; }
  var segLens=[], total=0;
  for(var i=0;i<it.pts.length-1;i++){ var L=it.pts[i].distanceTo(it.pts[i+1]); segLens.push(L); total+=L; }
  var dist=k*total, acc=0, done=false;
  for(var s2=0;s2<segLens.length;s2++){
    if(dist<=acc+segLens[s2]||s2===segLens.length-1){
      var t=segLens[s2]>0?(dist-acc)/segLens[s2]:0; t=Math.max(0,Math.min(1,t));
      walk.pos.lerpVectors(it.pts[s2],it.pts[s2+1],t); walk.yaw=it.yaws[Math.min(s2,it.yaws.length-1)]; done=true; break;
    }
    acc+=segLens[s2];
  }
  walk.pitch=0;
  return true;
}
function nudge(k,dist){
  var s=Math.sin(walk.yaw), c=Math.cos(walk.yaw);
  var f={x:-s,z:-c}, r={x:c,z:-s};
  var dx=0,dz=0;
  if(k==='f'){ dx=f.x*dist; dz=f.z*dist; }
  if(k==='b'){ dx=-f.x*dist; dz=-f.z*dist; }
  if(k==='l'){ dx=-r.x*dist; dz=-r.z*dist; }
  if(k==='r'){ dx=r.x*dist; dz=r.z*dist; }
  attemptMove(walk.pos.x+dx,walk.pos.z+dz);
  checkStairTrigger();
}
var lookDrag=null;
/* item 6: optional pointer lock for desktop walk mode. A toggle
   button in the walk HUD (hidden on touch devices) — click the
   scene to lock, Esc to unlock. While locked, mouse movement turns
   the view; tap-to-move is suspended (the cursor is hidden). */
export function updateWalk(dt,nowMs){
  if(!introPose(nowMs)){
    var sp=6.2*dt;
    var s=Math.sin(walk.yaw), c=Math.cos(walk.yaw);
    var f={x:-s,z:-c}, r={x:c,z:-s};
    var mv={x:0,z:0};
    if(walk.keys['w']||walk.keys['arrowup']||walk.press.f){ mv.x+=f.x; mv.z+=f.z; }
    if(walk.keys['s']||walk.keys['arrowdown']||walk.press.b){ mv.x-=f.x; mv.z-=f.z; }
    if(walk.keys['a']||walk.keys['arrowleft']||walk.press.l){ mv.x-=r.x; mv.z-=r.z; }
    if(walk.keys['d']||walk.keys['arrowright']||walk.press.r){ mv.x+=r.x; mv.z+=r.z; }
    if(walk.keys['q']) walk.yaw+=1.8*dt;
    if(walk.keys['e']) walk.yaw-=1.8*dt;
    var len=Math.hypot(mv.x,mv.z);
    if(len>0){
      attemptMove(walk.pos.x+mv.x/len*sp, walk.pos.z+mv.z/len*sp);
      /* any manual move input cancels a tap-to-move target */
      walk.clickTarget=null; walk.clickBlocked=0; hideMoveRing();
    }
    /* item 1: glide toward a tapped floor point. attemptMove slides
       along walls, so a straight-line target that clips a corner
       still gets there by sliding. */
    if(walk.clickTarget){
      var cdx=walk.clickTarget.x-walk.pos.x, cdz=walk.clickTarget.z-walk.pos.z;
      var cdd=Math.hypot(cdx,cdz);
      if(cdd<0.35){ arriveClickTarget(); }
      else{
        var bx=walk.pos.x, bz=walk.pos.z;
        attemptMove(walk.pos.x+cdx/cdd*sp, walk.pos.z+cdz/cdd*sp);
        if(Math.hypot(walk.pos.x-bx,walk.pos.z-bz)<sp*0.15){
          walk.clickBlocked=(walk.clickBlocked||0)+1;
          if(walk.clickBlocked>45){ walk.clickTarget=null; walk.clickBlocked=0; hideMoveRing(); }
        }else walk.clickBlocked=0;
        checkStairTrigger();
      }
    }
    checkStairTrigger();
    /* item 2: ground snap — keep the eye on the model's real floor.
       Only within tolerance of the level's expected floor (0 / -6.75),
       so a ray through the atrium opening can never drop the visitor.
       Base tolerance 1.0 covers the platform (-5.85) and G1 (-7.20). */
    if(modelReady&&colliderMeshes.length){
      ray.set(new THREE.Vector3(walk.pos.x,walk.pos.y+0.3,walk.pos.z),new THREE.Vector3(0,-1,0));
      ray.far=2.2;
      var gh=ray.intersectObjects(colliderMeshes,false);
      ray.far=Infinity;
      if(gh.length){
        var fy=gh[0].point.y;
        var expectY=(walk.level==='ground')?0:-6.75;
        var tol=(walk.level==='ground')?0.6:1.0;
        if(Math.abs(fy-expectY)<tol){
          walk.pos.y+=(fy+1.62-walk.pos.y)*Math.min(1,dt*8);
        }
      }
    }
  }
  camera.position.copy(walk.pos);
  var look=new THREE.Vector3(
    walk.pos.x - Math.sin(walk.yaw)*Math.cos(walk.pitch),
    walk.pos.y + Math.sin(walk.pitch),
    walk.pos.z - Math.cos(walk.yaw)*Math.cos(walk.pitch)
  );
  camera.lookAt(look);
  if(walk.level==='base'){
    /* release the hold once the visitor has actually walked away */
    if(walk.holdEx&&walk.pos.distanceTo(walk.holdEx.stand)>=0.05) walk.holdEx=null;
    var best=null,bd=1e9;
    exhibits.forEach(function(ex){ var d=ex.focus.distanceTo(walk.pos); if(d<bd){bd=d;best=ex;} });
    if(best&&bd<4.6&&best!==currentEx&&!walk.holdEx) showExhibit(best);
  }
}

export function initWalk(){
  initMoveRing();
  window.addEventListener('keydown',function(e){
    if(e.key!=='Escape') return;
    /* Esc unlocks the pointer first (real browsers also exit pointer lock
       natively on Esc, but a synthetic Esc — e.g. in a test — does not, so
       exit explicitly; calling it when not locked is a no-op). */
    if(document.pointerLockElement===renderer.domElement){ document.exitPointerLock(); return; }
    if(focusState){ exitFocus(); }
  });
  renderer.domElement.addEventListener('pointerdown',function(e){ downAt=[e.clientX,e.clientY]; });
  renderer.domElement.addEventListener('pointerup',function(e){
    if(!downAt) return;
    var moved=Math.hypot(e.clientX-downAt[0],e.clientY-downAt[1]); downAt=null;
    if(moved>6||mode==='exterior'||mode==='tour'||!pickMeshes.length) return;
    var r=renderer.domElement.getBoundingClientRect();
    ptr.x=((e.clientX-r.left)/r.width)*2-1; ptr.y=-((e.clientY-r.top)/r.height)*2+1;
    ray.setFromCamera(ptr,camera);
    var hits=ray.intersectObjects(pickMeshes,false);
    var exHit=hits.length?hits[0]:null;
    /* occlusion: a wall or floor between the camera and the exhibit
       hides it — without this, a tap on the lobby floor would "hit"
       an exhibit in the basement below through the slab. colliderMeshes
       holds walls/floors only (no exhibit meshes), so a clear sightline
       gives no collider hit at all, and any collider hit strictly in
       front of the exhibit (5 cm epsilon) means the exhibit is hidden
       behind structure. */
    var colliderHit=null;
    if(exHit&&colliderMeshes.length){
      var sh=ray.intersectObjects(colliderMeshes,false);
      if(sh.length) colliderHit=sh[0];
    }
    if(exHit&&(!colliderHit||colliderHit.distance>=exHit.distance-0.05)){
      focusExhibit(exHit.object.userData.exhibit);
      return;
    }
    if(focusState){ exitFocus(); return; }
    if(mode==='walk'&&!pointerLocked){
      /* item 1: tap the floor to walk there */
      var p=floorHitAt(e.clientX,e.clientY);
      if(p&&canStand(p.x,p.z)) setClickTarget(p.x,p.y,p.z);
    }
  });
  renderer.domElement.addEventListener('pointermove',function(e){
    if(mode!=='walk'||pointerLocked||!modelReady||walk.clickTarget) return;
    var nowMs=performance.now();
    if(nowMs-hoverTick<90) return; hoverTick=nowMs;
    var p=floorHitAt(e.clientX,e.clientY);
    if(p&&canStand(p.x,p.z)) showMoveRing(p.x,p.y,p.z,0.55);
    else hideMoveRing();
  });
  window.addEventListener('keydown',function(e){ walk.keys[e.key.toLowerCase()]=true; });
  window.addEventListener('keyup',function(e){ walk.keys[e.key.toLowerCase()]=false; });
  document.querySelectorAll('[data-move]').forEach(function(b){
    var k=b.dataset.move;
    function on(e){ e.preventDefault(); walk.press[k]=true; }
    function off(){ walk.press[k]=false; }
    b.addEventListener('pointerdown',on); b.addEventListener('pointerup',off); b.addEventListener('pointerleave',off); b.addEventListener('pointercancel',off);
    b.addEventListener('click',function(){ if(mode==='walk'&&!walk.intro) nudge(k,0.9); });
  });
  document.querySelectorAll('[data-look]').forEach(function(b){
    b.addEventListener('click',function(){ if(mode==='walk') walk.yaw+=parseFloat(b.dataset.look)*0.45; });
  });
  renderer.domElement.addEventListener('pointerdown',function(e){ if(mode==='walk') lookDrag=[e.clientX,e.clientY]; });
  window.addEventListener('pointermove',function(e){
    if(mode!=='walk'||!lookDrag||pointerLocked) return;
    walk.yaw-=(e.clientX-lookDrag[0])*0.005;
    walk.pitch-=(e.clientY-lookDrag[1])*0.004;
    walk.pitch=Math.max(-0.9,Math.min(0.9,walk.pitch));
    lookDrag=[e.clientX,e.clientY];
  });
  window.addEventListener('pointerup',function(){ lookDrag=null; });
  var lockBtn=document.getElementById('lockBtn');
  if(lockBtn){
    lockBtn.addEventListener('click',function(){
      if(document.pointerLockElement===renderer.domElement){ document.exitPointerLock(); return; }
      if(mode!=='walk') return;
      try{ renderer.domElement.requestPointerLock(); }catch(e){}
    });
    document.addEventListener('pointerlockchange',function(){
      pointerLocked=(document.pointerLockElement===renderer.domElement);
      lockBtn.setAttribute('aria-pressed',pointerLocked?'true':'false');
      lockBtn.textContent=pointerLocked?'已锁定':'锁定';
    });
    document.addEventListener('mousemove',function(e){
      if(!pointerLocked||mode!=='walk') return;
      walk.yaw-=e.movementX*0.0025;
      walk.pitch-=e.movementY*0.0025;
      walk.pitch=Math.max(-0.9,Math.min(0.9,walk.pitch));
    });
  }
}
