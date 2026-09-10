import bpy
import bmesh
import math
import random
import mathutils
from mathutils import Vector, Matrix, Euler

def build_box(bm, center_pos, size_x, size_y, size_z, rot_euler=None, mat_idx=0, uv_layer=None):
    """汎用ボックス（回転・UV付き）"""
    hx = size_x * 0.5
    hy = size_y * 0.5
    hz = size_z * 0.5

    local_verts = [
        (-hx, -hy, -hz), ( hx, -hy, -hz), ( hx,  hy, -hz), (-hx,  hy, -hz),
        (-hx, -hy,  hz), ( hx, -hy,  hz), ( hx,  hy,  hz), (-hx,  hy,  hz)
    ]
    rot_mat = rot_euler.to_matrix().to_4x4() if rot_euler else Matrix.Identity(4)

    bm_verts = []
    for v in local_verts:
        vec = Vector(v)
        vec = rot_mat @ vec
        bm_verts.append(bm.verts.new(center_pos + vec))

    faces_idx = [
        (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6),
        (3, 0, 4, 7), (4, 5, 6, 7), (0, 3, 2, 1)
    ]
    created_faces = []
    for f_idx in faces_idx:
        f = bm.faces.new((bm_verts[f_idx[0]], bm_verts[f_idx[1]], bm_verts[f_idx[2]], bm_verts[f_idx[3]]))
        f.material_index = mat_idx
        created_faces.append(f)

    if uv_layer:
        for f in created_faces:
            f.loops[0][uv_layer].uv = (0.0, 0.0)
            f.loops[1][uv_layer].uv = (1.0, 0.0)
            f.loops[2][uv_layer].uv = (1.0, 1.0)
            f.loops[3][uv_layer].uv = (0.0, 1.0)

    return bm_verts


def build_cylinder_log(bm, start_pt, end_pt, radius=0.08, segments=8, spike_top=False, spike_height=0.15, mat_idx=0, uv_layer=None):
    """丸太柱（尖りオプション付き）"""
    dir_vec = (end_pt - start_pt)
    length = dir_vec.length
    if length < 0.001:
        return []
    dir_norm = dir_vec.normalized()

    up = Vector((0, 0, 1))
    if abs(dir_norm.dot(up)) > 0.99:
        up = Vector((1, 0, 0))
    side1 = dir_norm.cross(up).normalized()
    side2 = dir_norm.cross(side1).normalized()

    bot_verts = []
    top_verts = []

    for s in range(segments):
        ang = s * (2.0 * math.pi / segments)
        rx = math.cos(ang) * radius
        ry = math.sin(ang) * radius
        offset = side1 * rx + side2 * ry
        bot_verts.append(bm.verts.new(start_pt + offset))
        top_verts.append(bm.verts.new(end_pt + offset))

    for s in range(segments):
        s_next = (s + 1) % segments
        f = bm.faces.new((bot_verts[s], bot_verts[s_next], top_verts[s_next], top_verts[s]))
        f.material_index = mat_idx

    f_bot = bm.faces.new(reversed(bot_verts))
    f_bot.material_index = mat_idx

    if spike_top:
        v_tip = bm.verts.new(end_pt + dir_norm * spike_height)
        for s in range(segments):
            s_next = (s + 1) % segments
            f_tip = bm.faces.new((top_verts[s], top_verts[s_next], v_tip))
            f_tip.material_index = mat_idx
    else:
        f_top = bm.faces.new(top_verts)
        f_top.material_index = mat_idx

    return bot_verts + top_verts


