import bpy
import bmesh
import math
import mathutils
import random

def build_tapered_blade(bm, base_pos, length=0.35, width=0.06, curve_x=0.0, curve_y=0.05, rot_euler=None, mat_idx=0, uv_layer=None):
    """【Mdesign式 5点先細り葉ブレード】UV.Y(0.0〜1.0)縦グラデーション対応"""
    half_w = width * 0.5
    mid_l = length * 0.52
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
            
            build_tapered_blade(
                bm, pt, length=leaf_sz, width=leaf_sz * 0.32,
                curve_x=0.0, curve_y=0.02 * side, rot_euler=rot,
                mat_idx=mat_idx, uv_layer=uv_layer
            )


def build_dense_foliage_clump(bm, center_pos, size_x=1.0, size_y=1.0, size_z=0.8, layers=4, blades_per_layer=18, seed=0, mat_idx=0, uv_layer=None):
    """【純粋な先細り葉ブレードの多層放射状展開（球体なし）】"""
    rng = random.Random(seed)
    
    for l in range(layers):
        t_layer = l / float(max(1, layers - 1)) # 0.0(最下層) 〜 1.0(最上層)
        layer_z = center_pos.z + t_layer * (size_z * 0.65)
        # 下層ほど広く外側に倒れ、上層ほど垂直に立つ
        pitch = (1.0 - t_layer * 0.75) * (math.pi * 0.45) # 80度傾斜(下) 〜 20度傾斜(上)
        layer_rad_x = (1.0 - t_layer * 0.3) * (size_x * 0.45)
        layer_rad_y = (1.0 - t_layer * 0.3) * (size_y * 0.45)
        blade_len = (size_z * 0.55) * rng.uniform(0.85, 1.15)
        blade_w = blade_len * 0.22

        b_count = int(blades_per_layer * (1.0 - t_layer * 0.25))
        for b in range(b_count):
            ang = b * (2.0 * math.pi / b_count) + rng.uniform(-0.15, 0.15) + (l * 0.3)
            bx = center_pos.x + math.cos(ang) * (layer_rad_x * 0.4)
            by = center_pos.y + math.sin(ang) * (layer_rad_y * 0.4)
            bz = layer_z
            b_pos = mathutils.Vector((bx, by, bz))

            # 外向き放射状に倒れる回転
            rot = mathutils.Euler((pitch + rng.uniform(-0.1, 0.1), rng.uniform(-0.15, 0.15), ang), 'XYZ')
            cx = rng.uniform(-0.03, 0.03)
            cy = rng.uniform(0.03, 0.08) # 外側へ反るカーブ
            build_tapered_blade(bm, b_pos, length=blade_len, width=blade_w,
                                curve_x=cx, curve_y=cy, rot_euler=rot,
                                mat_idx=mat_idx, uv_layer=uv_layer)


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
    """低木・茂み・シダ植物のプロシージャル BMesh 生成エンジン（球体ゼロ・完全先細り葉多層展開版）"""
    rng = random.Random(seed)
    half_x = size_x * 0.5
    half_y = size_y * 0.5

    if bush_type == "FERN_CLUMP":
        # 🌿 シダ植物の株（リアル羽状複葉）
        frond_count = max(10, int(density * 0.75))
        frond_len = max(size_x, size_y) * 0.65
        for fi in range(frond_count):
            ang = fi * (2.0 * math.pi / frond_count) + rng.uniform(-0.15, 0.15)
            f_len = frond_len * rng.uniform(0.85, 1.15)
            base_p = mathutils.Vector((rng.uniform(-0.03, 0.03), rng.uniform(-0.03, 0.03), size_z * 0.05))
            build_fern_frond(bm, base_p, frond_len=f_len, base_angle=ang,
                             mat_idx=0, uv_layer=uv_layer, seed=seed + fi * 31)

    elif bush_type == "HEDGE_ROW":
        # 🧱 生垣ブロック（多層先細りブレードクラスタが連なる生垣）
        num_clumps_x = max(2, int(round(size_x / 0.8)))
        num_clumps_y = max(1, int(round(size_y / 0.8)))
        for ix in range(num_clumps_x):
            for iy in range(num_clumps_y):
                cx = -half_x + (ix + 0.5) * (size_x / num_clumps_x)
                cy = -half_y + (iy + 0.5) * (size_y / max(1, num_clumps_y))
                c_pos = mathutils.Vector((cx, cy, 0.0))
                build_dense_foliage_clump(bm, c_pos, size_x=size_x/num_clumps_x*1.3, size_y=size_y/max(1, num_clumps_y)*1.3,
                                          size_z=size_z, layers=4, blades_per_layer=14,
                                          seed=seed + ix*10 + iy, mat_idx=0, uv_layer=uv_layer)

    elif bush_type == "WILD_SHRUB":
        # 🌿 野生の藪（四方に広がる木製細枝 ＋ 枝先の多層先細り葉クラスタ）
        stem_count = max(5, int(density * 0.35))
        for si in range(stem_count):
            ang = si * (2.0 * math.pi / stem_count) + rng.uniform(-0.25, 0.25)
            reach = rng.uniform(0.65, 1.0)
            s_len = max(size_x, size_y) * 0.48 * reach
            s_h = size_z * rng.uniform(0.5, 0.85)
            
            mid_p = mathutils.Vector((math.cos(ang) * s_len * 0.5, math.sin(ang) * s_len * 0.5, s_h * 0.45))
            tip_p = mathutils.Vector((math.cos(ang) * s_len, math.sin(ang) * s_len, s_h))
            pts = [mathutils.Vector((0, 0, 0)), mid_p, tip_p]
            radii = [0.032 * (size_z / 0.9), 0.02 * (size_z / 0.9), 0.01 * (size_z / 0.9)]
            build_stem_tube(bm, pts, radii, segments=5, mat_idx=1, uv_layer=uv_layer)

            # 枝先の多層ブレードクラスタ
            build_dense_foliage_clump(bm, tip_p, size_x=leaf_size * 2.2, size_y=leaf_size * 2.2,
                                      size_z=leaf_size * 1.8, layers=3, blades_per_layer=8,
                                      seed=seed + si * 20, mat_idx=0, uv_layer=uv_layer)

    else:
        # 🌳 ROUND_BUSH（丸型低木：中心の細幹 ＋ 4〜5層の放射状先細り葉ブレード計100〜150枚展開）
        # 1. 根元の中心細幹
        stem_pts = [mathutils.Vector((0, 0, 0)), mathutils.Vector((0, 0, size_z * 0.35))]
        build_stem_tube(bm, stem_pts, [0.035, 0.02], segments=5, mat_idx=1, uv_layer=uv_layer)

        # 2. 中心の密集メインクラスタ
        build_dense_foliage_clump(
            bm, mathutils.Vector((0, 0, 0)),
            size_x=size_x, size_y=size_y, size_z=size_z,
            layers=5, blades_per_layer=20,
            seed=seed, mat_idx=0, uv_layer=uv_layer
        )

        # 3. 周囲のサブクラスタ（ボリュームとふんわり感を補強）
        sub_count = 4
        for sbi in range(sub_count):
            s_ang = sbi * (2.0 * math.pi / sub_count) + rng.uniform(-0.2, 0.2)
            s_dist = min(half_x, half_y) * 0.35
            s_pos = mathutils.Vector((math.cos(s_ang) * s_dist, math.sin(s_ang) * s_dist, size_z * 0.15))
            build_dense_foliage_clump(
                bm, s_pos,
                size_x=size_x * 0.65, size_y=size_y * 0.65, size_z=size_z * 0.75,
                layers=3, blades_per_layer=10,
                seed=seed + sbi * 37, mat_idx=0, uv_layer=uv_layer
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
