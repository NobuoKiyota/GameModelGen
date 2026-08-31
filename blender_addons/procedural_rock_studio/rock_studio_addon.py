bl_info = {
    "name": "Procedural Prop Studio Pro",
    "author": "Antigravity & User",
    "version": "6.1.0",
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Prop Studio",
    "description": "Procedural Prop Studio with Complete Antique Furniture Suite: Bookshelves, Tables, Chairs, Chests, and Beds",
    "category": "Add Mesh",
}

import bpy
import bmesh
import math
import random
import os
import ast
import shutil
import subprocess
import mathutils
import addon_utils

# Auto-enable Sapling Tree Gen if available
try:
    addon_utils.enable("add_curve_sapling", default_set=True)
except Exception:
    pass

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

def apply_image_texture_material(obj, image_path, scale=1.0, bump_strength=0.35, is_transparent=False, slot_index=None):
    if not os.path.exists(image_path):
        return None
    
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
    node_bsdf.inputs['Roughness'].default_value = 0.8
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
        node_bump.inputs['Distance'].default_value = 0.08
        links.new(node_img.outputs['Color'], node_bump.inputs['Height'])
        links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    if slot_index is not None:
        while len(obj.data.materials) <= slot_index:
            obj.data.materials.append(None)
        obj.data.materials[slot_index] = mat
    else:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    
    return mat

