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

def build_courtyard_classic_pillar(
    bm,
    total_height=3.8,
    shaft_radius=0.26,
    flute_count=16,
    pedestal_width=0.72,
    pedestal_height=1.05,
    include_railing=True,
    railing_length=1.6,
    seed=0
):
    """
    【YouTube カミワダ テル氏『洋風の中庭風景』0:20-1:30 準拠】
    - ベベル彫り込みU字フルーテッド円柱身 (Smooth Beveled Fluted Shaft)
    - 多段ベベルモールディング ＆ 額縁彫り込みパネル付き台座 (Molded Pedestal with Recessed Panels)
    - クラシカル柱頭（エキヌス・アバクス）
    - オプション：接続手すり（手すり笠木・底板・装飾バラスター小支柱）
    """
    def add_box(center, size):
        res = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=size, verts=res['verts'])
        bmesh.ops.translate(bm, vec=center, verts=res['verts'])
        return res['verts']

    # 1. 台座 (Pedestal / Plinth Base)
    p_w = pedestal_width
    p_d = pedestal_width
    b_h1 = 0.10
    add_box((0, 0, b_h1 * 0.5), (p_w, p_d, b_h1))

    b_h2 = 0.08
    add_box((0, 0, b_h1 + b_h2 * 0.5), (p_w * 0.92, p_d * 0.92, b_h2))
    b_h3 = 0.04
    add_box((0, 0, b_h1 + b_h2 + b_h3 * 0.5), (p_w * 0.86, p_d * 0.86, b_h3))

    base_top_z = b_h1 + b_h2 + b_h3

    # 胴部 (Die / Dado with Recessed Inset Panels)
    die_w = p_w * 0.80
    die_d = p_d * 0.80
    die_top_z = pedestal_height - 0.16
    die_h = max(0.2, die_top_z - base_top_z)
    die_cz = base_top_z + die_h * 0.5

    add_box((0, 0, die_cz), (die_w, die_d, die_h))

    # 4面の額縁彫り込み（Recessed Inset Panels）
    panel_w = die_w * 0.65
    panel_h = die_h * 0.75
    frame_extra = 0.015

    frame_w = panel_w + 0.06
    frame_h = panel_h + 0.06
    add_box((0, die_d * 0.5 + frame_extra * 0.5, die_cz), (frame_w, frame_extra, frame_h))
    add_box((0, -die_d * 0.5 - frame_extra * 0.5, die_cz), (frame_w, frame_extra, frame_h))
    add_box((die_w * 0.5 + frame_extra * 0.5, 0, die_cz), (frame_extra, frame_w, frame_h))
    add_box((-die_w * 0.5 - frame_extra * 0.5, 0, die_cz), (frame_extra, frame_w, frame_h))

    # 台座笠石（Cap / Cornice）- 上部多段ベベルモールディング
    c_h1 = 0.03
    add_box((0, 0, die_top_z + c_h1 * 0.5), (die_w * 1.05, die_d * 1.05, c_h1))
    c_h2 = 0.04
    add_box((0, 0, die_top_z + c_h1 + c_h2 * 0.5), (die_w * 1.12, die_d * 1.12, c_h2))
    c_h3 = 0.05
    add_box((0, 0, die_top_z + c_h1 + c_h2 + c_h3 * 0.5), (die_w * 1.16, die_d * 1.16, c_h3))

    pedestal_top_z = die_top_z + c_h1 + c_h2 + c_h3

    # 2. 柱身台座・ベースリング (Column Attic Base)
    col_base_h = 0.11
    add_box((0, 0, pedestal_top_z + 0.025), (shaft_radius * 2.3, shaft_radius * 2.3, 0.05))
    res_torus1 = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=shaft_radius * 1.25, radius2=shaft_radius * 1.16, depth=0.035
    )
    bmesh.ops.translate(bm, vec=(0, 0, pedestal_top_z + 0.065), verts=res_torus1['verts'])
    res_torus2 = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=shaft_radius * 1.12, radius2=shaft_radius * 1.04, depth=0.025
    )
    bmesh.ops.translate(bm, vec=(0, 0, pedestal_top_z + 0.095), verts=res_torus2['verts'])

    shaft_start_z = pedestal_top_z + col_base_h

    # 3. フルーテッド柱身 (Smooth Beveled Fluted Shaft)
    capital_h = 0.26
    shaft_end_z = max(shaft_start_z + 0.5, total_height - capital_h)
    shaft_h = shaft_end_z - shaft_start_z

    profile_2d = []
    n_flutes = flute_count
    flute_ang_step = (2.0 * math.pi) / float(n_flutes)
    flute_depth = (2.0 * math.pi * shaft_radius / float(n_flutes)) * 0.38

    for fi in range(n_flutes):
        ang0 = fi * flute_ang_step
        profile_2d.append((math.cos(ang0) * shaft_radius, math.sin(ang0) * shaft_radius))

        t1 = ang0 + flute_ang_step * 0.25
        t2 = ang0 + flute_ang_step * 0.50
        t3 = ang0 + flute_ang_step * 0.75

        r_cove_shoulder = shaft_radius - flute_depth * 0.45
        r_cove_bottom   = shaft_radius - flute_depth

        profile_2d.append((math.cos(t1) * r_cove_shoulder, math.sin(t1) * r_cove_shoulder))
        profile_2d.append((math.cos(t2) * r_cove_bottom,   math.sin(t2) * r_cove_bottom))
        profile_2d.append((math.cos(t3) * r_cove_shoulder, math.sin(t3) * r_cove_shoulder))

    n_z_cuts = 16
    rings = []
    for zi in range(n_z_cuts + 1):
        zf = zi / float(n_z_cuts)
        curr_z = shaft_start_z + zf * shaft_h
        taper = 1.0 - 0.08 * (zf ** 1.6)
        
        ring_v = []
        for x2d, y2d in profile_2d:
            v = bm.verts.new((x2d * taper, y2d * taper, curr_z))
            ring_v.append(v)
        rings.append(ring_v)

    n_pts_ring = len(profile_2d)
    for zi in range(n_z_cuts):
        r_cur = rings[zi]
        r_nxt = rings[zi + 1]
        for pi in range(n_pts_ring):
            p_nxt = (pi + 1) % n_pts_ring
            bm.faces.new([r_cur[pi], r_cur[p_nxt], r_nxt[p_nxt], r_nxt[pi]])

    # 4. クラシカル柱頭 (Classical Capital)
    res_astragal = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=shaft_radius * 0.96, radius2=shaft_radius * 1.02, depth=0.035
    )
    bmesh.ops.translate(bm, vec=(0, 0, shaft_end_z + 0.017), verts=res_astragal['verts'])

    res_neck = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=shaft_radius * 0.94, radius2=shaft_radius * 0.96, depth=0.05
    )
    bmesh.ops.translate(bm, vec=(0, 0, shaft_end_z + 0.060), verts=res_neck['verts'])

    res_echinus = bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=shaft_radius * 0.96, radius2=shaft_radius * 1.25, depth=0.08
    )
    bmesh.ops.translate(bm, vec=(0, 0, shaft_end_z + 0.125), verts=res_echinus['verts'])

    abacus_w = shaft_radius * 2.35
    add_box((0, 0, shaft_end_z + 0.18), (abacus_w * 0.94, abacus_w * 0.94, 0.04))
    add_box((0, 0, shaft_end_z + 0.22), (abacus_w, abacus_w, 0.05))

    # 5. オプション：手すり（Balustrade / Railing）
    if include_railing:
        r_len = railing_length
        r_start_x = die_w * 0.5
        r_cx = r_start_x + r_len * 0.5
        r_w = 0.24

        subrail_h = 0.09
        subrail_z = base_top_z + subrail_h * 0.5
        add_box((r_cx, 0, subrail_z), (r_len, r_w, subrail_h))

        handrail_h = 0.12
        handrail_z = pedestal_top_z - handrail_h * 0.5
        add_box((r_cx, 0, handrail_z + 0.02), (r_len, r_w * 1.08, handrail_h * 0.6))
        add_box((r_cx, 0, handrail_z - 0.03), (r_len, r_w * 0.92, handrail_h * 0.4))

        baluster_space_h = (handrail_z - handrail_h * 0.5) - (subrail_z + subrail_h * 0.5)
        baluster_bottom_z = subrail_z + subrail_h * 0.5
        n_balusters = max(2, int(r_len / 0.32))
        b_spacing = r_len / float(n_balusters + 1)

        for bi in range(1, n_balusters + 1):
            bx = r_start_x + bi * b_spacing
            add_box((bx, 0, baluster_bottom_z + 0.05), (0.11, 0.11, 0.10))
            res_urn1 = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=12,
                radius1=0.035, radius2=0.065, depth=baluster_space_h * 0.35
            )
            bmesh.ops.translate(bm, vec=(bx, 0, baluster_bottom_z + 0.10 + baluster_space_h * 0.20), verts=res_urn1['verts'])

            res_urn2 = bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=12,
                radius1=0.065, radius2=0.040, depth=baluster_space_h * 0.35
            )
            bmesh.ops.translate(bm, vec=(bx, 0, baluster_bottom_z + 0.10 + baluster_space_h * 0.55), verts=res_urn2['verts'])
            add_box((bx, 0, baluster_bottom_z + baluster_space_h - 0.05), (0.11, 0.11, 0.10))

    return bm.verts[:]


