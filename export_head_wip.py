"""
チビキャラ頭部WIP書き出しスクリプト。

現時点で「動画に忠実に作り直し済み・検証済み」の頭部関連パーツ(頭・耳・眉・目・鼻・口)
だけを生成し、正面/側面下絵(SD正面下絵.PNG / SD横向き下絵.PNG)を実寸プレーンで
仮配置した状態で .blend として書き出す。

意図的に体・髪・服・靴は含めない。これらはまだ動画に忠実な作り直しをしていない
旧コードのままであり、フルキャラクター生成(create_procedural_chibi_character)を
呼ぶと、検証済みの頭部と未検証の旧コードが同じ書き出しに混在してしまうため。
頭部以外のパーツも作り直し・検証が済み次第、このスクリプトに追加していく想定。

実行方法(Blenderをインストールした環境で):
    "C:\\Program Files\\Blender Foundation\\Blender 3.6\\blender.exe" --background --python export_head_wip.py

出力先: Z:\\MeshCreator\\chibi_head_wip.blend (実行のたびに上書きされる)
"""

import bpy
import bmesh
import math
import sys
import os

ADDON_PARENT = r"Z:\MeshCreator\blender_addons"
DOCS_DIR = r"Z:\MeshCreator\docs\tutorial_transcripts"
OUTPUT_PATH = r"Z:\MeshCreator\chibi_head_wip.blend"

TOTAL_HEIGHT = 1.15
HEAD_RATIO = 2.2


def build_head_parts(context):
    """検証済みの頭部関連パーツのみを生成してマテリアルを適用し、head_centerを(0,0,0)に
    揃えて返す(参照下絵と位置合わせしやすくするため)。"""
    from procedural_rock_studio.generators.chibi_char_gen import (
        build_chibi_head_mesh, build_chibi_ears_mesh, build_chibi_eyes_mesh,
        build_chibi_eyebrows_mesh, build_chibi_nose_mesh, build_chibi_mouth_mesh,
    )
    from procedural_rock_studio.materials.character_shaders import create_chibi_character_shader

    head_height = TOTAL_HEIGHT / HEAD_RATIO
    head_center = (0, 0, 0)
    head_size = (head_height * 0.84, head_height * 0.82, head_height * 0.80)

    head = build_chibi_head_mesh(context, "Chibi_Head", head_center, head_size)
    ears = build_chibi_ears_mesh(context, "Chibi_Ears", head_center, head_size, head_obj=head)
    eyes = build_chibi_eyes_mesh(context, "Chibi_Eyes", "GIRL", "OVAL", 1.0, head_center, head_size, head_obj=head)
    eyebrows = build_chibi_eyebrows_mesh(context, "Chibi_Eyebrows", "ARCH", head_center, head_size)
    nose = build_chibi_nose_mesh(context, "Chibi_Nose", head_center, head_size)
    mouth = build_chibi_mouth_mesh(context, "Chibi_Mouth", head_center, head_size, head_obj=head)

    mats = {
        "skin": create_chibi_character_shader("Skin_Mat", "SKIN", (0.96, 0.82, 0.74, 1.0), 0.6, 0),
        "sclera": create_chibi_character_shader("Sclera_Mat", "EYE_SCLERA", (0.97, 0.97, 0.98, 1.0), 0.25, 0),
        "eye": create_chibi_character_shader("Eye_Mat", "EYE", (0.68, 0.36, 0.12, 1.0), 0.10, 0),
        "highlight": create_chibi_character_shader("Eye_Highlight_Mat", "EYE_HIGHLIGHT", (1.0, 1.0, 1.0, 1.0), 0.05, 0),
        "eyebrow": create_chibi_character_shader("Eyebrow_Mat", "EYEBROW", (0.35, 0.22, 0.14, 1.0), 0.55, 0),
        "nose": create_chibi_character_shader("Nose_Mat", "FACE_FEATURE", (0.88, 0.59, 0.50, 1.0), 0.40, 0),
        "mouth": create_chibi_character_shader("Mouth_Mat", "MOUTH", (0.85, 0.32, 0.38, 1.0), 0.35, 0),
    }

    head.data.materials.append(mats["skin"])
    ears.data.materials.append(mats["skin"])
    eyes.data.materials.append(mats["sclera"])
    eyes.data.materials.append(mats["eye"])
    eyes.data.materials.append(mats["highlight"])
    if eyebrows:
        eyebrows.data.materials.append(mats["eyebrow"])
    nose.data.materials.append(mats["nose"])
    mouth.data.materials.append(mats["mouth"])

    parts = [head, ears, eyes, eyebrows, nose, mouth]
    for part in parts:
        if part:
            for poly in part.data.polygons:
                poly.use_smooth = True

    return head, head_height


