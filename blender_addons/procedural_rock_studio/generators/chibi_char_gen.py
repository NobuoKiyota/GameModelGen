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
    v_knee = bm.verts.new((hip_x, 0.0, base_z + leg_len * 0.45))
    v_ankle = bm.verts.new((hip_x, 0.01, base_z + 0.025))

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
    """どうぶつの森風の愛らしい横長・ふっくら頭部（顔正面重視・後頭部最適化）"""
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    # 後頭部・頭頂部は髪で隠れるため 16x12 の適正解像度
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=0.5)
    sx, sy, sz = head_size[0], head_size[1], head_size[2]
    for v in bm.verts:
        norm_z = v.co.z / 0.5
        y_fac = 1.0 + max(0.0, -norm_z) * 0.12
        x_fac = 1.0 + max(0.0, -norm_z) * 0.16
        v.co.x *= sx * x_fac
        v.co.y *= sy * y_fac
        v.co.z *= sz
        v.co += Vector(head_center)

    bm.to_mesh(mesh)
    bm.free()

    # Subdiv Level 1 で十分滑らか（無駄な頂点爆発を抑制）
    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 1
    mod_sub.render_levels = 1

    return obj


def build_chibi_ears_mesh(context, name="Chibi_Ears", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """両耳メッシュ（軽量ミラー）"""
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    ear_pos = Vector((head_size[0] * 0.52, -0.02, head_center[2] - 0.02))
    res = bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.065)
    for v in res['verts']:
        v.co.x *= 0.35
        v.co.y *= 0.9
        v.co += ear_pos

    bm.to_mesh(mesh)
    bm.free()

    mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
    mod_mirror.use_axis[0] = True
    # スムーズシェードのみで十分丸いためSubdiv削除（約3000頂点を大幅間引き）

    return obj


