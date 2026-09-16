import bpy
import bmesh
import math
from mathutils import Vector, Matrix


def create_cube_bmesh(size=(1.0, 1.0, 1.0), offset=(0, 0, 0)):
    """指定サイズ・オフセットの直方体 BMesh を作成"""
    bm = bmesh.new()
    sx, sy, sz = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    ox, oy, oz = offset
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = v.co.x * size[0] + ox
        v.co.y = v.co.y * size[1] + oy
        v.co.z = v.co.z * size[2] + oz
    return bm


def build_chibi_body_mesh(context, name="Chibi_Body", gender="BOY", head_ratio=2.2, total_height=1.15):
    """
    動画核心技術: Single Vert ＋ 3段モディファイア（Mirror + Skin + Subdiv）による素体生成
    どうぶつの森風のコロンとした丸みとプロポーション
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    # 比率計算
    head_height = total_height / head_ratio
    body_total = total_height - head_height
    leg_len = body_total * 0.38
    torso_len = body_total * 0.62
    base_z = 0.05  # 靴底の少し上

    bm = bmesh.new()

    # 右半身の骨格頂点を作成（X >= 0）
    # 胴体・中心線 (X=0)
    v_crotch = bm.verts.new((0.0, 0.0, base_z + leg_len))
    v_belly = bm.verts.new((0.0, -0.015, base_z + leg_len + torso_len * 0.45))
    v_chest = bm.verts.new((0.0, 0.0, base_z + leg_len + torso_len * 0.85))
    v_neck = bm.verts.new((0.0, 0.0, base_z + leg_len + torso_len))

    # 腕
    sh_x = 0.11 if gender == "BOY" else 0.10
    v_shoulder = bm.verts.new((sh_x, 0.0, base_z + leg_len + torso_len * 0.78))
    v_elbow = bm.verts.new((sh_x + 0.07, -0.01, base_z + leg_len + torso_len * 0.42))
    # 手先（少し前に出してコロンとさせる）
    v_hand = bm.verts.new((sh_x + 0.11, 0.04, base_z + leg_len + torso_len * 0.12))

    # 脚
    hip_x = 0.075
    v_hip = bm.verts.new((hip_x, 0.0, base_z + leg_len * 0.95))
    v_knee = bm.verts.new((hip_x, 0.0, base_z + leg_len * 0.50))
    v_ankle = bm.verts.new((hip_x, 0.01, base_z + 0.06))

    # エッジ接続
    bm.edges.new((v_crotch, v_belly))
    bm.edges.new((v_belly, v_chest))
    bm.edges.new((v_chest, v_neck))

    bm.edges.new((v_chest, v_shoulder))
    bm.edges.new((v_shoulder, v_elbow))
    bm.edges.new((v_elbow, v_hand))

    bm.edges.new((v_crotch, v_hip))
    bm.edges.new((v_hip, v_knee))
    bm.edges.new((v_knee, v_ankle))

    bm.to_mesh(mesh)
    bm.free()

    # モディファイア追加（Mirror -> Skin -> Subdiv）
    mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
    mod_mirror.use_axis[0] = True
    mod_mirror.use_clip = True

    mod_skin = obj.modifiers.new(name="Skin", type='SKIN')
    # スキン頂点半径の設定（Ctrl+A 相当）
    skin_data = mesh.skin_vertices[0].data if mesh.skin_vertices else []
    if skin_data and len(skin_data) >= 10:
        # v_crotch
        skin_data[0].radius = (0.13, 0.13)
        # v_belly (お腹をふっくら)
        skin_data[1].radius = (0.145, 0.14)
        # v_chest
        skin_data[2].radius = (0.125, 0.12)
        # v_neck
        skin_data[3].radius = (0.09, 0.09)
        # v_shoulder
        skin_data[4].radius = (0.07, 0.07)
        # v_elbow
        skin_data[5].radius = (0.06, 0.06)
        # v_hand (指なしのミトン状丸い手)
        skin_data[6].radius = (0.08, 0.08)
        # v_hip
        skin_data[7].radius = (0.085, 0.085)
        # v_knee
        skin_data[8].radius = (0.075, 0.075)
        # v_ankle
        skin_data[9].radius = (0.07, 0.07)

    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 2
    mod_sub.render_levels = 2

    return obj


def build_chibi_head_mesh(context, name="Chibi_Head", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """どうぶつの森風の愛らしい横長・ふっくら頭部"""
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    sx, sy, sz = head_size[0], head_size[1], head_size[2]
    for v in bm.verts:
        # 下膨れ（頬をふっくら）の形状変形
        y_fac = 1.0 + (1.0 - v.co.z) * 0.12
        x_fac = 1.0 + (1.0 - v.co.z) * 0.16
        v.co.x *= sx * x_fac
        v.co.y *= sy * y_fac
        v.co.z *= sz
        v.co += Vector(head_center)

    bm.to_mesh(mesh)
    bm.free()

    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 2
    mod_sub.render_levels = 2

    return obj


def build_chibi_ears_mesh(context, name="Chibi_Ears", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """両耳メッシュ（Mirror）"""
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    ear_pos = Vector((head_size[0] * 0.52, -0.02, head_center[2] - 0.02))
    res = bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.065)
    for v in res['verts']:
        v.co.x *= 0.35  # 耳の厚みを薄く
        v.co.y *= 0.9
        v.co += ear_pos

    bm.to_mesh(mesh)
    bm.free()

    mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
    mod_mirror.use_axis[0] = True
    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 1

    return obj


def build_chibi_eyes_mesh(context, name="Chibi_Eyes", eye_style="OVAL", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """デフォルメされた瞳メッシュ ＋ キラキラハイライト（左右対称ミラー）"""
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    eye_x = head_size[0] * 0.26
    eye_y = -head_size[1] * 0.515
    eye_z = head_center[2] - 0.03
    eye_pos = Vector((eye_x, eye_y, eye_z))

    rx = 0.046
    rz = 0.068 if eye_style == "OVAL" else 0.048
    # 瞳本体
    res_pupil = bmesh.ops.create_circle(bm, cap_ends=True, radius=1.0, segments=16)
    for v in res_pupil['verts']:
        vx = v.co.x * rx
        vz = v.co.y * rz
        vy = -(vx * vx + vz * vz) * 0.4
        v.co = Vector((vx, vy, vz)) + eye_pos

    # 瞳ハイライト（白丸）
    hl_pos = eye_pos + Vector((rx * 0.35, -0.008, rz * 0.35))
    res_hl = bmesh.ops.create_circle(bm, cap_ends=True, radius=1.0, segments=12)
    for v in res_hl['verts']:
        vx = v.co.x * 0.016
        vz = v.co.y * 0.016
        v.co = Vector((vx, -0.002, vz)) + hl_pos

    # ハイライト面の material_index を 1 に設定
    for f in bm.faces:
        if any(v in res_hl['verts'] for v in f.verts):
            f.material_index = 1
        else:
            f.material_index = 0

    bm.to_mesh(mesh)
    bm.free()


    mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
    mod_mirror.use_axis[0] = True
    mod_sol = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_sol.thickness = 0.008

    return obj


def build_chibi_nose_mesh(context, name="Chibi_Nose", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """ちょこんとした小さな三角/丸鼻"""
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    nose_pos = Vector((0.0, -head_size[1] * 0.535, head_center[2] - 0.045))
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.024, radius2=0.006, depth=0.022)
    for v in res['verts']:
        vy = -v.co.z
        vz = v.co.y
        v.co = Vector((v.co.x, vy, vz)) + nose_pos

    bm.to_mesh(mesh)
    bm.free()

    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 1

    return obj


def build_chibi_hair_mesh(context, name="Chibi_Hair", gender="BOY", hair_style="SHORT", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """髪型メッシュ（ショート、ボブ、ツインテール）"""
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    hc = Vector(head_center)
    hsx, hsy, hsz = head_size[0] * 1.08, head_size[1] * 1.08, head_size[2] * 1.08

    # 頭部を覆うヘルメットベース
    res_base = bmesh.ops.create_cube(bm, size=1.0)
    for v in res_base['verts']:
        v.co.x *= hsx
        v.co.y *= hsy
        v.co.z = (v.co.z + 0.15) * hsz
        v.co += hc

    # スタイルごとの特徴造形
    if hair_style == "SHORT" or gender == "BOY":
        # 男の子ショート: 前髪のハネ感
        for v in bm.verts:
            if v.co.y < hc.y - 0.1 and v.co.z > hc.z:
                v.co.y -= 0.03
                v.co.z -= 0.02
    elif hair_style == "TWINTAILS":
        # 両サイドのお団子/ツインテール
        for side in (-1.0, 1.0):
            bun_pos = hc + Vector((side * hsx * 0.62, -0.02, hsz * 0.28))
            res_bun = bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.11)
            for v in res_bun['verts']:
                v.co += bun_pos
    elif hair_style == "BOB":
        # 女の子ボブ: 裾が内巻きに広がる
        for v in bm.verts:
            if v.co.z < hc.z + 0.05:
                v.co.x *= 1.12
                v.co.y *= 1.08

    bm.to_mesh(mesh)
    bm.free()

    mod_sol = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_sol.thickness = 0.025
    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 2
    mod_sub.render_levels = 2

    return obj


def build_chibi_outfit_mesh(context, name="Chibi_Outfit", gender="BOY", outfit_type="T_SHIRT", base_z=0.05, body_height=0.63):
    """衣装メッシュ（Tシャツ短パン、またはワンピースドレス）"""
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    leg_len = body_height * 0.38
    torso_len = body_height * 0.62

    if outfit_type == "ONE_PIECE" or gender == "GIRL":
        # 釣鐘型ワンピースドレス
        dress_z = base_z + leg_len * 0.35
        dress_top_z = base_z + leg_len + torso_len * 0.95
        depth = dress_top_z - dress_z

        bmesh.ops.create_cone(
            bm, cap_ends=False, segments=16,
            radius1=0.24, radius2=0.14, depth=depth
        )
        for v in bm.verts:
            v.co.z += dress_z + depth * 0.5
            v.co.y *= 0.92
    else:
        # Tシャツ（半袖胴体＋裾）
        t_z = base_z + leg_len * 0.65
        t_top_z = base_z + leg_len + torso_len * 0.96
        depth = t_top_z - t_z

        res_t = bmesh.ops.create_cone(
            bm, cap_ends=False, segments=16,
            radius1=0.20, radius2=0.155, depth=depth
        )
        for v in res_t['verts']:
            v.co.z += t_z + depth * 0.5
            v.co.y *= 0.88

    bm.to_mesh(mesh)
    bm.free()

    mod_sol = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_sol.thickness = 0.018
    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 2

    return obj


def build_chibi_shoes_mesh(context, name="Chibi_Shoes", foot_spacing=0.075, shoe_size=(0.10, 0.15, 0.085)):
    """
    コロンとした丸い靴（Mirror）
    重要: 接地位置を厳密に Z=0.0 に配置し、足音Surface判定用スロットを完備
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    sx, sy, sz = shoe_size

    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        y_fac = 1.0 + (v.co.y + 0.5) * 0.18
        vx = v.co.x * sx * y_fac + foot_spacing
        vy = v.co.y * sy + 0.02
        vz = (v.co.z + 0.5) * sz  # Z=0.0 接地
        v.co = Vector((vx, vy, vz))

    bm.to_mesh(mesh)
    bm.free()

    mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
    mod_mirror.use_axis[0] = True
    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 2

    return obj



