import bpy
import bmesh
import math
import mathutils
from mathutils import Vector, Matrix, Euler
import random

# ==============================================================================
# 1. 高度な立体成形・樋状カーブ葉ブレード (Curved 3D Leaf Blade)
# ==============================================================================
def build_curved_leaf_blade(
    bm,
    base_pos,
    length=0.35,
    width=0.09,
    curl=0.35,       # 長さ方向のしなり・放物線カーブ (0.0〜1.0)
    v_cup=0.45,      # 幅方向の樋（とい）状・V字深さ (0.0〜1.0)
    shape='OVAL',    # 'OVAL'(広葉), 'LANCEOLATE'(披針形・細長), 'FERN_PINNA'(シダ羽片)
    rot_euler=None,
    mat_idx=0,
    uv_layer=None
):
    """
    【リアル立体樋状カーブ葉】
    中央の主脈（Midrib）と左右の葉身がV字・樋状に折れ曲がり、
    先端にかけて放物線状に優雅にしなる立体メッシュ（6〜8ポリゴン）。
    日光下で左右に明暗コントラストが生まれ、板ポリゴン感が完全に消失。
    """
    rot_mat = rot_euler.to_matrix().to_4x4() if rot_euler else Matrix.Identity(4)
    
    # 葉の輪郭プロファイル関数 (t: 0.0=基部 〜 1.0=先端)
    def get_width_factor(t):
        if shape == 'OVAL':
            # 柔らかな卵形・楕円（基部狭く、中央〜やや先端寄りで最大幅、先端は丸みを帯びて収束）
            return math.sin(t * math.pi * 0.88 + 0.12) * math.pow(1.0 - t * 0.5, 0.4)
        elif shape == 'FERN_PINNA':
            # シダ小葉（基部が最も広く、先端へ直線的・わずかにアーチを描いて先細る）
            return (1.0 - t * 0.85) * (1.0 + math.sin(t * math.pi) * 0.25)
        else: # LANCEOLATE (披針形)
            # 細長くシャープ（中央で最大幅）
            return math.sin(t * math.pi)

    # 3セグメント（断面4箇所: t=0.0, 0.35, 0.72）
    t_steps = [0.0, 0.35, 0.72]
    cross_sections = [] # 各断面 [v_left, v_mid, v_right]

    for t in t_steps:
        # 長さ方向のカーブ（重力しなり）
        z_co = t * length
        # curl に応じて外側・下側へ放物線状に落ち込む
        drop_y = (t ** 2.0) * (length * 0.38 * curl)

        # 幅とV字の深さ
        w_factor = max(0.08, get_width_factor(t))
        w = width * w_factor * 0.5
        cup_depth = w * 0.55 * v_cup # 主脈が左右より沈み込む深さ

        # ローカル座標系: X=幅方向, Y=厚み/しなり方向, Z=長さ方向
        p_mid   = Vector((0.0, drop_y - cup_depth, z_co))
        p_left  = Vector((-w,  drop_y,             z_co))
        p_right = Vector(( w,  drop_y,             z_co))

        # 回転・配置
        v_m = bm.verts.new(base_pos + rot_mat @ p_mid)
        v_l = bm.verts.new(base_pos + rot_mat @ p_left)
        v_r = bm.verts.new(base_pos + rot_mat @ p_right)

        cross_sections.append((v_l, v_m, v_r, t))

    # 先端頂点 (t=1.0)
    drop_y_tip = (1.0 ** 2.0) * (length * 0.42 * curl)
    p_tip = Vector((0.0, drop_y_tip, length))
    v_tip = bm.verts.new(base_pos + rot_mat @ p_tip)

    # 面の構築（四角形メッシュで滑らかに接続）
    # 段ごとの左右四角形
    for s in range(len(cross_sections) - 1):
        l1, m1, r1, t1 = cross_sections[s]
        l2, m2, r2, t2 = cross_sections[s + 1]

        # 左半面
        f_left = bm.faces.new((l1, m1, m2, l2))
        f_left.material_index = mat_idx
        f_left.smooth = True

        # 右半面
        f_right = bm.faces.new((m1, r1, r2, m2))
        f_right.material_index = mat_idx
        f_right.smooth = True

        if uv_layer:
            # UVマッピング (U: 0.0=左端, 0.5=主脈, 1.0=右端 / V: 0.0=根元, 1.0=先端)
            for loop, uv in zip(f_left.loops, [(0.0, t1), (0.5, t1), (0.5, t2), (0.0, t2)]):
                loop[uv_layer].uv = uv
            for loop, uv in zip(f_right.loops, [(0.5, t1), (1.0, t1), (1.0, t2), (0.5, t2)]):
                loop[uv_layer].uv = uv

    # 先端三角形 (左右2枚)
    last_l, last_m, last_r, last_t = cross_sections[-1]
    f_tip_l = bm.faces.new((last_l, last_m, v_tip))
    f_tip_l.material_index = mat_idx
    f_tip_l.smooth = True

    f_tip_r = bm.faces.new((last_m, last_r, v_tip))
    f_tip_r.material_index = mat_idx
    f_tip_r.smooth = True

    if uv_layer:
        for loop, uv in zip(f_tip_l.loops, [(0.0, last_t), (0.5, last_t), (0.5, 1.0)]):
            loop[uv_layer].uv = uv
        for loop, uv in zip(f_tip_r.loops, [(0.5, last_t), (1.0, last_t), (0.5, 1.0)]):
            loop[uv_layer].uv = uv

    return [cs[1] for cs in cross_sections] + [v_tip]


