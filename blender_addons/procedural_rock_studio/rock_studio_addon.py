bl_info = {
    "name": "Procedural Prop Studio Pro",
    "author": "Antigravity & User",
    "version": "5.9.0",
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Prop Studio",
    "description": "Procedural Prop Studio with Grassland Mounds & Cross-Billboard Grass Tufts for Unity",
    "category": "Add Mesh",
}

import bpy
import bmesh
import math
import random
import os
import shutil
import subprocess
import mathutils

# =============================================================
# 1. Texture Auto-Scanner & Material Generator
# =============================================================
def get_textures_from_folder(folder_path):
    if not folder_path or not os.path.exists(folder_path):
        return []
    valid_exts = ('.png', '.jpg', '.jpeg', '.tga', '.tif', '.bmp', '.webp')
    files = [
        f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(valid_exts)
    ]
    return sorted(files)

def apply_image_texture_material(obj, image_path, scale=1.0, bump_strength=0.35, is_transparent=False):
    if not os.path.exists(image_path):
        return
    
    mat_name = os.path.splitext(os.path.basename(image_path))[0] + "_Mat"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (400, 0)

    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (100, 0)
    node_bsdf.inputs['Roughness'].default_value = 0.85
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    node_img = nodes.new(type='ShaderNodeTexImage')
    node_img.location = (-250, 0)
    
    img = bpy.data.images.load(image_path, check_existing=True)
    node_img.image = img
    links.new(node_img.outputs['Color'], node_bsdf.inputs['Base Color'])

    if is_transparent:
        mat.blend_method = 'CLIP'
        mat.shadow_method = 'CLIP'
        links.new(node_img.outputs['Alpha'], node_bsdf.inputs['Alpha'])

    if bump_strength > 0.01:
        node_bump = nodes.new(type='ShaderNodeBump')
        node_bump.location = (100, -150)
        node_bump.inputs['Strength'].default_value = bump_strength
        node_bump.inputs['Distance'].default_value = 0.1
        links.new(node_img.outputs['Color'], node_bump.inputs['Height'])
        links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    return mat

def create_procedural_pbr_material(mat_name, seed=0, is_grass=False):
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (650, 0)

    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (350, 0)
    node_bsdf.inputs['Roughness'].default_value = 0.85
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-750, 0)
    node_map = nodes.new(type='ShaderNodeMapping')
    node_map.location = (-550, 0)
    links.new(node_coord.outputs['Object'], node_map.inputs['Vector'])

    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-350, 100)
    node_noise.inputs['Scale'].default_value = 5.5
    node_noise.inputs['Detail'].default_value = 6.0
    node_noise.inputs['Roughness'].default_value = 0.7
    links.new(node_map.outputs['Vector'], node_noise.inputs['Vector'])

    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_ramp.location = (-100, 100)
    
    if is_grass:
        node_ramp.color_ramp.elements[0].position = 0.2
        node_ramp.color_ramp.elements[0].color = (0.08, 0.22, 0.05, 1.0) # Deep grass green
        node_ramp.color_ramp.elements[1].position = 0.8
        node_ramp.color_ramp.elements[1].color = (0.28, 0.48, 0.12, 1.0) # Bright grass green
    else:
        node_ramp.color_ramp.elements[0].position = 0.25
        node_ramp.color_ramp.elements[0].color = (0.12, 0.12, 0.13, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.75
        node_ramp.color_ramp.elements[1].color = (0.48, 0.44, 0.39, 1.0)
        
    links.new(node_noise.outputs['Fac'], node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.location = (100, -150)
    node_bump.inputs['Strength'].default_value = 0.35
    node_bump.inputs['Distance'].default_value = 0.08
    links.new(node_noise.outputs['Fac'], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat

# =============================================================
# 2. Advanced Organic Jagged Crack Builder
# =============================================================
def build_organic_crack_cutter(bm, length, depth, width, seed=0):
    random.seed(seed)
    num_pts = random.randint(4, 7)
    step_len = length / float(num_pts)
    
    pts = []
    cur_x = -length * 0.5
    cur_y = 0.0
    for i in range(num_pts + 1):
        dev_y = random.uniform(-width * 1.5, width * 1.5) if (0 < i < num_pts) else 0.0
        dev_z = random.uniform(-depth * 0.15, depth * 0.15)
        pts.append(mathutils.Vector((cur_x, cur_y + dev_y, dev_z)))
        cur_x += step_len
    
    all_verts = []
    for p in pts:
        w = random.uniform(width * 0.4, width * 1.2)
        v_left = bm.verts.new((p.x, p.y - w, depth * 0.6))
        v_right = bm.verts.new((p.x, p.y + w, depth * 0.6))
        v_root = bm.verts.new((p.x + random.uniform(-0.02, 0.02), p.y + random.uniform(-0.02, 0.02), -depth))
        all_verts.append((v_left, v_right, v_root))
    
    for i in range(len(all_verts) - 1):
        l1, r1, b1 = all_verts[i]
        l2, r2, b2 = all_verts[i + 1]
        bm.faces.new((l1, l2, b2, b1))
        bm.faces.new((r2, r1, b1, b2))
        bm.faces.new((l1, r1, r2, l2))

    l_start, r_start, b_start = all_verts[0]
    bm.faces.new((l_start, b_start, r_start))
    l_end, r_end, b_end = all_verts[-1]
    bm.faces.new((l_end, r_end, b_end))

    for v in bm.verts:
        v.co.x += (math.sin(v.co.y * 18.0 + seed) * math.cos(v.co.z * 18.0 + seed)) * (width * 0.35)
        v.co.y += (math.cos(v.co.x * 18.0 + seed) * math.sin(v.co.z * 18.0 + seed)) * (width * 0.35)

# =============================================================
# 3. Geometry Builders (Grass Mound & Cross-Billboard Grass Tuft)
# =============================================================
def build_grass_mound_base(bm, size_x, size_y, size_z, shape="SQUARE", seed=0):
    """Generates a natural organic meadow mound slab with soft uneven rolling surface"""
    random.seed(seed)
    if shape == "CIRCLE":
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=32,
            radius1=size_x * 0.5, radius2=size_x * 0.5, depth=size_z
        )
    elif shape == "HEXAGON":
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=6,
            radius1=size_x * 0.5, radius2=size_x * 0.5, depth=size_z
        )
    else: # SQUARE
        verts = bmesh.ops.create_cube(bm, size=1.0)['verts']
        bmesh.ops.scale(bm, vec=(size_x, size_y, size_z), verts=verts)

    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=4, use_grid_fill=True)
    
    # Apply soft organic rolling mound unevenness only to top surface (Z > 0)
    for v in bm.verts:
        if v.co.z > 0:
            nx = math.sin(v.co.x * 1.8 + seed) * math.cos(v.co.y * 1.8 + seed)
            ny = math.cos(v.co.x * 2.2 + seed * 2) * math.sin(v.co.y * 2.2 + seed * 2)
            v.co.z += (nx + ny) * (size_z * 0.18)

    return bm.verts[:]

