import bpy
import random
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
    elif species == "PALM":
        node_ramp.color_ramp.elements[0].position = 0.2
        node_ramp.color_ramp.elements[0].color = (0.18 + tone_shift, 0.13 + tone_shift, 0.08, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.8
        node_ramp.color_ramp.elements[1].color = (0.45 + tone_shift, 0.36 + tone_shift, 0.24, 1.0)
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
        node_bsdf.inputs['Subsurface Weight'].default_value = 0.25
    except Exception:
        try:
            node_bsdf.inputs['Subsurface'].default_value = 0.25
        except Exception:
            pass

    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-750, 150)

    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-520, -100)
    node_noise.inputs['Scale'].default_value = 16.0 + float((seed % 7) * 0.8)
    node_noise.inputs['Detail'].default_value = 4.0
    links.new(node_coord.outputs['Object'], node_noise.inputs['Vector'])

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
    elif species == "PALM":
        node_ramp.color_ramp.elements[0].position = 0.15
        node_ramp.color_ramp.elements[0].color = (0.12, 0.42 + hue_var, 0.10, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.85
        node_ramp.color_ramp.elements[1].color = (0.35, 0.65 + hue_var, 0.12, 1.0)
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

    links.new(node_noise.outputs['Fac'], node_ramp.inputs['Fac'])
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

    colors = {
        'TROPICAL': (0.05, 0.65, 0.72, 1.0),
        'DEEP_OCEAN': (0.02, 0.12, 0.35, 1.0),
        'POND_GREEN': (0.10, 0.35, 0.18, 1.0),
        'CRYSTAL': (0.75, 0.90, 0.98, 1.0)
    }
    base_col = colors.get(color_type, (0.05, 0.65, 0.72, 1.0))
    node_bsdf.inputs['Base Color'].default_value = base_col
    try:
        node_bsdf.inputs['Roughness'].default_value = 0.05
        node_bsdf.inputs['IOR'].default_value = 1.333
    except Exception:
        pass

    try:
        node_bsdf.inputs['Transmission Weight'].default_value = 0.85
    except Exception:
        try:
            node_bsdf.inputs['Transmission'].default_value = 0.85
        except Exception:
            pass

    # 泡（Foam）マテリアルノード
    node_foam_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_foam_bsdf.location = (380, -250)
    node_foam_bsdf.inputs['Base Color'].default_value = (0.95, 0.98, 1.0, 1.0)
    node_foam_bsdf.inputs['Roughness'].default_value = 0.4

    node_attr = nodes.new(type='ShaderNodeAttribute')
    node_attr.location = (80, -350)
    node_attr.attribute_name = "foam"

    node_foam_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_foam_ramp.location = (250, -350)
    node_foam_ramp.color_ramp.elements[0].position = 0.2
    node_foam_ramp.color_ramp.elements[1].position = 0.7
    links.new(node_attr.outputs['Fac'], node_foam_ramp.inputs['Fac'])

    # Mix Shader (水面 BSDF と 泡 BSDF の合成)
    node_mix_shader = nodes.new(type='ShaderNodeMixShader')
    node_mix_shader.location = (600, 0)
    links.new(node_foam_ramp.outputs['Color'], node_mix_shader.inputs['Fac'])
    links.new(node_bsdf.outputs['BSDF'], node_mix_shader.inputs[1])
    links.new(node_foam_bsdf.outputs['BSDF'], node_mix_shader.inputs[2])

    # マテリアル出力への接続
    links.new(node_mix_shader.outputs['Shader'], node_out.inputs['Surface'])



    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-900, 0)
    
    node_map = nodes.new(type='ShaderNodeMapping')
    node_map.location = (-700, 0)
    node_map.inputs['Location'].default_value = (float((seed * 23) % 100), float((seed * 41) % 100), 0.0)
    links.new(node_coord.outputs['Object'], node_map.inputs['Vector'])

    node_noise_l = nodes.new(type='ShaderNodeTexNoise')
    node_noise_l.location = (-480, 100)
    node_noise_l.inputs['Scale'].default_value = 2.5
    node_noise_l.inputs['Detail'].default_value = 4.0
    node_noise_l.inputs['Roughness'].default_value = 0.5
    links.new(node_map.outputs['Vector'], node_noise_l.inputs['Vector'])

    node_noise_s = nodes.new(type='ShaderNodeTexNoise')
    node_noise_s.location = (-480, -150)
    node_noise_s.inputs['Scale'].default_value = 8.5
    node_noise_s.inputs['Detail'].default_value = 2.0
    node_noise_s.inputs['Roughness'].default_value = 0.6
    links.new(node_map.outputs['Vector'], node_noise_s.inputs['Vector'])

    node_mix = nodes.new(type='ShaderNodeMix')
    node_mix.data_type = 'FLOAT'
    node_mix.location = (-250, 0)
    if 'Factor' in node_mix.inputs:
        node_mix.inputs['Factor'].default_value = 0.35
    links.new(node_noise_l.outputs['Fac'], get_mix_input(node_mix, ['A', 'Float1', 'Value', 'A_Float']))
    links.new(node_noise_s.outputs['Fac'], get_mix_input(node_mix, ['B', 'Float2', 'Value', 'B_Float']))

    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.location = (80, -150)
    node_bump.inputs['Strength'].default_value = wave_strength
    node_bump.inputs['Distance'].default_value = 0.08
    links.new(get_mix_output(node_mix), node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat


def create_procedural_water_bed_shader(mat_name, seed=0):
    """池底泥砂利プロシージャルシェーダー"""
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
    node_bsdf.inputs['Roughness'].default_value = 0.95
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-900, 0)
    
    node_map = nodes.new(type='ShaderNodeMapping')
    node_map.location = (-700, 0)
    node_map.inputs['Scale'].default_value = (1.5, 1.5, 1.5)
    links.new(node_coord.outputs['Object'], node_map.inputs['Vector'])

    node_vor = nodes.new(type='ShaderNodeTexVoronoi')
    node_vor.location = (-480, 100)
    node_vor.inputs['Scale'].default_value = 14.0
    node_vor.distance = 'EUCLIDEAN'
    links.new(node_map.outputs['Vector'], node_vor.inputs['Vector'])

    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-480, -150)
    node_noise.inputs['Scale'].default_value = 22.0
    node_noise.inputs['Detail'].default_value = 6.0
    links.new(node_map.outputs['Vector'], node_noise.inputs['Vector'])

    node_mix = nodes.new(type='ShaderNodeMix')
    node_mix.data_type = 'FLOAT'
    node_mix.location = (-260, 0)
    if 'Factor' in node_mix.inputs:
        node_mix.inputs['Factor'].default_value = 0.5
    links.new(node_vor.outputs['Distance'], get_mix_input(node_mix, ['A', 'Float1', 'Value', 'A_Float']))
    links.new(node_noise.outputs['Fac'], get_mix_input(node_mix, ['B', 'Float2', 'Value', 'B_Float']))

    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_ramp.location = (-50, 100)
    node_ramp.color_ramp.elements[0].position = 0.15
    node_ramp.color_ramp.elements[0].color = (0.08, 0.06, 0.04, 1.0)
    node_ramp.color_ramp.elements[1].position = 0.75
    node_ramp.color_ramp.elements[1].color = (0.22, 0.18, 0.13, 1.0)

    links.new(get_mix_output(node_mix), node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

    node_bump = nodes.new(type='ShaderNodeBump')
    node_bump.location = (120, -150)
    node_bump.inputs['Strength'].default_value = 0.6
    node_bump.inputs['Distance'].default_value = 0.05
    links.new(get_mix_output(node_mix), node_bump.inputs['Height'])
    links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat


def create_procedural_grass_blade_shader(mat_name, seed=0):
    """草ブレード用プロシージャルシェーダー（Translucency・葉脈パターン追加）
    - Translucent BSDF Mix: 光透過（薄い葉に光が当たると裏から緑が透ける）
    - 葉脈パターン: UV横グラデーション＋Noise（縦縞）
    - 先端/根元 Roughness 変化: 先端 乾燥(Rough高) / 根元 湿潤(Rough低)
    """
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    hue = ((seed % 17) - 8) * 0.008

    # ── 出力 ──────────────────────────────────────────────
    node_out  = nodes.new('ShaderNodeOutputMaterial'); node_out.location  = (900, 0)

    # ── Principled BSDF ───────────────────────────────────
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled'); node_bsdf.location = (580, 50)
    node_bsdf.inputs['Roughness'].default_value = 0.55
    # Subsurface (Blender 3.x / 4.x 互換)
    try:
        node_bsdf.inputs['Subsurface Weight'].default_value = 0.25
    except Exception:
        try:
            node_bsdf.inputs['Subsurface'].default_value = 0.25
        except Exception:
            pass

    # ── Translucent BSDF ──────────────────────────────────
    node_trans = nodes.new('ShaderNodeBsdfTranslucent'); node_trans.location = (580, -200)
    node_trans.inputs['Color'].default_value = (
        0.12 + hue * 0.3, 0.70 + hue, 0.05, 1.0)

    # ── Mix Shader (Principled + Translucent) ─────────────
    node_mix_shader = nodes.new('ShaderNodeMixShader'); node_mix_shader.location = (760, 0)
    node_mix_shader.inputs['Fac'].default_value = 0.20   # 20% 透過
    links.new(node_bsdf.outputs['BSDF'],   node_mix_shader.inputs[1])
    links.new(node_trans.outputs['BSDF'],  node_mix_shader.inputs[2])
    links.new(node_mix_shader.outputs['Shader'], node_out.inputs['Surface'])

    # ── TexCoord ──────────────────────────────────────────
    node_coord = nodes.new('ShaderNodeTexCoord'); node_coord.location = (-950, 0)

    # ── UV分離（縦=先端/根元 判定に使用）────────────────────
    node_sep = nodes.new('ShaderNodeSeparateXYZ'); node_sep.location = (-700, 120)
    links.new(node_coord.outputs['UV'], node_sep.inputs['Vector'])

    # ── Noise: 草の表面揺らぎ ───────────────────────────
    node_noise = nodes.new('ShaderNodeTexNoise'); node_noise.location = (-700, -150)
    node_noise.inputs['Scale'].default_value  = 8.0
    node_noise.inputs['Detail'].default_value = 2.0
    links.new(node_coord.outputs['Object'], node_noise.inputs['Vector'])

    # ── Mix Float: UV.Y と Noise ブレンド（色グラデ制御）──
    node_mix_fac = nodes.new('ShaderNodeMix')
    node_mix_fac.data_type = 'FLOAT'
    node_mix_fac.location = (-440, 0)
    if 'Factor' in node_mix_fac.inputs:
        node_mix_fac.inputs['Factor'].default_value = 0.15
    links.new(node_sep.outputs['Y'],     get_mix_input(node_mix_fac, ['A', 'Float1', 'Value', 'A_Float']))
    links.new(node_noise.outputs['Fac'], get_mix_input(node_mix_fac, ['B', 'Float2', 'Value', 'B_Float']))

    # ── ColorRamp: 色（根元濃緑〜先端鮮緑）──────────────
    node_ramp_col = nodes.new('ShaderNodeValToRGB'); node_ramp_col.location = (-180, 120)
    node_ramp_col.color_ramp.elements[0].position = 0.05
    node_ramp_col.color_ramp.elements[0].color    = (0.02, 0.22 + hue, 0.02, 1.0)   # 根元 深いフォレストグリーン
    node_ramp_col.color_ramp.elements[1].position = 0.90
    node_ramp_col.color_ramp.elements[1].color    = (0.18, 0.75 + hue, 0.06, 1.0)   # 先端 鮮やかライムグリーン
    links.new(get_mix_output(node_mix_fac), node_ramp_col.inputs['Fac'])
    links.new(node_ramp_col.outputs['Color'], node_bsdf.inputs['Base Color'])

    # ── Roughness: 先端(高)〜根元(低) ────────────────────
    node_ramp_rough = nodes.new('ShaderNodeValToRGB'); node_ramp_rough.location = (-180, -200)
    node_ramp_rough.color_ramp.elements[0].position = 0.0
    node_ramp_rough.color_ramp.elements[0].color    = (0.25, 0.25, 0.25, 1.0)   # 根元 湿潤
    node_ramp_rough.color_ramp.elements[1].position = 1.0
    node_ramp_rough.color_ramp.elements[1].color    = (0.55, 0.55, 0.55, 1.0)   # 先端 乾燥
    links.new(node_sep.outputs['Y'], node_ramp_rough.inputs['Fac'])
    links.new(node_ramp_rough.outputs['Color'], node_bsdf.inputs['Roughness'])

    return mat



def create_procedural_ground_terrain_shader(mat_name, seed=0, terrain_type="MEADOW"):
    """草地地面 多層PBRシェーダー（動画K1MMnQjvzZ8/M_AoNzdC4gI準拠）
    - BaseColor: 土色+草色+石点在の3層ブレンド
    - Normal:    大Bump+細Bump合成（動画準拠: Bumpノード多段）
    - Roughness: 位置依存で変化（湿った低地～乾燥高地）
    """
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    rng = __import__('random').Random(seed)
    # terrain_type 別色相バリエーション
    if terrain_type == "ROCKY":
        soil_c  = (rng.uniform(0.10, 0.18), rng.uniform(0.08, 0.12), rng.uniform(0.05, 0.08), 1.0)
        grass_c = (rng.uniform(0.10, 0.18), rng.uniform(0.20, 0.30), rng.uniform(0.04, 0.08), 1.0)
        base_roughness = 0.92
    elif terrain_type == "FLAT_DIRT":
        soil_c  = (rng.uniform(0.18, 0.28), rng.uniform(0.12, 0.18), rng.uniform(0.06, 0.09), 1.0)
        grass_c = (rng.uniform(0.08, 0.14), rng.uniform(0.18, 0.25), rng.uniform(0.03, 0.06), 1.0)
        base_roughness = 0.88
    else:  # MEADOW
        hue_shift = (seed % 17 - 8) * 0.012
        soil_c  = (rng.uniform(0.12, 0.20), rng.uniform(0.09, 0.13), rng.uniform(0.04, 0.07), 1.0)
        grass_c = (rng.uniform(0.06, 0.12), rng.uniform(0.28 + hue_shift, 0.42 + hue_shift), rng.uniform(0.05, 0.10), 1.0)
        base_roughness = 0.82

    # ── ノード配置 ────────────────────────────────────────
    node_out  = nodes.new('ShaderNodeOutputMaterial');   node_out.location  = (900, 0)
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled');   node_bsdf.location = (620, 0)
    node_bsdf.inputs['Roughness'].default_value = base_roughness
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    node_coord = nodes.new('ShaderNodeTexCoord');  node_coord.location = (-1100, 0)

    # ── Noise 1: 大スケール（土/草 マクロ分布）──────────────
    n1 = nodes.new('ShaderNodeTexNoise');  n1.location = (-800, 200)
    n1.inputs['Scale'].default_value  = 1.4
    n1.inputs['Detail'].default_value = 5.0
    n1.inputs['Roughness'].default_value = 0.55
    n1.inputs['Distortion'].default_value = 0.2
    links.new(node_coord.outputs['Object'], n1.inputs['Vector'])

    # ── Noise 2: 中スケール（土肌の模様）──────────────────
    n2 = nodes.new('ShaderNodeTexNoise');  n2.location = (-800, -80)
    n2.inputs['Scale'].default_value  = 6.0
    n2.inputs['Detail'].default_value = 4.0
    n2.inputs['Roughness'].default_value = 0.5
    links.new(node_coord.outputs['Object'], n2.inputs['Vector'])

    # ── Noise 3: 微細（表面ザラつき）────────────────────
    n3 = nodes.new('ShaderNodeTexNoise');  n3.location = (-800, -360)
    n3.inputs['Scale'].default_value  = 22.0
    n3.inputs['Detail'].default_value = 3.0
    n3.inputs['Roughness'].default_value = 0.4
    links.new(node_coord.outputs['Object'], n3.inputs['Vector'])

    # ── Voronoi: 小石・砂利の点在（斑点状）─────────────────
    vorn = nodes.new('ShaderNodeTexVoronoi'); vorn.location = (-800, -620)
    vorn.inputs['Scale'].default_value = 18.0
    vorn.voronoi_dimensions = '3D'
    links.new(node_coord.outputs['Object'], vorn.inputs['Vector'])

    # ── ColorRamp: 土色────────────────────────────────
    ramp_soil = nodes.new('ShaderNodeValToRGB');  ramp_soil.location = (-520, 200)
    ramp_soil.color_ramp.elements[0].position = 0.20
    ramp_soil.color_ramp.elements[0].color = soil_c
    ramp_soil.color_ramp.elements[1].position = 0.80
    ramp_soil.color_ramp.elements[1].color = (
        soil_c[0] * 1.2, soil_c[1] * 1.15, soil_c[2] * 1.05, 1.0)
    links.new(n1.outputs['Fac'], ramp_soil.inputs['Fac'])

    # ── ColorRamp: 草色────────────────────────────────
    ramp_grass = nodes.new('ShaderNodeValToRGB'); ramp_grass.location = (-520, -80)
    ramp_grass.color_ramp.elements[0].position = 0.15
    ramp_grass.color_ramp.elements[0].color = grass_c
    ramp_grass.color_ramp.elements[1].position = 0.85
    ramp_grass.color_ramp.elements[1].color = (
        grass_c[0] * 1.25, grass_c[1] * 1.12, grass_c[2] * 0.92, 1.0)
    links.new(n2.outputs['Fac'], ramp_grass.inputs['Fac'])

    # ── ColorRamp: 小石色────────────────────────────────
    ramp_stone = nodes.new('ShaderNodeValToRGB'); ramp_stone.location = (-520, -620)
    ramp_stone.color_ramp.elements[0].position = 0.0
    ramp_stone.color_ramp.elements[0].color = (0.45, 0.42, 0.38, 1.0)
    ramp_stone.color_ramp.elements[1].position = 0.08
    ramp_stone.color_ramp.elements[1].color    = soil_c
    links.new(vorn.outputs['Distance'], ramp_stone.inputs['Fac'])

    # ── MixColor: 土+草（n1 Factor でブレンド）──────────
    mix_soil_grass = nodes.new('ShaderNodeMixRGB'); mix_soil_grass.location = (-200, 100)
    mix_soil_grass.blend_type = 'MIX'
    links.new(n1.outputs['Fac'],          mix_soil_grass.inputs[0])
    links.new(ramp_soil.outputs['Color'],  mix_soil_grass.inputs[1])
    links.new(ramp_grass.outputs['Color'], mix_soil_grass.inputs[2])

    # ── MixColor: (土+草)+小石 ────────────────────────
    mix_stone = nodes.new('ShaderNodeMixRGB'); mix_stone.location = (60, 0)
    mix_stone.blend_type = 'MIX'
    if 'Fac' in mix_stone.inputs:
        mix_stone.inputs['Fac'].default_value = 0.06
    links.new(ramp_stone.outputs['Color'],      mix_stone.inputs[0])
    links.new(mix_soil_grass.outputs['Color'],  mix_stone.inputs[1])
    links.new(ramp_stone.outputs['Color'],      mix_stone.inputs[2])
    links.new(mix_stone.outputs['Color'],       node_bsdf.inputs['Base Color'])

    # ── Roughness: 大ノイズで変化（湿-乾）────────────────
    ramp_rough = nodes.new('ShaderNodeValToRGB'); ramp_rough.location = (-520, -360)
    ramp_rough.color_ramp.elements[0].position = 0.30
    ramp_rough.color_ramp.elements[0].color = (base_roughness - 0.12,) * 3 + (1.0,)
    ramp_rough.color_ramp.elements[1].position = 0.70
    ramp_rough.color_ramp.elements[1].color = (min(1.0, base_roughness + 0.05),) * 3 + (1.0,)
    links.new(n1.outputs['Fac'], ramp_rough.inputs['Fac'])
    links.new(ramp_rough.outputs['Color'], node_bsdf.inputs['Roughness'])

    # ── Normal: 大Bump + 細Bump 合成（動画準拠多段Bump）────
    bump_large = nodes.new('ShaderNodeBump'); bump_large.location = (200, -200)
    bump_large.inputs['Strength'].default_value = 0.40
    bump_large.inputs['Distance'].default_value = 0.08
    links.new(n1.outputs['Fac'], bump_large.inputs['Height'])

    bump_small = nodes.new('ShaderNodeBump'); bump_small.location = (200, -400)
    bump_small.inputs['Strength'].default_value = 0.22
    bump_small.inputs['Distance'].default_value = 0.02
    links.new(n3.outputs['Fac'], bump_small.inputs['Height'])
    links.new(bump_large.outputs['Normal'], bump_small.inputs['Normal'])
    links.new(bump_small.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat


def create_procedural_pillar_shader(mat_name, mat_type="MARBLE", seed=0):
    """柱（Pillar）用プロシージャルシェーダー（大理石 / 古代砂岩 / 苔むした遺跡）"""
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (750, 0)

    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (450, 0)
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-950, 0)

    if mat_type == "MARBLE":
        # 大理石（高級感のある筋模様と光沢）
        node_bsdf.inputs['Roughness'].default_value = 0.22
        node_noise = nodes.new(type='ShaderNodeTexNoise')
        node_noise.location = (-650, 0)
        node_noise.inputs['Scale'].default_value = 4.5
        node_noise.inputs['Detail'].default_value = 6.0
        node_noise.inputs['Roughness'].default_value = 0.6
        node_noise.inputs['Distortion'].default_value = 0.8
        links.new(node_coord.outputs['Object'], node_noise.inputs['Vector'])

        node_ramp = nodes.new(type='ShaderNodeValToRGB')
        node_ramp.location = (-250, 100)
        node_ramp.color_ramp.elements[0].position = 0.25
        node_ramp.color_ramp.elements[0].color = (0.35, 0.38, 0.42, 1.0) # 濃い筋
        node_ramp.color_ramp.elements[1].position = 0.65
        node_ramp.color_ramp.elements[1].color = (0.92, 0.93, 0.96, 1.0) # 白大理石
        links.new(node_noise.outputs['Fac'], node_ramp.inputs['Fac'])
        links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

        node_bump = nodes.new(type='ShaderNodeBump')
        node_bump.location = (150, -150)
        node_bump.inputs['Strength'].default_value = 0.08
        node_bump.inputs['Distance'].default_value = 0.02
        links.new(node_noise.outputs['Fac'], node_bump.inputs['Height'])
        links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    elif mat_type == "MOSSY_RUINS":
        # 苔むした遺跡石材
        node_bsdf.inputs['Roughness'].default_value = 0.75
        node_noise = nodes.new(type='ShaderNodeTexNoise')
        node_noise.location = (-650, 0)
        node_noise.inputs['Scale'].default_value = 5.0
        node_noise.inputs['Detail'].default_value = 4.0
        links.new(node_coord.outputs['Object'], node_noise.inputs['Vector'])

        node_ramp = nodes.new(type='ShaderNodeValToRGB')
        node_ramp.location = (-250, 100)
        node_ramp.color_ramp.elements[0].position = 0.35
        node_ramp.color_ramp.elements[0].color = (0.28, 0.27, 0.25, 1.0) # 古代石
        node_ramp.color_ramp.elements[1].position = 0.65
        node_ramp.color_ramp.elements[1].color = (0.12, 0.35, 0.08, 1.0) # 苔グリーン
        links.new(node_noise.outputs['Fac'], node_ramp.inputs['Fac'])
        links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

        node_bump = nodes.new(type='ShaderNodeBump')
        node_bump.location = (150, -150)
        node_bump.inputs['Strength'].default_value = 0.35
        node_bump.inputs['Distance'].default_value = 0.05
        links.new(node_noise.outputs['Fac'], node_bump.inputs['Height'])
        links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    else:
        # ANCIENT_STONE（風化した古代砂岩）
        node_bsdf.inputs['Roughness'].default_value = 0.8
        node_noise = nodes.new(type='ShaderNodeTexNoise')
        node_noise.location = (-650, 0)
        node_noise.inputs['Scale'].default_value = 7.0
        node_noise.inputs['Detail'].default_value = 5.0
        links.new(node_coord.outputs['Object'], node_noise.inputs['Vector'])

        node_ramp = nodes.new(type='ShaderNodeValToRGB')
        node_ramp.location = (-250, 100)
        node_ramp.color_ramp.elements[0].position = 0.2
        node_ramp.color_ramp.elements[0].color = (0.42, 0.38, 0.32, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.8
        node_ramp.color_ramp.elements[1].color = (0.75, 0.70, 0.62, 1.0)
        links.new(node_noise.outputs['Fac'], node_ramp.inputs['Fac'])
        links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

        node_bump = nodes.new(type='ShaderNodeBump')
        node_bump.location = (150, -150)
        node_bump.inputs['Strength'].default_value = 0.25
        node_bump.inputs['Distance'].default_value = 0.04
        links.new(node_noise.outputs['Fac'], node_bump.inputs['Height'])
        links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat


def create_procedural_telescope_shader(mat_name, part_type="SILVER", seed=0):
    """天体望遠鏡用プロシージャル PBR シェーダー（サテンシルバー / マットブラック / セレストロンオレンジ / 光学ガラス）"""
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
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    if part_type == "BRASS":
        # アンティーク磨き真鍮（ゴールド PBR）
        node_bsdf.inputs['Base Color'].default_value = (0.85, 0.68, 0.28, 1.0)
        node_bsdf.inputs['Metallic'].default_value = 0.95
        node_bsdf.inputs['Roughness'].default_value = 0.18

    elif part_type == "TEAL":
        # ポップ・パステルティールブルー（Acuter風）
        node_bsdf.inputs['Base Color'].default_value = (0.20, 0.72, 0.76, 1.0)
        node_bsdf.inputs['Metallic'].default_value = 0.05
        node_bsdf.inputs['Roughness'].default_value = 0.35

    elif part_type == "EMISSION_LED":
        # スマート望遠鏡 LED発光リング（シアン/ブルー）
        node_bsdf.inputs['Base Color'].default_value = (0.0, 0.6, 1.0, 1.0)
        try:
            node_bsdf.inputs['Emission Color'].default_value = (0.0, 0.6, 1.0, 1.0)
            node_bsdf.inputs['Emission Strength'].default_value = 4.0
        except Exception:
            try:
                node_bsdf.inputs['Emission'].default_value = (0.0, 0.6, 1.0, 1.0)
            except Exception:
                pass

    elif part_type == "CARBON":
        # サテン・カーボンブラック（プロ用三脚）
        node_bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.09, 1.0)
        node_bsdf.inputs['Metallic'].default_value = 0.30
        node_bsdf.inputs['Roughness'].default_value = 0.38

    elif part_type == "WHITE":
        # 光沢ホワイト（Sky-Watcher / レトロクラシック）
        node_bsdf.inputs['Base Color'].default_value = (0.92, 0.93, 0.95, 1.0)
        node_bsdf.inputs['Metallic'].default_value = 0.10
        node_bsdf.inputs['Roughness'].default_value = 0.25

    elif part_type == "SILVER":
        # 鏡筒シルバー（サテンアルミヘアライン）
        node_bsdf.inputs['Base Color'].default_value = (0.78, 0.80, 0.83, 1.0)
        node_bsdf.inputs['Metallic'].default_value = 0.88
        node_bsdf.inputs['Roughness'].default_value = 0.22

    elif part_type == "ORANGE":
        # セレストロン・シグネチャーオレンジ
        node_bsdf.inputs['Base Color'].default_value = (0.90, 0.32, 0.0, 1.0)
        node_bsdf.inputs['Metallic'].default_value = 0.0
        node_bsdf.inputs['Roughness'].default_value = 0.30

    elif part_type == "LENS":
        # 対物・接眼光学ガラス
        node_bsdf.inputs['Base Color'].default_value = (0.83, 0.92, 0.95, 1.0)
        node_bsdf.inputs['Roughness'].default_value = 0.02
        node_bsdf.inputs['IOR'].default_value = 1.52
        try:
            node_bsdf.inputs['Transmission Weight'].default_value = 0.95
        except Exception:
            try:
                node_bsdf.inputs['Transmission'].default_value = 0.95
            except Exception:
                pass

    else:
        # マットブラック（三脚・マウント・接眼部）
        node_bsdf.inputs['Base Color'].default_value = (0.09, 0.10, 0.11, 1.0)
        node_bsdf.inputs['Metallic'].default_value = 0.20
        node_bsdf.inputs['Roughness'].default_value = 0.42

    return mat





def create_procedural_cobblestone_shader(mat_name, seed=0, tile_scale=6.0):
    """Ryan King Art氏の動画（9Tq-6HReNEk）技法に基づくプロシージャル石畳・石壁PBRシェーダー
    - Voronoi Distance to Edge: 目地の溝マスク & 法線Bump
    - Voronoi Color: 個々の石ごとのランダム色相（自然な不均一カラー）
    - High-frequency Noise: 石表面のざらつき・風化岩肌バンプ
    - 目地と石の分離 Roughness / Base Color
    """
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    rng = random.Random(seed)
    
    # ── ノード配置 ────────────────────────────────────────
    node_out  = nodes.new('ShaderNodeOutputMaterial'); node_out.location  = (1000, 0)
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled'); node_bsdf.location = (700, 0)
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    node_coord = nodes.new('ShaderNodeTexCoord'); node_coord.location = (-1200, 0)
    
    # ── Voronoi 1: 目地マスク (Distance to Edge) ──────────
    vorn_edge = nodes.new('ShaderNodeTexVoronoi'); vorn_edge.location = (-900, 200)
    vorn_edge.inputs['Scale'].default_value = tile_scale
    vorn_edge.voronoi_dimensions = '3D'
    if hasattr(vorn_edge, 'feature'):
        vorn_edge.feature = 'DISTANCE_TO_EDGE'
    links.new(node_coord.outputs['Object'], vorn_edge.inputs['Vector'])

    # ── Voronoi 2: 石ごとのランダムカラー (F1 / Color) ────
    vorn_col = nodes.new('ShaderNodeTexVoronoi'); vorn_col.location = (-900, -100)
    vorn_col.inputs['Scale'].default_value = tile_scale
    vorn_col.voronoi_dimensions = '3D'
    links.new(node_coord.outputs['Object'], vorn_col.inputs['Vector'])

    # ── Noise: 石表面の風化ザラつき ───────────────────────
    node_noise = nodes.new('ShaderNodeTexNoise'); node_noise.location = (-900, -400)
    node_noise.inputs['Scale'].default_value  = 28.0
    node_noise.inputs['Detail'].default_value = 5.0
    node_noise.inputs['Roughness'].default_value = 0.65
    links.new(node_coord.outputs['Object'], node_noise.inputs['Vector'])

    # ── ColorRamp: 目地マスクのシャープ化 ────────────────
    ramp_edge = nodes.new('ShaderNodeValToRGB'); ramp_edge.location = (-600, 200)
    ramp_edge.color_ramp.elements[0].position = 0.03
    ramp_edge.color_ramp.elements[0].color    = (0.0, 0.0, 0.0, 1.0) # 目地
    ramp_edge.color_ramp.elements[1].position = 0.12
    ramp_edge.color_ramp.elements[1].color    = (1.0, 1.0, 1.0, 1.0) # 石面
    links.new(vorn_edge.outputs['Distance'], ramp_edge.inputs['Fac'])

    # ── ColorRamp: 石ごとのランダムカラーパレット ────────
    ramp_stone = nodes.new('ShaderNodeValToRGB'); ramp_stone.location = (-600, -100)
    # 温かみのあるヨーロッパ風砂岩・石畳アースカラー
    c_dark = (rng.uniform(0.32, 0.38), rng.uniform(0.31, 0.36), rng.uniform(0.29, 0.34), 1.0)
    c_mid  = (rng.uniform(0.48, 0.55), rng.uniform(0.45, 0.52), rng.uniform(0.41, 0.47), 1.0)
    c_warm = (rng.uniform(0.58, 0.66), rng.uniform(0.54, 0.61), rng.uniform(0.48, 0.55), 1.0)
    
    ramp_stone.color_ramp.elements[0].position = 0.10
    ramp_stone.color_ramp.elements[0].color    = c_dark
    ramp_stone.color_ramp.elements[1].position = 0.90
    ramp_stone.color_ramp.elements[1].color    = c_warm
    
    el_mid = ramp_stone.color_ramp.elements.new(0.50)
    el_mid.color = c_mid
    
    col_out = vorn_col.outputs.get('Color') or vorn_col.outputs.get('Distance')
    links.new(col_out, ramp_stone.inputs['Fac'])

    # ── MixRGB 1: 石カラーにノイズザラつきを重ねる ───────
    mix_stone_noise = nodes.new('ShaderNodeMixRGB'); mix_stone_noise.location = (-300, -80)
    mix_stone_noise.blend_type = 'MULTIPLY'
    if 'Fac' in mix_stone_noise.inputs:
        mix_stone_noise.inputs['Fac'].default_value = 0.15
    links.new(ramp_stone.outputs['Color'], mix_stone_noise.inputs[1])
    links.new(node_noise.outputs['Color'], mix_stone_noise.inputs[2])

    # ── MixRGB 2: 目地（モルタル/土色）と石面の合成 ───────
    mix_mortar = nodes.new('ShaderNodeMixRGB'); mix_mortar.location = (-50, 80)
    mix_mortar.blend_type = 'MIX'
    mortar_col = (0.22, 0.20, 0.18, 1.0)
    mix_mortar.inputs[1].default_value = mortar_col
    links.new(ramp_edge.outputs['Color'], mix_mortar.inputs[0])
    links.new(mix_stone_noise.outputs['Color'], mix_mortar.inputs[2])
    links.new(mix_mortar.outputs['Color'], node_bsdf.inputs['Base Color'])

    # ── Roughness: 目地(0.92) と 石(0.72) の変化 ─────────
    ramp_rough = nodes.new('ShaderNodeValToRGB'); ramp_rough.location = (-200, -320)
    ramp_rough.color_ramp.elements[0].position = 0.05
    ramp_rough.color_ramp.elements[0].color    = (0.92, 0.92, 0.92, 1.0)
    ramp_rough.color_ramp.elements[1].position = 0.20
    ramp_rough.color_ramp.elements[1].color    = (0.72, 0.72, 0.72, 1.0)
    links.new(vorn_edge.outputs['Distance'], ramp_rough.inputs['Fac'])
    links.new(ramp_rough.outputs['Color'], node_bsdf.inputs['Roughness'])

    # ── Normal: 目地溝Bump ＋ 石表面ノイズBump の連鎖 ─────
    bump_grout = nodes.new('ShaderNodeBump'); bump_grout.location = (250, -150)
    bump_grout.inputs['Strength'].default_value = 0.28
    bump_grout.inputs['Distance'].default_value = 0.04
    links.new(vorn_edge.outputs['Distance'], bump_grout.inputs['Height'])

    bump_micro = nodes.new('ShaderNodeBump'); bump_micro.location = (450, -150)
    bump_micro.inputs['Strength'].default_value = 0.40
    bump_micro.inputs['Distance'].default_value = 0.02
    links.new(node_noise.outputs['Fac'], bump_micro.inputs['Height'])
    links.new(bump_grout.outputs['Normal'], bump_micro.inputs['Normal'])
    links.new(bump_micro.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat
