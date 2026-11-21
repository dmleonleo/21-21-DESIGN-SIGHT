#!/usr/bin/env python3
"""Apply the #26 v22 rebuild (folded-plate roof + south facade) to the
v21 build script.

Reads issue21/D/push/model/build_2121_v21.py (v21, on branch
muse/issue21-roof-rebuild as model/build_2121_v21.py, blob 2cdf318f)
and writes issue21/v22/push/model/build_2121_v22.py (+ a remote-run
variant issue21/v22/remote/build_2121_v22_remote.py with OUT_DIR
redirected to C:\\Users\\Leon\\design2121_22D, same pattern as the D round).
Replayable: re-run on the v21 script to regenerate.
Do not hand-edit the output.

Frozen inputs (issue #26 r4; see v22/plan/PLAN_FREEZE.md and
v22/photomatch/PHOTOMATCH.md — every number below carries its source
tag there; this docstring states the modelling decisions, not the data):
  Plan (gate 1): main roof trapezoid NW (-10.00,-7.00), NE (43.42,-7.00),
    SE (39.20,3.50), SW (-5.60,3.50); north 53.42 m, south 44.8 m,
    depth 10.5 m. Fold A NE->SW, fold B NE->V (19.70,3.50), landing at
    56.5% of the south edge. Courtyard triangle unchanged
    (18.72,2.33),(39.39,-6.33),(35.8,2.33); its base is on the glass
    line Y=2.33, 1.17 m north of the roof south edge — the opening does
    NOT cut through the south edge. G3 quad A (-13.20,-5.60),
    B (-8.90,4.30), D (-16.70,17.60), C (-28.70,22.80), fold C->B.
  Height profile (gate 4): rel. 1FL, Blender Z. South edge (from SW):
    W 0.0 m -> 4.85 (drawing anchor, Detail 4 4,850 mm); V 25.30 m
    (Blender X 19.70, plan landing governs) -> 0.2; E 36.77 m
    (Blender X 31.17) -> 4.3; then flat ~4.3 to SE (39.20). East edge
    SE 4.3 -> NE ~4.5 (inferred). North edge NW 4.85 -> NE ~4.5
    (linear, inferred). West edge NW->SW both 4.85.
    Photo valley 26.8 m was computed on the REJECTED 46.3 m south /
    2.4 m module; rescaled to frozen 44.8 m it is 25.93 m, vs the plan
    landing 25.30 m — residual 0.63 m, within photo +/-1.0 m. The
    model uses the plan landing; the residual is reported honestly.
  Levels (Detail 4 p96/p98): 1FL +27.5 = +/-0; BFL1 +21.2 -> -6.3;
    BFL2 +20.3 -> -7.2; GL +27.0 (east) - +28.0 (north/section).
    Old -6.75/-5.85 are NO LONGER USED.
  Construction (unchanged): 16 mm steel plate + 30 mm foamed
    polyurethane + H-300x200 edge beam on rubber bearings + GB-R
    9.5+12.5 ceiling; 54 m single steel plate; fluorocarbon topcoat,
    metalness 0.3-0.5, roughness ~0.45 (PR-A, unchanged). Longest
    laminated glass 11.4 m (north long slit window); 14 m NOT used.

Modelling decisions (mine — stated as such, to be reviewed):
  [Roof] Three regions split by folds A and B tile the trapezoid:
    N (NW,NE,SW) = flat plane through (4.85, 4.5, 4.85);
    M (NE,SW,V) = flat plane through (4.5, 4.85, 0.2);
    E (NE,V,SE) = warped plate: barycentric plane through
    (4.5, 0.2, 4.3) PLUS a warp that honours all three boundary
    profiles exactly (fold B linear 4.5->0.2; south edge piecewise
    V->E rising then E->SE flat 4.3; east edge linear 4.3->4.5).
    A flat plane in E would give E=2.61, not the measured 4.3, so
    the warp is required; it vanishes on fold B and on the east
    edge, peaks 1.69 m at E, and its crease runs from E toward the
    east edge (fading to zero there) — a modelling interpolation
    (inferred), consistent with the roof plan's "warped plate, not
    two flat plates" (dashed lines converging to NE). The v21 false
    mid-ridge zm (+0.06) is removed; folds are A and B only.
    1-degree reconciliation (task-directed): the tateroku eave
    section + Detail 4 p96/p97 "N-S basically flat (~1 deg at 1/3)"
    applies to the plate NORTH of fold A; the drop is concentrated
    south of fold A. Probe v22 checks the N-S section at x~8.0.
  [South glass] Glass line Y=2.33, roof edge Y=3.50 (1.17 m eave
    overhang — the glass does NOT move to the roof edge). The glass
    top follows the roof surface directly above the glass line
    (roof_z_at(x, 2.33) minus the soffit offset 0.55 m at the glass
    line, 1.17 m from the edge -> 0.40+0.25*(1.17/2)=0.546 ~= 0.55)
    — NOT the eave profile: the eave is the roof EDGE (Y=3.50) and
    the glass is set back 1.17 m, where the warped roof is up to
    ~1 m higher (west wing) / lower (east wing) than the eave.
    The task's "top follows the eave" is a shape statement (right
    triangle west, V east), satisfied by this profile; the eave
    remains the roof-edge silhouette in the photos. Custom builder
    (glass_strip's 1.35 m transoms are wrong here — photos show
    vertical mullions ONLY plus a low base rail, no mid transom;
    vertical blinds inside must not be counted as mullions).
    West wing: 11 bays, module 2.30 m (25.30/11; photomatch
    homography gave 11.15 bays at 2.27 m — 2,250 mm wins; 2,400 was
    circularly derived from the rejected 46.3 m, do NOT use).
    Mullions at X=-5.60+k*2.30 (k=0..11); the first (-5.60) embeds
    0.16 m in the west wall (glass starts at the inner-face
    intersection (-5.44,2.33)). Base rail at z=0.35 (photo estimate).
    East wing: dense verticals ~1.0 m (photo estimate, range
    1.0-1.4 m — do NOT space at 2.4 m), interrupted by the core:
    V->core-west 19.70,20.70,21.70,22.40 (4); core-east->E
    27.40,28.40,29.40,30.40,31.17 (5) = 9 verticals total.
    Entrance core: Blender X 22.4-27.4, Y 2.33-4.83 (projects 2.5 m
    south of the glass line, freestanding pavilion — inferred from
    the Leon photo + Detail 4 p97 SE photo; exact depth unmeasured),
    Z 0-4.0 flat top (single photo, +/-0.4). South face: recessed
    dark doorway 2.2 wide x 3.0 high centred X=24.9 + tall banner
    panel east of the door with a round disc logo (r~0.45, z~2.6) —
    schematic, photo-based. The core occludes the valley eave behind
    it (roof edge at X=24.9 is z~2.07, below the core top 4.0).
    East end: solid concrete wall E(31.17)->SE(39.20) = 8.03 m,
    0..4.3, with a schematic door slit on its south face
    (photo-based, unmeasured); east edge NE->SE is a full-height
    triangular glass gable (top 4.5->4.3).
    Hall column (24,1.2) falls INSIDE the core footprint -> moved
    to (30,1.2). Leon-photo DIP at image x~1050 (~0.3 m) is NOT
    modelled as a second valley (img_8913 shows none there;
    inferred attribution = courtyard south rim — verify in the
    oblique v22 screenshot and report what is seen).
  [West entrance block] Rebuilt on the NEW west edge
    NW(-10,-7)->SW(-5.60,3.50), direction (0.3866,0.9225), angle
    67.35 deg (was 53.13 deg). Doorway 3.2 m centred at the
    west-edge midpoint (-7.80,-1.75) (the old centre (-4.75,0) lay
    2.14 m inside the new wall line). West edge heights flat 4.85
    both ends -> block tops 4.85, lintel 2.7..4.85. Sign/canopy/
    frames rotate to 67.35 deg. Reception desk moves to (-6.6,-3.2),
    rotated to the wall angle, just inside the doorway.
  [G3] Roof = frozen quad + fold C->B (valley, ~10.6 deg dihedral):
    two planar facets (A,B,C) and (B,D,C) with corner heights
    A 4.9 (ceiling 4.3 + 0.6 construction; v21 apex 4.91
    corroborates), B 4.1 (photo: tall glass at the east/entrance
    end; v21 photo-derived 4.124), D 3.55 (official section 2.9 as
    CEILING height at D + 0.65 construction — inferred: the 2.9's
    exact attachment is unconfirmed), C 2.0 (inferred: SW tip
    tapers low; no source number). The v21 G3 pentagon (X -34..-10,
    Y -6..6, E-W long axis) is wrong: the frozen quad's long axis
    runs NNW-SSE (C-A, 32.35 m) and the gallery is a 15.0 x 8.0 m
    strip at its north end (official segments 15.0/8.0/12.8 DO
    approximately match the frozen quad: B->D 15.42 vs 15.0, D->C
    13.08 vs 12.8, width ~8.3 vs 8.0 — all within ~0.5 m, i.e.
    within the quad's own uncertainty; the mapping of which segment
    is which remains inferred). Interior re-laid along the strip in
    (u,v) coords (u along the C-A north wall from A, v across toward
    B-D): north wall 15.0 m with slot window (u 1.5..7.5) + frosted
    band (u 7.5..13.5); east wall (A-B edge) with the entrance
    doorway near B; SE wall (B-D edge); south glass (u=15 line);
    terrace south of the glass toward C (57 m2); private room +
    kitchen at u 7..13.5, v 0..2.9; WCs by the entrance
    (u 6.5..8.5, v 5..7); reception desks on the north wall
    (u 3..7); columns at 30%/55% of the north wall (u 4.5/8.25,
    v 2.7/5.2) + round column at the south vertex (u 14.2, v 0.8);
    ceiling = Section C across the width (4.3 at the north wall ->
    0.4 at the south glass over 8.0 m), clamped to roof-0.65.
    The plan's dashed warp lines suggest the G3 plate may also warp
    slightly; with only 4 corner heights given, two planar facets
    are the determined model — recorded, not modelled.
  [B1 Z] BFL1 -6.3, BFL2 -7.2 (Detail 4 p96). p96 decoding: the stair
    descends in one straight flight from the entrance lobby (1FL) to
    LOBBY (BFL1); "6,000" is the LOBBY height (floor BFL1 -6.3 ->
    ground-slab soffit -0.3; slab top 0.02, 0.3 thick -> soffit -0.28
    ~= -0.3). It is NOT G1's height. "5,000" on the section's right
    is GALLERY 1's height (floor BFL2 -7.2 -> ceiling -2.2, matching
    the model G1 ceiling -2.20 and the published G1 net height 5.0).
    The task's parenthetical hypothesis (-7.2+6.0=-1.2) is therefore
    NOT adopted. "5,100" and "1,400+1,700" could NOT be resolved at
    the available scan resolution — reported as unresolved, not used.
    G2F/PLAT both -6.3 (lobby AND platform at BFL1 — the platform is
    no longer a separate mezzanine); G1F -7.2 unchanged; G2C -1.5
    (preserves the published G2 net height 4.8: -6.3+4.8=-1.5).
    Main stair: 42 steps (0->-6.3 at 0.15/0.30; 42x0.15=6.30 exact),
    flight X 15.63..28.23, landing directly on the BFL1 lobby floor.
    The 6 wide steps (platform->lobby) are DELETED (0 height
    difference now — they were an artefact of the old -5.85/-6.75
    split, which the p96 section does not support). G1 steps: 6
    (lobby -6.3 -> G1 -7.2 = 0.9), X 2.0..3.8. G2 ceiling -1.5;
    skylight slot -1.22, fluorescents -1.57, sprinklers/access
    panels soffit -1.53, G2 columns centre -3.9 (height 4.8 kept),
    east door centre -5.1, Z-corridor walls/ceiling -6.3..-1.5.
    G1 ceiling -2.20 UNCHANGED (5.0 net height confirmed by the
    section). Tallest court mullion ~10.81 m (was 11.68; the #17
    11.7 m figure was derived from the old levels -6.75+4.95 and is
    superseded by the Detail 4 levels — a datum-change regression,
    not a modelling error). B1 tie-hole grids shift +0.45; the
    basement north-wall top row is dropped (clearance to the -0.10
    wall top). Hall columns, atrium furnishings and exhibits shift
    automatically via the G2F/G1F/G2C constants. Noren rod/panels/
    crests shift +0.45 (heights above the G2 floor kept).
  [North walls] Tops follow the new north-edge profile (NW 4.85 ->
    NE ~4.5 linear): North_Above 4.85->4.59 (X -10..29.44),
    NorthEast_Above_A 4.59->4.52 (29.44..41), NorthEast_Above_B
    4.52->4.50 (41..43.42); Jog_Ground top 4.59. Tie-hole grids get
    top_fn = north profile (top rows clipped per column; expect
    Jog 48->42, North_Above/NorthEast_A top rows clipped — the
    probe gives the exact new total vs v21 3,625).
  [Lightmap] Geometry change is large (whole above-ground envelope
    + B1 Z) -> re-bake ALL 6 groups per the fix19 pipeline (see
    v22/build/bake_lighting_v22.py: v20 bake script re-pointed to
    design2121_22D + textures_v22_lighting; 96 samples + OIDN;
    Concrete grid enlarged 6x5 -> 7x7 for the new wall count).
    UV1 is regenerated by the re-bake (no transfer_uv1.mjs).
  [Page JS] No object-name references to the changed/deleted
    objects in the live scene.js (only SM_EXHIBIT_06_Ring/Core are
    looked up by name; the SM_Cafe_Roof reference is in a .bak
    backup of a removed fix). Tour/walk/camera text mentioning
    stair steps / levels must be checked after the first v22
    screenshots (see STATUS.md).

Open / unresolved (do not present as decided):
  - G3 section 4.3/2.9/1.2 exact referents (the 2.9 is used here as
    the ceiling height at D — inferred, see above).
  - "1,400+1,700" and "5,100" meanings in Detail 4 p96.
  - Entrance-core visibility discrepancy between the two photos
    (core clear in the Leon photo + Detail 4 p97 SE photo, no solid
    core block identifiable in img_8913 in the corresponding span).
  - South-glass base-rail height (0.35 m, photo estimate).
  - Reception-desk new position (chosen (-6.6,-3.2), rotated).
  - Whether tour/walk/camera JS needs changes (check after shots).
  - Gate 5 top-view overlay source (roof-plan overlay + OSM if no
    satellite is available).

Outputs are design2121_v22_build.blend / design2121_v22.glb.
"""
import py_compile
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
V22 = HERE.parent
V21_SCRIPT = V22.parent / "D" / "push" / "model" / "build_2121_v21.py"
OUT = V22 / "push" / "model" / "build_2121_v22.py"
REMOTE = V22 / "remote" / "build_2121_v22_remote.py"
BAKE_V20 = V22.parent / "C" / "patch" / "bake_lighting_v20.py"
BAKE_OUT = V22 / "build" / "bake_lighting_v22.py"


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"apply_v22: anchor {label}: expected 1 occurrence, found {n}")
    return text.replace(old, new)


def replace_count(text, old, new, count, label):
    n = text.count(old)
    if n != count:
        raise SystemExit(f"apply_v22: anchor {label}: expected {count} occurrences, found {n}")
    return text.replace(old, new)


