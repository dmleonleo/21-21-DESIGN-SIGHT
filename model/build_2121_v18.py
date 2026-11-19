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
#      Roof, ceiling (clamped to roof-0.30), north wall, cove strip and the
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
BLEND_PATH = os.path.join(OUT_DIR, "design2121_v18_build.blend")
GLB_PATH = os.path.join(OUT_DIR, "design2121_v18.glb")
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

MAT_CONCRETE = mat_principled("MAT_Concrete", (0.66, 0.64, 0.60), rough=0.92)
MAT_CONCRETE_DARK = mat_principled("MAT_Concrete_Dark", (0.42, 0.41, 0.40), rough=0.95)

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
add_concrete_noise(MAT_CONCRETE_DARK, scale=2.5, strength=0.10)
MAT_STEEL = mat_principled("MAT_Steel_Roof", (0.18, 0.19, 0.20), metallic=0.08, rough=0.55)
try:
    # v14r2: cut the grazing-angle sky reflection further — at the low front
    # angle the roof still mirrored the bright sky white. Specular IOR 0.5
    # was not enough; 0.25 kills the Fresnel wash while keeping a steel read.
    MAT_STEEL.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.25
except Exception as e:
    print("steel specular warning:", e)
MAT_STEEL_DARK = mat_principled("MAT_Steel_Dark", (0.30, 0.31, 0.32), metallic=0.8, rough=0.45)
MAT_STEEL_SEAM = mat_principled("MAT_Steel_Seam", (0.08, 0.08, 0.09), metallic=0.3, rough=0.6)

def add_board_form(mat, scale=5.0):
    """Board-formed concrete hint: stronger colour variation + horizontal board
    lines via a Brick texture used as bump only (colour stays concrete grey).
    Real 21_21 concrete shows plank lines ~0.3-0.5 m and a tie-hole grid."""
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
        brick = nt.nodes.new("ShaderNodeTexBrick")
        brick.inputs["Scale"].default_value = scale
        brick.inputs["Mortar Size"].default_value = 0.02
        # wide planks: ~0.6 m board lines on the 2 m bake plane
        brick.inputs["Brick Width"].default_value = 3.0
        brick.inputs["Row Height"].default_value = 1.5
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.25
        bump.inputs["Distance"].default_value = 0.05
        nt.links.new(brick.outputs["Color"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        # darken mortar lines in the colour as well: only the colour bakes
        # into the glTF texture, the procedural bump does not export
        mix = nt.nodes.new("ShaderNodeMixRGB")
        mix.blend_type = 'MIX'
        mix.inputs[2].default_value = (0.14, 0.14, 0.13, 1.0)
        # NOTE (v13r2): Brick "Factor" is 1.0 in the MORTAR, 0.0 in the brick
        # (proven by pixel-metering the baked PNG) — use it directly.
        nt.links.new(brick.outputs["Factor"], mix.inputs[0])
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
    """Fine brushed streaks + panel seams on the folded steel plate."""
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
        mix = _color_mix(mat, (0.18, 0.19, 0.20), 0.0)
        nt.links.new(m.outputs["Value"], mix.inputs[0])
        brick = nt.nodes.new("ShaderNodeTexBrick")
        brick.inputs["Scale"].default_value = 2.0
        brick.inputs["Mortar Size"].default_value = 0.01
        brick.inputs["Brick Width"].default_value = 2.0
        brick.inputs["Row Height"].default_value = 1.0
        m2 = nt.nodes.new("ShaderNodeMath")
        m2.operation = 'MULTIPLY'
        m2.inputs[1].default_value = 0.85
        nt.links.new(brick.outputs["Factor"], m2.inputs[0])
        mix2 = _color_mix(mat, (0.10, 0.10, 0.11), 0.0)
        nt.links.new(m2.outputs["Value"], mix2.inputs[0])
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
MAT_CONCRETE_BOARD = mat_principled("MAT_Concrete_Board", (0.38, 0.37, 0.36), rough=0.9)
add_board_form(MAT_CONCRETE_BOARD)
add_big_blotch(MAT_CONCRETE, scale=1.5, strength=0.30)
add_big_blotch(MAT_CONCRETE_BOARD, scale=1.5, strength=0.30)
add_big_blotch(MAT_CONCRETE_DARK, scale=1.5, strength=0.25)
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
    return a >= 0 and b >= 0 and (1 - a - b) >= 0

print("=== 21_21 build: header/materials/helpers done ===")

# ================= SITE =================
def _in_atrium_rect(px, py):
    return 0.0 <= px <= 8.0 and -5.0 <= py <= 5.0

def ground_grid_with_holes(name, mat_top, mat_side, hole_tri, x_step=1.0, y_step=1.0):
    """Lawn slab built as a grid; any quad whose centre falls inside the atrium
    rect or hole_tri is SKIPPED — the openings are part of the construction.
    (The EXACT boolean on the site-ground box silently failed to open the
    court/atrium: down-rays still hit SM_Site_Ground at Z=-0.05 everywhere.)
    Top faces get mat_top (lawn); underside/sides get mat_side (concrete).
    """
    xs, ys = [], []
    x = -47.5
    while x <= 47.5:
        xs.append(x); x += x_step
    if xs[-1] < 47.5:
        xs.append(47.5)
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
            if _in_atrium_rect(cx, cy) or _point_in_tri(cx, cy, hole_tri):
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
COURT_TRI = [(10, -1), (20, -1), (15, 5)]
ground = ground_grid_with_holes("SM_Site_Ground", MAT_GRASS, MAT_CONCRETE_DARK, COURT_TRI)
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
        ("SM_Site_FarGround_East", (423.75, 0), (752.5, 65))]:
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
# Paved courtyard between the two wings (x -12..0) + forecourt south of museum
# #18: tops flush with the lawn (top -0.03, 2 cm above lawn top
# -0.05) — the old 9-11 cm proud edges read as white outline lines.
# One paving material; slabs no longer overlap in plan, so no stagger.
box("SM_Site_Courtyard", (-6, 0, -0.06), (14, 16, 0.06), MAT_PAVING, COL_SITE)
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
def roof_z_north(x):
    if x <= 22:
        return 8.5 + (7.2 - 8.5) * ((x + 2) / 24.0)
    return 7.2 + (0.8 - 7.2) * ((x - 22) / 20.0)

def roof_z_south(x):
    return 5.5 + (0.8 - 5.5) * ((x + 2) / 44.0)

def edge_y_north(x):
    return -7.0 if x <= 22 else -7.0 + 0.4 * (x - 22)

def edge_y_south(x):
    return 7.0 - 0.13636 * (x + 2)

def roof_sections(xs):
    secs = []
    for x in xs:
        yn, ys = edge_y_north(x), edge_y_south(x)
        zn, zs = roof_z_north(x), roof_z_south(x)
        zm = (zn + zs) / 2.0 + 0.06  # near-flat single folded plate (real roof reads as one plane)
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

def roof_z_at(x, y):
    """Roof surface height at plan point (x, y), same profile as roof_sections.
    Used by the G3 sloped ceiling and the atrium soffit so both sit below the
    roof instead of poking through it."""
    yn, ys = edge_y_north(x), edge_y_south(x)
    zn, zs = roof_z_north(x), roof_z_south(x)
    zm = (zn + zs) / 2.0 + 0.06
    f = (y - yn) / (ys - yn) if ys != yn else 0.0
    f = max(0.0, min(1.0, f))
    if f < 0.5:
        return zn + (zm - zn) * (f / 0.5)
    return zm + (zs - zm) * ((f - 0.5) / 0.5)

def roof_grid_with_hole(name, mat, coll, hole_tri, x_step=0.25, f_step=0.05):
    """Dense-grid roof built from the same profile as roof_sections, but any
    quad whose centre falls inside hole_tri is SKIPPED — the opening is part
    of the construction, not a boolean. (The EXACT boolean on the lofted +
    solidified roof silently failed: 9 large faces still covered the court.)
    """
    xs = []
    x = -2.0
    while x <= 42.0:
        xs.append(x)
        x += x_step
    if xs[-1] < 42.0:
        xs.append(42.0)
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
        zn, zs = roof_z_north(x), roof_z_south(x)
        zm = (zn + zs) / 2.0 + 0.06
        for fi, f in enumerate(fs):
            y = yn + (ys - yn) * f
            if f == 0.5:
                z = zm
            elif f < 0.5:
                z = zn + (zm - zn) * (f / 0.5)
            else:
                z = zm + (zs - zm) * ((f - 0.5) / 0.5)
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

def roof_seam_ribbon(name, y_north_fn, y_south_fn, z_north_fn, z_south_fn, ridge, x0, x1, f, coll, hole_tri=None):
    """Thin dark strip (0.12 m wide, 2 cm above the roof) along one roof fold
    line — geometry seams stay visible at any distance and never bake away."""
    xs = []
    x = x0
    while x <= x1 - 0.5:
        xs.append(x)
        x += 1.0
    xs.append(x1)
    verts, faces = [], []
    for xi in xs:
        yn, ys = y_north_fn(xi), y_south_fn(xi)
        zn, zs = z_north_fn(xi), z_south_fn(xi)
        zm = (zn + zs) / 2.0 + ridge
        y = yn + (ys - yn) * f
        if f == 0.5:
            z = zm
        elif f < 0.5:
            z = zn + (zm - zn) * (f / 0.5)
        else:
            z = zm + (zs - zm) * ((f - 0.5) / 0.5)
        verts.append((xi, y - 0.06, z + 0.02))
        verts.append((xi, y + 0.06, z + 0.02))
    for i in range(len(xs) - 1):
        if hole_tri is not None:
            cx = (xs[i] + xs[i + 1]) / 2.0
            cy = (verts[2 * i][1] + verts[2 * i + 1][1]) / 2.0
            if _point_in_tri(cx, cy, hole_tri):
                continue
        faces.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    return mesh_from_pydata(name, verts, faces, MAT_STEEL_SEAM, coll)

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

MUSEUM_XS = [-2, 6, 14, 22, 30, 37, 42]
roof_m = roof_grid_with_hole("SM_Museum_Roof", MAT_STEEL, COL_MUSEUM, COURT_TRI, x_step=0.125, f_step=0.025)
for _f, _tag in [(0.25, "Q1"), (0.5, "Ridge"), (0.75, "Q3")]:
    roof_seam_ribbon(f"SM_Museum_RoofSeam_{_tag}", edge_y_north, edge_y_south, roof_z_north, roof_z_south, 0.06, -2, 42, _f, COL_MUSEUM, hole_tri=COURT_TRI)
# v16 P2 item 6: smooth rim around the court roof opening (lighter steel
# flashing, so it reads as a distinct curb against the darker roof).
# v16r2: subdivided (12 segments/edge) so it hugs the sloped roof.
# Phase 3 (item 6, 3rd attempt — NEW diagnosis from probe_court_edge.py):
# the rim's outer band was BURIED under the roof. The roof grid's solidify
# (offset -1) extrudes toward the grid's DOWNWARD normals, so the real roof
# top sits at roof_z+0.18, while the rim top was at roof_z+0.08 — 0.10 m
# UNDER the roof surface (probe: down-rays hit SM_Museum_Roof@roof_z+0.18
# everywhere the rim should have been; the rim only showed in the inset
# band inside the roof hole). The roof's stepped cut edge therefore stayed
# fully exposed from above, and its vertical cut face from below. Fix:
# raise the rim to lift=0.30 (top 0.12 m proud of the real roof top) and
# deepen it to thick=0.90, so it stands as a vertical fascia/skirt whose
# outer face covers the roof's 0.18 m cut face from below/side as well as
# the steps from above. If the renders do not clearly improve, revert.
# Phase 3 try 2: widen the inset 0.50 -> 0.90 m. The raised fascia fixed
# the ROOF edge on all sides (probe_court_edge2: rim covers the roof edge
# continuously), but the ground-slab / lawn 1 m-grid teeth still protrude
# up to ~0.7 m past the rim's inner edge on the east/south sides and read
# as steps from above (one ray at (14.9,4.0) hit SM_Ground_Slab@0.02 just
# inside the old inner edge). 0.90 m covers the deepest 1 m-grid tooth
# (half-diagonal 0.71 m). If this does not clean up CAM_Court, revert the
# inset to 0.50 and keep the raised fascia only.
roof_opening_rim("SM_Court_Roof_Rim", COURT_TRI, MAT_STEEL_DARK, COL_MUSEUM,
                 inset=0.90, lift=0.30, thick=0.90)

# North (rear) concrete wall: ground + basement, top follows roof north edge
wall_varying("SM_Museum_Wall_North", (-2, -7), (22, -7), -4.8, 8.5, -4.8, 7.2,
             MAT_CONCRETE, COL_MUSEUM, thick=0.35)
wall_varying("SM_Museum_Wall_NorthEast", (22, -7), (42, 1), -4.8, 7.2, -4.8, 0.8,
             MAT_CONCRETE_DARK, COL_MUSEUM, thick=0.35)
# West entrance block — v16 P2 item 10: REAL doorway. The solid fin is
# rebuilt as segments around a 3.2 m doorway at y=0 (courtyard -> lobby
# axis). No boolean: the wall is built in pieces with a gap for the door.
# North segment y -7.5..-1.6, south segment y 1.6..7.5, lintel z 2.7..5.2
# over the doorway. Glass door + frames + canopy + sign kept as before.
box("SM_Museum_Entrance_Block_N", (-2.6, -4.55, 2.6), (1.2, 5.9, 5.2), MAT_CONCRETE, COL_MUSEUM)
box("SM_Museum_Entrance_Block_S", (-2.6, 4.55, 2.6), (1.2, 5.9, 5.2), MAT_CONCRETE, COL_MUSEUM)
box("SM_Museum_Entrance_Lintel", (-2.6, 0, 3.95), (1.2, 3.2, 2.5), MAT_CONCRETE, COL_MUSEUM)
box("SM_Museum_Entrance_Door", (-3.25, 0, 1.35), (0.15, 3.2, 2.7), MAT_GLASS, COL_MUSEUM)
# door frame + canopy line (v11: bare glass plate on a plain fin)
box("SM_Museum_Entrance_Frame_L", (-3.32, -1.68, 1.35), (0.12, 0.12, 2.7), MAT_BLACK, COL_MUSEUM)
box("SM_Museum_Entrance_Frame_R", (-3.32, 1.68, 1.35), (0.12, 0.12, 2.7), MAT_BLACK, COL_MUSEUM)
box("SM_Museum_Entrance_Frame_Top", (-3.32, 0, 2.76), (0.12, 3.5, 0.12), MAT_BLACK, COL_MUSEUM)
box("SM_Museum_Entrance_Canopy", (-3.65, 0, 2.98), (0.9, 4.2, 0.08), MAT_STEEL_DARK, COL_MUSEUM)
# 21_21 sign plate on the west block
box("SM_Museum_Sign", (-3.3, 5.2, 3.6), (0.12, 4.5, 0.9), MAT_BLACK, COL_MUSEUM)

# South glass facade (continuous glazing, top follows roof south edge)
south_edge = []
for x in MUSEUM_XS:
    south_edge.append((x, edge_y_south(x), roof_z_south(x)))
glass_strip("SM_Museum_Glass_South", south_edge, 0.0, MAT_GLASS, COL_MUSEUM)
# East tip glass gable (triangular, at the point)
glass_strip("SM_Museum_Glass_Tip",
            [(42, 1, 0.8), (37, edge_y_south(37), roof_z_south(37))], 0.0, MAT_GLASS, COL_MUSEUM)

# ================= CAFE WING (exterior) =================
# Footprint quad: A2(-34,-6) B2(-12,-6) C2(-10,0) D2(-34,6). Area ~210 m2.
# v17 (#17): folded plate — HIGH at both ends, valley near x=-20.
# Photos: tall glass at the west end AND at the east/entrance end, short
# glass mid-span (aerial crop + plan elevation strip, both read 2026-11-19).
# The v16 monotonic descent to 0.8 m at the east tip was wrong.
def _fold(x, x0, z0, xv, zv, x1, z1):
    if x <= xv:
        return z0 + (zv - z0) * ((x - x0) / (xv - x0))
    return zv + (z1 - zv) * ((x - xv) / (x1 - xv))

def cafe_z_north(x):
    return _fold(x, -34, 5.0, -20, 3.0, -10, 4.2)

def cafe_z_south(x):
    return _fold(x, -34, 3.5, -20, 1.2, -10, 3.5)

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
    """Cafe roof surface height at plan point (x, y) — same profile as
    cafe_sections. Used by the Gallery 3 sloped ceiling (v15: G3 is the
    cafe wing) so it sits below the roof instead of poking through it."""
    yn, ys = cafe_y_north(x), cafe_y_south(x)
    zn, zs = cafe_z_north(x), cafe_z_south(x)
    zm = (zn + zs) / 2.0 + 0.05
    f = (y - yn) / (ys - yn) if ys != yn else 0.0
    f = max(0.0, min(1.0, f))
    if f < 0.5:
        return zn + (zm - zn) * (f / 0.5)
    return zm + (zs - zm) * ((f - 0.5) / 0.5)

roof_c = loft("SM_Cafe_Roof", cafe_sections(CAFE_XS), MAT_STEEL, COL_CAFE)
for _f, _tag in [(0.25, "Q1"), (0.5, "Ridge"), (0.75, "Q3")]:
    roof_seam_ribbon(f"SM_Cafe_RoofSeam_{_tag}", cafe_y_north, cafe_y_south, cafe_z_north, cafe_z_south, 0.05, -34, -10, _f, COL_CAFE)
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
wall_varying("SM_Cafe_Wall_North_High", (-34, -6), (-20, -6), 2.2, 5.0, 2.2, 3.0,
             MAT_CONCRETE, COL_CAFE, thick=0.3)
wall_varying("SM_Cafe_Wall_North_High_E", (-20, -6), (-12, -6), 2.2, 3.0, 2.2, 4.2,
             MAT_CONCRETE, COL_CAFE, thick=0.3)
wall_varying("SM_Cafe_Wall_North_SlotW", (-34, -6), (-31, -6), 1.0, 2.2, 1.0, 2.2,
             MAT_CONCRETE, COL_CAFE, thick=0.3)
wall_varying("SM_Cafe_Wall_North_SlotE", (-19, -6), (-12, -6), 1.0, 2.2, 1.0, 2.2,
             MAT_CONCRETE, COL_CAFE, thick=0.3)
box("SM_G3_WindowSlot", (-28, -6, 1.6), (6.0, 0.12, 1.2), MAT_GLASS, COL_CAFE)
wall_varying("SM_Cafe_Wall_West", (-34, -6), (-34, 6), 0.0, 5.0, 0.0, 3.5,
             MAT_CONCRETE, COL_CAFE, thick=0.3)
# Cafe south glass + east entrance (faces museum)
cafe_south = [(x, cafe_y_south(x), cafe_z_south(x)) for x in CAFE_XS]
glass_strip("SM_Cafe_Glass_South", cafe_south, 0.0, MAT_GLASS, COL_CAFE)
box("SM_Cafe_Entrance_Door", (-9.9, 0, 1.3), (0.15, 3.0, 2.6), MAT_GLASS, COL_CAFE)
# ================= GALLERY 3 (v15: the cafe wing IS Gallery 3) =================
# Since 2017 the former cafe wing is Gallery 3 (official leasing-page plan +
# section, measured). Gallery quad: north wall (-33,-5.7)->(-18,-5.7) 15.0 m,
# east/entrance tip (-13.5,0.3), south vertex (-25,3.6); private room 4.0x2.9 m +
# kitchen at the east end under a 2.7 m flat ceiling; WCs by the entrance.
_MAT_GRANITE = mat_principled("MAT_Granite", (0.22, 0.22, 0.21), rough=0.35)
add_speckle(_MAT_GRANITE, scale=18.0, strength=0.22, dark=(0.14, 0.14, 0.13))
_MAT_G3_FROSTED = mat_principled("MAT_G3_Frosted", (0.95, 0.95, 0.88), rough=0.4,
                                 emission=(1.0, 0.98, 0.90), emission_strength=2.0)
_MAT_G3_COVE = mat_principled("MAT_G3_Cove", (1.0, 0.9, 0.7), rough=0.4,
                              emission=(1.0, 0.85, 0.6), emission_strength=2.0)
G3_QUAD = [(-33, -5.7), (-18, -5.7), (-13.5, 0.3), (-25, 3.6)]
# Luminous frosted-glass band (east half of the north-wall slot; the window
# glass is the west half, set with the wall above).
box("SM_G3_FrostedSlot", (-22, -6, 1.6), (6.0, 0.12, 1.2), _MAT_G3_FROSTED, COL_CAFE)
# West diagonal wall of the gallery (12.8 m in the official plan).
# v17 (#17): tops 4.9->4.7 (north) and 2.4->1.8 (south vertex) — the folded
# roof is lower along this diagonal (4.86 / 3.59 / 2.05 at t=0 / 0.5 / 1);
# the v16 tops would poke through it.
wall_varying("SM_G3_Wall_West", (-33, -5.7), (-25, 3.6), 0.0, 4.7, 0.0, 1.8,
             MAT_CONCRETE, COL_CAFE, thick=0.3)
# Private room (4.0x2.9 m, X -18..-14, Y -5.7..-2.8) + kitchen (X -14..-11.5).
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
box("SM_G3_WC_W", (-13.8, -1.5, 1.2), (0.06, 2.0, 2.4), MAT_WHITE, COL_CAFE)
# Gallery ceiling: v16 P2 item 11 — Section C profile (official G3
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
    return min(_z, cafe_z_at(x, y) - 0.30)
# Gallery columns (official plan: 2 square + 1 round at the south vertex).
# v16 P2 item 12: square columns at 30% and 55% of the 15.0 m north wall
# from the west vertex: x = -33 + 0.30*15 = -28.5 and -33 + 0.55*15 =
# -24.75. (The plan drawing is not uniformly to scale, so the parent's
# stated fractions are implemented literally.) Round column confirmed at
# the south vertex (-25, 3.6). Heights follow the new Section C ceiling.
for _ci, (_ccx, _ccy) in enumerate([(-28.5, -3.0), (-24.75, -0.5)]):
    _chh = g3_ceiling_z(_ccx, _ccy)
    box(f"SM_G3_Column_{_ci}", (_ccx, _ccy, _chh / 2.0), (0.45, 0.45, _chh), MAT_CONCRETE_BOARD, COL_CAFE)
_chr = g3_ceiling_z(-25, 3.6)
bpy.ops.mesh.primitive_cylinder_add(radius=0.30, depth=_chr, location=(-25, 3.6, _chr / 2.0))
_o = bpy.context.active_object
_o.name = "SM_G3_Column_Round"
set_mat(_o, MAT_CONCRETE_BOARD); link(_o, COL_CAFE)
# Gallery ceiling grid (white gypsum); quads below 0.35 m (at the south
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
solidify(_g3_o, 0.08)
# Granite floor over the gallery quad (dark grey tiles, as photographed).
flat_poly_slab("SM_G3_Floor_Granite", G3_QUAD, 0.06, 0.06, _MAT_GRANITE, COL_CAFE)
# v17 (#17): flat 2.7 m ceiling over the WC / entrance strip
# (x -14..-11, y -2.0..-0.5) — the sloped ceiling is skipped there (see
# above) and the roof above it is 2.85-3.72 m, so 2.7 m clears everywhere.
flat_poly_slab("SM_G3_Entrance_Ceiling", [(-14, -2.0), (-11, -2.0), (-11, -0.5), (-14, -0.5)],
               2.7, 0.05, MAT_WHITE, COL_CAFE)
# Triangular folded reception desks (the triangle echoes the roof fold),
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
box("SM_G3_CoveStrip", (-30.5, -5.55, 3.70), (5.0, 0.08, 0.08), _MAT_G3_COVE, COL_CAFE)
# Recessed downlights just below the sloped ceiling (8, positions from the
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
    set_mat(_o, MAT_BLACK); link(_o, COL_CAFE)
# Terrace paving south of the gallery glass (57 m2 in the official plan,
# outline approximate).
flat_poly_slab("SM_G3_Terrace", [(-25, 3.6), (-13.5, 0.3), (-13.5, 4.8), (-25, 8.1)],
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

# ================= INTERIOR (museum wing) =================
# Footprint quad A(-2,-7) B(22,-7) C(42,1) D(-2,7)
FOOT = [(-2, -7), (22, -7), (42, 1), (-2, 7)]

def flat_slab(name, z, thick, mat, coll):
    """Flat slab over the museum footprint at height z (top), solidified down."""
    A, B, C, D = FOOT
    verts = [(A[0], A[1], z), (B[0], B[1], z), (C[0], C[1], z), (D[0], D[1], z)]
    faces = [(0, 1, 2), (0, 2, 3)]
    o = mesh_from_pydata(name, verts, faces, mat, coll)
    solidify(o, thick)
    return o

def footprint_grid_slab(name, quad, z, thick, mat, coll, skip_rect=None):
    """Ground-floor slab over a convex quad footprint, built as a 1 m grid with
    the atrium void + sunken court skipped at construction (never boolean:
    EXACT boolean on the 2-triangle flat_slab silently collapsed it to a
    10-vert court-triangle remnant, leaving the whole ground floor as lawn).
    skip_rect=(x0, x1, y0, y1) replaces the atrium-rect skip: only cells
    whose centre falls in the rect are left open. None = old behaviour."""
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
            if skip_rect is not None:
                if skip_rect[0] <= cx <= skip_rect[1] and skip_rect[2] <= cy <= skip_rect[3]:
                    continue
            elif _in_atrium_rect(cx, cy):
                continue
            if _point_in_tri(cx, cy, COURT_TRI):
                continue
            faces.append((a, b, c, d))
    o = mesh_from_pydata(name, verts, faces, mat, coll)
    solidify(o, thick)
    return o

# Basement floor (Z=-4.8) — light concrete like the real Gallery 2 floor.
# v16 P2 TOP PRIORITY (Leon 2026-11-17: the underground space was too small
# AND laid out wrong): the basement is BIGGER and re-laid out per the
# official BF plan. v15 was 816 m2 with G1 as a north strip / G2 as a south
# hall. Official numbers: total floor 1,932 m2 - building area 597.3 m2 =
# 1,334.7 m2 basement. New outline 1,336 m2. G1 = 129 m2 trapezoid (WEST,
# far wall = the diagonal museum wall, (22,-7)->(37,-1)); G2 = 448 m2
# rectangle (EAST, x 24..52, y -1..15). The 1.75x ratio in the v15 record
# came from a schematic that is not to scale (measured BF/1F-museum = 1.82
# in plan_big.png, but the two plans are drawn at different scales);
# 1,045 m2 (= 1.75 x 597.3) leaves ~290 m2 of the official 1,932 m2
# unaccounted for, so it is rejected. Court + atrium + stair/elevator core
# stay: court between G1/G2, north of G2's centre; core at the west end;
# atrium connects them (BF plan + Architectural Record: G1 is the trapezoid,
# G2 the rectangle; the void is two adjacent triangles, atrium + court).
# Exact outline path is inferred (the BF plan is schematic); the area is
# the constraint. G1 129 m2 (-3% vs 133) and G2 448 m2 (+1% vs 443) are
# within the schematic's tolerance.
BASEMENT_POLY = [(-10, -7), (22, -7), (52, -1), (52, 16), (-10, 16)]
# G1 polygon (trapezoid, WEST): north edge y=-7, far wall = diagonal museum
# wall (22,-7)->(37,-1), south edge y=-1, west edge x=8. Area 129 m2.
G1_POLY = [(8, -7), (22, -7), (37, -1), (8, -1)]
# G2 rectangle (EAST): x 24..52, y -1..15. Area 448 m2.
G2_RECT = (24, 52, -1, 15)
basement_floor = flat_poly_slab("SM_Basement_Floor", BASEMENT_POLY, -4.8, 0.2,
    mat_principled("MAT_Floor_Concrete", (0.72, 0.71, 0.69), rough=0.85), COL_INTER)
# Ground-floor slab over the museum footprint (top z=0.02, just above the
# lawn at -0.05 so it never Z-fights; atrium + court skipped at construction)
# v17 (#17): the atrium void is floored over — only the 30-step stairwell
# stays open (stair x 0..8.1, y -5..-3, balustrade at y=-3.0; the rect stops
# 0.1 m south of the balustrade). Leon confirmed the real lobby has floor
# here. The sunken-court opening (COURT_TRI) is untouched.
ground_slab = footprint_grid_slab("SM_Ground_Slab", FOOT, 0.02, 0.3, MAT_CONCRETE, COL_INTER,
                                  skip_rect=(0.0, 8.0, -5.0, -2.9))
# Cafe ground-floor slab (same construction; cafe quad A2/B2/C2/D2 from above)
CAFE_FOOT = [(-34, -6), (-12, -6), (-10, 0), (-34, 6)]
cafe_slab = footprint_grid_slab("SM_Cafe_Slab", CAFE_FOOT, 0.02, 0.3, MAT_CONCRETE, COL_INTER)

# Basement perimeter walls (below ground, Z -4.8..0) — v16 outline (see above).
# Gallery walls are WHITE (ref_gallery1/2.jpg: exhibition walls read white;
# concrete is reserved for the atrium/court/columns). The new walls are fully
# underground, so their outer faces are never seen.
wall_varying("SM_Basement_Wall_South", (-10, 16), (52, 16), -4.8, -0.10, -4.8, -0.10,  # #18: tops were 0.0; -0.10 is below lawn (-0.05) AND far ground (-0.07/-0.08)
             MAT_WHITE, COL_INTER, thick=0.35)
wall_varying("SM_Basement_Wall_West", (-10, -7), (-10, 16), -4.8, -0.10, -4.8, -0.10,  # #18: tops were 0.0; -0.10 is below lawn (-0.05) AND far ground (-0.07/-0.08)
             MAT_CONCRETE, COL_INTER, thick=0.35)
# North wall west extension (the basement runs 8 m west of the ground floor)
wall_varying("SM_Basement_Wall_North_West", (-10, -7), (-2, -7), -4.8, -0.10, -4.8, -0.10,  # #18: tops were 0.0; -0.10 is below lawn (-0.05) AND far ground (-0.07/-0.08)
             MAT_CONCRETE, COL_INTER, thick=0.35)
# North-east diagonal wall (follows the ground footprint edge, extended east)
wall_varying("SM_Basement_Wall_NorthEast", (22, -7), (52, -1), -4.8, -0.10, -4.8, -0.10,  # #18: tops were 0.0; -0.10 is below lawn (-0.05) AND far ground (-0.07/-0.08)
             MAT_WHITE, COL_INTER, thick=0.35)
# East wall of the (eastern) Gallery 2
wall_varying("SM_Basement_Wall_East", (52, -1), (52, 16), -4.8, -0.10, -4.8, -0.10,  # #18: tops were 0.0; -0.10 is below lawn (-0.05) AND far ground (-0.07/-0.08)
             MAT_WHITE, COL_INTER, thick=0.35)
# G2 ceiling: flat board-formed panels over the whole eastern gallery
# (most of G2 lies beyond the ground footprint, under the lawn), z=-0.38,
# just below the ground-slab underside (-0.28) so the ceiling reads flat.
# Two panels leave a 0.70 m gap for the skylight slot (Y 1.45..2.15),
# which sits recessed at z=-0.10 and reads as a real skylight well.
box("SM_G2_Ceiling_N", (38, 0.225, -0.38), (28.0, 2.45, 0.06), MAT_CONCRETE_BOARD, COL_INTER)
box("SM_G2_Ceiling_S", (38, 8.575, -0.38), (28.0, 12.85, 0.06), MAT_CONCRETE_BOARD, COL_INTER)
# G1 north wall lining: white plaster on the inside face of the concrete
# north wall (the wall itself must stay concrete above ground).
box("SM_G1_WallNorth_Lining", (15, -6.79, -2.4), (14.0, 0.06, 4.8), MAT_WHITE, COL_INTER)
# v16: white plaster lining on the G1 side of the diagonal (NE) wall below
# the skylight panels (ref_gallery1.jpg: ALL G1 walls white; v15 showed the
# bare MAT_Concrete_Dark wall face, gray + mottled, below the panels).
# v16 P2 REGRESSION (found 2026-11-17 in v16_verify_CAM_Gallery1/G1FarWall):
# the lining was BURIED inside the wall and invisible. Cause: the 0.22 m
# offset was measured from the OUTER face line (22.06,-7.16)->(42.06,0.84),
# which is the wall's NE face (s=-0.175 from the centreline), so the lining
# centre landed at s=+0.045 — inside the 0.35 m wall (faces s=+/-0.175).
# Phase 3 fix: centre at s=+0.197 from the centreline (front face s=+0.227,
# 0.052 m proud of the inner wall face, flush with the square window's back
# face), t centred on G1's far-wall segment (22,-7)->(37,-1), length 16.2 m
# (was 16.7 m, which overshot 0.53 m into G2's NW corner). Top z=-1.2 meets
# the skylight panels. Window NOT moved (it sits correctly on the lining).
box("SM_G1_WallDiagonal_Lining", (29.43, -3.82, -3.0), (16.2, 0.06, 3.6),
    MAT_WHITE, COL_INTER, rot=(0, 0, math.radians(21.79)))

# ---- Openings: atrium void (rect X 0..8, Y -5..+5) + sunken court (triangle) ----
# Both openings are skipped at construction time inside footprint_grid_slab
# (and ground_grid_with_holes / roof_grid_with_hole for site + roof).
# The EXACT boolean used here before silently collapsed the 2-triangle
# ground slab to a 10-vert remnant (2026-11-16 probe), so no boolean is
# applied to any slab anymore; boolean_cut() is kept unused for reference.

# ---- Atrium walls (the canyon): tall concrete, double height ----
def tie_holes(name, axis, fixed, u_range, v_range, step=1.2):
    """Small dark tie-hole discs on a wall face (board-formed concrete grid).
    axis 'x': face plane YZ at x=fixed; axis 'y': face plane XZ at y=fixed.
    u/v are the two in-plane coordinates."""
    n = 0
    u = u_range[0]
    while u <= u_range[1] + 1e-6:
        v = v_range[0]
        while v <= v_range[1] + 1e-6:
            if axis == 'x':
                loc = (fixed, u, v); rot = (0, math.radians(90), 0)
            else:
                loc = (u, fixed, v); rot = (math.radians(90), 0, 0)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.04, location=loc, rotation=rot)
            o = bpy.context.active_object
            o.name = f"{name}_{n:02d}"
            set_mat(o, MAT_TIEHOLE); link(o, COL_INTER)
            n += 1
            v += step
        u += step
    return n

# Atrium east wall (x=8): solid board-formed concrete on the north stretch
# (behind the stair, Y -5..-1); full-height glass on the court stretch
# (Y -1..5 — the real atrium overlooks the sunken court through tall glazing).
# v16 P2: the north stretch is now two segments with a 1.4 m doorway at
# Y -3.4..-2.0 — the stair landing steps straight into G1 (the one-stroke
# circulation: stair -> G1 -> G2 -> court -> atrium). G1's west wall north
# of the stair (Y -7..-5) is a separate white segment below.
wall_varying("SM_Atrium_Wall_East_A", (8, -5), (8, -3.4), -4.8, 0.0, -4.8, 0.0,
             MAT_CONCRETE_BOARD, COL_INTER, thick=0.3)
wall_varying("SM_Atrium_Wall_East_B", (8, -2.0), (8, -1), -4.8, 0.0, -4.8, 0.0,
             MAT_CONCRETE_BOARD, COL_INTER, thick=0.3)
wall_varying("SM_G1_Wall_West_North", (8, -7), (8, -5), -4.8, 0.0, -4.8, 0.0,
             MAT_WHITE, COL_INTER, thick=0.2)
glass_strip("SM_Atrium_Glass_East", [(8, -1, 0.0), (8, 5, 0.0)], -4.8,
            MAT_GLASS, COL_INTER, mullion_every=0.9)
# Tie-hole grid on the solid stretch's atrium-side face (x=7.85), north of
# the doorway only (the old range crossed the new doorway gap).
tie_holes("SM_Atrium_TieHole", 'x', 7.84, (-4.8, -3.6), (-4.2, -0.6))
# Tie-hole grid on the atrium north wall face (y=-6.825), visible above the stair
tie_holes("SM_Atrium_North_TieHole", 'y', -6.83, (0.8, 7.2), (-4.2, -0.6))
# Atrium north wall is the basement north wall (already there).
# ---- Sunken court walls (triangular pit, concrete + glass to Gallery 2) ----
# Court edges: (10,-1)-(20,-1) north edge (concrete), (20,-1)-(15,5) east (glass),
# (15,5)-(10,-1) west (concrete). Walls from basement floor up to ground.
wall_varying("SM_Court_Wall_North", (10, -1), (20, -1), -4.8, 0.0, -4.8, 0.0,
             MAT_CONCRETE, COL_INTER, thick=0.25)
wall_varying("SM_Court_Wall_West", (15, 5), (10, -1), -4.8, 0.0, -4.8, 0.0,
             MAT_CONCRETE, COL_INTER, thick=0.25)
# Glass wall on the court east edge (facing Gallery 2), full height to ground
wall_varying("SM_Court_Glass_East", (20, -1), (15, 5), -4.8, 0.0, -4.8, 0.0,
             MAT_GLASS, COL_INTER, thick=0.12)
# v15: dense mullions on the court glass (visitor night photo: tight verticals)
for _mx in [19.0, 18.0, 17.0, 16.0]:
    _my = -1.0 + (20.0 - _mx) * 6.0 / 5.0 if _mx < 20 else -1.0
    box(f"SM_Court_Glass_Mullion_{int(_mx)}", (_mx, _my, -2.4), (0.06, 0.06, 4.8), MAT_BLACK, COL_INTER)
# v15: horizontal slit window in the court north wall (glows in the night
# photo — G1 borrows light from the court through it). Emissive band on the
# wall's court-side face (y=-0.86).
box("SM_Court_SlitWindow", (15, -0.86, -2.05), (6.0, 0.06, 0.30),
    mat_principled("MAT_Court_Slit", (1.0, 0.96, 0.88), rough=0.4,
                   emission=(1.0, 0.95, 0.85), emission_strength=2.5), COL_INTER)
# Court floor planting + a small tree at the bottom
box("SM_Court_Planter", (15, 1.5, -4.7), (6.0, 3.5, 0.2), MAT_GRASS, COL_INTER)
# v16 P2 item 7: the court tree is planted on the PIT floor (z0=-4.8), not
# at ground level — the old z0=0 put its canopy through the roof opening
# into the entrance hall, reading as an interior lobby tree in a planter.
cedar(15, 1.5, h=3.8, r=0.9, z0=-4.8)

# ---- Interior partitions (basement) ----
# v16 P2: G1 (WEST) / G2 (EAST) are side by side, so P1 runs along Y=-1
# (G1's south edge = G2's north edge), X 8..52. The court pit (X 10..20)
# interrupts it — no wall across the open pit (the court's own north wall
# is there) — and a 3 m doorway gap at X 28..31 connects G1 to G2.
wall_varying("SM_Part_G1G2_A", (8, -1), (10, -1), -4.8, 0.0, -4.8, 0.0,
             MAT_WHITE, COL_INTER, thick=0.2)
wall_varying("SM_Part_G1G2_B", (20, -1), (28, -1), -4.8, 0.0, -4.8, 0.0,
             MAT_WHITE, COL_INTER, thick=0.2)
wall_varying("SM_Part_G1G2_C", (31, -1), (52, -1), -4.8, -0.10, -4.8, -0.10,  # #20: top was 0.0; its 21x0.2 m white cap poked 5 cm above the lawn east of x~42 (roof ends there) and read as the white line in aerial + exterior views (raycast-proven). -0.10 sits inside the ground slab (x<42) / lawn slab (x>42).
             MAT_WHITE, COL_INTER, thick=0.2)
# P2: the atrium/G1 wall is the atrium east wall itself (x=8, rebuilt above
# with the stair-landing doorway at Y -3.4..-2.0); no separate x=12 wall —
# the stair lands straight into G1 (the one-stroke circulation:
# stair -> G1 -> G2 -> court -> atrium).
# P3: full-height glass wall between atrium and sunken court along X=10
# (real atrium overlooks the court through tall glazing); doorway gap Y 1..3
# stays open for circulation.
glass_strip("SM_Part_Atrium_G2_Glass_A", [(10, -1, 0.0), (10, 1, 0.0)], -4.8,
            MAT_GLASS, COL_INTER, mullion_every=0.9)
glass_strip("SM_Part_Atrium_G2_Glass_B", [(10, 3, 0.0), (10, 5, 0.0)], -4.8,
            MAT_GLASS, COL_INTER, mullion_every=0.9)
# ---- Gallery 2 columns (row along north edge Y=1.8) ----
# v16 P2: G2 is the EASTERN rectangle (x 24..52, y -1..15). 7 columns,
# 0.55 m square (ref_gallery2.jpg: the row reads chunkier than 0.45),
# spacing 4 m, X 26..50 (inference: the photo shows 6 clearly).
for i, cx in enumerate([26, 30, 34, 38, 42, 46, 50]):
    box(f"SM_G2_Column_{i}", (cx, 1.8, -2.4), (0.55, 0.55, 4.8), MAT_CONCRETE_BOARD, COL_INTER)
    tie_holes(f"SM_G2_Column_TieHole_{i}", 'y', 2.08, (cx, cx), (-4.2, -0.6))
# v15: the real G2 skylight — one continuous bright slot running the full
# length of the hall just above the column line (ref_gallery2.jpg), NOT the
# small strip that used to sit mid-room. Emissive band set into the ceiling.
MAT_SKYLIGHT = mat_principled("MAT_Skylight", (1.0, 1.0, 0.95), rough=0.4,
                              emission=(1, 1, 0.9), emission_strength=2.5)
# v16 P2: slot runs the eastern hall's length (x 24..52) above the column
# line (y=1.8), recessed at z=-0.10 in the gap between the two ceiling
# panels (Y 1.45..2.15) so it reads as a real skylight well.
box("SM_G2_Skylight_Slot", (38, 1.8, -0.10), (28.0, 0.70, 0.10), MAT_SKYLIGHT, COL_INTER)
# v15: rows of linear fluorescent tubes on the exposed-concrete G2 ceiling
# (ref_gallery2.jpg: several parallel tube runs the length of the hall).
for _ri, _ry in enumerate([4.0, 7.0, 10.0, 13.0]):
    box(f"SM_G2_Fluorescent_{_ri}", (38, _ry, -0.45), (26.0, 0.12, 0.06), MAT_SKYLIGHT, COL_INTER)
# v16 P2 item 16: dark doorway in the far (east) wall, north/left side
# (ref_gallery2.jpg: a dark opening at the far end, left side). v16r2:
# moved to y=1.5 — the first position (y=1.0) still grazed the diagonal
# wall's east tip from the standard Gallery2 camera (the ray to the door
# centre hit SM_Museum_Wall_NorthEast 1 mm from the wall face); y=1.5
# clears the tip by ~0.27 m. Still the north end of the east wall
# (2.5 m south of the north wall y=-1). Matte near-black so it reads as
# a dark opening, not a reflective panel.
MAT_DARK_DOOR = mat_principled("MAT_Dark_Door", (0.02, 0.02, 0.02), metallic=0.0, rough=0.95)
box("SM_G2_East_Door", (51.85, 1.5, -3.6), (0.3, 1.2, 2.4), MAT_DARK_DOOR, COL_INTER)

# ---- Floating concrete stair (atrium north side, Y -5..-3, X 0..8.1) ----
# v15: the real stair is a normal staircase, not a steep 16-step ladder:
# 30 steps x 0.16 m riser = 4.8 m rise, 0.27 m tread, 2.0 m wide, one
# straight flight descending east (top at the hall, bottom at the basement).
# North side: solid concrete parapet + steel handrail (visitor photos);
# south side: sloped glass balustrade; smooth sloped soffit underneath so
# the hallway under the stair reads as a real passage.
NSTEPS = 30
_STAIR_X0, _STAIR_TREAD, _STAIR_RISER = 0.0, 0.27, 0.16
for i in range(NSTEPS):
    sx = _STAIR_X0 + i * _STAIR_TREAD + _STAIR_TREAD / 2.0
    sz = -0.08 - i * _STAIR_RISER - _STAIR_RISER / 2.0
    box(f"SM_Stair_Step_{i:02d}", (sx, -4.0, sz), (_STAIR_TREAD, 2.0, _STAIR_RISER), MAT_CONCRETE_BOARD, COL_INTER)
# Sloped soffit slab under the steps: top face parallel to the nosing line,
# ~0.25 m below it (the stair waist), so it never pokes through a step; the
# east tip disappears under the basement floor.
_soff_len = math.hypot(NSTEPS * _STAIR_TREAD, NSTEPS * _STAIR_RISER)
_soff_ang = math.atan2(NSTEPS * _STAIR_RISER, NSTEPS * _STAIR_TREAD)
box("SM_Stair_Soffit", (NSTEPS * _STAIR_TREAD / 2.0, -4.0, -2.80),
    (_soff_len, 2.0, 0.15), MAT_CONCRETE_BOARD, COL_INTER, rot=(0, _soff_ang, 0))
# North parapet: solid concrete upstand following the step profile, 1.0 m
# above the nosings. Vertices: A/B bottom-west, C/D bottom-east (on the
# nosing line), E/F top-west, G/H top-east (+1.0 m).
_par_verts = [
    (0.0, -5.0, -0.08), (0.0, -4.92, -0.08),          # A, B
    (8.1, -5.0, -4.88), (8.1, -4.92, -4.88),          # C, D
    (0.0, -5.0, 0.92), (0.0, -4.92, 0.92),            # E, F
    (8.1, -5.0, -3.88), (8.1, -4.92, -3.88),          # G, H
]
_par_faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 2, 6, 4), (1, 5, 7, 3),
              (0, 4, 5, 1), (2, 3, 7, 6)]