def build_grass_tuft_clump(bm, size_x, size_y, size_z, blade_count=4, seed=0):
    """Generates crossed billboard grass tuft clump optimized for Unity wind shaders"""
    random.seed(seed)
    h = size_z
    w = max(size_x, size_y) * 0.5
    
    # Generate multi-angle crossed billboard planes
    angles = [0, 45, 90, 135][:blade_count] if blade_count <= 4 else [i * (180.0 / blade_count) for i in range(blade_count)]
    
    for i, ang in enumerate(angles):
        ang_rad = math.radians(ang + random.uniform(-8.0, 8.0))
        cur_w = w * random.uniform(0.85, 1.15)
        cur_h = h * random.uniform(0.85, 1.2)
        
        dx = math.cos(ang_rad) * (cur_w * 0.5)
        dy = math.sin(ang_rad) * (cur_w * 0.5)
        
        # Tilt angle slightly
        tilt_x = random.uniform(-0.06, 0.06) * cur_h
        tilt_y = random.uniform(-0.06, 0.06) * cur_h
        
        # Bottom left, Bottom right, Top right, Top left
        v_bl = bm.verts.new((-dx, -dy, 0.0))
        v_br = bm.verts.new((dx, dy, 0.0))
        v_tr = bm.verts.new((dx + tilt_x, dy + tilt_y, cur_h))
        v_tl = bm.verts.new((-dx + tilt_x, -dy + tilt_y, cur_h))
        
        # Create double-sided quad face
        bm.faces.new((v_bl, v_br, v_tr, v_tl))

    return bm.verts[:]

def build_rock_base(bm, size_x, size_y, size_z, style):
    if style in ("SHARP", "FRACTURED", "CLIFF"):
        verts = bmesh.ops.create_cube(bm, size=1.0)['verts']
    else:
        verts = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)['verts']
    bmesh.ops.scale(bm, vec=(size_x, size_y, size_z), verts=verts)
    return verts

def build_floor_base(bm, size_x, size_y, size_z, shape="SQUARE", seed=0):
    random.seed(seed)
    if shape == "CIRCLE":
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=32,
            radius1=size_x * 0.5, radius2=size_x * 0.5, depth=size_z
        )
    elif shape == "HEXAGON":
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=6,
            radius1=size_x * 0.5, radius2=size_x * 0.5, depth=size_z
        )
    else: # SQUARE
        verts = bmesh.ops.create_cube(bm, size=1.0)['verts']
        bmesh.ops.scale(bm, vec=(size_x, size_y, size_z), verts=verts)

    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2, use_grid_fill=True)
    return bm.verts[:]

def build_wall_base(bm, size_x, size_y, size_z, shape="STRAIGHT", seed=0):
    random.seed(seed)
    if shape == "TRIANGLE":
        th = size_y * 0.35
        half_w = size_x * 0.5
        half_th = th * 0.5
        h = size_z
        
        v_ft = bm.verts.new((0, -half_th, h * 0.5))
        v_fl = bm.verts.new((-half_w, -half_th, -h * 0.5))
        v_fr = bm.verts.new((half_w, -half_th, -h * 0.5))
        
        v_bt = bm.verts.new((0, half_th, h * 0.5))
        v_bl = bm.verts.new((-half_w, half_th, -h * 0.5))
        v_br = bm.verts.new((half_w, half_th, -h * 0.5))
        
        bm.faces.new((v_fl, v_fr, v_ft))
        bm.faces.new((v_bl, v_bt, v_br))
        bm.faces.new((v_fl, v_bl, v_br, v_fr))
        bm.faces.new((v_ft, v_bt, v_bl, v_fl))
        bm.faces.new((v_fr, v_br, v_bt, v_ft))
    elif shape == "L_SHAPE":
        v1 = bmesh.ops.create_cube(bm, size=1.0)['verts']
        bmesh.ops.scale(bm, vec=(size_x, size_y * 0.4, size_z), verts=v1)
        bmesh.ops.translate(bm, vec=(0, -size_x * 0.25, 0), verts=v1)
        
        v2 = bmesh.ops.create_cube(bm, size=1.0)['verts']
        bmesh.ops.scale(bm, vec=(size_y * 0.4, size_x * 0.5, size_z), verts=v2)
        bmesh.ops.translate(bm, vec=(-size_x * 0.5 + size_y * 0.2, 0, 0), verts=v2)
    elif shape == "CURVED":
        res = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=size_x * 0.8, radius2=size_x * 0.8, depth=size_z
        )
        verts = res['verts']
        bmesh.ops.scale(bm, vec=(1.0, 0.4, 1.0), verts=verts)
    else: # STRAIGHT
        verts = bmesh.ops.create_cube(bm, size=1.0)['verts']
        bmesh.ops.scale(bm, vec=(size_x, size_y * 0.35, size_z), verts=verts)

    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2, use_grid_fill=True)
    return bm.verts[:]

def build_pillar_base(bm, size_x, size_y, size_z):
    res = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=size_x * 0.45, radius2=size_x * 0.45, depth=size_z * 2.0
    )
    verts = res['verts']
    
    cap_verts = bmesh.ops.create_cube(bm, size=1.0)['verts']
    bmesh.ops.scale(bm, vec=(size_x * 1.1, size_y * 1.1, size_z * 0.2), verts=cap_verts)
    bmesh.ops.translate(bm, vec=(0, 0, size_z * 1.0), verts=cap_verts)
    
    base_verts = bmesh.ops.create_cube(bm, size=1.0)['verts']
    bmesh.ops.scale(bm, vec=(size_x * 1.15, size_y * 1.15, size_z * 0.2), verts=base_verts)
    bmesh.ops.translate(bm, vec=(0, 0, -size_z * 1.0), verts=base_verts)
    
    return verts + cap_verts + base_verts

def build_beam_base(bm, size_x, size_y, size_z):
    rad = min(size_y, size_z) * 0.35
    length = size_x * 2.2
    res = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=rad, radius2=rad, depth=length
    )
    verts = res['verts']
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'Y'), verts=verts)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2, use_grid_fill=True)
    return bm.verts[:]

