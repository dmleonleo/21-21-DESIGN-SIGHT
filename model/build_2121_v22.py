# 21_21 DESIGN SIGHT — Blender build v19 (Issue #21 PR-B [geometry],
# based on the PR-A script: PR-A + #21B patch, see
# issue21/B/patch/apply_issue21B.py — replayable, do not
# hand-edit this file; re-run the patch on the PR-A script instead).
# v19 changes in PR-B (geometry rebuild; materials as in PR-A):
#  B1 whole level sinks: exhibition floor -6.75, upper platform -5.85,
#     G1 floor -7.20 (3 steps x 0.15 below G2); G2 ceiling -1.95,
#     G1 ceiling -2.20; roof apex +4.95 (trapezoid 54 m x ~9 m, ~448 m2);
#     roof construction 0.65 m (soffit = roof - 0.65); G3 ceiling
#     clamped to cafe roof - 0.65 (max 4.26 preserved); court 74 m2;
#     main stair 39 steps (0.15/0.30); long window 2 x 11.5 m.
# v19 FIX (Hark PR #23 review, comment 7031719587; Leon approved 2026-11-20;
#     see issue21/fix/patch/apply_fix.py — replayable, do not hand-edit):
#  [3] atrium soffit: eave ring thins to 0.40 m (steel plate + H-300 +
#      gypsum), middle keeps 0.65 m (Hark accepted 0.5-0.8, #21 §2);
#      blend over 2.0 m in from the FOOT perimeter. NE tip: the roof
#      itself is only +2.50 at the corner, so the soffit there is 2.10
#      even thinned — see fix/STATUS.md (residual, needs a ruling).
#  [4] long window, option (b): glass 0..+0.45, sill flush with GL;
#      shade strip 0.45..0.80; north walls re-stacked (below to 0.0,
#      slot infill 0..0.45, above from 0.45). No light well.
#  [RIM] SM_Court_Roof_Rim lift 0.30 -> -0.05: top +5.25 -> +4.90,
#      below the roof surface, inside the <=5.2 acceptance line.
# v20 PR-C (issue #21 §5 audit + Jog infill; Leon approved 2026-11-20;
#     see issue21/C/patch/apply_C.py — replayable, do not hand-edit):
#  §5 audit (probes C/probe_C.py on the v19 GLB): #01 long window
#      2x11.5x0.45 present; #02 smoke cover = the shade strips
#      (11.50, same span as the panes, 0.45..0.80, projecting 0.30);
#      #17 41 mullions 235x69 @ 0.80, tallest 11.55 m; #03 parapet
#      slope exactly 1:2 (0.500 fit); #07 parapet +1.00 vs glass
#      +1.10 differ by 0.10 as designed. No work on any of these.
#  [Jog] NEW ground-floor Jog wall (29.44,-7)->(29.44,-8.56),
#      0.0..4.95, MAT_Concrete, thick 0.35, P-con tie holes both
#      faces — closes the 1.2 m full-height slot in the ground
#      north wall (B1 Jog wall below, -6.75..0.0, untouched).
#  [Rail] steel handrail bar seated on the parapet (centre Z
#      -1.83 -> -1.897; it floated 0.06 m with no posts, and its
#      top at +1.12 stood above the glass top +1.10; now +1.05).
#  Outputs are design2121_v20_build.blend / design2121_v20.glb
#      (the v19-fix script's v19 names would clobber the v19 GLB
#      if run verbatim — found in the post-push review).
# v21 PR-D (issue #21 finish round; see issue21/D/patch/apply_D.py —
#     replayable, do not hand-edit):
#  [Holes] P-con tie holes (450x600, both faces) on all 17 other
#      above-ground exposed concrete walls + Jog re-grid: 3,086
#      discs placed, v21 total 3,660 (v20: 628). Audit + per-wall
#      table in issue21/D/STATUS.md (probe D/probe_D_audit.py).
#      New helper tie_holes_angled() for the diagonal entrance
#      block/lintel + G3 west wall; tie_holes() gains top_fn
#      (sloped-top walls clip rows per column, 0.10 m clearance).
#  [Jog] bottom row 0.0 -> 0.3, top row 4.8 -> 4.5 (grid shifts
#      up 0.3, 9 rows -> 8; Hark PR-C review: bottom row crossed
#      the ground plane; 600 module kept, 0.3-phase shared with
#      all other above-ground walls).
#  [Tex18] concrete texture period 2.0 m -> 1.8 m (Hark PR-A
#      review): board-form tile, bake plane and cube_project UV
#      tile all 1.8 m; 1.8 = 2x0.9 = 1x1.8, panel joints align
#      across tiles (the 2.0 m tile jogged 0.2 m per boundary).
#  [Bake] NO lightmap re-bake: no wall geometry changes, tie
#      holes are MAT_TIEHOLE (outside all bake groups), lightmaps
#      bake indirect+AO only (albedo-independent). v20 atlases +
#      UV1 reused via transfer_uv1.mjs (as PR-A reused v18).
#  [Fix] G2 thick-wall (B1) tie holes u_range 41.5 -> 39.5:
#      the wall stops at X=39.5 (doorway to the Z corridor),
#      so the 5 easternmost cols (35 discs) floated in air;
#      truncated to the wall end (47 cols, 329 discs).
#  Outputs are design2121_v21_build.blend / design2121_v21.glb.
# v22 (issue #26, see issue21/v22/build/apply_v22.py — replayable,
#     do not hand-edit): folded-plate roof + south facade rebuild.
#  [Roof] Frozen trapezoid NW(-10,-7) NE(43.42,-7) SE(39.20,3.50)
#      SW(-5.60,3.50); folds A NE->SW, B NE->V(19.70,3.50);
#      corner heights NW 4.85 / NE ~4.5 / SW 4.85 / SE ~4.3,
#      valley V 0.2, east point E(31.17,3.50) 4.3. Regions N/M
#      flat planes, region E warped plate (see roof_z_at).
#      v21 false mid-ridge zm (+0.06) removed.
#  [South] Glass line Y=2.33, roof edge Y=3.50 (1.17 m eave
#      overhang); west wing 11 bays x 2.30 m, east wing dense
#      verticals ~1.0 m, entrance core X 22.4..27.4 (top 4.0),
#      east solid wall E->SE + triangular glass gable.
#  [G3] Frozen quad A(-13.20,-5.60) B(-8.90,4.30)
#      D(-16.70,17.60) C(-28.70,22.80), fold C->B valley;
#      corners A 4.9 / B 4.1 / D 3.55 / C 2.0; interior
#      re-laid along the strip in (u,v) coords (see _g3_pt).
#  [B1] BFL1 -6.3, BFL2 -7.2 (Detail 4 p96); G2F/PLAT -6.3,
#      G2C -1.5 (net height 4.8 kept); stair 42 steps
#      (15.63..28.23); wide steps DELETED; G1 steps 6.
#  [Walls] North tops follow the new north-edge profile
#      (4.85->4.59->4.52->4.50); Jog ground top 4.59.
#  Outputs are design2121_v22_build.blend / design2121_v22.glb.
# v19 changes in PR-A (materials only, NO geometry):
#  A1 roof seams deleted (6 dark ribbons + MAT_Steel_Seam + the
#     panel-seam brick in add_steel_detail; site-welded plate).
#  A2 concrete 900x1800 film-faced formwork (Brick 2.25/4.5 @ Scale 5,
#     Offset 0), P-con grid 450x600 (tie_holes step_u/step_v, 12-vert
#     discs, 60 -> 182), roughness 0.55, no wood grain.
#  A3 ceilings white gypsum (GB-R 9.5+12.5 EP): G2 -> MAT_Ceiling_Gypsum,
#     atrium soffit -> MAT_Ceiling_Gypsum (#21B: merged, same params;
#     PR-A kept them apart only for lightmap lineage); G1/G3 already white.
#     Access panels (square 0.60 / round dia 0.45) + sprinklers added
#     (G2 12, G1 6, G3 3, atrium 4, stair 1 on a 0.25 m drop pipe).
#  A4 MAT_Concrete_Dark deleted; usages unified into MAT_Concrete
#     (baked base colours were already identical, 202.4 vs 202.3).
#  Roof finish: fluorocarbon topcoat over zinc-rich primer, mid-grey
#     (0.35 linear), metalness 0.4, roughness 0.45; Specular IOR 0.25
#     kept (v14r2 anti-glare).
#  Lightmap: NOT re-baked in PR-A — the v18 atlases are reused (see
#  issue21/A/STATUS.md for the transfer/attachment procedure).
# 21_21 DESIGN SIGHT — Blender build v18 (Issue #18 [site simplify],
# based on the v17 script: v17 + #18 patch, see
# issue17-18/18/patch/apply_site_simplify.py — replayable, do not
# hand-edit this file; re-run the patch on build_2121_v17.py and
# this script (patch/make_v18_script.py) instead).
# v18 changes: lawn/paving desaturated one notch, one paving
# material, flower row deleted, far ground = one GLB layer with a
# radial-gradient texture, trees become a background belt (north
# y~-23.5, new east belt x~60), basement wall tops buried to -0.10
# (below the lawn AND the far-ground strips), site materials
# Specular IOR 0. The page-side half (scene.js) deletes the
# page farGround ring, moves the G2 exhibit spotlight inside the
# gallery (it pooled the elliptical bright spot on the lawn),
# and sets background trees castShadow=false.
# fix20 (Hark PR #20 review, see
# issue17-18/fix-hark-review/20/patch/apply_fix20.py): far-ground
# gradient v2 — centre = lawn final colour (baked grass average
# desaturated 0.45, as the page does), outer = fog colour
# 0xc8d3d6, ramp completes at 220 m, 1024 px + dither; far ground
# enlarged 400 m -> 1600 m so its edge reads as the horizon.
# White line (Hark PR #20 item 2): partition wall SM_Part_G1G2_C
# top buried 0.0 -> -0.10 — its 21x0.2 m white cap poked 5 cm
# above the lawn east of x~42 (roof ends there) and read as the
# white line in aerial + exterior views (raycast-proven).
# 21_21 DESIGN SIGHT — Blender build v17 (dm-6000ada, Blender 5.2.2 headless)
# v17 = v16 + Issue #17 (Leon 2026-11-19 real-device feedback):
#  (a) G3 cafe roof rebuilt as a FOLDED PLATE — high at both ends, valley
#      near x=-20 (photos: ref_aerial.webp + plan elevation strip show tall
#      glass at the west end AND at the east/entrance end, short glass
#      mid-span). v16 descended monotonically to 0.8 m at the east tip, so
#      the 2.6 m entrance door + full-height east glass poked through it.
#      Roof, ceiling (clamped to roof-0.65), north wall, cove strip and the
#      passage roof all follow the new profile; west wall unchanged.
#  (b) Lobby floor: the atrium void is floored over; only the 30-step
#      stairwell stays open (x 0..8, y -5.0..-2.9). Leon confirmed the real
#      lobby has floor here. Court opening untouched.
# v16 Phase 2: basement RE-LAYOUT + geometry fixes (Leon 2026-11-17: the
# underground space was too small AND laid out wrong). v15 basement was
# 816 m2 with G1 as a north strip / G2 as a south hall. Official: total
# floor 1,932 m2 - building area 597.3 m2 = 1,334.7 m2 basement. New BF
# outline 1,336 m2; G1 = 129 m2 trapezoid (WEST, far wall = diagonal wall),
# G2 = 448 m2 rectangle (EAST, x 24..52, y 0..16). Court + atrium + stair /
# elevator core stay (court between G1/G2, north of G2's centre; core at
# the west end; atrium connects them). Phase 1 fixes kept: G1 walls white,
# red sphere true red, G2 ceiling board-formed gray, lawn muted, benches.
# Phase 2 items in this file: 6 court-roof rim, 7 court tree to pit floor,
# 8 tree-top cards tilted/smaller, 9 G1 ceiling follows diagonal wall,
# 10 real entrance doorway (segmented block), 11 G3 ceiling = Section C,
# 12 G3 columns 30%/55% of north wall, 13 G1 window left of far wall,
# 14 atrium white box = slit window (real feature, kept), 16 G2 east door
# to far east end (x=52, y=1.0). Atrium roof: NO skylight (confirmed:
# plan_section.png shows a continuous folded plate).
# Builds the real two-wing museum + site + true interior (atrium, sunken court,
# Gallery 1/2/3, stair, elevator) from researched dimensions, exports GLB for web.
# Units: metres. X = east (building length), Y = south (garden front), Z = up.
# Ground floor Z=0; basement floor Z=-4.8.
# Reference photos: design2121/ref_aerial.webp, ref_exterior.jpg, ref_interior.webp
# Facts (verified): two trapezoidal wings (museum 395 m2 + cafe 202 m2 = 597.3 m2
# building area), 54 m folded steel plate roof, 80% underground, G1 133 m2,
# G2 443 m2 (4.8 m ceiling, columns), G3 110 m2, triangular sunken court,
# double-height trapezoidal atrium void, floating concrete stair, trapezoidal
# elevator, 11 m double glazing, cedars at rear (north), lawn + courtyard front.
# Inferred/approximate (stated honestly in the record): exact footprint polygon,
# roof heights, interior partition positions, exhibit placement.

import bpy, math, os, random
from mathutils import Vector

OUT_DIR = r"C:\Users\Leon\design2121"
BLEND_PATH = os.path.join(OUT_DIR, "design2121_v22_build.blend")
GLB_PATH = os.path.join(OUT_DIR, "design2121_v22.glb")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------- clean scene ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
for coll in list(bpy.data.collections):
    if coll.name != "Collection":
        bpy.data.collections.remove(coll)