mesh_from_pydata("SM_Stair_Parapet", _par_verts, _par_faces, MAT_CONCRETE_BOARD, COL_INTER)
# Steel handrail on the parapet (thin sloped tube, on the parapet top line)
box("SM_Stair_Handrail", (NSTEPS * _STAIR_TREAD / 2.0, -4.96, -1.43),
    (_soff_len, 0.05, 0.05), MAT_BLACK, COL_INTER, rot=(0, _soff_ang, 0))
# Sloped glass balustrade along the stair (open edge Y=-3.0): bottom edge
# follows the stair stringer, top edge 1.0 m above the nosings.
wall_varying("SM_Stair_Balustrade", (0.0, -3.0), (8.1, -3.0), -0.3, 0.92, -4.9, -3.88,
             MAT_GLASS, COL_INTER, thick=0.08)
# Stair landing at basement
box("SM_Stair_Landing", (8.8, -4.0, -4.65), (1.6, 2.0, 0.3), MAT_CONCRETE_BOARD, COL_INTER)
# Atrium ceiling: concrete soffit following the roof 0.15 m below it, over the
# atrium void (X 0..8, Y -5..5). The ceiling seen from the atrium was the bare
# steel roof underside; the real atrium reads as concrete, not steel or grass.
_soff_v, _soff_f, _soff_idx = [], [], {}
_soff_xs = [0.0 + 0.5 * i for i in range(17)]
_soff_ys = [-5.0 + 0.5 * i for i in range(21)]
for _xi, _x in enumerate(_soff_xs):
    for _yi, _y in enumerate(_soff_ys):
        _soff_idx[(_xi, _yi)] = len(_soff_v)
        _soff_v.append((_x, _y, roof_z_at(_x, _y) - 0.15))