def build_chibi_eyes_mesh(context, name="Chibi_Eyes", eye_style="OVAL", eye_scale=1.0, head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """
    どうぶつの森風の愛らしい瞳メッシュ ＋ ハイライト
    ゲーム・アニメーション用シェイプキー（Basis, Blink, Smile, Wide, Squint）を完全装備
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    eye_x = head_size[0] * 0.235
    eye_z = head_center[2] - 0.040

    # 頭部曲面（下膨れ楕円体）にフィットするY座標を正確に計算
    norm_z = (eye_z - head_center[2]) / (head_size[2] * 0.5)
    y_fac = 1.0 + max(0.0, -norm_z) * 0.12
    x_fac = 1.0 + max(0.0, -norm_z) * 0.16
    nx = eye_x / max(0.01, head_size[0] * x_fac * 0.5)
    nz = (eye_z - head_center[2]) / max(0.01, head_size[2] * 0.5)
    ny_sq = max(0.05, 1.0 - nx * nx - nz * nz)
    eye_y = head_center[1] - math.sqrt(ny_sq) * 0.5 * head_size[1] * y_fac - 0.003
    eye_pos = Vector((eye_x, eye_y, eye_z))

    has_highlight = True
    hl_pos = eye_pos
    hl_r = 0.0085 * eye_scale

    if eye_style == "SMILING":
        # にっこり三日月目（アーチ形状の細長い笑顔目）
        has_highlight = False
        res_pupil = bmesh.ops.create_circle(bm, cap_ends=True, radius=1.0, segments=16)
        rx = 0.032 * eye_scale
        rz = 0.018 * eye_scale
        for v in res_pupil['verts']:
            vx = v.co.x * rx
            norm_vx = vx / rx
            arch_z = (1.0 - norm_vx * norm_vx) * rz * 0.85
            vz = v.co.y * rz * 0.35 + arch_z
            vy = -(vx * vx + vz * vz) * 0.5
            v.co = Vector((vx, vy, vz)) + eye_pos
        res_hl = {'verts': []}

    else:
        rx = 0.026 * eye_scale
        if eye_style == "ROUND":
            rz = 0.026 * eye_scale
        elif eye_style == "DROOPY":
            rz = 0.038 * eye_scale
        elif eye_style == "CAT_EYE":
            rz = 0.034 * eye_scale
        else:  # OVAL
            rz = 0.040 * eye_scale

        res_pupil = bmesh.ops.create_circle(bm, cap_ends=True, radius=1.0, segments=20)
        for v in res_pupil['verts']:
            vx = v.co.x * rx
            vz = v.co.y * rz

            if eye_style == "DROOPY":
                vz -= vx * 0.28
            elif eye_style == "CAT_EYE":
                vz += vx * 0.35

            vy = -(vx * vx + vz * vz) * 0.5
            v.co = Vector((vx, vy, vz)) + eye_pos

        if eye_style == "DROOPY":
            hl_pos = eye_pos + Vector((rx * 0.20, -0.003, -rz * 0.15))
            hl_r = 0.0075 * eye_scale
        elif eye_style == "CAT_EYE":
            hl_pos = eye_pos + Vector((-rx * 0.15, -0.003, rz * 0.25))
            hl_r = 0.0075 * eye_scale
        else:
            hl_pos = eye_pos + Vector((rx * 0.32, -0.003, rz * 0.32))
            hl_r = 0.0085 * eye_scale

        res_hl = bmesh.ops.create_circle(bm, cap_ends=True, radius=1.0, segments=12)
        for v in res_hl['verts']:
            vx = v.co.x * hl_r
            vz = v.co.y * hl_r
            v.co = Vector((vx, -0.002, vz)) + hl_pos

    for f in bm.faces:
        if has_highlight and any(v in res_hl['verts'] for v in f.verts):
            f.material_index = 1
        else:
            f.material_index = 0

    bm.to_mesh(mesh)
    bm.free()

    # 🌟 表情差分アニメーション用シェイプキー（Blend Shapes）の自動装備
    try:
        obj.shape_key_add(name="Basis", from_mix=False)

        # 1. Blink: まばたき（上下がつぶれて閉じる）
        sk_blink = obj.shape_key_add(name="Blink", from_mix=False)
        for pt in sk_blink.data:
            dz = pt.co.z - eye_pos.z
            pt.co.z = eye_pos.z + dz * 0.06
            pt.co.y += 0.001

        # 2. Smile: にっこり笑顔（上向き凸三日月アーチ）
        sk_smile = obj.shape_key_add(name="Smile", from_mix=False)
        for pt in sk_smile.data:
            dx = (pt.co.x - eye_pos.x) / max(0.001, rx)
            arch = (1.0 - min(1.0, dx * dx)) * 0.016
            pt.co.z = eye_pos.z + (pt.co.z - eye_pos.z) * 0.20 + arch
            pt.co.y += 0.0015

        # 3. Wide: 驚き見開き（1.25倍拡大）
        sk_wide = obj.shape_key_add(name="Wide", from_mix=False)
        for pt in sk_wide.data:
            pt.co.x = eye_pos.x + (pt.co.x - eye_pos.x) * 1.25
            pt.co.z = eye_pos.z + (pt.co.z - eye_pos.z) * 1.25

        # 4. Squint: ジト目（上半分が下がる）
        sk_squint = obj.shape_key_add(name="Squint", from_mix=False)
        for pt in sk_squint.data:
            dz = pt.co.z - eye_pos.z
            if dz > 0:
                pt.co.z = eye_pos.z + dz * 0.25
    except Exception:
        pass

    mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
    mod_mirror.use_axis[0] = True
    mod_sol = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_sol.thickness = 0.006

    return obj


def build_chibi_eyebrows_mesh(context, name="Chibi_Eyebrows", eyebrow_style="ARCH", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """
    愛らしい眉毛メッシュ（Mirror対称 ＋ 頭部曲面自動フィット）
    - ARCH: なだらかアーチ眉
    - DOT: ちょこんとした丸眉（麻呂眉）
    - STRAIGHT: キリッとしたまっすぐ眉
    """
    if eyebrow_style == "NONE":
        return None

    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    brow_x = head_size[0] * 0.235
    brow_z = head_center[2] + 0.006  # 目の上方約0.046m

    # 頭部曲面に沿うY座標
    norm_z = (brow_z - head_center[2]) / (head_size[2] * 0.5)
    y_fac = 1.0 + max(0.0, -norm_z) * 0.12
    x_fac = 1.0 + max(0.0, -norm_z) * 0.16
    nx = brow_x / max(0.01, head_size[0] * x_fac * 0.5)
    nz = (brow_z - head_center[2]) / max(0.01, head_size[2] * 0.5)
    ny_sq = max(0.05, 1.0 - nx * nx - nz * nz)
    brow_y = head_center[1] - math.sqrt(ny_sq) * 0.5 * head_size[1] * y_fac - 0.003
    brow_pos = Vector((brow_x, brow_y, brow_z))

    if eyebrow_style == "DOT":
        # まる眉（麻呂眉）
        r = 0.014
        res = bmesh.ops.create_circle(bm, cap_ends=True, radius=r, segments=14)
        for v in res['verts']:
            v.co = Vector((v.co.x, -(v.co.x*v.co.x + v.co.y*v.co.y)*0.5, v.co.y)) + brow_pos

    elif eyebrow_style == "STRAIGHT":
        # まっすぐ眉
        bw = 0.024
        bh = 0.0065
        res = bmesh.ops.create_cube(bm, size=1.0)
        for v in res['verts']:
            vx = v.co.x * bw * 2.0
            vz = v.co.z * bh * 2.0
            vy = v.co.y * 0.006
            v.co = Vector((vx, vy, vz)) + brow_pos

    else:
        # ARCH: なだらかアーチ眉
        res = bmesh.ops.create_circle(bm, cap_ends=True, radius=1.0, segments=16)
        rx = 0.026
        rz = 0.007
        for v in res['verts']:
            vx = v.co.x * rx
            norm_vx = vx / rx
            arch_z = (1.0 - norm_vx * norm_vx) * 0.0075 - norm_vx * 0.003
            vz = v.co.y * rz + arch_z
            vy = -(vx * vx + vz * vz) * 0.5
            v.co = Vector((vx, vy, vz)) + brow_pos

    bm.to_mesh(mesh)
    bm.free()

    mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
    mod_mirror.use_axis[0] = True
    mod_sol = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_sol.thickness = 0.005

    return obj


def build_chibi_nose_mesh(context, name="Chibi_Nose", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """
    ちょこんとした愛らしい三角小鼻（目とのバランスを最適化）
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    nose_z = head_center[2] - 0.054
    norm_z = (nose_z - head_center[2]) / (head_size[2] * 0.5)
    y_fac = 1.0 + max(0.0, -norm_z) * 0.12
    nz = (nose_z - head_center[2]) / max(0.01, head_size[2] * 0.5)
    ny_sq = max(0.05, 1.0 - nz * nz)
    nose_y = head_center[1] - math.sqrt(ny_sq) * 0.5 * head_size[1] * y_fac - 0.002
    nose_pos = Vector((0.0, nose_y, nose_z))

    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.017, radius2=0.004, depth=0.016)
    for v in res['verts']:
        vy = -v.co.z
        vz = v.co.y
        v.co = Vector((v.co.x, vy, vz)) + nose_pos

    bm.to_mesh(mesh)
    bm.free()

    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 1

    return obj


