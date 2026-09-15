import bpy
import math

CURTAIN_MATERIAL_PRESETS = {
    'SHEER_LACE': {
        'name': "透け感レース (Sheer Lace)",
        'base': (0.92, 0.93, 0.95, 1.0),
        'roughness': 0.65,
        'transmission': 0.45,
        'subsurface': 0.15,
        'sheen': 0.20
    },
    'HEAVY_VELVET': {
        'name': "重厚ベルベット (Royal Velvet)",
        'base': (0.06, 0.015, 0.025, 1.0), # Deep Royal Burgundy
        'roughness': 0.85,
        'transmission': 0.0,
        'subsurface': 0.05,
        'sheen': 0.90
    },
    'NATURAL_LINEN': {
        'name': "ナチュラルリネン (Natural Linen)",
        'base': (0.82, 0.78, 0.70, 1.0), # Warm Beige/Ecru
        'roughness': 0.75,
        'transmission': 0.05,
        'subsurface': 0.08,
        'sheen': 0.35
    },
    'SILK_SATIN': {
        'name': "シルクサテン (Silk Satin)",
        'base': (0.15, 0.25, 0.38, 1.0), # Elegant Midnight Teal
        'roughness': 0.28,
        'transmission': 0.0,
        'subsurface': 0.02,
        'sheen': 0.80
    }
}


def create_curtain_fabric_material(
    mat_name="M_Curtain_Fabric",
    fabric_type='SHEER_LACE',
    custom_color=None,
    opacity=0.85,
    seed=0
):
    """
    カーテン用布地PBRシェーダー（レースの透け感・ベルベットの光沢・リネンの織り目・サテン）
    """
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    preset = CURTAIN_MATERIAL_PRESETS.get(fabric_type, CURTAIN_MATERIAL_PRESETS['SHEER_LACE'])
    base_color = custom_color if custom_color else preset['base']

    # レースなど半透明素材の場合のブレンドモード
    if fabric_type == 'SHEER_LACE':
        mat.blend_method = 'HASHED'
        mat.shadow_method = 'HASHED'
    else:
        mat.blend_method = 'OPAQUE'
        mat.shadow_method = 'OPAQUE'

    # Output
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (800, 0)

    # Principled BSDF
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (400, 0)
    node_bsdf.inputs['Base Color'].default_value = base_color
    node_bsdf.inputs['Roughness'].default_value = preset['roughness']
    
    # Sheen (布地特有の斜め反射光)
    if 'Sheen' in node_bsdf.inputs:
        node_bsdf.inputs['Sheen'].default_value = preset['sheen']
    elif 'Sheen Weight' in node_bsdf.inputs:
        node_bsdf.inputs['Sheen Weight'].default_value = preset['sheen']

    # Subsurface Scattering / Translucency (逆光で光を通す布地の質感)
    if 'Subsurface Weight' in node_bsdf.inputs:
        node_bsdf.inputs['Subsurface Weight'].default_value = preset['subsurface']
    elif 'Subsurface' in node_bsdf.inputs:
        node_bsdf.inputs['Subsurface'].default_value = preset['subsurface']

    # Transmission (レースの透け感)
    if preset['transmission'] > 0.01:
        if 'Transmission Weight' in node_bsdf.inputs:
            node_bsdf.inputs['Transmission Weight'].default_value = preset['transmission']
        elif 'Transmission' in node_bsdf.inputs:
            node_bsdf.inputs['Transmission'].default_value = preset['transmission']
        if 'Alpha' in node_bsdf.inputs:
            node_bsdf.inputs['Alpha'].default_value = min(1.0, opacity)

    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    # 微細ファブリック・テクスチャノイズ（布の織り目）
    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-600, 0)

    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-400, 0)
    node_noise.inputs['Scale'].default_value = 250.0
    node_noise.inputs['Detail'].default_value = 4.0
    links.new(node_coord.outputs['Object'], node_noise.inputs['Vector'])

    # 微細バンプ
    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.location = (100, -200)
    node_bump.inputs['Strength'].default_value = 0.12 if fabric_type == 'NATURAL_LINEN' else 0.05
    node_bump.inputs['Distance'].default_value = 0.002
    links.new(node_noise.outputs['Fac'], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat


def create_curtain_rod_material(mat_name="M_Curtain_Rod_Hardware", style='BRASS'):
    """カーテンレール・リング金具用マテリアル（真鍮 / つや消しブラック / シルバー）"""
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

    if style == 'BRASS':
        node_bsdf.inputs['Base Color'].default_value = (0.85, 0.68, 0.28, 1.0) # Antique Brass
        node_bsdf.inputs['Metallic'].default_value = 0.90
        node_bsdf.inputs['Roughness'].default_value = 0.30
    elif style == 'MATTE_BLACK':
        node_bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.04, 1.0) # Industrial Black Iron
        node_bsdf.inputs['Metallic'].default_value = 0.70
        node_bsdf.inputs['Roughness'].default_value = 0.45
    else: # CHROME_SILVER
        node_bsdf.inputs['Base Color'].default_value = (0.80, 0.82, 0.85, 1.0)
        node_bsdf.inputs['Metallic'].default_value = 0.95
        node_bsdf.inputs['Roughness'].default_value = 0.20

    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat
