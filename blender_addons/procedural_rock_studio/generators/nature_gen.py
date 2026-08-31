import bpy
import bmesh
import math
import mathutils
import random
import os
import addon_utils
from ..materials.nature_shaders import (
    create_procedural_bark_material,
    create_procedural_leaf_material,
    create_procedural_grass_blade_shader,
    create_procedural_ground_terrain_shader,
    create_procedural_water_shader,
    create_procedural_water_bed_shader
)
from ..utils.texture_utils import get_textures_from_folder

def build_grass_terrain_ground(bm, size_x, size_y, seed=0, undulation=0.35, subdivisions=12):
    """自然な起伏地面（頂点変位）"""
    random.seed(seed)
    half_x = size_x * 0.5
    half_y = size_y * 0.5
    step_x = size_x / subdivisions
    step_y = size_y / subdivisions
    verts = []
    for iy in range(subdivisions + 1):
        row = []
        for ix in range(subdivisions + 1):
            x = -half_x + ix * step_x
            y = -half_y + iy * step_y
            nx = (math.sin(x * 0.55 + seed * 0.1) * math.cos(y * 0.45 + seed * 0.07)
                + math.sin(x * 1.3 + seed * 0.3) * math.cos(y * 1.1 + seed * 0.2) * 0.35
                + math.sin(x * 2.7 + seed * 0.7) * math.cos(y * 2.3 + seed * 0.5) * 0.12)
            z = nx * undulation
            row.append(bm.verts.new((x, y, z)))
        verts.append(row)
    for iy in range(subdivisions):
        for ix in range(subdivisions):
            bm.faces.new((verts[iy][ix], verts[iy][ix+1], verts[iy+1][ix+1], verts[iy+1][ix]))
    bm.verts.ensure_lookup_table()
    return [v for row in verts for v in row]


def build_grass_blade_with_uv(bm, uv_layer, height=0.6, base_width=0.04, curve_x=0.0, curve_y=0.08, seed=0):
    """UV付き5点先細りブレード"""
    rng = random.Random(seed)
    h = height * rng.uniform(0.82, 1.18)
    bw = base_width * rng.uniform(0.8, 1.2)
    mid_h = h * 0.55
    mid_curve_x = curve_x * rng.uniform(0.6, 1.0)
    mid_curve_y = curve_y * rng.uniform(0.6, 1.0)
    tip_curve_x = curve_x * rng.uniform(0.9, 1.3)
    tip_curve_y = curve_y * rng.uniform(0.9, 1.4)

    v_bl  = bm.verts.new((-bw * 0.5, 0.0, 0.0))
    v_br  = bm.verts.new(( bw * 0.5, 0.0, 0.0))
    v_ml  = bm.verts.new((-bw * 0.25 + mid_curve_x, mid_curve_y, mid_h))
    v_mr  = bm.verts.new(( bw * 0.25 + mid_curve_x, mid_curve_y, mid_h))
    v_tip = bm.verts.new((tip_curve_x, tip_curve_y, h))

    f_bot = bm.faces.new((v_bl, v_br, v_mr, v_ml))
    f_top = bm.faces.new((v_ml, v_mr, v_tip))
    bm.faces.ensure_lookup_table()

    for face, verts_uv in [(f_bot, [(0.0, 0.0), (1.0, 0.0), (1.0, 0.5), (0.0, 0.5)]),
                           (f_top, [(0.0, 0.5), (1.0, 0.5), (0.5, 1.0)])]:
        for loop, uv in zip(face.loops, verts_uv):
            loop[uv_layer].uv = uv

    return [v_bl, v_br, v_ml, v_mr, v_tip]


