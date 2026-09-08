import bpy
import bmesh
import math
from mathutils import Vector, Matrix

def find_speaker_root(obj):
    """選択されたオブジェクトからスピーカーのルート (Cabinet) を探す"""
    if not obj:
        return None
    curr = obj
    while curr.parent:
        curr = curr.parent
    return curr


def remove_speaker_children(root_obj):
    """既存のウーファー、ツイーター、グリル、LEDを安全に削除"""
    children = list(root_obj.children)
    for c in children:
        mesh = c.data if c.type == 'MESH' else None
        bpy.data.objects.remove(c, do_unlink=True)
        if mesh and mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def create_beveled_box(bm, width=0.18, depth=0.22, height=0.28, bevel_width=0.008):
    """角丸・ベベル加工されたスピーカーキャビネットを生成 (底面 Z=0, 前面 Y=-depth/2)"""
    w = width * 0.5
    d = depth * 0.5
    h = height

    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= width
        v.co.y *= depth
        v.co.z = (v.co.z + 0.5) * height

    if bevel_width > 0.001:
        bmesh.ops.bevel(
            bm,
            geom=bm.edges[:],
            offset=bevel_width,
            offset_type='OFFSET',
            segments=3,
            profile=0.5
        )

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def create_port_cylinder(bm, center_z=0.05, radius=0.020, depth=0.04, y_front=-0.11, segments=24):
    """前面バスレフポート (Bass Reflex Duct) の穴彫り込み"""
    rings = []
    r_lip = radius * 1.15
    for r, dy in [(r_lip, -0.001), (radius, 0.0), (radius * 0.95, depth * 0.5), (radius * 0.90, depth)]:
        ring = []
        for s in range(segments):
            ang = (s / segments) * 2.0 * math.pi
            x = r * math.cos(ang)
            z = center_z + r * math.sin(ang)
            y = y_front + dy
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)

    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i + 1]
        for s in range(segments):
            next_s = (s + 1) % segments
            bm.faces.new((r1[s], r2[s], r2[next_s], r1[next_s]))

    c_back = bm.verts.new((0.0, y_front + depth, center_z))
    for s in range(segments):
        next_s = (s + 1) % segments
        bm.faces.new((c_back, rings[-1][next_s], rings[-1][s]))


