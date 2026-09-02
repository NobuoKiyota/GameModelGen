import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

def build_gothic_clustered_pillar(bm, height=4.0, radius=0.4, colonnette_count=6, seed=0):
    """【動画 yR3hx1l7nn8 準拠】ゴシック調の束ね柱（Clustered Column）"""
    rng = random.Random(seed)
    
    # 1. 多段の八角形ベース (Plinth / Base)
    base_height = height * 0.12
    base_r = radius * 1.6
    # 下段
    bmesh.ops.create_circle(bm, cap_ends=True, radius=base_r, segments=8, matrix=Matrix.Translation((0, 0, 0)))
    bmesh.ops.extrude_face_region(bm, geom=bm.faces)
    for v in bm.verts:
        if v.co.z > 0:
            v.co.z = base_height * 0.5
    # 中段
    bmesh.ops.create_circle(bm, cap_ends=True, radius=base_r * 0.85, segments=8, matrix=Matrix.Translation((0, 0, base_height * 0.5)))
    # 上段トーラス
    bmesh.ops.create_circle(bm, cap_ends=True, radius=base_r * 0.7, segments=16, matrix=Matrix.Translation((0, 0, base_height)))

    # 2. 中央の主柱 (Main Shaft)
    shaft_start_z = base_height
    shaft_end_z = height * 0.88
    shaft_h = shaft_end_z - shaft_start_z
    main_r = radius * 0.65
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=main_r, radius2=main_r * 0.95, depth=shaft_h,
        matrix=Matrix.Translation((0, 0, shaft_start_z + shaft_h * 0.5))
    )

    # 3. 周囲に束ねられた小円柱群 (Colonnettes)
    col_r = radius * 0.22
    orbit_r = radius * 0.72
    angle_step = (2.0 * math.pi) / colonnette_count
    for i in range(colonnette_count):
        ang = i * angle_step
        cx = math.cos(ang) * orbit_r
        cy = math.sin(ang) * orbit_r
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=12,
            radius1=col_r, radius2=col_r * 0.92, depth=shaft_h,
            matrix=Matrix.Translation((cx, cy, shaft_start_z + shaft_h * 0.5))
        )

    # 4. フレア状の装飾柱頭 (Capital)
    cap_start_z = shaft_end_z
    cap_h = height - cap_start_z
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=radius * 0.85, radius2=radius * 1.5, depth=cap_h * 0.6,
        matrix=Matrix.Translation((0, 0, cap_start_z + cap_h * 0.3))
    )
    # 最上部の八角形アバカス（天板）
    bmesh.ops.create_circle(
        bm, cap_ends=True, radius=radius * 1.6, segments=8,
        matrix=Matrix.Translation((0, 0, height - cap_h * 0.2))
    )


def build_roman_fluted_pillar(bm, height=4.0, radius=0.4, flute_count=18, seed=0):
    """【動画 o6qQAKKbPRo 準拠】ギリシャ・ローマ溝彫り円柱 (Fluted Classical Column)"""
    # 1. 円形ベース (Plinth & Torus)
    base_h = height * 0.1
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((radius * 2.6, radius * 2.6, base_h * 0.5, 1.0)) @ Matrix.Translation((0, 0, base_h * 0.25)))
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=radius * 1.3, radius2=radius * 1.1, depth=base_h * 0.5,
        matrix=Matrix.Translation((0, 0, base_h * 0.75))
    )

    # 2. フルーティング（縦溝彫り）柱身 (Fluted Shaft)
    shaft_start_z = base_h
    shaft_end_z = height * 0.9
    shaft_h = shaft_end_z - shaft_start_z
    
    # 溝彫り断面のポリゴン生成
    ring_verts = []
    seg_step = (2.0 * math.pi) / flute_count
    for i in range(flute_count):
        base_ang = i * seg_step
        # 溝の外側ピーク
        px = math.cos(base_ang) * radius
        py = math.sin(base_ang) * radius
        # 溝の内側くぼみ
        mid_ang = base_ang + seg_step * 0.5
        ix = math.cos(mid_ang) * (radius * 0.88)
        iy = math.sin(mid_ang) * (radius * 0.88)
        ring_verts.extend([(px, py), (ix, iy)])

    # 下端と上端のリングを作成してロフト
    bot_verts = [bm.verts.new(Vector((vx, vy, shaft_start_z))) for vx, vy in ring_verts]
    # エンタシス（わずかな中央の膨らみと上部の先細り）
    top_scale = 0.9
    top_verts = [bm.verts.new(Vector((vx * top_scale, vy * top_scale, shaft_end_z))) for vx, vy in ring_verts]
    bm.verts.ensure_lookup_table()

    n = len(ring_verts)
    for i in range(n):
        i_next = (i + 1) % n
        bm.faces.new([bot_verts[i], bot_verts[i_next], top_verts[i_next], top_verts[i]])

    # 3. ドーリア式/トスカナ式 柱頭 (Capital & Abacus)
    cap_start_z = shaft_end_z
    cap_h = height - cap_start_z
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=radius * 0.95, radius2=radius * 1.3, depth=cap_h * 0.5,
        matrix=Matrix.Translation((0, 0, cap_start_z + cap_h * 0.25))
    )
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Diagonal((radius * 2.6, radius * 2.6, cap_h * 0.5, 1.0)) @ Matrix.Translation((0, 0, height - cap_h * 0.25))
    )