def new_collection(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    return c

COL_SITE   = new_collection("COL_Site")
COL_MUSEUM = new_collection("COL_Museum_Wing")
COL_CAFE   = new_collection("COL_Cafe_Wing")
COL_INTER  = new_collection("COL_Interior")
COL_EXH    = new_collection("COL_Exhibits")

# ---------- materials ----------
def mat_principled(name, color, metallic=0.0, rough=0.8, alpha=1.0, emission=None, emission_strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = 'DITHERED'
        except Exception:
            pass
        m.blend_method = 'BLEND'
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return m

MAT_CONCRETE = mat_principled("MAT_Concrete", (0.66, 0.64, 0.60), rough=0.55)  # #21A A2: fair-faced concrete roughness ~0.55 (checklist §4)

def add_concrete_noise(mat, scale=2.0, strength=0.12, lo=(0.55, 0.55, 0.55), hi=(0.70, 0.70, 0.70)):
    """Subtle procedural variation so the concrete is not a flat colour
    (hints at board-formed concrete). NOTE: the ramp REPLACES the base
    colour, so lo/hi ARE the baked colour — set them dark for paving."""
    try:
        nt = mat.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = scale
        tex.inputs["Detail"].default_value = 2.0
        tex.inputs["Roughness"].default_value = 0.7
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.5 - strength
        ramp.color_ramp.elements[0].color = (*lo, 1.0)
        ramp.color_ramp.elements[1].position = 0.5 + strength
        ramp.color_ramp.elements[1].color = (*hi, 1.0)
        nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    except Exception as e:
        print("concrete noise warning:", e)

add_concrete_noise(MAT_CONCRETE)
MAT_STEEL = mat_principled("MAT_Steel_Roof", (0.35, 0.35, 0.35), metallic=0.4, rough=0.45)  # #21A §2: fluorocarbon topcoat over zinc-rich primer, mid-grey; metalness 0.3-0.5, roughness ~0.45
try:
    # v14r2: cut the grazing-angle sky reflection further — at the low front
    # angle the roof still mirrored the bright sky white. Specular IOR 0.5
    # was not enough; 0.25 kills the Fresnel wash while keeping a steel read.
    MAT_STEEL.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.25
except Exception as e:
    print("steel specular warning:", e)
MAT_STEEL_DARK = mat_principled("MAT_Steel_Dark", (0.30, 0.31, 0.32), metallic=0.8, rough=0.45)

def add_board_form(mat, scale=5.0):
    """Film-faced plywood formwork (900x1800 panels), NOT timber boards:
    smooth concrete with a regular panel-joint grid + P-con tie holes
    (the holes are real discs, see tie_holes()). No wood grain.
    #21A (checklist §4, issue #21 §3 A2): panel 900 wide x 1800 tall,
    joints every 0.9 m (U) / 1.8 m (V). The bake plane is 1.8 m and the
    texture tiles every 1.8 m (cube_project 1.8), so Brick Width/Row Height
    are set in tile fractions: width 0.9/1.8*scale, height 1.8/1.8*scale
    (scale=5.0 -> 2.5 / 5.0). Joints are built from math nodes, NOT the
    Brick texture: Blender 5.2's Brick node has no Offset input (probe:
    inputs are Vector/Color1/Color2/Mortar/Scale/Mortar Size/Mortar
    Smooth/Bias/Brick Width/Row Height only), so its joints are always
    staggered half a brick — wrong for 900x1800 formwork panels, whose
    joints align in a grid. The math grid below is exact: lines every
    0.9 m (U) / 1.8 m (V) on the 1.8 m bake tile, 8 mm wide.
    NOTE (v21 PR-D [Tex18]): a 1.8 m tile IS a multiple of both
    0.9 m (2 joints) and 1.8 m (1 joint), so the joint phase is
    continuous across tile boundaries — the 2.0 m tile jogged
    0.2 m at each boundary (spacings read 0.9 / 1.1 alternating).
    Verified by metering the baked PNG (see D/STATUS.md)."""
    try:
        nt = mat.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 6.0
        tex.inputs["Detail"].default_value = 3.0
        tex.inputs["Roughness"].default_value = 0.7
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.35
        ramp.color_ramp.elements[0].color = (0.20, 0.20, 0.19, 1.0)
        ramp.color_ramp.elements[1].position = 0.65
        ramp.color_ramp.elements[1].color = (0.56, 0.56, 0.54, 1.0)
        nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        # Panel-joint grid from math nodes (see docstring): distance in metres
        # from each point to the nearest joint line, per axis, then a hard
        # 8 mm line mask. 1.0 in the mortar, 0.0 in the panel.
        _tc = nt.nodes.new("ShaderNodeTexCoord")
        _sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(_tc.outputs["Generated"], _sep.inputs["Vector"])
        def _grid_axis(_coord_out, _cell_m, _tile_m=1.8):  # PR-D [Tex18]: was 2.0
            _mul = nt.nodes.new("ShaderNodeMath")
            _mul.operation = 'MULTIPLY'
            _mul.inputs[1].default_value = _tile_m / _cell_m
            nt.links.new(_coord_out, _mul.inputs[0])
            _fr = nt.nodes.new("ShaderNodeMath")
            _fr.operation = 'FRACT'
            nt.links.new(_mul.outputs["Value"], _fr.inputs[0])
            _om = nt.nodes.new("ShaderNodeMath")
            _om.operation = 'SUBTRACT'
            _om.inputs[0].default_value = 1.0
            nt.links.new(_fr.outputs["Value"], _om.inputs[1])
            _mn = nt.nodes.new("ShaderNodeMath")
            _mn.operation = 'MINIMUM'
            nt.links.new(_fr.outputs["Value"], _mn.inputs[0])
            nt.links.new(_om.outputs["Value"], _mn.inputs[1])
            _tom = nt.nodes.new("ShaderNodeMath")
            _tom.operation = 'MULTIPLY'
            _tom.inputs[1].default_value = _cell_m
            nt.links.new(_mn.outputs["Value"], _tom.inputs[0])
            return _tom.outputs["Value"]
        _dx = _grid_axis(_sep.outputs["X"], 0.9)
        _dy = _grid_axis(_sep.outputs["Y"], 1.8)
        _dmin = nt.nodes.new("ShaderNodeMath")
        _dmin.operation = 'MINIMUM'
        nt.links.new(_dx, _dmin.inputs[0])
        nt.links.new(_dy, _dmin.inputs[1])
        _line = nt.nodes.new("ShaderNodeMath")
        _line.operation = 'LESS_THAN'
        _line.inputs[1].default_value = 0.004  # half of the 8 mm joint
        nt.links.new(_dmin.outputs["Value"], _line.inputs[0])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.25
        bump.inputs["Distance"].default_value = 0.05
        nt.links.new(_line.outputs["Value"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        # darken mortar lines in the colour as well: only the colour bakes
        # into the glTF texture, the procedural bump does not export
        mix = nt.nodes.new("ShaderNodeMixRGB")
        mix.blend_type = 'MIX'
        mix.inputs[2].default_value = (0.14, 0.14, 0.13, 1.0)
        nt.links.new(_line.outputs["Value"], mix.inputs[0])
        nt.links.new(ramp.outputs["Color"], mix.inputs[1])
        nt.links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
    except Exception as e:
        print("board-form warning:", e)

def add_big_blotch(mat, scale=1.5, strength=0.30):
    """Large-scale (0.5-1 m) colour blotches so the concrete reads at a
    distance; fine grain alone disappears in the bake."""
    try:
        nt = mat.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = scale
        tex.inputs["Detail"].default_value = 2.0
        tex.inputs["Roughness"].default_value = 0.8
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.30
        ramp.color_ramp.elements[0].color = (0.40, 0.40, 0.38, 1.0)
        ramp.color_ramp.elements[1].position = 0.70
        ramp.color_ramp.elements[1].color = (0.78, 0.78, 0.76, 1.0)
        nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
        mix = nt.nodes.new("ShaderNodeMixRGB")
        mix.blend_type = 'MIX'
        mix.inputs[0].default_value = strength
        nt.links.new(ramp.outputs["Color"], mix.inputs[2])
        links = bsdf.inputs["Base Color"].links
        if links:
            nt.links.new(links[0].from_socket, mix.inputs[1])
        else:
            rgb = nt.nodes.new("ShaderNodeRGB")
            rgb.outputs[0].default_value = bsdf.inputs["Base Color"].default_value
            nt.links.new(rgb.outputs["Color"], mix.inputs[1])
        nt.links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
    except Exception as e:
        print("big blotch warning:", e)

def _color_mix(mat, color2, fac_value):
    """Insert a MixRGB between the current Base Color source and the BSDF."""
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.blend_type = 'MIX'
    mix.inputs[0].default_value = fac_value
    mix.inputs[2].default_value = (*color2, 1.0)
    links = bsdf.inputs["Base Color"].links
    if links:
        nt.links.new(links[0].from_socket, mix.inputs[1])
    else:
        rgb = nt.nodes.new("ShaderNodeRGB")
        rgb.outputs[0].default_value = bsdf.inputs["Base Color"].default_value
        nt.links.new(rgb.outputs["Color"], mix.inputs[1])
    nt.links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
    return mix

def add_steel_detail(mat):
    """Fine brushed streaks on the folded steel plate. #21A A1: the panel-seam
    brick is gone — the 16 mm plate is site-welded, seams ground invisible
    (checklist §4); no dark strips on the roof."""
    try:
        nt = mat.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mapping = nt.nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (1.0, 12.0, 1.0)
        nt.links.new(tc.outputs["Generated"], mapping.inputs["Vector"])
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 3.0
        noise.inputs["Detail"].default_value = 2.0
        nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
        m = nt.nodes.new("ShaderNodeMath")
        m.operation = 'MULTIPLY'
        m.inputs[1].default_value = 0.30
        nt.links.new(noise.outputs["Fac"], m.inputs[0])
        mix = _color_mix(mat, (0.30, 0.30, 0.30), 0.0)  # #21A: streak tone follows the new mid-grey base
        nt.links.new(m.outputs["Value"], mix.inputs[0])
        # #21A A1: panel-seam brick deleted (see docstring above)
    except Exception as e:
        print("steel detail warning:", e)

def add_grass_detail(mat):
    """Mowing stripes (Wave bands) + speckle variation on the lawn."""
    try:
        nt = mat.node_tree
        wave = nt.nodes.new("ShaderNodeTexWave")
        wave.wave_type = 'BANDS'
        wave.bands_direction = 'X'
        wave.inputs["Scale"].default_value = 1.5
        wave.inputs["Distortion"].default_value = 1.5
        wave.inputs["Detail"].default_value = 2.0
        m = nt.nodes.new("ShaderNodeMath")
        m.operation = 'MULTIPLY'
        m.inputs[1].default_value = 0.28
        nt.links.new(wave.outputs["Fac"], m.inputs[0])
        mix = _color_mix(mat, (0.07, 0.17, 0.05), 0.0)
        nt.links.new(m.outputs["Value"], mix.inputs[0])
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 9.0
        noise.inputs["Detail"].default_value = 2.0
        m = nt.nodes.new("ShaderNodeMath")
        m.operation = 'MULTIPLY'
        m.inputs[1].default_value = 0.25
        nt.links.new(noise.outputs["Fac"], m.inputs[0])
        mix2 = _color_mix(mat, (0.06, 0.15, 0.045), 0.0)
        # v16: large-scale darker patches so the lawn is not one flat green
        _pn = nt.nodes.new("ShaderNodeTexNoise")
        _pn.inputs["Scale"].default_value = 2.5
        _pn.inputs["Detail"].default_value = 2.0
        _pm = nt.nodes.new("ShaderNodeMath")
        _pm.operation = 'MULTIPLY'
        _pm.inputs[1].default_value = 0.22
        nt.links.new(_pn.outputs["Fac"], _pm.inputs[0])
        mix3 = _color_mix(mat, (0.04, 0.10, 0.03), 0.0)
        nt.links.new(_pm.outputs["Value"], mix3.inputs[0])
        nt.links.new(m.outputs["Value"], mix2.inputs[0])
    except Exception as e:
        print("grass detail warning:", e)

def add_wood_grain(mat):
    """Wood grain: ring wave + noise, mixed into the base colour."""
    try:
        nt = mat.node_tree
        wave = nt.nodes.new("ShaderNodeTexWave")
        wave.wave_type = 'RINGS'
        wave.rings_direction = 'X'
        wave.inputs["Scale"].default_value = 6.0
        wave.inputs["Distortion"].default_value = 5.0
        wave.inputs["Detail"].default_value = 3.0
        m = nt.nodes.new("ShaderNodeMath")
        m.operation = 'MULTIPLY'
        m.inputs[1].default_value = 0.45
        nt.links.new(wave.outputs["Fac"], m.inputs[0])
        mix = _color_mix(mat, (0.38, 0.26, 0.15), 0.0)
        nt.links.new(m.outputs["Value"], mix.inputs[0])
    except Exception as e:
        print("wood grain warning:", e)

def add_speckle(mat, scale=12.0, strength=0.18, dark=(0.55, 0.55, 0.53)):
    """Fine aggregate speckle (paving / granite)."""
    try:
        nt = mat.node_tree
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = scale
        noise.inputs["Detail"].default_value = 3.0
        m = nt.nodes.new("ShaderNodeMath")
        m.operation = 'MULTIPLY'
        m.inputs[1].default_value = strength
        nt.links.new(noise.outputs["Fac"], m.inputs[0])
        mix = _color_mix(mat, dark, 0.0)
        nt.links.new(m.outputs["Value"], mix.inputs[0])
    except Exception as e:
        print("speckle warning:", e)

def add_paving_joints(mat):
    """Visible 1 m stone joints (Brick) so the paving is not a flat slab."""
    try:
        nt = mat.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        brick = nt.nodes.new("ShaderNodeTexBrick")
        brick.inputs["Scale"].default_value = 2.0
        brick.inputs["Mortar Size"].default_value = 0.02
        brick.inputs["Brick Width"].default_value = 1.0
        brick.inputs["Row Height"].default_value = 1.0
        m = nt.nodes.new("ShaderNodeMath")
        m.operation = 'MULTIPLY'
        m.inputs[1].default_value = 0.9
        nt.links.new(brick.outputs["Factor"], m.inputs[0])
        mix = _color_mix(mat, (0.25, 0.25, 0.24), 0.0)
        nt.links.new(m.outputs["Value"], mix.inputs[0])
    except Exception as e:
        print("paving joints warning:", e)

# Board-formed concrete for the atrium walls / stair / G2 columns (seen close-up)
MAT_CONCRETE_BOARD = mat_principled("MAT_Concrete_Board", (0.38, 0.37, 0.36), rough=0.55)  # #21A A2: roughness ~0.55
add_board_form(MAT_CONCRETE_BOARD)
add_big_blotch(MAT_CONCRETE, scale=1.5, strength=0.30)
add_big_blotch(MAT_CONCRETE_BOARD, scale=1.5, strength=0.30)
add_steel_detail(MAT_STEEL)
MAT_TIEHOLE = mat_principled("MAT_TieHole", (0.22, 0.22, 0.21), rough=0.95)
# v13: real glass — transmission, NOT milky alpha panels
MAT_GLASS = mat_principled("MAT_Glass", (0.45, 0.50, 0.55), metallic=0.0, rough=0.03)
try:
    _gbsdf = MAT_GLASS.node_tree.nodes["Principled BSDF"]
    _gbsdf.inputs["Transmission Weight"].default_value = 1.0
    _gbsdf.inputs["IOR"].default_value = 1.5
except Exception as e:
    print("glass transmission warning:", e)
MAT_WOOD = mat_principled("MAT_Wood_Floor", (0.55, 0.42, 0.28), rough=0.6)
add_wood_grain(MAT_WOOD)
MAT_GRASS = mat_principled("MAT_Grass", (0.06, 0.13, 0.05), rough=1.0)  # #18: one notch darker / less saturated (was 0.055,0.16,0.04)
MAT_FARGROUND = mat_principled("MAT_FarGround", (0.16, 0.26, 0.12), rough=1.0)
add_grass_detail(MAT_GRASS)
MAT_PAVING = mat_principled("MAT_Paving", (0.44, 0.43, 0.41), rough=0.9)  # #18: single paving, slightly darker / neutral
add_concrete_noise(MAT_PAVING, scale=4.0, strength=0.10, lo=(0.30, 0.30, 0.29), hi=(0.44, 0.44, 0.43))
add_speckle(MAT_PAVING, scale=14.0, strength=0.20, dark=(0.22, 0.22, 0.21))
# #18: paving joints (brick) pattern removed — no decorative joints
# #18: MAT_Paving_Dark deleted — one paving material only.
MAT_WHITE = mat_principled("MAT_White_Wall", (0.92, 0.92, 0.90), rough=0.85)
# #21A A3 (checklist §4, issue #21 §3): all ceilings are white gypsum board
# (GB-R 9.5+12.5, EP white paint). Two materials with IDENTICAL parameters —
# #21B: the atrium soffit and the G2 ceilings share one gypsum material
# (MAT_Ceiling_Gypsum, same values as the old MAT_Soffit_Gypsum); the
# re-bake uses a single gypsum lightmap group. G1/G3 ceilings stay
# MAT_White_Wall (white).
MAT_CEILING_GYPSUM = mat_principled("MAT_Ceiling_Gypsum", (0.93, 0.93, 0.91), rough=0.9)
# #21A A3: ceiling access panels (slightly grey-white so the panel reads
# against the ceiling; no lightmap atlas — new objects carry no TEXCOORD_1)
# and sprinkler heads (brass metal; no atlas).
MAT_CEILING_PANEL = mat_principled("MAT_Ceiling_Panel", (0.88, 0.88, 0.86), rough=0.9)
MAT_SPRINKLER = mat_principled("MAT_Sprinkler", (0.55, 0.45, 0.25), metallic=0.9, rough=0.35)
MAT_BLACK = mat_principled("MAT_Black_Metal", (0.08, 0.08, 0.09), metallic=0.6, rough=0.5)
MAT_RED = mat_principled("MAT_Red_Fabric", (0.22, 0.01, 0.02), rough=0.9)
# v16: exhibit-06 core sphere ONLY (probe_red_v16: variant B won — dark red
# base + slight red emissive reads TRUE RED under G2 light; A plain dark red
# went maroon, C shade-disc stayed dark maroon). MAT_RED kept for fabric/panel.
MAT_RED_SPHERE = mat_principled("MAT_Red_Sphere", (0.12, 0.005, 0.01), rough=0.9,
                                emission=(0.9, 0.01, 0.02), emission_strength=0.5)
# v16r2: kill the white specular sheen — diagnostics proved the pink is NOT
# the denoiser (far view identical denoise on/off: 223,158,157) and NOT the
# emission (probe2: higher emission went LIGHTER under AgX). The remaining
# white additive on the camera-facing hemisphere is specular reflection of
# the blown-white floor/room; a matte red ball needs Specular IOR 0.
MAT_RED_SPHERE.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.0
MAT_CERAMIC = mat_principled("MAT_Ceramic", (0.94, 0.93, 0.90), rough=0.25)
MAT_TREE = mat_principled("MAT_Cedar", (0.05, 0.10, 0.05), rough=1.0)
MAT_TREE2 = mat_principled("MAT_Cedar2", (0.04, 0.08, 0.045), rough=1.0)
MAT_TREE3 = mat_principled("MAT_Cedar3", (0.06, 0.12, 0.06), rough=1.0)
MAT_TRUNK = mat_principled("MAT_Trunk", (0.35, 0.26, 0.18), rough=0.95)
MAT_LIGHT = mat_principled("MAT_Pendant_Light", (1.0, 0.95, 0.85), rough=0.4,
                            emission=(1.0, 0.9, 0.7), emission_strength=0.9)
MAT_PLINTH = mat_principled("MAT_Plinth", (0.88, 0.88, 0.86), rough=0.7)

# ---------- helpers ----------
def link(obj, coll):
    coll.objects.link(obj)
    return obj

def set_mat(obj, mat):
    if obj.data and hasattr(obj.data, "materials"):
        obj.data.materials.append(mat)
    return obj

def box(name, loc, dims, mat, coll, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    set_mat(o, mat)
    return link(o, coll)

def mesh_from_pydata(name, verts, faces, mat, coll):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    set_mat(o, mat)
    return link(o, coll)

def wall_quad(name, p1, p2, z0, z1, mat, coll, thick=0.25):
    """Vertical wall between two plan points, from z0 to z1, with thickness."""
    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    t = thick / 2.0
    # 8 corners of a thin box
    v = []
    for (sx, sy, sz) in [(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]:
        bx = x1 + dx * sx + nx * (t if sy else -t)
        by = y1 + dy * sx + ny * (t if sy else -t)
        bz = z0 + (z1 - z0) * sz
        v.append((bx, by, bz))
    faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    return mesh_from_pydata(name, v, faces, mat, coll)

def loft(name, sections, mat, coll):
    """sections: list of (x, [(y,z),...]) with equal point counts. Builds a grid mesh."""
    n = len(sections[0][1])
    verts = []
    for (x, pts) in sections:
        assert len(pts) == n, "loft sections must have equal point counts"
        for (y, z) in pts:
            verts.append((x, y, z))
    faces = []
    ns = len(sections)
    for i in range(ns - 1):
        for j in range(n - 1):
            a = i * n + j
            b = i * n + j + 1
            c = (i + 1) * n + j + 1
            d = (i + 1) * n + j
            faces.append((a, b, c, d))
    return mesh_from_pydata(name, verts, faces, mat, coll)

def solidify(obj, thickness=0.15):
    mod = obj.modifiers.new("Solid", 'SOLIDIFY')
    mod.thickness = thickness
    mod.offset = -1.0
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj

def flat_poly_slab(name, poly, z, thick, mat, coll):
    """Flat slab over a CONVEX plan polygon at height z (top), solidified
    down. Fan triangulation from vertex 0 — no boolean anywhere."""
    verts = [(px, py, z) for (px, py) in poly]
    faces = [(0, i, i + 1) for i in range(1, len(poly) - 1)]
    o = mesh_from_pydata(name, verts, faces, mat, coll)
    solidify(o, thick)
    return o

def boolean_cut(target, cutter, name):
    mod = target.modifiers.new(name, 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = cutter
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return target

def _point_in_tri(px, py, tri):
    (x1, y1), (x2, y2), (x3, y3) = tri
    d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    if abs(d) < 1e-9:
        return False
    a = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / d
    b = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / d
    # v22: 1e-9 tolerance on edge points (float -7e-18, see above).
    return a >= -1e-9 and b >= -1e-9 and (1 - a - b) >= -1e-9

print("=== 21_21 build: header/materials/helpers done ===")

# ================= SITE =================
# #21B: ground-slab voids — the new sunken court triangle, the atrium
# void quad (ground-slab edge (25.9,2.5)->(28.9,9.3) east is 吹抜), and
# the main-stair rect. COURT_TRI is the new court triangle.
COURT_TRI = [(18.72, 2.33), (39.39, -6.33), (35.8, 2.33)]
VOID_QUAD = [(15.9, -4.5), (18.9, 2.3), (35.8, 2.33), (39.39, -6.33)]
STAIR_RECT = (15.63, 28.23, -6.16, -3.29)  # v22: 42 steps, flight to X 28.23

def _in_void(px, py):
    if _point_in_tri(px, py, COURT_TRI):
        return True
    if _point_in_tri(px, py, (VOID_QUAD[0], VOID_QUAD[1], VOID_QUAD[2])) or \
            _point_in_tri(px, py, (VOID_QUAD[0], VOID_QUAD[2], VOID_QUAD[3])):
        return True
    return STAIR_RECT[0] <= px <= STAIR_RECT[1] and STAIR_RECT[2] <= py <= STAIR_RECT[3]

def ground_grid_with_holes(name, mat_top, mat_side, hole_tri, x_step=1.0, y_step=1.0):
    """Lawn slab built as a grid; any quad whose centre falls inside the atrium
    rect or hole_tri is SKIPPED — the openings are part of the construction.
    (The EXACT boolean on the site-ground box silently failed to open the
    court/atrium: down-rays still hit SM_Site_Ground at Z=-0.05 everywhere.)
    Top faces get mat_top (lawn); underside/sides get mat_side (concrete).
    """
    xs, ys = [], []
    x = -47.5
    while x <= 52.5:  # #21B: lawn extends east (basement east edge 48.56)
        xs.append(x); x += x_step
    if xs[-1] < 52.5:
        xs.append(52.5)
    y = -32.5
    while y <= 32.5:
        ys.append(y); y += y_step
    if ys[-1] < 32.5:
        ys.append(32.5)
    verts, faces = [], []
    idx = {}
    for xi, x in enumerate(xs):
        for yi, y in enumerate(ys):
            idx[(xi, yi)] = len(verts)
            verts.append((x, y, -0.05))
    for xi in range(len(xs) - 1):
        for yi in range(len(ys) - 1):
            a = idx[(xi, yi)]; b = idx[(xi + 1, yi)]
            c = idx[(xi + 1, yi + 1)]; d = idx[(xi, yi + 1)]
            cx = (verts[a][0] + verts[b][0] + verts[c][0] + verts[d][0]) / 4.0
            cy = (verts[a][1] + verts[b][1] + verts[c][1] + verts[d][1]) / 4.0
            if _in_void(cx, cy) or _point_in_tri(cx, cy, hole_tri):
                continue
            faces.append((a, b, c, d))
    o = mesh_from_pydata(name, verts, faces, mat_top, COL_SITE)
    solidify(o, 0.1)
    o.data.materials.append(mat_side)
    for poly in o.data.polygons:
        if poly.normal.z > 0.9:
            poly.material_index = 0
        else:
            poly.material_index = 1
    return o

# Ground: big lawn slab (95x65m) with the atrium + court openings built in.
# Top face is lawn; underside/sides are concrete (the underside is the ceiling
# seen from the basement atrium/galleries, so it must NOT be green grass).
BASE_Z = -0.05
# #21B: COURT_TRI moved to the top of the SITE section (new court triangle).
ground = ground_grid_with_holes("SM_Site_Ground", MAT_GRASS, MAT_CONCRETE, COURT_TRI)  # #21A A4: MAT_Concrete_Dark deleted
# v13: 400x400 m far ground (top Z=-0.07, just below the lawn slab) so the
# aerial has ground context instead of a black void. NOTE: this grows the
# model bbox from 95x65 m to 400x400 m — the page camera fit must account.
# v15r3: the far ground was ONE solid 400x400 box — it sealed the atrium
# void and the sunken court at Z=-0.07 (the "green ceiling" in CAM_Atrium,
# the green triangle in CAM_Court, the green foreground in CAM_Hall_West:
# all three were this plane, MAT_FARGROUND, not the lawn). Rebuilt as 4
# strips OUTSIDE the 95x65 lawn, so the atrium void and the court stay open.
# #18: far ground is the ONE ground layer (page-side farGround ring
# is deleted in scene.js instead). Strips keep world-mapped UVs so
# the radial-gradient texture (attached after the bake) reads
# continuously across all four strips.
_FAR_OBJS = []
for _fname, _fc, _fs in [
        # #20: far ground enlarged 400 m -> 1600 m (Hark item 1): the
        # 400 m edge sat ~2.1 deg above the true horizon and read as
        # a floating straight edge; the 1600 m edge sits ~0.5 deg
        # above it and reads as the horizon itself. Lawn hole
        # unchanged (x -47.5..47.5, y -32.5..32.5).
        ("SM_Site_FarGround_North", (0, -416.25), (1600, 767.5)),
        ("SM_Site_FarGround_South", (0, 416.25), (1600, 767.5)),
        ("SM_Site_FarGround_West", (-423.75, 0), (752.5, 65)),
        ("SM_Site_FarGround_East", (426.25, 0), (747.5, 65))]:  # #21B: lawn east edge 52.5
    # #20: flat plane, NOT a box. A ground plane has no underside;
    # a thin box's bottom face becomes coplanar with the top in
    # the web pipeline (join node scale 800 -> quantize collapses
    # the 0.06 m thickness) and z-fights it; the bottom face
    # carries default cube UVs that sample the fog region, so the
    # foreground rendered light grey at grazing angles. Plane at
    # the box's former top height (-0.07), CCW from +Z, with its
    # own UVMap so the world-mapped UV loop below finds it.
    _fob = mesh_from_pydata(_fname,
        [(-_fs[0] / 2, -_fs[1] / 2, 0), (_fs[0] / 2, -_fs[1] / 2, 0),
         (_fs[0] / 2, _fs[1] / 2, 0), (-_fs[0] / 2, _fs[1] / 2, 0)],
        [(0, 1, 2, 3)], MAT_FARGROUND, COL_SITE)
    _fob.location = (_fc[0], _fc[1], -0.07)
    _fob.data.uv_layers.new(name="UVMap")
    _FAR_OBJS.append(_fob)
# #18: top-face UVs from world position (texture spans 800 m).
for _fob in _FAR_OBJS:
    _fme = _fob.data
    _fuv = _fme.uv_layers.get("UVMap")
    if _fuv is not None:
        for _fpoly in _fme.polygons:
            if _fpoly.normal.z > 0.9:
                for _fli in _fpoly.loop_indices:
                    _fv = _fme.vertices[_fme.loops[_fli].vertex_index].co
                    _fuv.data[_fli].uv = ((_fob.location.x + _fv.x + 800.0) / 1600.0,  # #20: texture spans 1600 m now
                                          (_fob.location.y + _fv.y + 800.0) / 1600.0)
# Paved courtyard between the two wings (x -14..-5) + forecourt south of museum
# #18: tops flush with the lawn (top -0.03, 2 cm above lawn top
# -0.05) — the old 9-11 cm proud edges read as white outline lines.
# One paving material; slabs no longer overlap in plan, so no stagger.
box("SM_Site_Courtyard", (-9.5, 0, -0.06), (9, 14, 0.06), MAT_PAVING, COL_SITE)  # #21B
box("SM_Site_Forecourt", (10, 11, -0.06), (30, 8, 0.06), MAT_PAVING, COL_SITE)
# Walkway from south garden to courtyard
box("SM_Site_Walkway", (-6, 22, -0.06), (5, 18, 0.06), MAT_PAVING, COL_SITE)
# #18: flower row deleted entirely (6 beds + 6 clusters, ~17.4k
# verts) — lawn runs straight to the wall base instead.
# v13: leaf-card trees — alpha-clipped leaf texture on crossed planes.
# (The old blob/icosphere method read as stacked toy plates.)
LEAF_IMG_PATH = os.path.join(OUT_DIR, "textures_v13", "tree_leaf.png")
_leaf_img = bpy.data.images.load(LEAF_IMG_PATH)
MAT_TREELEAF = mat_principled("MAT_TreeLeaf", (0.8, 0.85, 0.8), rough=0.9)  # #18: leaf multiplier, one notch darker / less saturated
try:
    _lnt = MAT_TREELEAF.node_tree
    _lbsdf = _lnt.nodes["Principled BSDF"]
    _ltex = _lnt.nodes.new("ShaderNodeTexImage")
    _ltex.image = _leaf_img
    _lnt.links.new(_ltex.outputs["Color"], _lbsdf.inputs["Base Color"])
    # v13r2: the 5.2 glTF exporter derives alphaMode from the NODE TREE, not
    # from blend_method (a dead legacy property in 5.2). A Math GREATER_THAN
    # on the alpha is what the exporter recognises as MASK (alphaCutoff).
    _lclip = _lnt.nodes.new("ShaderNodeMath")
    _lclip.operation = 'GREATER_THAN'
    _lclip.inputs[1].default_value = 0.45
    _lnt.links.new(_ltex.outputs["Alpha"], _lclip.inputs[0])
    _lnt.links.new(_lclip.outputs["Value"], _lbsdf.inputs["Alpha"])
    MAT_TREELEAF.alpha_threshold = 0.45
except Exception as e:
    print("tree leaf material warning:", e)
# #18: matte site materials — no sun specular glint on the ground.
for _m18 in (MAT_GRASS, MAT_PAVING, MAT_FARGROUND, MAT_TREELEAF):
    _m18.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.0

def _leaf_card(name, cx, cy, cz, w, h, rot_z, coll, tilt_x=0.0):
    """One leaf-textured quad (own 0..1 UVs — the cube-project UV pass
    skips these by name). Faces +Y in local space; rot_z spins it."""
    verts = [(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], [(0, 1, 2, 3)])
    me.update()
    uv = me.uv_layers.new(name="UVMap")
    uv.data[0].uv = (0, 0)
    uv.data[1].uv = (1, 0)
    uv.data[2].uv = (1, 1)
    uv.data[3].uv = (0, 1)
    o = bpy.data.objects.new(name, me)
    o.location = (cx, cy, cz)
    o.rotation_euler = (tilt_x, 0, rot_z)
    set_mat(o, MAT_TREELEAF)
    return link(o, coll)

def cedar(x, y, h=13.0, r=1.6, z0=0.0):
    """Cedar as alpha leaf cards: trunk cylinder + 3 crossed vertical cards
    (0/60/120 deg) + 2 small horizontal top cards. Irregular outline with
    leaf grain; NOT a cone, NOT stacked blobs.
    v16 P2 item 7: z0 = base elevation (the court tree is planted on the
    pit floor, z0=-4.8, not at ground level). Item 8: top cards smaller
    (w*0.32), tilted 90 deg +/- 18 deg, heights staggered (k*0.9) so the
    flat horizontal cut edge no longer reads as a table top."""
    g = []
    s = _tree_rng.uniform(0.85, 1.15)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=h * 0.28, location=(x, y, z0 + h * 0.14))
    trunk = bpy.context.active_object
    trunk.name = f"SM_Tree_Trunk_{x}_{y}"
    set_mat(trunk, MAT_TRUNK)
    link(trunk, COL_SITE)
    g.append(trunk)
    w = max(3.5, r * 3.2) * s
    ch = h * 0.85 * s
    cz = z0 + 1.0 + ch / 2
    base_rot = _tree_rng.uniform(0, 3.14159)
    for k in range(4):
        _kw = w * _tree_rng.uniform(0.7, 1.0)
        _kh = ch * _tree_rng.uniform(0.7, 1.0)
        _jx = _tree_rng.uniform(-0.4, 0.4)
        _jy = _tree_rng.uniform(-0.4, 0.4)
        g.append(_leaf_card(f"SM_Tree_Card_{x}_{y}_{k}", x + _jx, y + _jy, z0 + 1.0 + _kh / 2, _kw, _kh, base_rot + k * math.radians(45), COL_SITE))
    for k in range(2):
        g.append(_leaf_card(f"SM_Tree_TopCard_{x}_{y}_{k}",
                            x + _tree_rng.uniform(-0.6, 0.6), y + _tree_rng.uniform(-0.6, 0.6),
                            z0 + 1.0 + ch - 1.6 - k * 0.9, w * 0.32, w * 0.32,
                            _tree_rng.uniform(0, 3.14159), COL_SITE, tilt_x=math.radians(_tree_rng.uniform(72, 108))))
    return g

# Cedar row at the rear (north). #18: moved to y ~ -23.5 so the belt
# stands >=15 m from the north walls (museum y=-7, G3 y=-6); it is a
# background belt now, not trees planted on the lawn.
import random
random.seed(2121)
_tree_rng = random.Random(99)
for i in range(14):
    x = -38 + i * 5.6 + random.uniform(-0.8, 0.8)
    y = -23.5 + random.uniform(-1.5, 1.5)
    cedar(x, y, h=random.uniform(11.0, 15.0), r=random.uniform(1.4, 1.9))
# #18: the four isolated cherry trees on the front lawn are deleted
# (was: (-24,18), (30,20), (38,12), (-30,10)) — no lone trees on the lawn.
# East background belt instead: 6 cedars >=15 m east of the museum
# wing (east edge x=42), planted on the far ground (z0=-0.07 = its top).
# NOTE: deleting the cherries shifts _tree_rng, so the kept court
# tree's leaf-card jitter changes within the same ranges; its
# position/height are unchanged.
_belt_rng = random.Random(18)
for _by in (-24, -14, -4, 6, 16, 26):
    _bx = 60.0 + _belt_rng.uniform(-2.0, 2.0)
    cedar(_bx, _by, h=_belt_rng.uniform(11.0, 15.0), r=_belt_rng.uniform(1.4, 1.9), z0=-0.07)

print("=== site done ===")

# ================= HELPERS 2 =================
def wall_varying(name, p1, p2, zb1, zt1, zb2, zt2, mat, coll, thick=0.3):
    """Wall segment between plan points p1->p2; bottom/top Z differ per end."""
    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    t = thick / 2.0
    # bottom face corners (z=zb), top face corners (z=zt), each offset +/-t
    def pt(px, py, z, s):
        return (px + nx * t * s, py + ny * t * s, z)
    v = [pt(x1, y1, zb1, -1), pt(x2, y2, zb2, -1), pt(x2, y2, zb2, 1), pt(x1, y1, zb1, 1),
         pt(x1, y1, zt1, -1), pt(x2, y2, zt2, -1), pt(x2, y2, zt2, 1), pt(x1, y1, zt1, 1)]
    faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    return mesh_from_pydata(name, v, faces, mat, coll)

def glass_strip(name, edge, z_bottom, mat, coll, mullion_every=1.4):
    """Glass wall along a plan edge. edge = list of (x, y, z_top). Down to z_bottom.
    Adds thin vertical mullions."""
    verts, faces = [], []
    n = len(edge)
    for (x, y, zt) in edge:
        verts.append((x, y, z_bottom))
        verts.append((x, y, zt))
    for i in range(n - 1):
        a, b, c, d = 2*i, 2*i+1, 2*i+3, 2*i+2
        faces.append((a, b, c, d))
    g = mesh_from_pydata(name, verts, faces, mat, coll)
    # mullions: vertical thin boxes at intervals along the edge
    acc = 0.0
    for i in range(n - 1):
        (x1, y1, zt1), (x2, y2, zt2) = edge[i], edge[i+1]
        seg = math.hypot(x2-x1, y2-y1)
        k = int(seg / mullion_every)
        for j in range(k + 1):
            f = j / max(k, 1)
            mx, my = x1 + (x2-x1)*f, y1 + (y2-y1)*f
            mz = zt1 + (zt2-zt1)*f
            box(f"{name}_Mullion_{i}_{j}", (mx, my, (z_bottom+mz)/2),
                (0.06, 0.06, mz - z_bottom), MAT_BLACK, coll)
    # horizontal transoms every ~1.35 m (real facade is a dense mullion grid)
    _ztop = max(zt for (_, _, zt) in edge)
    _z = z_bottom + 1.35
    while _z < _ztop - 0.2:
        for i in range(n - 1):
            (x1, y1, zt1), (x2, y2, zt2) = edge[i], edge[i+1]
            if _z > min(zt1, zt2) - 0.1:
                continue
            _mx, _my = (x1 + x2) / 2, (y1 + y2) / 2
            _seg = math.hypot(x2 - x1, y2 - y1)
            _ang = math.atan2(y2 - y1, x2 - x1)
            box(f"{name}_Transom_{i}_{round(_z, 1)}", (_mx, _my, _z),
                (_seg, 0.06, 0.06), MAT_BLACK, coll, rot=(0, 0, _ang))
        _z += 1.35
    return g

# ================= MUSEUM WING (exterior) =================
# Footprint quad: A(-2,-7) B(22,-7) C(42,1) D(-2,7). Area ~404 m2.
# #21B D3: trapezoid roof — north edge 54 m (flat +4.95 to x=41, then down
# to +2.5 at the NE corner); south edge 42 m (flat +3.20, x -3..39);
# west/east edges are the slanted diagonals (NW 4.95 -> SW 3.20;
# SE 3.20 -> NE 2.5). The old scaled profile is NOT used: it put the
# tallest court mullion at ~8.7 m, contradicting the measured #17
# (11.7 m); the north edge stays at the apex so the court mullion
# at B (39.39,-6.33) reaches 4.95-0.02+6.75 = 11.68 m.
# v22 folded-plate roof (frozen trapezoid + height field, r4):
# NW (-10,-7,4.85), NE (43.42,-7,~4.5), SW (-5.60,3.50,4.85),
# SE (39.20,3.50,~4.3); valley V (19.70,3.50,0.2); east point
# E (31.17,3.50,4.3). Folds: A NE->SW, B NE->V. Regions N
# (NW,NE,SW) and M (NE,SW,V) are flat planes; region E (NE,V,SE)
# is a warped plate (see roof_z_at): a flat plane there would
# give E=2.61, not the measured 4.3.
_ROOF_NW = (-10.00, -7.00, 4.85)
_ROOF_NE = (43.42, -7.00, 4.50)
_ROOF_SW = (-5.60, 3.50, 4.85)
_ROOF_SE = (39.20, 3.50, 4.30)
_ROOF_V = (19.70, 3.50, 0.20)
_ROOF_E = (31.17, 3.50, 4.30)
# E is 58.8% along V->SE (south edge): (31.17-19.70)/(39.20-19.70).
_ROOF_E_T = (31.17 - 19.70) / (39.20 - 19.70)

def _tri_bary(px, py, tri):
    """Barycentric weights of (px,py) in triangle tri (None if degenerate)."""
    (x1, y1), (x2, y2), (x3, y3) = tri
    d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    if abs(d) < 1e-12:
        return None
    a = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / d
    b = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / d
    return (a, b, 1.0 - a - b)

def _plane_z(px, py, p1, p2, p3):
    """Height of the plane through 3D points p1/p2/p3 at plan (px,py)."""
    w = _tri_bary(px, py, ((p1[0], p1[1]), (p2[0], p2[1]), (p3[0], p3[1])))
    if w is None:
        return p1[2]
    return w[0] * p1[2] + w[1] * p2[2] + w[2] * p3[2]

def roof_z_north(x):
    """North edge: NW 4.85 -> NE ~4.5, linear (r4: inferred, straight)."""
    return 4.85 + (4.50 - 4.85) * ((x + 10.0) / 53.42)

def roof_z_south(x):
    """South ROOF EDGE (Y=3.50) height at Blender X: W 4.85 -> V 0.2
    -> E 4.3 -> SE 4.3 (flat). Outside the south edge proper the
    west/east diagonal edges apply (west flat 4.85, east 4.3->4.5)."""
    if x < -5.60:
        return 4.85  # west diagonal: NW 4.85 -> SW 4.85 (flat)
    if x <= 19.70:
        return 4.85 + (0.20 - 4.85) * ((x + 5.60) / 25.30)
    if x <= 31.17:
        return 0.20 + (4.30 - 0.20) * ((x - 19.70) / 11.47)
    if x <= 39.20:
        return 4.30
    return 4.30 + (4.50 - 4.30) * ((x - 39.20) / 4.22)  # east diagonal: SE 4.3 -> NE 4.5

def edge_y_north(x):
    return -7.0

def edge_y_south(x):
    """Roof south edge Y at Blender X: west diagonal NW->SW, then
    flat Y=3.50, then east diagonal SE->NE."""
    if x < -5.60:  # west diagonal: (-10,-7) -> (-5.60,3.50)
        return -7.0 + 10.5 * ((x + 10.0) / 4.40)
    if x <= 39.20:
        return 3.50
    return 3.50 - 10.5 * ((x - 39.20) / 4.22)  # east diagonal: (39.20,3.50) -> (43.42,-7)

def roof_sections(xs):
    # v22: sections sample the region-based roof_z_at directly
    # (single source of truth; the v21 zm mid-ridge is gone).
    secs = []
    for x in xs:
        yn, ys = edge_y_north(x), edge_y_south(x)
        pts = []
        for f in (0.0, 0.25, 0.5, 0.75, 1.0):
            y = yn + (ys - yn) * f
            pts.append((y, roof_z_at(x, y)))
        secs.append((x, pts))
    return secs

def roof_z_at(x, y):
    """v22 folded-plate roof height at plan point (x, y). Regions N/M
    are flat planes through their corners; region E is the warped
    plate: barycentric plane through NE/V/SE plus a warp that
    honours the south-edge piecewise profile exactly (V->E rising,
    E->SE flat 4.3) while keeping the fold-B and east-edge profiles
    linear. The warp vanishes on fold B (c=0) and on the east edge
    (b=0); on the south edge (a=0) it equals the tent T(c):
    2.8705*c for c<=E_T, 4.1*(1-c) above — the exact difference
    between the piecewise south profile and the linear barycentric
    profile (slopes 6.9705 vs 4.1 in c). Its crease runs from E
    toward the east edge (fading to zero there). Points outside
    the trapezoid fall through to region E with clamped weights
    (a reasonable extrapolation for soffit-grid vertices outside
    the FOOT, which are filtered out before meshing).
    Used by the atrium soffit (and the south glass tops) so both
    sit below the roof instead of poking through it."""
    _N = ((_ROOF_NW[0], _ROOF_NW[1]), (_ROOF_NE[0], _ROOF_NE[1]), (_ROOF_SW[0], _ROOF_SW[1]))
    _M = ((_ROOF_NE[0], _ROOF_NE[1]), (_ROOF_SW[0], _ROOF_SW[1]), (_ROOF_V[0], _ROOF_V[1]))
    _E = ((_ROOF_NE[0], _ROOF_NE[1]), (_ROOF_V[0], _ROOF_V[1]), (_ROOF_SE[0], _ROOF_SE[1]))
    if _point_in_tri(x, y, _N):
        return _plane_z(x, y, _ROOF_NW, _ROOF_NE, _ROOF_SW)
    if _point_in_tri(x, y, _M):
        return _plane_z(x, y, _ROOF_NE, _ROOF_SW, _ROOF_V)
    w = _tri_bary(x, y, _E)
    if w is None:
        return 4.30
    a, b, c = w
    a = max(0.0, min(1.0, a)); b = max(0.0, min(1.0, b)); c = max(0.0, min(1.0, c))
    _s = a + b + c
    if _s <= 0:
        return 4.30
    a, b, c = a / _s, b / _s, c / _s
    _z = a * 4.50 + b * 0.20 + c * 4.30
    if c <= _ROOF_E_T:
        _W = 2.8705 / (1.0 - c) if c < 1.0 else 0.0
    else:
        _W = 4.10 / c if c > 0.0 else 0.0
    return _z + _W * b * c

def roof_grid_with_hole(name, mat, coll, hole_tri, x_step=0.25, f_step=0.05):
    """Dense-grid roof built from the same profile as roof_sections, but any
    quad whose centre falls inside hole_tri is SKIPPED — the opening is part
    of the construction, not a boolean. (The EXACT boolean on the lofted +
    solidified roof silently failed: 9 large faces still covered the court.)
    """
    xs = []
    x = -10.0  # v22: roof x-range -10..43.42 (frozen trapezoid)
    while x <= 43.42:
        xs.append(x)
        x += x_step
    if xs[-1] < 43.42:
        xs.append(43.42)
    fs = []
    f = 0.0
    while f <= 1.0:
        fs.append(f)
        f += f_step
    if fs[-1] < 1.0:
        fs.append(1.0)
    verts, faces = [], []
    idx = {}
    for xi, x in enumerate(xs):
        yn, ys = edge_y_north(x), edge_y_south(x)
        for fi, f in enumerate(fs):
            y = yn + (ys - yn) * f
            z = roof_z_at(x, y)  # v22: region-based folded plate
            idx[(xi, fi)] = len(verts)
            verts.append((x, y, z))
    nfx = len(fs)
    for xi in range(len(xs) - 1):
        for fi in range(len(fs) - 1):
            a = idx[(xi, fi)]; b = idx[(xi, fi + 1)]
            c = idx[(xi + 1, fi + 1)]; d = idx[(xi + 1, fi)]
            cx = (verts[a][0] + verts[b][0] + verts[c][0] + verts[d][0]) / 4.0
            cy = (verts[a][1] + verts[b][1] + verts[c][1] + verts[d][1]) / 4.0
            if _point_in_tri(cx, cy, hole_tri):
                continue  # leave the opening
            faces.append((a, b, c, d))
    o = mesh_from_pydata(name, verts, faces, mat, coll)
    solidify(o, 0.18)
    return o

# #21A A1: roof seam ribbon function deleted — the 16 mm roof plate is a single
# welded sheet, seams ground invisible; no dark strips on the roof.

def _line_intersect(p1, d1, p2, d2):
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 1e-9:
        return None
    t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
    return (p1[0] + d1[0] * t, p1[1] + d1[1] * t)

def roof_opening_rim(name, tri, mat, coll, inset=0.50, outset=1.00, lift=0.08, thick=0.12, seg=12):
    """v16 P2 item 6: smooth triangular rim/curb around the court roof
    opening. The roof grid leaves a stepped edge (0.125 m x-steps, ~0.35 m
    y-steps); this border follows the roof surface (z = roof + 0.08) and
    hides the steps. Built as a triangle ring: the outer triangle is
    COURT_TRI expanded 1.00 m, the inner triangle is shrunk 0.50 m (the
    steps reach ~0.37 m either side of the edge; v16r3 widened the outset
    to 1.00 m after the close-up crops showed roof holes still showing
    outside the 0.50 m band), joined as quads sharing
    vertices so there are no gaps or overlaps. v16r2: each edge is
    SUBDIVIDED into 12 segments (the first version used one flat quad per
    edge, which could not follow the sloped/curved roof and dipped under
    it, leaving the steps visible). Solidified 0.12 down so it reads as a
    curb from above and below. No grid densification (that would push the
    GLB over 12 MB)."""
    cx = sum(p[0] for p in tri) / 3.0
    cy = sum(p[1] for p in tri) / 3.0
    edges = []
    for i in range(3):
        ax, ay = tri[i]
        bx, by = tri[(i + 1) % 3]
        ex, ey = bx - ax, by - ay
        L = math.hypot(ex, ey)
        ux, uy = ex / L, ey / L
        nx, ny = uy, -ux
        mx, my = (ax + bx) / 2.0, (ay + by) / 2.0
        if (nx * (cx - mx) + ny * (cy - my)) > 0:
            nx, ny = -nx, -ny
        edges.append(((ax, ay), (ux, uy), (nx, ny)))
    def offset_poly(dist):
        pts = []
        for i in range(3):
            (a1, d1, n1) = edges[i]
            (a0, d0, n0) = edges[(i - 1) % 3]
            p1 = (a1[0] + n1[0] * dist, a1[1] + n1[1] * dist)
            p0 = (a0[0] + n0[0] * dist, a0[1] + n0[1] * dist)
            pts.append(_line_intersect(p0, d0, p1, d1))
        return pts
    outer = offset_poly(outset)
    inner = offset_poly(-inset)
    verts, faces = [], []
    for i in range(3):
        j = (i + 1) % 3
        for s in range(seg):
            t0 = s / seg
            t1 = (s + 1) / seg
            ox0 = outer[i][0] + (outer[j][0] - outer[i][0]) * t0
            oy0 = outer[i][1] + (outer[j][1] - outer[i][1]) * t0
            ox1 = outer[i][0] + (outer[j][0] - outer[i][0]) * t1
            oy1 = outer[i][1] + (outer[j][1] - outer[i][1]) * t1
            ix0 = inner[i][0] + (inner[j][0] - inner[i][0]) * t0
            iy0 = inner[i][1] + (inner[j][1] - inner[i][1]) * t0
            ix1 = inner[i][0] + (inner[j][0] - inner[i][0]) * t1
            iy1 = inner[i][1] + (inner[j][1] - inner[i][1]) * t1
            o0 = (ox0, oy0, roof_z_at(ox0, oy0) + lift)
            o1 = (ox1, oy1, roof_z_at(ox1, oy1) + lift)
            i1 = (ix1, iy1, roof_z_at(ix1, iy1) + lift)
            i0 = (ix0, iy0, roof_z_at(ix0, iy0) + lift)
            base = len(verts)
            verts.extend([o0, o1, i1, i0])
            faces.append((base, base + 1, base + 2, base + 3))
    o = mesh_from_pydata(name, verts, faces, mat, coll)
    solidify(o, thick)
    return o

# v22 museum-wing exterior. Roof is the frozen trapezoid: north edge
# 53.42 m (-10,-7)->(43.42,-7), south edge 44.8 m (-5.60,3.50)->
# (39.20,3.50); north edge 4.85->~4.5 linear, south edge W 4.85 ->
# V 0.2 -> E 4.3 -> SE 4.3 (see roof_z_north/roof_z_south). The v21
# D3 trapezoid (54 m north, 42 m south, apex +4.95, south +3.20)
# is superseded by the r4 frozen plan + height profile.
MUSEUM_XS = [-10, -5.6, 5, 15, 19.7, 25, 31.17, 39.2, 43.42]  # v22: key X stations (W corner, valley, E point, SE corner)
roof_m = roof_grid_with_hole("SM_Museum_Roof", MAT_STEEL, COL_MUSEUM, COURT_TRI, x_step=0.125, f_step=0.025)
# #21A A1: museum roof seam ribbons deleted (3 strips)
# v16 P2 item 6: smooth rim around the court roof opening (lighter steel
# flashing, so it reads as a distinct curb against the darker roof).
# FIX [RIM]: lift 0.30 -> -0.05 — the rim top was +5.25, over the <=5.2
# acceptance line; now +4.90, just below the roof surface (solidify
# goes down 0.90, so the ring still reads as a curb around the opening
# from inside the court, and its outer band hides under the roof solid).
# v22: lift -0.05 kept; the rim top is now ~+4.45 (the roof near the
# court is ~4.5, down from 4.95), still just below the roof surface.
roof_opening_rim("SM_Court_Roof_Rim", COURT_TRI, MAT_STEEL_DARK, COL_MUSEUM,
                 inset=0.90, lift=-0.05, thick=0.90)

# North wall (B1 + ground), straight Y=-7 / Y=-8.56 with the jog at X=29.44.
# FIX [4] (b): the long-window slot moves up — below the slot
# (Z -6.3..0) it is continuous; the slot (Z 0..0.45, sill flush with
# GL) is glazed in two 11.5 m panes (#01/#02); above the slot
# (Z 0.45..roof) is the ground-floor north wall.
wall_varying("SM_Museum_Wall_North_Below", (-10, -7), (29.44, -7), -6.3, 0.0, -6.3, 0.0,  # FIX [4] (b); v22: BFL1 -6.3
             MAT_CONCRETE, COL_MUSEUM, thick=0.35)
wall_varying("SM_Museum_Wall_North_Above", (-10, -7), (29.44, -7), 0.45, 4.85, 0.45, 4.59,  # FIX [4] (b); v22: north profile 4.85->4.59
             MAT_CONCRETE, COL_MUSEUM, thick=0.35)
# Slot infill west of pane 1 and between the panes (Z -0.45..0)
wall_varying("SM_Museum_Wall_North_Slot_W", (-10, -7), (15.63, -7), 0.0, 0.45, 0.0, 0.45,  # FIX [4] (b)
             MAT_CONCRETE, COL_MUSEUM, thick=0.35)
wall_varying("SM_Museum_Wall_North_Slot_Mid", (27.13, -7), (29.44, -7), 0.0, 0.45, 0.0, 0.45,  # FIX [4] (b)
             MAT_CONCRETE, COL_MUSEUM, thick=0.35)
# FIX [4] (b): pane 1 (X 15.63..27.13, Y=-7, Z 0..0.45) + shade strip above (Z 0.45..0.80, projects north 0.3)
box("SM_LongWindow_Pane1", (21.38, -7, 0.225), (11.5, 0.06, 0.45), MAT_GLASS, COL_MUSEUM)  # FIX [4] (b)
box("SM_LongWindow_Shade1", (21.38, -7.15, 0.625), (11.5, 0.30, 0.35), MAT_CONCRETE, COL_MUSEUM)  # FIX [4] (b)
# Jog wall (B1 only, below lawn) + east north wall (Y=-8.56)
wall_varying("SM_Museum_Wall_North_Jog", (29.44, -7), (29.44, -8.56), -6.3, 0.0, -6.3, 0.0,  # FIX [4] (b): top to GL, the new slot sill; v22: BFL1 -6.3
             MAT_CONCRETE, COL_MUSEUM, thick=0.35)
# PR-C [Jog]: ground-floor Jog wall — the B1 wall above stops at GL,
# leaving a 1.2 m wide, full-height slot (x~29.44, z 7.18..8.39)
# through which the north side looks straight into the atrium/court
# (diagonal rays from (28,y,12) hit the court glass at (31,y,2.88)).
# This wall continues the same line and thickness, 0.0..4.59, to meet
# both neighbours' tops (west Above 4.59, east Above_A 4.59); ends
# embed into the west/east wall thickness bands like the B1 wall.
# P-con tie holes on both faces (450x600, 3 cols x 9 rows each).
wall_varying("SM_Museum_Wall_North_Jog_Ground", (29.44, -7), (29.44, -8.56), 0.0, 4.59, 0.0, 4.59,  # v22: north profile at the jog
             MAT_CONCRETE, COL_MUSEUM, thick=0.35)
# (Tie holes for this wall are placed with the other tie-hole grids
# below — tie_holes() is defined later in this script.)
wall_varying("SM_Museum_Wall_NorthEast_Below", (29.44, -8.56), (48.56, -8.56), -6.3, 0.0, -6.3, 0.0,  # FIX [4] (b); v22: BFL1 -6.3
             MAT_CONCRETE, COL_MUSEUM, thick=0.35)
# Ground-floor north wall east of the jog (Y=-8.56, Z 0..roof: 4.59 at
# the jog -> 4.52 at x=41, then 4.50 at the NE corner — the new
# north-edge profile, 4.85->~4.5 linear over 53.42 m).
wall_varying("SM_Museum_Wall_NorthEast_Above_A", (29.44, -8.56), (41, -8.56), 0.45, 4.59, 0.45, 4.52,  # FIX [4] (b); v22: north profile
             MAT_CONCRETE, COL_MUSEUM, thick=0.35)
wall_varying("SM_Museum_Wall_NorthEast_Above_B", (41, -8.56), (43.42, -8.56), 0.45, 4.52, 0.45, 4.50,  # FIX [4] (b); v22: north profile to the NE corner
             MAT_CONCRETE, COL_MUSEUM, thick=0.35)
# Slot infill east of pane 2 (Z -0.45..0)
wall_varying("SM_Museum_Wall_NorthEast_Slot_E", (40.94, -8.56), (48.56, -8.56), 0.0, 0.45, 0.0, 0.45,  # FIX [4] (b)
             MAT_CONCRETE, COL_MUSEUM, thick=0.35)
# FIX [4] (b): pane 2 (X 29.44..40.94, Y=-8.56, Z 0..0.45) + shade strip above (Z 0.45..0.80)
box("SM_LongWindow_Pane2", (35.19, -8.56, 0.225), (11.5, 0.06, 0.45), MAT_GLASS, COL_MUSEUM)  # FIX [4] (b)
box("SM_LongWindow_Shade2", (35.19, -8.71, 0.625), (11.5, 0.30, 0.35), MAT_CONCRETE, COL_MUSEUM)  # FIX [4] (b)

# West entrance block — v22: the west edge is now the slanted line
# NW (-10,-7)->SW (-5.60,3.50), direction (0.3866,0.9225), angle
# 67.35 deg (was 53.13 deg on the old edge). Doorway 3.2 m centred
# at the west-edge midpoint (-7.80,-1.75) — the old centre (-4.75,0)
# lay 2.14 m inside the new wall line. The west edge heights are
# flat 4.85 at both ends, so both segments + lintel top at 4.85
# (v21: 4.95->3.20 along the old edge). Glass door + frames +
# canopy + sign, rotated to the new wall angle.
_ENT_ANG = math.radians(67.35)
_ENT_C = (-7.80, -1.75)
_ENT_DIR = (0.3866, 0.9225)  # west-edge direction (unit)
_ENT_NRM_OUT = (-0.9225, 0.3866)  # outward normal (west) of the west edge
def _ent_pt(s):
    return (_ENT_C[0] + _ENT_DIR[0] * s, _ENT_C[1] + _ENT_DIR[1] * s)
# north segment (toward NW): s -5.695..-1.6, roof flat 4.85
_n0 = _ent_pt(-5.695); _n1 = _ent_pt(-1.6)
wall_varying("SM_Museum_Entrance_Block_N", _n0, _n1, 0.0, 4.85, 0.0, 4.85,
             MAT_CONCRETE, COL_MUSEUM, thick=1.2)
# south segment (toward SW): s 1.6..5.695, roof flat 4.85
_s0 = _ent_pt(1.6); _s1 = _ent_pt(5.695)
wall_varying("SM_Museum_Entrance_Block_S", _s0, _s1, 0.0, 4.85, 0.0, 4.85,
             MAT_CONCRETE, COL_MUSEUM, thick=1.2)
# lintel over the doorway (s -1.6..1.6, Z 2.7..4.85)
wall_varying("SM_Museum_Entrance_Lintel", _n1, _s0, 2.7, 4.85, 2.7, 4.85,
             MAT_CONCRETE, COL_MUSEUM, thick=1.2)
# glass door + frames + canopy + sign (rotated to the wall angle)
box("SM_Museum_Entrance_Door", (_ENT_C[0], _ENT_C[1], 1.35), (3.2, 0.15, 2.7), MAT_GLASS, COL_MUSEUM,
    rot=(0, 0, _ENT_ANG))
box("SM_Museum_Entrance_Frame_L", (_ent_pt(-1.68)[0], _ent_pt(-1.68)[1], 1.35), (0.12, 0.12, 2.7), MAT_BLACK, COL_MUSEUM,
    rot=(0, 0, _ENT_ANG))
box("SM_Museum_Entrance_Frame_R", (_ent_pt(1.68)[0], _ent_pt(1.68)[1], 1.35), (0.12, 0.12, 2.7), MAT_BLACK, COL_MUSEUM,
    rot=(0, 0, _ENT_ANG))
box("SM_Museum_Entrance_Frame_Top", (_ENT_C[0], _ENT_C[1], 2.76), (3.5, 0.12, 0.12), MAT_BLACK, COL_MUSEUM,
    rot=(0, 0, _ENT_ANG))
box("SM_Museum_Entrance_Canopy", (_ENT_C[0] + 0.6 * _ENT_NRM_OUT[0], _ENT_C[1] + 0.6 * _ENT_NRM_OUT[1], 2.98), (4.2, 0.9, 0.08), MAT_STEEL_DARK, COL_MUSEUM,
    rot=(0, 0, _ENT_ANG))
# 21_21 sign plate on the north block (offset 0.66 outward so it sits proud
# of the 1.2-thick wall face, not buried in it)
_sg = _ent_pt(-3.5)
box("SM_Museum_Sign", (_sg[0] + 0.66 * _ENT_NRM_OUT[0], _sg[1] + 0.66 * _ENT_NRM_OUT[1], 3.6), (4.5, 0.12, 0.9), MAT_BLACK, COL_MUSEUM,
    rot=(0, 0, _ENT_ANG))

# South glass facade — v22 (issue #26 r4): glass line Y=2.33, roof
# edge Y=3.50 (1.17 m eave overhang — the glass does NOT move to the
# roof edge). The glass top follows the roof surface directly above
# the glass line (roof_z_at(x, 2.33) minus the soffit offset 0.55 m
# at the glass line: 1.17 m from the edge -> 0.40+0.25*(1.17/2) =
# 0.546 ~= 0.55) — NOT the eave profile: the eave is the roof EDGE
# (Y=3.50) and the glass is set back 1.17 m, where the warped roof
# is up to ~1 m higher (west wing) / lower (east wing) than the
# eave. The task's "top follows the eave" is a shape statement
# (right triangle west, V east), satisfied by this profile; the
# eave remains the roof-edge silhouette in the photos. Custom
# builder: glass_strip's 1.35 m transoms are wrong here — the
# photos show vertical mullions ONLY plus a low base rail, no mid
# transom (vertical blinds inside must not be counted as mullions).
def _south_glass_top(x):
    """Glass-top height at Blender X (roof surface above the glass
    line Y=2.33, minus the 0.55 m soffit offset at the glass line)."""
    return roof_z_at(x, 2.33) - 0.55

def _south_glass_segment(name, xs, y_glass=2.33, base_rail_z=0.35):
    """Glass wall along Y=y_glass for the given X stations; top
    follows _south_glass_top. Vertical mullions at each station +
    one low base rail (z=0.35, photo estimate) — skipped where the
    glass is too low for it (near the valley)."""
    edge = [(x, y_glass, _south_glass_top(x)) for x in xs]
    verts, faces = [], []
    for (x, y, zt) in edge:
        verts.append((x, y, 0.0))
        verts.append((x, y, zt))
    for i in range(len(edge) - 1):
        a, b, c, d = 2*i, 2*i+1, 2*i+3, 2*i+2
        faces.append((a, b, c, d))
    g = mesh_from_pydata(name, verts, faces, MAT_GLASS, COL_MUSEUM)
    for _j, _x in enumerate(xs):
        _zt = _south_glass_top(_x)
        box(f"{name}_Mullion_{_j:02d}", (_x, y_glass, _zt / 2.0),
            (0.06, 0.06, _zt), MAT_BLACK, COL_MUSEUM)
    _min_top = min(_south_glass_top(_x) for _x in xs)
    _rail_z = min(base_rail_z, _min_top - 0.06)
    if _rail_z >= 0.12:
        _x0, _x1 = xs[0], xs[-1]
        box(f"{name}_BaseRail", ((_x0 + _x1) / 2.0, y_glass, _rail_z),
            (_x1 - _x0, 0.06, 0.06), MAT_BLACK, COL_MUSEUM)
    return g

# West wing: right-triangle glass, 11 bays, module 2.30 m
# (25.30/11; photomatch homography gave 11.15 bays at 2.27 m —
# 2,250 mm wins; 2,400 was circularly derived from the rejected
# 46.3 m south edge, do NOT use). Mullions at X=-5.60+k*2.30
# (k=0..11); the first (-5.60) embeds 0.16 m in the west wall
# (the glass starts at the inner-face intersection (-5.44,2.33)).
_WEST_MULLIONS = [-5.60 + 2.30 * k for k in range(12)]
_south_glass_segment("SM_Museum_Glass_South_West", _WEST_MULLIONS)
# Entrance core (freestanding pavilion in front of the glass,
# X 22.4..27.4, Y 2.33..4.83, flat top 4.0 — single photo,
# +/-0.4; exact depth unmeasured). It occludes the valley eave
# behind it (roof edge at X=24.9 is z~2.07, below the core top).
box("SM_Entrance_Core", (24.9, 3.58, 2.0), (5.0, 2.5, 4.0), MAT_CONCRETE, COL_MUSEUM)
# Recessed dark doorway (2.2 wide x 3.0 high, centred X=24.9) on
# the south face (Y=4.83): a dark panel slightly proud of the face
# (no boolean — reads as a doorway from the front).
box("SM_Entrance_Core_Door", (24.9, 4.84, 1.5), (2.2, 0.08, 3.0), MAT_BLACK, COL_MUSEUM)
# Tall banner panel east of the door with a round disc logo
# (schematic, photo-based: the Leon photo shows a tall poster
# with a circular logo east of the doorway).
box("SM_Entrance_Core_Banner", (26.9, 4.84, 2.6), (1.2, 0.06, 2.4), MAT_WHITE, COL_MUSEUM)
bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.45, depth=0.05,
                                    location=(26.9, 4.88, 2.6), rotation=(math.radians(90), 0, 0))
_o = bpy.context.active_object
_o.name = "SM_Entrance_Core_Disc"
set_mat(_o, MAT_BLACK); link(_o, COL_MUSEUM)
# East wing: V-shaped glass V->E, dense verticals ~1.0 m (photo
# estimate, range 1.0-1.4 m — do NOT space at 2.4 m), interrupted
# by the entrance core (X 22.4..27.4): 4 + 5 = 9 verticals total.
_EAST_MULLIONS_W = [19.70, 20.70, 21.70, 22.40]
_EAST_MULLIONS_E = [27.40, 28.40, 29.40, 30.40, 31.17]
_south_glass_segment("SM_Museum_Glass_South_East_W", _EAST_MULLIONS_W)
_south_glass_segment("SM_Museum_Glass_South_East_E", _EAST_MULLIONS_E)
# East end: solid concrete wall E(31.17)->SE(39.20) = 8.03 m, ON THE
# ROOF EDGE (Y=3.50), 0..4.3 (the eave is flat 4.3 there). A wall
# at the glass line (Y=2.33) would poke through the warped roof
# (roof is only 3.57 above the glass line at E) — the solid
# east block's south face is at the eave, per img_8913 (the
# block face steps forward of the glass plane). Schematic door
# slit on its south face (photo-based, unmeasured).
wall_varying("SM_Museum_Wall_South_East", (31.17, 3.50), (39.20, 3.50), -0.10, 4.3, -0.10, 4.3,
             MAT_CONCRETE, COL_MUSEUM, thick=0.35)
box("SM_Museum_EastWall_Door", (35.0, 3.70, 1.05), (0.9, 0.06, 2.1), MAT_BLACK, COL_MUSEUM)
# Return wall closing the 1.17 m facade step at E (glass line
# Y=2.33 -> wall face Y=3.50); top follows the roof surface
# (3.57 at the glass line, 4.30 at the eave), 0.08 below it:
# the warped roof deviates 0.04 m from linear at mid-span
# (roof 3.894 at Y=2.915 vs 3.935 linear), so a flush top
# would poke through by 0.04 m.
wall_varying("SM_Museum_Wall_East_Return", (31.17, 2.33), (31.17, 3.50), -0.10, 3.49, -0.10, 4.22,
             MAT_CONCRETE, COL_MUSEUM, thick=0.35)
# East tip glass gable (triangular, along the roof east edge NE(43.42,-7)->SE(39.20,3.50))
glass_strip("SM_Museum_Glass_Tip",
            [(43.42, -7, 4.5), (39.20, 3.50, 4.3)], 0.0, MAT_GLASS, COL_MUSEUM)

# ================= CAFE WING (exterior) =================
# v22: frozen quad A(-13.20,-5.60) B(-8.90,4.30) D(-16.70,17.60)
# C(-28.70,22.80), area 197.3 m2, fold C->B (valley). The v21 G3
# pentagon (X -34..-10, Y -6..6, E-W long axis, N-S valley at x=-20)
# was wrong: the frozen quad's long axis runs NNW-SSE (C-A, 32.35 m).
# Photos: tall glass at the A end AND at the B/entrance end; the SW tip
# (C) tapers low.
# v22 G3 roof (frozen quad + fold C->B, r4): the v21 G3 pentagon
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
    """v22 G3 roof surface height at plan point (x, y): barycentric in
    the facet the point falls in (fold C->B is the shared edge; the two
    facets agree on it). Used by the Gallery 3 sloped ceiling so it
    sits below the roof instead of poking through it. Points outside
    the quad fall through to the nearest facet with clamped weights."""
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
    """Plan point (x, y) at gallery coords (u, v)."""
    return (_G3_A2[0] + u * _G3_U[0] + v * _G3_V[0],
            _G3_A2[1] + u * _G3_U[1] + v * _G3_V[1])

def _g3_uv(x, y):
    """Gallery coords (u, v) of plan point (x, y) (inverse of _g3_pt)."""
    _dx, _dy = x - _G3_A2[0], y - _G3_A2[1]
    return (_dx * _G3_U[0] + _dy * _G3_U[1],
            _dx * _G3_V[0] + _dy * _G3_V[1])

# v22 G3 roof: two planar facets (A,B,C) and (B,D,C), fold C->B valley.
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
glass_strip("SM_Cafe_Glass_South", cafe_south, 0.0, MAT_GLASS, COL_CAFE)
# ================= GALLERY 3 (v15: the cafe wing IS Gallery 3) =================
# Since 2017 the former cafe wing is Gallery 3 (official leasing-page plan +
# section, measured). Gallery quad (frozen, r4): the 15.0 x 8.0 m strip at
# the quad's north end — A, B, (u=15,v=8), (u=15,v=0) — in (u,v) gallery
# coords (see _g3_pt). Private room 4.0x2.9 m + kitchen at the east end
# (u 7..13.5) under a 2.7 m flat ceiling; WCs by the entrance (u 6.5..8.5).
_MAT_GRANITE = mat_principled("MAT_Granite", (0.22, 0.22, 0.21), rough=0.35)
add_speckle(_MAT_GRANITE, scale=18.0, strength=0.22, dark=(0.14, 0.14, 0.13))
_MAT_G3_FROSTED = mat_principled("MAT_G3_Frosted", (0.95, 0.95, 0.88), rough=0.4,
                                 emission=(1.0, 0.98, 0.90), emission_strength=2.0)
_MAT_G3_COVE = mat_principled("MAT_G3_Cove", (1.0, 0.9, 0.7), rough=0.4,
                              emission=(1.0, 0.85, 0.6), emission_strength=2.0)
G3_QUAD = [(-13.20, -5.60), (-8.90, 4.30), _G3_SE_GAL, _G3_NW_END]
# Luminous frosted-glass band (east half of the north-wall slot, u 7.5..13.5;
# the window glass is the west half, set with the wall above).
box("SM_G3_FrostedSlot", (*_g3_pt(10.5, 0.0), 1.6), (6.0, 0.12, 1.2), _MAT_G3_FROSTED, COL_CAFE,
    rot=(0, 0, math.radians(118.63)))
# v22: no west diagonal wall — the gallery's SW edge is the south glass
# (u=15, SM_Cafe_Glass_South) and the SE wall (B-D edge) above.
# Private room (4.0x2.9 m, u 7..11, v 0..2.9) + kitchen (u 11..13.5).
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
    rot=(0, 0, math.radians(118.63)))
# Gallery ceiling: Section C profile (official G3 section C: ceiling
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
    return min(_z, cafe_z_at(x, y) - 0.65)  # roof construction 0.65 m
# Gallery columns (official plan: 2 square + 1 round at the south vertex).
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
bpy.ops.mesh.primitive_cylinder_add(radius=0.30, depth=_chr, location=(_g3rx, _g3ry, _chr / 2.0))
_o = bpy.context.active_object
_o.name = "SM_G3_Column_Round"
set_mat(_o, MAT_CONCRETE_BOARD); link(_o, COL_CAFE)
# Gallery ceiling grid (white gypsum) over the (u,v) strip; quads below
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
solidify(_g3_o, 0.08)
# Granite floor over the gallery quad (dark grey tiles, as photographed).
flat_poly_slab("SM_G3_Floor_Granite", G3_QUAD, 0.06, 0.06, _MAT_GRANITE, COL_CAFE)
# Flat 2.7 m ceiling over the WC strip (u 6.5..8.5, v 5..7) — the sloped
# ceiling is skipped there (see above); the roof above it is ~3.5-4.2 m,
# so 2.7 m clears everywhere.
flat_poly_slab("SM_G3_Entrance_Ceiling", [_g3_pt(6.5, 5.0), _g3_pt(8.5, 5.0), _g3_pt(8.5, 7.0), _g3_pt(6.5, 7.0)],
               2.7, 0.05, MAT_WHITE, COL_CAFE)
# Triangular folded reception desks (the triangle echoes the roof fold),
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
    _MAT_G3_COVE, COL_CAFE, rot=(0, 0, math.radians(118.63)))
# Recessed downlights just below the sloped ceiling (8, rows following
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
    set_mat(_o, MAT_BLACK); link(_o, COL_CAFE)
# Terrace paving south of the gallery glass (57 m2 in the official plan):
# from the south-glass edge (u=15) 7.0 m toward C along the strip
# (7.84 x 7.0 = 55 m2). The roof extends over it (covered terrace).
flat_poly_slab("SM_G3_Terrace", [_g3_pt(15.0, 0.0), _g3_pt(15.0, 8.0), _g3_pt(22.0, 8.0), _g3_pt(22.0, 0.0)],
               0.03, 0.06, MAT_PAVING, COL_CAFE)
# Covered walkway / exterior passage between wings (x -10..-2)
# v17 (#17): west end trimmed from x=-10.25 to -10.0 — it stuck ~0.25 m
# (up to ~0.36 m at the tip) past the G3 roof edge, floating in the air.
box("SM_Passage_Roof", (-5.875, 0, 3.4), (8.25, 3.0, 0.18), MAT_STEEL_DARK, COL_SITE)
box("SM_Passage_Post_1", (-9.5, 1.2, 1.7), (0.18, 0.18, 3.4), MAT_BLACK, COL_SITE)
box("SM_Passage_Post_2", (-9.5, -1.2, 1.7), (0.18, 0.18, 3.4), MAT_BLACK, COL_SITE)
box("SM_Passage_Post_3", (-2.5, 1.2, 1.7), (0.18, 0.18, 3.4), MAT_BLACK, COL_SITE)
box("SM_Passage_Post_4", (-2.5, -1.2, 1.7), (0.18, 0.18, 3.4), MAT_BLACK, COL_SITE)

print("=== museum + cafe exterior done ===")

# ---- helpers re-emitted from the PR-A interior (unchanged) ----
def tie_holes(name, axis, fixed, u_range, v_range, step_u=0.45, step_v=0.60, vertices=12, top_fn=None):
    """Small dark tie-hole discs on a wall face (P-con grid 450x600, #21A A2:
    a 900x1800 formwork panel = 2 cols x 3 rows = 6 holes; grid points at
    multiples of 0.45 (u) / 0.60 (v) so holes sit on the panel module).
    top_fn (PR-D): optional callable u -> wall top at that column; rows
    are clipped per column so the disc clears the top by >= 0.10 m
    (disc radius 0.035 + 0.10 clearance = 0.135). B1 calls pass no
    top_fn and behave exactly as before.
    axis 'x': face plane YZ at x=fixed; axis 'y': face plane XZ at y=fixed.
    u/v are the two in-plane coordinates. 12-vertex discs: at 70 mm dia the
    facets are invisible at any real viewing distance, and the denser grid
    (60 -> 182 discs) must not cost 22k tris (32-vert discs would)."""
    n = 0
    u = u_range[0]
    while u <= u_range[1] + 1e-6:
        _v_hi = v_range[1]
        if top_fn is not None:  # PR-D: clip rows to the sloped top
            _v_hi = min(_v_hi, top_fn(u) - 0.135)
        v = v_range[0]
        while v <= _v_hi + 1e-6:
            if axis == 'x':
                loc = (fixed, u, v); rot = (0, math.radians(90), 0)
            else:
                loc = (u, fixed, v); rot = (math.radians(90), 0, 0)
            bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=0.035, depth=0.04, location=loc, rotation=rot)
            o = bpy.context.active_object
            o.name = f"{name}_{n:02d}"
            set_mat(o, MAT_TIEHOLE); link(o, COL_INTER)
            n += 1
            v += step_v
        u += step_u
    return n

def tie_holes_angled(name, p0, direction, normal_deg, d_range, v_range, step_d=0.45, step_v=0.60, vertices=12, top_fn=None):
    """tie_holes() for a diagonal wall face (PR-D: entrance block/lintel
    at 53.13 deg + G3 west wall). p0 = a point ON the face plane (wall
    start on the face line); direction = unit (dx, dy) along the wall;
    normal_deg = azimuth (deg) of the face normal in Blender XY;
    d = distance along the wall from p0; v = height (Blender Z).
    The disc axis is the face normal: Euler (0, 90deg, normal_deg) is
    Rz(normal_deg) * Ry(90deg), which maps the cylinder axis Z to
    (cos normal_deg, sin normal_deg, 0). Same 70 mm dia / 0.04 deep
    discs, same 450x600 grid, same 0.135 top/bottom edge rule as
    tie_holes() (v_range[0] is the caller's first fitting row).
    """
    n = 0
    d = d_range[0]
    while d <= d_range[1] + 1e-6:
        _v_hi = v_range[1]
        if top_fn is not None:  # PR-D: clip rows to the sloped top
            _v_hi = min(_v_hi, top_fn(d) - 0.135)
        v = v_range[0]
        while v <= _v_hi + 1e-6:
            loc = (p0[0] + direction[0] * d, p0[1] + direction[1] * d, v)
            rot = (0, math.radians(90), math.radians(normal_deg))
            bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=0.035, depth=0.04, location=loc, rotation=rot)
            o = bpy.context.active_object
            o.name = f"{name}_{n:02d}"
            set_mat(o, MAT_TIEHOLE); link(o, COL_INTER)
            n += 1
            v += step_v
        d += step_d
    return n

def _ceiling_panel_square(name, cx, cy, z_face, rx=0.0, ry=0.0):
    box(name, (cx, cy, z_face - 0.015), (0.60, 0.60, 0.02), MAT_CEILING_PANEL, COL_INTER, rot=(rx, ry, 0))

def _ceiling_panel_round(name, cx, cy, z_face, rx=0.0, ry=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.225, depth=0.02, location=(cx, cy, z_face - 0.015), rotation=(rx, ry, 0))
    _o = bpy.context.active_object
    _o.name = name
    set_mat(_o, MAT_CEILING_PANEL); link(_o, COL_INTER)

def _sprinkler(name, cx, cy, z_face):
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.012, depth=0.06, location=(cx, cy, z_face - 0.03))
    _o = bpy.context.active_object
    _o.name = name + "_Stem"
    set_mat(_o, MAT_SPRINKLER); link(_o, COL_INTER)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=0.012, location=(cx, cy, z_face - 0.06))
    _o2 = bpy.context.active_object
    _o2.name = name
    set_mat(_o2, MAT_SPRINKLER); link(_o2, COL_INTER)