def create_procedural_bark_material(mat_name, seed=0, species="OAK"):
    """Procedural Bark Material matching Sapling Tree Gen tutorials (Wave Texture vertical woodgrain + Noise + Bump)"""
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (650, 0)

    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (350, 0)
    node_bsdf.inputs['Roughness'].default_value = 0.88
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-900, 0)
    
    node_map = nodes.new(type='ShaderNodeMapping')
    node_map.location = (-700, 0)
    # Stretch vertically along Z and offset position based on seed
    node_map.inputs['Location'].default_value = (float((seed * 37) % 100), float((seed * 71) % 100), float((seed * 19) % 100))
    node_map.inputs['Scale'].default_value = (1.0, 1.0, 0.15)
    links.new(node_coord.outputs['Object'], node_map.inputs['Vector'])

    # 1. Wave Texture for vertical bark grooves
    node_wave = nodes.new(type='ShaderNodeTexWave')
    node_wave.location = (-480, 120)
    node_wave.wave_type = 'BANDS'
    node_wave.bands_direction = 'X'
    node_wave.inputs['Scale'].default_value = 4.5 + float((seed % 7) * 0.2)
    node_wave.inputs['Distortion'].default_value = 5.5 + float((seed % 9) * 0.3)
    node_wave.inputs['Detail'].default_value = 4.0
    node_wave.inputs['Detail Roughness'].default_value = 0.75
    node_wave.inputs['Phase Offset'].default_value = float((seed % 100) * 0.08)
    links.new(node_map.outputs['Vector'], node_wave.inputs['Vector'])

    # 2. Fine Noise Texture for bark surface roughness
    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-480, -150)
    node_noise.inputs['Scale'].default_value = 13.0 + float((seed % 5) * 0.5)
    node_noise.inputs['Detail'].default_value = 8.0
    node_noise.inputs['Roughness'].default_value = 0.8
    links.new(node_map.outputs['Vector'], node_noise.inputs['Vector'])

    # 3. Mix Wave and Noise
    node_mix = nodes.new(type='ShaderNodeMix')
    node_mix.data_type = 'FLOAT'
    node_mix.location = (-260, 0)
    node_mix.inputs['Factor'].default_value = 0.4
    links.new(node_wave.outputs['Color'], node_mix.inputs[2])
    links.new(node_noise.outputs['Fac'], node_mix.inputs[3])

    # 4. ColorRamp tailored per species
    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_ramp.location = (-50, 100)

    # Seed-based brightness tone shift
    tone_shift = ((seed % 11) - 5) * 0.008

    if species == "BIRCH":
        # White Birch with black bark fissures
        node_ramp.color_ramp.elements[0].position = 0.18
        node_ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.05, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.55
        node_ramp.color_ramp.elements[1].color = (max(0.7, 0.88 + tone_shift), max(0.7, 0.88 + tone_shift), max(0.68, 0.85 + tone_shift), 1.0)
    elif species == "PINE":
        # Reddish-brown rough pine bark
        node_ramp.color_ramp.elements[0].position = 0.22
        node_ramp.color_ramp.elements[0].color = (0.12 + tone_shift, 0.06 + tone_shift, 0.03, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.75
        node_ramp.color_ramp.elements[1].color = (0.35 + tone_shift, 0.18 + tone_shift, 0.11, 1.0)
    elif species == "JAPANESE_MAPLE":
        # Smooth elegant grey-brown bark
        node_ramp.color_ramp.elements[0].position = 0.25
        node_ramp.color_ramp.elements[0].color = (0.18 + tone_shift, 0.14 + tone_shift, 0.11, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.75
        node_ramp.color_ramp.elements[1].color = (0.38 + tone_shift, 0.32 + tone_shift, 0.26, 1.0)
    else: # OAK / WILLOW
        # Deep aged dark brown oak bark
        node_ramp.color_ramp.elements[0].position = 0.2
        node_ramp.color_ramp.elements[0].color = (0.10 + tone_shift, 0.07 + tone_shift, 0.04, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.8
        node_ramp.color_ramp.elements[1].color = (0.32 + tone_shift, 0.23 + tone_shift, 0.16, 1.0)

    links.new(node_mix.outputs[0], node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

    # 5. Deep Bark Bump Normal
    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.location = (120, -150)
    node_bump.inputs['Strength'].default_value = 0.75
    node_bump.inputs['Distance'].default_value = 0.06
    links.new(node_mix.outputs[0], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat

def create_procedural_leaf_material(mat_name, seed=0, species="OAK"):
    """Procedural Leaf Material matching Sapling Tree Gen tutorials (Object Info Random Color Variation + Subsurface Scattering)"""
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (650, 0)

    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (350, 0)
    node_bsdf.inputs['Roughness'].default_value = 0.38
    # Enable subtle SSS (Subsurface Scattering) for leaf translucency
    try:
        node_bsdf.inputs['Subsurface Weight'].default_value = 0.2
    except Exception:
        try:
            node_bsdf.inputs['Subsurface'].default_value = 0.2
        except Exception:
            pass

    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    # 1. Object Info Random for leaf-to-leaf color variations
    node_objinfo = nodes.new(type='ShaderNodeObjectInfo')
    node_objinfo.location = (-750, 150)

    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-750, -100)
    node_noise.inputs['Scale'].default_value = 18.0 + float((seed % 7) * 0.8)
    node_noise.inputs['Detail'].default_value = 4.0

    node_mix = nodes.new(type='ShaderNodeMix')
    node_mix.data_type = 'FLOAT'
    node_mix.location = (-450, 50)
    node_mix.inputs['Factor'].default_value = 0.45 + float((seed % 10) * 0.015)
    links.new(node_objinfo.outputs['Random'], node_mix.inputs[2])
    links.new(node_noise.outputs['Fac'], node_mix.inputs[3])

    # 2. ColorRamp with rich botanical palettes per species
    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_ramp.location = (-200, 50)

    # Seed-based hue/warmth shift
    hue_var = ((seed % 13) - 6) * 0.01

    if species == "JAPANESE_MAPLE":
        # 🍁 Japanese Autumn Maple: Crimson Red -> Warm Orange -> Golden Yellow
        node_ramp.color_ramp.elements[0].position = 0.1
        node_ramp.color_ramp.elements[0].color = (0.75 + hue_var, 0.06, 0.02, 1.0)
        
        elem_mid = node_ramp.color_ramp.elements.new(0.55)
        elem_mid.color = (0.92, 0.38 + hue_var, 0.05, 1.0)
        
        node_ramp.color_ramp.elements[2].position = 0.9
        node_ramp.color_ramp.elements[2].color = (0.85, 0.68 + hue_var, 0.08, 1.0)
    elif species == "PINE":
        # 🌲 Conifer Pine: Deep forest dark pine needle green
        node_ramp.color_ramp.elements[0].position = 0.15
        node_ramp.color_ramp.elements[0].color = (0.04, 0.15 + hue_var, 0.06, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.85
        node_ramp.color_ramp.elements[1].color = (0.10, 0.28 + hue_var, 0.12, 1.0)
    elif species == "BIRCH":
        # ⚪ White Birch: Fresh vibrant spring lime green
        node_ramp.color_ramp.elements[0].position = 0.2
        node_ramp.color_ramp.elements[0].color = (0.22, 0.52 + hue_var, 0.10, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.8
        node_ramp.color_ramp.elements[1].color = (0.42, 0.68 + hue_var, 0.14, 1.0)
    elif species == "WILLOW":
        # 🌿 Weeping Willow: Soft sage light green
        node_ramp.color_ramp.elements[0].position = 0.2
        node_ramp.color_ramp.elements[0].color = (0.16, 0.38 + hue_var, 0.15, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.8
        node_ramp.color_ramp.elements[1].color = (0.35, 0.56 + hue_var, 0.20, 1.0)
    else: # OAK / Deciduous
        # 🌳 Oak: Rich lush deciduous canopy green
        node_ramp.color_ramp.elements[0].position = 0.2
        node_ramp.color_ramp.elements[0].color = (0.12, 0.32 + hue_var, 0.06, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.8
        node_ramp.color_ramp.elements[1].color = (0.26, 0.54 + hue_var, 0.12, 1.0)

    links.new(node_mix.outputs[0], node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

    # 3. Micro vein bump
    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.location = (120, -150)
    node_bump.inputs['Strength'].default_value = 0.25
    node_bump.inputs['Distance'].default_value = 0.02
    links.new(node_noise.outputs['Fac'], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat

def create_procedural_pbr_material(mat_name, seed=0, is_grass=False):
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (650, 0)

    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (350, 0)
    node_bsdf.inputs['Roughness'].default_value = 0.75
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
        node_ramp.color_ramp.elements[0].color = (0.08, 0.22, 0.05, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.8
        node_ramp.color_ramp.elements[1].color = (0.28, 0.48, 0.12, 1.0)
    else:
        node_ramp.color_ramp.elements[0].position = 0.25
        node_ramp.color_ramp.elements[0].color = (0.15, 0.11, 0.08, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.75
        node_ramp.color_ramp.elements[1].color = (0.42, 0.32, 0.24, 1.0)
        
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
# 2. Antique Column / Leg Geometry Generator
# =============================================================
def build_antique_leg_or_column(bm, height, radius, style="ORNAMENTAL", is_twist=False, seed=0):
    random.seed(seed)
    all_verts = []
    
    if style == "SIMPLE":
        res = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=radius, radius2=radius, depth=height
        )
        all_verts.extend(res['verts'])
        
    elif style == "REINFORCED":
        shaft_h = height * 0.8
        cap_h = height * 0.1
        res_s = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=radius * 0.85, radius2=radius * 0.85, depth=shaft_h
        )
        all_verts.extend(res_s['verts'])
        
        res_tc = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(radius * 2.4, radius * 2.4, cap_h), verts=res_tc['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, height * 0.45), verts=res_tc['verts'])
        all_verts.extend(res_tc['verts'])
        
        res_bc = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(radius * 2.4, radius * 2.4, cap_h), verts=res_bc['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, -height * 0.45), verts=res_bc['verts'])
        all_verts.extend(res_bc['verts'])

    elif style == "TWISTED" or is_twist:
        res = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=radius * 0.9, radius2=radius * 0.9, depth=height * 0.8
        )
        bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=8, use_grid_fill=True)
        
        for v in bm.verts:
            z_fac = (v.co.z / (height * 0.8))
            angle = z_fac * math.pi * 3.0
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            x_new = v.co.x * cos_a - v.co.y * sin_a
            y_new = v.co.x * sin_a + v.co.y * cos_a
            v.co.x = x_new
            v.co.y = y_new
        all_verts.extend(bm.verts[:])
        
        cap_h = height * 0.1
        res_tc = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(radius * 2.2, radius * 2.2, cap_h), verts=res_tc['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, height * 0.45), verts=res_tc['verts'])
        all_verts.extend(res_tc['verts'])
        
        res_bc = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(radius * 2.2, radius * 2.2, cap_h), verts=res_bc['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, -height * 0.45), verts=res_bc['verts'])
        all_verts.extend(res_bc['verts'])

    else: # ORNAMENTAL
        shaft_h = height * 0.76
        cap_h = height * 0.12
        res_s = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=radius * 0.65, radius2=radius * 0.65, depth=shaft_h
        )
        all_verts.extend(res_s['verts'])
        
        res_ub = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=radius * 1.35)
        bmesh.ops.scale(bm, vec=(1.0, 1.0, 0.8), verts=res_ub['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, height * 0.22), verts=res_ub['verts'])
        all_verts.extend(res_ub['verts'])

        res_lb = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=radius * 1.35)
        bmesh.ops.scale(bm, vec=(1.0, 1.0, 0.8), verts=res_lb['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, -height * 0.22), verts=res_lb['verts'])
        all_verts.extend(res_lb['verts'])

        res_mr = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=radius * 1.1, radius2=radius * 1.1, depth=height * 0.05
        )
        all_verts.extend(res_mr['verts'])

        res_tc = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(radius * 2.3, radius * 2.3, cap_h), verts=res_tc['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, height * 0.44), verts=res_tc['verts'])
        all_verts.extend(res_tc['verts'])
        
        res_bc = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(radius * 2.3, radius * 2.3, cap_h), verts=res_bc['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, -height * 0.44), verts=res_bc['verts'])
        all_verts.extend(res_bc['verts'])

    return all_verts

# =============================================================
# 3. Dedicated Geometry Builders: Furniture Suite
# =============================================================
def build_bookshelf_base(bm, size_x, size_y, size_z, tiers=3, column_style="ORNAMENTAL", seed=0):
    random.seed(seed)
    w = size_x
    d = size_y
    h = size_z
    board_th = 0.04
    col_rad = min(w, d) * 0.06
    
    # Back Plate
    res_back = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w - board_th * 2.0, board_th * 0.5, h), verts=res_back['verts'])
    bmesh.ops.translate(bm, vec=(0, -d * 0.5 + board_th * 0.25, 0), verts=res_back['verts'])
    
    # Side Panels
    res_lside = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(board_th, d, h), verts=res_lside['verts'])
    bmesh.ops.translate(bm, vec=(-w * 0.5 + board_th * 0.5, 0, 0), verts=res_lside['verts'])
    
    res_rside = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(board_th, d, h), verts=res_rside['verts'])
    bmesh.ops.translate(bm, vec=(w * 0.5 - board_th * 0.5, 0, 0), verts=res_rside['verts'])
    
    # Top & Bottom Crown Boards
    res_top = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w * 1.06, d * 1.06, board_th * 1.5), verts=res_top['verts'])
    bmesh.ops.translate(bm, vec=(0, 0, h * 0.5 - board_th * 0.75), verts=res_top['verts'])

    res_bot = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w * 1.04, d * 1.04, board_th * 1.5), verts=res_bot['verts'])
    bmesh.ops.translate(bm, vec=(0, 0, -h * 0.5 + board_th * 0.75), verts=res_bot['verts'])
    
    # Inner Shelves (2-4 tiers)
    shelf_count = max(2, min(4, tiers))
    inner_h = h - board_th * 3.0
    step_z = inner_h / float(shelf_count)
    for s in range(1, shelf_count):
        cur_z = -h * 0.5 + board_th * 1.5 + (s * step_z)
        res_sh = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w - board_th * 2.2, d * 0.94, board_th), verts=res_sh['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.02, cur_z), verts=res_sh['verts'])

    # Symmetrical Front Ornamental Side Columns
    for sign_x in [-1, 1]:
        bm_col = bmesh.new()
        build_antique_leg_or_column(bm_col, height=h * 0.96, radius=col_rad, style=column_style, seed=seed)
        for v in bm_col.verts:
            v.co.x += sign_x * (w * 0.5 - col_rad * 1.2)
            v.co.y += (d * 0.5 - col_rad * 0.8)
        for f in bm_col.faces:
            bm.faces.new([bm.verts.new(v.co) for v in f.verts])
        bm_col.free()
    
    return bm.verts[:]

def build_table_base(bm, size_x, size_y, size_z, shape="RECTANGLE", leg_style="ORNAMENTAL", seed=0):
    """Generates an Antique Table or Modern PC Desk / Workstation with steel loop or pipe legs"""
    random.seed(seed)
    w = size_x
    d = size_y
    h = size_z
    top_th = 0.035 if shape in ("MODERN_DESK", "MONITOR_RISER_DESK", "L_SHAPED_CORNER") else 0.05
    leg_h = h - top_th
    
    # 1. 🖥️ Tabletop Construction
    if shape == "OVAL":
        res_top = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=32,
            radius1=1.0, radius2=1.0, depth=top_th
        )
        bmesh.ops.scale(bm, vec=(w * 0.5, d * 0.5, 1.0), verts=res_top['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, h * 0.5 - top_th * 0.5), verts=res_top['verts'])
    elif shape == "ROUNDED_RECT":
        res_top = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w, d, top_th), verts=res_top['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, h * 0.5 - top_th * 0.5), verts=res_top['verts'])
        bmesh.ops.bevel(bm, geom=res_top['verts'], offset=min(w, d) * 0.08, segments=3)
    elif shape == "L_SHAPED_CORNER":
        # Main top
        res_main = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w, d * 0.6, top_th), verts=res_main['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.2, h * 0.5 - top_th * 0.5), verts=res_main['verts'])
        # Side return top
        res_side = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.45, d * 0.8, top_th), verts=res_side['verts'])
        bmesh.ops.translate(bm, vec=(w * 0.275, d * 0.2, h * 0.5 - top_th * 0.5), verts=res_side['verts'])
    elif shape == "MONITOR_RISER_DESK":
        # Main PC Desk top
        res_top = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w, d, top_th), verts=res_top['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, h * 0.5 - top_th * 0.5), verts=res_top['verts'])
        # 🖥️ Upper Monitor Shelf Riser (モニタースタンド棚)
        shelf_w = w * 0.85
        shelf_d = d * 0.32
        shelf_h = 0.12
        res_riser = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(shelf_w, shelf_d, 0.02), verts=res_riser['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.3, h * 0.5 + shelf_h), verts=res_riser['verts'])
        # Shelf mini steel legs
        for sx in [-shelf_w * 0.45, shelf_w * 0.45]:
            for sy in [-d * 0.3 - shelf_d * 0.4, -d * 0.3 + shelf_d * 0.4]:
                res_sleg = bmesh.ops.create_cone(
                    bm, cap_ends=True, cap_tris=False, segments=8,
                    radius1=0.012, radius2=0.012, depth=shelf_h
                )
                bmesh.ops.translate(bm, vec=(sx, sy, h * 0.5 + shelf_h * 0.5), verts=res_sleg['verts'])
    else: # RECTANGLE or MODERN_DESK
        res_top = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w, d, top_th), verts=res_top['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, h * 0.5 - top_th * 0.5), verts=res_top['verts'])

    # 2. 🦿 Leg Framework (近代スチール口の字脚 / 丸パイプ脚 / アンティーク4本脚)
    if leg_style == "STEEL_LOOP" or shape in ("MODERN_DESK", "MONITOR_RISER_DESK") and leg_style != "STEEL_PIPE" and leg_style not in ("ORNAMENTAL", "TWISTED", "REINFORCED"):
        # 🌟 Modern Square Steel Loop Legs (左右のスタイリッシュな口の字型ブラックスチール脚)
        pipe_w = 0.035
        for sx in [-w * 0.42, w * 0.42]:
            # Left/Right Vertical Pillars
            res_v1 = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(pipe_w, pipe_w, leg_h), verts=res_v1['verts'])
            bmesh.ops.translate(bm, vec=(sx, -d * 0.38, 0), verts=res_v1['verts'])

            res_v2 = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(pipe_w, pipe_w, leg_h), verts=res_v2['verts'])
            bmesh.ops.translate(bm, vec=(sx, d * 0.38, 0), verts=res_v2['verts'])

            # Bottom Foot Bar
            res_b = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(pipe_w, d * 0.8, pipe_w), verts=res_b['verts'])
            bmesh.ops.translate(bm, vec=(sx, 0, -leg_h * 0.5 + pipe_w * 0.5), verts=res_b['verts'])

            # Top Mount Bar
            res_t = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(pipe_w, d * 0.8, pipe_w), verts=res_t['verts'])
            bmesh.ops.translate(bm, vec=(sx, 0, leg_h * 0.5 - pipe_w * 0.5), verts=res_t['verts'])

        # Rear Cross Stretcher Beam (背面の横揺れ防止ビーム)
        res_cross = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.84, pipe_w * 0.8, pipe_w * 0.8), verts=res_cross['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.38, -leg_h * 0.2), verts=res_cross['verts'])

    elif leg_style == "STEEL_PIPE":
        # 🌟 Modern Steel Round Pipe Legs + Reinforcement Underframe
        pipe_rad = 0.02
        for (lx, ly) in [(-w * 0.42, -d * 0.4), (w * 0.42, -d * 0.4), (-w * 0.42, d * 0.4), (w * 0.42, d * 0.4)]:
            res_pipe = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=16,
                radius1=pipe_rad, radius2=pipe_rad, depth=leg_h
            )
            bmesh.ops.translate(bm, vec=(lx, ly, 0), verts=res_pipe['verts'])
        # Underframe steel apron
        res_uf = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.84, d * 0.8, 0.03), verts=res_uf['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, leg_h * 0.5 - 0.015), verts=res_uf['verts'])

    else:
        # 🌟 Classic Antique Turned/Reinforced 4 Legs with Wood Apron
        apron_h = 0.08
        res_apron_f = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.82, 0.025, apron_h), verts=res_apron_f['verts'])
        bmesh.ops.translate(bm, vec=(0, d * 0.36, h * 0.5 - top_th - apron_h * 0.5), verts=res_apron_f['verts'])
        
        res_apron_b = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.82, 0.025, apron_h), verts=res_apron_b['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.36, h * 0.5 - top_th - apron_h * 0.5), verts=res_apron_b['verts'])

        leg_rad = max(0.03, min(w, d) * 0.055)
        offset_x = (w * 0.5) * 0.78 * (0.82 if shape == "OVAL" else 1.0)
        offset_y = (d * 0.5) * 0.76 * (0.82 if shape == "OVAL" else 1.0)

        for (lx, ly) in [(-offset_x, -offset_y), (offset_x, -offset_y), (-offset_x, offset_y), (offset_x, offset_y)]:
            bm_leg = bmesh.new()
            build_antique_leg_or_column(bm_leg, height=leg_h, radius=leg_rad, style=leg_style, seed=seed)
            for v in bm_leg.verts:
                v.co.x += lx
                v.co.y += ly
                v.co.z += (-top_th * 0.5)
            for f in bm_leg.faces:
                bm.faces.new([bm.verts.new(v.co) for v in f.verts])
            bm_leg.free()

    return bm.verts[:]

def build_chair_base(
    bm, size_x, size_y, size_z,
    chair_type="DINING_CHAIR",
    leg_style="ORNAMENTAL",
    seat_style="CUSHION",
    back_style="SOLID",
    leg_layout="FOUR_LEGS",
    seed=0
):
    """Generates an Antique Chair / Stool or Modern Office Task Chair / Shell Chair (YouTube chan14 method)"""
    random.seed(seed)
    w = size_x
    d = size_y
    h = size_z
    seat_h = h * 0.46
    seat_th = 0.06
    leg_h = seat_h - seat_th
    
    # 🌟 A. 近代オフィスチェア (Modern Office Task Chair with 5-Star Casters & Gas Cylinder)
    if chair_type == "OFFICE_TASK_CHAIR":
        # 1. Ergonomic Curved Padded Seat (エルゴノミクスカーブ座面)
        res_seat = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w, d, seat_th), verts=res_seat['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, seat_h - seat_th * 0.5), verts=res_seat['verts'])
        for v in res_seat['verts']:
            if v.co.z > (seat_h - seat_th * 0.5):
                nx = max(0.0, 1.0 - abs(v.co.x / (w * 0.5)))
                ny = max(0.0, 1.0 - abs(v.co.y / (d * 0.5)))
                v.co.z += (nx * ny + 0.4) * 0.02
        bmesh.ops.bevel(bm, geom=res_seat['verts'], offset=0.02, segments=2)

        # 2. Ergonomic Mesh Curved Backrest (カーブ背もたれ ＆ 背面サポートフレーム)
        back_h = h - seat_h
        res_back = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.88, 0.035, back_h * 0.85), verts=res_back['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.44, seat_h + back_h * 0.45), verts=res_back['verts'])
        for v in res_back['verts']:
            # Gentle spine curve
            curve = math.sin((v.co.z - seat_h) / back_h * math.pi) * 0.03
            v.co.y += curve
        bmesh.ops.bevel(bm, geom=res_back['verts'], offset=0.015, segments=2)

        # Rear L-Support Spine (背もたれを座面下から支えるスチール製L字フレーム)
        res_spine = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(0.06, 0.04, back_h * 0.7), verts=res_spine['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.48, seat_h + back_h * 0.35), verts=res_spine['verts'])

        # 3. Modern T-Shaped Armrests (左右のT字アームレスト)
        arm_h = back_h * 0.45
        for sx in [-w * 0.48, w * 0.48]:
            # Vertical post
            res_apost = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=12,
                radius1=0.018, radius2=0.018, depth=arm_h
            )
            bmesh.ops.translate(bm, vec=(sx, 0, seat_h + arm_h * 0.5), verts=res_apost['verts'])
            # Top arm pad
            res_apad = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(0.06, d * 0.55, 0.025), verts=res_apad['verts'])
            bmesh.ops.translate(bm, vec=(sx, 0, seat_h + arm_h + 0.012), verts=res_apad['verts'])
            bmesh.ops.bevel(bm, geom=res_apad['verts'], offset=0.008, segments=2)

        # 4. Central Gas Cylinder Column (中央ガスシリンダー支柱 ＆ メカニカル受け台)
        res_cyl = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=0.03, radius2=0.025, depth=leg_h * 0.8
        )
        bmesh.ops.translate(bm, vec=(0, 0, leg_h * 0.45), verts=res_cyl['verts'])

        # 5. 5-Star Caster Base (星型に放射状に伸びる五叉キャスター脚)
        base_r = min(w, d) * 0.65
        for i in range(5):
            ang = math.radians(i * 72.0)
            res_leg_bar = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(0.035, base_r, 0.025), verts=res_leg_bar['verts'])
            bmesh.ops.translate(bm, vec=(0, base_r * 0.5, 0.04), verts=res_leg_bar['verts'])
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(ang, 3, 'Z'), verts=res_leg_bar['verts'])
            
            # Caster Wheel (各脚先端の回転キャスター車輪)
            res_caster = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=12,
                radius1=0.025, radius2=0.025, depth=0.02
            )
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'Y'), verts=res_caster['verts'])
            bmesh.ops.translate(bm, vec=(math.sin(ang) * base_r, math.cos(ang) * base_r, 0.025), verts=res_caster['verts'])

        return bm.verts[:]

    # 🌟 B. 北欧風モダンシェルチェア (Modern Eames-style Shell Chair with splayed dowel legs)
    elif chair_type == "MODERN_SHELL_CHAIR":
        # 1. Seamless Molded Shell Body (一体成型シェル座面＆背もたれ)
        res_seat = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w, d * 0.95, 0.025), verts=res_seat['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, seat_h), verts=res_seat['verts'])
        
        back_h = h - seat_h
        res_back = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.88, 0.025, back_h * 0.85), verts=res_back['verts'])
        bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(-10), 3, 'X'), verts=res_back['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.4, seat_h + back_h * 0.45), verts=res_back['verts'])

        # 2. Splayed Symmetrical Wood/Steel Legs (外側にハの字に広がる4本脚)
        leg_rad = 0.016
        for (lx, ly, rot_x, rot_y) in [
            (-w * 0.32, -d * 0.32, 10, -10),
            (w * 0.32, -d * 0.32, 10, 10),
            (-w * 0.32, d * 0.32, -10, -10),
            (w * 0.32, d * 0.32, -10, 10)
        ]:
            res_sleg = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=12,
                radius1=leg_rad * 1.2, radius2=leg_rad * 0.7, depth=leg_h
            )
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(rot_x), 3, 'X'), verts=res_sleg['verts'])
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(rot_y), 3, 'Y'), verts=res_sleg['verts'])
            bmesh.ops.translate(bm, vec=(lx, ly, leg_h * 0.5), verts=res_sleg['verts'])

        # Eiffel Wire Cross Bracing (ワイヤークロス補強)
        res_wire = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.6, d * 0.6, 0.01), verts=res_wire['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, leg_h * 0.8), verts=res_wire['verts'])

        return bm.verts[:]

    # 🌟 C. クラシック・アンティークチェア (Dining Chair, Armchair, Stool)
    # 1. Cushion / Seat Construction (ふっくら革張りクッション座面 / 木製座面)
    if chair_type == "ROUND_STOOL":
        rad = w * 0.46
        res_uf = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=24,
            radius1=rad * 0.92, radius2=rad * 0.92, depth=0.03
        )
        bmesh.ops.translate(bm, vec=(0, 0, seat_h - seat_th + 0.015), verts=res_uf['verts'])

        if seat_style == "CUSHION":
            res_cushion = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=24,
                radius1=rad, radius2=rad * 0.94, depth=seat_th
            )
            for v in res_cushion['verts']:
                if v.co.z > 0:
                    r_dist = math.sqrt(v.co.x**2 + v.co.y**2) / rad
                    v.co.z += (1.0 - r_dist) * 0.025
            bmesh.ops.translate(bm, vec=(0, 0, seat_h - seat_th * 0.5), verts=res_cushion['verts'])
        else:
            res_seat = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=24,
                radius1=rad, radius2=rad, depth=seat_th
            )
            bmesh.ops.translate(bm, vec=(0, 0, seat_h - seat_th * 0.5), verts=res_seat['verts'])

    else: # Dining Chair, Armchair, Square Stool
        res_uf = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.88, d * 0.88, 0.04), verts=res_uf['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, seat_h - seat_th + 0.02), verts=res_uf['verts'])

        res_seat = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w, d, seat_th), verts=res_seat['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, seat_h - seat_th * 0.5), verts=res_seat['verts'])
        if seat_style == "CUSHION":
            for v in res_seat['verts']:
                if v.co.z > (seat_h - seat_th * 0.5):
                    nx = max(0.0, 1.0 - abs(v.co.x / (w * 0.5)))
                    ny = max(0.0, 1.0 - abs(v.co.y / (d * 0.5)))
                    v.co.z += (nx * ny + 0.5) * 0.02 # Plump dome
        bmesh.ops.bevel(bm, geom=res_seat['verts'], offset=0.015, segments=2)

    # 2. Leg Structure (1本中央台座脚 / Xクロス脚 / 3本脚 / 4本脚)
    if leg_layout == "PEDESTAL_ONE":
        col_rad = min(w, d) * 0.12
        bm_col = bmesh.new()
        build_antique_leg_or_column(bm_col, height=leg_h * 0.95, radius=col_rad, style=leg_style, seed=seed)
        for v in bm_col.verts:
            v.co.z += (leg_h * 0.5)
        for f in bm_col.faces:
            bm.faces.new([bm.verts.new(v.co) for v in f.verts])
        bm_col.free()

        foot_len = min(w, d) * 0.42
        for ang in [45, 135, 225, 315]:
            rad_ang = math.radians(ang)
            res_foot = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=8,
                radius1=0.035, radius2=0.02, depth=foot_len
            )
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(75), 3, 'X'), verts=res_foot['verts'])
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(rad_ang, 3, 'Z'), verts=res_foot['verts'])
            bmesh.ops.translate(bm, vec=(math.cos(rad_ang) * (foot_len * 0.45), math.sin(rad_ang) * (foot_len * 0.45), 0.04), verts=res_foot['verts'])

    elif leg_layout == "X_CROSS":
        x_th = min(w, d) * 0.06
        for sx in [-w * 0.36, w * 0.36]:
            res_b1 = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(x_th, 0.04, leg_h * 1.1), verts=res_b1['verts'])
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(28), 3, 'X'), verts=res_b1['verts'])
            bmesh.ops.translate(bm, vec=(sx, 0, leg_h * 0.5), verts=res_b1['verts'])

            res_b2 = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(x_th, 0.04, leg_h * 1.1), verts=res_b2['verts'])
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(-28), 3, 'X'), verts=res_b2['verts'])
            bmesh.ops.translate(bm, vec=(sx, 0, leg_h * 0.5), verts=res_b2['verts'])

        res_str = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.02, radius2=0.02, depth=w * 0.72)
        bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'Y'), verts=res_str['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, leg_h * 0.5), verts=res_str['verts'])

    elif leg_layout == "TRIPOD_THREE":
        leg_rad = min(w, d) * 0.055
        dist_r = min(w, d) * 0.32
        for ang in [90, 210, 330]:
            rad_ang = math.radians(ang)
            lx = math.cos(rad_ang) * dist_r
            ly = math.sin(rad_ang) * dist_r
            bm_leg = bmesh.new()
            build_antique_leg_or_column(bm_leg, height=leg_h, radius=leg_rad, style=leg_style, seed=seed)
            for v in bm_leg.verts:
                v.co.x += lx
                v.co.y += ly
                v.co.z += (leg_h * 0.5)
            for f in bm_leg.faces:
                bm.faces.new([bm.verts.new(v.co) for v in f.verts])
            bm_leg.free()

    else: # FOUR_LEGS (Default)
        leg_rad = min(w, d) * 0.055
        if chair_type == "ROUND_STOOL":
            offset_x = (w * 0.5) * 0.58
            offset_y = (d * 0.5) * 0.58
        else:
            offset_x = (w * 0.5) * 0.72
            offset_y = (d * 0.5) * 0.72

        for (lx, ly) in [(-offset_x, -offset_y), (offset_x, -offset_y), (-offset_x, offset_y), (offset_x, offset_y)]:
            bm_leg = bmesh.new()
            build_antique_leg_or_column(bm_leg, height=leg_h, radius=leg_rad, style=leg_style, seed=seed)
            for v in bm_leg.verts:
                v.co.x += lx
                v.co.y += ly
                v.co.z += (leg_h * 0.5)
            for f in bm_leg.faces:
                bm.faces.new([bm.verts.new(v.co) for v in f.verts])
            bm_leg.free()

    # 3. Backrest & Armrest (Dining Chair & Armchair)
    if chair_type in ("DINING_CHAIR", "ARMCHAIR"):
        back_h = h - seat_h
        post_rad = min(w, d) * 0.045
        
        # Left & Right Back Posts
        for sx in [-w * 0.42, w * 0.42]:
            bm_post = bmesh.new()
            build_antique_leg_or_column(bm_post, height=back_h, radius=post_rad, style=leg_style, seed=seed)
            for v in bm_post.verts:
                v.co.x += sx
                v.co.y += (-d * 0.42)
                v.co.z += (seat_h + back_h * 0.5)
            for f in bm_post.faces:
                bm.faces.new([bm.verts.new(v.co) for v in f.verts])
            bm_post.free()

        # Top Crest Rail
        res_top_rail = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.94, 0.045, 0.08), verts=res_top_rail['verts'])
        bmesh.ops.translate(bm, vec=(0, -d * 0.42, h - 0.04), verts=res_top_rail['verts'])
        bmesh.ops.bevel(bm, geom=res_top_rail['verts'], offset=0.015, segments=2)

        # Backrest Style
        if back_style == "SOLID":
            res_panel = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(w * 0.76, 0.025, back_h * 0.78), verts=res_panel['verts'])
            bmesh.ops.translate(bm, vec=(0, -d * 0.42, seat_h + back_h * 0.45), verts=res_panel['verts'])
            bmesh.ops.bevel(bm, geom=res_panel['verts'], offset=0.01, segments=2)

        elif back_style == "OVAL":
            res_oval = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=24,
                radius1=1.0, radius2=1.0, depth=0.025
            )
            bmesh.ops.scale(bm, vec=(w * 0.36, back_h * 0.38, 1.0), verts=res_oval['verts'])
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'X'), verts=res_oval['verts'])
            bmesh.ops.translate(bm, vec=(0, -d * 0.42, seat_h + back_h * 0.48), verts=res_oval['verts'])

        else: # SPINDLE
            num_spindles = 4
            step = (w * 0.68) / (num_spindles - 1)
            for i in range(num_spindles):
                sp_x = -w * 0.34 + i * step
                res_sp = bmesh.ops.create_cone(
                    bm, cap_ends=True, cap_tris=False, segments=8,
                    radius1=0.014, radius2=0.014, depth=back_h * 0.88
                )
                bmesh.ops.translate(bm, vec=(sp_x, -d * 0.42, seat_h + back_h * 0.46), verts=res_sp['verts'])

        # 4. Armchair Full Armrests (Spanning from Back Post to Front of Seat)
        if chair_type == "ARMCHAIR":
            arm_h = back_h * 0.42
            arm_len = d * 0.82
            arm_z = seat_h + arm_h
            
            for sx in [-w * 0.45, w * 0.45]:
                # Front Arm Support Post
                res_arm_post = bmesh.ops.create_cone(
                    bm, cap_ends=True, cap_tris=False, segments=12,
                    radius1=0.02, radius2=0.018, depth=arm_h
                )
                bmesh.ops.translate(bm, vec=(sx, d * 0.28, seat_h + arm_h * 0.5), verts=res_arm_post['verts'])

                # Horizontal Armrest Pad
                res_arm_pad = bmesh.ops.create_cube(bm, size=1.0)
                bmesh.ops.scale(bm, vec=(0.055, arm_len, 0.03), verts=res_arm_pad['verts'])
                bmesh.ops.translate(bm, vec=(sx, -d * 0.06, arm_z), verts=res_arm_pad['verts'])
                bmesh.ops.bevel(bm, geom=res_arm_pad['verts'], offset=0.01, segments=2)

    return bm.verts[:]

