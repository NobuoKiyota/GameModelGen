import bpy
import bmesh
import math
import mathutils
from mathutils import Vector, Matrix, Euler
import random

# ==============================================================================
# 1. Cave Path Waypoints Generator (洞窟骨格パス生成)
# ==============================================================================

def generate_cave_path_waypoints(path_type='STRAIGHT_S', length=25.0, slope=2.0,
                                 chamber_scale=2.2, num_steps=32, seed=0):
    rng = random.Random(seed)
    waypoints = []

    freq1 = 2.5 * math.pi / max(5.0, length)
    freq2 = 5.0 * math.pi / max(5.0, length)
    ph_x1 = rng.uniform(0, 10.0)
    ph_x2 = rng.uniform(0, 10.0)

    for i in range(num_steps):
        t = i / float(num_steps - 1)  # 0.0 to 1.0
        y_pos = (t - 0.5) * length

        # 基本のS字カーブ横揺れ
        curve_x = (
            math.sin(y_pos * freq1 + ph_x1) * 3.5 +
            math.sin(y_pos * freq2 + ph_x2) * 1.5
        )

        # 立体的な傾斜（上り/下り坂）
        curve_z = t * slope + math.cos(y_pos * freq1 + ph_x2) * 1.0

        rad_scale = 1.0

        if path_type == 'CHAMBER_HALL':
            # 中央（t=0.35〜0.65）で大空洞（Chamber）に広がる
            dist_from_center = abs(t - 0.5)
            if dist_from_center < 0.25:
                w = math.cos(dist_from_center / 0.25 * math.pi * 0.5)
                rad_scale = 1.0 + (chamber_scale - 1.0) * w
                curve_z += (rad_scale - 1.0) * 1.2
        elif path_type == 'FORK_Y':
            # Y字分岐（幹から途中で枝分かれするカーブ）
            if t > 0.4:
                branch_factor = (t - 0.4) / 0.6
                curve_x += math.sin(branch_factor * math.pi * 0.5) * 6.0
                rad_scale = 1.0 + math.sin(branch_factor * math.pi) * 0.35

        pt = Vector((curve_x, y_pos, curve_z))
        waypoints.append((pt, rad_scale))

    return waypoints


# ==============================================================================
# 2. Cave Tube Mesh Extrusion (チューブ押し出し & 空洞構築)
# ==============================================================================

def build_cave_tube_bmesh(waypoints, base_width=6.0, base_height=4.5,
                          cross_segments=20, seed=0):
    rng = random.Random(seed)
    bm = bmesh.new()

    rings = []
    num_wp = len(waypoints)

    for i in range(num_wp):
        pt, rad_scale = waypoints[i]

        # 進行方向（接線ベクトル）の計算
        if i == 0:
            tangent = (waypoints[1][0] - pt).normalized()
        elif i == num_wp - 1:
            tangent = (pt - waypoints[i - 1][0]).normalized()
        else:
            tangent = (waypoints[i + 1][0] - waypoints[i - 1][0]).normalized()

        up_approx = Vector((0, 0, 1))
        right = tangent.cross(up_approx)
        if right.length < 0.001:
            right = Vector((1, 0, 0))
        else:
            right.normalize()
        up = right.cross(tangent).normalized()

        rx = (base_width * 0.5) * rad_scale * rng.uniform(0.92, 1.08)
        rz = (base_height * 0.5) * rad_scale * rng.uniform(0.92, 1.08)

        ring_verts = []
        for s in range(cross_segments):
            angle = 2.0 * math.pi * (s / float(cross_segments))
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)

            # 底面（sin_a < 0）は平らに潰して歩ける床にする
            local_z = sin_a * rz
            if sin_a < 0:
                local_z *= 0.55

            local_x = cos_a * rx

            v_pos = pt + right * local_x + up * local_z
            v = bm.verts.new(v_pos)
            ring_verts.append(v)

        rings.append(ring_verts)

    bm.verts.ensure_lookup_table()

    # フェイス作成時に床属性 (is_floor) を整然とタグ付け
    floor_layer = bm.faces.layers.int.new("is_floor")

    for i in range(num_wp - 1):
        r0 = rings[i]
        r1 = rings[i + 1]
        for s in range(cross_segments):
            s_next = (s + 1) % cross_segments
            v0 = r0[s]
            v1 = r0[s_next]
            v2 = r1[s_next]
            v3 = r1[s]
            f = bm.faces.new((v0, v3, v2, v1))

            # 底面 (s / cross_segments ~= 0.75) を中心とした下半周を床とする
            norm_s = (s + 0.5) / float(cross_segments)
            dist_to_bottom = abs(norm_s - 0.75)
            if dist_to_bottom > 0.5:
                dist_to_bottom = abs(dist_to_bottom - 1.0)

            # 底面を中心とした円周の55%を下部床面（Floor）、上部45%を天井（Ceiling）に綺麗に二分
            f[floor_layer] = 1 if dist_to_bottom <= 0.28 else 0

    bm.faces.ensure_lookup_table()
    return bm