def build_wooden_fence_mesh(
    bm,
    fence_type="POST_AND_RAIL",
    length=4.0,
    height=1.2,
    rails_count=2,
    post_spacing=1.8,
    decay_jitter=0.03,
    seed=0
):
    """クラシック木製フェンス（後方互換対応）"""
    rng = random.Random(seed)
    uv_layer = bm.loops.layers.uv.verify()

    num_posts = max(2, int(round(length / max(0.5, post_spacing))) + 1)
    actual_spacing = length / float(num_posts - 1)

    post_positions = []
    for i in range(num_posts):
        x = -length * 0.5 + i * actual_spacing
        y = rng.uniform(-decay_jitter * 0.5, decay_jitter * 0.5)
        z = 0.0
        post_positions.append(Vector((x, y, z)))

    post_width = 0.11 * (height / 1.2)
    rail_width = post_width * 0.55
    rail_height = post_width * 0.75

    for i, ppos in enumerate(post_positions):
        post_seed = seed + i * 47
        p_rng = random.Random(post_seed)
        jx = p_rng.uniform(-decay_jitter, decay_jitter)
        jy = p_rng.uniform(-decay_jitter, decay_jitter)
        rot_euler = Euler((jx, jy, p_rng.uniform(-0.05, 0.05)), 'XYZ')
        post_h = height * p_rng.uniform(0.96, 1.04)

        if fence_type == "PALISADE":
            start_p = ppos
            end_p = ppos + Vector((jx * height, jy * height, post_h))
            build_cylinder_log(bm, start_p, end_p, radius=post_width * 0.75,
                               segments=8, spike_top=True, spike_height=post_h * 0.15,
                               mat_idx=0, uv_layer=uv_layer)
        else:
            c_pos = ppos + Vector((0, 0, post_h * 0.5))
            build_box(bm, c_pos, post_width, post_width, post_h, rot_euler=rot_euler, mat_idx=0, uv_layer=uv_layer)
            if fence_type in ("PICKET", "POST_AND_RAIL"):
                tip_h = post_width * 0.6
                top_c = ppos + Vector((0, 0, post_h))
                v1 = bm.verts.new(top_c + Vector((-post_width*0.5, -post_width*0.5, 0)))
                v2 = bm.verts.new(top_c + Vector(( post_width*0.5, -post_width*0.5, 0)))
                v3 = bm.verts.new(top_c + Vector(( post_width*0.5,  post_width*0.5, 0)))
                v4 = bm.verts.new(top_c + Vector((-post_width*0.5,  post_width*0.5, 0)))
                v_tip = bm.verts.new(top_c + Vector((0, 0, tip_h)))
                for f_v in [(v1, v2, v_tip), (v2, v3, v_tip), (v3, v4, v_tip), (v4, v1, v_tip)]:
                    f = bm.faces.new(f_v)
                    f.material_index = 0

    for i in range(num_posts - 1):
        p1 = post_positions[i]
        p2 = post_positions[i+1]
        seg_vec = p2 - p1
        seg_len = seg_vec.length
        seg_mid = (p1 + p2) * 0.5

        if fence_type == "PALISADE":
            log_radius = 0.08 * (height / 1.2)
            logs_in_seg = max(3, int(round(seg_len / (log_radius * 1.95))))
            for li in range(1, logs_in_seg):
                t_l = li / float(logs_in_seg)
                l_pos = p1 + seg_vec * t_l
                l_rng = random.Random(seed + i * 100 + li)
                l_h = height * l_rng.uniform(0.92, 1.08)
                l_jx = l_rng.uniform(-decay_jitter * 0.4, decay_jitter * 0.4)
                l_jy = l_rng.uniform(-decay_jitter * 0.4, decay_jitter * 0.4)
                l_start = l_pos
                l_end = l_pos + Vector((l_jx * l_h, l_jy * l_h, l_h))
                build_cylinder_log(bm, l_start, l_end, radius=log_radius * l_rng.uniform(0.9, 1.1),
                                   segments=6, spike_top=True, spike_height=l_h * 0.18,
                                   mat_idx=0, uv_layer=uv_layer)

            for r_lvl in (0.35, 0.75):
                beam_z = height * r_lvl
                beam_pos = seg_mid + Vector((0, post_width * 0.6, beam_z))
                build_box(bm, beam_pos, seg_len * 0.98, rail_width, rail_height,
                          mat_idx=0, uv_layer=uv_layer)
                rope_pos = p1 + Vector((0, 0, beam_z))
                build_box(bm, rope_pos, post_width * 1.15, post_width * 1.15, rail_height * 0.45,
                          mat_idx=1, uv_layer=uv_layer)

        elif fence_type == "CROSS_BRACE":
            r_bot_z = height * 0.22
            r_top_z = height * 0.82
            for rz in (r_bot_z, r_top_z):
                r_pos = seg_mid + Vector((0, 0, rz))
                build_box(bm, r_pos, seg_len * 0.98, rail_width, rail_height, mat_idx=0, uv_layer=uv_layer)

            cross_h = r_top_z - r_bot_z
            cross_ang = math.atan2(cross_h, seg_len)
            cross_diag = math.sqrt(seg_len**2 + cross_h**2) * 0.95
            rot1 = Euler((0, -cross_ang, 0), 'XYZ')
            build_box(bm, seg_mid + Vector((0, 0, (r_bot_z + r_top_z)*0.5)),
                      cross_diag, rail_width * 0.85, rail_height * 0.85,
                      rot_euler=rot1, mat_idx=0, uv_layer=uv_layer)
            rot2 = Euler((0, cross_ang, 0), 'XYZ')
            build_box(bm, seg_mid + Vector((0, 0, (r_bot_z + r_top_z)*0.5)),
                      cross_diag, rail_width * 0.85, rail_height * 0.85,
                      rot_euler=rot2, mat_idx=0, uv_layer=uv_layer)

        elif fence_type == "PICKET":
            r_bot_z = height * 0.28
            r_top_z = height * 0.72
            for rz in (r_bot_z, r_top_z):
                r_pos = seg_mid + Vector((0, -rail_width * 0.5, rz))
                build_box(bm, r_pos, seg_len * 0.98, rail_width, rail_height, mat_idx=0, uv_layer=uv_layer)

            picket_w = post_width * 0.65
            picket_thick = post_width * 0.22
            picket_spacing = picket_w * 1.8
            picket_count = max(2, int(round(seg_len / picket_spacing)))
            for pi in range(picket_count):
                pt_ratio = (pi + 0.5) / float(picket_count)
                pk_x = p1.x + seg_vec.x * pt_ratio
                pk_rng = random.Random(seed + i * 50 + pi)
                pk_h = height * pk_rng.uniform(0.88, 0.96)
                pk_pos = Vector((pk_x, p1.y + rail_width * 0.6, pk_h * 0.5))
                build_box(bm, pk_pos, picket_w, picket_thick, pk_h, mat_idx=0, uv_layer=uv_layer)
                tip_h = picket_w * 0.5
                v_top_c = Vector((pk_x, p1.y + rail_width * 0.6, pk_h))
                v_p1 = bm.verts.new(v_top_c + Vector((-picket_w*0.5, -picket_thick*0.5, 0)))
                v_p2 = bm.verts.new(v_top_c + Vector(( picket_w*0.5, -picket_thick*0.5, 0)))
                v_p3 = bm.verts.new(v_top_c + Vector(( picket_w*0.5,  picket_thick*0.5, 0)))
                v_p4 = bm.verts.new(v_top_c + Vector((-picket_w*0.5,  picket_thick*0.5, 0)))
                v_ptip = bm.verts.new(v_top_c + Vector((0, 0, tip_h)))
                for f_v in [(v_p1, v_p2, v_ptip), (v_p2, v_p3, v_ptip), (v_p3, v_p4, v_ptip), (v_p4, v_p1, v_ptip)]:
                    f = bm.faces.new(f_v)
                    f.material_index = 0

        else:
            actual_rails = max(1, min(4, rails_count))
            for ri in range(actual_rails):
                rz = height * (0.28 + 0.5 * (ri / max(1, actual_rails - 1)))
                r_pos = seg_mid + Vector((0, 0, rz))
                build_box(bm, r_pos, seg_len * 0.98, rail_width, rail_height, mat_idx=0, uv_layer=uv_layer)

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm.verts[:]



