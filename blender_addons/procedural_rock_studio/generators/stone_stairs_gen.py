import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# ==============================================================================
# 🎨 Procedural Shaders for Stone Stairs (石畳・風化石材・苔・鍛鉄)
# ==============================================================================

def get_or_create_material(name):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
    return mat


def create_aged_stone_shader(name="StoneStairs_AgedStone", preset='AGED_COBBLE', moss_amount=0.35, damage=0.40):
    """
    年季の入った地下石畳・風化石材のPBRプロシージャルシェーダー
    歩行摩耗、目地汚れ、雨垂れ水垢、苔（Moss）レイヤーを完備
    """
    mat = get_or_create_material(name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (800, 0)

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (500, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-1000, 0)

    # 1. 石材テクスチャ用マッピング
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-800, 0)
    mapping.inputs['Scale'].default_value = (3.0, 3.0, 3.0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    # 石肌基本ノイズ
    noise_stone = nodes.new(type='ShaderNodeTexNoise')
    noise_stone.location = (-600, 100)
    noise_stone.inputs['Scale'].default_value = 12.0
    noise_stone.inputs['Detail'].default_value = 8.0
    noise_stone.inputs['Roughness'].default_value = 0.65
    links.new(mapping.outputs['Vector'], noise_stone.inputs['Vector'])

    # 微細グランジノイズ
    noise_grunge = nodes.new(type='ShaderNodeTexNoise')
    noise_grunge.location = (-600, -100)
    noise_grunge.inputs['Scale'].default_value = 28.0
    noise_grunge.inputs['Detail'].default_value = 6.0
    noise_grunge.inputs['Roughness'].default_value = 0.8
    links.new(mapping.outputs['Vector'], noise_grunge.inputs['Vector'])

    # 苔用ノイズ（上面・湿気）
    noise_moss = nodes.new(type='ShaderNodeTexNoise')
    noise_moss.location = (-600, -300)
    noise_moss.inputs['Scale'].default_value = 6.5
    noise_moss.inputs['Detail'].default_value = 5.0
    links.new(mapping.outputs['Vector'], noise_moss.inputs['Vector'])

    # 石材カラーランプ
    ramp_stone = nodes.new(type='ShaderNodeValToRGB')
    ramp_stone.location = (-350, 100)

    if preset == 'AGED_COBBLE':
        # 地下室・ワインセラー風グレー石畳（やや湿った暗灰色）
        ramp_stone.color_ramp.elements[0].position = 0.15
        ramp_stone.color_ramp.elements[0].color = (0.12, 0.11, 0.10, 1.0)
        ramp_stone.color_ramp.elements[1].position = 0.85
        ramp_stone.color_ramp.elements[1].color = (0.35, 0.33, 0.31, 1.0)
        base_rough = 0.78
    elif preset == 'DARK_FLAGSTONE':
        # カタコンベ・ダンジョン風スレート
        ramp_stone.color_ramp.elements[0].position = 0.15
        ramp_stone.color_ramp.elements[0].color = (0.05, 0.05, 0.055, 1.0)
        ramp_stone.color_ramp.elements[1].position = 0.85
        ramp_stone.color_ramp.elements[1].color = (0.18, 0.18, 0.19, 1.0)
        base_rough = 0.65
    elif preset == 'MEDIEVAL_SANDSTONE':
        # 古城・修道院の温かみのある砂岩
        ramp_stone.color_ramp.elements[0].position = 0.15
        ramp_stone.color_ramp.elements[0].color = (0.32, 0.25, 0.16, 1.0)
        ramp_stone.color_ramp.elements[1].position = 0.85
        ramp_stone.color_ramp.elements[1].color = (0.58, 0.48, 0.34, 1.0)
        base_rough = 0.82
    else:  # ANCIENT_RUINS
        # 白化・遺跡大理石
        ramp_stone.color_ramp.elements[0].position = 0.15
        ramp_stone.color_ramp.elements[0].color = (0.40, 0.38, 0.36, 1.0)
        ramp_stone.color_ramp.elements[1].position = 0.85
        ramp_stone.color_ramp.elements[1].color = (0.75, 0.72, 0.68, 1.0)
        base_rough = 0.60

    links.new(noise_stone.outputs['Fac'], ramp_stone.inputs['Fac'])

    # 苔ブレンド（Mix Color）
    mix_moss = nodes.new(type='ShaderNodeMix')
    mix_moss.data_type = 'RGBA'
    mix_moss.location = (-50, 0)
    
    # 苔のカラー（湿り気のある暗緑色）
    moss_col = (0.08, 0.14, 0.04, 1.0)
    mix_moss.inputs[7].default_value = moss_col  # B (moss)
    links.new(ramp_stone.outputs['Color'], mix_moss.inputs[6])  # A (stone)

    # 苔のファクター（苔ノイズ × moss_amount）
    moss_factor = nodes.new(type='ShaderNodeMath')
    moss_factor.operation = 'MULTIPLY'
    moss_factor.location = (-250, -200)
    moss_factor.inputs[1].default_value = moss_amount * 1.5
    links.new(noise_moss.outputs['Fac'], moss_factor.inputs[0])
    links.new(moss_factor.outputs['Value'], mix_moss.inputs['Factor'])

    links.new(mix_moss.outputs[2], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = base_rough

    # バンプ（石肌のノミ削り凹凸 ＋ チッピング）
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (200, -150)
    bump.inputs['Strength'].default_value = 0.35 + (damage * 0.35)
    bump.inputs['Distance'].default_value = 0.012
    links.new(noise_grunge.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat


def create_dungeon_iron_shader(name="StoneStairs_DungeonIron"):
    """地下ダンジョン・黒鍛鉄パイプ用PBRシェーダー"""
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
    noise.inputs['Scale'].default_value = 35.0
    noise.inputs['Detail'].default_value = 5.0
    noise.inputs['Roughness'].default_value = 0.65
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (0, -150)
    bump.inputs['Distance'].default_value = 0.003
    bump.inputs['Strength'].default_value = 0.35
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    # 黒鍛鉄
    bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.045, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.92
    bsdf.inputs['Roughness'].default_value = 0.45

    return mat


# ==============================================================================
# 🔨 BMesh Modeling Elements (幾何学パーツ生成)
# ==============================================================================

def build_stone_steps(bm, step_count=12, width=1.8, step_depth=0.32, step_height=0.18, wear_amount=0.35, include_landing=True, mat_idx=0):
    """
    石段（ステップ）スラブ列の生成
    歩行による中央すり減り（凹み）と段鼻（ノーズ）オーバーハングを完備
    """
    tread_thick = 0.10
    nose_oh = 0.025
    half_w = width * 0.5
    w_segs = 8  # 幅方向の分割（中央摩耗パラボラ用）

    for i in range(step_count):
        y_start = i * step_depth
        y_end   = y_start + step_depth + nose_oh
        z_base  = -i * step_height
        z_top_base = z_base

        # 各段の頂点グリッド生成 (w_segs+1) x 2列 (front & back)
        grid_top = []
        grid_bot = []

        for row_idx, y_val in enumerate([y_start, y_end]):
            row_top = []
            row_bot = []
            for col_idx in range(w_segs + 1):
                frac = col_idx / w_segs
                x_val = -half_w + frac * width
                # 中央すり減り（中央ほど深く凹むパラボラカーブ）
                wear_fac = math.sin(frac * math.pi) ** 2
                wear_z = -wear_amount * 0.022 * wear_fac if row_idx == 0 else (-wear_amount * 0.015 * wear_fac)

                v_top = bm.verts.new((x_val, y_val, z_top_base + wear_z))
                v_bot = bm.verts.new((x_val, y_val, z_top_base - tread_thick))
                row_top.append(v_top)
                row_bot.append(v_bot)
            grid_top.append(row_top)
            grid_bot.append(row_bot)

        # 面張り
        for col_idx in range(w_segs):
            # 上面
            f_t = bm.faces.new([grid_top[0][col_idx], grid_top[1][col_idx], grid_top[1][col_idx+1], grid_top[0][col_idx+1]])
            # 下面
            f_b = bm.faces.new([grid_bot[0][col_idx], grid_bot[0][col_idx+1], grid_bot[1][col_idx+1], grid_bot[1][col_idx]])
            # 前面（蹴込み・ノーズ面）
            f_f = bm.faces.new([grid_top[1][col_idx], grid_bot[1][col_idx], grid_bot[1][col_idx+1], grid_top[1][col_idx+1]])
            # 後面
            f_bk = bm.faces.new([grid_top[0][col_idx], grid_top[0][col_idx+1], grid_bot[0][col_idx+1], grid_bot[0][col_idx]])
            for f in [f_t, f_b, f_f, f_bk]:
                f.material_index = mat_idx

        # 左右側面
        f_left = bm.faces.new([grid_top[0][0], grid_bot[0][0], grid_bot[1][0], grid_top[1][0]])
        f_right = bm.faces.new([grid_top[0][-1], grid_top[1][-1], grid_bot[1][-1], grid_bot[0][-1]])
        f_left.material_index = mat_idx
        f_right.material_index = mat_idx

    # 最下段の踊り場・地下フロア石畳スラブ
    if include_landing:
        landing_y_start = step_count * step_depth
        landing_length = 1.20
        landing_y_end = landing_y_start + landing_length
        z_floor = -step_count * step_height

        bm_land = bmesh.new()
        res_land = bmesh.ops.create_cube(bm_land, size=1.0)
        bmesh.ops.scale(bm_land, vec=(width * 1.05, landing_length, tread_thick), verts=res_land['verts'])
        bmesh.ops.translate(bm_land, vec=(0, landing_y_start + landing_length * 0.5, z_floor - tread_thick * 0.5), verts=res_land['verts'])

        for f in bm_land.faces:
            new_f = bm.faces.new([bm.verts.new(v.co) for v in f.verts])
            new_f.material_index = mat_idx
        bm_land.free()


def build_newel_post(bm, x, y, z_base, height=1.05, width=0.34, mat_idx=0):
    """
    動画準拠の親柱（ニューエルポスト / Newel Post）
    下部台座（Plinth）+ 中央掘り込みパネル + 上部多段コーニスモールディング
    """
    bm_temp = bmesh.new()
    hw = width * 0.5

    # 1. 下部ベース台座 (Base Plinth)
    base_h = 0.18
    base_w = width * 1.15
    res_base = bmesh.ops.create_cube(bm_temp, size=1.0)
    bmesh.ops.scale(bm_temp, vec=(base_w, base_w, base_h), verts=res_base['verts'])
    bmesh.ops.translate(bm_temp, vec=(0, 0, base_h * 0.5), verts=res_base['verts'])

    # 2. 中央シャフト (Shaft with recessed panel styling)
    shaft_h = height - 0.36
    res_shaft = bmesh.ops.create_cube(bm_temp, size=1.0)
    bmesh.ops.scale(bm_temp, vec=(width, width, shaft_h), verts=res_shaft['verts'])
    bmesh.ops.translate(bm_temp, vec=(0, 0, base_h + shaft_h * 0.5), verts=res_shaft['verts'])

    # シャフト四面の装飾パネル（わずかに張り出したトリム枠）
    trim_thick = 0.015
    res_panel = bmesh.ops.create_cube(bm_temp, size=1.0)
    bmesh.ops.scale(bm_temp, vec=(width * 1.04, width * 1.04, shaft_h * 0.85), verts=res_panel['verts'])
    bmesh.ops.translate(bm_temp, vec=(0, 0, base_h + shaft_h * 0.5), verts=res_panel['verts'])

    # 3. 上部キャピタル（Cornice Crown & Cap）
    crown_h = 0.18
    crown_w = width * 1.18
    res_crown = bmesh.ops.create_cube(bm_temp, size=1.0)
    bmesh.ops.scale(bm_temp, vec=(crown_w, crown_w, crown_h * 0.5), verts=res_crown['verts'])
    bmesh.ops.translate(bm_temp, vec=(0, 0, height - crown_h * 0.75), verts=res_crown['verts'])

    # ピラミッド型トップキャップ
    res_cap = bmesh.ops.create_cone(
        bm_temp, cap_ends=True, cap_tris=False, segments=4,
        radius1=crown_w * 0.65, radius2=0.01, depth=crown_h * 0.5
    )
    bmesh.ops.rotate(bm_temp, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(45), 3, 'Z'), verts=res_cap['verts'])
    bmesh.ops.translate(bm_temp, vec=(0, 0, height - crown_h * 0.25), verts=res_cap['verts'])

    # 位置移動 & メインBMeshへ統合
    for v in bm_temp.verts:
        v.co.x += x
        v.co.y += y
        v.co.z += z_base

    for f in bm_temp.faces:
        new_f = bm.faces.new([bm.verts.new(v.co) for v in f.verts])
        new_f.material_index = mat_idx

    bm_temp.free()


def build_urn_baluster(bm, x, y, z_bottom, z_top, width=0.12, mat_idx=0):
    """
    動画準拠のクラシカル壺型バラスター（Urn Baluster）
    上下角座 + 壺型曲面ボディ + くびれネック + リングモールディング
    """
    height = z_top - z_bottom
    if height <= 0.1:
        return

    bm_temp = bmesh.new()
    segs = 12
    hw = width * 0.5

    # 下部角座 (Bottom square base)
    foot_h = height * 0.15
    res_foot = bmesh.ops.create_cube(bm_temp, size=1.0)
    bmesh.ops.scale(bm_temp, vec=(width, width, foot_h), verts=res_foot['verts'])
    bmesh.ops.translate(bm_temp, vec=(0, 0, foot_h * 0.5), verts=res_foot['verts'])

    # 上部角座 (Top square capital)
    top_h = height * 0.12
    res_top = bmesh.ops.create_cube(bm_temp, size=1.0)
    bmesh.ops.scale(bm_temp, vec=(width, width, top_h), verts=res_top['verts'])
    bmesh.ops.translate(bm_temp, vec=(0, 0, height - top_h * 0.5), verts=res_top['verts'])

    # 中央の壺型ボディ (Vase / Urn bulbous body)
    bulb_r = hw * 1.15
    res_bulb = bmesh.ops.create_icosphere(bm_temp, subdivisions=2, radius=bulb_r)
    bmesh.ops.scale(bm_temp, vec=(1.0, 1.0, 1.45), verts=res_bulb['verts'])
    bmesh.ops.translate(bm_temp, vec=(0, 0, height * 0.38), verts=res_bulb['verts'])

    # 上部のくびれシャフト・ネック (Slender neck)
    neck_r = hw * 0.55
    neck_h = height * 0.35
    res_neck = bmesh.ops.create_cone(
        bm_temp, cap_ends=True, cap_tris=False, segments=segs,
        radius1=neck_r, radius2=neck_r * 0.85, depth=neck_h
    )
    bmesh.ops.translate(bm_temp, vec=(0, 0, height * 0.65), verts=res_neck['verts'])

    # ネック周りのリング飾り (Collar ring)
    ring_r = hw * 0.85
    res_ring = bmesh.ops.create_icosphere(bm_temp, subdivisions=2, radius=ring_r)
    bmesh.ops.scale(bm_temp, vec=(1.0, 1.0, 0.4), verts=res_ring['verts'])
    bmesh.ops.translate(bm_temp, vec=(0, 0, height * 0.78), verts=res_ring['verts'])

    for v in bm_temp.verts:
        v.co.x += x
        v.co.y += y
        v.co.z += z_bottom

    for f in bm_temp.faces:
        new_f = bm.faces.new([bm.verts.new(v.co) for v in f.verts])
        new_f.material_index = mat_idx

    bm_temp.free()


def build_slanted_rails(bm, x_center, y_start, y_end, z_start, z_end, rail_width=0.18, rail_height=0.12, is_top=True, mat_idx=0):
    """
    階段の傾斜に沿った笠木（トップレール）または台輪（ボトムレール）の生成
    """
    # 始点と終点の中心座標
    p_start = Vector((x_center, y_start, z_start))
    p_end   = Vector((x_center, y_end, z_end))

    # 方向ベクトル
    dir_vec = p_end - p_start
    length = dir_vec.length
    if length <= 0.01:
        return

    bm_temp = bmesh.new()

    # レール断面の生成 (Cubeから変形)
    res = bmesh.ops.create_cube(bm_temp, size=1.0)
    bmesh.ops.scale(bm_temp, vec=(rail_width, rail_height, length), verts=res['verts'])

    # Z軸から dir_vec への回転
    dir_norm = dir_vec.normalized()
    rot_quat = Vector((0, 0, 1)).rotation_difference(dir_norm)
    bmesh.ops.rotate(bm_temp, cent=(0, 0, 0), matrix=rot_quat.to_matrix().to_3x3(), verts=res['verts'])

    # 中心位置へ移動
    mid_pos = (p_start + p_end) * 0.5
    bmesh.ops.translate(bm_temp, vec=mid_pos, verts=res['verts'])

    for f in bm_temp.faces:
        new_f = bm.faces.new([bm.verts.new(v.co) for v in f.verts])
        new_f.material_index = mat_idx

    bm_temp.free()


def build_medieval_stone_wall(bm, x_center, y_start, y_end, z_start, z_end, wall_thick=0.20, wall_h=0.38, mat_idx=0):
    """
    カタコンベ・古城風の重厚な石積み袖壁（低い石壁の手すり＋笠石）
    """
    p_start = Vector((x_center, y_start, z_start))
    p_end   = Vector((x_center, y_end, z_end))
    dir_vec = p_end - p_start
    length = dir_vec.length
    if length <= 0.01:
        return

    bm_temp = bmesh.new()

    # 壁本体
    res_w = bmesh.ops.create_cube(bm_temp, size=1.0)
    bmesh.ops.scale(bm_temp, vec=(wall_thick, wall_h, length), verts=res_w['verts'])

    # 笠石（上部の幅広キャップ）
    res_cap = bmesh.ops.create_cube(bm_temp, size=1.0)
    bmesh.ops.scale(bm_temp, vec=(wall_thick * 1.30, 0.07, length * 1.02), verts=res_cap['verts'])
    bmesh.ops.translate(bm_temp, vec=(0, wall_h * 0.5 + 0.035, 0), verts=res_cap['verts'])

    dir_norm = dir_vec.normalized()
    rot_quat = Vector((0, 0, 1)).rotation_difference(dir_norm)
    all_verts = res_w['verts'] + res_cap['verts']
    bmesh.ops.rotate(bm_temp, cent=(0, 0, 0), matrix=rot_quat.to_matrix().to_3x3(), verts=all_verts)

    mid_pos = (p_start + p_end) * 0.5 + Vector((0, 0, wall_h * 0.5))
    bmesh.ops.translate(bm_temp, vec=mid_pos, verts=all_verts)

    for f in bm_temp.faces:
        new_f = bm.faces.new([bm.verts.new(v.co) for v in f.verts])
        new_f.material_index = mat_idx

    bm_temp.free()


# ==============================================================================
# 🚀 Master Generator Entry Point
# ==============================================================================

def generate_stone_stairs(
    style='CLASSICAL_BALUSTRADE',
    step_count=12,
    width=1.8,
    step_depth=0.32,
    step_height=0.18,
    rail_placement='BOTH_SIDES',
    wear_amount=0.35,
    damage=0.40,
    moss=0.30,
    material_preset='AGED_COBBLE',
    include_landing=True,
    combine_mesh=True,
    location=(0, 0, 0),
    rotation=(0, 0, 0)
):
    """
    年季の入った石畳の地下階段 統合生成エンジン
    """
    # マテリアル生成
    stone_mat = create_aged_stone_shader(f"StoneStairs_Stone_{material_preset}", preset=material_preset, moss_amount=moss, damage=damage)
    iron_mat = create_dungeon_iron_shader("StoneStairs_DungeonIron")

    bm = bmesh.new()

    # 1. 石段ステップの生成 (mat_idx = 0)
    build_stone_steps(
        bm,
        step_count=step_count,
        width=width,
        step_depth=step_depth,
        step_height=step_height,
        wear_amount=wear_amount,
        include_landing=include_landing,
        mat_idx=0
    )

    # 手すり配置のX座標決定
    half_w = width * 0.5
    rail_x_list = []
    if rail_placement == 'BOTH_SIDES':
        rail_x_list = [-half_w - 0.14, half_w + 0.14]
    elif rail_placement == 'LEFT_ONLY':
        rail_x_list = [-half_w - 0.14]
    elif rail_placement == 'RIGHT_ONLY':
        rail_x_list = [half_w + 0.14]

    # 2. 手すり・欄干システムの生成
    if rail_x_list and style != 'SIMPLE_STEPS':
        total_depth = step_count * step_depth
        z_top_landing = 0.0
        z_bottom_landing = -step_count * step_height

        for rx in rail_x_list:
            if style == 'CLASSICAL_BALUSTRADE':
                # (A) 親柱ニューエルポスト（最上段と最下段）
                post_w = 0.32
                build_newel_post(bm, x=rx, y=0.0, z_base=z_top_landing, height=1.05, width=post_w, mat_idx=0)
                build_newel_post(bm, x=rx, y=total_depth, z_base=z_bottom_landing, height=1.05, width=post_w, mat_idx=0)

                # (B) 斜め笠木（トップレール）& 底面台輪レール
                rail_y_start = post_w * 0.5
                rail_y_end   = total_depth - post_w * 0.5
                rail_z_start = z_top_landing + 0.88
                rail_z_end   = z_bottom_landing + 0.88

                build_slanted_rails(bm, rx, rail_y_start, rail_y_end, rail_z_start, rail_z_end, rail_width=0.18, rail_height=0.10, is_top=True, mat_idx=0)
                build_slanted_rails(bm, rx, rail_y_start, rail_y_end, z_top_landing + 0.12, z_bottom_landing + 0.12, rail_width=0.16, rail_height=0.08, is_top=False, mat_idx=0)

                # (C) 壺型バラスター（等間隔配置）
                baluster_spacing = 0.28
                span_len = rail_y_end - rail_y_start
                bal_count = max(2, int(span_len / baluster_spacing))

                for b_idx in range(bal_count):
                    frac = (b_idx + 0.5) / bal_count
                    by = rail_y_start + frac * span_len
                    bz_bot = z_top_landing + frac * (z_bottom_landing - z_top_landing) + 0.16
                    bz_top = z_top_landing + frac * (z_bottom_landing - z_top_landing) + 0.83

                    build_urn_baluster(bm, x=rx, y=by, z_bottom=bz_bot, z_top=bz_top, width=0.12, mat_idx=0)

            elif style == 'DUNGEON_FORGED_IRON':
                # 武骨な地下ダンジョン黒鍛鉄パイプ手すり (mat_idx = 1)
                rail_y_start = 0.0
                rail_y_end   = total_depth
                rail_z_start = z_top_landing + 0.90
                rail_z_end   = z_bottom_landing + 0.90

                # メインパイプ
                build_slanted_rails(bm, rx, rail_y_start, rail_y_end, rail_z_start, rail_z_end, rail_width=0.05, rail_height=0.05, is_top=True, mat_idx=1)

                # 垂直アイアン支柱（数段おきに配置）
                post_step_interval = max(2, step_count // 4)
                for s_idx in range(0, step_count + 1, post_step_interval):
                    py = s_idx * step_depth
                    pz_bot = -s_idx * step_height
                    pz_top = -s_idx * step_height + 0.90

                    bm_post = bmesh.new()
                    res_p = bmesh.ops.create_cone(
                        bm_post, cap_ends=True, cap_tris=False, segments=12,
                        radius1=0.024, radius2=0.024, depth=(pz_top - pz_bot)
                    )
                    bmesh.ops.translate(bm_post, vec=(rx, py, pz_bot + (pz_top - pz_bot) * 0.5), verts=res_p['verts'])

                    # ベースフランジ座金
                    res_flange = bmesh.ops.create_cone(
                        bm_post, cap_ends=True, cap_tris=False, segments=12,
                        radius1=0.06, radius2=0.04, depth=0.03
                    )
                    bmesh.ops.translate(bm_post, vec=(rx, py, pz_bot + 0.015), verts=res_flange['verts'])

                    for f in bm_post.faces:
                        new_f = bm.faces.new([bm.verts.new(v.co) for v in f.verts])
                        new_f.material_index = 1
                    bm_post.free()

            elif style == 'MEDIEVAL_STONE_WALL':
                # 古城・カタコンベの重厚な石積み袖壁
                build_medieval_stone_wall(bm, rx, 0.0, total_depth, z_top_landing, z_bottom_landing, wall_thick=0.28, wall_h=0.85, mat_idx=0)

    # メッシュ生成
    mesh = bpy.data.meshes.new("Stone_Stairs_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Stone_Stairs_Asset", mesh)
    bpy.context.collection.objects.link(obj)

    obj.data.materials.append(stone_mat)  # Index 0
    obj.data.materials.append(iron_mat)   # Index 1

    obj.location = location
    obj.rotation_euler = rotation

    for poly in mesh.polygons:
        poly.use_smooth = True

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    return [obj]
