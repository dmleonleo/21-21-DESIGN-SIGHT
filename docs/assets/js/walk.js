// walk.js — walk mode: zones, collision, stair, picking, exhibit approach.
// Split from the single inline script of docs/index.html (main @62eeaac6).
// Behaviour unchanged: only the module boundary is new.
import * as THREE from 'three';
import { camera, renderer, pickMeshes } from './scene.js';
import { mode, setMode, camAnimBox } from './camera.js';
import { showExhibit, currentEx } from './ui.js';
import { exhibits, EYE_Y } from './labels.js';

var ray=new THREE.Raycaster(), ptr=new THREE.Vector2(), downAt=null;
export function goNearExhibit(ex){
  if(mode!=='walk'){ setMode('walk'); }
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
/* ================= Walk mode (v16 layout, re-measured) =================
   Two walkable levels, tested as point-in-polygon zones + AABB blockers.
   These tables were re-derived from the v16 GLB's actual triangles —
   mesh AABBs alone hide the plan diagonals — after walk mode was found
   passing through walls the old tables got wrong: the z=1 partition's
   only real opening is the noren doorway at x 28-31 (the old "gaps" at
   x 18-21 and 23.5-24.5 are solid Part_G1G2_B / Court_Wall_North), the
   x=8 atrium wall line opened only at z 2.0-3.4 (SM_Atrium_Wall_East_A
   stood solid across the stair foot at z 3.4-5.0 — it is shifted north
   at load, see fixStairFootWall — and the old x=12 blockers guarded a
   wall that does not exist), the museum's NE diagonal wall and the G1/G3
   diagonal walls cut straight through the old axis-aligned zones, the
   lobby zone ran east over the atrium opening and south through the
   sloped glass, and the sunken-courtyard pit — enclosed by glass and
   walls in the model — was covered by the G2 rectangle. Zone edges now
   sit ~0.35-0.5 m inside the real wall faces.
   Ground (eye y=1.62): entrance lobby (solid slab west of the atrium
   opening; the sloped south glass crosses eye height at z≈-5.23, so the
   lobby stops at z=-4.95) -> entrance door -> covered passage -> paved
   courtyard -> cafe door -> Gallery 3 hall (diagonal glass + diagonal
   west wall) and its terrace (reached from the courtyard around the
   terrace's east end, not through the glass). Basement (floor y=-4.8,
   eye -3.18): stair landing -> atrium vestibule -> the x=8 gap
   (z 2.0-3.4) -> Gallery 1 trapezoid -> noren doorway -> Gallery 2
   (NE corner cut by the diagonal exterior wall, NW corner cut around
   the courtyard glass) -> lookout strip along the pit's west wall,
   through the x=10 glass gap (z -3..-1) to the pocket between the two
   glass walls. The pit itself is looked into, not entered.
   The 30-step stair (x 0-8.1, z 3-5) links the levels; its trigger is
   edge-latched (see checkStairTrigger). */
var GEYE=1.62;
export const walk={pos:new THREE.Vector3(-1.0,GEYE,-1.8),yaw:-2.88,pitch:0,keys:{},press:{},intro:null,level:'ground',inStair:false};
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
  rectPoly(-2,-4.95,1.1,5.6),            /* lobby: solid slab west of the atrium opening */
  rectPoly(-3.4,-1.7,1.1,1.7),           /* entrance threshold */
  rectPoly(-10.6,-1.35,-2.2,1.35),       /* covered passage between the wings */
  rectPoly(-13.2,-8.6,-3.55,8),          /* paved courtyard west of the entrance blocks */
  rectPoly(-10.6,-8.6,1,-7.35),          /* apron south of the glass foot (glass meets floor at z=-7) */
  [[-24.75,-3.17],[-10.5,0.4],[-10.5,5.5],[-31.85,5.5]],  /* Gallery 3 hall, inset from its diagonal west wall and plan-diagonal south glass */
  [[-25,-8.1],[-13.5,-8.1],[-13.5,-1.29],[-25,-4.16]],    /* G3 terrace, outside the glass line */
  rectPoly(-13.7,-2.4,-12.6,-1.3)        /* terrace <-> courtyard link at the terrace's east end */
];
var BASE_ZONES=[
  rectPoly(-1.8,-5,7.6,6.45),            /* atrium vestibule (north edge inset from the z=6.82 wall) */
  rectPoly(7.4,2.9,9.7,5.1),             /* stair landing, east of the atrium wall line */
  rectPoly(7.4,2.4,12,3.0),              /* doorway corridor through the x=8 gap (z 2.0-3.4) */
  [[8.45,1.45],[34.11,1.45],[21.73,6.43],[8.45,6.43]],  /* Gallery 1 trapezoid, inset from partition / north lining / NE diagonal */
  [[10.35,-15.45],[51.45,-15.45],[51.45,0.5],[42.45,0.5],[42.45,-1.85],[36.8,0.28],[20.18,0.5],[15.35,-5.29],[10.35,-5.75]],  /* Gallery 2: NE corner cut by the diagonal exterior wall (SW face z=-0.4x+15.62), NW corner cut around the courtyard glass */
  rectPoly(28.3,0.4,30.7,1.55),          /* noren doorway (exhibit 09), G1 <-> G2 */
  rectPoly(8.35,-6.2,10.35,0.55),        /* pocket between the atrium glass (x=8) and the atrium/G2 glass (x=10) */
  [[10.35,-5.75],[14.8,-5.45],[9.79,0.55],[10.35,0.55]] /* lookout strip along the pit's west wall, inset from it */
];
var GROUND_BLOCKERS=[
  [-1.15,-6.35,5.5,-5.05],   /* reception desk + shop counter */
  [-0.4,-4.8,2,-2.4],        /* elevator shaft */
  [-3.25,-7.5,-1.95,-1.6],[-3.25,1.6,-1.95,7.5],  /* entrance blocks S / N */
  [-9.72,-1.42,-9.28,-0.98],[-9.72,0.98,-9.28,1.42],[-2.72,-1.42,-2.28,-0.98],[-2.72,0.98,-2.28,1.42],  /* passage posts */
  [-13.4,5.78,-11.85,6.22],  /* cafe north wall, east tip (from the courtyard side) */
  [-18,2.8,-11.4,5.7],       /* Private Room + Kitchen block (G3 east end) */
  [-13.85,0.45,-12.15,2.55], /* WC block */
  [-22.05,4.62,-18.2,5.38],  /* G3 reception desks */
  [-28.85,2.68,-28.15,3.32],[-25.07,0.18,-24.43,0.82]  /* G3 square columns */
];
var BASE_BLOCKERS=[
  [-0.4,-4.8,2,-2.4],        /* elevator shaft */
  [-0.2,2.95,6.5,5.05],      /* under the stair flight (incl. the bookshelf) */
  [6.85,-4.05,7.55,0.55],    /* atrium benches along the east glass */
  [1.6,5.1,2.4,5.9],[5.6,5.1,6.4,5.9],  /* atrium tables */
  [7.8,-5.2,8.2,2.0],        /* x=8 line: atrium glass (z -5..1) + wall B (z 1..2) */
  [7.8,5.0,8.2,7.0],         /* x=8 line: wall A (shifted north at load to z 5..6.6) + G1 west wall (z 5..7) — the stair foot (z 3.4..5) and the gap z 2.0..3.4 (the G1 door) are open */
  [9.8,-5.1,10.2,-3.0],[9.8,-1.0,10.2,1.05],  /* x=10 atrium/G2 glass — the gap z -3..-1 is the opening */
  [8,0.82,28,1.18],[31,0.82,52,1.18],  /* z=1 partition + courtyard north wall — the noren opening x 28..31 is the only break */
  /* v16 exhibit footprints (measured from the GLB): 01..12 */
  [29.4,-10.3,34.6,-8.95],[33,-9,37,-5],[39.9,-8.8,44.1,-7.6],[34,-15.95,42,-15.7],
  [44.4,-10.7,48.0,-9.3],[34.9,-3.6,37.1,-1.4],[47.4,-5.1,48.6,-3.9],[46.35,-13.85,47.65,-13.15],
  [14.5,3.2,15.5,3.8],[27.55,-4.45,28.45,-3.55],[5.79,5.35,6.21,5.65]
];
/* v16 Gallery 2 colonnade: 0.55 m columns at z=-1.8, x = 26..50 step 4 */
[26,30,34,38,42,46,50].forEach(function(cx){ BASE_BLOCKERS.push([cx-0.3,-2.1,cx+0.3,-1.5]); });
function canStand(x,z){
  var zones=(walk.level==='ground')?GROUND_ZONES:BASE_ZONES;
  var ok=false;
  for(var i=0;i<zones.length;i++){ if(inPoly(x,z,zones[i])){ ok=true; break; } }
  if(!ok) return false;
  var bl=(walk.level==='ground')?GROUND_BLOCKERS:BASE_BLOCKERS, r=0.3;
  for(var k=0;k<bl.length;k++){ var b=bl[k]; if(x>b[0]-r&&x<b[2]+r&&z>b[1]-r&&z<b[3]+r) return false; }
  return true;
}
function attemptMove(nx,nz){
  if(canStand(nx,nz)){ walk.pos.x=nx; walk.pos.z=nz; return true; }
  if(canStand(nx,walk.pos.z)){ walk.pos.x=nx; return true; }
  if(canStand(walk.pos.x,nz)){ walk.pos.z=nz; return true; }
  return false;
}
function startStair(down){
  var top=new THREE.Vector3(0.2,GEYE,4.0), bot=new THREE.Vector3(8.8,EYE_Y,4.0);
  walk.intro={s:performance.now(),d:3000,
    pts:down?[top,bot]:[bot,top],
    yaws:down?[Math.atan2(-8.6,-0.1)]:[Math.atan2(8.6,0.1)],
    endLevel:down?'base':'ground'};
  walk.pos.copy(walk.intro.pts[0]); walk.yaw=walk.intro.yaws[0]; walk.pitch=0;
}
function checkStairTrigger(){
  if(walk.intro) return;
  var p=walk.pos;
  var inRect=(walk.level==='ground')
    ? (p.x>-0.3&&p.x<2.2&&p.z>3.0&&p.z<5.0)
    : (p.x>6.5&&p.x<9.8&&p.z>3.0&&p.z<5.0);
  if(!inRect){ walk.inStair=false; return; }
  /* Edge-latched: a descent ARRIVES inside the basement rect (8.8,4.0)
     and an ascent inside the ground rect (0.2,4.0), so the plain level
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
  walk.level='ground';
  walk.intro={s:performance.now(),d:5600,
    pts:[new THREE.Vector3(-1.0,GEYE,-1.8), new THREE.Vector3(0.5,GEYE,3.9), new THREE.Vector3(8.8,EYE_Y,4.0)],
    yaws:[Math.atan2(-1.5,-5.7), Math.atan2(-8.3,-0.1)],
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
    if(len>0){ attemptMove(walk.pos.x+mv.x/len*sp, walk.pos.z+mv.z/len*sp); }
    checkStairTrigger();
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
    if(mode!=='walk'||!lookDrag) return;
    walk.yaw-=(e.clientX-lookDrag[0])*0.005;
    walk.pitch-=(e.clientY-lookDrag[1])*0.004;
    walk.pitch=Math.max(-0.9,Math.min(0.9,walk.pitch));
    lookDrag=[e.clientX,e.clientY];
  });
  window.addEventListener('pointerup',function(){ lookDrag=null; });
  renderer.domElement.addEventListener('pointerdown',function(e){ downAt=[e.clientX,e.clientY]; });
  renderer.domElement.addEventListener('pointerup',function(e){
    if(!downAt) return;
    var moved=Math.hypot(e.clientX-downAt[0],e.clientY-downAt[1]); downAt=null;
    if(moved>6||mode==='exterior'||mode==='tour'||!pickMeshes.length) return;
    var r=renderer.domElement.getBoundingClientRect();
    ptr.x=((e.clientX-r.left)/r.width)*2-1; ptr.y=-((e.clientY-r.top)/r.height)*2+1;
    ray.setFromCamera(ptr,camera);
    var hits=ray.intersectObjects(pickMeshes,false);
    if(hits.length&&hits[0].object.userData.exhibit) showExhibit(hits[0].object.userData.exhibit);
  });
}