def build_chibi_hair_front_mesh(context, name="Chibi_Hair_Front", front_style="SHORT", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """
    前髪メッシュ（前髪・毛束フリンジ・もみあげ 独立パーツ）
    耳の手前で自然に抜けるレイヤー構造により、耳へのめり込みを完全に防止
    対応スタイル: SHORT, SHORT_MESSY, CENTER_PART, MUSHROOM, NONE
    """
    if front_style == "NONE":
        return None

    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    hc = Vector(head_center)
    hsx, hsy, hsz = head_size[0], head_size[1], head_size[2]

    # 高精細UV球ベース（前頭部特化）
    bmesh.ops.create_uvsphere(bm, u_segments=36, v_segments=22, radius=0.5)

    def calc_front_cutoff(norm_x, style):
        if style == "MUSHROOM":
            return 0.12 + 0.02 * math.cos(norm_x * 2.0 * math.pi)
        elif style == "CENTER_PART":
            return 0.20 - 0.10 * math.cos(norm_x * math.pi * 0.85)
        elif style == "SHORT_MESSY":
            wave1 = math.sin((norm_x + 0.15) * 3.5 * math.pi) * 0.030
            wave2 = math.cos((norm_x - 0.20) * 2.0 * math.pi) * 0.020
            return 0.13 + 0.04 * norm_x + wave1 + wave2
        else:  # SHORT
            fringe = math.sin((norm_x - 0.12) * 3.0 * math.pi) * 0.025 + math.cos(norm_x * 1.8 * math.pi) * 0.018
            return 0.13 + 0.03 * norm_x + fringe

    del_verts = []
    for v in bm.verts:
        norm_z = v.co.z / 0.5
        norm_y = v.co.y / 0.5
        norm_x = v.co.x / 0.5

        # 1. 後頭部側の除外（頭頂部は深くオーバーラップして隙間を防止、耳まわりだけ前で抜く）
        back_limit = 0.18 if norm_z > 0.15 else 0.02
        if norm_y > back_limit:
            del_verts.append(v)
            continue

        # 2. 耳の逃げ穴（耳位置近傍のめり込み防止）
        if abs(norm_x) > 0.40 and norm_y > -0.04 and norm_z < 0.12:
            del_verts.append(v)
            continue

        # 3. 前髪生え際＆もみあげのカットライン
        cutoff = calc_front_cutoff(norm_x, front_style)
        if abs(norm_x) > 0.32:
            # 耳前もみあげ（耳の手前・前方に自然に下ろす）
            side_depth = (abs(norm_x) - 0.32) * 1.10
            cutoff -= side_depth

        if norm_z < cutoff:
            del_verts.append(v)

    bmesh.ops.delete(bm, geom=del_verts, context='VERTS')

    # 境界エッジの滑らかなスナップ
    for v in bm.verts:
        if v.is_boundary and v.co.y < 0.0:
            nx = v.co.x / 0.5
            cz = calc_front_cutoff(nx, front_style)
            if abs(nx) > 0.32:
                cz -= (abs(nx) - 0.32) * 1.10
            v.co.z = cz * 0.5

    # 頭部サイズにフィット＆ふっくらボリューム
    for v in bm.verts:
        norm_z = v.co.z / 0.5
        y_fac = 1.0 + max(0.0, -norm_z) * 0.07
        x_fac = 1.0 + max(0.0, -norm_z) * 0.09
        vx = v.co.x * hsx * x_fac * 1.08
        vy = v.co.y * hsy * y_fac * 1.08
        vz = v.co.z * hsz * 1.08
        v.co = Vector((vx, vy, vz)) + hc

    bm.to_mesh(mesh)
    bm.free()

    mod_sol = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_sol.thickness = 0.018
    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 1
    mod_sub.render_levels = 1

    return obj


def build_chibi_hair_back_mesh(context, name="Chibi_Hair_Back", back_style="SHORT_NAPE", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """
    後ろ髪メッシュ（後頭部・襟足・サイドお団子・長髪 独立パーツ）
    耳の後ろから首筋を包み込むレイヤー構造により、耳へのめり込みを完全に防止
    対応スタイル: SHORT_NAPE, BOB, WAVY_LONG, TWINTAILS, BRAIDS, PONYTAIL, TOPKNOT, SPIKY, AFRO, NONE
    """
    if back_style == "NONE":
        return None

    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    hc = Vector(head_center)
    hsx, hsy, hsz = head_size[0], head_size[1], head_size[2]

    if back_style == "AFRO":
        res_afro = bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=18, radius=0.32)
        afro_p = hc + Vector((0.0, 0.05, hsz * 0.12))
        afro_del = []
        for v in res_afro['verts']:
            pos = (v.co * 1.05) + afro_p
            if pos.y < hc.y - 0.04 and pos.z < hc.z + 0.10:
                afro_del.append(v)
            else:
                bump = math.sin(v.co.x * 35.0) * math.cos(v.co.z * 35.0) * 0.007
                v.co = pos + Vector((bump, bump, bump))
        if afro_del:
            bmesh.ops.delete(bm, geom=afro_del, context='VERTS')

    else:
        bmesh.ops.create_uvsphere(bm, u_segments=36, v_segments=22, radius=0.5)

        del_verts = []
        for v in bm.verts:
            norm_z = v.co.z / 0.5
            norm_y = v.co.y / 0.5
            norm_x = v.co.x / 0.5

            # 1. 前面側の除外判定（頭頂部は前髪としっかり重ね、耳の高さは前方を抜く）
            front_limit = -0.16 if norm_z > 0.15 else 0.00
            if norm_y < front_limit:
                del_verts.append(v)
                continue

            # 2. 耳の逃げ穴（耳位置近傍の切り欠き）
            if abs(norm_x) > 0.40 and -0.06 <= norm_y <= 0.08 and norm_z < 0.12:
                del_verts.append(v)
                continue

            # 3. 襟足カットライン
            if back_style == "WAVY_LONG":
                limit_z = -0.58
            elif back_style == "BOB":
                limit_z = -0.26 - 0.04 * (1.0 - abs(norm_x))
            else:  # SHORT_NAPE 等
                center_depth = 1.0 - min(1.0, abs(norm_x) * 1.1)
                limit_z = -0.30 - 0.16 * center_depth

            if norm_z < limit_z:
                del_verts.append(v)

        bmesh.ops.delete(bm, geom=del_verts, context='VERTS')

        # 境界エッジの滑らかなスナップ
        for v in bm.verts:
            if v.is_boundary and v.co.y >= -0.04:
                nx = v.co.x / 0.5
                if back_style == "WAVY_LONG":
                    tz = -0.58
                elif back_style == "BOB":
                    tz = -0.26 - 0.04 * (1.0 - abs(nx))
                else:
                    cd = 1.0 - min(1.0, abs(nx) * 1.1)
                    tz = -0.30 - 0.16 * cd
                v.co.z = max(v.co.z, tz * 0.5)

        # スケール＆配置
        for v in bm.verts:
            norm_z = v.co.z / 0.5
            y_fac = 1.0 + max(0.0, -norm_z) * 0.08
            x_fac = 1.0 + max(0.0, -norm_z) * 0.10
            vx = v.co.x * hsx * x_fac * 1.08
            vy = v.co.y * hsy * y_fac * 1.08
            vz = v.co.z * hsz * 1.08
            v.co = Vector((vx, vy, vz)) + hc

        # スタイル固有の付属物（お団子、三つ編み、ポニテ、スパイク）
        if back_style == "TWINTAILS":
            for side in (-1.0, 1.0):
                bun_pos = hc + Vector((side * hsx * 0.55, 0.04, hsz * 0.18))
                res_bun = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=0.105)
                for v in res_bun['verts']:
                    v.co += bun_pos

        elif back_style == "BRAIDS":
            for side in (-1.0, 1.0):
                base_braid = hc + Vector((side * hsx * 0.48, 0.02, -hsz * 0.05))
                for i in range(3):
                    b_pos = base_braid + Vector((side * i * 0.012, -0.01 * i, -i * 0.08))
                    b_rad = 0.048 - i * 0.006
                    res_b = bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=10, radius=b_rad)
                    for v in res_b['verts']:
                        v.co.x *= 0.85
                        v.co += b_pos
                tip_p = base_braid + Vector((side * 0.038, -0.03, -0.26))
                res_tip = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.025, radius2=0.005, depth=0.05)
                for v in res_tip['verts']:
                    v.co += tip_p

        elif back_style == "TOPKNOT":
            knot_p = hc + Vector((0.0, 0.04, hsz * 0.52))
            res_knot = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=0.085)
            for v in res_knot['verts']:
                v.co.z *= 0.85
                v.co += knot_p
            res_ring = bmesh.ops.create_cone(bm, cap_ends=False, segments=14, radius1=0.05, radius2=0.045, depth=0.02)
            for v in res_ring['verts']:
                v.co += knot_p - Vector((0, 0, 0.04))

        elif back_style == "PONYTAIL":
            tie_p = hc + Vector((0.0, hsy * 0.48, hsz * 0.18))
            res_tie = bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=10, radius=0.034)
            for v in res_tie['verts']:
                v.co += tie_p
            res_tail = bmesh.ops.create_cone(bm, cap_ends=True, segments=14, radius1=0.065, radius2=0.015, depth=0.15)
            for v in res_tail['verts']:
                vx = v.co.x
                vy = v.co.z * 0.65 + v.co.y * 0.75 + 0.06
                vz = -v.co.z * 0.75 + v.co.y * 0.65 - 0.04
                v.co = Vector((vx, vy, vz)) + tie_p

        elif back_style == "SPIKY":
            spikes = [
                (0.0, 0.02, hsz * 0.50, 0.0, 0.0),
                (-0.08, 0.04, hsz * 0.46, -0.25, 0.0),
                (0.08, 0.04, hsz * 0.46, 0.25, 0.0),
                (0.0, 0.14, hsz * 0.38, 0.0, 0.30),
                (-0.10, 0.10, hsz * 0.35, -0.20, 0.25),
                (0.10, 0.10, hsz * 0.35, 0.20, 0.25),
            ]
            for sx, sy, sz, rx, ry in spikes:
                res_spk = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.038, radius2=0.005, depth=0.09)
                base_p = hc + Vector((sx, sy, sz))
                for v in res_spk['verts']:
                    vx = v.co.x + ry * v.co.z
                    vy = v.co.y + rx * v.co.z
                    vz = v.co.z
                    v.co = Vector((vx, vy, vz)) + base_p

        elif back_style == "WAVY_LONG":
            for v in bm.verts:
                if v.co.z < hc.z + 0.02:
                    wave_x = math.sin((v.co.z - hc.z) * 24.0) * 0.014
                    wave_y = math.cos((v.co.z - hc.z) * 24.0) * 0.010
                    v.co.x += wave_x
                    v.co.y += wave_y
                    v.co.x = hc.x + (v.co.x - hc.x) * 1.10

        elif back_style == "BOB":
            for v in bm.verts:
                if v.co.z < hc.z + 0.05:
                    v.co.x *= 1.10
                    v.co.y *= 1.06

    bm.to_mesh(mesh)
    bm.free()

    mod_sol = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_sol.thickness = 0.022
    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 1
    mod_sub.render_levels = 1

    return obj


