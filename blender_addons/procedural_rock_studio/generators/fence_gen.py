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


def build_wood_horizontal_fence(bm, length=4.0, height=1.6, post_spacing=1.8, slat_h=0.09, slat_gap=0.015):
    """
    3. 木板打ち付け・横 (WOOD_HORIZ): 画像2準拠
    角柱支柱 + 等間隔スリット隙間の横板スラットルーバー
    """
    num_posts = max(2, int(math.ceil(length / post_spacing)) + 1)
    actual_spacing = length / float(num_posts - 1)
    half_l = length * 0.5

    post_w = 0.060
    post_d = 0.060
    slat_thick = 0.016

    # 1. 支柱 (角柱支柱)
    for i in range(num_posts):
        x = -half_l + i * actual_spacing
        # 支柱は板の裏側 (Y = +post_d*0.5)
        c_pos = Vector((x, post_d * 0.5 + 0.001, height * 0.5))
        add_box(bm, c_pos, (post_w, post_d, height), mat_idx=0)

    # 2. 横板スラット (Horizontal Slats)
    pitch = slat_h + slat_gap
    num_slats = int((height - 0.05) / pitch)
    z_start = 0.06

    for s in range(num_slats):
        sz = z_start + s * pitch + slat_h * 0.5
        c_slat = Vector((0.0, -slat_thick * 0.5, sz))
        add_box(bm, c_slat, (length, slat_thick, slat_h), mat_idx=1)

        # 支柱ごとの固定ビス（ネジ頭）
        for i in range(num_posts):
            bx = -half_l + i * actual_spacing
            add_box(bm, Vector((bx, -slat_thick - 0.001, sz)), (0.008, 0.004, 0.008), mat_idx=0)


def build_wood_vertical_fence(bm, length=4.0, height=1.6, post_spacing=1.8, slat_w=0.08, slat_gap=0.02):
    """
    4. 木板打ち付け・縦 (WOOD_VERT):
    角柱支柱 + 上下横桟レール + 等間隔スリットの縦板スラット
    """
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
        sx = x_start + s * pitch
        c_slat = Vector((sx, -slat_thick * 0.5, slat_z_mid))
        add_box(bm, c_slat, (slat_w, slat_thick, slat_len), mat_idx=1)


def create_fence_materials(name_prefix, preset_type="WIRE_CROSS"):
    """各プリセットに最適化されたPBRマテリアルを構築"""
    # フレーム用マテリアル (mat_0)
    m0 = bpy.data.materials.new(f"{name_prefix}_Frame")
    m0.use_nodes = True
    b0 = m0.node_tree.nodes.get("Principled BSDF")

    # メッシュ/板用マテリアル (mat_1)
    m1 = bpy.data.materials.new(f"{name_prefix}_Body")
    m1.use_nodes = True
    b1 = m1.node_tree.nodes.get("Principled BSDF")

    if preset_type == "WIRE_CROSS":
        # パウダーコートブラックメタリック (画像1)
        b0.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1.0)
        b0.inputs['Roughness'].default_value = 0.35
        b0.inputs['Metallic'].default_value = 0.20
        b1.inputs['Base Color'].default_value = (0.06, 0.06, 0.06, 1.0)
        b1.inputs['Roughness'].default_value = 0.30
        b1.inputs['Metallic'].default_value = 0.30

    elif preset_type == "WIRE_X":
        # グラウンドグリーン / 亜鉛メッキ (画像3)
        b0.inputs['Base Color'].default_value = (0.08, 0.38, 0.22, 1.0) # グリーン支柱
        b0.inputs['Roughness'].default_value = 0.35
        b1.inputs['Base Color'].default_value = (0.08, 0.42, 0.24, 1.0) # グリーン金網
        b1.inputs['Roughness'].default_value = 0.40

    else:
        # ウッドフェンス (画像2)
        # 支柱: ダークブロンズ/アルミ
        b0.inputs['Base Color'].default_value = (0.18, 0.12, 0.08, 1.0)
        b0.inputs['Roughness'].default_value = 0.45
        # 木板: ウォールナット/チーク調木目
        b1.inputs['Base Color'].default_value = (0.42, 0.25, 0.15, 1.0)
        b1.inputs['Roughness'].default_value = 0.55

    return m0, m1


def generate_fence_preset_asset(
    context,
    name="Fence_Preset",
    preset_type="WIRE_CROSS",
    length=4.0,
    height=1.5,
    post_spacing=2.0,
    slat_gap=0.015,
    scale=1.0,
    target_obj=None
):
    """
    実用フェンス4大プリセットをプロシージャル一発生成・再構築
    target_obj が渡された場合はその場でトランスフォームを維持して置換
    """
    root_fence = None
    if target_obj:
        root_fence = find_fence_root(target_obj)

    if root_fence:
        obj_fence = root_fence
        remove_fence_children(obj_fence)
        mesh_fence = obj_fence.data
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
        build_wood_horizontal_fence(bm, length=scaled_l, height=scaled_h, post_spacing=scaled_spacing, slat_gap=slat_gap * scale)
    elif preset_type == "WOOD_VERT":
        build_wood_vertical_fence(bm, length=scaled_l, height=scaled_h, post_spacing=scaled_spacing, slat_gap=slat_gap * scale)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh_fence)
    bm.free()

    # マテリアル適用
    m0, m1 = create_fence_materials(name, preset_type=preset_type)
    obj_fence.data.materials.clear()
    obj_fence.data.materials.append(m0)
    obj_fence.data.materials.append(m1)

    context.view_layer.objects.active = obj_fence
    obj_fence.select_set(True)

    return obj_fence
