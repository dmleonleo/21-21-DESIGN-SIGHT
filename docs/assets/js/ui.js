// ui.js — exhibit card, Gallery 3 viewpoints, sidebar, labels toggle, hide-all.
// Split from the single inline script of docs/index.html (main @62eeaac6).
// Behaviour unchanged: only the module boundary is new.
import * as THREE from 'three';
import { mode, flyTo, setMode } from './camera.js';
import { goNearExhibit } from './walk.js';
import { exhibits, applyLabels, labelState } from './labels.js';

/* ================= Modes & views ================= */
var exhibitCard=document.getElementById('exhibitCard');
var caption=document.getElementById('caption');
export let captionDismissed = false;
/* Gallery 3 (v15: west / former cafe wing, ground floor) guided viewpoints */
export const g3Spots=[
  {no:'G3 · 1 / 4',title:'Gallery 3 · 全景与三角接待台',
   desc:'Gallery 3 在西翼（原咖啡翼，2017 年改建）——不在博物馆翼。从展厅西端望向东端，看清整个四边形展厅：北边长 15.0 米、深 8.0 米，约 111.7 m²，地面是深灰花岗岩；东端入口处两张三角形接待台（每张宽 1.73 米）与北墙平行。（旧机位贴在东端斜顶与 Private Room 隔墙之间，画面被墙面填满，现已移到西端开阔处。）',
   cam:new THREE.Vector3(-31.5,1.7,4.6), tgt:new THREE.Vector3(-16,0.9,0.5)},
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
}
function stepExhibit(dir){
  var i=currentEx?exhibits.indexOf(currentEx):0;
  i=(i+dir+exhibits.length)%exhibits.length;
  showExhibit(exhibits[i]); goNearExhibit(exhibits[i]);
}

var exFoldBtn=document.getElementById('exFold');
function setExFolded(f){
  exhibitCard.classList.toggle('folded',f);
  exFoldBtn.textContent=f?'展开说明':'收起说明';
  exFoldBtn.setAttribute('aria-expanded',f?'false':'true');
}

export function initUi(){
  document.getElementById('captionHide').addEventListener('click',function(){ captionDismissed=true; caption.style.display='none'; });
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
}