def _slope_rot(zfn, cx, cy):
    """Panel tilt matching the local ceiling slope (radians about X/Y)."""
    _dzdx = (zfn(cx + 0.3, cy) - zfn(cx - 0.3, cy)) / 0.6
    _dzdy = (zfn(cx, cy + 0.3) - zfn(cx, cy - 0.3)) / 0.6
    return (math.atan(_dzdy), -math.atan(_dzdx))

# ================= INTERIOR (museum wing) — #21B geometry rebuild =================
# Levels (D1): exhibition floor G2F=-6.3, upper platform PLAT=-6.3, G1 floor G1F=-7.20.
# Roof construction 0.65 m mid-roof (FIX [3]: eave ring thins to 0.40 —
# atrium soffit = roof_z_at - 0.40 at the FOOT perimeter, blending to
# roof_z_at - 0.65 at 2.0 m in; G2 ceiling flat -1.5).
# (Helpers flat_slab / tie_holes / _ceiling_panel_* / _sprinkler / _slope_rot are
# re-emitted above by apply_issue21B.py from the PR-A script.)
G2F = -6.3
PLAT = -6.3
G1F = -7.20
G2C = -1.5
G1C = -2.20

FOOT = [(-10, -7), (43.42, -7), (39.67, 2.33), (-6.09, 2.33)]  # v22: glass-line trapezoid

