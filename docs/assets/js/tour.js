// tour.js — the 14-stop automatic tour (route, pacing, progress, controls).
// Split from the single inline script of docs/index.html
// (merged14: #9-#14 serial chain + round-2 review fixes).
// Behaviour unchanged: only the module boundary is new.
import * as THREE from 'three';
import { camera, controls } from './scene.js';
import { mode, exteriorCamPos, EXT_TARGET, setMode, camAnimBox, syncHash } from './camera.js';
import { flashVertical } from './ui.js';

/* ================= Auto tour =================
   A fixed cinematic route through the whole building, reusing the same
   verified camera positions as the lobby / G3 / gallery / walk modes:
   aerial -> facade -> courtyard -> lobby -> 39-step stair -> Gallery 1 ->
   Gallery 2 overview -> exhibits 01/02 -> 06 -> 05 -> sunken courtyard ->
   up and over the lawn -> Gallery 3 (west wing) -> closing aerial.
   Each leg flies smoothly to the stop, then dwells there (with a slow
   push-in) while its narration card is shown, then moves on. The visitor
   can pause, jump to the previous / next stop, tap a progress segment to
   jump, or exit at any time; picking any other mode also ends the tour. */
export const tourStops=[
  {title:'鸟瞰开场 · 两栋建筑',dwell:3400,
   desc:'先从空中看全貌：东侧是博物馆翼，一整张 54 米长的钢板折成屋顶；西侧较小的咖啡翼是 Gallery 3 所在。约八成空间藏在地下，草坪上只露出折叠的屋顶。',
   cam:new THREE.Vector3(12,26,-66), tgt:new THREE.Vector3(7,0,-4)},
  {title:'正面 · 玻璃立面',dwell:3400,
   desc:'博物馆翼的南立面几乎全是玻璃，清水混凝土墙与折叠钢板屋顶在这里交汇。透过玻璃能隐约看到入口大堂——游览的下一站就在里面。',
   cam:new THREE.Vector3(20,5.5,-36), tgt:new THREE.Vector3(19,2,-3)},
  {title:'两栋之间 · 铺地庭院',dwell:3200,
   desc:'两栋建筑之间的铺地庭院是地面的交通核：向东进博物馆翼大堂，穿过庭院向西，就是 Gallery 3 的入口。',
   cam:new THREE.Vector3(-13,3.4,-20), tgt:new THREE.Vector3(-5,1.2,1)},
  {title:'入口大堂 · 接待台与电梯',dwell:3400,
   desc:'大堂在博物馆翼地面层：接待台与商店在西侧，梯形平面的电梯在北侧平台角。展厅在地下——接下来走楼梯下去。',
   cam:new THREE.Vector3(-6,1.9,2), tgt:new THREE.Vector3(2,0.4,-1)},
  {title:'39 级楼梯 · 下到地下层',dwell:3000,
   desc:'楼梯共 39 级、每级高 0.15 米，北侧是混凝土墙加钢扶手、南侧是玻璃栏板。顺着它下行 5.85 米，就到了地下展厅层。',
   cam:new THREE.Vector3(28,-4.2,5.8), tgt:new THREE.Vector3(15,0.5,4.7)},
  {title:'Gallery 1 · 天窗斜板厅',dwell:3400,
   desc:'Gallery 1 约 129 m²，斜置四边形平面，靠 6 块斜向半透明板把天光引进来，白色天花下有一扇深色方窗。这里是地下层最明亮的房间。',
   cam:new THREE.Vector3(6,-5.6,-9), tgt:new THREE.Vector3(12,-4.5,-0.5)},
  {title:'Gallery 2 · 全景',dwell:3400,
   desc:'Gallery 2 层高 4.8 米，是全馆最大的展厅。地下层约 1,338 m²，轮廓向东到 x≈48.6；0.55 米方柱仅一排 6 根，沿柱线有一条连续天窗缝。全馆共 12 件：01–08 与 11 在这间东侧大厅里，09 暖帘挂在两厅之间，10 在 Gallery 1，12 在下层大厅。',
   cam:new THREE.Vector3(18,-1.2,-15), tgt:new THREE.Vector3(45,-4.5,-6)} /* #7: reframe — red fabric to the right edge as a frame, not a wall */,
  {title:'展品 01 · 一块布 / 02 · 光的织物',dwell:3800,
   desc:'01《一块布 · A-POC 织物》：一块布直接织造成衣，正是折叠钢板屋顶的灵感来源。02《光的织物》：七盏球形吊灯如经纬般垂落——地下展厅里，光本身就是展品。',
   cam:new THREE.Vector3(22,-4.5,-9), tgt:new THREE.Vector3(26,-4.5,-12)},
  {title:'展品 06 · 转动的圆',dwell:3600,
   desc:'Gallery 2 中央，圆环装置在缓慢旋转——圆是这栋三角建筑里唯一的曲线。旁边的展带上还有 03《坐的设计》三把椅子与南墙上的 04《字与形》平面设计墙。',
   cam:new THREE.Vector3(33.7,-5.13,-6.31), tgt:new THREE.Vector3(29.43,-4.65,-6.31)},
  {title:'展品 05 · 器物（展厅深处）',dwell:3400,
   desc:'走到展厅东侧深处，是 05《器物 · 陶罐》：拉坯的曲线没有一处多余。再往东到尽头，是 07《Akari 纸灯》的暖光。21_21 常把最日常的器物放上展台——设计就在每天端起的那只杯子里。',
   cam:new THREE.Vector3(41.39,-5.13,-10.77), tgt:new THREE.Vector3(41.39,-5.85,-12.87)},
  {title:'下沉庭院 · 露天深坑',dwell:3400,
   desc:'三角形下沉庭院是一个真正的露天坑，坑底就是地下层地面，约 74 m²。庭院把阳光送进地下展厅——这是这栋地下建筑真正的「立面」。从下层大厅望去，隔着整面玻璃正对坑底，最高的方立柱约 11.6 米。',
   cam:new THREE.Vector3(22,-4.0,4.0), tgt:new THREE.Vector3(33,-5.0,1.0)}, /* #7: pit-floor-looking-up is impossible — OrbitControls maxPolarAngle (PI*0.52) clamps the camera to level with the target; this IS the clamped position, verified by screenshot (pit opening, west-wall skylight slit, stair, sky) */
  {title:'前往西翼 · 越过草坪',dwell:1400,
   desc:'地下参观到此结束。镜头升上草坪上空，越过下沉庭院，飞往西侧咖啡翼——Gallery 3 在那里。',
   cam:new THREE.Vector3(-2,24,-28), tgt:new THREE.Vector3(-20,1,1)},
  {title:'Gallery 3 · 西翼展厅',dwell:4000,
   desc:'Gallery 3 在西翼（原咖啡厅，2017 年改建），不在博物馆翼：四边形展厅约 111.7 m²，深灰花岗岩地面，白色石膏斜顶最高 4.26 米，北墙有窗缝与磨砂玻璃带，南侧整面玻璃外是 57 m² 露台。',
   cam:new THREE.Vector3(-24,1.6,4.2), tgt:new THREE.Vector3(-13,0.8,-2.0)}, /* #14 review (Hark 2026-11-19): #7 had set this back to (-31.5,1.7,4.6), which shows the black wedge seam between roof and ceiling — restored to #9's G3 view 1, same as g3Spots[0] */
  {title:'收尾 · 回到鸟瞰',dwell:5200,
   desc:'游览结束：从空中再看一次两栋建筑——一块布折成的屋顶、藏在地下的展厅、引光的庭院。想自己走走，可以点「进入展厅 · 步行参观」；想再看一遍，点「下一站」会从头开始。',
   /* the closing aerial is the verified aerial preset view (issue
      #2.1): the old stop sat at (4,46,-54), and the flight into it
      from stop 13 ran low over the museum roof, so the frame filled
      with one grey roof slope. From the aerial preset the flight
      climbs steeply and the closing frame is the whole site. */
   cam:new THREE.Vector3(7,74,-34), tgt:new THREE.Vector3(7,0,-4)}
];
var tourHud=document.getElementById('tourHud');
var tourNoEl=document.getElementById('tourNo');
var tourTitleEl=document.getElementById('tourTitle');
var tourDescEl=document.getElementById('tourDesc');
var tourFillEl=document.getElementById('tourFill');
var tourDotsEl=document.getElementById('tourDots');
var tourPauseBtn=document.getElementById('tourPause');
var tourDots=[];
tourStops.forEach(function(s,i){
  var b=document.createElement('button');
  b.type='button'; b.title=s.title;
  b.setAttribute('aria-label','跳到第 '+(i+1)+' 站：'+s.title);
  b.addEventListener('click',function(){ tourJump(i); });
  tourDotsEl.appendChild(b); tourDots.push(b);
});
/* item 4: the progress bar itself is clickable — tap anywhere on the
   track to jump to that stop. The dots already did this; the track
   makes the whole bar a target, and it is keyboard-operable too. */
