import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

from .window_gen import add_box_to_bmesh, add_cylinder_bar
from .architecture_gen import build_procedural_stone_arch_bmesh
from .pillar_gen import build_roman_fluted_pillar
from ..materials.image_shaders import create_door_wood_material, create_door_iron_material
from ..materials.nature_shaders import create_procedural_pillar_shader


def _door_arch_inner_z(x, style, r_in, spring_z, arch_rise):
    """build_procedural_stone_arch_bmesh の内周アーチカーブ(inner_pts)と同一の数式で、
    扉パネルの上端カーブを算出する（石枠の開口内周に扉の板がぴったり追従するように）。"""
    if style == 'GOTHIC_POINTED':
        d_center = r_in * 0.45
        radius = r_in + d_center
        val = radius * radius - (abs(x) + d_center) ** 2
        return spring_z + math.sqrt(max(0.0, val))
    elif style == 'SEGMENTAL':
        h_sag = max(0.01, arch_rise)
        r_seg = (r_in ** 2 + h_sag ** 2) / (2.0 * h_sag)
        c_seg_z = spring_z - (r_seg - h_sag)
        val = r_seg * r_seg - x * x
        return c_seg_z + math.sqrt(max(0.0, val))
    else:  # ROMAN_ROUND
        val = r_in * r_in - x * x
        return spring_z + math.sqrt(max(0.0, val))


def add_rivet_stud(bm, center, radius=0.016, mat_idx=1):
    """鋲(リベット)ヘッドを表す小さな六角錐を、扉の正面(-Y方向)に突出させて追加。"""
    cx, cy, cz = center
    res = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=True, segments=6,
        radius1=radius, radius2=radius * 0.2, depth=radius * 1.3,
        matrix=Matrix.Translation((cx, cy, cz)) @ Matrix.Rotation(math.radians(90), 4, 'X')
    )
    for g in res.get('geom', []):
        if isinstance(g, bmesh.types.BMFace):
            g.material_index = mat_idx
            g.smooth = True


def build_arch_cap_bmesh_into(bm, x_min, x_max, base_z, top_z_fn, thickness, mat_idx, arc_segments=24):
    """
    スプリングライン(base_z)から扉上端のアーチ弧までを、1枚の押し出しソリッドとして bm に追加。
    Cubeを何個も並べるのではなく、輪郭(底辺2点＋弧のサンプル点)を1つの面にしてY方向へ押し出す
    （Blenderの「輪郭を作ってEで厚みを出す」操作と同じ考え方）ことで、低ポリのまま滑らかな弧になる。
    底辺と左右の垂直エッジはフラットシェード、弧の部分だけスムーズシェードにして境目をはっきりさせる。
    """
    front_y = -(thickness * 0.5)
    back_y = thickness * 0.5

    top_pts = []
    for i in range(arc_segments + 1):
        t = i / float(arc_segments)
        x = x_min + (x_max - x_min) * t
        z = max(base_z, top_z_fn(x))
        top_pts.append((x, z))

    # 輪郭: 底辺左→底辺右→(弧を自由端側から蝶番側へ辿る)
    outline = [(x_min, base_z), (x_max, base_z)] + list(reversed(top_pts))
    n_pts = len(outline)

    front_verts = [bm.verts.new((x, front_y, z)) for x, z in outline]
    back_verts = [bm.verts.new((x, back_y, z)) for x, z in outline]
    bm.verts.ensure_lookup_table()

    f_front = bm.faces.new(front_verts)
    f_front.material_index = mat_idx
    f_front.smooth = False

    f_back = bm.faces.new(list(reversed(back_verts)))
    f_back.material_index = mat_idx
    f_back.smooth = False

    new_side_faces = []
    for i in range(n_pts):
        j = (i + 1) % n_pts
        f_side = bm.faces.new([front_verts[i], front_verts[j], back_verts[j], back_verts[i]])
        f_side.material_index = mat_idx
        # 0=底辺, 1=自由端側の垂直エッジ, (n_pts-1)=蝶番側の垂直エッジ はフラット。それ以外(弧)はスムーズ。
        f_side.smooth = (2 <= i <= n_pts - 2)
        new_side_faces.append(f_side)

    bmesh.ops.recalc_face_normals(bm, faces=[f_front, f_back] + new_side_faces)


