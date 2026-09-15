import bpy
import math

DICTIONARY_COLOR_PALETTES = {
    'NAVY': {
        'name': "Oxford Navy",
        'base': (0.025, 0.045, 0.095, 1.0),
        'foil': (0.85, 0.72, 0.35, 1.0), # Soft Antique Gold
        'roughness': 0.45
    },
    'BURGUNDY': {
        'name': "Royal Burgundy",
        'base': (0.090, 0.015, 0.025, 1.0),
        'foil': (0.90, 0.78, 0.40, 1.0), # Gold
        'roughness': 0.42
    },
    'FOREST': {
        'name': "Archive Forest",
        'base': (0.018, 0.055, 0.030, 1.0),
        'foil': (0.88, 0.75, 0.38, 1.0),
        'roughness': 0.46
    },
    'CHARCOAL': {
        'name': "Slate Charcoal",
        'base': (0.045, 0.048, 0.052, 1.0),
        'foil': (0.80, 0.82, 0.85, 1.0), # Silver
        'roughness': 0.50
    },
    'AMBER': {
        'name': "Vintage Leather Amber",
        'base': (0.120, 0.065, 0.030, 1.0),
        'foil': (0.88, 0.76, 0.38, 1.0),
        'roughness': 0.38
    },
    'DARK_BROWN': {
        'name': "Antique Dark Brown",
        'base': (0.055, 0.028, 0.015, 1.0),
        'foil': (0.86, 0.74, 0.36, 1.0),
        'roughness': 0.44
    },
    'RUST_RED': {
        'name': "Terracotta Rust",
        'base': (0.130, 0.040, 0.022, 1.0),
        'foil': (0.88, 0.75, 0.38, 1.0),
        'roughness': 0.42
    },
    'TEAL_BLUE': {
        'name': "Antique Teal",
        'base': (0.015, 0.065, 0.075, 1.0),
        'foil': (0.82, 0.84, 0.88, 1.0),
        'roughness': 0.45
    },
    'MUSTARD_GOLD': {
        'name': "Old Mustard Gold",
        'base': (0.145, 0.100, 0.025, 1.0),
        'foil': (0.35, 0.25, 0.12, 1.0),
        'roughness': 0.40
    },
    'PURPLE': {
        'name': "Imperial Purple",
        'base': (0.060, 0.018, 0.075, 1.0),
        'foil': (0.88, 0.78, 0.42, 1.0),
        'roughness': 0.43
    },
    'PARCHMENT': {
        'name': "Aged Parchment Ivory",
        'base': (0.280, 0.250, 0.200, 1.0),
        'foil': (0.18, 0.14, 0.10, 1.0),
        'roughness': 0.55
    },
    'EBONY': {
        'name': "Obsidian Ebony Black",
        'base': (0.018, 0.018, 0.020, 1.0),
        'foil': (0.86, 0.76, 0.38, 1.0),
        'roughness': 0.35
    }
}

COVER_PATTERN_STYLES = ['RUNES', 'LATTICE', 'BORDER', 'STRIPES', 'PLAIN']