def create_woofer_mesh(name, radius=0.065, scale=1.0, segments=36):
    """
    リアルなウーファーユニット生成
    (外枠リング + 固定ビス + ロールエッジゴム + 湾曲コーン + 中央ダストキャップ)
    マテリアルスロット分け: 0=コーン, 1=フレーム/ゴムサラウンド
    """
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm = bmesh.new()

    r = radius * scale
    r_frame_out = r * 1.16
    r_frame_in  = r * 1.02
    r_surround_outer = r * 1.00
    r_surround_mid   = r * 0.88
    r_surround_inner = r * 0.76
    r_cone_deep      = r * 0.32
    r_dustcap_base   = r * 0.28

    # (r, y) プロファイル (前方向: -Y)
    prof = [
        (r_frame_out, -0.006 * scale),       # 0: 金属フレーム外周
        (r_frame_out, -0.010 * scale),       # 1:
        (r_frame_in,  -0.010 * scale),       # 2:
        (r_surround_outer, -0.008 * scale),  # 3: サラウンド外縁
        (r_surround_mid,   -0.014 * scale),  # 4: ロールエッジふくらみ
        (r_surround_inner, -0.008 * scale),  # 5: サラウンド内縁
        ((r_surround_inner + r_cone_deep)*0.5, -0.003 * scale), # 6: 湾曲コーン
        (r_cone_deep, -0.001 * scale),       # 7: コーン最深部
        (r_dustcap_base, -0.001 * scale),    # 8: ダストキャップ接合
        (r_dustcap_base * 0.5, -0.005 * scale), # 9: ドームふくらみ
        (0.0, -0.007 * scale)                # 10: ダストキャップ頂点
    ]

    rings = []
    for pr, py in prof:
        ring = []
        for s in range(segments):
            ang = (s / segments) * 2.0 * math.pi
            x = pr * math.cos(ang)
            z = pr * math.sin(ang)
            v = bm.verts.new((x, py, z))
            ring.append(v)
        rings.append(ring)

    # 面張り (マテリアルインデックス: 0〜4はゴム/フレーム=1, 5〜10はコーン=0)
    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i + 1]
        mat_idx = 1 if i < 5 else 0
        for s in range(segments):
            next_s = (s + 1) % segments
            f = bm.faces.new((r1[s], r2[s], r2[next_s], r1[next_s]))
            f.material_index = mat_idx

    c_tip = bm.verts.new((0.0, prof[-1][1], 0.0))
    for s in range(segments):
        next_s = (s + 1) % segments
        f = bm.faces.new((c_tip, rings[-1][next_s], rings[-1][s]))
        f.material_index = 0

    # 固定ビス (8個)
    r_screw_track = (r_frame_out + r_frame_in) * 0.5
    for i in range(8):
        ang = (i / 8.0) * 2.0 * math.pi + (math.pi / 8.0)
        sx = r_screw_track * math.cos(ang)
        sz = r_screw_track * math.sin(ang)
        sy = -0.011 * scale
        r_sc = 0.003 * scale
        sc_ring = []
        for s in range(6):
            s_ang = (s / 6.0) * 2.0 * math.pi
            sc_ring.append(bm.verts.new((sx + r_sc * math.cos(s_ang), sy, sz + r_sc * math.sin(s_ang))))
        c_sc = bm.verts.new((sx, sy - 0.001 * scale, sz))
        for s in range(6):
            next_s = (s + 1) % 6
            f = bm.faces.new((c_sc, sc_ring[next_s], sc_ring[s]))
            f.material_index = 1

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0002)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    for f in mesh.polygons:
        f.use_smooth = True

    return mesh


def create_tweeter_mesh(name, radius=0.025, scale=1.0, segments=32):
    """高音用ドームツイーター ＋ 音波拡散ウェーブガイド生成"""
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm = bmesh.new()

    r = radius * scale
    prof = [
        (r * 1.35, -0.004 * scale),
        (r * 1.35, -0.007 * scale),
        (r * 1.00, -0.005 * scale),
        (r * 0.65, -0.002 * scale),
        (r * 0.50, -0.001 * scale),
        (r * 0.28, -0.005 * scale),
        (0.0, -0.007 * scale)
    ]

    rings = []
    for pr, py in prof:
        ring = []
        for s in range(segments):
            ang = (s / segments) * 2.0 * math.pi
            x = pr * math.cos(ang)
            z = pr * math.sin(ang)
            v = bm.verts.new((x, py, z))
            ring.append(v)
        rings.append(ring)

    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i + 1]
        for s in range(segments):
            next_s = (s + 1) % segments
            bm.faces.new((r1[s], r2[s], r2[next_s], r1[next_s]))

    c_tip = bm.verts.new((0.0, prof[-1][1], 0.0))
    for s in range(segments):
        next_s = (s + 1) % segments
        bm.faces.new((c_tip, rings[-1][next_s], rings[-1][s]))

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0002)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    for f in mesh.polygons:
        f.use_smooth = True

    return mesh


def create_grille_mesh(name, width=0.176, height=0.276, depth=0.012, scale=1.0):
    """着脱可能な前面保護サランネット (Grille) 生成"""
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm = bmesh.new()

    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= width * scale
        v.co.y *= depth * scale
        v.co.z = (v.co.z + 0.5) * height * scale

    bmesh.ops.bevel(
        bm,
        geom=bm.edges[:],
        offset=0.006 * scale,
        offset_type='OFFSET',
        segments=2,
        profile=0.5
    )

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    for f in mesh.polygons:
        f.use_smooth = True

    return mesh