def build_chest_base(bm, size_x, size_y, size_z, tiers=3, handle_style="RING", seed=0):
    """Generates an antique Chest of Drawers with 2-5 drawers, raised panel frames, and hardware handles"""
    random.seed(seed)
    w = size_x
    d = size_y
    h = size_z
    leg_h = h * 0.14
    body_h = h - leg_h
    body_z_center = -h * 0.5 + leg_h + body_h * 0.5
    
    # 1. Main Cabinet Body (本体箱)
    res_body = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w * 0.94, d * 0.94, body_h), verts=res_body['verts'])
    bmesh.ops.translate(bm, vec=(0, 0, body_z_center), verts=res_body['verts'])
    
    # 2. Top Crown Board (天板モールディング)
    res_top = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w * 1.04, d * 1.04, 0.05), verts=res_top['verts'])
    bmesh.ops.translate(bm, vec=(0, 0, h * 0.5 - 0.025), verts=res_top['verts'])

    # 3. 4 Base Feet (4つのアンティーク台座脚)
    foot_rad = min(w, d) * 0.07
    offset_x = (w * 0.5) * 0.8
    offset_y = (d * 0.5) * 0.8
    for (lx, ly) in [(-offset_x, -offset_y), (offset_x, -offset_y), (-offset_x, offset_y), (offset_x, offset_y)]:
        res_foot = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=foot_rad)
        bmesh.ops.scale(bm, vec=(1.1, 1.1, (leg_h / (foot_rad * 2.0))), verts=res_foot['verts'])
        bmesh.ops.translate(bm, vec=(lx, ly, -h * 0.5 + leg_h * 0.5), verts=res_foot['verts'])

    # 4. Drawers & Handles (2 ~ 5段の引き出し)
    drawer_count = max(2, min(5, tiers))
    drawer_h = (body_h * 0.88) / float(drawer_count)
    front_y = d * 0.5 * 0.94
    
    for i in range(drawer_count):
        cur_z = (-h * 0.5 + leg_h + (body_h * 0.06)) + (i + 0.5) * drawer_h
        
        # Drawer Front Panel (引き出し前板)
        res_dp = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.86, 0.025, drawer_h * 0.88), verts=res_dp['verts'])
        bmesh.ops.translate(bm, vec=(0, front_y + 0.012, cur_z), verts=res_dp['verts'])
        
        # Raised Panel Molding (立体飾り縁)
        res_frame = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(w * 0.8, 0.015, drawer_h * 0.72), verts=res_frame['verts'])
        bmesh.ops.translate(bm, vec=(0, front_y + 0.025, cur_z), verts=res_frame['verts'])

        # Handles (左右2個の取っ手)
        for hx in [-w * 0.24, w * 0.24]:
            if handle_style == "KNOB":
                # Antique Round Knob
                res_knob = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.018)
                bmesh.ops.translate(bm, vec=(hx, front_y + 0.045, cur_z), verts=res_knob['verts'])
            elif handle_style == "BAR":
                # Horizontal Bar
                res_bar = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.008, radius2=0.008, depth=0.09)
                bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'Y'), verts=res_bar['verts'])
                bmesh.ops.translate(bm, vec=(hx, front_y + 0.04, cur_z), verts=res_bar['verts'])
            else: # RING
                # Drop Ring Handle
                res_ring = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=0.022, radius2=0.022, depth=0.008)
                bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'X'), verts=res_ring['verts'])
                bmesh.ops.translate(bm, vec=(hx, front_y + 0.04, cur_z - 0.01), verts=res_ring['verts'])

    return bm.verts[:]

