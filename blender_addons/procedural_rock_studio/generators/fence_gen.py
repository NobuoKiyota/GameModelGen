import bpy
import bmesh
import math
import mathutils
import random

def build_box(bm, center_pos, size_x, size_y, size_z, rot_euler=None, mat_idx=0, uv_layer=None):
    """汎用直方体ボックス（回転・UV付き）"""
    hx = size_x * 0.5
    hy = size_y * 0.5
    hz = size_z * 0.5

    local_verts = [
        (-hx, -hy, -hz), ( hx, -hy, -hz), ( hx,  hy, -hz), (-hx,  hy, -hz),
        (-hx, -hy,  hz), ( hx, -hy,  hz), ( hx,  hy,  hz), (-hx,  hy,  hz)
    ]
    rot_mat = rot_euler.to_matrix().to_4x4() if rot_euler else mathutils.Matrix.Identity(4)

    bm_verts = []
    for v in local_verts:
        vec = mathutils.Vector(v)
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
    """円柱丸太（槍状先端オプション付き）"""
    dir_vec = (end_pt - start_pt)
    length = dir_vec.length
    if length < 0.001:
        return []
    dir_norm = dir_vec.normalized()

    # 垂直ベクトルの基準
    up = mathutils.Vector((0, 0, 1))
    if abs(dir_norm.dot(up)) > 0.99:
        up = mathutils.Vector((1, 0, 0))
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

    # 側面
    for s in range(segments):
        s_next = (s + 1) % segments
        f = bm.faces.new((bot_verts[s], bot_verts[s_next], top_verts[s_next], top_verts[s]))
        f.material_index = mat_idx

    # 底面
    f_bot = bm.faces.new(reversed(bot_verts))
    f_bot.material_index = mat_idx

    # 上面または尖り先端
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
    decay_jitter=0.04,
    seed=0,
    uv_layer=None
):
    """木製の柵・フェンス・砦のプロシージャル BMesh 生成エンジン"""
    rng = random.Random(seed)
    
    # 支柱の配置点計算
    num_posts = max(2, int(math.ceil(length / max(0.8, post_spacing))) + 1)
    actual_spacing = length / float(num_posts - 1)
    post_half_len = length * 0.5

    post_positions = []
    for i in range(num_posts):
        x = -post_half_len + i * actual_spacing
        y = rng.uniform(-decay_jitter * 0.5, decay_jitter * 0.5)
        z = 0.0
        post_positions.append(mathutils.Vector((x, y, z)))

    post_width = 0.11 * (height / 1.2)
    rail_width = post_width * 0.55
    rail_height = post_width * 0.75

    # ── 1. 支柱（Posts）の生成
    for i, ppos in enumerate(post_positions):
        post_seed = seed + i * 47
        p_rng = random.Random(post_seed)
        
        # 経年劣化の傾き
        jx = p_rng.uniform(-decay_jitter, decay_jitter)
        jy = p_rng.uniform(-decay_jitter, decay_jitter)
        rot_euler = mathutils.Euler((jx, jy, p_rng.uniform(-0.05, 0.05)), 'XYZ')
        
        post_h = height * p_rng.uniform(0.96, 1.04)

        if fence_type == "PALISADE":
            # 丸太砦の主柱
            start_p = ppos
            end_p = ppos + mathutils.Vector((jx * height, jy * height, post_h))
            build_cylinder_log(bm, start_p, end_p, radius=post_width * 0.75,
                               segments=8, spike_top=True, spike_height=post_h * 0.15,
                               mat_idx=0, uv_layer=uv_layer)
        else:
            # 角柱支柱
            c_pos = ppos + mathutils.Vector((0, 0, post_h * 0.5))
            build_box(bm, c_pos, post_width, post_width, post_h, rot_euler=rot_euler, mat_idx=0, uv_layer=uv_layer)
            
            # ピラミッド型尖り先端（PICKET または POST_AND_RAIL）
            if fence_type in ("PICKET", "POST_AND_RAIL"):
                tip_h = post_width * 0.6
                top_c = ppos + mathutils.Vector((0, 0, post_h))
                v1 = bm.verts.new(top_c + mathutils.Vector((-post_width*0.5, -post_width*0.5, 0)))
                v2 = bm.verts.new(top_c + mathutils.Vector(( post_width*0.5, -post_width*0.5, 0)))
                v3 = bm.verts.new(top_c + mathutils.Vector(( post_width*0.5,  post_width*0.5, 0)))
                v4 = bm.verts.new(top_c + mathutils.Vector((-post_width*0.5,  post_width*0.5, 0)))
                v_tip = bm.verts.new(top_c + mathutils.Vector((0, 0, tip_h)))
                for f_v in [(v1, v2, v_tip), (v2, v3, v_tip), (v3, v4, v_tip), (v4, v1, v_tip)]:
                    f = bm.faces.new(f_v)
                    f.material_index = 0

    # ── 2. セグメントごとの横木・筋交い・ピケット・丸太の生成
    for i in range(num_posts - 1):
        p1 = post_positions[i]
        p2 = post_positions[i+1]
        seg_vec = p2 - p1
        seg_len = seg_vec.length
        seg_dir = seg_vec.normalized()
        seg_mid = (p1 + p2) * 0.5

        if fence_type == "PALISADE":
            # 丸太砦（隙間なく並ぶ尖り丸太）
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
                l_end = l_pos + mathutils.Vector((l_jx * l_h, l_jy * l_h, l_h))
                build_cylinder_log(bm, l_start, l_end, radius=log_radius * l_rng.uniform(0.9, 1.1),
                                   segments=6, spike_top=True, spike_height=l_h * 0.18,
                                   mat_idx=0, uv_layer=uv_layer)

            # 背面サポート梁（2段）
            for r_lvl in (0.35, 0.75):
                beam_z = height * r_lvl
                beam_pos = seg_mid + mathutils.Vector((0, post_width * 0.6, beam_z))
                build_box(bm, beam_pos, seg_len * 0.98, rail_width, rail_height,
                          mat_idx=0, uv_layer=uv_layer)
                
                # 結束ロープ（マテリアルインデックス 1）
                rope_pos = p1 + mathutils.Vector((0, 0, beam_z))
                build_box(bm, rope_pos, post_width * 1.15, post_width * 1.15, rail_height * 0.45,
                          mat_idx=1, uv_layer=uv_layer)

        elif fence_type == "CROSS_BRACE":
            # 頑丈なX字筋交いフェンス（上下水平レール + X字クロス梁）
            r_bot_z = height * 0.22
            r_top_z = height * 0.82
            
            # 上下レール
            for rz in (r_bot_z, r_top_z):
                r_pos = seg_mid + mathutils.Vector((0, 0, rz))
                build_box(bm, r_pos, seg_len * 0.98, rail_width, rail_height, mat_idx=0, uv_layer=uv_layer)

            # X字斜め筋交い
            cross_h = r_top_z - r_bot_z
            cross_ang = math.atan2(cross_h, seg_len)
            cross_diag = math.sqrt(seg_len**2 + cross_h**2) * 0.95
            
            # 斜め梁1（左下➔右上）
            rot1 = mathutils.Euler((0, -cross_ang, 0), 'XYZ')
            build_box(bm, seg_mid + mathutils.Vector((0, 0, (r_bot_z + r_top_z)*0.5)),
                      cross_diag, rail_width * 0.85, rail_height * 0.85,
                      rot_euler=rot1, mat_idx=0, uv_layer=uv_layer)
            
            # 斜め梁2（左上➔右下）
            rot2 = mathutils.Euler((0, cross_ang, 0), 'XYZ')
            build_box(bm, seg_mid + mathutils.Vector((0, 0, (r_bot_z + r_top_z)*0.5)),
                      cross_diag, rail_width * 0.85, rail_height * 0.85,
                      rot_euler=rot2, mat_idx=0, uv_layer=uv_layer)

        elif fence_type == "PICKET":
            # ピケットフェンス（2段横木 + 先端山型の縦板等間隔配置）
            r_bot_z = height * 0.28
            r_top_z = height * 0.72
            for rz in (r_bot_z, r_top_z):
                r_pos = seg_mid + mathutils.Vector((0, -rail_width * 0.5, rz))
                build_box(bm, r_pos, seg_len * 0.98, rail_width, rail_height, mat_idx=0, uv_layer=uv_layer)

            # 縦板ピケット
            picket_w = post_width * 0.65
            picket_thick = post_width * 0.22
            picket_spacing = picket_w * 1.8
            picket_count = max(2, int(round(seg_len / picket_spacing)))
            
            for pi in range(picket_count):
                pt_ratio = (pi + 0.5) / float(picket_count)
                pk_x = p1.x + seg_vec.x * pt_ratio
                pk_rng = random.Random(seed + i * 50 + pi)
                pk_h = height * pk_rng.uniform(0.88, 0.96)
                pk_pos = mathutils.Vector((pk_x, p1.y + rail_width * 0.6, pk_h * 0.5))
                
                # 縦板胴体
                build_box(bm, pk_pos, picket_w, picket_thick, pk_h, mat_idx=0, uv_layer=uv_layer)
                
                # 先端山型カット
                tip_h = picket_w * 0.5
                v_top_c = mathutils.Vector((pk_x, p1.y + rail_width * 0.6, pk_h))
                v_p1 = bm.verts.new(v_top_c + mathutils.Vector((-picket_w*0.5, -picket_thick*0.5, 0)))
                v_p2 = bm.verts.new(v_top_c + mathutils.Vector(( picket_w*0.5, -picket_thick*0.5, 0)))
                v_p3 = bm.verts.new(v_top_c + mathutils.Vector(( picket_w*0.5,  picket_thick*0.5, 0)))
                v_p4 = bm.verts.new(v_top_c + mathutils.Vector((-picket_w*0.5,  picket_thick*0.5, 0)))
                v_ptip = bm.verts.new(v_top_c + mathutils.Vector((0, 0, tip_h)))
                for f_v in [(v_p1, v_p2, v_ptip), (v_p2, v_p3, v_ptip), (v_p3, v_p4, v_ptip), (v_p4, v_p1, v_ptip)]:
                    f = bm.faces.new(f_v)
                    f.material_index = 0

        else:
            # POST_AND_RAIL（シンプルな2〜3段横木）
            actual_rails = max(1, min(4, rails_count))
            for ri in range(actual_rails):
                rz = height * (0.28 + 0.5 * (ri / max(1, actual_rails - 1)))
                r_pos = seg_mid + mathutils.Vector((0, 0, rz))
                build_box(bm, r_pos, seg_len * 0.98, rail_width, rail_height, mat_idx=0, uv_layer=uv_layer)

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm.verts[:]
