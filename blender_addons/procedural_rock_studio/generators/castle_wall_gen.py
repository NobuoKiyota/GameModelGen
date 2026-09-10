import bpy
import bmesh
import math
import mathutils
from mathutils import Vector, Matrix, Euler
import random

# ==============================================================================
# 1. Procedural Stone Block Assets Builder (立体石材ブロック)
# ==============================================================================

def build_chiseled_stone_block(bm, width=0.6, height=0.3, depth=0.35,
                               bevel_radius=0.035, chip_noise=0.016,
                               style='ASHLAR', aspect='STANDARD',
                               seed=0, mat_idx=0):
    rng = random.Random(seed)
    res = bmesh.ops.create_cube(bm, size=1.0)
    verts = res['verts']

    # アスペクト比の調整
    aspect_w, aspect_h, aspect_d = 1.0, 1.0, 1.0
    if aspect == 'WIDE':
        aspect_w, aspect_h = 1.35, 0.85
    elif aspect == 'SQUARE':
        aspect_w, aspect_h = 0.85, 1.20
    elif aspect == 'FLAT':
        aspect_w, aspect_h, aspect_d = 1.45, 0.55, 1.15

    # スタイルによる寸法の調整
    if style == 'CYCLOPEAN':
        aspect_w *= 1.4
        aspect_h *= 1.35
        aspect_d *= 1.3
    elif style == 'SLATE':
        aspect_h *= 0.6
        aspect_w *= 1.25

    wx = width * aspect_w * rng.uniform(0.90, 1.10)
    hy = height * aspect_h * rng.uniform(0.90, 1.10)
    dz = depth * aspect_d * rng.uniform(0.90, 1.10)
    bmesh.ops.scale(bm, vec=(wx, dz, hy), verts=verts)

    if style == 'RUBBLE':
        # 野面・丸石: 細分化して丸みを帯びさせる
        bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2, use_grid_fill=True)
        for v in bm.verts:
            n = v.co.normalized()
            v.co = v.co.lerp(n * (wx * 0.45), 0.35)
            v.co.x += rng.uniform(-chip_noise * 1.5, chip_noise * 1.5)
            v.co.y += rng.uniform(-chip_noise * 1.5, chip_noise * 1.5)
            v.co.z += rng.uniform(-chip_noise * 1.5, chip_noise * 1.5)
    else:
        # 切石・スレート・巨石: 面取り（Bevel）とチゼル削り
        bev = bevel_radius
        if style == 'CYCLOPEAN':
            bev *= 1.8
        elif style == 'SLATE':
            bev *= 0.6

        bmesh.ops.bevel(
            bm,
            geom=bm.edges[:] + bm.verts[:],
            offset=bev * rng.uniform(0.75, 1.25),
            segments=2,
            profile=0.5,
            affect='EDGES'
        )
        for v in bm.verts:
            v.co.x += rng.uniform(-chip_noise, chip_noise)
            v.co.y += rng.uniform(-chip_noise, chip_noise)
            v.co.z += rng.uniform(-chip_noise, chip_noise)

    for f in bm.faces:
        f.material_index = mat_idx
        f.smooth = True
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm.verts[:]

def build_stone_block_assets(base_name, seed=0, style='ASHLAR', aspect='STANDARD',
                            roundness=0.035, chipping=0.016, mat_stone=None):
    col_name = base_name + '_StoneAssets'
    if col_name in bpy.data.collections:
        old_col = bpy.data.collections[col_name]
        for obj in list(old_col.objects):
            mesh = obj.data if obj.type == 'MESH' else None
            bpy.data.objects.remove(obj, do_unlink=True)
            if mesh and mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        bpy.data.collections.remove(old_col)

    stone_col = bpy.data.collections.new(col_name)
    bpy.context.scene.collection.children.link(stone_col)
    rng = random.Random(seed)

    defs = [
        ('Ashlar_Large_A', 0.68, 0.32, 0.38),
        ('Ashlar_Large_B', 0.75, 0.30, 0.36),
        ('Ashlar_Mid_A',   0.48, 0.26, 0.32),
        ('Ashlar_Mid_B',   0.42, 0.28, 0.34),
        ('Cobble_Small',   0.26, 0.20, 0.26),
        ('Corner_Quoin',   0.58, 0.38, 0.42),
    ]
    for suffix, w, h, d in defs:
        bm = bmesh.new()
        build_chiseled_stone_block(
            bm, width=w, height=h, depth=d,
            bevel_radius=roundness, chip_noise=chipping,
            style=style, aspect=aspect,
            seed=rng.randint(1, 99999), mat_idx=0
        )
        mesh = bpy.data.meshes.new(f'{base_name}_{suffix}')
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(f'{base_name}_{suffix}', mesh)
        if mat_stone:
            obj.data.materials.append(mat_stone)
        stone_col.objects.link(obj)
        obj.location = (1000.0, 1000.0, 0.0)

    return stone_col