for _xi in range(len(_soff_xs) - 1):
    for _yi in range(len(_soff_ys) - 1):
        _a = _soff_idx[(_xi, _yi)]; _b = _soff_idx[(_xi + 1, _yi)]
        _c = _soff_idx[(_xi + 1, _yi + 1)]; _d = _soff_idx[(_xi, _yi + 1)]
        _soff_f.append((_a, _b, _c, _d))
_soff_o = mesh_from_pydata("SM_Atrium_Soffit", _soff_v, _soff_f, MAT_CONCRETE, COL_INTER)
solidify(_soff_o, 0.08)

# ---- Trapezoidal elevator shaft (Japan's only trapezoidal elevator) ----
# v15: moved out of the canyon's sightline to the atrium's south-west corner,
# next to the stair top and the reception desk; plan is a real trapezoid
# (wide 2.4 m on the hall side, narrow 1.6 m on the east side — exact
# dimensions are inference, the trapezoid itself is documented). Concrete
# shaft, dark steel door facing the hall (west), car inside at basement level.
_ELEV_PLAN = [(-0.4, 2.4), (2.0, 2.8), (2.0, 4.4), (-0.4, 4.8)]
_elev_v = [(x, y, -4.8) for (x, y) in _ELEV_PLAN] + [(x, y, 0.0) for (x, y) in _ELEV_PLAN]
_elev_f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
mesh_from_pydata("SM_Elevator_Shaft", _elev_v, _elev_f, MAT_CONCRETE, COL_INTER)
box("SM_Elevator_Door", (-0.44, 3.6, 1.2), (0.08, 1.2, 2.4), MAT_STEEL_DARK, COL_INTER)
box("SM_Elevator_Door_Basement", (-0.44, 3.6, -3.6), (0.08, 1.2, 2.4), MAT_STEEL_DARK, COL_INTER)
box("SM_Elevator_Car", (0.8, 3.6, -3.7), (1.6, 1.4, 2.2), MAT_STEEL_DARK, COL_INTER)