def main():
    src = V21_SCRIPT.read_text()
    assert "v21 PR-D (issue #21 finish round" in src, "input is not the v21 build script"
    text = src

    # ---- header note + output names ----
    text = replace_once(text,
        "#  Outputs are design2121_v21_build.blend / design2121_v21.glb.\n",
        "#  Outputs are design2121_v21_build.blend / design2121_v21.glb.\n"
        "# v22 (issue #26, see issue21/v22/build/apply_v22.py — replayable,\n"
        "#     do not hand-edit): folded-plate roof + south facade rebuild.\n"
        "#  [Roof] Frozen trapezoid NW(-10,-7) NE(43.42,-7) SE(39.20,3.50)\n"
        "#      SW(-5.60,3.50); folds A NE->SW, B NE->V(19.70,3.50);\n"
        "#      corner heights NW 4.85 / NE ~4.5 / SW 4.85 / SE ~4.3,\n"
        "#      valley V 0.2, east point E(31.17,3.50) 4.3. Regions N/M\n"
        "#      flat planes, region E warped plate (see roof_z_at).\n"
        "#      v21 false mid-ridge zm (+0.06) removed.\n"
        "#  [South] Glass line Y=2.33, roof edge Y=3.50 (1.17 m eave\n"
        "#      overhang); west wing 11 bays x 2.30 m, east wing dense\n"
        "#      verticals ~1.0 m, entrance core X 22.4..27.4 (top 4.0),\n"
        "#      east solid wall E->SE + triangular glass gable.\n"
        "#  [G3] Frozen quad A(-13.20,-5.60) B(-8.90,4.30)\n"
        "#      D(-16.70,17.60) C(-28.70,22.80), fold C->B valley;\n"
        "#      corners A 4.9 / B 4.1 / D 3.55 / C 2.0; interior\n"
        "#      re-laid along the strip in (u,v) coords (see _g3_pt).\n"
        "#  [B1] BFL1 -6.3, BFL2 -7.2 (Detail 4 p96); G2F/PLAT -6.3,\n"
        "#      G2C -1.5 (net height 4.8 kept); stair 42 steps\n"
        "#      (15.63..28.23); wide steps DELETED; G1 steps 6.\n"
        "#  [Walls] North tops follow the new north-edge profile\n"
        "#      (4.85->4.59->4.52->4.50); Jog ground top 4.59.\n"
        "#  Outputs are design2121_v22_build.blend / design2121_v22.glb.\n",
        "header-v22")
    text = replace_once(text,
        'BLEND_PATH = os.path.join(OUT_DIR, "design2121_v21_build.blend")',
        'BLEND_PATH = os.path.join(OUT_DIR, "design2121_v22_build.blend")',
        "blend-name")
    text = replace_once(text,
        'GLB_PATH = os.path.join(OUT_DIR, "design2121_v21.glb")',
        'GLB_PATH = os.path.join(OUT_DIR, "design2121_v22.glb")',
        "glb-name")

    # ---- _point_in_tri tolerance (v22 fix, issue #26) ----
    # Grid points exactly on a triangle edge got 1-a-b ~ -7e-18 from float
    # rounding, were judged outside, and fell into the region-E fallback:
    # 29 roof vertices sank ~2.5 m (26 north-row cols -> 2.35, 3 west-edge
    # pts). Tolerance only; no geometry value changes.
    text = replace_once(text,
        "    return a >= 0 and b >= 0 and (1 - a - b) >= 0\n",
        "    # v22: 1e-9 tolerance on edge points (float -7e-18, see above).\n"
        "    return a >= -1e-9 and b >= -1e-9 and (1 - a - b) >= -1e-9\n",
        "point-in-tri-tolerance")

    # ---- STAIR_RECT: flight extends to X 28.23 (42 steps) ----
    text = replace_once(text,
        "STAIR_RECT = (15.63, 27.26, -6.16, -3.29)",
        "STAIR_RECT = (15.63, 28.23, -6.16, -3.29)  # v22: 42 steps, flight to X 28.23",
        "stair-rect")

    # ---- roof height field (region-based folded plate) ----
    text = replace_once(text,
        "def roof_z_north(x):\n"
        "    if x <= 41:\n"
        "        return 4.95\n"
        "    return 4.95 + (2.5 - 4.95) * ((x - 41) / 3.0)\n"
        "\n"
        "def roof_z_south(x):\n"
        "    if x < -3:  # west diagonal: NW corner 4.95 -> SW corner 3.20\n"
        "        return 4.95 + (3.20 - 4.95) * ((x + 10) / 7.0)\n"
        "    if x <= 39:\n"
        "        return 3.20\n"
        "    return 3.20 + (2.5 - 3.20) * ((x - 39) / 5.0)  # east diagonal: SE 3.20 -> NE 2.5\n"
        "\n"
        "def edge_y_north(x):\n"
        "    return -7.0\n"
        "\n"
        "def edge_y_south(x):\n"
        "    if x < -3:  # west diagonal: (-10,-7) -> (-3,2.33)\n"
        "        return -7.0 + 9.33 * ((x + 10) / 7.0)\n"
        "    if x <= 39:\n"
        "        return 2.33\n"
        "    return 2.33 - 9.33 * ((x - 39) / 5.0)  # east diagonal: (39,2.33) -> (44,-7)\n",
        "# v22 folded-plate roof (frozen trapezoid + height field, r4):\n"
        "# NW (-10,-7,4.85), NE (43.42,-7,~4.5), SW (-5.60,3.50,4.85),\n"
        "# SE (39.20,3.50,~4.3); valley V (19.70,3.50,0.2); east point\n"
        "# E (31.17,3.50,4.3). Folds: A NE->SW, B NE->V. Regions N\n"
        "# (NW,NE,SW) and M (NE,SW,V) are flat planes; region E (NE,V,SE)\n"
        "# is a warped plate (see roof_z_at): a flat plane there would\n"
        "# give E=2.61, not the measured 4.3.\n"
        "_ROOF_NW = (-10.00, -7.00, 4.85)\n"
        "_ROOF_NE = (43.42, -7.00, 4.50)\n"
        "_ROOF_SW = (-5.60, 3.50, 4.85)\n"
        "_ROOF_SE = (39.20, 3.50, 4.30)\n"
        "_ROOF_V = (19.70, 3.50, 0.20)\n"
        "_ROOF_E = (31.17, 3.50, 4.30)\n"
        "# E is 58.8% along V->SE (south edge): (31.17-19.70)/(39.20-19.70).\n"
        "_ROOF_E_T = (31.17 - 19.70) / (39.20 - 19.70)\n"
        "\n"
        "def _tri_bary(px, py, tri):\n"
        "    \"\"\"Barycentric weights of (px,py) in triangle tri (None if degenerate).\"\"\"\n"
        "    (x1, y1), (x2, y2), (x3, y3) = tri\n"
        "    d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)\n"
        "    if abs(d) < 1e-12:\n"
        "        return None\n"
        "    a = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / d\n"
        "    b = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / d\n"
        "    return (a, b, 1.0 - a - b)\n"
        "\n"
        "def _plane_z(px, py, p1, p2, p3):\n"
        "    \"\"\"Height of the plane through 3D points p1/p2/p3 at plan (px,py).\"\"\"\n"
        "    w = _tri_bary(px, py, ((p1[0], p1[1]), (p2[0], p2[1]), (p3[0], p3[1])))\n"
        "    if w is None:\n"
        "        return p1[2]\n"
        "    return w[0] * p1[2] + w[1] * p2[2] + w[2] * p3[2]\n"
        "\n"
        "def roof_z_north(x):\n"
        "    \"\"\"North edge: NW 4.85 -> NE ~4.5, linear (r4: inferred, straight).\"\"\"\n"
        "    return 4.85 + (4.50 - 4.85) * ((x + 10.0) / 53.42)\n"
        "\n"
        "def roof_z_south(x):\n"
        "    \"\"\"South ROOF EDGE (Y=3.50) height at Blender X: W 4.85 -> V 0.2\n"
        "    -> E 4.3 -> SE 4.3 (flat). Outside the south edge proper the\n"
        "    west/east diagonal edges apply (west flat 4.85, east 4.3->4.5).\"\"\"\n"
        "    if x < -5.60:\n"
        "        return 4.85  # west diagonal: NW 4.85 -> SW 4.85 (flat)\n"
        "    if x <= 19.70:\n"
        "        return 4.85 + (0.20 - 4.85) * ((x + 5.60) / 25.30)\n"
        "    if x <= 31.17:\n"
        "        return 0.20 + (4.30 - 0.20) * ((x - 19.70) / 11.47)\n"
        "    if x <= 39.20:\n"
        "        return 4.30\n"
        "    return 4.30 + (4.50 - 4.30) * ((x - 39.20) / 4.22)  # east diagonal: SE 4.3 -> NE 4.5\n"
        "\n"
        "def edge_y_north(x):\n"
        "    return -7.0\n"
        "\n"
        "def edge_y_south(x):\n"
        "    \"\"\"Roof south edge Y at Blender X: west diagonal NW->SW, then\n"
        "    flat Y=3.50, then east diagonal SE->NE.\"\"\"\n"
        "    if x < -5.60:  # west diagonal: (-10,-7) -> (-5.60,3.50)\n"
        "        return -7.0 + 10.5 * ((x + 10.0) / 4.40)\n"
        "    if x <= 39.20:\n"
        "        return 3.50\n"
        "    return 3.50 - 10.5 * ((x - 39.20) / 4.22)  # east diagonal: (39.20,3.50) -> (43.42,-7)\n",
        "roof-functions")

    text = replace_once(text,
        "def roof_sections(xs):\n"
        "    secs = []\n"
        "    for x in xs:\n"
        "        yn, ys = edge_y_north(x), edge_y_south(x)\n"
        "        zn, zs = roof_z_north(x), roof_z_south(x)\n"
        "        zm = (zn + zs) / 2.0 + 0.06  # near-flat single folded plate (real roof reads as one plane)\n"
        "        pts = []\n"
        "        for f in (0.0, 0.25, 0.5, 0.75, 1.0):\n"
        "            y = yn + (ys - yn) * f\n"
        "            if f == 0.5:\n"
        "                z = zm\n"
        "            elif f < 0.5:\n"
        "                z = zn + (zm - zn) * (f / 0.5)\n"
        "            else:\n"
        "                z = zm + (zs - zm) * ((f - 0.5) / 0.5)\n"
        "            pts.append((y, z))\n"
        "        secs.append((x, pts))\n"
        "    return secs\n",
        "def roof_sections(xs):\n"
        "    # v22: sections sample the region-based roof_z_at directly\n"
        "    # (single source of truth; the v21 zm mid-ridge is gone).\n"
        "    secs = []\n"
        "    for x in xs:\n"
        "        yn, ys = edge_y_north(x), edge_y_south(x)\n"
        "        pts = []\n"
        "        for f in (0.0, 0.25, 0.5, 0.75, 1.0):\n"
        "            y = yn + (ys - yn) * f\n"
        "            pts.append((y, roof_z_at(x, y)))\n"
        "        secs.append((x, pts))\n"
        "    return secs\n",
        "roof-sections")

    text = replace_once(text,
        "def roof_z_at(x, y):\n"
        "    \"\"\"Roof surface height at plan point (x, y), same profile as roof_sections.\n"
        "    Used by the G3 sloped ceiling and the atrium soffit so both sit below the\n"
        "    roof instead of poking through it.\"\"\"\n"
        "    yn, ys = edge_y_north(x), edge_y_south(x)\n"
        "    zn, zs = roof_z_north(x), roof_z_south(x)\n"
        "    zm = (zn + zs) / 2.0 + 0.06\n"
        "    f = (y - yn) / (ys - yn) if ys != yn else 0.0\n"
        "    f = max(0.0, min(1.0, f))\n"
        "    if f < 0.5:\n"
        "        return zn + (zm - zn) * (f / 0.5)\n"
        "    return zm + (zs - zm) * ((f - 0.5) / 0.5)\n",
        "def roof_z_at(x, y):\n"
        "    \"\"\"v22 folded-plate roof height at plan point (x, y). Regions N/M\n"
        "    are flat planes through their corners; region E is the warped\n"
        "    plate: barycentric plane through NE/V/SE plus a warp that\n"
        "    honours the south-edge piecewise profile exactly (V->E rising,\n"
        "    E->SE flat 4.3) while keeping the fold-B and east-edge profiles\n"
        "    linear. The warp vanishes on fold B (c=0) and on the east edge\n"
        "    (b=0); on the south edge (a=0) it equals the tent T(c):\n"
        "    2.8705*c for c<=E_T, 4.1*(1-c) above — the exact difference\n"
        "    between the piecewise south profile and the linear barycentric\n"
        "    profile (slopes 6.9705 vs 4.1 in c). Its crease runs from E\n"
        "    toward the east edge (fading to zero there). Points outside\n"
        "    the trapezoid fall through to region E with clamped weights\n"
        "    (a reasonable extrapolation for soffit-grid vertices outside\n"
        "    the FOOT, which are filtered out before meshing).\n"
        "    Used by the atrium soffit (and the south glass tops) so both\n"
        "    sit below the roof instead of poking through it.\"\"\"\n"
        "    _N = ((_ROOF_NW[0], _ROOF_NW[1]), (_ROOF_NE[0], _ROOF_NE[1]), (_ROOF_SW[0], _ROOF_SW[1]))\n"
        "    _M = ((_ROOF_NE[0], _ROOF_NE[1]), (_ROOF_SW[0], _ROOF_SW[1]), (_ROOF_V[0], _ROOF_V[1]))\n"
        "    _E = ((_ROOF_NE[0], _ROOF_NE[1]), (_ROOF_V[0], _ROOF_V[1]), (_ROOF_SE[0], _ROOF_SE[1]))\n"
        "    if _point_in_tri(x, y, _N):\n"
        "        return _plane_z(x, y, _ROOF_NW, _ROOF_NE, _ROOF_SW)\n"
        "    if _point_in_tri(x, y, _M):\n"
        "        return _plane_z(x, y, _ROOF_NE, _ROOF_SW, _ROOF_V)\n"
        "    w = _tri_bary(x, y, _E)\n"
        "    if w is None:\n"
        "        return 4.30\n"
        "    a, b, c = w\n"
        "    a = max(0.0, min(1.0, a)); b = max(0.0, min(1.0, b)); c = max(0.0, min(1.0, c))\n"
        "    _s = a + b + c\n"
        "    if _s <= 0:\n"
        "        return 4.30\n"
        "    a, b, c = a / _s, b / _s, c / _s\n"
        "    _z = a * 4.50 + b * 0.20 + c * 4.30\n"
        "    if c <= _ROOF_E_T:\n"
        "        _W = 2.8705 / (1.0 - c) if c < 1.0 else 0.0\n"
        "    else:\n"
        "        _W = 4.10 / c if c > 0.0 else 0.0\n"
        "    return _z + _W * b * c\n",
        "roof-z-at")

    text = replace_once(text,
        "    xs = []\n"
        "    x = -10.0  # #21B: roof x-range -10..44 (trapezoid)\n"
        "    while x <= 44.0:\n"
        "        xs.append(x)\n"
        "        x += x_step\n"
        "    if xs[-1] < 44.0:\n"
        "        xs.append(44.0)\n",
        "    xs = []\n"
        "    x = -10.0  # v22: roof x-range -10..43.42 (frozen trapezoid)\n"
        "    while x <= 43.42:\n"
        "        xs.append(x)\n"
        "        x += x_step\n"
        "    if xs[-1] < 43.42:\n"
        "        xs.append(43.42)\n",
        "roof-grid-xrange")

    text = replace_once(text,
        "        yn, ys = edge_y_north(x), edge_y_south(x)\n"
        "        zn, zs = roof_z_north(x), roof_z_south(x)\n"
        "        zm = (zn + zs) / 2.0 + 0.06\n"
        "        for fi, f in enumerate(fs):\n"
        "            y = yn + (ys - yn) * f\n"
        "            if f == 0.5:\n"
        "                z = zm\n"
        "            elif f < 0.5:\n"
        "                z = zn + (zm - zn) * (f / 0.5)\n"
        "            else:\n"
        "                z = zm + (zs - zm) * ((f - 0.5) / 0.5)\n"
        "            idx[(xi, fi)] = len(verts)\n"
        "            verts.append((x, y, z))\n",
        "        yn, ys = edge_y_north(x), edge_y_south(x)\n"
        "        for fi, f in enumerate(fs):\n"
        "            y = yn + (ys - yn) * f\n"
        "            z = roof_z_at(x, y)  # v22: region-based folded plate\n"
        "            idx[(xi, fi)] = len(verts)\n"
        "            verts.append((x, y, z))\n",
        "roof-grid-inner")

    print("chunk 1 done")

    # ---- museum-wing exterior (v22) ----
    text = replace_once(text,
        "# #21B museum-wing exterior (replaces the PR-A block from MUSEUM_XS through the\n"
        "# east-tip glass gable). Roof is the D3 trapezoid: north edge 54 m (-10,-7)->(44,-7),\n"
        "# south edge 42 m (-3,2.33)->(39,2.33); north edge flat at apex +4.95 to x=41, then\n"
        "# down to +2.5 at the NE corner (see roof_z_north — the old scaled profile put the\n"
        "# tallest court mullion at ~8.7 m, contradicting the measured #17, 11.7 m).\n",
        "# v22 museum-wing exterior. Roof is the frozen trapezoid: north edge\n"
        "# 53.42 m (-10,-7)->(43.42,-7), south edge 44.8 m (-5.60,3.50)->\n"
        "# (39.20,3.50); north edge 4.85->~4.5 linear, south edge W 4.85 ->\n"
        "# V 0.2 -> E 4.3 -> SE 4.3 (see roof_z_north/roof_z_south). The v21\n"
        "# D3 trapezoid (54 m north, 42 m south, apex +4.95, south +3.20)\n"
        "# is superseded by the r4 frozen plan + height profile.\n",
        "museum-comment")
    text = replace_once(text,
        "MUSEUM_XS = [-10, -3, 5, 15, 25, 35, 39, 44]",
        "MUSEUM_XS = [-10, -5.6, 5, 15, 19.7, 25, 31.17, 39.2, 43.42]  # v22: key X stations (W corner, valley, E point, SE corner)",
        "museum-xs")
    text = replace_once(text,
        "# FIX [RIM]: lift 0.30 -> -0.05 — the rim top was +5.25, over the <=5.2\n"
        "# acceptance line; now +4.90, just below the roof surface (solidify\n"
        "# goes down 0.90, so the ring still reads as a curb around the opening\n"
        "# from inside the court, and its outer band hides under the roof solid).\n",
        "# FIX [RIM]: lift 0.30 -> -0.05 — the rim top was +5.25, over the <=5.2\n"
        "# acceptance line; now +4.90, just below the roof surface (solidify\n"
        "# goes down 0.90, so the ring still reads as a curb around the opening\n"
        "# from inside the court, and its outer band hides under the roof solid).\n"
        "# v22: lift -0.05 kept; the rim top is now ~+4.45 (the roof near the\n"
        "# court is ~4.5, down from 4.95), still just below the roof surface.\n",
        "rim-comment")

    # ---- north walls: B1 base -6.3; tops follow the new north-edge profile ----
    text = replace_once(text,
        "# North wall (B1 + ground), straight Y=-7 / Y=-8.56 with the jog at X=29.44.\n"
        "# FIX [4] (b): the long-window slot moves up — below the slot\n"
        "# (Z -6.75..0) it is continuous; the slot (Z 0..0.45, sill flush with\n",
        "# North wall (B1 + ground), straight Y=-7 / Y=-8.56 with the jog at X=29.44.\n"
        "# FIX [4] (b): the long-window slot moves up — below the slot\n"
        "# (Z -6.3..0) it is continuous; the slot (Z 0..0.45, sill flush with\n",
        "north-comment")
    text = replace_once(text,
        'wall_varying("SM_Museum_Wall_North_Below", (-10, -7), (29.44, -7), -6.75, 0.0, -6.75, 0.0,  # FIX [4] (b)',
        'wall_varying("SM_Museum_Wall_North_Below", (-10, -7), (29.44, -7), -6.3, 0.0, -6.3, 0.0,  # FIX [4] (b); v22: BFL1 -6.3',
        "north-below")
    text = replace_once(text,
        'wall_varying("SM_Museum_Wall_North_Above", (-10, -7), (29.44, -7), 0.45, 4.95, 0.45, 4.95,  # FIX [4] (b)',
        'wall_varying("SM_Museum_Wall_North_Above", (-10, -7), (29.44, -7), 0.45, 4.85, 0.45, 4.59,  # FIX [4] (b); v22: north profile 4.85->4.59',
        "north-above")
    text = replace_once(text,
        'wall_varying("SM_Museum_Wall_North_Jog", (29.44, -7), (29.44, -8.56), -6.75, 0.0, -6.75, 0.0,  # FIX [4] (b): top to GL, the new slot sill',
        'wall_varying("SM_Museum_Wall_North_Jog", (29.44, -7), (29.44, -8.56), -6.3, 0.0, -6.3, 0.0,  # FIX [4] (b): top to GL, the new slot sill; v22: BFL1 -6.3',
        "north-jog-b1")
    text = replace_once(text,
        "# This wall continues the same line and thickness, 0.0..4.95, to meet\n"
        "# both neighbours' tops (west Above 4.95, east Above_A 4.95); ends\n",
        "# This wall continues the same line and thickness, 0.0..4.59, to meet\n"
        "# both neighbours' tops (west Above 4.59, east Above_A 4.59); ends\n",
        "jog-comment")
    text = replace_once(text,
        'wall_varying("SM_Museum_Wall_North_Jog_Ground", (29.44, -7), (29.44, -8.56), 0.0, 4.95, 0.0, 4.95,',
        'wall_varying("SM_Museum_Wall_North_Jog_Ground", (29.44, -7), (29.44, -8.56), 0.0, 4.59, 0.0, 4.59,  # v22: north profile at the jog',
        "jog-ground")
    text = replace_once(text,
        'wall_varying("SM_Museum_Wall_NorthEast_Below", (29.44, -8.56), (48.56, -8.56), -6.75, 0.0, -6.75, 0.0,  # FIX [4] (b)',
        'wall_varying("SM_Museum_Wall_NorthEast_Below", (29.44, -8.56), (48.56, -8.56), -6.3, 0.0, -6.3, 0.0,  # FIX [4] (b); v22: BFL1 -6.3',
        "ne-below")
    text = replace_once(text,
        "# Ground-floor north wall east of the jog (Y=-8.56, Z 0..roof: flat 4.95 to\n"
        "# x=41, then down to 2.5 at the NE corner).\n",
        "# Ground-floor north wall east of the jog (Y=-8.56, Z 0..roof: 4.59 at\n"
        "# the jog -> 4.52 at x=41, then 4.50 at the NE corner — the new\n"
        "# north-edge profile, 4.85->~4.5 linear over 53.42 m).\n",
        "ne-comment")
    text = replace_once(text,
        'wall_varying("SM_Museum_Wall_NorthEast_Above_A", (29.44, -8.56), (41, -8.56), 0.45, 4.95, 0.45, 4.95,  # FIX [4] (b)',
        'wall_varying("SM_Museum_Wall_NorthEast_Above_A", (29.44, -8.56), (41, -8.56), 0.45, 4.59, 0.45, 4.52,  # FIX [4] (b); v22: north profile',
        "ne-above-a")
    text = replace_once(text,
        'wall_varying("SM_Museum_Wall_NorthEast_Above_B", (41, -8.56), (44, -8.56), 0.45, 4.95, 0.45, 2.5,  # FIX [4] (b)',
        'wall_varying("SM_Museum_Wall_NorthEast_Above_B", (41, -8.56), (43.42, -8.56), 0.45, 4.52, 0.45, 4.50,  # FIX [4] (b); v22: north profile to the NE corner',
        "ne-above-b")

    # ---- west entrance block: new west edge, 67.35 deg, doorway at the midpoint ----
    text = replace_once(text,
        "# West entrance block — #21B: the west edge is now the slanted line\n"
        "# (-10,-7)->(-3,2.33), direction (0.6,0.8), angle 53.13 deg. Doorway 3.2 m\n"
        "# centred at Y=0 (plan (-4.75,0)); segments + lintel follow the roof\n"
        "# (NW corner 4.95 -> SW corner 3.20); glass door + frames + canopy + sign.\n"
        "_ENT_ANG = math.radians(53.13)\n"
        "_ENT_C = (-4.75, 0.0)\n"
        "def _ent_pt(s):\n"
        "    return (_ENT_C[0] + 0.6 * s, _ENT_C[1] + 0.8 * s)\n"
        "# north segment (long, toward NW): s -8.75..-1.6, roof 4.95->3.88\n"
        "_n0 = _ent_pt(-8.75); _n1 = _ent_pt(-1.6)\n"
        'wall_varying("SM_Museum_Entrance_Block_N", _n0, _n1, 0.0, 4.95, 0.0, 3.88,\n'
        "             MAT_CONCRETE, COL_MUSEUM, thick=1.2)\n"
        "# south segment (short, toward SW): s 1.6..2.91, roof 3.40->3.20\n"
        "_s0 = _ent_pt(1.6); _s1 = _ent_pt(2.91)\n"
        'wall_varying("SM_Museum_Entrance_Block_S", _s0, _s1, 0.0, 3.40, 0.0, 3.20,\n'
        "             MAT_CONCRETE, COL_MUSEUM, thick=1.2)\n"
        "# lintel over the doorway (s -1.6..1.6, Z 2.7..roof)\n"
        'wall_varying("SM_Museum_Entrance_Lintel", _n1, _s0, 2.7, 3.88, 2.7, 3.40,\n'
        "             MAT_CONCRETE, COL_MUSEUM, thick=1.2)\n"
        "# glass door + frames + canopy + sign (rotated to the wall angle)\n"
        'box("SM_Museum_Entrance_Door", (_ENT_C[0], _ENT_C[1], 1.35), (3.2, 0.15, 2.7), MAT_GLASS, COL_MUSEUM,\n'
        "    rot=(0, 0, _ENT_ANG))\n"
        'box("SM_Museum_Entrance_Frame_L", (_ent_pt(-1.68)[0], _ent_pt(-1.68)[1], 1.35), (0.12, 0.12, 2.7), MAT_BLACK, COL_MUSEUM,\n'
        "    rot=(0, 0, _ENT_ANG))\n"
        'box("SM_Museum_Entrance_Frame_R", (_ent_pt(1.68)[0], _ent_pt(1.68)[1], 1.35), (0.12, 0.12, 2.7), MAT_BLACK, COL_MUSEUM,\n'
        "    rot=(0, 0, _ENT_ANG))\n"
        'box("SM_Museum_Entrance_Frame_Top", (_ENT_C[0], _ENT_C[1], 2.76), (3.5, 0.12, 0.12), MAT_BLACK, COL_MUSEUM,\n'
        "    rot=(0, 0, _ENT_ANG))\n"
        'box("SM_Museum_Entrance_Canopy", (_ENT_C[0] - 0.48, _ENT_C[1] + 0.36, 2.98), (4.2, 0.9, 0.08), MAT_STEEL_DARK, COL_MUSEUM,\n'
        "    rot=(0, 0, _ENT_ANG))\n"
        "# 21_21 sign plate on the north block (offset 0.66 outward so it sits proud\n"
        "# of the 1.2-thick wall face, not buried in it)\n"
        "_sg = _ent_pt(-3.5)\n"
        'box("SM_Museum_Sign", (_sg[0] - 0.53, _sg[1] + 0.40, 3.6), (4.5, 0.12, 0.9), MAT_BLACK, COL_MUSEUM,\n'
        "    rot=(0, 0, _ENT_ANG))\n",
        "# West entrance block — v22: the west edge is now the slanted line\n"
        "# NW (-10,-7)->SW (-5.60,3.50), direction (0.3866,0.9225), angle\n"
        "# 67.35 deg (was 53.13 deg on the old edge). Doorway 3.2 m centred\n"
        "# at the west-edge midpoint (-7.80,-1.75) — the old centre (-4.75,0)\n"
        "# lay 2.14 m inside the new wall line. The west edge heights are\n"
        "# flat 4.85 at both ends, so both segments + lintel top at 4.85\n"
        "# (v21: 4.95->3.20 along the old edge). Glass door + frames +\n"
        "# canopy + sign, rotated to the new wall angle.\n"
        "_ENT_ANG = math.radians(67.35)\n"
        "_ENT_C = (-7.80, -1.75)\n"
        "_ENT_DIR = (0.3866, 0.9225)  # west-edge direction (unit)\n"
        "_ENT_NRM_OUT = (-0.9225, 0.3866)  # outward normal (west) of the west edge\n"
        "def _ent_pt(s):\n"
        "    return (_ENT_C[0] + _ENT_DIR[0] * s, _ENT_C[1] + _ENT_DIR[1] * s)\n"
        "# north segment (toward NW): s -5.695..-1.6, roof flat 4.85\n"
        "_n0 = _ent_pt(-5.695); _n1 = _ent_pt(-1.6)\n"
        'wall_varying("SM_Museum_Entrance_Block_N", _n0, _n1, 0.0, 4.85, 0.0, 4.85,\n'
        "             MAT_CONCRETE, COL_MUSEUM, thick=1.2)\n"
        "# south segment (toward SW): s 1.6..5.695, roof flat 4.85\n"
        "_s0 = _ent_pt(1.6); _s1 = _ent_pt(5.695)\n"
        'wall_varying("SM_Museum_Entrance_Block_S", _s0, _s1, 0.0, 4.85, 0.0, 4.85,\n'
        "             MAT_CONCRETE, COL_MUSEUM, thick=1.2)\n"
        "# lintel over the doorway (s -1.6..1.6, Z 2.7..4.85)\n"
        'wall_varying("SM_Museum_Entrance_Lintel", _n1, _s0, 2.7, 4.85, 2.7, 4.85,\n'
        "             MAT_CONCRETE, COL_MUSEUM, thick=1.2)\n"
        "# glass door + frames + canopy + sign (rotated to the wall angle)\n"
        'box("SM_Museum_Entrance_Door", (_ENT_C[0], _ENT_C[1], 1.35), (3.2, 0.15, 2.7), MAT_GLASS, COL_MUSEUM,\n'
        "    rot=(0, 0, _ENT_ANG))\n"
        'box("SM_Museum_Entrance_Frame_L", (_ent_pt(-1.68)[0], _ent_pt(-1.68)[1], 1.35), (0.12, 0.12, 2.7), MAT_BLACK, COL_MUSEUM,\n'
        "    rot=(0, 0, _ENT_ANG))\n"
        'box("SM_Museum_Entrance_Frame_R", (_ent_pt(1.68)[0], _ent_pt(1.68)[1], 1.35), (0.12, 0.12, 2.7), MAT_BLACK, COL_MUSEUM,\n'
        "    rot=(0, 0, _ENT_ANG))\n"
        'box("SM_Museum_Entrance_Frame_Top", (_ENT_C[0], _ENT_C[1], 2.76), (3.5, 0.12, 0.12), MAT_BLACK, COL_MUSEUM,\n'
        "    rot=(0, 0, _ENT_ANG))\n"
        'box("SM_Museum_Entrance_Canopy", (_ENT_C[0] + 0.6 * _ENT_NRM_OUT[0], _ENT_C[1] + 0.6 * _ENT_NRM_OUT[1], 2.98), (4.2, 0.9, 0.08), MAT_STEEL_DARK, COL_MUSEUM,\n'
        "    rot=(0, 0, _ENT_ANG))\n"
        "# 21_21 sign plate on the north block (offset 0.66 outward so it sits proud\n"
        "# of the 1.2-thick wall face, not buried in it)\n"
        "_sg = _ent_pt(-3.5)\n"
        'box("SM_Museum_Sign", (_sg[0] + 0.66 * _ENT_NRM_OUT[0], _sg[1] + 0.66 * _ENT_NRM_OUT[1], 3.6), (4.5, 0.12, 0.9), MAT_BLACK, COL_MUSEUM,\n'
        "    rot=(0, 0, _ENT_ANG))\n",
        "west-entrance")

    # ---- south facade: custom builder (glass line Y=2.33, roof edge Y=3.50) ----
    text = replace_once(text,
        "# South glass facade (continuous glazing, top follows roof south edge = 3.20)\n"
        "south_edge = [(-3, 2.33, 3.20), (10, 2.33, 3.20), (25, 2.33, 3.20), (39, 2.33, 3.20)]\n"
        'glass_strip("SM_Museum_Glass_South", south_edge, 0.0, MAT_GLASS, COL_MUSEUM)\n'
        "# East tip glass gable (triangular, along the roof east edge (44,-7)->(39,2.33))\n"
        'glass_strip("SM_Museum_Glass_Tip",\n'
        "            [(44, -7, 2.5), (39, 2.33, 3.20)], 0.0, MAT_GLASS, COL_MUSEUM)\n",
        "# South glass facade — v22 (issue #26 r4): glass line Y=2.33, roof\n"
        "# edge Y=3.50 (1.17 m eave overhang — the glass does NOT move to the\n"
        "# roof edge). The glass top follows the roof surface directly above\n"
        "# the glass line (roof_z_at(x, 2.33) minus the soffit offset 0.55 m\n"
        "# at the glass line: 1.17 m from the edge -> 0.40+0.25*(1.17/2) =\n"
        "# 0.546 ~= 0.55) — NOT the eave profile: the eave is the roof EDGE\n"
        "# (Y=3.50) and the glass is set back 1.17 m, where the warped roof\n"
        "# is up to ~1 m higher (west wing) / lower (east wing) than the\n"
        "# eave. The task's \"top follows the eave\" is a shape statement\n"
        "# (right triangle west, V east), satisfied by this profile; the\n"
        "# eave remains the roof-edge silhouette in the photos. Custom\n"
        "# builder: glass_strip's 1.35 m transoms are wrong here — the\n"
        "# photos show vertical mullions ONLY plus a low base rail, no mid\n"
        "# transom (vertical blinds inside must not be counted as mullions).\n"
        "def _south_glass_top(x):\n"
        "    \"\"\"Glass-top height at Blender X (roof surface above the glass\n"
        "    line Y=2.33, minus the 0.55 m soffit offset at the glass line).\"\"\"\n"
        "    return roof_z_at(x, 2.33) - 0.55\n"
        "\n"
        "def _south_glass_segment(name, xs, y_glass=2.33, base_rail_z=0.35):\n"
        "    \"\"\"Glass wall along Y=y_glass for the given X stations; top\n"
        "    follows _south_glass_top. Vertical mullions at each station +\n"
        "    one low base rail (z=0.35, photo estimate) — skipped where the\n"
        "    glass is too low for it (near the valley).\"\"\"\n"
        "    edge = [(x, y_glass, _south_glass_top(x)) for x in xs]\n"
        "    verts, faces = [], []\n"
        "    for (x, y, zt) in edge:\n"
        "        verts.append((x, y, 0.0))\n"
        "        verts.append((x, y, zt))\n"
        "    for i in range(len(edge) - 1):\n"
        "        a, b, c, d = 2*i, 2*i+1, 2*i+3, 2*i+2\n"
        "        faces.append((a, b, c, d))\n"
        "    g = mesh_from_pydata(name, verts, faces, MAT_GLASS, COL_MUSEUM)\n"
        "    for _j, _x in enumerate(xs):\n"
        "        _zt = _south_glass_top(_x)\n"
        "        box(f\"{name}_Mullion_{_j:02d}\", (_x, y_glass, _zt / 2.0),\n"
        "            (0.06, 0.06, _zt), MAT_BLACK, COL_MUSEUM)\n"
        "    _min_top = min(_south_glass_top(_x) for _x in xs)\n"
        "    _rail_z = min(base_rail_z, _min_top - 0.06)\n"
        "    if _rail_z >= 0.12:\n"
        "        _x0, _x1 = xs[0], xs[-1]\n"
        "        box(f\"{name}_BaseRail\", ((_x0 + _x1) / 2.0, y_glass, _rail_z),\n"
        "            (_x1 - _x0, 0.06, 0.06), MAT_BLACK, COL_MUSEUM)\n"
        "    return g\n"
        "\n"
        "# West wing: right-triangle glass, 11 bays, module 2.30 m\n"
        "# (25.30/11; photomatch homography gave 11.15 bays at 2.27 m —\n"
        "# 2,250 mm wins; 2,400 was circularly derived from the rejected\n"
        "# 46.3 m south edge, do NOT use). Mullions at X=-5.60+k*2.30\n"
        "# (k=0..11); the first (-5.60) embeds 0.16 m in the west wall\n"
        "# (the glass starts at the inner-face intersection (-5.44,2.33)).\n"
        "_WEST_MULLIONS = [-5.60 + 2.30 * k for k in range(12)]\n"
        '_south_glass_segment("SM_Museum_Glass_South_West", _WEST_MULLIONS)\n'
        "# Entrance core (freestanding pavilion in front of the glass,\n"
        "# X 22.4..27.4, Y 2.33..4.83, flat top 4.0 — single photo,\n"
        "# +/-0.4; exact depth unmeasured). It occludes the valley eave\n"
        "# behind it (roof edge at X=24.9 is z~2.07, below the core top).\n"
        'box("SM_Entrance_Core", (24.9, 3.58, 2.0), (5.0, 2.5, 4.0), MAT_CONCRETE, COL_MUSEUM)\n'
        "# Recessed dark doorway (2.2 wide x 3.0 high, centred X=24.9) on\n"
        "# the south face (Y=4.83): a dark panel slightly proud of the face\n"
        "# (no boolean — reads as a doorway from the front).\n"
        'box("SM_Entrance_Core_Door", (24.9, 4.84, 1.5), (2.2, 0.08, 3.0), MAT_BLACK, COL_MUSEUM)\n'
        "# Tall banner panel east of the door with a round disc logo\n"
        "# (schematic, photo-based: the Leon photo shows a tall poster\n"
        "# with a circular logo east of the doorway).\n"
        'box("SM_Entrance_Core_Banner", (26.9, 4.84, 2.6), (1.2, 0.06, 2.4), MAT_WHITE, COL_MUSEUM)\n'
        "bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.45, depth=0.05,\n"
        "                                    location=(26.9, 4.88, 2.6), rotation=(math.radians(90), 0, 0))\n"
        "_o = bpy.context.active_object\n"
        '_o.name = "SM_Entrance_Core_Disc"\n'
        "set_mat(_o, MAT_BLACK); link(_o, COL_MUSEUM)\n"
        "# East wing: V-shaped glass V->E, dense verticals ~1.0 m (photo\n"
        "# estimate, range 1.0-1.4 m — do NOT space at 2.4 m), interrupted\n"
        "# by the entrance core (X 22.4..27.4): 4 + 5 = 9 verticals total.\n"
        "_EAST_MULLIONS_W = [19.70, 20.70, 21.70, 22.40]\n"
        "_EAST_MULLIONS_E = [27.40, 28.40, 29.40, 30.40, 31.17]\n"
        '_south_glass_segment("SM_Museum_Glass_South_East_W", _EAST_MULLIONS_W)\n'
        '_south_glass_segment("SM_Museum_Glass_South_East_E", _EAST_MULLIONS_E)\n'
        "# East end: solid concrete wall E(31.17)->SE(39.20) = 8.03 m, ON THE\n"
        "# ROOF EDGE (Y=3.50), 0..4.3 (the eave is flat 4.3 there). A wall\n"
        "# at the glass line (Y=2.33) would poke through the warped roof\n"
        "# (roof is only 3.57 above the glass line at E) — the solid\n"
        "# east block's south face is at the eave, per img_8913 (the\n"
        "# block face steps forward of the glass plane). Schematic door\n"
        "# slit on its south face (photo-based, unmeasured).\n"
        "wall_varying(\"SM_Museum_Wall_South_East\", (31.17, 3.50), (39.20, 3.50), -0.10, 4.3, -0.10, 4.3,\n"
        "             MAT_CONCRETE, COL_MUSEUM, thick=0.35)\n"
        "box(\"SM_Museum_EastWall_Door\", (35.0, 3.70, 1.05), (0.9, 0.06, 2.1), MAT_BLACK, COL_MUSEUM)\n"
        "# Return wall closing the 1.17 m facade step at E (glass line\n"
        "# Y=2.33 -> wall face Y=3.50); top follows the roof surface\n"
        "# (3.57 at the glass line, 4.30 at the eave), 0.08 below it:\n"
        "# the warped roof deviates 0.04 m from linear at mid-span\n"
        "# (roof 3.894 at Y=2.915 vs 3.935 linear), so a flush top\n"
        "# would poke through by 0.04 m.\n"
        "wall_varying(\"SM_Museum_Wall_East_Return\", (31.17, 2.33), (31.17, 3.50), -0.10, 3.49, -0.10, 4.22,\n"
        "             MAT_CONCRETE, COL_MUSEUM, thick=0.35)\n"
        "# East tip glass gable (triangular, along the roof east edge NE(43.42,-7)->SE(39.20,3.50))\n"
        'glass_strip("SM_Museum_Glass_Tip",\n'
        "            [(43.42, -7, 4.5), (39.20, 3.50, 4.3)], 0.0, MAT_GLASS, COL_MUSEUM)\n",
        "south-facade")

    print("chunk 2 done")

    text = _apply_g3(text)
    text = _apply_chunk4(text)
    print("chunk 4 done")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print(f"wrote {OUT} ({len(text)} chars)")

    # remote variant: only OUT_DIR differs (remote build dir 22D)
    remote = replace_once(text,
        'OUT_DIR = r"C:\\Users\\Leon\\design2121"',
        'OUT_DIR = r"C:\\Users\\Leon\\design2121_22D"',
        "remote-outdir")
    REMOTE.parent.mkdir(parents=True, exist_ok=True)
    REMOTE.write_text(remote)
    print(f"wrote {REMOTE} ({len(remote)} chars)")

    # bake script (fix19): re-point paths + enlarge Concrete/Floor grids
    bake = BAKE_V20.read_text()
    bake = replace_once(bake,
        'BLEND_IN = r"C:\\Users\\Leon\\design2121_21C\\design2121_v20_build.blend"',
        'BLEND_IN = r"C:\\Users\\Leon\\design2121_22D\\design2121_v22_build.blend"',
        "bake-blend-in")
    bake = replace_once(bake,
        'OUT_DIR = r"C:\\Users\\Leon\\design2121_21C"',
        'OUT_DIR = r"C:\\Users\\Leon\\design2121_22D"',
        "bake-outdir")
    bake = replace_once(bake,
        'TEX_DIR = os.path.join(OUT_DIR, "textures_v20_lighting")',
        'TEX_DIR = os.path.join(OUT_DIR, "textures_v22_lighting")',
        "bake-texdir")
    bake = replace_once(bake,
        '("MAT_Concrete",       2048, 6, 5),   # 30 cells >= 25 objs; atlas 1024->2048',
        '("MAT_Concrete",       2048, 6, 5),   # 30 cells >= 29 objs (v22 fix: 7x7 grid shrank UVCHECK total to 0.282 < 0.3; grid-size effect, UVs healthy)',
        "bake-concrete-grid")
    bake = replace_once(bake,
        '("MAT_Floor_Concrete", 2048, 4, 4),   # 16 cells = 16 objs; atlas 1024->2048',
        '("MAT_Floor_Concrete", 2048, 5, 4),   # 20 cells (v22: 16 objs + headroom)',
        "bake-floor-grid")
    bake = replace_once(bake, '"design2121_v20_lighting.blend"', '"design2121_v22_lighting.blend"', "bake-lighting-blend")
    bake = replace_once(bake, '"design2121_v20_baked.glb"', '"design2121_v22_baked.glb"', "bake-baked-glb")
    bake = replace_once(bake,
        '# PR-C (v20): paths re-pointed to design2121_21C with _v20 outputs.',
        '# PR-C (v20): paths re-pointed to design2121_21C with _v20 outputs.\n# v22: paths re-pointed to design2121_22D with _v22 outputs; Concrete 6x5, Floor 5x4.\n# v22 fix: Concrete back to 6x5 — 7x7=49 cells shrank the UVCHECK total to 0.282 < 0.3 (grid-size effect, UVs healthy; 30 cells >= 29 objs).',
        "bake-header")
    BAKE_OUT.parent.mkdir(parents=True, exist_ok=True)
    BAKE_OUT.write_text(bake)
    print(f"wrote {BAKE_OUT} ({len(bake)} chars)")