def add_flat_strap(bm, p1, p2, width=0.05, thickness=0.014, mat_idx=1, smooth=False):
    """2点間を結ぶ平帯鉄（ストラップ金具・たすき掛け・蝶番帯）を追加。"""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 0.002:
        return
    cx = (p1[0] + p2[0]) * 0.5
    cy = (p1[1] + p2[1]) * 0.5
    cz = (p1[2] + p2[2]) * 0.5

    v_dir = Vector((dx, dy, dz)).normalized()
    z_axis = Vector((0, 0, 1))
    rot_quat = z_axis.rotation_difference(v_dir)

    res = bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Translation((cx, cy, cz)) @ rot_quat.to_matrix().to_4x4() @ Matrix.Diagonal((width, thickness, length, 1.0))
    )
    v_res = set(res['verts'])
    for f in bm.faces:
        if any(v in v_res for v in f.verts):
            f.material_index = mat_idx
            f.smooth = smooth


def add_edge_trim_bmesh(bm, outline_pts, front_y, trim_width=0.05, trim_depth=0.014, mat_idx=1):
    """
    扉外周(輪郭)を一周するように、内側にオフセットした金属の縁取り帯を追加する。
    木材とは別のマテリアルスロット(iron)を使うため、後から独立してテクスチャを差し替え可能。
    """
    n = len(outline_pts)
    if n < 3:
        return
    xs = [p[0] for p in outline_pts]
    zs = [p[1] for p in outline_pts]
    anchor = ((min(xs) + max(xs)) * 0.5, min(zs) + (max(zs) - min(zs)) * 0.35)

    inset_pts = []
    for (x, z) in outline_pts:
        dx = anchor[0] - x
        dz = anchor[1] - z
        d = math.sqrt(dx * dx + dz * dz)
        if d < 1e-5:
            inset_pts.append((x, z))
        else:
            f = (trim_width * 0.5) / d
            inset_pts.append((x + dx * f, z + dz * f))

    for i in range(n):
        j = (i + 1) % n
        x0, z0 = inset_pts[i]
        x1, z1 = inset_pts[j]
        is_curve_seg = (i >= 2) and (j != 0)  # 底辺(0-1)と左右の垂直エッジはフラット、弧の内部区間だけスムーズ
        add_flat_strap(bm, (x0, front_y, z0), (x1, front_y, z1), width=trim_width, thickness=trim_depth, mat_idx=mat_idx, smooth=is_curve_seg)