# ---- Atrium furnishings (real atrium: curved wooden bookshelf under the stair,
# wooden benches by the floor-to-ceiling windows, long slit window, warm
# ceiling light strip) ----
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
# Curved bookshelf under the stair: arc centred (4.5,-1.0) r=3.2, angles 235..285 deg
_book_rng = random.Random(7)
for _si, _ang in enumerate([235, 247.5, 260, 272.5, 285]):
    _a = math.radians(_ang)
    _cx = 4.5 + 3.2 * math.cos(_a)
    _cy = -1.0 + 3.2 * math.sin(_a)
    _rot = _a + math.pi / 2.0
    box(f"SM_Atrium_Shelf_Base_{_si}", (_cx, _cy, -4.74), (0.95, 0.35, 0.12), MAT_WOOD_SHELF, COL_INTER, rot=(0, 0, _rot))
    for _li, _lz in enumerate([-4.45, -3.98]):
        box(f"SM_Atrium_Shelf_Board_{_si}_{_li}", (_cx, _cy, _lz), (0.95, 0.35, 0.05), MAT_WOOD_SHELF, COL_INTER, rot=(0, 0, _rot))
        for _bi in range(3):
            _s = -0.28 + _bi * 0.28
            _bx = _cx + _s * math.cos(_rot)
            _by = _cy + _s * math.sin(_rot)
            _bh = _book_rng.uniform(0.18, 0.28)
            _bm = MAT_BOOKS[_book_rng.randrange(len(MAT_BOOKS))]
            box(f"SM_Atrium_Shelf_Book_{_si}_{_li}_{_bi}", (_bx, _by, _lz + 0.025 + _bh / 2),
                (0.16, 0.22, _bh), _bm, COL_INTER, rot=(0, 0, _rot + _book_rng.uniform(-0.06, 0.06)))
