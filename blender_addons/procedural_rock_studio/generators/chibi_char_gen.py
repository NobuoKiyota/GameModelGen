import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler


def _apply_boolean_and_fix_normals(context, obj, bool_mod):
    """
    Booleanモディファイアをその場でBake(適用)し、実メッシュ化した直後に
    bmeshで法線を明示的に再計算する。

    目・口のソケットのように、同じ頭部メッシュへBooleanモディファイアを
    ライブのまま複数回(目→口)チェーンして積み重ねると、EXACTソルバーでも
    ごく一部の面(境界付近)で隣接面と法線が大きく矛盾する不整合が発生し、
    Subsurf適用後に顔面へ亀裂状のシェーディング異常として現れることが
    分かった。生成の都度Bakeしてbmeshで法線を再計算し直すことで、次の
    Boolean(や最終的なSubsurf)に不整合を持ち越さないようにする。
    """
    prev_active = context.view_layer.objects.active
    prev_selected = list(context.selected_objects)
    for o in context.selected_objects:
        o.select_set(False)
    context.view_layer.objects.active = obj
    obj.select_set(True)
    try:
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    except Exception:
        try:
            with context.temp_override(active_object=obj, object=obj, selected_objects=[obj]):
                bpy.ops.object.modifier_apply(modifier=bool_mod.name)
        except Exception:
            pass
    finally:
        context.view_layer.objects.active = prev_active
        for o in prev_selected:
            o.select_set(True)

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


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


def compute_chibi_body_layout(gender="BOY", head_ratio=2.2, total_height=1.15):
    """
    体の関節座標・半径を1箇所で計算する共通レイアウト。
    build_chibi_body_mesh と、服・靴（build_chibi_outfit_mesh / build_chibi_shoes_mesh）が
    同じ値を参照することで、プロポーションを変えても服・靴が体から乖離しないようにする。
    """
    head_height = total_height / head_ratio
    body_total = total_height - head_height
    leg_len = body_total * 0.38
    torso_len = body_total * 0.62
    base_z = 0.05  # 靴底の少し上

    sh_x = 0.11 if gender == "BOY" else 0.10
    hip_x = 0.075

    return {
        'base_z': base_z, 'leg_len': leg_len, 'torso_len': torso_len,
        'head_height': head_height, 'body_total': body_total,
        'crotch':   {'pos': Vector((0.0, 0.0, base_z + leg_len)), 'radius': (0.13, 0.13)},
        'belly':    {'pos': Vector((0.0, -0.015, base_z + leg_len + torso_len * 0.45)), 'radius': (0.145, 0.14)},
        'chest':    {'pos': Vector((0.0, 0.0, base_z + leg_len + torso_len * 0.85)), 'radius': (0.125, 0.12)},
        'neck':     {'pos': Vector((0.0, 0.0, base_z + leg_len + torso_len)), 'radius': (0.09, 0.09)},
        'shoulder': {'pos': Vector((sh_x, 0.0, base_z + leg_len + torso_len * 0.78)), 'radius': (0.07, 0.07)},
        'elbow':    {'pos': Vector((sh_x + 0.07, -0.01, base_z + leg_len + torso_len * 0.42)), 'radius': (0.06, 0.06)},
        'hand':     {'pos': Vector((sh_x + 0.11, 0.04, base_z + leg_len + torso_len * 0.12)), 'radius': (0.08, 0.08)},
        'hip':      {'pos': Vector((hip_x, 0.0, base_z + leg_len * 0.95)), 'radius': (0.085, 0.085)},
        'knee':     {'pos': Vector((hip_x, 0.0, base_z + leg_len * 0.45)), 'radius': (0.075, 0.075)},
        'ankle':    {'pos': Vector((hip_x, 0.01, base_z + 0.025)), 'radius': (0.07, 0.07)},
    }