def build_bed_base(bm, size_x, size_y, size_z, bed_size="SINGLE", leg_style="ORNAMENTAL", seed=0):
    """Generates an antique Bedframe with Headboard, Footboard, Posts, and Mattress"""
    random.seed(seed)
    
    # Standard Bed Dimensions
    if bed_size == "KING":
        w = 2.0
    elif bed_size == "DOUBLE":
        w = 1.6
    else: # SINGLE
        w = 1.2
        
    d = max(size_y, 2.0)
    h = size_z
    frame_h = 0.35
    head_h = h
    foot_h = h * 0.65
    post_rad = 0.065
    
    # 1. 4 Corner Antique Posts (四隅の装飾支柱)
    offset_x = w * 0.5
    offset_y = d * 0.5
    
    # Head Posts (高い頭側ポスト 2本)
    for sx in [-offset_x, offset_x]:
        bm_hp = bmesh.new()
        build_antique_leg_or_column(bm_hp, height=head_h, radius=post_rad, style=leg_style, seed=seed)
        for v in bm_hp.verts:
            v.co.x += sx
            v.co.y += -offset_y
            v.co.z += (head_h * 0.5)
        for f in bm_hp.faces:
            bm.faces.new([bm.verts.new(v.co) for v in f.verts])
        bm_hp.free()

    # Foot Posts (足側ポスト 2本)
    for sx in [-offset_x, offset_x]:
        bm_fp = bmesh.new()
        build_antique_leg_or_column(bm_fp, height=foot_h, radius=post_rad, style=leg_style, seed=seed)
        for v in bm_fp.verts:
            v.co.x += sx
            v.co.y += offset_y
            v.co.z += (foot_h * 0.5)
        for f in bm_fp.faces:
            bm.faces.new([bm.verts.new(v.co) for v in f.verts])
        bm_fp.free()

    # 2. Headboard Panel (頭側装飾背板)
    res_hb = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w - post_rad * 1.5, 0.04, head_h * 0.65), verts=res_hb['verts'])
    bmesh.ops.translate(bm, vec=(0, -offset_y, frame_h + (head_h * 0.65) * 0.5), verts=res_hb['verts'])

    # 3. Footboard Panel (足側装飾板)
    res_fb = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w - post_rad * 1.5, 0.04, foot_h * 0.5), verts=res_fb['verts'])
    bmesh.ops.translate(bm, vec=(0, offset_y, frame_h + (foot_h * 0.5) * 0.5), verts=res_fb['verts'])

    # 4. Bed Side Rails & Platform (サイドフレーム＆床板)
    res_lrail = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.04, d, 0.12), verts=res_lrail['verts'])
    bmesh.ops.translate(bm, vec=(-offset_x + post_rad * 0.5, 0, frame_h), verts=res_lrail['verts'])
    
    res_rrail = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.04, d, 0.12), verts=res_rrail['verts'])
    bmesh.ops.translate(bm, vec=(offset_x - post_rad * 0.5, 0, frame_h), verts=res_rrail['verts'])

    # 5. Mattress (ふっくらマットレス)
    mat_th = 0.24
    res_mat = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w * 0.88, d * 0.9, mat_th), verts=res_mat['verts'])
    bmesh.ops.translate(bm, vec=(0, 0, frame_h + mat_th * 0.5 + 0.02), verts=res_mat['verts'])
    bmesh.ops.bevel(bm, geom=res_mat['verts'], offset=0.04, segments=2)

    return bm.verts[:]

# =============================================================
# 4. Standard Base Geometry Builders
# =============================================================
def build_grass_mound_base(bm, size_x, size_y, size_z, shape="SQUARE", seed=0):
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
    else:
        verts = bmesh.ops.create_cube(bm, size=1.0)['verts']
        bmesh.ops.scale(bm, vec=(size_x, size_y, size_z), verts=verts)

    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=4, use_grid_fill=True)
    for v in bm.verts:
        if v.co.z > 0:
            nx = math.sin(v.co.x * 1.8 + seed) * math.cos(v.co.y * 1.8 + seed)
            ny = math.cos(v.co.x * 2.2 + seed * 2) * math.sin(v.co.y * 2.2 + seed * 2)
            v.co.z += (nx + ny) * (size_z * 0.18)
    return bm.verts[:]

def build_grass_tuft_clump(bm, size_x, size_y, size_z, blade_count=4, seed=0):
    random.seed(seed)
    h = size_z
    w = max(size_x, size_y) * 0.5
    angles = [0, 45, 90, 135][:blade_count] if blade_count <= 4 else [i * (180.0 / blade_count) for i in range(blade_count)]
    for ang in angles:
        ang_rad = math.radians(ang + random.uniform(-8.0, 8.0))
        cur_w = w * random.uniform(0.85, 1.15)
        cur_h = h * random.uniform(0.85, 1.2)
        dx = math.cos(ang_rad) * (cur_w * 0.5)
        dy = math.sin(ang_rad) * (cur_w * 0.5)
        tilt_x = random.uniform(-0.06, 0.06) * cur_h
        tilt_y = random.uniform(-0.06, 0.06) * cur_h
        v_bl = bm.verts.new((-dx, -dy, 0.0))
        v_br = bm.verts.new((dx, dy, 0.0))
        v_tr = bm.verts.new((dx + tilt_x, dy + tilt_y, cur_h))
        v_tl = bm.verts.new((-dx + tilt_x, -dy + tilt_y, cur_h))
        bm.faces.new((v_bl, v_br, v_tr, v_tl))
    return bm.verts[:]

def build_convex_hull_rock(bm, size_x, size_y, size_z, point_count=18, is_crag=True, seed=0):
    """Generates 100% SOLID ultra-realistic procedural rocks via Convex Hull algorithm (YouTube Sacoche Ito 3D method)"""
    random.seed(seed)
    
    # 1. 🌟 Distribute Random 3D Points & Cloud Cluster (動画手法: ランダム点群＆キューブ群の配置)
    points = []
    
    # Main central bounding ellipsoid points
    num_pts = max(10, min(36, point_count))
    rx = size_x * 0.5
    ry = size_y * 0.5
    rz = size_z * 0.5
    
    for _ in range(num_pts):
        u = random.random()
        theta = random.uniform(0, math.pi * 2)
        phi = random.uniform(-math.pi * 0.5, math.pi * 0.5)
        # Power distribution for faceted corners
        rad_scale = (u ** 0.5) if is_crag else (u ** 0.8)
        px = math.cos(phi) * math.cos(theta) * rx * rad_scale
        py = math.cos(phi) * math.sin(theta) * ry * rad_scale
        pz = math.sin(phi) * rz * rad_scale
        
        # Additional asymmetric directional push
        if is_crag:
            px += (random.random() - 0.5) * (rx * 0.3)
            py += (random.random() - 0.5) * (ry * 0.3)
            pz += (random.random() - 0.5) * (rz * 0.3)
        points.append((px, py, pz))

    # Add 2~4 sub-chunk satellite points for jagged mountain clusters
    if is_crag:
        sub_clusters = random.randint(2, 4)
        for _ in range(sub_clusters):
            c_center_x = random.uniform(-rx * 0.6, rx * 0.6)
            c_center_y = random.uniform(-ry * 0.6, ry * 0.6)
            c_center_z = random.uniform(-rz * 0.4, rz * 0.2)
            c_rad = min(rx, ry, rz) * random.uniform(0.3, 0.6)
            for _ in range(6):
                ang = random.uniform(0, math.pi * 2)
                p_phi = random.uniform(-math.pi * 0.5, math.pi * 0.5)
                points.append((
                    c_center_x + math.cos(p_phi) * math.cos(ang) * c_rad,
                    c_center_y + math.cos(p_phi) * math.sin(ang) * c_rad,
                    c_center_z + math.sin(p_phi) * c_rad
                ))

    # Create vertices in bmesh
    created_verts = [bm.verts.new(p) for p in points]
    bm.verts.ensure_lookup_table()

    # 2. 📐 Execute CONVEX HULL (凸包を実行して一発で中身の詰まった多面体岩を形成)
    res_hull = bmesh.ops.convex_hull(
        bm,
        input=created_verts,
        use_existing_faces=False
    )

    # Delete un-used internal vertices
    internal_verts = [v for v in created_verts if v not in res_hull['geom']]
    bmesh.ops.delete(bm, geom=internal_verts, context='VERTS')

    # 3. ⚡ Edge Chipping & Bevel (角の欠けと岩肌の微細ディテール)
    hull_geom = [e for e in res_hull['geom'] if isinstance(e, bmesh.types.BMEdge)]
    if hull_geom and is_crag:
        try:
            bmesh.ops.bevel(
                bm,
                geom=hull_geom,
                offset=min(rx, ry, rz) * 0.04,
                segments=1,
                profile=0.7
            )
        except Exception:
            pass

    return bm.verts[:]

def build_rock_base(bm, size_x, size_y, size_z, style="BOULDER"):
    """Generates natural weathered rounded boulders & stones via Convex Hull"""
    return build_convex_hull_rock(bm, size_x, size_y, size_z, point_count=24, is_crag=False)

