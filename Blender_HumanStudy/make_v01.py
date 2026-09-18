"""
v01: 下絵(2D)の配置のみ。キャラクターメッシュは一切含まない。

【今回のリセットの目的】
これまで「下絵から実測した」と言いながら、実際には頭部メッシュと下絵を
Blender上で直接並べて縮尺を検証したことが一度もなかった。この失敗を踏まえ、
v01では下絵の縮尺・位置だけを、頭部の実寸(head_height)を基準に検証可能な形で
配置する。頭頂・顎(首の付け根)の位置に目印の球を置き、下絵の輪郭と
一致しているかをBlender上で目視確認できるようにしてある。

計算根拠:
- 下絵の頭部領域(頭頂〜首の付け根)をピクセルで実測:
    正面下絵: 頭頂=107px, 首の付け根=825px (高さ718px)
    側面下絵: 頭頂=100px, 首の付け根=830px (高さ730px)
  (画像サイズはどちらも1000x1500px。実測方法は
   Z:\\MeshCreator\\docs\\tutorial_transcripts\\head_profile_data.json 等を参照)
- このプロジェクトの頭身設定 head_ratio=2.2, total_height=1.15 から
  head_height = total_height / head_ratio ≈ 0.5227 (Blender単位)
- 「下絵の頭部領域の高さ(px)」が「head_height(Blender単位)」に一致するよう
  各画像ごとに独立してスケールを決める(正面・側面で下絵の描き起こしが
  ピクセル単位で微妙にずれているため、それぞれ自身の実測値でスケールする)
- 頭部中心(頭頂と首の付け根の中点)がワールド原点(0,0,0)に来るように配置する
"""

import bpy
import bmesh
import math

DOCS_DIR = r"Z:\MeshCreator\docs\tutorial_transcripts"
OUTPUT_PATH = r"Z:\MeshCreator\Blender_HumanStudy\v01_reference_only.blend"

TOTAL_HEIGHT = 1.15
HEAD_RATIO = 2.2
HEAD_HEIGHT = TOTAL_HEIGHT / HEAD_RATIO  # ≈0.5227

# 実測値(ピクセル、画像サイズ1000x1500、display_row: 0=画像上端)
FRONT_HEAD_TOP_PX = 107
FRONT_HEAD_BOTTOM_PX = 825
SIDE_HEAD_TOP_PX = 100
SIDE_HEAD_BOTTOM_PX = 830
IMG_W_PX = 1000
IMG_H_PX = 1500


def make_reference_plane(context, name, image_path, head_top_px, head_bottom_px, axis):
    """下絵を「頭部領域の高さ = HEAD_HEIGHT」となるスケールで配置する。
    頭部中心(頭頂と首の付け根の中点)がワールドZ=0に来るようにする。
    """
    img = bpy.data.images.load(image_path)
    head_height_px = head_bottom_px - head_top_px
    scale = HEAD_HEIGHT / head_height_px  # 1px = scale Blender単位

    plane_h = IMG_H_PX * scale
    plane_w = IMG_W_PX * scale

    # 画像下端(row=IMG_H_PX, つまりdisplay_row=0)のワールドZを求める:
    # 頭部中心(display_row基準で (head_top_px+head_bottom_px)/2)がZ=0になるように。
    head_center_px_from_top = (head_top_px + head_bottom_px) / 2.0
    head_center_px_from_bottom = IMG_H_PX - head_center_px_from_top
    z_bottom = -head_center_px_from_bottom * scale

    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    if axis == 'front':
        v0 = bm.verts.new((-plane_w / 2, 0.35, z_bottom))
        v1 = bm.verts.new((plane_w / 2, 0.35, z_bottom))
        v2 = bm.verts.new((plane_w / 2, 0.35, z_bottom + plane_h))
        v3 = bm.verts.new((-plane_w / 2, 0.35, z_bottom + plane_h))
    else:
        v0 = bm.verts.new((0.35, -plane_w / 2, z_bottom))
        v1 = bm.verts.new((0.35, plane_w / 2, z_bottom))
        v2 = bm.verts.new((0.35, plane_w / 2, z_bottom + plane_h))
        v3 = bm.verts.new((0.35, -plane_w / 2, z_bottom + plane_h))

    face = bm.faces.new((v0, v1, v2, v3))
    uv_layer = bm.loops.layers.uv.new()
    for loop, uv in zip(face.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        loop[uv_layer].uv = uv
    bm.to_mesh(mesh)
    bm.free()

    mat = bpy.data.materials.new(name + "_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    node_out = nodes.new('ShaderNodeOutputMaterial')
    node_tex = nodes.new('ShaderNodeTexImage')
    node_tex.image = img
    node_emit = nodes.new('ShaderNodeEmission')
    links.new(node_tex.outputs['Color'], node_emit.inputs['Color'])
    links.new(node_emit.outputs['Emission'], node_out.inputs['Surface'])
    obj.data.materials.append(mat)

    print(f"{name}: scale={scale:.6f} plane_w={plane_w:.4f} plane_h={plane_h:.4f} z_bottom={z_bottom:.4f}")
    return obj


def make_marker(context, name, z, color):
    """頭頂/首の付け根の目印球。下絵の輪郭と一致しているかを目視確認するため。"""
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.012)
    for v in bm.verts:
        v.co.z += z
    bm.to_mesh(mesh)
    bm.free()
    mat = bpy.data.materials.new(name + "_Mat")
    mat.use_nodes = True
    b = mat.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs['Base Color'].default_value = color
    obj.data.materials.append(mat)
    return obj


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    context = bpy.context

    make_reference_plane(
        context, "Ref_Front", rf"{DOCS_DIR}\SD正面下絵.PNG",
        FRONT_HEAD_TOP_PX, FRONT_HEAD_BOTTOM_PX, 'front'
    )
    make_reference_plane(
        context, "Ref_Side", rf"{DOCS_DIR}\SD横向き下絵.PNG",
        SIDE_HEAD_TOP_PX, SIDE_HEAD_BOTTOM_PX, 'side'
    )

    # 頭頂(Z=+HEAD_HEIGHT/2)と首の付け根(Z=-HEAD_HEIGHT/2)に目印(赤=頭頂, 青=首の付け根)
    make_marker(context, "Marker_HeadTop", HEAD_HEIGHT / 2, (1.0, 0.1, 0.1, 1.0))
    make_marker(context, "Marker_NeckBase", -HEAD_HEIGHT / 2, (0.1, 0.3, 1.0, 1.0))
    make_marker(context, "Marker_HeadCenter", 0.0, (0.1, 1.0, 0.1, 1.0))

    print(f"HEAD_HEIGHT = {HEAD_HEIGHT:.6f}")

    world = bpy.data.worlds.new("W")
    context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.05, 0.05, 0.06, 1.0)
        bg.inputs['Strength'].default_value = 1.0

    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_PATH)
    print("Saved:", OUTPUT_PATH)


if __name__ == "__main__":
    main()