# v16: wooden benches by the floor-to-ceiling east glass (visitor photo:
# "three men seated on wooden benches by floor-to-ceiling windows").
# Replaces the v11/v15 round stools at the north wall. Simple: light-wood
# seat slab + two light-wood slab legs, 2.0 m long, 0.45 m seat height.
def _wood_bench(_name, _x, _y):
    box(f"{_name}_Seat", (_x, _y, -4.8 + 0.42), (0.55, 2.0, 0.07), MAT_WOOD_LIGHT, COL_INTER)
    for _ly in (_y - 0.85, _y + 0.85):
        box(f"{_name}_Leg_{_ly}", (_x, _ly, -4.8 + 0.20), (0.5, 0.06, 0.40), MAT_WOOD_LIGHT, COL_INTER)
for _bi, (_bx, _by) in enumerate([(7.2, 0.5), (7.2, 3.0)]):
    _wood_bench(f"SM_Atrium_Bench_{_bi}", _bx, _by)
for _ti, (_tx, _ty) in enumerate([(2.0, -5.5), (6.0, -5.5)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.05, location=(_tx, _ty, -4.8 + 0.55))
    _t = bpy.context.active_object
    _t.name = f"SM_Atrium_Table_{_ti}_Top"
    set_mat(_t, MAT_WOOD_LIGHT); link(_t, COL_INTER)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.52, location=(_tx, _ty, -4.8 + 0.28))
    _tl = bpy.context.active_object
    _tl.name = f"SM_Atrium_Table_{_ti}_Leg"
    set_mat(_tl, MAT_BLACK); link(_tl, COL_INTER)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.04, location=(_tx, _ty, -4.8 + 0.02))
    _tb = bpy.context.active_object
    _tb.name = f"SM_Atrium_Table_{_ti}_Base"
    set_mat(_tb, MAT_BLACK); link(_tb, COL_INTER)
# Long narrow slit window high on the atrium north wall (v15: was at z=-0.8,
# below ground — the visitor photos show it above the stair / high on the
# entrance-hall wall, with greenery visible through it).
box("SM_Atrium_SlitWindow", (4, -6.80, 2.2), (6.0, 0.06, 0.30), MAT_SLIT, COL_INTER)
# Warm recessed-look light strip under the sloped atrium soffit (tilted to follow it)
box("SM_Atrium_WarmStrip", (4, 0, 6.28), (5.0, 0.25, 0.06), MAT_WARM_STRIP, COL_INTER, rot=(0, 0.122, 0))

# ---- Ground floor: entrance hall (reception + shop) ----
# v15: Gallery 3 is NOT here — it is the west (cafe) wing (see the cafe
# section below). The museum ground floor is the entrance hall: reception
# and shop either side of the route to the stair. The old reception desk
# stood at (2,-2), floating over the atrium void (no slab under it); it now
# sits on solid slab on the hall's south strip.
box("SM_Reception_Desk", (0.5, 5.8, 0.55), (3.2, 1.0, 1.1), MAT_WHITE, COL_INTER)
box("SM_Reception_Desk_Top", (0.5, 5.8, 1.12), (3.3, 1.1, 0.06), MAT_WOOD, COL_INTER)
box("SM_Shop_Counter", (4, 5.5, 0.5), (3.0, 0.9, 1.0), MAT_WOOD, COL_INTER)
# v15: entrance-hall columns — a row of square concrete columns just inside
# the south glass, ceiling sloping down over them (visitor photo). Heights
# follow the roof profile at each column.
for _cx, _cy in [(10, 5.0), (16, 4.2), (22, 3.4)]:
    _ch = max(2.5, roof_z_at(_cx, _cy) - 0.10)
    box(f"SM_Hall_Column_{_cx}", (_cx, _cy, _ch / 2.0), (0.45, 0.45, _ch), MAT_CONCRETE_BOARD, COL_INTER)

# Gallery 1 skylight (v15): the real G1 feature is a row of sloped translucent
# panels at the top of the far (diagonal) wall, washing it with indirect
# light from above (ref_gallery1.jpg) — not flat strips on the ceiling.
# 6 panels leaning 35 deg back from the wall top (z -1.2) up into the room
# (z -0.1); emissive, so they read as daylight slots.
# v15r5: the panels MUST sit on the diagonal wall's ACTUAL southwest face —
# the wall wedge SM_Museum_Wall_NorthEast runs (22.06,-7.16)->(42.06,0.84),
# NOT the (22,-7)->(46,-1) polygon diagonal the panels first used, so they
# ended up 0.9 m north of the wall face, hidden inside the building (every
# probe ray to a panel centre hit the wall). Panels now follow the wall face.
_G1_WALL_A = (22.06, -7.16)   # wall face, west end
_G1_WALL_B = (42.06, 0.84)    # wall face, east end
_G1_WALL_D = (0.928, 0.371)   # wall face direction (unit)
_G1_WALL_N = (-0.371, 0.928)  # inward normal (into G1)
# v16 P2: G1 is the WEST trapezoid; its far wall is the diagonal segment
# (22,-7)->(37,-1) (16.7 m). 6 panels spread along it (t=0.08..0.68).
for _pi, _t in enumerate([0.08, 0.20, 0.32, 0.44, 0.56, 0.68]):
    _cx, _cy = _G1_WALL_A[0] + 20.0 * _t, _G1_WALL_A[1] + 8.0 * _t
    _b1 = (_cx - 1.1 * _G1_WALL_D[0], _cy - 1.1 * _G1_WALL_D[1], -1.2)
    _b2 = (_cx + 1.1 * _G1_WALL_D[0], _cy + 1.1 * _G1_WALL_D[1], -1.2)
    _t2 = (_b2[0] + 0.7 * _G1_WALL_N[0], _b2[1] + 0.7 * _G1_WALL_N[1], -0.1)
    _t1 = (_b1[0] + 0.7 * _G1_WALL_N[0], _b1[1] + 0.7 * _G1_WALL_N[1], -0.1)
    mesh_from_pydata(f"SM_G1_Skylight_{_pi}", [_b1, _b2, _t2, _t1],
                     [(0, 3, 2, 1)], MAT_SKYLIGHT, COL_INTER)
# G1 white ceiling (ref_gallery1.jpg: flat white, not bare concrete slab).
# v16 P2 item 9: rebuilt to follow the diagonal wall exactly — the old
# polygon's far edge was 2.61 m inside the wall. The new far edge is
# parallel to the wall line, offset 0.8 m inward, so the skylight band
# stays open (panels cross z=-0.15 at 0.668 m inward; 0.8 m clears them
# by 0.13 m) and no part of the ceiling sits inside the wall.
flat_poly_slab("SM_G1_Ceiling", [(8, -7), (19.85, -7), (34.86, -1), (8, -1)],
               -0.15, 0.05, MAT_WHITE, COL_INTER)