def create_speaker_materials(name_prefix, style="STUDIO_BLACK", cone_color="WHITE_CONE", led_color=(0.1, 0.6, 1.0, 1.0)):
    """PBRマテリアル構築"""
    # 1. キャビネット
    c_mat = bpy.data.materials.new(f"{name_prefix}_Cabinet")
    c_mat.use_nodes = True
    c_bsdf = c_mat.node_tree.nodes.get("Principled BSDF")
    if style == "VINTAGE_WOOD":
        c_bsdf.inputs['Base Color'].default_value = (0.24, 0.12, 0.06, 1.0) # ウォールナット木目
        c_bsdf.inputs['Roughness'].default_value = 0.38
    elif style == "STUDIO_WHITE":
        c_bsdf.inputs['Base Color'].default_value = (0.92, 0.92, 0.92, 1.0)
        c_bsdf.inputs['Roughness'].default_value = 0.30
    else: # STUDIO_BLACK
        c_bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1.0)
        c_bsdf.inputs['Roughness'].default_value = 0.35

    # 2. ウーファーコーン
    w_cone_mat = bpy.data.materials.new(f"{name_prefix}_Cone")
    w_cone_mat.use_nodes = True
    w_bsdf = w_cone_mat.node_tree.nodes.get("Principled BSDF")
    if cone_color == "WHITE_CONE":
        w_bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0) # Yamaha HS風ホワイト
        w_bsdf.inputs['Roughness'].default_value = 0.42
    elif cone_color == "YELLOW_KEVLAR":
        w_bsdf.inputs['Base Color'].default_value = (0.85, 0.70, 0.12, 1.0) # KRK風イエローケブラー
        w_bsdf.inputs['Roughness'].default_value = 0.48
    else: # BLACK_CONE
        w_bsdf.inputs['Base Color'].default_value = (0.07, 0.07, 0.07, 1.0)
        w_bsdf.inputs['Roughness'].default_value = 0.35

    # 3. ウーファーサラウンドゴム & 金属フレーム
    w_rubber_mat = bpy.data.materials.new(f"{name_prefix}_Rubber")
    w_rubber_mat.use_nodes = True
    r_bsdf = w_rubber_mat.node_tree.nodes.get("Principled BSDF")
    r_bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.08, 1.0)
    r_bsdf.inputs['Roughness'].default_value = 0.65

    # 4. ツイーター
    t_mat = bpy.data.materials.new(f"{name_prefix}_Tweeter")
    t_mat.use_nodes = True
    t_bsdf = t_mat.node_tree.nodes.get("Principled BSDF")
    t_bsdf.inputs['Base Color'].default_value = (0.12, 0.12, 0.12, 1.0)
    t_bsdf.inputs['Roughness'].default_value = 0.25

    # 5. LED
    l_mat = bpy.data.materials.new(f"{name_prefix}_LED")
    l_mat.use_nodes = True
    l_bsdf = l_mat.node_tree.nodes.get("Principled BSDF")
    l_bsdf.inputs['Base Color'].default_value = led_color
    l_bsdf.inputs['Emission'].default_value = led_color
    l_bsdf.inputs['Emission Strength'].default_value = 4.0

    # 6. サランネット (Grille)
    g_mat = bpy.data.materials.new(f"{name_prefix}_Grille")
    g_mat.use_nodes = True
    g_bsdf = g_mat.node_tree.nodes.get("Principled BSDF")
    g_bsdf.inputs['Base Color'].default_value = (0.07, 0.07, 0.07, 1.0)
    g_bsdf.inputs['Roughness'].default_value = 0.85

    return c_mat, w_cone_mat, w_rubber_mat, t_mat, l_mat, g_mat