def apply_organic_wall_deformation(bm, length, height, thickness, seed=0, batter=0.18, roughness=0.14):
    if roughness <= 0.001 and batter <= 0.001:
        return
    rng = random.Random(seed)

    freq_x1 = 2.0 * math.pi / max(0.5, length)
    freq_x2 = 4.5 * math.pi / max(0.5, length)
    freq_z1 = 2.0 * math.pi / max(0.5, height)
    freq_z2 = 4.8 * math.pi / max(0.5, height)

    ph_x1 = rng.uniform(0, 10.0)
    ph_x2 = rng.uniform(0, 10.0)
    ph_z1 = rng.uniform(0, 10.0)
    ph_z2 = rng.uniform(0, 10.0)

    # 局所的な大きな出っ張り（石垣のせり出し・ふくらみ）
    bulge_x1 = rng.uniform(-length * 0.30, length * 0.30)
    bulge_z1 = rng.uniform(height * 0.2, height * 0.7)
    bulge_rad1 = rng.uniform(0.9, 1.8)
    bulge_amp1 = rng.uniform(0.15, 0.35) * max(0.1, roughness) * 2.5

    bulge_x2 = rng.uniform(-length * 0.30, length * 0.30)
    bulge_z2 = rng.uniform(height * 0.1, height * 0.5)
    bulge_rad2 = rng.uniform(0.7, 1.5)
    bulge_amp2 = rng.uniform(0.12, 0.28) * max(0.1, roughness) * 2.5

    for v in bm.verts:
        z_norm = max(0.0, min(1.3, v.co.z / max(0.1, height)))

        # 1. 裾野の末広がり傾斜 (Batter / Slope): 底面ほど外側に広がる
        slope_factor = ((1.0 - min(1.0, z_norm)) ** 1.3) * batter * thickness * 1.6
        if v.co.y > 0.02:
            v.co.y += slope_factor
        elif v.co.y < -0.02:
            v.co.y -= slope_factor

        # 2. 壁面の有機的な波打ち・うねり（Y方向：厚み方向の出っ張り・へこみ）
        wave_y = (
            math.sin(v.co.x * freq_x1 + ph_x1) * math.cos(v.co.z * freq_z1 + ph_z1) * 0.65 +
            math.sin(v.co.x * freq_x2 + ph_x2) * math.sin(v.co.z * freq_z2 + ph_z2) * 0.35
        ) * roughness * thickness * 1.4
        v.co.y += wave_y

        # 3. 局所的な大きな出っ張り（せり出し）
        d1 = math.hypot(v.co.x - bulge_x1, v.co.z - bulge_z1)
        if d1 < bulge_rad1:
            factor1 = (math.cos(math.pi * d1 / bulge_rad1) + 1.0) * 0.5
            if v.co.y > 0.0:
                v.co.y += factor1 * bulge_amp1
            elif v.co.y < 0.0:
                v.co.y -= factor1 * bulge_amp1

        d2 = math.hypot(v.co.x - bulge_x2, v.co.z - bulge_z2)
        if d2 < bulge_rad2:
            factor2 = (math.cos(math.pi * d2 / bulge_rad2) + 1.0) * 0.5
            if v.co.y > 0.0:
                v.co.y += factor2 * bulge_amp2
            elif v.co.y < 0.0:
                v.co.y -= factor2 * bulge_amp2

        # 4. 壁全体の微小な傾き・歪み（X方向の横揺れ・ねじれ）
        wave_x = math.sin(v.co.z * freq_z1 + ph_z1) * roughness * 0.35 * length * 0.08
        v.co.x += wave_x

        # 5. 上部稜線や天面の高低差ゆらぎ（Z方向）
        if v.co.z > 0.1:
            wave_z = math.cos(v.co.x * freq_x1 + ph_x2) * roughness * 0.30 * height * 0.12
            v.co.z += wave_z

        # 6. 微小な手削り岩肌凹凸
        v.co.x += rng.uniform(-roughness * 0.08, roughness * 0.08)
        v.co.y += rng.uniform(-roughness * 0.12, roughness * 0.12)
        if v.co.z > 0.1:
            v.co.z += rng.uniform(-roughness * 0.05, roughness * 0.05)