# G1 linear fluorescents: 2 long parallel tube rows on the white ceiling.
for _fi, _fy in enumerate([-3.5, -5.2]):
    box(f"SM_G1_Fluorescent_{_fi}", (22, _fy, -0.22), (20.0, 0.12, 0.06), MAT_SKYLIGHT, COL_INTER)
# G1 small dark square window in the far wall, LEFT side (ref_gallery1.jpg).
# v16 P2 item 13: moved to the left (north/west) end of the far wall —
# along-wall 2.0 m from the wall's west end (photo: ~6% of the far wall's
# width from the left corner), mid-height, flush with the lining face.
# v16: moved onto the white lining face (was at (30.3,-4.7): 0.78 m on the
# far side of the museum-wall face, embedded behind the white basement wall
# and invisible from G1). Now flush with the lining, wall angle 21.79 deg.
box("SM_G1_SquareWindow", (23.76, -6.02, -2.4), (1.0, 0.06, 1.0), MAT_BLACK, COL_INTER,
    rot=(0, 0, math.radians(21.79)))
# G1 side walls: dark vertical slat panels (upper) + white doors (lower).
_MAT_G1_SLAT = mat_principled("MAT_G1_Slat", (0.12, 0.12, 0.12), rough=0.9)
box("SM_G1_Slat_North", (15, -6.72, -0.9), (14.0, 0.06, 1.2), _MAT_G1_SLAT, COL_INTER)
box("SM_G1_Slat_South", (22, -1.14, -0.9), (20.0, 0.06, 1.2), _MAT_G1_SLAT, COL_INTER)
box("SM_G1_Door_North", (12, -6.70, -3.75), (0.9, 0.06, 2.1), MAT_WHITE, COL_INTER)
box("SM_G1_Door_South", (26, -1.16, -3.75), (0.9, 0.06, 2.1), MAT_WHITE, COL_INTER)

# Basement ramp (the lower level's "subtle elevation changes"): v16 P2
# moves it south of the sunken court — the old wedge (X 8.5..12.5, Y 1..3)
# poked through the court west wall into the pit (court west edge at Y=1
# is X~11.7). Now a gentle wedge in the atrium->G2 passage (X 8.5..12.5,
# Y 6..8), rising 0.35 m eastward, clear of the court triangle (court ends
# at Y=5). Position and rise are interpretation, not measured.
_ramp_v = [(8.5, 6, -4.8), (12.5, 6, -4.8), (12.5, 6, -4.45),
           (8.5, 8, -4.8), (12.5, 8, -4.8), (12.5, 8, -4.45)]
_ramp_f = [(0, 1, 4, 3), (0, 2, 5, 3), (1, 2, 5, 4), (0, 1, 2), (3, 4, 5)]
mesh_from_pydata("SM_Ramp_Atrium_G2", _ramp_v, _ramp_f, MAT_CONCRETE, COL_INTER)

print("=== interior done ===")

# ================= EXHIBITS (virtual show "A Piece of Cloth, A Beam of Light") =================
# All in Gallery 2 (floor Z=-4.8), X 24..52, Y -1..15 (v16 P2: G2 moved east).
G2F = -4.8

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

# EXHIBIT 01 — A-POC red fabric: draped hanging textile panel (waved grid mesh)
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

# EXHIBIT_01 A-POC red fabric at (32, 9.5) — in the eastern Gallery 2,
# clear of the sunken-court triangle (the old (16,2) spot was INSIDE the
# court; the v15 (20,4.5) spot is west of the new G2).
draped_fabric("SM_EXHIBIT_01_RedFabric", 32, 9.5)
plinth("SM_EXHIBIT_01_Plinth", 32, 9.5, 5.0, 0.9, h=0.12)

# EXHIBIT 02 — pendant light cluster: 7 lamps at varying heights
for i, (px, py, drop) in enumerate([(34, 6.0, 1.6), (35.2, 7.2, 2.2), (36, 5.6, 1.2),
                                     (33.4, 7.6, 2.6), (35.8, 8.2, 1.9), (34.4, 8.6, 2.4), (36.4, 6.8, 1.4)]):
    top_z = 0.0
    bot_z = -drop
    box(f"SM_EXHIBIT_02_Cord_{i}", (px, py, (top_z + bot_z) / 2), (0.02, 0.02, top_z - bot_z), MAT_BLACK, COL_EXH)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(px, py, bot_z))
    s = bpy.context.active_object
    s.name = f"SM_EXHIBIT_02_Lamp_{i}"
    set_mat(s, MAT_LIGHT); link(s, COL_EXH)
plinth("SM_EXHIBIT_02_Plinth", 35, 7.0, 4.0, 4.0, h=0.1)

# EXHIBIT 03 — three chairs in a row
for i, cx in enumerate([40.5, 42.0, 43.5]):
    chair(f"SM_EXHIBIT_03_Chair_{i}", cx, 8.2, rot_z=0.15)
plinth("SM_EXHIBIT_03_Plinth", 42, 8.2, 4.2, 1.2, h=0.12)

# EXHIBIT 04 — graphic design wall: white panel + coloured geometric shapes (south wall)
box("SM_EXHIBIT_04_Panel", (38, 15.85, G2F + 1.8), (8.0, 0.12, 3.6), MAT_WHITE, COL_EXH)
box("SM_EXHIBIT_04_Red", (35.5, 15.78, G2F + 2.2), (1.6, 0.06, 1.6), MAT_RED, COL_EXH)
box("SM_EXHIBIT_04_Blue",
    (38.5, 15.78, G2F + 1.6), (1.8, 0.06, 1.0),
    mat_principled("MAT_Blue", (0.10, 0.25, 0.65), rough=0.6), COL_EXH)
box("SM_EXHIBIT_04_Black", (41.0, 15.78, G2F + 2.6), (1.2, 0.06, 0.8), MAT_BLACK, COL_EXH)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(40.6, 15.78, G2F + 1.0))
o = bpy.context.active_object
o.name = "SM_EXHIBIT_04_Circle"
o.scale = (1, 0.12, 1)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.object.shade_smooth()
set_mat(o, mat_principled("MAT_Yellow", (0.95, 0.75, 0.10), rough=0.6)); link(o, COL_EXH)

# EXHIBIT 05 — ceramic jars on a plinth at (46, 10), far east in Gallery 2
plinth("SM_EXHIBIT_05_Plinth", 46, 10, 3.0, 1.2, h=0.5)
for i, (jx, jr, jh) in enumerate([(45.0, 0.28, 0.75), (45.9, 0.34, 0.95), (46.8, 0.26, 0.65),
                                   (47.6, 0.30, 0.85), (46.3, 0.22, 0.55)]):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=jr, location=(jx, 10, G2F + 0.5 + jh * 0.45))
    s = bpy.context.active_object
    s.name = f"SM_EXHIBIT_05_Jar_{i}"
    s.scale = (1, 1, jh / (jr * 2) * 1.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    set_mat(s, MAT_CERAMIC); link(s, COL_EXH)
    box(f"SM_EXHIBIT_05_Neck_{i}", (jx, 10, G2F + 0.5 + jh * 0.95), (0.12, 0.12, 0.18), MAT_CERAMIC, COL_EXH)

# EXHIBIT 06 — central rotating installation: plinth + tilted torus ring on a stand
# v16 P2: moved to (36, 2.5) — just south of the column line, between the
# columns at x=34 and x=38, on the Gallery2 camera's sightline.
plinth("SM_EXHIBIT_06_Plinth", 36, 2.5, 2.2, 2.2, h=0.5)
box("SM_EXHIBIT_06_Stand", (36, 2.5, G2F + 1.1), (0.18, 0.18, 1.2), MAT_BLACK, COL_EXH)
bpy.ops.mesh.primitive_torus_add(major_radius=0.85, minor_radius=0.09,
    location=(36, 2.5, G2F + 2.1), rotation=(math.radians(65), 0, math.radians(20)))
t = bpy.context.active_object
t.name = "SM_EXHIBIT_06_Ring"
bpy.context.view_layer.objects.active = t
bpy.ops.object.shade_smooth()
set_mat(t, MAT_STEEL_DARK); link(t, COL_EXH)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(36, 2.5, G2F + 2.1))
s = bpy.context.active_object
s.name = "SM_EXHIBIT_06_Core"
bpy.context.view_layer.objects.active = s
bpy.ops.object.shade_smooth()
set_mat(s, MAT_RED_SPHERE); link(s, COL_EXH)

# ================= EXHIBITS 07-12 (v16 Phase 3: Leon 2026-11-17 — "the
# exhibition items should double too" now the underground space is bigger).
# 6 new pieces on the "everyday design" theme (Japanese daily-life design,
# same language as 01-06). Existing 01-06 untouched. All procedural
# primitives, low poly; positions keep the stair / ramp / court / atrium
# circulation clear. G2 = east hall, G1 = west trapezoid, floor Z = -4.8.
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

def low_table(name, x, y, w, d, h=0.45, floor_z=G2F):
    """Low wooden display table: top slab + 4 legs. Top surface at floor_z+h+0.03."""
    box(f"{name}_Top", (x, y, floor_z + h), (w, d, 0.06), MAT_WOOD, COL_EXH)
    for (lx, ly) in [(-w / 2 + 0.06, -d / 2 + 0.06), (w / 2 - 0.06, -d / 2 + 0.06),
                     (-w / 2 + 0.06, d / 2 - 0.06), (w / 2 - 0.06, d / 2 - 0.06)]:
        box(f"{name}_Leg_{lx:.2f}_{ly:.2f}", (x + lx, y + ly, floor_z + (h - 0.03) / 2),
            (0.05, 0.05, h - 0.03), MAT_BLACK, COL_EXH)