def footprint_grid_slab(name, quad, z, thick, mat, coll, skip_rect=None, skip_fn=None):
    """Ground-floor slab over a convex quad footprint, built as a 1 m grid with
    openings skipped at construction (never boolean). #21B: skip_fn(cx, cy)
    replaces the old atrium-rect skip; skip_rect kept for compatibility."""
    A, B, C, D = quad
    tri1 = (A, B, C)
    tri2 = (A, C, D)
    xs = []
    x = min(p[0] for p in quad)
    xmax = max(p[0] for p in quad)
    while x <= xmax:
        xs.append(x); x += 1.0
    if xs[-1] < xmax:
        xs.append(xmax)
    ys = []
    y = min(p[1] for p in quad)
    ymax = max(p[1] for p in quad)
    while y <= ymax:
        ys.append(y); y += 1.0
    if ys[-1] < ymax:
        ys.append(ymax)
    verts, faces = [], []
    idx = {}
    for xi, xv in enumerate(xs):
        for yi, yv in enumerate(ys):
            idx[(xi, yi)] = len(verts)
            verts.append((xv, yv, z))
    for xi in range(len(xs) - 1):
        for yi in range(len(ys) - 1):
            a = idx[(xi, yi)]; b = idx[(xi + 1, yi)]
            c = idx[(xi + 1, yi + 1)]; d = idx[(xi, yi + 1)]
            cx = (verts[a][0] + verts[b][0] + verts[c][0] + verts[d][0]) / 4.0
            cy = (verts[a][1] + verts[b][1] + verts[c][1] + verts[d][1]) / 4.0
            if not (_point_in_tri(cx, cy, tri1) or _point_in_tri(cx, cy, tri2)):
                continue
            if skip_fn is not None:
                if skip_fn(cx, cy):
                    continue
            elif skip_rect is not None:
                if skip_rect[0] <= cx <= skip_rect[1] and skip_rect[2] <= cy <= skip_rect[3]:
                    continue
            if _point_in_tri(cx, cy, COURT_TRI):
                continue
            faces.append((a, b, c, d))
    o = mesh_from_pydata(name, verts, faces, mat, coll)
    solidify(o, thick)
    return o