# ==============================================================================
# 2. 幹・細枝チューブ (Stem & Branch Tube)
# ==============================================================================
def build_stem_tube(bm, pts, radii, segments=5, mat_idx=1, uv_layer=None):
    """【木製細枝チューブ】滑らかな断面リング押し出し"""
    if len(pts) < 2:
        return
    ring_verts = []
    up = Vector((0, 0, 1))

    for i, pt in enumerate(pts):
        if i < len(pts) - 1:
            dir_norm = (pts[i+1] - pt).normalized()
        else:
            dir_norm = (pt - pts[i-1]).normalized()

        if abs(dir_norm.dot(up)) > 0.98:
            side1 = dir_norm.cross(Vector((1, 0, 0))).normalized()
        else:
            side1 = dir_norm.cross(up).normalized()
        side2 = dir_norm.cross(side1).normalized()

        r = radii[i]
        ring = []
        for s in range(segments):
            ang = s * (2.0 * math.pi / segments)
            off = side1 * (math.cos(ang) * r) + side2 * (math.sin(ang) * r)
            ring.append(bm.verts.new(pt + off))
        ring_verts.append(ring)

    for i in range(len(pts) - 1):
        for s in range(segments):
            s_next = (s + 1) % segments
            f = bm.faces.new((ring_verts[i][s], ring_verts[i][s_next],
                              ring_verts[i+1][s_next], ring_verts[i+1][s]))
            f.material_index = mat_idx
            f.smooth = True


# ==============================================================================
# 3. シダのゼンマイ新芽 (Fiddlehead / Crozier)
# ==============================================================================
def build_fiddlehead(bm, base_pos, height=0.45, scale=1.0, base_angle=0.0, mat_idx=1, seed=0):
    """
    【シダのゼンマイ芽】
    根元から立ち上がり、先端が対数螺旋（らせん）状にクルリと巻いた本物のシダ新芽。
    シダの中心クラウンに配置され、植物のリアルさを圧倒的に高める。
    """
    rng = random.Random(seed)
    spiral_pts = []
    radii = []

    # 1. 立ち上がりステム (5点)
    stem_steps = 5
    for i in range(stem_steps):
        t = i / float(stem_steps)
        sz = t * height * 0.65
        sx = base_pos.x + math.cos(base_angle) * (t * 0.05)
        sy = base_pos.y + math.sin(base_angle) * (t * 0.05)
        sz = base_pos.z + sz
        spiral_pts.append(Vector((sx, sy, sz)))
        radii.append((0.022 - t * 0.008) * scale)

    # 2. カール螺旋（2回転の対数スパイラル、14点）
    head_center = spiral_pts[-1]
    curl_dir = Vector((math.cos(base_angle), math.sin(base_angle), 0.0))

    spiral_steps = 14
    theta_start = 0.0
    theta_end = math.pi * 3.5 # 約1.75回転

    for step in range(1, spiral_steps + 1):
        st = step / float(spiral_steps)
        theta = theta_start + st * (theta_end - theta_start)
        r_spiral = (0.055 * math.exp(-st * 1.4)) * scale
        
        spiral_local_x = math.sin(theta) * r_spiral
        spiral_local_z = (1.0 - math.cos(theta)) * r_spiral * 0.85

        pt = head_center + curl_dir * spiral_local_x + Vector((0, 0, spiral_local_z))
        spiral_pts.append(pt)
        radii.append(max(0.003 * scale, (0.012 - st * 0.009) * scale))

    build_stem_tube(bm, spiral_pts, radii, segments=4, mat_idx=mat_idx)