# EXHIBIT 07 — Akari paper lantern (Noguchi): warm glowing paper shade on a
# thin stand, east end of G2 (48, 4.5). Clear of the east door (51.85, 1.5),
# the column row (y=1.8) and exhibit 05 (46, 10). Echoes 02's light theme.
plinth("SM_EXHIBIT_07_Plinth", 48, 4.5, 1.2, 1.2, h=0.10)
box("SM_EXHIBIT_07_Stand", (48, 4.5, G2F + 0.38), (0.05, 0.05, 0.56), MAT_BLACK, COL_EXH)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.38,
                                     location=(48, 4.5, G2F + 1.04))
_s = bpy.context.active_object
_s.name = "SM_EXHIBIT_07_Shade"
_s.scale = (1, 1, 1.15)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.object.shade_smooth()
set_mat(_s, MAT_AKARI); link(_s, COL_EXH)

# EXHIBIT 08 — Kyusu teapot + 2 cups on a low wooden table, G2 south wall
# (47, 13.5), east of exhibit 04's wall (x 34..42). Side-handle teapot:
# squashed-sphere clay body, lid + knob, angled spout, loop handle.
low_table("SM_EXHIBIT_08_Table", 47, 13.5, 1.3, 0.65, h=0.45)
_top08 = G2F + 0.48
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.16,
                                     location=(47, 13.5, _top08 + 0.12))
_s = bpy.context.active_object
_s.name = "SM_EXHIBIT_08_Teapot_Body"
_s.scale = (1, 1, 0.75)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.object.shade_smooth()
set_mat(_s, MAT_KYUSU_CLAY); link(_s, COL_EXH)
bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.03, location=(47, 13.5, _top08 + 0.24))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_08_Teapot_Lid"
set_mat(_o, MAT_KYUSU_CLAY); link(_o, COL_EXH)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(47, 13.5, _top08 + 0.27))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_08_Teapot_Knob"
set_mat(_o, MAT_KYUSU_CLAY); link(_o, COL_EXH)
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.24,
                                    location=(47.19, 13.5, _top08 + 0.17),
                                    rotation=(0, math.radians(50), 0))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_08_Teapot_Spout"
set_mat(_o, MAT_KYUSU_CLAY); link(_o, COL_EXH)
bpy.ops.mesh.primitive_torus_add(major_radius=0.085, minor_radius=0.016,
                                 location=(46.83, 13.5, _top08 + 0.14),
                                 rotation=(math.radians(90), 0, 0))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_08_Teapot_Handle"
set_mat(_o, MAT_KYUSU_CLAY); link(_o, COL_EXH)
for _ci, (_cx, _cy) in enumerate([(47.40, 13.70), (47.40, 13.30)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.09, location=(_cx, _cy, _top08 + 0.045))
    _o = bpy.context.active_object
    _o.name = f"SM_EXHIBIT_08_Cup_{_ci}"
    set_mat(_o, MAT_CERAMIC); link(_o, COL_EXH)
bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.012, location=(47.40, 13.70, _top08 + 0.085))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_08_Tea"
set_mat(_o, MAT_TEA_DARK); link(_o, COL_EXH)

# EXHIBIT 09 — Noren indigo curtain in the G1->G2 doorway (x 28..31, y=-1).
# Rod 2.25 m above the floor; two panels with a centre split so the passage
# reads open (you walk through the split, as with a real noren). White
# crest discs on both faces of each panel.
box("SM_EXHIBIT_09_Rod", (29.5, -1, -2.55), (3.0, 0.05, 0.05), MAT_BLACK, COL_EXH)
box("SM_EXHIBIT_09_Panel_L", (28.75, -1, -3.45), (1.3, 0.04, 1.8), MAT_INDIGO, COL_EXH)
box("SM_EXHIBIT_09_Panel_R", (30.25, -1, -3.45), (1.3, 0.04, 1.8), MAT_INDIGO, COL_EXH)
for _di, (_dx, _dy) in enumerate([(28.75, -1.03), (28.75, -0.97),
                                  (30.25, -1.03), (30.25, -0.97)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.02,
                                        location=(_dx, _dy, -3.30),
                                        rotation=(math.radians(90), 0, 0))
    _o = bpy.context.active_object
    _o.name = f"SM_EXHIBIT_09_Crest_{_di}"
    set_mat(_o, MAT_WHITE); link(_o, COL_EXH)

# EXHIBIT 10 — Lacquer bento box (black + red tiers) on a low table, G1
# (15, -3.5). Clear of the stair-landing doorway (x=8) and the G1->G2
# doorway (29.5, -1); chopsticks beside the box.
low_table("SM_EXHIBIT_10_Table", 15, -3.5, 0.95, 0.6, h=0.40)
_top10 = G2F + 0.43
box("SM_EXHIBIT_10_Tier_Black", (15, -3.5, _top10 + 0.045), (0.34, 0.24, 0.09), MAT_LACQUER_BLACK, COL_EXH)
box("SM_EXHIBIT_10_Tier_Red", (15.01, -3.5, _top10 + 0.135), (0.32, 0.22, 0.09), MAT_LACQUER_RED, COL_EXH)
box("SM_EXHIBIT_10_Lid", (15, -3.5, _top10 + 0.19), (0.34, 0.24, 0.02), MAT_LACQUER_BLACK, COL_EXH)
box("SM_EXHIBIT_10_Chopstick_0", (15.35, -3.28, _top10 + 0.008), (0.22, 0.016, 0.016), MAT_BAMBOO_DARK, COL_EXH, rot=(0, 0, 0.20))
box("SM_EXHIBIT_10_Chopstick_1", (15.35, -3.24, _top10 + 0.008), (0.22, 0.016, 0.016), MAT_BAMBOO_DARK, COL_EXH, rot=(0, 0, 0.16))

# EXHIBIT 11 — Bamboo basket on a low round plinth, G2 west end (28, 4).
# Clear of the column row (y=1.8), exhibit 06 (36, 2.5) and the G1->G2
# doorway (28..31, y=-1). Tapered woven-look body + rim + dark interior.
bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.10, location=(28, 4, G2F + 0.05))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_11_Plinth"
set_mat(_o, MAT_PLINTH); link(_o, COL_EXH)
bpy.ops.mesh.primitive_cone_add(radius1=0.26, radius2=0.32, depth=0.42, vertices=24,
                                location=(28, 4, G2F + 0.31))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_11_Basket"
set_mat(_o, MAT_BAMBOO); link(_o, COL_EXH)
bpy.ops.mesh.primitive_torus_add(major_radius=0.32, minor_radius=0.02, location=(28, 4, G2F + 0.52))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_11_Rim"
set_mat(_o, MAT_BAMBOO_DARK); link(_o, COL_EXH)
bpy.ops.mesh.primitive_cylinder_add(radius=0.29, depth=0.02, location=(28, 4, G2F + 0.50))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_11_Interior"
set_mat(_o, MAT_BAMBOO_DARK); link(_o, COL_EXH)
bpy.ops.mesh.primitive_torus_add(major_radius=0.30, minor_radius=0.015, location=(28, 4, G2F + 0.31))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_11_Band"
set_mat(_o, MAT_BAMBOO_DARK); link(_o, COL_EXH)

# EXHIBIT 12 — Tea bowl + chasen (bamboo whisk) on a wooden tray, on the
# east round table in the atrium (6.0, -5.5, table top z=-4.225). Uses the
# existing atrium furniture; nothing new on the floor, circulation untouched.
box("SM_EXHIBIT_12_Tray", (6.0, -5.5, -4.215), (0.42, 0.30, 0.02), MAT_WOOD, COL_EXH)
bpy.ops.mesh.primitive_cylinder_add(radius=0.085, depth=0.08, location=(5.88, -5.55, -4.165))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_12_TeaBowl"
set_mat(_o, MAT_TEA_BOWL); link(_o, COL_EXH)
bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.012, location=(5.88, -5.55, -4.125))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_12_Matcha"
set_mat(_o, MAT_MATCHA); link(_o, COL_EXH)
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.06, location=(6.12, -5.42, -4.175))
_o = bpy.context.active_object
_o.name = "SM_EXHIBIT_12_Chasen_Handle"
set_mat(_o, MAT_BAMBOO); link(_o, COL_EXH)
bpy.ops.mesh.primitive_cone_add(radius1=0.022, radius2=0.05, depth=0.09, vertices=16,
                                location=(6.12, -5.42, -4.10))
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
    ("MAT_Granite", 512), ("MAT_Concrete_Dark", 512),  # #18: MAT_Flowers gone with the beds
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
    bpy.ops.mesh.primitive_plane_add(size=2.0, location=(120.0, 120.0, -20.0))
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
# UVs: cube projection (world-scale, 2 m tile) on every mesh so baked
# textures map at a consistent scale; required for image textures in glTF.
for _o in list(bpy.context.scene.objects):
    if _o.type != 'MESH':
        continue
    if _o.name.startswith("SM_Tree_Card") or _o.name.startswith("SM_Tree_TopCard"):
        continue  # leaf cards already carry their own 0..1 UVs
    if _o.name.startswith("SM_Site_FarGround_"):
        continue  # #18/#20: far-ground strips keep their world-mapped UVs (u=(x+800)/1600) for the radial-gradient texture; cube_project would tile it every 2 m into a dot grid
    bpy.context.view_layer.objects.active = _o
    _o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    try:
        bpy.ops.uv.cube_project(cube_size=2.0)
    except Exception as _e:
        print(f"UV-FAIL {_o.name}: {_e}")
    bpy.ops.object.mode_set(mode='OBJECT')
    _o.select_set(False)
print("=== UV done ===")

bpy.ops.wm.save_mainfile(filepath=BLEND_PATH)
print(f"saved {BLEND_PATH}")

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