# ==============================================================================
# 3. Organic Cave Deformation (岩肌凹凸・うねり・棚状段差)
# ==============================================================================

def apply_organic_cave_noise(bm, roughness=0.35, seed=0):
    if roughness <= 0.001:
        return

    rng = random.Random(seed)
    ph1 = rng.uniform(0, 20.0)
    ph2 = rng.uniform(0, 20.0)
    ph3 = rng.uniform(0, 20.0)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    for v in bm.verts:
        # 低周波ノイズ（大きな岩盤のうねり・棚）
        f1 = 0.25
        wave1 = (
            math.sin(v.co.x * f1 + ph1) * math.cos(v.co.y * f1 + ph2) +
            math.sin(v.co.z * f1 * 1.5 + ph3) * 0.5
        ) * roughness * 1.4

        # 中周波ノイズ（角張った岩の割れ目・ゴツゴツ）
        f2 = 0.75
        wave2 = (
            math.sin(v.co.x * f2 + ph2) * math.sin(v.co.z * f2 + ph1)
        ) * roughness * 0.6

        # 高周波微細凹凸（岩肌チッピング）
        micro_noise = rng.uniform(-0.04, 0.04) * roughness * 2.0

        disp = wave1 + wave2 + micro_noise
        v.co += v.normal * disp

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()


# ==============================================================================
# 4. Floor & Ceiling Separation (地面と天井・壁の自動分離)
# ==============================================================================

def separate_cave_floor_and_ceiling(bm_cave, floor_normal_threshold=0.25):
    bm_floor = bmesh.new()
    bm_ceiling = bmesh.new()

    floor_layer = bm_cave.faces.layers.int.get("is_floor")
    floor_faces = []
    ceiling_faces = []

    for f in bm_cave.faces:
        if floor_layer and f[floor_layer] == 1:
            floor_faces.append(f)
        else:
            ceiling_faces.append(f)

    vert_map_floor = {}
    for f in floor_faces:
        face_verts = []
        for v in f.verts:
            if v not in vert_map_floor:
                vert_map_floor[v] = bm_floor.verts.new(v.co)
            face_verts.append(vert_map_floor[v])
        try:
            bm_floor.faces.new(face_verts)
        except Exception:
            pass

    vert_map_ceil = {}
    for f in ceiling_faces:
        face_verts = []
        for v in f.verts:
            if v not in vert_map_ceil:
                vert_map_ceil[v] = bm_ceiling.verts.new(v.co)
            face_verts.append(vert_map_ceil[v])
        try:
            bm_ceiling.faces.new(face_verts)
        except Exception:
            pass

    bm_floor.verts.ensure_lookup_table()
    bm_floor.faces.ensure_lookup_table()
    bm_ceiling.verts.ensure_lookup_table()
    bm_ceiling.faces.ensure_lookup_table()

    for f in bm_floor.faces:
        f.smooth = True
    for f in bm_ceiling.faces:
        f.smooth = True

    return bm_floor, bm_ceiling


# ==============================================================================
# 5. Materials (仮の暗色岩石マテリアル)
# ==============================================================================