from .architecture_gen import (
    build_fluted_shaft,
    build_classical_capital_and_base,
    build_gothic_clustered_pillar as build_gothic_pillar_arch,
    build_stone_drum_pillar,
    build_solomonic_twisted_pillar
)


def create_procedural_pillar(context, name="Procedural_Pillar", pillar_type="COURTYARD_CLASSIC",
                             height=3.8, radius=0.26, colonnettes=6, flutes=16, entasis=0.08,
                             mat_type="MARBLE", include_railing=True, railing_length=1.6,
                             pedestal_width=0.72, pedestal_height=1.05, seed=0, **kwargs):
    """プロシージャル柱（Pillar）を生成し、メッシュ・マテリアル・モディファイアを構築"""
    mesh = bpy.data.meshes.new(name=f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    bm = bmesh.new()

    if pillar_type == "COURTYARD_CLASSIC":
        build_courtyard_classic_pillar(
            bm, total_height=height, shaft_radius=radius, flute_count=flutes,
            pedestal_width=pedestal_width, pedestal_height=pedestal_height,
            include_railing=include_railing, railing_length=railing_length, seed=seed
        )
    elif pillar_type in ("CLASSIC_FLUTED", "ROMAN_FLUTED"):
        shaft_h = height * 0.83
        build_fluted_shaft(bm, shaft_h, radius, flutes=flutes, entasis=entasis)
        build_classical_capital_and_base(bm, shaft_h, radius)
    elif pillar_type == "GOTHIC_CLUSTERED":
        build_gothic_pillar_arch(bm, height=height, radius=radius, colonnettes=colonnettes)
    elif pillar_type in ("STONE_DRUM", "RUINED_ANCIENT"):
        build_stone_drum_pillar(bm, height=height, radius=radius, drums=7, seed=seed)
    elif pillar_type == "TWISTED_SOLOMONIC":
        build_solomonic_twisted_pillar(bm, height=height, radius=radius)
    elif pillar_type == "SQUARE_MONUMENT":
        build_square_monument_pillar(bm, height=height, radius=radius, seed=seed)
    else:
        build_courtyard_classic_pillar(
            bm, total_height=height, shaft_radius=radius, flute_count=flutes,
            pedestal_width=pedestal_width, pedestal_height=pedestal_height,
            include_railing=include_railing, railing_length=railing_length, seed=seed
        )

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