def build_grass_tuft_clump(bm, size_x, size_y, size_z, blade_count=5, seed=0):
    """草の株 (Tuft/Clump)"""
    random.seed(seed)
    uv_layer = bm.loops.layers.uv.verify()
    blade_count = max(3, min(8, blade_count))
    angles = [i * (180.0 / blade_count) for i in range(blade_count)]
    for i, ang in enumerate(angles):
        ang_rad = math.radians(ang + random.uniform(-12.0, 12.0))
        height   = size_z * random.uniform(0.82, 1.22)
        base_w   = max(size_x, size_y) * 0.06 * random.uniform(0.8, 1.2)
        cx = math.cos(ang_rad + math.pi * 0.5) * random.uniform(0.01, 0.025)
        cy = math.sin(ang_rad + math.pi * 0.5) * random.uniform(0.01, 0.025)
        blade_verts = build_grass_blade_with_uv(bm, uv_layer, height=height, base_width=base_w,
                                                 curve_x=cx, curve_y=cy, seed=seed + i * 37)
        offset_x = random.uniform(-size_x * 0.06, size_x * 0.06)
        offset_y = random.uniform(-size_y * 0.06, size_y * 0.06)
        bmesh.ops.translate(bm, vec=(offset_x, offset_y, 0.0), verts=blade_verts)
    return bm.verts[:]


def build_grass_mound_base(bm, size_x, size_y, size_z, shape="SQUARE", seed=0):
    """草地丘陵地面テレイン"""
    return build_grass_terrain_ground(bm, size_x, size_y, seed=seed,
                                      undulation=size_z * 0.18, subdivisions=14)


def build_water_surface_base(bm, size_x, size_y, size_z, shape="LAKE", seed=0, include_bed=True):
    """水面形状ビルダー (LAKE, POND, SQUARE, CIRCLE, OCEAN)"""
    random.seed(seed)
    subdiv = 16
    half_x = size_x * 0.5
    half_y = size_y * 0.5

    if shape == "SQUARE":
        step_x = size_x / float(subdiv)
        step_y = size_y / float(subdiv)
        verts = []
        for iy in range(subdiv + 1):
            row = []
            for ix in range(subdiv + 1):
                x = -half_x + ix * step_x
                y = -half_y + iy * step_y
                z = (math.sin(x * 1.8 + seed * 0.2) * math.cos(y * 1.5 + seed * 0.3)) * (size_z * 0.05)
                row.append(bm.verts.new((x, y, z)))
            verts.append(row)
        for iy in range(subdiv):
            for ix in range(subdiv):
                bm.faces.new((verts[iy][ix], verts[iy][ix+1], verts[iy+1][ix+1], verts[iy+1][ix]))

    elif shape == "CIRCLE":
        rings = 8
        segments = 24
        center_v = bm.verts.new((0.0, 0.0, 0.0))
        prev_ring = [center_v] * segments
        for r in range(1, rings + 1):
            cur_ring = []
            rad_ratio = r / float(rings)
            for s in range(segments):
                ang = s * (math.pi * 2.0 / segments)
                rx = math.cos(ang) * half_x * rad_ratio
                ry = math.sin(ang) * half_y * rad_ratio
                rz = (math.sin(rx * 2.0 + seed * 0.3) * math.cos(ry * 2.0 + seed * 0.4)) * (size_z * 0.04)
                cur_ring.append(bm.verts.new((rx, ry, rz)))
            
            if r == 1:
                for s in range(segments):
                    s_next = (s + 1) % segments
                    bm.faces.new((center_v, cur_ring[s], cur_ring[s_next]))
            else:
                for s in range(segments):
                    s_next = (s + 1) % segments
                    bm.faces.new((prev_ring[s], cur_ring[s], cur_ring[s_next], prev_ring[s_next]))
            prev_ring = cur_ring

    elif shape == "POND":
        rings = 10
        segments = 28
        center_v = bm.verts.new((0.0, 0.0, 0.0))
        prev_ring = [center_v] * segments
        for r in range(1, rings + 1):
            cur_ring = []
            rad_ratio = r / float(rings)
            for s in range(segments):
                ang = s * (math.pi * 2.0 / segments)
                coast_noise = (1.0 + math.sin(ang * 3.0 + seed * 0.7) * 0.12
                                   + math.cos(ang * 5.0 + seed * 0.3) * 0.08)
                rx = math.cos(ang) * half_x * rad_ratio * coast_noise
                ry = math.sin(ang) * half_y * rad_ratio * coast_noise
                rz = (math.sin(rx * 1.5) * math.cos(ry * 1.5)) * (size_z * 0.03)
                cur_ring.append(bm.verts.new((rx, ry, rz)))

            if r == 1:
                for s in range(segments):
                    s_next = (s + 1) % segments
                    bm.faces.new((center_v, cur_ring[s], cur_ring[s_next]))
            else:
                for s in range(segments):
                    s_next = (s + 1) % segments
                    bm.faces.new((prev_ring[s], cur_ring[s], cur_ring[s_next], prev_ring[s_next]))
            prev_ring = cur_ring

        if include_bed:
            bed_depth = size_z * 0.8
            bed_center = bm.verts.new((0.0, 0.0, -bed_depth))
            prev_bed_ring = [bed_center] * segments
            for r in range(1, rings + 1):
                cur_bed_ring = []
                rad_ratio = r / float(rings)
                for s in range(segments):
                    ang = s * (math.pi * 2.0 / segments)
                    coast_noise = (1.0 + math.sin(ang * 3.0 + seed * 0.7) * 0.12
                                       + math.cos(ang * 5.0 + seed * 0.3) * 0.08)
                    rx = math.cos(ang) * half_x * 1.15 * rad_ratio * coast_noise
                    ry = math.sin(ang) * half_y * 1.15 * rad_ratio * coast_noise
                    rz = -bed_depth * (1.0 - (rad_ratio ** 1.8)) - (size_z * 0.08)
                    cur_bed_ring.append(bm.verts.new((rx, ry, rz)))

                if r == 1:
                    for s in range(segments):
                        s_next = (s + 1) % segments
                        f = bm.faces.new((bed_center, cur_bed_ring[s_next], cur_bed_ring[s]))
                        f.material_index = 1
                else:
                    for s in range(segments):
                        s_next = (s + 1) % segments
                        f = bm.faces.new((prev_bed_ring[s], prev_bed_ring[s_next], cur_bed_ring[s_next], cur_bed_ring[s]))
                        f.material_index = 1
                prev_bed_ring = cur_bed_ring

    elif shape == "OCEAN":
        step_x = size_x / float(subdiv)
        step_y = size_y / float(subdiv)
        verts = []
        for iy in range(subdiv + 1):
            row = []
            for ix in range(subdiv + 1):
                x = -half_x + ix * step_x
                y = -half_y + iy * step_y
                row.append(bm.verts.new((x, y, 0.0)))
            verts.append(row)
        for iy in range(subdiv):
            for ix in range(subdiv):
                bm.faces.new((verts[iy][ix], verts[iy][ix+1], verts[iy+1][ix+1], verts[iy+1][ix]))

    else: # LAKE
        step_x = size_x / float(subdiv)
        step_y = size_y / float(subdiv)
        verts = []
        for iy in range(subdiv + 1):
            row = []
            for ix in range(subdiv + 1):
                x = -half_x + ix * step_x
                y = -half_y + iy * step_y
                z = (math.sin(x * 0.8 + seed * 0.15) * math.cos(y * 0.7 + seed * 0.2)
                     + math.sin(x * 2.1 + seed * 0.4) * math.cos(y * 1.8 + seed * 0.3) * 0.35) * (size_z * 0.12)
                row.append(bm.verts.new((x, y, z)))
            verts.append(row)
        for iy in range(subdiv):
            for ix in range(subdiv):
                bm.faces.new((verts[iy][ix], verts[iy][ix+1], verts[iy+1][ix+1], verts[iy+1][ix]))

    return bm.verts[:]


