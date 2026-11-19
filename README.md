# 21_21 DESIGN SIGHT 3D

Interactive 3D web exhibition of **21_21 DESIGN SIGHT** — Tadao Ando's museum in
Tokyo Midtown, Roppongi (9-7-6 Akasaka). One ground floor + one basement,
~80% underground, under a single 54 m folded steel-plate roof (the A-POC
"A Piece of Cloth" concept). Founded by Issey Miyake with Taku Satoh and
Naoto Fukasawa; opened 2007.

The virtual exhibition inside is 《一块布 · 一束光》 ("A Piece of Cloth,
A Beam of Light") — 12 pieces of Japanese everyday design in the two
basement galleries.

Private project. Not published.

## Model — v16 (current)

- File: `model/design2121_v16.glb` — 10,457,172 bytes, MD5
  `6de0d55413ada62f302415e6a930428c`
- 637 objects / 636 meshes, 133,712 triangles, 53 materials, 12 embedded images
- Basement **1,336 m²** (outline extends east to x=52); G1 **129 m²**,
  G2 **448 m²** (official 133 / 443)
- G3 is in the **west** wing (former café, converted 2017) — quadrilateral
  111.7 m², Private Room 4.0×2.9 m, ceiling max 4.26 m, terrace 57 m²,
  granite floor
- Exhibits 6 → 12: 07 Akari paper lamp, 08 kyusu teapot + cups, 09 noren
  curtain, 10 lacquer bento box, 11 bamboo basket, 12 tea bowl + chasen
- Confirmed: G2 red sphere is true red, G1 walls white, atrium roof has
  **no** skylight, G3 south glass only the bottom ~0.4 m is visible from inside
- Built with Blender 5.2.2 (`model/build_2121_v16.py`), verified by
  `model/verify_2121_v16.py`. Full build log:
  `docs/DESIGN2121_EXPORT_RECORD.md`; design/research log:
  `docs/DESIGN2121_RESEARCH_REVIEW.md`

## Layout

```
21-21-DESIGN-SIGHT/
├── README.md
├── .gitattributes               # model/**/*.glb -> Git LFS (see below; docs/ GLBs stay plain git)
├── .gitignore
├── model/
│   ├── design2121_v16.glb       # source model (10.46 MB, Blender source of truth)
│   ├── build_2121_v16.py        # Blender build script (v16)
│   └── verify_2121_v16.py       # Blender verification renders
└── docs/                        # the website source (GitHub Pages serves this folder)
    ├── index.html               # page shell: CSS + HTML + import map + module entry
    ├── assets/
    │   ├── design2121.glb       # served model: baked + compressed build, 4,573,688 bytes
    │   ├── three.module.min.js  # three.js r186, ES module build
    │   ├── three.core.js        # three.js r186 core (imported by three.module.min.js)
    │   ├── addons/              # three.js addons actually used (see below)
    │   │   ├── loaders/GLTFLoader.js
    │   │   ├── controls/OrbitControls.js
    │   │   └── utils/{BufferGeometryUtils,SkeletonUtils}.js
    │   └── js/                  # page code, one module per concern (issue #8)
    │       ├── scene.js         # renderer, sky, model loading, model fixes, render loop
    │       ├── lighting.js      # four light moments (palette + scene light together)
    │       ├── camera.js        # current mode, preset cameras, fly-to, mode switching
    │       ├── tour.js          # the 14-stop automatic tour
    │       ├── walk.js          # walk mode: zones, collision, stair, picking
    │       ├── ui.js            # exhibit card, G3 viewpoints, sidebar, hide-all
    │       └── labels.js        # exhibit catalogue + 3D signage sprites
    ├── DESIGN2121_RESEARCH_REVIEW.md
    ├── DESIGN2121_EXPORT_RECORD.md
    └── underground-structure-research/
        └── report.md            # basement-plan research (no dimensioned BF plan exists online)
```

`web/` (the old copy of the page) is **gone**: it duplicated `docs/` byte for
byte, and its copy could not even load the model on its own (it had no GLB).
Only `docs/` is the site source now. (The deletion itself is a local git
step — see the PR for issue #8; the connector used for that PR cannot
delete files.)

## How to use

**View the exhibition:** the live site is GitHub Pages (main branch,
`/docs` folder). Locally, serve `docs/` over HTTP — the page is ES modules
now, and browsers refuse module imports from `file://` (CORS):

```sh
cd docs && python3 -m http.server
# then open http://127.0.0.1:8000/
```

Orbit / zoom, walk the galleries, or run the 14-stop auto tour. Night is
the default of four light moments (morning / noon / dusk / night); the
header button cycles through them.

**Rebuild the model:** run `model/build_2121_v16.py` in Blender 5.2.2
(headless, Cycles GPU). It regenerates `model/design2121_v16.glb` from the
procedural build. Verify with `model/verify_2121_v16.py`. The served file
`docs/assets/design2121.glb` is a baked + compressed build of that model
(Cycles lightmap + AO on a second UV set, then the same dedup / meshopt /
WebP compression pass); re-bake and re-compress it after any re-export —
the page loads it by relative path, so it is **not** embedded in the HTML.

## Adding the model file

Both GLBs are binary and cannot be pushed through the GitHub connector
(text files only). Add them with a direct commit or the GitHub web UI,
which is the normal practice for files of this size (GitHub allows 100 MB
per file, 25 MB per web upload):

- `model/design2121_v16.glb` (10.46 MB) — the Blender source model.
- `docs/assets/design2121.glb` (4,573,688 bytes) — the baked + compressed build the page loads.
  **The page depends on this file**: opening `docs/index.html` without it
  shows the loading screen forever.

## Git LFS for `model/**/*.glb` (only)

`.gitattributes` tracks only `model/**/*.glb` in Git LFS, so future source-model
revisions do not bloat the clone. `docs/assets/design2121.glb` — the file the
live site actually serves — must stay plain git: GitHub Pages serves the
deployment branch as plain files and does not resolve LFS pointers, so an
LFS-tracked web GLB would ship as a pointer file and the live site could
not load it. Any `model/**/*.glb` committed **after** that file exists is
stored in LFS automatically. The GLBs already in history are still plain git
objects until they are migrated — a one-off local step (the connector
cannot run it):

```sh
git lfs install
git lfs migrate import --include="model/**/*.glb" --above=1MB
git push --force   # rewrites history: do this only when no PR branch
                   # is based on the old history, or rebase them after
```

## Page architecture (issue #8)

- **three.js r186**, loaded as ES modules through an import map in
  `docs/index.html` (`"three"` → `./assets/three.module.min.js`,
  `"three/addons/"` → `./assets/addons/`). The version is pinned; the
  build is local, so the page makes **zero external requests**.
- Of the old 865 KB bundle's 17 addons, only **two** are actually used and
  kept: `GLTFLoader` and `OrbitControls` (plus the two utils GLTFLoader
  itself imports). The other 15 were dead weight.
- The former ~134 KB inline script (2,528 lines, after the #9–#14 chain) is split into the seven modules under
  `docs/assets/js/` (see the layout above). The split is behaviour-only:
  same cameras, same tour, same walk mode, same loader. Each PR touches
  one module where possible, so reviews stay small.
- Shared state lives in exactly one module each (see the header comment of
  each file): `mode` + cameras in `camera.js`, the light moment in `lighting.js`,
  exhibit selection in `ui.js`, `walk` in `walk.js`, the tour in `tour.js`,
  the renderer/scene/model in `scene.js`, the exhibit catalogue in
  `labels.js`.

## Notes / known limits

- No dimensioned/scaled basement (BF) plan or section exists freely online;
  the model follows the official schematic topology + the 2007 original
  figures (G1 133 m² / 5.0 m, G2 443 m² / 4.8 m). See
  `docs/underground-structure-research/report.md`. Print sources
  (*Shinkenchiku* 2007:05, *Tadao Ando 3*) are the only path to a scaled plan.
- Known model limits: sunken-court opening has a slight kink at the south
  vertex; G3 roof–ceiling wedge gap; noren has no cloth folds; basement
  outline exact path, G2 east doorway, ramp position/slope, elevator
  trapezoid dimensions are inferred, not measured.
