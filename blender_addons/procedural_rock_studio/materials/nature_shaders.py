import bpy
from .helpers import get_mix_input, get_mix_output

def create_procedural_bark_material(mat_name, seed=0, species="OAK"):
    """樹皮プロシージャルマテリアル"""
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
    node_map.inputs['Location'].default_value = (float((seed * 37) % 100), float((seed * 71) % 100), float((seed * 19) % 100))
    node_map.inputs['Scale'].default_value = (1.0, 1.0, 0.15)
    links.new(node_coord.outputs['Object'], node_map.inputs['Vector'])

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

    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-480, -150)
    node_noise.inputs['Scale'].default_value = 13.0 + float((seed % 5) * 0.5)
    node_noise.inputs['Detail'].default_value = 8.0
    node_noise.inputs['Roughness'].default_value = 0.8
    links.new(node_map.outputs['Vector'], node_noise.inputs['Vector'])

    node_mix = nodes.new(type='ShaderNodeMix')
    node_mix.data_type = 'FLOAT'
    node_mix.location = (-260, 0)
    if 'Factor' in node_mix.inputs:
        node_mix.inputs['Factor'].default_value = 0.4
    links.new(node_wave.outputs['Color'], get_mix_input(node_mix, ['A', 'Float1', 'Value', 'A_Float']))
    links.new(node_noise.outputs['Fac'], get_mix_input(node_mix, ['B', 'Float2', 'Value', 'B_Float']))

    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_ramp.location = (-50, 100)

    tone_shift = ((seed % 11) - 5) * 0.008

    if species == "BIRCH":
        node_ramp.color_ramp.elements[0].position = 0.18
        node_ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.05, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.55
        node_ramp.color_ramp.elements[1].color = (max(0.7, 0.88 + tone_shift), max(0.7, 0.88 + tone_shift), max(0.68, 0.85 + tone_shift), 1.0)
    elif species == "PINE":
        node_ramp.color_ramp.elements[0].position = 0.22
        node_ramp.color_ramp.elements[0].color = (0.12 + tone_shift, 0.06 + tone_shift, 0.03, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.75
        node_ramp.color_ramp.elements[1].color = (0.35 + tone_shift, 0.18 + tone_shift, 0.11, 1.0)
    elif species == "JAPANESE_MAPLE":
        node_ramp.color_ramp.elements[0].position = 0.25
        node_ramp.color_ramp.elements[0].color = (0.18 + tone_shift, 0.14 + tone_shift, 0.11, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.75
        node_ramp.color_ramp.elements[1].color = (0.38 + tone_shift, 0.32 + tone_shift, 0.26, 1.0)
    else: # OAK / WILLOW
        node_ramp.color_ramp.elements[0].position = 0.2
        node_ramp.color_ramp.elements[0].color = (0.10 + tone_shift, 0.07 + tone_shift, 0.04, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.8
        node_ramp.color_ramp.elements[1].color = (0.32 + tone_shift, 0.23 + tone_shift, 0.16, 1.0)

    links.new(get_mix_output(node_mix), node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.location = (120, -150)
    node_bump.inputs['Strength'].default_value = 0.75
    node_bump.inputs['Distance'].default_value = 0.06
    links.new(get_mix_output(node_mix), node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat


def create_procedural_leaf_material(mat_name, seed=0, species="OAK"):
    """葉プロシージャルマテリアル"""
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
    try:
        node_bsdf.inputs['Subsurface Weight'].default_value = 0.2
    except Exception:
        try:
            node_bsdf.inputs['Subsurface'].default_value = 0.2
        except Exception:
            pass

    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    node_objinfo = nodes.new(type='ShaderNodeObjectInfo')
    node_objinfo.location = (-750, 150)

    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-750, -100)
    node_noise.inputs['Scale'].default_value = 18.0 + float((seed % 7) * 0.8)
    node_noise.inputs['Detail'].default_value = 4.0

    node_mix = nodes.new(type='ShaderNodeMix')
    node_mix.data_type = 'FLOAT'
    node_mix.location = (-450, 50)
    if 'Factor' in node_mix.inputs:
        node_mix.inputs['Factor'].default_value = 0.45 + float((seed % 10) * 0.015)
    links.new(node_objinfo.outputs['Random'], get_mix_input(node_mix, ['A', 'Float1', 'Value', 'A_Float']))
    links.new(node_noise.outputs['Fac'], get_mix_input(node_mix, ['B', 'Float2', 'Value', 'B_Float']))

    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_ramp.location = (-200, 50)

    hue_var = ((seed % 13) - 6) * 0.01

    if species == "JAPANESE_MAPLE":
        node_ramp.color_ramp.elements[0].position = 0.1
        node_ramp.color_ramp.elements[0].color = (0.75 + hue_var, 0.06, 0.02, 1.0)
        elem_mid = node_ramp.color_ramp.elements.new(0.55)
        elem_mid.color = (0.92, 0.38 + hue_var, 0.05, 1.0)
        node_ramp.color_ramp.elements[2].position = 0.9
        node_ramp.color_ramp.elements[2].color = (0.85, 0.68 + hue_var, 0.08, 1.0)
    elif species == "PINE":
        node_ramp.color_ramp.elements[0].position = 0.15
        node_ramp.color_ramp.elements[0].color = (0.04, 0.15 + hue_var, 0.06, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.85
        node_ramp.color_ramp.elements[1].color = (0.10, 0.28 + hue_var, 0.12, 1.0)
    elif species == "BIRCH":
        node_ramp.color_ramp.elements[0].position = 0.2
        node_ramp.color_ramp.elements[0].color = (0.22, 0.52 + hue_var, 0.10, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.8
        node_ramp.color_ramp.elements[1].color = (0.42, 0.68 + hue_var, 0.14, 1.0)
    elif species == "WILLOW":
        node_ramp.color_ramp.elements[0].position = 0.2
        node_ramp.color_ramp.elements[0].color = (0.16, 0.38 + hue_var, 0.15, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.8
        node_ramp.color_ramp.elements[1].color = (0.35, 0.56 + hue_var, 0.20, 1.0)
    else: # OAK / Deciduous
        node_ramp.color_ramp.elements[0].position = 0.2
        node_ramp.color_ramp.elements[0].color = (0.12, 0.32 + hue_var, 0.06, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.8
        node_ramp.color_ramp.elements[1].color = (0.26, 0.54 + hue_var, 0.12, 1.0)

    links.new(get_mix_output(node_mix), node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.location = (120, -150)
    node_bump.inputs['Strength'].default_value = 0.25
    node_bump.inputs['Distance'].default_value = 0.02
    links.new(node_noise.outputs['Fac'], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat


def create_procedural_water_shader(mat_name, color_type='TROPICAL', wave_strength=0.12, seed=0):
    """水面プロシージャルシェーダー"""
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    try:
        mat.use_screen_refraction = True
    except Exception:
        pass

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (700, 0)

    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (380, 0)
    try:
        node_bsdf.inputs['Roughness'].default_value = 0.02
    except Exception:
        pass

    try:
        node_bsdf.inputs['IOR'].default_value = 1.333
    except Exception:
        pass

    try:
        node_bsdf.inputs['Transmission Weight'].default_value = 1.0
    except Exception:
        try:
            node_bsdf.inputs['Transmission'].default_value = 1.0
        except Exception:
            pass

    if color_type == 'DEEP_OCEAN':
        base_col = (0.015, 0.045, 0.14, 1.0)
        vol_col = (0.01, 0.08, 0.18, 1.0)
        vol_density = 1.2
    elif color_type == 'POND_GREEN':
        base_col = (0.05, 0.20, 0.12, 1.0)
        vol_col = (0.08, 0.25, 0.15, 1.0)
        vol_density = 0.85
    elif color_type == 'CRYSTAL':
        base_col = (0.85, 0.95, 1.0, 1.0)
        vol_col = (0.2, 0.6, 0.8, 1.0)
        vol_density = 0.2
    else: # TROPICAL
        base_col = (0.06, 0.62, 0.68, 1.0)
        vol_col = (0.04, 0.38, 0.45, 1.0)
        vol_density = 0.65

    node_bsdf.inputs['Base Color'].default_value = base_col
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    node_vol = nodes.new(type='ShaderNodeVolumeAbsorption')
    node_vol.location = (380, -280)
    node_vol.inputs['Color'].default_value = vol_col
    node_vol.inputs['Density'].default_value = vol_density
    links.new(node_vol.outputs['Volume'], node_out.inputs['Volume'])

    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-750, 0)
    node_map = nodes.new(type='ShaderNodeMapping')
    node_map.location = (-580, 0)
    node_map.inputs['Location'].default_value = (float((seed * 17) % 10), float((seed * 31) % 10), 0.0)
    links.new(node_coord.outputs['Object'], node_map.inputs['Vector'])

    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-380, 100)
    node_noise.inputs['Scale'].default_value = 16.0
    node_noise.inputs['Detail'].default_value = 4.0
    node_noise.inputs['Roughness'].default_value = 0.5
    links.new(node_map.outputs['Vector'], node_noise.inputs['Vector'])

    node_vor = nodes.new(type='ShaderNodeTexVoronoi')
    node_vor.location = (-380, -150)
    node_vor.inputs['Scale'].default_value = 4.0
    links.new(node_map.outputs['Vector'], node_vor.inputs['Vector'])

    node_mix = nodes.new(type='ShaderNodeMix')
    node_mix.data_type = 'FLOAT'
    node_mix.location = (-160, 0)
    if 'Factor' in node_mix.inputs:
        node_mix.inputs['Factor'].default_value = 0.35
    links.new(node_noise.outputs['Fac'], get_mix_input(node_mix, ['A', 'Float1', 'Value', 'A_Float']))
    links.new(node_vor.outputs['Distance'], get_mix_input(node_mix, ['B', 'Float2', 'Value', 'B_Float']))

    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.location = (120, -150)
    node_bump.inputs['Strength'].default_value = max(0.02, wave_strength)
    node_bump.inputs['Distance'].default_value = 0.04
    links.new(get_mix_output(node_mix), node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat


def create_procedural_water_bed_shader(mat_name, seed=0):
    """池底・川底用マテリアル"""
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Roughness'].default_value = 0.85
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.inputs['Scale'].default_value = 8.0
    links.new(node_coord.outputs['Object'], node_noise.inputs['Vector'])

    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_ramp.color_ramp.elements[0].color = (0.08, 0.06, 0.04, 1.0)
    node_ramp.color_ramp.elements[1].color = (0.28, 0.22, 0.15, 1.0)
    links.new(node_noise.outputs['Fac'], node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.inputs['Strength'].default_value = 0.4
    links.new(node_noise.outputs['Fac'], node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat
