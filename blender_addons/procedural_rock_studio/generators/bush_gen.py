import bpy
import bmesh
import math
import mathutils
import random

def build_tapered_leaf_blade(bm, base_pos, length=0.35, width=0.06, curve_x=0.0, curve_y=0.05, rot_euler=None, mat_idx=0, uv_layer=None):
    """【Mdesign式 5点先細り葉メッシュ】UV.Y(0.0〜1.0)縦グラデーション対応"""
    half_w = width * 0.5
    mid_l = length * 0.55
    rot_mat = rot_euler.to_matrix().to_4x4() if rot_euler else mathutils.Matrix.Identity(4)

    # 5頂点（根元2, 中間2, 先端1）
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


def build_leaf_cluster_tuft(bm, center_pos, size=0.35, blades_count=4, seed=0, mat_idx=0, uv_layer=None):
    """【先細り葉クラスタ】放射状に3〜5枚の葉が広がる密集ユニット"""
    rng = random.Random(seed)
    for b in range(blades_count):
        ang = b * (2.0 * math.pi / blades_count) + rng.uniform(-0.25, 0.25)
        pitch = rng.uniform(0.3, 0.8) # 外側に広がる傾斜
        roll = rng.uniform(-0.3, 0.3)
        rot = mathutils.Euler((pitch, roll, ang), 'XYZ')
        
        b_len = size * rng.uniform(0.85, 1.25)
        b_w = b_len * 0.25
        cx = rng.uniform(-0.04, 0.04)
        cy = rng.uniform(0.02, 0.08)
        build_tapered_leaf_blade(bm, center_pos, length=b_len, width=b_w,
                                 curve_x=cx, curve_y=cy, rot_euler=rot,
                                 mat_idx=mat_idx, uv_layer=uv_layer)


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
    """【リアルシダ羽状複葉】アーチを描く軸に沿って左右に先細り小葉がびっしり並ぶ"""
    rng = random.Random(seed)
    segs = 8
    arch_pts = []
    
    # 軸の曲線
    for i in range(segs + 1):
        t = i / float(segs)
        dist = t * frond_len
        drop = -(t ** 2.0) * (frond_len * 0.45) + math.sin(t * math.pi) * (frond_len * 0.18)
        x = base_pos.x + math.cos(base_angle) * dist
        y = base_pos.y + math.sin(base_angle) * dist
        z = base_pos.z + drop
        arch_pts.append(mathutils.Vector((x, y, z)))

    # 葉軸チューブ
    radii = [(1.0 - (i/float(segs))*0.7) * 0.015 for i in range(segs+1)]
    build_stem_tube(bm, arch_pts, radii, segments=4, mat_idx=1, uv_layer=uv_layer)

    # 左右の小葉（5点先細りメッシュ）
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


def build_foliage_volume_core(bm, center_pos, radius=0.45, seed=0, mat_idx=0):
    """【有機的Icosphere変形ボリュームコア】茂みの中心部を埋めるふんわりメッシュ"""
    rng = random.Random(seed)
    res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=radius)
    v_list = res['verts']
    
    for v in v_list:
        p = v.co
        noise = (math.sin(p.x * 5.0 + seed) * math.cos(p.y * 5.0 + seed * 0.7) * 0.15)
        v.co = p * (1.0 + noise)

    bmesh.ops.translate(bm, vec=center_pos, verts=v_list)
    for f in bm.faces:
        if all(v in v_list for v in f.verts):
            f.material_index = mat_idx


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
    """低木・茂み・シダ植物のプロシージャル BMesh 生成エンジン（学習資産完全統合版）"""
    rng = random.Random(seed)
    half_x = size_x * 0.5
    half_y = size_y * 0.5
    center_z = size_z * 0.45

    if bush_type == "FERN_CLUMP":
        # 🌿 シダ植物の株（放射状に広がるリアル羽状複葉）
        frond_count = max(10, int(density * 0.75))
        frond_len = max(size_x, size_y) * 0.65
        for fi in range(frond_count):
            ang = fi * (2.0 * math.pi / frond_count) + rng.uniform(-0.15, 0.15)
            f_len = frond_len * rng.uniform(0.85, 1.15)
            base_p = mathutils.Vector((rng.uniform(-0.03, 0.03), rng.uniform(-0.03, 0.03), size_z * 0.05))
            build_fern_frond(bm, base_p, frond_len=f_len, base_angle=ang,
                             mat_idx=0, uv_layer=uv_layer, seed=seed + fi * 31)

    elif bush_type == "HEDGE_ROW":
        # 🧱 生垣ブロック（内部コア ＋ 表面の先細り葉クラスタ密集）
        steps_x = max(3, int(size_x / max(0.25, leaf_size * 0.9)))
        steps_y = max(2, int(size_y / max(0.25, leaf_size * 0.9)))
        steps_z = max(2, int(size_z / max(0.25, leaf_size * 0.9)))

        for ix in range(steps_x):
            for iy in range(steps_y):
                for iz in range(steps_z):
                    tx = -half_x + (ix + 0.5) * (size_x / steps_x) + rng.uniform(-0.03, 0.03)
                    ty = -half_y + (iy + 0.5) * (size_y / steps_y) + rng.uniform(-0.03, 0.03)
                    tz = (iz + 0.5) * (size_z / steps_z) + rng.uniform(-0.03, 0.03)
                    pos = mathutils.Vector((tx, ty, tz))
                    
                    # 葉クラスタ（先細りブレード×3枚）
                    build_leaf_cluster_tuft(bm, pos, size=leaf_size, blades_count=3,
                                            seed=seed + ix*50 + iy*10 + iz, mat_idx=0, uv_layer=uv_layer)

    elif bush_type == "WILD_SHRUB":
        # 🌿 野生の藪（木製細枝 ＋ 枝先の先細り葉クラスタ密集）
        stem_count = max(6, int(density * 0.4))
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

            # 中間部と先端部に葉クラスタ（各3〜5枚）
            for pt in (mid_p, tip_p):
                build_leaf_cluster_tuft(bm, pt, size=leaf_size * rng.uniform(0.9, 1.2),
                                        blades_count=4, seed=seed + si*20, mat_idx=0, uv_layer=uv_layer)

    else:
        # 🌳 ROUND_BUSH（丸型ふんわり低木：内部ボリューム ＋ 5点先細り葉クラスタ超密集）
        # 1. 内部ボリュームコア（隙間防止）
        build_foliage_volume_core(bm, mathutils.Vector((0, 0, center_z)), radius=min(half_x, half_y)*0.75, seed=seed, mat_idx=0)

        # 2. 表面を覆い尽くす先細り葉クラスタ（40〜60箇所 × 各3〜4枚 = 計150〜200枚以上のリアルな葉）
        clusters_count = max(20, density * 2)
        for ci in range(clusters_count):
            u = rng.random()
            v = rng.random()
            theta = u * 2.0 * math.pi
            phi = math.acos(v) # 半球ドーム
            r = rng.uniform(0.65, 1.05)

            rx = math.sin(phi) * math.cos(theta) * half_x * r
            ry = math.sin(phi) * math.sin(theta) * half_y * r
            rz = math.cos(phi) * (size_z * 0.55) * r + center_z * 0.25
            pos = mathutils.Vector((rx, ry, rz))

            build_leaf_cluster_tuft(
                bm, pos,
                size=leaf_size * rng.uniform(0.85, 1.2),
                blades_count=rng.randint(3, 4),
                seed=seed + ci * 17,
                mat_idx=0,
                uv_layer=uv_layer
            )

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
