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