def find_fence_root(obj):
    """選択されたオブジェクトからフェンスのルートを探す"""
    if not obj:
        return None
    curr = obj
    while curr.parent:
        curr = curr.parent
    return curr


def remove_fence_children(root_obj):
    """子オブジェクトを安全にクリーンアップ"""
    for c in list(root_obj.children):
        mesh = c.data if c.type == 'MESH' else None
        bpy.data.objects.remove(c, do_unlink=True)
        if mesh and mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def add_box(bm, center, size, rot_euler=None, mat_idx=0):
    """直方体を bmesh に追加"""
    sx, sy, sz = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    local_verts = [
        (-sx, -sy, -sz), ( sx, -sy, -sz), ( sx,  sy, -sz), (-sx,  sy, -sz),
        (-sx, -sy,  sz), ( sx, -sy,  sz), ( sx,  sy,  sz), (-sx,  sy,  sz)
    ]
    rot_mat = rot_euler.to_matrix().to_4x4() if rot_euler else Matrix.Identity(4)
    bm_v = []
    for v in local_verts:
        bm_v.append(bm.verts.new(center + rot_mat @ Vector(v)))

    faces_idx = [
        (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6),
        (3, 0, 4, 7), (4, 5, 6, 7), (0, 3, 2, 1)
    ]
    for idxs in faces_idx:
        f = bm.faces.new((bm_v[idxs[0]], bm_v[idxs[1]], bm_v[idxs[2]], bm_v[idxs[3]]))
        f.material_index = mat_idx
        f.smooth = False
    return bm_v


def add_cylinder(bm, start_pt, end_pt, radius=0.025, segments=12, mat_idx=0):
    """円柱パイプを bmesh に追加"""
    dir_vec = end_pt - start_pt
    length = dir_vec.length
    if length < 0.001:
        return
    dir_norm = dir_vec.normalized()
    up = Vector((0, 0, 1))
    if abs(dir_norm.dot(up)) > 0.99:
        up = Vector((1, 0, 0))
    side1 = dir_norm.cross(up).normalized()
    side2 = dir_norm.cross(side1).normalized()

    bot_v = []
    top_v = []
    for s in range(segments):
        ang = s * (2.0 * math.pi / segments)
        rx = math.cos(ang) * radius
        ry = math.sin(ang) * radius
        offset = side1 * rx + side2 * ry
        bot_v.append(bm.verts.new(start_pt + offset))
        top_v.append(bm.verts.new(end_pt + offset))

    for s in range(segments):
        s_next = (s + 1) % segments
        f = bm.faces.new((bot_v[s], bot_v[s_next], top_v[s_next], top_v[s]))
        f.material_index = mat_idx
        f.smooth = True

    f_bot = bm.faces.new(reversed(bot_v))
    f_bot.material_index = mat_idx
    f_bot.smooth = False
    f_top = bm.faces.new(top_v)
    f_top.material_index = mat_idx
    f_top.smooth = False



def build_wire_cross_fence(bm, length=4.0, height=1.5, post_spacing=2.0):
    """
    1. 十字の鉄線 (WIRE_CROSS): 画像1準拠
    丸パイプ支柱 + 上下フレームパイプ + 十字直交ワイヤー格子
    """
    num_posts = max(2, int(math.ceil(length / post_spacing)) + 1)
    actual_spacing = length / float(num_posts - 1)
    half_l = length * 0.5

    post_r = 0.028
    rail_r = 0.016
    wire_r = 0.0022

    # 1. 支柱 (Posts)
    for i in range(num_posts):
        x = -half_l + i * actual_spacing
        p_start = Vector((x, 0.0, 0.0))
        p_end   = Vector((x, 0.0, height + 0.04))
        add_cylinder(bm, p_start, p_end, radius=post_r, segments=12, mat_idx=0)
        # 頭頂部キャップ (球キャップ)
        cap_c = p_end
        add_cylinder(bm, cap_c, cap_c + Vector((0, 0, 0.015)), radius=post_r * 1.08, segments=12, mat_idx=0)

    # 2. 上下フレームパイプ (Top/Bottom Rails)
    rail_z_top = height - 0.04
    rail_z_bot = 0.08
    for i in range(num_posts - 1):
        x1 = -half_l + i * actual_spacing + post_r * 1.1
        x2 = -half_l + (i + 1) * actual_spacing - post_r * 1.1
        # 上段
        add_cylinder(bm, Vector((x1, 0, rail_z_top)), Vector((x2, 0, rail_z_top)), radius=rail_r, segments=8, mat_idx=0)
        # 下段
        add_cylinder(bm, Vector((x1, 0, rail_z_bot)), Vector((x2, 0, rail_z_bot)), radius=rail_r, segments=8, mat_idx=0)

        # 3. 各スパン内の十字格子鉄線 (直交ワイヤーメッシュ)
        # 縦線 (Pitch ~ 0.05m)
        span_w = x2 - x1
        v_count = max(4, int(span_w / 0.05))
        for vi in range(v_count + 1):
            vx = x1 + vi * (span_w / v_count)
            p_bot = Vector((vx, 0.0, rail_z_bot))
            p_top = Vector((vx, 0.0, rail_z_top))
            # 極細ローポリリボン/角柱 (mat_idx=1)
            add_box(bm, (p_bot + p_top) * 0.5, (wire_r * 2.0, wire_r * 2.0, rail_z_top - rail_z_bot), mat_idx=1)

        # 横線 (Pitch ~ 0.12m)
        h_h = rail_z_top - rail_z_bot
        h_count = max(3, int(h_h / 0.12))
        for hi in range(1, h_count):
            hz = rail_z_bot + hi * (h_h / h_count)
            # 水平ワイヤー
            add_box(bm, Vector(((x1 + x2) * 0.5, 0.003, hz)), (span_w, wire_r * 2.0, wire_r * 2.0), mat_idx=1)


def build_wire_x_fence(bm, length=4.0, height=1.8, post_spacing=2.0):
    """
    2. X字の鉄線 (WIRE_X): 画像3準拠
    丸パイプ支柱 + トップレール + 45度斜め交差ひし形チェーンリンク金網
    """
    num_posts = max(2, int(math.ceil(length / post_spacing)) + 1)
    actual_spacing = length / float(num_posts - 1)
    half_l = length * 0.5

    post_r = 0.032
    rail_r = 0.020
    wire_r = 0.0018

    # 1. 支柱 (Posts)
    for i in range(num_posts):
        x = -half_l + i * actual_spacing
        p_start = Vector((x, 0.0, 0.0))
        p_end   = Vector((x, 0.0, height + 0.03))
        add_cylinder(bm, p_start, p_end, radius=post_r, segments=12, mat_idx=0)

    # 2. トップレール (Top Rail: 上部を通る横パイプ)
    add_cylinder(bm, Vector((-half_l, 0.0, height)), Vector((half_l, 0.0, height)), radius=rail_r, segments=10, mat_idx=0)
    # 最下部テンションワイヤー
    add_cylinder(bm, Vector((-half_l, 0.0, 0.05)), Vector((half_l, 0.0, 0.05)), radius=wire_r * 2.5, segments=6, mat_idx=0)

    # 3. 各スパン内のひし形チェーンリンクメッシュ (45度斜めX字)
    z_bot = 0.05
    z_top = height
    span_h = z_top - z_bot
    diamond_size = 0.065 # ひし形の格子サイズ

    for i in range(num_posts - 1):
        x1 = -half_l + i * actual_spacing + post_r * 1.1
        x2 = -half_l + (i + 1) * actual_spacing - post_r * 1.1
        span_w = x2 - x1

        # +45度 方向の斜めワイヤー群
        diag_step = diamond_size * 1.414
        num_diags = int((span_w + span_h) / diag_step)
        for d in range(num_diags):
            # 直線方程式: z - z_bot = (x - offset_x)
            offset = -span_h + d * diag_step
            # スパン矩形 [x1, x2] x [z_bot, z_top] との交点クリッピング
            # 点A (x_a, z_a), 点B (x_b, z_b)
            # z = x - x1 + offset
            pts = []
            # x = x1
            z_at_x1 = z_bot + (0 - offset)
            if z_bot <= z_at_x1 <= z_top:
                pts.append(Vector((x1, 0.0, z_at_x1)))
            # x = x2
            z_at_x2 = z_bot + (span_w - offset)
            if z_bot <= z_at_x2 <= z_top:
                pts.append(Vector((x2, 0.0, z_at_x2)))
            # z = z_bot
            x_at_zbot = x1 + offset
            if x1 < x_at_zbot < x2:
                pts.append(Vector((x_at_zbot, 0.0, z_bot)))
            # z = z_top
            x_at_ztop = x1 + span_h + offset
            if x1 < x_at_ztop < x2:
                pts.append(Vector((x_at_ztop, 0.0, z_top)))

            if len(pts) >= 2:
                p_a, p_b = pts[0], pts[1]
                mid_p = (p_a + p_b) * 0.5
                l_seg = (p_b - p_a).length
                ang = math.atan2(p_b.z - p_a.z, p_b.x - p_a.x)
                rot = mathutils.Euler((0.0, -ang + math.pi*0.5, 0.0), 'XYZ')
                add_box(bm, mid_p, (wire_r * 2.0, wire_r * 2.0, l_seg), rot_euler=rot, mat_idx=1)

        # -45度 方向の斜めワイヤー群 (交差してX字・ひし形を形成)
        for d in range(num_diags):
            offset = d * diag_step
            pts = []
            z_at_x1 = z_top - (0 - (offset - span_h))
            if z_bot <= z_at_x1 <= z_top:
                pts.append(Vector((x1, 0.002, z_at_x1)))
            z_at_x2 = z_top - (span_w - (offset - span_h))
            if z_bot <= z_at_x2 <= z_top:
                pts.append(Vector((x2, 0.002, z_at_x2)))
            x_at_zbot = x1 + (offset - span_h) + span_h
            if x1 < x_at_zbot < x2:
                pts.append(Vector((x_at_zbot, 0.002, z_bot)))
            x_at_ztop = x1 + (offset - span_h)
            if x1 < x_at_ztop < x2:
                pts.append(Vector((x_at_ztop, 0.002, z_top)))

            if len(pts) >= 2:
                p_a, p_b = pts[0], pts[1]
                mid_p = (p_a + p_b) * 0.5
                l_seg = (p_b - p_a).length
                ang = math.atan2(p_b.z - p_a.z, p_b.x - p_a.x)
                rot = mathutils.Euler((0.0, -ang + math.pi*0.5, 0.0), 'XYZ')
                add_box(bm, mid_p, (wire_r * 2.0, wire_r * 2.0, l_seg), rot_euler=rot, mat_idx=1)


