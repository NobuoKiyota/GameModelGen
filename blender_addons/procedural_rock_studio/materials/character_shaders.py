import bpy
from .helpers import get_mix_input, get_mix_output


def set_bsdf_input_safe(bsdf_node, socket_candidates, value):
    """Blender 3.6 / 4.x 互換で Principled BSDF の入力値を安全に設定"""
    for name in socket_candidates:
        if name in bsdf_node.inputs:
            bsdf_node.inputs[name].default_value = value
            return True
    return False


def create_chibi_character_shader(mat_name, part_type="SKIN", color=(0.96, 0.82, 0.74, 1.0), roughness=0.65, seed=0):
    """
    どうぶつの森風デフォルメキャラクター向けプロシージャルマテリアル生成
    part_type:
      - 'SKIN': 肌色。アニメ・トイ調のわずかなSSSとソフトな質感
      - 'HAIR': 髪色。マットで発色の良い質感
      - 'CLOTH_TOP': トップス衣服。細やかなファブリック質感
      - 'CLOTH_BOTTOM': ボトムス衣服。
      - 'FOOTSTEP_SURFACE': 靴底。ゲームエンジン内で足音(Footstep Surface ID)として認識される最重要スロット
      - 'EYE': 瞳
      - 'EYE_HIGHLIGHT': 瞳ハイライト
      - 'FACE_FEATURE': 眉・鼻・口
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
        # 肌のトイ調・アニメ調のほんのりとしたSubsurface
        set_bsdf_input_safe(node_bsdf, ['Subsurface', 'Subsurface Weight'], 0.12)
        set_bsdf_input_safe(node_bsdf, ['Subsurface Radius'], (1.0, 0.4, 0.2))
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.6)

    elif part_type == "HAIR":
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.45)
        set_bsdf_input_safe(node_bsdf, ['Specular', 'Specular IOR Level'], 0.35)

    elif part_type in ("CLOTH_TOP", "CLOTH_BOTTOM"):
        # 微細な布地ノイズをバンプに適用
        node_texcoord = nodes.new(type='ShaderNodeTexCoord')
        node_texcoord.location = (-650, 0)

        node_noise = nodes.new(type='ShaderNodeTexNoise')
        node_noise.location = (-450, 0)
        node_noise.inputs['Scale'].default_value = 85.0
        node_noise.inputs['Detail'].default_value = 2.0
        node_noise.inputs['Roughness'].default_value = 0.5
        links.new(node_texcoord.outputs['Object'], node_noise.inputs['Vector'])

        node_bump = nodes.new(type='ShaderNodeBump')
        node_bump.location = (-150, -100)
        node_bump.inputs['Strength'].default_value = 0.05
        node_bump.inputs['Distance'].default_value = 0.02
        links.new(node_noise.outputs['Fac'], node_bump.inputs['Height'])
        links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])

    elif part_type == "FOOTSTEP_SURFACE":
        # Unity / UnrealEngine の Footstep / Physic Material 判定用スロット
        # 靴底のラバー・レザー質感
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.8)
        set_bsdf_input_safe(node_bsdf, ['Specular', 'Specular IOR Level'], 0.15)

    elif part_type == "EYE":
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.15)
        set_bsdf_input_safe(node_bsdf, ['Specular', 'Specular IOR Level'], 0.8)

    elif part_type == "EYE_HIGHLIGHT":
        set_bsdf_input_safe(node_bsdf, ['Roughness'], 0.05)
        set_bsdf_input_safe(node_bsdf, ['Specular', 'Specular IOR Level'], 1.0)
        # わずかに発光させてキラキラした瞳に
        set_bsdf_input_safe(node_bsdf, ['Emission Color'], (1.0, 1.0, 1.0, 1.0))
        set_bsdf_input_safe(node_bsdf, ['Emission Strength'], 0.3)

    return mat