def _dist_to_foot_edge(_x, _y):
    """Plan distance from (_x, _y) to the FOOT trapezoid boundary."""
    _best = 1e9
    _pts = [FOOT[0], FOOT[1], FOOT[2], FOOT[3], FOOT[0]]
    for _i in range(4):
        (_ax, _ay), (_bx, _by) = _pts[_i], _pts[_i + 1]
        _dx, _dy = _bx - _ax, _by - _ay
        _L2 = _dx * _dx + _dy * _dy
        _t = 0.0 if _L2 == 0 else max(0.0, min(1.0, ((_x - _ax) * _dx + (_y - _ay) * _dy) / _L2))
        _px, _py = _ax + _t * _dx, _ay + _t * _dy
        _best = min(_best, math.hypot(_x - _px, _y - _py))
    return _best

def _atrium_soffit_z(_x, _y):
    # FIX [3] (Hark PR #23): the eave ring thins to 0.40 m (steel plate +
    # H-300 + gypsum, mid of Hark's 0.35-0.45) so the soffit meets the
    # facade glass tops; the middle keeps the 0.65 m construction Hark
    # accepted (#21 §2, 0.5-0.8). Blend over 2.0 m in from the FOOT
    # perimeter. The warm strip / sprinklers / access panel sit >=2 m
    # inside, so they stay on the 0.65 offset, unchanged.
    _d = _dist_to_foot_edge(_x, _y)
    _t = min(max(_d / 2.0, 0.0), 1.0)
    _off = 0.40 + (0.65 - 0.40) * _t
    return roof_z_at(_x, _y) - _off

def _wood_bench(_name, _x, _y):
    # #21B: bench on the B1 lobby floor (G2F), not the old -4.8.
    box(f"{_name}_Seat", (_x, _y, G2F + 0.42), (0.55, 2.0, 0.07), MAT_WOOD_LIGHT, COL_INTER)
    for _ly in (_y - 0.85, _y + 0.85):
        box(f"{_name}_Leg_{_ly}", (_x, _ly, G2F + 0.20), (0.5, 0.06, 0.40), MAT_WOOD_LIGHT, COL_INTER)

# Interior-local materials (re-defined here; the section is replaced wholesale).
MAT_SKYLIGHT = mat_principled("MAT_Skylight", (1.0, 1.0, 0.95), rough=0.4,
                              emission=(1, 1, 0.9), emission_strength=2.5)
MAT_DARK_DOOR = mat_principled("MAT_Dark_Door", (0.02, 0.02, 0.02), metallic=0.0, rough=0.95)
MAT_WOOD_SHELF = mat_principled("MAT_Wood_Shelf", (0.45, 0.32, 0.20), rough=0.7)
add_wood_grain(MAT_WOOD_SHELF)
MAT_WOOD_LIGHT = mat_principled("MAT_Wood_Light", (0.72, 0.58, 0.40), rough=0.6)
add_wood_grain(MAT_WOOD_LIGHT)
MAT_LEATHER = mat_principled("MAT_Black_Leather", (0.05, 0.05, 0.05), rough=0.85)
MAT_WARM_STRIP = mat_principled("MAT_Warm_Strip", (1.0, 0.85, 0.6), rough=0.4,
                                emission=(1.0, 0.75, 0.45), emission_strength=2.0)
MAT_SLIT = mat_principled("MAT_Slit_Light", (1.0, 0.96, 0.88), rough=0.4,
                          emission=(1.0, 0.95, 0.85), emission_strength=2.5)
_book_cols = [(0.60, 0.10, 0.10), (0.10, 0.30, 0.60), (0.90, 0.70, 0.10),
              (0.20, 0.50, 0.20), (0.80, 0.40, 0.10), (0.88, 0.88, 0.85)]
MAT_BOOKS = [mat_principled(f"MAT_Book_{i}", c, rough=0.8) for i, c in enumerate(_book_cols)]
MAT_FLOOR_CONCRETE = mat_principled("MAT_Floor_Concrete", (0.72, 0.71, 0.69), rough=0.85)

# ---- B1 floors ----
# B1 outline (model): (-10,-7),(29.44,-7),(29.44,-8.56),(48.56,-8.56),(48.56,17.24),
# (5.35,17.24),(1.56,20.98). Area 1337.9 m2. Tiled with exact convex pieces
# (flat_poly_slab is fan-triangulated, convex only) — no grid teeth around
# the G1 pit or the platform. G1 quad: (7.21,13.77),(2.43,2.21),(15.08,-0.46),(15.08,12.04).
# Platform block (north band, X -1..29.44, Y -7..-3.29): in v22 a flush
# sub-floor fill, top -6.3 (one level with the lobby), 0.9 m down to G1F.
G1_POLY = [(7.21, 13.77), (2.43, 2.21), (15.08, -0.46), (15.08, 12.04)]
_B1_FLOORS = [
    ("SM_Basement_Floor_N1", [(0.015, -3.29), (48.56, -3.29), (48.56, -0.46), (0.015, -0.46)]),
    ("SM_Basement_Floor_N2", [(29.44, -7), (48.56, -7), (48.56, -3.29), (29.44, -3.29)]),
    ("SM_Basement_Floor_E1", [(15.08, -0.46), (48.56, -0.46), (48.56, 17.24), (15.08, 17.24)]),
    ("SM_Basement_Floor_W1", [(0.015, -0.46), (2.43, -0.46), (2.43, 17.24), (0.015, 17.24)]),
    ("SM_Basement_Floor_M1", [(2.43, -0.46), (15.08, -0.46), (2.43, 2.21)]),
    ("SM_Basement_Floor_M2", [(2.43, 2.21), (7.21, 13.77), (2.43, 13.77)]),
    ("SM_Basement_Floor_M3", [(7.21, 13.77), (15.08, 12.04), (15.08, 17.24), (7.21, 17.24)]),
    ("SM_Basement_Floor_M4", [(2.43, 13.77), (7.21, 13.77), (7.21, 17.24), (2.43, 17.24)]),
    ("SM_Basement_Floor_Q2S", [(-8.47, -3.29), (0.015, -3.29), (0.015, 17.24)]),
    ("SM_Basement_Floor_Q2N", [(-10, -7), (-1, -7), (-1, -3.29), (-8.47, -3.29)]),
    ("SM_Basement_Floor_Q3", [(0.015, 17.24), (5.35, 17.24), (1.56, 20.98)]),
    ("SM_Basement_Floor_Q4", [(29.44, -8.56), (48.56, -8.56), (48.56, -7), (29.44, -7)]),
]
for _fn, _fp in _B1_FLOORS:
    flat_poly_slab(_fn, _fp, G2F, 0.2, MAT_FLOOR_CONCRETE, COL_INTER)
# G1 floor (0.45 below G2 = 3 steps x 0.15, within the 0.2-0.75 range).
flat_poly_slab("SM_G1_Floor", G1_POLY, G1F, 0.2, MAT_FLOOR_CONCRETE, COL_INTER)
# Upper platform: top -6.3 in v22 (one level with the lobby); the 0.9 m
# thickness runs -7.2..-6.3. North strip + landing follow the longer flight.
flat_poly_slab("SM_Platform_West", [(-1, -7), (15.63, -7), (15.63, -3.29), (-1, -3.29)],
               PLAT, 0.9, MAT_FLOOR_CONCRETE, COL_INTER)
flat_poly_slab("SM_Platform_NorthStrip", [(15.63, -7), (28.23, -7), (28.23, -6.16), (15.63, -6.16)],
               PLAT, 0.9, MAT_FLOOR_CONCRETE, COL_INTER)
# Landing extended south to Y=-3.29: it closes the arrival-floor hole
# east of the flight (X 28.23..29.44, Y -5.39..-3.29). Safe vs the
# balustrade, which ends at X=28.23 (the slab starts exactly there).
flat_poly_slab("SM_Platform_Landing", [(28.23, -6.16), (29.44, -6.16), (29.44, -3.29), (28.23, -3.29)],
               PLAT, 0.9, MAT_FLOOR_CONCRETE, COL_INTER)

# Ground-floor slab over the museum footprint (top z=0.02; court + void + stair
# skipped at construction) + cafe slab (same construction).
ground_slab = footprint_grid_slab("SM_Ground_Slab", FOOT, 0.02, 0.3, MAT_CONCRETE, COL_INTER,
                                  skip_fn=_in_void)
CAFE_FOOT = [(-13.20, -5.60), (-8.90, 4.30), (-16.70, 17.60), (-28.70, 22.80)]
cafe_slab = footprint_grid_slab("SM_Cafe_Slab", CAFE_FOOT, 0.02, 0.3, MAT_CONCRETE, COL_INTER)

# ---- B1 perimeter walls (Z -6.3..-0.10, tops below lawn -0.05) ----
# North wall is built in the museum-wing section (with the long window).
wall_varying("SM_Basement_Wall_South", (48.56, 17.24), (5.35, 17.24), -6.3, -0.10, -6.3, -0.10,
             MAT_WHITE, COL_INTER, thick=0.35)
wall_varying("SM_Basement_Wall_SW", (5.35, 17.24), (1.56, 20.98), -6.3, -0.10, -6.3, -0.10,
             MAT_WHITE, COL_INTER, thick=0.35)
wall_varying("SM_Basement_Wall_West", (1.56, 20.98), (-10, -7), -6.3, -0.10, -6.3, -0.10,
             MAT_CONCRETE, COL_INTER, thick=0.35)
wall_varying("SM_Basement_Wall_East", (48.56, -8.56), (48.56, 17.24), -6.3, -0.10, -6.3, -0.10,
             MAT_WHITE, COL_INTER, thick=0.35)

# ---- G2 north thick wall (solid concrete, X 18.03..41.87, Y 2.33..3.25, Z -6.3..-0.10) ----
# Box stops at X=39.5: the doorway gap X 39.5..41.87 = G2 exit to the Z corridor.
# Top at -0.10 (below the lawn plane at 0, so no Z-fight with the site ground).
box("SM_G2_ThickWall", (28.77, 2.79, -3.2), (21.47, 0.92, 6.2), MAT_CONCRETE_BOARD, COL_INTER)
# Tie-hole grid on the thick wall's north (court) face (P-con 450x600).
tie_holes("SM_ThickWall_TieHole", 'y', 2.33, (18.5, 39.5), (-5.75, -2.15))  # D-fix: was (18.5, 41.5); wall stops at X=39.5, 35 discs floated in the doorway gap
# Tie-hole grid on the basement north wall face (Y=-6.83), above the stair.
tie_holes("SM_NorthWall_TieHole", 'y', -6.83, (16.2, 26.55), (-3.75, -0.75))  # 24 cols x 6 rows = 144 (top row dropped: -0.15 would sit 0.05 below the -0.10 wall top)
# PR-C [Jog]: tie-hole grids on both faces of the new ground-floor
# Jog wall (P-con 450x600, 3 cols x 9 rows per face, 54 total).
# PR-D [Jog]: bottom row 0.0 -> 0.3, top row 4.8 -> 4.5 (grid shifts
# up 0.3, 8 rows per face, 48 total; Hark PR-C review: the 0.0 row
# crossed the ground plane; 600 module kept, 0.3-phase shared with
# all other above-ground walls).
tie_holes("SM_JogWall_TieHole_W", 'x', 29.26, (-8.23, -7.33), (0.3, 4.5), top_fn=lambda y: 4.59)
tie_holes("SM_JogWall_TieHole_E", 'x', 29.62, (-8.23, -7.33), (0.3, 4.5), top_fn=lambda y: 4.59)
# PR-D [Holes]: P-con grids on all other above-ground exposed
# concrete walls (450x600, both faces; v rows on the global
# 0.3+0.6k grid, u cols on global 0.45 multiples, 0.135 edge
# clearance; sloped tops clip per column via top_fn).
# Museum north wall above the long window (0.45..4.95).
print("v22 holes North_Above N:", tie_holes("SM_NorthAbove_TieHole_N", 'y', -7.175, (-9.45, 29.25), (0.9, 4.5), top_fn=roof_z_north))
print("v22 holes North_Above S:", tie_holes("SM_NorthAbove_TieHole_S", 'y', -6.825, (-9.45, 29.25), (0.9, 4.5), top_fn=roof_z_north))
# Museum north-east wall, flat section (0.45..4.95).
print("v22 holes NorthEast_A N:", tie_holes("SM_NorthEastA_TieHole_N", 'y', -8.735, (29.70, 40.50), (0.9, 4.5), top_fn=roof_z_north))
print("v22 holes NorthEast_A S:", tie_holes("SM_NorthEastA_TieHole_S", 'y', -8.385, (29.70, 40.50), (0.9, 4.5), top_fn=roof_z_north))
# Museum north-east wall, sloped-top section (top 4.95 -> 2.5).
print("v22 holes NorthEast_B N:", tie_holes("SM_NorthEastB_TieHole_N", 'y', -8.735, (41.40, 43.20), (0.9, 4.5), top_fn=roof_z_north))
print("v22 holes NorthEast_B S:", tie_holes("SM_NorthEastB_TieHole_S", 'y', -8.385, (41.40, 43.20), (0.9, 4.5), top_fn=roof_z_north))
# Slot infills beside/between the long-window panes (0..0.45: one row at 0.3).
print("PR-D holes North_Slot_W N:", tie_holes("SM_NorthSlotW_TieHole_N", 'y', -7.175, (-9.45, 15.30), (0.3, 0.3)))
print("PR-D holes North_Slot_W S:", tie_holes("SM_NorthSlotW_TieHole_S", 'y', -6.825, (-9.45, 15.30), (0.3, 0.3)))
print("PR-D holes North_Slot_Mid N:", tie_holes("SM_NorthSlotMid_TieHole_N", 'y', -7.175, (27.45, 29.25), (0.3, 0.3)))
print("PR-D holes North_Slot_Mid S:", tie_holes("SM_NorthSlotMid_TieHole_S", 'y', -6.825, (27.45, 29.25), (0.3, 0.3)))
print("PR-D holes NorthEast_Slot_E N:", tie_holes("SM_NorthEastSlotE_TieHole_N", 'y', -8.735, (41.40, 48.15), (0.3, 0.3)))
print("PR-D holes NorthEast_Slot_E S:", tie_holes("SM_NorthEastSlotE_TieHole_S", 'y', -8.385, (41.40, 48.15), (0.3, 0.3)))
# Stair parapet, south (stair-side) face only: above GL only where
# the 1:2 top clears 0.435 (X 16.20/16.65 at row 0.3); the north face
# sits in the 0.6 m slot behind the parapet and is not visible.
print("PR-D holes Stair_Parapet S:", tie_holes("SM_StairParapet_TieHole_S", 'y', -5.80, (16.20, 16.65), (0.3, 0.3), top_fn=lambda x: 1.0 - 0.5 * (x - 15.63)))
# Cafe/G3 north wall: low band (0..1.0: one row at 0.3).
# (G3 north wall: direction U=(-0.4791,0.8779) from A; interior
# normal V=(0.8779,0.4791) az 28.62, exterior -V az -151.38;
# face-line starts A-/+V*0.15.)
print("v22 holes Cafe_North_Low out:", tie_holes_angled("SM_CafeNorthLow_TieHole_Out", (-13.3317, -5.6719), (-0.4791, 0.8779), -151.38, (0.45, 14.40), (0.3, 0.3)))
print("v22 holes Cafe_North_Low in:", tie_holes_angled("SM_CafeNorthLow_TieHole_In", (-13.0683, -5.5281), (-0.4791, 0.8779), 28.62, (0.45, 14.40), (0.3, 0.3)))
# Cafe/G3 north wall: high band west (2.2..roof, top 4.91 -> 2.946).
print("v22 holes Cafe_North_High out:", tie_holes_angled("SM_CafeNorthHigh_TieHole_Out", (-13.3317, -5.6719), (-0.4791, 0.8779), -151.38, (0.45, 14.40), (2.7, 4.5), top_fn=lambda d: 4.90 - 0.08964 * d))
print("v22 holes Cafe_North_High in:", tie_holes_angled("SM_CafeNorthHigh_TieHole_In", (-13.0683, -5.5281), (-0.4791, 0.8779), 28.62, (0.45, 14.40), (2.7, 4.5), top_fn=lambda d: 4.90 - 0.08964 * d))
# Cafe/G3 north wall: high band east (2.2..roof, top 2.946 -> 4.124).
# (High_E folded into the single High band above: the v22 north wall
    # is one 15 m wall with a single straight roof line 4.90 -> 3.56.)