def get_or_create_cave_material(mat_name, is_floor=False):
    mat = bpy.data.materials.get(mat_name)
    if mat and mat.node_tree:
        return mat
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    n_out = tree.nodes.new('ShaderNodeOutputMaterial')
    n_out.location = (400, 0)
    n_bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')
    n_bsdf.location = (100, 0)
    tree.links.new(n_bsdf.outputs['BSDF'], n_out.inputs['Surface'])

    n_coord = tree.nodes.new('ShaderNodeTexCoord')
    n_coord.location = (-700, 0)
    n_noise = tree.nodes.new('ShaderNodeTexNoise')
    n_noise.location = (-500, 0)
    n_noise.inputs['Scale'].default_value = 5.0
    n_noise.inputs['Detail'].default_value = 4.0
    n_noise.inputs['Roughness'].default_value = 0.7
    tree.links.new(n_coord.outputs['Object'], n_noise.inputs['Vector'])

    n_ramp = tree.nodes.new('ShaderNodeValToRGB')
    n_ramp.location = (-250, 100)
    if is_floor:
        n_ramp.color_ramp.elements[0].color = (0.12, 0.11, 0.10, 1.0)
        n_ramp.color_ramp.elements[1].color = (0.28, 0.25, 0.22, 1.0)
        n_bsdf.inputs['Roughness'].default_value = 0.70
    else:
        n_ramp.color_ramp.elements[0].color = (0.15, 0.15, 0.16, 1.0)
        n_ramp.color_ramp.elements[1].color = (0.32, 0.31, 0.30, 1.0)
        n_bsdf.inputs['Roughness'].default_value = 0.88

    tree.links.new(n_noise.outputs['Fac'], n_ramp.inputs['Fac'])
    tree.links.new(n_ramp.outputs['Color'], n_bsdf.inputs['Base Color'])

    n_bump = tree.nodes.new('ShaderNodeBump')
    n_bump.location = (-100, -150)
    n_bump.inputs['Strength'].default_value = 0.35
    n_bump.inputs['Distance'].default_value = 0.05
    tree.links.new(n_noise.outputs['Fac'], n_bump.inputs['Height'])
    tree.links.new(n_bump.outputs['Normal'], n_bsdf.inputs['Normal'])

    return mat


# ==============================================================================
# 6. Main Cave Scene Builder (シーン配置 & 堆積防止)
# ==============================================================================

def create_procedural_cave_scene(
    context,
    name="Cave",
    seed=0,
    path_type='STRAIGHT_S',
    length=25.0,
    width=6.0,
    height=4.5,
    slope=2.0,
    chamber_scale=2.2,
    roughness=0.35,
    separate_ceiling=True,
    target_obj=None
):
    col = context.collection

    waypoints = generate_cave_path_waypoints(
        path_type=path_type,
        length=length,
        slope=slope,
        chamber_scale=chamber_scale,
        num_steps=32,
        seed=seed
    )

    bm_cave = build_cave_tube_bmesh(
        waypoints=waypoints,
        base_width=width,
        base_height=height,
        cross_segments=20,
        seed=seed
    )

    apply_organic_cave_noise(bm_cave, roughness=roughness, seed=seed)

    bm_floor, bm_ceiling = separate_cave_floor_and_ceiling(bm_cave, floor_normal_threshold=0.25)
    bm_cave.free()

    mat_floor = get_or_create_cave_material(name + "_Floor_Mat", is_floor=True)
    mat_ceiling = get_or_create_cave_material(name + "_Ceiling_Mat", is_floor=False)

    floor_obj_name = name + "_Floor"
    ceiling_obj_name = name + "_Ceiling"

    floor_obj = bpy.data.objects.get(floor_obj_name)
    if floor_obj and floor_obj.type == 'MESH':
        bm_floor.to_mesh(floor_obj.data)
        floor_obj.data.update()
    else:
        mesh_floor = bpy.data.meshes.new(floor_obj_name)
        bm_floor.to_mesh(mesh_floor)
        floor_obj = bpy.data.objects.new(floor_obj_name, mesh_floor)
        col.objects.link(floor_obj)

    ceiling_obj = bpy.data.objects.get(ceiling_obj_name)
    if ceiling_obj and ceiling_obj.type == 'MESH':
        bm_ceiling.to_mesh(ceiling_obj.data)
        ceiling_obj.data.update()
    else:
        mesh_ceiling = bpy.data.meshes.new(ceiling_obj_name)
        bm_ceiling.to_mesh(mesh_ceiling)
        ceiling_obj = bpy.data.objects.new(ceiling_obj_name, mesh_ceiling)
        col.objects.link(ceiling_obj)

    bm_floor.free()
    bm_ceiling.free()

    if floor_obj.data.materials:
        floor_obj.data.materials[0] = mat_floor
    else:
        floor_obj.data.materials.append(mat_floor)

    if ceiling_obj.data.materials:
        ceiling_obj.data.materials[0] = mat_ceiling
    else:
        ceiling_obj.data.materials.append(mat_ceiling)

    context.view_layer.objects.active = floor_obj
    floor_obj.select_set(True)
    ceiling_obj.select_set(False)

    return floor_obj, ceiling_obj