var tourTrackEl=document.getElementById('tourTrack');
tourTrackEl.addEventListener('click',function(e){
  var r=tourTrackEl.getBoundingClientRect();
  var frac=Math.max(0,Math.min(1,(e.clientX-r.left)/r.width));
  tourJump(Math.min(tourStops.length-1,Math.floor(frac*tourStops.length)));
});
tourTrackEl.addEventListener('keydown',function(e){
  if(e.key==='ArrowLeft'){ e.preventDefault(); tourJump(tour.idx-1); }
  else if(e.key==='ArrowRight'){ e.preventDefault(); tourJump(tour.idx+1); }
  else if(e.key==='Home'){ e.preventDefault(); tourJump(0); }
  else if(e.key==='End'){ e.preventDefault(); tourJump(tourStops.length-1); }
});
export const tour={idx:0,phase:'travel',start:0,travelDur:3000,dwellDur:3400,
  fromPos:new THREE.Vector3(),fromTgt:new THREE.Vector3(),
  paused:false,pauseAt:0,drift:new THREE.Vector3()};
function tourEase(k){ return k<0.5 ? 4*k*k*k : 1-Math.pow(-2*k+2,3)/2; }
function tourShowCard(){
  var s=tourStops[tour.idx];
  tourNoEl.textContent='自动游览 · '+(tour.idx+1)+' / '+tourStops.length+(tour.paused?' · 已暂停':'');
  tourTitleEl.textContent=s.title;
  tourDescEl.textContent=s.desc;
  tourFillEl.style.width=((tour.idx)/tourStops.length*100)+'%';
  var trackEl=document.getElementById('tourTrack');
  if(trackEl){
    trackEl.setAttribute('aria-valuenow',String(tour.idx+1));
    trackEl.setAttribute('aria-valuetext','第 '+(tour.idx+1)+' 站：'+s.title);
  }
  tourDots.forEach(function(b,i){
    b.className=i<tour.idx?'done':(i===tour.idx?'now':'');
  });
}
export function tourGoTo(idx,nowMs){
  tour.idx=(idx+tourStops.length)%tourStops.length;
  var s=tourStops[tour.idx];
  tour.fromPos.copy(camera.position);
  tour.fromTgt.copy(controls.target);
  var dist=tour.fromPos.distanceTo(s.cam);
  tour.travelDur=Math.max(2600,Math.min(6800,dist*150));
  /* item 4: the dwell follows the narration length (6-10 s), not a
     fixed 3.4 s — ~55 ms per character plus a 2 s base, clamped. */
  tour.dwellDur=Math.max(6000,Math.min(10000,2000+Math.round(s.desc.length*55)));
  tour.phase='travel';
  tour.start=nowMs;
  tour.paused=false; tourPauseBtn.textContent='暂停';
  tourShowCard();
  syncHash();
  flashVertical();
}
function tourJump(idx){ if(mode==='tour') tourGoTo(idx,performance.now()); }
export function startTour(){
  camAnimBox.current=null;
  tourGoTo(0,performance.now());
  /* start from the fitted exterior framing so the first leg is short */
  camera.position.copy(exteriorCamPos()); controls.target.copy(EXT_TARGET);
  tour.fromPos.copy(camera.position); tour.fromTgt.copy(controls.target);
  var dist=tour.fromPos.distanceTo(tourStops[0].cam);
  tour.travelDur=Math.max(2600,Math.min(6800,dist*150));
  tour.start=performance.now();
}
function setTourPaused(p){
  if(mode!=='tour') return;
  var nowMs=performance.now();
  if(p&&!tour.paused){ tour.paused=true; tour.pauseAt=nowMs; }
  else if(!p&&tour.paused){ tour.paused=false; tour.start+=nowMs-tour.pauseAt; }
  tourPauseBtn.textContent=tour.paused?'继续':'暂停';
  tourShowCard();
}
var tourFoldBtn=document.getElementById('tourFold');
export function setTourFolded(f){
  tourHud.classList.toggle('folded',f);
  tourFoldBtn.textContent=f?'展开讲解':'收起讲解';
  tourFoldBtn.setAttribute('aria-expanded',f?'false':'true');
}
export function updateTour(nowMs){
  if(tour.paused) return true;
  var s=tourStops[tour.idx];
  if(tour.phase==='travel'){
    var k=(nowMs-tour.start)/tour.travelDur;
    if(k>=1){
      camera.position.copy(s.cam); controls.target.copy(s.tgt);
      tour.phase='dwell'; tour.start=nowMs;
      /* slow push-in direction for the dwell phase */
      tour.drift.copy(s.tgt).sub(s.cam).normalize().multiplyScalar(0.55);
      tourFillEl.style.width=((tour.idx+1)/tourStops.length*100)+'%';
      return true;
    }
    var e=tourEase(Math.max(0,k));
    camera.position.lerpVectors(tour.fromPos,s.cam,e);
    controls.target.lerpVectors(tour.fromTgt,s.tgt,e);
    return true;
  }
  /* dwell: hold the stop, drifting very slightly toward the subject */
  if(tour.phase==='done') return true;
  var dk=(nowMs-tour.start)/tour.dwellDur;
  if(dk>=1){
    if(tour.idx>=tourStops.length-1){
      /* final stop: stay here — the tour ends, 「下一站」 restarts it */
      tour.phase='done';
      tourNoEl.textContent='自动游览 · '+tourStops.length+' / '+tourStops.length+' · 已结束';
      tourFillEl.style.width='100%';
      return true;
    }
    tourGoTo(tour.idx+1,nowMs); return true;
  }
  /* item 4: a very slow push-and-pull during the dwell — the camera
     eases 0.55 m toward the subject and back over the whole dwell,
     instead of a one-way drift that never returns. */
  camera.position.copy(s.cam).addScaledVector(tour.drift,Math.sin(dk*Math.PI));
  controls.target.copy(s.tgt);
  return true;
}

export function initTour(){
  tourPauseBtn.addEventListener('click',function(){ setTourPaused(!tour.paused); });
  tourFoldBtn.addEventListener('click',function(){ setTourFolded(!tourHud.classList.contains('folded')); });
  document.getElementById('tourPrev').addEventListener('click',function(){ tourJump(tour.idx-1); });
  document.getElementById('tourNext').addEventListener('click',function(){ tourJump(tour.idx+1); });
  document.getElementById('tourExit').addEventListener('click',function(){ setMode('exterior'); });
  window.addEventListener('keydown',function(e){
    if(mode==='tour'){
      if(e.key===' '){ e.preventDefault(); setTourPaused(!tour.paused); }
      if(e.key==='Escape') setMode('exterior');
    }else if(mode==='walk'&&e.key==='Escape'){ setMode('exterior'); }
  });
}