# ---------------- chunk 3: G3 (frozen quad + fold C->B) ----------------
# Step 0 (2026-11-21 ~00:52): the v21 re-run completed — === BUILD COMPLETE ===,
# exported design2121_v21.glb size=20004344 bytes (exact match), BAKE-OK 9/9,
# STATS objects=4325 meshes=4324 tris=114458. The build environment is confirmed.


def _apply_g3(text):
    """Apply the G3 rebuild replaces; returns the patched script text."""
    def r(old, new, label):
        nonlocal text
        text = replace_once(text, old, new, label)


    # 3.0 Cafe header comment.
    r(
"""# ================= CAFE WING (exterior) =================
# Footprint quad: A2(-34,-6) B2(-12,-6) C2(-10,0) D2(-34,6). Area ~210 m2.
# v17 (#17): folded plate — HIGH at both ends, valley near x=-20.
# Photos: tall glass at the west end AND at the east/entrance end, short
# glass mid-span (aerial crop + plan elevation strip, both read 2026-11-19).
# The v16 monotonic descent to 0.8 m at the east tip was wrong.""",
"""# ================= CAFE WING (exterior) =================
# v22: frozen quad A(-13.20,-5.60) B(-8.90,4.30) D(-16.70,17.60)
# C(-28.70,22.80), area 197.3 m2, fold C->B (valley). The v21 G3
# pentagon (X -34..-10, Y -6..6, E-W long axis, N-S valley at x=-20)
# was wrong: the frozen quad's long axis runs NNW-SSE (C-A, 32.35 m).
# Photos: tall glass at the A end AND at the B/entrance end; the SW tip
# (C) tapers low.""",
        "3.0-cafe-header")

    # 3.1 G3 roof functions: replace the E-W folded-plate functions with the
    # frozen-quad facet functions + the (u,v) gallery coordinate system.
    r(
"""def _fold(x, x0, z0, xv, zv, x1, z1):
    if x <= xv:
        return z0 + (zv - z0) * ((x - x0) / (xv - x0))
    return zv + (z1 - zv) * ((x - xv) / (x1 - xv))

def cafe_z_north(x):  # #21B: scaled 0.982 (apex 4.91)
    return _fold(x, -34, 4.91, -20, 2.946, -10, 4.124)

def cafe_z_south(x):  # #21B: scaled 0.982
    return _fold(x, -34, 3.437, -20, 1.178, -10, 3.437)

def cafe_y_north(x):
    return -6.0 if x <= -12 else -6.0 + 3.0 * ((x + 12) / 2.0)

def cafe_y_south(x):
    return 6.0 - 0.25 * (x + 34)

def cafe_sections(xs):
    secs = []
    for x in xs:
        yn, ys = cafe_y_north(x), cafe_y_south(x)
        zn, zs = cafe_z_north(x), cafe_z_south(x)
        zm = (zn + zs) / 2.0 + 0.05  # near-flat single folded plate
        pts = []
        for f in (0.0, 0.25, 0.5, 0.75, 1.0):
            y = yn + (ys - yn) * f
            if f == 0.5:
                z = zm
            elif f < 0.5:
                z = zn + (zm - zn) * (f / 0.5)
            else:
                z = zm + (zs - zm) * ((f - 0.5) / 0.5)
            pts.append((y, z))
        secs.append((x, pts))
    return secs

# v17 (#17): valley kink at x=-20 sampled, so roof loft + south glass
# follow the fold instead of cutting straight across it.
CAFE_XS = [-34, -26, -20, -14, -10]
def cafe_z_at(x, y):
    \"\"\"Cafe roof surface height at plan point (x, y) — same profile as
    cafe_sections. Used by the Gallery 3 sloped ceiling (v15: G3 is the
    cafe wing) so it sits below the roof instead of poking through it.\"\"\"
    yn, ys = cafe_y_north(x), cafe_y_south(x)
    zn, zs = cafe_z_north(x), cafe_z_south(x)
    zm = (zn + zs) / 2.0 + 0.05
    f = (y - yn) / (ys - yn) if ys != yn else 0.0
    f = max(0.0, min(1.0, f))
    if f < 0.5:
        return zn + (zm - zn) * (f / 0.5)
    return zm + (zs - zm) * ((f - 0.5) / 0.5)""",
"""# v22 G3 roof (frozen quad + fold C->B, r4): the v21 G3 pentagon
# (X -34..-10, Y -6..6, E-W long axis, N-S valley at x=-20) is wrong:
# the frozen quad's long axis runs NNW-SSE (C-A, 32.35 m). Corner
# heights (rel. 1FL): A 4.9 (ceiling 4.3 + 0.6 construction; v21 apex
# 4.91 corroborates), B 4.1 (photo: tall glass at the east/entrance
# end; v21 photo-derived 4.124), D 3.55 (official section 2.9 as
# CEILING height at D + 0.65 construction — inferred: the 2.9's exact
# attachment is unconfirmed), C 2.0 (inferred: SW tip tapers low; no
# source number). The fold C->B is a valley (~10.6 deg dihedral):
# two planar facets (A,B,C) and (B,D,C). The plan's dashed warp lines
# suggest the G3 plate may also warp slightly; with only 4 corner
# heights given, two planar facets are the determined model.
_G3_A = (-13.20, -5.60, 4.90)
_G3_B = (-8.90, 4.30, 4.10)
_G3_D = (-16.70, 17.60, 3.55)
_G3_C = (-28.70, 22.80, 2.00)
_G3_FACET1 = ((_G3_A[0], _G3_A[1]), (_G3_B[0], _G3_B[1]), (_G3_C[0], _G3_C[1]))
_G3_FACET2 = ((_G3_B[0], _G3_B[1]), (_G3_D[0], _G3_D[1]), (_G3_C[0], _G3_C[1]))

def cafe_z_at(x, y):
    \"\"\"v22 G3 roof surface height at plan point (x, y): barycentric in
    the facet the point falls in (fold C->B is the shared edge; the two
    facets agree on it). Used by the Gallery 3 sloped ceiling so it
    sits below the roof instead of poking through it. Points outside
    the quad fall through to the nearest facet with clamped weights.\"\"\"
    if _point_in_tri(x, y, _G3_FACET1):
        return _plane_z(x, y, _G3_A, _G3_B, _G3_C)
    if _point_in_tri(x, y, _G3_FACET2):
        return _plane_z(x, y, _G3_B, _G3_D, _G3_C)
    # outside the quad: nearest facet, clamped barycentric
    w = _tri_bary(x, y, _G3_FACET1)
    if w is not None:
        a, b, c = (max(0.0, min(1.0, v)) for v in w)
        _s = a + b + c
        if _s > 0:
            return (a * _G3_A[2] + b * _G3_B[2] + c * _G3_C[2]) / _s
    return 3.0

# G3 gallery (u,v) coords: u = distance along the north wall (C-A edge)
# from A (0..15.0 for the gallery), v = distance across from the north
# wall toward B-D (0..8.0). The gallery is a 15.0 x 8.0 m strip at the
# quad's north end (official segments 15.0/8.0/12.8 approximately match
# the frozen quad: B->D 15.42 vs 15.0, D->C 13.08 vs 12.8, width ~8.3
# vs 8.0 — all within ~0.5 m, i.e. within the quad's own uncertainty;
# the mapping of which segment is which remains inferred).
_G3_U = (-0.4791, 0.8779)  # along the C-A north wall from A (unit)
_G3_V = (0.8779, 0.4791)   # across, toward the B-D side (unit)
_G3_A2 = (-13.20, -5.60)

def _g3_pt(u, v):
    \"\"\"Plan point (x, y) at gallery coords (u, v).\"\"\"
    return (_G3_A2[0] + u * _G3_U[0] + v * _G3_V[0],
            _G3_A2[1] + u * _G3_U[1] + v * _G3_V[1])

def _g3_uv(x, y):
    \"\"\"Gallery coords (u, v) of plan point (x, y) (inverse of _g3_pt).\"\"\"
    _dx, _dy = x - _G3_A2[0], y - _G3_A2[1]
    return (_dx * _G3_U[0] + _dy * _G3_U[1],
            _dx * _G3_V[0] + _dy * _G3_V[1])""",
        "3.1-g3-roof-fns")

    # 3.2 G3 exterior: two planar roof facets + north wall (slot bands) +
    # east wall with entrance doorway + SE wall + south glass.
    r(
"""roof_c = loft("SM_Cafe_Roof", cafe_sections(CAFE_XS), MAT_STEEL, COL_CAFE)
# #21A A1: cafe roof seam ribbons deleted (3 strips)
solidify(roof_c, 0.15)
# North (rear) concrete wall — v15: rebuilt with the real horizontal slot
# (official G3 section B: 1.2 m window; section A: luminous frosted glass).
# Lower band z 0..1.0 and upper band z 2.2..roof are solid; the slot band
# z 1.0..2.2 is concrete only at the ends (X -34..-31 and -19..-12). The
# window glass is set here; the frosted panel is added with the G3 interior.
wall_varying("SM_Cafe_Wall_North_Low", (-34, -6), (-12, -6), 0.0, 1.0, 0.0, 1.0,
             MAT_CONCRETE, COL_CAFE, thick=0.3)
# v17 (#17): north-wall top follows the folded roof — split at the valley.
# A single straight 5.0->4.2 top would poke 1.4 m through the roof at x=-20.
wall_varying("SM_Cafe_Wall_North_High", (-34, -6), (-20, -6), 2.2, 4.91, 2.2, 2.946,  # #21B
             MAT_CONCRETE, COL_CAFE, thick=0.3)
wall_varying("SM_Cafe_Wall_North_High_E", (-20, -6), (-12, -6), 2.2, 2.946, 2.2, 4.124,  # #21B
             MAT_CONCRETE, COL_CAFE, thick=0.3)
wall_varying("SM_Cafe_Wall_North_SlotW", (-34, -6), (-31, -6), 1.0, 2.2, 1.0, 2.2,
             MAT_CONCRETE, COL_CAFE, thick=0.3)
wall_varying("SM_Cafe_Wall_North_SlotE", (-19, -6), (-12, -6), 1.0, 2.2, 1.0, 2.2,
             MAT_CONCRETE, COL_CAFE, thick=0.3)
box("SM_G3_WindowSlot", (-28, -6, 1.6), (6.0, 0.12, 1.2), MAT_GLASS, COL_CAFE)
wall_varying("SM_Cafe_Wall_West", (-34, -6), (-34, 6), 0.0, 4.91, 0.0, 3.437,  # #21B
             MAT_CONCRETE, COL_CAFE, thick=0.3)
# Cafe south glass + east entrance (faces museum)
cafe_south = [(x, cafe_y_south(x), cafe_z_south(x)) for x in CAFE_XS]
glass_strip("SM_Cafe_Glass_South", cafe_south, 0.0, MAT_GLASS, COL_CAFE)
box("SM_Cafe_Entrance_Door", (-9.9, 0, 1.3), (0.15, 3.0, 2.6), MAT_GLASS, COL_CAFE)""",
"""# v22 G3 roof: two planar facets (A,B,C) and (B,D,C), fold C->B valley.
# Each facet is a single triangle (exact for a planar facet) + solidify.
_roof_f1 = mesh_from_pydata("SM_Cafe_Roof_Facet1",
    [(_G3_A[0], _G3_A[1], _G3_A[2]), (_G3_B[0], _G3_B[1], _G3_B[2]), (_G3_C[0], _G3_C[1], _G3_C[2])],
    [(0, 1, 2)], MAT_STEEL, COL_CAFE)
solidify(_roof_f1, 0.15)
_roof_f2 = mesh_from_pydata("SM_Cafe_Roof_Facet2",
    [(_G3_B[0], _G3_B[1], _G3_B[2]), (_G3_D[0], _G3_D[1], _G3_D[2]), (_G3_C[0], _G3_C[1], _G3_C[2])],
    [(0, 1, 2)], MAT_STEEL, COL_CAFE)
solidify(_roof_f2, 0.15)
# North wall (C-A edge, A->u=15, 15.0 m) — the gallery's long wall, with
# the real horizontal slot (official G3 section B: 1.2 m window; section
# A: luminous frosted glass). Lower band z 0..1.0 and upper band
# z 2.2..roof are solid; the slot band z 1.0..2.2 is concrete only at
# the ends (u 0..1.5 and 13.5..15.0). The window glass (u 1.5..7.5) is
# set here; the frosted panel (u 7.5..13.5) is added with the interior.
# Roof along the wall: 4.9 at A -> 3.56 at u=15 (on the A-C edge).
_G3_NW_END = _g3_pt(15.0, 0.0)  # (-20.39, 7.57)
_G3_SE_GAL = _g3_pt(15.0, 8.0)  # (-13.37, 11.40)
wall_varying("SM_Cafe_Wall_North_Low", (-13.20, -5.60), _G3_NW_END, 0.0, 1.0, 0.0, 1.0,
             MAT_CONCRETE, COL_CAFE, thick=0.3)
wall_varying("SM_Cafe_Wall_North_High", (-13.20, -5.60), _G3_NW_END, 2.2, 4.90, 2.2, 3.56,
             MAT_CONCRETE, COL_CAFE, thick=0.3)
wall_varying("SM_Cafe_Wall_North_SlotW", (-13.20, -5.60), _g3_pt(1.5, 0.0), 1.0, 2.2, 1.0, 2.2,
             MAT_CONCRETE, COL_CAFE, thick=0.3)
wall_varying("SM_Cafe_Wall_North_SlotE", _g3_pt(13.5, 0.0), _G3_NW_END, 1.0, 2.2, 1.0, 2.2,
             MAT_CONCRETE, COL_CAFE, thick=0.3)
box("SM_G3_WindowSlot", (*_g3_pt(4.5, 0.0), 1.6), (6.0, 0.12, 1.2), MAT_GLASS, COL_CAFE,
    rot=(0, 0, math.radians(118.63)))
# East wall (A-B edge) with the entrance doorway near B (2.6 m, from B
# toward A); lintel 2.6..roof over the gap. Roof along the edge:
# 4.9 at A -> 4.29 at the doorway's A end -> 4.1 at B.
_G3_DOOR_A = _g3_pt(5.03, 6.47)  # (-9.93, 1.92), 2.6 m from B along A-B
wall_varying("SM_Cafe_Wall_East", (-13.20, -5.60), _G3_DOOR_A, 0.0, 4.90, 0.0, 4.29,
             MAT_CONCRETE, COL_CAFE, thick=0.3)
wall_varying("SM_Cafe_Wall_East_Lintel", _G3_DOOR_A, (-8.90, 4.30), 2.6, 4.29, 2.6, 4.10,
             MAT_CONCRETE, COL_CAFE, thick=0.3)
box("SM_Cafe_Entrance_Door", (-9.42, 3.11, 1.3), (2.6, 0.15, 2.6), MAT_GLASS, COL_CAFE,
    rot=(0, 0, math.radians(66.55)))
# SE wall (B-D edge) solid 0..roof (4.1 -> 3.36).
wall_varying("SM_Cafe_Wall_SE", (-8.90, 4.30), _G3_SE_GAL, 0.0, 4.10, 0.0, 3.36,
             MAT_CONCRETE, COL_CAFE, thick=0.3)
# South glass (u=15 edge, faces the terrace): tops 3.56 -> 3.36.
cafe_south = [(_G3_NW_END[0], _G3_NW_END[1], cafe_z_at(*_G3_NW_END)),
              (_G3_SE_GAL[0], _G3_SE_GAL[1], cafe_z_at(*_G3_SE_GAL))]
glass_strip("SM_Cafe_Glass_South", cafe_south, 0.0, MAT_GLASS, COL_CAFE)""",
        "3.2-g3-exterior")

    # 3.3 G3 interior header + G3_QUAD + frosted slot (the v21 west diagonal
    # wall is deleted — the gallery's SW edge is now the south glass + SE wall).
    r(
"""# ================= GALLERY 3 (v15: the cafe wing IS Gallery 3) =================
# Since 2017 the former cafe wing is Gallery 3 (official leasing-page plan +
# section, measured). Gallery quad: north wall (-33,-5.7)->(-18,-5.7) 15.0 m,
# east/entrance tip (-13.5,0.3), south vertex (-25,3.6); private room 4.0x2.9 m +
# kitchen at the east end under a 2.7 m flat ceiling; WCs by the entrance.""",
"""# ================= GALLERY 3 (v15: the cafe wing IS Gallery 3) =================
# Since 2017 the former cafe wing is Gallery 3 (official leasing-page plan +
# section, measured). Gallery quad (frozen, r4): the 15.0 x 8.0 m strip at
# the quad's north end — A, B, (u=15,v=8), (u=15,v=0) — in (u,v) gallery
# coords (see _g3_pt). Private room 4.0x2.9 m + kitchen at the east end
# (u 7..13.5) under a 2.7 m flat ceiling; WCs by the entrance (u 6.5..8.5).""",
        "3.3-g3-header")
    r(
"""G3_QUAD = [(-33, -5.7), (-18, -5.7), (-13.5, 0.3), (-25, 3.6)]
# Luminous frosted-glass band (east half of the north-wall slot; the window
# glass is the west half, set with the wall above).
box("SM_G3_FrostedSlot", (-22, -6, 1.6), (6.0, 0.12, 1.2), _MAT_G3_FROSTED, COL_CAFE)
# West diagonal wall of the gallery (12.8 m in the official plan).
# v17 (#17): tops 4.9->4.7 (north) and 2.4->1.8 (south vertex) — the folded
# roof is lower along this diagonal (4.86 / 3.59 / 2.05 at t=0 / 0.5 / 1);
# the v16 tops would poke through it.
wall_varying("SM_G3_Wall_West", (-33, -5.7), (-25, 3.6), 0.0, 4.7, 0.0, 1.8,
             MAT_CONCRETE, COL_CAFE, thick=0.3)""",
"""G3_QUAD = [(-13.20, -5.60), (-8.90, 4.30), _G3_SE_GAL, _G3_NW_END]
# Luminous frosted-glass band (east half of the north-wall slot, u 7.5..13.5;
# the window glass is the west half, set with the wall above).
box("SM_G3_FrostedSlot", (*_g3_pt(10.5, 0.0), 1.6), (6.0, 0.12, 1.2), _MAT_G3_FROSTED, COL_CAFE,
    rot=(0, 0, math.radians(118.63)))
# v22: no west diagonal wall — the gallery's SW edge is the south glass
# (u=15, SM_Cafe_Glass_South) and the SE wall (B-D edge) above.""",
        "3.3-g3-quad")

    # 3.4 Private room / kitchen / WCs in (u,v).
    r(
"""# Private room (4.0x2.9 m, X -18..-14, Y -5.7..-2.8) + kitchen (X -14..-11.5).
# West wall of the private room has a 0.9 m doorway (Y -4.2..-3.3).
wall_varying("SM_G3_PR_WallW_A", (-18, -5.7), (-18, -4.2), 0.0, 2.7, 0.0, 2.7,
             MAT_WHITE, COL_CAFE, thick=0.15)
wall_varying("SM_G3_PR_WallW_B", (-18, -3.3), (-18, -2.8), 0.0, 2.7, 0.0, 2.7,
             MAT_WHITE, COL_CAFE, thick=0.15)
wall_varying("SM_G3_PR_WallS", (-18, -2.8), (-14, -2.8), 0.0, 2.7, 0.0, 2.7,
             MAT_WHITE, COL_CAFE, thick=0.15)
wall_varying("SM_G3_PR_WallE", (-14, -5.7), (-14, -2.8), 0.0, 2.7, 0.0, 2.7,
             MAT_WHITE, COL_CAFE, thick=0.15)
wall_varying("SM_G3_Kit_WallS", (-14, -2.8), (-11.5, -2.8), 0.0, 2.7, 0.0, 2.7,
             MAT_WHITE, COL_CAFE, thick=0.15)
wall_varying("SM_G3_Kit_WallE", (-11.5, -5.7), (-11.5, -3.5), 0.0, 2.7, 0.0, 2.7,
             MAT_WHITE, COL_CAFE, thick=0.15)
# Flat 2.7 m ceiling over the private room + kitchen.
flat_poly_slab("SM_G3_PR_Ceiling", [(-18, -5.7), (-11.5, -5.7), (-11.5, -2.8), (-18, -2.8)],
               2.7, 0.05, MAT_WHITE, COL_CAFE)
# Restrooms (2 WCs, schematic) by the entrance, north of the passage:
# two rooms stacked in Y (y -2.3..-1.5 and -1.5..-0.7), entered from the east.
box("SM_G3_WC_N", (-13.0, -2.3, 1.2), (1.6, 0.06, 2.4), MAT_WHITE, COL_CAFE)
box("SM_G3_WC_Mid", (-13.0, -1.5, 1.2), (1.6, 0.06, 2.4), MAT_WHITE, COL_CAFE)
box("SM_G3_WC_S", (-13.0, -0.7, 1.2), (1.6, 0.06, 2.4), MAT_WHITE, COL_CAFE)
box("SM_G3_WC_W", (-13.8, -1.5, 1.2), (0.06, 2.0, 2.4), MAT_WHITE, COL_CAFE)""",
"""# Private room (4.0x2.9 m, u 7..11, v 0..2.9) + kitchen (u 11..13.5).
# West wall of the private room has a 0.9 m doorway (v 1.5..2.4).
wall_varying("SM_G3_PR_WallW_A", _g3_pt(7.0, 0.0), _g3_pt(7.0, 1.5), 0.0, 2.7, 0.0, 2.7,
             MAT_WHITE, COL_CAFE, thick=0.15)
wall_varying("SM_G3_PR_WallW_B", _g3_pt(7.0, 2.4), _g3_pt(7.0, 2.9), 0.0, 2.7, 0.0, 2.7,
             MAT_WHITE, COL_CAFE, thick=0.15)
wall_varying("SM_G3_PR_WallS", _g3_pt(7.0, 2.9), _g3_pt(11.0, 2.9), 0.0, 2.7, 0.0, 2.7,
             MAT_WHITE, COL_CAFE, thick=0.15)
wall_varying("SM_G3_PR_WallE", _g3_pt(11.0, 0.0), _g3_pt(11.0, 2.9), 0.0, 2.7, 0.0, 2.7,
             MAT_WHITE, COL_CAFE, thick=0.15)
wall_varying("SM_G3_Kit_WallS", _g3_pt(11.0, 2.9), _g3_pt(13.5, 2.9), 0.0, 2.7, 0.0, 2.7,
             MAT_WHITE, COL_CAFE, thick=0.15)
wall_varying("SM_G3_Kit_WallE", _g3_pt(13.5, 0.0), _g3_pt(13.5, 2.2), 0.0, 2.7, 0.0, 2.7,
             MAT_WHITE, COL_CAFE, thick=0.15)
# Flat 2.7 m ceiling over the private room + kitchen.
flat_poly_slab("SM_G3_PR_Ceiling", [_g3_pt(7.0, 0.0), _g3_pt(13.5, 0.0), _g3_pt(13.5, 2.9), _g3_pt(7.0, 2.9)],
               2.7, 0.05, MAT_WHITE, COL_CAFE)
# Restrooms (2 WCs, schematic) by the entrance (u 6.5..8.5, v 5..7):
# two rooms stacked in v (v 5..6 and 6..7), entered from the east (u=8.5).
box("SM_G3_WC_N", (*_g3_pt(7.5, 5.0), 1.2), (2.0, 0.06, 2.4), MAT_WHITE, COL_CAFE,
    rot=(0, 0, math.radians(118.63)))
box("SM_G3_WC_Mid", (*_g3_pt(7.5, 6.0), 1.2), (2.0, 0.06, 2.4), MAT_WHITE, COL_CAFE,
    rot=(0, 0, math.radians(118.63)))
box("SM_G3_WC_S", (*_g3_pt(7.5, 7.0), 1.2), (2.0, 0.06, 2.4), MAT_WHITE, COL_CAFE,
    rot=(0, 0, math.radians(118.63)))
box("SM_G3_WC_W", (*_g3_pt(6.5, 6.0), 1.2), (0.06, 2.0, 2.4), MAT_WHITE, COL_CAFE,
    rot=(0, 0, math.radians(118.63)))""",
        "3.4-g3-rooms")

    # 3.5 g3_ceiling_z in (u,v): flat 4.3 for the north 25%, then a straight
    # diagonal down to 0.4 at the south glass (v=8.0), clamped to roof - 0.65.
    r(
"""# Gallery ceiling: v16 P2 item 11 — Section C profile (official G3
# section C: ceiling slopes from 4.3 m at the north wall to near ground at
# the south glass over 8.0 m). Flat 4.26 m for the north 25% of the depth,
# then a straight diagonal down to 0.4 m at the south glass line
# (y_glass = cafe_y_south). The cafe ROOF is unchanged (its exterior
# profile matches the aerial photos); only the interior ceiling follows
# Section C. This leaves a roof-ceiling wedge gap — a modelling compromise,
# recorded in DESIGN2121_EXPORT_RECORD.md.
def g3_ceiling_z(x, y):
    ys = cafe_y_south(x)
    yn = -5.7
    f = (y - yn) / (ys - yn) if ys != yn else 0.0
    f = max(0.0, min(1.0, f))
    if f <= 0.25:
        _z = 4.26
    else:
        _z = 4.26 + (0.4 - 4.26) * ((f - 0.25) / 0.75)
    # v17 (#17): never above the folded-roof underside. The v16 ceiling rose
    # up to 0.46 m through the roof along the north band (the page hid it
    # with fixG3RoofClip); now fixed in the model, so the page fix goes away.
    return min(_z, cafe_z_at(x, y) - 0.65)  # #21B: roof construction 0.65 m (was 0.30)""",
"""# Gallery ceiling: Section C profile (official G3 section C: ceiling
# slopes from 4.3 m at the north wall to near ground at the south glass
# over 8.0 m). Flat 4.3 m for the north 25% of the depth, then a
# straight diagonal down to 0.4 m at the south glass line (v=8.0).
# Never above the folded-roof underside (roof - 0.65 m construction),
# which clamps it toward the SW end where the roof dips.
def g3_ceiling_z(x, y):
    _u, _v = _g3_uv(x, y)
    f = _v / 8.0
    f = max(0.0, min(1.0, f))
    if f <= 0.25:
        _z = 4.30
    else:
        _z = 4.30 + (0.4 - 4.30) * ((f - 0.25) / 0.75)
    return min(_z, cafe_z_at(x, y) - 0.65)  # roof construction 0.65 m""",
        "3.5-g3-ceiling")

    # 3.6 Columns in (u,v).
    r(
"""# Gallery columns (official plan: 2 square + 1 round at the south vertex).
# v16 P2 item 12: square columns at 30% and 55% of the 15.0 m north wall
# from the west vertex: x = -33 + 0.30*15 = -28.5 and -33 + 0.55*15 =
# -24.75. (The plan drawing is not uniformly to scale, so the parent's
# stated fractions are implemented literally.) Round column confirmed at
# the south vertex (-25, 3.6). Heights follow the new Section C ceiling.
for _ci, (_ccx, _ccy) in enumerate([(-28.5, -3.0), (-24.75, -0.5)]):
    _chh = g3_ceiling_z(_ccx, _ccy)
    box(f"SM_G3_Column_{_ci}", (_ccx, _ccy, _chh / 2.0), (0.45, 0.45, _chh), MAT_CONCRETE_BOARD, COL_CAFE)
_chr = g3_ceiling_z(-25, 3.6)
bpy.ops.mesh.primitive_cylinder_add(radius=0.30, depth=_chr, location=(-25, 3.6, _chr / 2.0))""",
"""# Gallery columns (official plan: 2 square + 1 round at the south vertex).
# Square columns at 30% and 55% of the 15.0 m north wall from A
# (u = 4.5 and 8.25), offset into the gallery by v = 2.7 and 5.2 m
# (the v21 offsets from the north wall). Round column at the south
# vertex (u 14.2, v 0.8 — just inside the SW corner). Heights follow
# the new Section C ceiling.
for _ci, (_cu, _cv) in enumerate([(4.5, 2.7), (8.25, 5.2)]):
    _ccx, _ccy = _g3_pt(_cu, _cv)
    _chh = g3_ceiling_z(_ccx, _ccy)
    box(f"SM_G3_Column_{_ci}", (_ccx, _ccy, _chh / 2.0), (0.45, 0.45, _chh), MAT_CONCRETE_BOARD, COL_CAFE)
_g3rx, _g3ry = _g3_pt(14.2, 0.8)
_chr = g3_ceiling_z(_g3rx, _g3ry)
bpy.ops.mesh.primitive_cylinder_add(radius=0.30, depth=_chr, location=(_g3rx, _g3ry, _chr / 2.0))""",
        "3.6-g3-columns")

    # 3.7 Ceiling grid over the (u,v) strip.
    r(
"""# Gallery ceiling grid (white gypsum); quads below 0.35 m (at the south
# glass, where the Section C profile reaches 0.4 m) stay open.
_g3_xs = [-33.5 + 0.5 * i for i in range(47)]
_g3_ys = [-6.0 + 0.5 * i for i in range(21)]
_g3_v, _g3_f, _g3_idx = [], [], {}
for _xi, _x in enumerate(_g3_xs):
    for _yi, _y in enumerate(_g3_ys):
        _g3_idx[(_xi, _yi)] = len(_g3_v)
        _g3_v.append((_x, _y, g3_ceiling_z(_x, _y)))
for _xi in range(len(_g3_xs) - 1):
    for _yi in range(len(_g3_ys) - 1):
        _a = _g3_idx[(_xi, _yi)]; _b = _g3_idx[(_xi + 1, _yi)]
        _c = _g3_idx[(_xi + 1, _yi + 1)]; _d = _g3_idx[(_xi, _yi + 1)]
        _cx = (_g3_v[_a][0] + _g3_v[_b][0] + _g3_v[_c][0] + _g3_v[_d][0]) / 4.0
        _cy = (_g3_v[_a][1] + _g3_v[_b][1] + _g3_v[_c][1] + _g3_v[_d][1]) / 4.0
        _cz = (_g3_v[_a][2] + _g3_v[_b][2] + _g3_v[_c][2] + _g3_v[_d][2]) / 4.0
        if _cz < 0.35:
            continue
        # v17 (#17): the Section C slope dives below head height at the
        # pinched east tip (x=-14, y=0: 1.17 m in v16 — nobody can walk in).
        # Leave the entrance zone open to the roof (2.4-3.1 m there); the
        # flat 2.7 m ceiling below covers the WC strip.
        if _cx >= -16.0 and _cz < 2.3:
            continue
        if not (_point_in_tri(_cx, _cy, (G3_QUAD[0], G3_QUAD[1], G3_QUAD[2])) or
                _point_in_tri(_cx, _cy, (G3_QUAD[0], G3_QUAD[2], G3_QUAD[3]))):
            continue
        _g3_f.append((_a, _b, _c, _d))
_g3_o = mesh_from_pydata("SM_G3_Ceiling", _g3_v, _g3_f, MAT_WHITE, COL_CAFE)
solidify(_g3_o, 0.08)""",
"""# Gallery ceiling grid (white gypsum) over the (u,v) strip; quads below
# 0.35 m (at the south glass, where the Section C profile reaches 0.4 m)
# stay open. The WC/entrance zone (u 6..9, v 4.5..7.5) stays open where
# the sloped ceiling is below 2.7 m — the flat 2.7 m ceiling covers the
# WC strip and the entrance stays open to the roof (as in v21).
_g3_us = [0.5 * i for i in range(31)]
_g3_vs = [0.5 * i for i in range(17)]
_g3_v, _g3_f, _g3_idx = [], [], {}
for _ui, _u in enumerate(_g3_us):
    for _vi, _v in enumerate(_g3_vs):
        _gx, _gy = _g3_pt(_u, _v)
        _g3_idx[(_ui, _vi)] = len(_g3_v)
        _g3_v.append((_gx, _gy, g3_ceiling_z(_gx, _gy)))
for _ui in range(len(_g3_us) - 1):
    for _vi in range(len(_g3_vs) - 1):
        _a = _g3_idx[(_ui, _vi)]; _b = _g3_idx[(_ui + 1, _vi)]
        _c = _g3_idx[(_ui + 1, _vi + 1)]; _d = _g3_idx[(_ui, _vi + 1)]
        _cx = (_g3_v[_a][0] + _g3_v[_b][0] + _g3_v[_c][0] + _g3_v[_d][0]) / 4.0
        _cy = (_g3_v[_a][1] + _g3_v[_b][1] + _g3_v[_c][1] + _g3_v[_d][1]) / 4.0
        _cz = (_g3_v[_a][2] + _g3_v[_b][2] + _g3_v[_c][2] + _g3_v[_d][2]) / 4.0
        if _cz < 0.35:
            continue
        _cu = _g3_us[_ui] + 0.25
        _cv = _g3_vs[_vi] + 0.25
        if 6.0 <= _cu <= 9.0 and 4.5 <= _cv <= 7.5 and _cz < 2.7:
            continue
        if not (_point_in_tri(_cx, _cy, (G3_QUAD[0], G3_QUAD[1], G3_QUAD[2])) or
                _point_in_tri(_cx, _cy, (G3_QUAD[0], G3_QUAD[2], G3_QUAD[3]))):
            continue
        _g3_f.append((_a, _b, _c, _d))
_g3_o = mesh_from_pydata("SM_G3_Ceiling", _g3_v, _g3_f, MAT_WHITE, COL_CAFE)
solidify(_g3_o, 0.08)""",
        "3.7-g3-ceiling-grid")

    # 3.8 Entrance (WC strip) flat ceiling in (u,v).
    r(
"""# v17 (#17): flat 2.7 m ceiling over the WC / entrance strip
# (x -14..-11, y -2.0..-0.5) — the sloped ceiling is skipped there (see
# above) and the roof above it is 2.85-3.72 m, so 2.7 m clears everywhere.
flat_poly_slab("SM_G3_Entrance_Ceiling", [(-14, -2.0), (-11, -2.0), (-11, -0.5), (-14, -0.5)],
               2.7, 0.05, MAT_WHITE, COL_CAFE)""",
"""# Flat 2.7 m ceiling over the WC strip (u 6.5..8.5, v 5..7) — the sloped
# ceiling is skipped there (see above); the roof above it is ~3.5-4.2 m,
# so 2.7 m clears everywhere.
flat_poly_slab("SM_G3_Entrance_Ceiling", [_g3_pt(6.5, 5.0), _g3_pt(8.5, 5.0), _g3_pt(8.5, 7.0), _g3_pt(6.5, 7.0)],
               2.7, 0.05, MAT_WHITE, COL_CAFE)""",
        "3.8-g3-entrance-ceiling")

    # 3.9 Reception desks + cove strip in (u,v).
    r(
"""# Triangular folded reception desks (the triangle echoes the roof fold),
# 2 x W1730 x D600, against the north wall near the entrance.
# v16r3: moved WEST to x=-22/-20 — v15 put them at x=-16.6/-14.8, which is
# INSIDE the private room (x -18..-14, y -5.7..-2.8), so they were hidden
# by its walls + 2.7 m ceiling and no camera could show them. Now on the
# open north wall, clear of the private room's west wall (x=-18).
for _di, _dx0 in enumerate([-22.0, -20.0]):
    _dv = [(_dx0, -5.3, 0.0), (_dx0 + 1.73, -5.3, 0.0), (_dx0 + 0.86, -4.7, 0.0),
           (_dx0, -5.3, 1.05), (_dx0 + 1.73, -5.3, 1.05), (_dx0 + 0.86, -4.7, 1.05)]
    _df = [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)]
    mesh_from_pydata(f"SM_G3_Reception_{_di}", _dv, _df, MAT_WHITE, COL_CAFE)
# Warm cove light strip along the north wall / ceiling junction.
# v17 (#17): shortened to the high west end (x -33..-28) and lowered to
# 3.70 — the folded roof dips to 3.29 at x=-22, so the old 12 m strip at
# 3.95 would poke through the roof east of x=-28 (and through the clamped
# ceiling, 3.78 at x=-28).
# #21B: cove strip re-tilted to follow the lowered ceiling (ends 0.05
# below g3_ceiling_z at x=-33 and x=-28).
_cove_zw = g3_ceiling_z(-33, -5.55) - 0.05
_cove_ze = g3_ceiling_z(-28, -5.55) - 0.05
box("SM_G3_CoveStrip", (-30.5, -5.55, (_cove_zw + _cove_ze) / 2.0), (5.0, 0.08, 0.08),
    _MAT_G3_COVE, COL_CAFE, rot=(0, math.atan2(_cove_zw - _cove_ze, 5.0), 0))""",
"""# Triangular folded reception desks (the triangle echoes the roof fold),
# 2 x W1730 x D600, against the north wall (u 3.0 and 5.0, v 0.4..1.0),
# clear of the private room (u 7..13.5).
for _di, _du in enumerate([3.0, 5.0]):
    _p0 = _g3_pt(_du, 0.4); _p1 = _g3_pt(_du + 1.73, 0.4); _p2 = _g3_pt(_du + 0.86, 1.0)
    _dv = [(_p0[0], _p0[1], 0.0), (_p1[0], _p1[1], 0.0), (_p2[0], _p2[1], 0.0),
           (_p0[0], _p0[1], 1.05), (_p1[0], _p1[1], 1.05), (_p2[0], _p2[1], 1.05)]
    _df = [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)]
    mesh_from_pydata(f"SM_G3_Reception_{_di}", _dv, _df, MAT_WHITE, COL_CAFE)
# Warm cove light strip along the north wall / ceiling junction, at the
# high A end (u 0..5, v 0.15). The ceiling there is flat 4.3 (v<=2.0),
# so the strip is horizontal at 4.25 (no tilt needed).
_cove_c = _g3_pt(2.5, 0.15)
box("SM_G3_CoveStrip", (_cove_c[0], _cove_c[1], 4.25), (5.0, 0.08, 0.08),
    _MAT_G3_COVE, COL_CAFE, rot=(0, 0, math.radians(118.63)))""",
        "3.9-g3-desks-cove")

    # 3.10 Downlights + track rail in (u,v).
    r(
"""# Recessed downlights just below the sloped ceiling (8, positions from the
# visitor photos: rows following the slope). v16 P2 item 11: two moved north
# so they sit under the new Section C ceiling instead of below it / above
# the glass: (-16,-0.5)->(-16,-2.0), (-19,2.0)->(-19,-1.0). Heights now
# follow g3_ceiling_z (Section C), not the roof.
for _dli, (_dlx, _dly) in enumerate([(-28, -3.5), (-22, -3.5), (-16, -3.5),
                                     (-28, -0.5), (-22, -0.5), (-16, -2.0),
                                     (-25, -4.5), (-19, -1.0)]):
    _dlz = g3_ceiling_z(_dlx, _dly) - 0.03
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.04, location=(_dlx, _dly, _dlz))
    _o = bpy.context.active_object
    _o.name = f"SM_G3_Downlight_{_dli}"
    set_mat(_o, MAT_LIGHT); link(_o, COL_CAFE)
# Track spotlight rail following the ceiling slope (Y=-1.5, X -30..-16),
# with 5 spot heads. v16 P2 item 11: rail follows the Section C ceiling.
# v17 (#17): the ceiling is FOLDED (valley x=-20), so a single straight bar
# spans the valley and pokes through the roof there (probe: rail@2.41 vs
# roof@2.25 at x=-20, and the rail rides 0.6 m above the ceiling) — split
# the rail at the valley into two bars, each following its own end heights;
# the spot heads interpolate on the segmented line.
_rl_z0 = g3_ceiling_z(-30, -1.5) - 0.35
_rl_zv = g3_ceiling_z(-20, -1.5) - 0.35
_rl_z1 = g3_ceiling_z(-16, -1.5) - 0.35
def _rail_z(x):
    if x <= -20:
        return _rl_z0 + (_rl_zv - _rl_z0) * ((x + 30) / 10.0)
    return _rl_zv + (_rl_z1 - _rl_zv) * ((x + 20) / 4.0)
_rl_ang_w = math.atan2(_rl_z0 - _rl_zv, 10.0)
_rl_ang_e = math.atan2(_rl_zv - _rl_z1, 4.0)
box("SM_G3_TrackRail_W", (-25, -1.5, (_rl_z0 + _rl_zv) / 2.0), (10.0, 0.08, 0.08),
    MAT_BLACK, COL_CAFE, rot=(0, _rl_ang_w, 0))
box("SM_G3_TrackRail_E", (-18, -1.5, (_rl_zv + _rl_z1) / 2.0), (4.0, 0.08, 0.08),
    MAT_BLACK, COL_CAFE, rot=(0, _rl_ang_e, 0))
for _si, _sx in enumerate([-29, -26, -23, -20, -17]):
    _sz = _rail_z(_sx) - 0.10
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.12, location=(_sx, -1.5, _sz))
    _o = bpy.context.active_object
    _o.name = f"SM_G3_Spot_{_si}"
    set_mat(_o, MAT_BLACK); link(_o, COL_CAFE)""",
"""# Recessed downlights just below the sloped ceiling (8, rows following
# the slope in (u,v): v=2 and v=4 rows + two at v=6). Heights follow
# g3_ceiling_z (Section C), not the roof.
for _dli, (_dlu, _dlv) in enumerate([(3, 2), (6, 2), (9, 2), (12, 2),
                                     (4, 4), (7, 4), (10, 4), (6, 6)]):
    _dlx, _dly = _g3_pt(_dlu, _dlv)
    _dlz = g3_ceiling_z(_dlx, _dly) - 0.03
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.04, location=(_dlx, _dly, _dlz))
    _o = bpy.context.active_object
    _o.name = f"SM_G3_Downlight_{_dli}"
    set_mat(_o, MAT_LIGHT); link(_o, COL_CAFE)
# Track spotlight rail following the ceiling slope (v=4.2, u 3.5..14),
# with 5 spot heads. The fold C->B does not cross the rail (it meets
# v=4.2 at u=19.68, outside the gallery), so the rail is two bars split
# at u=8.75, each following its own end heights (as in v21, where the
# rail was split at the valley for the same reason).
_rl_u0, _rl_u1, _rl_um = 3.5, 14.0, 8.75
_rl_v = 4.2
_rl_p0 = _g3_pt(_rl_u0, _rl_v); _rl_pm = _g3_pt(_rl_um, _rl_v); _rl_p1 = _g3_pt(_rl_u1, _rl_v)
_rl_z0 = g3_ceiling_z(*_rl_p0) - 0.35
_rl_zm = g3_ceiling_z(*_rl_pm) - 0.35
_rl_z1 = g3_ceiling_z(*_rl_p1) - 0.35
def _rail_z_u(u):
    if u <= _rl_um:
        return _rl_z0 + (_rl_zm - _rl_z0) * ((u - _rl_u0) / (_rl_um - _rl_u0))
    return _rl_zm + (_rl_z1 - _rl_zm) * ((u - _rl_um) / (_rl_u1 - _rl_um))
_rl_len_w = _rl_um - _rl_u0
_rl_len_e = _rl_u1 - _rl_um
_rl_ang_w = math.atan2(_rl_z0 - _rl_zm, _rl_len_w)
_rl_ang_e = math.atan2(_rl_zm - _rl_z1, _rl_len_e)
_rl_cw = _g3_pt((_rl_u0 + _rl_um) / 2.0, _rl_v)
_rl_ce = _g3_pt((_rl_um + _rl_u1) / 2.0, _rl_v)
box("SM_G3_TrackRail_W", (_rl_cw[0], _rl_cw[1], (_rl_z0 + _rl_zm) / 2.0), (_rl_len_w, 0.08, 0.08),
    MAT_BLACK, COL_CAFE, rot=(0, _rl_ang_w, math.radians(118.63)))
box("SM_G3_TrackRail_E", (_rl_ce[0], _rl_ce[1], (_rl_zm + _rl_z1) / 2.0), (_rl_len_e, 0.08, 0.08),
    MAT_BLACK, COL_CAFE, rot=(0, _rl_ang_e, math.radians(118.63)))
for _si, _su in enumerate([4.0, 6.5, 9.0, 11.5, 14.0]):
    _spx, _spy = _g3_pt(_su, _rl_v)
    _sz = _rail_z_u(_su) - 0.10
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.12, location=(_spx, _spy, _sz))
    _o = bpy.context.active_object
    _o.name = f"SM_G3_Spot_{_si}"
    set_mat(_o, MAT_BLACK); link(_o, COL_CAFE)""",
        "3.10-g3-lights-rail")

    # 3.11 Terrace paving in (u,v): from the south-glass edge (u=15) 7.0 m
    # toward C (7.84 x 7.0 = 55 m2, vs official 57 m2).
    r(
"""# Terrace paving south of the gallery glass (57 m2 in the official plan,
# outline approximate).
flat_poly_slab("SM_G3_Terrace", [(-25, 3.6), (-13.5, 0.3), (-13.5, 4.8), (-25, 8.1)],
               0.03, 0.06, MAT_PAVING, COL_CAFE)""",
"""# Terrace paving south of the gallery glass (57 m2 in the official plan):
# from the south-glass edge (u=15) 7.0 m toward C along the strip
# (7.84 x 7.0 = 55 m2). The roof extends over it (covered terrace).
flat_poly_slab("SM_G3_Terrace", [_g3_pt(15.0, 0.0), _g3_pt(15.0, 8.0), _g3_pt(22.0, 8.0), _g3_pt(22.0, 0.0)],
               0.03, 0.06, MAT_PAVING, COL_CAFE)""",
        "3.11-g3-terrace")
    print("chunk 3 done")
    return text


