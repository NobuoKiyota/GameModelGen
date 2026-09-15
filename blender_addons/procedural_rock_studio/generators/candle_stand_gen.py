import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix


# ==============================================================================
# 🎨 Procedural Shaders for Candle Stand
# ==============================================================================

def get_or_create_material(name):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
    return mat


def create_candle_holder_shader(name="Candle_Holder_Mat", style='FORGED_IRON'):
    """鍛造アイアン、アンティーク真鍮、燻し銀、錆びた鉄のPBRプロシージャルシェーダー"""
    mat = get_or_create_material(name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (600, 0)

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)

    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = 28.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.6
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (0, -150)
    bump.inputs['Distance'].default_value = 0.005
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    if style == 'FORGED_IRON':
        # 鍛造黒鉄（黒皮鉄・わずかに叩き痕のあるアンティークアイアン）
        bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.055, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.88
        bsdf.inputs['Roughness'].default_value = 0.42
        bump.inputs['Strength'].default_value = 0.35
    elif style == 'ANTIQUE_BRASS':
        # アンティーク真鍮（渋いブロンズゴールド）
        bsdf.inputs['Base Color'].default_value = (0.55, 0.40, 0.16, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.92
        bsdf.inputs['Roughness'].default_value = 0.35
        bump.inputs['Strength'].default_value = 0.20
    elif style == 'TARNISHED_SILVER':
        # 燻し銀（くすんだアンティークシルバー）
        bsdf.inputs['Base Color'].default_value = (0.68, 0.68, 0.70, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.95
        bsdf.inputs['Roughness'].default_value = 0.38
        bump.inputs['Strength'].default_value = 0.25
    else:  # RUSTY_IRON
        # 錆びた鉄
        ramp = nodes.new(type='ShaderNodeValToRGB')
        ramp.location = (-150, 100)
        ramp.color_ramp.elements[0].position = 0.35
        ramp.color_ramp.elements[0].color = (0.06, 0.05, 0.05, 1.0)
        ramp.color_ramp.elements[1].position = 0.65
        ramp.color_ramp.elements[1].color = (0.35, 0.14, 0.05, 1.0)
        links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
        bsdf.inputs['Metallic'].default_value = 0.4
        bsdf.inputs['Roughness'].default_value = 0.8
        bump.inputs['Strength'].default_value = 0.65

    return mat


def create_candle_wax_shader(name="Candle_Wax_Mat", color_type='IVORY_BEESWAX'):
    """半透明感（Subsurface Scattering）を持つプロシージャル蝋シェーダー"""
    mat = get_or_create_material(name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (100, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    # 蝋の種類ごとの基本色とSSS設定
    if color_type == 'IVORY_BEESWAX':
        wax_col = (0.92, 0.86, 0.72, 1.0)  # 蜜蝋アイボリー
        sss_rad = (1.0, 0.6, 0.3)
    elif color_type == 'ANTIQUE_WHITE':
        wax_col = (0.95, 0.94, 0.90, 1.0)  # 古色白蝋
        sss_rad = (0.8, 0.7, 0.6)
    elif color_type == 'BLOOD_RED':
        wax_col = (0.45, 0.02, 0.04, 1.0)  # 深紅・ゴシック
        sss_rad = (0.8, 0.1, 0.1)
    else:  # BLACK_WAX
        wax_col = (0.04, 0.04, 0.045, 1.0)  # 漆黒蝋
        sss_rad = (0.2, 0.2, 0.2)

    bsdf.inputs['Base Color'].default_value = wax_col
    bsdf.inputs['Roughness'].default_value = 0.38
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.5
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.5

    # Blender 3.6 / 4.x / 5.x 互換 SSS
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.45
        bsdf.inputs['Subsurface Radius'].default_value = sss_rad
    elif 'Subsurface' in bsdf.inputs:
        bsdf.inputs['Subsurface'].default_value = 0.45
        bsdf.inputs['Subsurface Radius'].default_value = sss_rad
        if 'Subsurface Color' in bsdf.inputs:
            bsdf.inputs['Subsurface Color'].default_value = wax_col

    return mat


def create_candle_wick_shader(name="Candle_Wick_Mat"):
    """焦げた黒い芯マテリアル"""
    mat = get_or_create_material(name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.95
    return mat


def create_candle_flame_shader(name="Candle_Flame_Mat"):
    """青・オレンジ・黄の自然なグラデーション発光炎シェーダー"""
    mat = get_or_create_material(name)
    mat.blend_method = 'BLEND'
    if hasattr(mat, 'shadow_method'):
        mat.shadow_method = 'NONE'

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (700, 0)

    emission = nodes.new(type='ShaderNodeEmission')
    emission.location = (450, 0)
    emission.inputs['Strength'].default_value = 14.0
    links.new(emission.outputs['Emission'], output.inputs['Surface'])

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)

    sep_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
    sep_xyz.location = (-400, 0)
    links.new(tex_coord.outputs['Generated'], sep_xyz.inputs['Vector'])

    # 縦方向 (Z軸: 0=根本, 1=先端) のカラーグラデーション
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.location = (-150, 0)
    ramp.color_ramp.interpolation = 'EASE'

    # 炎のグラデーション: 根本=微青/透明 -> 下部=オレンジ -> 中央〜先端=鮮やかな黄白色
    elem0 = ramp.color_ramp.elements[0]
    elem0.position = 0.05
    elem0.color = (0.1, 0.3, 1.0, 1.0)  # 青い根本

    elem1 = ramp.color_ramp.elements[1]
    elem1.position = 0.35
    elem1.color = (1.0, 0.25, 0.02, 1.0)  # 燃え盛るオレンジ

    elem2 = ramp.color_ramp.elements.new(0.85)
    elem2.color = (1.0, 0.85, 0.30, 1.0)  # 暖色イエロー

    elem3 = ramp.color_ramp.elements.new(1.0)
    elem3.color = (1.0, 1.0, 0.9, 1.0)  # 先端の白熱光

    links.new(sep_xyz.outputs['Z'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], emission.inputs['Color'])

    return mat


# ==============================================================================
# 🕯️ BMesh Procedural Geometry Helpers
# ==============================================================================

def add_lathe_cylinder(bm, center, radius_bottom, radius_top, height, segments=16):
    """段差やテーパー付きの円柱/チューブを生成"""
    v_bot = []
    v_top = []
    cx, cy, cz = center

    for s in range(segments):
        ang = (s / segments) * 2.0 * math.pi
        cos_a, sin_a = math.cos(ang), math.sin(ang)
        v_bot.append(bm.verts.new((cx + radius_bottom * cos_a, cy + radius_bottom * sin_a, cz)))
        v_top.append(bm.verts.new((cx + radius_top * cos_a, cy + radius_top * sin_a, cz + height)))

    faces = []
    for s in range(segments):
        next_s = (s + 1) % segments
        faces.append(bm.faces.new((v_bot[s], v_bot[next_s], v_top[next_s], v_top[s])))

    return v_bot, v_top, faces


def add_curved_tube(bm, points, radii, segments=8):
    """中心線の3D点列と半径リストに沿った滑らかなパイプ/ロッドを生成"""
    if len(points) < 2:
        return [], []

    rings = []
    for i, p in enumerate(points):
        # 接線ベクトルの算出
        if i == 0:
            tangent = (points[1] - p).normalized()
        elif i == len(points) - 1:
            tangent = (p - points[i - 1]).normalized()
        else:
            tangent = ((points[i + 1] - p).normalized() + (p - points[i - 1]).normalized()).normalized()

        if tangent.length < 1e-6:
            tangent = Vector((0, 0, 1))

        # 接線に直交する基底ベクトル
        up = Vector((0, 0, 1)) if abs(tangent.z) < 0.99 else Vector((1, 0, 0))
        normal = tangent.cross(up).normalized()
        binormal = tangent.cross(normal).normalized()

        r = radii[i] if isinstance(radii, list) else radii
        ring = []
        for s in range(segments):
            ang = (s / segments) * 2.0 * math.pi
            offset = (normal * math.cos(ang) + binormal * math.sin(ang)) * r
            v = bm.verts.new(p + offset)
            ring.append(v)
        rings.append(ring)

    faces = []
    for i in range(len(rings) - 1):
        r1, r2 = rings[i], rings[i + 1]
        for s in range(segments):
            next_s = (s + 1) % segments
            faces.append(bm.faces.new((r1[s], r1[next_s], r2[next_s], r2[s])))

    return rings, faces


def create_drip_pan_cup(bm, center=Vector((0, 0, 0)), pan_radius=0.065, cup_radius=0.022, cup_height=0.028, segments=20):
    """キャンドル受け皿（Bobeche）とソケット金具を生成"""
    cx, cy, cz = center

    # 1. ソケットカップ（蝋燭を差し込む筒）
    _, v_cup_top, faces_cup = add_lathe_cylinder(bm, (cx, cy, cz), cup_radius * 1.15, cup_radius * 1.25, cup_height, segments)

    # 2. 受け皿（花弁/段差リム形状のボウル）
    profile = [
        (cup_radius * 1.2, cz + cup_height * 0.3),
        (pan_radius * 0.6, cz + cup_height * 0.15),
        (pan_radius * 0.95, cz + cup_height * 0.5),
        (pan_radius, cz + cup_height * 0.8),
        (pan_radius * 0.92, cz + cup_height * 0.75)
    ]
    rings = []
    for r, z in profile:
        ring = []
        for s in range(segments):
            ang = (s / segments) * 2.0 * math.pi
            v = bm.verts.new((cx + r * math.cos(ang), cy + r * math.sin(ang), z))
            ring.append(v)
        rings.append(ring)

    faces_pan = []
    for i in range(len(rings) - 1):
        r1, r2 = rings[i], rings[i + 1]
        for s in range(segments):
            next_s = (s + 1) % segments
            faces_pan.append(bm.faces.new((r1[s], r1[next_s], r2[next_s], r2[s])))

    all_faces = faces_cup + faces_pan
    return all_faces


def create_candle_geometry(bm, base_pos=Vector((0, 0, 0)), height=0.18, radius=0.018, melt_level=0.5, segments=16, seed=0):
    """蝋燭本体、蝋だれ（Wax Drips）、芯、炎メッシュを生成"""
    rng = random.Random(seed)
    bx, by, bz = base_pos

    # 蝋燭の高さ方向リング
    tiers = 8
    rings = []
    for t in range(tiers + 1):
        tz = bz + (t / tiers) * height
        r_tier = radius
        if t == tiers:
            r_tier *= 0.88  # 天頂部のわずかな丸まり

        ring = []
        for s in range(segments):
            ang = (s / segments) * 2.0 * math.pi
            noise_r = r_tier + rng.uniform(-0.0012, 0.0012) * melt_level
            vx = bx + noise_r * math.cos(ang)
            vy = by + noise_r * math.sin(ang)
            v = bm.verts.new((vx, vy, tz))
            ring.append(v)
        rings.append(ring)

    faces_candle = []
    for t in range(tiers):
        r1, r2 = rings[t], rings[t + 1]
        for s in range(segments):
            next_s = (s + 1) % segments
            faces_candle.append(bm.faces.new((r1[s], r1[next_s], r2[next_s], r2[s])))

    # 天頂部の受け面・くぼみ
    v_top_center = bm.verts.new((bx, by, bz + height - 0.004))
    r_top = rings[-1]
    for s in range(segments):
        next_s = (s + 1) % segments
        faces_candle.append(bm.faces.new((v_top_center, r_top[next_s], r_top[s])))

    # 底面
    v_bot_center = bm.verts.new((bx, by, bz))
    r_bot = rings[0]
    for s in range(segments):
        next_s = (s + 1) % segments
        faces_candle.append(bm.faces.new((v_bot_center, r_bot[s], r_bot[next_s])))

    # 蝋だれ（Wax Drips）の立体造形
    if melt_level > 0.15:
        drip_count = rng.randint(2, 5)
        for _ in range(drip_count):
            drip_ang = rng.uniform(0, 2 * math.pi)
            drip_len = rng.uniform(height * 0.25, height * 0.75) * melt_level
            drip_rad = rng.uniform(0.0025, 0.005)

            cos_d, sin_d = math.cos(drip_ang), math.sin(drip_ang)
            p_start = Vector((bx + radius * 0.95 * cos_d, by + radius * 0.95 * sin_d, bz + height - 0.005))
            p_mid = Vector((bx + (radius + drip_rad * 0.8) * cos_d, by + (radius + drip_rad * 0.8) * sin_d, bz + height - drip_len * 0.6))
            p_bulb = Vector((bx + (radius + drip_rad * 1.3) * cos_d, by + (radius + drip_rad * 1.3) * sin_d, bz + height - drip_len))

            _, d_faces = add_curved_tube(bm, [p_start, p_mid, p_bulb], [drip_rad * 0.5, drip_rad, drip_rad * 1.4], segments=6)
            faces_candle.extend(d_faces)

    # 芯（Charred Wick）
    wick_base = Vector((bx, by, bz + height - 0.002))
    wick_tip = wick_base + Vector((rng.uniform(-0.002, 0.002), rng.uniform(-0.002, 0.002), 0.016))
    _, faces_wick = add_curved_tube(bm, [wick_base, (wick_base + wick_tip) * 0.5, wick_tip], 0.0012, segments=6)

    # 炎メッシュ（涙滴ティアドロップ形状）
    flame_base_z = wick_tip.z - 0.003
    flame_height = 0.038
    flame_rad = 0.009
    flame_prof = [
        (0.002, flame_base_z),
        (flame_rad, flame_base_z + flame_height * 0.35),
        (flame_rad * 0.7, flame_base_z + flame_height * 0.65),
        (0.0005, flame_base_z + flame_height)
    ]
    f_rings = []
    for r, z in flame_prof:
        f_ring = []
        for s in range(12):
            ang = (s / 12) * 2.0 * math.pi
            v = bm.verts.new((wick_tip.x + r * math.cos(ang), wick_tip.y + r * math.sin(ang), z))
            f_ring.append(v)
        f_rings.append(f_ring)

    faces_flame = []
    for i in range(len(f_rings) - 1):
        r1, r2 = f_rings[i], f_rings[i + 1]
        for s in range(12):
            next_s = (s + 1) % 12
            faces_flame.append(bm.faces.new((r1[s], r1[next_s], r2[next_s], r2[s])))

    flame_light_pos = Vector((wick_tip.x, wick_tip.y, flame_base_z + flame_height * 0.5))
    return faces_candle, faces_wick, faces_flame, flame_light_pos


# ==============================================================================
# 🏰 4 Major Architectural Generator Functions
# ==============================================================================

def build_hanging_chandelier_mesh(bm, radius=0.65, candle_count=6, rod_count=3, suspension_height=0.85, melt_level=0.5, seed=0):
    """
    【スタイル1】吊り下げ式ホイール・シャンデリア（画像準拠）
    鍛造アイアンの円形外枠、放射状スポーク、吊り下げロッド/チェーン、均等配置キャンドル
    """
    rng = random.Random(seed)
    metal_faces = []
    candle_faces = []
    wick_faces = []
    flame_faces = []
    light_positions = []

    # 1. 外周の円形アイアンリング（Hoop / Wheel）
    rim_segments = 48
    rim_points = []
    rim_thickness = 0.020
    for s in range(rim_segments):
        ang = (s / rim_segments) * 2.0 * math.pi
        rim_points.append(Vector((radius * math.cos(ang), radius * math.sin(ang), 0.0)))
    rim_points.append(rim_points[0])  # ループ
    _, f_rim = add_curved_tube(bm, rim_points, rim_thickness, segments=8)
    metal_faces.extend(f_rim)

    # 2. 内側の補強スポーク（十字または放射状）
    spoke_count = rod_count
    for sp in range(spoke_count):
        ang = (sp / spoke_count) * 2.0 * math.pi
        p_rim = Vector((radius * math.cos(ang), radius * math.sin(ang), 0.0))
        p_center = Vector((0, 0, 0))
        _, f_spk = add_curved_tube(bm, [p_center, p_rim], rim_thickness * 0.75, segments=6)
        metal_faces.extend(f_spk)

    # 3. 上部吊り下げ部（天井金具 ＆ 吊り下げロッド）
    top_apex = Vector((0, 0, suspension_height))
    _, f_top = add_curved_tube(bm, [top_apex - Vector((0, 0, 0.06)), top_apex, top_apex + Vector((0, 0, 0.05))], rim_thickness * 1.4, segments=8)
    metal_faces.extend(f_top)

    for r in range(rod_count):
        ang = (r / rod_count) * 2.0 * math.pi
        p_mount = Vector((radius * 0.9 * math.cos(ang), radius * 0.9 * math.sin(ang), 0.02))
        _, f_rod = add_curved_tube(bm, [p_mount, top_apex], rim_thickness * 0.42, segments=6)
        metal_faces.extend(f_rod)

    # 4. 円周上のキャンドル受け皿 & キャンドル
    for c in range(candle_count):
        ang = (c / candle_count) * 2.0 * math.pi
        c_pos = Vector((radius * math.cos(ang), radius * math.sin(ang), rim_thickness))

        # 受け皿
        f_pan = create_drip_pan_cup(bm, center=c_pos, pan_radius=0.06, cup_radius=0.020, cup_height=0.026)
        metal_faces.extend(f_pan)

        # 蝋燭
        c_h = rng.uniform(0.14, 0.22)
        c_seed = seed + c * 107
        f_cnd, f_wck, f_flm, l_pos = create_candle_geometry(
            bm,
            base_pos=c_pos + Vector((0, 0, 0.026)),
            height=c_h,
            radius=0.018,
            melt_level=melt_level,
            seed=c_seed
        )
        candle_faces.extend(f_cnd)
        wick_faces.extend(f_wck)
        flame_faces.extend(f_flm)
        light_positions.append(l_pos)

    # 5. 中央上段のセンターキャンドル（アクセント）
    center_stem_h = 0.16
    _, f_c_stem = add_curved_tube(bm, [Vector((0, 0, 0)), Vector((0, 0, center_stem_h))], rim_thickness * 1.1, segments=8)
    metal_faces.extend(f_c_stem)

    c_center_pos = Vector((0, 0, center_stem_h))
    f_pan_c = create_drip_pan_cup(bm, center=c_center_pos, pan_radius=0.062, cup_radius=0.022, cup_height=0.028)
    metal_faces.extend(f_pan_c)

    f_cnd_c, f_wck_c, f_flm_c, l_pos_c = create_candle_geometry(
        bm,
        base_pos=c_center_pos + Vector((0, 0, 0.028)),
        height=0.20,
        radius=0.019,
        melt_level=melt_level,
        seed=seed + 999
    )
    candle_faces.extend(f_cnd_c)
    wick_faces.extend(f_wck_c)
    flame_faces.extend(f_flm_c)
    light_positions.append(l_pos_c)

    return metal_faces, candle_faces, wick_faces, flame_faces, light_positions


def build_table_candelabra_mesh(bm, height=0.45, arm_count=4, spread=0.20, melt_level=0.5, seed=0):
    """
    【スタイル2】卓上枝分かれ多灯燭台（Tabletop Candelabra）
    クラシックろくろ挽き台座、S字湾曲アーム、中央＋周囲のキャンドル
    """
    rng = random.Random(seed)
    metal_faces = []
    candle_faces = []
    wick_faces = []
    flame_faces = []
    light_positions = []

    # 1. 段差付き装飾台座（Base）
    base_profile = [
        (0.10, 0.0),
        (0.09, 0.02),
        (0.07, 0.035),
        (0.045, 0.07),
        (0.03, 0.12),
        (0.038, 0.16),
        (0.024, 0.22),
        (0.032, 0.28),
        (0.020, height * 0.85)
    ]
    rings = []
    for r, z in base_profile:
        ring = []
        for s in range(24):
            ang = (s / 24) * 2.0 * math.pi
            ring.append(bm.verts.new((r * math.cos(ang), r * math.sin(ang), z)))
        rings.append(ring)

    for i in range(len(rings) - 1):
        r1, r2 = rings[i], rings[i + 1]
        for s in range(24):
            next_s = (s + 1) % 24
            metal_faces.append(bm.faces.new((r1[s], r1[next_s], r2[next_s], r2[s])))

    # 台座底面
    v_bot = bm.verts.new((0, 0, 0))
    for s in range(24):
        next_s = (s + 1) % 24
        metal_faces.append(bm.faces.new((v_bot, rings[0][s], rings[0][next_s])))

    # 2. 中央トップのキャンドル
    center_top = Vector((0, 0, height * 0.85))
    f_pan_top = create_drip_pan_cup(bm, center=center_top, pan_radius=0.052, cup_radius=0.018, cup_height=0.024)
    metal_faces.extend(f_pan_top)

    f_cnd_c, f_wck_c, f_flm_c, l_pos_c = create_candle_geometry(
        bm,
        base_pos=center_top + Vector((0, 0, 0.024)),
        height=0.16,
        radius=0.016,
        melt_level=melt_level,
        seed=seed + 101
    )
    candle_faces.extend(f_cnd_c)
    wick_faces.extend(f_wck_c)
    flame_faces.extend(f_flm_c)
    light_positions.append(l_pos_c)

    # 3. 湾曲した枝分かれアーム（S-scroll Arms）
    arm_junction_z = height * 0.52
    arm_tip_z = height * 0.72
    for a in range(arm_count):
        ang = (a / arm_count) * 2.0 * math.pi
        cos_a, sin_a = math.cos(ang), math.sin(ang)

        p0 = Vector((0.02 * cos_a, 0.02 * sin_a, arm_junction_z))
        p1 = Vector((spread * 0.45 * cos_a, spread * 0.45 * sin_a, arm_junction_z - 0.06))
        p2 = Vector((spread * 0.9 * cos_a, spread * 0.9 * sin_a, arm_junction_z + 0.04))
        p3 = Vector((spread * cos_a, spread * sin_a, arm_tip_z))

        _, f_arm = add_curved_tube(bm, [p0, p1, p2, p3], 0.009, segments=8)
        metal_faces.extend(f_arm)

        f_pan_arm = create_drip_pan_cup(bm, center=p3, pan_radius=0.046, cup_radius=0.016, cup_height=0.022)
        metal_faces.extend(f_pan_arm)

        c_h = rng.uniform(0.12, 0.18)
        f_cnd_a, f_wck_a, f_flm_a, l_pos_a = create_candle_geometry(
            bm,
            base_pos=p3 + Vector((0, 0, 0.022)),
            height=c_h,
            radius=0.015,
            melt_level=melt_level,
            seed=seed + (a + 1) * 73
        )
        candle_faces.extend(f_cnd_a)
        wick_faces.extend(f_wck_a)
        flame_faces.extend(f_flm_a)
        light_positions.append(l_pos_a)

    return metal_faces, candle_faces, wick_faces, flame_faces, light_positions


def build_chamberstick_mesh(bm, saucer_radius=0.09, height=0.07, melt_level=0.5, seed=0):
    """
    【スタイル3】手持ち受け皿付き単灯燭台（Chamberstick）
    洋館探索・ホラー定番のリングハンドル付き1灯キャンドルホルダー
    """
    metal_faces = []
    candle_faces = []
    wick_faces = []
    flame_faces = []
    light_positions = []

    # 1. 幅広の蝋受け皿（Saucer）
    saucer_prof = [
        (0.001, 0.0),
        (saucer_radius * 0.7, 0.003),
        (saucer_radius * 0.9, 0.014),
        (saucer_radius, 0.022),
        (saucer_radius * 0.95, 0.020)
    ]
    rings = []
    for r, z in saucer_prof:
        ring = []
        for s in range(24):
            ang = (s / 24) * 2.0 * math.pi
            ring.append(bm.verts.new((r * math.cos(ang), r * math.sin(ang), z)))
        rings.append(ring)

    for i in range(len(rings) - 1):
        r1, r2 = rings[i], rings[i + 1]
        for s in range(24):
            next_s = (s + 1) % 24
            metal_faces.append(bm.faces.new((r1[s], r1[next_s], r2[next_s], r2[s])))

    # 2. 中央のソケットカップ（Socket Column）
    f_cup = create_drip_pan_cup(bm, center=Vector((0, 0, 0.004)), pan_radius=0.036, cup_radius=0.018, cup_height=0.045)
    metal_faces.extend(f_cup)

    # 3. 指を通すリング取手（Ring Handle）
    handle_center = Vector((saucer_radius * 0.80, 0, 0.036))
    handle_rad = 0.020
    h_points = []
    for s in range(16):
        ang = (s / 16) * 2.0 * math.pi
        h_points.append(handle_center + Vector((handle_rad * math.cos(ang), 0, handle_rad * math.sin(ang))))
    h_points.append(h_points[0])
    _, f_handle = add_curved_tube(bm, h_points, 0.0042, segments=6)
    metal_faces.extend(f_handle)

    # 4. キャンドル本体
    f_cnd, f_wck, f_flm, l_pos = create_candle_geometry(
        bm,
        base_pos=Vector((0, 0, 0.049)),
        height=0.15,
        radius=0.016,
        melt_level=melt_level,
        seed=seed
    )
    candle_faces.extend(f_cnd)
    wick_faces.extend(f_wck)
    flame_faces.extend(f_flm)
    light_positions.append(l_pos)

    return metal_faces, candle_faces, wick_faces, flame_faces, light_positions


def build_wall_sconce_mesh(bm, arm_length=0.22, height=0.30, candle_count=1, melt_level=0.5, seed=0):
    """
    【スタイル4】壁掛けブラケット燭台（Wall Sconce）
    壁面取り付けプレート、前方へ突き出す優美な湾曲アーム、受け皿とキャンドル
    """
    rng = random.Random(seed)
    metal_faces = []
    candle_faces = []
    wick_faces = []
    flame_faces = []
    light_positions = []

    # 1. 壁面マウントプレート（菱形: Y=0が壁面）
    plate_prof = [
        Vector((0, 0.005, height * 0.5)),
        Vector((0.045, 0.005, 0.0)),
        Vector((0, 0.005, -height * 0.5)),
        Vector((-0.045, 0.005, 0.0))
    ]
    v_plate_front = [bm.verts.new(p - Vector((0, 0.008, 0))) for p in plate_prof]
    v_plate_back = [bm.verts.new(p) for p in plate_prof]

    # 前面
    metal_faces.append(bm.faces.new((v_plate_front[0], v_plate_front[1], v_plate_front[2], v_plate_front[3])))
    # 側面
    for s in range(4):
        ns = (s + 1) % 4
        metal_faces.append(bm.faces.new((v_plate_back[s], v_plate_back[ns], v_plate_front[ns], v_plate_front[s])))

    # 2. 前方へ伸びるスクロールアーム
    if candle_count <= 1:
        p0 = Vector((0, -0.008, -0.05))
        p1 = Vector((0, -arm_length * 0.45, -0.12))
        p2 = Vector((0, -arm_length * 0.9, -0.02))
        p3 = Vector((0, -arm_length, 0.06))

        _, f_arm = add_curved_tube(bm, [p0, p1, p2, p3], 0.008, segments=8)
        metal_faces.extend(f_arm)

        f_pan = create_drip_pan_cup(bm, center=p3, pan_radius=0.052, cup_radius=0.017, cup_height=0.024)
        metal_faces.extend(f_pan)

        f_cnd, f_wck, f_flm, l_pos = create_candle_geometry(
            bm,
            base_pos=p3 + Vector((0, 0, 0.024)),
            height=0.17,
            radius=0.016,
            melt_level=melt_level,
            seed=seed
        )
        candle_faces.extend(f_cnd)
        wick_faces.extend(f_wck)
        flame_faces.extend(f_flm)
        light_positions.append(l_pos)
    else:  # 2灯
        for idx, sign in enumerate([-1, 1]):
            p0 = Vector((0, -0.008, -0.04))
            p1 = Vector((sign * 0.06, -arm_length * 0.5, -0.08))
            p2 = Vector((sign * 0.12, -arm_length * 0.85, 0.02))
            p3 = Vector((sign * 0.14, -arm_length, 0.08))

            _, f_arm = add_curved_tube(bm, [p0, p1, p2, p3], 0.0075, segments=8)
            metal_faces.extend(f_arm)

            f_pan = create_drip_pan_cup(bm, center=p3, pan_radius=0.048, cup_radius=0.016, cup_height=0.022)
            metal_faces.extend(f_pan)

            f_cnd, f_wck, f_flm, l_pos = create_candle_geometry(
                bm,
                base_pos=p3 + Vector((0, 0, 0.022)),
                height=rng.uniform(0.14, 0.19),
                radius=0.015,
                melt_level=melt_level,
                seed=seed + idx * 83
            )
            candle_faces.extend(f_cnd)
            wick_faces.extend(f_wck)
            flame_faces.extend(f_flm)
            light_positions.append(l_pos)

    return metal_faces, candle_faces, wick_faces, flame_faces, light_positions


# ==============================================================================
# 🚀 Master Generator Entry Point
# ==============================================================================

def generate_candle_stand(
    context,
    name="Antique_Candle_Stand",
    style='HANGING_CHANDELIER',
    candle_count=6,
    melt_level=0.5,
    has_flame=True,
    add_point_lights=True,
    holder_material='FORGED_IRON',
    wax_material='IVORY_BEESWAX',
    combine=True,
    target_obj=None,
    seed=42
):
    """
    アンティーク蝋燭立て・シャンデリアのプロシージャル生成メインエントリーポイント
    """
    # 既存ターゲットまたは古いオブジェクトの削除
    if target_obj:
        try:
            if hasattr(target_obj, "name") and target_obj.name in context.collection.objects:
                for c in list(getattr(target_obj, "children", [])):
                    try:
                        bpy.data.objects.remove(c, do_unlink=True)
                    except Exception:
                        pass
                bpy.data.objects.remove(target_obj, do_unlink=True)
        except (ReferenceError, Exception):
            pass

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm = bmesh.new()

    # スタイル別ジオメトリ構築
    if style == 'HANGING_CHANDELIER':
        # 吊り下げホイール・シャンデリア
        m_faces, c_faces, w_faces, f_faces, light_positions = build_hanging_chandelier_mesh(
            bm,
            radius=0.65,
            candle_count=candle_count if candle_count >= 4 else 6,
            rod_count=3 if candle_count % 3 == 0 else 4,
            suspension_height=0.85,
            melt_level=melt_level,
            seed=seed
        )
    elif style == 'TABLE_CANDELABRA':
        # 卓上多灯燭台
        m_faces, c_faces, w_faces, f_faces, light_positions = build_table_candelabra_mesh(
            bm,
            height=0.42,
            arm_count=candle_count - 1 if candle_count > 1 else 4,
            spread=0.20,
            melt_level=melt_level,
            seed=seed
        )
    elif style == 'CHAMBERSTICK':
        # 手持ち受け皿付き単灯燭台
        m_faces, c_faces, w_faces, f_faces, light_positions = build_chamberstick_mesh(
            bm,
            saucer_radius=0.09,
            height=0.07,
            melt_level=melt_level,
            seed=seed
        )
    else:  # WALL_SCONCE
        # 壁掛けブラケット燭台
        m_faces, c_faces, w_faces, f_faces, light_positions = build_wall_sconce_mesh(
            bm,
            arm_length=0.22,
            height=0.30,
            candle_count=1 if candle_count <= 1 else 2,
            melt_level=melt_level,
            seed=seed
        )

    # 炎（Flame）を非表示にする場合は炎面を削除
    if not has_flame:
        bmesh.ops.delete(bm, geom=f_faces, context='FACES')
        f_faces = []

    # 法線の再計算＆スムーズシェーディング
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0003)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for face in bm.faces:
        face.smooth = True

    # マテリアルスロットの割り当て
    mat_metal = create_candle_holder_shader(f"{name}_Metal_{holder_material}", style=holder_material)
    mat_wax = create_candle_wax_shader(f"{name}_Wax_{wax_material}", color_type=wax_material)
    mat_wick = create_candle_wick_shader(f"{name}_Wick")
    mat_flame = create_candle_flame_shader(f"{name}_Flame")

    for f in m_faces:
        if f.is_valid:
            f.material_index = 0
    for f in c_faces:
        if f.is_valid:
            f.material_index = 1
    for f in w_faces:
        if f.is_valid:
            f.material_index = 2
    for f in f_faces:
        if f.is_valid:
            f.material_index = 3

    bm.to_mesh(mesh)
    bm.free()

    # メッシュオブジェクト作成
    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    # マテリアル登録
    obj.data.materials.append(mat_metal)
    obj.data.materials.append(mat_wax)
    obj.data.materials.append(mat_wick)
    if has_flame:
        obj.data.materials.append(mat_flame)

    # UV展開 (Smart Project)
    context.view_layer.objects.active = obj
    obj.select_set(True)
    try:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(island_margin=0.02)
        bpy.ops.object.mode_set(mode='OBJECT')
    except Exception:
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

    # 実体ライト（Point Light）の配置
    if has_flame and add_point_lights:
        for idx, l_pos in enumerate(light_positions):
            light_data = bpy.data.lights.new(name=f"{name}_PointLight_{idx+1}", type='POINT')
            light_data.energy = 22.0
            light_data.color = (1.0, 0.68, 0.32)
            light_data.shadow_soft_size = 0.04

            light_obj = bpy.data.objects.new(f"{name}_PointLight_{idx+1}", light_data)
            light_obj.location = l_pos
            context.collection.objects.link(light_obj)
            light_obj.parent = obj

    return obj