def build_crag_base(bm, size_x, size_y, size_z, style="JAGGED_CRAG", chisel_cuts=6, seed=0):
    """Generates ultra-rugged jagged crags via Convex Hull with satellite cluster points"""
    pts = 16 if style in ("SHARP", "FRACTURED") else 22
    return build_convex_hull_rock(bm, size_x, size_y, size_z, point_count=pts, is_crag=True, seed=seed)

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
    else:
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
    else:
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
    return all_verts

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
    """Generates an authentic procedural tree using Blender's official Sapling Tree Gen addon (Game-optimized lightweight mesh)"""
    if context.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

    try:
        addon_utils.enable("add_curve_sapling", default_set=True)
    except Exception:
        pass

    # Save target object's transform if re-rolling in place
    old_loc = target_obj.location.copy() if target_obj else mathutils.Vector((0, 0, 0))
    old_rot = target_obj.rotation_euler.copy() if target_obj else mathutils.Euler((0, 0, 0))
    old_name = target_obj.name if target_obj else name

    # Clear previous active tree objects or old target if replacing
    for obj in list(bpy.data.objects):
        if obj.name in ('tree', 'leaves') or "treemesh" in obj.name.lower() or "leavesmesh" in obj.name.lower():
            bpy.data.objects.remove(obj, do_unlink=True)
    if target_obj and target_obj in bpy.data.objects.values():
        bpy.data.objects.remove(target_obj, do_unlink=True)

    # Deterministic random generator from seed for randomized leaves
    rng = random.Random(seed)
    num_l = max(20, min(300, leaf_count if not target_obj else leaf_count + rng.randint(-15, 25)))
    bl = max(1, min(3, branch_levels))

    # Randomized leaf shapes and dynamics
    leaf_shapes = ['hex', 'rect', 'dFace', 'dVert']
    chosen_leaf_shape = rng.choice(leaf_shapes)
    rand_leaf_scale = rng.uniform(0.25, 0.45)
    rand_leaf_scale_x = rng.uniform(0.5, 1.0)
    rand_leaf_down_angle = rng.uniform(30.0, 75.0)

    base_scale = max(2.5, size_z)

    if species == "PINE":
        # 🌲 Pine / Conifer (円錐状・常緑針葉樹)
        tree_args = {
            'do_update': True,
            'bevel': True,
            'bevelRes': 1,
            'resU': 2,
            'curveRes': (4, 3, 2, 1),
            'levels': bl,
            'branches': (35, 12, 0, 0),
            'scale': base_scale,
            'scale0': 1.0,
            'shape': '7',
            'baseSize': 0.25,
            'downAngle': (75.0 + rng.uniform(-10, 10), 45.0, 0.0, 0.0),
            'rotate': (140.0, 140.0, 0.0, 0.0),
            'showLeaves': has_leaves,
            'leaves': num_l,
            'leafScale': rand_leaf_scale * 0.75,
            'leafScaleX': 0.35,
            'leafShape': 'dFace',
            'leafDownAngle': rand_leaf_down_angle,
            'seed': seed,
            'makeMesh': True
        }
    elif species == "WILLOW":
        # 🌿 Weeping Willow (優雅にしだれる柳)
        tree_args = {
            'do_update': True,
            'bevel': True,
            'bevelRes': 1,
            'resU': 2,
            'curveRes': (4, 3, 2, 1),
            'levels': bl,
            'branches': (28, 16, 8, 0),
            'scale': base_scale,
            'scale0': 1.0,
            'shape': '2',
            'baseSize': 0.35,
            'curve': (-30.0 + rng.uniform(-10, 5), -45.0, 0.0, 0.0),
            'downAngle': (-15.0, 105.0 + rng.uniform(-15, 15), 45.0, 0.0),
            'rotate': (137.5, 137.5, 0.0, 0.0),
            'showLeaves': has_leaves,
            'leaves': num_l,
            'leafScale': rand_leaf_scale,
            'leafScaleX': rand_leaf_scale_x * 0.7,
            'leafShape': chosen_leaf_shape,
            'leafDownAngle': rand_leaf_down_angle + 20.0,
            'seed': seed,
            'makeMesh': True
        }
    elif species == "JAPANESE_MAPLE":
        # 🍁 Japanese Maple (盆栽風・水平に広がる和風の紅葉)
        tree_args = {
            'do_update': True,
            'bevel': True,
            'bevelRes': 1,
            'resU': 2,
            'curveRes': (4, 3, 2, 1),
            'levels': bl,
            'branches': (22, 14, 6, 0),
            'scale': base_scale,
            'scale0': 1.0,
            'baseSplits': 2,
            'splitAngle': (35.0, 30.0, 0.0, 0.0),
            'downAngle': (55.0 + rng.uniform(-10, 10), 60.0, 45.0, 0.0),
            'rotate': (137.5, 137.5, 0.0, 0.0),
            'showLeaves': has_leaves,
            'leaves': num_l,
            'leafScale': rand_leaf_scale * 0.85,
            'leafScaleX': rand_leaf_scale_x,
            'leafShape': 'hex',
            'leafDownAngle': rand_leaf_down_angle,
            'seed': seed,
            'makeMesh': True
        }
    elif species == "BIRCH":
        # ⚪ White Birch (すらりと伸びる白樺)
        tree_args = {
            'do_update': True,
            'bevel': True,
            'bevelRes': 1,
            'resU': 2,
            'curveRes': (4, 3, 2, 1),
            'levels': bl,
            'branches': (24, 12, 0, 0),
            'scale': base_scale,
            'scale0': 1.0,
            'shape': '4',
            'baseSize': 0.45,
            'downAngle': (50.0 + rng.uniform(-10, 10), 45.0, 0.0, 0.0),
            'rotate': (137.5, 137.5, 0.0, 0.0),
            'showLeaves': has_leaves,
            'leaves': num_l,
            'leafScale': rand_leaf_scale * 0.9,
            'leafScaleX': rand_leaf_scale_x,
            'leafShape': chosen_leaf_shape,
            'leafDownAngle': rand_leaf_down_angle,
            'seed': seed,
            'makeMesh': True
        }
    else: # OAK / Deciduous
        # 🌳 Oak / Deciduous (どっしりとした大木・自然な枝分かれの広葉樹)
        tree_args = {
            'do_update': True,
            'bevel': True,
            'bevelRes': 1,
            'resU': 2,
            'curveRes': (4, 3, 2, 1),
            'levels': bl,
            'branches': (25, 15, 6, 0),
            'scale': base_scale,
            'scale0': 1.0,
            'baseSplits': 2,
            'splitAngle': (30.0 + rng.uniform(-8, 8), 25.0, 0.0, 0.0),
            'downAngle': (45.0 + rng.uniform(-10, 10), 50.0, 35.0, 0.0),
            'rotate': (137.5, 137.5, 0.0, 0.0),
            'showLeaves': has_leaves,
            'leaves': num_l,
            'leafScale': rand_leaf_scale,
            'leafScaleX': rand_leaf_scale_x,
            'leafShape': chosen_leaf_shape,
            'leafDownAngle': rand_leaf_down_angle,
            'seed': seed,
            'makeMesh': True
        }

    try:
        bpy.ops.curve.tree_add(**tree_args)
    except Exception as e:
        print("Sapling Tree Gen call error:", e)

    tree_obj = bpy.data.objects.get('tree')
    leaves_obj = bpy.data.objects.get('leaves')

    # Convert curve tree to mesh
    if tree_obj and tree_obj.type == 'CURVE':
        bpy.ops.object.select_all(action='DESELECT')
        tree_obj.select_set(True)
        context.view_layer.objects.active = tree_obj
        bpy.ops.object.convert(target='MESH')

    # Apply materials (Procedural Shader vs Image Texture)
    if mat_mode == "PROCEDURAL":
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
    else:
        # Image Texture from folder
        tex_files_wood = get_textures_from_folder(r"Z:\MeshCreator\textures\Wood")
        if tree_obj:
            if tex_files_wood:
                bark_tex = random.choice(tex_files_wood)
                apply_image_texture_material(tree_obj, os.path.join(r"Z:\MeshCreator\textures\Wood", bark_tex), scale=1.0, bump_strength=0.45, slot_index=0)
            else:
                mat_bark = create_procedural_bark_material(old_name + "_Bark_Procedural", seed=seed, species=species)
                tree_obj.data.materials.append(mat_bark)

        if leaves_obj and has_leaves:
            tex_files_grass = get_textures_from_folder(r"Z:\MeshCreator\textures\Grass")
            if tex_files_grass:
                leaf_tex = random.choice(tex_files_grass)
                apply_image_texture_material(leaves_obj, os.path.join(r"Z:\MeshCreator\textures\Grass", leaf_tex), scale=1.0, bump_strength=0.25, is_transparent=True, slot_index=1)
            else:
                mat_leaf = create_procedural_leaf_material(old_name + "_Leaf_Procedural", seed=seed, species=species)
                leaves_obj.data.materials.append(mat_leaf)

    # Join tree and leaves into single unified prop mesh
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

    # Clean any leftover intermediate meshes created by Sapling
    for o in list(bpy.data.objects):
        if o != final_obj and ("treemesh" in o.name.lower() or "leavesmesh" in o.name.lower() or o.name in ('tree', 'leaves')):
            bpy.data.objects.remove(o, do_unlink=True)

    return final_obj

