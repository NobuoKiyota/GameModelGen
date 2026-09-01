import bpy
import bmesh
import math
import mathutils
import random

def build_tapered_leaf_blade(bm, base_pos, length=0.25, width=0.05, curve_x=0.0, curve_y=0.04, rot_euler=None, mat_idx=0, uv_layer=None):
    """【Mdesign式 5点先細り葉メッシュ】"""
    half_w = width * 0.5
    mid_l = length * 0.55
    rot_mat = rot_euler.to_matrix().to_4x4() if rot_euler else mathutils.Matrix.Identity(4)

    p_bl  = rot_mat @ mathutils.Vector((-half_w, 0.0, 0.0))
    p_br  = rot_mat @ mathutils.Vector(( half_w, 0.0, 0.0))
    p_ml  = rot_mat @ mathutils.Vector((-half_w * 0.6 + curve_x * 0.5, curve_y * 0.5, mid_l))
    p_mr  = rot_mat @ mathutils.Vector(( half_w * 0.6 + curve_x * 0.5, curve_y * 0.5, mid_l))
    p_tip = rot_mat @ mathutils.Vector((curve_x, curve_y, length))

    v_bl  = bm.verts.new(base_pos + p_bl)
    v_br  = bm.verts.new(base_pos + p_br)
    v_ml  = bm.verts.new(base_pos + p_ml)
    v_mr  = bm.verts.new(base_pos + p_mr)
    v_tip = bm.verts.new(base_pos + p_tip)

    f_bot = bm.faces.new((v_bl, v_br, v_mr, v_ml))
    f_top = bm.faces.new((v_ml, v_mr, v_tip))
    f_bot.material_index = mat_idx
    f_top.material_index = mat_idx

    if uv_layer:
        for loop, uv in zip(f_bot.loops, [(0.0, 0.0), (1.0, 0.0), (1.0, 0.5), (0.0, 0.5)]):
            loop[uv_layer].uv = uv
        for loop, uv in zip(f_top.loops, [(0.0, 0.5), (1.0, 0.5), (0.5, 1.0)]):
            loop[uv_layer].uv = uv

    return [v_bl, v_br, v_ml, v_mr, v_tip]


def build_foliage_puff(bm, center_pos, radius_x=0.3, radius_y=0.3, radius_z=0.25, seed=0, mat_idx=0, uv_layer=None):
    """【モコモコ葉クラウドパフ】ボロノイノイズで有機的に波打つ個別の葉塊"""
    rng = random.Random(seed)
    res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    v_list = res['verts']
    
    # 表面に葉っぱのモコモコした細かな凹凸を波打たせる
    for v in v_list:
        p = v.co.normalized()
        # 多重周波数ノイズで「ブロッコリー・雲」のような有機的凹凸を形成
        noise = (math.sin(p.x * 6.0 + seed) * math.cos(p.y * 6.0 + seed * 0.7) * 0.18
               + math.sin(p.y * 12.0 + seed * 2.0) * math.cos(p.z * 12.0 + seed * 1.5) * 0.08)
        r = 1.0 + noise
        v.co = mathutils.Vector((p.x * radius_x * r, p.y * radius_y * r, p.z * radius_z * r))

    bmesh.ops.translate(bm, vec=center_pos, verts=v_list)
    for f in bm.faces:
        if all(v in v_list for v in f.verts):
            f.material_index = mat_idx

    # パフの表面に先細り葉ブレードを数枚アクセント配置
    for _ in range(rng.randint(4, 7)):
        u = rng.random()
        v = rng.random()
        theta = u * 2.0 * math.pi
        phi = math.acos(2.0 * v - 1.0)
        nx = math.sin(phi) * math.cos(theta)
        ny = math.sin(phi) * math.sin(theta)
        nz = math.cos(phi)
        
        pos = center_pos + mathutils.Vector((nx * radius_x * 0.95, ny * radius_y * 0.95, nz * radius_z * 0.95))
        dir_out = mathutils.Vector((nx, ny, nz)).normalized()
        rot = dir_out.to_track_quat('Z', 'Y').to_euler()
        rot.x += rng.uniform(-0.25, 0.25)
        rot.y += rng.uniform(-0.25, 0.25)
        build_tapered_leaf_blade(bm, pos, length=radius_x * 0.65, width=radius_x * 0.18,
                                 rot_euler=rot, mat_idx=mat_idx, uv_layer=uv_layer)


def build_stem_tube(bm, pts, radii, segments=5, mat_idx=1, uv_layer=None):
    """【木製細枝チューブ】"""
    if len(pts) < 2:
        return
    ring_verts = []
    up = mathutils.Vector((0, 0, 1))

    for i, pt in enumerate(pts):
        if i < len(pts) - 1:
            dir_norm = (pts[i+1] - pt).normalized()
        else:
            dir_norm = (pt - pts[i-1]).normalized()

        if abs(dir_norm.dot(up)) > 0.98:
            side1 = dir_norm.cross(mathutils.Vector((1, 0, 0))).normalized()
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


def build_fern_frond(bm, base_pos, frond_len=0.9, base_angle=0.0, mat_idx=0, uv_layer=None, seed=0):
    """【リアルシダ羽状複葉】"""
    rng = random.Random(seed)
    segs = 8
    arch_pts = []
    
    for i in range(segs + 1):
        t = i / float(segs)
        dist = t * frond_len
        drop = -(t ** 2.0) * (frond_len * 0.45) + math.sin(t * math.pi) * (frond_len * 0.18)
        x = base_pos.x + math.cos(base_angle) * dist
        y = base_pos.y + math.sin(base_angle) * dist
        z = base_pos.z + drop
        arch_pts.append(mathutils.Vector((x, y, z)))

    radii = [(1.0 - (i/float(segs))*0.7) * 0.015 for i in range(segs+1)]
    build_stem_tube(bm, arch_pts, radii, segments=4, mat_idx=1, uv_layer=uv_layer)

    for i in range(1, segs):
        pt = arch_pts[i]
        t = i / float(segs)
        leaf_sz = (1.0 - t * 0.55) * (frond_len * 0.32)
        
        for side in (-1.0, 1.0):
            side_ang = base_angle + side * (math.pi * 0.42) + rng.uniform(-0.08, 0.08)
            pitch = rng.uniform(-0.1, 0.2)
            rot = mathutils.Euler((pitch, math.pi * 0.22 * side, side_ang), 'XYZ')
            
            build_tapered_leaf_blade(
                bm, pt, length=leaf_sz, width=leaf_sz * 0.32,
                curve_x=0.0, curve_y=0.02 * side, rot_euler=rot,
                mat_idx=mat_idx, uv_layer=uv_layer
            )


