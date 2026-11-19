// ui.js — exhibit card, Gallery 3 viewpoints, sidebar, labels toggle,
// hide-all, intro, drawer handles.
// Split from the single inline script of docs/index.html
// (merged14: #9-#14 serial chain + round-2 review fixes).
// Behaviour unchanged: only the module boundary is new.
import * as THREE from 'three';
import { renderer } from './scene.js';
import { mode, flyTo, setMode, syncHash } from './camera.js';
import { goNearExhibit } from './walk.js';
import { exhibits, applyLabels, labelState } from './labels.js';
import { setTourFolded } from './tour.js';

/* ================= Modes & views ================= */
var exhibitCard=document.getElementById('exhibitCard');
var caption=document.getElementById('caption');
export let captionDismissed = false;
/* ---- #6.1 first entry only ----
   The two-line introduction (brand p) + the prologue card show on
   first entry and collapse 9 s after the visitor can actually see
   them (i.e. after the opening), or on the first interaction —
   whichever comes first. Returning visitors start collapsed;
   tapping the title re-opens the introduction. */
var introSeen=false;
try{ introSeen=window.localStorage&&localStorage.getItem('2121-intro-seen')==='1'; }catch(e){ introSeen=false; }
var introTimer=null;
function endIntro(){
  if(introTimer){ clearTimeout(introTimer); introTimer=null; }
  if(document.body.classList.contains('intro-done')) return;
  document.body.classList.add('intro-done');
  captionDismissed=true; caption.style.display='none';
  try{ if(window.localStorage) localStorage.setItem('2121-intro-seen','1'); }catch(e){}
}
export function armIntro(){
  if(introSeen){ document.body.classList.add('intro-done'); captionDismissed=true; caption.style.display='none'; return; }
  if(introTimer) return;
  introTimer=setTimeout(endIntro,9000);
  renderer.domElement.addEventListener('pointerdown',function(){ endIntro(); },{once:true});
}
function toggleIntro(){
  var done=document.body.classList.toggle('intro-done');
  captionDismissed=done;
  caption.style.display=(done||mode!=='exterior')?'none':'block';
  try{ if(window.localStorage) localStorage.setItem('2121-intro-seen',done?'1':'0'); }catch(e){}
  if(!done&&!introTimer) introTimer=setTimeout(endIntro,9000);
}
/* ---- #6.4 the vertical margin text: hidden except at chapter
   transitions (mode changes, tour stops) and during the opening ---- */
export const verticalEl = document.getElementById('vertical');
var verticalTimer=null;
export function flashVertical(){
  if(!verticalEl||window.innerWidth<=760) return;
  if(document.body.classList.contains('ui-hidden')) return;
  verticalEl.classList.add('on');
  if(verticalTimer) clearTimeout(verticalTimer);
  verticalTimer=setTimeout(function(){ verticalEl.classList.remove('on'); },2400);
}
var walkTip=document.getElementById('walkTip');
/* ---- #6.7 walk tip, wording follows the controls that exist ----
   Desktop: WASD / direction keys. Mobile: tap-to-move once #5's
   click-to-move layer is present (probed via its __2121 handle),
   the direction pad before that. */
export function updateWalkTip(){
  var coarse=false;
  try{ coarse=window.matchMedia('(pointer: coarse)').matches; }catch(e){}
  var tapMove=(typeof window.__2121!=='undefined');
  if(!coarse){
    walkTip.textContent='W A S D 或左下按钮移动 · 拖动画面转头 · 楼梯口可上下层 · 穿暖帘门洞去 Gallery 2 · 下沉庭院隔着玻璃看 · 过庭院去西翼 Gallery 3';
  }else if(tapMove){
    walkTip.textContent='点按地面走过去 · 拖动画面转头 · 楼梯口可上下层 · 穿暖帘门洞去 Gallery 2 · 下沉庭院隔着玻璃看 · 过庭院去西翼 Gallery 3';
  }else{
    walkTip.textContent='左下按钮移动 · 拖动画面转头 · 楼梯口可上下层 · 穿暖帘门洞去 Gallery 2 · 下沉庭院隔着玻璃看 · 过庭院去西翼 Gallery 3';
  }
}
/* Gallery 3 (v15: west / former cafe wing, ground floor) guided viewpoints */
export const g3Spots=[
  {no:'G3 · 1 / 4',title:'Gallery 3 · 全景与斜顶',
   desc:'Gallery 3 在西翼（原咖啡翼，2017 年改建）——不在博物馆翼。从展厅南侧望向东端：四边形展厅约 111.7 m²，地面是深灰花岗岩，白色石膏斜顶顺着折叠钢板屋顶倾斜，最高 4.26 米；南侧整面玻璃外是 57 m² 的露台，东端是 Private Room 与 Kitchen 的隔墙。（旧机位贴在西端方柱与斜顶之间，画面被柱子挡住一半、顶部露出屋顶与吊顶之间的黑色楔形缝，现已移到南侧开阔处，楔形缝不在框内。）',
   cam:new THREE.Vector3(-24,1.6,4.2), tgt:new THREE.Vector3(-13,0.8,-2.0)},
  {no:'G3 · 2 / 4',title:'Gallery 3 · 白石膏斜顶与轨道灯',
   desc:'白色石膏斜天花顺着折叠钢板屋顶的内侧倾斜，最高点 4.26 米。一条黑色轨道带 5 盏射灯贯穿展厅，筒灯与北墙上方的暖色灯槽补充照明——和地下展厅靠天窗采光不同，这里是完整的地上层光环境。',
   cam:new THREE.Vector3(-19,1.5,-1.4), tgt:new THREE.Vector3(-28,2.7,2.4)},
  {no:'G3 · 3 / 4',title:'Gallery 3 · Private Room 与 Kitchen',
   desc:'展厅东端隔出 Private Room（4.0 × 2.9 米）与 Kitchen，旁边是 2 个 WC。2 根方柱与 1 根圆柱支撑斜顶：方柱一根在展厅中部、一根靠东，圆柱贴近南侧玻璃。',
   cam:new THREE.Vector3(-21.5,1.55,-1.6), tgt:new THREE.Vector3(-13.2,1.15,2.9)},
  {no:'G3 · 4 / 4',title:'Gallery 3 · 北墙开口与南侧露台',
   desc:'北墙上有真实开口：西段是窗，东段是磨砂玻璃槽，光线柔和地漫进来。南侧整面玻璃外是 57 m² 的铺地露台，正对草坪与下沉庭院方向。',
   cam:new THREE.Vector3(-19,1.6,3.8), tgt:new THREE.Vector3(-25.5,0.9,-3.4)}
];
export let g3Idx = 0;
export function showG3Spot(i){
  g3Idx=(i+g3Spots.length)%g3Spots.length;
  var s=g3Spots[g3Idx];
  var ghG3=document.getElementById('exGhost'); if(ghG3) ghG3.textContent='G3';
  document.getElementById('exNo').textContent=s.no;
  document.getElementById('exTitle').textContent=s.title;
  document.getElementById('exDesc').textContent=s.desc;
  document.getElementById('exGo').textContent='飞到这个位置';
  exhibitCard.classList.add('show'); setExFolded(true);
  syncHash();
}
var labelToggleBtn=document.getElementById('labelToggle');
var uiToggleBtn=document.getElementById('uiToggle');
function toggleUi(){
  var hidden=document.body.classList.toggle('ui-hidden');
  uiToggleBtn.textContent=hidden?'显示':'隐藏';
  applyLabels();
}
/* ================= Exhibit selection ================= */
export let currentEx = null;
export function showExhibit(ex){
  currentEx=ex;
  var ghEl=document.getElementById('exGhost'); if(ghEl) ghEl.textContent=ex.key;
  setExFolded(true);
  document.getElementById('exGo').textContent='走到这件展品前';
  document.getElementById('exNo').textContent=ex.no+' / 共 '+exhibits.length+' 件';
  document.getElementById('exTitle').textContent=ex.title;
  document.getElementById('exDesc').textContent=ex.desc;
  exhibitCard.classList.add('show');
  syncHash();
}
function stepExhibit(dir){
  var i=currentEx?exhibits.indexOf(currentEx):0;
  i=(i+dir+exhibits.length)%exhibits.length;
  showExhibit(exhibits[i]); goNearExhibit(exhibits[i]);
}