# Cafe/G3 north wall: slot bands (1.0..2.2: one row at 1.5).
print("v22 holes Cafe_North_SlotW out:", tie_holes_angled("SM_CafeNorthSlotW_TieHole_Out", (-13.3317, -5.6719), (-0.4791, 0.8779), -151.38, (0.45, 1.35), (1.5, 1.5)))
print("v22 holes Cafe_North_SlotW in:", tie_holes_angled("SM_CafeNorthSlotW_TieHole_In", (-13.0683, -5.5281), (-0.4791, 0.8779), 28.62, (0.45, 1.35), (1.5, 1.5)))
print("v22 holes Cafe_North_SlotE out:", tie_holes_angled("SM_CafeNorthSlotE_TieHole_Out", (-13.3317, -5.6719), (-0.4791, 0.8779), -151.38, (13.95, 14.40), (1.5, 1.5)))
print("v22 holes Cafe_North_SlotE in:", tie_holes_angled("SM_CafeNorthSlotE_TieHole_In", (-13.0683, -5.5281), (-0.4791, 0.8779), 28.62, (13.95, 14.40), (1.5, 1.5)))
# Cafe west wall (X=-34, 0..roof, top 4.91 -> 3.437; u is Blender Y).
# Cafe_West deleted with its wall (chunk 3: no west wall in the
    # frozen quad; the gallery SW edge is south glass + SE wall).
# Entrance block + lintel (diagonal, 53.13 deg; s = distance from the
# doorway centre _ENT_C along the wall; face lines are the centreline
# offset by +/-0.6 m (half of the 1.2 m thickness) along the normal
# (-0.8, 0.6) exterior / (0.8, -0.6) interior; azimuths 143.13 / -36.87).
_ent_n_out = (-10.55519, -6.77168); _ent_n_in = (-9.44819, -7.23560)
_ent_s_out = (-7.73494, -0.04204); _ent_s_in = (-6.62794, -0.50596)
_ent_l_out = (-8.97206, -2.99404); _ent_l_in = (-7.86506, -3.45796)
_ent_dir = (0.3866, 0.9225)
print("v22 holes Entrance_N out:", tie_holes_angled("SM_EntranceN_TieHole_Out", _ent_n_out, _ent_dir, 157.35, (0.20, 3.90), (0.3, 4.5)))
print("v22 holes Entrance_N in:", tie_holes_angled("SM_EntranceN_TieHole_In", _ent_n_in, _ent_dir, -22.65, (0.20, 3.90), (0.3, 4.5)))
print("v22 holes Entrance_S out:", tie_holes_angled("SM_EntranceS_TieHole_Out", _ent_s_out, _ent_dir, 157.35, (0.20, 3.90), (0.3, 4.5)))
print("v22 holes Entrance_S in:", tie_holes_angled("SM_EntranceS_TieHole_In", _ent_s_in, _ent_dir, -22.65, (0.20, 3.90), (0.3, 4.5)))
print("v22 holes Entrance_Lintel out:", tie_holes_angled("SM_EntranceLintel_TieHole_Out", _ent_l_out, _ent_dir, 157.35, (0.25, 2.95), (3.3, 3.3)))
print("v22 holes Entrance_Lintel in:", tie_holes_angled("SM_EntranceLintel_TieHole_In", _ent_l_in, _ent_dir, -22.65, (0.25, 2.95), (3.3, 3.3)))
# G3 west diagonal wall (from (-33,-5.7) to (-25,3.6), thick 0.30;
# direction (8, 9.3)/12.268; exterior normal (-uy, ux), interior (uy, -ux);
# face lines offset by +/-0.15 m; d from the wall start; top 4.7 -> 1.8).
_g3dx, _g3dy = 8.0, 9.3
_g3len = math.hypot(_g3dx, _g3dy)
_g3ux, _g3uy = _g3dx / _g3len, _g3dy / _g3len
_g3nx, _g3ny = -_g3uy, _g3ux
_g3az_out = math.degrees(math.atan2(_g3ny, _g3nx))
_g3az_in = math.degrees(math.atan2(-_g3ny, -_g3nx))
_g3p_out = (-33 + _g3nx * 0.15, -5.7 + _g3ny * 0.15)
_g3p_in = (-33 - _g3nx * 0.15, -5.7 - _g3ny * 0.15)
# G3_West holes deleted with their wall (chunk 3: no west wall).

# ---- G2 ceiling (flat white gypsum, -1.5; net height 4.8) + skylight + fluorescents ----
box("SM_G2_Ceiling_N", (31.82, 4.225, -1.5), (33.48, 1.95, 0.06), MAT_CEILING_GYPSUM, COL_INTER)
box("SM_G2_Ceiling_S", (31.82, 11.57, -1.5), (33.48, 11.34, 0.06), MAT_CEILING_GYPSUM, COL_INTER)
# Skylight slot (emissive) in the 0.70 m gap (Y 5.2..5.9), recessed at z=-1.67.
box("SM_G2_Skylight_Slot", (31.82, 5.55, -1.22), (33.48, 0.70, 0.10), MAT_SKYLIGHT, COL_INTER)
# Linear fluorescents (4 rows, just below the ceiling).
for _ri, _ry in enumerate([6.5, 9.5, 12.5, 15.5]):
    box(f"SM_G2_Fluorescent_{_ri}", (32, _ry, -1.57), (30.0, 0.12, 0.06), MAT_SKYLIGHT, COL_INTER)
# East door (dark opening, far east wall).
box("SM_G2_East_Door", (48.4, 5.0, -5.1), (0.3, 1.2, 2.4), MAT_DARK_DOOR, COL_INTER)

# ---- G2 columns (one row of 6, Y=5.55, 0.55 sq, height 4.8) + tie holes ----
for i, cx in enumerate([19.09, 23.25, 27.39, 31.52, 35.68, 39.84]):
    box(f"SM_G2_Column_{i}", (cx, 5.55, -3.9), (0.55, 0.55, 4.8), MAT_CONCRETE_BOARD, COL_INTER)
    tie_holes(f"SM_G2_Column_TieHole_{i}", 'y', 5.83, (cx, cx), (-5.75, -2.15))

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

# ---- G1 walls (white, Z -7.20..-2.20) ----
# West wall (A-B edge) with a doorway gap at Y 3.45..5.55 (3 steps down from lobby).
wall_varying("SM_G1_Wall_West_A", (2.43, 2.21), (2.94, 3.45), -7.20, -2.20, -7.20, -2.20,
             MAT_WHITE, COL_INTER, thick=0.2)
wall_varying("SM_G1_Wall_West_B", (3.81, 5.55), (7.21, 13.77), -7.20, -2.20, -7.20, -2.20,
             MAT_WHITE, COL_INTER, thick=0.2)
# Diagonal (north) wall B-C with the 1800x1800 square window (centre Z -4.5, t=0.25).
# Below-window band + above-window band (full length) + side pieces at window height.
wall_varying("SM_G1_Wall_Diag_Below", (2.43, 2.21), (15.08, -0.46), -7.20, -5.40, -7.20, -5.40,
             MAT_WHITE, COL_INTER, thick=0.2)
wall_varying("SM_G1_Wall_Diag_Above", (2.43, 2.21), (15.08, -0.46), -3.60, -2.20, -3.60, -2.20,
             MAT_WHITE, COL_INTER, thick=0.2)
_G1D = (0.978, -0.207)  # B->C direction (unit)
_G1N = (0.207, 0.978)   # inward normal (into G1)
def _g1_wall_pt(t):
    return (2.43 + 12.65 * t, 2.21 - 2.67 * t)
_w0 = _g1_wall_pt(0.0); _w1 = _g1_wall_pt(0.18); _w2 = _g1_wall_pt(0.32); _w3 = _g1_wall_pt(1.0)
wall_varying("SM_G1_Wall_Diag_Side_W", _w0, _w1, -5.40, -3.60, -5.40, -3.60,
             MAT_WHITE, COL_INTER, thick=0.2)
wall_varying("SM_G1_Wall_Diag_Side_E", _w2, _w3, -5.40, -3.60, -5.40, -3.60,
             MAT_WHITE, COL_INTER, thick=0.2)
# Square window glass in the opening (1.8 x 1.8, centre t=0.25, Z -4.5).
_wc = _g1_wall_pt(0.25)
box("SM_G1_SquareWindow_Glass", (_wc[0], _wc[1], -4.5), (1.8, 0.06, 1.8), MAT_GLASS, COL_INTER,
    rot=(0, 0, math.radians(-11.9)))
# East wall (X=15.08) with the G1->G2 doorway gap at Y 5..8 (noren, exhibit 09).
wall_varying("SM_G1_Wall_East_A", (15.08, -0.46), (15.08, 5.0), -7.20, -2.20, -7.20, -2.20,
             MAT_WHITE, COL_INTER, thick=0.2)
wall_varying("SM_G1_Wall_East_B", (15.08, 8.0), (15.08, 12.04), -7.20, -2.20, -7.20, -2.20,
             MAT_WHITE, COL_INTER, thick=0.2)
# South wall (D-A edge).
wall_varying("SM_G1_Wall_South", (15.08, 12.04), (7.21, 13.77), -7.20, -2.20, -7.20, -2.20,
             MAT_WHITE, COL_INTER, thick=0.2)
# G1 ceiling: flat white at -2.2; far edge offset 0.8 m inward from the B-C wall
# so the skylight band stays open. (C' clamped to X=15.08 so the ceiling does
# not overhang the east wall.)
flat_poly_slab("SM_G1_Ceiling", [(7.21, 13.77), (2.60, 2.99), (15.08, 0.32), (15.08, 12.04)],
               -2.20, 0.05, MAT_CEILING_GYPSUM, COL_INTER)
# G1 skylight: 6 emissive panels leaning from the wall top (-2.2) up-inward to -1.1.
# Panels 1.4 m long along the wall, 1.52 m apart (no overlap / Z-fight).
for _pi, _t in enumerate([0.08, 0.20, 0.32, 0.44, 0.56, 0.68]):
    _cx, _cy = _g1_wall_pt(_t)
    _b1 = (_cx - 0.7 * _G1D[0], _cy - 0.7 * _G1D[1], -2.2)
    _b2 = (_cx + 0.7 * _G1D[0], _cy + 0.7 * _G1D[1], -2.2)
    _t2 = (_b2[0] + 0.7 * _G1N[0], _b2[1] + 0.7 * _G1N[1], -1.1)
    _t1 = (_b1[0] + 0.7 * _G1N[0], _b1[1] + 0.7 * _G1N[1], -1.1)
    mesh_from_pydata(f"SM_G1_Skylight_{_pi}", [_b1, _b2, _t2, _t1],
                     [(0, 3, 2, 1)], MAT_SKYLIGHT, COL_INTER)
# G1 linear fluorescents (2 rows, just below the ceiling).
for _fi, _fy in enumerate([4.0, 8.0]):
    box(f"SM_G1_Fluorescent_{_fi}", (9, _fy, -2.28), (10.0, 0.12, 0.06), MAT_SKYLIGHT, COL_INTER)
# G1 side walls: dark vertical slat panel (south wall, upper) + white door (west wall).
# Both offset 0.13 m inward from the wall centreline so they sit proud of the
# 0.2-thick wall's inner face instead of being buried in it.
_MAT_G1_SLAT = mat_principled("MAT_G1_Slat", (0.12, 0.12, 0.12), rough=0.9)
box("SM_G1_Slat_South", (11.12, 12.77, -2.8), (8.0, 0.06, 1.2), _MAT_G1_SLAT, COL_INTER,
    rot=(0, 0, math.radians(167.6)))
box("SM_G1_Door_West", (5.63, 9.61, -6.15), (0.9, 0.06, 2.1), MAT_WHITE, COL_INTER,
    rot=(0, 0, math.radians(67.5)))

# ---- Sunken court (triangle (18.72,2.33),(39.39,-6.33),(35.8,2.33), area 74 m2) ----
# South edge is the G2 thick wall. Diagonal glass wall A-B (tall, to the roof)
# with a 1.2 m doorway gap near the west end; east glass wall B-C.
# Mullions: solid steel 235x69 mm, dense (~0.8 m), from the pit floor (-6.3)
# to the roof plate underside (roof_z_at - 0.02); tallest ~11.68 m at B (#17).
_COURT_A = (18.72, 2.33); _COURT_B = (39.39, -6.33); _COURT_C = (35.8, 2.33)
def _court_roof_z(x, y):
    return roof_z_at(x, y) - 0.02
# Diagonal glass: two segments around the doorway gap (2.5..3.7 m from A along A-B).
_diag_d = (0.922, -0.387)
_gap0 = (_COURT_A[0] + 2.5 * _diag_d[0], _COURT_A[1] + 2.5 * _diag_d[1])
_gap1 = (_COURT_A[0] + 3.7 * _diag_d[0], _COURT_A[1] + 3.7 * _diag_d[1])
wall_varying("SM_Court_Glass_Diag_A", _COURT_A, _gap0, -6.3, _court_roof_z(*_COURT_A),
             -6.3, _court_roof_z(*_gap0), MAT_GLASS, COL_INTER, thick=0.12)
wall_varying("SM_Court_Glass_Diag_B", _gap1, _COURT_B, -6.3, _court_roof_z(*_gap1),
             -6.3, _court_roof_z(*_COURT_B), MAT_GLASS, COL_INTER, thick=0.12)
wall_varying("SM_Court_Glass_East", _COURT_B, _COURT_C, -6.3, _court_roof_z(*_COURT_B),
             -6.3, _court_roof_z(*_COURT_C), MAT_GLASS, COL_INTER, thick=0.12)
# Steel mullions along the diagonal (skip the doorway gap) and the east edge.
# Corner posts at A, B and C so the tallest mullion is exactly at B (11.68 m).
_diag_len = 22.41
_diag_ang = math.radians(-22.76)
_mi = 0
_s = 0.4
while _s < _diag_len:
    if not (2.5 <= _s <= 3.7):
        _mx = _COURT_A[0] + _s * _diag_d[0]
        _my = _COURT_A[1] + _s * _diag_d[1]
        _top = _court_roof_z(_mx, _my)
        box(f"SM_Court_Mullion_D{_mi:02d}", (_mx, _my, (G2F + _top) / 2),
            (0.069, 0.235, _top - G2F), MAT_BLACK, COL_INTER, rot=(0, 0, _diag_ang))
        _mi += 1
    _s += 0.8
for _cs, _cang in [(0.0, _diag_ang), (_diag_len, _diag_ang)]:
    _mx = _COURT_A[0] + _cs * _diag_d[0]
    _my = _COURT_A[1] + _cs * _diag_d[1]
    _top = _court_roof_z(_mx, _my)
    box(f"SM_Court_Mullion_D{_mi:02d}", (_mx, _my, (G2F + _top) / 2),
        (0.069, 0.235, _top - G2F), MAT_BLACK, COL_INTER, rot=(0, 0, _cang))
    _mi += 1
_east_d = (-0.383, 0.924)  # B->C direction (unit), length 9.38
_east_ang = math.radians(112.4)
_s = 0.4
while _s < 9.38:
    _mx = _COURT_B[0] + _s * _east_d[0]
    _my = _COURT_B[1] + _s * _east_d[1]
    _top = _court_roof_z(_mx, _my)
    box(f"SM_Court_Mullion_E{_mi:02d}", (_mx, _my, (G2F + _top) / 2),
        (0.069, 0.235, _top - G2F), MAT_BLACK, COL_INTER, rot=(0, 0, _east_ang))
    _mi += 1
    _s += 0.8
# Corner post at C (east edge end).
_mx = _COURT_C[0]; _my = _COURT_C[1]
_top = _court_roof_z(_mx, _my)
box(f"SM_Court_Mullion_E{_mi:02d}", (_mx, _my, (G2F + _top) / 2),
    (0.069, 0.235, _top - G2F), MAT_BLACK, COL_INTER, rot=(0, 0, _east_ang))
_mi += 1
# Court floor planting + tree on the pit floor (centroid (31.3,-0.56)).
box("SM_Court_Planter", (31.3, -0.56, -6.2), (6.0, 3.5, 0.2), MAT_GRASS, COL_INTER)
cedar(31.3, -0.56, h=3.8, r=0.9, z0=-6.3)

# ---- Main stair (D2): 42 steps, riser 0.15 / tread 0.30, west->east GL 0 -> -6.3 ----
# Flight X 15.63..28.23, 1.9 m wide (Y -5.8..-3.9); north concrete wall + steel
# handrail, south glass balustrade (heights differ: parapet 1.0 / bar top 1.05,
# balustrade 1.1 — PR-C: bar seated, was floating 0.06 with top at 1.12).
# v22: the flight lands on the lobby/platform (both BFL1 -6.3); 6.30 / 0.15 = 42.
NSTEPS = 42
_STAIR_X0, _STAIR_TREAD, _STAIR_RISER = 15.63, 0.30, 0.15
for i in range(NSTEPS):
    sx = _STAIR_X0 + i * _STAIR_TREAD + _STAIR_TREAD / 2.0
    sz = -i * _STAIR_RISER - _STAIR_RISER / 2.0
    box(f"SM_Stair_Step_{i:02d}", (sx, -4.85, sz), (_STAIR_TREAD, 1.9, _STAIR_RISER), MAT_CONCRETE_BOARD, COL_INTER)
# Sloped soffit slab under the steps (top flush with the step blocks' undersides:
# nosing line - 0.15, centre 0.075 below that, 0.15 thick).
_soff_len = math.hypot(NSTEPS * _STAIR_TREAD, NSTEPS * _STAIR_RISER)
_soff_ang = math.atan2(NSTEPS * _STAIR_RISER, NSTEPS * _STAIR_TREAD)
box("SM_Stair_Soffit", (_STAIR_X0 + NSTEPS * _STAIR_TREAD / 2.0, -4.85, -3.375),
    (_soff_len, 1.9, 0.15), MAT_CONCRETE_BOARD, COL_INTER, rot=(0, _soff_ang, 0))
# North concrete wall (parapet, top = nosing line + 1.0 m) + steel handrail on top
# (PR-C: bar seated — centre = parapet top -1.925 + 0.028 vertical half-thickness).
# Full height down to the B1 floor (-6.3); 0.4 thick so it embeds into the
# platform's north strip edge (no floating bottom over the stair well).
wall_varying("SM_Stair_Wall_North", (15.63, -6.0), (28.23, -6.0), -6.3, 1.0, -6.3, -5.30,
             MAT_CONCRETE_BOARD, COL_INTER, thick=0.4)
box("SM_Stair_Handrail", (21.93, -6.0, -2.122),  # PR-C [Rail]: seated on the parapet (was -1.83, floating 0.06)
    (_soff_len, 0.05, 0.05), MAT_BLACK, COL_INTER, rot=(0, _soff_ang, 0))
# South glass balustrade (top 1.1 m above the nosings, bottom 0.3 below).
wall_varying("SM_Stair_Balustrade", (15.63, -3.9), (28.23, -3.9), -0.3, 1.1, -6.6, -5.2,
             MAT_GLASS, COL_INTER, thick=0.08)
# Wide steps DELETED in v22: they descended the platform (-5.85) to the
# lobby (-6.75); in v22 both are BFL1 -6.3 (one level, per Detail 4 p96),
# so their blocks (PLAT..G2F) have zero height. They were an artefact of
# the old -5.85/-6.75 split, which the p96 section does not support.
# G1 steps: 6 steps from the lobby (-6.3) down into G1 (-7.20),
# X 2.0..3.8, Y 3.45..5.55, descending eastward. Solid blocks to the G1 floor.
for _gi in range(6):
    _gz = G2F - _gi * 0.15
    box(f"SM_G1Step_{_gi}", (2.0 + (_gi + 0.5) * 0.30, 4.5, (_gz + G1F) / 2),
        (0.30, 2.10, _gz - G1F), MAT_CONCRETE_BOARD, COL_INTER)

