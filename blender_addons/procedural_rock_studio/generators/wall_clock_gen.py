import bpy
import bmesh
import math
from mathutils import Vector, Matrix

ROMAN_NUMS = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]

def create_circle_profile_lathe(bm, profile_points, segments=48):
    """(radius, y) のプロファイルからY軸周りの回転体フレームを生成 (部屋向き: 前面=-Y)"""
    rings = []
    for r, y in profile_points:
        ring = []
        for s in range(segments):
            angle = (s / segments) * 2.0 * math.pi
            x = r * math.cos(angle)
            z = r * math.sin(angle)
            v = bm.verts.new((x, y, z))
            ring.append(v)
        rings.append(ring)

    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i + 1]
        for s in range(segments):
            next_s = (s + 1) % segments
            bm.faces.new((r1[s], r1[next_s], r2[next_s], r2[s]))

    # 背面 (壁面 y=0)
    c_back = bm.verts.new((0.0, profile_points[0][1], 0.0))
    for s in range(segments):
        next_s = (s + 1) % segments
        bm.faces.new((c_back, rings[0][s], rings[0][next_s]))

    # 内枠 (文字盤の受け面)
    if profile_points[-1][0] > 0.001:
        c_front = bm.verts.new((0.0, profile_points[-1][1], 0.0))
        for s in range(segments):
            next_s = (s + 1) % segments
            bm.faces.new((c_front, rings[-1][next_s], rings[-1][s]))

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def create_octagon_profile_extrusion(bm, radius=0.25, depth=0.05, rim_thick=0.04):
    """八角形のクラシック木製フレームを生成 (前面=-Y)"""
    segments = 8
    outer_verts_back = []
    outer_verts_front = []
    for s in range(segments):
        ang = (s / segments) * 2.0 * math.pi + (math.pi / 8.0)
        x = radius * math.cos(ang)
        z = radius * math.sin(ang)
        outer_verts_back.append(bm.verts.new((x, 0.0, z)))
        outer_verts_front.append(bm.verts.new((x, -depth, z)))

    r_inner = radius - rim_thick
    inner_verts_front = []
    for s in range(segments):
        ang = (s / segments) * 2.0 * math.pi + (math.pi / 8.0)
        x = r_inner * math.cos(ang)
        z = r_inner * math.sin(ang)
        inner_verts_front.append(bm.verts.new((x, -depth * 0.7, z)))

    # 外側面
    for s in range(segments):
        next_s = (s + 1) % segments
        bm.faces.new((outer_verts_back[s], outer_verts_front[s], outer_verts_front[next_s], outer_verts_back[next_s]))

    # 前面リム
    for s in range(segments):
        next_s = (s + 1) % segments
        bm.faces.new((outer_verts_front[s], inner_verts_front[s], inner_verts_front[next_s], outer_verts_front[next_s]))

    # 背面を閉じる (y=0)
    c_back = bm.verts.new((0.0, 0.0, 0.0))
    for s in range(segments):
        next_s = (s + 1) % segments
        bm.faces.new((c_back, outer_verts_back[s], outer_verts_back[next_s]))

    # 文字盤受け面
    c_dial = bm.verts.new((0.0, -depth * 0.7, 0.0))
    for s in range(segments):
        next_s = (s + 1) % segments
        bm.faces.new((c_dial, inner_verts_front[next_s], inner_verts_front[s]))

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def build_roman_numerals_mesh(context, radius_dial=0.17, y_pos=-0.038, scale=1.0):
    """12個の立体ローマ数字 (I〜XII) を円周上に生成して1つのメッシュとして結合 (前面=-Y)"""
    num_objs = []
    
    font_size = 0.032 * scale
    extrude_depth = 0.004 * scale
    r_track = radius_dial * 0.75

    for i in range(12):
        txt = ROMAN_NUMS[i]
        ang = math.radians(90.0 - i * 30.0)
        x = r_track * math.cos(ang)
        z = r_track * math.sin(ang)

        curve_data = bpy.data.curves.new(type='FONT', name=f"Num_{txt}")
        curve_data.body = txt
        curve_data.size = font_size
        curve_data.extrude = extrude_depth
        curve_data.align_x = 'CENTER'
        curve_data.align_y = 'CENTER'

        txt_obj = bpy.data.objects.new(f"Txt_{txt}", curve_data)
        context.collection.objects.link(txt_obj)
        txt_obj.location = (x, y_pos, z)
        # 前面 (-Y) を向くように X軸周りに -90度回転
        txt_obj.rotation_euler = (math.radians(-90.0), 0.0, 0.0)
        num_objs.append(txt_obj)

    context.view_layer.update()
    depsgraph = context.evaluated_depsgraph_get()

    combined_bm = bmesh.new()
    for obj in num_objs:
        eval_obj = obj.evaluated_get(depsgraph)
        tmp_mesh = bpy.data.meshes.new_from_object(eval_obj)
        
        matrix = obj.matrix_world
        tmp_bm = bmesh.new()
        tmp_bm.from_mesh(tmp_mesh)
        for v in tmp_bm.verts:
            v.co = matrix @ v.co
        tmp_bm.to_mesh(tmp_mesh)
        tmp_bm.free()

        combined_bm.from_mesh(tmp_mesh)
        bpy.data.meshes.remove(tmp_mesh)
        bpy.data.objects.remove(obj, do_unlink=True)

    bmesh.ops.remove_doubles(combined_bm, verts=combined_bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(combined_bm, faces=combined_bm.faces)

    merged_mesh = bpy.data.meshes.new("Roman_Numerals_Mesh")
    combined_bm.to_mesh(merged_mesh)
    combined_bm.free()

    num_obj = bpy.data.objects.new("Roman_Numerals", merged_mesh)
    context.collection.objects.link(num_obj)
    return num_obj


def create_dial_ticks_bmesh(bm, radius_dial=0.17, y_pos=-0.038, scale=1.0):
    """文字盤の 60 個の目盛り（5分毎の長ライン ＋ 1分毎の刻み点）を生成 (前面=-Y)"""
    r_outer = radius_dial * 0.95
    r_inner_5min = radius_dial * 0.88
    r_inner_1min = radius_dial * 0.92
    thick_5min = 0.003 * scale
    thick_1min = 0.0015 * scale
    tick_height = 0.003 * scale

    for i in range(60):
        is_5min = (i % 5 == 0)
        r_start = r_inner_5min if is_5min else r_inner_1min
        th = thick_5min if is_5min else thick_1min
        
        ang = (i / 60.0) * 2.0 * math.pi
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        perp_x = -sin_a * (th * 0.5)
        perp_z = cos_a * (th * 0.5)

        p1 = (r_start * cos_a - perp_x, y_pos, r_start * sin_a - perp_z)
        p2 = (r_start * cos_a + perp_x, y_pos, r_start * sin_a + perp_z)
        p3 = (r_outer * cos_a + perp_x, y_pos, r_outer * sin_a + perp_z)
        p4 = (r_outer * cos_a - perp_x, y_pos, r_outer * sin_a - perp_z)

        v1 = bm.verts.new(p1)
        v2 = bm.verts.new(p2)
        v3 = bm.verts.new(p3)
        v4 = bm.verts.new(p4)

        v1_t = bm.verts.new((p1[0], p1[1] - tick_height, p1[2]))
        v2_t = bm.verts.new((p2[0], p2[1] - tick_height, p2[2]))
        v3_t = bm.verts.new((p3[0], p3[1] - tick_height, p3[2]))
        v4_t = bm.verts.new((p4[0], p4[1] - tick_height, p4[2]))

        bm.faces.new((v4_t, v3_t, v2_t, v1_t))
        bm.faces.new((v4, v4_t, v1_t, v1))
        bm.faces.new((v2_t, v3_t, v3, v2))
        bm.faces.new((v3, v3_t, v4_t, v4))
        bm.faces.new((v1_t, v2_t, v2, v1))

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def create_hand_mesh(name, length=0.12, width=0.012, is_hour=False, is_second=False, scale=1.0):
    """クラシック装飾針（スペード針 / 矢印針 / 細身秒針）の生成 (前面=-Y)"""
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm = bmesh.new()

    thick = 0.002 * scale
    l = length * scale
    w = width * scale

    if is_second:
        tail_l = l * 0.3
        v1 = bm.verts.new((-w*0.3, 0.0, -tail_l))
        v2 = bm.verts.new((w*0.3, 0.0, -tail_l))
        v3 = bm.verts.new((w*0.15, 0.0, l))
        v4 = bm.verts.new((-w*0.15, 0.0, l))
        bm.faces.new((v4, v3, v2, v1))
        v_tip = bm.verts.new((0.0, 0.0, l + w*0.8))
        bm.faces.new((v_tip, v3, v4))
    else:
        pts = [
            (-w*0.4, -l*0.15),
            (w*0.4, -l*0.15),
            (w*0.3, l*0.45),
            (w*0.9, l*0.60),
            (w*0.3, l*0.75),
            (0.0, l),
            (-w*0.3, l*0.75),
            (-w*0.9, l*0.60),
            (-w*0.3, l*0.45),
        ]
        verts_front = [bm.verts.new((px, -thick, pz)) for px, pz in pts]
        verts_back = [bm.verts.new((px, 0.0, pz)) for px, pz in pts]

        bm.faces.new(list(reversed(verts_front)))
        bm.faces.new(verts_back)
        for i in range(len(pts)):
            next_i = (i + 1) % len(pts)
            bm.faces.new((verts_front[i], verts_front[next_i], verts_back[next_i], verts_back[i]))

    # 中心ピンキャップ
    r_cap = w * 1.2
    c_front = bm.verts.new((0.0, -thick * 1.8, 0.0))
    cap_ring = []
    for s in range(12):
        ang = (s / 12.0) * 2.0 * math.pi
        cap_ring.append(bm.verts.new((r_cap * math.cos(ang), -thick * 1.2, r_cap * math.sin(ang))))
    for s in range(12):
        next_s = (s + 1) % 12
        bm.faces.new((c_front, cap_ring[next_s], cap_ring[s]))

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    for f in mesh.polygons:
        f.use_smooth = True

    return mesh


def create_clock_materials(name_prefix, style="ANTIQUE_WOOD"):
    """フレーム・文字盤・針・ガラスのマテリアル構築"""
    f_mat = bpy.data.materials.new(f"{name_prefix}_Frame")
    f_mat.use_nodes = True
    f_nodes = f_mat.node_tree.nodes
    f_bsdf = f_nodes.get("Principled BSDF")
    if style == "ANTIQUE_WOOD":
        f_bsdf.inputs['Base Color'].default_value = (0.22, 0.10, 0.05, 1.0) # ダークマホガニー
        f_bsdf.inputs['Roughness'].default_value = 0.35
    elif style == "VINTAGE_BRASS":
        f_bsdf.inputs['Base Color'].default_value = (0.85, 0.65, 0.28, 1.0) # アンティーク真鍮
        f_bsdf.inputs['Metallic'].default_value = 0.90
        f_bsdf.inputs['Roughness'].default_value = 0.30
    else: # MODERN_BLACK
        f_bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1.0)
        f_bsdf.inputs['Roughness'].default_value = 0.25

    d_mat = bpy.data.materials.new(f"{name_prefix}_Dial")
    d_mat.use_nodes = True
    d_bsdf = d_mat.node_tree.nodes.get("Principled BSDF")
    d_bsdf.inputs['Base Color'].default_value = (0.95, 0.92, 0.85, 1.0) # アイボリー
    d_bsdf.inputs['Roughness'].default_value = 0.60

    n_mat = bpy.data.materials.new(f"{name_prefix}_Numerals")
    n_mat.use_nodes = True
    n_bsdf = n_mat.node_tree.nodes.get("Principled BSDF")
    n_bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1.0) # マットブラック
    n_bsdf.inputs['Roughness'].default_value = 0.35

    s_mat = bpy.data.materials.new(f"{name_prefix}_Seconds")
    s_mat.use_nodes = True
    s_bsdf = s_mat.node_tree.nodes.get("Principled BSDF")
    s_bsdf.inputs['Base Color'].default_value = (0.85, 0.12, 0.12, 1.0) # 真紅
    s_bsdf.inputs['Roughness'].default_value = 0.30

    g_mat = bpy.data.materials.new(f"{name_prefix}_Glass")
    g_mat.use_nodes = True
    g_bsdf = g_mat.node_tree.nodes.get("Principled BSDF")
    g_bsdf.inputs['Base Color'].default_value = (0.95, 0.98, 1.0, 1.0)
    g_bsdf.inputs['Transmission'].default_value = 1.0
    g_bsdf.inputs['Roughness'].default_value = 0.02
    g_bsdf.inputs['IOR'].default_value = 1.50
    g_mat.blend_method = 'BLEND'
    g_mat.shadow_method = 'HASHED'
    if hasattr(g_mat, 'use_screen_refraction'):
        g_mat.use_screen_refraction = True

    return f_mat, d_mat, n_mat, s_mat, g_mat