def generate_sapling_real_tree(
    context,
    target_obj=None,
    name="Real_Tree",
    species="OAK",
    has_leaves=True,
    leaf_count=120,
    branch_levels=2,
    mat_mode="PROCEDURAL",
    seed=0,
    size_z=4.5
):
    """Sapling Tree Gen によるプロシージャル樹木生成"""
    if context.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

    try:
        addon_utils.enable("add_curve_sapling", default_set=True)
    except Exception:
        pass

    old_loc = target_obj.location.copy() if target_obj else mathutils.Vector((0, 0, 0))
    old_rot = target_obj.rotation_euler.copy() if target_obj else mathutils.Euler((0, 0, 0))
    old_name = target_obj.name if target_obj else name

    for obj in list(bpy.data.objects):
        if obj.name in ('tree', 'leaves') or "treemesh" in obj.name.lower() or "leavesmesh" in obj.name.lower():
            bpy.data.objects.remove(obj, do_unlink=True)
    if target_obj and target_obj in bpy.data.objects.values():
        bpy.data.objects.remove(target_obj, do_unlink=True)

    rng = random.Random(seed)
    num_l = max(20, min(300, leaf_count if not target_obj else leaf_count + rng.randint(-15, 25)))
    bl = max(1, min(3, branch_levels))

    leaf_shapes = ['hex', 'rect', 'dFace', 'dVert']
    chosen_leaf_shape = rng.choice(leaf_shapes)
    rand_leaf_scale = rng.uniform(0.25, 0.45)
    rand_leaf_scale_x = rng.uniform(0.5, 1.0)
    rand_leaf_down_angle = rng.uniform(30.0, 75.0)

    base_scale = max(2.5, size_z)

    if species == "PINE":
        tree_args = {
            'do_update': True, 'bevel': True, 'bevelRes': 1, 'resU': 2,
            'curveRes': (4, 3, 2, 1), 'levels': bl, 'branches': (35, 12, 0, 0),
            'scale': base_scale, 'scale0': 1.0, 'shape': '7', 'baseSize': 0.25,
            'downAngle': (75.0 + rng.uniform(-10, 10), 45.0, 0.0, 0.0),
            'rotate': (140.0, 140.0, 0.0, 0.0), 'showLeaves': has_leaves,
            'leaves': num_l, 'leafScale': rand_leaf_scale * 0.75,
            'leafScaleX': 0.35, 'leafShape': 'dFace',
            'leafDownAngle': rand_leaf_down_angle, 'seed': seed, 'makeMesh': True
        }
    elif species == "WILLOW":
        tree_args = {
            'do_update': True, 'bevel': True, 'bevelRes': 1, 'resU': 2,
            'curveRes': (4, 3, 2, 1), 'levels': bl, 'branches': (28, 16, 8, 0),
            'scale': base_scale, 'scale0': 1.0, 'shape': '2', 'baseSize': 0.35,
            'curve': (-30.0 + rng.uniform(-10, 5), -45.0, 0.0, 0.0),
            'downAngle': (-15.0, 105.0 + rng.uniform(-15, 15), 45.0, 0.0),
            'rotate': (137.5, 137.5, 0.0, 0.0), 'showLeaves': has_leaves,
            'leaves': num_l, 'leafScale': rand_leaf_scale,
            'leafScaleX': rand_leaf_scale_x * 0.7, 'leafShape': chosen_leaf_shape,
            'leafDownAngle': rand_leaf_down_angle + 20.0, 'seed': seed, 'makeMesh': True
        }
    elif species == "JAPANESE_MAPLE":
        tree_args = {
            'do_update': True, 'bevel': True, 'bevelRes': 1, 'resU': 2,
            'curveRes': (4, 3, 2, 1), 'levels': bl, 'branches': (22, 14, 6, 0),
            'scale': base_scale, 'scale0': 1.0, 'baseSplits': 2,
            'splitAngle': (35.0, 30.0, 0.0, 0.0),
            'downAngle': (55.0 + rng.uniform(-10, 10), 60.0, 45.0, 0.0),
            'rotate': (137.5, 137.5, 0.0, 0.0), 'showLeaves': has_leaves,
            'leaves': num_l, 'leafScale': rand_leaf_scale * 0.85,
            'leafScaleX': rand_leaf_scale_x, 'leafShape': 'hex',
            'leafDownAngle': rand_leaf_down_angle, 'seed': seed, 'makeMesh': True
        }
    elif species == "BIRCH":
        tree_args = {
            'do_update': True, 'bevel': True, 'bevelRes': 1, 'resU': 2,
            'curveRes': (4, 3, 2, 1), 'levels': bl, 'branches': (24, 12, 0, 0),
            'scale': base_scale, 'scale0': 1.0, 'shape': '4', 'baseSize': 0.45,
            'downAngle': (50.0 + rng.uniform(-10, 10), 45.0, 0.0, 0.0),
            'rotate': (137.5, 137.5, 0.0, 0.0), 'showLeaves': has_leaves,
            'leaves': num_l, 'leafScale': rand_leaf_scale * 0.9,
            'leafScaleX': rand_leaf_scale_x, 'leafShape': chosen_leaf_shape,
            'leafDownAngle': rand_leaf_down_angle, 'seed': seed, 'makeMesh': True
        }
    else: # OAK
        tree_args = {
            'do_update': True, 'bevel': True, 'bevelRes': 1, 'resU': 2,
            'curveRes': (4, 3, 2, 1), 'levels': bl, 'branches': (25, 15, 6, 0),
            'scale': base_scale, 'scale0': 1.0, 'baseSplits': 2,
            'splitAngle': (30.0 + rng.uniform(-8, 8), 25.0, 0.0, 0.0),
            'downAngle': (45.0 + rng.uniform(-10, 10), 50.0, 35.0, 0.0),
            'rotate': (137.5, 137.5, 0.0, 0.0), 'showLeaves': has_leaves,
            'leaves': num_l, 'leafScale': rand_leaf_scale,
            'leafScaleX': rand_leaf_scale_x, 'leafShape': chosen_leaf_shape,
            'leafDownAngle': rand_leaf_down_angle, 'seed': seed, 'makeMesh': True
        }

    try:
        bpy.ops.curve.tree_add(**tree_args)
    except Exception as e:
        print("Sapling Tree Gen call error:", e)

    tree_obj = bpy.data.objects.get('tree')
    leaves_obj = bpy.data.objects.get('leaves')

    if tree_obj and tree_obj.type == 'CURVE':
        bpy.ops.object.select_all(action='DESELECT')
        tree_obj.select_set(True)
        context.view_layer.objects.active = tree_obj
        bpy.ops.object.convert(target='MESH')

    if tree_obj:
        mat_bark = create_procedural_bark_material(old_name + "_Bark_Procedural", seed=seed, species=species)
        if tree_obj.data.materials:
            tree_obj.data.materials[0] = mat_bark
        else:
            tree_obj.data.materials.append(mat_bark)

    if leaves_obj and has_leaves:
        mat_leaf = create_procedural_leaf_material(old_name + "_Leaf_Procedural", seed=seed, species=species)
        if leaves_obj.data.materials:
            leaves_obj.data.materials[0] = mat_leaf
        else:
            leaves_obj.data.materials.append(mat_leaf)

    if tree_obj and leaves_obj and has_leaves:
        bpy.ops.object.select_all(action='DESELECT')
        leaves_obj.select_set(True)
        tree_obj.select_set(True)
        context.view_layer.objects.active = tree_obj
        bpy.ops.object.join()

    final_obj = tree_obj if tree_obj else (leaves_obj if leaves_obj else None)
    if final_obj:
        final_obj.name = old_name
        bpy.ops.object.select_all(action='DESELECT')
        final_obj.select_set(True)
        context.view_layer.objects.active = final_obj
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        final_obj.location = old_loc
        final_obj.rotation_euler = old_rot

    for o in list(bpy.data.objects):
        if o != final_obj and ("treemesh" in o.name.lower() or "leavesmesh" in o.name.lower() or o.name in ('tree', 'leaves')):
            bpy.data.objects.remove(o, do_unlink=True)

    return final_obj