def build_beam_arch_base(bm, size_x, size_y, size_z):
    all_verts = []
    rad = min(size_x, size_y) * 0.14
    
    res_top = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=rad, radius2=rad, depth=size_x * 2.2
    )
    top_verts = res_top['verts']
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'Y'), verts=top_verts)
    bmesh.ops.translate(bm, vec=(0, 0, size_z * 1.0), verts=top_verts)
    all_verts.extend(top_verts)
    
    res_lp = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=rad * 1.1, radius2=rad * 1.1, depth=size_z * 2.0
    )
    lp_verts = res_lp['verts']
    bmesh.ops.translate(bm, vec=(-size_x * 0.85, 0, 0), verts=lp_verts)
    all_verts.extend(lp_verts)
    
    res_rp = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=rad * 1.1, radius2=rad * 1.1, depth=size_z * 2.0
    )
    rp_verts = res_rp['verts']
    bmesh.ops.translate(bm, vec=(size_x * 0.85, 0, 0), verts=rp_verts)
    all_verts.extend(rp_verts)
    
    res_lb = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=12,
        radius1=rad * 0.85, radius2=rad * 0.85, depth=size_z * 0.8
    )
    lb_verts = res_lb['verts']
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(-45), 3, 'Y'), verts=lb_verts)
    bmesh.ops.translate(bm, vec=(-size_x * 0.55, 0, size_z * 0.7), verts=lb_verts)
    all_verts.extend(lb_verts)

    res_rb = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=12,
        radius1=rad * 0.85, radius2=rad * 0.85, depth=size_z * 0.8
    )
    rb_verts = res_rb['verts']
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(45), 3, 'Y'), verts=rb_verts)
    bmesh.ops.translate(bm, vec=(size_x * 0.55, 0, size_z * 0.7), verts=rb_verts)
    all_verts.extend(rb_verts)
    
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=1, use_grid_fill=True)
    return all_verts