def build_ruined_ancient_pillar(bm, height=3.5, radius=0.42, seed=101):
    """古代遺跡の崩壊石柱 (Ruined Broken Pillar)"""
    rng = random.Random(seed)
    
    # 1. 荒削りなベース
    base_h = height * 0.12
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=radius * 1.4, radius2=radius * 1.15, depth=base_h,
        matrix=Matrix.Translation((0, 0, base_h * 0.5))
    )

    # 2. 不揃いなドラム状石積み柱身 (Stacked Drum Shaft)
    drum_count = rng.randint(3, 5)
    drum_h = (height * 0.75) / drum_count
    curr_z = base_h
    
    for d in range(drum_count):
        # 最上部のドラムは斜めに破損
        is_top = (d == drum_count - 1)
        r1 = radius * (1.0 - d * 0.03)
        r2 = radius * (0.97 - d * 0.03)
        
        offset_x = (rng.random() - 0.5) * 0.04
        offset_y = (rng.random() - 0.5) * 0.04
        
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=16,
            radius1=r1, radius2=r2, depth=drum_h * (0.6 if is_top else 0.96),
            matrix=Matrix.Translation((offset_x, offset_y, curr_z + drum_h * 0.5))
        )
        curr_z += drum_h


def build_square_monument_pillar(bm, height=4.0, radius=0.4, seed=202):
    """【動画 b8g8j-7KWYM 準拠】西洋角柱・モニュメント (Classical Square Pillar)"""
    # 1. 多段四角形ベース
    base_h = height * 0.15
    w = radius * 2.0
    # 下段台座
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((w * 1.4, w * 1.4, base_h * 0.5, 1.0)) @ Matrix.Translation((0, 0, base_h * 0.25)))
    # 上段台座
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((w * 1.15, w * 1.15, base_h * 0.5, 1.0)) @ Matrix.Translation((0, 0, base_h * 0.75)))

    # 2. 四角柱身 (Shaft with Inset Panel)
    shaft_start_z = base_h
    shaft_end_z = height * 0.85
    shaft_h = shaft_end_z - shaft_start_z
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Diagonal((w, w, shaft_h, 1.0)) @ Matrix.Translation((0, 0, shaft_start_z + shaft_h * 0.5))
    )

    # 3. コーニス・天頂装飾 (Capital & Crown)
    cap_start_z = shaft_end_z
    cap_h = height - cap_start_z
    # フレア段差
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Diagonal((w * 1.25, w * 1.25, cap_h * 0.4, 1.0)) @ Matrix.Translation((0, 0, cap_start_z + cap_h * 0.2))
    )
    # 最上部コーニス
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Diagonal((w * 1.45, w * 1.45, cap_h * 0.6, 1.0)) @ Matrix.Translation((0, 0, height - cap_h * 0.3))
    )


def create_procedural_pillar(context, name="Procedural_Pillar", pillar_type="GOTHIC_CLUSTERED",
                             height=4.0, radius=0.4, colonnettes=6, flutes=18,
                             mat_type="MARBLE", seed=0):
    """プロシージャル柱（Pillar）を生成し、メッシュ・マテリアル・モディファイアを構築"""
    mesh = bpy.data.meshes.new(name=f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()

    if pillar_type == "GOTHIC_CLUSTERED":
        build_gothic_clustered_pillar(bm, height=height, radius=radius, colonnette_count=colonnettes, seed=seed)
    elif pillar_type == "ROMAN_FLUTED":
        build_roman_fluted_pillar(bm, height=height, radius=radius, flute_count=flutes, seed=seed)
    elif pillar_type == "RUINED_ANCIENT":
        build_ruined_ancient_pillar(bm, height=height, radius=radius, seed=seed)
    elif pillar_type == "SQUARE_MONUMENT":
        build_square_monument_pillar(bm, height=height, radius=radius, seed=seed)
    else:
        build_gothic_clustered_pillar(bm, height=height, radius=radius, colonnette_count=colonnettes, seed=seed)

    # 頂点・面のクリーンアップとスムースシェード
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True

    bm.to_mesh(mesh)
    bm.free()

    # 自動スムーズ法線
    try:
        mesh.use_auto_smooth = True
        mesh.auto_smooth_angle = math.radians(35.0)
    except Exception:
        pass

    # ピボット（原点）を底面に配置
    min_z = min((v.co.z for v in mesh.vertices), default=0.0)
    for v in mesh.vertices:
        v.co.z -= min_z
    mesh.update()

    # ベベルモディファイアの追加（ハイライトの強調）
    bev = obj.modifiers.new(name="Edge_Bevel", type='BEVEL')
    bev.width = 0.015
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(30.0)

    # 遺跡タイプの場合はディスプレイス（ひび割れ・風化）を追加
    if pillar_type == "RUINED_ANCIENT":
        disp = obj.modifiers.new(name="Rock_Erosion", type='DISPLACE')
        tex = bpy.data.textures.new(name=f"{name}_Erosion_Tex", type='CLOUDS')
        tex.noise_scale = 0.35
        disp.texture = tex
        disp.strength = 0.04
        disp.mid_level = 0.5

    # UV 自動展開
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    try:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
        bpy.ops.object.mode_set(mode='OBJECT')
    except Exception:
        pass

    return obj
