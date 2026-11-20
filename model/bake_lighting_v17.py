# 21_21 #4 lighting bake — v17 FIX19 (Hark review on PR #19).
# Based on bake_lighting_v17.py (v7 script, paths re-pointed to v17).
# EVERYTHING about the bake itself is unchanged: 32 samples + OIDN (CPU),
# same 6 groups / grids / sizes, same world 1.5 + sun 5.0, same glass fix,
# same sqrt(irr * soft-AO) combine, same p90 -> 0.95 clamp [0.08, 1.0] norm.
#
# FIX19 — root cause (proven by A/B probes, see PR #19 review thread (comment 7011678176)):
# the v17 script interleaved UV creation and baking per group
# (UV -> bake -> UV -> bake ...). After a group's bake the group's objects
# stay SELECTED (the script never deselects them), so the next group's
# ensure_lightmap_uv() enters MULTI-OBJECT edit mode on mode_set(EDIT) and
# smart_project packs ALL selected objects' islands into the shared [0,1]^2
# UV space — the current object's islands come out as degenerate slivers
# (~1/150 of their proper area). White_Wall (first group, no prior bake)
# was the only healthy atlas; Board/Concrete/Floor/Granite/Dark all baked
# flat (Board whole-atlas mean 0.0012 pre-norm, 21/10 post-norm vs main 38/70).
# The v16 run had the same latent bug (its saved UVs are equally slivered);
# main's healthy atlases came from an earlier healthy run's PNGs.
#
# The fix (two independent layers, either alone suffices):
#  (1) REORDER: Phase 1 creates ALL groups' lightmap UVs first; only then
#      does Phase 2 run any bake. No bake (and no leftover selection) can
#      exist while UVs are being made.
#  (2) DESELECT: ensure_lightmap_uv() starts with a full select_all(DESELECT),
#      so even a leftover selection cannot leak into edit mode. Verified:
#      with a 33-object leftover selection, Board UV total = 0.39446
#      (healthy baseline) vs 0.00262 without the deselect.
#  (3) ASSERT: after Phase 1, each group's total UV island area is measured
#      (fresh read) and must exceed 0.30 (healthy 0.39-0.64, broken <= 0.24);
#      otherwise the script aborts BEFORE any baking, instead of wasting a
#      1-2 h bake on dead UVs.
import bpy, os, math
import numpy as np
import mathutils

BLEND_IN = r"C:\Users\Leon\design2121\design2121_v17_build.blend"
OUT_DIR = r"C:\Users\Leon\design2121"
TEX_DIR = os.path.join(OUT_DIR, "textures_v17_lighting")
os.makedirs(TEX_DIR, exist_ok=True)
UV_LAYER = "UVMap_Lightmap"
# Healthy per-group UV island totals measured on the v17 build .blend
# (WW 0.516, Board 0.394, Concrete 0.565, Floor 0.635, Granite 0.540,
# Dark 0.552); broken runs give <= 0.24. Abort below this.
UV_AREA_MIN = 0.30

def log(*a, **kw):
    # accepts (and ignores) flush= etc. so a stray kwarg can never kill a bake
    print("BAKE:", *a, flush=True)

