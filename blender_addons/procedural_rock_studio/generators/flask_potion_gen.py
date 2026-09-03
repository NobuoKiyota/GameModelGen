import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

def create_lathe_mesh(bm, profile_points, segments=32):
    """(radius, z) のプロファイルリストからY軸/Z軸周りの回転体メッシュを生成"""
    rings = []
    for r, z in profile_points:
        ring = []
        for s in range(segments):
            angle = (s / segments) * 2.0 * math.pi
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            v = bm.verts.new((x, y, z))
            ring.append(v)
        rings.append(ring)

    # リング間をクワッド面で接続
    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i + 1]
        for s in range(segments):
            next_s = (s + 1) % segments
            bm.faces.new((r1[s], r1[next_s], r2[next_s], r2[s]))

    # 底面を閉じる (最初のリングの半径が 0 でない場合、中心頂点を打ってファン張り)
    if profile_points[0][0] > 0.0001:
        c_bottom = bm.verts.new((0.0, 0.0, profile_points[0][1]))
        r_bot = rings[0]
        for s in range(segments):
            next_s = (s + 1) % segments
            bm.faces.new((c_bottom, r_bot[next_s], r_bot[s]))

    # 上面を閉じる (最後のリングの半径が 0 でない場合)
    if profile_points[-1][0] > 0.0001:
        c_top = bm.verts.new((0.0, 0.0, profile_points[-1][1]))
        r_top = rings[-1]
        for s in range(segments):
            next_s = (s + 1) % segments
            bm.faces.new((c_top, r_top[s], r_top[next_s]))

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def generate_flask_profiles(shape_type='CONICAL', scale=1.0):
    """外殻および内殻のプロファイル点を生成"""
    # scale基準: 高さ約 0.45m (卓上サイズ)
    h = 0.45 * scale
    thick = 0.012 * scale

    if shape_type == 'CONICAL': # 三角フラスコ
        # (r, z)
        # 底面半径 0.20, 首の付け根 z=0.28 r=0.05, 口元 z=0.42 r=0.045, リップ z=0.45 r=0.06
        outer = [
            (0.0, 0.0),
            (0.18 * scale, 0.0),
            (0.20 * scale, 0.03 * scale),
            (0.18 * scale, 0.12 * scale),
            (0.12 * scale, 0.22 * scale),
            (0.065 * scale, 0.30 * scale),
            (0.055 * scale, 0.40 * scale),
            (0.070 * scale, 0.44 * scale), # リップふち
            (0.070 * scale, 0.45 * scale),
            (0.055 * scale, 0.45 * scale), # 内壁へ折り返し
        ]
        inner_r_func = lambda z: max(0.04 * scale, (0.19 * scale - (z / (0.30 * scale)) * 0.13 * scale) if z < 0.30 * scale else 0.045 * scale)
    else: # ROUND (丸底/平底球形ポーション)
        outer = [
            (0.0, 0.0),
            (0.10 * scale, 0.0),
            (0.18 * scale, 0.06 * scale),
            (0.22 * scale, 0.16 * scale), # 球の最大部
            (0.18 * scale, 0.26 * scale),
            (0.09 * scale, 0.32 * scale),
            (0.06 * scale, 0.40 * scale),
            (0.075 * scale, 0.44 * scale), # リップふち
            (0.075 * scale, 0.45 * scale),
            (0.055 * scale, 0.45 * scale),
        ]
        inner_r_func = lambda z: max(0.04 * scale, math.sqrt(max(0.001, (0.20 * scale)**2 - (z - 0.16 * scale)**2)))

    return outer, inner_r_func, h