def build_castle_wall_base_mesh(
    bm,
    shape='STRAIGHT',
    length=6.0,
    height=3.5,
    thickness=1.2,
    crenels=True,
    crenel_width=0.8,
    crenel_height=0.7,
    crenel_gap=0.6,
    seed=0,
    mat_mortar_idx=0,
    batter=0.18,
    roughness=0.14
):
    half_l = length * 0.5
    half_t = thickness * 0.5
    rng = random.Random(seed)
    if shape == 'RANDOM':
        shape = rng.choice(['STRAIGHT', 'BATTLEMENT', 'TOWER_CURVED', 'CORNER_L', 'CRANK_Z', 'GATE_ARCH'])

    if shape == 'TOWER_CURVED':
        radius = length * 0.5
        segments = 24
        r_out = radius + half_t
        r_in = max(0.2, radius - half_t)
        for iz in (0, 1):
            z_pos = 0.0 if iz == 0 else height
            for s in range(segments + 1):
                ang = math.pi * (s / segments)
                vx_out = math.cos(ang) * r_out
                vy_out = math.sin(ang) * r_out
                vx_in = math.cos(ang) * r_in
                vy_in = math.sin(ang) * r_in
                bm.verts.new((vx_out, vy_out, z_pos))
                bm.verts.new((vx_in, vy_in, z_pos))
        v = bm.verts
        v.ensure_lookup_table()
        pts_per_slice = 2
        for s in range(segments):
            i0 = s * pts_per_slice
            i1 = (s + 1) * pts_per_slice
            i2 = (segments + 1) * pts_per_slice + s * pts_per_slice
            i3 = (segments + 1) * pts_per_slice + (s + 1) * pts_per_slice
            bm.faces.new((v[i0], v[i1], v[i3], v[i2]))
            bm.faces.new((v[i1+1], v[i0+1], v[i2+1], v[i3+1]))
            bm.faces.new((v[i2], v[i3], v[i3+1], v[i2+1]))
            bm.faces.new((v[i0+1], v[i1+1], v[i1], v[i0]))
    elif shape == 'CORNER_L':
        res1 = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(length, thickness, height), verts=res1['verts'])
        bmesh.ops.translate(bm, vec=(half_l - half_t, 0, height * 0.5), verts=res1['verts'])
        res2 = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(thickness, length - thickness, height), verts=res2['verts'])
        bmesh.ops.translate(bm, vec=(0, (length - thickness) * 0.5 + half_t, height * 0.5), verts=res2['verts'])
    elif shape == 'CRANK_Z':
        # クランク折れ曲がり壁 (Z字・段差要塞壁)
        seg_w = length * 0.45
        offset_y = thickness * 1.6
        res1 = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(seg_w, thickness, height), verts=res1['verts'])
        bmesh.ops.translate(bm, vec=(-half_l + seg_w * 0.5, 0, height * 0.5), verts=res1['verts'])

        res_conn = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(thickness, offset_y + thickness, height), verts=res_conn['verts'])
        bmesh.ops.translate(bm, vec=(0, offset_y * 0.5, height * 0.5), verts=res_conn['verts'])

        res2 = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(seg_w, thickness, height), verts=res2['verts'])
        bmesh.ops.translate(bm, vec=(half_l - seg_w * 0.5, offset_y, height * 0.5), verts=res2['verts'])
    elif shape == 'GATE_ARCH':
        # 城門アーチ開口壁 (左右の門柱壁 + 上部アーチ梁)
        pier_w = length * 0.32
        open_w = length - pier_w * 2.0
        gate_h = height * 0.65
        lintel_h = height - gate_h

        # 左壁
        res_l = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(pier_w, thickness, height), verts=res_l['verts'])
        bmesh.ops.translate(bm, vec=(-half_l + pier_w * 0.5, 0, height * 0.5), verts=res_l['verts'])

        # 右壁
        res_r = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(pier_w, thickness, height), verts=res_r['verts'])
        bmesh.ops.translate(bm, vec=(half_l - pier_w * 0.5, 0, height * 0.5), verts=res_r['verts'])

        # 上部梁
        res_t = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(open_w, thickness, lintel_h), verts=res_t['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, gate_h + lintel_h * 0.5), verts=res_t['verts'])
    else:
        res = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(length, thickness, height), verts=res['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, height * 0.5), verts=res['verts'])
        if crenels or shape == 'BATTLEMENT':
            step = crenel_width + crenel_gap
            num_crenels = max(2, int(length / step))
            start_x = -((num_crenels - 1) * step) * 0.5
            crenel_thick = thickness * 0.40
            front_y = -half_t + crenel_thick * 0.5
            for ci in range(num_crenels):
                cx = start_x + ci * step
                res_c = bmesh.ops.create_cube(bm, size=1.0)
                bmesh.ops.scale(bm, vec=(crenel_width, crenel_thick, crenel_height), verts=res_c['verts'])
                bmesh.ops.translate(bm, vec=(cx, front_y, height + crenel_height * 0.5), verts=res_c['verts'])

    # 細分化（グリッド分割）して有機的変形を可能にする
    subdiv_cuts = 4 if length <= 10.0 else 6
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=subdiv_cuts, use_grid_fill=True)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # 自然な傾き・裾野の広がり・出っ張り・うねりを付加
    apply_organic_wall_deformation(bm, length=length, height=height, thickness=thickness,
                                  seed=seed, batter=batter, roughness=roughness)

    for f in bm.faces:
        f.material_index = mat_mortar_idx
        f.smooth = True
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm.verts[:]

def create_castle_wall_geometry_nodes(node_tree_name, stone_col, seed=0,
                                     density=20.0, min_dist=0.22, jitter=0.04):
    if node_tree_name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[node_tree_name])

    tree = bpy.data.node_groups.new(node_tree_name, 'GeometryNodeTree')
    tree.inputs.new('NodeSocketGeometry', 'Geometry')
    sock_dens = tree.inputs.new('NodeSocketFloat', 'Density')
    sock_dens.default_value = density
    sock_dens.min_value = 1.0
    sock_seed = tree.inputs.new('NodeSocketInt', 'Seed')
    sock_seed.default_value = seed
    sock_dist = tree.inputs.new('NodeSocketFloat', 'Min Distance')
    sock_dist.default_value = min_dist
    sock_dist.min_value = 0.05
    tree.outputs.new('NodeSocketGeometry', 'Geometry')

    n_in = tree.nodes.new('NodeGroupInput')
    n_out = tree.nodes.new('NodeGroupOutput')
    n_in.location = (-700, 0)
    n_out.location = (900, 0)

    n_dist = tree.nodes.new('GeometryNodeDistributePointsOnFaces')
    n_dist.distribute_method = 'POISSON'
    n_dist.location = (-450, 100)
    tree.links.new(n_in.outputs['Geometry'], n_dist.inputs['Mesh'])
    tree.links.new(n_in.outputs['Density'], n_dist.inputs['Density Max'])
    tree.links.new(n_in.outputs['Min Distance'], n_dist.inputs['Distance Min'])
    tree.links.new(n_in.outputs['Seed'], n_dist.inputs['Seed'])

    n_align = tree.nodes.new('FunctionNodeAlignEulerToVector')
    n_align.axis = 'Y'
    n_align.pivot_axis = 'Z'
    n_align.location = (-200, 150)
    tree.links.new(n_dist.outputs['Normal'], n_align.inputs['Vector'])

    n_col = tree.nodes.new('GeometryNodeCollectionInfo')
    n_col.location = (100, -200)
    n_col.inputs['Collection'].default_value = stone_col
    n_col.inputs['Separate Children'].default_value = True
    n_col.inputs['Reset Children'].default_value = True

    n_rand_scale = tree.nodes.new('FunctionNodeRandomValue')
    n_rand_scale.data_type = 'FLOAT'
    n_rand_scale.inputs[2].default_value = 0.88
    n_rand_scale.inputs[3].default_value = 1.15
    n_rand_scale.location = (100, -400)
    tree.links.new(n_in.outputs['Seed'], n_rand_scale.inputs[8])

    n_inst = tree.nodes.new('GeometryNodeInstanceOnPoints')
    n_inst.location = (380, 100)
    n_inst.inputs['Pick Instance'].default_value = True
    tree.links.new(n_dist.outputs['Points'], n_inst.inputs['Points'])
    tree.links.new(n_col.outputs['Instances'], n_inst.inputs['Instance'])
    tree.links.new(n_align.outputs['Rotation'], n_inst.inputs['Rotation'])
    tree.links.new(n_rand_scale.outputs[1], n_inst.inputs['Scale'])

    n_join = tree.nodes.new('GeometryNodeJoinGeometry')
    n_join.location = (650, 100)
    tree.links.new(n_in.outputs['Geometry'], n_join.inputs['Geometry'])
    tree.links.new(n_inst.outputs['Instances'], n_join.inputs['Geometry'])
    tree.links.new(n_join.outputs['Geometry'], n_out.inputs['Geometry'])
    return tree