# ---- Trapezoidal elevator shaft (Japan's only trapezoidal elevator) ----
# Plan (model): (-0.72,-3.68),(-1.51,-5.46),(-0.1,-5.79),(0.4,-4.6) — the platform's
# NW corner. Concrete shaft Z -6.75..2.4 (a lift core in the ground lobby);
# dark steel doors on the east face at platform level and ground level; car inside.
_ELEV_PLAN = [(-0.72, -3.68), (-1.51, -5.46), (-0.1, -5.79), (0.4, -4.6)]
_elev_v = [(x, y, -6.3) for (x, y) in _ELEV_PLAN] + [(x, y, 2.4) for (x, y) in _ELEV_PLAN]
# Winding outward (plan is CCW in XY): bottom reversed, sides bottom->bottom->top->top.
_elev_f = [(3, 2, 1, 0), (7, 6, 5, 4), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
mesh_from_pydata("SM_Elevator_Shaft", _elev_v, _elev_f, MAT_CONCRETE, COL_INTER)
# East face: edge P2(-0.1,-5.79)->P3(0.4,-4.6), midpoint (0.15,-5.2), direction 67.3 deg;
# doors sit 0.05 proud of the face, wide along it.
box("SM_Elevator_Door", (0.20, -5.22, 1.2), (1.2, 0.08, 2.4), MAT_STEEL_DARK, COL_INTER,
    rot=(0, 0, math.radians(67.3)))
box("SM_Elevator_Door_Basement", (0.20, -5.22, -5.10), (1.2, 0.08, 2.4), MAT_STEEL_DARK, COL_INTER,
    rot=(0, 0, math.radians(67.3)))
box("SM_Elevator_Car", (0.0, -4.7, -5.15), (1.2, 1.0, 2.2), MAT_STEEL_DARK, COL_INTER)

# ---- BOH (south-west back of house: office + storage), walls Z -6.3..-0.10 ----
# Polygon (model): (-0.84,14.99),(-4.11,7.16),(0.23,5.43),(2.38,10.63),(3.3,10.21),(3.44,13.23).
# Doorway gap (1.0 m) in the north edge (P1->P2).
_BOH = [(-0.84, 14.99), (-4.11, 7.16), (0.23, 5.43), (2.38, 10.63), (3.3, 10.21), (3.44, 13.23)]
wall_varying("SM_BOH_Wall_0", _BOH[5], _BOH[0], -6.3, -0.10, -6.3, -0.10,
             MAT_WHITE, COL_INTER, thick=0.2)
wall_varying("SM_BOH_Wall_1a", _BOH[1], (-2.44, 6.49), -6.3, -0.10, -6.3, -0.10,
             MAT_WHITE, COL_INTER, thick=0.2)
wall_varying("SM_BOH_Wall_1b", (-1.51, 6.12), _BOH[2], -6.3, -0.10, -6.3, -0.10,
             MAT_WHITE, COL_INTER, thick=0.2)
wall_varying("SM_BOH_Wall_2", _BOH[2], _BOH[3], -6.3, -0.10, -6.3, -0.10,
             MAT_WHITE, COL_INTER, thick=0.2)
wall_varying("SM_BOH_Wall_3", _BOH[3], _BOH[4], -6.3, -0.10, -6.3, -0.10,
             MAT_WHITE, COL_INTER, thick=0.2)
wall_varying("SM_BOH_Wall_4", _BOH[4], _BOH[5], -6.3, -0.10, -6.3, -0.10,
             MAT_WHITE, COL_INTER, thick=0.2)

# ---- Z corridor (G2 exit -> court), X 36..44, Y -1..3, flat ceiling -1.5 ----
# Zigzag: baffle wall at X=40.5 (Y -1..1.5) forces the fold; doorway gap in the
# thick wall (X 39.5..41.87) is the G2 exit. 20 mm chamfers at the two sharp
# outer corners are below modelling resolution — noted, not modelled.
wall_varying("SM_ZCorr_Wall_West", (36, -1), (36, 3), -6.3, -1.5, -6.3, -1.5,
             MAT_WHITE, COL_INTER, thick=0.2)
wall_varying("SM_ZCorr_Wall_North", (36, -1), (44, -1), -6.3, -1.5, -6.3, -1.5,
             MAT_WHITE, COL_INTER, thick=0.2)
wall_varying("SM_ZCorr_Wall_East", (44, -1), (44, 3), -6.3, -1.5, -6.3, -1.5,
             MAT_WHITE, COL_INTER, thick=0.2)
# South side: the thick wall itself is the south boundary for X 36..39.5;
# X 39.5..41.87 is the G2-exit doorway gap; only the east segment is built.
wall_varying("SM_ZCorr_Wall_South_E", (41.87, 3), (44, 3), -6.3, -1.5, -6.3, -1.5,
             MAT_WHITE, COL_INTER, thick=0.2)
wall_varying("SM_ZCorr_Baffle", (40.5, -1), (40.5, 1.5), -6.3, -1.5, -6.3, -1.5,
             MAT_WHITE, COL_INTER, thick=0.2)
flat_poly_slab("SM_ZCorr_Ceiling", [(36, -1), (44, -1), (44, 3), (36, 3)],
               -1.5, 0.06, MAT_CEILING_GYPSUM, COL_INTER)

# ---- Atrium furnishings (lower lobby, floor -6.3) ----
# Curved bookshelf: arc centred (8,7) r=2.8, angles 235..285 deg.
_book_rng = random.Random(7)
for _si, _ang in enumerate([235, 247.5, 260, 272.5, 285]):
    _a = math.radians(_ang)
    _cx = 8 + 2.8 * math.cos(_a)
    _cy = 7 + 2.8 * math.sin(_a)
    _rot = _a + math.pi / 2.0
    box(f"SM_Atrium_Shelf_Base_{_si}", (_cx, _cy, G2F + 0.06), (0.95, 0.35, 0.12), MAT_WOOD_SHELF, COL_INTER, rot=(0, 0, _rot))
    for _li, _lz in enumerate([G2F + 0.35, G2F + 0.82]):
        box(f"SM_Atrium_Shelf_Board_{_si}_{_li}", (_cx, _cy, _lz), (0.95, 0.35, 0.05), MAT_WOOD_SHELF, COL_INTER, rot=(0, 0, _rot))
        for _bi in range(3):
            _s = -0.28 + _bi * 0.28
            _bx = _cx + _s * math.cos(_rot)
            _by = _cy + _s * math.sin(_rot)
            _bh = _book_rng.uniform(0.18, 0.28)
            _bm = MAT_BOOKS[_book_rng.randrange(len(MAT_BOOKS))]
            box(f"SM_Atrium_Shelf_Book_{_si}_{_li}_{_bi}", (_bx, _by, _lz + 0.025 + _bh / 2),
                (0.16, 0.22, _bh), _bm, COL_INTER, rot=(0, 0, _rot + _book_rng.uniform(-0.06, 0.06)))
# Wooden benches by the south glass.
for _bi, (_bx, _by) in enumerate([(12, 0.5), (12, 3.0)]):
    _wood_bench(f"SM_Atrium_Bench_{_bi}", _bx, _by)
# Round tables (exhibit 12 sits on the (6,4) table).
for _ti, (_tx, _ty) in enumerate([(6.0, 4.0), (10.0, 3.0)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.05, location=(_tx, _ty, G2F + 0.55))
    _t = bpy.context.active_object
    _t.name = f"SM_Atrium_Table_{_ti}_Top"
    set_mat(_t, MAT_WOOD_LIGHT); link(_t, COL_INTER)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.52, location=(_tx, _ty, G2F + 0.28))
    _tl = bpy.context.active_object
    _tl.name = f"SM_Atrium_Table_{_ti}_Leg"
    set_mat(_tl, MAT_BLACK); link(_tl, COL_INTER)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.04, location=(_tx, _ty, G2F + 0.02))
    _tb = bpy.context.active_object
    _tb.name = f"SM_Atrium_Table_{_ti}_Base"
    set_mat(_tb, MAT_BLACK); link(_tb, COL_INTER)
# Warm recessed-look light strip under the sloped atrium soffit (tilted to follow it).
_warm_z = _atrium_soffit_z(4, 0) - 0.05
box("SM_Atrium_WarmStrip", (4, 0, _warm_z), (5.0, 0.25, 0.06), MAT_WARM_STRIP, COL_INTER,
    rot=(math.radians(-11.4), 0, 0))

# ---- Ground floor: entrance hall (reception + shop, new west lobby) ----
# (v22: desk moved to the entrance doorway (-7.80,-1.75), rotated to the
# west wall angle 67.35 deg; chunk 2 planned this move but never wrote it.)
box("SM_Reception_Desk", (-6.6, -3.2, 0.55), (3.2, 1.0, 1.1), MAT_WHITE, COL_INTER,
    rot=(0, 0, math.radians(67.35)))
box("SM_Reception_Desk_Top", (-6.6, -3.2, 1.12), (3.3, 1.1, 0.06), MAT_WOOD, COL_INTER,
    rot=(0, 0, math.radians(67.35)))
box("SM_Shop_Counter", (-1, 1, 0.5), (3.0, 0.9, 1.0), MAT_WOOD, COL_INTER)
# Entrance-hall columns — square concrete just inside the south glass, heights
# follow the roof profile at each column.
# v22: (24,1.2) and (34,1.2) fall INSIDE the sunken-court triangle
# (at y=1.2 the court spans x 21.42..36.27) — they floated over the
# -6.3 pit. (20,1.2) would poke 0.46 m through the low roof (roof
# 2.04, column min height 2.5). Moved to (16,1.2) (roof 2.78) and
# (38,1.2) (roof 4.34, inside the east diagonal at X=40.12).
for _cx, _cy in [(0, 1.2), (12, 1.2), (16, 1.2), (38, 1.2)]:
    _ch = max(2.5, roof_z_at(_cx, _cy) - 0.10)
    box(f"SM_Hall_Column_{_cx}", (_cx, _cy, _ch / 2.0), (0.45, 0.45, _ch), MAT_CONCRETE_BOARD, COL_INTER)

# ---- Atrium soffit: white gypsum following the roof (FIX [3]: 0.40 m below
# it at the eave ring, 0.65 m in the middle), over the FOOT trapezoid minus
# the court / void / stair openings (1.0 m grid). ----
_soff_v, _soff_f, _soff_idx = [], [], {}
_soff_xs = [-10.0 + 1.0 * i for i in range(54)] + [43.42]
_soff_ys = [-7.0 + 1.0 * i for i in range(11)]
for _xi, _x in enumerate(_soff_xs):
    for _yi, _y in enumerate(_soff_ys):
        _soff_idx[(_xi, _yi)] = len(_soff_v)
        _soff_v.append((_x, _y, _atrium_soffit_z(_x, _y)))
for _xi in range(len(_soff_xs) - 1):
    for _yi in range(len(_soff_ys) - 1):
        _a = _soff_idx[(_xi, _yi)]; _b = _soff_idx[(_xi + 1, _yi)]
        _c = _soff_idx[(_xi + 1, _yi + 1)]; _d = _soff_idx[(_xi, _yi + 1)]
        _cx = (_soff_v[_a][0] + _soff_v[_b][0] + _soff_v[_c][0] + _soff_v[_d][0]) / 4.0
        _cy = (_soff_v[_a][1] + _soff_v[_b][1] + _soff_v[_c][1] + _soff_v[_d][1]) / 4.0
        if not (_point_in_tri(_cx, _cy, (FOOT[0], FOOT[1], FOOT[2])) or
                _point_in_tri(_cx, _cy, (FOOT[0], FOOT[2], FOOT[3]))):
            continue
        if _in_void(_cx, _cy):
            continue
        _soff_f.append((_a, _b, _c, _d))
_soff_o = mesh_from_pydata("SM_Atrium_Soffit", _soff_v, _soff_f, MAT_CEILING_GYPSUM, COL_INTER)
solidify(_soff_o, 0.08)

# ---- #21A A3: ceiling access panels + sprinkler heads (white gypsum ceilings) ----
# (Helpers _ceiling_panel_square / _ceiling_panel_round / _sprinkler / _slope_rot
# re-emitted above by apply_issue21B.py.)
# G2 ceiling (flat, soffit z=-1.53): 2 rows of sprinklers + 1 square + 1 round panel.
for _si, _sx in enumerate([19.0, 23.5, 28.0, 32.5, 37.0, 41.5, 46.0]):
    _sprinkler(f"SM_G2_Sprinkler_N_{_si}", _sx, 4.2, -1.53)
    _sprinkler(f"SM_G2_Sprinkler_S_{_si}", _sx, 15.0, -1.53)
_ceiling_panel_square("SM_G2_Access_Square", 25.0, 10.0, -1.53)
_ceiling_panel_round("SM_G2_Access_Round", 42.0, 14.0, -1.53)
# G1 ceiling (flat, soffit z=-2.25): 4 sprinklers + 1 square + 1 round panel.
for _si, (_gx, _gy) in enumerate([(6.0, 4.0), (10.0, 4.0), (6.0, 9.0), (10.0, 9.0)]):
    _sprinkler(f"SM_G1_Sprinkler_{_si}", _gx, _gy, -2.25)
_ceiling_panel_square("SM_G1_Access_Square", 8.0, 6.0, -2.25)
_ceiling_panel_round("SM_G1_Access_Round", 12.0, 10.0, -2.25)
# G3 ceiling (sloped, Section C profile): 3 sprinklers + 1 square + 1 round panel.
for _si, (_gx, _gy) in enumerate([_g3_pt(5, 3), _g3_pt(10, 3), _g3_pt(12, 5)]):
    _sprinkler(f"SM_G3_Sprinkler_{_si}", _gx, _gy, g3_ceiling_z(_gx, _gy))
_ax, _ay = _g3_pt(4, 3)
_rx, _ry = _slope_rot(g3_ceiling_z, _ax, _ay)
_ceiling_panel_square("SM_G3_Access_Square", _ax, _ay, g3_ceiling_z(_ax, _ay), _rx, _ry)
_bx, _by = _g3_pt(9, 5)
_rx, _ry = _slope_rot(g3_ceiling_z, _bx, _by)
_ceiling_panel_round("SM_G3_Access_Round", _bx, _by, g3_ceiling_z(_bx, _by), _rx, _ry)
# Atrium soffit (sloped, z = roof_z_at - 0.40..0.65): 4 sprinklers + 1 square panel.
for _si, (_ax, _ay) in enumerate([(0.0, 0.0), (8.0, 0.0), (0.0, -4.0), (8.0, -4.0)]):
    _sprinkler(f"SM_Atrium_Sprinkler_{_si}", _ax, _ay, _atrium_soffit_z(_ax, _ay))
_rx, _ry = _slope_rot(_atrium_soffit_z, 4.0, -2.0)
_ceiling_panel_square("SM_Atrium_Access_Square", 4.0, -2.0, _atrium_soffit_z(4.0, -2.0), _rx, _ry)
# Stair sprinkler, low mount on a 0.25 m drop pipe under the stair soffit.
# Nosing line: z = -(x-15.63)/0.30*0.15; soffit bottom = nosing - 0.30.
_sx = 21.93
_sz_nose = -(_sx - 15.63) / 0.30 * 0.15
_sz_soffit = _sz_nose - 0.30
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.015, depth=0.25, location=(_sx, -4.85, _sz_soffit - 0.125))
_o = bpy.context.active_object
_o.name = "SM_Stair_Sprinkler_Drop"
set_mat(_o, MAT_SPRINKLER); link(_o, COL_INTER)
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=0.012, location=(_sx, -4.85, _sz_soffit - 0.25))
_o2 = bpy.context.active_object
_o2.name = "SM_Stair_Sprinkler"
set_mat(_o2, MAT_SPRINKLER); link(_o2, COL_INTER)

print("=== interior done ===")
# ---- helpers re-emitted from the PR-A exhibits (unchanged) ----
def plinth(name, x, y, w, d, h=0.45):
    return box(name, (x, y, G2F + h / 2), (w, d, h), MAT_PLINTH, COL_EXH)

def chair(name, x, y, rot_z=0.0, mat=None):
    m = mat or MAT_WOOD
    # seat, back, 4 legs — simple modern chair, ~0.45 seat height
    box(f"{name}_Seat", (x, y, G2F + 0.45), (0.46, 0.44, 0.05), m, COL_EXH)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x - 0.20, y, G2F + 0.72))
    b = bpy.context.active_object
    b.name = f"{name}_Back"
    b.dimensions = (0.05, 0.44, 0.55)
    b.rotation_euler = (0, -0.12, rot_z)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    set_mat(b, m); link(b, COL_EXH)
    for (lx, ly) in [(-0.19, -0.18), (0.19, -0.18), (-0.19, 0.18), (0.19, 0.18)]:
        box(f"{name}_Leg_{lx}_{ly}", (x + lx, y + ly, G2F + 0.225), (0.04, 0.04, 0.45), MAT_BLACK, COL_EXH)

def draped_fabric(name, x, y, w=4.5, h=3.6):
    # Denser grid + irregular folds + a billow so it reads as a hanging textile,
    # not a set of flat boards. (v1-v4: a coarse 10x14 grid with a single sine
    # wave rendered as rigid red panels.)
    nx, ny = 28, 22
    verts, faces = [], []
    for j in range(ny):
        for i in range(nx):
            fx, fy = i / (nx - 1), j / (ny - 1)
            px = x - w / 2 + w * fx
            pz = G2F + 0.15 + h * fy
            # irregular draped folds: two sine components, deeper toward the bottom
            fold = (math.sin(fx * math.pi * 3.0) * 0.38
                    + math.sin(fx * math.pi * 7.0 + 1.3) * 0.16)
            fold *= (0.35 + 0.65 * (1.0 - fy))
            # billow: the cloth bows outward at mid-height
            billow = math.sin(fy * math.pi) * 0.28
            # uneven bottom edge
            edge = 0.0
            if fy < 0.12:
                edge = math.sin(fx * math.pi * 5.0) * 0.12 * (1.0 - fy / 0.12)
            verts.append((px, y + fold + billow, pz + edge))
    for j in range(ny - 1):
        for i in range(nx - 1):
            a, b = j * nx + i, j * nx + i + 1
            c, d = (j + 1) * nx + i + 1, (j + 1) * nx + i
            faces.append((a, b, c, d))
    o = mesh_from_pydata(name, verts, faces, MAT_RED, COL_EXH)
    solidify(o, 0.04)
    # hanging rod
    box(f"{name}_Rod", (x, y, G2F + 0.15 + h + 0.05), (w + 0.3, 0.06, 0.06), MAT_BLACK, COL_EXH)
    return o

def low_table(name, x, y, w, d, h=0.45, floor_z=G2F):
    """Low wooden display table: top slab + 4 legs. Top surface at floor_z+h+0.03."""
    box(f"{name}_Top", (x, y, floor_z + h), (w, d, 0.06), MAT_WOOD, COL_EXH)
    for (lx, ly) in [(-w / 2 + 0.06, -d / 2 + 0.06), (w / 2 - 0.06, -d / 2 + 0.06),
                     (-w / 2 + 0.06, d / 2 - 0.06), (w / 2 - 0.06, d / 2 - 0.06)]:
        box(f"{name}_Leg_{lx:.2f}_{ly:.2f}", (x + lx, y + ly, floor_z + (h - 0.03) / 2),
            (0.05, 0.05, h - 0.03), MAT_BLACK, COL_EXH)

# ================= EXHIBITS — #21B geometry rebuild =================
# Faithful remap of the PR-A exhibits (same designs, same materials).
# G2 remap (old G2 X 24..52, Y -1..15 -> new X 15.08..48.56, Y 3.25..17.24):
# x' = 15.08 + (x-24)*1.1957, y' = 3.25 + (y+1)*0.8744. Floor G2F=-6.75.
# Exhibit 10 (bento) sits in G1 (floor G1F=-7.20); exhibit 12 sits on the
# atrium table (6,4). (Helpers plinth / chair / draped_fabric / low_table are
# re-emitted above by apply_issue21B.py from the PR-A script.)
G2F = -6.3
G1F = -7.20
G2C = -1.5

# Material values identical to the PR-A exhibits section (no material change in PR-B).
MAT_AKARI = mat_principled("MAT_Akari_Paper", (0.98, 0.90, 0.75), rough=0.9,
                           emission=(1.0, 0.85, 0.6), emission_strength=1.2)
MAT_KYUSU_CLAY = mat_principled("MAT_Kyusu_Clay", (0.32, 0.20, 0.13), rough=0.85)
MAT_INDIGO = mat_principled("MAT_Indigo_Cloth", (0.10, 0.16, 0.35), rough=0.95)
MAT_LACQUER_BLACK = mat_principled("MAT_Lacquer_Black", (0.02, 0.02, 0.02), rough=0.25)
MAT_LACQUER_RED = mat_principled("MAT_Lacquer_Red", (0.45, 0.03, 0.02), rough=0.30)
MAT_BAMBOO = mat_principled("MAT_Bamboo", (0.72, 0.58, 0.35), rough=0.9)
MAT_BAMBOO_DARK = mat_principled("MAT_Bamboo_Dark", (0.45, 0.33, 0.18), rough=0.9)
MAT_TEA_BOWL = mat_principled("MAT_Tea_Bowl", (0.12, 0.08, 0.06), rough=0.35)
MAT_MATCHA = mat_principled("MAT_Matcha", (0.25, 0.45, 0.15), rough=0.6)
MAT_TEA_DARK = mat_principled("MAT_Tea_Dark", (0.15, 0.08, 0.03), rough=0.6)

# EXHIBIT 01 — A-POC red fabric: draped hanging textile panel (32,9.5) -> (24.65,12.43)
draped_fabric("SM_EXHIBIT_01_RedFabric", 24.65, 12.43)
plinth("SM_EXHIBIT_01_Plinth", 24.65, 12.43, 5.0, 0.9, h=0.12)

# EXHIBIT 02 — pendant light cluster: 7 lamps. Old cords ran from z=0.0;
# new cords hang from the G2 ceiling (-1.5); lamp heights above the floor kept.
for i, (px, py, drop) in enumerate([(27.04, 9.37, 1.6), (28.47, 10.42, 2.2), (29.43, 9.02, 1.2),
                                     (26.32, 10.77, 2.6), (29.19, 11.29, 1.9), (27.51, 11.64, 2.4),
                                     (29.91, 10.07, 1.4)]):
    top_z = G2C
    bot_z = G2C - drop
    box(f"SM_EXHIBIT_02_Cord_{i}", (px, py, (top_z + bot_z) / 2), (0.02, 0.02, top_z - bot_z), MAT_BLACK, COL_EXH)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(px, py, bot_z))
    s = bpy.context.active_object
    s.name = f"SM_EXHIBIT_02_Lamp_{i}"
    set_mat(s, MAT_LIGHT); link(s, COL_EXH)
plinth("SM_EXHIBIT_02_Plinth", 28.23, 10.25, 4.0, 4.0, h=0.1)

# EXHIBIT 03 — three chairs in a row (40.5/42/43.5, 8.2) -> (34.80/36.60/38.39, 11.29)
for i, cx in enumerate([34.80, 36.60, 38.39]):
    chair(f"SM_EXHIBIT_03_Chair_{i}", cx, 11.29, rot_z=0.15)
plinth("SM_EXHIBIT_03_Plinth", 36.60, 11.29, 4.2, 1.2, h=0.12)

# EXHIBIT 04 — graphic design wall: white panel + coloured shapes (south wall).
# Old panel (38,15.85) -> (31.82,17.10); shapes keep their offsets from the panel.
box("SM_EXHIBIT_04_Panel", (31.82, 17.10, G2F + 1.8), (8.0, 0.12, 3.6), MAT_WHITE, COL_EXH)
box("SM_EXHIBIT_04_Red", (28.94, 17.03, G2F + 2.2), (1.6, 0.06, 1.6), MAT_RED, COL_EXH)
box("SM_EXHIBIT_04_Blue",
    (32.53, 17.03, G2F + 1.6), (1.8, 0.06, 1.0),
    mat_principled("MAT_Blue", (0.10, 0.25, 0.65), rough=0.6), COL_EXH)
