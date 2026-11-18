// tour.js — the 14-stop automatic tour (route, pacing, progress, controls).
// Split from the single inline script of docs/index.html (main @62eeaac6).
// Behaviour unchanged: only the module boundary is new.
import * as THREE from 'three';
import { camera, controls } from './scene.js';
import { mode, exteriorCamPos, EXT_TARGET, setMode, camAnimBox } from './camera.js';

/* ================= Auto tour =================
   A fixed cinematic route through the whole building, reusing the same
   verified camera positions as the lobby / G3 / gallery / walk modes:
   aerial -> facade -> courtyard -> lobby -> 30-step stair -> Gallery 1 ->
   Gallery 2 overview -> exhibits 01/02 -> 06 -> 05 -> sunken courtyard ->
   up and over the lawn -> Gallery 3 (west wing) -> closing aerial.
   Each leg flies smoothly to the stop, then dwells there (with a slow
   push-in) while its narration card is shown, then moves on. The visitor
   can pause, jump to the previous / next stop, tap a progress segment to
   jump, or exit at any time; picking any other mode also ends the tour. */
var tourStops=[
  {title:'鸟瞰开场 · 两栋建筑',dwell:3400,
   desc:'先从空中看全貌：东侧是博物馆翼，一整张 54 米长的钢板折成屋顶；西侧较小的咖啡翼是 Gallery 3 所在。约八成空间藏在地下，草坪上只露出折叠的屋顶。',
   cam:new THREE.Vector3(10,26,-66), tgt:new THREE.Vector3(4,0,-2)},
  {title:'正面 · 玻璃立面',dwell:3400,
   desc:'博物馆翼的南立面几乎全是玻璃，清水混凝土墙与折叠钢板屋顶在这里交汇。透过玻璃能隐约看到入口大堂——游览的下一站就在里面。',
   cam:new THREE.Vector3(20,5.5,-36), tgt:new THREE.Vector3(19,2,-3)},
  {title:'两栋之间 · 铺地庭院',dwell:3200,
   desc:'两栋建筑之间的铺地庭院是地面的交通核：向东进博物馆翼大堂，穿过庭院向西，就是 Gallery 3 的入口。',
   cam:new THREE.Vector3(-13,3.4,-20), tgt:new THREE.Vector3(-5,1.2,1)},
  {title:'入口大堂 · 接待台与电梯',dwell:3400,
   desc:'大堂在博物馆翼地面层：接待台立在实心楼板上，西南角是梯形平面的电梯。展厅在地下——接下来走楼梯下去。',
   cam:new THREE.Vector3(-1.15,1.85,1.15), tgt:new THREE.Vector3(0.9,0.6,-5.5)},
  {title:'30 级楼梯 · 下到地下层',dwell:3000,
   desc:'楼梯共 30 级、每级高 0.16 米，北侧是混凝土栏板、南侧是玻璃栏杆。顺着它下行 4.8 米，就到了地下展厅层。',
   cam:new THREE.Vector3(0.5,1.62,3.9), tgt:new THREE.Vector3(8.8,-2.8,4.0)},
  {title:'Gallery 1 · 天窗斜板厅',dwell:3400,
   desc:'Gallery 1 约 132 m²，梯形平面，靠 6 块斜向半透明板把天光引进来，白色天花下有一扇深色方窗。这里是地下层最明亮的房间。',
   cam:new THREE.Vector3(14,-1.7,5.8), tgt:new THREE.Vector3(28,-3.4,3.8)},
  {title:'Gallery 2 · 全景（地下层已放大）',dwell:3400,
   desc:'Gallery 2 层高 4.8 米，是全馆最大的展厅。地下层按官方总楼面放大到约 1,336 m²，轮廓向东一直延到 x=52；0.55 米方柱成列排开，沿柱线有一条连续天窗缝。空间做大后展品也翻倍——全馆共 12 件：01–08 与 11 在这间东侧大厅里，09 暖帘挂在两厅之间，10 在 Gallery 1，12 在楼梯底旁。',
   cam:new THREE.Vector3(27,-0.7,-14.8), tgt:new THREE.Vector3(46,-3.9,-2.5)},
  {title:'展品 01 · 一块布 / 02 · 光的织物',dwell:3800,
   desc:'01《一块布 · A-POC 织物》：一块布直接织造成衣，正是折叠钢板屋顶的灵感来源。02《光的织物》：七盏球形吊灯如经纬般垂落——地下展厅里，光本身就是展品。',
   cam:new THREE.Vector3(31,-3.18,-5.2), tgt:new THREE.Vector3(34,-2.4,-8.6)},
  {title:'展品 06 · 转动的圆',dwell:3600,
   desc:'Gallery 2 中央，圆环装置在缓慢旋转——圆是这栋三角建筑里唯一的曲线。旁边的展带上还有 03《坐的设计》三把椅子与南墙上的 04《字与形》平面设计墙。',
   cam:new THREE.Vector3(39.6,-3.18,-2.5), tgt:new THREE.Vector3(36,-2.7,-2.5)},
  {title:'展品 05 · 器物（展厅深处）',dwell:3400,
   desc:'走到展厅东侧深处，是 05《器物 · 陶罐》：拉坯的曲线没有一处多余。再往东到尽头，是 07《Akari 纸灯》的暖光。21_21 常把最日常的器物放上展台——设计就在每天端起的那只杯子里。',
   cam:new THREE.Vector3(43,-3.18,-7.6), tgt:new THREE.Vector3(46,-3.9,-10.0)},
  {title:'下沉庭院 · 露天深坑',dwell:3400,
   desc:'三角形下沉庭院是一个真正的露天坑，坑底就是地下层地面。庭院和中庭把阳光送进地下展厅——这是这栋地下建筑真正的「立面」。站在 Gallery 2 里，隔着整面玻璃正对坑底。',
   cam:new THREE.Vector3(11,-1.0,-3.5), tgt:new THREE.Vector3(17.5,-4.6,0.8)},
  {title:'前往西翼 · 越过草坪',dwell:1400,
   desc:'地下参观到此结束。镜头升上草坪上空，越过下沉庭院，飞往西侧咖啡翼——Gallery 3 在那里。',
   cam:new THREE.Vector3(-2,16,-24), tgt:new THREE.Vector3(-20,1,1)},
  {title:'Gallery 3 · 西翼展厅',dwell:4000,
   desc:'Gallery 3 在西翼（原咖啡厅，2017 年改建），不在博物馆翼：四边形展厅约 111.7 m²，深灰花岗岩地面，白色石膏斜顶最高 4.26 米，北墙有窗缝与磨砂玻璃带，南侧整面玻璃外是 57 m² 露台。',
   cam:new THREE.Vector3(-20.5,1.55,-1.8), tgt:new THREE.Vector3(-28,1.2,2.8)},
  {title:'收尾 · 回到鸟瞰',dwell:5200,
   desc:'游览结束：从空中再看一次两栋建筑——一块布折成的屋顶、藏在地下的展厅、引光的庭院。想自己走走，可以点「进入展厅 · 步行参观」；想再看一遍，点「下一站」会从头开始。',
   cam:new THREE.Vector3(4,46,-54), tgt:new THREE.Vector3(4,0,-2)}
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
var tour={idx:0,phase:'travel',start:0,travelDur:3000,dwellDur:3400,
  fromPos:new THREE.Vector3(),fromTgt:new THREE.Vector3(),
  paused:false,pauseAt:0,drift:new THREE.Vector3()};
function tourEase(k){ return k<0.5 ? 4*k*k*k : 1-Math.pow(-2*k+2,3)/2; }
function tourShowCard(){
  var s=tourStops[tour.idx];
  tourNoEl.textContent='自动游览 · '+(tour.idx+1)+' / '+tourStops.length+(tour.paused?' · 已暂停':'');
  tourTitleEl.textContent=s.title;
  tourDescEl.textContent=s.desc;
  tourFillEl.style.width=((tour.idx)/tourStops.length*100)+'%';
  tourDots.forEach(function(b,i){
    b.className=i<tour.idx?'done':(i===tour.idx?'now':'');
  });
}
function tourGoTo(idx,nowMs){
  tour.idx=(idx+tourStops.length)%tourStops.length;
  var s=tourStops[tour.idx];
  tour.fromPos.copy(camera.position);
  tour.fromTgt.copy(controls.target);
  var dist=tour.fromPos.distanceTo(s.cam);
  tour.travelDur=Math.max(2600,Math.min(6800,dist*150));
  tour.dwellDur=s.dwell||3400;
  tour.phase='travel';
  tour.start=nowMs;
  tour.paused=false; tourPauseBtn.textContent='暂停';
  tourShowCard();
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
  camera.position.copy(s.cam).addScaledVector(tour.drift,dk);
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
    if(mode!=='tour') return;
    if(e.key===' '){ e.preventDefault(); setTourPaused(!tour.paused); }
    if(e.key==='Escape') setMode('exterior');
  });
}