def create_flask_liquid_bmesh(bm, shape_type='CONICAL', liquid_level=0.55, liquid_tilt_deg=0.0, surface_noise=0.02, scale=1.0, segments=32):
    """内壁に沿った液体メッシュを生成し、上面にノイズ歪みと傾き補正を適用"""
    h_max = 0.30 * scale # 液面の最大限界（首の下あたりまで）
    h_liquid = max(0.03 * scale, h_max * liquid_level)

    # 液体プロファイル点 (底面から液面高さまで)
    steps = 14
    prof = []
    for step in range(steps + 1):
        t = step / steps
        z = t * h_liquid
        if shape_type == 'CONICAL':
            r = max(0.03 * scale, (0.19 * scale - (z / (0.30 * scale)) * 0.125 * scale))
        else: # ROUND
            r = max(0.03 * scale, math.sqrt(max(0.002, (0.20 * scale)**2 - (z - 0.16 * scale)**2)))
        prof.append((r, z))

    create_lathe_mesh(bm, prof, segments=segments)

    # 液面（上面頂点群）を特定して傾きとノイズ歪みを適用
    bm.verts.ensure_lookup_table()
    tilt_rad = math.radians(liquid_tilt_deg)
    sin_t = math.sin(tilt_rad)
    cos_t = math.cos(tilt_rad)

    surface_verts = [v for v in bm.verts if abs(v.co.z - h_liquid) < 0.001 * scale]

    # 液面の中心を細分化して波紋・歪みを豊かにする
    top_faces = [f for f in bm.faces if any(v in surface_verts for v in f.verts) and f.normal.z > 0.6]
    if top_faces:
        bmesh.ops.subdivide_edges(bm, edges=list({e for f in top_faces for e in f.edges}), cuts=2)
        bm.verts.ensure_lookup_table()

    # 液面頂点（Z が液面付近の頂点）に傾きとノイズ歪みを乗せる
    for v in bm.verts:
        if v.co.z >= h_liquid - 0.005 * scale:
            # 1. 傾き補正 (X軸周りまたはY軸周りの回転: 水平維持)
            x = v.co.x
            y = v.co.y
            # 傾きによるZのオフセット
            z_tilt = y * math.tan(tilt_rad)

            # 2. 静止画向けの表面張力・微細ノイズ歪み (多重サイン波合成)
            wave1 = math.sin(x * 25.0 + 1.2) * math.cos(y * 25.0 + 0.8)
            wave2 = math.sin(math.hypot(x, y) * 35.0) * 0.5
            distort = (wave1 + wave2) * surface_noise * scale

            # 外周は内壁に接触しているので歪みを減衰 (マージン)
            r = math.hypot(x, y)
            edge_factor = min(1.0, max(0.0, (prof[-1][0] - r) / (0.02 * scale)))

            v.co.z = h_liquid + z_tilt + (distort * edge_factor)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def create_cork_stopper_bmesh(bm, z_base=0.42, r_bottom=0.048, r_top=0.058, height=0.08, segments=24):
    """コルク栓メッシュの生成"""
    prof = [
        (0.0, z_base),
        (r_bottom, z_base),
        (r_top, z_base + height),
        (0.0, z_base + height)
    ]
    create_lathe_mesh(bm, prof, segments=segments)


def create_flask_materials(name_prefix, liquid_color=(0.9, 0.15, 0.25, 1.0), glow=0.2):
    """ガラス・液体・コルクのプロシージャルシェーダーを構築"""
    # 1. ガラスマテリアル (Glass Material)
    g_mat = bpy.data.materials.new(f"{name_prefix}_Glass")
    g_mat.use_nodes = True
    g_nodes = g_mat.node_tree.nodes
    g_links = g_mat.node_tree.links
    g_nodes.clear()

    g_out = g_nodes.new('ShaderNodeOutputMaterial')
    g_bsdf = g_nodes.new('ShaderNodeBsdfPrincipled')
    g_bsdf.inputs['Base Color'].default_value = (0.95, 0.98, 1.0, 1.0)
    g_bsdf.inputs['Roughness'].default_value = 0.04
    g_bsdf.inputs['Transmission'].default_value = 1.0
    g_bsdf.inputs['IOR'].default_value = 1.50
    g_links.new(g_bsdf.outputs['BSDF'], g_out.inputs['Surface'])

    # EEVEE 屈折・透過設定
    g_mat.blend_method = 'BLEND'
    g_mat.shadow_method = 'HASHED'
    if hasattr(g_mat, 'use_screen_refraction'):
        g_mat.use_screen_refraction = True

    # 2. 液体マテリアル (Liquid Material)
    l_mat = bpy.data.materials.new(f"{name_prefix}_Liquid")
    l_mat.use_nodes = True
    l_nodes = l_mat.node_tree.nodes
    l_links = l_mat.node_tree.links
    l_nodes.clear()

    l_out = l_nodes.new('ShaderNodeOutputMaterial')
    l_bsdf = l_nodes.new('ShaderNodeBsdfPrincipled')
    l_bsdf.inputs['Base Color'].default_value = liquid_color
    l_bsdf.inputs['Roughness'].default_value = 0.08
    l_bsdf.inputs['Transmission'].default_value = 0.85
    l_bsdf.inputs['IOR'].default_value = 1.333

    # 発光 (Glow / Emission)
    if glow > 0.001:
        l_bsdf.inputs['Emission'].default_value = liquid_color
        l_bsdf.inputs['Emission Strength'].default_value = glow * 2.5

    l_links.new(l_bsdf.outputs['BSDF'], l_out.inputs['Surface'])
    l_mat.blend_method = 'BLEND'
    l_mat.shadow_method = 'HASHED'

    # 3. コルクマテリアル (Cork Material)
    c_mat = bpy.data.materials.new(f"{name_prefix}_Cork")
    c_mat.use_nodes = True
    c_nodes = c_mat.node_tree.nodes
    c_links = c_mat.node_tree.links
    c_nodes.clear()

    c_out = c_nodes.new('ShaderNodeOutputMaterial')
    c_bsdf = c_nodes.new('ShaderNodeBsdfPrincipled')
    c_bsdf.inputs['Base Color'].default_value = (0.42, 0.28, 0.16, 1.0)
    c_bsdf.inputs['Roughness'].default_value = 0.88
    c_links.new(c_bsdf.outputs['BSDF'], c_out.inputs['Surface'])

    return g_mat, l_mat, c_mat