def generate_wall_clock_asset(
    context,
    name="Wall_Clock",
    shape='ROUND',
    style="ANTIQUE_WOOD",
    hour=10,
    minute=10,
    second=35,
    show_seconds=True,
    show_glass=True,
    diameter=0.45,
    scale=1.0
):
    """
    ローマ数字刻印の壁掛け時計をプロシージャル生成 (前面=-Y)
    時針・分針・秒針が独立した子オブジェクトとして時刻角度に自動回転
    """
    radius = (diameter * 0.5) * scale
    r_dial = radius * 0.78
    depth = 0.055 * scale
    y_dial = -depth * 0.65

    f_mat, d_mat, n_mat, s_mat, g_mat = create_clock_materials(name, style=style)

    mesh_frame = bpy.data.meshes.new(f"{name}_Frame_Mesh")
    obj_clock = bpy.data.objects.new(name, mesh_frame)
    context.collection.objects.link(obj_clock)

    bm_frame = bmesh.new()
    if shape == 'ROUND':
        prof = [
            (radius, 0.0),                      # 背面外周 (壁 y=0)
            (radius * 1.02, -depth * 0.2),      # 外周ふくらみ
            (radius * 0.98, -depth * 0.5),      # くびれ
            (radius * 0.92, -depth * 0.9),      # 前面モールディング頂点
            (radius * 0.85, -depth),            # 前面リップ
            (r_dial, y_dial),                   # 文字盤受け面
        ]
        create_circle_profile_lathe(bm_frame, prof, segments=48)
    else: # OCTAGON
        create_octagon_profile_extrusion(bm_frame, radius=radius, depth=depth, rim_thick=radius - r_dial)

    bm_frame.to_mesh(mesh_frame)
    bm_frame.free()

    for f in mesh_frame.polygons:
        f.use_smooth = True

    obj_clock.data.materials.append(f_mat)

    # 3. 文字盤プレート
    mesh_dial = bpy.data.meshes.new(f"{name}_Dial_Mesh")
    obj_dial = bpy.data.objects.new(f"{name}_Dial", mesh_dial)
    context.collection.objects.link(obj_dial)

    bm_dial = bmesh.new()
    c_d = bm_dial.verts.new((0.0, y_dial - 0.0005 * scale, 0.0))
    d_ring = []
    for s in range(48):
        ang = (s / 48.0) * 2.0 * math.pi
        d_ring.append(bm_dial.verts.new((r_dial * 0.98 * math.cos(ang), y_dial - 0.0005 * scale, r_dial * 0.98 * math.sin(ang))))
    for s in range(48):
        next_s = (s + 1) % 48
        bm_dial.faces.new((c_d, d_ring[next_s], d_ring[s]))

    create_dial_ticks_bmesh(bm_dial, radius_dial=r_dial, y_pos=y_dial - 0.001 * scale, scale=scale)

    bm_dial.to_mesh(mesh_dial)
    bm_dial.free()
    for f in mesh_dial.polygons:
        f.use_smooth = True
    obj_dial.data.materials.append(d_mat)
    obj_dial.parent = obj_clock

    # 4. 3D 立体ローマ数字 (I 〜 XII)
    obj_nums = build_roman_numerals_mesh(context, radius_dial=r_dial, y_pos=y_dial - 0.0015 * scale, scale=scale)
    obj_nums.name = f"{name}_Roman_Numerals"
    obj_nums.data.materials.append(n_mat)
    obj_nums.parent = obj_clock

    # 5. 時計の針
    y_hands = y_dial - 0.008 * scale

    # A. 時針 (Hour Hand)
    mesh_hour = create_hand_mesh(f"{name}_Hour", length=r_dial * 0.55, width=0.014 * scale, is_hour=True, scale=scale)
    obj_hour = bpy.data.objects.new(f"{name}_Hand_Hour", mesh_hour)
    context.collection.objects.link(obj_hour)
    obj_hour.location = (0.0, y_hands, 0.0)
    # 前面(-Y)から見て時計回り回転 (Y軸周りにマイナス回転)
    hour_rot_deg = ((hour % 12 + minute / 60.0) / 12.0) * 360.0
    obj_hour.rotation_euler = (0.0, math.radians(hour_rot_deg), 0.0)
    obj_hour.data.materials.append(n_mat)
    obj_hour.parent = obj_clock

    # B. 分針 (Minute Hand)
    mesh_min = create_hand_mesh(f"{name}_Minute", length=r_dial * 0.82, width=0.011 * scale, is_hour=False, scale=scale)
    obj_min = bpy.data.objects.new(f"{name}_Hand_Minute", mesh_min)
    context.collection.objects.link(obj_min)
    obj_min.location = (0.0, y_hands - 0.003 * scale, 0.0)
    min_rot_deg = (minute / 60.0) * 360.0
    obj_min.rotation_euler = (0.0, math.radians(min_rot_deg), 0.0)
    obj_min.data.materials.append(n_mat)
    obj_min.parent = obj_clock

    # C. 秒針 (Second Hand)
    obj_sec = None
    if show_seconds:
        mesh_sec = create_hand_mesh(f"{name}_Second", length=r_dial * 0.88, width=0.006 * scale, is_second=True, scale=scale)
        obj_sec = bpy.data.objects.new(f"{name}_Hand_Second", mesh_sec)
        context.collection.objects.link(obj_sec)
        obj_sec.location = (0.0, y_hands - 0.006 * scale, 0.0)
        sec_rot_deg = (second / 60.0) * 360.0
        obj_sec.rotation_euler = (0.0, math.radians(sec_rot_deg), 0.0)
        obj_sec.data.materials.append(s_mat)
        obj_sec.parent = obj_clock

    # 6. 前面ドームガラス
    obj_glass = None
    if show_glass:
        mesh_glass = bpy.data.meshes.new(f"{name}_Glass_Mesh")
        obj_glass = bpy.data.objects.new(f"{name}_Glass", mesh_glass)
        context.collection.objects.link(obj_glass)

        bm_glass = bmesh.new()
        rings_g = []
        dome_h = 0.015 * scale
        for d_step in range(6):
            t = d_step / 5.0
            r_g = r_dial * math.cos(t * 0.4)
            y_g = y_hands - 0.008 * scale - dome_h * (1.0 - math.sin(t * (math.pi * 0.5)))
            ring = []
            for s in range(36):
                ang = (s / 36.0) * 2.0 * math.pi
                ring.append(bm_glass.verts.new((r_g * math.cos(ang), y_g, r_g * math.sin(ang))))
            rings_g.append(ring)

        for d_step in range(len(rings_g) - 1):
            r1 = rings_g[d_step]
            r2 = rings_g[d_step + 1]
            for s in range(36):
                next_s = (s + 1) % 36
                bm_glass.faces.new((r1[s], r2[s], r2[next_s], r1[next_s]))

        c_top = bm_glass.verts.new((0.0, y_hands - 0.008 * scale - dome_h, 0.0))
        for s in range(36):
            next_s = (s + 1) % 36
            bm_glass.faces.new((c_top, rings_g[-1][next_s], rings_g[-1][s]))

        bmesh.ops.remove_doubles(bm_glass, verts=bm_glass.verts, dist=0.0005)
        bmesh.ops.recalc_face_normals(bm_glass, faces=bm_glass.faces)
        bm_glass.to_mesh(mesh_glass)
        bm_glass.free()

        for f in mesh_glass.polygons:
            f.use_smooth = True

        obj_glass.data.materials.append(g_mat)
        obj_glass.parent = obj_clock

    context.view_layer.objects.active = obj_clock
    obj_clock.select_set(True)

    return obj_clock, obj_dial, obj_nums, obj_hour, obj_min, obj_sec, obj_glass
