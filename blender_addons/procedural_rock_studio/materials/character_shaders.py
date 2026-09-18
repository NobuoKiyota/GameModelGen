import bpy
from .helpers import get_mix_input, get_mix_output


def set_bsdf_input_safe(bsdf_node, socket_candidates, value):
    """Blender 3.6 / 4.x 互換で Principled BSDF の入力値を安全に設定"""
    for name in socket_candidates:
        if name in bsdf_node.inputs:
            bsdf_node.inputs[name].default_value = value
            return True
    return False


def create_chibi_character_shader(mat_name, part_type="SKIN", color=(0.96, 0.82, 0.74, 1.0), roughness=0.65, seed=0, pattern="PLAIN"):
    """
    どうぶつの森風デフォルメキャラクター向けプロシージャルマテリアル生成
    part_type:
      - 'SKIN': 肌色。アニメ・トイ調のわずかなSSSとソフトな質感
      - 'HAIR': 髪色。マットで発色の良い質感
      - 'CLOTH_TOP': トップス衣服。プロシージャル柄（ボーダー、ドット、葉っぱ）対応
      - 'CLOTH_BOTTOM': ボトムス衣服
      - 'FOOTSTEP_SURFACE': 靴底。ゲームエンジン内で足音(Footstep Surface ID)として認識されるスロット
      - 'EYE': 瞳
      - 'EYE_HIGHLIGHT': 瞳ハイライト
      - 'FACE_FEATURE': 眉・鼻・口
      - 'GLASSES': メガネフレーム
      - 'BLUSH': チークほっぺ
    """
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (450, 0)

    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (150, 0)
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    # 基本カラーと粗さの設定
    set_bsdf_input_safe(node_bsdf, ['Base Color'], color)
    set_bsdf_input_safe(node_bsdf, ['Roughness'], roughness)
    set_bsdf_input_safe(node_bsdf, ['Specular', 'Specular IOR Level'], 0.25)

    if part_type == "SKIN":
        # 肌のトイ調・アニメ調のほんのりとしたSubsurface（EEVEEでの暗転を防ぐ適正値）
        set_bsdf_input_safe(node_bsdf, ['Subsurface', 'Subsurface Weight'], 0.04)
        set_bsdf_input_safe(node_bsdf, ['Subsurface Radius'], (1.0, 0.5, 0.3))
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.45)
        set_bsdf_input_safe(node_bsdf, ['Specular', 'Specular IOR Level'], 0.35)

    elif part_type == "HAIR":
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.45)
        set_bsdf_input_safe(node_bsdf, ['Specular', 'Specular IOR Level'], 0.35)

    elif part_type in ("CLOTH_TOP", "CLOTH_BOTTOM"):
        node_texcoord = nodes.new(type='ShaderNodeTexCoord')
        node_texcoord.location = (-750, 0)

        # プロシージャル柄（Pattern）の適用
        if part_type == "CLOTH_TOP" and pattern == "STRIPED":
            # ボーダー縞模様
            node_wave = nodes.new(type='ShaderNodeTexWave')
            node_wave.location = (-500, 150)
            node_wave.wave_type = 'BANDS'
            node_wave.bands_direction = 'Z'
            node_wave.inputs['Scale'].default_value = 16.0
            node_wave.inputs['Distortion'].default_value = 0.0
            links.new(node_texcoord.outputs['Object'], node_wave.inputs['Vector'])

            # 2色カラーミックス
            node_ramp = nodes.new(type='ShaderNodeValToRGB')
            node_ramp.location = (-280, 150)
            node_ramp.color_ramp.interpolation = 'CONSTANT'
            node_ramp.color_ramp.elements[0].position = 0.5
            node_ramp.color_ramp.elements[0].color = color
            node_ramp.color_ramp.elements[1].position = 0.501
            node_ramp.color_ramp.elements[1].color = (0.95, 0.95, 0.96, 1.0) # 白ボーダー
            links.new(node_wave.outputs['Color'], node_ramp.inputs['Fac'])
            links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

        elif part_type == "CLOTH_TOP" and pattern == "POLKA_DOT":
            # 水玉ドット
            node_voro = nodes.new(type='ShaderNodeTexVoronoi')
            node_voro.location = (-500, 150)
            node_voro.feature = 'F1'
            node_voro.inputs['Scale'].default_value = 22.0
            links.new(node_texcoord.outputs['Object'], node_voro.inputs['Vector'])

            node_ramp = nodes.new(type='ShaderNodeValToRGB')
            node_ramp.location = (-280, 150)
            node_ramp.color_ramp.interpolation = 'CONSTANT'
            node_ramp.color_ramp.elements[0].position = 0.28
            node_ramp.color_ramp.elements[0].color = (0.96, 0.96, 0.98, 1.0) # 白ドット
            node_ramp.color_ramp.elements[1].position = 0.281
            node_ramp.color_ramp.elements[1].color = color
            links.new(node_voro.outputs['Distance'], node_ramp.inputs['Fac'])
            links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

        elif part_type == "CLOTH_TOP" and pattern == "ISLAND_LEAF":
            # 胸元のアイランドリーフワンポイント
            node_map = nodes.new(type='ShaderNodeMapping')
            node_map.location = (-550, 150)
            node_map.inputs['Location'].default_value = (-0.05, 0.12, -0.65)
            node_map.inputs['Scale'].default_value = (8.0, 8.0, 8.0)
            links.new(node_texcoord.outputs['Object'], node_map.inputs['Vector'])

            node_tex = nodes.new(type='ShaderNodeTexVoronoi')
            node_tex.location = (-350, 150)
            node_tex.inputs['Scale'].default_value = 5.0
            links.new(node_map.outputs['Vector'], node_tex.inputs['Vector'])

            node_ramp = nodes.new(type='ShaderNodeValToRGB')
            node_ramp.location = (-150, 150)
            node_ramp.color_ramp.interpolation = 'CONSTANT'
            node_ramp.color_ramp.elements[0].position = 0.25
            node_ramp.color_ramp.elements[0].color = (0.35, 0.85, 0.45, 1.0) # 葉っぱグリーン
            node_ramp.color_ramp.elements[1].position = 0.251
            node_ramp.color_ramp.elements[1].color = color
            links.new(node_tex.outputs['Distance'], node_ramp.inputs['Fac'])
            links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

        # 微細な布地ノイズバンプ
        node_noise = nodes.new(type='ShaderNodeTexNoise')
        node_noise.location = (-450, -150)
        node_noise.inputs['Scale'].default_value = 85.0
        node_noise.inputs['Detail'].default_value = 2.0
        node_noise.inputs['Roughness'].default_value = 0.5
        links.new(node_texcoord.outputs['Object'], node_noise.inputs['Vector'])

        node_bump = nodes.new(type='ShaderNodeBump')
        node_bump.location = (-150, -150)
        node_bump.inputs['Strength'].default_value = 0.04
        node_bump.inputs['Distance'].default_value = 0.02
        links.new(node_noise.outputs['Fac'], node_bump.inputs['Height'])
        links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    elif part_type == "FOOTSTEP_SURFACE":
        # Unity / UnrealEngine の Footstep / Physic Material 判定用スロット
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.8)
        set_bsdf_input_safe(node_bsdf, ['Specular', 'Specular IOR Level'], 0.15)

    elif part_type == "EYE_SCLERA":
        # シンプル2層構成 slot0 = 白目玉（つややかな白磁のような質感）
        set_bsdf_input_safe(node_bsdf, ['Base Color'], (0.97, 0.97, 0.98, 1.0))
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.25)
        set_bsdf_input_safe(node_bsdf, ['Specular', 'Specular IOR Level'], 0.5)

    elif part_type == "EYE":
        # slot1 = 瞳・虹彩（Pupil/Iris）: ツヤのある濃色でハイライトが自然に乗る
        set_bsdf_input_safe(node_bsdf, ['Base Color'], color)
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.12)
        set_bsdf_input_safe(node_bsdf, ['Specular', 'Specular IOR Level'], 0.8)

    elif part_type == "EYE_HIGHLIGHT":
        # slot2 = 瞳のキャッチライト（正球、瞳表面に浅く埋め込み）
        set_bsdf_input_safe(node_bsdf, ['Base Color'], (1.0, 1.0, 1.0, 1.0))
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.05)
        set_bsdf_input_safe(node_bsdf, ['Specular', 'Specular IOR Level'], 1.0)
        set_bsdf_input_safe(node_bsdf, ['Emission Strength'], 1.2)
        set_bsdf_input_safe(node_bsdf, ['Emission', 'Emission Color'], (1.0, 1.0, 1.0, 1.0))

    elif part_type == "GLASSES":
        set_bsdf_input_safe(node_bsdf, ['Base Color'], (0.15, 0.15, 0.18, 1.0))
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.25)
        set_bsdf_input_safe(node_bsdf, ['Metallic'], 0.4)

    elif part_type == "BLUSH":
        # ほんのりピンクほっぺ
        set_bsdf_input_safe(node_bsdf, ['Base Color'], (0.95, 0.45, 0.55, 1.0))
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.8)

    elif part_type == "EYEBROW":
        # まゆ毛（髪色に馴染むマットな質感）
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.55)
        set_bsdf_input_safe(node_bsdf, ['Specular', 'Specular IOR Level'], 0.30)

    elif part_type == "BUTTON":
        # 衣服の小さなボタン（光沢のあるプラスチック・金具調）
        set_bsdf_input_safe(node_bsdf, ['Base Color'], color or (0.92, 0.88, 0.82, 1.0))
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.30)
        set_bsdf_input_safe(node_bsdf, ['Specular', 'Specular IOR Level'], 0.65)

    elif part_type == "EYELASH":
        # Option B: slot3 = ハイライト（白、輝点）
        set_bsdf_input_safe(node_bsdf, ['Base Color'], (1.0, 1.0, 1.0, 1.0))
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.05)
        set_bsdf_input_safe(node_bsdf, ['Specular', 'Specular IOR Level'], 1.0)
        set_bsdf_input_safe(node_bsdf, ['Emission Color'], (1.0, 1.0, 1.0, 1.0))
        set_bsdf_input_safe(node_bsdf, ['Emission Strength'], 0.6)

    elif part_type == "MOUTH":
        # お口・リップライン（自然で愛らしいピンクトーン）
        set_bsdf_input_safe(node_bsdf, ['Base Color'], color or (0.85, 0.42, 0.45, 1.0))
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.50)
        set_bsdf_input_safe(node_bsdf, ['Specular', 'Specular IOR Level'], 0.35)

    return mat