# ==============================================================================
# 4. リアルシダ羽状複葉 (Pinnate Fern Frond)
# ==============================================================================
def build_fern_frond(
    bm,
    base_pos,
    frond_len=0.9,
    base_angle=0.0,
    mat_idx=0,
    stem_mat_idx=1,
    uv_layer=None,
    seed=0
):
    """
    【リアルシダ羽状複葉】
    美しくアーチを描く中肋軸に沿って、左右交互に立体樋状小葉（Pinna）が密に展開。
    重力によるしなりと微小なツイストで自然な陰影を生み出す。
    """
    rng = random.Random(seed)
    segs = 10
    arch_pts = []

    arch_power = rng.uniform(1.8, 2.2)
    for i in range(segs + 1):
        t = i / float(segs)
        dist = t * frond_len
        drop = -(t ** arch_power) * (frond_len * 0.40) + math.sin(t * math.pi * 0.9) * (frond_len * 0.22)
        x = base_pos.x + math.cos(base_angle) * dist
        y = base_pos.y + math.sin(base_angle) * dist
        z = base_pos.z + drop
        arch_pts.append(Vector((x, y, z)))

    radii = [(1.0 - (i / float(segs)) * 0.75) * 0.018 for i in range(segs + 1)]
    build_stem_tube(bm, arch_pts, radii, segments=4, mat_idx=stem_mat_idx, uv_layer=uv_layer)

    # 左右の小葉（羽片）展開：中肋の接線に沿って水平〜自然な傾斜で展開
    up_vec = Vector((0, 0, 1))
    for i in range(1, segs):
        pt = arch_pts[i]
        t = i / float(segs)
        
        # 中肋の接線ベクトル (tangent)
        tangent = (arch_pts[min(segs, i + 1)] - arch_pts[i - 1]).normalized()
        # 左右の展開ベクトル (normal to tangent and up)
        normal_side = tangent.cross(up_vec).normalized()
        # 葉の表面上向きベクトル
        leaf_up = normal_side.cross(tangent).normalized()

        size_profile = math.sin(t * math.pi * 0.88 + 0.12)
        pinna_len = max(0.06, (frond_len * 0.38) * size_profile * rng.uniform(0.94, 1.06))
        pinna_w = pinna_len * 0.28

        for side in (-1.0, 1.0):
            # 軸から左右外向きへ前傾約60度で展開
            dir_pinna = (normal_side * side * 0.85 + tangent * 0.45).normalized()
            # 重力による緩やかな外側下がり
            dir_pinna.z -= (0.15 + t * 0.25)
            dir_pinna = dir_pinna.normalized()

            # 局所座標系マトリクスを構築
            pinna_side = tangent * side
            pinna_normal = dir_pinna.cross(pinna_side).normalized()
            rot_mat = Matrix([
                [pinna_side.x, pinna_normal.x, dir_pinna.x, 0],
                [pinna_side.y, pinna_normal.y, dir_pinna.y, 0],
                [pinna_side.z, pinna_normal.z, dir_pinna.z, 0],
                [0, 0, 0, 1]
            ])
            rot = rot_mat.to_euler()

            build_curved_leaf_blade(
                bm,
                base_pos=pt,
                length=pinna_len,
                width=pinna_w,
                curl=0.40,
                v_cup=0.45,
                shape='FERN_PINNA',
                rot_euler=rot,
                mat_idx=mat_idx,
                uv_layer=uv_layer
            )