def build_wood_slat_mesh(
    bm,
    center_pos,
    size,
    top_style="FLAT",
    jitter=0.35,
    wear=0.25,
    rot_euler=None,
    mat_idx=1,
    seed=0
):
    """
    リアルな木板スラット（上部形状・ゆがみ・角欠け対応）を密閉メッシュで生成
    size: (width_w, thick_t, height_h)
    top_style: 'FLAT', 'POINTED', 'ROUNDED', 'DOG_EAR'
    """
    rng = random.Random(seed)
    w, t, h = size
    hw = w * 0.5
    hh = h * 0.5
    ht = t * 0.5

    # 1. 2D輪郭頂点の構築 (XZ平面、反時計回り)
    pts_2d = []
    # 底面 2点
    pts_2d.append((-hw, -hh))
    pts_2d.append(( hw, -hh))

    if top_style == "POINTED":
        # 山型尖り (ピケット風45度カット)
        shoulder_h = hh - hw * 0.55
        pts_2d.append(( hw, shoulder_h))
        # 頂点 (わずかにランダム左右に揺らす)
        peak_x = rng.uniform(-0.002, 0.002) * jitter
        pts_2d.append((peak_x, hh))
        pts_2d.append((-hw, shoulder_h))

    elif top_style == "DOG_EAR":
        # ドッグイヤー (角取り45度カット)
        d = min(hw * 0.42, 0.024)
        pts_2d.append(( hw, hh - d))
        pts_2d.append(( hw - d, hh))
        pts_2d.append((-hw + d, hh))
        pts_2d.append((-hw, hh - d))

    elif top_style == "ROUNDED":
        # アーチ丸型 (多角形円弧)
        r = hw
        cy = hh - r
        segs = 6
        for s in range(segs + 1):
            ang = s * (math.pi / segs)
            rx = r * math.cos(ang)
            rz = cy + r * math.sin(ang)
            pts_2d.append((rx, rz))

    else:
        # FLAT (直線カット)
        pts_2d.append(( hw, hh))
        pts_2d.append((-hw, hh))

    # 2. 角欠け (Chips / Notch)
    if wear > 0.08 and rng.random() < wear * 0.7:
        # 上部頂点のいずれかを欠けさせる
        c_idx = rng.randint(2, len(pts_2d) - 1)
        px, pz = pts_2d[c_idx]
        chip_amount = rng.uniform(0.004, 0.014) * wear
        pts_2d[c_idx] = (px * (1.0 - chip_amount * 2.0), pz - chip_amount)

    # 3. Y軸前後の頂点生成（厚みムラ・ゆがみを付与）
    front_verts = []
    back_verts = []

    # スラット全体の回転マトリクス（反り・傾き）
    base_rot = rot_euler if rot_euler else Euler((0, 0, 0), 'XYZ')
    jx = rng.uniform(-0.015, 0.015) * jitter
    jy = rng.uniform(-0.010, 0.010) * jitter
    jz = rng.uniform(-0.018, 0.018) * jitter
    total_rot = Euler((base_rot.x + jx, base_rot.y + jy, base_rot.z + jz), 'XYZ')
    rot_mat = total_rot.to_matrix().to_4x4()

    # 全体の微小位置オフセット
    dy = rng.uniform(-0.0025, 0.0025) * jitter
    dz = rng.uniform(-0.012, 0.012) * jitter if top_style != "FLAT" else rng.uniform(-0.004, 0.004) * jitter
    offset_center = center_pos + Vector((0.0, dy, dz))

    for px, pz in pts_2d:
        # 表面の細かな揺らぎ
        vy_f = -ht + rng.uniform(-0.0012, 0.0012) * jitter
        vy_b =  ht + rng.uniform(-0.0012, 0.0012) * jitter

        v_local_f = rot_mat @ Vector((px, vy_f, pz))
        v_local_b = rot_mat @ Vector((px, vy_b, pz))

        front_verts.append(bm.verts.new(offset_center + v_local_f))
        back_verts.append(bm.verts.new(offset_center + v_local_b))

    # 4. 面の構築
    n = len(pts_2d)
    # 前面 (反時計回り)
    f_front = bm.faces.new(front_verts)
    f_front.material_index = mat_idx
    f_front.smooth = False

    # 背面 (時計回りで外向き)
    f_back = bm.faces.new(reversed(back_verts))
    f_back.material_index = mat_idx
    f_back.smooth = False

    # 側面 (前と奥を繋ぐ四角形)
    for i in range(n):
        i_next = (i + 1) % n
        v1 = front_verts[i]
        v2 = front_verts[i_next]
        v3 = back_verts[i_next]
        v4 = back_verts[i]
        f_side = bm.faces.new((v1, v2, v3, v4))
        f_side.material_index = mat_idx
        f_side.smooth = False


