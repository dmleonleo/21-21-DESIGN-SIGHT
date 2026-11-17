# Verify design2121.glb: re-import, print stats, render key views (Cycles/GPU).
import bpy, math, os
from mathutils import Vector

GLB = r"C:\Users\Leon\design2121\design2121_v16.glb"
OUT = r"C:\Users\Leon\design2121"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)

# ---- stats ----
nmesh = 0; tris = 0
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        nmesh += 1
        tris += len(o.data.polygons)
print(f"GLB-STATS objects={len(bpy.context.scene.objects)} meshes={nmesh} tris={tris}")
mn = Vector((1e9, 1e9, 1e9)); mx = Vector((-1e9, -1e9, -1e9))
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
print(f"GLB-BBOX min={tuple(round(v,2) for v in mn)} max={tuple(round(v,2) for v in mx)} size={tuple(round(v,2) for v in (mx-mn))}")
# hierarchy: top-level objects
for o in bpy.context.scene.objects:
    if o.parent is None:
        print(f"GLB-ROOT {o.name} type={o.type} children={len(o.children)}")
# v12: baked textures must survive the GLB round-trip
for m in bpy.data.materials:
    if not m.use_nodes:
        continue
    imgs = [n.image.name for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
    if imgs:
        print(f"GLB-MAT-TEX {m.name}: {imgs}")
print(f"GLB-IMAGES {len(bpy.data.images)}")

# ---- render setup: Cycles GPU OptiX, AgX ----
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.render.resolution_x = 1280
scene.render.resolution_y = 800
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'AgX'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    for d in prefs.devices:
        d.use = True
except Exception as e:
    print("GPU prefs warning:", e)

# world: real Nishita sky, daytime, sun ~40 deg (v12: no more flat colour bg)
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
# Blender 5.2 TexSky: no Sun Elevation/Rotation inputs any more; the sun
# direction comes from the Vector input. Default sky_type
# MULTIPLE_SCATTERING *is* the Nishita model. Sun in the SW sky at 40 deg
# elevation -> direction to sun (-0.383, +0.663, +0.643); matches the SUN
# light object rotation (50 deg, 0, 210 deg) below.
sky = world.node_tree.nodes.new("ShaderNodeTexSky")
# no standalone Vector node exists in shader trees: set the socket default
sky.inputs[0].default_value = (-0.383, 0.663, 0.643)  # 5.2 quirk: name lookup fails, index works
# v14: procedural clouds in the sky — the flat gradient read cheap. Noise
# (direction-based) shaped by a ramp, masked to above the horizon by the
# direction Z, mixed with the Nishita sky colour.
_cloud_tc = world.node_tree.nodes.new("ShaderNodeTexCoord")
_cloud_map = world.node_tree.nodes.new("ShaderNodeMapping")
_cloud_map.inputs["Scale"].default_value = (3.0, 3.0, 3.0)
world.node_tree.links.new(_cloud_tc.outputs["Generated"], _cloud_map.inputs["Vector"])
_cloud_noise = world.node_tree.nodes.new("ShaderNodeTexNoise")
_cloud_noise.inputs["Scale"].default_value = 4.0
_cloud_noise.inputs["Detail"].default_value = 4.0
_cloud_noise.inputs["Roughness"].default_value = 0.7
world.node_tree.links.new(_cloud_map.outputs["Vector"], _cloud_noise.inputs["Vector"])
_cloud_ramp = world.node_tree.nodes.new("ShaderNodeValToRGB")
_cloud_ramp.color_ramp.elements[0].position = 0.38
_cloud_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
_cloud_ramp.color_ramp.elements[1].position = 0.55
_cloud_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
world.node_tree.links.new(_cloud_noise.outputs["Fac"], _cloud_ramp.inputs["Fac"])
_cloud_sep = world.node_tree.nodes.new("ShaderNodeSeparateXYZ")
world.node_tree.links.new(_cloud_tc.outputs["Generated"], _cloud_sep.inputs["Vector"])
_cloud_zmask = world.node_tree.nodes.new("ShaderNodeMapRange")
_cloud_zmask.inputs["From Min"].default_value = -0.05
_cloud_zmask.inputs["From Max"].default_value = 0.35
_cloud_zmask.inputs["To Min"].default_value = 0.0
_cloud_zmask.inputs["To Max"].default_value = 1.0
_cloud_zmask.clamp = True
world.node_tree.links.new(_cloud_sep.outputs["Z"], _cloud_zmask.inputs["Value"])
_cloud_fac = world.node_tree.nodes.new("ShaderNodeMath")
_cloud_fac.operation = 'MULTIPLY'
world.node_tree.links.new(_cloud_ramp.outputs["Color"], _cloud_fac.inputs[0])
world.node_tree.links.new(_cloud_zmask.outputs["Result"], _cloud_fac.inputs[1])
_cloud_mix = world.node_tree.nodes.new("ShaderNodeMixRGB")
_cloud_mix.blend_type = 'MIX'
_cloud_mix.inputs[2].default_value = (1.0, 1.0, 1.0, 1.0)
world.node_tree.links.new(sky.outputs["Color"], _cloud_mix.inputs[1])
world.node_tree.links.new(_cloud_fac.outputs["Value"], _cloud_mix.inputs[0])
world.node_tree.links.new(_cloud_mix.outputs["Color"], bg.inputs["Color"])
bg.inputs[1].default_value = 0.22
print("world: Nishita sky + procedural clouds")

# sun
bpy.ops.object.light_add(type='SUN', location=(20, -25, 30))
sun = bpy.context.active_object
sun.name = "LGT_Sun"
sun.rotation_euler = (math.radians(50), 0, math.radians(210))
sun.data.energy = 4.5  # v14: materials darkened (roof/paving/lawn base colours), so the sun goes back up to 4-5 for sharp shadows + contrast; do NOT lower the sun to excuse bright materials
sun.data.angle = 0.002  # ~0.11 deg: sharp shadows (v13 fix 4)
# interior fill lights (for atrium / gallery renders)
# v16 P2: G2 point fills moved to the eastern hall (x 24..52, y -1..15).
for (lx, ly, lz, e) in [(4, 1, -2.5, 125), (30, 4, -2.6, 500), (15, 1, -1.0, 150),
                        (25, -2, 2.0, 150), (22, -4, -2.0, 400),
                        (14, 2, -2.6, 500), (38, 8, -2.6, 600),
                        (46, 12, -2.6, 500), (38, 2, -2.6, 500),
                        (-22, -1, 2.5, 300), (-14, 1, 2.0, 200)]:  # v16: G2 fills lowered z -1.5 -> -2.6 (ceiling wash); G3 fills unchanged
    bpy.ops.object.light_add(type='POINT', location=(lx, ly, lz))
    p = bpy.context.active_object
    p.data.energy = e
    p.data.shadow_soft_size = 0.5

# v15: broad AREA light just below the G2 ceiling, pointing down — the
# point fills alone left the far half dark; a ceiling wash makes the whole
# 443 m2 gallery read as one bright uniform white space. v16 P2: moved to
# the eastern G2 (38 x 16 m, centre (38,7)).
bpy.ops.object.light_add(type='AREA', location=(38, 7, -1.2))
_g2area = bpy.context.active_object
_g2area.name = "LGT_G2_Ceiling"
_g2area.data.energy = 3500
_g2area.data.size = 30.0
_g2area.data.shape = 'RECTANGLE'
_g2area.scale = (1.0, 0.53, 1.0)
tgt_g2 = bpy.data.objects.new("TGT_G2_Ceiling", None)
bpy.context.scene.collection.objects.link(tgt_g2)
tgt_g2.location = (38, 7, -4.8)
con_g2 = _g2area.constraints.new('TRACK_TO')
con_g2.target = tgt_g2
con_g2.track_axis = 'TRACK_NEGATIVE_Z'
con_g2.up_axis = 'UP_Y'

# r5: wash the atrium soffit with an UPWARD area light — the point wash
# (600) only whitened the centre; the green lawn bounce still tinted the
# edges olive. A broad area light just below the soffit evens it out.
bpy.ops.object.light_add(type='AREA', location=(4, 0, -2.0))
_ceiling = bpy.context.active_object
_ceiling.name = "LGT_Atrium_Ceiling"
_ceiling.data.energy = 1500
_ceiling.data.size = 8.0
_ceiling.data.shape = 'RECTANGLE'
_ceiling.scale = (1.0, 0.75, 1.0)
tgt_c = bpy.data.objects.new("TGT_Atrium_Ceiling", None)
bpy.context.scene.collection.objects.link(tgt_c)
tgt_c.location = (4, 0, 0)
con_c = _ceiling.constraints.new('TRACK_TO')
con_c.target = tgt_c
con_c.track_axis = 'TRACK_NEGATIVE_Z'
con_c.up_axis = 'UP_Y'

# v13: area light outside the atrium glass wall, shining in — bright near
# the glass, dark at the far end (light/dark layering in the atrium)
bpy.ops.object.light_add(type='AREA', location=(4, 12, 3))
area = bpy.context.active_object
area.name = "LGT_Atrium_Area"
area.data.energy = 2000
area.data.size = 6.0
tgt_a = bpy.data.objects.new("TGT_Atrium_Area", None)
bpy.context.scene.collection.objects.link(tgt_a)
tgt_a.location = (4, 0, -3)
con_a = area.constraints.new('TRACK_TO')
con_a.target = tgt_a
con_a.track_axis = 'TRACK_NEGATIVE_Z'
con_a.up_axis = 'UP_Y'

def render_cam(name, loc, target, lens=35):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.active_object
    cam.name = name
    cam.data.lens = lens
    # track to target
    tgt = bpy.data.objects.new(f"TGT_{name}", None)
    bpy.context.scene.collection.objects.link(tgt)
    tgt.location = target
    con = cam.constraints.new('TRACK_TO')
    con.target = tgt
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'
    scene.camera = cam
    scene.render.filepath = os.path.join(OUT, f"v16_verify_{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"rendered {name}")

def hide_for_plan(names):
    """Hide objects whose name contains any of the given substrings (for the
    top-down basement plan: everything above the basement must go)."""
    for o in bpy.context.scene.objects:
        if any(s in o.name for s in names):
            o.hide_render = True

def unhide_all():
    for o in bpy.context.scene.objects:
        o.hide_render = False

# v16 Phase 2: full verification set (Aerial, Front, Atrium, Gallery2,
# Court, Gallery1, Gallery3, Entrance, Stair, Ramp) + AtriumBench +
# G1FarWall (item 13 straight-on far wall) + BasementPlan (top-down) +
# BasementSection (south cutaway).
# Basement plan FIRST (it hides the roof/slabs/ceilings/lawn), then unhide.
hide_for_plan(["Roof", "Slab", "Ceiling", "Soffit", "Ground", "Glass_South",
               "Glass_Tip", "Cafe_Glass", "Tree", "Canopy", "Sign", "Entrance_",
               "Reception", "Shop_", "Hall_Column", "Passage", "Terrace",
               "Paving", "Flower", "G3_", "Cafe_Wall", "SlitWindow", "WarmStrip",
               "Skylight_Slot", "Fluorescent", "Downlight", "TrackRail", "Spot_",
               "CoveStrip"])
render_cam("CAM_BasementPlan", (21, 4.5, 60), (21, 4.5, -4.8), lens=28)
unhide_all()
# Basement section: south cutaway (hide the south wall + south glass so the
# camera south of the building sees into the basement).
for _n in ["SM_Basement_Wall_South", "SM_Museum_Glass_South"]:
    _o = bpy.data.objects.get(_n)
    if _o is not None:
        _o.hide_render = True
render_cam("CAM_BasementSection", (21, 30, -2.0), (21, 0, -2.5), lens=28)
unhide_all()
# Aerial + Front (exterior)
render_cam("CAM_Aerial", (34, 34, 26), (4, 0, 1), lens=32)
render_cam("CAM_Front", (8, 32, 2.5), (6, 0, 3.5), lens=28)
# Atrium interior: from the basement floor looking up at the floating stair + glass
render_cam("CAM_Atrium", (3, 4, -3.0), (7, -4.5, -1.5), lens=28)
# Gallery 2 interior (v15r2: camera back at the v14 position (x=22, beside
# the ring exhibit) looking east — r1's camera at x=14 sat behind the glass
# ring, which filled the frame and washed the room out)
# v16r2: camera moved SOUTH to y=3.5 — the first v16 position (y=1.3) put
# the G2 column at (26,1.8) 4 m dead ahead, filling the frame centre and
# hiding the ring exhibit + east doorway. From y=3.5 the column row is
# off to the left and the hall, ring, and far east doorway read clearly.
render_cam("CAM_Gallery2", (22, 3.5, -2.4), (44, 3.5, -3.0), lens=32)
# Sunken court: top-down through the roof opening (the only angle that shows
# the whole triangle + tree + planter + glass; eye-level angles inside the
# small pit cannot fit the 8 m tree and read only as walls)
render_cam("CAM_Court", (15, 2, 10), (15, 1.5, -4.8), lens=28)
# Gallery 1 (v15r5: back to the r3 framing — it showed the room well; the
# panels were hidden behind the wall, not a camera problem. Panels now sit
# on the wall's actual face, so this view should show the row of 6.)
# v16 P2: G1 is the western trapezoid; camera inside it looking NE at the
# diagonal far wall (panels + square window on the left).
render_cam("CAM_Gallery1", (18, -2.0, -2.5), (32, -4.3, -0.6), lens=28)
# v16 P2 item 13: straight-on view of G1's far (diagonal) wall, to confirm
# the square window sits on the LEFT side of the wall, mid-height.
# v16r2: camera moved to the SOUTH-EAST end of G1 (34,-2.0) looking
# north-west — the first position (14,-2.5, looking NE) put the wall's
# west end (where the window is) on the right of the frame, opposite to
# ref_gallery1.jpg. From the south-east the window (west end) reads on
# the LEFT, as in the photo.
# v16r3: camera pulled back from the south wall and aimed at the window
# itself (24,-5.5) — the r2 position (34,-2.0) sat against the south
# slat panel, which filled a third of the frame and left the far wall
# small and blocked. Now (28,-1.5), just off the south wall, looking
# north-west at the window.
render_cam("CAM_G1FarWall", (28, -1.5, -2.0), (24, -5.5, -2.4), lens=32)
# Gallery 3 (v16 P2 item 15): camera moved to the west end looking ESE
# (lens 22) so the north-wall reception desks (east end, left of frame)
# and the south glass edge (right of frame) are both in view. The old
# camera looked west and showed neither.
# v16r2: camera moved INSIDE G3 (-30,-3.5) — the first position (-30,0.5)
# was SOUTH of G3's south edge (y=-2.2 at x=-30), outside the room,
# so it showed only a blank exterior wall.
# v16r3: camera moved to the NORTH-WEST (-31,-4.5) — the r2 position put
# Column_0 (-28.5,-3.0) 1.6 m dead ahead, filling the frame, and the
# reception desks were hidden behind the private room. From the
# north-west the column is off to the right, the (relocated) desks are
# on the left (north wall), and the south glass is on the right.
render_cam("CAM_Gallery3", (-31, -4.5, 2.0), (-15, -3, 1.0), lens=22)
# Entrance: from the courtyard looking in through the new real doorway.
render_cam("CAM_Entrance", (0, 0, 1.7), (8, -1, 3.5), lens=28)
# v16r2 item 10: the standard Entrance camera sits INSIDE the lobby
# (x=0, east of the entrance at x=-2.6) looking east, so it cannot see
# the doorway itself. This shot stands in the courtyard (x=-8) looking
# east through the real opening in the entrance block + glass door.
render_cam("CAM_EntranceDoorway", (-8, 0, 1.7), (0, 0, 1.7), lens=28)
# Stair + Ramp (basement circulation)
render_cam("CAM_Stair", (7.5, -4.0, -3.5), (0, -4.5, 1.0), lens=28)
# v16r2: ramp moved to Y 6..8 (north of the old camera); the old target
# (11,2) looked SOUTH, away from the new ramp. Now looking north at it.
render_cam("CAM_Ramp", (11, 4.5, -3.0), (11, 7, -4.6), lens=28)
# v16r2: benches by the east glass — the standard CAM_Atrium looks up at the
# stair and cuts the floor furniture out of frame, so this extra shot looks
# down at the benches (7.2, 0.5/3.0) with the court glass behind them.
render_cam("CAM_AtriumBench", (2.5, 4.5, -3.0), (7.2, 1.7, -4.2), lens=32)
# v16 Phase 3 item 3: dedicated G3 south-glass camera. Inside G3 from the
# west end looking ESE along the room: the south glass on the left, both
# triangular reception desks on the right (north wall). NOTE: a camera
# looking due south/north breaks TRACK_TO (view dir parallel to the UP_Y
# up axis), so this camera looks EAST, not south.
render_cam("CAM_Gallery3South", (-29, -1.5, 2.0), (-14, -1.5, 1.0), lens=22)
# v16 Phase 3 (exhibits 07-12): dedicated exhibit views.
render_cam("CAM_G2East", (40, 6, -2.5), (48, 11, -3.5), lens=28)
render_cam("CAM_G1Exhibits", (26, -2, -2.2), (13, -4, -3.2), lens=28)
render_cam("CAM_Noren", (33, 1, -2.5), (29.5, -1, -3.2), lens=32)
# v16 Phase 3 fix: the first TeaSet camera (4,2,-2.5) looked THROUGH the
# stair (its sightline to the table passed under the stair nosings and hit
# the north parapet), so the table was hidden. This one looks EAST along
# the north-wall strip (y=-6), with the stair parapet to the right.
render_cam("CAM_TeaSet", (1, -6, -2.5), (6, -5.5, -4.3), lens=32)
# v16 Phase 3 item 3 (2nd angle): the ESE camera shows both desks but the
# south glass only as a foreshortened sliver. This one looks SW from the
# north-east corner, so the south glass (mullions + terrace + round column
# at the south vertex) reads face-on.
render_cam("CAM_Gallery3South2", (-17, -2.5, 2.0), (-28, 3, 1.0), lens=22)
# v16 Phase 3 item 3 (3rd angle, low): the first two angles show the glass
# only as a ~0.4 m band, because the Section C ceiling slopes down to meet
# it at z=0.4 — from inside, that band is all of the glass that is visible.
# This low camera (eye level with the band) shows the band, its mullions
# and the terrace beyond filling the frame.
render_cam("CAM_Gallery3South3", (-22, -4, 0.8), (-24, 3, 0.4), lens=28)
print("=== VERIFY V16 COMPLETE ===")
