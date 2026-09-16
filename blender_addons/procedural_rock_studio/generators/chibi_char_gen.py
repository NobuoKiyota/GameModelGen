import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler


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
    """
    マスター2D三面図（human_boy_2D / human_girl_2D）に完全準拠した愛らしいチビ頭部
    - ぷにっと丸いチーク（頬）と愛らしく丸みのある顎先（尖り解消）
    - 側面図S字プロファイル（額 → 鼻根の窪み → ツンと出るボタンノーズ → 人中）
    - 眼窩（アイホール）の窪みにより、奥の眼球（白目＋瞳）が自然に収まる本格アニメ構造
    - 後頭部の豊かな丸み（奥行き/高さ比率 ≒ 1.05）
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=20, radius=0.5)
    sx, sy, sz = head_size[0], head_size[1], head_size[2]
    for v in bm.verts:
        norm_z = v.co.z / 0.5  # -1.0(顎先) ~ +1.0(頭頂)
        norm_y = v.co.y / 0.5  # -1.0(顔正面) ~ +1.0(後頭部)
        norm_x = v.co.x / 0.5  # -1.0(左) ~ +1.0(右)

        # 1. 頬（チーク）の愛らしい丸みふくらみ（目の斜め下・耳の前）
        if -0.45 < norm_z < 0.15 and norm_y < 0.10:
            z_w = max(0.0, 1.0 - ((norm_z - (-0.10)) / 0.30) ** 2)
            cheek_y = max(0.0, -norm_y) * z_w * 0.14
            cheek_x = abs(norm_x) * z_w * 0.10
            v.co.y -= cheek_y * 0.45
            v.co.x *= (1.0 + cheek_x)

        # 2. 顎先（Chin）の丸み形成（尖らせず、三面図通りのふっくらした愛らしい顎）
        if norm_z < -0.25:
            chin_depth = min(1.0, (-norm_z - 0.25) / 0.75)
            # 顎先は適度な幅と丸みを保つ
            v.co.x *= (1.0 - chin_depth * 0.10)
            if norm_y < 0:
                v.co.y *= (1.0 - chin_depth * 0.06)
            else:
                # 顎裏（首元への移行ライン）
                v.co.z += chin_depth * norm_y * 0.05
                v.co.y *= (1.0 - chin_depth * 0.15)

        # 3. 側面図S字プロファイル（鼻根の窪み ＆ 滑らかなボタンノーズ）
        # 正面中央 (|norm_x| < 0.16 かつ norm_y < -0.05)
        if abs(norm_x) < 0.16 and norm_y < -0.05:
            x_falloff = max(0.0, 1.0 - (abs(norm_x) / 0.16) ** 2)
            # A. 鼻根の緩やかな窪み (norm_z: -0.12 ~ 0.04、目の上端〜眉間)
            if -0.12 < norm_z < 0.04:
                bridge_w = max(0.0, 1.0 - ((norm_z - (-0.04)) / 0.08) ** 2)
                v.co.y += bridge_w * x_falloff * 0.015
            # B. 小さな丸いボタンノーズのツンとした突起 (norm_z: -0.34 ~ -0.16、中心 -0.25)
            if -0.34 < norm_z < -0.16:
                nose_w = max(0.0, 1.0 - ((norm_z - (-0.25)) / 0.09) ** 2)
                v.co.y -= nose_w * x_falloff * 0.028
                v.co.z += nose_w * x_falloff * 0.005

        # 4. 眼窩（アイホール）の自然なくぼみ
        # 目の幾何位置に完全連動 (中心 |norm_x|: 0.44, norm_z: -0.175)
        eye_cx = 0.44
        eye_cz = -0.175
        if 0.22 < abs(norm_x) < 0.66 and -0.36 < norm_z < 0.02 and norm_y < -0.10:
            dx = (abs(norm_x) - eye_cx) / 0.22
            dz = (norm_z - eye_cz) / 0.18
            dist_sq = dx * dx + dz * dz
            if dist_sq < 1.0:
                socket_w = (1.0 - dist_sq) * max(0.0, -norm_y) * 0.018
                v.co.y += socket_w

        # 全体スケール適用
        y_fac = 1.0 + max(0.0, -norm_z) * 0.05
        x_fac = 1.0 + max(0.0, -norm_z) * 0.05
        v.co.x *= sx * x_fac
        v.co.y *= sy * y_fac
        v.co.z *= sz
        v.co += Vector(head_center)

    bm.to_mesh(mesh)
    bm.free()

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
    ear_pos = Vector((head_size[0] * 0.50, -0.02, head_center[2] - 0.02))
    res = bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.065)
    for v in res['verts']:
        v.co.x *= 0.35
        v.co.y *= 0.9
        v.co += ear_pos

    bm.to_mesh(mesh)
    bm.free()

    mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
    mod_mirror.use_axis[0] = True

    return obj


def build_chibi_eyes_mesh(context, name="Chibi_Eyes", gender="BOY", eye_style="OVAL", eye_scale=1.0, head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40), head_obj=None):
    """
    マスター2D三面図に完全準拠した本格アニメ多層眼球メッシュ
    - スロット 0: 白目（Sclera）瞳の輪郭を包むアイホール形状（横幅1.14倍、高さ1.05倍）
    - スロット 1: 瞳・虹彩（Iris / Pupil）大きな愛らしい縦長オーバル瞳（白目の手前）
    - スロット 2: ハイライト（Highlight）左上メイン光＋右下セカンド光
    - スロット 3: 上まつ毛・アイライン（Eyelash）女の子は目尻に2本の可愛いハネ付き
    - 頭部実メッシュ（チーク・アイホール適用後）へのレイキャスト吸着による完璧な曲面追従
    - 表情差分シェイプキー（Basis, Blink, Smile, Wide, Squint）完全連動
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()

    # 三面図の黄金比率（目幅 : 目と目の間 : 目幅 ≒ 1 : 1 : 1）
    eye_x = head_size[0] * 0.220
    eye_z = head_center[2] - 0.035

    # 瞳のサイズ（三面図に即した大きな丸い縦長オーバル）
    rx = 0.036 * eye_scale
    if eye_style == "ROUND":
        rz = 0.038 * eye_scale
    elif eye_style == "DROOPY":
        rz = 0.044 * eye_scale
    elif eye_style == "CAT_EYE":
        rz = 0.042 * eye_scale
    elif eye_style == "SMILING":
        rz = 0.022 * eye_scale
    else:  # OVAL
        rz = 0.046 * eye_scale

    sx = head_size[0] * 0.5
    sy = head_size[1] * 0.5
    sz = head_size[2] * 0.5

    # 頭部メッシュ（Subsurf & チーク適用済み）の評価オブジェクト取得
    eval_head = None
    if head_obj:
        try:
            dg = context.evaluated_depsgraph_get()
            eval_head = head_obj.evaluated_get(dg)
        except Exception:
            eval_head = head_obj

    def get_surface_point(vx, vz, depth_offset=0.001):
        """頭部実メッシュ皮膚表面への高精度レイキャスト吸着"""
        wx = eye_x + vx
        wz = eye_z + vz
        if eval_head:
            ray_origin = Vector((wx, head_center[1] - 0.60, wz))
            ray_dir = Vector((0.0, 1.0, 0.0))
            hit, loc, norm, idx = eval_head.ray_cast(ray_origin, ray_dir)
            if hit:
                return loc + norm * depth_offset

        # フォールバック（楕円体計算）
        norm_x = wx / max(0.01, sx)
        norm_z = (wz - head_center[2]) / max(0.01, sz)
        y_fac = 1.0 + max(0.0, -norm_z) * 0.05
        rad_sq = max(0.02, 1.0 - norm_x * norm_x - norm_z * norm_z)
        wy = head_center[1] - math.sqrt(rad_sq) * sy * y_fac - depth_offset
        return Vector((wx, wy, wz))

    # 1. 🌟 白目メッシュ（Sclera: Slot 0）
    # 瞳の周囲を自然に縁取る横長形状
    sw = rx * 1.15
    sh = rz * 1.06
    res_sclera = bmesh.ops.create_circle(bm, cap_ends=True, radius=1.0, segments=20)
    for v in res_sclera['verts']:
        vx = v.co.x * sw
        vz = v.co.y * sh
        v.co = get_surface_point(vx, vz, depth_offset=0.0007)
    res_sclera_verts = set(res_sclera['verts'])

    # 2. 🌟 瞳メッシュ（Pupil / Iris: Slot 1）
    res_pupil = bmesh.ops.create_circle(bm, cap_ends=True, radius=1.0, segments=20)
    for v in res_pupil['verts']:
        vx = v.co.x * rx
        vz = v.co.y * rz
        if eye_style == "DROOPY":
            vz -= vx * 0.20
        elif eye_style == "CAT_EYE":
            vz += vx * 0.22
        v.co = get_surface_point(vx, vz, depth_offset=0.0016)
    res_pupil_verts = set(res_pupil['verts'])

    # 3. 🌟 ハイライト（Highlight: Slot 2）
    # 左上メインハイライト
    hl_ox = -rx * 0.32
    hl_oz = rz * 0.30
    hl_r1 = 0.011 * eye_scale
    res_hl1 = bmesh.ops.create_circle(bm, cap_ends=True, radius=1.0, segments=12)
    for v in res_hl1['verts']:
        vx = hl_ox + v.co.x * hl_r1
        vz = hl_oz + v.co.y * hl_r1
        v.co = get_surface_point(vx, vz, depth_offset=0.0025)

    # 右下セカンドハイライト（反射光）
    hl_ox2 = rx * 0.28
    hl_oz2 = -rz * 0.30
    hl_r2 = 0.0055 * eye_scale
    res_hl2 = bmesh.ops.create_circle(bm, cap_ends=True, radius=1.0, segments=10)
    for v in res_hl2['verts']:
        vx = hl_ox2 + v.co.x * hl_r2
        vz = hl_oz2 + v.co.y * hl_r2
        v.co = get_surface_point(vx, vz, depth_offset=0.0025)

    res_hl_verts = set(res_hl1['verts']) | set(res_hl2['verts'])

    # 4. 🌟 上まつ毛・アイライン（Eyelash: Slot 3）
    eyelash_faces = []
    eyelash_verts_bot = []
    eyelash_verts_top = []

    lash_segs = 10
    is_girl = (gender == "GIRL")

    for i in range(lash_segs + 1):
        t = i / lash_segs
        rel_x = -sw * 0.90 + t * (sw * 2.02)
        clamped_nx = max(-1.0, min(1.0, rel_x / max(0.001, sw)))
        arch_height = sh * math.sqrt(max(0.0, 1.0 - clamped_nx * clamped_nx))
        if eye_style == "DROOPY":
            arch_height -= rel_x * 0.18
        elif eye_style == "CAT_EYE":
            arch_height += rel_x * 0.22

        wing_lift = 0.0
        if is_girl and t > 0.65:
            w_factor = (t - 0.65) / 0.35
            wing_lift = (w_factor ** 1.8) * (0.013 * eye_scale)

        base_z = arch_height + wing_lift
        lash_thick = (0.007 + t * 0.009) * eye_scale if is_girl else (0.006 + t * 0.005) * eye_scale

        p_bot = get_surface_point(rel_x, base_z, depth_offset=0.0034)
        v_bot = bm.verts.new(p_bot)
        eyelash_verts_bot.append(v_bot)

        p_top = get_surface_point(rel_x, base_z + lash_thick, depth_offset=0.0044)
        v_top = bm.verts.new(p_top)
        eyelash_verts_top.append(v_top)

    bm.verts.ensure_lookup_table()
    for i in range(lash_segs):
        f = bm.faces.new([
            eyelash_verts_bot[i],
            eyelash_verts_bot[i + 1],
            eyelash_verts_top[i + 1],
            eyelash_verts_top[i]
        ])
        eyelash_faces.append(f)

    # 女の子用の目尻2本目のハネ（セカンドウィング）
    if is_girl:
        wing_v1 = eyelash_verts_top[-1]
        wing_v2 = eyelash_verts_bot[-1]
        p_wing = get_surface_point(sw * 1.24, sh * 0.14, depth_offset=0.0038)
        wing_v3 = bm.verts.new(p_wing)
        f_wing = bm.faces.new([wing_v2, wing_v1, wing_v3])
        eyelash_faces.append(f_wing)

    # マテリアルインデックスの割り当て
    # 0: 白目 (EYE_SCLERA), 1: 瞳 (EYE), 2: ハイライト (EYE_HIGHLIGHT), 3: 上まつ毛 (EYELASH)
    for f in bm.faces:
        if f in eyelash_faces:
            f.material_index = 3
        elif any(v in res_hl_verts for v in f.verts):
            f.material_index = 2
        elif any(v in res_pupil_verts for v in f.verts):
            f.material_index = 1
        else:
            f.material_index = 0

    bm.to_mesh(mesh)
    bm.free()

    # 🌟 表情差分アニメーション用シェイプキー
    try:
        obj.shape_key_add(name="Basis", from_mix=False)

        # 1. Blink: まばたき
        sk_blink = obj.shape_key_add(name="Blink", from_mix=False)
        for pt in sk_blink.data:
            dx = pt.co.x - eye_x
            dz = pt.co.z - eye_z
            pt.co.z = eye_z - rz * 0.15 + dz * 0.05

        # 2. Smile: にっこり笑顔（瞳が薄くつぶれ、まつ毛が完璧な三日月アーチに）
        sk_smile = obj.shape_key_add(name="Smile", from_mix=False)
        for pt in sk_smile.data:
            dx = (pt.co.x - eye_x) / max(0.001, rx)
            arch = (1.0 - min(1.2, dx * dx)) * 0.015
            pt.co.z = eye_z + (pt.co.z - eye_z) * 0.10 + arch

        # 3. Wide: 驚き見開き
        sk_wide = obj.shape_key_add(name="Wide", from_mix=False)
        for pt in sk_wide.data:
            pt.co.x = eye_x + (pt.co.x - eye_x) * 1.15
            pt.co.z = eye_z + (pt.co.z - eye_z) * 1.15

        # 4. Squint: ジト目
        sk_squint = obj.shape_key_add(name="Squint", from_mix=False)
        for pt in sk_squint.data:
            dz = pt.co.z - eye_z
            if dz > 0:
                pt.co.z = eye_z + dz * 0.20
    except Exception:
        pass

    mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
    mod_mirror.use_axis[0] = True

    return obj


def build_chibi_mouth_mesh(context, name="Chibi_Mouth", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """
    アニメ調の小さくキュッと結んだ可愛いお口（リップパーツ）
    むえん氏の作例に合わせた自然な配置と表情シェイプキー
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    mouth_x = 0.0
    mouth_z = head_center[2] - 0.072  # 鼻の下、自然なリップライン

    norm_z = (mouth_z - head_center[2]) / (head_size[2] * 0.5)
    y_fac = 1.0 + max(0.0, -norm_z) * 0.06
    nz = (mouth_z - head_center[2]) / max(0.01, head_size[2] * 0.5)
    ny_sq = max(0.05, 1.0 - nz * nz)
    mouth_y = head_center[1] - math.sqrt(ny_sq) * 0.5 * head_size[1] * y_fac - 0.004
    mouth_pos = Vector((mouth_x, mouth_y, mouth_z))

    # リップライン生成（幅約 0.032m、中央がわずかに下がった愛らしい微笑みカーブ）
    mw = 0.016  # 片側半幅
    mouth_segs = 6
    v_top_list = []
    v_bot_list = []

    for i in range(mouth_segs + 1):
        t = (i / mouth_segs) * 2.0 - 1.0  # -1.0 ~ +1.0
        vx = t * mw
        arch = (1.0 - t * t) * (-0.0025)
        vy_curve = -(vx * vx) * 0.45

        v_top = bm.verts.new(mouth_pos + Vector((vx, vy_curve - 0.002, arch + 0.0035)))
        v_bot = bm.verts.new(mouth_pos + Vector((vx, vy_curve, arch - 0.0025)))
        v_top_list.append(v_top)
        v_bot_list.append(v_bot)

    bm.verts.ensure_lookup_table()
    for i in range(mouth_segs):
        bm.faces.new([
            v_bot_list[i],
            v_bot_list[i + 1],
            v_top_list[i + 1],
            v_top_list[i]
        ])

    bm.to_mesh(mesh)
    bm.free()

    # 口の表情差分シェイプキー
    try:
        obj.shape_key_add(name="Basis", from_mix=False)

        # 1. Smile: 口角がキュッと上がる
        sk_smile = obj.shape_key_add(name="Smile", from_mix=False)
        for pt in sk_smile.data:
            dx = pt.co.x / max(0.001, mw)
            smile_lift = (dx * dx) * 0.006
            pt.co.z += smile_lift
            pt.co.x *= 1.15

        # 2. Open: お口を縦に開ける
        sk_open = obj.shape_key_add(name="Open", from_mix=False)
        for pt in sk_open.data:
            if pt.co.z > mouth_pos.z:
                pt.co.z += 0.006
            else:
                pt.co.z -= 0.010

        # 3. Pout: むすっと不満口
        sk_pout = obj.shape_key_add(name="Pout", from_mix=False)
        for pt in sk_pout.data:
            dx = pt.co.x / max(0.001, mw)
            pt.co.z -= (dx * dx) * 0.0045
    except Exception:
        pass

    mod_sol = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_sol.thickness = 0.005
    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 1

    return obj


def build_chibi_eyebrows_mesh(context, name="Chibi_Eyebrows", eyebrow_style="ARCH", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """
    愛らしい眉毛メッシュ（Mirror対称 ＋ 頭部曲面自動フィット）
    """
    if eyebrow_style == "NONE":
        return None

    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    brow_x = head_size[0] * 0.205
    brow_z = head_center[2] + 0.032  # まつ毛の少し上、前髪の下からチラッと見える愛らしい位置

    norm_z = (brow_z - head_center[2]) / (head_size[2] * 0.5)
    y_fac = 1.0 + max(0.0, -norm_z) * 0.06
    x_fac = 1.0 + max(0.0, -norm_z) * 0.06
    nx = brow_x / max(0.01, head_size[0] * x_fac * 0.5)
    nz = (brow_z - head_center[2]) / max(0.01, head_size[2] * 0.5)
    ny_sq = max(0.05, 1.0 - nx * nx - nz * nz)
    brow_y = head_center[1] - math.sqrt(ny_sq) * 0.5 * head_size[1] * y_fac - 0.005
    brow_pos = Vector((brow_x, brow_y, brow_z))

    if eyebrow_style == "DOT":
        r = 0.016
        res = bmesh.ops.create_circle(bm, cap_ends=True, radius=r, segments=14)
        for v in res['verts']:
            v.co = Vector((v.co.x, -(v.co.x*v.co.x + v.co.y*v.co.y)*0.5, v.co.y)) + brow_pos

    elif eyebrow_style == "STRAIGHT":
        bw = 0.030
        bh = 0.008
        res = bmesh.ops.create_cube(bm, size=1.0)
        for v in res['verts']:
            vx = v.co.x * bw * 2.0
            vz = v.co.z * bh * 2.0
            vy = v.co.y * 0.006
            v.co = Vector((vx, vy, vz)) + brow_pos

    else:
        # ARCH: なだらかアーチ眉
        res = bmesh.ops.create_circle(bm, cap_ends=True, radius=1.0, segments=16)
        rx = 0.032
        rz = 0.009
        for v in res['verts']:
            vx = v.co.x * rx
            norm_vx = vx / rx
            arch_z = (1.0 - norm_vx * norm_vx) * 0.009 - norm_vx * 0.003
            vz = v.co.y * rz + arch_z
            vy = -(vx * vx + vz * vz) * 0.5
            v.co = Vector((vx, vy, vz)) + brow_pos

    bm.to_mesh(mesh)
    bm.free()

    mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
    mod_mirror.use_axis[0] = True
    mod_sol = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_sol.thickness = 0.005
    mod_sol.offset = 1.0

    return obj


def build_chibi_nose_mesh(context, name="Chibi_Nose", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """
    マスター三面図に即した、頭部メッシュの突起に自然に重なる繊細で愛らしい小鼻アクセント
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    # 頭部メッシュのボタンノーズ突起中心 (norm_z = -0.25) に完全一致
    nose_z = head_center[2] - 0.050
    norm_z = (nose_z - head_center[2]) / (head_size[2] * 0.5)
    y_fac = 1.0 + max(0.0, -norm_z) * 0.05
    nz = (nose_z - head_center[2]) / max(0.01, head_size[2] * 0.5)
    ny_sq = max(0.05, 1.0 - nz * nz)
    # 頭部の鼻先突起 (-0.028) の前面に乗るY位置
    nose_y = head_center[1] - math.sqrt(ny_sq) * 0.5 * head_size[1] * y_fac - 0.022
    nose_pos = Vector((0.0, nose_y, nose_z))

    # 丸みのある愛らしいボタンノーズ（UV半球）
    res = bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.011)
    for v in res['verts']:
        vx = v.co.x * 1.05
        vy = min(0.001, v.co.y * 0.70)
        vz = v.co.z * 0.95 + max(0.0, -vy) * 0.15
        v.co = Vector((vx, vy, vz)) + nose_pos

    bm.to_mesh(mesh)
    bm.free()

    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 1

    return obj


def calc_front_cutoff(norm_x, style):
    if style == "MUSHROOM":
        return 0.12 + 0.02 * math.cos(norm_x * 2.0 * math.pi)
    elif style == "CENTER_PART":
        return 0.20 - 0.10 * math.cos(norm_x * math.pi * 0.85)
    elif style == "SHORT_MESSY":
        wave1 = math.sin((norm_x + 0.15) * 3.5 * math.pi) * 0.030
        wave2 = math.cos((norm_x - 0.20) * 2.0 * math.pi) * 0.020
        return 0.13 + 0.04 * norm_x + wave1 + wave2
    else:  # SHORT 等
        fringe = math.sin((norm_x - 0.12) * 3.0 * math.pi) * 0.025 + math.cos(norm_x * 1.8 * math.pi) * 0.018
        return 0.13 + 0.03 * norm_x + fringe


def build_chibi_hair_front_mesh(context, name="Chibi_Hair_Front", front_style="SHORT", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """
    独立した前髪パーツメッシュ生成
    SHORT, SHORT_MESSY, CENTER_PART, MUSHROOM, NONE
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
    どうぶつの森風 単一統合ヘアスタイルメッシュ
    前後の継ぎ目・隙間のない一体成型 ＋ 耳逃げ穴クリアランスによる自然な耳の露出
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    hc = Vector(head_center)
    hsx, hsy, hsz = head_size

    if hair_style == "AFRO":
        res_afro = bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=22, radius=0.32)
        afro_p = hc + Vector((0.0, 0.02, hsz * 0.15))
        afro_del = []
        for v in res_afro['verts']:
            pos = (v.co * 1.12) + afro_p
            if pos.y < hc.y - 0.05 and pos.z < hc.z + 0.08:
                afro_del.append(v)
            else:
                bump = math.sin(v.co.x * 35.0) * math.cos(v.co.z * 35.0) * 0.008
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

            # 1. 前髪生え際カット（Y < 0.0）
            if norm_y < 0.0:
                cutoff = calc_front_cutoff(norm_x, hair_style)
                if abs(norm_x) > 0.32:
                    cutoff -= (abs(norm_x) - 0.32) * 1.10
                if norm_z < cutoff:
                    del_verts.append(v)
                    continue

            # 2. 耳の逃げ穴（耳根元の最小限クリアランスで側頭部の露出を完全に防止）
            if abs(norm_x) > 0.46 and -0.02 <= norm_y <= 0.05 and -0.24 < norm_z < -0.06:
                del_verts.append(v)
                continue

            # 3. 襟足カット（Y >= 0.0）
            if norm_y >= 0.0:
                if hair_style == "WAVY_LONG":
                    limit_z = -0.58
                elif hair_style == "BOB":
                    limit_z = -0.26 - 0.04 * (1.0 - abs(norm_x))
                else:  # SHORT, SHORT_MESSY, MUSHROOM, TWINTAILS, PONYTAIL 等
                    center_depth = 1.0 - min(1.0, abs(norm_x) * 1.1)
                    limit_z = -0.32 - 0.14 * center_depth
                if norm_z < limit_z:
                    del_verts.append(v)

        bmesh.ops.delete(bm, geom=del_verts, context='VERTS')

        # 頭部サイズにフィット＆ふっくらボリューム（前髪は額に吸い付き、側頭・後頭・頭頂は豊かに）
        for v in bm.verts:
            norm_z = v.co.z / 0.5
            norm_y = v.co.y / 0.5
            y_fac = 1.0 + max(0.0, -norm_z) * 0.05
            x_fac = 1.0 + max(0.0, -norm_z) * 0.06
            front_snug = 1.025 if norm_y < 0 else 1.07
            vx = v.co.x * hsx * x_fac * 1.06
            vy = v.co.y * hsy * y_fac * front_snug
            vz = v.co.z * hsz * 1.06
            v.co = Vector((vx, vy, vz)) + hc

        # サイドパーツ・装飾（ツインテール、ポニーテール、三つ編み、スパイキー、トップノット）
        if hair_style == "TWINTAILS":
            for side in (-1.0, 1.0):
                res_bun = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=0.105)
                bun_p = hc + Vector((side * hsx * 0.58, 0.02, hsz * 0.20))
                for v in res_bun['verts']:
                    v.co.x *= 0.95
                    v.co += bun_p

        elif hair_style == "BRAIDS":
            for side in (-1.0, 1.0):
                braid_p = hc + Vector((side * hsx * 0.44, 0.01, -hsz * 0.12))
                for i in range(4):
                    r_seg = 0.042 - i * 0.006
                    res_seg = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=r_seg)
                    seg_offset = Vector((side * 0.01 * math.sin(i * 1.5), 0.0, -i * 0.045))
                    for v in res_seg['verts']:
                        v.co += braid_p + seg_offset

        elif hair_style == "TOPKNOT":
            res_knot = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=0.10)
            knot_p = hc + Vector((0.0, 0.02, hsz * 0.58))
            for v in res_knot['verts']:
                v.co.z *= 0.85
                v.co += knot_p

        elif hair_style == "PONYTAIL":
            tie_p = hc + Vector((0.0, hsy * 0.48, hsz * 0.22))
            res_tie = bmesh.ops.create_cone(bm, cap_ends=False, segments=12, radius1=0.038, radius2=0.038, depth=0.025)
            for v in res_tie['verts']:
                v.co = Vector((v.co.x, v.co.z, v.co.y)) + tie_p

            res_tail = bmesh.ops.create_cone(bm, cap_ends=True, segments=14, radius1=0.075, radius2=0.025, depth=0.22)
            for v in res_tail['verts']:
                vx = v.co.x
                vy = v.co.z * 0.65 + v.co.y * 0.75 + 0.06
                vz = -v.co.z * 0.75 + v.co.y * 0.65 - 0.04
                v.co = Vector((vx, vy, vz)) + tie_p

        elif hair_style == "SPIKY":
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

        elif hair_style == "WAVY_LONG":
            for v in bm.verts:
                if v.co.z < hc.z + 0.02:
                    wave_x = math.sin((v.co.z - hc.z) * 24.0) * 0.014
                    wave_y = math.cos((v.co.z - hc.z) * 24.0) * 0.010
                    v.co.x += wave_x
                    v.co.y += wave_y
                    v.co.x = hc.x + (v.co.x - hc.x) * 1.10

        elif hair_style == "BOB":
            for v in bm.verts:
                if v.co.z < hc.z + 0.05:
                    v.co.x *= 1.10
                    v.co.y *= 1.06

    bm.to_mesh(mesh)
    bm.free()

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
        # 釣鐘型ワンピース（丸い撫で肩・ラウンドショルダー ＋ Aラインスカート ＋ 丸い袖）
        dress_z = base_z + leg_len * 0.35
        dress_top_z = base_z + leg_len + torso_len * 0.96
        depth = dress_top_z - dress_z
        res_d = bmesh.ops.create_cone(
            bm, cap_ends=False, segments=24,
            radius1=0.255, radius2=0.175, depth=depth
        )
        for v in res_d['verts']:
            v.co.z += dress_z + depth * 0.5
            v.co.y *= 0.90
            # 撫で肩カーブ（首元が高く、肩先に向かってなだらかに下がる）
            if v.co.z > dress_top_z - 0.10:
                fac = (v.co.z - (dress_top_z - 0.10)) / 0.10
                drop = ((abs(v.co.x) / 0.175) ** 1.8) * 0.038 * fac
                v.co.z -= drop
                if abs(v.co.x) > 0.11:
                    v.co.x *= (1.0 - (abs(v.co.x) - 0.11) * 0.35 * fac)

        # 丸い袖（フレンチスリーブ／パフスリーブ：肩から腕の接続を滑らかに包み込み、脇のギザギザをカバー）
        sleeve_len = 0.085
        for side in (-1.0, 1.0):
            sh_x = side * 0.120
            center_x = sh_x + side * (sleeve_len * 0.5 * sin_theta)
            center_z = sh_z - (sleeve_len * 0.5 * cos_theta) + 0.005
            res_sl = bmesh.ops.create_cone(bm, cap_ends=False, segments=16, radius1=0.088, radius2=0.102, depth=sleeve_len)
            for v in res_sl['verts']:
                vx, vy, vz = v.co.x, v.co.y, v.co.z
                if vz > 0:
                    vx *= 0.80
                    vy *= 0.85
                v.co.x = vx * cos_theta - side * vz * sin_theta + center_x
                v.co.y = vy * 0.92 - 0.01
                v.co.z = side * vx * sin_theta + vz * cos_theta + center_z
                if v.co.z > sh_z - 0.03 and abs(v.co.x) > 0.12:
                    v.co.z -= (abs(v.co.x) - 0.12) * 0.32

    elif outfit_type == "KIMONO":
        # 和服・浴衣（ストレートに足元まで伸びる裾 ＋ 角型振袖 ＋ 丸い撫で肩）
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
            if v.co.z > kimono_top_z - 0.08:
                fac = (v.co.z - (kimono_top_z - 0.08)) / 0.08
                v.co.z -= ((abs(v.co.x) / 0.175) ** 1.8) * 0.030 * fac

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
        # サロペット・オーバーオール（胴体 ＋ 肩紐サスペンダー ＋ 丸い撫で肩）
        t_z = base_z + leg_len * 0.25
        t_top_z = base_z + leg_len + torso_len * 0.93
        depth = t_top_z - t_z
        res_ov = bmesh.ops.create_cone(bm, cap_ends=False, segments=20, radius1=0.22, radius2=0.18, depth=depth)
        for v in res_ov['verts']:
            v.co.z += t_z + depth * 0.5
            v.co.y *= 0.89
            if v.co.z > t_top_z - 0.08:
                fac = (v.co.z - (t_top_z - 0.08)) / 0.08
                v.co.z -= ((abs(v.co.x) / 0.18) ** 1.8) * 0.032 * fac

        # 肩紐サスペンダー（左右の帯）
        for side in (-1.0, 1.0):
            res_strap = bmesh.ops.create_cube(bm, size=1.0)
            for v in res_strap['verts']:
                v.co.x = v.co.x * 0.025 + (side * 0.075)
                v.co.y = v.co.y * 0.15 - 0.01
                v.co.z = v.co.z * 0.02 + (base_z + leg_len + torso_len * 0.92)

    elif outfit_type == "HOODIE":
        # パーカー（少しゆったり胴体 ＋ 長袖 ＋ 背中大型立体フード ＋ 丸い撫で肩）
        t_z = base_z + leg_len * 0.55
        t_top_z = base_z + leg_len + torso_len * 0.96
        depth = t_top_z - t_z
        res_t = bmesh.ops.create_cone(bm, cap_ends=False, segments=20, radius1=0.225, radius2=0.18, depth=depth)
        for v in res_t['verts']:
            v.co.z += t_z + depth * 0.5
            v.co.y *= 0.91
            # 撫で肩カーブ
            if v.co.z > t_top_z - 0.08:
                fac = (v.co.z - (t_top_z - 0.08)) / 0.08
                v.co.z -= ((abs(v.co.x) / 0.18) ** 1.8) * 0.035 * fac
                if abs(v.co.x) > 0.12:
                    v.co.x *= (1.0 - (abs(v.co.x) - 0.12) * 0.32 * fac)

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

        # 背中の大型立体フード（首の後ろから背中にふっくら垂れ下がった存在感のある袋状フード）
        res_hood = bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=14, radius=0.15)
        hood_p = Vector((0.0, 0.145, base_z + leg_len + torso_len * 0.78))
        for v in res_hood['verts']:
            v.co.x *= 1.35  # 幅 0.28m
            v.co.y *= 1.05  # 奥行 0.16m
            v.co.z *= 1.25  # 高さ 0.22m
            if v.co.y < 0:
                v.co.y *= 0.65
            v.co += hood_p

        # フードの折り返し襟・開口部リップ（首周りの立体的な布の厚み）
        res_lip = bmesh.ops.create_cone(bm, cap_ends=False, segments=18, radius1=0.14, radius2=0.11, depth=0.06)
        lip_p = Vector((0.0, 0.06, base_z + leg_len + torso_len * 0.92))
        for v in res_lip['verts']:
            v.co.x *= 1.15
            v.co.y *= 1.20
            v.co += lip_p

        # フードのドローコード（胸元に垂れる2本の紐）
        for side in (-1.0, 1.0):
            res_str = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.005, radius2=0.004, depth=0.09)
            str_p = Vector((side * 0.045, -0.162, base_z + leg_len + torso_len * 0.84))
            for v in res_str['verts']:
                v.co += str_p

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
            if v.co.z > c_top_z - 0.08:
                fac = (v.co.z - (c_top_z - 0.08)) / 0.08
                v.co.z -= ((abs(v.co.x) / 0.185) ** 1.8) * 0.035 * fac
                if abs(v.co.x) > 0.12:
                    v.co.x *= (1.0 - (abs(v.co.x) - 0.12) * 0.32 * fac)

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
            if v.co.z > t_top_z - 0.08:
                fac = (v.co.z - (t_top_z - 0.08)) / 0.08
                v.co.z -= ((abs(v.co.x) / 0.18) ** 1.8) * 0.035 * fac
                if abs(v.co.x) > 0.12:
                    v.co.x *= (1.0 - (abs(v.co.x) - 0.12) * 0.32 * fac)

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
        r_lens = 0.052
        pipe_r = 0.0052

        # 1. 滑らかな丸パイプ（トーラス）による左右のレンズリム
        for side in (-1.0, 1.0):
            center = Vector((side * eye_x, glasses_y, eye_z))
            yaw = -side * 0.09  # 顔の球面に沿ったラップ角（約5.2度）
            cos_y = math.cos(yaw)
            sin_y = math.sin(yaw)

            major_segs = 22
            minor_segs = 8
            grid = []
            for i in range(major_segs):
                theta = 2.0 * math.pi * i / major_segs
                ring = []
                for j in range(minor_segs):
                    phi = 2.0 * math.pi * j / minor_segs
                    r = r_lens + pipe_r * math.cos(phi)
                    lx = r * math.cos(theta)
                    lz = r * math.sin(theta)
                    ly = pipe_r * math.sin(phi)
                    rx = lx * cos_y + ly * sin_y
                    ry = -lx * sin_y + ly * cos_y
                    rz = lz
                    v_pos = Vector((rx, ry, rz)) + center
                    ring.append(bm.verts.new(v_pos))
                grid.append(ring)

            for i in range(major_segs):
                i_next = (i + 1) % major_segs
                for j in range(minor_segs):
                    j_next = (j + 1) % minor_segs
                    bm.faces.new((grid[i][j], grid[i_next][j], grid[i_next][j_next], grid[i][j_next]))

            # 2. テンプル（つる: リム外端から耳元へ自然に伸びる滑らかなパイプ）
            start_x = side * (eye_x + r_lens * 0.94)
            start_p = Vector((start_x, glasses_y + 0.008, eye_z + 0.004))
            end_p = Vector((side * (hsx * 0.44), hc.y + 0.02, hc.z - 0.015))
            t_depth = (end_p - start_p).length
            t_dir = (end_p - start_p).normalized()

            res_tmp = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.0045, radius2=0.0040, depth=t_depth)
            mid_p = (start_p + end_p) * 0.5
            rot_quat = Vector((0.0, 0.0, 1.0)).rotation_difference(t_dir)
            for v in res_tmp['verts']:
                v.co = rot_quat @ v.co + mid_p

        # 3. ブリッジ（鼻の上の滑らかなアーチ型パイプ）
        brg_width = (eye_x - r_lens * 0.90) * 2.0
        res_brg = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.0048, radius2=0.0048, depth=brg_width)
        rot_brg = Euler((0.0, math.pi * 0.5, 0.0)).to_matrix()
        for v in res_brg['verts']:
            # X軸に沿って配置し、中央部を前・上にアーチさせる
            v.co = rot_brg @ v.co
            arch_fac = max(0.0, 1.0 - (abs(v.co.x) / (brg_width * 0.5)) ** 2)
            v.co.z += arch_fac * 0.007 + eye_z + 0.006
            v.co.y += -arch_fac * 0.005 + glasses_y - 0.002

        bm.to_mesh(mesh)
        bm.free()

        mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
        mod_sub.levels = 1
        mod_sub.render_levels = 1

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
    # アニメ調の小顔・黄金比率（横幅を適度に引き締めて美しいセルルック輪郭に）
    head_size = (head_height * 0.84, head_height * 0.82, head_height * 0.80)

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
    eyes_obj = build_chibi_eyes_mesh(context, f"{name}_Eyes", gender, eye_style, eye_scale, (0, 0, head_center_z), head_size, head_obj=head_obj)
    eyebrow_obj = build_chibi_eyebrows_mesh(context, f"{name}_Eyebrows", eyebrow_style, (0, 0, head_center_z), head_size)
    nose_obj = build_chibi_nose_mesh(context, f"{name}_Nose", (0, 0, head_center_z), head_size)
    mouth_obj = build_chibi_mouth_mesh(context, f"{name}_Mouth", (0, 0, head_center_z), head_size)

    # 単一統合ヘアスタイルメッシュ生成（継ぎ目なし・耳逃げ穴クリアランス）
    hair_obj = build_chibi_hair_mesh(context, f"{name}_Hair", gender, hair_style, (0, 0, head_center_z), head_size)

    outfit_obj = build_chibi_outfit_mesh(context, f"{name}_Outfit", gender, outfit_type, 0.05, body_height)
    shoes_obj = build_chibi_shoes_mesh(context, f"{name}_Shoes")
    acc_obj = build_chibi_accessories_mesh(context, f"{name}_Accessory", accessory, (0, 0, head_center_z), head_size)

    # 3. マテリアルの生成と適用
    mat_skin = create_chibi_character_shader(f"{name}_Skin_Mat", "SKIN", skin_color, 0.6, seed)
    mat_hair = create_chibi_character_shader(f"{name}_Hair_Mat", "HAIR", hair_color, 0.45, seed)
    mat_top = create_chibi_character_shader(f"{name}_ClothTop_Mat", "CLOTH_TOP", cloth_top_color, 0.7, seed, pattern=pattern)
    mat_button = create_chibi_character_shader(f"{name}_Button_Mat", "BUTTON", (0.88, 0.80, 0.45, 1.0), 0.3, seed)
    
    # 三面図に忠実な瞳カラー（男の子: ディープエスプレッソ、女の子: 鮮やかなリッチアンバー）
    eye_base_color = (0.12, 0.08, 0.06, 1.0) if gender == "BOY" else (0.68, 0.36, 0.12, 1.0)
    mat_sclera = create_chibi_character_shader(f"{name}_Sclera_Mat", "EYE_SCLERA", (0.98, 0.98, 0.98, 1.0), 0.15, seed)
    mat_eye = create_chibi_character_shader(f"{name}_Eye_Mat", "EYE", eye_base_color, 0.10, seed)
    mat_eye_hl = create_chibi_character_shader(f"{name}_Eye_Highlight_Mat", "EYE_HIGHLIGHT", (1.0, 1.0, 1.0, 1.0), 0.02, seed)
    mat_eyelash = create_chibi_character_shader(f"{name}_Eyelash_Mat", "EYELASH", (0.08, 0.06, 0.07, 1.0), 0.30, seed)
    mat_eyebrow = create_chibi_character_shader(f"{name}_Eyebrow_Mat", "EYEBROW", hair_color, 0.55, seed)
    mat_nose = create_chibi_character_shader(f"{name}_Nose_Mat", "FACE_FEATURE", (skin_color[0]*0.92, skin_color[1]*0.72, skin_color[2]*0.68, 1.0), 0.40, seed)
    mat_mouth = create_chibi_character_shader(f"{name}_Mouth_Mat", "MOUTH", (0.85, 0.32, 0.38, 1.0), 0.35, seed)
    
    # Unity / Unreal Engine の足音・サーフェス判定用スロット
    mat_footstep = create_chibi_character_shader(f"{name}_Footstep_Surface_Mat", "FOOTSTEP_SURFACE", (0.2, 0.2, 0.2, 1.0), 0.85, seed)
    mat_shoe = create_chibi_character_shader(f"{name}_Shoe_Mat", "CLOTH_BOTTOM", shoe_color, 0.5, seed)

    # マテリアル割り当て
    body_obj.data.materials.append(mat_skin)
    head_obj.data.materials.append(mat_skin)
    ears_obj.data.materials.append(mat_skin)
    if hair_obj:
        hair_obj.data.materials.append(mat_hair)

    outfit_obj.data.materials.append(mat_top)
    outfit_obj.data.materials.append(mat_button)  # スロット1: 衣装装飾ボタン（オーバーオール留め具・コート・Tシャツ等）
    eyes_obj.data.materials.append(mat_sclera)   # スロット0: 白目（Sclera）
    eyes_obj.data.materials.append(mat_eye)      # スロット1: 瞳・虹彩（Iris / Pupil）
    eyes_obj.data.materials.append(mat_eye_hl)   # スロット2: ハイライト
    eyes_obj.data.materials.append(mat_eyelash)  # スロット3: 上まつ毛・アイライン
    if eyebrow_obj:
        eyebrow_obj.data.materials.append(mat_eyebrow)
    nose_obj.data.materials.append(mat_nose)
    mouth_obj.data.materials.append(mat_mouth)

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
    child_parts = [head_obj, ears_obj, eyes_obj, nose_obj, mouth_obj, outfit_obj, shoes_obj]
    if hair_obj:
        child_parts.append(hair_obj)
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