# ==============================================================================
# 5. ふんわり広葉クラスタ (Dense Foliage Cluster)
# ==============================================================================
def build_dense_foliage_clump(
    bm,
    center_pos,
    size_x=1.0,
    size_y=1.0,
    size_z=0.8,
    layers=4,
    blades_per_layer=14,
    leaf_scale=1.0,
    seed=0,
    mat_idx=0,
    uv_layer=None
):
    """
    【ふんわり広葉樹冠クラスタ】
    刺々しいトゲを完全排除し、V字カーブと重力しなりを持つ立体広葉（OVAL）が
    ドーム状・球状に多層展開。隙間からの木漏れ日と豊かな陰影を実現。
    """
    rng = random.Random(seed)

    for l in range(layers):
        t_layer = l / float(max(1, layers - 1))
        layer_z = center_pos.z + t_layer * (size_z * 0.70)
        
        pitch = (1.0 - t_layer * 0.70) * (math.pi * 0.42)
        layer_rad_x = (1.0 - t_layer * 0.25) * (size_x * 0.45)
        layer_rad_y = (1.0 - t_layer * 0.25) * (size_y * 0.45)
        
        leaf_len = (size_z * 0.50) * leaf_scale * rng.uniform(0.85, 1.15)
        leaf_w = leaf_len * 0.38

        b_count = int(blades_per_layer * (1.0 - t_layer * 0.20))
        for b in range(b_count):
            ang = b * (2.0 * math.pi / b_count) + rng.uniform(-0.18, 0.18) + (l * 0.45)
            bx = center_pos.x + math.cos(ang) * (layer_rad_x * 0.5)
            by = center_pos.y + math.sin(ang) * (layer_rad_y * 0.5)
            bz = layer_z + rng.uniform(-0.02, 0.02)
            b_pos = Vector((bx, by, bz))

            rot = Euler((
                pitch + rng.uniform(-0.12, 0.12),
                rng.uniform(-0.20, 0.20),
                ang + rng.uniform(-0.10, 0.10)
            ), 'XYZ')

            build_curved_leaf_blade(
                bm,
                base_pos=b_pos,
                length=leaf_len,
                width=leaf_w,
                curl=rng.uniform(0.30, 0.55),
                v_cup=rng.uniform(0.40, 0.60),
                shape='OVAL',
                rot_euler=rot,
                mat_idx=mat_idx,
                uv_layer=uv_layer
            )