# =============================================================
# 4. Master Generator Core
# =============================================================
def generate_procedural_prop_mesh(
    context,
    target_obj=None,
    category="ROCK",
    name="Prop_Asset",
    style="FRACTURED",
    floor_shape="SQUARE",
    wall_shape="STRAIGHT",
    grass_mode="MOUND",
    uv_mode="FIT",
    size_x=2.0,
    size_y=2.0,
    size_z=1.5,
    roughness=0.7,
    chisel_strength=0.8,
    crack_depth=0.6,
    big_chunk_cuts=2,
    crack_count=5,
    create_debris=True,
    debris_count=6,
    detail_level=2,
    tex_folder=r"Z:\MeshCreator\textures\Rock",
    use_folder_tex=True,
    selected_tex="",
    tex_tiling=1.0,
    seed=0
):
    random.seed(seed)
    cleanup_old_debris(context, name if not target_obj else target_obj.name)

    if target_obj and target_obj.type == 'MESH':
        obj = target_obj
        obj.name = name
        mesh = obj.data
        mesh.clear_geometry()
        obj.modifiers.clear()
        obj.data.materials.clear()
    else:
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        context.collection.objects.link(obj)

    context.view_layer.objects.active = obj
    obj.select_set(True)

    # 1. Base Geometry Construction
    bm = bmesh.new()
    if category == "GRASS":
        if grass_mode == "TUFT":
            build_grass_tuft_clump(bm, size_x, size_y, size_z, blade_count=4, seed=seed)
        else:
            build_grass_mound_base(bm, size_x, size_y, size_z, shape=floor_shape, seed=seed)
    elif category == "FLOOR":
        build_floor_base(bm, size_x, size_y, size_z, shape=floor_shape, seed=seed)
    elif category == "WALL":
        build_wall_base(bm, size_x, size_y, size_z, shape=wall_shape, seed=seed)
    elif category == "PILLAR":
        build_pillar_base(bm, size_x, size_y, size_z)
    elif category == "BEAM":
        build_beam_base(bm, size_x, size_y, size_z)
    elif category == "BEAM_ARCH":
        build_beam_arch_base(bm, size_x, size_y, size_z)
    else: # ROCK
        build_rock_base(bm, size_x, size_y, size_z, style)

    # Debris (Rock only)
    if create_debris and debris_count > 0 and category == "ROCK":
        max_rad = max(size_x, size_y)
        for i in range(debris_count):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(max_rad * 0.55, max_rad * 0.95)
            dx = math.cos(angle) * dist
            dy = math.sin(angle) * dist
            dz = -size_z * 0.35 + random.uniform(-0.05, 0.08)
            
            d_rad = random.uniform(0.12, 0.35)
            d_verts = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=d_rad)['verts']
            
            sx = random.uniform(0.8, 1.4)
            sy = random.uniform(0.8, 1.4)
            sz = random.uniform(0.5, 1.0)
            bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=d_verts)
            bmesh.ops.translate(bm, vec=(dx, dy, dz), verts=d_verts)

    bm.to_mesh(mesh)
    bm.free()

    # 2. Organic Jagged Cracks for Floor & Wall (Not on Grass Tuft)
    if category in ("FLOOR", "WALL") and crack_count > 0:
        half_x = size_x * 0.35
        half_y = (size_y * 0.4) if category == "FLOOR" else (size_z * 0.35)
        for sc in range(min(crack_count, 20)):
            scar_mesh = bpy.data.meshes.new(f"Temp_Jagged_Crack_{sc}")
            scar_obj = bpy.data.objects.new("Temp_Jagged_Crack", scar_mesh)
            context.collection.objects.link(scar_obj)
            
            sbm = bmesh.new()
            c_len = random.uniform(0.3, 0.85) * max(size_x, size_z) * 0.35
            c_width = random.uniform(0.02, 0.06) * (crack_depth * 1.6)
            c_depth = random.uniform(0.03, 0.09) * (crack_depth * 1.6)
            
            build_organic_crack_cutter(sbm, length=c_len, depth=c_depth, width=c_width, seed=seed + sc * 17)
            sbm.to_mesh(scar_mesh)
            sbm.free()
            
            px = random.uniform(-half_x, half_x)
            if category == "FLOOR":
                py = random.uniform(-half_y, half_y)
                pz = (size_z * 0.5)
                scar_obj.location = (obj.location.x + px, obj.location.y + py, obj.location.z + pz)
                scar_obj.rotation_euler = (
                    random.uniform(-0.08, 0.08),
                    random.uniform(-0.08, 0.08),
                    random.uniform(0, math.pi * 2)
                )
            else:
                py = (size_y * 0.35 * 0.5) * random.choice([1, -1])
                pz = random.uniform(-half_y, half_y * 0.7)
                scar_obj.location = (obj.location.x + px, obj.location.y + py, obj.location.z + pz)
                scar_obj.rotation_euler = (
                    math.radians(90) if py > 0 else math.radians(-90),
                    random.uniform(0, math.pi * 2),
                    random.uniform(-0.08, 0.08)
                )
            
            bool_mod = obj.modifiers.new(name=f"Bool_Crack_{sc}", type='BOOLEAN')
            bool_mod.operation = 'DIFFERENCE'
            bool_mod.object = scar_obj
            bool_mod.solver = 'FAST'
            
            try:
                bpy.ops.object.modifier_apply(modifier=bool_mod.name)
            except Exception:
                pass
            
            bpy.data.objects.remove(scar_obj, do_unlink=True)
            bpy.data.meshes.remove(scar_mesh, do_unlink=True)

    # 3. Big Chunk Boolean Fractures (Rock & Pillar)
    if big_chunk_cuts > 0 and category in ("ROCK", "PILLAR"):
        for c in range(big_chunk_cuts):
            cutter_mesh = bpy.data.meshes.new("Temp_Cutter_Mesh")
            cutter_obj = bpy.data.objects.new("Temp_Cutter", cutter_mesh)
            context.collection.objects.link(cutter_obj)
            
            cbm = bmesh.new()
            bmesh.ops.create_cube(cbm, size=random.uniform(1.0, 2.2))
            cbm.to_mesh(cutter_mesh)
            cbm.free()
            
            cutter_obj.location = (
                obj.location.x + (random.choice([-1, 1]) * size_x * random.uniform(0.35, 0.65)),
                obj.location.y + (random.choice([-1, 1]) * size_y * random.uniform(0.35, 0.65)),
                obj.location.z + (random.choice([-1, 1]) * size_z * random.uniform(0.2, 0.6))
            )
            cutter_obj.rotation_euler = (
                random.uniform(0, math.pi),
                random.uniform(0, math.pi),
                random.uniform(0, math.pi)
            )
            
            bool_mod = obj.modifiers.new(name=f"Bool_Cut_{c}", type='BOOLEAN')
            bool_mod.operation = 'DIFFERENCE'
            bool_mod.object = cutter_obj
            bool_mod.solver = 'FAST'
            
            try:
                bpy.ops.object.modifier_apply(modifier=bool_mod.name)
            except Exception:
                pass
            
            bpy.data.objects.remove(cutter_obj, do_unlink=True)
            bpy.data.meshes.remove(cutter_mesh, do_unlink=True)

    # 4. Bevel for Floor, Wall & Grass Mound
    if category in ("FLOOR", "WALL") or (category == "GRASS" and grass_mode == "MOUND"):
        bevel_mod = obj.modifiers.new(name="Bevel_Chipping", type='BEVEL')
        bevel_mod.width = min(0.03, (size_z if category != "WALL" else size_y) * 0.15)
        bevel_mod.segments = 2
        try:
            bpy.ops.object.modifier_apply(modifier=bevel_mod.name)
        except Exception:
            pass

    # 5. Subdivision & Displacements (Rock / Pillar / Beam Architecture)
    if category not in ("FLOOR", "WALL", "GRASS"):
        subsurf = obj.modifiers.new(name="Subsurf_Base", type='SUBSURF')
        subsurf.render_levels = detail_level + 1
        subsurf.levels = detail_level + 1

        tex_large = bpy.data.textures.new(name + "_Tex_Large", type='CLOUDS')
        tex_large.noise_scale = 1.6 if category in ("BEAM", "BEAM_ARCH") else 1.2
        tex_large.noise_depth = 2 if category in ("BEAM", "BEAM_ARCH") else 3
        
        disp_large = obj.modifiers.new(name="Disp_Large", type='DISPLACE')
        disp_large.texture = tex_large
        disp_large.strength = roughness * (0.22 if category in ("BEAM", "BEAM_ARCH") else 0.8)
        disp_large.mid_level = 0.5

        if chisel_strength > 0.05:
            tex_voronoi = bpy.data.textures.new(name + "_Tex_Chisel", type='VORONOI' if category not in ("BEAM", "BEAM_ARCH") else 'WOOD')
            tex_voronoi.noise_scale = 0.8
            
            disp_voronoi = obj.modifiers.new(name="Disp_Chisel", type='DISPLACE')
            disp_voronoi.texture = tex_voronoi
            disp_voronoi.strength = chisel_strength * (0.18 if category in ("BEAM", "BEAM_ARCH") else 0.5)
            disp_voronoi.mid_level = 0.5

        if crack_depth > 0.05:
            tex_crack = bpy.data.textures.new(name + "_Tex_Crack", type='VORONOI')
            tex_crack.noise_scale = 0.5
            tex_crack.distance_metric = 'DISTANCE_SQUARED'
            
            disp_crack = obj.modifiers.new(name="Disp_Crack", type='DISPLACE')
            disp_crack.texture = tex_crack
            disp_crack.strength = -crack_depth * (0.12 if category in ("BEAM", "BEAM_ARCH") else 0.4)
            disp_crack.mid_level = 0.85

    # 6. Apply Modifiers & Smooth
    for p in mesh.polygons:
        p.use_smooth = True

    for mod in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception:
            pass

    # 7. Smart UV Projection
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    if category == "GRASS" and grass_mode == "TUFT":
        # Standard UV unwrap for billboard planes (0 to 1 quad mapping)
        bpy.ops.uv.smart_project(angle_limit=88.0, island_margin=0.0)
    elif category in ("FLOOR", "WALL", "BEAM", "BEAM_ARCH", "GRASS"):
        if uv_mode == "FIT":
            max_dim = max(size_x, size_y, size_z)
            bpy.ops.uv.cube_project(cube_size=max_dim, correct_aspect=True, clip_to_bounds=True)
        else: # TILING
            bpy.ops.uv.cube_project(cube_size=2.0 / max(0.1, tex_tiling), correct_aspect=True)
    else: # ROCK
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
        
    bpy.ops.object.mode_set(mode='OBJECT')

    # 8. Material Assignment
    tex_files = get_textures_from_folder(tex_folder)
    if use_folder_tex and tex_files:
        chosen_tex = selected_tex if (selected_tex and selected_tex in tex_files) else random.choice(tex_files)
        full_tex_path = os.path.join(tex_folder, chosen_tex)
        apply_image_texture_material(
            obj, full_tex_path,
            scale=1.0 if uv_mode == "FIT" else tex_tiling,
            bump_strength=0.35,
            is_transparent=(category == "GRASS" and grass_mode == "TUFT")
        )
    else:
        mat = create_procedural_pbr_material(name + "_Mat", seed, is_grass=(category == "GRASS"))
        obj.data.materials.append(mat)

    return obj

def cleanup_old_debris(context, parent_name):
    to_delete = [
        o for o in bpy.data.objects
        if "Debris" in o.name and (parent_name in o.name or (o.parent and o.parent.name == parent_name))
    ]
    for o in to_delete:
        bpy.data.objects.remove(o, do_unlink=True)