def generate_flask_potion_asset(
    context,
    name="Flask_Potion",
    shape_type='CONICAL',
    liquid_level=0.55,
    flask_tilt_deg=0.0,
    liquid_tilt_deg=0.0,
    surface_noise=0.02,
    liquid_color=(0.9, 0.15, 0.25, 1.0),
    glow=0.2,
    has_cork=True,
    scale=1.0
):
    """
    フラスコ容器・液体・コルクを統合生成するマスター関数
    容器自体の傾き(flask_tilt_deg)と、液面の水平補正傾き(liquid_tilt_deg)に対応
    """
    # 1. フラスコガラス容器
    mesh_glass = bpy.data.meshes.new(f"{name}_Glass_Mesh")
    obj_glass = bpy.data.objects.new(name, mesh_glass)
    context.collection.objects.link(obj_glass)

    bm_glass = bmesh.new()
    outer, _, _ = generate_flask_profiles(shape_type=shape_type, scale=scale)
    create_lathe_mesh(bm_glass, outer, segments=32)
    bm_glass.to_mesh(mesh_glass)
    bm_glass.free()

    for f in mesh_glass.polygons:
        f.use_smooth = True

    # ガラスに厚みをつける (Solidify)
    sol = obj_glass.modifiers.new(name="Glass_Thickness", type='SOLIDIFY')
    sol.thickness = 0.010 * scale
    sol.offset = -1.0
    sol.use_rim = True

    # サブディビジョンで丸み
    sub = obj_glass.modifiers.new(name="Subdiv", type='SUBSURF')
    sub.levels = 1

    # 2. 内部液体メッシュ
    mesh_liq = bpy.data.meshes.new(f"{name}_Liquid_Mesh")
    obj_liq = bpy.data.objects.new(f"{name}_Liquid", mesh_liq)
    context.collection.objects.link(obj_liq)

    bm_liq = bmesh.new()
    create_flask_liquid_bmesh(
        bm_liq,
        shape_type=shape_type,
        liquid_level=liquid_level,
        liquid_tilt_deg=liquid_tilt_deg,
        surface_noise=surface_noise,
        scale=scale,
        segments=32
    )
    bm_liq.to_mesh(mesh_liq)
    bm_liq.free()

    for f in mesh_liq.polygons:
        f.use_smooth = True

    # 3. コルク栓メッシュ
    obj_cork = None
    if has_cork:
        mesh_cork = bpy.data.meshes.new(f"{name}_Cork_Mesh")
        obj_cork = bpy.data.objects.new(f"{name}_Cork", mesh_cork)
        context.collection.objects.link(obj_cork)

        bm_cork = bmesh.new()
        create_cork_stopper_bmesh(
            bm_cork,
            z_base=0.41 * scale,
            r_bottom=0.048 * scale,
            r_top=0.060 * scale,
            height=0.08 * scale,
            segments=24
        )
        bm_cork.to_mesh(mesh_cork)
        bm_cork.free()
        for f in mesh_cork.polygons:
            f.use_smooth = True

    # 4. マテリアルの適用
    g_mat, l_mat, c_mat = create_flask_materials(name, liquid_color=liquid_color, glow=glow)
    obj_glass.data.materials.append(g_mat)
    obj_liq.data.materials.append(l_mat)
    if obj_cork:
        obj_cork.data.materials.append(c_mat)

    # 5. 親子付け (液体とコルクをガラス容器の子にする)
    obj_liq.parent = obj_glass
    if obj_cork:
        obj_cork.parent = obj_glass

    # 6. フラスコ容器自体の傾き設定 (flask_tilt_deg)
    if abs(flask_tilt_deg) > 0.01:
        obj_glass.rotation_euler = (0.0, math.radians(flask_tilt_deg), 0.0)

    context.view_layer.objects.active = obj_glass
    obj_glass.select_set(True)

    return obj_glass, obj_liq, obj_cork