# =============================================================
# 5. Master Generator Core
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
    table_shape="RECTANGLE",
    table_leg_style="ORNAMENTAL",
    chair_type="DINING_CHAIR",
    chair_seat_style="CUSHION",
    chair_back_style="SOLID",
    chair_leg_layout="FOUR_LEGS",
    chest_tiers=3,
    chest_handle_style="RING",
    bed_size="SINGLE",
    shelf_tiers=3,
    column_style="ORNAMENTAL",
    tree_species="OAK",
    tree_has_leaves=True,
    tree_leaf_count=120,
    tree_branch_levels=2,
    tree_leaf_style="QUAD_CROSS",
    tree_curvature=0.6,
    tree_mat_mode="PROCEDURAL",
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
    if context.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

    random.seed(seed)

    # 🌳 Official Native Sapling Tree Gen Direct Call
    if category == "TREE":
        return generate_sapling_real_tree(
            context=context,
            target_obj=target_obj,
            name=name,
            species=tree_species,
            has_leaves=tree_has_leaves,
            leaf_count=tree_leaf_count,
            branch_levels=tree_branch_levels,
            mat_mode=tree_mat_mode,
            seed=seed,
            size_z=size_z
        )

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
    if category in ("CHAIR", "OFFICE_CHAIR"):
        build_chair_base(
            bm, size_x, size_y, size_z,
            chair_type=chair_type,
            leg_style=table_leg_style,
            seat_style=chair_seat_style,
            back_style=chair_back_style,
            leg_layout=chair_leg_layout,
            seed=seed
        )
    elif category == "CHEST":
        build_chest_base(bm, size_x, size_y, size_z, tiers=chest_tiers, handle_style=chest_handle_style, seed=seed)
    elif category == "BED":
        build_bed_base(bm, size_x, size_y, size_z, bed_size=bed_size, leg_style=column_style, seed=seed)
    elif category == "BOOKSHELF":
        build_bookshelf_base(bm, size_x, size_y, size_z, tiers=shelf_tiers, column_style=column_style, seed=seed)
    elif category in ("TABLE", "PC_DESK"):
        build_table_base(bm, size_x, size_y, size_z, shape=table_shape, leg_style=table_leg_style, seed=seed)
    elif category == "GRASS":
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
    elif category == "CRAG":
        build_crag_base(bm, size_x, size_y, size_z, style=style, chisel_cuts=big_chunk_cuts * 3 + 4, seed=seed)
    else: # ROCK (従来の丸岩・巨石)
        build_rock_base(bm, size_x, size_y, size_z, style=style)

    # Debris (Rock / Crag only)
    if create_debris and debris_count > 0 and category in ("ROCK", "CRAG"):
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

    # 2. Bevel for Furniture, Floor, Wall & Grass Mound
    if category in ("FLOOR", "WALL", "BOOKSHELF", "TABLE", "PC_DESK", "CHAIR", "OFFICE_CHAIR", "CHEST", "BED") or (category == "GRASS" and grass_mode == "MOUND"):
        bevel_mod = obj.modifiers.new(name="Bevel_Chipping", type='BEVEL')
        bevel_mod.width = 0.012 if category in ("BOOKSHELF", "TABLE", "PC_DESK", "CHAIR", "OFFICE_CHAIR", "CHEST", "BED") else min(0.03, (size_z if category != "WALL" else size_y) * 0.15)
        bevel_mod.segments = 2
        try:
            bpy.ops.object.modifier_apply(modifier=bevel_mod.name)
        except Exception:
            pass

    # 3. Subdivision & Displacements
    if category in ("ROCK", "CRAG", "PILLAR", "BEAM", "BEAM_ARCH"):
        subsurf = obj.modifiers.new(name="Subsurf_Base", type='SUBSURF')
        subsurf.render_levels = 1 if category == "CRAG" else (detail_level + 1)
        subsurf.levels = 1 if category == "CRAG" else (detail_level + 1)

        # Texture displacement
        tex_large = bpy.data.textures.new(name + "_Tex_Large", type='VORONOI' if category == "CRAG" else 'CLOUDS')
        if category == "CRAG":
            tex_large.noise_scale = 0.95
            tex_large.distance_metric = 'DISTANCE_SQUARED'
        else:
            tex_large.noise_scale = 1.6 if category in ("BEAM", "BEAM_ARCH") else 1.2
            tex_large.noise_depth = 2 if category in ("BEAM", "BEAM_ARCH") else 3
        
        disp_large = obj.modifiers.new(name="Disp_Large", type='DISPLACE')
        disp_large.texture = tex_large
        disp_large.strength = roughness * (0.45 if category == "CRAG" else 0.8)
        disp_large.mid_level = 0.5

        if chisel_strength > 0.05:
            tex_voronoi = bpy.data.textures.new(name + "_Tex_Chisel", type='VORONOI' if category in ("ROCK", "CRAG") else 'WOOD')
            tex_voronoi.noise_scale = 0.65 if category == "CRAG" else 0.8
            disp_voronoi = obj.modifiers.new(name="Disp_Chisel", type='DISPLACE')
            disp_voronoi.texture = tex_voronoi
            disp_voronoi.strength = chisel_strength * (0.35 if category == "CRAG" else 0.5)
            disp_voronoi.mid_level = 0.5

        if crack_depth > 0.05:
            tex_crack = bpy.data.textures.new(name + "_Tex_Crack", type='VORONOI')
            tex_crack.noise_scale = 0.4 if category == "CRAG" else 0.5
            tex_crack.distance_metric = 'DISTANCE_SQUARED'
            disp_crack = obj.modifiers.new(name="Disp_Crack", type='DISPLACE')
            disp_crack.texture = tex_crack
            disp_crack.strength = -crack_depth * (0.25 if category == "CRAG" else 0.4)
            disp_crack.mid_level = 0.85

    # 4. Apply Modifiers & Auto Smooth
    for p in mesh.polygons:
        p.use_smooth = True

    for mod in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception:
            pass

    if category == "CRAG":
        try:
            mesh.use_auto_smooth = True
            mesh.auto_smooth_angle = math.radians(40.0)
        except Exception:
            pass

    # 5. Smart UV Projection
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    if category == "GRASS" and grass_mode == "TUFT":
        bpy.ops.uv.smart_project(angle_limit=88.0, island_margin=0.0)
    elif category in ("FLOOR", "WALL", "BEAM", "BEAM_ARCH", "GRASS", "BOOKSHELF", "TABLE", "CHAIR", "CHEST", "BED"):
        if uv_mode == "FIT":
            max_dim = max(size_x, size_y, size_z)
            bpy.ops.uv.cube_project(cube_size=max_dim, correct_aspect=True, clip_to_bounds=True)
        else:
            bpy.ops.uv.cube_project(cube_size=2.0 / max(0.1, tex_tiling), correct_aspect=True)
    else: # ROCK
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
        
    # 6. Material Assignment
    if category == "TREE":
        # Slot 0: Bark (Wood Bark Texture)
        tex_files_wood = get_textures_from_folder(r"Z:\MeshCreator\textures\Wood")
        if tex_files_wood:
            bark_tex = chosen_tex if (chosen_tex and chosen_tex in tex_files_wood) else random.choice(tex_files_wood)
            apply_image_texture_material(obj, os.path.join(r"Z:\MeshCreator\textures\Wood", bark_tex), scale=1.0, bump_strength=0.45, slot_index=0)
        else:
            mat_bark = create_procedural_pbr_material(name + "_Bark_Mat", seed)
            obj.data.materials.append(mat_bark)

        # Slot 1: Leaves (Grass / Leaf Texture with Alpha Transparency)
        tex_files_grass = get_textures_from_folder(r"Z:\MeshCreator\textures\Grass")
        if tex_files_grass:
            leaf_tex = random.choice(tex_files_grass)
            apply_image_texture_material(obj, os.path.join(r"Z:\MeshCreator\textures\Grass", leaf_tex), scale=1.0, bump_strength=0.25, is_transparent=True, slot_index=1)
        else:
            mat_leaf = create_procedural_pbr_material(name + "_Leaves_Mat", seed + 7, is_grass=True)
            obj.data.materials.append(mat_leaf)
    else:
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
# 6. Helper to Resolve Parameters
# =============================================================
def resolve_prop_parameters(props):
    cat = props.prop_category
    types = ['JAGGED_CRAG', 'COLUMNAR_CLIFF', 'VOLCANIC_SPIKE', 'FRACTURED', 'SHARP', 'BOULDER']
    final_type = random.choice(types) if props.rand_type else props.rock_type
    
    if props.rand_dimensions:
        if cat == "CHAIR":
            final_sx = round(random.uniform(0.48, 0.62), 2)
            final_sy = round(random.uniform(0.48, 0.62), 2)
            final_sz = round(random.uniform(0.85, 1.1), 2)
        elif cat == "CHEST":
            final_sx = round(random.uniform(1.2, 1.8), 2)
            final_sy = round(random.uniform(0.5, 0.7), 2)
            final_sz = round(random.uniform(0.9, 1.4), 2)
        elif cat == "BED":
            final_sx = round(random.uniform(1.2, 2.0), 2)
            final_sy = round(random.uniform(2.0, 2.2), 2)
            final_sz = round(random.uniform(1.2, 1.6), 2)
        elif cat == "BOOKSHELF":
            final_sx = round(random.uniform(1.2, 2.0), 2)
            final_sy = round(random.uniform(0.4, 0.65), 2)
            final_sz = round(random.uniform(1.8, 2.4), 2)
        elif cat == "TABLE":
            final_sx = round(random.uniform(1.4, 2.4), 2)
            final_sy = round(random.uniform(0.8, 1.4), 2)
            final_sz = round(random.uniform(0.7, 0.9), 2)
        elif cat in ("FLOOR", "GRASS"):
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

    tex_files = get_textures_from_folder(props.texture_folder)
    if props.rand_texture and tex_files:
        chosen_tex = random.choice(tex_files)
    else:
        chosen_tex = props.selected_texture if (props.selected_texture in tex_files) else (tex_files[0] if tex_files else "")

    leg_styles = ['STEEL_LOOP', 'STEEL_PIPE', 'SIMPLE', 'REINFORCED', 'ORNAMENTAL', 'TWISTED']
    final_leg_style = random.choice(leg_styles) if props.rand_furniture_style else props.table_leg_style
    final_col_style = random.choice(['SIMPLE', 'REINFORCED', 'ORNAMENTAL', 'TWISTED']) if props.rand_furniture_style else props.column_ornament_style
    table_shapes = ['MODERN_DESK', 'MONITOR_RISER_DESK', 'L_SHAPED_CORNER', 'RECTANGLE', 'ROUNDED_RECT', 'OVAL']
    final_table_shape = random.choice(table_shapes) if props.rand_furniture_style else props.table_shape
    
    chair_backs = ['SOLID', 'SPINDLE', 'OVAL']
    final_chair_back = random.choice(chair_backs) if props.rand_furniture_style else props.chair_back_style
    chair_seats = ['CUSHION', 'WOOD_FLAT']
    final_chair_seat = random.choice(chair_seats) if props.rand_furniture_style else props.chair_seat_style
    chair_legs = ['FOUR_LEGS', 'PEDESTAL_ONE', 'X_CROSS', 'TRIPOD_THREE']
    final_chair_leg = random.choice(chair_legs) if props.rand_furniture_style else props.chair_leg_layout

    return {
        "category": cat,
        "style": final_type,
        "floor_shape": props.floor_shape,
        "wall_shape": props.wall_shape,
        "grass_mode": props.grass_mode,
        "table_shape": final_table_shape,
        "table_leg_style": final_leg_style,
        "chair_type": props.chair_type,
        "chair_seat_style": final_chair_seat,
        "chair_back_style": final_chair_back,
        "chair_leg_layout": final_chair_leg,
        "chest_tiers": props.chest_tiers,
        "chest_handle_style": props.chest_handle_style,
        "bed_size": props.bed_size,
        "shelf_tiers": props.shelf_tiers,
        "column_style": final_col_style,
        "tree_species": props.tree_species,
        "tree_has_leaves": props.tree_has_leaves,
        "tree_leaf_style": props.tree_leaf_style,
        "tree_leaf_count": props.tree_leaf_count,
        "tree_branch_levels": props.tree_branch_levels,
        "tree_curvature": props.tree_curvature,
        "tree_mat_mode": props.tree_material_mode,
        "uv_mode": props.uv_mapping_mode,
        "size_x": final_sx,
        "size_y": final_sy,
        "size_z": final_sz,
        "roughness": props.roughness,
        "chisel_strength": props.chisel_strength,
        "crack_depth": props.crack_depth,
        "big_chunk_cuts": props.big_chunk_cuts,
        "crack_count": props.floor_crack_count,
        "create_debris": False if cat in ("FLOOR", "WALL", "GRASS", "BOOKSHELF", "TABLE", "PC_DESK", "CHAIR", "OFFICE_CHAIR", "CHEST", "BED", "TREE") else props.create_debris,
        "debris_count": props.debris_count,
        "detail_level": props.detail_level,
        "tex_folder": props.texture_folder,
        "use_folder_tex": props.use_folder_texture,
        "selected_tex": chosen_tex,
        "tex_tiling": props.texture_tiling,
    }

# =============================================================
# 7. Clean Unity FBX Exporter
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

        copied_textures = []
        for mat in active_obj.data.materials:
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image and node.image.filepath:
                        src_img = bpy.path.abspath(node.image.filepath)
                        if os.path.exists(src_img):
                            try:
                                dst_img = os.path.join(export_dir, os.path.basename(src_img))
                                shutil.copy2(src_img, dst_img)
                                copied_textures.append(os.path.basename(src_img))
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
        if copied_textures:
            msg += f" (テクスチャ同封: {', '.join(set(copied_textures))})"
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
        try:
            subprocess.Popen(f'explorer "{export_dir}"')
            self.report({'INFO'}, f"Opened: {export_dir}")
        except Exception as e:
            self.report({'WARNING'}, f"Could not open folder: {e}")
        return {'FINISHED'}