def build_wood_horizontal_fence(
    bm,
    length=4.0,
    height=1.6,
    post_spacing=1.8,
    slat_h=0.09,
    slat_gap=0.015,
    jitter=0.35,
    wear=0.25,
    top_style="FLAT",
    seed=42
):
    """
    3. 木板打ち付け・横 (WOOD_HORIZ): 画像2準拠
    角柱支柱 + 等間隔スリット隙間のリアルな横板スラットルーバー（反り・段差・ビス）
    """
    rng = random.Random(seed)
    num_posts = max(2, int(math.ceil(length / post_spacing)) + 1)
    actual_spacing = length / float(num_posts - 1)
    half_l = length * 0.5

    post_w = 0.060
    post_d = 0.060
    slat_thick = 0.016

    # 1. 支柱 (角柱支柱)
    for i in range(num_posts):
        x = -half_l + i * actual_spacing
        p_seed = seed + i * 83
        p_rng = random.Random(p_seed)
        p_jx = p_rng.uniform(-0.01, 0.01) * jitter
        p_jy = p_rng.uniform(-0.01, 0.01) * jitter
        rot_p = Euler((p_jx, p_jy, 0.0), 'XYZ')
        c_pos = Vector((x, post_d * 0.5 + 0.001, height * 0.5))
        add_box(bm, c_pos, (post_w, post_d, height), rot_euler=rot_p, mat_idx=0)

    # 2. 横板スラット (Horizontal Slats)
    pitch = slat_h + slat_gap
    num_slats = int((height - 0.05) / pitch)
    z_start = 0.06

    for s in range(num_slats):
        s_seed = seed + s * 137
        s_rng = random.Random(s_seed)
        sz = z_start + s * pitch + slat_h * 0.5

        # 板ごとの前後のわずかな浮き沈み（光が当たると段差シャドウがクッキリ出る）
        s_dy = s_rng.uniform(-0.0025, 0.0025) * jitter
        c_slat = Vector((0.0, -slat_thick * 0.5 + s_dy, sz))

        # 横板の微妙な傾き
        rot_s = Euler((s_rng.uniform(-0.02, 0.02) * jitter, 0.0, s_rng.uniform(-0.005, 0.005) * jitter), 'XYZ')

        # 横板を生成 (横向きサイズ: length, slat_thick, slat_h)
        add_box(bm, c_slat, (length, slat_thick, slat_h), rot_euler=rot_s, mat_idx=1)

        # 支柱ごとの固定ビス（ネジ頭）
        for i in range(num_posts):
            bx = -half_l + i * actual_spacing + s_rng.uniform(-0.002, 0.002) * jitter
            bz = sz + s_rng.uniform(-0.003, 0.003) * jitter
            add_box(bm, Vector((bx, -slat_thick + s_dy - 0.001, bz)), (0.008, 0.004, 0.008), mat_idx=0)


def build_wood_vertical_fence(
    bm,
    length=4.0,
    height=1.6,
    post_spacing=1.8,
    slat_w=0.08,
    slat_gap=0.02,
    top_style="POINTED",
    jitter=0.35,
    wear=0.25,
    seed=42
):
    """
    4. 木板打ち付け・縦 (WOOD_VERT):
    角柱支柱 + 上下横桟レール + 上部形状スタイル（尖り/丸み/ドッグイヤー）＆ゆがみ・欠け付き縦板
    """
    rng = random.Random(seed)
    num_posts = max(2, int(math.ceil(length / post_spacing)) + 1)
    actual_spacing = length / float(num_posts - 1)
    half_l = length * 0.5

    post_w = 0.070
    rail_h = 0.045
    rail_d = 0.040
    slat_thick = 0.018

    # 1. 支柱
    for i in range(num_posts):
        x = -half_l + i * actual_spacing
        c_pos = Vector((x, rail_d * 0.5, height * 0.5))
        add_box(bm, c_pos, (post_w, post_w, height), mat_idx=0)

    # 2. 上下横桟レール
    for rz in [height * 0.25, height * 0.80]:
        add_box(bm, Vector((0.0, rail_d * 0.5, rz)), (length, rail_d, rail_h), mat_idx=0)

    # 3. 縦板スラット (Vertical Slats)
    pitch = slat_w + slat_gap
    num_slats = int(length / pitch)
    x_start = -half_l + (length - (num_slats - 1) * pitch) * 0.5
    slat_len = height * 0.90
    slat_z_mid = height * 0.5

    for s in range(num_slats):
        s_seed = seed + s * 71
        sx = x_start + s * pitch
        c_slat = Vector((sx, -slat_thick * 0.5, slat_z_mid))

        build_wood_slat_mesh(
            bm,
            center_pos=c_slat,
            size=(slat_w, slat_thick, slat_len),
            top_style=top_style,
            jitter=jitter,
            wear=wear,
            mat_idx=1,
            seed=s_seed
        )