# ---------------------------------------------------------------- scene setup
def setup_bake_scene():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'   # v6: CPU — GPU OptiX dies inside the bake (see header)
    scene.cycles.samples = 32     # v6: 32 + denoise is plenty for a smooth indirect atlas
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    log("CPU mode: 32 samples + OpenImageDenoise")
    # world: soft overcast sky (boosted for bake SNR; level normalised later)
    world = bpy.data.worlds.get("BakeWorld") or bpy.data.worlds.new("BakeWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.62, 0.70, 0.85, 1.0)
    bg.inputs["Strength"].default_value = 1.5
    scene.world = world
    # sun: same direction as the page noon sun (SE-high), boosted for SNR
    sun = None
    for o in bpy.context.scene.objects:
        if o.type == 'LIGHT' and o.data.type == 'SUN':
            sun = o
            break
    if sun is None:
        bpy.ops.object.light_add(type='SUN', location=(0, 0, 30))
        sun = bpy.context.active_object
    sun.data.energy = 5.0
    # NOTE: do NOT set sun.data.angle here — v4 set it to 0.5 and the bake
    # still died; the diagnostic bakes that worked never touched it.
    target = mathutils.Vector((-0.55, -0.68, -0.35)).normalized()
    sun.rotation_euler = target.to_track_quat('-Z', 'Y').to_euler()
    log("sun rotation:", tuple(round(v, 3) for v in sun.rotation_euler))
    # glass: transmission 0, alpha 0.18 (so the bake sees through it)
    mat_glass = bpy.data.materials.get("MAT_Glass")
    if mat_glass and mat_glass.use_nodes:
        bsdf = next((n for n in mat_glass.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf:
            if "Transmission Weight" in bsdf.inputs:
                bsdf.inputs["Transmission Weight"].default_value = 0.0
            if "Alpha" in bsdf.inputs:
                bsdf.inputs["Alpha"].default_value = 0.18
            log("glass fixed: transmission 0, alpha 0.18")
    return scene

# ---------------------------------------------------------------- lightmap UV
def _tri_area2d(a, b, c):
    return abs((b[0]-a[0])*(c[1]-a[1]) - (c[0]-a[0])*(b[1]-a[1])) * 0.5

def uv_island_area(obj):
    """Total UV area of obj's UVMap_Lightmap islands (fresh read, OBJECT mode).
    Used by the Phase 1 verification: a healthy group totals 0.39-0.64."""
    me = obj.data
    uv = me.uv_layers.get(UV_LAYER)
    if uv is None:
        return 0.0
    uvs = np.array([tuple(d.uv) for d in uv.data], dtype=np.float64)
    area = 0.0
    for poly in me.polygons:
        li = list(poly.loop_indices)
        if len(li) < 3:
            continue
        a, b = uvs[li[0]], uvs[li[1]]
        for k in li[2:]:
            area += _tri_area2d(a, b, uvs[k])
            b = uvs[k]
    return area

def ensure_lightmap_uv(obj, cols, rows, cell_idx):
    """Smart-project onto UVMap_Lightmap, then pack into one grid cell."""
    # FIX19 (2): clear ANY leftover selection first. A previous bake leaves
    # its group selected; without this, mode_set(EDIT) enters multi-object
    # edit mode and smart_project squeezes this object's islands to make
    # room for all selected objects (Board 0.394 -> 0.0026). The deselect
    # restores the healthy result exactly (verified 0.39446).
    bpy.ops.object.select_all(action='DESELECT')
    me = obj.data
    uv = me.uv_layers.get(UV_LAYER) or me.uv_layers.new(name=UV_LAYER)
    me.uv_layers.active = uv
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)
    # pack into grid cell (2% inset so islands don't bleed across cells)
    cw, ch = 1.0 / cols, 1.0 / rows
    ox, oy = (cell_idx % cols) * cw, (cell_idx // cols) * ch
    inset = 0.02
    for loop in me.uv_layers[UV_LAYER].data:
        u, v = loop.uv
        loop.uv = (ox + inset * cw + u * cw * (1 - 2 * inset),
                   oy + inset * ch + v * ch * (1 - 2 * inset))

# ---------------------------------------------------------------- one bake pass
def bake_pass(mat_name, bake_type, size, tex, ntree, pass_filter=None):
    """Bake one pass into a fresh image. Follows the diagnostic bake's exact
    call pattern (the three diag bakes that worked): pass_filter= in the
    operator call, ntree.nodes.active, and only type/pass_filter/margin as
    operator kwargs. Granular logging: v3/v4/v5 all died silently inside this
    function, so each step logs before it runs."""
    log(f"    [{bake_type}] creating {size}x{size} image ...")
    img = bpy.data.images.new(f"{mat_name}_lm_{bake_type}", width=size, height=size, alpha=False)
    log(f"    [{bake_type}] image created, setting colorspace ...")
    img.colorspace_settings.name = 'Non-Color'
    log(f"    [{bake_type}] setting tex.image + nodes.active ...")
    tex.image = img
    ntree.nodes.active = tex
    log(f"    [{bake_type}] calling bpy.ops.object.bake ...")
    if bake_type == 'DIFFUSE':
        res = bpy.ops.object.bake(type='DIFFUSE', pass_filter=pass_filter or {'INDIRECT'}, margin=4)
    else:  # AO
        res = bpy.ops.object.bake(type='AO', margin=4)
    log(f"    {bake_type} bake -> {res}", flush=True)
    return img

# ---------------------------------------------------------------- main
def main():
    setup_bake_scene()
    # groups: (material, atlas size, grid cols, grid rows)
    groups = [
        ("MAT_White_Wall",     2048, 6, 6),
        ("MAT_Concrete_Board", 2048, 8, 7),
        ("MAT_Concrete",       1024, 5, 4),
        ("MAT_Floor_Concrete", 1024, 1, 1),
        ("MAT_Granite",         512, 1, 1),
        ("MAT_Concrete_Dark",  1024, 1, 1),
    ]
    # ---- collect group objects first (no baking yet) ----
    collected = []  # (mat_name, size, cols, rows, mat, objs)
    for mat_name, size, cols, rows in groups:
        mat = bpy.data.materials.get(mat_name)
        if mat is None:
            log(f"GROUP {mat_name}: material not found, skipping")
            continue
        objs = [o for o in bpy.context.scene.objects
                if o.type == 'MESH' and o.material_slots and o.material_slots[0].material
                and o.material_slots[0].material.name == mat_name]
        if not objs:
            log(f"GROUP {mat_name}: no objects, skipping")
            continue
        log(f"GROUP {mat_name}: {len(objs)} objs, grid {cols}x{rows}, atlas {size}")
        collected.append((mat_name, size, cols, rows, mat, objs))
    # ---- PHASE 1 (FIX19): ALL lightmap UVs first, before ANY bake ----
    # The lightmap UV MUST stay the active layer through both bakes:
    # Cycles writes the bake into the ACTIVE UV. (v3 restored the
    # colour UV here, before baking — the bake then rasterised into
    # the cube-projected colour UV, whose coordinates run far outside
    # [0,1], and Blender died silently. The three diagnostic bakes
    # that worked all left the lightmap UV active.)
    for mat_name, size, cols, rows, mat, objs in collected:
        for idx, o in enumerate(objs):
            ensure_lightmap_uv(o, cols, rows, idx)
        total = sum(uv_island_area(o) for o in objs)
        log(f"UVCHECK {mat_name}: total island area = {total:.5f} (min {UV_AREA_MIN})")
        if total < UV_AREA_MIN:
            raise RuntimeError(
                f"UVCHECK FAILED {mat_name}: island area {total:.5f} < {UV_AREA_MIN} — "
                "lightmap UVs are degenerate (see fix19 header); aborting before baking")
    log("UVCHECK all groups passed — starting bakes")
    # ---- PHASE 2: bake each group (UVs already exist and are verified) ----
    kept = []   # (atlas image, path) — saved at the end
    for mat_name, size, cols, rows, mat, objs in collected:
        # 2) one bake-target image node in the material
        ntree = mat.node_tree
        tex = ntree.nodes.new("ShaderNodeTexImage")
        # 3) select the group objects and bake DIFFUSE-indirect, then AO
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        log(f"  baking DIFFUSE-indirect {mat_name} ...")
        img_irr = bake_pass(mat_name, 'DIFFUSE', size, tex, ntree, {'INDIRECT'})
        log(f"  baking AO {mat_name} ...")
        img_ao = bake_pass(mat_name, 'AO', size, tex, ntree, None)
        # 4) combine: atlas = sqrt(irradiance * soft-AO).
        #    v6 used a straight multiply + mean normalisation and it failed:
        #    the basement's indirect light is so skewed (most pixels ~0,
        #    a few near the skylight/court ~100x brighter) that scaling the
        #    mean to 0.75 pushed >90% of pixels to the 0.12 floor and clipped
        #    the bright 1-8% to white — the atlases came out binary (dark
        #    with white hotspots, no gradient). Two fixes: (a) soft AO
        #    (0.35+0.65*AO) so occlusion darkens at most to 35%, never to
        #    black; (b) sqrt compression, which lifts the dark end and
        #    compresses the bright end before scaling.
        irr = np.array(img_irr.pixels[:], dtype=np.float32).reshape(-1, 4)
        ao = np.array(img_ao.pixels[:], dtype=np.float32).reshape(-1, 4)
        ao_soft = 0.35 + 0.65 * ao[:, :3]
        rgb = np.sqrt(np.maximum(irr[:, :3] * ao_soft, 0.0))
        atlas = bpy.data.images.new(f"{mat_name}_lightmap", width=size, height=size, alpha=False)
        atlas.colorspace_settings.name = 'Non-Color'
        px = np.zeros((size * size, 4), dtype=np.float32)
        px[:, :3] = rgb
        px[:, 3] = 1.0
        atlas.pixels = px.flatten().tolist()
        # 5) remove the two bake-target images + the node; keep the atlas
        ntree.nodes.remove(tex)
        bpy.data.images.remove(img_irr)
        bpy.data.images.remove(img_ao)
        # 6) NOW restore the colour UV as the active layer (after the bakes)
        #    so the exporter keeps the base-colour texture on TEXCOORD_0
        #    and the lightmap on TEXCOORD_1.
        for o in objs:
            o.data.uv_layers.active = o.data.uv_layers[0]
        bpy.ops.object.select_all(action='DESELECT')
        path = os.path.join(TEX_DIR, f"{mat_name}_lightmap.png")
        atlas.filepath_raw = path
        atlas.file_format = 'PNG'
        atlas.save()
        kept.append((atlas, path))
        log(f"  saved {path} ({os.path.getsize(path)} bytes)")
    # ---- normalisation (v7): percentile-based, robust to the skewed
    #    basement distribution. Scale so the 90th percentile maps to 0.95
    #    (ignores the few extreme hotspots), clamp [0.08, 1.0]. The mean
    #    lands wherever it lands (~0.4-0.6); the page compensates with
    #    envIntensity. v6's mean-based scaling destroyed the gradient.
    for atlas, path in kept:
        px = np.array(atlas.pixels[:], dtype=np.float32).reshape(-1, 4)
        vals = px[:, :3].reshape(-1)
        nz = vals[vals > 1e-6]
        if len(nz) == 0:
            log(f"NORM {os.path.basename(path)}: all ~0, left as-is")
            continue
        p90 = float(np.percentile(nz, 90))
        mean_before = float(vals.mean())
        px[:, :3] = np.clip(px[:, :3] * (0.95 / p90), 0.08, 1.0)
        px[:, 3] = 1.0
        atlas.pixels = px.flatten().tolist()
        atlas.filepath_raw = path
        atlas.file_format = 'PNG'
        atlas.save()
        log(f"NORM {os.path.basename(path)}: p90 {p90:.4f} -> 0.95, mean {mean_before:.4f} -> {float(px[:, :3].mean()):.3f} (clamped 0.08..1.0)")
    # ---- save the baked .blend + export the baked GLB ----
    blend_path = os.path.join(OUT_DIR, "design2121_v17_lighting.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    log(f"saved blend {blend_path}")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT_DIR, "design2121_v17_baked.glb"),
        export_format='GLB', use_selection=True, export_yup=True,
        export_apply=False, export_animations=False,
        export_texcoords=True, export_normals=True,
        export_materials='EXPORT', export_image_format='AUTO',
        export_cameras=False, export_lights=False)
    log("exported design2121_v17_baked.glb")
    log("=== BAKE COMPLETE ===")

main()