# =============================================================
# 8. Core Operators
# =============================================================
class MESH_OT_reroll_selected_prop(bpy.types.Operator):
    """Re-roll and morph the selected prop in-place with new random seed & texture"""
    bl_idname = "mesh.reroll_selected_prop"
    bl_label = "Re-Roll Selected Prop"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass

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
            table_shape=p["table_shape"],
            table_leg_style=p["table_leg_style"],
            chair_type=p["chair_type"],
            chair_seat_style=p["chair_seat_style"],
            chair_back_style=p["chair_back_style"],
            chair_leg_layout=p["chair_leg_layout"],
            chest_tiers=p["chest_tiers"],
            chest_handle_style=p["chest_handle_style"],
            bed_size=p["bed_size"],
            shelf_tiers=p["shelf_tiers"],
            column_style=p["column_style"],
            tree_species=p["tree_species"],
            tree_has_leaves=p["tree_has_leaves"],
            tree_leaf_style=p["tree_leaf_style"],
            tree_leaf_count=p["tree_leaf_count"],
            tree_branch_levels=p["tree_branch_levels"],
            tree_curvature=p["tree_curvature"],
            tree_mat_mode=p["tree_mat_mode"],
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
        if context.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass

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
            table_shape=p["table_shape"],
            table_leg_style=p["table_leg_style"],
            chair_type=p["chair_type"],
            chair_seat_style=p["chair_seat_style"],
            chair_back_style=p["chair_back_style"],
            chair_leg_layout=p["chair_leg_layout"],
            chest_tiers=p["chest_tiers"],
            chest_handle_style=p["chest_handle_style"],
            bed_size=p["bed_size"],
            shelf_tiers=p["shelf_tiers"],
            column_style=p["column_style"],
            tree_species=p["tree_species"],
            tree_has_leaves=p["tree_has_leaves"],
            tree_leaf_style=p["tree_leaf_style"],
            tree_leaf_count=p["tree_leaf_count"],
            tree_branch_levels=p["tree_branch_levels"],
            tree_curvature=p["tree_curvature"],
            tree_mat_mode=p["tree_mat_mode"],
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
# 9. Category Preset Callback
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
        'ROCK': "Rock_Boulder",
        'CRAG': "Crag_Rock",
        'TREE': "Real_Tree",
        'PC_DESK': "Modern_PC_Desk",
        'OFFICE_CHAIR': "Modern_Office_Chair",
        'FLOOR': "Floor_Tile",
        'WALL': "Wall_Block",
        'PILLAR': "Pillar_Column",
        'BEAM': "Timber_Beam",
        'BEAM_ARCH': "Beam_Arch",
        'GRASS': "Grass_Meadow",
        'BOOKSHELF': "Antique_Bookshelf",
        'TABLE': "Antique_Table",
        'CHAIR': "Antique_Chair",
        'CHEST': "Antique_Chest",
        'BED': "Antique_Bed"
    }
    props.asset_name = name_map.get(cat, "Prop_Asset")

    if cat == "TREE":
        props.size_x = 3.5
        props.size_y = 3.5
        props.size_z = 4.5
        props.uv_mapping_mode = 'FIT'
    elif cat in ("ROCK", "CRAG"):
        props.size_x = 2.2
        props.size_y = 2.0
        props.size_z = 1.6
        props.uv_mapping_mode = 'TILING'
    elif cat == "PC_DESK":
        props.size_x = 1.6
        props.size_y = 0.75
        props.size_z = 0.72
        props.table_shape = 'MONITOR_RISER_DESK'
        props.table_leg_style = 'STEEL_LOOP'
        props.uv_mapping_mode = 'FIT'
    elif cat == "OFFICE_CHAIR":
        props.size_x = 0.62
        props.size_y = 0.60
        props.size_z = 0.96
        props.chair_type = 'OFFICE_TASK_CHAIR'
        props.uv_mapping_mode = 'FIT'
    elif cat == "CHAIR":
        props.size_x = 0.55
        props.size_y = 0.55
        props.size_z = 0.95
        props.chair_type = 'DINING_CHAIR'
        props.uv_mapping_mode = 'FIT'
    elif cat == "CHEST":
        props.size_x = 1.4
        props.size_y = 0.6
        props.size_z = 1.1
        props.chest_tiers = 3
        props.chest_handle_style = 'RING'
        props.uv_mapping_mode = 'FIT'
    elif cat == "BED":
        props.size_x = 1.4
        props.size_y = 2.1
        props.size_z = 1.35
        props.bed_size = 'SINGLE'
        props.uv_mapping_mode = 'FIT'
    elif cat == "BOOKSHELF":
        props.size_x = 1.6
        props.size_y = 0.5
        props.size_z = 2.1
        props.shelf_tiers = 3
        props.column_ornament_style = 'ORNAMENTAL'
        props.uv_mapping_mode = 'FIT'
    elif cat == "TABLE":
        props.size_x = 1.8
        props.size_y = 1.0
        props.size_z = 0.78
        props.table_shape = 'RECTANGLE'
        props.table_leg_style = 'ORNAMENTAL'
        props.uv_mapping_mode = 'FIT'
    elif cat == "GRASS":
        props.size_x = 3.0
        props.size_y = 3.0
        props.size_z = 0.3
        props.uv_mapping_mode = 'FIT'
    elif cat == "FLOOR":
        props.size_x = 2.0
        props.size_y = 2.0
        props.size_z = 0.2
        props.uv_mapping_mode = 'FIT'
    elif cat == "WALL":
        props.size_x = 3.0
        props.size_y = 1.0
        props.size_z = 2.5
        props.uv_mapping_mode = 'FIT'
    elif cat in ("BEAM", "BEAM_ARCH"):
        props.size_x = 2.4
        props.size_y = 1.5
        props.size_z = 2.0
        props.uv_mapping_mode = 'FIT'
    elif cat == "PILLAR":
        props.size_x = 1.2
        props.size_y = 1.2
        props.size_z = 2.5
        props.uv_mapping_mode = 'FIT'

    folder_map = {
        'ROCK': r"Z:\MeshCreator\textures\Rock",
        'CRAG': r"Z:\MeshCreator\textures\Rock",
        'TREE': r"Z:\MeshCreator\textures\Wood",
        'PC_DESK': r"Z:\MeshCreator\textures\Wood",
        'OFFICE_CHAIR': r"Z:\MeshCreator\textures\Wood",
        'FLOOR': r"Z:\MeshCreator\textures\Floor",
        'WALL': r"Z:\MeshCreator\textures\Wall",
        'PILLAR': r"Z:\MeshCreator\textures\Pillar",
        'BEAM': r"Z:\MeshCreator\textures\Wood",
        'BEAM_ARCH': r"Z:\MeshCreator\textures\Wood",
        'GRASS': r"Z:\MeshCreator\textures\Grass",
        'BOOKSHELF': r"Z:\MeshCreator\textures\Wood",
        'TABLE': r"Z:\MeshCreator\textures\Wood",
        'CHAIR': r"Z:\MeshCreator\textures\Wood",
        'CHEST': r"Z:\MeshCreator\textures\Wood",
        'BED': r"Z:\MeshCreator\textures\Wood"
    }
    
    target_folder = folder_map.get(cat, r"Z:\MeshCreator\textures\Rock")
    os.makedirs(target_folder, exist_ok=True)
    props.texture_folder = target_folder

# =============================================================
# 10. Property Group
# =============================================================
class PropStudioProperties(bpy.types.PropertyGroup):
    prop_category: bpy.props.EnumProperty(
        name="Category",
        items=[
            ('TREE', "🌳 リアル樹木・自然木 (Real Tree / Sapling)", "textures/Wood/ と自動連動（オーク/針葉樹/柳/ヤシ/白樺/紅葉・幹枝葉生成）"),
            ('PC_DESK', "🖥️ 近代PCデスク (Modern PC Desk)", "textures/Wood/ と自動連動（モニタースタンド付き・スチール口の字脚・L字型）"),
            ('OFFICE_CHAIR', "💺 近代オフィスチェア (Modern Office Chair)", "textures/Wood/ と自動連動（5本足キャスター＆ガスシリンダー＆シェル）"),
            ('TABLE', "🪑 アンティーク机 (Antique Table)", "textures/Wood/ と自動連動（四角/角丸/楕円＆アンティーク4本脚）"),
            ('CHAIR', "💺 アンティーク椅子 (Antique Chair)", "textures/Wood/ と自動連動（革張り座面/埋め込み背板/1本脚/X脚）"),
            ('BOOKSHELF', "📚 本棚・収納棚 (Bookshelf / Rack)", "textures/Wood/ と自動連動（2~4段棚＆対称装飾柱）"),
            ('CHEST', "🚪 チェスト・タンス (Chest of Drawers)", "textures/Wood/ と自動連動（2~5段引き出し＆取っ手金具）"),
            ('BED', "🛏️ アンティークベッド (Antique Bedframe)", "textures/Wood/ と自動連動（四隅装飾柱＆ヘッドボード＆マットレス）"),
            ('CRAG', "🏔️ 険岩・ごつごつ岩 (Jagged Crags)", "textures/Rock/ と自動連動（Convex Hull多面体＆鋭利な稜線岩）"),
            ('ROCK', "🪨 丸岩・巨石 (Round Boulder / Soft Rock)", "textures/Rock/ と自動連動（自然な丸みを持つ丸岩・河原の石）"),
            ('GRASS', "🌿 草原・草地 (Grassland / Meadow)", "textures/Grass/ と自動連動（草地丘陵スラブ＆十字草むら）"),
            ('FLOOR', "🟫 床・タイル (Floor / Tile)", "textures/Floor/ と自動連動（正方形・円形・六角形＆有機的亀裂）"),
            ('WALL', "🧱 壁・城壁 (Wall / Ruins)", "textures/Wall/ と自動連動（直線・L字・円弧・▲三角切妻壁）"),
            ('PILLAR', "🏛️ 柱・石柱 (Pillar / Column)", "textures/Pillar/ と自動連動"),
            ('BEAM', "🪵 梁・丸太支柱 (Timber Log Beam)", "textures/Wood/ と自動連動（シリンダー丸太梁）"),
            ('BEAM_ARCH', "🪵🏛️ 梁アーチ (Beam Arch)", "textures/Wood/ と自動連動（シリンダー丸太アーチ）")
        ],
        default='TREE',
        update=update_category_preset
    )

    studio_tab: bpy.props.EnumProperty(
        name="Studio Tab",
        items=[
            ('SHAPE', "📐 形状", "形状・寸法・家具パーツ設定"),
            ('TEX', "🎨 テクスチャ", "PBRテクスチャ連動・UVフィット設定"),
            ('EXPORT', "📦 出力", "Unity FBXエクスポート設定")
        ],
        default='SHAPE'
    )

    # Tree Specific (リアル樹木・自然木設定)
    tree_species: bpy.props.EnumProperty(
        name="樹種 (Tree Species)",
        items=[
            ('OAK', "🌳 オーク・カシ (Oak / Deciduous)", "どっしりとした大木・自然な枝分かれの広葉樹"),
            ('PINE', "🌲 パイン・マツ (Pine / Conifer)", "上に向かって三角錐状に広がる常緑針葉樹"),
            ('WILLOW', "🌿 シダレヤナギ (Weeping Willow)", "下に向かって優雅に垂れ下がる枝"),
            ('PALM', "🌴 ヤシの木 (Palm Tree)", "南国・ビーチの放射状大葉を持つヤシの木"),
            ('BIRCH', "⚪ シラカバ (Birch)", "すらりと伸びる白い幹の落葉樹"),
            ('JAPANESE_MAPLE', "🍁 モミジ・カエデ (Japanese Maple)", "繊細で風情ある和風の枝ぶり")
        ],
        default='OAK'
    )
    tree_has_leaves: bpy.props.BoolProperty(name="🍃 葉を付ける (Foliage)", default=True, description="葉（リーフクラスタ）を生成するか（OFFで冬の枯れ木・枝のみ）")
    tree_leaf_style: bpy.props.EnumProperty(
        name="葉の表現スタイル",
        items=[
            ('QUAD_CROSS', "🍃 十字リーフ (Cross Billboard)", "ゲーム向け最適化十字ビルボード葉（アルファ透過連動）"),
            ('CANOPY_VOLUME', "🌳 ボリューム樹冠 (Canopy Volume)", "アニメ調・スタイライズドローポリ樹冠クラスタ")
        ],
        default='QUAD_CROSS'
    )
    tree_leaf_count: bpy.props.IntProperty(name="葉の密度 (Leaf Density)", default=120, min=20, max=400, description="生成する葉クラスタの数量")
    tree_branch_levels: bpy.props.IntProperty(name="枝分かれ階層 (Branch Levels)", default=2, min=1, max=3, description="枝分かれの深さ (1:主枝のみ, 2:小枝あり, 3:細枝)")
    tree_curvature: bpy.props.FloatProperty(name="枝のうねり・曲がり度", default=0.6, min=0.0, max=1.0, description="幹や枝の自然なくねり・重力による垂れ下がり具合")
    tree_material_mode: bpy.props.EnumProperty(
        name="樹木マテリアル方式",
        items=[
            ('PROCEDURAL', "🎨 プロシージャルPBR (動画準拠)", "Wave Texture縦木目樹皮 ＆ 葉ごとのランダム色相・半透明シェーダー"),
            ('IMAGE_TEXTURE', "🖼️ 外部画像テクスチャ (Image Texture)", "Wood/Grassフォルダの画像ファイルを使用")
        ],
        default='PROCEDURAL',
        description="マテリアルの生成方式（画像不要のBlender完全内蔵プロシージャルシェーダーか、外部画像テクスチャか）"
    )

    # Chair specific
    chair_type: bpy.props.EnumProperty(
        name="椅子タイプ",
        items=[
            ('OFFICE_TASK_CHAIR', "💺 近代オフィスチェア (Modern Office Task Chair)", "5本足キャスター＆ガスシリンダー＆エルゴノミクス背もたれ"),
            ('MODERN_SHELL_CHAIR', "🪑 北欧風シェルチェア (Modern Shell Chair)", "イームズ風一体成型シェル座面＆ハの字脚"),
            ('DINING_CHAIR', "💺 背もたれチェア (Dining Chair)", "クラシックな背もたれ付き椅子"),
            ('ARMCHAIR', "🛋️ アームチェア (Armchair)", "肘掛け付きアンティークチェア"),
            ('ROUND_STOOL', "⚪ 丸スツール (Round Stool)", "円形座面の腰掛け"),
            ('SQUARE_STOOL', "🔲 角スツール (Square Stool)", "四角座面の腰掛け")
        ],
        default='OFFICE_TASK_CHAIR'
    )
    chair_seat_style: bpy.props.EnumProperty(
        name="座面スタイル",
        items=[
            ('CUSHION', "🛋️ 革張り・ふっくらクッション (Cushion)", "ふくらみのある革張り/ファブリック座面"),
            ('WOOD_FLAT', "🪵 フラット木製座面 (Wood Flat)", "クラシックな木製座面")
        ],
        default='CUSHION'
    )
    chair_back_style: bpy.props.EnumProperty(
        name="背もたれ形状",
        items=[
            ('SOLID', "🪵 埋め込み装飾背板 (Solid Panel)", "隙間のない重厚なアンティーク彫刻背板"),
            ('SPINDLE', "🪑 縦格子スピンドル (Spindles)", "座面と笠木を直結するクラシック格子"),
            ('OVAL', "🔘 楕円メダリオン (Oval Medallion)", "貴族風の楕円背もたれ")
        ],
        default='SOLID'
    )
    chair_leg_layout: bpy.props.EnumProperty(
        name="脚の配置構造",
        items=[
            ('FOUR_LEGS', "🦿 4本脚 (Four Legs)", "スタンダードな4本脚"),
            ('PEDESTAL_ONE', "🏛️ 1本中央台座脚 (Pedestal)", "中央の太いろくろ挽き柱＋広がるフット"),
            ('X_CROSS', "⚔️ Xクロス交差脚 (X-Cross)", "交差したスタイリッシュなX脚"),
            ('TRIPOD_THREE', "📐 3本脚 (Tripod 3-Legs)", "丸スツール等に最適な三脚")
        ],
        default='FOUR_LEGS'
    )

    # Chest specific
    chest_tiers: bpy.props.IntProperty(name="引き出し段数", default=3, min=2, max=5, description="チェストの引き出し段数 (2段〜5段)")
    chest_handle_style: bpy.props.EnumProperty(
        name="取っ手金具",
        items=[
            ('RING', "リング金具 (Ring Handle)", "アンティークなドロップリング金具"),
            ('KNOB', "丸ノブ (Round Knob)", "クラシックな丸型つまみ"),
            ('BAR', "水平バー (Bar Handle)", "水平ハンドルバー")
        ],
        default='RING'
    )

    # Bed specific
    bed_size: bpy.props.EnumProperty(
        name="ベッドサイズ",
        items=[
            ('SINGLE', "シングル (Single: 1.2m)", "幅 1.2m のベッド"),
            ('DOUBLE', "ダブル (Double: 1.6m)", "幅 1.6m のベッド"),
            ('KING', "キング (King: 2.0m)", "幅 2.0m の広々ベッド")
        ],
        default='SINGLE'
    )

    # Bookshelf specific
    shelf_tiers: bpy.props.IntProperty(name="棚の段数", default=3, min=2, max=4, description="本棚の棚板段数 (2段, 3段, 4段)")
    column_ornament_style: bpy.props.EnumProperty(
        name="柱装飾",
        items=[
            ('ORNAMENTAL', "アンティーク・ろくろ挽き (Turned)", "ビーズ・リング・コーンを重ねたクラシック装飾柱"),
            ('TWISTED', "螺旋・ツイスト (Twisted)", "スパイラル状のひねり装飾柱"),
            ('REINFORCED', "補強台座付き (Reinforced)", "上下にキャピタル台座を持つ柱"),
            ('SIMPLE', "シンプル角柱/円柱 (Simple)", "クリーンなストレート柱")
        ],
        default='ORNAMENTAL'
    )

    # Table specific
    table_shape: bpy.props.EnumProperty(
        name="天板形状",
        items=[
            ('MODERN_DESK', "🖥️ 近代PCデスク (Modern PC Desk)", "すっきりとしたストレートモダン天板"),
            ('MONITOR_RISER_DESK', "🖥️ モニタースタンド付きデスク (Monitor Riser Desk)", "液晶ディスプレイ棚・ライザー付きPCデスク"),
            ('L_SHAPED_CORNER', "📐 L字スタジオデスク (L-Shaped Corner Desk)", "広々としたL字型コーナースタジオデスク"),
            ('RECTANGLE', "🔲 スタンダード四角 (Rectangle)", "標準の長方形天板"),
            ('ROUNDED_RECT', "🔘 角丸長方形 (Rounded Rect)", "四隅が滑らかに丸まった天板"),
            ('OVAL', "⬭ 楕円 (Oval / Ellipse)", "美しい楕円形天板")
        ],
        default='MODERN_DESK'
    )
    table_leg_style: bpy.props.EnumProperty(
        name="脚の形状",
        items=[
            ('STEEL_LOOP', "⬛ 口の字スチール脚 (Steel Loop Legs)", "スタイリッシュなブラックスチール角パイプ脚"),
            ('STEEL_PIPE', "🔩 丸スチールパイプ脚 (Steel Round Pipe)", "スリムな丸パイプ脚＋補強ビーム"),
            ('ORNAMENTAL', "アンティーク・ろくろ挽き (Turned)", "球体ビーズ・リング・コーンの4本脚"),
            ('TWISTED', "螺旋・ツイスト (Twisted)", "スパイラルひねりの4本脚"),
            ('REINFORCED', "補強台座付き (Reinforced)", "上下に段差リング・台座を持つ4本脚"),
            ('SIMPLE', "シンプル (Simple)", "プレーンな4本脚")
        ],
        default='STEEL_LOOP'
    )
    rand_furniture_style: bpy.props.BoolProperty(name="🎲 家具スタイルガチャ", default=True)

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
            ('JAGGED_CRAG', "🏔️ Jagged Crag (ごつごつ鋭岩)", "多面体スライスカットによる荒々しい鋭利な岩"),
            ('COLUMNAR_CLIFF', "🧱 Columnar Cliff (柱状断崖岩)", "水平・垂直の鋭角テラス段差を持つ巨岩"),
            ('VOLCANIC_SPIKE', "🌋 Volcanic Spike (溶岩・尖角岩)", "上に向かって尖るスパイク状の鋭利な岩"),
            ('FRACTURED', "🪨 Fractured (大破砕・巨岩)", "Heavily fractured rock with large broken chunks"),
            ('SHARP', "🔪 Sharp Slate (鋭利な割れ石)", "Chiseled slate rock"),
            ('BOULDER', "🥔 Boulder (丸岩・巨石)", "Weathered rounded massive boulder")
        ],
        default='JAGGED_CRAG'
    )
    rand_type: bpy.props.BoolProperty(name="🎲 形状ランダム", default=True)

    size_x: bpy.props.FloatProperty(name="X (幅/スパン)", default=1.8, min=0.2, max=20.0)
    size_y: bpy.props.FloatProperty(name="Y (厚み/奥行)", default=1.0, min=0.1, max=20.0)
    size_z: bpy.props.FloatProperty(name="Z (高さ)", default=0.78, min=0.05, max=20.0)
    rand_dimensions: bpy.props.BoolProperty(name="🎲 サイズランダム", default=True)

    roughness: bpy.props.FloatProperty(name="Roughness (粗さ)", default=0.75, min=0.0, max=2.0)
    chisel_strength: bpy.props.FloatProperty(name="Chisel (削り角)", default=0.85, min=0.0, max=1.5)
    rand_surface: bpy.props.BoolProperty(name="🎲 粗さランダム", default=True)

    big_chunk_cuts: bpy.props.IntProperty(name="Big Chunks (大きな欠け数)", default=2, min=0, max=5)
    crack_depth: bpy.props.FloatProperty(name="Crack Depth (亀裂・傷の深さ)", default=0.6, min=0.0, max=1.5)
    floor_crack_count: bpy.props.IntProperty(name="亀裂・傷の箇所数", default=6, min=0, max=20)
    rand_fractures: bpy.props.BoolProperty(name="🎲 亀裂ランダム", default=True)

    create_debris: bpy.props.BoolProperty(name="Create Debris (周囲の破片・小石)", default=False)
    debris_count: bpy.props.IntProperty(name="Shard Count", default=4, min=1, max=20)

    texture_folder: bpy.props.StringProperty(name="Texture Folder", subtype='DIR_PATH', default=r"Z:\MeshCreator\textures\Rock")
    use_folder_texture: bpy.props.BoolProperty(name="Use Folder Textures", default=True)
    rand_texture: bpy.props.BoolProperty(name="🎲 テクスチャをランダム抽選", default=True)
    selected_texture: bpy.props.EnumProperty(name="Select Texture", items=get_texture_enum_items)
    texture_tiling: bpy.props.FloatProperty(name="Tiling (リピート倍率)", default=1.0, min=0.1, max=10.0)

    detail_level: bpy.props.IntProperty(name="Quality", default=2, min=1, max=3)
    seed: bpy.props.IntProperty(name="Seed", default=42, min=0)
    auto_random: bpy.props.BoolProperty(name="Auto Random", default=True)

