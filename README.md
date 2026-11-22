# 21_21 DESIGN SIGHT · 线上体验

安藤忠雄设计的 21_21 DESIGN SIGHT（东京中城，2007）三维线上体验。
在线地址：https://dmleonleo.github.io/21-21-DESIGN-SIGHT/

这一版完全替换了旧程序（Blender v16–v21 脚本和旧网页）。模型、网页都是重新做的。

## 体验
- **鸟瞰**：拖动旋转、滚轮缩放，看整个建筑和庭园。
- **导览**：10 个站点，从庭园、广场、主入口、大厅、楼梯到 B1 的 Gallery 1、2、下沉庭院、东侧尖角和 Gallery 3。拖动可以环顾。
- **漫游**：WASD / 方向键行走，Shift 快走，拖动转头；手机用左下摇杆。有碰撞和上下楼梯。点小地图可以直接跳过去。
- **时间**：右下滑块按东京的太阳位置改变光照（6:00–18:30）。
- 小地图会按所在楼层切换 1F / B1 平面。

## 模型（v3）
- 来源：一份 SketchUp 模型（21_21+DS+CORREGIDO，作者不详）重新拼装，按 PLATEAU 港区 2025 建筑轮廓（CC BY 4.0）缩放校正（rms 0.25 m）。
- 高度按官方数据：屋顶最高 4.8 m，B1 地面 −6.0 m，G1 天花 5.0 m。
- 细节按官方资料和照片逐项校对：清水混凝土 1800×900 模板与 6 个对拉孔、钢板屋顶、主入口、自由矮墙与扶手、西高东低约 0.6 m 的地面坡度、东侧磨砂玻璃护栏、白色天花与 B1 灯光。
- 推断值在 `tools/model-v3/` 脚本里都有注明。
- 网页模型 `docs/model/2121.glb`（约 320 KB，meshopt 压缩，webp 贴图）。

坐标：X 东、Y 北、Z 上（米），原点 35.6674N 139.7301E，GL = 0（T.P. 27.05）。GLB 为 Y 向上。

## 开发
```
npm install
npm run build    # src/main.js -> docs/js/app.js（three.js 打包进来，不依赖 CDN）
npm run serve    # http://localhost:8000
```
GitHub Pages 从 `main` 分支的 `docs/` 发布。`docs/` 里的文件不能用 Git LFS。

## 资料
2121designsight.jp 建筑介绍；PLATEAU 港区（CC BY 4.0）；Wikimedia Commons 照片（CC BY / BY-SA）；日经 xTECH；新建築 2007 年 5 月号；ディテール 2007 年 10 月号。官方图片仅作参考，不在仓库里分发。