def build_bush_mesh(
    bm,
    bush_type="ROUND_BUSH",
    foliage_style="LEAF_CARDS",
    size_x=1.2,
    size_y=1.2,
    size_z=0.9,
    density=24,
    leaf_size=0.32,
    seed=0,
    uv_layer=None
):
    """低木・茂み・シダ植物のプロシージャル BMesh 生成エンジン（多重クラウドパフ版）"""
    rng = random.Random(seed)
    half_x = size_x * 0.5
    half_y = size_y * 0.5
    center_z = size_z * 0.45

    if bush_type == "FERN_CLUMP":
        # 🌿 シダ植物の株
        frond_count = max(10, int(density * 0.75))
        frond_len = max(size_x, size_y) * 0.65
        for fi in range(frond_count):
            ang = fi * (2.0 * math.pi / frond_count) + rng.uniform(-0.15, 0.15)
            f_len = frond_len * rng.uniform(0.85, 1.15)
            base_p = mathutils.Vector((rng.uniform(-0.03, 0.03), rng.uniform(-0.03, 0.03), size_z * 0.05))
            build_fern_frond(bm, base_p, frond_len=f_len, base_angle=ang,
                             mat_idx=0, uv_layer=uv_layer, seed=seed + fi * 31)

    elif bush_type == "HEDGE_ROW":
        # 🧱 生垣ブロック（複数のパフが連なる生垣）
        num_puffs_x = max(2, int(round(size_x / 0.75)))
        num_puffs_y = max(1, int(round(size_y / 0.75)))
        puff_rx = (size_x / num_puffs_x) * 0.65
        puff_ry = (size_y / max(1, num_puffs_y)) * 0.65
        puff_rz = size_z * 0.45

        for ix in range(num_puffs_x):
            for iy in range(num_puffs_y):
                px = -half_x + (ix + 0.5) * (size_x / num_puffs_x) + rng.uniform(-0.04, 0.04)
                py = -half_y + (iy + 0.5) * (size_y / max(1, num_puffs_y)) + rng.uniform(-0.04, 0.04)
                pz = center_z + rng.uniform(-0.05, 0.05)
                build_foliage_puff(bm, mathutils.Vector((px, py, pz)),
                                   radius_x=puff_rx, radius_y=puff_ry, radius_z=puff_rz,
                                   seed=seed + ix*10 + iy, mat_idx=0, uv_layer=uv_layer)

    elif bush_type == "WILD_SHRUB":
        # 🌿 野生の藪（細枝 ＋ 枝先に重なるモコモコパフ）
        stem_count = max(5, int(density * 0.35))
        for si in range(stem_count):
            ang = si * (2.0 * math.pi / stem_count) + rng.uniform(-0.25, 0.25)
            reach = rng.uniform(0.65, 1.0)
            s_len = max(size_x, size_y) * 0.48 * reach
            s_h = size_z * rng.uniform(0.7, 1.05)
            
            mid_p = mathutils.Vector((math.cos(ang) * s_len * 0.5, math.sin(ang) * s_len * 0.5, s_h * 0.45))
            tip_p = mathutils.Vector((math.cos(ang) * s_len, math.sin(ang) * s_len, s_h))
            pts = [mathutils.Vector((0, 0, 0)), mid_p, tip_p]
            radii = [0.032 * (size_z / 0.9), 0.02 * (size_z / 0.9), 0.01 * (size_z / 0.9)]
            build_stem_tube(bm, pts, radii, segments=5, mat_idx=1, uv_layer=uv_layer)

            # 枝先にモコモコパフ
            p_rad = rng.uniform(0.22, 0.35) * (size_z / 0.9)
            build_foliage_puff(bm, tip_p, radius_x=p_rad, radius_y=p_rad, radius_z=p_rad * 0.85,
                               seed=seed + si * 20, mat_idx=0, uv_layer=uv_layer)

    else:
        # 🌳 ROUND_BUSH（丸型低木：大小 7〜10 個のパフが有機的に重なり合うブドウの房/雲構造）
        num_puffs = max(7, int(density * 0.45))
        base_puff_r = min(half_x, half_y) * 0.55
        
        # 1. 根元の中心細枝（土台）
        stem_pts = [mathutils.Vector((0, 0, 0)), mathutils.Vector((0, 0, center_z * 0.6))]
        build_stem_tube(bm, stem_pts, [0.04, 0.025], segments=5, mat_idx=1, uv_layer=uv_layer)

        # 2. クラウド状に重なり合う複数のパフ
        for pi in range(num_puffs):
            if pi == 0:
                # トップクラウン（頭頂部）
                p_pos = mathutils.Vector((rng.uniform(-0.05, 0.05), rng.uniform(-0.05, 0.05), size_z * 0.65))
                pr_x = base_puff_r * rng.uniform(0.95, 1.2)
                pr_y = base_puff_r * rng.uniform(0.95, 1.2)
                pr_z = base_puff_r * rng.uniform(0.75, 0.95)
            else:
                # 周囲に広がるサイドパフ
                ang = (pi - 1) * (2.0 * math.pi / (num_puffs - 1)) + rng.uniform(-0.2, 0.2)
                dist = min(half_x, half_y) * rng.uniform(0.45, 0.75)
                pz = center_z * rng.uniform(0.55, 1.0)
                px = math.cos(ang) * dist
                py = math.sin(ang) * dist
                p_pos = mathutils.Vector((px, py, pz))
                
                pr_x = base_puff_r * rng.uniform(0.8, 1.15)
                pr_y = base_puff_r * rng.uniform(0.8, 1.15)
                pr_z = base_puff_r * rng.uniform(0.7, 0.9)

            build_foliage_puff(bm, p_pos, radius_x=pr_x, radius_y=pr_y, radius_z=pr_z,
                               seed=seed + pi * 17, mat_idx=0, uv_layer=uv_layer)

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm.verts[:]


def apply_bush_spherical_normals(obj, leaf_mat_idx=0):
    """【樹冠球状法線転送】茂みの中心から放射状に法線を整え、ふんわり陰影を実現"""
    if not obj or obj.type != 'MESH':
        return
    mesh = obj.data
    mesh.calc_normals()
    center = mathutils.Vector((0, 0, obj.dimensions.z * 0.45))

    custom_normals = []
    for poly in mesh.polygons:
        for loop_idx in poly.loop_indices:
            vert_idx = mesh.loops[loop_idx].vertex_index
            v_co = mesh.vertices[vert_idx].co
            if poly.material_index == leaf_mat_idx:
                dir_vec = (v_co - center).normalized()
                custom_normals.append(dir_vec)
            else:
                custom_normals.append(mesh.vertices[vert_idx].normal)

    mesh.use_auto_smooth = True
    mesh.normals_split_custom_set(custom_normals)
