import bpy
import bmesh
import math
import mathutils
import random

def build_leaf_card(bm, center_pos, size_x=0.35, size_y=0.35, rot_euler=None, mat_idx=0, uv_layer=None):
    """単一葉カード（2面クロスまたは単一面）"""
    hx = size_x * 0.5
    hy = size_y * 0.5
    rot_mat = rot_euler.to_matrix().to_4x4() if rot_euler else mathutils.Matrix.Identity(4)

    # 十字に交差する2枚のビルボード
    for ang_offset in (0.0, math.pi * 0.5):
        sub_rot = mathutils.Euler((0, 0, ang_offset)).to_matrix().to_4x4()
        comb_rot = rot_mat @ sub_rot

        p1 = comb_rot @ mathutils.Vector((-hx, 0.0, 0.0))
        p2 = comb_rot @ mathutils.Vector(( hx, 0.0, 0.0))
        p3 = comb_rot @ mathutils.Vector(( hx, 0.0, size_y))
        p4 = comb_rot @ mathutils.Vector((-hx, 0.0, size_y))

        v1 = bm.verts.new(center_pos + p1)
        v2 = bm.verts.new(center_pos + p2)
        v3 = bm.verts.new(center_pos + p3)
        v4 = bm.verts.new(center_pos + p4)

        f = bm.faces.new((v1, v2, v3, v4))
        f.material_index = mat_idx

        if uv_layer:
            f.loops[0][uv_layer].uv = (0.0, 0.0)
            f.loops[1][uv_layer].uv = (1.0, 0.0)
            f.loops[2][uv_layer].uv = (1.0, 1.0)
            f.loops[3][uv_layer].uv = (0.0, 1.0)


def build_fern_frond(bm, base_pos, frond_len=0.8, base_angle=0.0, pitch=0.45, mat_idx=0, uv_layer=None, seed=0):
    """シダ植物のアーチ羽状複葉（Frond）"""
    rng = random.Random(seed)
    segs = 6
    arch_pts = []
    
    for i in range(segs + 1):
        t = i / float(segs)
        dist = t * frond_len
        # アーチ状に外側＆下へ垂れる曲線
        drop = -(t ** 1.8) * (frond_len * 0.4) + math.sin(t * math.pi) * (frond_len * 0.15)
        x = base_pos.x + math.cos(base_angle) * dist
        y = base_pos.y + math.sin(base_angle) * dist
        z = base_pos.z + drop
        arch_pts.append(mathutils.Vector((x, y, z)))

    # 葉軸に沿って左右に小葉カードを配置
    for i in range(1, segs):
        pt = arch_pts[i]
        t = i / float(segs)
        leaf_sz = (1.0 - t * 0.6) * (frond_len * 0.28)
        
        # 左右の羽
        for side in (-1.0, 1.0):
            side_ang = base_angle + side * (math.pi * 0.5) + rng.uniform(-0.1, 0.1)
            tilt = rng.uniform(-0.15, 0.15)
            rot = mathutils.Euler((tilt, math.pi * 0.25 * side, side_ang), 'XYZ')
            
            p1 = mathutils.Vector((-leaf_sz*0.5, 0, 0))
            p2 = mathutils.Vector(( leaf_sz*0.5, 0, 0))
            p3 = mathutils.Vector(( leaf_sz*0.3, 0, leaf_sz*0.8))
            p4 = mathutils.Vector((-leaf_sz*0.3, 0, leaf_sz*0.8))

            rot_m = rot.to_matrix().to_4x4()
            v1 = bm.verts.new(pt + rot_m @ p1)
            v2 = bm.verts.new(pt + rot_m @ p2)
            v3 = bm.verts.new(pt + rot_m @ p3)
            v4 = bm.verts.new(pt + rot_m @ p4)

            f = bm.faces.new((v1, v2, v3, v4))
            f.material_index = mat_idx
            if uv_layer:
                f.loops[0][uv_layer].uv = (0.0, 0.0)
                f.loops[1][uv_layer].uv = (1.0, 0.0)
                f.loops[2][uv_layer].uv = (1.0, 1.0)
                f.loops[3][uv_layer].uv = (0.0, 1.0)


def build_stem_tube(bm, pts, radii, segments=4, mat_idx=1, uv_layer=None):
    """細枝チューブ（Stem）"""
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


