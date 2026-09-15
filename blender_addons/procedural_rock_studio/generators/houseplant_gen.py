import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler


# ==============================================================================
# 🎨 PBR Shaders for Houseplant (Leaves, Pot, Soil, Macrame)
# ==============================================================================

def get_or_create_material(name):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
    return mat


def create_houseplant_leaf_shader(name="Houseplant_Leaf_Mat", color_type='VIBRANT_GREEN', variegated=False):
    """半透明透過光 (Subsurface Scattering) とクチクラ光沢を持つプロシージャル葉シェーダー"""
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
    tex_coord.location = (-700, 0)

    # 微細な葉脈・表面凹凸ノイズ
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-450, -150)
    noise.inputs['Scale'].default_value = 55.0
    noise.inputs['Detail'].default_value = 5.0
    noise.inputs['Roughness'].default_value = 0.50
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (50, -150)
    bump.inputs['Distance'].default_value = 0.002
    bump.inputs['Strength'].default_value = 0.20
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    # 葉の色とSSS設定
    if color_type == 'VIBRANT_GREEN':
        base_green = (0.12, 0.48, 0.06, 1.0)  # 鮮やかな若葉
        sss_color = (0.28, 0.65, 0.08)
    elif color_type == 'DEEP_FOREST':
        base_green = (0.05, 0.28, 0.04, 1.0)  # 落ち着いた深緑
        sss_color = (0.15, 0.45, 0.06)
    else:  # JADE_OLIVE
        base_green = (0.18, 0.38, 0.12, 1.0)  # オリーブ・翡翠
        sss_color = (0.30, 0.52, 0.14)

    if variegated:
        # 斑入り（外周がクリーム黄色のサンスベリア・ポトス）
        ramp = nodes.new(type='ShaderNodeValToRGB')
        ramp.location = (-150, 100)
        ramp.color_ramp.elements[0].position = 0.25
        ramp.color_ramp.elements[0].color = base_green
        ramp.color_ramp.elements[1].position = 0.85
        ramp.color_ramp.elements[1].color = (0.88, 0.82, 0.40, 1.0)
        links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = base_green

    bsdf.inputs['Roughness'].default_value = 0.26
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.55
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.55

    # Blender 3.6 / 4.x / 5.x 互換 SSS
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.45
        bsdf.inputs['Subsurface Radius'].default_value = sss_color
    elif 'Subsurface' in bsdf.inputs:
        bsdf.inputs['Subsurface'].default_value = 0.45
        bsdf.inputs['Subsurface Radius'].default_value = sss_color
        if 'Subsurface Color' in bsdf.inputs:
            bsdf.inputs['Subsurface Color'].default_value = base_green

    return mat


