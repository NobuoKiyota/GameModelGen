import bpy
from .helpers import get_mix_input, get_mix_output

def build_procedural_rock_material(mat_name, seed=0, palette='AUTO'):
    """整然としたノードグリッド配置 ＋ 重厚なアースカラー ＋ 高精細ノイズによるフォトリアル岩石シェーダー"""
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # パレットの決定 (AUTOの場合はseedから決定)
    available_palettes = ['MOSSY_FOREST', 'RED_SANDSTONE', 'GRANITE', 'VOLCANIC_BASALT', 'WHITE_LIMESTONE', 'SLATE_BLUE']
    selected_palette = palette
    if selected_palette == 'AUTO' or selected_palette not in available_palettes:
        selected_palette = available_palettes[seed % len(available_palettes)]
    
    # 🌟 グリッド配置基準
    # X軸: -1100 (Coord) -> -900 (Mapping) -> -650 (Noises) -> -350 (ColorRamps) -> -50 (Mix) -> 200 (Bumps) -> 550 (BSDF) -> 850 (Output)
    
    # 1. Output & Principled BSDF
    node_out = nodes.new('ShaderNodeOutputMaterial')
    node_out.location = (850, 100)
    
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.location = (550, 100)
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    
    # 2. Texture Coordinate & Mapping
    node_coord = nodes.new('ShaderNodeTexCoord')
    node_coord.location = (-1100, 100)
    
    node_map = nodes.new('ShaderNodeMapping')
    node_map.location = (-900, 100)
    node_map.inputs['Location'].default_value = (float((seed * 13) % 40), float((seed * 29) % 40), float((seed * 7) % 40))
    links.new(node_coord.outputs['Object'], node_map.inputs['Vector'])
    
    # 3. 🌟 自然な岩石の高精細ノイズ
    node_noise_base = nodes.new('ShaderNodeTexNoise')
    node_noise_base.location = (-650, 300)
    node_noise_base.inputs['Scale'].default_value = 2.8
    node_noise_base.inputs['Detail'].default_value = 10.0
    node_noise_base.inputs['Roughness'].default_value = 0.65
    node_noise_base.inputs['Distortion'].default_value = 0.5
    links.new(node_map.outputs['Vector'], node_noise_base.inputs['Vector'])
    
    # 微細な鉱物グレイン用 Voronoi
    node_vor_fleck = nodes.new('ShaderNodeTexVoronoi')
    node_vor_fleck.location = (-650, 0)
    node_vor_fleck.inputs['Scale'].default_value = 28.0
    links.new(node_map.outputs['Vector'], node_vor_fleck.inputs['Vector'])
    
    # 4. 🌟 重厚で落ち着いたリアル・アースカラーパレット
    node_ramp_base = nodes.new('ShaderNodeValToRGB')
    node_ramp_base.location = (-350, 300)
    
    if selected_palette == 'RED_SANDSTONE':
        # 🏜️ リアル赤砂岩: ビビッドすぎない自然な赤褐色・テラコッタ・サンドアース
        node_ramp_base.color_ramp.elements[0].position = 0.2
        node_ramp_base.color_ramp.elements[0].color = (0.28, 0.12, 0.08, 1.0)
        mid1 = node_ramp_base.color_ramp.elements.new(0.52)
        mid1.color = (0.46, 0.22, 0.14, 1.0)
        node_ramp_base.color_ramp.elements[2].position = 0.85
        node_ramp_base.color_ramp.elements[2].color = (0.58, 0.40, 0.28, 1.0)
    elif selected_palette == 'GRANITE':
        # 🪨 花崗岩: 落ち着いたチャコール・石英グレー・微小ピンク鉱物
        node_ramp_base.color_ramp.elements[0].position = 0.25
        node_ramp_base.color_ramp.elements[0].color = (0.12, 0.12, 0.12, 1.0)
        mid1 = node_ramp_base.color_ramp.elements.new(0.55)
        mid1.color = (0.35, 0.33, 0.32, 1.0)
        node_ramp_base.color_ramp.elements[2].position = 0.85
        node_ramp_base.color_ramp.elements[2].color = (0.52, 0.50, 0.48, 1.0)
    elif selected_palette == 'VOLCANIC_BASALT':
        # 🌋 溶岩玄武岩: 漆黒のチャコール・ダークアッシュ
        node_ramp_base.color_ramp.elements[0].position = 0.25
        node_ramp_base.color_ramp.elements[0].color = (0.05, 0.05, 0.06, 1.0)
        mid1 = node_ramp_base.color_ramp.elements.new(0.65)
        mid1.color = (0.14, 0.14, 0.16, 1.0)
        node_ramp_base.color_ramp.elements[2].position = 0.90
        node_ramp_base.color_ramp.elements[2].color = (0.24, 0.24, 0.26, 1.0)
    elif selected_palette == 'WHITE_LIMESTONE':
        # 🏔️ 白石灰岩: 白飛びしない落ち着いたクリームグレー・サンドベージュ
        node_ramp_base.color_ramp.elements[0].position = 0.2
        node_ramp_base.color_ramp.elements[0].color = (0.28, 0.27, 0.25, 1.0)
        mid1 = node_ramp_base.color_ramp.elements.new(0.6)
        mid1.color = (0.50, 0.48, 0.44, 1.0)
        node_ramp_base.color_ramp.elements[2].position = 0.88
        node_ramp_base.color_ramp.elements[2].color = (0.68, 0.66, 0.62, 1.0)
    elif selected_palette == 'SLATE_BLUE':
        # 💎 青粘板岩: 落ち着いたスレートブルーグレー・暗灰
        node_ramp_base.color_ramp.elements[0].position = 0.2
        node_ramp_base.color_ramp.elements[0].color = (0.10, 0.13, 0.16, 1.0)
        mid1 = node_ramp_base.color_ramp.elements.new(0.55)
        mid1.color = (0.22, 0.26, 0.30, 1.0)
        node_ramp_base.color_ramp.elements[2].position = 0.85
        node_ramp_base.color_ramp.elements[2].color = (0.42, 0.48, 0.52, 1.0)
    else: # MOSSY_FOREST / デフォルト
        # 🌿 森林岩: 湿った自然なチャコールグレー・暗褐色
        node_ramp_base.color_ramp.elements[0].position = 0.2
        node_ramp_base.color_ramp.elements[0].color = (0.12, 0.12, 0.11, 1.0)
        mid1 = node_ramp_base.color_ramp.elements.new(0.58)
        mid1.color = (0.24, 0.24, 0.22, 1.0)
        node_ramp_base.color_ramp.elements[2].position = 0.85
        node_ramp_base.color_ramp.elements[2].color = (0.38, 0.37, 0.35, 1.0)
        
    links.new(node_noise_base.outputs['Fac'], node_ramp_base.inputs['Fac'])
    
    # 5. 🌟 鉱物斑点ブレンド (Overlay)
    node_mix_fleck = nodes.new('ShaderNodeMix')
    node_mix_fleck.location = (-100, 300)
    node_mix_fleck.data_type = 'RGBA'
    node_mix_fleck.blend_type = 'OVERLAY'
    if 'Factor' in node_mix_fleck.inputs:
        node_mix_fleck.inputs['Factor'].default_value = 0.25 if selected_palette == 'GRANITE' else 0.12
    links.new(node_ramp_base.outputs['Color'], get_mix_input(node_mix_fleck, ['A', 'Color1', 'Color', 'Color_A']))
    links.new(node_vor_fleck.outputs['Color'], get_mix_input(node_mix_fleck, ['B', 'Color2', 'Color', 'Color_B']))
    
    # 6. 🌟 上面限定・苔（Moss）自動生成レイヤー
    if selected_palette == 'MOSSY_FOREST':
        node_geom = nodes.new('ShaderNodeNewGeometry')
        node_geom.location = (-650, -350)
        
        node_sep_norm = nodes.new('ShaderNodeSeparateXYZ')
        node_sep_norm.location = (-450, -350)
        links.new(node_geom.outputs['Normal'], node_sep_norm.inputs['Vector'])
        
        node_ramp_top = nodes.new('ShaderNodeValToRGB')
        node_ramp_top.location = (-250, -350)
        node_ramp_top.color_ramp.elements[0].position = 0.45
        node_ramp_top.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
        node_ramp_top.color_ramp.elements[1].position = 0.85
        node_ramp_top.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
        links.new(node_sep_norm.outputs['Z'], node_ramp_top.inputs['Fac'])
        
        node_moss_noise = nodes.new('ShaderNodeTexNoise')
        node_moss_noise.location = (-450, -600)
        node_moss_noise.inputs['Scale'].default_value = 12.0
        node_moss_noise.inputs['Detail'].default_value = 4.0
        links.new(node_map.outputs['Vector'], node_moss_noise.inputs['Vector'])
        
        # 苔カラー（彩度を落としたリアルな自然の苔色）
        node_ramp_moss_col = nodes.new('ShaderNodeValToRGB')
        node_ramp_moss_col.location = (-200, -600)
        node_ramp_moss_col.color_ramp.elements[0].color = (0.05, 0.14, 0.04, 1.0)
        node_ramp_moss_col.color_ramp.elements[1].color = (0.18, 0.28, 0.08, 1.0)
        links.new(node_moss_noise.outputs['Fac'], node_ramp_moss_col.inputs['Fac'])
        
        # 苔と岩肌の合成
        node_mix_final_col = nodes.new('ShaderNodeMix')
        node_mix_final_col.location = (200, 300)
        node_mix_final_col.data_type = 'RGBA'
        links.new(node_ramp_top.outputs['Color'], get_mix_input(node_mix_final_col, ['Factor', 'Fac']))
        links.new(get_mix_output(node_mix_fleck), get_mix_input(node_mix_final_col, ['A', 'Color1', 'Color', 'Color_A']))
        links.new(node_ramp_moss_col.outputs['Color'], get_mix_input(node_mix_final_col, ['B', 'Color2', 'Color', 'Color_B']))
        
        links.new(get_mix_output(node_mix_final_col), node_bsdf.inputs['Base Color'])
    else:
        links.new(get_mix_output(node_mix_fleck), node_bsdf.inputs['Base Color'])
    
    # 7. 🌟 不均一Roughness（完全なマット質感とわずかな湿り気）
    node_noise_rough = nodes.new('ShaderNodeTexNoise')
    node_noise_rough.location = (-350, -50)
    node_noise_rough.inputs['Scale'].default_value = 8.0
    links.new(node_map.outputs['Vector'], node_noise_rough.inputs['Vector'])
    
    node_ramp_rough = nodes.new('ShaderNodeValToRGB')
    node_ramp_rough.location = (-100, -50)
    node_ramp_rough.color_ramp.elements[0].color = (0.80, 0.80, 0.80, 1.0)
    node_ramp_rough.color_ramp.elements[1].color = (0.98, 0.98, 0.98, 1.0)
    links.new(node_noise_rough.outputs['Fac'], node_ramp_rough.inputs['Fac'])
    links.new(node_ramp_rough.outputs['Color'], node_bsdf.inputs['Roughness'])
    
    # 8. 🌟 直列多層バンプ（大うねり ＋ 微細なざらざら）
    node_bump_large = nodes.new('ShaderNodeBump')
    node_bump_large.location = (150, -100)
    node_bump_large.inputs['Strength'].default_value = 0.25
    node_bump_large.inputs['Distance'].default_value = 0.03
    links.new(node_noise_base.outputs['Fac'], node_bump_large.inputs['Height'])
    
    node_noise_fine = nodes.new('ShaderNodeTexNoise')
    node_noise_fine.location = (-100, -300)
    node_noise_fine.inputs['Scale'].default_value = 35.0
    node_noise_fine.inputs['Detail'].default_value = 6.0
    links.new(node_map.outputs['Vector'], node_noise_fine.inputs['Vector'])
    
    node_bump_fine = nodes.new('ShaderNodeBump')
    node_bump_fine.location = (350, -100)
    node_bump_fine.inputs['Strength'].default_value = 0.12
    node_bump_fine.inputs['Distance'].default_value = 0.005
    links.new(node_bump_large.outputs['Normal'], node_bump_fine.inputs['Normal'])
    links.new(node_noise_fine.outputs['Fac'], node_bump_fine.inputs['Height'])
    
    links.new(node_bump_fine.outputs['Normal'], node_bsdf.inputs['Normal'])
    
    return mat