def build_chibi_body_mesh(context, name="Chibi_Body", gender="BOY", head_ratio=2.2, total_height=1.15):
    """
    動画核心技術: Single Vert ＋ 3段モディファイア（Mirror + Skin + Subdiv）による素体生成
    どうぶつの森風のコロンとした丸みとプロポーション
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    layout = compute_chibi_body_layout(gender, head_ratio, total_height)

    bm = bmesh.new()

    # 右半身の骨格頂点を作成（X >= 0）（作成順は skin_data のインデックスと対応）
    v_crotch = bm.verts.new(layout['crotch']['pos'])
    v_belly = bm.verts.new(layout['belly']['pos'])
    v_chest = bm.verts.new(layout['chest']['pos'])
    v_neck = bm.verts.new(layout['neck']['pos'])

    v_shoulder = bm.verts.new(layout['shoulder']['pos'])
    v_elbow = bm.verts.new(layout['elbow']['pos'])
    v_hand = bm.verts.new(layout['hand']['pos'])

    v_hip = bm.verts.new(layout['hip']['pos'])
    v_knee = bm.verts.new(layout['knee']['pos'])
    v_ankle = bm.verts.new(layout['ankle']['pos'])

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
    # スキン頂点半径の設定（Ctrl+A 相当、layoutの radius と同じ作成順）
    skin_data = mesh.skin_vertices[0].data if mesh.skin_vertices else []
    if skin_data and len(skin_data) >= 10:
        joint_order = ['crotch', 'belly', 'chest', 'neck', 'shoulder', 'elbow', 'hand', 'hip', 'knee', 'ankle']
        for i, joint_name in enumerate(joint_order):
            skin_data[i].radius = layout[joint_name]['radius']

    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 2
    mod_sub.render_levels = 2

    return obj


# 下絵(Z:\MeshCreator\docs\tutorial_transcripts\SD正面下絵.PNG / SD横向き下絵.PNG)の
# シルエットを実測して得た輪郭プロファイル。頭頂(0.0)→顎(1.0)の高さ比率ごとに、
# 最大幅/最大奥行きに対する正規化値を格納している。
# 勘の彫刻式ではなく実測データそのものを使うことで、単純な楕円体では出ない
# 「こめかみで一度窄まってから頬(正面)・鼻先(側面)でもう一段膨らむ」という
# 非単調な輪郭を再現する。将来的に別の3面図が与えられた場合も、同じ手順で
# シルエットを実測してこの2本の配列を差し替えるだけで対応できる想定。
FRONT_WIDTH_PROFILE = [
    (0.0, 0.0576), (0.025, 0.291), (0.05, 0.418), (0.075, 0.5081), (0.1, 0.5864),
    (0.125, 0.6544), (0.15, 0.712), (0.175, 0.7607), (0.2, 0.8021), (0.225, 0.836),
    (0.25, 0.8641), (0.275, 0.8877), (0.3, 0.9114), (0.325, 0.9321), (0.35, 0.9498),
    (0.375, 0.9645), (0.4, 0.9764), (0.425, 0.9852), (0.45, 0.9926), (0.475, 0.997),
    (0.5, 1.0), (0.525, 1.0), (0.55, 0.997), (0.575, 0.9911), (0.6, 0.9808),
    (0.625, 0.969), (0.65, 0.9542), (0.675, 0.935), (0.7, 0.9114), (0.725, 0.9734),
    (0.75, 0.9941), (0.775, 0.9941), (0.8, 0.9808), (0.825, 0.9439), (0.85, 0.8848),
    (0.875, 0.8168), (0.9, 0.7371), (0.925, 0.6366), (0.95, 0.5199), (0.975, 0.3648),
    (1.0, 0.1403),
]

# 側面の「奥行き」は前面(顔)と後面(後頭部)を分離して測っている。
# 単純な合計の奥行きを前後対称に割り振ると、片方の出っ張りがもう片方にも
# 同じだけ適用されてしまい、頭を一周する不自然な帯(段差)になってしまうことが
# 分かったため、実測時点で頭頂点を基準の中心軸として前面距離・後面距離を
# 別々に算出し直した。
#
# 注意: 下絵(SD横向き下絵.PNG)のどちらが前面かは形状だけでは一意に決まらず、
# 当初は誤って逆(向かって右側を前)と判断していた。実際は複数の身体的手がかり
# (眉間〜鼻の窪みの位置、耳の向き、肩から下がる腕が首の前ではなく後ろにある
# こと、胸〜腹のラインの自然さ、臀部の位置、脚の分割、膝裏の折れ方)から
# 総合的に判断して「向かって左側が前面」が正しい。以下の2配列はこの正しい
# 判定に基づいて中身を入れ替え済み。
# FRONT_DEPTH_PROFILE: 顔の輪郭。額から顎にかけて滑らかに減少するだけでなく、
#   t≈0.7-0.8あたり(顎の少し上)でもう一段膨らむ(頬〜顎のふくらみ)。
# BACK_DEPTH_PROFILE: 後頭部の輪郭。滑らかな減少のみで単純な丸み。
FRONT_DEPTH_PROFILE = [
    (0.0, 0.0234), (0.025, 0.144), (0.05, 0.2059), (0.075, 0.2557), (0.1, 0.2919),
    (0.125, 0.322), (0.15, 0.3492), (0.175, 0.3748), (0.2, 0.3944), (0.225, 0.4125),
    (0.25, 0.4261), (0.275, 0.4382), (0.3, 0.4487), (0.325, 0.4578), (0.35, 0.4638),
    (0.375, 0.4698), (0.4, 0.4744), (0.425, 0.4759), (0.45, 0.4774), (0.475, 0.4759),
    (0.5, 0.4729), (0.525, 0.4683), (0.55, 0.4653), (0.575, 0.4623), (0.6, 0.4623),
    (0.625, 0.4638), (0.65, 0.4683), (0.675, 0.4804), (0.7, 0.4955), (0.725, 0.5045),
    (0.75, 0.5106), (0.775, 0.509), (0.8, 0.5045), (0.825, 0.497), (0.85, 0.4864),
    (0.875, 0.4729), (0.9, 0.4548), (0.925, 0.4291), (0.95, 0.3944), (0.975, 0.3416),
    (1.0, 0.0551),
]

BACK_DEPTH_PROFILE = [
    (0.0, 0.0234), (0.025, 0.1667), (0.05, 0.23), (0.075, 0.2813), (0.1, 0.3205),
    (0.125, 0.3537), (0.15, 0.3824), (0.175, 0.408), (0.2, 0.4291), (0.225, 0.4472),
    (0.25, 0.4623), (0.275, 0.4759), (0.3, 0.4864), (0.325, 0.4955), (0.35, 0.503),
    (0.375, 0.509), (0.4, 0.5151), (0.425, 0.5181), (0.45, 0.5211), (0.475, 0.5241),
    (0.5, 0.5241), (0.525, 0.5226), (0.55, 0.5211), (0.575, 0.5181), (0.6, 0.5136),
    (0.625, 0.5075), (0.65, 0.5), (0.675, 0.491), (0.7, 0.4819), (0.725, 0.4698),
    (0.75, 0.4563), (0.775, 0.4412), (0.8, 0.4261), (0.825, 0.408), (0.85, 0.3854),
    (0.875, 0.3582), (0.9, 0.3235), (0.925, 0.2783), (0.95, 0.2179), (0.975, 0.1033),
    (1.0, 0.0792),
]


def _sample_profile(profile, t):
    """profile: [(高さ比率0-1, 正規化値0-1), ...] を線形補間してサンプルする"""
    t = max(0.0, min(1.0, t))
    if t <= profile[0][0]:
        return profile[0][1]
    if t >= profile[-1][0]:
        return profile[-1][1]
    for i in range(len(profile) - 1):
        f0, v0 = profile[i]
        f1, v1 = profile[i + 1]
        if f0 <= t <= f1:
            local = (t - f0) / (f1 - f0) if f1 > f0 else 0.0
            return v0 + (v1 - v0) * local
    return profile[-1][1]


def _baseline_and_bump_profile(profile):
    """
    プロファイルからピーク以降の「なだらかな下降のみ」のベースラインを、
    ピーク以降の累積最小値として求め、実測値との差分(ふくらみ量)を分離する。

    例: 正面幅プロファイルの「こめかみで窄まってから頬でもう一段膨らむ」という
    山は、単純な楕円体ロフトでは輪(リング)全体を一律に膨らませてしまい、
    頭を一周する不自然な帯になる。この関数で「膨らみ量」だけを取り出しておき、
    呼び出し側で頬に近い角度(側面寄り)だけに減衰させながら適用することで、
    局所的なふくらみとして再現できるようにする。
    """
    peak_i = max(range(len(profile)), key=lambda i: profile[i][1])
    n = len(profile)
    baseline_vals = [v for _, v in profile]

    last_i = peak_i
    i = peak_i + 1
    while i < n:
        if profile[i][1] <= baseline_vals[last_i]:
            baseline_vals[i] = profile[i][1]
            last_i = i
            i += 1
        else:
            # 膨らみ区間: 一旦フラットに固定するとそれ自体が段差(棚)の原因になる
            # ため、直前の下降点(last_i)から、値が再び基準を下回る点(j)まで
            # 直線で滑らかに橋渡しする。
            j = i
            while j < n and profile[j][1] > baseline_vals[last_i]:
                j += 1
            if j < n:
                t0, v0 = profile[last_i][0], baseline_vals[last_i]
                t1, v1 = profile[j][0], profile[j][1]
                for k in range(i, j):
                    tk = profile[k][0]
                    frac = (tk - t0) / (t1 - t0) if t1 > t0 else 0.0
                    baseline_vals[k] = v0 + (v1 - v0) * frac
                last_i = j
                i = j + 1
            else:
                # 基準を下回る点が最後まで見つからない場合は直前の傾きで素直に延長する
                for k in range(i, n):
                    baseline_vals[k] = baseline_vals[last_i]
                i = n

    baseline = [(profile[i][0], baseline_vals[i]) for i in range(n)]
    bump = [(profile[i][0], max(0.0, profile[i][1] - baseline_vals[i])) for i in range(n)]
    return baseline, bump


FRONT_WIDTH_BASELINE, FRONT_WIDTH_BUMP = _baseline_and_bump_profile(FRONT_WIDTH_PROFILE)

# 鼻先の丸い膨らみ。下絵(SD横向き下絵.PNG)は身体プロポーション用の単純な
# シルエットのみで鼻の彫刻までは含まれていないため、これは実測値ではなく
# 動画の実際の彫刻結果(参考スクリーンショットで確認した鼻筋のカーブ位置)に
# 合わせた目安値。正面中央かつ前面のみに局所的に効かせ、頬の帯と同様に
# リング全体へ一律適用しないようにする。
NOSE_T_CENTER = 0.58
NOSE_T_HALF = 0.09
NOSE_X_HALF = 0.22
NOSE_STRENGTH = 0.20


def build_chibi_head_mesh(context, name="Chibi_Head", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40)):
    """
    下絵(SD正面下絵.PNG / SD横向き下絵.PNG)から実測したシルエット輪郭プロファイルを
    そのままメッシュに反映する「輪郭ロフト」方式。

    以前は勘の解析式(法線方向への一律プッシュ)で頬・顎・鼻根を近似していたが、
    参考画像なしに数式だけを調整しても実物との対応が取れず改善が頭打ちになって
    いた。UV球の各頂点を、その高さ(Z)に対応する正面幅プロファイル/側面奥行き
    プロファイルの実測値でX/Y方向にスケールし直すことで、単純な楕円体では
    出せない「こめかみで窄まってから頬・鼻先でもう一段膨らむ」輪郭を直接再現する。
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=40, radius=0.5)

    sx, sy, sz = head_size[0] * 0.5, head_size[1] * 0.5, head_size[2] * 0.5
    avg_r = (sx + sy + sz) / 3.0

    for v in bm.verts:
        # 元のUV球上での「高さ比率」(0=頭頂, 1=顎)と水平方向の単位ベクトルを求める
        t = (0.5 - v.co.z) / 1.0  # v.co.z: +0.5(頭頂)～-0.5(顎)
        horiz_r = math.sqrt(v.co.x * v.co.x + v.co.y * v.co.y)
        if horiz_r > 1e-6:
            # 極(horiz_r≈0)はux,uyが不定になるため何もスケールしない。
            # ここで誤って(rx,0)等に飛ばすと、極が輪の縁まで引き伸ばされて
            # 頭頂/顎が平らに潰れる不具合になる。
            ux, uy = v.co.x / horiz_r, v.co.y / horiz_r
            # 頬のふくらみ(ベースラインからの超過分)は側面寄りの角度(|ux|が大きい
            # ＝真横に近い)ほど強く、正面・後面に近づくほど0へ減衰させる。
            # そのままリング全体に一律適用すると、頭を一周する不自然な帯になる。
            side_weight = ux * ux
            rx = sx * (
                _sample_profile(FRONT_WIDTH_BASELINE, t)
                + _sample_profile(FRONT_WIDTH_BUMP, t) * side_weight
            )
            # 奥行きは前面(uy<0, 顔側)と後面(uy>0, 後頭部側)で別プロファイルを使う。
            # 同じ値を両側に使うと、後頭部のふくらみが顔の前面にも漏れ出てしまう
            # (逆も同様)。*2 は測定時の正規化基準(前後合計に対する片側の比率)を
            # sy(片側の基準半径)に合わせて揃えるための係数。
            if uy < 0.0:
                ry = sy * 2.0 * _sample_profile(FRONT_DEPTH_PROFILE, t)
            else:
                ry = sy * 2.0 * _sample_profile(BACK_DEPTH_PROFILE, t)
            v.co.x = ux * rx
            v.co.y = uy * ry

            # 鼻先の膨らみ: 正面中央(ux≈0, uy<0)かつ鼻の高さ(t≈NOSE_T_CENTER)
            # の頂点だけを前方(-Y)へ押し出す。頬の帯と同じ理由で、リング全体では
            # なく局所的な範囲にだけガウス風の重みで効かせる。
            front_w = max(0.0, -uy)
            center_w = max(0.0, 1.0 - (ux / NOSE_X_HALF) ** 2)
            dt = (t - NOSE_T_CENTER) / NOSE_T_HALF
            height_w = max(0.0, 1.0 - dt * dt)
            nose_w = front_w * center_w * height_w
            if nose_w > 0.0:
                v.co.y -= nose_w * NOSE_STRENGTH * avg_r
        v.co.z = v.co.z * (sz / 0.5)

    hc = Vector(head_center)
    for v in bm.verts:
        v.co += hc

    bm.to_mesh(mesh)
    bm.free()

    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 1
    mod_sub.render_levels = 1

    return obj