# =============================================================
# 11. Sidebar Panel (N-Panel)
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

        # 🌟 4. Tab 1: Shape & Dimensions & Specific Controls
        if props.studio_tab == 'SHAPE':
            # Tree Specific (リアル樹木・自然木設定)
            if props.prop_category == 'TREE':
                box_tree = layout.box()
                box_tree.label(text="Tree Settings (リアル樹木設定):", icon='OUTLINER_OB_LIGHT')
                box_tree.prop(props, "tree_species", text="樹種")
                box_tree.prop(props, "tree_material_mode", text="マテリアル方式")
                box_tree.prop(props, "tree_branch_levels", text="枝分かれ深さ")
                box_tree.prop(props, "tree_curvature", text="枝のうねり・曲がり", slider=True)
                box_tree.prop(props, "tree_has_leaves", text="🍃 葉を付ける")
                if props.tree_has_leaves:
                    box_tree.prop(props, "tree_leaf_style", text="葉のスタイル")
                    box_tree.prop(props, "tree_leaf_count", text="葉の密度")

            # Chair Specific (近代オフィスチェア ＆ アンティーク椅子)
            elif props.prop_category in ('CHAIR', 'OFFICE_CHAIR'):
                box_chair = layout.box()
                box_chair.label(text="Chair Settings (椅子設定):", icon='PASTEDOWN')
                box_chair.prop(props, "chair_type", text="タイプ")
                if props.chair_type in ('DINING_CHAIR', 'ARMCHAIR', 'ROUND_STOOL', 'SQUARE_STOOL'):
                    box_chair.prop(props, "chair_seat_style", text="座面")
                    if props.chair_type in ('DINING_CHAIR', 'ARMCHAIR'):
                        box_chair.prop(props, "chair_back_style", text="背もたれ")
                    box_chair.prop(props, "chair_leg_layout", text="脚の構造")
                    box_chair.prop(props, "table_leg_style", text="脚の装飾")
                box_chair.prop(props, "rand_furniture_style", text="🎲 スタイルランダム")

            # Table Specific (近代PCデスク ＆ アンティーク机)
            elif props.prop_category in ('TABLE', 'PC_DESK'):
                box_tab = layout.box()
                box_tab.label(text="Table / Desk Settings (机・デスク設定):", icon='WORKSPACE')
                box_tab.prop(props, "table_shape", text="天板形状")
                box_tab.prop(props, "table_leg_style", text="脚の形状・フレーム")
                box_tab.prop(props, "rand_furniture_style", text="🎲 スタイルランダム")

            # Chest Specific
            elif props.prop_category == 'CHEST':
                box_chest = layout.box()
                box_chest.label(text="Chest Settings (タンス設定):", icon='FILE_ARCHIVE')
                box_chest.prop(props, "chest_tiers", text="引き出し段数 (2~5段)")
                box_chest.prop(props, "chest_handle_style", text="取っ手金具")
                box_chest.prop(props, "rand_furniture_style", text="🎲 スタイルランダム")

            # Bed Specific
            elif props.prop_category == 'BED':
                box_bed = layout.box()
                box_bed.label(text="Bed Settings (ベッド設定):", icon='COMMUNITY')
                box_bed.prop(props, "bed_size", text="サイズ")
                box_bed.prop(props, "column_ornament_style", text="四隅ポスト装飾")
                box_bed.prop(props, "rand_furniture_style", text="🎲 スタイルランダム")

            # Bookshelf Specific
            elif props.prop_category == 'BOOKSHELF':
                box_shelf = layout.box()
                box_shelf.label(text="Bookshelf Settings (本棚設定):", icon='BOOKMARKS')
                box_shelf.prop(props, "shelf_tiers", text="棚段数 (2~4段)")
                box_shelf.prop(props, "column_ornament_style", text="側柱の装飾")
                box_shelf.prop(props, "rand_furniture_style", text="🎲 スタイルランダム")

            # Grass Specific
            elif props.prop_category == 'GRASS':
                box_gmode = layout.box()
                box_gmode.label(text="Grass Type (草原タイプ):", icon='OUTLINER_OB_CURVE')
                box_gmode.prop(props, "grass_mode", text="")
                if props.grass_mode == 'MOUND':
                    box_gmode.prop(props, "floor_shape", text="床形状")

            # Floor Specific
            elif props.prop_category == 'FLOOR':
                box_fshape = layout.box()
                box_fshape.label(text="Floor Shape (床の形状):", icon='MESH_PLANE')
                box_fshape.prop(props, "floor_shape", text="")

            # Wall Specific
            elif props.prop_category == 'WALL':
                box_wshape = layout.box()
                box_wshape.label(text="Wall Shape (壁の形状):", icon='MESH_CUBE')
                box_wshape.prop(props, "wall_shape", text="")

            # Dimensions Box
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

            # Surface / Fractures for Rock & Architecture
            if props.prop_category in ("FLOOR", "WALL"):
                box_scar = layout.box()
                row_sch = box_scar.row(align=True)
                row_sch.label(text="Organic Cracks (有機的亀裂・傷):", icon='MOD_BOOLEAN')
                row_sch.prop(props, "rand_fractures", text="🎲 ランダム")
                col_sc = box_scar.column(align=True)
                col_sc.enabled = not props.rand_fractures
                col_sc.prop(props, "floor_crack_count", text="亀裂・傷の箇所数 (1~20)")
                col_sc.prop(props, "crack_depth", text="亀裂の深さ・太さ", slider=True)
            elif props.prop_category in ("ROCK", "PILLAR", "BEAM", "BEAM_ARCH"):
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
# 12. Registration
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