box("SM_EXHIBIT_04_Black", (35.52, 17.03, G2F + 2.6), (1.2, 0.06, 0.8), MAT_BLACK, COL_EXH)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(35.05, 17.03, G2F + 1.0))
o = bpy.context.active_object
o.name = "SM_EXHIBIT_04_Circle"
o.scale = (1, 0.12, 1)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.object.shade_smooth()
set_mat(o, mat_principled("MAT_Yellow", (0.95, 0.75, 0.10), rough=0.6)); link(o, COL_EXH)

# EXHIBIT 05 — ceramic jars on a plinth (46,10) -> (41.39,12.87)
plinth("SM_EXHIBIT_05_Plinth", 41.39, 12.87, 3.0, 1.2, h=0.5)
for i, (jx, jr, jh) in enumerate([(40.19, 0.28, 0.75), (41.27, 0.34, 0.95), (42.34, 0.26, 0.65),
                                   (43.30, 0.30, 0.85), (41.75, 0.22, 0.55)]):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=jr, location=(jx, 12.87, G2F + 0.5 + jh * 0.45))
    s = bpy.context.active_object
    s.name = f"SM_EXHIBIT_05_Jar_{i}"
    s.scale = (1, 1, jh / (jr * 2) * 1.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    set_mat(s, MAT_CERAMIC); link(s, COL_EXH)
    box(f"SM_EXHIBIT_05_Neck_{i}", (jx, 12.87, G2F + 0.5 + jh * 0.95), (0.12, 0.12, 0.18), MAT_CERAMIC, COL_EXH)

# EXHIBIT 06 — central rotating installation: plinth + tilted torus ring (36,2.5) -> (29.43,6.31)
plinth("SM_EXHIBIT_06_Plinth", 29.43, 6.31, 2.2, 2.2, h=0.5)
box("SM_EXHIBIT_06_Stand", (29.43, 6.31, G2F + 1.1), (0.18, 0.18, 1.2), MAT_BLACK, COL_EXH)
bpy.ops.mesh.primitive_torus_add(major_radius=0.85, minor_radius=0.09,
    location=(29.43, 6.31, G2F + 2.1), rotation=(math.radians(65), 0, math.radians(20)))
t = bpy.context.active_object
t.name = "SM_EXHIBIT_06_Ring"
bpy.context.view_layer.objects.active = t
bpy.ops.object.shade_smooth()
set_mat(t, MAT_STEEL_DARK); link(t, COL_EXH)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(29.43, 6.31, G2F + 2.1))
s = bpy.context.active_object
s.name = "SM_EXHIBIT_06_Core"
bpy.context.view_layer.objects.active = s
bpy.ops.object.shade_smooth()
set_mat(s, MAT_RED_SPHERE); link(s, COL_EXH)

# EXHIBIT 07 — Akari paper lantern (Noguchi) (48,4.5) -> (43.78,8.06)
plinth("SM_EXHIBIT_07_Plinth", 43.78, 8.06, 1.2, 1.2, h=0.10)
box("SM_EXHIBIT_07_Stand", (43.78, 8.06, G2F + 0.38), (0.05, 0.05, 0.56), MAT_BLACK, COL_EXH)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.38,
                                     location=(43.78, 8.06, G2F + 1.04))
_s = bpy.context.active_object
_s.name = "SM_EXHIBIT_07_Shade"
_s.scale = (1, 1, 1.15)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.object.shade_smooth()
set_mat(_s, MAT_AKARI); link(_s, COL_EXH)

# EXHIBIT 08 — Kyusu teapot + 2 cups on a low wooden table (47,13.5) -> (42.58,15.93)
low_table("SM_EXHIBIT_08_Table", 42.58, 15.93, 1.3, 0.65, h=0.45)
_top08 = G2F + 0.48
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.16,
                                     location=(42.58, 15.93, _top08 + 0.12))
_s = bpy.context.active_object
_s.name = "SM_EXHIBIT_08_Teapot_Body"
_s.scale = (1, 1, 0.75)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.object.shade_smooth()
set_mat(_s, MAT_KYUSU_CLAY); link(_s, COL_EXH)
bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.03, location=(42.58, 15.93, _top08 + 0.24))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_08_Teapot_Lid"
set_mat(_o, MAT_KYUSU_CLAY); link(_o, COL_EXH)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(42.58, 15.93, _top08 + 0.27))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_08_Teapot_Knob"
set_mat(_o, MAT_KYUSU_CLAY); link(_o, COL_EXH)
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.24,
                                    location=(42.81, 15.93, _top08 + 0.17),
                                    rotation=(0, math.radians(50), 0))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_08_Teapot_Spout"
set_mat(_o, MAT_KYUSU_CLAY); link(_o, COL_EXH)
bpy.ops.mesh.primitive_torus_add(major_radius=0.085, minor_radius=0.016,
                                 location=(42.38, 15.93, _top08 + 0.14),
                                 rotation=(math.radians(90), 0, 0))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_08_Teapot_Handle"
set_mat(_o, MAT_KYUSU_CLAY); link(_o, COL_EXH)
for _ci, (_cx, _cy) in enumerate([(43.06, 16.10), (43.06, 15.75)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.09, location=(_cx, _cy, _top08 + 0.045))
    _o = bpy.context.active_object
    _o.name = f"SM_EXHIBIT_08_Cup_{_ci}"
    set_mat(_o, MAT_CERAMIC); link(_o, COL_EXH)
bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.012, location=(43.06, 16.10, _top08 + 0.085))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_08_Tea"
set_mat(_o, MAT_TEA_DARK); link(_o, COL_EXH)

# EXHIBIT 09 — Noren indigo curtain in the G1->G2 doorway (X=15.08, Y 5..8).
# Rotated 90 deg from the old doorway (x 28..31, y=-1): rod along Y, panels
# thin in X; crests face +/-X (cylinder axis along X). Rod 2.25 m above floor.
box("SM_EXHIBIT_09_Rod", (15.08, 6.5, -4.05), (0.05, 3.0, 0.05), MAT_BLACK, COL_EXH)
box("SM_EXHIBIT_09_Panel_L", (15.08, 5.75, -4.95), (0.04, 1.3, 1.8), MAT_INDIGO, COL_EXH)
box("SM_EXHIBIT_09_Panel_R", (15.08, 7.25, -4.95), (0.04, 1.3, 1.8), MAT_INDIGO, COL_EXH)
for _di, (_dx, _dy) in enumerate([(15.05, 5.75), (15.11, 5.75),
                                  (15.05, 7.25), (15.11, 7.25)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.02,
                                        location=(_dx, _dy, -4.80),
                                        rotation=(0, math.radians(90), 0))
    _o = bpy.context.active_object
    _o.name = f"SM_EXHIBIT_09_Crest_{_di}"
    set_mat(_o, MAT_WHITE); link(_o, COL_EXH)

# EXHIBIT 10 — Lacquer bento box (black + red tiers) on a low table, G1 (9,6).
# Table on the G1 floor (floor_z=G1F=-7.20).
low_table("SM_EXHIBIT_10_Table", 9.0, 6.0, 0.95, 0.6, h=0.40, floor_z=G1F)
_top10 = G1F + 0.43
box("SM_EXHIBIT_10_Tier_Black", (9.0, 6.0, _top10 + 0.045), (0.34, 0.24, 0.09), MAT_LACQUER_BLACK, COL_EXH)
box("SM_EXHIBIT_10_Tier_Red", (9.01, 6.0, _top10 + 0.135), (0.32, 0.22, 0.09), MAT_LACQUER_RED, COL_EXH)
box("SM_EXHIBIT_10_Lid", (9.0, 6.0, _top10 + 0.19), (0.34, 0.24, 0.02), MAT_LACQUER_BLACK, COL_EXH)
box("SM_EXHIBIT_10_Chopstick_0", (9.35, 6.22, _top10 + 0.008), (0.22, 0.016, 0.016), MAT_BAMBOO_DARK, COL_EXH, rot=(0, 0, 0.20))
box("SM_EXHIBIT_10_Chopstick_1", (9.35, 6.26, _top10 + 0.008), (0.22, 0.016, 0.016), MAT_BAMBOO_DARK, COL_EXH, rot=(0, 0, 0.16))

# EXHIBIT 11 — Bamboo basket on a low round plinth, G2 west end (28,4) -> (19.86,7.62)
bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.10, location=(19.86, 7.62, G2F + 0.05))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_11_Plinth"
set_mat(_o, MAT_PLINTH); link(_o, COL_EXH)
bpy.ops.mesh.primitive_cone_add(radius1=0.26, radius2=0.32, depth=0.42, vertices=24,
                                location=(19.86, 7.62, G2F + 0.31))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_11_Basket"
set_mat(_o, MAT_BAMBOO); link(_o, COL_EXH)
bpy.ops.mesh.primitive_torus_add(major_radius=0.32, minor_radius=0.02, location=(19.86, 7.62, G2F + 0.52))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_11_Rim"
set_mat(_o, MAT_BAMBOO_DARK); link(_o, COL_EXH)
bpy.ops.mesh.primitive_cylinder_add(radius=0.29, depth=0.02, location=(19.86, 7.62, G2F + 0.50))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_11_Interior"
set_mat(_o, MAT_BAMBOO_DARK); link(_o, COL_EXH)
bpy.ops.mesh.primitive_torus_add(major_radius=0.30, minor_radius=0.015, location=(19.86, 7.62, G2F + 0.31))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_11_Band"
set_mat(_o, MAT_BAMBOO_DARK); link(_o, COL_EXH)

# EXHIBIT 12 — Tea bowl + chasen (bamboo whisk) on a wooden tray, on the
# atrium round table (6,4). Table top at G2F+0.55 (top surface -6.175);
# tray sits on it (centre -6.165), bowl/matcha/chasen above the tray.
box("SM_EXHIBIT_12_Tray", (6.0, 4.0, -6.165), (0.42, 0.30, 0.02), MAT_WOOD, COL_EXH)
bpy.ops.mesh.primitive_cylinder_add(radius=0.085, depth=0.08, location=(5.88, 3.95, -6.115))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_12_TeaBowl"
set_mat(_o, MAT_TEA_BOWL); link(_o, COL_EXH)
bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.012, location=(5.88, 3.95, -6.075))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_12_Matcha"
set_mat(_o, MAT_MATCHA); link(_o, COL_EXH)
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.06, location=(6.12, 4.08, -6.125))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_12_Chasen_Handle"
set_mat(_o, MAT_BAMBOO); link(_o, COL_EXH)
bpy.ops.mesh.primitive_cone_add(radius1=0.022, radius2=0.05, depth=0.09, vertices=16,
                                location=(6.12, 4.08, -6.05))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_12_Chasen_Bristles"
set_mat(_o, MAT_BAMBOO); link(_o, COL_EXH)

print("=== exhibits done ===")
# ================= ROOT + SAVE + EXPORT =================
# Single wrapper root for a clean GLB hierarchy (two wings + site + interior + exhibits)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
root = bpy.context.active_object
root.name = "WEB_ROOT"
root.empty_display_size = 2.0
for coll in (COL_SITE, COL_MUSEUM, COL_CAFE, COL_INTER, COL_EXH):
    for o in list(coll.objects):
        if o.parent is None:
            o.parent = root
            o.matrix_parent_inverse = root.matrix_world.inverted()

# ================= BAKE (v12): procedural -> image textures =================
# The glTF exporter does NOT export procedural textures, so every key material
# is baked to a PNG and re-wired through an Image Texture node on Base Color.
# Bake planes are created far outside the model and deleted right after each
# bake, so they never reach the export. Verified after export by re-import
# (verify_2121_v12.py prints GLB-MAT-TEX lines + GLB-IMAGES count).
TEX_DIR = os.path.join(OUT_DIR, "textures_v16")
os.makedirs(TEX_DIR, exist_ok=True)
BAKE_JOBS = [
    ("MAT_Concrete", 1024), ("MAT_Concrete_Board", 1024), ("MAT_Steel_Roof", 1024),
    ("MAT_Grass", 1024), ("MAT_Paving", 1024), ("MAT_Wood_Floor", 512),
    ("MAT_Granite", 512),  # #18: MAT_Flowers gone with the beds; #21A A4: MAT_Concrete_Dark deleted
    ("MAT_Wood_Shelf", 512), ("MAT_Wood_Light", 512),
]
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = 8
try:
    _bprefs = bpy.context.preferences.addons['cycles'].preferences
    _bprefs.compute_device_type = 'OPTIX'
    for _d in _bprefs.devices:
        _d.use = True
except Exception as _e:
    print("bake GPU prefs warning:", _e)
for _mat_name, _size in BAKE_JOBS:
    _mat = bpy.data.materials.get(_mat_name)
    if _mat is None:
        print(f"BAKE-SKIP missing material {_mat_name}")
        continue
    _img = bpy.data.images.new(f"{_mat_name}_bake", width=_size, height=_size, alpha=False)
    _img.filepath_raw = os.path.join(TEX_DIR, f"{_mat_name}.png")
    _img.file_format = 'PNG'
    _nt = _mat.node_tree
    _tex = _nt.nodes.new("ShaderNodeTexImage")
    _tex.image = _img
    _nt.nodes.active = _tex
    bpy.ops.mesh.primitive_plane_add(size=1.8, location=(120.0, 120.0, -20.0))  # PR-D [Tex18]: bake tile 2.0 -> 1.8 m
    _plane = bpy.context.active_object
    _plane.name = f"BAKE_{_mat_name}"
    _plane.data.materials.append(_mat)
    bpy.context.view_layer.objects.active = _plane
    _plane.select_set(True)
    _baked = False
    for _attempt in range(2):
        try:
            try:
                bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, margin=4)
            except TypeError:
                bpy.ops.object.bake(type='DIFFUSE', use_pass_direct=False,
                                    use_pass_indirect=False, use_pass_color=True, margin=4)
            _baked = True
            break
        except Exception as _e:
            print(f"BAKE-ATTEMPT{_attempt} fail {_mat_name}: {_e}")
            if _attempt == 0:
                scene.cycles.device = 'CPU'
                print("BAKE-RETRY on CPU")
    if _baked:
        try:
            _img.save()
            print(f"BAKE-OK {_mat_name} {_size}x{_size} -> {_img.filepath_raw}")
        except Exception as _e:
            print(f"BAKE-SAVE-FAIL {_mat_name}: {_e}")
            _baked = False
    else:
        print(f"BAKE-FAIL {_mat_name} (kept procedural; will export flat)")
    bpy.data.objects.remove(_plane, do_unlink=True)
    if _baked:
        _bsdf = _nt.nodes["Principled BSDF"]
        _nt.links.new(_tex.outputs["Color"], _bsdf.inputs["Base Color"])
    scene.cycles.device = 'GPU'
print("=== bake done ===")
# ================= #20: far-ground radial gradient v2 =================
# Hark PR #20 item 1: the v18 gradient made the far ground MORE saturated
# than the lawn ("carpet") and left a hard line at the 400 m horizon edge.
# Two errors, both fixed here:
#  (a) centre: v18 used the raw baked-grass average. The lawn's FINAL
#      colour is that average AFTER the page's 0.45 desaturation
#      (applyAestheticMaterials -> desaturateTexture, Rec.601 luma, sRGB
#      bytes). Measured v18: grass mean (68.7,102.3,61.4) -> desat45
#      (77.2,95.7,73.2). Centre must equal that, or the lawn reads as a
#      dark square inside brighter far ground.
#  (b) outer: v18 faded to (0.32,0.35,0.32) dark grey-green, NOT the fog
#      colour. The edge then relied on three.js fog alone, and fog colour
#      (0xc8d3d6) vs the sky just above the edge (~12% lighter) left a
#      straight step. Now the texture itself reaches the exact fog colour
#      (200,211,214) by 220 m, so the ground is fog-coloured long before
#      its edge; the ground is also enlarged to 1600 m (see strips below)
#      so the edge sits ~0.5 deg above the true horizon.
# Colour-space note: Blender loads/saves these image pixels RAW
# (byte/255, no sRGB conversion) — verified on the v18 gradient (saved
# centre bytes (69,102,61) = grass PNG byte mean; edge bytes (82,89,82)
# = (0.32,0.35,0.32)*255). All math below is in byte/255 space.
# Dither: deterministic +/-1 LSB triangular noise, so the 8-bit ramp does
# not quantise into the faint concentric rings seen in the v18 aerials.
try:
    _fg_grass = bpy.data.images.load(os.path.join(TEX_DIR, "MAT_Grass.png"))
    _fg_px = _fg_grass.pixels[:]
    _fg_n = 0
    _fg_r = _fg_g = _fg_b = 0.0
    for _fg_i in range(0, len(_fg_px), 64):  # every 16th pixel (RGBA)
        _fg_r += _fg_px[_fg_i]
        _fg_g += _fg_px[_fg_i + 1]
        _fg_b += _fg_px[_fg_i + 2]
        _fg_n += 1
    _lawn_raw = (_fg_r / _fg_n, _fg_g / _fg_n, _fg_b / _fg_n)
    _fg_luma = 0.299 * _lawn_raw[0] + 0.587 * _lawn_raw[1] + 0.114 * _lawn_raw[2]
    _lawn = tuple(_c + (_fg_luma - _c) * 0.45 for _c in _lawn_raw)
    print(f"#20 far gradient: baked lawn avg (raw) = {_lawn_raw}, desat45 = {_lawn}")
    if max(_lawn) < 0.03:
        raise ValueError("baked lawn sample implausibly dark")
except Exception as _e:
    print(f"#20 far gradient: grass sample failed ({_e}), using measured v18 value")
    _lawn = (77 / 255, 96 / 255, 73 / 255)
_FOG20 = (200 / 255, 211 / 255, 214 / 255)  # scene fog colour 0xc8d3d6
_FG_SIZE = 1024
_FG_SPAN = 1600.0  # texture spans the 1600 m far ground
_fg_img = bpy.data.images.new("FarGround_Gradient", width=_FG_SIZE, height=_FG_SIZE, alpha=False)
_fg_img.filepath_raw = os.path.join(TEX_DIR, "far_ground_gradient.png")
_fg_img.file_format = 'PNG'
import numpy as _fg_np
_fg_yy, _fg_xx = _fg_np.mgrid[0:_FG_SIZE, 0:_FG_SIZE]
_fg_dx = (_fg_xx - _FG_SIZE / 2 + 0.5) / (_FG_SIZE / 2)
_fg_dy = (_fg_yy - _FG_SIZE / 2 + 0.5) / (_FG_SIZE / 2)
_fg_r = _fg_np.sqrt(_fg_dx * _fg_dx + _fg_dy * _fg_dy) * (_FG_SPAN / 2.0)
_fg_t = (_fg_r - 60.0) / (220.0 - 60.0)
_fg_t = _fg_np.clip(_fg_t, 0.0, 1.0)
_fg_t = _fg_t * _fg_t * (3.0 - 2.0 * _fg_t)  # smoothstep
_fg_rng = _fg_np.random.default_rng(20)
_fg_pix = _fg_np.zeros((_FG_SIZE, _FG_SIZE, 4), dtype=_fg_np.float32)
for _fg_i in range(3):
    _fg_pix[:, :, _fg_i] = _lawn[_fg_i] + (_FOG20[_fg_i] - _lawn[_fg_i]) * _fg_t
    _fg_pix[:, :, _fg_i] += (_fg_rng.random((_FG_SIZE, _FG_SIZE)) + _fg_rng.random((_FG_SIZE, _FG_SIZE)) - 1.0) / 255.0
_fg_pix[:, :, 3] = 1.0
_fg_pix = _fg_np.clip(_fg_pix, 0.0, 1.0)
_fg_img.pixels = _fg_pix.reshape(-1).tolist()
_fg_img.save()
print(f"#20 far gradient saved -> {_fg_img.filepath_raw} (centre={tuple(round(_c * 255) for _c in _lawn)}, fog={tuple(round(_c * 255) for _c in _FOG20)})")
# Wire it onto MAT_FarGround (base colour to white so the exporter does
# not multiply the texture by the old flat factor).
try:
    _fnt = MAT_FARGROUND.node_tree
    _fbsdf = _fnt.nodes["Principled BSDF"]
    _fbsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    _ftex = _fnt.nodes.new("ShaderNodeTexImage")
    _ftex.image = _fg_img
    _fnt.links.new(_ftex.outputs["Color"], _fbsdf.inputs["Base Color"])
    print("#20 far gradient wired onto MAT_FarGround")
except Exception as _e:
    print(f"#20 far gradient wiring failed: {_e}")
# UVs: cube projection (world-scale, 1.8 m tile) on every mesh so baked
# textures map at a consistent scale; required for image textures in glTF.
for _o in list(bpy.context.scene.objects):
    if _o.type != 'MESH':
        continue
    if _o.name.startswith("SM_Tree_Card") or _o.name.startswith("SM_Tree_TopCard"):
        continue  # leaf cards already carry their own 0..1 UVs
    if _o.name.startswith("SM_Site_FarGround_"):
        continue  # #18/#20: far-ground strips keep their world-mapped UVs (u=(x+800)/1600) for the radial-gradient texture; cube_project would tile it every 1.8 m into a dot grid
    bpy.context.view_layer.objects.active = _o
    _o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    try:
        bpy.ops.uv.cube_project(cube_size=1.8)  # PR-D [Tex18]: was 2.0
    except Exception as _e:
        print(f"UV-FAIL {_o.name}: {_e}")
    bpy.ops.object.mode_set(mode='OBJECT')
    _o.select_set(False)
print("=== UV done ===")

bpy.ops.wm.save_mainfile(filepath=BLEND_PATH)
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

# ---- stats ----
import collections as _c
total_tris = 0
nmesh = 0
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        nmesh += 1
        total_tris += len(o.data.polygons)
print(f"STATS objects={len(bpy.context.scene.objects)} meshes={nmesh} tris={total_tris}")
# bounding box of the whole model
import mathutils
mn = mathutils.Vector((1e9, 1e9, 1e9)); mx = mathutils.Vector((-1e9, -1e9, -1e9))
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        for c in o.bound_box:
            w = o.matrix_world @ mathutils.Vector(c)
            mn = mathutils.Vector(map(min, mn, w)); mx = mathutils.Vector(map(max, mx, w))
print(f"BBOX min={tuple(round(v,2) for v in mn)} max={tuple(round(v,2) for v in mx)} size={tuple(round(v,2) for v in (mx-mn))}")

# ---- export GLB (selection = everything under WEB_ROOT) ----
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
    if o.type in ('MESH', 'EMPTY'):
        o.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=GLB_PATH, export_format='GLB', use_selection=True,
    export_yup=True, export_apply=False, export_animations=False,
    export_texcoords=True, export_normals=True, export_materials='EXPORT',
    export_image_format='AUTO', export_cameras=False, export_lights=False)
print(f"exported {GLB_PATH} size={os.path.getsize(GLB_PATH)} bytes")
print("=== BUILD COMPLETE ===")