def create_procedural_chibi_character(
    context,
    name="Chibi_Character",
    gender="BOY",
    head_ratio=2.2,
    total_height=1.15,
    hair_style="SHORT",
    outfit_type="T_SHIRT",
    skin_color=(0.96, 0.82, 0.74, 1.0),
    hair_color=(0.35, 0.22, 0.14, 1.0),
    cloth_top_color=(0.18, 0.55, 0.82, 1.0),
    cloth_bottom_color=(0.15, 0.25, 0.45, 1.0),
    shoe_color=(0.85, 0.25, 0.22, 1.0),
    seed=0
):
    """
    『どうぶつの森』風デフォルメ3Dキャラクター統合生成
    体（Body）を親（Root）として各パーツを親子付けし、マテリアルを一括適用
    """
    from ..materials.character_shaders import create_chibi_character_shader

    # 1. 幾何学パラメータ計算
    head_height = total_height / head_ratio
    body_height = total_height - head_height
    head_center_z = body_height + head_height * 0.38
    head_size = (head_height * 0.95, head_height * 0.85, head_height * 0.80)

    # 2. 各パーツメッシュ生成
    body_obj = build_chibi_body_mesh(context, f"{name}_Body", gender, head_ratio, total_height)
    head_obj = build_chibi_head_mesh(context, f"{name}_Head", (0, 0, head_center_z), head_size)
    ears_obj = build_chibi_ears_mesh(context, f"{name}_Ears", (0, 0, head_center_z), head_size)
    eyes_obj = build_chibi_eyes_mesh(context, f"{name}_Eyes", "OVAL", (0, 0, head_center_z), head_size)
    nose_obj = build_chibi_nose_mesh(context, f"{name}_Nose", (0, 0, head_center_z), head_size)
    hair_obj = build_chibi_hair_mesh(context, f"{name}_Hair", gender, hair_style, (0, 0, head_center_z), head_size)
    outfit_obj = build_chibi_outfit_mesh(context, f"{name}_Outfit", gender, outfit_type, 0.05, body_height)
    shoes_obj = build_chibi_shoes_mesh(context, f"{name}_Shoes")

    # 3. マテリアルの生成と適用
    mat_skin = create_chibi_character_shader(f"{name}_Skin_Mat", "SKIN", skin_color, 0.6, seed)
    mat_hair = create_chibi_character_shader(f"{name}_Hair_Mat", "HAIR", hair_color, 0.45, seed)
    mat_top = create_chibi_character_shader(f"{name}_ClothTop_Mat", "CLOTH_TOP", cloth_top_color, 0.7, seed)
    mat_eye = create_chibi_character_shader(f"{name}_Eye_Mat", "EYE", (0.12, 0.12, 0.14, 1.0), 0.15, seed)
    mat_eye_hl = create_chibi_character_shader(f"{name}_Eye_Highlight_Mat", "EYE_HIGHLIGHT", (1.0, 1.0, 1.0, 1.0), 0.05, seed)
    mat_nose = create_chibi_character_shader(f"{name}_Nose_Mat", "FACE_FEATURE", (skin_color[0]*0.9, skin_color[1]*0.75, skin_color[2]*0.7, 1.0), 0.5, seed)
    
    # Unity / Unreal Engine の足音・サーフェス判定用スロット
    mat_footstep = create_chibi_character_shader(f"{name}_Footstep_Surface_Mat", "FOOTSTEP_SURFACE", (0.2, 0.2, 0.2, 1.0), 0.85, seed)
    mat_shoe = create_chibi_character_shader(f"{name}_Shoe_Mat", "CLOTH_BOTTOM", shoe_color, 0.5, seed)

    # マテリアル割り当て
    body_obj.data.materials.append(mat_skin)
    head_obj.data.materials.append(mat_skin)
    ears_obj.data.materials.append(mat_skin)
    hair_obj.data.materials.append(mat_hair)
    outfit_obj.data.materials.append(mat_top)
    eyes_obj.data.materials.append(mat_eye)
    eyes_obj.data.materials.append(mat_eye_hl)
    nose_obj.data.materials.append(mat_nose)


    # 靴にはアッパー用と足音判定用（Footstep）の2スロットを確実に付与
    shoes_obj.data.materials.append(mat_shoe)
    shoes_obj.data.materials.append(mat_footstep)

    # 4. 親子付け（Body を Root として階層化）
    child_parts = [head_obj, ears_obj, eyes_obj, nose_obj, hair_obj, outfit_obj, shoes_obj]
    for child in child_parts:
        child.parent = body_obj
        child.matrix_parent_inverse = body_obj.matrix_world.inverted()

    # スムーズシェードを全パーツに適用
    for part in [body_obj] + child_parts:
        for poly in part.data.polygons:
            poly.use_smooth = True

    # アクティブオブジェクト設定
    context.view_layer.objects.active = body_obj
    body_obj.select_set(True)

    return body_obj