# =============================================================
# 5. Helper to Resolve Parameters
# =============================================================
def resolve_prop_parameters(props):
    cat = props.prop_category
    types = ['FRACTURED', 'SHARP', 'CLIFF', 'BOULDER', 'WEATHERED']
    final_type = random.choice(types) if props.rand_type else props.rock_type
    
    if props.rand_dimensions:
        if cat in ("FLOOR", "GRASS"):
            if cat == "GRASS" and props.grass_mode == 'TUFT':
                final_sx = round(random.uniform(0.6, 1.2), 2)
                final_sy = final_sx
                final_sz = round(random.uniform(0.6, 1.3), 2)
            else:
                sq = round(random.choice([2.0, 3.0, 4.0]), 2)
                final_sx = sq
                final_sy = sq
                final_sz = round(random.uniform(0.15, 0.35), 2)
        elif cat == "WALL":
            final_sx = round(random.choice([2.0, 3.0, 4.0]), 2)
            final_sy = round(random.uniform(0.8, 1.2), 2)
            final_sz = round(random.choice([2.0, 2.5, 3.0]), 2)
        elif cat in ("BEAM", "BEAM_ARCH"):
            final_sx = round(random.uniform(1.8, 3.5), 2)
            final_sy = round(random.uniform(1.5, 2.5), 2)
            final_sz = round(random.uniform(1.8, 2.8), 2)
        elif cat == "PILLAR":
            final_sx = round(random.uniform(0.8, 1.6), 2)
            final_sy = round(random.uniform(0.8, 1.6), 2)
            final_sz = round(random.uniform(1.8, 3.5), 2)
        else:
            final_sx = round(random.uniform(1.2, 3.5), 2)
            final_sy = round(random.uniform(1.2, 3.5), 2)
            final_sz = round(random.uniform(0.8, 2.5), 2)
    else:
        final_sx, final_sy, final_sz = props.size_x, props.size_y, props.size_z

    if props.rand_surface:
        final_roughness = round(random.uniform(0.4, 1.2), 2)
        final_chisel = round(random.uniform(0.4, 1.3), 2)
    else:
        final_roughness = props.roughness
        final_chisel = props.chisel_strength

    if props.rand_fractures:
        final_chunks = random.randint(1, 4) if cat in ("ROCK", "PILLAR") else 0
        final_crack = round(random.uniform(0.3, 1.0), 2)
        final_cracks_count = random.randint(2, 12) if cat in ("FLOOR", "WALL") else 0
    else:
        final_chunks = props.big_chunk_cuts
        final_crack = props.crack_depth
        final_cracks_count = props.floor_crack_count

    if props.rand_debris:
        final_debris_count = random.randint(3, 10)
    else:
        final_debris_count = props.debris_count

    tex_files = get_textures_from_folder(props.texture_folder)
    if props.rand_texture and tex_files:
        chosen_tex = random.choice(tex_files)
    else:
        chosen_tex = props.selected_texture if (props.selected_texture in tex_files) else (tex_files[0] if tex_files else "")

    return {
        "category": cat,
        "style": final_type,
        "floor_shape": props.floor_shape,
        "wall_shape": props.wall_shape,
        "grass_mode": props.grass_mode,
        "uv_mode": props.uv_mapping_mode,
        "size_x": final_sx,
        "size_y": final_sy,
        "size_z": final_sz,
        "roughness": final_roughness,
        "chisel_strength": final_chisel,
        "crack_depth": final_crack,
        "big_chunk_cuts": final_chunks,
        "crack_count": final_cracks_count,
        "create_debris": False if cat in ("FLOOR", "WALL", "GRASS") else props.create_debris,
        "debris_count": final_debris_count,
        "detail_level": props.detail_level,
        "tex_folder": props.texture_folder,
        "use_folder_tex": props.use_folder_texture,
        "selected_tex": chosen_tex,
        "tex_tiling": props.texture_tiling,
    }

# =============================================================
# 6. Clean Unity FBX Exporter
# =============================================================
def get_next_available_fbx_path(export_dir, base_name):
    os.makedirs(export_dir, exist_ok=True)
    target_path = os.path.join(export_dir, f"{base_name}.fbx")
    if not os.path.exists(target_path):
        return target_path

    idx = 1
    while True:
        candidate_path = os.path.join(export_dir, f"{base_name}_{idx:02d}.fbx")
        if not os.path.exists(candidate_path):
            return candidate_path
        idx += 1

class MESH_OT_export_selected_fbx(bpy.types.Operator):
    """Export active prop to FBX for Unity"""
    bl_idname = "mesh.export_selected_fbx"
    bl_label = "1-Click Auto-Increment FBX Export"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        active_obj = context.active_object
        if not active_obj or active_obj.type != 'MESH':
            self.report({'WARNING'}, "Please select a prop mesh to export")
            return {'CANCELLED'}

        export_dir = props.export_folder.strip() or r"Z:\MeshCreator\exports"
        os.makedirs(export_dir, exist_ok=True)

        base_name = props.asset_name.strip() or active_obj.name
        final_fbx_path = get_next_available_fbx_path(export_dir, base_name)
        file_name_only = os.path.basename(final_fbx_path)

        for obj in context.scene.objects:
            obj.select_set(False)
        active_obj.select_set(True)
        context.view_layer.objects.active = active_obj

        copied_texture_name = None
        if active_obj.data.materials and len(active_obj.data.materials) > 0:
            mat = active_obj.data.materials[0]
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image and node.image.filepath:
                        src_img = bpy.path.abspath(node.image.filepath)
                        if os.path.exists(src_img):
                            try:
                                dst_img = os.path.join(export_dir, os.path.basename(src_img))
                                shutil.copy2(src_img, dst_img)
                                copied_texture_name = os.path.basename(src_img)
                            except Exception:
                                pass

        bpy.ops.export_scene.fbx(
            filepath=final_fbx_path,
            use_selection=True,
            object_types={'MESH'},
            bake_space_transform=True,
            apply_scale_options='FBX_SCALE_ALL',
            path_mode='COPY',
            embed_textures=True,
            axis_forward='-Z',
            axis_up='Y'
        )

        msg = f"✅ FBX出力完了: {file_name_only}"
        if copied_texture_name:
            msg += f" (テクスチャ同封: {copied_texture_name})"
        self.report({'INFO'}, msg)
        return {'FINISHED'}

class MESH_OT_open_export_folder(bpy.types.Operator):
    """Open the export folder in Windows Explorer"""
    bl_idname = "mesh.open_export_folder"
    bl_label = "Open Export Folder"

    def execute(self, context):
        props = context.scene.prop_studio_props
        export_dir = props.export_folder.strip() or r"Z:\MeshCreator\exports"
        os.makedirs(export_dir, exist_ok=True)
        subprocess.Popen(f'explorer "{export_dir}"')
        return {'FINISHED'}

# =============================================================
# 7. Core Operators
# =============================================================
class MESH_OT_reroll_selected_prop(bpy.types.Operator):
    """Re-roll and morph the selected prop in-place with new random seed & texture"""
    bl_idname = "mesh.reroll_selected_prop"
    bl_label = "Re-Roll Selected Prop"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        active_obj = context.active_object
        target = active_obj if (active_obj and active_obj.type == 'MESH') else None
        
        props.seed = random.randint(1, 999999)
        p = resolve_prop_parameters(props)
        
        generate_procedural_prop_mesh(
            context=context,
            target_obj=target,
            category=p["category"],
            name=props.asset_name if not target else target.name,
            style=p["style"],
            floor_shape=p["floor_shape"],
            wall_shape=p["wall_shape"],
            grass_mode=p["grass_mode"],
            uv_mode=p["uv_mode"],
            size_x=p["size_x"],
            size_y=p["size_y"],
            size_z=p["size_z"],
            roughness=p["roughness"],
            chisel_strength=p["chisel_strength"],
            crack_depth=p["crack_depth"],
            big_chunk_cuts=p["big_chunk_cuts"],
            crack_count=p["crack_count"],
            create_debris=p["create_debris"],
            debris_count=p["debris_count"],
            detail_level=p["detail_level"],
            tex_folder=p["tex_folder"],
            use_folder_tex=p["use_folder_tex"],
            selected_tex=p["selected_tex"],
            tex_tiling=p["tex_tiling"],
            seed=props.seed
        )
        self.report({'INFO'}, f"🎲 再抽選完了: {props.asset_name}")
        return {'FINISHED'}

class MESH_OT_create_new_prop(bpy.types.Operator):
    """Create a brand new procedural prop object"""
    bl_idname = "mesh.create_new_prop"
    bl_label = "Create New Prop"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        props.seed = random.randint(1, 999999) if props.auto_random else props.seed
        p = resolve_prop_parameters(props)
        
        generate_procedural_prop_mesh(
            context=context,
            target_obj=None,
            category=p["category"],
            name=props.asset_name,
            style=p["style"],
            floor_shape=p["floor_shape"],
            wall_shape=p["wall_shape"],
            grass_mode=p["grass_mode"],
            uv_mode=p["uv_mode"],
            size_x=p["size_x"],
            size_y=p["size_y"],
            size_z=p["size_z"],
            roughness=p["roughness"],
            chisel_strength=p["chisel_strength"],
            crack_depth=p["crack_depth"],
            big_chunk_cuts=p["big_chunk_cuts"],
            crack_count=p["crack_count"],
            create_debris=p["create_debris"],
            debris_count=p["debris_count"],
            detail_level=p["detail_level"],
            tex_folder=p["tex_folder"],
            use_folder_tex=p["use_folder_tex"],
            selected_tex=p["selected_tex"],
            tex_tiling=p["tex_tiling"],
            seed=props.seed
        )
        self.report({'INFO'}, f"➕ 新規作成完了: {props.asset_name}")
        return {'FINISHED'}

class MESH_OT_apply_random_texture_only(bpy.types.Operator):
    """Apply random texture from folder to selected object without changing geometry"""
    bl_idname = "mesh.apply_random_texture_only"
    bl_label = "Random Texture Only"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        active_obj = context.active_object
        if not active_obj or active_obj.type != 'MESH':
            self.report({'WARNING'}, "Please select a mesh object first")
            return {'CANCELLED'}

        tex_files = get_textures_from_folder(props.texture_folder)
        if not tex_files:
            self.report({'WARNING'}, f"No texture files found in {props.texture_folder}")
            return {'CANCELLED'}

        chosen_tex = random.choice(tex_files)
        full_path = os.path.join(props.texture_folder, chosen_tex)
        apply_image_texture_material(
            active_obj, full_path,
            scale=1.0 if props.uv_mapping_mode == 'FIT' else props.texture_tiling,
            bump_strength=0.35,
            is_transparent=(props.prop_category == 'GRASS' and props.grass_mode == 'TUFT')
        )
        
        self.report({'INFO'}, f"Applied Texture: {chosen_tex}")
        return {'FINISHED'}

# =============================================================
# 8. Category Preset Callback
# =============================================================
def get_texture_enum_items(self, context):
    props = context.scene.prop_studio_props
    tex_files = get_textures_from_folder(props.texture_folder)
    if not tex_files:
        return [('NONE', "No Textures Found", "No image files found in folder")]
    return [(f, f, f) for f in tex_files]

def update_category_preset(self, context):
    props = context.scene.prop_studio_props
    cat = props.prop_category
    
    name_map = {
        'ROCK': "Rock_Asset",
        'FLOOR': "Floor_Tile",
        'WALL': "Wall_Block",
        'PILLAR': "Pillar_Column",
        'BEAM': "Timber_Beam",
        'BEAM_ARCH': "Beam_Arch",
        'GRASS': "Grass_Meadow"
    }
    props.asset_name = name_map.get(cat, "Prop_Asset")

    if cat == "GRASS":
        props.size_x = 3.0
        props.size_y = 3.0
        props.size_z = 0.3
        props.create_debris = False
        props.big_chunk_cuts = 0
        props.floor_crack_count = 0
        props.uv_mapping_mode = 'FIT'
        props.texture_tiling = 1.0
    elif cat == "FLOOR":
        props.size_x = 2.0
        props.size_y = 2.0
        props.size_z = 0.2
        props.create_debris = False
        props.big_chunk_cuts = 0
        props.floor_crack_count = 5
        props.uv_mapping_mode = 'FIT'
        props.texture_tiling = 1.0
    elif cat == "WALL":
        props.size_x = 3.0
        props.size_y = 1.0
        props.size_z = 2.5
        props.create_debris = False
        props.big_chunk_cuts = 0
        props.floor_crack_count = 6
        props.uv_mapping_mode = 'FIT'
        props.texture_tiling = 1.0
    elif cat in ("BEAM", "BEAM_ARCH"):
        props.size_x = 2.4
        props.size_y = 1.5
        props.size_z = 2.0
        props.create_debris = False
        props.big_chunk_cuts = 0
        props.uv_mapping_mode = 'FIT'
        props.texture_tiling = 1.0
    elif cat == "PILLAR":
        props.size_x = 1.2
        props.size_y = 1.2
        props.size_z = 2.5
        props.create_debris = False
        props.big_chunk_cuts = 1
        props.uv_mapping_mode = 'FIT'
        props.texture_tiling = 1.0
    else: # ROCK
        props.size_x = 2.2
        props.size_y = 2.0
        props.size_z = 1.6
        props.create_debris = True
        props.big_chunk_cuts = 2
        props.uv_mapping_mode = 'TILING'
        props.texture_tiling = 1.5

    folder_map = {
        'ROCK': r"Z:\MeshCreator\textures\Rock",
        'FLOOR': r"Z:\MeshCreator\textures\Floor",
        'WALL': r"Z:\MeshCreator\textures\Wall",
        'PILLAR': r"Z:\MeshCreator\textures\Pillar",
        'BEAM': r"Z:\MeshCreator\textures\Wood",
        'BEAM_ARCH': r"Z:\MeshCreator\textures\Wood",
        'GRASS': r"Z:\MeshCreator\textures\Grass"
    }
    
    target_folder = folder_map.get(cat, r"Z:\MeshCreator\textures\Rock")
    os.makedirs(target_folder, exist_ok=True)
    props.texture_folder = target_folder