def get_or_create_material(mat_name):
    """マテリアルを取得、なければ新規作成"""
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
    return mat


def setup_wood_weathering_shader(material, base_color=(0.42, 0.25, 0.15, 1.0), weathering=0.4, roughness=0.55, is_vertical=True):
    """プロシージャルな木目（縦繊維/横繊維・年輪）と経年汚しを構築"""
    material.use_nodes = True
    tree = material.node_tree
    tree.nodes.clear()

    node_out = tree.nodes.new("ShaderNodeOutputMaterial")
    node_out.location = (600, 0)

    node_bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    node_bsdf.location = (300, 0)
    tree.links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    if weathering <= 0.05:
        node_bsdf.inputs['Base Color'].default_value = base_color
        node_bsdf.inputs['Roughness'].default_value = roughness
        node_bsdf.inputs['Metallic'].default_value = 0.0
        return

    node_tc = tree.nodes.new("ShaderNodeTexCoord")
    node_tc.location = (-700, 0)

    node_map = tree.nodes.new("ShaderNodeMapping")
    node_map.location = (-500, 0)

    # 縦板（WOOD_VERT）なら繊維がZ方向に伸びる（Zスケール小、Xスケール大、帯はX方向）
    # 横板（WOOD_HORIZ）なら繊維がX方向に伸びる（Xスケール小、Zスケール大、帯はZ方向）
    if is_vertical:
        node_map.inputs['Scale'].default_value = (10.0, 2.0, 0.05)
        wave_dir = 'X'
    else:
        node_map.inputs['Scale'].default_value = (0.05, 2.0, 10.0)
        wave_dir = 'Z'

    tree.links.new(node_tc.outputs['Generated'], node_map.inputs['Vector'])

    node_wave = tree.nodes.new("ShaderNodeTexWave")
    node_wave.location = (-300, 100)
    node_wave.wave_type = 'BANDS'
    node_wave.bands_direction = wave_dir
    node_wave.inputs['Scale'].default_value = 1.8
    node_wave.inputs['Distortion'].default_value = 5.5
    node_wave.inputs['Detail'].default_value = 2.5
    node_wave.inputs['Detail Scale'].default_value = 1.0
    node_wave.inputs['Detail Roughness'].default_value = 0.5
    tree.links.new(node_map.outputs['Vector'], node_wave.inputs['Vector'])

    node_ramp = tree.nodes.new("ShaderNodeValToRGB")
    node_ramp.location = (-50, 0)
    cr = node_ramp.color_ramp
    cr.interpolation = 'EASE'

    # 年輪と汚しの3段階カラー (汚し強度 weathering に応じた自然な陰影コントラスト)
    contrast = 0.20 + weathering * 0.35
    dark_mult = max(0.40, 1.0 - contrast)
    light_mult = min(1.30, 1.0 + contrast * 0.40)

    cr.elements[0].position = 0.22
    cr.elements[0].color = (base_color[0] * dark_mult, base_color[1] * dark_mult * 0.95, base_color[2] * dark_mult * 0.90, 1.0)

    cr.elements[1].position = 0.78
    cr.elements[1].color = (min(1.0, base_color[0] * light_mult), min(1.0, base_color[1] * light_mult), min(1.0, base_color[2] * light_mult), 1.0)

    el_mid = cr.elements.new(0.50)
    el_mid.color = base_color

    tree.links.new(node_wave.outputs['Fac'], node_ramp.inputs['Fac'])
    tree.links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])

    node_bsdf.inputs['Roughness'].default_value = roughness
    node_bsdf.inputs['Metallic'].default_value = 0.0


def create_fence_materials(
    name_prefix,
    preset_type="WIRE_CROSS",
    frame_color=None,
    body_color=None,
    metallic=None,
    roughness=None,
    weathering=0.40
):
    """各プリセットに最適化されたPBRマテリアルを構築・色反映"""
    m0 = get_or_create_material(f"{name_prefix}_Frame")
    m0.use_nodes = True
    b0 = m0.node_tree.nodes.get("Principled BSDF")

    m1 = get_or_create_material(f"{name_prefix}_Body")
    m1.use_nodes = True
    b1 = m1.node_tree.nodes.get("Principled BSDF")

    # デフォルト値決定
    if preset_type == "WIRE_CROSS":
        def_frame = (0.05, 0.05, 0.05, 1.0)
        def_body  = (0.06, 0.06, 0.06, 1.0)
        def_met   = 0.25
        def_rough = 0.35
    elif preset_type == "WIRE_X":
        def_frame = (0.08, 0.38, 0.22, 1.0)
        def_body  = (0.08, 0.42, 0.24, 1.0)
        def_met   = 0.15
        def_rough = 0.40
    else: # WOOD
        def_frame = (0.18, 0.12, 0.08, 1.0)
        def_body  = (0.42, 0.25, 0.15, 1.0)
        def_met   = 0.0
        def_rough = 0.60

    f_col = frame_color if frame_color is not None else def_frame
    b_col = body_color if body_color is not None else def_body
    met   = metallic if metallic is not None else def_met
    rgh   = roughness if roughness is not None else def_rough

    if b0:
        b0.inputs['Base Color'].default_value = f_col
        b0.inputs['Metallic'].default_value = met
        b0.inputs['Roughness'].default_value = rgh

    if preset_type in ("WOOD_HORIZ", "WOOD_VERT") and weathering > 0.05:
        is_vert = (preset_type == "WOOD_VERT")
        setup_wood_weathering_shader(m1, base_color=b_col, weathering=weathering, roughness=rgh, is_vertical=is_vert)
    else:
        if b1:
            b1.inputs['Base Color'].default_value = b_col
            b1.inputs['Metallic'].default_value = met
            b1.inputs['Roughness'].default_value = rgh

    return m0, m1