def build_chibi_hair_mesh(context, name="Chibi_Hair", gender="BOY", hair_style="SHORT", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """
    旧互換用ヘアスタイルメッシュ（前髪・後ろ髪を一体化して生成）
    """
    front_style = "SHORT"
    back_style = "SHORT_NAPE"
    if hair_style in ("SHORT", "SHORT_MESSY", "CENTER_PART", "MUSHROOM"):
        front_style = hair_style
        back_style = "SHORT_NAPE"
    elif hair_style == "BOB":
        front_style = "SHORT"
        back_style = "BOB"
    elif hair_style == "TWINTAILS":
        front_style = "SHORT"
        back_style = "TWINTAILS"
    elif hair_style == "BRAIDS":
        front_style = "SHORT"
        back_style = "BRAIDS"
    elif hair_style == "PONYTAIL":
        front_style = "SHORT"
        back_style = "PONYTAIL"
    elif hair_style == "TOPKNOT":
        front_style = "CENTER_PART"
        back_style = "TOPKNOT"
    elif hair_style == "SPIKY":
        front_style = "SHORT_MESSY"
        back_style = "SPIKY"
    elif hair_style == "WAVY_LONG":
        front_style = "SHORT"
        back_style = "WAVY_LONG"
    elif hair_style == "AFRO":
        front_style = "NONE"
        back_style = "AFRO"

    # 前髪・後ろ髪の両方を生成して1つのメッシュに結合（後方互換）
    f_obj = build_chibi_hair_front_mesh(context, name + "_Front_Temp", front_style, head_center, head_size)
    b_obj = build_chibi_hair_back_mesh(context, name + "_Back_Temp", back_style, head_center, head_size)

    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    if f_obj and f_obj.data:
        bm.from_mesh(f_obj.data)
    if b_obj and b_obj.data:
        bm.from_mesh(b_obj.data)
    bm.to_mesh(mesh)
    bm.free()

    # クリーンアップ
    for temp in (f_obj, b_obj):
        if temp:
            m = temp.data
            bpy.data.objects.remove(temp, do_unlink=True)
            if m and m.users == 0:
                bpy.data.meshes.remove(m)

    mod_sol = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_sol.thickness = 0.020
    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 1
    mod_sub.render_levels = 1

    return obj


def build_chibi_outfit_mesh(context, name="Chibi_Outfit", gender="BOY", outfit_type="T_SHIRT", base_z=0.05, body_height=0.63):
    """
    衣装メッシュ（全6種類対応）
    T_SHIRT, ONE_PIECE, HOODIE, OVERALLS, KIMONO, COAT
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    leg_len = body_height * 0.38
    torso_len = body_height * 0.62

    sin_theta = 0.36
    cos_theta = 0.933
    sh_z = base_z + leg_len + torso_len * 0.80

    if outfit_type == "ONE_PIECE":
        # 釣鐘型ワンピース
        dress_z = base_z + leg_len * 0.35
        dress_top_z = base_z + leg_len + torso_len * 0.95
        depth = dress_top_z - dress_z
        res_d = bmesh.ops.create_cone(
            bm, cap_ends=False, segments=24,
            radius1=0.25, radius2=0.165, depth=depth
        )
        for v in res_d['verts']:
            v.co.z += dress_z + depth * 0.5
            v.co.y *= 0.90

    elif outfit_type == "KIMONO":
        # 和服・浴衣（ストレートに足元まで伸びる裾 ＋ 角型振袖）
        kimono_z = base_z + leg_len * 0.15
        kimono_top_z = base_z + leg_len + torso_len * 0.96
        depth = kimono_top_z - kimono_z
        res_k = bmesh.ops.create_cone(
            bm, cap_ends=False, segments=20,
            radius1=0.21, radius2=0.175, depth=depth
        )
        for v in res_k['verts']:
            v.co.z += kimono_z + depth * 0.5
            v.co.y *= 0.92

        # 帯（Obi: 腰の太いベルト）
        obi_z = base_z + leg_len + torso_len * 0.38
        res_obi = bmesh.ops.create_cone(bm, cap_ends=False, segments=20, radius1=0.215, radius2=0.21, depth=0.08)
        for v in res_obi['verts']:
            v.co.z += obi_z
            v.co.y *= 0.94

        # 振袖（左右の四角い和風垂れ袖）
        for side in (-1.0, 1.0):
            sleeve_p = Vector((side * 0.20, -0.01, sh_z - 0.08))
            res_sl = bmesh.ops.create_cube(bm, size=1.0)
            for v in res_sl['verts']:
                v.co.x = v.co.x * 0.06 + sleeve_p.x
                v.co.y = v.co.y * 0.10 + sleeve_p.y
                v.co.z = v.co.z * 0.16 + sleeve_p.z

    elif outfit_type == "OVERALLS":
        # サロペット・オーバーオール（胴体 ＋ 肩紐サスペンダー）
        t_z = base_z + leg_len * 0.25
        t_top_z = base_z + leg_len + torso_len * 0.92
        depth = t_top_z - t_z
        res_ov = bmesh.ops.create_cone(bm, cap_ends=False, segments=20, radius1=0.22, radius2=0.18, depth=depth)
        for v in res_ov['verts']:
            v.co.z += t_z + depth * 0.5
            v.co.y *= 0.89

        # 肩紐サスペンダー（左右の帯）
        for side in (-1.0, 1.0):
            res_strap = bmesh.ops.create_cube(bm, size=1.0)
            for v in res_strap['verts']:
                v.co.x = v.co.x * 0.025 + (side * 0.075)
                v.co.y = v.co.y * 0.15 - 0.01
                v.co.z = v.co.z * 0.02 + (base_z + leg_len + torso_len * 0.92)

    elif outfit_type == "HOODIE":
        # パーカー（少しゆったり胴体 ＋ 長袖 ＋ 背中フード ＋ 丸い撫で肩）
        t_z = base_z + leg_len * 0.55
        t_top_z = base_z + leg_len + torso_len * 0.96
        depth = t_top_z - t_z
        res_t = bmesh.ops.create_cone(bm, cap_ends=False, segments=20, radius1=0.225, radius2=0.18, depth=depth)
        for v in res_t['verts']:
            v.co.z += t_z + depth * 0.5
            v.co.y *= 0.91
            # 撫で肩カーブ
            if v.co.z > t_top_z - 0.07:
                v.co.z -= (abs(v.co.x) / 0.18) ** 2 * 0.022

        # 長袖（丸いラウンドスリーブ）
        sleeve_len = 0.18
        for side in (-1.0, 1.0):
            sh_x = side * 0.125
            center_x = sh_x + side * (sleeve_len * 0.5 * sin_theta)
            center_z = sh_z - (sleeve_len * 0.5 * cos_theta)
            res_sl = bmesh.ops.create_cone(bm, cap_ends=False, segments=16, radius1=0.085, radius2=0.100, depth=sleeve_len)
            for v in res_sl['verts']:
                vx, vy, vz = v.co.x, v.co.y, v.co.z
                if vz > 0:
                    vx *= 0.82
                    vy *= 0.85
                v.co.x = vx * cos_theta - side * vz * sin_theta + center_x
                v.co.y = vy * 0.93 - 0.01
                v.co.z = side * vx * sin_theta + vz * cos_theta + center_z
                if v.co.z > sh_z - 0.04 and abs(v.co.x) > 0.13:
                    v.co.z -= (abs(v.co.x) - 0.13) * 0.35

        # 背中のフード（ふっくら垂れ下がった袋状メッシュ）
        res_hood = bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=10, radius=0.12)
        hood_p = Vector((0.0, 0.13, base_z + leg_len + torso_len * 0.82))
        for v in res_hood['verts']:
            v.co.x *= 0.95
            v.co.y *= 0.75
            v.co.z *= 0.80
            v.co += hood_p

    elif outfit_type == "COAT":
        # ダッフルコート（腰下長め ＋ 折り返し襟 ＋ 長袖 ＋ 丸い撫で肩）
        c_z = base_z + leg_len * 0.30
        c_top_z = base_z + leg_len + torso_len * 0.96
        depth = c_top_z - c_z
        res_c = bmesh.ops.create_cone(bm, cap_ends=False, segments=20, radius1=0.23, radius2=0.185, depth=depth)
        for v in res_c['verts']:
            v.co.z += c_z + depth * 0.5
            v.co.y *= 0.90
            # 撫で肩カーブ
            if v.co.z > c_top_z - 0.07:
                v.co.z -= (abs(v.co.x) / 0.18) ** 2 * 0.022

        # 長袖
        sleeve_len = 0.18
        for side in (-1.0, 1.0):
            sh_x = side * 0.125
            center_x = sh_x + side * (sleeve_len * 0.5 * sin_theta)
            center_z = sh_z - (sleeve_len * 0.5 * cos_theta)
            res_sl = bmesh.ops.create_cone(bm, cap_ends=False, segments=16, radius1=0.088, radius2=0.105, depth=sleeve_len)
            for v in res_sl['verts']:
                vx, vy, vz = v.co.x, v.co.y, v.co.z
                if vz > 0:
                    vx *= 0.82
                    vy *= 0.85
                v.co.x = vx * cos_theta - side * vz * sin_theta + center_x
                v.co.y = vy * 0.93 - 0.01
                v.co.z = side * vx * sin_theta + vz * cos_theta + center_z
                if v.co.z > sh_z - 0.04 and abs(v.co.x) > 0.13:
                    v.co.z -= (abs(v.co.x) - 0.13) * 0.35

        # 首元の折り返し襟 (Collar)
        res_col = bmesh.ops.create_cone(bm, cap_ends=False, segments=16, radius1=0.17, radius2=0.14, depth=0.06)
        col_z = base_z + leg_len + torso_len * 0.94
        for v in res_col['verts']:
            v.co.z += col_z
            v.co.y *= 0.95

    else:
        # T_SHIRT: 半袖 ＋ 短パン ＋ 丸い撫で肩
        t_z = base_z + leg_len * 0.65
        t_top_z = base_z + leg_len + torso_len * 0.96
        depth = t_top_z - t_z
        res_t = bmesh.ops.create_cone(bm, cap_ends=False, segments=20, radius1=0.21, radius2=0.18, depth=depth)
        for v in res_t['verts']:
            v.co.z += t_z + depth * 0.5
            v.co.y *= 0.88
            # 撫で肩カーブ（首元が高く、肩端に向かってなだらかに下がる）
            if v.co.z > t_top_z - 0.07:
                v.co.z -= (abs(v.co.x) / 0.18) ** 2 * 0.022

        sleeve_len = 0.125
        for side in (-1.0, 1.0):
            sh_x = side * 0.125
            center_x = sh_x + side * (sleeve_len * 0.5 * sin_theta)
            center_z = sh_z - (sleeve_len * 0.5 * cos_theta)
            res_sl = bmesh.ops.create_cone(bm, cap_ends=False, segments=16, radius1=0.090, radius2=0.105, depth=sleeve_len)
            for v in res_sl['verts']:
                vx, vy, vz = v.co.x, v.co.y, v.co.z
                # 肩の付け根を内側に寄せて丸いラウンドショルダーに
                if vz > 0:
                    vx *= 0.80
                    vy *= 0.85
                v.co.x = vx * cos_theta - side * vz * sin_theta + center_x
                v.co.y = vy * 0.93 - 0.01
                v.co.z = side * vx * sin_theta + vz * cos_theta + center_z
                # 肩先の角を落として丸める
                if v.co.z > sh_z - 0.04 and abs(v.co.x) > 0.13:
                    v.co.z -= (abs(v.co.x) - 0.13) * 0.35

    # 🔘 小さな立体ボタンの追加（オーバーオール、コート、Tシャツ等）
    btn_verts = []
    if outfit_type == "OVERALLS":
        # サロペットの左右肩紐留め具ボタン（2個）
        for side in (-1.0, 1.0):
            bp = Vector((side * 0.075, -0.162, base_z + leg_len + torso_len * 0.72))
            res_b = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.015)
            for v in res_b['verts']:
                v.co.y *= 0.4
                v.co += bp
                btn_verts.append(v)

    elif outfit_type == "COAT":
        # コートの前立て中央ボタン（縦2個）
        for bz in (base_z + leg_len + torso_len * 0.70, base_z + leg_len + torso_len * 0.48):
            bp = Vector((0.0, -0.178, bz))
            res_b = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.016)
            for v in res_b['verts']:
                v.co.y *= 0.45
                v.co += bp
                btn_verts.append(v)

    elif outfit_type == "T_SHIRT":
        # Tシャツのヘンリーネックアクセントボタン（1個）
        bp = Vector((0.0, -0.158, base_z + leg_len + torso_len * 0.86))
        res_b = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.011)
        for v in res_b['verts']:
            v.co.y *= 0.4
            v.co += bp
            btn_verts.append(v)

    # ボタン面の材質スロット割り当て (0: 服地, 1: ボタン)
    for f in bm.faces:
        if btn_verts and any(v in btn_verts for v in f.verts):
            f.material_index = 1
        else:
            f.material_index = 0

    bm.to_mesh(mesh)
    bm.free()

    mod_sol = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_sol.thickness = 0.018
    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 1
    mod_sub.render_levels = 1

    return obj


def build_chibi_shoes_mesh(context, name="Chibi_Shoes", foot_spacing=0.075, shoe_size=(0.10, 0.15, 0.085)):
    """
    コロンとした丸い靴（Mirror）
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
        vz = (v.co.z + 0.5) * sz
        v.co = Vector((vx, vy, vz))

    bm.to_mesh(mesh)
    bm.free()

    mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
    mod_mirror.use_axis[0] = True
    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 2
    mod_sub.render_levels = 2

    return obj





def build_chibi_accessories_mesh(context, name="Chibi_Accessory", accessory_type="NONE", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """
    アクセサリーメッシュ生成
    - ROUND_GLASSES: 知的な丸メガネ（フレーム ＋ ブリッジ ＋ テンプル）
    - CHEEK_BLUSH: 両頬のふんわりピンクチーク
    """
    if accessory_type == "NONE":
        return None

    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    hc = Vector(head_center)
    hsx, hsy, hsz = head_size

    if accessory_type == "ROUND_GLASSES":
        eye_x = hsx * 0.235
        eye_z = hc.z - 0.038
        glasses_y = hc.y - hsy * 0.535
        r_lens = 0.054

        for side in (-1.0, 1.0):
            res_ring = bmesh.ops.create_circle(bm, cap_ends=False, radius=r_lens, segments=18)
            for v in res_ring['verts']:
                v.co = Vector((side * eye_x + v.co.x, glasses_y, eye_z + v.co.y))

            temple_p = Vector((side * (eye_x + r_lens * 0.95), glasses_y, eye_z))
            res_tmp = bmesh.ops.create_cone(bm, cap_ends=False, segments=6, radius1=0.006, radius2=0.006, depth=0.22)
            for v in res_tmp['verts']:
                v.co = Vector((temple_p.x, temple_p.y + (v.co.z + 0.11) * 1.0, temple_p.z + v.co.y))

        res_brg = bmesh.ops.create_cone(bm, cap_ends=False, segments=6, radius1=0.007, radius2=0.007, depth=eye_x * 0.85)
        for v in res_brg['verts']:
            v.co = Vector((v.co.z, glasses_y + 0.005, eye_z + 0.005 + v.co.y))

        bm.to_mesh(mesh)
        bm.free()

        mod_sol = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
        mod_sol.thickness = 0.012

    elif accessory_type == "CHEEK_BLUSH":
        for side in (-1.0, 1.0):
            blush_x = side * hsx * 0.32
            blush_z = hc.z - 0.065
            blush_y = hc.y - hsy * 0.42 - 0.005
            res_bl = bmesh.ops.create_circle(bm, cap_ends=True, radius=1.0, segments=14)
            for v in res_bl['verts']:
                vx = v.co.x * 0.035
                vz = v.co.y * 0.022
                vy = -(vx * vx + vz * vz) * 0.6
                v.co = Vector((blush_x + vx, blush_y + vy, blush_z + vz))

        bm.to_mesh(mesh)
        bm.free()

        mod_sol = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
        mod_sol.thickness = 0.003

    return obj


def create_procedural_chibi_character(
    context,
    name="Chibi_Character",
    gender="BOY",
    head_ratio=2.2,
    total_height=1.15,
    hair_style="SHORT",
    hair_front="SHORT",
    hair_back="SHORT_NAPE",
    outfit_type="T_SHIRT",
    eye_style="OVAL",
    eye_scale=1.0,
    pattern="PLAIN",
    accessory="NONE",
    eyebrow_style="ARCH",
    skin_color=(0.96, 0.82, 0.74, 1.0),
    hair_color=(0.35, 0.22, 0.14, 1.0),
    cloth_top_color=(0.18, 0.55, 0.82, 1.0),
    cloth_bottom_color=(0.15, 0.25, 0.45, 1.0),
    shoe_color=(0.85, 0.25, 0.22, 1.0),
    seed=0
):
    """
    『どうぶつの森』風デフォルメ3Dキャラクター統合生成
    前髪・後ろ髪を完全独立分離パーツ化（耳めり込み解消 ＆ 着せ替え自由度向上）
    体（Body）を親（Root）として各パーツを親子付けし、マテリアルを一括適用
    """
    from ..materials.character_shaders import create_chibi_character_shader

    # 1. 幾何学パラメータ計算
    head_height = total_height / head_ratio
    body_height = total_height - head_height
    head_center_z = body_height + head_height * 0.38
    head_size = (head_height * 0.95, head_height * 0.85, head_height * 0.80)

    # hair_style プリセットからのフォールバック分解
    if hair_front is None or hair_back is None:
        style = hair_style or "SHORT"
        if style in ("SHORT", "SHORT_MESSY", "CENTER_PART", "MUSHROOM"):
            hair_front = style
            hair_back = "SHORT_NAPE"
        elif style == "BOB":
            hair_front = "SHORT"
            hair_back = "BOB"
        elif style == "TWINTAILS":
            hair_front = "SHORT"
            hair_back = "TWINTAILS"
        elif style == "BRAIDS":
            hair_front = "SHORT"
            hair_back = "BRAIDS"
        elif style == "PONYTAIL":
            hair_front = "SHORT"
            hair_back = "PONYTAIL"
        elif style == "TOPKNOT":
            hair_front = "CENTER_PART"
            hair_back = "TOPKNOT"
        elif style == "SPIKY":
            hair_front = "SHORT_MESSY"
            hair_back = "SPIKY"
        elif style == "WAVY_LONG":
            hair_front = "SHORT"
            hair_back = "WAVY_LONG"
        elif style == "AFRO":
            hair_front = "NONE"
            hair_back = "AFRO"

    # 2. 各パーツメッシュ生成
    body_obj = build_chibi_body_mesh(context, f"{name}_Body", gender, head_ratio, total_height)
    head_obj = build_chibi_head_mesh(context, f"{name}_Head", (0, 0, head_center_z), head_size)
    ears_obj = build_chibi_ears_mesh(context, f"{name}_Ears", (0, 0, head_center_z), head_size)
    eyes_obj = build_chibi_eyes_mesh(context, f"{name}_Eyes", eye_style, eye_scale, (0, 0, head_center_z), head_size)
    eyebrow_obj = build_chibi_eyebrows_mesh(context, f"{name}_Eyebrows", eyebrow_style, (0, 0, head_center_z), head_size)
    nose_obj = build_chibi_nose_mesh(context, f"{name}_Nose", (0, 0, head_center_z), head_size)

    # 前髪・後ろ髪の独立生成
    hair_front_obj = build_chibi_hair_front_mesh(context, f"{name}_Hair_Front", hair_front, (0, 0, head_center_z), head_size)
    hair_back_obj = build_chibi_hair_back_mesh(context, f"{name}_Hair_Back", hair_back, (0, 0, head_center_z), head_size)

    outfit_obj = build_chibi_outfit_mesh(context, f"{name}_Outfit", gender, outfit_type, 0.05, body_height)
    shoes_obj = build_chibi_shoes_mesh(context, f"{name}_Shoes")
    acc_obj = build_chibi_accessories_mesh(context, f"{name}_Accessory", accessory, (0, 0, head_center_z), head_size)

    # 3. マテリアルの生成と適用
    mat_skin = create_chibi_character_shader(f"{name}_Skin_Mat", "SKIN", skin_color, 0.6, seed)
    mat_hair = create_chibi_character_shader(f"{name}_Hair_Mat", "HAIR", hair_color, 0.45, seed)
    mat_top = create_chibi_character_shader(f"{name}_ClothTop_Mat", "CLOTH_TOP", cloth_top_color, 0.7, seed, pattern=pattern)
    mat_button = create_chibi_character_shader(f"{name}_Button_Mat", "BUTTON", (0.88, 0.80, 0.45, 1.0), 0.3, seed)
    mat_eye = create_chibi_character_shader(f"{name}_Eye_Mat", "EYE", (0.12, 0.12, 0.14, 1.0), 0.15, seed)
    mat_eye_hl = create_chibi_character_shader(f"{name}_Eye_Highlight_Mat", "EYE_HIGHLIGHT", (1.0, 1.0, 1.0, 1.0), 0.05, seed)
    mat_eyebrow = create_chibi_character_shader(f"{name}_Eyebrow_Mat", "EYEBROW", hair_color, 0.55, seed)
    mat_nose = create_chibi_character_shader(f"{name}_Nose_Mat", "FACE_FEATURE", (skin_color[0]*0.9, skin_color[1]*0.75, skin_color[2]*0.7, 1.0), 0.5, seed)
    
    # Unity / Unreal Engine の足音・サーフェス判定用スロット
    mat_footstep = create_chibi_character_shader(f"{name}_Footstep_Surface_Mat", "FOOTSTEP_SURFACE", (0.2, 0.2, 0.2, 1.0), 0.85, seed)
    mat_shoe = create_chibi_character_shader(f"{name}_Shoe_Mat", "CLOTH_BOTTOM", shoe_color, 0.5, seed)

    # マテリアル割り当て
    body_obj.data.materials.append(mat_skin)
    head_obj.data.materials.append(mat_skin)
    ears_obj.data.materials.append(mat_skin)
    if hair_front_obj:
        hair_front_obj.data.materials.append(mat_hair)
    if hair_back_obj:
        hair_back_obj.data.materials.append(mat_hair)

    outfit_obj.data.materials.append(mat_top)
    outfit_obj.data.materials.append(mat_button)  # スロット1: 衣装装飾ボタン（オーバーオール留め具・コート・Tシャツ等）
    eyes_obj.data.materials.append(mat_eye)
    eyes_obj.data.materials.append(mat_eye_hl)
    if eyebrow_obj:
        eyebrow_obj.data.materials.append(mat_eyebrow)
    nose_obj.data.materials.append(mat_nose)

    # 靴にはアッパー用と足音判定用（Footstep）の2スロットを確実に付与
    shoes_obj.data.materials.append(mat_shoe)
    shoes_obj.data.materials.append(mat_footstep)

    # アクセサリーのマテリアル
    if acc_obj:
        if accessory == "ROUND_GLASSES":
            mat_acc = create_chibi_character_shader(f"{name}_Glasses_Mat", "GLASSES", (0.15, 0.15, 0.18, 1.0), 0.25, seed)
            acc_obj.data.materials.append(mat_acc)
        elif accessory == "CHEEK_BLUSH":
            mat_acc = create_chibi_character_shader(f"{name}_Blush_Mat", "BLUSH", (0.95, 0.45, 0.55, 1.0), 0.8, seed)
            acc_obj.data.materials.append(mat_acc)

    # 4. 親子付け（Body を Root として階層化）
    child_parts = [head_obj, ears_obj, eyes_obj, nose_obj, outfit_obj, shoes_obj]
    if hair_front_obj:
        child_parts.append(hair_front_obj)
    if hair_back_obj:
        child_parts.append(hair_back_obj)
    if eyebrow_obj:
        child_parts.append(eyebrow_obj)
    if acc_obj:
        child_parts.append(acc_obj)

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
