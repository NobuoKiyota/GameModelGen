import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

from ..materials.document_mat import create_document_stack_materials


def generate_document_stack(
    context,
    name="Document_Stack",
    base_width=0.21,   # A4幅 21cm
    base_length=0.297, # A4長 29.7cm
    stack_height=0.15, # 山の全高 15cm
    layer_count=26,    # 紙層数
    messiness=0.65,    # 乱雑さ・飛び出し量 (0.0 ~ 1.0)
    include_folders=True, # 色付きフォルダー・厚紙を混ぜる
    seed=0
):
    """
    リアルな書類の束・ペーパースタック（画像2枚目リファレンス再現）
    不揃いな紙、クラフト紙、黄ばみ紙、フォルダーが雑に重なり、端が飛び出し・めくれた書類の山
    """
    rng = random.Random(seed)
    layer_count = max(8, min(50, int(layer_count)))

    mesh_name = f"{name}_Mesh"
    mesh = bpy.data.meshes.new(mesh_name)
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()

    # 各層の厚み配分（全高になるようにスケーリング）
    raw_thicknesses = [rng.uniform(0.002, 0.008) for _ in range(layer_count)]
    total_raw = sum(raw_thicknesses)
    scale_factor = stack_height / max(0.01, total_raw)
    layer_thicknesses = [t * scale_factor for t in raw_thicknesses]

    current_z = 0.0

    for i in range(layer_count):
        layer_rng = random.Random(seed + (i * 97))
        th = layer_thicknesses[i]

        # フォルダー・大型用紙の判定（時々端が大きく飛び出す）
        is_folder = include_folders and (layer_rng.random() < 0.18)
        
        # 寸法（フォルダーは少し大きく、通常紙はわずかな個体差）
        if is_folder:
            w = base_width * layer_rng.uniform(1.03, 1.08)
            l = base_length * layer_rng.uniform(1.03, 1.08)
            mat_idx = 3 # M_Paper_Folder
        else:
            w = base_width * layer_rng.uniform(0.96, 1.02)
            l = base_length * layer_rng.uniform(0.96, 1.02)
            # 紙色の配分: 白(50%), クラフト(25%), 黄ばみ(25%)
            paper_choice = layer_rng.random()
            if paper_choice < 0.50:
                mat_idx = 0 # White
            elif paper_choice < 0.75:
                mat_idx = 1 # Kraft
            else:
                mat_idx = 2 # Aged

        # 乱雑な位置ズレ (XYオフセット)
        max_shift = 0.018 * messiness
        if is_folder:
            max_shift *= 1.4
        dx = layer_rng.uniform(-max_shift, max_shift)
        dy = layer_rng.uniform(-max_shift, max_shift)

        # 微小回転ズレ (Yaw: -4.5° ~ +4.5°)
        yaw = math.radians(layer_rng.uniform(-4.5, 4.5) * messiness)
        cos_y = math.cos(yaw)
        sin_y = math.sin(yaw)

        # 紙の角のめくれ・カール（角ごとに微妙にZが浮く・反る）
        curl_fl = layer_rng.uniform(-0.002, 0.004) * messiness # 前左角
        curl_fr = layer_rng.uniform(-0.002, 0.004) * messiness # 前右角
        curl_bl = layer_rng.uniform(-0.002, 0.004) * messiness # 奥左角
        curl_br = layer_rng.uniform(-0.002, 0.004) * messiness # 奥右角

        # 4隅のローカル座標
        hw, hl = w * 0.5, l * 0.5
        corners = [
            (-hw, -hl, curl_bl),
            ( hw, -hl, curl_br),
            ( hw,  hl, curl_fr),
            (-hw,  hl, curl_fl)
        ]

        # 回転・位置適用して底面と天面の頂点を生成
        bot_verts = []
        top_verts = []
        for lx, ly, cz in corners:
            rx = lx * cos_y - ly * sin_y + dx
            ry = lx * sin_y + ly * cos_y + dy
            # 底面
            vb = bm.verts.new((rx, ry, current_z + cz * 0.3))
            bot_verts.append(vb)
            # 天面
            vt = bm.verts.new((rx, ry, current_z + th + cz))
            top_verts.append(vt)

        # 直方体ポリゴン作成
        # 底面 (-Z), 天面 (+Z)
        f_bot = bm.faces.new([bot_verts[0], bot_verts[1], bot_verts[2], bot_verts[3]])
        f_top = bm.faces.new([top_verts[0], top_verts[3], top_verts[2], top_verts[1]])
        # 側面
        f_s0 = bm.faces.new([bot_verts[0], bot_verts[1], top_verts[1], top_verts[0]])
        f_s1 = bm.faces.new([bot_verts[1], bot_verts[2], top_verts[2], top_verts[1]])
        f_s2 = bm.faces.new([bot_verts[2], bot_verts[3], top_verts[3], top_verts[2]])
        f_s3 = bm.faces.new([bot_verts[3], bot_verts[0], top_verts[0], top_verts[3]])

        for f in (f_bot, f_top, f_s0, f_s1, f_s2, f_s3):
            f.material_index = mat_idx

        current_z += th + 0.0003 # 0.3mmセーフティマージン

    # BMesh を Mesh に書き出し
    bm.to_mesh(mesh)
    bm.free()

    # マテリアル割り当て
    materials = create_document_stack_materials(prefix=name)
    obj.data.materials.clear()
    for m in materials:
        obj.data.materials.append(m)

    # 接地 (Z=0) 調整
    context.view_layer.objects.active = obj
    min_z = min(v.co.z for v in mesh.vertices)
    for v in mesh.vertices:
        v.co.z -= min_z

    # スマートUV投影（PBRテクスチャベイク完全対応）
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

    return obj