def get_or_create_castle_stone_mat(mat_name):
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
    n_noise.inputs['Scale'].default_value = 7.5
    n_noise.inputs['Detail'].default_value = 4.0
    n_noise.inputs['Roughness'].default_value = 0.65
    tree.links.new(n_coord.outputs['Object'], n_noise.inputs['Vector'])

    n_ramp = tree.nodes.new('ShaderNodeValToRGB')
    n_ramp.location = (-250, 100)
    n_ramp.color_ramp.elements[0].position = 0.15
    n_ramp.color_ramp.elements[0].color = (0.24, 0.22, 0.20, 1.0)
    n_ramp.color_ramp.elements[1].position = 0.85
    n_ramp.color_ramp.elements[1].color = (0.52, 0.48, 0.43, 1.0)
    tree.links.new(n_noise.outputs['Fac'], n_ramp.inputs['Fac'])
    tree.links.new(n_ramp.outputs['Color'], n_bsdf.inputs['Base Color'])

    n_bump = tree.nodes.new('ShaderNodeBump')
    n_bump.location = (-100, -150)
    n_bump.inputs['Strength'].default_value = 0.18
    n_bump.inputs['Distance'].default_value = 0.04
    tree.links.new(n_noise.outputs['Fac'], n_bump.inputs['Height'])
    tree.links.new(n_bump.outputs['Normal'], n_bsdf.inputs['Normal'])

    n_bsdf.inputs['Roughness'].default_value = 0.85
    return mat

