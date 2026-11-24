// The city around the garden: PLATEAU Minato City LOD buildings (CC BY 4.0) as plain dark volumes,
// plus a ground that runs to the horizon. Kept quiet on purpose: no windows, no colour,
// and every volume dissolves into the haze as it rises, so the low city grounds the building and the towers stay back.
import * as THREE from 'three';
import * as BufferGeometryUtils from 'three/addons/utils/BufferGeometryUtils.js';

const SINK = 14;   // walls run this far below their PLATEAU base, so no volume floats where the ground is simplified

export function buildContext(scene, rows) {
  const pos = [], idx = [];
  for (const r of rows) {
    const base = r[0], h = r[1], pts = [];
    for (let k = 2; k < r.length; k += 2) pts.push(new THREE.Vector2(r[k], r[k + 1]));
    if (THREE.ShapeUtils.isClockWise(pts)) pts.reverse();
    const n = pts.length, y0 = base - SINK, y1 = base + h;
    // walls: model X east, Y north -> three x = X, z = -Y
    for (let i = 0; i < n; i++) {
      const a = pts[i], b = pts[(i + 1) % n], o = pos.length / 3;
      pos.push(a.x, y0, -a.y, b.x, y0, -b.y, b.x, y1, -b.y, a.x, y1, -a.y);
      idx.push(o, o + 1, o + 2, o, o + 2, o + 3);
    }
    // roof
    const o = pos.length / 3;
    for (const p of pts) pos.push(p.x, y1, -p.y);
    for (const t of THREE.ShapeUtils.triangulateShape(pts, [])) idx.push(o + t[0], o + t[2], o + t[1]);
  }
  let geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  geo.setIndex(idx);
  geo = geo.toNonIndexed(); geo.computeVertexNormals();
  const mat = new THREE.MeshStandardMaterial({ color: 0x24272a, roughness: 0.96, metalness: 0 });
  mat.onBeforeCompile = (s) => {
    s.vertexShader = s.vertexShader.replace('#include <common>', '#include <common>\nvarying float vWY;')
      .replace('#include <fog_vertex>', '#include <fog_vertex>\nvWY = (modelMatrix * vec4(transformed, 1.0)).y;');
    s.fragmentShader = s.fragmentShader.replace('#include <common>', '#include <common>\nvarying float vWY;')
      .replace('#include <fog_fragment>', `#ifdef USE_FOG
        float fogDepth2 = vFogDepth;
        float ff = smoothstep(fogNear, fogFar, fogDepth2);
        ff = max(ff, 0.42 + 0.5 * smoothstep(10.0, 140.0, vWY));     // always a little behind the haze; towers rise into it
        ff = max(ff, 0.85 * (1.0 - smoothstep(18.0, 70.0, fogDepth2)));   // a volume right in front of the camera steps back too
        gl_FragColor.rgb = mix(gl_FragColor.rgb, fogColor, ff);
      #endif`);
  };
  const mesh = new THREE.Mesh(geo, mat);
  mesh.name = 'CONTEXT_plateau'; mesh.receiveShadow = true; mesh.castShadow = false; mesh.matrixAutoUpdate = false;
  scene.add(mesh);
  return mesh;
}

// The far ground: a large flat sheet under the fitted garden ground. Lawn near the building,
// fading through a soft, irregular edge into the dark paving of the city, then into haze.
export function buildFarGround(scene) {
  const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1 });
  mat.onBeforeCompile = (s) => groundShader(s, true);
  const g = new THREE.Mesh(new THREE.PlaneGeometry(9000, 9000, 1, 1).rotateX(-Math.PI / 2), mat);
  g.position.y = -0.62; g.receiveShadow = true; g.name = 'GROUND_far';
  scene.add(g);
  return g;
}

// Shared by the fitted garden ground and the far sheet: colour by distance from the garden, with low-frequency noise.
export function groundShader(s) {
  s.vertexShader = s.vertexShader.replace('#include <common>', '#include <common>\nvarying vec2 vGP;')
    .replace('#include <fog_vertex>', '#include <fog_vertex>\nvec4 gw = modelMatrix * vec4(transformed, 1.0); vGP = vec2(gw.x, -gw.z);');
  s.fragmentShader = s.fragmentShader.replace('#include <common>', `#include <common>
    varying vec2 vGP;
    float h2(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
    float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
      return mix(mix(h2(i), h2(i + vec2(1, 0)), f.x), mix(h2(i + vec2(0, 1)), h2(i + vec2(1, 1)), f.x), f.y); }`)
    .replace('vec4 diffuseColor = vec4( diffuse, opacity );', `
      // garden: an ellipse around the site (Midtown garden runs west and north), edge broken by noise
      vec2 q = (vGP - vec2(22.0, 18.0)) / vec2(120.0, 78.0);
      float n = vn(vGP * 0.025) * 0.6 + vn(vGP * 0.09) * 0.4;
      float lawnK = 1.0 - smoothstep(0.75, 1.15, length(q) + (n - 0.5) * 0.35);
      vec3 lawn = vec3(0.105, 0.135, 0.085) * (0.9 + 0.2 * vn(vGP * 0.3));
      vec3 pave = vec3(0.085, 0.088, 0.092) * (0.88 + 0.24 * n);
      vec4 diffuseColor = vec4(mix(pave, lawn, lawnK) * diffuse, opacity);`);
}