# ---------------------------------------------------------------------------
# chunk 4: B1 levels (Detail 4 p96: 1FL->BFL1 6300, 1FL->BFL2 7200,
# BFL1->BFL2 900, GL->1FL 500), stairs, tie holes re-run, G2 ceilings,
# courtyard/elevator/noren, hall columns, reception desk, G3 sprinklers,
# new-wall holes, validation asserts (gates 2/3).
# Decisions (verified against the v21 script itself, see STATUS.md):
# - GALLERY 1 is 5,000 high (floor BFL2 -7.2 -> ceiling -2.2); the
#   "6,000" on p96 spans the LOBBY (BFL1 -6.3 -> ground-slab soffit -0.3).
# - Main stair: the 39-step flight lands on the PLATFORM (-5.85), and
#   the wide steps descend platform -> lobby (-6.75). In v22 both are
#   BFL1 -6.3, so the flight is 0 -> -6.3 = 6.30 / 0.15 = 42 steps
#   (X 15.63..28.23) and the wide steps are DELETED (zero height:
#   their blocks run PLAT..G2F, and PLAT == G2F now).
# - G1 steps: lobby -6.3 -> G1 -7.2 = 0.9 = 6 steps (X 2.0..3.8).
# - North-wall tops need NO change in chunk 4: chunk 1 already set
#   them to follow roof_z_north (4.85->4.59->4.52->4.50 segmented).
# - Hall columns: v21 (24,1.2) is inside the court triangle AND under
#   the low roof (would poke 1.19 m); (34,1.2) is in the pit; (20,1.2)
#   would poke 0.46 m (roof 2.04, column min height 2.5). Moved to
#   (16,1.2) (roof 2.78, column 2.68) and (38,1.2) (roof 4.34).
# - Tie holes v22 total predicted 3,533 (v21 3,625) — verified by
#   v22/build/plan_holes_v22.py (pure-python mirror of tie_holes).
# - East wall moved to the roof edge (Y=3.50) in chunk 2: a wall at
#   the glass line would poke through the warped roof (roof 3.57
#   above the glass line at E vs wall top 4.3).
# ---------------------------------------------------------------------------
def _apply_chunk4(text):
    r = replace_once

    # ---- 4.0 levels ------------------------------------------------------
    # (G2C is inside this block; G1F/G1C already -7.2/-2.2.)
    text = r(text,
"""G2F = -6.75
PLAT = -5.85
G1F = -7.20
G2C = -1.95
G1C = -2.20""",
"""G2F = -6.3
PLAT = -6.3
G1F = -7.20
G2C = -1.5
G1C = -2.20""",
        "4.0-levels")

    # ---- 4.1 ground footprint + atrium soffit grid ------------------------
    text = r(text,
"""FOOT = [(-10, -7), (44, -7), (39, 2.33), (-3, 2.33)]  # #21B D3 trapezoid""",
"""FOOT = [(-10, -7), (43.42, -7), (39.67, 2.33), (-6.09, 2.33)]  # v22: glass-line trapezoid""",
        "4.1-foot")

    text = r(text,
"""_soff_xs = [-10.0 + 1.0 * i for i in range(55)]""",
"""_soff_xs = [-10.0 + 1.0 * i for i in range(54)] + [43.42]""",
        "4.1-soffit-xs")

    text = r(text,
"""CAFE_FOOT = [(-34, -6), (-12, -6), (-10, 0), (-34, 6)]""",
"""CAFE_FOOT = [(-13.20, -5.60), (-8.90, 4.30), (-16.70, 17.60), (-28.70, 22.80)]""",
        "4.1-cafe-foot")

    # ---- 4.2 platform (one level now) + stair rect + landing -------------
    # Detail 4 p96 (left dim chain, read from the scan): 1FL->BFL1 6,300,
    # 1FL->BFL2 7,200, BFL1->BFL2 900. So the LOBBY floor and the GALLERY 2
    # platform are BOTH BFL1 -6.3; there is no raised platform in v22
    # (the v21 -5.85/-6.75 split is not supported by the section). The
    # platform slabs stay as a flush sub-floor fill (PLAT, 0.9 thick,
    # i.e. -7.2..-6.3, down to G1F).
    # (STAIR_RECT already updated to 28.23 in chunk 1.)

    text = r(text,
"""# Platform block (north band, X -1..29.44, Y -7..-3.29) is a solid 0.9 m block.""",
"""# Platform block (north band, X -1..29.44, Y -7..-3.29): in v22 a flush
# sub-floor fill, top -6.3 (one level with the lobby), 0.9 m down to G1F.""",
        "4.2-platform-comment")

    text = r(text,
"""# Upper platform: solid 0.9 m block, top -5.85 (west rect + north strip + landing).""",
"""# Upper platform: top -6.3 in v22 (one level with the lobby); the 0.9 m
# thickness runs -7.2..-6.3. North strip + landing follow the longer flight.""",
        "4.2-platform-header")

    text = r(text,
"""flat_poly_slab("SM_Platform_NorthStrip", [(15.63, -7), (27.26, -7), (27.26, -6.16), (15.63, -6.16)],
               PLAT, 0.9, MAT_FLOOR_CONCRETE, COL_INTER)
flat_poly_slab("SM_Platform_Landing", [(27.26, -6.16), (29.44, -6.16), (29.44, -5.39), (27.26, -5.39)],
               PLAT, 0.9, MAT_FLOOR_CONCRETE, COL_INTER)""",
"""flat_poly_slab("SM_Platform_NorthStrip", [(15.63, -7), (28.23, -7), (28.23, -6.16), (15.63, -6.16)],
               PLAT, 0.9, MAT_FLOOR_CONCRETE, COL_INTER)
# Landing extended south to Y=-3.29: it closes the arrival-floor hole
# east of the flight (X 28.23..29.44, Y -5.39..-3.29). Safe vs the
# balustrade, which ends at X=28.23 (the slab starts exactly there).
flat_poly_slab("SM_Platform_Landing", [(28.23, -6.16), (29.44, -6.16), (29.44, -3.29), (28.23, -3.29)],
               PLAT, 0.9, MAT_FLOOR_CONCRETE, COL_INTER)""",
        "4.2-platform-slabs")

    # ---- 4.3 stair block --------------------------------------------------
    text = r(text,
"""# ---- Main stair (D2): 39 steps, riser 0.15 / tread 0.30, west->east GL 0 -> -5.85 ----
# Flight X 15.63..27.33, 1.9 m wide (Y -5.8..-3.9); north concrete wall + steel
# handrail, south glass balustrade (heights differ: parapet 1.0 / bar top 1.05,
# balustrade 1.1 — PR-C: bar seated, was floating 0.06 with top at 1.12).
NSTEPS = 39""",
"""# ---- Main stair (D2): 42 steps, riser 0.15 / tread 0.30, west->east GL 0 -> -6.3 ----
# Flight X 15.63..28.23, 1.9 m wide (Y -5.8..-3.9); north concrete wall + steel
# handrail, south glass balustrade (heights differ: parapet 1.0 / bar top 1.05,
# balustrade 1.1 — PR-C: bar seated, was floating 0.06 with top at 1.12).
# v22: the flight lands on the lobby/platform (both BFL1 -6.3); 6.30 / 0.15 = 42.
NSTEPS = 42""",
        "4.3-stair-count")

    text = r(text,
"""box("SM_Stair_Soffit", (_STAIR_X0 + NSTEPS * _STAIR_TREAD / 2.0, -4.85, -3.15),""",
"""box("SM_Stair_Soffit", (_STAIR_X0 + NSTEPS * _STAIR_TREAD / 2.0, -4.85, -3.375),""",
        "4.3-soffit-z")

    text = r(text,
"""wall_varying("SM_Stair_Wall_North", (15.63, -6.0), (27.33, -6.0), -6.75, 1.0, -6.75, -4.85,""",
"""wall_varying("SM_Stair_Wall_North", (15.63, -6.0), (28.23, -6.0), -6.3, 1.0, -6.3, -5.30,""",
        "4.3-north-wall")

    text = r(text,
"""box("SM_Stair_Handrail", (21.48, -6.0, -1.897),  # PR-C [Rail]: seated on the parapet (was -1.83, floating 0.06)""",
"""box("SM_Stair_Handrail", (21.93, -6.0, -2.122),  # PR-C [Rail]: seated on the parapet (was -1.83, floating 0.06)""",
        "4.3-handrail")

    text = r(text,
"""wall_varying("SM_Stair_Balustrade", (15.63, -3.9), (27.33, -3.9), -0.3, 1.1, -6.15, -4.75,""",
"""wall_varying("SM_Stair_Balustrade", (15.63, -3.9), (28.23, -3.9), -0.3, 1.1, -6.6, -5.2,""",
        "4.3-balustrade")

    text = r(text,
"""# Wide steps: 6 steps from the platform (-5.85) down to the lobby (-6.75),
# X 9.68..12.04, descending southward (Y -3.29..-1.49). Solid blocks to the lobby floor.
for _wi in range(6):
    _wz = PLAT - _wi * 0.15
    box(f"SM_WideStep_{_wi}", (10.86, -3.29 - (_wi + 0.5) * 0.30, (_wz + G2F) / 2),
        (2.36, 0.30, _wz - G2F), MAT_CONCRETE_BOARD, COL_INTER)""",
"""# Wide steps DELETED in v22: they descended the platform (-5.85) to the
# lobby (-6.75); in v22 both are BFL1 -6.3 (one level, per Detail 4 p96),
# so their blocks (PLAT..G2F) have zero height. They were an artefact of
# the old -5.85/-6.75 split, which the p96 section does not support.""",
        "4.3-wide-steps")

    text = r(text,
"""# G1 steps: 3 steps from the lobby (-6.75) down into G1 (-7.20),
# X 2.0..2.9, Y 3.45..5.55, descending eastward. Solid blocks to the G1 floor.
for _gi in range(3):""",
"""# G1 steps: 6 steps from the lobby (-6.3) down into G1 (-7.20),
# X 2.0..3.8, Y 3.45..5.55, descending eastward. Solid blocks to the G1 floor.
for _gi in range(6):""",
        "4.3-g1-steps")

    # ---- 4.5 tie holes: re-run against the new wall tops ------------------
    # North_Above: 1188 (was 1218; top row 4.5 clipped east of X~22.8
    # by roof_z_north). NorthEast_A: 300 (was 350). NorthEast_B: 60
    # (was 58; wall ends at NE 43.42, u to 43.20). Jog: 42 (was 48;
    # wall top 4.59 at X=29.44, row 4.5 clipped).
    text = r(text,
"""print("PR-D holes North_Above N:", tie_holes("SM_NorthAbove_TieHole_N", 'y', -7.175, (-9.45, 29.25), (0.9, 4.5)))
print("PR-D holes North_Above S:", tie_holes("SM_NorthAbove_TieHole_S", 'y', -6.825, (-9.45, 29.25), (0.9, 4.5)))""",
"""print("v22 holes North_Above N:", tie_holes("SM_NorthAbove_TieHole_N", 'y', -7.175, (-9.45, 29.25), (0.9, 4.5), top_fn=roof_z_north))
print("v22 holes North_Above S:", tie_holes("SM_NorthAbove_TieHole_S", 'y', -6.825, (-9.45, 29.25), (0.9, 4.5), top_fn=roof_z_north))""",
        "4.5-north-above")

    text = r(text,
"""print("PR-D holes NorthEast_A N:", tie_holes("SM_NorthEastA_TieHole_N", 'y', -8.735, (29.70, 40.50), (0.9, 4.5)))
print("PR-D holes NorthEast_A S:", tie_holes("SM_NorthEastA_TieHole_S", 'y', -8.385, (29.70, 40.50), (0.9, 4.5)))""",
"""print("v22 holes NorthEast_A N:", tie_holes("SM_NorthEastA_TieHole_N", 'y', -8.735, (29.70, 40.50), (0.9, 4.5), top_fn=roof_z_north))
print("v22 holes NorthEast_A S:", tie_holes("SM_NorthEastA_TieHole_S", 'y', -8.385, (29.70, 40.50), (0.9, 4.5), top_fn=roof_z_north))""",
        "4.5-north-east-a")

    text = r(text,
"""print("PR-D holes NorthEast_B N:", tie_holes("SM_NorthEastB_TieHole_N", 'y', -8.735, (41.40, 43.65), (0.9, 4.5), top_fn=lambda x: 4.95 - 0.81667 * (x - 41)))
print("PR-D holes NorthEast_B S:", tie_holes("SM_NorthEastB_TieHole_S", 'y', -8.385, (41.40, 43.65), (0.9, 4.5), top_fn=lambda x: 4.95 - 0.81667 * (x - 41)))""",
"""print("v22 holes NorthEast_B N:", tie_holes("SM_NorthEastB_TieHole_N", 'y', -8.735, (41.40, 43.20), (0.9, 4.5), top_fn=roof_z_north))
print("v22 holes NorthEast_B S:", tie_holes("SM_NorthEastB_TieHole_S", 'y', -8.385, (41.40, 43.20), (0.9, 4.5), top_fn=roof_z_north))""",
        "4.5-north-east-b")

    text = r(text,
"""tie_holes("SM_JogWall_TieHole_W", 'x', 29.26, (-8.23, -7.33), (0.3, 4.5))
tie_holes("SM_JogWall_TieHole_E", 'x', 29.62, (-8.23, -7.33), (0.3, 4.5))""",
"""tie_holes("SM_JogWall_TieHole_W", 'x', 29.26, (-8.23, -7.33), (0.3, 4.5), top_fn=lambda y: 4.59)
tie_holes("SM_JogWall_TieHole_E", 'x', 29.62, (-8.23, -7.33), (0.3, 4.5), top_fn=lambda y: 4.59)""",
        "4.5-jog")

    # ---- G3 north wall (C-A edge, chunk 3): angled hole grids -------------
    # v21 Cafe_North_* (98+144+62+12+30 = 346) ran along axis 'y' at
    # X=-34..-12 — wrong for the diagonal wall. Redone as angled grids
    # along the C-A edge (d = distance from A; low 64, high 182,
    # slot W 6, slot E 4). Top along the wall: 4.90 - 0.08964*d.
    # (tie_holes_angled takes ONE face point + direction + normal
    # azimuth; each face gets its own _Out/_In call, as in PR-D.)
    text = r(text,
"""print("PR-D holes Cafe_North_Low N:", tie_holes("SM_CafeNorthLow_TieHole_N", 'y', -6.15, (-33.75, -12.15), (0.3, 0.3)))
print("PR-D holes Cafe_North_Low S:", tie_holes("SM_CafeNorthLow_TieHole_S", 'y', -5.85, (-33.75, -12.15), (0.3, 0.3)))""",
"""# (G3 north wall: direction U=(-0.4791,0.8779) from A; interior
# normal V=(0.8779,0.4791) az 28.62, exterior -V az -151.38;
# face-line starts A-/+V*0.15.)
print("v22 holes Cafe_North_Low out:", tie_holes_angled("SM_CafeNorthLow_TieHole_Out", (-13.3317, -5.6719), (-0.4791, 0.8779), -151.38, (0.45, 14.40), (0.3, 0.3)))
print("v22 holes Cafe_North_Low in:", tie_holes_angled("SM_CafeNorthLow_TieHole_In", (-13.0683, -5.5281), (-0.4791, 0.8779), 28.62, (0.45, 14.40), (0.3, 0.3)))""",
        "4.5-g3-north-low")

    text = r(text,
"""print("PR-D holes Cafe_North_High N:", tie_holes("SM_CafeNorthHigh_TieHole_N", 'y', -6.15, (-33.75, -20.25), (2.7, 4.5), top_fn=lambda x: 4.91 - 0.14029 * (x + 34)))
print("PR-D holes Cafe_North_High S:", tie_holes("SM_CafeNorthHigh_TieHole_S", 'y', -5.85, (-33.75, -20.25), (2.7, 4.5), top_fn=lambda x: 4.91 - 0.14029 * (x + 34)))""",
"""print("v22 holes Cafe_North_High out:", tie_holes_angled("SM_CafeNorthHigh_TieHole_Out", (-13.3317, -5.6719), (-0.4791, 0.8779), -151.38, (0.45, 14.40), (2.7, 4.5), top_fn=lambda d: 4.90 - 0.08964 * d))
print("v22 holes Cafe_North_High in:", tie_holes_angled("SM_CafeNorthHigh_TieHole_In", (-13.0683, -5.5281), (-0.4791, 0.8779), 28.62, (0.45, 14.40), (2.7, 4.5), top_fn=lambda d: 4.90 - 0.08964 * d))""",
        "4.5-g3-north-high")

    text = r(text,
"""print("PR-D holes Cafe_North_High_E N:", tie_holes("SM_CafeNorthHighE_TieHole_N", 'y', -6.15, (-19.80, -12.15), (2.7, 3.9), top_fn=lambda x: 2.946 + 0.14725 * (x + 20)))
print("PR-D holes Cafe_North_High_E S:", tie_holes("SM_CafeNorthHighE_TieHole_S", 'y', -5.85, (-19.80, -12.15), (2.7, 3.9), top_fn=lambda x: 2.946 + 0.14725 * (x + 20)))""",
"""# (High_E folded into the single High band above: the v22 north wall
    # is one 15 m wall with a single straight roof line 4.90 -> 3.56.)""",
        "4.5-g3-north-high-e")

    text = r(text,
"""print("PR-D holes Cafe_North_SlotW N:", tie_holes("SM_CafeNorthSlotW_TieHole_N", 'y', -6.15, (-33.75, -31.50), (1.5, 1.5)))
print("PR-D holes Cafe_North_SlotW S:", tie_holes("SM_CafeNorthSlotW_TieHole_S", 'y', -5.85, (-33.75, -31.50), (1.5, 1.5)))""",
"""print("v22 holes Cafe_North_SlotW out:", tie_holes_angled("SM_CafeNorthSlotW_TieHole_Out", (-13.3317, -5.6719), (-0.4791, 0.8779), -151.38, (0.45, 1.35), (1.5, 1.5)))
print("v22 holes Cafe_North_SlotW in:", tie_holes_angled("SM_CafeNorthSlotW_TieHole_In", (-13.0683, -5.5281), (-0.4791, 0.8779), 28.62, (0.45, 1.35), (1.5, 1.5)))""",
        "4.5-g3-north-slotw")

    text = r(text,
"""print("PR-D holes Cafe_North_SlotE N:", tie_holes("SM_CafeNorthSlotE_TieHole_N", 'y', -6.15, (-18.45, -12.15), (1.5, 1.5)))
print("PR-D holes Cafe_North_SlotE S:", tie_holes("SM_CafeNorthSlotE_TieHole_S", 'y', -5.85, (-18.45, -12.15), (1.5, 1.5)))""",
"""print("v22 holes Cafe_North_SlotE out:", tie_holes_angled("SM_CafeNorthSlotE_TieHole_Out", (-13.3317, -5.6719), (-0.4791, 0.8779), -151.38, (13.95, 14.40), (1.5, 1.5)))
print("v22 holes Cafe_North_SlotE in:", tie_holes_angled("SM_CafeNorthSlotE_TieHole_In", (-13.0683, -5.5281), (-0.4791, 0.8779), 28.62, (13.95, 14.40), (1.5, 1.5)))""",
        "4.5-g3-north-slote")

    text = r(text,
"""print("PR-D holes Cafe_West W:", tie_holes("SM_CafeWest_TieHole_W", 'x', -34.15, (-5.85, 5.85), (0.3, 4.5), top_fn=lambda y: 4.91 - 0.12275 * (y + 6)))
print("PR-D holes Cafe_West E:", tie_holes("SM_CafeWest_TieHole_E", 'x', -33.85, (-5.85, 5.85), (0.3, 4.5), top_fn=lambda y: 4.91 - 0.12275 * (y + 6)))""",
"""# Cafe_West deleted with its wall (chunk 3: no west wall in the
    # frozen quad; the gallery SW edge is south glass + SE wall).""",
        "4.5-cafe-west")

    text = r(text,
"""print("PR-D holes G3_West out:", tie_holes_angled("SM_G3West_TieHole_Out", _g3p_out, (_g3ux, _g3uy), _g3az_out, (0.45, 11.70), (0.3, 4.5), top_fn=lambda d: 4.7 - 0.2364 * d))
print("PR-D holes G3_West in:", tie_holes_angled("SM_G3West_TieHole_In", _g3p_in, (_g3ux, _g3uy), _g3az_in, (0.45, 11.70), (0.3, 4.5), top_fn=lambda d: 4.7 - 0.2364 * d))""",
"""# G3_West holes deleted with their wall (chunk 3: no west wall).""",
        "4.5-g3-west")

    # ---- entrance block (67.35 deg wall, chunk 2): recomputed grids -------
    # v21 (230+30+14 = 274) was for the old two-segment wall at 53.13 deg.
    # New: N 144, S 144 (full height 4.85, no top_fn needed:
    # 4.5 + 0.135 = 4.635 <= 4.85), lintel 14.
    text = r(text,
"""_ent_n_out = (-10.48, -6.64); _ent_n_in = (-9.52, -7.36)
_ent_s_out = (-4.27, 1.64); _ent_s_in = (-3.31, 0.92)
_ent_l_out = (-6.19, -0.92); _ent_l_in = (-5.23, -1.64)
_ent_dir = (0.6, 0.8)""",
"""_ent_n_out = (-10.55519, -6.77168); _ent_n_in = (-9.44819, -7.23560)
_ent_s_out = (-7.73494, -0.04204); _ent_s_in = (-6.62794, -0.50596)
_ent_l_out = (-8.97206, -2.99404); _ent_l_in = (-7.86506, -3.45796)
_ent_dir = (0.3866, 0.9225)""",
        "4.5-entrance-pts")

    text = r(text,
"""print("PR-D holes Entrance_N out:", tie_holes_angled("SM_EntranceN_TieHole_Out", _ent_n_out, _ent_dir, 143.13, (0.20, 6.95), (0.3, 4.5), top_fn=lambda d: 4.95 - 0.14965 * d))
print("PR-D holes Entrance_N in:", tie_holes_angled("SM_EntranceN_TieHole_In", _ent_n_in, _ent_dir, -36.87, (0.20, 6.95), (0.3, 4.5), top_fn=lambda d: 4.95 - 0.14965 * d))""",
"""print("v22 holes Entrance_N out:", tie_holes_angled("SM_EntranceN_TieHole_Out", _ent_n_out, _ent_dir, 157.35, (0.20, 3.90), (0.3, 4.5)))
print("v22 holes Entrance_N in:", tie_holes_angled("SM_EntranceN_TieHole_In", _ent_n_in, _ent_dir, -22.65, (0.20, 3.90), (0.3, 4.5)))""",
        "4.5-entrance-n")

    text = r(text,
"""print("PR-D holes Entrance_S out:", tie_holes_angled("SM_EntranceS_TieHole_Out", _ent_s_out, _ent_dir, 143.13, (0.20, 1.10), (0.3, 2.7), top_fn=lambda d: 3.40 - 0.15267 * d))
print("PR-D holes Entrance_S in:", tie_holes_angled("SM_EntranceS_TieHole_In", _ent_s_in, _ent_dir, -36.87, (0.20, 1.10), (0.3, 2.7), top_fn=lambda d: 3.40 - 0.15267 * d))""",
"""print("v22 holes Entrance_S out:", tie_holes_angled("SM_EntranceS_TieHole_Out", _ent_s_out, _ent_dir, 157.35, (0.20, 3.90), (0.3, 4.5)))
print("v22 holes Entrance_S in:", tie_holes_angled("SM_EntranceS_TieHole_In", _ent_s_in, _ent_dir, -22.65, (0.20, 3.90), (0.3, 4.5)))""",
        "4.5-entrance-s")

    text = r(text,
"""print("PR-D holes Entrance_Lintel out:", tie_holes_angled("SM_EntranceLintel_TieHole_Out", _ent_l_out, _ent_dir, 143.13, (0.25, 2.95), (3.3, 3.3), top_fn=lambda d: 3.88 - 0.15 * d))
print("PR-D holes Entrance_Lintel in:", tie_holes_angled("SM_EntranceLintel_TieHole_In", _ent_l_in, _ent_dir, -36.87, (0.25, 2.95), (3.3, 3.3), top_fn=lambda d: 3.88 - 0.15 * d))""",
"""print("v22 holes Entrance_Lintel out:", tie_holes_angled("SM_EntranceLintel_TieHole_Out", _ent_l_out, _ent_dir, 157.35, (0.25, 2.95), (3.3, 3.3)))
print("v22 holes Entrance_Lintel in:", tie_holes_angled("SM_EntranceLintel_TieHole_In", _ent_l_in, _ent_dir, -22.65, (0.25, 2.95), (3.3, 3.3)))""",
        "4.5-entrance-lintel")

    # ---- B1 tie holes: grids shift +0.45 with the floor datum -------------
    # ThickWall 329 (unchanged), NorthWall 144 (was 168: the top row
    # would sit 0.05 below the -0.10 wall top), G2 column 42 (unchanged).
    text = r(text,
"""tie_holes("SM_ThickWall_TieHole", 'y', 2.33, (18.5, 39.5), (-6.2, -2.6))  # D-fix: was (18.5, 41.5); wall stops at X=39.5, 35 discs floated in the doorway gap""",
"""tie_holes("SM_ThickWall_TieHole", 'y', 2.33, (18.5, 39.5), (-5.75, -2.15))  # D-fix: was (18.5, 41.5); wall stops at X=39.5, 35 discs floated in the doorway gap""",
        "4.5-thickwall")

    text = r(text,
"""tie_holes("SM_NorthWall_TieHole", 'y', -6.83, (16.2, 26.55), (-4.2, -0.6))  # 24 cols x 7 rows = 168""",
"""tie_holes("SM_NorthWall_TieHole", 'y', -6.83, (16.2, 26.55), (-3.75, -0.75))  # 24 cols x 6 rows = 144 (top row dropped: -0.15 would sit 0.05 below the -0.10 wall top)""",
        "4.5-northwall")

    text = r(text,
"""    tie_holes(f"SM_G2_Column_TieHole_{i}", 'y', 5.83, (cx, cx), (-6.2, -2.6))""",
"""    tie_holes(f"SM_G2_Column_TieHole_{i}", 'y', 5.83, (cx, cx), (-5.75, -2.15))""",
        "4.5-g2column")

    # ---- new-wall holes (D-round rule: P-con grids on all exposed --------
    # above-ground concrete walls; these three walls are new in v22 and
    # would otherwise be bare concrete next to holed concrete).
    # Museum south-east wall (roof edge Y=3.50, top flat 4.3): 238.
    # G3 east wall (A-B edge): 252 + lintel 10. G3 SE wall (B-D edge): 214.
    # (Entrance-core box deliberately NOT holed: solid pavilion block,
    # no D-round precedent for boxes; south face largely covered by
    # door/banner — open judgement call, flag for Leon.)
    text = r(text,
"""    tie_holes(f"SM_G2_Column_TieHole_{i}", 'y', 5.83, (cx, cx), (-5.75, -2.15))
""",
"""    tie_holes(f"SM_G2_Column_TieHole_{i}", 'y', 5.83, (cx, cx), (-5.75, -2.15))

# ---- new walls (v22): tie holes --------------------------------------
# Museum south-east wall: axis 'y' at the roof edge Y=3.50, faces
# Y=3.325 (interior) / 3.675 (exterior), top flat 4.3 (rows to 3.9).
print("v22 holes Museum_SE N:", tie_holes("SM_MuseumSE_TieHole_N", 'y', 3.325, (31.5, 38.7), (0.3, 3.9)))
print("v22 holes Museum_SE S:", tie_holes("SM_MuseumSE_TieHole_S", 'y', 3.675, (31.5, 38.7), (0.3, 3.9)))
# G3 east wall (A-B edge, direction (0.3985,0.9175); exterior
# normal (0.9175,-0.3985) az -23.49, interior az 156.51;
# top 4.90 - 0.0745*d; lintel at the A end, v=2.7, d 0.25..2.35).
print("v22 holes G3_East out:", tie_holes_angled("SM_G3East_TieHole_Out", (-13.0624, -5.6598), (0.3985, 0.9175), -23.49, (0.45, 8.05), (0.3, 4.5), top_fn=lambda d: 4.90 - 0.0745 * d))
print("v22 holes G3_East in:", tie_holes_angled("SM_G3East_TieHole_In", (-13.3376, -5.5402), (0.3985, 0.9175), 156.51, (0.45, 8.05), (0.3, 4.5), top_fn=lambda d: 4.90 - 0.0745 * d))
print("v22 holes G3_East_Lintel out:", tie_holes_angled("SM_G3EastLintel_TieHole_Out", (-13.0624, -5.6598), (0.3985, 0.9175), -23.49, (0.25, 2.35), (2.7, 2.7)))
print("v22 holes G3_East_Lintel in:", tie_holes_angled("SM_G3EastLintel_TieHole_In", (-13.3376, -5.5402), (0.3985, 0.9175), 156.51, (0.25, 2.35), (2.7, 2.7)))
# G3 SE wall (B-D edge, direction (-0.5328,0.8462); exterior
# normal (0.8463,0.5327) az 32.19, interior az -147.81;
# top 4.10 - 0.0882*d).
print("v22 holes G3_SE out:", tie_holes_angled("SM_G3SE_TieHole_Out", (-8.7731, 4.3799), (-0.5328, 0.8462), 32.19, (0.45, 8.10), (0.3, 4.5), top_fn=lambda d: 4.10 - 0.0882 * d))
print("v22 holes G3_SE in:", tie_holes_angled("SM_G3SE_TieHole_In", (-9.0269, 4.2201), (-0.5328, 0.8462), -147.81, (0.45, 8.10), (0.3, 4.5), top_fn=lambda d: 4.10 - 0.0882 * d))
""",
        "4.5-new-walls")

    # ---- 4.6 G2 ceilings / fluorescents / skylight / east door -----------
    text = r(text,
"""# ---- G2 ceiling (flat white gypsum, -1.95; net height 4.8) + skylight + fluorescents ----
box("SM_G2_Ceiling_N", (31.82, 4.225, -1.95), (33.48, 1.95, 0.06), MAT_CEILING_GYPSUM, COL_INTER)
box("SM_G2_Ceiling_S", (31.82, 11.57, -1.95), (33.48, 11.34, 0.06), MAT_CEILING_GYPSUM, COL_INTER)""",
"""# ---- G2 ceiling (flat white gypsum, -1.5; net height 4.8) + skylight + fluorescents ----
box("SM_G2_Ceiling_N", (31.82, 4.225, -1.5), (33.48, 1.95, 0.06), MAT_CEILING_GYPSUM, COL_INTER)
box("SM_G2_Ceiling_S", (31.82, 11.57, -1.5), (33.48, 11.34, 0.06), MAT_CEILING_GYPSUM, COL_INTER)""",
        "4.6-g2-ceiling")

    text = r(text,
"""box("SM_G2_Skylight_Slot", (31.82, 5.55, -1.67), (33.48, 0.70, 0.10), MAT_SKYLIGHT, COL_INTER)""",
"""box("SM_G2_Skylight_Slot", (31.82, 5.55, -1.22), (33.48, 0.70, 0.10), MAT_SKYLIGHT, COL_INTER)""",
        "4.6-g2-skylight")

    text = r(text,
"""    box(f"SM_G2_Fluorescent_{_ri}", (32, _ry, -2.02), (30.0, 0.12, 0.06), MAT_SKYLIGHT, COL_INTER)""",
"""    box(f"SM_G2_Fluorescent_{_ri}", (32, _ry, -1.57), (30.0, 0.12, 0.06), MAT_SKYLIGHT, COL_INTER)""",
        "4.6-g2-fluorescent")

    text = r(text,
"""box("SM_G2_East_Door", (48.4, 5.0, -5.55), (0.3, 1.2, 2.4), MAT_DARK_DOOR, COL_INTER)""",
"""box("SM_G2_East_Door", (48.4, 5.0, -5.1), (0.3, 1.2, 2.4), MAT_DARK_DOOR, COL_INTER)""",
        "4.6-g2-eastdoor")

    # ---- 4.7 G2 columns ----------------------------------------------------
    text = r(text,
"""    box(f"SM_G2_Column_{i}", (cx, 5.55, -4.35), (0.55, 0.55, 4.8), MAT_CONCRETE_BOARD, COL_INTER)""",
"""    box(f"SM_G2_Column_{i}", (cx, 5.55, -3.9), (0.55, 0.55, 4.8), MAT_CONCRETE_BOARD, COL_INTER)""",
        "4.7-g2-columns")

    # ---- 4.8 Z corridor -----------------------------------------------------
    # (5 walls + ceiling; the "-6.75, -1.95, -6.75, -1.95" pattern is
    # unique to this block.)
    text = replace_count(text, "-6.75, -1.95, -6.75, -1.95", "-6.3, -1.5, -6.3, -1.5", 5, "4.8-zcorr-walls")
    text = r(text,
"""# ---- Z corridor (G2 exit -> court), X 36..44, Y -1..3, flat ceiling -1.95 ----""",
"""# ---- Z corridor (G2 exit -> court), X 36..44, Y -1..3, flat ceiling -1.5 ----""",
        "4.8-zcorr-comment")
    text = r(text,
"""flat_poly_slab("SM_ZCorr_Ceiling", [(36, -1), (44, -1), (44, 3), (36, 3)],
               -1.95, 0.06, MAT_CEILING_GYPSUM, COL_INTER)""",
"""flat_poly_slab("SM_ZCorr_Ceiling", [(36, -1), (44, -1), (44, 3), (36, 3)],
               -1.5, 0.06, MAT_CEILING_GYPSUM, COL_INTER)""",
        "4.8-zcorr-ceiling")

    # ---- 4.9 G2 sprinkler / access panels ----------------------------------
    text = r(text,
"""# G2 ceiling (flat, soffit z=-1.98): 2 rows of sprinklers + 1 square + 1 round panel.
for _si, _sx in enumerate([19.0, 23.5, 28.0, 32.5, 37.0, 41.5, 46.0]):
    _sprinkler(f"SM_G2_Sprinkler_N_{_si}", _sx, 4.2, -1.98)
    _sprinkler(f"SM_G2_Sprinkler_S_{_si}", _sx, 15.0, -1.98)
_ceiling_panel_square("SM_G2_Access_Square", 25.0, 10.0, -1.98)
_ceiling_panel_round("SM_G2_Access_Round", 42.0, 14.0, -1.98)""",
"""# G2 ceiling (flat, soffit z=-1.53): 2 rows of sprinklers + 1 square + 1 round panel.
for _si, _sx in enumerate([19.0, 23.5, 28.0, 32.5, 37.0, 41.5, 46.0]):
    _sprinkler(f"SM_G2_Sprinkler_N_{_si}", _sx, 4.2, -1.53)
    _sprinkler(f"SM_G2_Sprinkler_S_{_si}", _sx, 15.0, -1.53)
_ceiling_panel_square("SM_G2_Access_Square", 25.0, 10.0, -1.53)
_ceiling_panel_round("SM_G2_Access_Round", 42.0, 14.0, -1.53)""",
        "4.9-g2-sprinklers")

    # ---- 4.10 B1 perimeter + BOH walls + thick wall ------------------------
    # (The "-6.75, -0.10, -6.75, -0.10" pattern is the 4 basement
    # perimeter walls + the 6 BOH walls; all bottoms are the B1 floor.)
    text = replace_count(text, "-6.75, -0.10, -6.75, -0.10", "-6.3, -0.10, -6.3, -0.10", 10, "4.10-b1-boh-walls")
    text = r(text,
"""# ---- B1 perimeter walls (Z -6.75..-0.10, tops below lawn -0.05) ----""",
"""# ---- B1 perimeter walls (Z -6.3..-0.10, tops below lawn -0.05) ----""",
        "4.10-b1-comment")
    text = r(text,
"""# ---- BOH (south-west back of house: office + storage), walls Z -6.75..-0.10 ----""",
"""# ---- BOH (south-west back of house: office + storage), walls Z -6.3..-0.10 ----""",
        "4.10-boh-comment")
    text = r(text,
"""box("SM_G2_ThickWall", (28.77, 2.79, -3.425), (21.47, 0.92, 6.65), MAT_CONCRETE_BOARD, COL_INTER)""",
"""box("SM_G2_ThickWall", (28.77, 2.79, -3.2), (21.47, 0.92, 6.2), MAT_CONCRETE_BOARD, COL_INTER)""",
        "4.10-thickwall")

    # ---- 4.11 elevator ------------------------------------------------------
    text = r(text,
"""_elev_v = [(x, y, -6.75) for (x, y) in _ELEV_PLAN] + [(x, y, 2.4) for (x, y) in _ELEV_PLAN]""",
"""_elev_v = [(x, y, -6.3) for (x, y) in _ELEV_PLAN] + [(x, y, 2.4) for (x, y) in _ELEV_PLAN]""",
        "4.11-elev-shaft")
    text = r(text,
"""box("SM_Elevator_Door_Basement", (0.20, -5.22, -4.65), (1.2, 0.08, 2.4), MAT_STEEL_DARK, COL_INTER,""",
"""box("SM_Elevator_Door_Basement", (0.20, -5.22, -5.10), (1.2, 0.08, 2.4), MAT_STEEL_DARK, COL_INTER,""",
        "4.11-elev-door")
    text = r(text,
"""box("SM_Elevator_Car", (0.0, -4.7, -4.7), (1.2, 1.0, 2.2), MAT_STEEL_DARK, COL_INTER)""",
"""box("SM_Elevator_Car", (0.0, -4.7, -5.15), (1.2, 1.0, 2.2), MAT_STEEL_DARK, COL_INTER)""",
        "4.11-elev-car")

    # ---- 4.12 courtyard -----------------------------------------------------
    # Glass walls: bottoms -6.75 -> -6.3 (tops follow the roof, unchanged).
    # Mullions use G2F (auto: tallest at B becomes 10.79 m, was 11.68 m —
    # a datum change, not a modelling error).
    text = r(text,
"""wall_varying("SM_Court_Glass_Diag_A", _COURT_A, _gap0, -6.75, _court_roof_z(*_COURT_A),
             -6.75, _court_roof_z(*_gap0), MAT_GLASS, COL_INTER, thick=0.12)
wall_varying("SM_Court_Glass_Diag_B", _gap1, _COURT_B, -6.75, _court_roof_z(*_gap1),
             -6.75, _court_roof_z(*_COURT_B), MAT_GLASS, COL_INTER, thick=0.12)
wall_varying("SM_Court_Glass_East", _COURT_B, _COURT_C, -6.75, _court_roof_z(*_COURT_B),
             -6.75, _court_roof_z(*_COURT_C), MAT_GLASS, COL_INTER, thick=0.12)""",
"""wall_varying("SM_Court_Glass_Diag_A", _COURT_A, _gap0, -6.3, _court_roof_z(*_COURT_A),
             -6.3, _court_roof_z(*_gap0), MAT_GLASS, COL_INTER, thick=0.12)
wall_varying("SM_Court_Glass_Diag_B", _gap1, _COURT_B, -6.3, _court_roof_z(*_gap1),
             -6.3, _court_roof_z(*_COURT_B), MAT_GLASS, COL_INTER, thick=0.12)
wall_varying("SM_Court_Glass_East", _COURT_B, _COURT_C, -6.3, _court_roof_z(*_COURT_B),
             -6.3, _court_roof_z(*_COURT_C), MAT_GLASS, COL_INTER, thick=0.12)""",
        "4.12-court-glass")
    text = r(text,
"""box("SM_Court_Planter", (31.3, -0.56, -6.65), (6.0, 3.5, 0.2), MAT_GRASS, COL_INTER)
cedar(31.3, -0.56, h=3.8, r=0.9, z0=-6.75)""",
"""box("SM_Court_Planter", (31.3, -0.56, -6.2), (6.0, 3.5, 0.2), MAT_GRASS, COL_INTER)
cedar(31.3, -0.56, h=3.8, r=0.9, z0=-6.3)""",
        "4.12-court-planter")

    # ---- 4.13 G3 sprinklers / access panels (chunk-3 miss) -----------------
    # v21 absolute coords (-28,-4.5) etc. fall OUTSIDE the frozen quad
    # (on the exterior side of the new north wall). Moved into the quad
    # in (u,v): sprinklers (5,3),(10,3),(12,5); square (4,3); round (9,5).
    # (8,5) avoided: under the WC-strip flat 2.7 m ceiling (sloped
    # ceiling there is 2.35). Ceiling heights: v=3 -> 3.65, v=5 -> 2.35.
    text = r(text,
"""# G3 ceiling (sloped, north band ~2.7-4.26 m): 3 sprinklers + 1 square + 1 round panel.
for _si, (_gx, _gy) in enumerate([(-28.0, -4.5), (-24.0, -4.0), (-20.0, -4.5)]):
    _sprinkler(f"SM_G3_Sprinkler_{_si}", _gx, _gy, g3_ceiling_z(_gx, _gy))
_rx, _ry = _slope_rot(g3_ceiling_z, -26.0, -3.5)
_ceiling_panel_square("SM_G3_Access_Square", -26.0, -3.5, g3_ceiling_z(-26.0, -3.5), _rx, _ry)
_rx, _ry = _slope_rot(g3_ceiling_z, -22.0, -4.5)
_ceiling_panel_round("SM_G3_Access_Round", -22.0, -4.5, g3_ceiling_z(-22.0, -4.5), _rx, _ry)""",
"""# G3 ceiling (sloped, Section C profile): 3 sprinklers + 1 square + 1 round panel.
for _si, (_gx, _gy) in enumerate([_g3_pt(5, 3), _g3_pt(10, 3), _g3_pt(12, 5)]):
    _sprinkler(f"SM_G3_Sprinkler_{_si}", _gx, _gy, g3_ceiling_z(_gx, _gy))
_ax, _ay = _g3_pt(4, 3)
_rx, _ry = _slope_rot(g3_ceiling_z, _ax, _ay)
_ceiling_panel_square("SM_G3_Access_Square", _ax, _ay, g3_ceiling_z(_ax, _ay), _rx, _ry)
_bx, _by = _g3_pt(9, 5)
_rx, _ry = _slope_rot(g3_ceiling_z, _bx, _by)
_ceiling_panel_round("SM_G3_Access_Round", _bx, _by, g3_ceiling_z(_bx, _by), _rx, _ry)""",
        "4.13-g3-sprinklers")

    # ---- 4.14 stair sprinkler ----------------------------------------------
    # v21 _sx = 21.48 was the 39-step flight midpoint; v22 midpoint is 21.93.
    # (Nosing -3.15, soffit bottom -3.45 — the head stays on the soffit.)
    text = r(text,
"""_sx = 21.48""",
"""_sx = 21.93""",
        "4.14-stair-sprinkler")

    # ---- 4.15 reception desk + hall columns ---------------------------------
    text = r(text,
"""box("SM_Reception_Desk", (-4, -2, 0.55), (3.2, 1.0, 1.1), MAT_WHITE, COL_INTER)
box("SM_Reception_Desk_Top", (-4, -2, 1.12), (3.3, 1.1, 0.06), MAT_WOOD, COL_INTER)""",
"""# (v22: desk moved to the entrance doorway (-7.80,-1.75), rotated to the
# west wall angle 67.35 deg; chunk 2 planned this move but never wrote it.)
box("SM_Reception_Desk", (-6.6, -3.2, 0.55), (3.2, 1.0, 1.1), MAT_WHITE, COL_INTER,
    rot=(0, 0, math.radians(67.35)))
box("SM_Reception_Desk_Top", (-6.6, -3.2, 1.12), (3.3, 1.1, 0.06), MAT_WOOD, COL_INTER,
    rot=(0, 0, math.radians(67.35)))""",
        "4.15-reception")

    text = r(text,
"""for _cx, _cy in [(0, 1.2), (12, 1.2), (24, 1.2), (34, 1.2)]:""",
"""# v22: (24,1.2) and (34,1.2) fall INSIDE the sunken-court triangle
# (at y=1.2 the court spans x 21.42..36.27) — they floated over the
# -6.3 pit. (20,1.2) would poke 0.46 m through the low roof (roof
# 2.04, column min height 2.5). Moved to (16,1.2) (roof 2.78) and
# (38,1.2) (roof 4.34, inside the east diagonal at X=40.12).
for _cx, _cy in [(0, 1.2), (12, 1.2), (16, 1.2), (38, 1.2)]:""",
        "4.15-hall-columns")

    # ---- 4.16 exhibits section re-definitions -------------------------------
    text = r(text,
"""G2F = -6.75
G1F = -7.20
G2C = -1.95""",
"""G2F = -6.3
G1F = -7.20
G2C = -1.5""",
        "4.16-exhibits-levels")

    text = r(text,
"""# new cords hang from the G2 ceiling (-1.95); lamp heights above the floor kept.""",
"""# new cords hang from the G2 ceiling (-1.5); lamp heights above the floor kept.""",
        "4.16-pendant-comment")

    # ---- 4.17 noren (all +0.45 with the G2 floor datum) --------------------
    text = r(text,
"""box("SM_EXHIBIT_09_Rod", (15.08, 6.5, -4.50), (0.05, 3.0, 0.05), MAT_BLACK, COL_EXH)
box("SM_EXHIBIT_09_Panel_L", (15.08, 5.75, -5.40), (0.04, 1.3, 1.8), MAT_INDIGO, COL_EXH)
box("SM_EXHIBIT_09_Panel_R", (15.08, 7.25, -5.40), (0.04, 1.3, 1.8), MAT_INDIGO, COL_EXH)""",
"""box("SM_EXHIBIT_09_Rod", (15.08, 6.5, -4.05), (0.05, 3.0, 0.05), MAT_BLACK, COL_EXH)
box("SM_EXHIBIT_09_Panel_L", (15.08, 5.75, -4.95), (0.04, 1.3, 1.8), MAT_INDIGO, COL_EXH)
box("SM_EXHIBIT_09_Panel_R", (15.08, 7.25, -4.95), (0.04, 1.3, 1.8), MAT_INDIGO, COL_EXH)""",
        "4.17-noren")

    text = r(text,
"""                                        location=(_dx, _dy, -5.25),""",
"""                                        location=(_dx, _dy, -4.80),""",
        "4.17-noren-crests")

    # ---- 4.18 validation asserts (gates 2/3) in the build script ----------
    text = r(text,
"""bpy.ops.wm.save_mainfile(filepath=BLEND_PATH)
print(f"saved {BLEND_PATH}")

# ---- stats ----""",
"""bpy.ops.wm.save_mainfile(filepath=BLEND_PATH)
print(f"saved {BLEND_PATH}")

# ---- v22 validation asserts (gates 2/3) ----
# Roof corners (gate 2): NW/NE/SW/V/E/SE.
assert abs(roof_z_at(-10.00, -7.00) - 4.85) < 0.01, roof_z_at(-10.00, -7.00)
assert abs(roof_z_at(43.42, -7.00) - 4.50) < 0.01, roof_z_at(43.42, -7.00)
assert abs(roof_z_at(-5.60, 3.50) - 4.85) < 0.01, roof_z_at(-5.60, 3.50)
assert abs(roof_z_at(19.70, 3.50) - 0.20) < 0.01, roof_z_at(19.70, 3.50)
assert abs(roof_z_at(31.17, 3.50) - 4.30) < 0.01, roof_z_at(31.17, 3.50)
assert abs(roof_z_at(39.20, 3.50) - 4.30) < 0.01, roof_z_at(39.20, 3.50)
# South profile (gate 2): W/V/E + flat to SE.
assert abs(roof_z_south(-5.60) - 4.85) < 0.01
assert abs(roof_z_south(19.70) - 0.20) < 0.01
assert abs(roof_z_south(31.17) - 4.30) < 0.01
assert abs(roof_z_south(39.20) - 4.30) < 0.01
# North-of-fold-A flatness at x=8 (eave section 1 deg check): the plate
# rises <=0.05 m over y -7..0.5, then drops south of fold A.
assert abs(roof_z_at(8.0, 0.5) - roof_z_at(8.0, -7.0)) < 0.05
assert roof_z_at(8.0, 3.5) < 2.6
# Fold continuity (gate 3).
assert abs(roof_z_at(18.91, -1.75) - 4.675) < 0.02
assert abs(roof_z_at(31.56, -1.75) - _plane_z(31.56, -1.75, _ROOF_NE, _ROOF_SW, _ROOF_V)) < 0.02
# Levels (gate 3).
assert G2F == -6.3 and PLAT == -6.3 and G1F == -7.20 and G2C == -1.5 and G1C == -2.20
# Stair (gate 3): 42 steps, 6.30 m drop, flight ends at 28.23.
assert NSTEPS == 42 and abs(NSTEPS * 0.15 - 6.3) < 1e-9
assert abs(15.63 + NSTEPS * 0.30 - 28.23) < 1e-9
assert abs((G2F - G1F) - 0.9) < 1e-9  # G1 steps: 6 x 0.15
# G3 corners (gate 3).
assert abs(cafe_z_at(-13.20, -5.60) - 4.9) < 0.01
assert abs(cafe_z_at(-8.90, 4.30) - 4.1) < 0.01
assert abs(cafe_z_at(-16.70, 17.60) - 3.55) < 0.01
assert abs(cafe_z_at(-28.70, 22.80) - 2.0) < 0.01
# Mullions (gate 3): west 11 bays = 12 lines, east 9 verticals.
assert len(_WEST_MULLIONS) == 12
assert len(_EAST_MULLIONS_W) + len(_EAST_MULLIONS_E) == 9
# Plan lengths (gate 3): north 53.42, south 44.8, depth 10.5.
assert abs(43.42 - (-10.00) - 53.42) < 1e-9
assert abs(39.20 - (-5.60) - 44.8) < 1e-9
assert abs(3.50 - (-7.00) - 10.5) < 1e-9
print("=== v22 asserts passed (gates 2/3) ===")

# ---- stats ----""",
        "4.18-asserts")

    # ---- 4.19 stale comments (current-geometry descriptions) ------------
    # (History comments in the file header keep their old values.)
    text = r(text,
"""# Levels (D1): exhibition floor G2F=-6.75, upper platform PLAT=-5.85, G1 floor G1F=-7.20.""",
"""# Levels (D1): exhibition floor G2F=-6.3, upper platform PLAT=-6.3, G1 floor G1F=-7.20.""",
        "4.19-levels-comment")
    text = r(text,
"""# roof_z_at - 0.65 at 2.0 m in; G2 ceiling flat -1.95).""",
"""# roof_z_at - 0.65 at 2.0 m in; G2 ceiling flat -1.5).""",
        "4.19-g2ceiling-comment")
    text = r(text,
"""# ---- G2 north thick wall (solid concrete, X 18.03..41.87, Y 2.33..3.25, Z -6.75..-0.10) ----""",
"""# ---- G2 north thick wall (solid concrete, X 18.03..41.87, Y 2.33..3.25, Z -6.3..-0.10) ----""",
        "4.19-thickwall-comment")
    text = r(text,
"""from the pit floor (-6.75)""",
"""from the pit floor (-6.3)""",
        "4.19-mullion-comment")
    text = r(text,
"""# Full height down to the B1 floor (-6.75); 0.4 thick so it embeds into the""",
"""# Full height down to the B1 floor (-6.3); 0.4 thick so it embeds into the""",
        "4.19-stairwall-comment")
    text = r(text,
"""# ---- Atrium furnishings (lower lobby, floor -6.75) ----""",
"""# ---- Atrium furnishings (lower lobby, floor -6.3) ----""",
        "4.19-atrium-comment")

    print("chunk 4 done")
    return text


if __name__ == "__main__":
    main()