# 側面下絵(SD横向き下絵.PNG)の耳の輪郭線(黒い「へ」の字カーブ)を実測して得た値。
# 頭頂(t=0)～顎(t=1)の高さ比率での耳の中心位置・上下方向の半径(head_size[2]基準)・
# 前後方向の半径(head_size[1]基準)・中心軸からの前後オフセット(head_size[1]基準)。
# 測定手順: 頭部シルエットの黒枠とは別に、頭部内側にある耳カーブだけの暗ピクセル
# クラスタをbboxで抽出し、頭頂/顎の実測基準(head_top=100px, head_bottom=830px,
# 前後中心軸=496.5px, 前後合計奥行き=663px)に対する比率に変換した。
EAR_T_CENTER = 0.7808
EAR_R_Z = 0.0753       # 上下方向の半径 (× head_size[2])
EAR_R_Y = 0.0415       # 前後方向の半径 (× head_size[1])
EAR_BACK_OFFSET = 0.0196  # 中心軸から後方向へのオフセット (× head_size[1])


def build_chibi_ears_mesh(context, name="Chibi_Ears", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40), head_obj=None):
    """
    動画①(08:20-10:30、耳の押し出し)に準拠した耳メッシュ。
    位置・縦横比は側面下絵(SD横向き下絵.PNG)の耳カーブを実測した値
    (EAR_T_CENTER/EAR_R_Z/EAR_R_Y/EAR_BACK_OFFSET)を使用する。
    左右方向(頭からどれだけ張り出すか)は下絵の側面図だけでは分からないため、
    頭部表面へのレイキャスト・アンカー方式(目と同じ考え方)で実際の頭部形状
    (輪郭ロフト方式・こめかみの窄まり等)に自動で沿わせる。
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    ear_x = head_size[0] * 0.46
    ear_z = head_center[2] + head_size[2] * (0.5 - EAR_T_CENTER)

    sx = head_size[0] * 0.5
    sy = head_size[1] * 0.5
    sz = head_size[2] * 0.5

    eval_head = None
    if head_obj:
        try:
            dg = context.evaluated_depsgraph_get()
            eval_head = head_obj.evaluated_get(dg)
        except Exception:
            eval_head = head_obj

    def raycast_point(vx, vz):
        wx = vx
        wz = vz
        if eval_head:
            ray_origin = Vector((wx, head_center[1] - 0.60, wz))
            ray_dir = Vector((0.0, 1.0, 0.0))
            hit, loc, norm, idx = eval_head.ray_cast(ray_origin, ray_dir)
            if hit:
                return loc, norm.normalized()
        norm_x = wx / max(0.01, sx)
        norm_z = (wz - head_center[2]) / max(0.01, sz)
        rad_sq = max(0.02, 1.0 - norm_x * norm_x - norm_z * norm_z)
        wy = head_center[1] - math.sqrt(rad_sq) * sy
        return Vector((wx, wy, wz)), Vector((0.0, -1.0, 0.0))

    # 下絵で耳は頭の前後中心軸よりわずかに後ろ(後頭部寄り)にあったので、その分
    # だけ後方向(+Y)へアンカーをずらしてからレイキャストする。
    back_offset = head_size[1] * EAR_BACK_OFFSET
    anchor_loc, anchor_norm = raycast_point(ear_x, ear_z)
    anchor_loc = anchor_loc + Vector((0.0, back_offset, 0.0))

    world_up = Vector((0.0, 0.0, 1.0))
    tangent_x = world_up.cross(anchor_norm)
    if tangent_x.length < 1e-6:
        tangent_x = Vector((1.0, 0.0, 0.0))
    tangent_x.normalize()
    if tangent_x.x < 0.0:
        tangent_x = -tangent_x
    tangent_z = anchor_norm.cross(tangent_x).normalized()
    if tangent_z.z < 0.0:
        tangent_z = -tangent_z

    # 扁平球を頭部表面の法線方向に半分ほどめり込ませて配置する(目と同じ考え方)。
    # リム付きの円盤形状は法線の向き次第で「お皿」のように見えてしまい破綻しやすい
    # ため、向きに左右されにくい扁平球で頭部に自然になじませる方式に単純化した。
    # tangent_zはこの位置ではほぼ上下方向、tangent_xはほぼ前後方向に一致するため、
    # 実測した縦横比(上下 vs 前後)をそれぞれに反映する。
    r_tan_x = head_size[1] * EAR_R_Y * 1.15             # 接平面: 前後方向の広がり(実測)
    r_tan_z = head_size[2] * EAR_R_Z * 1.15             # 接平面: 上下方向の広がり(実測)
    r_out = min(r_tan_x, r_tan_z) * 0.7                 # 外向き(法線方向)の厚み(未実測、控えめに設定)
    embed = r_out * 0.55   # 頭部内部にめり込ませる量

    bm = bmesh.new()
    res = bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=10, radius=1.0)
    center = anchor_loc - anchor_norm * embed
    for v in res['verts']:
        lt = v.co.x * r_tan_x
        ln = v.co.y * r_out
        lb = v.co.z * r_tan_z
        v.co = center + tangent_x * lt + anchor_norm * ln + tangent_z * lb

    bm.to_mesh(mesh)
    bm.free()

    mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
    mod_mirror.use_axis[0] = True

    mod_sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod_sub.levels = 1
    mod_sub.render_levels = 1

    return obj


def _build_sphere_verts(bm, u=18, v=14, radius=1.0):
    """単位球（半径1.0のUVスフィア）をbmに追加し、頂点リストを返す"""
    res = bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=radius)
    return res['verts']


def build_chibi_eyes_mesh(context, name="Chibi_Eyes", gender="BOY", eye_style="OVAL", eye_scale=1.0, head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40), head_obj=None):
    """
    正球ベースの3層目メッシュ（白目玉/瞳・虹彩/ハイライト）＋頭部への実Boolean眼窩。

    背景: 以前の「奥行きだけ潰した楕円体デカール」方式は、正面からは丸く見えても
    真横から見ると薄い板の断面（細い線）に潰れてしまうという構造的な欠陥があった
    （参考: MeshySample クレイモデル・Head_Test.blend では真横でも目が丸く残る）。
    球はどの角度から見ても輪郭が円になる性質を持つため、正球を頭部にBooleanで
    浅く埋め込む方式に変更し、この問題を原理的に解消する。

    - head_obj側: 白目玉と同じ半径の正球カッター（Mirrorで左右複製）をBoolean
      DIFFERENCEで追加し、実際の眼窩の穴を頭部メッシュに開ける
      （カッターは非表示・頭部の子オブジェクトとしてエクスポート選択に含める）
    - このメッシュ（eyes_obj）側: slot0=白目玉、slot1=瞳・虹彩、slot2=ハイライト。
      いずれも正球がベース。瞳・ハイライトのみスタイルごとに位置/縦横比を変え、
      白目玉は常に正球のまま（＝全角度で丸いことを担保する部分は変形しない）。
    - 表情シェイプキー（Blink/Smile/Wide/Squint）は従来通り維持。
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()

    # ─── パラメータ ────────────────────────────────────────────────────────────
    # 注意: 0.300 は旧・薄い楕円体デカール方式のときの値。正球方式は半径そのものが
    # 頭部横幅に対して大きな割合を占めるため、同じ0.300だと側頭部の際まで到達して
    # Boolean カッターが頭部の縁の急カーブと干渉し、歪んだ穴になってしまう。
    eye_x = head_size[0] * 0.230
    eye_z = head_center[2] - head_size[2] * 0.095

    sx = head_size[0] * 0.5
    sy = head_size[1] * 0.5
    sz = head_size[2] * 0.5
    avg_r = (sx + sy + sz) / 3.0

    # スタイル別パラメータ。白目玉(sclera)は常に正球のため r_f/protrusion_f のみ変化させ、
    # 「見た目の個性」は主に瞳(pupil)の縦横比・位置・突出量で表現する
    # （瞳は白目玉の輪郭の内側に収まる副次要素なので、変形しても全角度で丸いという
    # 白目玉の性質を壊さない）。
    style_params = {
        "OVAL":    dict(r_f=0.30, protrusion_f=0.30, pupil_scale=1.00, pupil_flat=1.00, pupil_dz=0.00, pupil_dx=0.00),
        "ROUND":   dict(r_f=0.30, protrusion_f=0.32, pupil_scale=1.05, pupil_flat=1.00, pupil_dz=0.00, pupil_dx=0.00),
        "DROOPY":  dict(r_f=0.30, protrusion_f=0.22, pupil_scale=1.00, pupil_flat=1.00, pupil_dz=-0.35, pupil_dx=0.00),
        "CAT_EYE": dict(r_f=0.30, protrusion_f=0.34, pupil_scale=0.85, pupil_flat=0.75, pupil_dz=0.20, pupil_dx=0.25),
        "SMILING": dict(r_f=0.28, protrusion_f=0.10, pupil_scale=1.00, pupil_flat=0.30, pupil_dz=0.00, pupil_dx=0.00),
    }
    sp = style_params.get(eye_style, style_params["OVAL"])

    sclera_r = avg_r * sp["r_f"] * eye_scale
    protrusion_f = sp["protrusion_f"]

    # ガチャ安全クランプ: eye_scale を大きくしても左右の目が重ならず、
    # 側頭部の外にもはみ出さないようにする
    min_gap = sclera_r * 0.35
    min_eye_x = sclera_r + min_gap
    max_eye_x = sx * 0.92 - sclera_r
    eye_x = max(min_eye_x, min(eye_x, max(min_eye_x, max_eye_x)))

    eval_head = None
    if head_obj:
        try:
            dg = context.evaluated_depsgraph_get()
            eval_head = head_obj.evaluated_get(dg)
        except Exception:
            eval_head = head_obj

    def raycast_point(vx, vz):
        """頭部実メッシュ皮膚表面への単発レイキャスト（アンカー算出専用）"""
        wx = eye_x + vx
        wz = eye_z + vz
        if eval_head:
            ray_origin = Vector((wx, head_center[1] - 0.60, wz))
            ray_dir = Vector((0.0, 1.0, 0.0))
            hit, loc, norm, idx = eval_head.ray_cast(ray_origin, ray_dir)
            if hit:
                return loc, norm.normalized()
        norm_x = wx / max(0.01, sx)
        norm_z = (wz - head_center[2]) / max(0.01, sz)
        y_fac = 1.0 + max(0.0, -norm_z) * 0.05
        rad_sq = max(0.02, 1.0 - norm_x * norm_x - norm_z * norm_z)
        wy = head_center[1] - math.sqrt(rad_sq) * sy * y_fac
        return Vector((wx, wy, wz)), Vector((0.0, -1.0, 0.0))

    # アンカー（目の中心1点のみ）をレイキャストし、そこに剛体の接平面フレームを張る。
    # 頂点ごとにレイキャストすると頭部メッシュの微小な凹凸に追従してガタつくため、
    # 中心1点の法線・接線でフラットに配置する（正球なので変形には使わず、瞳の
    # オフセット方向の基準としてのみ使用）。
    anchor_loc, anchor_norm = raycast_point(0.0, 0.0)
    world_up = Vector((0.0, 0.0, 1.0))
    tangent_x = world_up.cross(anchor_norm)
    if tangent_x.length < 1e-6:
        tangent_x = Vector((1.0, 0.0, 0.0))
    tangent_x.normalize()
    if tangent_x.x < 0.0:
        tangent_x = -tangent_x
    tangent_z = anchor_norm.cross(tangent_x).normalized()
    if tangent_z.z < 0.0:
        tangent_z = -tangent_z

    # 白目玉の中心: アンカー表面から anchor_norm の逆方向へ sclera_r*(1-protrusion_f) だけ
    # 沈めることで、半径 sclera_r*protrusion_f の分だけ表面から丸く飛び出す
    sclera_center = anchor_loc - anchor_norm * (sclera_r * (1.0 - protrusion_f))
    sclera_front = sclera_center + anchor_norm * sclera_r

    def place_sphere(verts_local, center, rt, rn, rb):
        """単位球の各頂点を、接線T/法線N/接線Bの3軸半径でスケールし配置する
        （rt=rn=rbなら真の正球のまま平行移動するだけになる）"""
        for v in verts_local:
            lt = v.co.x * rt
            ln = v.co.y * rn
            lb = v.co.z * rb
            v.co = center + tangent_x * lt + anchor_norm * ln + tangent_z * lb

    # ─── 1. 白目玉（sclera）: 常に正球 ─────────────────────────────────────
    sclera_verts = _build_sphere_verts(bm, u=18, v=14)
    place_sphere(sclera_verts, sclera_center, sclera_r, sclera_r, sclera_r)
    sclera_vset = set(sclera_verts)

    # ─── 2. 瞳・虹彩（pupil）: 白目玉の露出面よりわずかに前へ、スタイルに応じて
    # 位置・縦横比を変える（白目玉自体は変形しないので全角度での丸さは保たれる）─
    pupil_r = sclera_r * 0.55 * sp["pupil_scale"]
    pupil_margin = sclera_r * 0.08
    pupil_center = sclera_front + anchor_norm * (pupil_margin - pupil_r)
    pupil_center += tangent_x * (sp["pupil_dx"] * sclera_r) + tangent_z * (sp["pupil_dz"] * sclera_r)
    pupil_verts = _build_sphere_verts(bm, u=14, v=10)
    place_sphere(pupil_verts, pupil_center, pupil_r, pupil_r, pupil_r * sp["pupil_flat"])
    pupil_vset = set(pupil_verts)
    pupil_front = pupil_center + anchor_norm * pupil_r

    # ─── 3. ハイライト（キャッチライト）: 瞳の上寄りにごく浅く埋め込む正球 ──
    # 注意: オフセットはtangent_z(頭部ローカルの上下)とanchor_norm(奥行き)のみで
    # 構成し、tangent_x(左右)方向は使わない。頭部を回転させて多角度検証した際、
    # 左右方向のオフセットは真横視点で「奥行き」に化けてハイライトが瞳から浮いて
    # 見えるバグになることが分かっている。
    hl_r = pupil_r * 0.30
    hl_protrusion = 0.35
    hl_center = pupil_front - anchor_norm * (hl_r * (1.0 - hl_protrusion)) + tangent_z * (pupil_r * 0.35)
    hl_verts = _build_sphere_verts(bm, u=10, v=8)
    place_sphere(hl_verts, hl_center, hl_r, hl_r, hl_r)
    hl_vset = set(hl_verts)

    # ─── 法線整列（各正球＝凸形状なので重心基準の再計算で正しく外向きになる） ──
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))

    # ─── マテリアルインデックス ───────────────────────────────────────────────
    # slot 0: 白目玉　slot 1: 瞳・虹彩　slot 2: ハイライト
    for f in bm.faces:
        if any(v in hl_vset for v in f.verts):
            f.material_index = 2
        elif any(v in pupil_vset for v in f.verts):
            f.material_index = 1
        else:
            f.material_index = 0

    bm.to_mesh(mesh)
    bm.free()

    # シェイプキー
    # 注意: 正球は tangent_x/anchor_norm/tangent_z の接平面フレームで組み立てられており、
    # このフレームは頭部の曲率次第でワールド軸(X/Z)から少し傾く。旧コードはワールドの
    # pt.co.x/pt.co.z をそのまま潰す/伸ばす方式だったが、これをそのまま正球に適用すると
    # フレームのズレ分だけ非対称に歪んだ形（左右の目で歪み方が変わる）になってしまうため、
    # 必ずこのフレーム基準のローカル座標に変換してから変形する。
    def _to_local(p):
        rel = p - anchor_loc
        return rel.dot(tangent_x), rel.dot(anchor_norm), rel.dot(tangent_z)

    def _from_local(lt, ln, lb):
        return anchor_loc + tangent_x * lt + anchor_norm * ln + tangent_z * lb

    try:
        obj.shape_key_add(name="Basis", from_mix=False)

        sk_blink = obj.shape_key_add(name="Blink", from_mix=False)
        for pt in sk_blink.data:
            lt, ln, lb = _to_local(pt.co)
            lb = -sclera_r * 0.12 + lb * 0.05
            pt.co = _from_local(lt, ln, lb)

        sk_smile = obj.shape_key_add(name="Smile", from_mix=False)
        for pt in sk_smile.data:
            lt, ln, lb = _to_local(pt.co)
            dx = lt / max(0.001, sclera_r)
            arch = (1.0 - min(1.2, dx * dx)) * sclera_r * 0.28
            lb = lb * 0.12 + arch
            pt.co = _from_local(lt, ln, lb)

        sk_wide = obj.shape_key_add(name="Wide", from_mix=False)
        for pt in sk_wide.data:
            lt, ln, lb = _to_local(pt.co)
            lt *= 1.12
            lb *= 1.12
            pt.co = _from_local(lt, ln, lb)

        sk_squint = obj.shape_key_add(name="Squint", from_mix=False)
        for pt in sk_squint.data:
            lt, ln, lb = _to_local(pt.co)
            if lb > 0:
                lb *= 0.22
            pt.co = _from_local(lt, ln, lb)
    except Exception:
        pass

    mod_mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
    mod_mirror.use_axis[0] = True

    # ─── 頭部側: 白目玉と同じ正球をBoolean DIFFERENCEカッターとして頭部に埋め込む ──
    if head_obj is not None:
        cutter_mesh = bpy.data.meshes.new(name + "_SocketCutter_Mesh")
        cutter_obj = bpy.data.objects.new(name + "_SocketCutter", cutter_mesh)
        context.collection.objects.link(cutter_obj)

        cbm = bmesh.new()
        cutter_verts = _build_sphere_verts(cbm, u=18, v=14)
        for v in cutter_verts:
            v.co = v.co * sclera_r + sclera_center
        bmesh.ops.recalc_face_normals(cbm, faces=list(cbm.faces))
        cbm.to_mesh(cutter_mesh)
        cbm.free()

        cutter_mirror = cutter_obj.modifiers.new(name="Mirror", type='MIRROR')
        cutter_mirror.use_axis[0] = True

        bool_mod = head_obj.modifiers.new(name="EyeSocketBoolean", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = cutter_obj
        bool_mod.solver = 'EXACT'

        # Boolean は Subdivision より前(低ポリの元メッシュ)に適用し、その後に
        # Subdivisionで穴の縁ごと滑らかにする方が綺麗な仕上がりになる。
        # Subdivision後(高密度メッシュ)にBooleanをかけると、カッター球の粗い分割と
        # 密なメッシュが干渉して縁が歪む・欠けることがあるため順序を入れ替える。
        try:
            bool_index = list(head_obj.modifiers).index(bool_mod)
            if bool_index > 0:
                head_obj.modifiers.move(bool_index, 0)
        except Exception:
            pass

        # その場でBakeして法線を再計算しておく(後段のBoolean・Subsurfに
        # 不整合を持ち越さないため。詳細は_apply_boolean_and_fix_normalsを参照)
        _apply_boolean_and_fix_normals(context, head_obj, bool_mod)

        cutter_obj.hide_render = True
        cutter_obj.hide_viewport = True
        cutter_obj.parent = head_obj
        cutter_obj.matrix_parent_inverse = head_obj.matrix_world.inverted()

    return obj


def build_chibi_mouth_mesh(context, name="Chibi_Mouth", head_center=(0, 0, 0.72), head_size=(0.48, 0.42, 0.40), head_obj=None):
    """
    動画①(10:30-12:04、口のナイフカット+口内ソケット)に準拠した口メッシュ。

    動画は実メッシュにナイフで開口線を切り、面を削除して穴を開けたあと、
    開口の縁を複製して奥へ2段階で押し出し・中心でマージすることで口内
    ソケットを作る。この「実際に頭部へ穴を開け、奥に見える内側を別途作る」
    という構造を、目(build_chibi_eyes_mesh)で確立したBoolean方式で再現する
    (旧来の「表面に貼り付けた薄い唇デカール」から刷新)。
    - head_obj側: 扁平な楕円体カッターをBoolean DIFFERENCEで頭部に埋め込み、
      実際に開口させる。
    - このメッシュ(mouth_obj)側: カッターよりひと回り小さい扁平楕円体を、
      口内の奥側に配置して「開口の奥に見える口内」を表現する。
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    sx = head_size[0] * 0.5
    sy = head_size[1] * 0.5
    sz = head_size[2] * 0.5

    mouth_x = 0.0
    mouth_z = head_center[2] - head_size[2] * 0.25
    mw = head_size[0] * 0.115   # 開口の半幅
    mh = head_size[2] * 0.045   # 開口の半高さ
    depth_r = mh * 1.3          # 奥行き半径(浅すぎるとBooleanが安定しないため一定の厚みを持たせる)

    eval_head = None
    if head_obj:
        try:
            dg = context.evaluated_depsgraph_get()
            eval_head = head_obj.evaluated_get(dg)
        except Exception:
            eval_head = head_obj

    def raycast_point(vx, vz):
        wx = mouth_x + vx
        wz = mouth_z + vz
        if eval_head:
            ray_origin = Vector((wx, head_center[1] - 0.60, wz))
            ray_dir = Vector((0.0, 1.0, 0.0))
            hit, loc, norm, idx = eval_head.ray_cast(ray_origin, ray_dir)
            if hit:
                return loc, norm.normalized()
        norm_x = wx / max(0.01, sx)
        norm_z = (wz - head_center[2]) / max(0.01, sz)
        rad_sq = max(0.02, 1.0 - norm_x * norm_x - norm_z * norm_z)
        wy = head_center[1] - math.sqrt(rad_sq) * sy
        return Vector((wx, wy, wz)), Vector((0.0, -1.0, 0.0))

    anchor_loc, anchor_norm = raycast_point(0.0, 0.0)
    world_up = Vector((0.0, 0.0, 1.0))
    tangent_x = world_up.cross(anchor_norm)
    if tangent_x.length < 1e-6:
        tangent_x = Vector((1.0, 0.0, 0.0))
    tangent_x.normalize()
    tangent_z = anchor_norm.cross(tangent_x).normalized()
    if tangent_z.z < 0.0:
        tangent_z = -tangent_z

    def build_flat_ellipsoid(rx, ry, rz, center, u=18, v=12):
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
        for v_ in bm.verts:
            lt = v_.co.x * rx
            ln = v_.co.y * ry
            lb = v_.co.z * rz
            v_.co = center + tangent_x * lt + anchor_norm * ln + tangent_z * lb
        m = bpy.data.meshes.new(name + "_Tmp")
        bm.to_mesh(m)
        bm.free()
        return m

    # 頭部表面から半分ほど埋め込んだ位置を開口の中心にする(目の眼球と同じ考え方)
    protrusion_f = 0.5
    cutter_center = anchor_loc - anchor_norm * (depth_r * (1.0 - protrusion_f))

    cutter_mesh = build_flat_ellipsoid(mw, depth_r, mh, cutter_center)
    cutter_obj = bpy.data.objects.new(name + "_SocketCutter", cutter_mesh)
    context.collection.objects.link(cutter_obj)

    if head_obj is not None:
        bool_mod = head_obj.modifiers.new(name="MouthSocketBoolean", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = cutter_obj
        # 目のBooleanと同じ理由でEXACTソルバーに変更(FASTだと2つのBooleanが
        # 干渉して法線不整合による亀裂状のシェーディング異常が出ることがあった)
        bool_mod.solver = 'EXACT'
        try:
            bool_index = list(head_obj.modifiers).index(bool_mod)
            if bool_index > 0:
                head_obj.modifiers.move(bool_index, 0)
        except Exception:
            pass

        # その場でBakeして法線を再計算しておく(目と同じ理由。詳細は
        # _apply_boolean_and_fix_normalsを参照)
        _apply_boolean_and_fix_normals(context, head_obj, bool_mod)

        cutter_obj.parent = head_obj
        cutter_obj.matrix_parent_inverse = head_obj.matrix_world.inverted()

    cutter_obj.hide_render = True
    cutter_obj.hide_viewport = True

    # 口内(奥に見える赤い面): カッターよりひと回り小さく、さらに奥へ配置する
    inner_center = anchor_loc - anchor_norm * (depth_r * 0.9)
    inner_mesh = build_flat_ellipsoid(mw * 0.82, depth_r * 0.7, mh * 0.75, inner_center, u=16, v=10)
    inner_mesh.name = name + "_Mesh"
    obj.data = inner_mesh
    bpy.data.meshes.remove(mesh)

    # 口の表情差分シェイプキー(接平面フレーム基準。目と同じ理由でワールド軸ではなく
    # tangent_x/anchor_norm/tangent_zのローカル座標で変形する)
    def to_local(p):
        rel = p - anchor_loc
        return rel.dot(tangent_x), rel.dot(anchor_norm), rel.dot(tangent_z)

    def from_local(lt, ln, lb):
        return anchor_loc + tangent_x * lt + anchor_norm * ln + tangent_z * lb

    try:
        obj.shape_key_add(name="Basis", from_mix=False)

        sk_smile = obj.shape_key_add(name="Smile", from_mix=False)
        for pt in sk_smile.data:
            lt, ln, lb = to_local(pt.co)
            dx = lt / max(0.001, mw)
            lb += (dx * dx) * mh * 0.5
            lt *= 1.1
            pt.co = from_local(lt, ln, lb)

        sk_open = obj.shape_key_add(name="Open", from_mix=False)
        for pt in sk_open.data:
            lt, ln, lb = to_local(pt.co)
            lb *= 1.8
            ln -= mh * 0.6
            pt.co = from_local(lt, ln, lb)

        sk_pout = obj.shape_key_add(name="Pout", from_mix=False)
        for pt in sk_pout.data:
            lt, ln, lb = to_local(pt.co)
            dx = lt / max(0.001, mw)
            lb -= (dx * dx) * mh * 0.4
            pt.co = from_local(lt, ln, lb)
    except Exception:
        pass

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
    # 目(build_chibi_eyes_mesh)の eye_x と同じ係数(0.230)に揃える。
    # かつて目が0.300位置の薄いデカール式だった頃は0.270（目よりやや内側）が
    # ちょうど良かったが、正球方式で目が0.230に内寄せされた今は、旧定数のままだと
    # 眉が目より外側にずれて目の上部と不自然に交差して見えてしまう。
    brow_x = head_size[0] * 0.230
    brow_z = head_center[2] + 0.045  # 正球の目は縦にも大きいため、旧値より少し高く逃がす

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
        rx = 0.038
        rz = 0.006  # より細く自然な眉
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
    Option B: 小さなドット鼻（UV半球廃止）
    - 半径 0.008 の単純円板 → 肌より少し濃いピンクベージュ
    - 鼻は目立たせすぎずに「鼻がある」程度の自然な存在感
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj  = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()

    # 頭部メッシュの鼻突起中心（ボタンノーズ突起: norm_z=-0.25）
    nose_z = head_center[2] - 0.065
    nz     = (nose_z - head_center[2]) / max(0.01, head_size[2] * 0.5)
    ny_sq  = max(0.05, 1.0 - nz * nz)
    y_fac  = 1.0 + max(0.0, -nz) * 0.05
    nose_y = head_center[1] - math.sqrt(ny_sq) * 0.5 * head_size[1] * y_fac - 0.024

    nose_pos = Vector((0.0, nose_y, nose_z))

    # 小さな円板（fan）
    dot_r    = 0.008
    dot_segs = 12
    center_v = bm.verts.new(nose_pos)
    rim_verts = []
    for i in range(dot_segs):
        ang = (i / dot_segs) * 2.0 * math.pi
        vx  = math.cos(ang) * dot_r
        vz  = math.sin(ang) * dot_r * 0.75  # 少し縦を短く
        rim_verts.append(bm.verts.new(nose_pos + Vector((vx, 0.0, vz))))

    bm.verts.ensure_lookup_table()
    for i in range(dot_segs):
        bm.faces.new([center_v, rim_verts[(i + 1) % dot_segs], rim_verts[i]])

    bm.to_mesh(mesh)
    bm.free()

    mod_sol = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod_sol.thickness = 0.004
    mod_sol.offset    = 1.0

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

        # 耳の逃げ穴（実座標系で build_chibi_ears_mesh と同じ耳中心・実サイズを参照し、
        # 楕円形の滑らかなクリアランスで開ける。耳メッシュより一回り大きくして露出を防ぐ）
        ear_ry = 0.065 * 0.9 * 1.05
        ear_rz = 0.065 * 1.05
        ear_cy = -0.02
        ear_cz = hc.z - 0.02
        ear_del = []
        for side in (-1.0, 1.0):
            for v in bm.verts:
                if side * (v.co.x - hc.x) < hsx * 0.30:
                    continue
                dy = (v.co.y - ear_cy) / ear_ry
                dz = (v.co.z - ear_cz) / ear_rz
                if dy * dy + dz * dz < 1.0:
                    ear_del.append(v)
        if ear_del:
            bmesh.ops.delete(bm, geom=list(set(ear_del)), context='VERTS')

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


def build_chibi_outfit_mesh(context, name="Chibi_Outfit", gender="BOY", outfit_type="T_SHIRT", head_ratio=2.2, total_height=1.15):
    """
    衣装メッシュ（全6種類対応）
    T_SHIRT, ONE_PIECE, HOODIE, OVERALLS, KIMONO, COAT

    袖・肩の位置と角度は compute_chibi_body_layout() の実際の肩・肘座標から算出し、
    build_chibi_body_mesh と独立した数値でズレないようにしている。
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    layout = compute_chibi_body_layout(gender, head_ratio, total_height)
    base_z = layout['base_z']
    leg_len = layout['leg_len']
    torso_len = layout['torso_len']

    bm = bmesh.new()

    # 実際の肩→肘ベクトルから袖の角度を算出（固定値ではなく体形に追従）
    shoulder_pos = layout['shoulder']['pos']
    elbow_pos = layout['elbow']['pos']
    arm_dx = elbow_pos.x - shoulder_pos.x
    arm_dz = elbow_pos.z - shoulder_pos.z
    arm_xz_len = max(1e-6, math.sqrt(arm_dx * arm_dx + arm_dz * arm_dz))
    sin_theta = arm_dx / arm_xz_len
    cos_theta = -arm_dz / arm_xz_len
    shoulder_x = shoulder_pos.x
    sh_z = shoulder_pos.z

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
            sh_x = side * shoulder_x
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
            sh_x = side * shoulder_x
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
            sh_x = side * shoulder_x
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
            sh_x = side * shoulder_x
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


def build_chibi_shoes_mesh(context, name="Chibi_Shoes", gender="BOY", head_ratio=2.2, total_height=1.15, foot_spacing=None, shoe_size=(0.10, 0.15, 0.085)):
    """
    コロンとした丸い靴（Mirror）
    foot_spacing 未指定時は compute_chibi_body_layout() の実際の足首X座標を使い、
    体のプロポーションが変わっても靴が足首の真下からズレないようにする。
    """
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    if foot_spacing is None:
        layout = compute_chibi_body_layout(gender, head_ratio, total_height)
        foot_spacing = layout['ankle']['pos'].x

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
    ears_obj = build_chibi_ears_mesh(context, f"{name}_Ears", (0, 0, head_center_z), head_size, head_obj=head_obj)
    eyes_obj = build_chibi_eyes_mesh(context, f"{name}_Eyes", gender, eye_style, eye_scale, (0, 0, head_center_z), head_size, head_obj=head_obj)
    eyebrow_obj = build_chibi_eyebrows_mesh(context, f"{name}_Eyebrows", eyebrow_style, (0, 0, head_center_z), head_size)
    nose_obj = build_chibi_nose_mesh(context, f"{name}_Nose", (0, 0, head_center_z), head_size)
    mouth_obj = build_chibi_mouth_mesh(context, f"{name}_Mouth", (0, 0, head_center_z), head_size, head_obj=head_obj)

    # 単一統合ヘアスタイルメッシュ生成（継ぎ目なし・耳逃げ穴クリアランス）
    hair_obj = build_chibi_hair_mesh(context, f"{name}_Hair", gender, hair_style, (0, 0, head_center_z), head_size)

    outfit_obj = build_chibi_outfit_mesh(context, f"{name}_Outfit", gender, outfit_type, head_ratio, total_height)
    shoes_obj = build_chibi_shoes_mesh(context, f"{name}_Shoes", gender, head_ratio, total_height)
    acc_obj = build_chibi_accessories_mesh(context, f"{name}_Accessory", accessory, (0, 0, head_center_z), head_size)

    # 3. マテリアルの生成と適用
    mat_skin = create_chibi_character_shader(f"{name}_Skin_Mat", "SKIN", skin_color, 0.6, seed)
    mat_hair = create_chibi_character_shader(f"{name}_Hair_Mat", "HAIR", hair_color, 0.45, seed)
    mat_top = create_chibi_character_shader(f"{name}_ClothTop_Mat", "CLOTH_TOP", cloth_top_color, 0.7, seed, pattern=pattern)
    mat_button = create_chibi_character_shader(f"{name}_Button_Mat", "BUTTON", (0.88, 0.80, 0.45, 1.0), 0.3, seed)
    
    # 三面図に忠実な瞳カラー（男の子: ディープエスプレッソ、女の子: 鮮やかなリッチアンバー）
    eye_base_color = (0.12, 0.08, 0.06, 1.0) if gender == "BOY" else (0.68, 0.36, 0.12, 1.0)
    # 3層構成: slot0 = 白目玉、slot1 = 瞳・虹彩（Pupil/Iris）、slot2 = ハイライト
    mat_sclera = create_chibi_character_shader(f"{name}_Sclera_Mat", "EYE_SCLERA", (0.97, 0.97, 0.98, 1.0), 0.25, seed)
    mat_eye = create_chibi_character_shader(f"{name}_Eye_Pupil_Mat", "EYE", eye_base_color, 0.10, seed)
    mat_eye_highlight = create_chibi_character_shader(f"{name}_Eye_Highlight_Mat", "EYE_HIGHLIGHT", (1.0, 1.0, 1.0, 1.0), 0.05, seed)
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
    eyes_obj.data.materials.append(mat_sclera)          # slot0: 白目玉（White eyeball）
    eyes_obj.data.materials.append(mat_eye)             # slot1: 瞳・虹彩（Pupil/Iris）
    eyes_obj.data.materials.append(mat_eye_highlight)   # slot2: ハイライト（キャッチライト）
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