def build_door_leaf_bmesh(
    width, top_z_fn, thickness=0.08,
    hinge_side='LEFT',
    strap_style='CROSS_Z',
    stud_pattern='GRID',
    handle_style='RING_PULL',
    is_handle_leaf=True,
    has_hinges=True,
    has_edge_trim=True,
    edge_trim_width=0.05,
    wood_mat_idx=0,
    iron_mat_idx=1,
    seed=0
):
    """
    片開き扉パネル（板張り+鉄帯金具+鋲+取っ手）のBMeshを生成。
    【重要】ローカル原点 (0, 0, 0) を蝶番の回転軸に配置！
    - hinge_side == 'LEFT': メッシュは +X 方向 [0, width] に配置（蝶番は左端=原点）
    - hinge_side == 'RIGHT': メッシュは -X 方向 [-width, 0] に配置（蝶番は右端=原点）
    これにより、ヒンジを中心に自然に開閉・将来のアニメーションに対応可能。
    top_z_fn(local_x) は、そのX位置における扉上端の高さ（floor=0基準の絶対値）を返す関数。
    """
    bm = bmesh.new()

    x_min = 0.0 if hinge_side == 'LEFT' else -width
    x_max = width if hinge_side == 'LEFT' else 0.0
    front_y = -(thickness * 0.5) - 0.006

    # このリーフ内でアーチカーブが最も低くなる基準面（蝶番側のスプリングライン高さ）
    spring_h = max(0.25, top_z_fn(x_min if hinge_side == 'LEFT' else x_max))

    # 1. 矩形パネル（スプリングラインまでの板張り部）：単一ブロックで構成し、板目・継ぎ目はマテリアル側(バンプ)で表現
    add_box_to_bmesh(bm, ((x_min + x_max) * 0.5, 0.0, spring_h * 0.5), (width, thickness, spring_h), mat_idx=wood_mat_idx)

    # 2. アーチカーブ追従キャップ：単一の押し出しソリッド（Cube積みではなく輪郭→押し出し）で滑らかな弧にする
    build_arch_cap_bmesh_into(bm, x_min, x_max, spring_h, top_z_fn, thickness, wood_mat_idx, arc_segments=24)

    # 3. 縁取り金属フレーム：扉外周（底辺＋左右＋アーチ弧）を一周する補強縁。木材とは別のironマテリアルスロットを使用
    if has_edge_trim:
        trim_segments = 24
        trim_top_pts = []
        for i in range(trim_segments + 1):
            t = i / float(trim_segments)
            x = x_min + (x_max - x_min) * t
            z = max(0.02, top_z_fn(x))
            trim_top_pts.append((x, z))
        full_outline = [(x_min, 0.0), (x_max, 0.0)] + list(reversed(trim_top_pts))
        add_edge_trim_bmesh(bm, full_outline, front_y, trim_width=edge_trim_width, trim_depth=0.014, mat_idx=iron_mat_idx)

    # 金具類は矩形部（アーチが始まる手前）に収める
    flat_h = spring_h * 0.94
    top_band_z = flat_h * 0.86
    bot_band_z = flat_h * 0.14
    margin = width * 0.08

    # 4. 帯金具（ストラップ）
    if strap_style != 'NONE' and width > 0.05:
        strap_w = max(0.035, width * 0.10)
        strap_th = 0.014
        lx = x_min + margin
        rx = x_max - margin
        if strap_style == 'HORIZONTAL_BANDS':
            for b in range(3):
                t = b / 2.0
                bz = bot_band_z + (top_band_z - bot_band_z) * t
                add_flat_strap(bm, (lx, front_y, bz), (rx, front_y, bz), width=strap_w, thickness=strap_th, mat_idx=iron_mat_idx)
        elif strap_style == 'DOUBLE_DIAGONAL':
            add_flat_strap(bm, (lx, front_y, bot_band_z), (rx, front_y, top_band_z), width=strap_w, thickness=strap_th, mat_idx=iron_mat_idx)
            add_flat_strap(bm, (lx, front_y, top_band_z), (rx, front_y, bot_band_z), width=strap_w, thickness=strap_th, mat_idx=iron_mat_idx)
            add_flat_strap(bm, (lx, front_y, top_band_z), (rx, front_y, top_band_z), width=strap_w, thickness=strap_th, mat_idx=iron_mat_idx)
            add_flat_strap(bm, (lx, front_y, bot_band_z), (rx, front_y, bot_band_z), width=strap_w, thickness=strap_th, mat_idx=iron_mat_idx)
        else:  # CROSS_Z（Z字たすき掛け）
            add_flat_strap(bm, (lx, front_y, top_band_z), (rx, front_y, top_band_z), width=strap_w, thickness=strap_th, mat_idx=iron_mat_idx)
            add_flat_strap(bm, (lx, front_y, bot_band_z), (rx, front_y, bot_band_z), width=strap_w, thickness=strap_th, mat_idx=iron_mat_idx)
            if hinge_side == 'LEFT':
                add_flat_strap(bm, (lx, front_y, top_band_z), (rx, front_y, bot_band_z), width=strap_w, thickness=strap_th, mat_idx=iron_mat_idx)
            else:
                add_flat_strap(bm, (lx, front_y, bot_band_z), (rx, front_y, top_band_z), width=strap_w, thickness=strap_th, mat_idx=iron_mat_idx)

    # 5. 蝶番帯（ヒンジ側から伸びる装飾補強帯）
    if has_hinges:
        hinge_x0 = x_min if hinge_side == 'LEFT' else x_max
        hinge_reach = width * 0.42
        sign = 1.0 if hinge_side == 'LEFT' else -1.0
        for hz_t in (0.14, 0.50, 0.86):
            hz = flat_h * hz_t
            hx1 = hinge_x0 + hinge_reach * sign
            add_flat_strap(bm, (hinge_x0, front_y, hz), (hx1, front_y, hz), width=0.05, thickness=0.016, mat_idx=iron_mat_idx)
            add_rivet_stud(bm, (hinge_x0 + 0.03 * sign, front_y - 0.012, hz), radius=0.016, mat_idx=iron_mat_idx)

    # 6. 鋲(スタッド)グリッド
    if stud_pattern != 'NONE':
        rows = max(3, int(flat_h / 0.28))
        cols = max(3, int(width / 0.22))
        for r in range(rows):
            row_t = (r + 0.5) / rows
            rz = bot_band_z * 0.4 + (top_band_z * 1.05 - bot_band_z * 0.4) * row_t
            row_offset = (0.5 / cols) * width if (stud_pattern == 'DIAMOND' and r % 2 == 1) else 0.0
            for c in range(cols):
                col_t = (c + 0.5) / cols
                cx = x_min + width * col_t + row_offset
                if cx <= x_min + margin * 0.3 or cx >= x_max - margin * 0.3:
                    continue
                add_rivet_stud(bm, (cx, front_y - 0.010, rz), radius=0.014, mat_idx=iron_mat_idx)

    # 7. 取っ手（リングプル／ドロップノッカー）— ヒンジと反対側の自由端に配置
    if handle_style != 'NONE' and is_handle_leaf:
        free_x = x_max if hinge_side == 'LEFT' else x_min
        handle_x = free_x - (0.14 if hinge_side == 'LEFT' else -0.14)
        handle_z = flat_h * 0.50
        add_box_to_bmesh(bm, (handle_x, front_y - 0.006, handle_z), (0.09, 0.02, 0.09), mat_idx=iron_mat_idx)

        ring_r = 0.075 if handle_style == 'DROP_KNOCKER' else 0.06
        ring_cz = handle_z - ring_r * 0.9 if handle_style == 'DROP_KNOCKER' else handle_z
        seg = 12
        pts = []
        for i in range(seg):
            a = (i / float(seg)) * math.pi * 2.0
            pts.append((handle_x + math.sin(a) * ring_r, front_y - 0.018, ring_cz + math.cos(a) * ring_r))
        for i in range(seg):
            add_cylinder_bar(bm, pts[i], pts[(i + 1) % seg], 0.011, segments=6, mat_idx=iron_mat_idx)

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bm.normal_update()
    return bm


def generate_western_door(
    context,
    size_x=2.2,
    size_y=0.5,
    size_z=2.6,
    door_arch_style='ROMAN_ROUND',
    pillar_shape='SQUARE_PIER',
    pillar_width=0.42,
    column_height=1.7,
    has_keystone=True,
    strap_style='CROSS_Z',
    stud_pattern='GRID',
    handle_style='RING_PULL',
    has_hinges=True,
    has_edge_trim=True,
    edge_trim_width=0.05,
    wood_material='WEATHERED_OAK',
    iron_style='BLACK_FORGED',
    damage=0.35,
    weathering=0.55,
    moss_amount=0.20,
    open_angle=0.0,
    open_direction='OUTWARD',
    combine_mesh=False,
    location=(0, 0, 0),
    rotation=(0, 0, 0),
    seed=0,
    name="Western_Door",
    **kwargs
):
    """
    ダンジョン向け・西洋風アーチ両開き扉の完全生成システム。
    - Door_Frame（親オブジェクト）: build_procedural_stone_arch_bmesh を再利用した石造アーチ開口枠（経年欠け対応）
    - Door_Leaf_L / Door_Leaf_R（子オブジェクト）: ヒンジ位置に原点(Pivot)を持つ、板張り+鉄帯金具+鋲+取っ手の重厚な扉パネル
    - combine_mesh == True の場合は、全オブジェクトを単一メッシュに結合して出力。
    """
    span_w = max(1.2, float(size_x))
    depth = max(0.22, float(size_y))

    style = door_arch_style if door_arch_style in ('ROMAN_ROUND', 'GOTHIC_POINTED', 'SEGMENTAL') else 'ROMAN_ROUND'

    pillar_w = max(0.15, min(pillar_width, span_w * 0.45))
    col_h = max(0.6, column_height)
    plinth_h = min(0.35, col_h * 0.12)
    capital_h = min(0.35, col_h * 0.13)
    spring_z = plinth_h + col_h + capital_h
    opening_w = max(0.6, span_w - pillar_w)
    r_in = opening_w * 0.5

    if style == 'GOTHIC_POINTED':
        arch_rise = r_in * 1.30
    elif style == 'SEGMENTAL':
        arch_rise = r_in * 0.55
    else:  # ROMAN_ROUND
        arch_rise = r_in

    # ── マテリアル準備 ──
    stone_type = "MOSSY_RUINS" if moss_amount >= 0.35 else "ANCIENT_STONE"
    mat_stone = create_procedural_pillar_shader(f"{name}_Stone_Mat", mat_type=stone_type, seed=seed)
    mat_wood = create_door_wood_material(f"{name}_Wood_Mat", wood_type=wood_material, weathering=weathering, moss_amount=moss_amount, seed=seed)
    mat_iron = create_door_iron_material(f"{name}_Iron_Mat", iron_style=iron_style, weathering=weathering, seed=seed)

    # ==============================================================================
    # ── A. 石造アーチ開口枠（Door_Frame）── build_procedural_stone_arch_bmesh を再利用
    # ==============================================================================
    bm_frame = bmesh.new()
    build_procedural_stone_arch_bmesh(
        bm_frame,
        size_x=span_w, size_y=depth,
        style=style, structure_type='SINGLE',
        pillar_shape=pillar_shape, pillar_width=pillar_w, column_height=col_h,
        damage=damage, has_keystone=has_keystone, keystone_scale=1.2,
        has_spandrel=True, has_pedestal=True, seed=seed
    )
    # 左右の柱に付柱（Engaged Fluted Column）を前面に融合し、四角柱だけの安っぽい見た目を回避
    # （柱プリセット(pillar_gen.py)の溝彫り円柱ビルダーを再利用。柱本体は別メッシュを繋がずbm_frameに直接追加）
    col_radius = pillar_w * 0.5 * 0.92
    col_front_y = -depth * 0.5
    for pier_x in (-span_w * 0.5, span_w * 0.5):
        verts_before = set(bm_frame.verts[:])
        build_roman_fluted_pillar(bm_frame, height=col_h, radius=col_radius, flute_count=14, seed=seed)
        bm_frame.verts.ensure_lookup_table()
        new_verts = [v for v in bm_frame.verts if v not in verts_before]
        bmesh.ops.translate(bm_frame, verts=new_verts, vec=(pier_x, col_front_y, plinth_h))
        new_vert_set = set(new_verts)
        for f in bm_frame.faces:
            if all(v in new_vert_set for v in f.verts):
                f.smooth = True

    bm_frame.verts.ensure_lookup_table()
    bm_frame.faces.ensure_lookup_table()

    mesh_frame = bpy.data.meshes.new(f"{name}_Frame_Mesh")
    bm_frame.to_mesh(mesh_frame)
    bm_frame.free()

    obj_frame = bpy.data.objects.new(f"{name}_Frame", mesh_frame)
    context.collection.objects.link(obj_frame)
    obj_frame.data.materials.append(mat_stone)  # 0: Stone

    obj_frame.location = location
    obj_frame.rotation_euler = rotation

    created_objects = [obj_frame]

    # ==============================================================================
    # ── B. 両開き扉パネル（Door_Leaf_L / Door_Leaf_R）──
    # ==============================================================================
    gap = 0.012
    leaf_w = max(0.4, r_in - gap)
    leaf_thickness = min(0.09, depth * 0.35)

    ang_rad = math.radians(open_angle)
    rot_mult = 1.0 if open_direction == 'OUTWARD' else -1.0

    def top_z_fn_left(local_x):
        world_x = -r_in + local_x
        return _door_arch_inner_z(world_x, style, r_in, spring_z, arch_rise) - 0.012

    def top_z_fn_right(local_x):
        world_x = r_in + local_x
        return _door_arch_inner_z(world_x, style, r_in, spring_z, arch_rise) - 0.012

    bm_l = build_door_leaf_bmesh(
        width=leaf_w, top_z_fn=top_z_fn_left, thickness=leaf_thickness,
        hinge_side='LEFT',
        strap_style=strap_style, stud_pattern=stud_pattern,
        handle_style=handle_style, is_handle_leaf=True, has_hinges=has_hinges,
        has_edge_trim=has_edge_trim, edge_trim_width=edge_trim_width,
        wood_mat_idx=0, iron_mat_idx=1, seed=seed
    )
    mesh_l = bpy.data.meshes.new(f"{name}_Leaf_L_Mesh")
    bm_l.to_mesh(mesh_l)
    bm_l.free()

    obj_l = bpy.data.objects.new(f"{name}_Leaf_L", mesh_l)
    context.collection.objects.link(obj_l)
    obj_l.data.materials.append(mat_wood)  # 0: Wood
    obj_l.data.materials.append(mat_iron)  # 1: Iron

    obj_l.location = Vector((-r_in, 0.0, 0.0))
    obj_l.rotation_euler = Vector((0.0, 0.0, -ang_rad * rot_mult))
    obj_l.parent = obj_frame
    created_objects.append(obj_l)

    bm_r = build_door_leaf_bmesh(
        width=leaf_w, top_z_fn=top_z_fn_right, thickness=leaf_thickness,
        hinge_side='RIGHT',
        strap_style=strap_style, stud_pattern=stud_pattern,
        handle_style=handle_style, is_handle_leaf=False, has_hinges=has_hinges,
        has_edge_trim=has_edge_trim, edge_trim_width=edge_trim_width,
        wood_mat_idx=0, iron_mat_idx=1, seed=seed + 1
    )
    mesh_r = bpy.data.meshes.new(f"{name}_Leaf_R_Mesh")
    bm_r.to_mesh(mesh_r)
    bm_r.free()

    obj_r = bpy.data.objects.new(f"{name}_Leaf_R", mesh_r)
    context.collection.objects.link(obj_r)
    obj_r.data.materials.append(mat_wood)  # 0: Wood
    obj_r.data.materials.append(mat_iron)  # 1: Iron

    obj_r.location = Vector((r_in, 0.0, 0.0))
    obj_r.rotation_euler = Vector((0.0, 0.0, ang_rad * rot_mult))
    obj_r.parent = obj_frame
    created_objects.append(obj_r)

    # 結合モード
    if combine_mesh:
        for o in created_objects:
            o.select_set(True)
        context.view_layer.objects.active = obj_frame
        bpy.ops.object.join()
        return [obj_frame]

    context.view_layer.objects.active = obj_frame
    obj_frame.select_set(True)
    return created_objects
