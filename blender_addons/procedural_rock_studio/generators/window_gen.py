import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

from ..materials.image_shaders import (
    create_window_glass_material,
    create_window_iron_material,
    create_window_sash_material,
    create_window_brass_material
)
from ..materials.nature_shaders import create_procedural_pillar_shader


def add_box_to_bmesh(bm, center, size, mat_idx=0, subdiv=0):
    """BMeshに直方体ブロックを追加し、マテリアルスロットを設定"""
    cx, cy, cz = center
    sx, sy, sz = size
    res = bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Translation((cx, cy, cz)) @ Matrix.Diagonal((sx, sy, sz, 1.0))
    )
    v_res = res['verts']
    if subdiv > 0:
        edges_to_sub = [e for e in bm.edges if all(v in v_res for v in e.verts)]
        if edges_to_sub:
            sub_res = bmesh.ops.subdivide_edges(bm, edges=edges_to_sub, cuts=subdiv, use_grid_fill=True)
            new_verts = [g for g in sub_res.get('geom_inner', []) if isinstance(g, bmesh.types.BMVert)]
            v_res = list(set(v_res + new_verts))

    for f in bm.faces:
        if any(v in v_res for v in f.verts):
            f.material_index = mat_idx
            f.smooth = False
    return v_res


def add_cylinder_bar(bm, p1, p2, radius, segments=12, mat_idx=2):
    """2点間を結ぶ円柱バーを生成（格子・ハンドルロッド用）"""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    if length < 0.002:
        return
    cx = (p1[0] + p2[0]) * 0.5
    cy = (p1[1] + p2[1]) * 0.5
    cz = (p1[2] + p2[2]) * 0.5

    v_dir = Vector((dx, dy, dz)).normalized()
    z_axis = Vector((0, 0, 1))
    rot_quat = z_axis.rotation_difference(v_dir)

    res = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=radius, radius2=radius, depth=length,
        matrix=Matrix.Translation((cx, cy, cz)) @ rot_quat.to_matrix().to_4x4()
    )
    for g in res.get('geom', []):
        if isinstance(g, bmesh.types.BMFace):
            g.material_index = mat_idx
            g.smooth = True