def create_houseplant_stem_shader(name="Houseplant_Stem_Mat"):
    """茎・葉柄・つる用のフレッシュグリーンシェーダー"""
    mat = get_or_create_material(name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (100, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    bsdf.inputs['Base Color'].default_value = (0.16, 0.42, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.40
    return mat


def create_houseplant_pot_shader(name="Houseplant_Pot_Mat", pot_material='TERRACOTTA'):
    """植木鉢用プロシージャルシェーダー（テラコッタ、石材、釉薬陶器、ブロンズ）"""
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
    tex_coord.location = (-700, 0)
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-450, -100)
    noise.inputs['Scale'].default_value = 35.0
    noise.inputs['Detail'].default_value = 6.0
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (50, -100)
    bump.inputs['Distance'].default_value = 0.005
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    if pot_material == 'TERRACOTTA':
        bsdf.inputs['Base Color'].default_value = (0.68, 0.36, 0.22, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.75
        bsdf.inputs['Metallic'].default_value = 0.0
        bump.inputs['Strength'].default_value = 0.35
    elif pot_material == 'ANTIQUE_STONE':
        ramp = nodes.new(type='ShaderNodeValToRGB')
        ramp.location = (-150, 100)
        ramp.color_ramp.elements[0].position = 0.3
        ramp.color_ramp.elements[0].color = (0.55, 0.52, 0.48, 1.0)
        ramp.color_ramp.elements[1].position = 0.7
        ramp.color_ramp.elements[1].color = (0.75, 0.73, 0.68, 1.0)
        links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
        bsdf.inputs['Roughness'].default_value = 0.60
        bsdf.inputs['Metallic'].default_value = 0.0
        bump.inputs['Strength'].default_value = 0.55
    elif pot_material == 'GLAZED_CERAMIC':
        bsdf.inputs['Base Color'].default_value = (0.92, 0.92, 0.90, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.12
        bsdf.inputs['Metallic'].default_value = 0.02
        bump.inputs['Strength'].default_value = 0.05
    else:  # AGED_BRONZE
        bsdf.inputs['Base Color'].default_value = (0.35, 0.32, 0.22, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.42
        bsdf.inputs['Metallic'].default_value = 0.85
        bump.inputs['Strength'].default_value = 0.35

    return mat


def create_houseplant_soil_shader(name="Houseplant_Soil_Mat"):
    """黒褐色・有機的粒状感を持つ培養土シェーダー"""
    mat = get_or_create_material(name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (100, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-500, 0)
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-300, 0)
    noise.inputs['Scale'].default_value = 80.0
    noise.inputs['Detail'].default_value = 8.0
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (-50, -100)
    bump.inputs['Distance'].default_value = 0.005
    bump.inputs['Strength'].default_value = 0.85
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    bsdf.inputs['Base Color'].default_value = (0.08, 0.055, 0.04, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.92
    return mat


def create_macrame_rope_shader(name="Houseplant_Macrame_Mat"):
    """ナチュラル麻縄・コットンロープシェーダー"""
    mat = get_or_create_material(name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (100, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    bsdf.inputs['Base Color'].default_value = (0.84, 0.79, 0.68, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.82
    return mat


# ==============================================================================
# 🪴 BMesh Geometry Helpers (Pots, Soil, Macrame, Tubes, Knots)
# ==============================================================================

def add_curved_tube(bm, points, radii, segments=8):
    """中心線の3D点列と半径リストに沿った滑らかなパイプ/茎/ロープを生成（スムーズシェーディング付）"""
    if len(points) < 2:
        return [], []

    rings = []
    for i, p in enumerate(points):
        if i == 0:
            tangent = (points[1] - p).normalized()
        elif i == len(points) - 1:
            tangent = (p - points[i - 1]).normalized()
        else:
            tangent = ((points[i + 1] - p).normalized() + (p - points[i - 1]).normalized()).normalized()

        if tangent.length < 1e-6:
            tangent = Vector((0, 0, 1))

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
            f = bm.faces.new((r1[s], r1[next_s], r2[next_s], r2[s]))
            f.smooth = True
            faces.append(f)

    return rings, faces


def add_small_knot_sphere(bm, center, radius=0.007, segments_u=8, segments_v=6):
    """マクラメ編み交差点用の立体結び目（ノット）球メッシュ"""
    faces = []
    rings = []
    for v in range(1, segments_v):
        theta = (v / float(segments_v)) * math.pi
        z = radius * math.cos(theta)
        r = radius * math.sin(theta)
        ring = []
        for u in range(segments_u):
            phi = (u / float(segments_u)) * 2.0 * math.pi
            ring.append(bm.verts.new((
                center.x + r * math.cos(phi),
                center.y + r * math.sin(phi),
                center.z + z
            )))
        rings.append(ring)

    v_top = bm.verts.new((center.x, center.y, center.z + radius))
    v_bot = bm.verts.new((center.x, center.y, center.z - radius))

    for u in range(segments_u):
        nu = (u + 1) % segments_u
        f_top = bm.faces.new((v_top, rings[0][nu], rings[0][u]))
        f_top.smooth = True
        faces.append(f_top)
        f_bot = bm.faces.new((v_bot, rings[-1][u], rings[-1][nu]))
        f_bot.smooth = True
        faces.append(f_bot)

    for v in range(len(rings) - 1):
        r1, r2 = rings[v], rings[v + 1]
        for u in range(segments_u):
            nu = (u + 1) % segments_u
            f = bm.faces.new((r1[u], r1[nu], r2[nu], r2[u]))
            f.smooth = True
            faces.append(f)

    return faces


def build_pot_lathe(bm, profile_points, segments=28, center_z=0.0):
    """(radius, z) の回転体プロファイルから植木鉢を生成"""
    rings = []
    for r, z in profile_points:
        ring = []
        for s in range(segments):
            ang = (s / segments) * 2.0 * math.pi
            ring.append(bm.verts.new((r * math.cos(ang), r * math.sin(ang), z + center_z)))
        rings.append(ring)

    faces = []
    for i in range(len(rings) - 1):
        r1, r2 = rings[i], rings[i + 1]
        for s in range(segments):
            next_s = (s + 1) % segments
            f = bm.faces.new((r1[s], r1[next_s], r2[next_s], r2[s]))
            f.smooth = True
            faces.append(f)

    # 底面閉鎖
    if profile_points[0][0] > 0.001:
        v_bot = bm.verts.new((0, 0, profile_points[0][1] + center_z))
        for s in range(segments):
            next_s = (s + 1) % segments
            f = bm.faces.new((v_bot, rings[0][s], rings[0][next_s]))
            f.smooth = True
            faces.append(f)

    return faces


def build_soil_mound(bm, radius=0.18, rim_z=0.25, segments=24):
    """鉢の上部を覆うリアルな培養土マウンド"""
    v_center = bm.verts.new((0, 0, rim_z + 0.012))
    ring_inner = []
    ring_outer = []
    for s in range(segments):
        ang = (s / segments) * 2.0 * math.pi
        cos_a, sin_a = math.cos(ang), math.sin(ang)
        ring_inner.append(bm.verts.new((radius * 0.5 * cos_a, radius * 0.5 * sin_a, rim_z + 0.008)))
        ring_outer.append(bm.verts.new((radius * 0.98 * cos_a, radius * 0.98 * sin_a, rim_z)))

    faces = []
    for s in range(segments):
        ns = (s + 1) % segments
        f1 = bm.faces.new((v_center, ring_inner[s], ring_inner[ns]))
        f2 = bm.faces.new((ring_inner[s], ring_outer[s], ring_outer[ns], ring_inner[ns]))
        f1.smooth = True
        f2.smooth = True
        faces.extend([f1, f2])

    return faces


# ==============================================================================
# 🍃 多彩な葉形状パターン生成エンジン (HEART, IVY_LOBED, PEARLS, FERN, COIN, FIDDLE)
# ==============================================================================

def build_organic_ivy_leaf(
    bm,
    base_pos,
    out_dir,
    length=0.065,
    width=0.052,
    curl=0.35,
    v_cup=0.45,
    petiole_len=0.022,
    rot_euler=None,
    shape_type='HEART'
):
    """
    【有機的葉形状ビルダー】
    - shape_type:
      'HEART'     : 滑らかなハート型心臓葉（ポトス）
      'IVY_LOBED' : 3裂のシャープな角が飛び出すクラシック洋館ツタ葉（イングリッシュアイビー）
      'COIN'      : ほぼ真円の平たい丸コイン葉（ユーカリ・ポポラス）
      'FIDDLE'    : 基部がくびれ先端が広がり縁が波打つバイオリン大葉（カシワバ）
    """
    stem_faces = []
    leaf_faces = []

    out_norm = out_dir.normalized()
    up_norm = Vector((0, 0, 1))

    # 1. 葉柄（ペティオール）の生成
    p_p0 = base_pos
    p_p1 = base_pos + out_norm * (petiole_len * 0.5) + Vector((0, 0, petiole_len * 0.35))
    p_p2 = base_pos + out_norm * petiole_len + Vector((0, 0, petiole_len * 0.20))
    _, f_petiole = add_curved_tube(bm, [p_p0, p_p1, p_p2], 0.0016, segments=6)
    stem_faces.extend(f_petiole)

    # 2. 葉身（ブレード）の生成
    leaf_origin = p_p2
    rot_mat = rot_euler.to_matrix().to_4x4() if rot_euler else Matrix.Identity(4)

    def get_width_profile(t):
        if shape_type == 'IVY_LOBED':
            # 3裂イングリッシュアイビー（基部 -> 左右側裂片の鋭い角 -> 切れ込みくびれ -> 中央長裂片）
            if t <= 0.18:
                return 0.35 + 0.55 * math.sin((t / 0.18) * math.pi * 0.5)
            elif t <= 0.42:
                st = (t - 0.18) / 0.24
                return 0.90 + 0.55 * math.sin(st * math.pi)  # 左右側裂片のシャープなピーク(1.45)
            elif t <= 0.60:
                st = (t - 0.42) / 0.18
                return 1.45 - 0.90 * math.sin(st * math.pi * 0.5)  # 切れ込みくびれ(0.55)
            elif t <= 0.85:
                st = (t - 0.60) / 0.25
                return 0.55 * (1.0 - st * 0.50)
            else:
                st = (t - 0.85) / 0.15
                return 0.28 * (1.0 - st)
        elif shape_type == 'COIN':
            # ユーカリ・丸コイン葉 (ほぼ真円形)
            return math.sin(t * math.pi) * 1.15
        elif shape_type == 'FIDDLE':
            # カシワバ・バイオリン葉 (基部くびれ -> 先端扇状拡大)
            if t <= 0.35:
                return 0.40 + 0.12 * math.sin((t / 0.35) * math.pi)
            elif t <= 0.75:
                st = (t - 0.35) / 0.40
                return 0.42 + 0.95 * math.sin(st * math.pi * 0.5)
            else:
                st = (t - 0.75) / 0.25
                return 1.37 * (1.0 - st) ** 0.75
        else:  # 'HEART' (標準ポトス)
            if t <= 0.20:
                st = t / 0.20
                return 0.35 + 0.65 * math.sin(st * math.pi * 0.5)
            elif t <= 0.50:
                st = (t - 0.20) / 0.30
                return 1.0 - 0.12 * math.sin(st * math.pi)
            else:
                st = (t - 0.50) / 0.50
                return (1.0 - st) ** 1.35

    t_steps = [0.0, 0.20, 0.42, 0.65, 0.88]
    cross_sections = []

    for t in t_steps:
        z_co = t * length
        drop_y = (t ** 2.2) * (length * 0.45 * curl)
        w_factor = max(0.05, get_width_profile(t))
        w = width * w_factor * 0.5
        cup_depth = w * 0.55 * v_cup

        # カシワバの場合、縁にフリルの波打ちを加える
        frill_wave = 0.0
        if shape_type == 'FIDDLE':
            frill_wave = math.sin(t * 16.0) * (width * 0.12)

        p_mid = Vector((0.0, drop_y - cup_depth, z_co))
        p_l_inner = Vector((-w * 0.52, drop_y - cup_depth * 0.4 + frill_wave * 0.5, z_co))
        p_r_inner = Vector((w * 0.52, drop_y - cup_depth * 0.4 - frill_wave * 0.5, z_co))
        p_l_outer = Vector((-w, drop_y + frill_wave, z_co))
        p_r_outer = Vector((w, drop_y - frill_wave, z_co))

        # 3裂アイビーの側裂片（t=0.42）の外縁を少し後方に引いて角を強調
        if shape_type == 'IVY_LOBED' and abs(t - 0.42) < 0.05:
            p_l_outer.y += width * 0.15
            p_r_outer.y += width * 0.15

        v_m = bm.verts.new(leaf_origin + rot_mat @ p_mid)
        v_li = bm.verts.new(leaf_origin + rot_mat @ p_l_inner)
        v_ri = bm.verts.new(leaf_origin + rot_mat @ p_r_inner)
        v_lo = bm.verts.new(leaf_origin + rot_mat @ p_l_outer)
        v_ro = bm.verts.new(leaf_origin + rot_mat @ p_r_outer)

        cross_sections.append((v_lo, v_li, v_m, v_ri, v_ro))

    drop_y_tip = (1.0 ** 2.2) * (length * 0.45 * curl)
    p_tip = Vector((0.0, drop_y_tip, length))
    v_tip = bm.verts.new(leaf_origin + rot_mat @ p_tip)

    for s in range(len(cross_sections) - 1):
        lo1, li1, m1, ri1, ro1 = cross_sections[s]
        lo2, li2, m2, ri2, ro2 = cross_sections[s + 1]

        f1 = bm.faces.new((lo1, li1, li2, lo2))
        f2 = bm.faces.new((li1, m1, m2, li2))
        f3 = bm.faces.new((m1, ri1, ri2, m2))
        f4 = bm.faces.new((ri1, ro1, ro2, ri2))
        for f in [f1, f2, f3, f4]:
            f.smooth = True
            leaf_faces.append(f)

    last_lo, last_li, last_m, last_ri, last_ro = cross_sections[-1]
    f_tip1 = bm.faces.new((last_lo, last_li, v_tip))
    f_tip2 = bm.faces.new((last_li, last_m, v_tip))
    f_tip3 = bm.faces.new((last_m, last_ri, v_tip))
    f_tip4 = bm.faces.new((last_ri, last_ro, v_tip))
    for f in [f_tip1, f_tip2, f_tip3, f_tip4]:
        f.smooth = True
        leaf_faces.append(f)

    return stem_faces, leaf_faces


def build_pearl_succulent(bm, base_pos, out_dir, radius=0.011, petiole_len=0.007):
    """
    【グリーンネックレス（String of Pearls）多肉ビーズ玉】
    細い小柄の先端に、丸く膨らんだ多肉球体玉（UV球 8x6）を生成
    """
    stem_faces = []
    leaf_faces = []

    out_norm = out_dir.normalized()
    p0 = base_pos
    p1 = base_pos + out_norm * petiole_len
    _, f_pet = add_curved_tube(bm, [p0, p1], 0.0013, segments=6)
    stem_faces.extend(f_pet)

    center = p1 + out_norm * (radius * 0.95)
    f_sphere = add_small_knot_sphere(bm, center, radius=radius, segments_u=8, segments_v=6)
    leaf_faces.extend(f_sphere)

    return stem_faces, leaf_faces


def build_fern_leaflet(bm, base_pos, out_dir, length=0.032, width=0.012, curl=0.25, rot_euler=None):
    """
    【ボストンファーン・シダ用波打つフリル小葉】
    """
    leaf_faces = []
    rot_mat = rot_euler.to_matrix().to_4x4() if rot_euler else Matrix.Identity(4)

    t_steps = [0.0, 0.35, 0.70]
    cross_sections = []

    for t in t_steps:
        z_co = t * length
        drop_y = (t ** 2.0) * (length * 0.30 * curl)
        w = width * math.sin(t * math.pi * 0.85 + 0.15) * 0.5
        cup_depth = w * 0.35

        p_mid = Vector((0.0, drop_y - cup_depth, z_co))
        p_l = Vector((-w, drop_y + math.sin(t * 12.0) * 0.002, z_co))
        p_r = Vector((w, drop_y - math.sin(t * 12.0) * 0.002, z_co))

        v_m = bm.verts.new(base_pos + rot_mat @ p_mid)
        v_l = bm.verts.new(base_pos + rot_mat @ p_l)
        v_r = bm.verts.new(base_pos + rot_mat @ p_r)
        cross_sections.append((v_l, v_m, v_r))

    p_tip = Vector((0.0, length * 0.30 * curl, length))
    v_tip = bm.verts.new(base_pos + rot_mat @ p_tip)

    for s in range(len(cross_sections) - 1):
        l1, m1, r1 = cross_sections[s]
        l2, m2, r2 = cross_sections[s + 1]
        f1 = bm.faces.new((l1, m1, m2, l2))
        f2 = bm.faces.new((m1, r1, r2, m2))
        f1.smooth = True
        f2.smooth = True
        leaf_faces.extend([f1, f2])

    last_l, last_m, last_r = cross_sections[-1]
    f_t1 = bm.faces.new((last_l, last_m, v_tip))
    f_t2 = bm.faces.new((last_m, last_r, v_tip))
    f_t1.smooth = True
    f_t2.smooth = True
    leaf_faces.extend([f_t1, f_t2])

    return leaf_faces


def build_curved_leaf_blade(
    bm,
    base_pos,
    length=0.35,
    width=0.08,
    curl=0.40,
    v_cup=0.45,
    shape='OVAL',
    rot_euler=None
):
    """
    【立体樋状カーブ葉（サンスベリア・ヤシ・モンステラ用）】
    5ステップ×左右2分割の滑らかな二重曲面トポロジー
    """
    rot_mat = rot_euler.to_matrix().to_4x4() if rot_euler else Matrix.Identity(4)

    def get_width_factor(t):
        if shape == 'SWORD':  # サンスベリア剣葉: 肉厚で先端が自然に先細る
            return math.sin(t * math.pi * 0.72 + 0.28) * math.pow(1.0 - t * 0.75, 0.6)
        elif shape == 'LANCEOLATE':  # ヤシ羽片: 細長い披針形
            return math.sin(t * math.pi)
        else:  # MONSTERA
            return math.sin(t * math.pi * 0.8 + 0.2) * 1.25

    t_steps = [0.0, 0.22, 0.48, 0.74, 0.90]
    cross_sections = []

    for t in t_steps:
        z_co = t * length
        if shape == 'SWORD':
            drop_y = (t ** 1.8) * (length * 0.15 * curl) - math.sin(t * math.pi) * 0.015
        else:
            drop_y = (t ** 2.2) * (length * 0.42 * curl)

        w_factor = max(0.06, get_width_factor(t))
        w = width * w_factor * 0.5
        cup_depth = w * 0.55 * v_cup

        p_mid = Vector((0.0, drop_y - cup_depth, z_co))
        p_l_inner = Vector((-w * 0.5, drop_y - cup_depth * 0.35, z_co))
        p_r_inner = Vector((w * 0.5, drop_y - cup_depth * 0.35, z_co))
        p_l_outer = Vector((-w, drop_y, z_co))
        p_r_outer = Vector((w, drop_y, z_co))

        v_m = bm.verts.new(base_pos + rot_mat @ p_mid)
        v_li = bm.verts.new(base_pos + rot_mat @ p_l_inner)
        v_ri = bm.verts.new(base_pos + rot_mat @ p_r_inner)
        v_lo = bm.verts.new(base_pos + rot_mat @ p_l_outer)
        v_ro = bm.verts.new(base_pos + rot_mat @ p_r_outer)
        cross_sections.append((v_lo, v_li, v_m, v_ri, v_ro))

    drop_y_tip = (1.0 ** 2.2) * (length * 0.42 * curl)
    p_tip = Vector((0.0, drop_y_tip, length))
    v_tip = bm.verts.new(base_pos + rot_mat @ p_tip)

    faces = []
    for s in range(len(cross_sections) - 1):
        lo1, li1, m1, ri1, ro1 = cross_sections[s]
        lo2, li2, m2, ri2, ro2 = cross_sections[s + 1]
        f1 = bm.faces.new((lo1, li1, li2, lo2))
        f2 = bm.faces.new((li1, m1, m2, li2))
        f3 = bm.faces.new((m1, ri1, ri2, m2))
        f4 = bm.faces.new((ri1, ro1, ro2, ri2))
        for f in [f1, f2, f3, f4]:
            f.smooth = True
            faces.append(f)

    last_lo, last_li, last_m, last_ri, last_ro = cross_sections[-1]
    f_t1 = bm.faces.new((last_lo, last_li, v_tip))
    f_t2 = bm.faces.new((last_li, last_m, v_tip))
    f_t3 = bm.faces.new((last_m, last_ri, v_tip))
    f_t4 = bm.faces.new((last_ri, last_ro, v_tip))
    for f in [f_t1, f_t2, f_t3, f_t4]:
        f.smooth = True
        faces.append(f)

    return faces


# ==============================================================================
# 🌿 4 Major Houseplant Style Generators (トレース実装)
# ==============================================================================

def build_hanging_macrame_houseplant(
    bm,
    pot_radius=0.15,
    pot_height=0.18,
    vine_count=7,
    hanging_length=1.1,
    leaf_shape='AUTO',
    melt_level=0.5,
    seed=0
):
    """
    【スタイル1】吊り下げ式マクラメ編みハンギング・プランター ＆ 下垂植物
    ・天井からの吊りロープ ＆ 鉢の丸みに完全吸着したマクラメ編みネット ＆ 立体結び目
    ・leaf_shape に応じてハート型ポトス、3裂アイビー、グリーンネックレス玉、シダ、ユーカリコイン、バイオリン大葉を切り替え
    """
    rng = random.Random(seed)
    pot_faces = []
    soil_faces = []
    macrame_faces = []
    stem_faces = []
    leaf_faces = []

    effective_shape = 'HEART' if leaf_shape in ('AUTO', None) else leaf_shape

    # 1. 吊り下げボウル型テラコッタ鉢
    pot_prof = [
        (0.06, -pot_height * 0.4),
        (pot_radius * 0.90, -pot_height * 0.2),
        (pot_radius, 0.0),
        (pot_radius * 0.98, pot_height * 0.3),
        (pot_radius * 1.05, pot_height * 0.36),
        (pot_radius * 0.92, pot_height * 0.34)
    ]
    f_pot = build_pot_lathe(bm, pot_prof, segments=28, center_z=0.0)
    pot_faces.extend(f_pot)

    def get_pot_radius_at(z):
        t = (z + pot_height * 0.4) / (pot_height * 0.76)
        t = max(0.0, min(1.0, t))
        return pot_radius * (0.65 + 0.38 * math.sin(t * math.pi * 0.85 + 0.15))

    # 2. 培養土
    f_soil = build_soil_mound(bm, radius=pot_radius * 0.90, rim_z=pot_height * 0.32, segments=24)
    soil_faces.extend(f_soil)

    # 3. マクラメ編みネット ＆ 吊りロープ
    top_anchor = Vector((0, 0, hanging_length))
    r_ring = 0.035
    ring_pts = [top_anchor + Vector((r_ring * math.cos(s * math.pi / 8), 0, r_ring * math.sin(s * math.pi / 8))) for s in range(16)]
    ring_pts.append(ring_pts[0])
    _, f_ring = add_curved_tube(bm, ring_pts, 0.005, segments=8)
    macrame_faces.extend(f_ring)

    top_knot = top_anchor - Vector((0, 0, 0.07))
    _, f_tknot = add_curved_tube(bm, [top_anchor, top_knot], 0.012, segments=8)
    macrame_faces.extend(f_tknot)
    f_tknot_sphere = add_small_knot_sphere(bm, top_knot, radius=0.014, segments_u=8, segments_v=6)
    macrame_faces.extend(f_tknot_sphere)

    rope_count = 4
    bottom_knot = Vector((0, 0, -pot_height * 0.44))

    for r in range(rope_count):
        ang = (r / float(rope_count)) * 2.0 * math.pi
        cos_r, sin_r = math.cos(ang), math.sin(ang)

        p_rim = Vector(((pot_radius * 1.05 + 0.004) * cos_r, (pot_radius * 1.05 + 0.004) * sin_r, pot_height * 0.32))
        p_upper = Vector(((get_pot_radius_at(pot_height * 0.15) + 0.004) * cos_r, (get_pot_radius_at(pot_height * 0.15) + 0.004) * sin_r, pot_height * 0.15))
        p_mid = Vector(((get_pot_radius_at(0.0) + 0.004) * cos_r, (get_pot_radius_at(0.0) + 0.004) * sin_r, 0.0))
        p_lower = Vector(((get_pot_radius_at(-pot_height * 0.25) + 0.004) * cos_r, (get_pot_radius_at(-pot_height * 0.25) + 0.004) * sin_r, -pot_height * 0.25))

        rope_pts = [top_knot, p_rim, p_upper, p_mid, p_lower, bottom_knot]
        _, f_mrope = add_curved_tube(bm, rope_pts, [0.005, 0.0045, 0.0045, 0.0045, 0.0045, 0.006], segments=8)
        macrame_faces.extend(f_mrope)

        f_rim_knot = add_small_knot_sphere(bm, p_rim, radius=0.007, segments_u=8, segments_v=6)
        macrame_faces.extend(f_rim_knot)

    for r in range(rope_count):
        ang_curr = (r / float(rope_count)) * 2.0 * math.pi
        ang_next = ((r + 1) / float(rope_count)) * 2.0 * math.pi
        ang_mid = (ang_curr + ang_next) * 0.5

        r_up = get_pot_radius_at(pot_height * 0.15) + 0.004
        r_mid = get_pot_radius_at(0.0) + 0.004
        r_low = get_pot_radius_at(-pot_height * 0.20) + 0.004

        p_c = Vector((r_up * math.cos(ang_curr), r_up * math.sin(ang_curr), pot_height * 0.15))
        p_m = Vector((r_mid * math.cos(ang_mid), r_mid * math.sin(ang_mid), 0.0))
        p_n = Vector((r_up * math.cos(ang_next), r_up * math.sin(ang_next), pot_height * 0.15))
        p_b = Vector((r_low * math.cos(ang_mid), r_low * math.sin(ang_mid), -pot_height * 0.20))

        _, f_d1 = add_curved_tube(bm, [p_c, p_m, p_b], 0.0032, segments=6)
        _, f_d2 = add_curved_tube(bm, [p_n, p_m, p_b], 0.0032, segments=6)
        macrame_faces.extend(f_d1 + f_d2)

        f_k_mid = add_small_knot_sphere(bm, p_m, radius=0.0055, segments_u=8, segments_v=6)
        f_k_bot = add_small_knot_sphere(bm, p_b, radius=0.0055, segments_u=8, segments_v=6)
        macrame_faces.extend(f_k_mid + f_k_bot)

    f_b_sphere = add_small_knot_sphere(bm, bottom_knot, radius=0.016, segments_u=10, segments_v=8)
    macrame_faces.extend(f_b_sphere)

    tassel_length = 0.40
    for t in range(16):
        t_ang = (t / 16.0) * 2.0 * math.pi
        rad_t = rng.uniform(0.005, 0.018)
        t_top = bottom_knot + Vector((rad_t * math.cos(t_ang), rad_t * math.sin(t_ang), 0.0))
        t_mid = t_top + Vector((0.02 * math.cos(t_ang), 0.02 * math.sin(t_ang), -tassel_length * 0.5))
        t_end = t_top + Vector((0.03 * math.cos(t_ang), 0.03 * math.sin(t_ang), -tassel_length * rng.uniform(0.85, 1.15)))
        _, f_tas = add_curved_tube(bm, [t_top, t_mid, t_end], 0.0028, segments=6)
        macrame_faces.extend(f_tas)

    # 4. つる性植物の生成 (effective_shape に応じて切り替え)
    for v in range(vine_count):
        v_ang = (v / float(vine_count)) * 2.0 * math.pi + rng.uniform(-0.18, 0.18)
        cos_v, sin_v = math.cos(v_ang), math.sin(v_ang)
        vine_len = rng.uniform(0.50, 0.90)

        p_soil = Vector((pot_radius * 0.75 * cos_v, pot_radius * 0.75 * sin_v, pot_height * 0.32))
        p_rim_up = Vector((pot_radius * 1.12 * cos_v, pot_radius * 1.12 * sin_v, pot_height * 0.36))
        p_rim_out = Vector((pot_radius * 1.28 * cos_v, pot_radius * 1.28 * sin_v, pot_height * 0.22))

        vine_points = [p_soil, p_rim_up, p_rim_out]

        steps = 15
        freq_a = rng.uniform(2.5, 4.0)
        freq_b = rng.uniform(4.5, 7.0)
        phase_a = rng.uniform(0, math.pi * 2)
        phase_b = rng.uniform(0, math.pi * 2)
        tangent_perp = Vector((-sin_v, cos_v, 0))
        rad_dir = Vector((cos_v, sin_v, 0))

        for s in range(1, steps + 1):
            t = s / float(steps)
            z_curr = pot_height * 0.22 - t * (vine_len + pot_height * 0.22)
            r_curr = pot_radius * (1.20 - t * 0.22)
            sway_x = math.sin(t * math.pi * freq_a + phase_a) * (0.025 + 0.035 * t)
            sway_y = math.cos(t * math.pi * freq_b + phase_b) * (0.020 + 0.025 * t)
            pos = rad_dir * (r_curr + sway_y) + tangent_perp * sway_x + Vector((0, 0, z_curr))
            vine_points.append(pos)

        stem_radius = 0.0022 if effective_shape == 'PEARLS' else 0.0035
        _, f_stem = add_curved_tube(bm, vine_points, stem_radius, segments=8)
        stem_faces.extend(f_stem)

        total_pts = len(vine_points)

        # 形状タイプに応じた葉の配置
        if effective_shape == 'PEARLS':
            # グリーンネックレス: 多数の丸い多肉玉（35〜45個/ツル）
            pearl_count = int(vine_len * 50)
            for p in range(pearl_count):
                t_v = (p + 1) / float(pearl_count + 1)
                float_idx = t_v * (total_pts - 1)
                idx0 = int(float_idx)
                idx1 = min(total_pts - 1, idx0 + 1)
                pos_node = vine_points[idx0].lerp(vine_points[idx1], float_idx - idx0)

                phi = p * 2.39996  # 黄金比回転で全方位に散布
                node_out = Vector((math.cos(phi), math.sin(phi), rng.uniform(-0.3, 0.3))).normalized()
                r_pearl = rng.uniform(0.008, 0.012) * (1.0 - t_v * 0.25)
                f_pet, f_p = build_pearl_succulent(bm, pos_node, node_out, radius=r_pearl, petiole_len=rng.uniform(0.005, 0.008))
                stem_faces.extend(f_pet)
                leaf_faces.extend(f_p)

        elif effective_shape == 'FERN':
            # ボストンファーン: 細かなフリル小葉の対生（両側に密生）
            pair_count = int(vine_len * 42)
            for pr in range(pair_count):
                t_v = (pr + 1) / float(pair_count + 1)
                float_idx = t_v * (total_pts - 1)
                idx0 = int(float_idx)
                idx1 = min(total_pts - 1, idx0 + 1)
                pos_node = vine_points[idx0].lerp(vine_points[idx1], float_idx - idx0)

                tang = (vine_points[idx1] - vine_points[idx0]).normalized()
                side_vec = tang.cross(Vector((0, 0, 1))).normalized()

                for side in (-1.0, 1.0):
                    f_dir = (side_vec * side + Vector((0, 0, 0.08))).normalized()
                    f_yaw = math.atan2(f_dir.y, f_dir.x)
                    f_pitch = 0.22 + rng.uniform(-0.08, 0.08)
                    rot_fern = Euler((f_pitch, rng.uniform(-0.08, 0.08), f_yaw), 'XYZ')
                    fn_len = rng.uniform(0.042, 0.068) * math.sin(t_v * math.pi * 0.88 + 0.12)
                    f_fern = build_fern_leaflet(bm, pos_node, f_dir, length=fn_len, width=fn_len * 0.40, rot_euler=rot_fern)
                    leaf_faces.extend(f_fern)

        elif effective_shape == 'COIN':
            # ユーカリ・丸コイン葉: 節ごとに向かい合う2枚の丸葉（対生）
            pair_count = int(vine_len * 14)
            for pr in range(pair_count):
                t_v = (pr + 1) / float(pair_count + 1)
                float_idx = t_v * (total_pts - 1)
                idx0 = int(float_idx)
                idx1 = min(total_pts - 1, idx0 + 1)
                pos_node = vine_points[idx0].lerp(vine_points[idx1], float_idx - idx0)

                tang = (vine_points[idx1] - vine_points[idx0]).normalized()
                side_vec = tang.cross(Vector((0, 0, 1))).normalized()

                for side in (-1.0, 1.0):
                    c_dir = (side_vec * side + Vector((0, 0, 0.20))).normalized()
                    c_yaw = math.atan2(c_dir.y, c_dir.x)
                    rot_coin = Euler((0.35, 0.0, c_yaw), 'XYZ')
                    c_len = rng.uniform(0.040, 0.055) * (1.0 - t_v * 0.2)
                    f_pet, f_c = build_organic_ivy_leaf(
                        bm, pos_node, c_dir,
                        length=c_len, width=c_len * 0.95,
                        curl=0.20, v_cup=0.25,
                        petiole_len=0.010, rot_euler=rot_coin,
                        shape_type='COIN'
                    )
                    stem_faces.extend(f_pet)
                    leaf_faces.extend(f_c)

        else:
            # 'HEART', 'IVY_LOBED', 'FIDDLE'
            leaves_count = int(vine_len * 22)
            for lv in range(leaves_count):
                t_vine = (lv + 1) / float(leaves_count + 1)
                float_idx = t_vine * (total_pts - 1)
                idx0 = int(float_idx)
                idx1 = min(total_pts - 1, idx0 + 1)
                frac = float_idx - idx0
                pos_node = vine_points[idx0].lerp(vine_points[idx1], frac)

                tang = (vine_points[idx1] - vine_points[idx0]).normalized()
                if tang.length < 1e-4:
                    tang = Vector((0, 0, -1))

                side_flip = -1.0 if lv % 2 == 0 else 1.0
                node_rad = Vector((pos_node.x, pos_node.y, 0)).normalized()
                if node_rad.length < 1e-4:
                    node_rad = rad_dir
                leaf_out = (node_rad + tangent_perp * (side_flip * 0.85) + Vector((0, 0, 0.25))).normalized()

                leaf_yaw = math.atan2(leaf_out.y, leaf_out.x)
                leaf_pitch = 0.40 + rng.uniform(-0.15, 0.15)
                rot_leaf = Euler((leaf_pitch, rng.uniform(-0.1, 0.1), leaf_yaw), 'XYZ')

                l_len = rng.uniform(0.048, 0.072) * (1.0 - t_vine * 0.25)
                l_w = l_len * (0.95 if effective_shape == 'IVY_LOBED' else 0.82)

                f_petiole, f_blade = build_organic_ivy_leaf(
                    bm,
                    base_pos=pos_node,
                    out_dir=leaf_out,
                    length=l_len,
                    width=l_w,
                    curl=0.42,
                    v_cup=0.48,
                    petiole_len=rng.uniform(0.016, 0.024),
                    rot_euler=rot_leaf,
                    shape_type=effective_shape
                )
                stem_faces.extend(f_petiole)
                leaf_faces.extend(f_blade)

    return pot_faces, soil_faces, macrame_faces, stem_faces, leaf_faces


def build_pedestal_urn_houseplant(bm, pot_radius=0.18, pot_height=0.32, leaf_count=14, seed=0):
    """
    【スタイル2】アンティーク脚付き聖杯鉢 ＆ サンスベリア剣葉 (画像2トレース)
    """
    rng = random.Random(seed)
    pot_faces = []
    soil_faces = []
    macrame_faces = []
    stem_faces = []
    leaf_faces = []

    urn_prof = [
        (pot_radius * 0.75, 0.0),
        (pot_radius * 0.70, 0.02),
        (pot_radius * 0.45, 0.04),
        (pot_radius * 0.32, 0.09),
        (pot_radius * 0.42, 0.12),
        (pot_radius * 0.75, 0.16),
        (pot_radius * 1.0, 0.22),
        (pot_radius * 0.95, 0.28),
        (pot_radius * 1.08, 0.31),
        (pot_radius * 0.92, 0.30)
    ]
    f_pot = build_pot_lathe(bm, urn_prof, segments=28, center_z=0.0)
    pot_faces.extend(f_pot)

    f_soil = build_soil_mound(bm, radius=pot_radius * 0.90, rim_z=0.29, segments=24)
    soil_faces.extend(f_soil)

    rings_cfg = [
        (3, 0.58, 0.03, 0.08),
        (5, 0.50, 0.07, 0.18),
        (6, 0.38, 0.11, 0.32)
    ]
    for count, l_len_base, rad_ring, pitch_base in rings_cfg:
        for c in range(count):
            ang = (c / float(count)) * 2.0 * math.pi + rng.uniform(-0.1, 0.1)
            p_base = Vector((rad_ring * math.cos(ang), rad_ring * math.sin(ang), 0.29))

            pitch = pitch_base + rng.uniform(-0.04, 0.04)
            yaw = ang + math.pi * 0.5
            rot_leaf = Euler((pitch, rng.uniform(-0.06, 0.06), yaw), 'XYZ')

            l_len = l_len_base * rng.uniform(0.92, 1.08)
            l_w = l_len * 0.18
            f_l = build_curved_leaf_blade(
                bm,
                base_pos=p_base,
                length=l_len,
                width=l_w,
                curl=0.20,
                v_cup=0.65,
                shape='SWORD',
                rot_euler=rot_leaf
            )
            leaf_faces.extend(f_l)

    return pot_faces, soil_faces, macrame_faces, stem_faces, leaf_faces


def build_floor_palm_houseplant(bm, pot_radius=0.22, pot_height=0.35, frond_count=7, seed=0):
    """
    【スタイル3】床置き大型アレカヤシ・シダ陶器鉢 (画像3トレース)
    """
    rng = random.Random(seed)
    pot_faces = []
    soil_faces = []
    macrame_faces = []
    stem_faces = []
    leaf_faces = []

    pot_prof = [
        (pot_radius * 0.85, 0.02),
        (pot_radius * 0.88, 0.05),
        (pot_radius * 0.98, pot_height * 0.6),
        (pot_radius * 1.0, pot_height),
        (pot_radius * 0.88, pot_height - 0.02)
    ]
    f_pot = build_pot_lathe(bm, pot_prof, segments=28, center_z=0.0)
    pot_faces.extend(f_pot)

    saucer_prof = [
        (pot_radius * 0.82, 0.0),
        (pot_radius * 1.15, 0.008),
        (pot_radius * 1.18, 0.035),
        (pot_radius * 1.12, 0.032)
    ]
    f_saucer = build_pot_lathe(bm, saucer_prof, segments=28, center_z=0.0)
    pot_faces.extend(f_saucer)

    f_soil = build_soil_mound(bm, radius=pot_radius * 0.88, rim_z=pot_height - 0.02, segments=24)
    soil_faces.extend(f_soil)

    frond_configs = [
        (3, 0.95, 0.04, 0.25),
        (4, 0.82, 0.08, 0.48),
        (3, 0.65, 0.12, 0.72)
    ]
    for count, stem_len_base, rad_base, bend_base in frond_configs:
        for c in range(count):
            ang = (c / float(count)) * 2.0 * math.pi + rng.uniform(-0.15, 0.15)
            cos_a, sin_a = math.cos(ang), math.sin(ang)

            p_start = Vector((rad_base * cos_a, rad_base * sin_a, pot_height - 0.02))
            stem_len = stem_len_base * rng.uniform(0.9, 1.1)

            arch_pts = []
            for sp in range(6):
                t = sp / 5.0
                rad_t = rad_base + (t ** 1.3) * (stem_len * 0.45 * math.sin(bend_base))
                z_t = (pot_height - 0.02) + t * (stem_len * math.cos(bend_base)) - (t ** 2.2) * (stem_len * 0.20)
                arch_pts.append(Vector((rad_t * cos_a, rad_t * sin_a, z_t)))

            _, f_stem = add_curved_tube(bm, arch_pts, [0.009, 0.007, 0.005, 0.004, 0.003, 0.002], segments=8)
            stem_faces.extend(f_stem)

            pinna_pairs = 16
            for p in range(pinna_pairs):
                t_pinna = 0.25 + (p / float(pinna_pairs)) * 0.72
                float_sp = t_pinna * 5.0
                isp0 = int(float_sp)
                isp1 = min(5, isp0 + 1)
                frac = float_sp - isp0
                p_node = arch_pts[isp0].lerp(arch_pts[isp1], frac)

                tang = (arch_pts[isp1] - arch_pts[isp0]).normalized()
                side_vec = tang.cross(Vector((0, 0, 1))).normalized()

                for side in (-1.0, 1.0):
                    p_w = side_vec * side
                    p_dir = (p_w * 0.85 + tang * 0.35 - Vector((0, 0, 0.18))).normalized()
                    p_yaw = math.atan2(p_dir.y, p_dir.x)
                    p_pitch = math.asin(max(-1.0, min(1.0, p_dir.z)))
                    rot_p = Euler((-p_pitch, 0.0, p_yaw), 'XYZ')

                    pinna_len = rng.uniform(0.20, 0.36) * math.sin(t_pinna * math.pi)
                    f_pinna = build_curved_leaf_blade(
                        bm,
                        base_pos=p_node,
                        length=pinna_len,
                        width=0.022,
                        curl=0.55,
                        v_cup=0.40,
                        shape='LANCEOLATE',
                        rot_euler=rot_p
                    )
                    leaf_faces.extend(f_pinna)

    return pot_faces, soil_faces, macrame_faces, stem_faces, leaf_faces


def build_monstera_desk_houseplant(bm, pot_radius=0.14, pot_height=0.18, leaf_count=6, leaf_shape='AUTO', seed=0):
    """
    【スタイル4】卓上広葉鉢（モンステラ／カシワババイオリン葉等）
    """
    rng = random.Random(seed)
    pot_faces = []
    soil_faces = []
    macrame_faces = []
    stem_faces = []
    leaf_faces = []

    pot_prof = [
        (pot_radius * 0.75, 0.0),
        (pot_radius * 0.82, 0.02),
        (pot_radius * 0.98, pot_height * 0.85),
        (pot_radius * 1.04, pot_height),
        (pot_radius * 0.90, pot_height - 0.02)
    ]
    f_pot = build_pot_lathe(bm, pot_prof, segments=28, center_z=0.0)
    pot_faces.extend(f_pot)

    f_soil = build_soil_mound(bm, radius=pot_radius * 0.90, rim_z=pot_height - 0.02, segments=24)
    soil_faces.extend(f_soil)

    for m in range(leaf_count):
        ang = (m / float(leaf_count)) * 2.0 * math.pi + rng.uniform(-0.2, 0.2)
        cos_m, sin_m = math.cos(ang), math.sin(ang)

        p0 = Vector((0.02 * cos_m, 0.02 * sin_m, pot_height - 0.02))
        s_len = rng.uniform(0.24, 0.38)
        p1 = Vector((0.08 * cos_m, 0.08 * sin_m, pot_height + s_len * 0.5))
        p2 = Vector((0.18 * cos_m, 0.18 * sin_m, pot_height + s_len * 0.85))

        _, f_mstem = add_curved_tube(bm, [p0, p1, p2], [0.007, 0.006, 0.005], segments=8)
        stem_faces.extend(f_mstem)

        yaw = ang + math.pi * 0.5
        rot_leaf = Euler((0.45, rng.uniform(-0.1, 0.1), yaw), 'XYZ')

        if leaf_shape == 'FIDDLE':
            # カシワバ・バイオリン大葉
            _, f_blade = build_organic_ivy_leaf(
                bm, base_pos=p2, out_dir=Vector((cos_m, sin_m, 0.5)),
                length=rng.uniform(0.22, 0.30), width=rng.uniform(0.18, 0.24),
                curl=0.30, v_cup=0.35, petiole_len=0.015,
                rot_euler=rot_leaf, shape_type='FIDDLE'
            )
        else:
            # 標準モンステラ広葉
            f_blade = build_curved_leaf_blade(
                bm,
                base_pos=p2,
                length=rng.uniform(0.18, 0.26),
                width=rng.uniform(0.16, 0.22),
                curl=0.35,
                v_cup=0.30,
                shape='MONSTERA',
                rot_euler=rot_leaf
            )
        leaf_faces.extend(f_blade)

    return pot_faces, soil_faces, macrame_faces, stem_faces, leaf_faces


# ==============================================================================
# 🌟 Foliage Spherical Normal Transfer (球状法線転送によるリアルボリューム感)
# ==============================================================================

def apply_spherical_foliage_normals(mesh, leaf_vert_indices, center=Vector((0, 0, 0.3)), normal_factor=0.65):
    """
    ゲームアセット/フォトリアルCG標準:
    葉ポリゴンの法線を植物全体のバウンディング球中心からの放射ベクトル方向へブレンド。
    """
    if not leaf_vert_indices:
        return

    mesh.calc_normals()
    if not mesh.has_custom_normals:
        mesh.create_normals_split()

    custom_normals = []
    for poly in mesh.polygons:
        for loop_idx in poly.loop_indices:
            v_idx = mesh.loops[loop_idx].vertex_index
            if v_idx in leaf_vert_indices:
                orig_n = mesh.vertices[v_idx].normal
                rad_n = (mesh.vertices[v_idx].co - center).normalized()
                blended = (orig_n * (1.0 - normal_factor) + rad_n * normal_factor).normalized()
                custom_normals.append(blended)
            else:
                custom_normals.append(mesh.vertices[v_idx].normal)

    mesh.normals_split_custom_set(custom_normals)
    mesh.use_auto_smooth = True
    mesh.auto_smooth_angle = math.radians(70)


# ==============================================================================
# 🚀 Houseplant Generation Main Entry Point
# ==============================================================================

def generate_houseplant(
    context,
    name="Houseplant",
    style='HANGING_MACRAME',
    leaf_shape='AUTO',
    leaf_density='MEDIUM',
    pot_material='TERRACOTTA',
    leaf_color='VIBRANT_GREEN',
    variegated=False,
    combine=True,
    target_obj=None,
    seed=42
):
    """
    観葉植物（ハンギングプランター、脚付き聖杯鉢、床置きヤシ等）のプロシージャル生成メインエントリーポイント
    """
    # 既存ターゲットオブジェクトの安全な削除
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

    # スタイル別ジオメトリ生成
    if style == 'HANGING_MACRAME':
        p_faces, s_faces, m_faces, st_faces, l_faces = build_hanging_macrame_houseplant(
            bm,
            pot_radius=0.15,
            pot_height=0.18,
            vine_count=9 if leaf_density == 'HIGH' else (5 if leaf_density == 'LOW' else 7),
            leaf_shape=leaf_shape,
            seed=seed
        )
        spherical_center = Vector((0, 0, -0.15))
    elif style == 'PEDESTAL_URN':
        p_faces, s_faces, m_faces, st_faces, l_faces = build_pedestal_urn_houseplant(
            bm,
            pot_radius=0.18,
            pot_height=0.32,
            leaf_count=18 if leaf_density == 'HIGH' else (10 if leaf_density == 'LOW' else 14),
            seed=seed
        )
        spherical_center = Vector((0, 0, 0.45))
    elif style == 'FLOOR_PALM':
        p_faces, s_faces, m_faces, st_faces, l_faces = build_floor_palm_houseplant(
            bm,
            pot_radius=0.22,
            pot_height=0.35,
            frond_count=9 if leaf_density == 'HIGH' else (5 if leaf_density == 'LOW' else 7),
            seed=seed
        )
        spherical_center = Vector((0, 0, 0.65))
    else:  # MONSTERA_DESK
        p_faces, s_faces, m_faces, st_faces, l_faces = build_monstera_desk_houseplant(
            bm,
            pot_radius=0.14,
            pot_height=0.18,
            leaf_count=8 if leaf_density == 'HIGH' else (4 if leaf_density == 'LOW' else 6),
            leaf_shape=leaf_shape,
            seed=seed
        )
        spherical_center = Vector((0, 0, 0.30))

    # マテリアルインデックスの割り当て
    # 0: Leaf, 1: Stem, 2: Pot, 3: Soil, 4: Macrame (if exists)
    for f in l_faces:
        f.material_index = 0
        f.smooth = True
    for f in st_faces:
        f.material_index = 1
        f.smooth = True
    for f in p_faces:
        f.material_index = 2
        f.smooth = True
    for f in s_faces:
        f.material_index = 3
        f.smooth = True
    for f in m_faces:
        f.material_index = 4
        f.smooth = True

    leaf_vert_indices = set()
    for f in l_faces:
        for v in f.verts:
            leaf_vert_indices.add(v.index)

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)
    context.view_layer.objects.active = obj
    obj.select_set(True)

    mat_leaf = create_houseplant_leaf_shader(f"{name}_Leaf_{leaf_color}", color_type=leaf_color, variegated=variegated)
    mat_stem = create_houseplant_stem_shader(f"{name}_Stem")
    mat_pot = create_houseplant_pot_shader(f"{name}_Pot_{pot_material}", pot_material=pot_material)
    mat_soil = create_houseplant_soil_shader(f"{name}_Soil")

    obj.data.materials.append(mat_leaf)
    obj.data.materials.append(mat_stem)
    obj.data.materials.append(mat_pot)
    obj.data.materials.append(mat_soil)

    if m_faces:
        mat_macrame = create_macrame_rope_shader(f"{name}_Macrame")
        obj.data.materials.append(mat_macrame)

    # 球状法線転送の適用（グリーンネックレスの場合は球形本来の立体感を活かすため控えめに）
    norm_factor = 0.25 if leaf_shape == 'PEARLS' else 0.65
    try:
        apply_spherical_foliage_normals(mesh, leaf_vert_indices, center=spherical_center, normal_factor=norm_factor)
    except Exception as e:
        print(f"Spherical normal transfer warning: {e}")

    return obj