# =============================================================
# 9. Property Group
# =============================================================
class PropStudioProperties(bpy.types.PropertyGroup):
    prop_category: bpy.props.EnumProperty(
        name="Category",
        items=[
            ('ROCK', "🪨 岩 (Rock / Boulder)", "textures/Rock/ と自動連動"),
            ('GRASS', "🌿 草原・草地 (Grassland / Meadow)", "textures/Grass/ と自動連動（草地丘陵スラブ＆十字草むら）"),
            ('FLOOR', "🟫 床・タイル (Floor / Tile)", "textures/Floor/ と自動連動（正方形・円形・六角形＆有機的亀裂）"),
            ('WALL', "🧱 壁・城壁 (Wall / Ruins)", "textures/Wall/ と自動連動（直線・L字・円弧・▲三角切妻壁）"),
            ('PILLAR', "🏛️ 柱・石柱 (Pillar / Column)", "textures/Pillar/ と自動連動"),
            ('BEAM', "🪵 梁・丸太支柱 (Timber Log Beam)", "textures/Wood/ と自動連動（シリンダー丸太梁）"),
            ('BEAM_ARCH', "🪵🏛️ 梁アーチ (Beam Arch)", "textures/Wood/ と自動連動（シリンダー丸太アーチ）")
        ],
        default='ROCK',
        update=update_category_preset
    )

    studio_tab: bpy.props.EnumProperty(
        name="Studio Tab",
        items=[
            ('SHAPE', "📐 形状", "形状・寸法・有機的クラック傷設定"),
            ('TEX', "🎨 テクスチャ", "PBRテクスチャ連動・UVフィット設定"),
            ('EXPORT', "📦 出力", "Unity FBXエクスポート設定")
        ],
        default='SHAPE'
    )

    grass_mode: bpy.props.EnumProperty(
        name="Grass Type",
        items=[
            ('MOUND', "🌿 草地ベース床 (Meadow Mound Slab)", "自然な緩やかな起伏を持つ草地スラブ（足場）"),
            ('TUFT', "🌾 草の束・草むら (Grass Tuft Clump)", "風に揺らすための十字クロス草メッシュ（ビルボード）")
        ],
        default='MOUND'
    )

    uv_mapping_mode: bpy.props.EnumProperty(
        name="UV Mode",
        items=[
            ('FIT', "🔲 1枚全面フィット (Fit to Object)", "オブジェクトのサイズ全体に1枚絵としてフィット（反復ループなし）"),
            ('TILING', "🔁 タイル反復 (Tiling Repeat)", "レンガや敷石のようにテクスチャを反復リピート")
        ],
        default='FIT'
    )

    floor_shape: bpy.props.EnumProperty(
        name="Floor Shape",
        items=[
            ('SQUARE', "🔲 正方形 (Square)", "Clean flat square slab"),
            ('CIRCLE', "⚪ 円形・丸 (Circle / Round)", "Clean round circular slab / pedestal"),
            ('HEXAGON', "⬡ 六角形 (Hexagon)", "Hexagonal pavement tile")
        ],
        default='SQUARE'
    )

    wall_shape: bpy.props.EnumProperty(
        name="Wall Shape",
        items=[
            ('STRAIGHT', "🧱 直線壁 (Straight Wall)", "Clean straight stone wall"),
            ('TRIANGLE', "🔺 三角壁・切妻壁 (Triangle / Gable)", "Triangular gable wall for roofs & slopes"),
            ('L_SHAPE', "🧱 L字コーナー壁 (L-Corner Wall)", "L-shaped corner wall block"),
            ('CURVED', "🧱 円弧・カーブ壁 (Curved Wall)", "Curved arched wall segment")
        ],
        default='STRAIGHT'
    )

    asset_name: bpy.props.StringProperty(name="Name", default="Rock_Asset")
    export_folder: bpy.props.StringProperty(name="Export Folder", subtype='DIR_PATH', default=r"Z:\MeshCreator\exports")

    rock_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ('FRACTURED', "Fractured (大破砕・巨岩)", "Heavily fractured rock with large broken chunks"),
            ('SHARP', "Sharp Slate (鋭利な割れ石)", "Chiseled slate rock"),
            ('CLIFF', "Cliff Slab (断崖・板状岩)", "Terraced layered cliff block"),
            ('BOULDER', "Boulder (丸岩・巨石)", "Weathered rounded massive boulder"),
            ('WEATHERED', "Weathered (風化岩)", "Soft organic eroded stone")
        ],
        default='FRACTURED'
    )
    rand_type: bpy.props.BoolProperty(name="🎲 形状ランダム", default=True)

    size_x: bpy.props.FloatProperty(name="X (幅/スパン)", default=3.0, min=0.2, max=20.0)
    size_y: bpy.props.FloatProperty(name="Y (厚み/奥行)", default=3.0, min=0.1, max=20.0)
    size_z: bpy.props.FloatProperty(name="Z (高さ)", default=0.3, min=0.05, max=20.0)
    rand_dimensions: bpy.props.BoolProperty(name="🎲 サイズランダム", default=True)

    roughness: bpy.props.FloatProperty(name="Roughness (粗さ)", default=0.75, min=0.0, max=2.0)
    chisel_strength: bpy.props.FloatProperty(name="Chisel (削り角)", default=0.85, min=0.0, max=1.5)
    rand_surface: bpy.props.BoolProperty(name="🎲 粗さランダム", default=True)

    big_chunk_cuts: bpy.props.IntProperty(name="Big Chunks (大きな欠け数)", default=2, min=0, max=5)
    crack_depth: bpy.props.FloatProperty(name="Crack Depth (亀裂・傷の深さ)", default=0.6, min=0.0, max=1.5)
    floor_crack_count: bpy.props.IntProperty(name="亀裂・傷の箇所数", default=6, min=0, max=20)
    rand_fractures: bpy.props.BoolProperty(name="🎲 亀裂ランダム", default=True)

    create_debris: bpy.props.BoolProperty(name="Create Debris (周囲の破片・小石)", default=True)
    debris_count: bpy.props.IntProperty(name="Shard Count", default=6, min=1, max=20)
    rand_debris: bpy.props.BoolProperty(name="🎲 破片数ランダム", default=True)

    texture_folder: bpy.props.StringProperty(name="Texture Folder", subtype='DIR_PATH', default=r"Z:\MeshCreator\textures\Rock")
    use_folder_texture: bpy.props.BoolProperty(name="Use Folder Textures", default=True)
    rand_texture: bpy.props.BoolProperty(name="🎲 テクスチャをランダム抽選", default=True)
    selected_texture: bpy.props.EnumProperty(name="Select Texture", items=get_texture_enum_items)
    texture_tiling: bpy.props.FloatProperty(name="Tiling (リピート倍率)", default=1.0, min=0.1, max=10.0)

    detail_level: bpy.props.IntProperty(name="Quality", default=2, min=1, max=3)
    seed: bpy.props.IntProperty(name="Seed", default=42, min=0)
    auto_random: bpy.props.BoolProperty(name="Auto Random", default=True)

