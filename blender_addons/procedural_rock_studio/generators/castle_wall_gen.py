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
                               bevel_radius=0.03, chip_noise=0.015,
                               seed=0, mat_idx=0):
    rng = random.Random(seed)
    res = bmesh.ops.create_cube(bm, size=1.0)
    verts = res['verts']
    wx = width * rng.uniform(0.92, 1.08)
    hy = height * rng.uniform(0.92, 1.08)
    dz = depth * rng.uniform(0.92, 1.08)
    bmesh.ops.scale(bm, vec=(wx, dz, hy), verts=verts)
    bmesh.ops.bevel(
        bm,
        geom=bm.edges[:] + bm.verts[:],
        offset=bevel_radius * rng.uniform(0.7, 1.3),
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

def build_stone_block_assets(base_name, seed=0, style='ASHLAR', mat_stone=None):
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
        ('Ashlar_Large_A', 0.65, 0.32, 0.38, 0.035, 0.015),
        ('Ashlar_Large_B', 0.72, 0.30, 0.36, 0.030, 0.014),
        ('Ashlar_Mid_A',   0.45, 0.26, 0.32, 0.025, 0.012),
        ('Ashlar_Mid_B',   0.40, 0.28, 0.34, 0.028, 0.013),
        ('Cobble_Small',   0.24, 0.20, 0.26, 0.040, 0.018),
        ('Corner_Quoin',   0.55, 0.38, 0.42, 0.035, 0.015),
    ]
    for suffix, w, h, d, bev, chip in defs:
        bm = bmesh.new()
        build_chiseled_stone_block(
            bm, width=w, height=h, depth=d,
            bevel_radius=bev, chip_noise=chip,
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
    mat_mortar_idx=0
):
    half_l = length * 0.5
    half_t = thickness * 0.5
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
    else:
        res = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(length, thickness, height), verts=res['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, height * 0.5), verts=res['verts'])
        if crenels:
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

    for f in bm.faces:
        f.material_index = mat_mortar_idx
        f.smooth = True
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=1, use_grid_fill=True)
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
    length=6.0,
    height=3.5,
    thickness=1.2,
    crenels=True,
    density=22.0,
    min_dist=0.22,
    jitter=0.04,
    target_obj=None
):
    col = context.collection
    mat_stone = get_or_create_castle_stone_mat(name + '_Stone_Mat')
    mat_mortar = get_or_create_castle_mortar_mat(name + '_Mortar_Mat')

    stone_col = build_stone_block_assets(name, seed=seed, style=wall_style, mat_stone=mat_stone)
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
            crenels=crenels, seed=seed, mat_mortar_idx=0
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
            crenels=crenels, seed=seed, mat_mortar_idx=0
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