def get_or_create_castle_mortar_mat(mat_name):
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
    n_noise.inputs['Scale'].default_value = 16.0
    n_noise.inputs['Detail'].default_value = 3.0
    n_noise.inputs['Roughness'].default_value = 0.8
    tree.links.new(n_coord.outputs['Object'], n_noise.inputs['Vector'])

    n_ramp = tree.nodes.new('ShaderNodeValToRGB')
    n_ramp.location = (-250, 100)
    n_ramp.color_ramp.elements[0].color = (0.09, 0.08, 0.07, 1.0)
    n_ramp.color_ramp.elements[1].color = (0.16, 0.15, 0.14, 1.0)
    tree.links.new(n_noise.outputs['Fac'], n_ramp.inputs['Fac'])
    tree.links.new(n_ramp.outputs['Color'], n_bsdf.inputs['Base Color'])

    n_bump = tree.nodes.new('ShaderNodeBump')
    n_bump.location = (-100, -150)
    n_bump.inputs['Strength'].default_value = 0.25
    n_bump.inputs['Distance'].default_value = 0.03
    tree.links.new(n_noise.outputs['Fac'], n_bump.inputs['Height'])
    tree.links.new(n_bump.outputs['Normal'], n_bsdf.inputs['Normal'])

    n_bsdf.inputs['Roughness'].default_value = 0.95
    return mat