# =============================================================
# 10. Sidebar Panel (N-Panel)
# =============================================================
class VIEW3D_PT_prop_studio_panel(bpy.types.Panel):
    bl_label = "Procedural Prop Studio Pro"
    bl_idname = "VIEW3D_PT_prop_studio_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Prop Studio"

    def draw(self, context):
        layout = self.layout
        props = context.scene.prop_studio_props

        # 🌟 1. Category Selector Box
        box_cat = layout.box()
        box_cat.label(text="Preset Category (プリセット):", icon='ASSET_MANAGER')
        box_cat.prop(props, "prop_category", text="")

        # 🌟 2. Giant Top Action Bar
        box_act = layout.box()
        col_act = box_act.column(align=True)
        col_act.scale_y = 1.4
        col_act.operator("mesh.reroll_selected_prop", text="🎲 形状を再抽選 (Re-Roll)", icon='FILE_REFRESH')
        
        row_sub_act = col_act.row(align=True)
        row_sub_act.operator("mesh.create_new_prop", text="➕ 新規作成", icon='ADD')
        row_sub_act.operator("mesh.apply_random_texture_only", text="🎨 テクスチャ変更", icon='IMAGE_DATA')

        col_exp = box_act.column(align=True)
        col_exp.scale_y = 1.3
        col_exp.operator("mesh.export_selected_fbx", text="📦 一発 FBX 出力 (Unity用・自動+1連番)", icon='EXPORT')

        layout.separator()

        # 🌟 3. Studio Mode Tab Switcher
        row_tabs = layout.row(align=True)
        row_tabs.prop(props, "studio_tab", expand=True)

        layout.separator()

        # 🌟 4. Tab 1: Shape & Dimensions
        if props.studio_tab == 'SHAPE':
            if props.prop_category == 'GRASS':
                box_gmode = layout.box()
                box_gmode.label(text="Grass Type (草原タイプ):", icon='OUTLINER_OB_CURVE')
                box_gmode.prop(props, "grass_mode", text="")
                if props.grass_mode == 'MOUND':
                    box_gmode.prop(props, "floor_shape", text="床形状")
            elif props.prop_category == 'FLOOR':
                box_fshape = layout.box()
                box_fshape.label(text="Floor Shape (床の形状):", icon='MESH_PLANE')
                box_fshape.prop(props, "floor_shape", text="")
            elif props.prop_category == 'WALL':
                box_wshape = layout.box()
                box_wshape.label(text="Wall Shape (壁の形状):", icon='MESH_CUBE')
                box_wshape.prop(props, "wall_shape", text="")

            box_dim = layout.box()
            row_dh = box_dim.row(align=True)
            row_dh.label(text="Dimensions (サイズ):", icon='EMPTY_DATA')
            row_dh.prop(props, "rand_dimensions", text="🎲 ランダム")
            
            row_d = box_dim.row(align=True)
            row_d.enabled = not props.rand_dimensions
            if (props.prop_category in ('FLOOR', 'GRASS')) and props.floor_shape in ('CIRCLE', 'HEXAGON'):
                row_d.prop(props, "size_x", text="直径")
                row_d.prop(props, "size_z", text="厚み/高さ")
            else:
                row_d.prop(props, "size_x", text="X (幅)")
                row_d.prop(props, "size_y", text="Y (奥行)")
                row_d.prop(props, "size_z", text="Z (高さ)")

            if props.prop_category in ("FLOOR", "WALL"):
                box_scar = layout.box()
                row_sch = box_scar.row(align=True)
                row_sch.label(text="Organic Cracks (有機的亀裂・傷):", icon='MOD_BOOLEAN')
                row_sch.prop(props, "rand_fractures", text="🎲 ランダム")
                
                col_sc = box_scar.column(align=True)
                col_sc.enabled = not props.rand_fractures
                col_sc.prop(props, "floor_crack_count", text="亀裂・傷の箇所数 (1~20)")
                col_sc.prop(props, "crack_depth", text="亀裂の深さ・太さ", slider=True)
            elif props.prop_category != 'GRASS':
                box_surf = layout.box()
                row_sh = box_surf.row(align=True)
                row_sh.label(text="Surface (粗さ・削り):", icon='MOD_SUBSURF')
                row_sh.prop(props, "rand_surface", text="🎲 ランダム")
                col_s = box_surf.column(align=True)
                col_s.enabled = not props.rand_surface
                col_s.prop(props, "roughness", slider=True)
                col_s.prop(props, "chisel_strength", slider=True)

                box_frac = layout.box()
                row_fh = box_frac.row(align=True)
                row_fh.label(text="Fractures (欠け・亀裂):", icon='MOD_BOOLEAN')
                row_fh.prop(props, "rand_fractures", text="🎲 ランダム")
                col_f = box_frac.column(align=True)
                col_f.enabled = not props.rand_fractures
                col_f.prop(props, "big_chunk_cuts")
                col_f.prop(props, "crack_depth", slider=True)

        # 🌟 5. Tab 2: Textures & UV Mapping Mode
        elif props.studio_tab == 'TEX':
            box_map = layout.box()
            box_map.label(text="Texture UV Mapping Mode (貼り方):", icon='UV')
            box_map.prop(props, "uv_mapping_mode", text="")
            if props.uv_mapping_mode == 'TILING':
                box_map.prop(props, "texture_tiling", text="リピート倍率", slider=True)

            box_tex = layout.box()
            box_tex.label(text="PBR Texture Folder (自動連動):", icon='FILE_FOLDER')
            box_tex.prop(props, "texture_folder", text="")
            
            row_tf = box_tex.row(align=True)
            row_tf.prop(props, "use_folder_texture", text="テクスチャ有効")
            row_tf.prop(props, "rand_texture", text="🎲 ランダム")
            
            if props.use_folder_texture and not props.rand_texture:
                box_tex.prop(props, "selected_texture", text="")
            
            box_tex.operator("mesh.apply_random_texture_only", text="🎨 テクスチャのみ再抽選", icon='IMAGE_DATA')

        # 🌟 6. Tab 3: Export Settings
        elif props.studio_tab == 'EXPORT':
            box_exp = layout.box()
            box_exp.label(text="Unity FBX Settings:", icon='EXPORT')
            box_exp.prop(props, "asset_name", text="アセット名")
            box_exp.prop(props, "export_folder", text="")
            box_exp.operator("mesh.open_export_folder", text="📂 保存先フォルダを開く", icon='FOLDER_REDIRECT')

# =============================================================
# 11. Registration
# =============================================================
classes = (
    PropStudioProperties,
    MESH_OT_reroll_selected_prop,
    MESH_OT_create_new_prop,
    MESH_OT_apply_random_texture_only,
    MESH_OT_export_selected_fbx,
    MESH_OT_open_export_folder,
    VIEW3D_PT_prop_studio_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.prop_studio_props = bpy.props.PointerProperty(type=PropStudioProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.prop_studio_props

if __name__ == "__main__":
    register()