# ==============================================================================
# 6. メイン BMesh 生成エンジン (build_bush_mesh)
# ==============================================================================
def build_bush_mesh(
    bm,
    bush_type="ROUND_BUSH",
    foliage_style="LEAF_CARDS",
    size_x=1.2,
    size_y=1.2,
    size_z=0.9,
    density=24,
    leaf_size=0.32,
    include_fiddleheads=True,
    seed=0,
    uv_layer=None
):
    """
    低木・茂み・シダ植物のプロシージャル BMesh 生成エンジン
    - FERN_CLUMP: リアル羽状複葉 ＋ 中央ゼンマイ新芽（Fiddlehead）
    - ROUND_BUSH: 中心の幹枝 ＋ ふんわり多層立体広葉クラスタ
    - WILD_SHRUB: 露出した荒々しい細枝 ＋ 枝先の密集立体葉
    - HEDGE_ROW: 連なる生垣ブロック
    """
    rng = random.Random(seed)
    half_x = size_x * 0.5
    half_y = size_y * 0.5

    if bush_type == "FERN_CLUMP":
        # 🌿 シダ植物の株（リアル羽状複葉 + ゼンマイ新芽）
        frond_count = max(8, int(density * 0.60))
        frond_len = max(size_x, size_y) * 0.75
        
        for fi in range(frond_count):
            ang = fi * (2.0 * math.pi / frond_count) + rng.uniform(-0.15, 0.15)
            f_len = frond_len * rng.uniform(0.85, 1.15)
            base_p = Vector((rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04), size_z * 0.05))
            build_fern_frond(
                bm, base_p, frond_len=f_len, base_angle=ang,
                mat_idx=0, stem_mat_idx=1, uv_layer=uv_layer,
                seed=seed + fi * 31
            )

        if include_fiddleheads:
            fiddle_count = max(2, int(frond_count * 0.35))
            for fdi in range(fiddle_count):
                fd_ang = fdi * (2.0 * math.pi / fiddle_count) + rng.uniform(-0.25, 0.25)
                fd_pos = Vector((math.cos(fd_ang) * 0.04, math.sin(fd_ang) * 0.04, size_z * 0.03))
                build_fiddlehead(
                    bm, fd_pos, height=size_z * 0.45, scale=size_z * 0.85,
                    base_angle=fd_ang, mat_idx=1, seed=seed + fdi * 53
                )

    elif bush_type == "HEDGE_ROW":
        # 🧱 生垣ブロック（連なる多層立体広葉クラスタ）
        num_clumps_x = max(2, int(round(size_x / 0.8)))
        num_clumps_y = max(1, int(round(size_y / 0.8)))
        for ix in range(num_clumps_x):
            for iy in range(num_clumps_y):
                cx = -half_x + (ix + 0.5) * (size_x / num_clumps_x)
                cy = -half_y + (iy + 0.5) * (size_y / max(1, num_clumps_y))
                c_pos = Vector((cx, cy, 0.0))
                build_dense_foliage_clump(
                    bm, c_pos,
                    size_x=size_x / num_clumps_x * 1.35,
                    size_y=size_y / max(1, num_clumps_y) * 1.35,
                    size_z=size_z, layers=4, blades_per_layer=12,
                    seed=seed + ix * 10 + iy, mat_idx=0, uv_layer=uv_layer
                )

    elif bush_type == "WILD_SHRUB":
        # 🌿 野生の藪（四方に伸びる木製細枝 ＋ 枝先の多層立体葉クラスタ）
        stem_count = max(5, int(density * 0.30))
        for si in range(stem_count):
            ang = si * (2.0 * math.pi / stem_count) + rng.uniform(-0.25, 0.25)
            reach = rng.uniform(0.70, 1.05)
            s_len = max(size_x, size_y) * 0.48 * reach
            s_h = size_z * rng.uniform(0.55, 0.88)

            mid_p = Vector((math.cos(ang) * s_len * 0.5, math.sin(ang) * s_len * 0.5, s_h * 0.42))
            tip_p = Vector((math.cos(ang) * s_len, math.sin(ang) * s_len, s_h))
            pts = [Vector((0, 0, 0)), mid_p, tip_p]
            radii = [0.035 * (size_z / 0.9), 0.022 * (size_z / 0.9), 0.012 * (size_z / 0.9)]
            build_stem_tube(bm, pts, radii, segments=5, mat_idx=1, uv_layer=uv_layer)

            build_dense_foliage_clump(
                bm, tip_p,
                size_x=leaf_size * 2.4, size_y=leaf_size * 2.4, size_z=leaf_size * 1.9,
                layers=3, blades_per_layer=7,
                seed=seed + si * 20, mat_idx=0, uv_layer=uv_layer
            )

    else:
        # 🌳 ROUND_BUSH（丸型低木：中心の細幹 ＋ ふんわり多層立体広葉クラスタ）
        stem_pts = [Vector((0, 0, 0)), Vector((0, 0, size_z * 0.35))]
        build_stem_tube(bm, stem_pts, [0.040, 0.022], segments=5, mat_idx=1, uv_layer=uv_layer)

        build_dense_foliage_clump(
            bm, Vector((0, 0, 0)),
            size_x=size_x, size_y=size_y, size_z=size_z,
            layers=5, blades_per_layer=16,
            seed=seed, mat_idx=0, uv_layer=uv_layer
        )

        sub_count = 4
        for sbi in range(sub_count):
            s_ang = sbi * (2.0 * math.pi / sub_count) + rng.uniform(-0.2, 0.2)
            s_dist = min(half_x, half_y) * 0.38
            s_pos = Vector((math.cos(s_ang) * s_dist, math.sin(s_ang) * s_dist, size_z * 0.18))
            build_dense_foliage_clump(
                bm, s_pos,
                size_x=size_x * 0.65, size_y=size_y * 0.65, size_z=size_z * 0.75,
                layers=3, blades_per_layer=8,
                seed=seed + sbi * 37, mat_idx=0, uv_layer=uv_layer
            )

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm.verts[:]


# ==============================================================================
# 7. 樹冠ハイブリッド法線転送 (Foliage Spherical Normal Blending)
# ==============================================================================
def apply_bush_spherical_normals(obj, leaf_mat_idx=0, blend_factor=0.65):
    """
    【樹冠ハイブリッド法線転送】
    個々の葉の立体的なハイライト（主脈の明暗）を残しつつ、
    茂み全体の中心から外向きに放射する球状法線をブレンド（blend_factor=0.65）。
    板ポリゴン特有のチラつきを完全に消し去り、ふんわりとしたボリューム陰影を実現。
    """
    if not obj or obj.type != 'MESH':
        return
    mesh = obj.data
    mesh.calc_normals()
    center = Vector((0, 0, obj.dimensions.z * 0.40))

    custom_normals = []
    for poly in mesh.polygons:
        for loop_idx in poly.loop_indices:
            vert_idx = mesh.loops[loop_idx].vertex_index
            v_co = mesh.vertices[vert_idx].co
            geom_normal = mesh.vertices[vert_idx].normal

            if poly.material_index == leaf_mat_idx:
                dir_vec = (v_co - center).normalized()
                hybrid_normal = (geom_normal * (1.0 - blend_factor) + dir_vec * blend_factor).normalized()
                custom_normals.append(hybrid_normal)
            else:
                custom_normals.append(geom_normal)

    mesh.use_auto_smooth = True
    mesh.normals_split_custom_set(custom_normals)