def generate_speaker_asset(
    context,
    name="Studio_Speaker",
    style="STUDIO_BLACK",
    cone_color="WHITE_CONE",
    has_grille=False,
    led_color=(0.1, 0.6, 1.0, 1.0),
    scale=1.0,
    target_obj=None
):
    """
    スピーカーアセットをプロシージャル生成・再構築
    target_obj が指定された場合、既存のトランスフォーム(位置・回転)を維持して子オブジェクトとメッシュをその場で更新
    """
    width = 0.185 * scale
    depth = 0.220 * scale
    height = 0.285 * scale
    y_front = -depth * 0.5

    c_mat, w_cone_mat, w_rubber_mat, t_mat, l_mat, g_mat = create_speaker_materials(
        name, style=style, cone_color=cone_color, led_color=led_color
    )

    root_spk = None
    if target_obj:
        root_spk = find_speaker_root(target_obj)

    if root_spk:
        obj_cabinet = root_spk
        remove_speaker_children(obj_cabinet)
        mesh_cabinet = obj_cabinet.data
        bm_cab = bmesh.new()
    else:
        mesh_cabinet = bpy.data.meshes.new(f"{name}_Cabinet_Mesh")
        obj_cabinet = bpy.data.objects.new(name, mesh_cabinet)
        context.collection.objects.link(obj_cabinet)
        bm_cab = bmesh.new()

    # キャビネット ＋ バスレフポート生成
    create_beveled_box(bm_cab, width=width, depth=depth, height=height, bevel_width=0.008 * scale)
    create_port_cylinder(bm_cab, center_z=0.045 * scale, radius=0.018 * scale, depth=0.035 * scale, y_front=y_front, segments=24)

    bm_cab.to_mesh(mesh_cabinet)
    bm_cab.free()

    for f in mesh_cabinet.polygons:
        f.use_smooth = True

    obj_cabinet.data.materials.clear()
    obj_cabinet.data.materials.append(c_mat)

    # 3. ウーファーユニット (Woofer)
    z_woofer = 0.130 * scale
    mesh_woof = create_woofer_mesh(f"{name}_Woofer", radius=0.052 * scale, scale=1.0, segments=36)
    obj_woofer = bpy.data.objects.new(f"{name}_Woofer", mesh_woof)
    context.collection.objects.link(obj_woofer)
    obj_woofer.location = (0.0, y_front, z_woofer)
    obj_woofer.rotation_euler = (0.0, 0.0, 0.0)
    obj_woofer.data.materials.append(w_cone_mat)    # スロット0: コーン
    obj_woofer.data.materials.append(w_rubber_mat)  # スロット1: ゴム/フレーム
    obj_woofer.parent = obj_cabinet

    # 4. ツイーターユニット (Tweeter)
    z_tweeter = 0.228 * scale
    mesh_tweet = create_tweeter_mesh(f"{name}_Tweeter", radius=0.024 * scale, scale=1.0, segments=32)
    obj_tweeter = bpy.data.objects.new(f"{name}_Tweeter", mesh_tweet)
    context.collection.objects.link(obj_tweeter)
    obj_tweeter.location = (0.0, y_front, z_tweeter)
    obj_tweeter.rotation_euler = (0.0, 0.0, 0.0)
    obj_tweeter.data.materials.append(t_mat)
    obj_tweeter.parent = obj_cabinet

    # 5. 電源LEDランプ (LED Light)
    mesh_led = bpy.data.meshes.new(f"{name}_LED_Mesh")
    obj_led = bpy.data.objects.new(f"{name}_LED", mesh_led)
    context.collection.objects.link(obj_led)
    bm_led = bmesh.new()
    bmesh.ops.create_cube(bm_led, size=0.004 * scale)
    bm_led.to_mesh(mesh_led)
    bm_led.free()
    obj_led.location = (0.0, y_front - 0.002 * scale, 0.045 * scale)
    obj_led.data.materials.append(l_mat)
    obj_led.parent = obj_cabinet

    # 6. 保護グリル (Grille)
    obj_grille = None
    if has_grille:
        mesh_grille = create_grille_mesh(f"{name}_Grille", width=width * 0.96, height=height * 0.96, depth=0.010 * scale, scale=1.0)
        obj_grille = bpy.data.objects.new(f"{name}_Grille", mesh_grille)
        context.collection.objects.link(obj_grille)
        obj_grille.location = (0.0, y_front - 0.008 * scale, 0.005 * scale)
        obj_grille.data.materials.append(g_mat)
        obj_grille.parent = obj_cabinet

    context.view_layer.objects.active = obj_cabinet
    obj_cabinet.select_set(True)

    return obj_cabinet, obj_woofer, obj_tweeter, obj_led, obj_grille