var exFoldBtn=document.getElementById('exFold');
const tourHud = document.getElementById('tourHud');
export function setExFolded(f){
  exhibitCard.classList.toggle('folded',f);
  exFoldBtn.textContent=f?'展开说明':'收起说明';
  exFoldBtn.setAttribute('aria-expanded',f?'false':'true');
}
/* ---- #6.5 bottom-drawer handle + swipe-down to fold (mobile) ---- */
function addDrawerSwipe(el,foldFn){
  var sy=null;
  el.addEventListener('touchstart',function(e){ if(e.target.closest('button')) return; sy=e.touches[0].clientY; },{passive:true});
  el.addEventListener('touchend',function(e){
    if(sy===null) return;
    var dy=e.changedTouches[0].clientY-sy; sy=null;
    if(dy>50) foldFn();
  },{passive:true});
}

export function initUi(){
  document.getElementById('captionHide').addEventListener('click',function(){ captionDismissed=true; caption.style.display='none'; });
  var brandEl=document.querySelector('.brand');
  if(brandEl){
    brandEl.setAttribute('tabindex','0');
    brandEl.addEventListener('click',toggleIntro);
    brandEl.addEventListener('keydown',function(e){ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); toggleIntro(); } });
  }
  updateWalkTip();
  document.getElementById('sideToggle').addEventListener('click',function(){
    var s=document.getElementById('side');
    if(window.innerWidth<=760){ s.classList.remove('closed'); s.classList.toggle('open'); }
    else{ s.classList.toggle('closed'); }
  });
  document.getElementById('sideHide').addEventListener('click',function(){
    var s=document.getElementById('side'); s.classList.remove('open'); s.classList.add('closed');
  });
  labelToggleBtn.addEventListener('click',function(){
    labelState.on=!labelState.on;
    labelToggleBtn.setAttribute('aria-pressed',labelState.on?'true':'false');
    applyLabels();
  });
  uiToggleBtn.addEventListener('click',toggleUi);
  window.addEventListener('keydown',function(e){
    if(e.key&&e.key.toLowerCase()==='h'&&!e.metaKey&&!e.ctrlKey&&!e.altKey) toggleUi();
  });
  document.getElementById('walkExit').addEventListener('click',function(){ setMode('exterior'); });
  exFoldBtn.addEventListener('click',function(){ setExFolded(!exhibitCard.classList.contains('folded')); });
  document.getElementById('exHide').addEventListener('click',function(){ exhibitCard.classList.remove('show'); });
  document.getElementById('exPrev').addEventListener('click',function(){
    if(mode==='g3'){ showG3Spot(g3Idx-1); var s=g3Spots[g3Idx]; flyTo(s.cam,s.tgt,1200); } else stepExhibit(-1);
  });
  document.getElementById('exNext').addEventListener('click',function(){
    if(mode==='g3'){ showG3Spot(g3Idx+1); var s=g3Spots[g3Idx]; flyTo(s.cam,s.tgt,1200); } else stepExhibit(1);
  });
  document.getElementById('exGo').addEventListener('click',function(){
    if(mode==='g3'){ var s=g3Spots[g3Idx]; flyTo(s.cam,s.tgt,1200); }
    else if(currentEx) goNearExhibit(currentEx);
  });
  document.querySelectorAll('.drawerHandle').forEach(function(h){
    h.addEventListener('click',function(){
      var card=h.parentElement;
      if(card.id==='exhibitCard') setExFolded(!exhibitCard.classList.contains('folded'));
      else if(card.id==='tourHud') setTourFolded(!tourHud.classList.contains('folded'));
    });
  });
  addDrawerSwipe(exhibitCard,function(){ setExFolded(true); });
  addDrawerSwipe(tourHud,function(){ setTourFolded(true); });
}
