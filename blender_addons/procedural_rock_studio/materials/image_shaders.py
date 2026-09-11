import bpy
import os
from ..utils.texture_utils import find_pbr_texture_set

def apply_image_texture_material(obj, image_path, scale=1.0, bump_strength=0.35,
                                 displacement_strength=0.15, is_transparent=False, slot_index=None):
    """PBRテクスチャセット (Color, Roughness, Normal, Disp, AO) をマテリアルとして自動構築"""
    if not os.path.exists(image_path):
        return None
    
    pbr_set = find_pbr_texture_set(image_path)
    mat_name = os.path.splitext(os.path.basename(image_path))[0] + "_PBR_Mat"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    
    mat.use_nodes = True
    try:
        mat.cycles.displacement_method = 'BOTH'
    except Exception:
        pass

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # 1. Output & Principled BSDF
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (600, 0)

    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (300, 0)
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    # 2. UV & Mapping Nodes
    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-900, 0)
    node_map = nodes.new(type='ShaderNodeMapping')
    node_map.location = (-700, 0)
    if scale != 1.0:
        node_map.inputs['Scale'].default_value = (scale, scale, scale)
    links.new(node_coord.outputs['UV'], node_map.inputs['Vector'])

    # 3. Base Color (Albedo)
    node_col = nodes.new(type='ShaderNodeTexImage')
    node_col.location = (-450, 150)
    img_col = bpy.data.images.load(image_path, check_existing=True)
    node_col.image = img_col
    links.new(node_map.outputs['Vector'], node_col.inputs['Vector'])

    if pbr_set.get('ao'):
        try:
            node_ao = nodes.new(type='ShaderNodeTexImage')
            node_ao.location = (-450, -50)
            img_ao = bpy.data.images.load(pbr_set['ao'], check_existing=True)
            img_ao.colorspace_settings.name = 'Non-Color'
            node_ao.image = img_ao
            links.new(node_map.outputs['Vector'], node_ao.inputs['Vector'])

            node_mix_ao = nodes.new(type='ShaderNodeMix')
            node_mix_ao.data_type = 'RGBA'
            node_mix_ao.blend_type = 'MULTIPLY'
            node_mix_ao.location = (-150, 150)
            if 'Factor' in node_mix_ao.inputs:
                node_mix_ao.inputs['Factor'].default_value = 0.8
            links.new(node_col.outputs['Color'], node_mix_ao.inputs[6])
            links.new(node_ao.outputs['Color'], node_mix_ao.inputs[7])
            links.new(node_mix_ao.outputs[2], node_bsdf.inputs['Base Color'])
        except Exception:
            links.new(node_col.outputs['Color'], node_bsdf.inputs['Base Color'])
    else:
        links.new(node_col.outputs['Color'], node_bsdf.inputs['Base Color'])

    # 4. Alpha Transparency
    if is_transparent:
        mat.blend_method = 'CLIP'
        mat.shadow_method = 'CLIP'
        links.new(node_col.outputs['Alpha'], node_bsdf.inputs['Alpha'])

    # 5. Roughness Map
    if pbr_set.get('roughness'):
        try:
            node_rough = nodes.new(type='ShaderNodeTexImage')
            node_rough.location = (-450, -250)
            img_rough = bpy.data.images.load(pbr_set['roughness'], check_existing=True)
            img_rough.colorspace_settings.name = 'Non-Color'
            node_rough.image = img_rough
            links.new(node_map.outputs['Vector'], node_rough.inputs['Vector'])
            links.new(node_rough.outputs['Color'], node_bsdf.inputs['Roughness'])
        except Exception:
            node_bsdf.inputs['Roughness'].default_value = 0.75
    else:
        node_bsdf.inputs['Roughness'].default_value = 0.75

    # 6. Normal Map / Bump
    if pbr_set.get('normal'):
        try:
            node_nor = nodes.new(type='ShaderNodeTexImage')
            node_nor.location = (-450, -450)
            img_nor = bpy.data.images.load(pbr_set['normal'], check_existing=True)
            img_nor.colorspace_settings.name = 'Non-Color'
            node_nor.image = img_nor
            links.new(node_map.outputs['Vector'], node_nor.inputs['Vector'])

            node_norm_map = nodes.new(type='ShaderNodeNormalMap')
            node_norm_map.location = (-150, -450)
            node_norm_map.inputs['Strength'].default_value = max(0.5, bump_strength * 2.0)
            links.new(node_nor.outputs['Color'], node_norm_map.inputs['Color'])
            links.new(node_norm_map.outputs['Normal'], node_bsdf.inputs['Normal'])
        except Exception:
            pass
    elif bump_strength > 0.01:
        node_bump = nodes.new(type='ShaderNodeBump')
        node_bump.location = (50, -250)
        node_bump.inputs['Strength'].default_value = bump_strength
        node_bump.inputs['Distance'].default_value = 0.08
        links.new(node_col.outputs['Color'], node_bump.inputs['Height'])
        links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    # 7. Shader Displacement
    disp_img_path = pbr_set.get('displacement') or image_path
    if displacement_strength > 0.001 and disp_img_path:
        try:
            node_disp_img = nodes.new(type='ShaderNodeTexImage')
            node_disp_img.location = (-150, -650)
            img_disp = bpy.data.images.load(disp_img_path, check_existing=True)
            img_disp.colorspace_settings.name = 'Non-Color'
            node_disp_img.image = img_disp
            links.new(node_map.outputs['Vector'], node_disp_img.inputs['Vector'])

            node_disp = nodes.new(type='ShaderNodeDisplacement')
            node_disp.location = (300, -300)
            node_disp.inputs['Scale'].default_value = displacement_strength
            node_disp.inputs['Midlevel'].default_value = 0.5
            links.new(node_disp_img.outputs['Color'], node_disp.inputs['Height'])
            links.new(node_disp.outputs['Displacement'], node_out.inputs['Displacement'])
        except Exception:
            pass

    # Assign to slot
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