def create_castle_wall_scene(
    context,
    name='Castle_Wall',
    seed=0,
    wall_shape='STRAIGHT',
    wall_style='ASHLAR',
    stone_aspect='STANDARD',
    stone_roundness=0.035,
    stone_chipping=0.016,
    length=6.0,
    height=3.5,
    thickness=1.2,
    crenels=True,
    density=22.0,
    min_dist=0.22,
    jitter=0.04,
    batter=0.18,
    roughness=0.14,
    target_obj=None
):
    col = context.collection
    mat_stone = get_or_create_castle_stone_mat(name + '_Stone_Mat')
    mat_mortar = get_or_create_castle_mortar_mat(name + '_Mortar_Mat')

    stone_col = build_stone_block_assets(
        name, seed=seed, style=wall_style, aspect=stone_aspect,
        roundness=stone_roundness, chipping=stone_chipping, mat_stone=mat_stone
    )
    wall_obj_name = name + '_Core'

    if not target_obj:
        act = context.active_object
        if act and act.type == 'MESH' and ('CastleWallScatter' in act.modifiers or '_Core' in act.name):
            target_obj = act

    if target_obj and target_obj.name in bpy.data.objects:
        wall_obj = target_obj
        bm = bmesh.new()
        build_castle_wall_base_mesh(
            bm, shape=wall_shape, length=length, height=height, thickness=thickness,
            crenels=crenels, seed=seed, mat_mortar_idx=0,
            batter=batter, roughness=roughness
        )
        bm.to_mesh(wall_obj.data)
        bm.free()
        wall_obj.data.update()
    else:
        if wall_obj_name in bpy.data.objects:
            old_w = bpy.data.objects[wall_obj_name]
            old_mesh = old_w.data if old_w.type == 'MESH' else None
            bpy.data.objects.remove(old_w, do_unlink=True)
            if old_mesh and old_mesh.users == 0:
                bpy.data.meshes.remove(old_mesh)

        bm = bmesh.new()
        build_castle_wall_base_mesh(
            bm, shape=wall_shape, length=length, height=height, thickness=thickness,
            crenels=crenels, seed=seed, mat_mortar_idx=0,
            batter=batter, roughness=roughness
        )
        mesh = bpy.data.meshes.new(wall_obj_name)
        bm.to_mesh(mesh)
        bm.free()
        wall_obj = bpy.data.objects.new(wall_obj_name, mesh)
        col.objects.link(wall_obj)

    context.view_layer.objects.active = wall_obj
    wall_obj.select_set(True)

    if wall_obj.data.materials:
        wall_obj.data.materials[0] = mat_mortar
    else:
        wall_obj.data.materials.append(mat_mortar)

    gn_mod = wall_obj.modifiers.get('CastleWallScatter')
    if not gn_mod or gn_mod.type != 'NODES':
        gn_mod = wall_obj.modifiers.new('CastleWallScatter', 'NODES')

    gn_tree = create_castle_wall_geometry_nodes(
        name + '_Scatter_GN', stone_col, seed=seed,
        density=density, min_dist=min_dist, jitter=jitter
    )
    gn_mod.node_group = gn_tree
    return wall_obj, stone_col

def convert_castle_wall_to_game_mesh(context, wall_obj):
    if not wall_obj or wall_obj.type != 'MESH':
        return False
    gn_mod = wall_obj.modifiers.get('CastleWallScatter')
    if not gn_mod or gn_mod.type != 'NODES' or not gn_mod.node_group:
        return False
    tree = gn_mod.node_group
    n_real = tree.nodes.new('GeometryNodeRealizeInstances')
    n_join = tree.nodes.get('Join Geometry')
    n_out = tree.nodes.get('Group Output')
    if n_join and n_out:
        tree.links.new(n_join.outputs['Geometry'], n_real.inputs['Geometry'])
        tree.links.new(n_real.outputs['Geometry'], n_out.inputs['Geometry'])
    context.view_layer.objects.active = wall_obj
    bpy.ops.object.modifier_apply(modifier=gn_mod.name)
    return True
