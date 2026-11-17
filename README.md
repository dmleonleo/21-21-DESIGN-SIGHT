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
├── .gitignore
├── web/
│   └── 21-21-design-sight-3d.html   # self-contained page (model embedded, 11.3 MB)
├── model/
│   ├── design2121_v16.glb           # source model — see "Adding the model file"
│   ├── build_2121_v16.py            # Blender build script (v16)
│   └── verify_2121_v16.py           # Blender verification renders
└── docs/
    ├── DESIGN2121_RESEARCH_REVIEW.md
    ├── DESIGN2121_EXPORT_RECORD.md
    └── underground-structure-research/
        └── report.md                # basement-plan research (no dimensioned BF plan exists online)
```

## How to use

**View the exhibition:** open `web/21-21-design-sight-3d.html` in a browser.
It is fully self-contained — the slimmed model (7.55 MB) is embedded in the
page as base64, so no separate files are needed. Orbit / zoom, walk the
galleries, or run the 14-stop auto tour. Night mode is the default; the
sun/moon button in the header switches to day.

**Rebuild the model:** run `model/build_2121_v16.py` in Blender 5.2.2
(headless, Cycles GPU). It regenerates `design2121_v16.glb` from the
procedural build. Verify with `model/verify_2121_v16.py`.

## Adding the model file

`model/design2121_v16.glb` (10.46 MB) is **not** in the initial text-only
commit — the GitHub connector used for this upload handles text files only
and cannot transfer binary files. Add it with a direct commit, which is the
normal practice for a single model file of this size:

- GitHub allows individual files up to **100 MB** per push (warning at
  50 MB), and browser uploads up to **25 MB** per file — 10.46 MB is well
  inside both limits.
- Easiest: on github.com, open the `model/` folder → **Add file → Upload
  files** → drop in `design2121_v16.glb` → Commit. Done in a minute, no
  tools needed.
- Or from a local clone: `git add model/design2121_v16.glb && git commit -m
  "Add v16 model" && git push`.

The web page does **not** depend on this file (its model is embedded), so
the page works before and after the upload. The GLB is the Blender source
for future model revisions.

**If model revisions accumulate:** consider Git LFS for `*.glb`
(`git lfs install && git lfs track "*.glb"`, then commit the generated
`.gitattributes`). Each re-export stores a whole new copy in plain git
history, so LFS keeps the clone small over many versions. Not enabled by
default — direct commit is the right call for a single current model.

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