def create_dictionary_cover_material(
    mat_name="M_Dictionary_Cover",
    color_preset='NAVY',
    has_runes=True,
    rune_intensity=0.85,
    foil_style='GOLD',
    pattern_style='RUNES',
    seed=0
):
    """
    知性的で中性的な辞書表紙＋多様な幾何学・ルーン・箔押し/型押し刻印
    - color_preset: 全12色パレット (NAVY, BURGUNDY, FOREST, CHARCOAL, AMBER, DARK_BROWN, RUST_RED, TEAL_BLUE, MUSTARD_GOLD, PURPLE, PARCHMENT, EBONY)
    - has_runes: 表紙および背表紙に装飾模様をつける
    - rune_intensity: 箔押し・刻印の鮮明度 (0.0 ~ 1.0)
    - foil_style: 'GOLD' (アンティーク金箔), 'SILVER' (銀箔), 'DEBOSS' (空押し・型押し凹み)
    - pattern_style: 'RUNES' (古代グリフ), 'LATTICE' (ダイヤ格子), 'BORDER' (額縁枠線), 'STRIPES' (縞ライン), 'PLAIN' (無地シボ革)
    """
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    palette = DICTIONARY_COLOR_PALETTES.get(color_preset, DICTIONARY_COLOR_PALETTES['NAVY'])

    # 箔（Foil）の特性設定
    if foil_style == 'GOLD':
        foil_col = (0.88, 0.74, 0.35, 1.0) # Antique Soft Gold
        foil_metallic = 0.92
        foil_roughness = 0.26
    elif foil_style == 'SILVER':
        foil_col = (0.82, 0.86, 0.90, 1.0) # Mystic Silver
        foil_metallic = 0.95
        foil_roughness = 0.22
    else: # DEBOSS (空押し・素押し)
        base = palette['base']
        foil_col = (base[0] * 0.45, base[1] * 0.45, base[2] * 0.45, 1.0)
        foil_metallic = 0.0
        foil_roughness = 0.62

    # Output
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (1200, 0)

    # Principled BSDF
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (900, 0)
    # FBXエクスポート時（プロシージャルノードが無視された場合）のフォールバック色
    node_bsdf.inputs['Base Color'].default_value = palette['base']
    node_bsdf.inputs['Roughness'].default_value = palette['roughness']
    if has_runes and foil_style in ('GOLD', 'SILVER') and pattern_style != 'PLAIN':
        node_bsdf.inputs['Metallic'].default_value = 0.35
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    # Coordinates & Mapping
    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-1300, 0)

    node_map = nodes.new(type='ShaderNodeMapping')
    node_map.location = (-1100, 0)
    node_map.inputs['Location'].default_value = (
        float((seed * 19) % 30),
        float((seed * 37) % 30),
        float((seed * 53) % 30)
    )
    links.new(node_coord.outputs['Object'], node_map.inputs['Vector'])

    # 1. Micro Fabric / Leather Grain Noise
    node_noise_fine = nodes.new(type='ShaderNodeTexNoise')
    node_noise_fine.location = (-800, 200)
    node_noise_fine.inputs['Scale'].default_value = 180.0
    node_noise_fine.inputs['Detail'].default_value = 8.0
    node_noise_fine.inputs['Roughness'].default_value = 0.65
    links.new(node_map.outputs['Vector'], node_noise_fine.inputs['Vector'])

    # 2. Subtle Macro Leather Variation
    node_noise_macro = nodes.new(type='ShaderNodeTexNoise')
    node_noise_macro.location = (-800, -100)
    node_noise_macro.inputs['Scale'].default_value = 12.0
    node_noise_macro.inputs['Detail'].default_value = 3.0
    links.new(node_map.outputs['Vector'], node_noise_macro.inputs['Vector'])

    # 3. Base Cover Leather Color Ramp
    node_ramp_base = nodes.new(type='ShaderNodeValToRGB')
    node_ramp_base.location = (-500, -100)
    base_col = palette['base']
    darker_col = (base_col[0] * 0.78, base_col[1] * 0.78, base_col[2] * 0.78, 1.0)
    lighter_col = (min(1.0, base_col[0] * 1.15), min(1.0, base_col[1] * 1.15), min(1.0, base_col[2] * 1.15), 1.0)
    node_ramp_base.color_ramp.elements[0].position = 0.3
    node_ramp_base.color_ramp.elements[0].color = darker_col
    node_ramp_base.color_ramp.elements[1].position = 0.8
    node_ramp_base.color_ramp.elements[1].color = lighter_col
    links.new(node_noise_macro.outputs['Fac'], node_ramp_base.inputs['Fac'])

    # -------------------------------------------------------------
    # 4. 表紙柄・幾何学装飾システム (Pattern Styles)
    # -------------------------------------------------------------
    is_patterned = has_runes and (rune_intensity > 0.01) and (pattern_style != 'PLAIN')

    if is_patterned:
        if pattern_style == 'LATTICE':
            # ダイヤモンド格子パターン (Diamond Lattice)
            node_voro_lat = nodes.new(type='ShaderNodeTexVoronoi')
            node_voro_lat.location = (-800, -350)
            node_voro_lat.feature = 'DISTANCE_TO_EDGE'
            node_voro_lat.inputs['Scale'].default_value = 38.0
            links.new(node_map.outputs['Vector'], node_voro_lat.inputs['Vector'])

            node_ramp_pat = nodes.new(type='ShaderNodeValToRGB')
            node_ramp_pat.location = (-500, -350)
            node_ramp_pat.color_ramp.elements[0].position = 0.04
            node_ramp_pat.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1.0)
            node_ramp_pat.color_ramp.elements[1].position = 0.08
            node_ramp_pat.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0)
            links.new(node_voro_lat.outputs['Distance'], node_ramp_pat.inputs['Fac'])
            pat_out = node_ramp_pat.outputs['Color']

        elif pattern_style == 'BORDER':
            # 額縁フレーム枠線＋中央メダリオン (Classical Frame & Medallion)
            node_rings = nodes.new(type='ShaderNodeTexWave')
            node_rings.location = (-800, -350)
            node_rings.wave_type = 'RINGS'
            node_rings.inputs['Scale'].default_value = 16.0
            links.new(node_map.outputs['Vector'], node_rings.inputs['Vector'])

            node_ramp_pat = nodes.new(type='ShaderNodeValToRGB')
            node_ramp_pat.location = (-500, -350)
            node_ramp_pat.color_ramp.elements[0].position = 0.48
            node_ramp_pat.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
            node_ramp_pat.color_ramp.elements[1].position = 0.52
            node_ramp_pat.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
            links.new(node_rings.outputs['Color'], node_ramp_pat.inputs['Fac'])
            pat_out = node_ramp_pat.outputs['Color']

        elif pattern_style == 'STRIPES':
            # エレガントな横ライン・ストライプ (Horizontal Bands)
            node_wave_s = nodes.new(type='ShaderNodeTexWave')
            node_wave_s.location = (-800, -350)
            node_wave_s.wave_type = 'BANDS'
            node_wave_s.bands_direction = 'Y'
            node_wave_s.inputs['Scale'].default_value = 45.0
            node_wave_s.inputs['Distortion'].default_value = 0.0
            links.new(node_map.outputs['Vector'], node_wave_s.inputs['Vector'])

            node_ramp_pat = nodes.new(type='ShaderNodeValToRGB')
            node_ramp_pat.location = (-500, -350)
            node_ramp_pat.color_ramp.elements[0].position = 0.46
            node_ramp_pat.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
            node_ramp_pat.color_ramp.elements[1].position = 0.54
            node_ramp_pat.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
            links.new(node_wave_s.outputs['Color'], node_ramp_pat.inputs['Fac'])
            pat_out = node_ramp_pat.outputs['Color']

        else:  # 'RUNES'
            # 古代グリフ・謎文字テキスト列 (Voronoi × Wave Bands)
            node_voro = nodes.new(type='ShaderNodeTexVoronoi')
            node_voro.location = (-800, -350)
            node_voro.feature = 'DISTANCE_TO_EDGE'
            node_voro.inputs['Scale'].default_value = 95.0
            links.new(node_map.outputs['Vector'], node_voro.inputs['Vector'])

            node_ramp_voro = nodes.new(type='ShaderNodeValToRGB')
            node_ramp_voro.location = (-500, -350)
            node_ramp_voro.color_ramp.elements[0].position = 0.035
            node_ramp_voro.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1.0)
            node_ramp_voro.color_ramp.elements[1].position = 0.075
            node_ramp_voro.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0)
            links.new(node_voro.outputs['Distance'], node_ramp_voro.inputs['Fac'])

            node_wave_y = nodes.new(type='ShaderNodeTexWave')
            node_wave_y.location = (-800, -600)
            node_wave_y.wave_type = 'BANDS'
            node_wave_y.bands_direction = 'Y'
            node_wave_y.inputs['Scale'].default_value = 120.0
            node_wave_y.inputs['Distortion'].default_value = 0.4
            links.new(node_map.outputs['Vector'], node_wave_y.inputs['Vector'])

            node_ramp_wave_y = nodes.new(type='ShaderNodeValToRGB')
            node_ramp_wave_y.location = (-500, -600)
            node_ramp_wave_y.color_ramp.elements[0].position = 0.25
            node_ramp_wave_y.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
            node_ramp_wave_y.color_ramp.elements[1].position = 0.45
            node_ramp_wave_y.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
            links.new(node_wave_y.outputs['Color'], node_ramp_wave_y.inputs['Fac'])

            node_mult_runes = nodes.new(type='ShaderNodeMath')
            node_mult_runes.location = (-250, -450)
            node_mult_runes.operation = 'MULTIPLY'
            links.new(node_ramp_voro.outputs['Color'], node_mult_runes.inputs[0])
            links.new(node_ramp_wave_y.outputs['Color'], node_mult_runes.inputs[1])
            pat_out = node_mult_runes.outputs['Value']

        # 最終箔押し強度マスク
        node_mult_int = nodes.new(type='ShaderNodeMath')
        node_mult_int.location = (200, -450)
        node_mult_int.operation = 'MULTIPLY'
        node_mult_int.inputs[1].default_value = min(1.0, max(0.0, rune_intensity))
        links.new(pat_out, node_mult_int.inputs[0])

        # Base Color Mix (地色 と 箔押し色)
        node_mix_col = nodes.new(type='ShaderNodeMix')
        node_mix_col.location = (450, -50)
        node_mix_col.data_type = 'RGBA'
        node_mix_col.blend_type = 'MIX'
        links.new(node_mult_int.outputs['Value'], node_mix_col.inputs[0])
        links.new(node_ramp_base.outputs['Color'], node_mix_col.inputs[6])
        node_mix_col.inputs[7].default_value = foil_col
        links.new(node_mix_col.outputs[2], node_bsdf.inputs['Base Color'])

        # Metallic
        node_mix_metal = nodes.new(type='ShaderNodeMath')
        node_mix_metal.location = (650, -250)
        node_mix_metal.operation = 'MULTIPLY'
        node_mix_metal.inputs[1].default_value = foil_metallic
        links.new(node_mult_int.outputs['Value'], node_mix_metal.inputs[0])
        links.new(node_mix_metal.outputs['Value'], node_bsdf.inputs['Metallic'])

        # Roughness
        node_mix_rough = nodes.new(type='ShaderNodeMath')
        node_mix_rough.location = (650, -450)
        node_mix_rough.operation = 'MULTIPLY'
        node_mix_rough.inputs[1].default_value = (foil_roughness - palette['roughness'])
        links.new(node_mult_int.outputs['Value'], node_mix_rough.inputs[0])
        
        node_add_rough = nodes.new(type='ShaderNodeMath')
        node_add_rough.location = (850, -450)
        node_add_rough.operation = 'ADD'
        node_add_rough.inputs[0].default_value = palette['roughness']
        links.new(node_mix_rough.outputs['Value'], node_add_rough.inputs[1])
        links.new(node_add_rough.outputs['Value'], node_bsdf.inputs['Roughness'])

        # 型押しデボス凹みバンプ + レザーグレインバンプ
        node_bump_deboss = nodes.new(type='ShaderNodeBump')
        node_bump_deboss.location = (450, 300)
        node_bump_deboss.inputs['Strength'].default_value = 0.35 * rune_intensity
        node_bump_deboss.inputs['Distance'].default_value = -0.003
        links.new(node_mult_int.outputs['Value'], node_bump_deboss.inputs['Height'])

        node_bump_leather = nodes.new(type='ShaderNodeBump')
        node_bump_leather.location = (680, 200)
        node_bump_leather.inputs['Strength'].default_value = 0.16
        node_bump_leather.inputs['Distance'].default_value = 0.004
        links.new(node_noise_fine.outputs['Fac'], node_bump_leather.inputs['Height'])
        links.new(node_bump_deboss.outputs['Normal'], node_bump_leather.inputs['Normal'])
        links.new(node_bump_leather.outputs['Normal'], node_bsdf.inputs['Normal'])

    else:
        # プレーン表紙（文字なし）
        links.new(node_ramp_base.outputs['Color'], node_bsdf.inputs['Base Color'])
        node_bump = nodes.new(type='ShaderNodeBump')
        node_bump.location = (650, 150)
        node_bump.inputs['Strength'].default_value = 0.18
        node_bump.inputs['Distance'].default_value = 0.005
        links.new(node_noise_fine.outputs['Fac'], node_bump.inputs['Height'])
        links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat


def create_dictionary_pages_material(mat_name="M_Dictionary_Pages", aging=0.65, seed=0):
    """
    年季を感じさせる辞書用紙ブロック断面マテリアル
    - aging: 0.0 (清潔な生成り) ~ 1.0 (重厚なアンティーク古辞書・日焼け・黄ばみ・フォクシング)
    - 水平Wave（不揃い積層スジ）
    - マクロNoise（酸化・手油・まだら黄ばみ）
    - ミクロNoise（古紙の繊維質・フォクシング斑点）
    - 二重バンプ（微細積層バンプ＋ざらつき）
    """
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    ag = max(0.0, min(1.0, aging))

    # Output
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (1100, 0)

    # Principled BSDF
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (800, 0)
    # FBXエクスポート時（プロシージャルノードが無視された場合）のフォールバック色（酸化黄ばみ古紙色）
    node_bsdf.inputs['Base Color'].default_value = (0.92, 0.86 - (ag * 0.12), 0.74 - (ag * 0.25), 1.0)
    node_bsdf.inputs['Roughness'].default_value = 0.88 + (ag * 0.08)
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    # Coordinates & Mapping
    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-1250, 0)

    node_map = nodes.new(type='ShaderNodeMapping')
    node_map.location = (-1050, 0)
    node_map.inputs['Location'].default_value = (
        float((seed * 17) % 50),
        float((seed * 31) % 50),
        float((seed * 43) % 50)
    )
    links.new(node_coord.outputs['Object'], node_map.inputs['Vector'])

    # 1. Page Lines (Wave Texture along Z with organic aging distortion)
    node_wave = nodes.new(type='ShaderNodeTexWave')
    node_wave.location = (-750, 150)
    node_wave.wave_type = 'BANDS'
    node_wave.bands_direction = 'Z'
    node_wave.inputs['Scale'].default_value = 920.0
    node_wave.inputs['Distortion'].default_value = 1.4 + (ag * 1.6)
    node_wave.inputs['Detail'].default_value = 4.0
    links.new(node_map.outputs['Vector'], node_wave.inputs['Vector'])

    # 2. Aging Mottling / Foxing (酸化・手油・経年ムラ)
    node_mottle = nodes.new(type='ShaderNodeTexNoise')
    node_mottle.location = (-750, -150)
    node_mottle.inputs['Scale'].default_value = 16.0
    node_mottle.inputs['Detail'].default_value = 6.0
    node_mottle.inputs['Roughness'].default_value = 0.65
    links.new(node_map.outputs['Vector'], node_mottle.inputs['Vector'])

    # 3. Micro Paper Grain
    node_grain = nodes.new(type='ShaderNodeTexNoise')
    node_grain.location = (-750, -400)
    node_grain.inputs['Scale'].default_value = 140.0
    node_grain.inputs['Detail'].default_value = 6.0
    links.new(node_map.outputs['Vector'], node_grain.inputs['Vector'])

    # 4. Color Ramp for Wave Lines (物理的な酸化による黄ばみ・青B成分の低下)
    node_ramp_wave = nodes.new(type='ShaderNodeValToRGB')
    node_ramp_wave.location = (-450, 150)
    c_dark_line = (
        max(0.25, 0.78 - (ag * 0.30)), # 赤褐色
        max(0.18, 0.72 - (ag * 0.36)), # 黄褐色
        max(0.08, 0.62 - (ag * 0.44)), # 青が抜けてセピアブラウンに！
        1.0
    )
    c_page_base = (
        max(0.45, 0.96 - (ag * 0.08)), # 明るいアンバー
        max(0.38, 0.94 - (ag * 0.16)), # 黄ばみ
        max(0.20, 0.88 - (ag * 0.35)), # 黄色を強調
        1.0
    )
    node_ramp_wave.color_ramp.elements[0].position = 0.18
    node_ramp_wave.color_ramp.elements[0].color = c_dark_line
    node_ramp_wave.color_ramp.elements[1].position = 0.68
    node_ramp_wave.color_ramp.elements[1].color = c_page_base
    links.new(node_wave.outputs['Color'], node_ramp_wave.inputs['Fac'])

    # 5. Color Ramp for Mottling / Stains (経年斑点・シミ)
    node_ramp_mottle = nodes.new(type='ShaderNodeValToRGB')
    node_ramp_mottle.location = (-450, -150)
    c_stain = (
        max(0.22, 0.64 - (ag * 0.20)),
        max(0.14, 0.50 - (ag * 0.22)),
        max(0.05, 0.32 - (ag * 0.20)),
        1.0
    )
    node_ramp_mottle.color_ramp.elements[0].position = 0.28
    node_ramp_mottle.color_ramp.elements[0].color = c_stain
    node_ramp_mottle.color_ramp.elements[1].position = 0.75
    node_ramp_mottle.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    links.new(node_mottle.outputs['Fac'], node_ramp_mottle.inputs['Fac'])

    # 6. Mix Shader Nodes (Blend Page Lines with Mottling Stains)
    node_mix_stain = nodes.new(type='ShaderNodeMix')
    node_mix_stain.location = (-150, 0)
    node_mix_stain.data_type = 'RGBA'
    node_mix_stain.blend_type = 'MULTIPLY'
    node_mix_stain.inputs[0].default_value = min(1.0, ag * 0.85) # Factor
    links.new(node_ramp_wave.outputs['Color'], node_mix_stain.inputs[6]) # A (RGBA)
    links.new(node_ramp_mottle.outputs['Color'], node_mix_stain.inputs[7]) # B (RGBA)
    links.new(node_mix_stain.outputs[2], node_bsdf.inputs['Base Color']) # Result (RGBA)

    # 7. Dual Bump (Wave Layer Ridges + Paper Grain Roughness)
    node_bump_grain = nodes.new(type='ShaderNodeBump')
    node_bump_grain.location = (200, -350)
    node_bump_grain.inputs['Strength'].default_value = 0.10 + (ag * 0.15)
    node_bump_grain.inputs['Distance'].default_value = 0.003
    links.new(node_grain.outputs['Fac'], node_bump_grain.inputs['Height'])

    node_bump_wave = nodes.new(type='ShaderNodeBump')
    node_bump_wave.location = (500, -180)
    node_bump_wave.inputs['Strength'].default_value = 0.22 + (ag * 0.22)
    node_bump_wave.inputs['Distance'].default_value = 0.003
    links.new(node_wave.outputs['Fac'], node_bump_wave.inputs['Height'])
    links.new(node_bump_grain.outputs['Normal'], node_bump_wave.inputs['Normal'])
    links.new(node_bump_wave.outputs['Normal'], node_bsdf.inputs['Normal'])

    return mat


def create_dictionary_ribbon_material(mat_name="M_Dictionary_Ribbon", color=(0.55, 0.04, 0.06, 1.0)):
    """サテン布製しおり紐マテリアル"""
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (600, 0)

    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (300, 0)
    node_bsdf.inputs['Base Color'].default_value = color
    node_bsdf.inputs['Roughness'].default_value = 0.35
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat
