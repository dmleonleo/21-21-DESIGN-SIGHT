// labels.js — exhibit catalogue, 3D signage sprites, label visibility.
// Split from the single inline script of docs/index.html
// (merged14: #9-#14 serial chain + round-2 review fixes).
// Behaviour unchanged: only the module boundary is new.
import * as THREE from 'three';
import { canvasTexture, scene } from './scene.js';
import { mode } from './camera.js';

/* Shared level constants: basement floor y=-4.8, eye height 1.62 m.
   They live here (not in scene.js) because the exhibit catalogue below
   needs EYE_Y while this module is being evaluated, and scene.js is
   still mid-evaluation at that point (circular import); scene.js and
   walk.js import them from here instead. */
export const FLOOR_Y = -4.8, EYE = 1.62, EYE_Y = FLOOR_Y + EYE;
export const labelSprites=[];
export const labelState = { on: true };
export function applyLabels(){
  var vis=(typeof mode!=='undefined'&&mode!=='exterior')&&labelState.on&&!document.body.classList.contains('ui-hidden');
  labelSprites.forEach(function(sp){ sp.visible=vis; });
}
export function labelSprite(text,x,y,z,dark){
  var tex=canvasTexture(512,104,function(ctx,w,h){
    /* Fukasawa-quiet signage: no board, no colour block — just small
       lettering with a hairline beneath, like the museum's own
       captions. Legibility comes from ONE tight shade (1px offset,
       2px blur), never a blurred light halo — the halo is what made
       the lettering look lit up. White ink for the dark basement
       rooms; dark ink for the bright white G3 room (dark=true),
       where white lettering would vanish against the white ceiling. */
    ctx.font='300 33px "Noto Sans SC","Noto Sans JP","Hiragino Kaku Gothic ProN","PingFang SC","Microsoft YaHei",sans-serif';
    ctx.shadowColor=dark?'rgba(255,255,255,0.55)':'rgba(5,7,5,0.55)'; ctx.shadowBlur=2; ctx.shadowOffsetY=1;
    ctx.fillStyle=dark?'rgba(28,28,30,0.95)':'rgba(255,255,255,0.96)';
    ctx.fillText(text,4,42);
    ctx.shadowBlur=0; ctx.shadowOffsetY=0;
    ctx.fillStyle=dark?'rgba(28,28,30,0.55)':'rgba(255,255,255,0.55)'; ctx.fillRect(5,60,110,2);
  });
  var sp=new THREE.Sprite(new THREE.SpriteMaterial({map:tex,transparent:true,depthTest:true,opacity:0.96}));
  sp.scale.set(2.7,0.55,1); sp.position.set(x,y,z); sp.renderOrder=5; sp.visible=false; scene.add(sp); labelSprites.push(sp); return sp;
}
/* ================= Exhibits ================= */
export const exhibits=[
  {key:'01',no:'EXHIBIT 01',title:'一块布 · A-POC 织物',
   desc:'三宅一生的 A-POC：一块布经织造直接成衣，几乎不产生裁剪废料。这件悬垂的红色织物正是整栋建筑的灵感——博物馆翼屋顶那张 54 米折叠钢板，就是「一块布」的建筑版本。',
   focus:new THREE.Vector3(32,-2.8,-9.5), stand:new THREE.Vector3(32,EYE_Y,-6.4)},
  {key:'02',no:'EXHIBIT 02',title:'光的织物 · 吊灯群',
   desc:'七盏球形灯以织物经纬般的节奏垂落。21_21 的地下展厅大量依靠下沉庭院与天窗引入自然光，人工光只作补充——光线本身就是展品，也是这栋地下建筑真正的「立面」。',
   focus:new THREE.Vector3(35,-1.9,-7.0), stand:new THREE.Vector3(31.6,EYE_Y,-7.0)},
  {key:'03',no:'EXHIBIT 03',title:'坐的设计 · 三把椅子',
   desc:'三把椅子并排放在 Gallery 2 的柱列之间，材料与结构各不相同。深泽直人说设计是「不用意识到的行为」——坐下这个动作，就是最好的检验。',
   focus:new THREE.Vector3(42,-4.0,-8.2), stand:new THREE.Vector3(42,EYE_Y,-5.6)},
  {key:'04',no:'EXHIBIT 04',title:'字与形 · 平面设计墙',
   desc:'佐藤卓负责本馆的视觉识别：黑、白、红与粗壮的无衬线字。平面设计在这里不是海报，而是建筑的一部分——标识、导视与展墙共同决定了参观者如何读懂这座馆。',
   focus:new THREE.Vector3(38,-2.9,-15.8), stand:new THREE.Vector3(38,EYE_Y,-12.8)},
  {key:'05',no:'EXHIBIT 05',title:'器物 · 陶罐',
   desc:'拉坯成型的曲线没有一处多余：口、肩、腹、足都是手与重力的谈判结果。21_21 常把最日常的器物放上展台——设计不在远方，就在每天端起的那只杯子里。',
   focus:new THREE.Vector3(46,-3.9,-10.0), stand:new THREE.Vector3(46,EYE_Y,-7.6)},
  {key:'06',no:'EXHIBIT 06',title:'转动的圆 · 中央装置',
   desc:'圆环在 Gallery 2 中央缓慢旋转——圆是这栋三角建筑里唯一的曲线。它提醒参观者：理性（钢板、混凝土、三角）与感性（光、织物、圆）从来不是对立面，而是同一块布的正反两面。',
   focus:new THREE.Vector3(36,-2.7,-2.5), stand:new THREE.Vector3(39.6,EYE_Y,-2.5)},
  {key:'07',no:'EXHIBIT 07',title:'Akari 纸灯 · 野口勇',
   desc:'野口勇的 Akari：和纸与竹篾撑起一团暖光，1951 年起就是「带回家的雕塑」。它立在 Gallery 2 最东端、地下层轮廓延到 x=52 的尽头——最现代的展厅深处，放着最接近手作温度的一盏灯。',
   focus:new THREE.Vector3(48,-3.8,-4.5), stand:new THREE.Vector3(45.2,EYE_Y,-4.5)},
  {key:'08',no:'EXHIBIT 08',title:'急须与茶杯 · 茶具一组',
   desc:'矮桌上一把急须、两只茶杯：注水、浸泡、出汤，动作被器物的形状一一规定好。日本的日常设计常藏在这种分寸里——壶嘴的角度、杯口的厚薄，都是用手思考的结果。',
   focus:new THREE.Vector3(47,-4.2,-13.5), stand:new THREE.Vector3(44.2,EYE_Y,-13.5)},
  {key:'09',no:'EXHIBIT 09',title:'暖帘 · 蓝染门帘',
   desc:'两幅蓝染暖帘挂在 Gallery 1 与 Gallery 2 之间的门洞上，白色的圆纹家纹在靛蓝布面上。暖帘既是隔断也是邀请：布一掀开，就是另一个展厅——它标出的正是两间展厅的分界线。',
   focus:new THREE.Vector3(29.5,-3.3,1.0), stand:new THREE.Vector3(28.0,EYE_Y,-2.0)},
  {key:'10',no:'EXHIBIT 10',title:'漆器便当盒 · 重箱',
   desc:'黑漆与朱漆两层重箱叠在 Gallery 1 的矮桌上，旁边一双竹筷。漆器是日本器物里最「慢」的工艺：一层一层上漆、阴干、打磨，时间本身成了材料的一部分。',
   focus:new THREE.Vector3(15,-4.3,3.5), stand:new THREE.Vector3(15,EYE_Y,5.9)},
  {key:'11',no:'EXHIBIT 11',title:'竹篮 · 编织容器',
   desc:'一只竹编篮立在 Gallery 2 中央的展台上：篾条的经纬既是结构也是图案。和 A-POC 的「一块布」一样，编织是把一根连续的材料变成容器的技术——只不过这里的材料来自竹林。',
   focus:new THREE.Vector3(28,-4.4,-4.0), stand:new THREE.Vector3(28,EYE_Y,-1.2)},
  {key:'12',no:'EXHIBIT 12',title:'茶碗与茶筅 · 一服茶',
   desc:'楼梯底旁的木托盘上，一只茶碗、一柄茶筅，碗里是抹茶的绿。下到地下层先遇见它，像主人递来的一服茶：参观这座地下美术馆，从最安静的日常开始。',
   focus:new THREE.Vector3(6,-4.15,5.5), stand:new THREE.Vector3(3.4,EYE_Y,5.5)}
];