def make_reference_plane(context, name, image_path, plane_wh, offset, axis):
    """正面/側面下絵を実寸(ワールド単位)のテクスチャ付きプレーンとして配置する。
    axis='front' -> XZ平面(Y方向を向く) / axis='side' -> YZ平面(X方向を向く)
    """
    img = bpy.data.images.load(image_path)
    w, h = plane_wh

    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    if axis == 'front':
        v0 = bm.verts.new((-w / 2, offset, 0))
        v1 = bm.verts.new((w / 2, offset, 0))
        v2 = bm.verts.new((w / 2, offset, h))
        v3 = bm.verts.new((-w / 2, offset, h))
    else:
        v0 = bm.verts.new((offset, -w / 2, 0))
        v1 = bm.verts.new((offset, w / 2, 0))
        v2 = bm.verts.new((offset, w / 2, h))
        v3 = bm.verts.new((offset, -w / 2, h))

    face = bm.faces.new((v0, v1, v2, v3))
    uv_layer = bm.loops.layers.uv.new()
    for loop, uv in zip(face.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        loop[uv_layer].uv = uv
    bm.to_mesh(mesh)
    bm.free()

    mat = bpy.data.materials.new(name + "_Mat")
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    node_tex = nodes.new('ShaderNodeTexImage')
    node_tex.image = img
    node_transp = nodes.new('ShaderNodeBsdfTransparent')
    node_mix = nodes.new('ShaderNodeMixShader')
    node_emit = nodes.new('ShaderNodeEmission')
    links.new(node_tex.outputs['Color'], node_emit.inputs['Color'])
    node_mix.inputs['Fac'].default_value = 0.5
    links.new(node_transp.outputs['BSDF'], node_mix.inputs[1])
    links.new(node_emit.outputs['Emission'], node_mix.inputs[2])
    links.new(node_mix.outputs['Shader'], node_out.inputs['Surface'])
    obj.data.materials.append(mat)

    return obj


def add_reference_planes(context, head_height):
    """下絵は全身プロポーション基準の絵なので、頭部単体に合わせて縦位置を調整して
    仮配置する(あくまで大まかな位置合わせ用)。"""
    img_w, img_h = 1000, 1500
    plane_h = TOTAL_HEIGHT
    plane_w = plane_h * (img_w / img_h)
    head_center_z_in_fullbody = (TOTAL_HEIGHT - head_height) + head_height * 0.38

    front = make_reference_plane(
        context, "Ref_Front", os.path.join(DOCS_DIR, "SD正面下絵.PNG"),
        (plane_w, plane_h), 0.35, 'front'
    )
    front.location.z -= head_center_z_in_fullbody

    side = make_reference_plane(
        context, "Ref_Side", os.path.join(DOCS_DIR, "SD横向き下絵.PNG"),
        (plane_w, plane_h), 0.35, 'side'
    )
    side.location.z -= head_center_z_in_fullbody

    return front, side


def add_simple_lighting(context):
    world = bpy.data.worlds.new("W")
    context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.12, 0.14, 0.18, 1.0)
        bg.inputs['Strength'].default_value = 1.0

    key_data = bpy.data.lights.new(name="KeyLight", type='SUN')
    key_data.energy = 2.0
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    context.collection.objects.link(key_obj)
    key_obj.rotation_euler = (math.radians(55), math.radians(10), math.radians(-30))

    fill_data = bpy.data.lights.new(name="FillLight", type='SUN')
    fill_data.energy = 0.7
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    context.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(35), math.radians(-15), math.radians(140))


def main():
    if ADDON_PARENT not in sys.path:
        sys.path.insert(0, ADDON_PARENT)

    bpy.ops.wm.read_factory_settings(use_empty=True)

    from procedural_rock_studio import rock_studio_addon
    rock_studio_addon.register()

    head, head_height = build_head_parts(bpy.context)
    add_reference_planes(bpy.context, head_height)
    add_simple_lighting(bpy.context)

    bpy.context.view_layer.objects.active = head
    head.select_set(True)

    for _ in range(3):
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_PATH)
    print("Saved:", OUTPUT_PATH)


if __name__ == "__main__":
    main()