def build_volume_canopy(bm, center_pos, radius=0.45, seed=0, mat_idx=0, uv_layer=None):
    """スタイライズド有機的ボリューム樹冠（Icosphere変形）"""
    rng = random.Random(seed)
    res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=radius)
    v_list = res['verts']
    
    sx = rng.uniform(0.85, 1.25)
    sy = rng.uniform(0.85, 1.25)
    sz = rng.uniform(0.75, 1.1)

    for v in v_list:
        p = v.co
        noise = (math.sin(p.x * 4.0 + seed) * math.cos(p.y * 4.0 + seed * 0.5) * 0.18)
        v.co.x = (p.x * sx) * (1.0 + noise)
        v.co.y = (p.y * sy) * (1.0 + noise)
        v.co.z = (p.z * sz) * (1.0 + noise)

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
    density=18,
    leaf_size=0.35,
    seed=0,
    uv_layer=None
):
    """低木・茂み・シダ植物のプロシージャル BMesh 生成エンジン"""
    rng = random.Random(seed)
    half_x = size_x * 0.5
    half_y = size_y * 0.5

    if bush_type == "FERN_CLUMP":
        # 🌿 シダ植物の株（中心から放射状に広がるアーチ葉）
        frond_count = max(8, int(density * 0.8))
        frond_len = max(size_x, size_y) * 0.55
        for fi in range(frond_count):
            ang = fi * (2.0 * math.pi / frond_count) + rng.uniform(-0.15, 0.15)
            f_len = frond_len * rng.uniform(0.85, 1.15)
            base_p = mathutils.Vector((rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04), size_z * 0.05))
            build_fern_frond(bm, base_p, frond_len=f_len, base_angle=ang,
                             mat_idx=0, uv_layer=uv_layer, seed=seed + fi * 23)

    elif bush_type == "HEDGE_ROW":
        # 🧱 生垣ブロック（直方体ボリューム内に均一散布）
        steps_x = max(2, int(size_x / max(0.2, leaf_size * 0.8)))
        steps_y = max(1, int(size_y / max(0.2, leaf_size * 0.8)))
        steps_z = max(1, int(size_z / max(0.2, leaf_size * 0.8)))

        for ix in range(steps_x):
            for iy in range(steps_y):
                for iz in range(steps_z):
                    tx = -half_x + (ix + 0.5) * (size_x / steps_x) + rng.uniform(-0.05, 0.05)
                    ty = -half_y + (iy + 0.5) * (size_y / steps_y) + rng.uniform(-0.05, 0.05)
                    tz = (iz + 0.5) * (size_z / steps_z) + rng.uniform(-0.05, 0.05)
                    pos = mathutils.Vector((tx, ty, tz))

                    if foliage_style == "VOLUME_CANOPY":
                        build_volume_canopy(bm, pos, radius=leaf_size * 0.55, seed=seed + ix*100 + iy*10 + iz, mat_idx=0)
                    else:
                        rot = mathutils.Euler((rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), rng.uniform(0, math.pi*2)), 'XYZ')
                        build_leaf_card(bm, pos, size_x=leaf_size, size_y=leaf_size, rot_euler=rot, mat_idx=0, uv_layer=uv_layer)

    elif bush_type == "WILD_SHRUB":
        # 🌿 野生の藪（根元から四方に伸びる細枝 ＋ 枝先の葉クラスタ）
        stem_count = max(4, int(density * 0.35))
        for si in range(stem_count):
            ang = si * (2.0 * math.pi / stem_count) + rng.uniform(-0.25, 0.25)
            reach = rng.uniform(0.5, 0.95)
            s_len = max(size_x, size_y) * 0.45 * reach
            s_h = size_z * rng.uniform(0.65, 1.0)
            
            # 細枝パス
            pts = [
                mathutils.Vector((0, 0, 0)),
                mathutils.Vector((math.cos(ang) * s_len * 0.45, math.sin(ang) * s_len * 0.45, s_h * 0.4)),
                mathutils.Vector((math.cos(ang) * s_len, math.sin(ang) * s_len, s_h))
            ]
            radii = [0.035 * (size_z / 0.9), 0.022 * (size_z / 0.9), 0.012 * (size_z / 0.9)]
            build_stem_tube(bm, pts, radii, segments=4, mat_idx=1, uv_layer=uv_layer)

            # 枝先の葉クラスタ
            for pt in (pts[1], pts[2]):
                c_cards = rng.randint(2, 4)
                for ci in range(c_cards):
                    off = mathutils.Vector((rng.uniform(-0.08, 0.08), rng.uniform(-0.08, 0.08), rng.uniform(-0.05, 0.08)))
                    if foliage_style == "VOLUME_CANOPY":
                        build_volume_canopy(bm, pt + off, radius=leaf_size * 0.6, seed=seed + si*10 + ci, mat_idx=0)
                    else:
                        rot = mathutils.Euler((rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), rng.uniform(0, math.pi*2)), 'XYZ')
                        build_leaf_card(bm, pt + off, size_x=leaf_size * rng.uniform(0.85, 1.2), size_y=leaf_size * rng.uniform(0.85, 1.2),
                                        rot_euler=rot, mat_idx=0, uv_layer=uv_layer)

    else:
        # 🌳 ROUND_BUSH（丸型ふんわり低木：ドーム状に多層散布）
        card_count = max(8, density)
        center_z = size_z * 0.45
        for ci in range(card_count):
            # 半球ドーム状に均一散布
            u = rng.random()
            v = rng.random()
            theta = u * 2.0 * math.pi
            phi = math.acos(v) # 0 to pi/2
            r = (rng.uniform(0.35, 1.0) ** 0.5)

            rx = math.sin(phi) * math.cos(theta) * half_x * r
            ry = math.sin(phi) * math.sin(theta) * half_y * r
            rz = math.cos(phi) * (size_z * 0.5) * r + center_z * 0.3
            pos = mathutils.Vector((rx, ry, rz))

            if foliage_style == "VOLUME_CANOPY":
                build_volume_canopy(bm, pos, radius=leaf_size * 0.65, seed=seed + ci * 19, mat_idx=0)
            else:
                # 茂みの中心から外向きの法線に近い角度でカードを配置
                dir_out = (pos - mathutils.Vector((0, 0, center_z))).normalized()
                rot = dir_out.to_track_quat('Z', 'Y').to_euler()
                rot.x += rng.uniform(-0.35, 0.35)
                rot.y += rng.uniform(-0.35, 0.35)
                build_leaf_card(bm, pos, size_x=leaf_size * rng.uniform(0.85, 1.2),
                                size_y=leaf_size * rng.uniform(0.85, 1.2),
                                rot_euler=rot, mat_idx=0, uv_layer=uv_layer)

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm.verts[:]


def apply_bush_spherical_normals(obj, leaf_mat_idx=0):
    """茂みの中心から放射状に外向き法線を設定（球状法線転送）"""
    if not obj or obj.type != 'MESH':
        return
    mesh = obj.data
    mesh.calc_normals()
    
    # 茂みの中心座標
    center = mathutils.Vector((0, 0, obj.dimensions.z * 0.45))

    # 各ポリゴンの頂点法線を外向きベクトルに設定
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
