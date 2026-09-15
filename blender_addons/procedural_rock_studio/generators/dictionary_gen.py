import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

def create_box_mesh(bm, center=(0, 0, 0), size=(1, 1, 1), mat_idx=0):
    """安定・確実な直方体生成ヘルパー（マテリアルインデックス即時割当）"""
    cx, cy, cz = center
    sx, sy, sz = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5

    v0 = bm.verts.new((cx - sx, cy - sy, cz - sz))
    v1 = bm.verts.new((cx + sx, cy - sy, cz - sz))
    v2 = bm.verts.new((cx + sx, cy + sy, cz - sz))
    v3 = bm.verts.new((cx - sx, cy + sy, cz - sz))
    v4 = bm.verts.new((cx - sx, cy - sy, cz + sz))
    v5 = bm.verts.new((cx + sx, cy - sy, cz + sz))
    v6 = bm.verts.new((cx + sx, cy + sy, cz + sz))
    v7 = bm.verts.new((cx - sx, cy + sy, cz + sz))

    faces = [
        (v0, v1, v2, v3), # -Z
        (v4, v7, v6, v5), # +Z
        (v0, v4, v5, v1), # -Y
        (v2, v6, v7, v3), # +Y
        (v0, v3, v7, v4), # -X
        (v1, v5, v6, v2), # +X
    ]
    created = []
    for f_verts in faces:
        f = bm.faces.new(f_verts)
        f.material_index = mat_idx
        created.append(f)
    return created


def build_dictionary_mesh(
    bm,
    width=0.16,
    height=0.23,
    thickness=0.065,
    rib_count=4,
    cover_overhang=0.0035,
    cover_thickness=0.0035,
    spine_curvature=0.22,
    fore_edge_hollow=0.14,
    has_ribbon=True,
    seed=0
):
    """
    中性的な辞書（ハードカバー本）プロシージャルメッシュ生成
    マテリアルインデックス:
      0: M_Dictionary_Cover (表紙・背表紙・背バンド)
      1: M_Dictionary_Pages (ページブロック・小口)
      2: M_Dictionary_Ribbon (しおり紐)
    """
    random.seed(seed)

    w = max(0.08, width)
    h = max(0.12, height)
    th = max(0.02, thickness)
    ct = max(0.002, cover_thickness)
    oh = max(0.002, cover_overhang)

    # 背表紙の丸みと小口の窪み量
    spine_arch_x = th * spine_curvature
    hollow_x = th * fore_edge_hollow
    joint_x = spine_arch_x * 0.45

    # -------------------------------------------------------------
    # 1. ページブロック (Page Block / Text Block) -> Material Index 1
    # -------------------------------------------------------------
    segments_z = 12
    segments_y = 10
    slices_x = 8

    grid = []
    for ix in range(slices_x + 1):
        u_x = ix / float(slices_x) # 0.0 (背) -> 1.0 (前小口)
        slice_plane = []
        for iy in range(segments_y + 1):
            u_y = iy / float(segments_y) # 0.0 (地 -Y) -> 1.0 (天 +Y)
            cur_y = -h * 0.5 + u_y * h
            row_z = []
            for iz in range(segments_z + 1):
                u_z = iz / float(segments_z) # 0.0 (-Z) -> 1.0 (+Z)
                cur_z = -th * 0.5 + u_z * th
                
                norm_z = (u_z - 0.5) * 2.0
                hollow_factor = max(0.0, 1.0 - (norm_z * norm_z))

                spine_convex = (1.0 - u_x) * (-spine_arch_x * 0.5 * (1.0 - norm_z * norm_z))
                fore_concave = u_x * (-hollow_x * hollow_factor)
                cur_x = (u_x * w) + spine_convex + fore_concave

                v = bm.verts.new((cur_x, cur_y, cur_z))
                row_z.append(v)
            slice_plane.append(row_z)
        grid.append(slice_plane)

    # 前小口 (+X)
    for iy in range(segments_y):
        for iz in range(segments_z):
            v1 = grid[slices_x][iy][iz]
            v2 = grid[slices_x][iy + 1][iz]
            v3 = grid[slices_x][iy + 1][iz + 1]
            v4 = grid[slices_x][iy][iz + 1]
            f = bm.faces.new((v1, v2, v3, v4))
            f.material_index = 1

    # 天面 (+Y)
    for ix in range(slices_x):
        for iz in range(segments_z):
            v1 = grid[ix][segments_y][iz]
            v2 = grid[ix][segments_y][iz + 1]
            v3 = grid[ix + 1][segments_y][iz + 1]
            v4 = grid[ix + 1][segments_y][iz]
            f = bm.faces.new((v1, v2, v3, v4))
            f.material_index = 1

    # 地面 (-Y)
    for ix in range(slices_x):
        for iz in range(segments_z):
            v1 = grid[ix][0][iz]
            v2 = grid[ix + 1][0][iz]
            v3 = grid[ix + 1][0][iz + 1]
            v4 = grid[ix][0][iz + 1]
            f = bm.faces.new((v1, v2, v3, v4))
            f.material_index = 1

    # 背面 (X=0)
    for iy in range(segments_y):
        for iz in range(segments_z):
            v1 = grid[0][iy][iz]
            v2 = grid[0][iy][iz + 1]
            v3 = grid[0][iy + 1][iz + 1]
            v4 = grid[0][iy + 1][iz]
            f = bm.faces.new((v1, v2, v3, v4))
            f.material_index = 1

    # 上下接着面
    for ix in range(slices_x):
        for iy in range(segments_y):
            # +Z
            v1 = grid[ix][iy][segments_z]
            v2 = grid[ix + 1][iy][segments_z]
            v3 = grid[ix + 1][iy + 1][segments_z]
            v4 = grid[ix][iy + 1][segments_z]
            f = bm.faces.new((v1, v2, v3, v4))
            f.material_index = 1

            # -Z
            v1_b = grid[ix][iy][0]
            v2_b = grid[ix][iy + 1][0]
            v3_b = grid[ix + 1][iy + 1][0]
            v4_b = grid[ix + 1][iy][0]
            f_b = bm.faces.new((v1_b, v2_b, v3_b, v4_b))
            f_b.material_index = 1

    # -------------------------------------------------------------
    # 2. ハードカバー (Hardcover Case) -> Material Index 0
    # -------------------------------------------------------------
    cover_w = w + oh - joint_x
    cover_h = h + (oh * 2.0)
    cover_center_x = joint_x + (cover_w * 0.5)

    # 2-A: 表表紙 (Front Cover: +Z)
    create_box_mesh(
        bm,
        center=(cover_center_x, 0, (th * 0.5) + (ct * 0.5)),
        size=(cover_w, cover_h, ct),
        mat_idx=0
    )

    # 2-B: 裏表紙 (Back Cover: -Z)
    create_box_mesh(
        bm,
        center=(cover_center_x, 0, -(th * 0.5) - (ct * 0.5)),
        size=(cover_w, cover_h, ct),
        mat_idx=0
    )

    # 2-C: 丸背 (Curved Spine)
    spine_h = cover_h
    spine_total_th = th + (ct * 2.0)
    spine_segs_z = 16
    spine_rings = []
    for iy in range(segments_y + 1):
        u_y = iy / float(segments_y)
        cur_y = -spine_h * 0.5 + u_y * spine_h
        ring = []
        for iz in range(spine_segs_z + 1):
            u_z = iz / float(spine_segs_z)
            angle = -math.pi * 0.5 + (u_z * math.pi)
            cur_z = math.sin(angle) * (spine_total_th * 0.5)
            cur_x = -math.cos(angle) * spine_arch_x + joint_x * (1.0 - math.cos(angle))
            v = bm.verts.new((cur_x, cur_y, cur_z))
            ring.append(v)
        spine_rings.append(ring)

    for iy in range(segments_y):
        for iz in range(spine_segs_z):
            v1 = spine_rings[iy][iz]
            v2 = spine_rings[iy][iz + 1]
            v3 = spine_rings[iy + 1][iz + 1]
            v4 = spine_rings[iy + 1][iz]
            f = bm.faces.new((v1, v2, v3, v4))
            f.material_index = 0

    # 2-D: 背バンド / リブ (Raised Bands on Spine)
    if rib_count > 0:
        band_th = max(0.003, spine_arch_x * 0.18)
        band_width = max(0.005, h * 0.035)
        rib_margin = spine_h * 0.16
        rib_usable_h = spine_h - (rib_margin * 2.0)
        rib_step = rib_usable_h / float(max(1, rib_count - 1)) if rib_count > 1 else 0

        for r in range(rib_count):
            cur_rib_y = -spine_h * 0.5 + rib_margin + (r * rib_step) if rib_count > 1 else 0.0
            rib_ring_a = []
            rib_ring_b = []
            for iz in range(spine_segs_z + 1):
                u_z = iz / float(spine_segs_z)
                angle = -math.pi * 0.5 + (u_z * math.pi)
                cur_z = math.sin(angle) * (spine_total_th * 0.5 + band_th * 0.4)
                cur_x = -math.cos(angle) * (spine_arch_x + band_th) + joint_x * (1.0 - math.cos(angle))
                
                va = bm.verts.new((cur_x, cur_rib_y - band_width * 0.5, cur_z))
                vb = bm.verts.new((cur_x, cur_rib_y + band_width * 0.5, cur_z))
                rib_ring_a.append(va)
                rib_ring_b.append(vb)
            
            for iz in range(spine_segs_z):
                v1 = rib_ring_a[iz]
                v2 = rib_ring_a[iz + 1]
                v3 = rib_ring_b[iz + 1]
                v4 = rib_ring_b[iz]
                f = bm.faces.new((v1, v2, v3, v4))
                f.material_index = 0

    # -------------------------------------------------------------
    # 3. しおり紐 (Ribbon Bookmark) -> Material Index 2
    # -------------------------------------------------------------
    if has_ribbon:
        rib_w = max(0.004, w * 0.045)
        ribbon_pts = [
            Vector((0.01, h * 0.48, th * 0.1)),
            Vector((w * 0.35, h * 0.35, th * 0.05)),
            Vector((w * 0.85, -h * 0.15, 0.0)),
            Vector((w + oh * 1.5, -h * 0.52, -th * 0.2)),
            Vector((w + oh * 2.0, -h * 0.65, -th * 0.48)),
            Vector((w + oh * 1.2, -h * 0.72, -th * 0.5 - ct))
        ]

        subdiv = 24
        spline_pts = []
        for i in range(subdiv):
            t = i / float(subdiv - 1)
            idx = t * (len(ribbon_pts) - 1)
            i0 = int(idx)
            i1 = min(len(ribbon_pts) - 1, i0 + 1)
            frac = idx - i0
            p = ribbon_pts[i0].lerp(ribbon_pts[i1], frac)
            p.x += math.sin(t * math.pi * 3.0) * 0.003
            spline_pts.append(p)

        prev_v_left = None
        prev_v_right = None
        for i, pt in enumerate(spline_pts):
            v_l = bm.verts.new((pt.x - rib_w * 0.5, pt.y, pt.z))
            v_r = bm.verts.new((pt.x + rib_w * 0.5, pt.y, pt.z))
            if prev_v_left and prev_v_right:
                f = bm.faces.new((prev_v_left, prev_v_right, v_r, v_l))
                f.material_index = 2
            prev_v_left = v_l
            prev_v_right = v_r

    # -------------------------------------------------------------
    # 4. 接地調整 (机の上に平置き: 底面 Z = 0 に合わせる)
    # -------------------------------------------------------------
    min_z = min(v.co.z for v in bm.verts)
    for v in bm.verts:
        v.co.z -= min_z

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm.verts[:]


def sample_random_dictionary_specs(seed=0):
    """ランダムな中性的辞書パラメータをサンプリング"""
    rng = random.Random(seed)

    # 幅 13cm ~ 21cm
    w = round(rng.uniform(0.13, 0.21), 3)
    # アスペクト比 1.3 ~ 1.55
    aspect = rng.uniform(1.30, 1.52)
    h = round(w * aspect, 3)
    # 厚み: 3.5cm (中型辞書) ~ 11.5cm (超極厚大辞書・百科事典)
    th = round(rng.uniform(0.038, 0.115), 3)
    # リブ本数: 3, 4, 5
    ribs = rng.choice([3, 4, 5])
    # カラー
    colors = ['NAVY', 'BURGUNDY', 'FOREST', 'CHARCOAL', 'AMBER']
    color = rng.choice(colors)
    # しおり紐の有無
    ribbon = rng.random() < 0.85
    # 紙の年季・黄ばみ度 (0.40 ~ 0.85: 味わい深いヴィンテージ古書)
    aging = round(rng.uniform(0.40, 0.85), 2)
    # 謎文字・古代グリフ刻印 (約88%で付与、金箔/銀箔/空押し)
    has_runes = rng.random() < 0.88
    rune_int = round(rng.uniform(0.65, 0.95), 2)
    foil = rng.choice(['GOLD', 'GOLD', 'SILVER', 'DEBOSS'])

    return {
        'width': w,
        'height': h,
        'thickness': th,
        'rib_count': ribs,
        'color_preset': color,
        'has_ribbon': ribbon,
        'page_aging': aging,
        'has_runes': has_runes,
        'rune_intensity': rune_int,
        'foil_style': foil,
        'seed': seed
    }