def apply_fence_material_colors(obj, frame_color, body_color, metallic=0.2, roughness=0.4, weathering=0.4):
    """選択中フェンスのマテリアル色・質感をメッシュ再構築なしで即座に塗り替え"""
    if not obj:
        return False
    root = find_fence_root(obj)
    target = root if root else obj
    if not target or target.type != 'MESH':
        return False

    mats = target.data.materials
    if len(mats) > 0 and mats[0] and mats[0].use_nodes:
        bsdf0 = mats[0].node_tree.nodes.get("Principled BSDF")
        if bsdf0:
            bsdf0.inputs['Base Color'].default_value = frame_color
            bsdf0.inputs['Metallic'].default_value = metallic
            bsdf0.inputs['Roughness'].default_value = roughness

    if len(mats) > 1 and mats[1] and mats[1].use_nodes:
        is_wood = "Wood" in target.name or "WOOD" in target.name
        if is_wood and weathering > 0.05:
            is_vert = "Vert" in target.name or "VERT" in target.name
            setup_wood_weathering_shader(mats[1], base_color=body_color, weathering=weathering, roughness=roughness, is_vertical=is_vert)
        else:
            bsdf1 = mats[1].node_tree.nodes.get("Principled BSDF")
            if bsdf1:
                bsdf1.inputs['Base Color'].default_value = body_color
                bsdf1.inputs['Metallic'].default_value = metallic
                bsdf1.inputs['Roughness'].default_value = roughness
    return True


def generate_fence_preset_asset(
    context,
    name="Fence_Preset",
    preset_type="WIRE_CROSS",
    length=4.0,
    height=1.5,
    post_spacing=2.0,
    slat_gap=0.015,
    scale=1.0,
    frame_color=None,
    body_color=None,
    metallic=None,
    roughness=None,
    top_style="POINTED",
    wood_jitter=0.35,
    wood_wear=0.25,
    wood_weathering=0.40,
    target_obj=None
):
    """
    実用フェンス4大プリセットをプロシージャル一発生成・再構築
    target_obj が渡された場合はその場でトランスフォームを維持して置換
    """
    if context.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

    root_fence = None
    if target_obj:
        root_fence = find_fence_root(target_obj)

    if root_fence and root_fence.type == 'MESH':
        obj_fence = root_fence
        remove_fence_children(obj_fence)
        mesh_fence = obj_fence.data
        mesh_fence.clear_geometry()
        bm = bmesh.new()
    else:
        mesh_fence = bpy.data.meshes.new(f"{name}_Mesh")
        obj_fence = bpy.data.objects.new(name, mesh_fence)
        context.collection.objects.link(obj_fence)
        bm = bmesh.new()

    # プリセットごとの生成ディスパッチ
    scaled_l = length * scale
    scaled_h = height * scale
    scaled_spacing = post_spacing * scale

    if preset_type == "WIRE_CROSS":
        build_wire_cross_fence(bm, length=scaled_l, height=scaled_h, post_spacing=scaled_spacing)
    elif preset_type == "WIRE_X":
        build_wire_x_fence(bm, length=scaled_l, height=scaled_h, post_spacing=scaled_spacing)
    elif preset_type == "WOOD_HORIZ":
        build_wood_horizontal_fence(
            bm,
            length=scaled_l,
            height=scaled_h,
            post_spacing=scaled_spacing,
            slat_gap=slat_gap * scale,
            jitter=wood_jitter,
            wear=wood_wear,
            top_style=top_style
        )
    elif preset_type == "WOOD_VERT":
        build_wood_vertical_fence(
            bm,
            length=scaled_l,
            height=scaled_h,
            post_spacing=scaled_spacing,
            slat_gap=slat_gap * scale,
            top_style=top_style,
            jitter=wood_jitter,
            wear=wood_wear
        )

    # マテリアル構築・割り当て（bm.to_mesh より前にスロットを用意してマテリアルインデックスの欠落を防止）
    m0, m1 = create_fence_materials(
        name_prefix=name,
        preset_type=preset_type,
        frame_color=frame_color,
        body_color=body_color,
        metallic=metallic,
        roughness=roughness,
        weathering=wood_weathering
    )
    if len(mesh_fence.materials) == 0:
        mesh_fence.materials.append(m0)
        mesh_fence.materials.append(m1)
    else:
        mesh_fence.materials[0] = m0
        if len(mesh_fence.materials) > 1:
            mesh_fence.materials[1] = m1
        else:
            mesh_fence.materials.append(m1)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh_fence)
    bm.free()

    context.view_layer.objects.active = obj_fence
    obj_fence.select_set(True)

    return obj_fence