def apply_weathered_stone_arch_material(obj, image_path, weathering=0.5, moss_amount=0.3,
                                         scale=1.0, bump_strength=0.45, slot_index=None):
    """
    PBR石壁テクスチャに、アンビエントオクルージョン黒ずみ（AO Grime）、
    雨垂れ染み（Rain Streaks）、足元の苔（Ground Moss）をプロシージャル合成する建築専用シェーダー。
    """
    if not os.path.exists(image_path):
        return None

    pbr_set = find_pbr_texture_set(image_path)
    base_stem = os.path.splitext(os.path.basename(image_path))[0]
    mat_name = f"{base_stem}_Weathered_Arch_Mat"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)

    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # 1. Output & Principled BSDF
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (850, 0)

    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (550, 0)
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    # 2. Coordinates & Mapping
    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-1200, 0)

    node_map_uv = nodes.new(type='ShaderNodeMapping')
    node_map_uv.location = (-1000, 150)
    if scale != 1.0:
        node_map_uv.inputs['Scale'].default_value = (scale, scale, scale)
    links.new(node_coord.outputs['UV'], node_map_uv.inputs['Vector'])

    # 3. Base PBR Textures
    node_col = nodes.new(type='ShaderNodeTexImage')
    node_col.location = (-750, 200)
    img_col = bpy.data.images.load(image_path, check_existing=True)
    node_col.image = img_col
    links.new(node_map_uv.outputs['Vector'], node_col.inputs['Vector'])

    # 4. Ambient Occlusion (AO Grime - 窪み・目地・くびれの黒ずみ)
    curr_color_out = node_col.outputs['Color']

    if weathering > 0.01:
        # AO Node
        node_ao = nodes.new(type='ShaderNodeAmbientOcclusion')
        node_ao.location = (-750, -100)
        node_ao.inputs['Distance'].default_value = 0.6

        # AO ColorRamp (目地コントラスト強化)
        ramp_ao = nodes.new(type='ShaderNodeValToRGB')
        ramp_ao.location = (-550, -100)
        ramp_ao.color_ramp.elements[0].position = 0.25
        ramp_ao.color_ramp.elements[1].position = 0.75
        links.new(node_ao.outputs['AO'], ramp_ao.inputs['Fac'])

        # Multiply with grime darkness
        mix_ao = nodes.new(type='ShaderNodeMix')
        mix_ao.data_type = 'RGBA'
        mix_ao.blend_type = 'MULTIPLY'
        mix_ao.location = (-350, 150)
        mix_ao.inputs['Factor'].default_value = min(0.95, weathering * 1.1)
        links.new(curr_color_out, mix_ao.inputs[6])
        links.new(ramp_ao.outputs['Color'], mix_ao.inputs[7])
        curr_color_out = mix_ao.outputs[2]

        # 5. Rain Streaks (天板からの垂直雨垂れ染み)
        node_map_rain = nodes.new(type='ShaderNodeMapping')
        node_map_rain.location = (-1000, -250)
        # 縦方向に引き伸ばす
        node_map_rain.inputs['Scale'].default_value = (2.0, 0.15, 2.0)
        links.new(node_coord.outputs['Object'], node_map_rain.inputs['Vector'])

        tex_rain = nodes.new(type='ShaderNodeTexNoise')
        tex_rain.location = (-750, -250)
        tex_rain.inputs['Scale'].default_value = 8.0
        tex_rain.inputs['Detail'].default_value = 4.0
        tex_rain.inputs['Roughness'].default_value = 0.65
        links.new(node_map_rain.outputs['Vector'], tex_rain.inputs['Vector'])

        ramp_rain = nodes.new(type='ShaderNodeValToRGB')
        ramp_rain.location = (-550, -250)
        ramp_rain.color_ramp.elements[0].position = 0.40
        ramp_rain.color_ramp.elements[1].position = 0.70
        links.new(tex_rain.outputs['Fac'], ramp_rain.inputs['Fac'])

        mix_rain = nodes.new(type='ShaderNodeMix')
        mix_rain.data_type = 'RGBA'
        mix_rain.blend_type = 'DARKEN'
        mix_rain.location = (-150, 150)
        mix_rain.inputs['Factor'].default_value = min(0.85, weathering * 0.75)
        links.new(curr_color_out, mix_rain.inputs[6])
        links.new(ramp_rain.outputs['Color'], mix_rain.inputs[7])
        curr_color_out = mix_rain.outputs[2]

    # 6. Ground Moss (足元・柱脚の自然な苔)
    if moss_amount > 0.01:
        node_sep = nodes.new(type='ShaderNodeSeparateXYZ')
        node_sep.location = (-750, -500)
        links.new(node_coord.outputs['Object'], node_sep.inputs['Vector'])

        # Height gradient for moss (Z = 0.0 ~ 1.2m)
        ramp_moss_h = nodes.new(type='ShaderNodeValToRGB')
        ramp_moss_h.location = (-550, -500)
        ramp_moss_h.color_ramp.elements[0].position = 0.05
        ramp_moss_h.color_ramp.elements[1].position = min(0.85, 0.35 + moss_amount * 0.4)
        ramp_moss_h.color_ramp.elements[0].color = (1, 1, 1, 1) # Ground = high moss
        ramp_moss_h.color_ramp.elements[1].color = (0, 0, 0, 1) # Higher up = no moss
        links.new(node_sep.outputs['Z'], ramp_moss_h.inputs['Fac'])

        # Moss patch noise
        tex_moss = nodes.new(type='ShaderNodeTexNoise')
        tex_moss.location = (-550, -650)
        tex_moss.inputs['Scale'].default_value = 14.0
        tex_moss.inputs['Detail'].default_value = 3.0
        links.new(node_coord.outputs['Object'], tex_moss.inputs['Vector'])

        # Combine height & patch noise
        mix_moss_mask = nodes.new(type='ShaderNodeMath')
        mix_moss_mask.operation = 'MULTIPLY'
        mix_moss_mask.location = (-350, -550)
        links.new(ramp_moss_h.outputs['Color'], mix_moss_mask.inputs[0])
        links.new(tex_moss.outputs['Fac'], mix_moss_mask.inputs[1])

        # ColorRamp for sharp moss clumps
        ramp_clump = nodes.new(type='ShaderNodeValToRGB')
        ramp_clump.location = (-150, -550)
        ramp_clump.color_ramp.elements[0].position = max(0.1, 0.45 - moss_amount * 0.3)
        ramp_clump.color_ramp.elements[1].position = 0.65
        links.new(mix_moss_mask.outputs['Value'], ramp_clump.inputs['Fac'])

        # Moss Color Blend
        mix_moss = nodes.new(type='ShaderNodeMix')
        mix_moss.data_type = 'RGBA'
        mix_moss.blend_type = 'MIX'
        mix_moss.location = (50, 150)
        links.new(ramp_clump.outputs['Color'], mix_moss.inputs['Factor'])
        links.new(curr_color_out, mix_moss.inputs[6])
        # 深いオリーブグリーンの苔色
        mix_moss.inputs[7].default_value = (0.13, 0.20, 0.08, 1.0)
        curr_color_out = mix_moss.outputs[2]

    links.new(curr_color_out, node_bsdf.inputs['Base Color'])

    # 7. Roughness & Normal Map
    if pbr_set.get('roughness'):
        try:
            node_r = nodes.new(type='ShaderNodeTexImage')
            node_r.location = (-450, -350)
            img_r = bpy.data.images.load(pbr_set['roughness'], check_existing=True)
            img_r.colorspace_settings.name = 'Non-Color'
            node_r.image = img_r
            links.new(node_map_uv.outputs['Vector'], node_r.inputs['Vector'])
            links.new(node_r.outputs['Color'], node_bsdf.inputs['Roughness'])
        except Exception:
            node_bsdf.inputs['Roughness'].default_value = 0.85
    else:
        node_bsdf.inputs['Roughness'].default_value = 0.85

    if pbr_set.get('normal'):
        try:
            node_nor = nodes.new(type='ShaderNodeTexImage')
            node_nor.location = (-450, -550)
            img_nor = bpy.data.images.load(pbr_set['normal'], check_existing=True)
            img_nor.colorspace_settings.name = 'Non-Color'
            node_nor.image = img_nor
            links.new(node_map_uv.outputs['Vector'], node_nor.inputs['Vector'])

            node_nmap = nodes.new(type='ShaderNodeNormalMap')
            node_nmap.location = (-150, -550)
            node_nmap.inputs['Strength'].default_value = max(0.6, bump_strength * 2.2)
            links.new(node_nor.outputs['Color'], node_nmap.inputs['Color'])
            links.new(node_nmap.outputs['Normal'], node_bsdf.inputs['Normal'])
        except Exception:
            pass

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