def build_casement_sash_bmesh(
    width, height, thickness=0.038,
    hinge_side='LEFT',
    grille_style='SUNBURST',
    wire_density=6,
    wire_thickness=0.012,
    has_handle=True,
    has_hinges=True,
    sash_mat_idx=3,
    glass_mat_idx=1,
    metal_mat_idx=2,
    brass_mat_idx=4
):
    """
    可動サッシュ（窓障子）のBMeshを生成。
    【重要】ローカル原点 (0, 0, 0) をヒンジの回転軸に配置！
    - hinge_side == 'LEFT': メッシュは +X 方向 [0, width] に配置
    - hinge_side == 'RIGHT': メッシュは -X 方向 [-width, 0] に配置
    これにより、UE側で Yaw を回転させるだけでヒンジを中心に自然に開閉可能！
    """
    bm = bmesh.new()

    frame_w = min(0.065, width * 0.22) # サッシュの木枠幅（約5〜6cm）
    half_th = thickness * 0.5

    x_min = 0.0 if hinge_side == 'LEFT' else -width
    x_max = width if hinge_side == 'LEFT' else 0.0
    sash_cx = (x_min + x_max) * 0.5

    # 1. サッシュ外枠（四角枠：左右縦框、上下横桟）
    # 左右の縦框 (Stiles)
    left_cx = x_min + frame_w * 0.5
    right_cx = x_max - frame_w * 0.5
    add_box_to_bmesh(bm, (left_cx, 0.0, height * 0.5), (frame_w, thickness, height), mat_idx=sash_mat_idx)
    add_box_to_bmesh(bm, (right_cx, 0.0, height * 0.5), (frame_w, thickness, height), mat_idx=sash_mat_idx)

    # 上下の横桟 (Rails)
    inner_span_w = width - frame_w * 2.0
    bot_cz = frame_w * 0.5
    top_cz = height - frame_w * 0.5
    if inner_span_w > 0.01:
        add_box_to_bmesh(bm, (sash_cx, 0.0, bot_cz), (inner_span_w, thickness, frame_w), mat_idx=sash_mat_idx)
        add_box_to_bmesh(bm, (sash_cx, 0.0, top_cz), (inner_span_w, thickness, frame_w), mat_idx=sash_mat_idx)

    # 2. ガラス板 (Glass Pane)
    glass_th = 0.006
    g_w = inner_span_w + 0.008 # 枠の溝に少し食い込ませる
    g_h = height - frame_w * 2.0 + 0.008
    g_cz = height * 0.5
    add_box_to_bmesh(bm, (sash_cx, 0.0, g_cz), (g_w, glass_th, g_h), mat_idx=glass_mat_idx)

    # 3. 格子・小桟 (Muntins / Grille)
    w_th = max(0.006, wire_thickness)
    w_dp = thickness * 0.8
    y_front = thickness * 0.15

    inner_x0 = x_min + frame_w
    inner_x1 = x_max - frame_w
    inner_z0 = frame_w
    inner_z1 = height - frame_w

    if grille_style in ('SUNBURST', 'CROSS'):
        # 端正なクラシック格子（洋館両開き窓の標準スタイル：縦1〜2本、横2〜3段）
        cols = 2 if width > 0.35 else 1
        rows = 3 if height > 0.8 else 2

        # 縦小桟
        for c in range(1, cols):
            gx = inner_x0 + (inner_x1 - inner_x0) * (c / float(cols))
            add_box_to_bmesh(bm, (gx, y_front, g_cz), (w_th, w_dp, g_h), mat_idx=sash_mat_idx)
        # 横小桟
        for r in range(1, rows):
            gz = inner_z0 + (inner_z1 - inner_z0) * (r / float(rows))
            add_box_to_bmesh(bm, (sash_cx, y_front, gz), (inner_span_w, w_dp, w_th), mat_idx=sash_mat_idx)

    elif grille_style == 'DIAMOND_WIRE':
        # 菱形鉛線・X字針金
        n_diag = max(2, int(wire_density * 0.5))
        d_step = inner_span_w / float(n_diag)
        for i in range(-n_diag, n_diag * 2):
            add_cylinder_bar(bm, (sash_cx, y_front, inner_z0 + 0.1), (sash_cx, y_front, inner_z1 - 0.1), w_th * 0.5, mat_idx=metal_mat_idx)

    elif grille_style == 'IRON_BARS':
        # 縦鉄格子
        n_bars = max(2, int(width / 0.12))
        for b in range(1, n_bars):
            bx = inner_x0 + (inner_x1 - inner_x0) * (b / float(n_bars))
            add_cylinder_bar(bm, (bx, y_front, inner_z0), (bx, y_front, inner_z1), w_th * 1.2, mat_idx=metal_mat_idx)

    # 4. 蝶番金具 (Hinges on sash side)
    if has_hinges:
        hinge_x = 0.0 # ローカル原点 X=0 がヒンジ軸！
        hinge_r = 0.012
        h_len = 0.06
        for z_frac in (0.18, 0.82):
            hz = height * z_frac
            # ヒンジのナックル円筒（回転ピン）
            add_cylinder_bar(bm, (hinge_x, 0.0, hz - h_len * 0.5), (hinge_x, 0.0, hz + h_len * 0.5), hinge_r, mat_idx=metal_mat_idx)
            # サッシュ側への取り付けプレート
            plate_w = frame_w * 0.55
            plate_cx = hinge_x + (plate_w * 0.5 if hinge_side == 'LEFT' else -plate_w * 0.5)
            add_box_to_bmesh(bm, (plate_cx, half_th + 0.003, hz), (plate_w, 0.005, h_len * 0.6), mat_idx=metal_mat_idx)

    # 5. クレモン錠・開閉レバーハンドル (Espagnolette Bolt & Handle)
    if has_handle:
        # 召し合わせ側（ヒンジの反対側）
        meet_x = x_max if hinge_side == 'LEFT' else x_min
        handle_x = meet_x - (frame_w * 0.45 if hinge_side == 'LEFT' else -frame_w * 0.45)
        rod_y = half_th + 0.014
        handle_z = height * 0.45

        # 垂直ロッド（上下に走る真鍮製/鍛鉄製ボルト）
        rod_r = 0.0055
        add_cylinder_bar(bm, (handle_x, rod_y, frame_w * 0.6), (handle_x, rod_y, height - frame_w * 0.6), rod_r, mat_idx=brass_mat_idx)

        # 中央のギアボックス台座
        add_box_to_bmesh(bm, (handle_x, rod_y, handle_z), (0.024, 0.018, 0.065), mat_idx=brass_mat_idx)

        # 水平レバーハンドル（手前に突出し、下または横にカーブ）
        stem_p1 = (handle_x, rod_y, handle_z)
        stem_p2 = (handle_x, rod_y + 0.045, handle_z)
        add_cylinder_bar(bm, stem_p1, stem_p2, 0.006, mat_idx=brass_mat_idx)

        # ハンドルバー（握り玉）
        lever_dir = 1.0 if hinge_side == 'LEFT' else -1.0
        bar_p1 = (handle_x, rod_y + 0.045, handle_z)
        bar_p2 = (handle_x + 0.07 * lever_dir, rod_y + 0.045, handle_z - 0.035)
        add_cylinder_bar(bm, bar_p1, bar_p2, 0.007, mat_idx=brass_mat_idx)

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm


def generate_western_window(
    context,
    size_x=1.6,
    size_y=0.35,
    size_z=2.5,
    frame_style='ROMAN_ROUND',
    grille_style='SUNBURST',
    arch_style='MOLDED_FRENCH',
    jamb_style='ENGAGED_FLUTED',
    column_flutes=8,
    column_pedestal=True,
    has_keystone=True,
    wire_density=6,
    wire_thickness=0.012,
    frame_width=0.18,
    has_sill=True,
    has_hood=True,
    damage=0.30,
    weathering=0.50,
    moss_amount=0.25,
    sash_mode='DOUBLE_CASEMENT',
    open_angle=0.0,
    open_direction='OUTWARD',
    has_handle=True,
    has_hinges=True,
    sash_material='DARK_WOOD',
    combine_mesh=False,
    location=(0, 0, 0),
    rotation=(0, 0, 0),
    seed=0,
    name="Western_Window",
    **kwargs
):
    """
    UE開閉対応リアル西洋窓の完全生成システム。
    - Window_Frame（親オブジェクト）: 外枠、窓台、コーニス、固定上部ファンライト
    - Window_Sash_L / Window_Sash_R（子オブジェクト）: ヒンジ位置に原点(Pivot)を持つ可動サッシュ
    - combine_mesh == True の場合は、全オブジェクトを単一メッシュに結合して出力。
    """
    rng = random.Random(seed)

    total_w = max(0.8, float(size_x))
    depth = max(0.18, float(size_y))
    total_h = max(1.2, float(size_z))
    f_w = max(0.08, min(frame_width, total_w * 0.28))
    half_w = total_w * 0.5
    half_d = depth * 0.5
    inner_w = total_w - f_w * 2.0
    r_in = inner_w * 0.5

    sill_h = total_h * 0.08 if has_sill else 0.0
    sill_proj = depth * 0.35

    # 1. 幾何学パラメータ計算
    if frame_style == 'RECTANGLE':
        spring_z = total_h - f_w
        arch_rise = 0.0
    elif frame_style == 'ROMAN_ROUND':
        arch_rise = r_in
        spring_z = max(sill_h + 0.5, total_h - f_w - arch_rise)
    elif frame_style == 'TUDOR':
        arch_rise = r_in * 0.55
        spring_z = max(sill_h + 0.5, total_h - f_w - arch_rise)
    else: # GOTHIC_POINTED
        arch_rise = r_in * 1.35
        spring_z = max(sill_h + 0.5, total_h - f_w - arch_rise)

    def get_arch_z(x):
        x_c = max(-r_in, min(r_in, x))
        if frame_style == 'RECTANGLE':
            return spring_z
        elif frame_style == 'GOTHIC_POINTED':
            d_c = r_in * 0.42
            R = r_in + d_c
            rad_sq = max(0.0, R**2 - (x_c - d_c if x_c <= 0 else x_c + d_c)**2)
            return spring_z + math.sqrt(rad_sq)
        elif frame_style == 'TUDOR':
            t = math.sqrt(max(0.0, 1.0 - (x_c / r_in)**2))
            return spring_z + arch_rise * t
        else: # ROMAN_ROUND
            rad_sq = max(0.0, r_in**2 - x_c**2)
            return spring_z + math.sqrt(rad_sq)

    # ── マテリアル準備 ──
    mat_stone = create_procedural_pillar_shader(f"{name}_Stone_Mat", mat_type="SANDSTONE", seed=seed)
    mat_glass = create_window_glass_material(f"{name}_Glass_Mat")
    mat_iron = create_window_iron_material(f"{name}_Iron_Mat")
    mat_sash = create_window_sash_material(f"{name}_Sash_Mat", mat_type=sash_material)
    mat_brass = create_window_brass_material(f"{name}_Brass_Mat")

    # ==============================================================================
    # ── A. 窓枠オブジェクト（Window_Frame）のメッシュ生成 ──
    # ==============================================================================
    bm_frame = bmesh.new()

    # 1. 窓台 (Window Sill)
    if has_sill:
        add_box_to_bmesh(bm_frame, (0.0, sill_proj * 0.35, sill_h * 0.35), (total_w + 0.14, depth + sill_proj * 0.7, sill_h * 0.7), mat_idx=0, subdiv=1)
        add_box_to_bmesh(bm_frame, (0.0, sill_proj * 0.45, sill_h * 0.85), (total_w + 0.10, depth + sill_proj, sill_h * 0.3), mat_idx=0, subdiv=1)

    # 2. 左右側枠（Jambs / Columns）
    jamb_h = spring_z - sill_h
    lx_c = -half_w + f_w * 0.5
    rx_c = half_w - f_w * 0.5

    col_cy = half_d * 0.85
    col_r = f_w * 0.52
    if jamb_style == 'ENGAGED_FLUTED':
        for cx in (lx_c, rx_c):
            ped_h = min(0.32, jamb_h * 0.16)
            add_box_to_bmesh(bm_frame, (cx, col_cy - depth * 0.3, sill_h + ped_h * 0.5), (f_w * 1.15, depth * 0.8, ped_h), mat_idx=0, subdiv=1)
            shaft_h = jamb_h - ped_h - 0.12
            shaft_cz = sill_h + ped_h + shaft_h * 0.5
            res_col = bmesh.ops.create_cone(
                bm_frame, cap_ends=True, cap_tris=False, segments=16,
                radius1=col_r, radius2=col_r * 0.95, depth=shaft_h,
                matrix=Matrix.Translation((cx, col_cy, shaft_cz))
            )
            for g in res_col.get('geom', []):
                if isinstance(g, bmesh.types.BMFace):
                    g.material_index = 0
                    g.smooth = True
            add_box_to_bmesh(bm_frame, (cx, 0.0, sill_h + jamb_h * 0.5), (f_w, depth * 0.6, jamb_h), mat_idx=0, subdiv=1)
            add_box_to_bmesh(bm_frame, (cx, col_cy - 0.02, spring_z - 0.05), (f_w * 1.25, f_w * 1.25, 0.10), mat_idx=0, subdiv=1)
    else:
        for cx in (lx_c, rx_c):
            add_box_to_bmesh(bm_frame, (cx, 0.0, sill_h + jamb_h * 0.5), (f_w, depth, jamb_h), mat_idx=0, subdiv=1)
            add_box_to_bmesh(bm_frame, (cx, half_d + 0.015, sill_h + jamb_h * 0.5), (f_w * 0.7, 0.03, jamb_h), mat_idx=0, subdiv=1)

    # 3. 上部コーニス天板 (Top Cornice)
    top_beam_h = max(0.12, f_w)
    add_box_to_bmesh(bm_frame, (0.0, 0.0, total_h - top_beam_h * 0.5), (total_w, depth, top_beam_h), mat_idx=0, subdiv=1)
    if has_hood:
        add_box_to_bmesh(bm_frame, (0.0, half_d + 0.025, total_h - top_beam_h * 0.5), (total_w + 0.14, 0.06, top_beam_h * 1.12), mat_idx=0, subdiv=1)

    # 4. 水平トランサムバー (Transom Bar) - スプリングラインの区切り
    transom_h = min(0.08, f_w * 0.45)
    transom_d = depth * 0.75
    add_box_to_bmesh(bm_frame, (0.0, 0.0, spring_z + transom_h * 0.5), (inner_w + 0.04, transom_d, transom_h), mat_idx=0, subdiv=1)

    # 5. 上枠・アーチ・スパンドレル壁
    top_limit = total_h - top_beam_h
    if frame_style != 'RECTANGLE':
        side_wall_h = top_limit - spring_z
        add_box_to_bmesh(bm_frame, (lx_c, 0.0, spring_z + side_wall_h * 0.5), (f_w, depth, side_wall_h), mat_idx=0, subdiv=1)
        add_box_to_bmesh(bm_frame, (rx_c, 0.0, spring_z + side_wall_h * 0.5), (f_w, depth, side_wall_h), mat_idx=0, subdiv=1)

        apex_z = get_arch_z(0.0)
        apex_gap = top_limit - apex_z
        if apex_gap > 0.005:
            add_box_to_bmesh(bm_frame, (0.0, 0.0, apex_z + apex_gap * 0.5), (2.0 * r_in, depth, apex_gap), mat_idx=0, subdiv=1)

        # アーチモールディング
        n_seg = 24
        for i in range(n_seg):
            t0 = i / float(n_seg)
            t1 = (i + 1) / float(n_seg)
            x0 = -r_in + 2.0 * r_in * t0
            x1 = -r_in + 2.0 * r_in * t1
            z0 = get_arch_z(x0)
            z1 = get_arch_z(x1)
            add_box_to_bmesh(bm_frame, ((x0+x1)*0.5, half_d - 0.02, (z0+z1)*0.5 + 0.05), (abs(x1-x0)+0.01, 0.04, top_limit - (z0+z1)*0.5), mat_idx=0)

        # 6. 上部固定ファンライト
        fan_pts_f = [bm_frame.verts.new((x, 0.003, get_arch_z(x) - 0.01)) for x in [-r_in + 2.0*r_in*(i/16.0) for i in range(17)]]
        fan_pts_b = [bm_frame.verts.new((x, -0.003, get_arch_z(x) - 0.01)) for x in [-r_in + 2.0*r_in*(i/16.0) for i in range(17)]]
        v_bot_f1 = bm_frame.verts.new((-r_in, 0.003, spring_z + transom_h))
        v_bot_f2 = bm_frame.verts.new(( r_in, 0.003, spring_z + transom_h))
        v_bot_b1 = bm_frame.verts.new((-r_in, -0.003, spring_z + transom_h))
        v_bot_b2 = bm_frame.verts.new(( r_in, -0.003, spring_z + transom_h))

        f_fan = bm_frame.faces.new([v_bot_f1, v_bot_f2] + list(reversed(fan_pts_f)))
        f_fan.material_index = 1
        b_fan = bm_frame.faces.new([v_bot_b2, v_bot_b1] + fan_pts_b)
        b_fan.material_index = 1

        # 放射サンバースト
        for sp in range(5):
            ang = math.pi * (sp + 1) / 6.0
            p_start = (0.0, 0.012, spring_z + transom_h)
            p_end = (r_in * 0.95 * math.cos(ang), 0.012, spring_z + transom_h + r_in * 0.95 * math.sin(ang))
            add_cylinder_bar(bm_frame, p_start, p_end, 0.008, mat_idx=2)
    else:
        mid_h = top_limit - spring_z
        if mid_h > 0.01:
            add_box_to_bmesh(bm_frame, (0.0, 0.0, spring_z + mid_h * 0.5), (total_w, depth, mid_h), mat_idx=0, subdiv=1)

    # 7. 枠側の固定ヒンジ受け座金（左右枠の内側に上下2箇所）
    h_z_bot = sill_h + (spring_z - sill_h) * 0.18
    h_z_top = sill_h + (spring_z - sill_h) * 0.82
    for hx in (-r_in, r_in):
        for hz in (h_z_bot, h_z_top):
            bracket_w = 0.02
            add_box_to_bmesh(bm_frame, (hx - bracket_w * 0.5 if hx > 0 else hx + bracket_w * 0.5, 0.0, hz), (bracket_w, 0.035, 0.05), mat_idx=2)

    bm_frame.verts.ensure_lookup_table()
    bm_frame.faces.ensure_lookup_table()

    # 窓枠メッシュオブジェクト作成
    mesh_frame = bpy.data.meshes.new(f"{name}_Frame_Mesh")
    bm_frame.to_mesh(mesh_frame)
    bm_frame.free()

    obj_frame = bpy.data.objects.new(f"{name}_Frame", mesh_frame)
    context.collection.objects.link(obj_frame)
    obj_frame.data.materials.append(mat_stone)  # 0: Stone
    obj_frame.data.materials.append(mat_glass)  # 1: Glass
    obj_frame.data.materials.append(mat_iron)   # 2: Iron
    obj_frame.data.materials.append(mat_sash)   # 3: Sash Wood
    obj_frame.data.materials.append(mat_brass)  # 4: Brass

    obj_frame.location = location
    obj_frame.rotation_euler = rotation

    created_objects = [obj_frame]

    # ==============================================================================
    # ── B. 開閉サッシュ（Window_Sash_L / Window_Sash_R）の生成 ──
    # ==============================================================================
    gap = 0.006
    sash_h = (spring_z - sill_h) - gap * 2.0
    sash_th = 0.038

    ang_rad = math.radians(open_angle)
    rot_mult = 1.0 if open_direction == 'OUTWARD' else -1.0

    if sash_mode == 'DOUBLE_CASEMENT':
        sash_w = (inner_w - gap * 3.0) * 0.5

        # 左サッシュ (Window_Sash_L)
        bm_sash_l = build_casement_sash_bmesh(
            width=sash_w, height=sash_h, thickness=sash_th,
            hinge_side='LEFT', grille_style=grille_style,
            wire_density=wire_density, wire_thickness=wire_thickness,
            has_handle=has_handle, has_hinges=has_hinges,
            sash_mat_idx=3, glass_mat_idx=1, metal_mat_idx=2, brass_mat_idx=4
        )
        mesh_l = bpy.data.meshes.new(f"{name}_Sash_L_Mesh")
        bm_sash_l.to_mesh(mesh_l)
        bm_sash_l.free()

        obj_sash_l = bpy.data.objects.new(f"{name}_Sash_L", mesh_l)
        context.collection.objects.link(obj_sash_l)
        for m in (mat_stone, mat_glass, mat_iron, mat_sash, mat_brass):
            obj_sash_l.data.materials.append(m)

        hinge_pos_l = Vector((-r_in + gap, 0.0, sill_h + gap))
        obj_sash_l.location = hinge_pos_l
        obj_sash_l.rotation_euler = Vector((0.0, 0.0, -ang_rad * rot_mult))
        obj_sash_l.parent = obj_frame
        created_objects.append(obj_sash_l)

        # 右サッシュ (Window_Sash_R)
        bm_sash_r = build_casement_sash_bmesh(
            width=sash_w, height=sash_h, thickness=sash_th,
            hinge_side='RIGHT', grille_style=grille_style,
            wire_density=wire_density, wire_thickness=wire_thickness,
            has_handle=False, has_hinges=has_hinges,
            sash_mat_idx=3, glass_mat_idx=1, metal_mat_idx=2, brass_mat_idx=4
        )
        mesh_r = bpy.data.meshes.new(f"{name}_Sash_R_Mesh")
        bm_sash_r.to_mesh(mesh_r)
        bm_sash_r.free()

        obj_sash_r = bpy.data.objects.new(f"{name}_Sash_R", mesh_r)
        context.collection.objects.link(obj_sash_r)
        for m in (mat_stone, mat_glass, mat_iron, mat_sash, mat_brass):
            obj_sash_r.data.materials.append(m)

        hinge_pos_r = Vector((r_in - gap, 0.0, sill_h + gap))
        obj_sash_r.location = hinge_pos_r
        obj_sash_r.rotation_euler = Vector((0.0, 0.0, ang_rad * rot_mult))
        obj_sash_r.parent = obj_frame
        created_objects.append(obj_sash_r)

    elif sash_mode in ('SINGLE_LEFT', 'SINGLE_RIGHT'):
        sash_w = inner_w - gap * 2.0
        h_side = 'LEFT' if sash_mode == 'SINGLE_LEFT' else 'RIGHT'
        bm_sash = build_casement_sash_bmesh(
            width=sash_w, height=sash_h, thickness=sash_th,
            hinge_side=h_side, grille_style=grille_style,
            wire_density=wire_density, wire_thickness=wire_thickness,
            has_handle=has_handle, has_hinges=has_hinges,
            sash_mat_idx=3, glass_mat_idx=1, metal_mat_idx=2, brass_mat_idx=4
        )
        mesh_s = bpy.data.meshes.new(f"{name}_Sash_Mesh")
        bm_sash.to_mesh(mesh_s)
        bm_sash.free()

        obj_sash = bpy.data.objects.new(f"{name}_Sash", mesh_s)
        context.collection.objects.link(obj_sash)
        for m in (mat_stone, mat_glass, mat_iron, mat_sash, mat_brass):
            obj_sash.data.materials.append(m)

        hinge_x = (-r_in + gap) if h_side == 'LEFT' else (r_in - gap)
        obj_sash.location = Vector((hinge_x, 0.0, sill_h + gap))
        rot_yaw = (-ang_rad * rot_mult) if h_side == 'LEFT' else (ang_rad * rot_mult)
        obj_sash.rotation_euler = Vector((0.0, 0.0, rot_yaw))
        obj_sash.parent = obj_frame
        created_objects.append(obj_sash)

    else: # FIXED
        sash_w = inner_w - gap * 2.0
        bm_sash = build_casement_sash_bmesh(
            width=sash_w, height=sash_h, thickness=sash_th,
            hinge_side='LEFT', grille_style=grille_style,
            wire_density=wire_density, wire_thickness=wire_thickness,
            has_handle=False, has_hinges=False,
            sash_mat_idx=3, glass_mat_idx=1, metal_mat_idx=2, brass_mat_idx=4
        )
        mesh_s = bpy.data.meshes.new(f"{name}_Sash_Fixed_Mesh")
        bm_sash.to_mesh(mesh_s)
        bm_sash.free()

        obj_sash = bpy.data.objects.new(f"{name}_Sash_Fixed", mesh_s)
        context.collection.objects.link(obj_sash)
        for m in (mat_stone, mat_glass, mat_iron, mat_sash, mat_brass):
            obj_sash.data.materials.append(m)
        obj_sash.location = Vector((-r_in + gap, 0.0, sill_h + gap))
        obj_sash.parent = obj_frame
        created_objects.append(obj_sash)

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
