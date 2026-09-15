import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

from ..materials.curtain_mat import (
    create_curtain_fabric_material,
    create_curtain_rod_material,
    CURTAIN_MATERIAL_PRESETS
)


def generate_curtain(
    context,
    name="Curtain_Studio",
    width=1.80,
    height=2.20,
    pleats_per_panel=12,
    style='DOUBLE_OPEN',
    fabric_type='SHEER_LACE',
    rod_style='BRASS',
    include_rod=True,
    simulate_wind=True,
    wind_strength=45.0,
    wind_direction=(0.35, 1.0, 0.15),
    bake_to_static=True,
    combine=True,
    open_amount=0.0,
    tied_back=False,
    generate_shapekey=True,
    smoothness='MEDIUM',
    seed=0
):
    """
    プロシージャル・カーテン生成エンジン（開閉・タッセル・シェイプキー・高品位スムーズ曲面対応）
    
    【主要機能】
    1. 左右両開き（中央スリット）/ 片開き プリーツ布地モデリング
    2. ヒダの丸み・柔らかさ（smoothness: 1ヒダあたり6~18分割）で角張りを完全解消
    3. 開閉度スライダー（open_amount: 0.0 閉 ~ 1.0 全開）によるアコーディオン圧縮
    4. タッセル・房掛け束ね（tied_back）による優雅なくびれドレープ
    5. カーテンロッド（レール）、ブラケット、リング金具、および壁掛けタッセル金具の自動生成
    6. UE5風揺れシェーダー向け【頂点カラー（Vertex Color）自動ベイク】:
       - R: 上下ピン留めグラデーション (上=0.0 ~ 下=1.0)
       - G: 中央スリット距離グラデーション (中央=1.0 ~ 外側=0.0)
       - B: 左右カーテン識別フラグ (左=0.0 / 右=1.0)
       - A: プリーツ峰谷マスク (0.0 ~ 1.0)
    7. UE5対応【シェイプキー（Morph Target）自動生成】:
       - Basis(閉) と Open(開) の2つのシェイプキーを埋め込み、インゲーム開閉アニメーションに対応
    8. Blender内部【Cloth ＋ Wind Force 横風シミュレーション】
    """
    rng = random.Random(seed)
    created_objs = []

    eff_w = max(0.60, min(5.00, float(width)))
    eff_h = max(0.80, min(4.50, float(height)))
    pleats = max(4, min(32, int(pleats_per_panel)))
    cur_open = max(0.0, min(1.0, float(open_amount)))

    # ヒダの分割密度（角張りをなくし、柔らかい布地曲面を実現）
    if smoothness == 'HIGH':
        subdiv_per_pleat = 18
        subdiv_y = 48
    elif smoothness == 'LOW':
        subdiv_per_pleat = 6
        subdiv_y = 28
    else:  # 'MEDIUM'
        subdiv_per_pleat = 12
        subdiv_y = 38

    # 1. カーテン布地パネルの設定
    if style == 'DOUBLE_OPEN':
        panel_configs = [
            {'side': 'LEFT', 'width': eff_w * 0.51, 'center_x': -eff_w * 0.25, 'flag': 0.0, 'outer_x': -eff_w * 0.50},
            {'side': 'RIGHT', 'width': eff_w * 0.51, 'center_x': eff_w * 0.25, 'flag': 1.0, 'outer_x': eff_w * 0.50}
        ]
    elif style == 'SINGLE_LEFT':
        panel_configs = [
            {'side': 'LEFT', 'width': eff_w, 'center_x': 0.0, 'flag': 0.0, 'outer_x': -eff_w * 0.50}
        ]
    else:  # 'SINGLE_RIGHT'
        panel_configs = [
            {'side': 'RIGHT', 'width': eff_w, 'center_x': 0.0, 'flag': 1.0, 'outer_x': eff_w * 0.50}
        ]

    fabric_objs = []
    for p_idx, p_cfg in enumerate(panel_configs):
        p_name = f"{name}_Panel_{p_cfg['side']}"
        mesh = bpy.data.meshes.new(f"{p_name}_Mesh")
        obj = bpy.data.objects.new(p_name, mesh)
        context.collection.objects.link(obj)

        _build_curtain_panel_mesh(
            obj=obj,
            panel_width=p_cfg['width'],
            panel_height=eff_h,
            pleat_count=pleats,
            subdiv_per_pleat=subdiv_per_pleat,
            subdiv_y=subdiv_y,
            side=p_cfg['side'],
            center_x=p_cfg['center_x'],
            outer_x=p_cfg['outer_x'],
            side_flag=p_cfg['flag'],
            open_amount=cur_open,
            tied_back=tied_back,
            generate_shapekey=generate_shapekey,
            seed=seed + (p_idx * 31)
        )

        # 頂点グループ 'Pin'（上端固定ウェイト）の作成
        pin_group = obj.vertex_groups.new(name="Pin")
        pin_threshold = eff_h - 0.035
        for v in mesh.vertices:
            if v.co.z >= pin_threshold:
                pin_group.add([v.index], 1.0, 'REPLACE')
            elif v.co.z >= pin_threshold - 0.08:
                w_factor = (v.co.z - (pin_threshold - 0.08)) / 0.08
                pin_group.add([v.index], w_factor, 'REPLACE')

        # ファブリックマテリアル割り当て
        mat_fabric = create_curtain_fabric_material(
            mat_name=f"{name}_Fabric_Mat",
            fabric_type=fabric_type,
            seed=seed
        )
        obj.data.materials.append(mat_fabric)

        fabric_objs.append(obj)
        created_objs.append(obj)

    # 2. タッセル（束ね帯紐・房掛け金具）の生成
    if tied_back:
        tassel_obj = _build_curtain_tassels(
            context=context,
            name=f"{name}_Tassels",
            total_width=eff_w,
            height=eff_h,
            panel_configs=panel_configs,
            generate_shapekey=generate_shapekey,
            rod_style=rod_style
        )
        created_objs.append(tassel_obj)

    # 3. カーテンロッド（レール）＆ 金具の生成
    rod_obj = None
    if include_rod:
        rod_obj = _build_curtain_rod_and_rings(
            context=context,
            name=f"{name}_Rod_Hardware",
            total_width=eff_w,
            top_z=eff_h + 0.04,
            panel_configs=panel_configs,
            pleat_count=pleats,
            open_amount=cur_open,
            generate_shapekey=generate_shapekey,
            rod_style=rod_style
        )
        created_objs.append(rod_obj)

    # 4. Blender内 Cloth ＋ Wind Force シミュレーションの実行
    if simulate_wind and len(fabric_objs) > 0 and cur_open < 0.90:
        _run_curtain_wind_simulation(
            context=context,
            curtain_objs=fabric_objs,
            eff_height=eff_h,
            wind_strength=wind_strength,
            wind_direction=wind_direction,
            bake_to_static=bake_to_static
        )

    # 5. 単一Static Meshへの結合処理
    if combine and len(created_objs) > 1:
        final_obj = _combine_curtain_objects(context, created_objs, name)
        return final_obj
    else:
        context.view_layer.objects.active = created_objs[0]
        return created_objs[0]


def _calc_panel_vertex_coords(u_x, v_y, panel_width, panel_height, pleat_count, side, center_x, outer_x, open_amt, tied_back):
    """カーテン頂点の三次元座標を計算（滑らかなS字波打ち・アコーディオン圧縮・タッセルくびれ）"""
    half_w = panel_width * 0.5
    start_x_closed = center_x - half_w
    cur_z = v_y * panel_height

    # 1. 閉じた状態のX座標
    cur_x_closed = start_x_closed + (u_x * panel_width)

    # 2. 全開状態のX座標（外側端に向かってアコーディオン圧縮）
    compressed_w = panel_width * 0.22
    if side == 'LEFT':
        cur_x_opened = outer_x + (u_x * compressed_w) + 0.02
    else:
        cur_x_opened = outer_x - ((1.0 - u_x) * compressed_w) - 0.02

    # 開閉度によるX補間
    cur_x = cur_x_closed + (cur_x_opened - cur_x_closed) * open_amt

    # 3. 滑らかなS字プリーツ曲面（角張りのない柔らかな丸み）
    wave_phase = u_x * pleat_count * math.pi * 2.0
    
    # 布地のふっくらとした丸みを引き出す滑らかな波打ち
    sin_val = math.sin(wave_phase)
    # 開くほどヒダが重なり合って自然に前後に深みが増す
    pleat_depth = 0.045 * (1.0 + (0.50 * open_amt))
    cur_depth = pleat_depth * (0.85 + (0.35 * (1.0 - v_y)))
    cur_y = sin_val * cur_depth

    # 4. タッセル（束ね紐）によるくびれドレープ（tied_back=True時）
    if tied_back:
        z_norm = v_y
        dist_to_tassel = abs(z_norm - 0.42) / 0.45
        pinch = math.exp(- (dist_to_tassel ** 2) * 5.5)

        target_tassel_x = outer_x * 0.88
        cur_x = cur_x + (target_tassel_x - cur_x) * (pinch * 0.72)
        cur_y = cur_y * (1.0 - (pinch * 0.45))
        if v_y < 0.35:
            cur_x += (center_x - cur_x) * ((0.35 - v_y) * 0.25)

    return cur_x, cur_y, cur_z, wave_phase


def _build_curtain_panel_mesh(obj, panel_width, panel_height, pleat_count, subdiv_per_pleat, subdiv_y, side, center_x, outer_x, side_flag, open_amount=0.0, tied_back=False, generate_shapekey=True, seed=0):
    """
    プリーツ（ヒダ）付きカーテンパネルの生成、開閉変形、シェイプキー、および頂点カラーベイク
    """
    rng = random.Random(seed)
    mesh = obj.data
    bm = bmesh.new()

    # 水平方向の分割数を大幅に引き上げ、完全な滑らか円弧を実現
    subdiv_x = pleat_count * subdiv_per_pleat

    vert_grid = []
    vert_info_list = []
    basis_coords = []
    open_coords = []

    for iy in range(subdiv_y + 1):
        v_y = iy / float(subdiv_y)  # 0.0 (裾) ~ 1.0 (上端)
        
        row = []
        for ix in range(subdiv_x + 1):
            u_x = ix / float(subdiv_x)  # 0.0 ~ 1.0 (パネル内)

            cur_x, cur_y, cur_z, wave_phase = _calc_panel_vertex_coords(
                u_x, v_y, panel_width, panel_height, pleat_count,
                side, center_x, outer_x, open_amount, tied_back
            )

            # Basis: 完全密閉 0.0, Open: 全開 1.0 (tied_back反映)
            bx, by, bz, _ = _calc_panel_vertex_coords(
                u_x, v_y, panel_width, panel_height, pleat_count,
                side, center_x, outer_x, 0.0, False
            )
            ox, oy, oz, _ = _calc_panel_vertex_coords(
                u_x, v_y, panel_width, panel_height, pleat_count,
                side, center_x, outer_x, 1.0, tied_back
            )
            basis_coords.append((bx, by, bz))
            open_coords.append((ox, oy, oz))

            if side == 'LEFT':
                dist_to_center = 1.0 - u_x
            else:
                dist_to_center = u_x

            vert = bm.verts.new((cur_x, cur_y, cur_z))
            row.append(vert)

            info = {
                'v_y': v_y,
                'dist_to_center': max(0.0, min(1.0, 1.0 - dist_to_center)),
                'pleat_peak': (math.sin(wave_phase) + 1.0) * 0.5
            }
            vert_info_list.append(info)
        vert_grid.append(row)

    # 面の生成
    for iy in range(subdiv_y):
        for ix in range(subdiv_x):
            v1 = vert_grid[iy][ix]
            v2 = vert_grid[iy][ix + 1]
            v3 = vert_grid[iy + 1][ix + 1]
            v4 = vert_grid[iy + 1][ix]
            f = bm.faces.new((v1, v2, v3, v4))
            f.smooth = True

    bm.to_mesh(mesh)
    bm.free()

    # 頂点カラー属性
    color_layer = mesh.color_attributes.new(
        name="Col",
        type='FLOAT_COLOR',
        domain='CORNER'
    )

    for poly in mesh.polygons:
        for loop_idx in poly.loop_indices:
            v_idx = mesh.loops[loop_idx].vertex_index
            info = vert_info_list[v_idx] if v_idx < len(vert_info_list) else {'v_y': 1.0, 'dist_to_center': 0.5, 'pleat_peak': 0.5}

            r = 1.0 - info['v_y']
            g = info['dist_to_center']
            b = side_flag
            a = info['pleat_peak']

            color_layer.data[loop_idx].color = (r, g, b, a)

    mesh.update()

    # シェイプキー（Morph Target）
    if generate_shapekey:
        sk_basis = obj.shape_key_add(name="Basis", from_mix=False)
        for i, co in enumerate(basis_coords):
            if i < len(sk_basis.data):
                sk_basis.data[i].co = co

        sk_open = obj.shape_key_add(name="Open", from_mix=False)
        for i, co in enumerate(open_coords):
            if i < len(sk_open.data):
                sk_open.data[i].co = co

        sk_open.value = open_amount


def _build_curtain_tassels(context, name, total_width, height, panel_configs, generate_shapekey=True, rod_style='BRASS'):
    """壁掛けタッセルフックおよび帯紐ジオメトリを生成"""
    bm = bmesh.new()

    tassel_z = height * 0.42
    hook_radius = 0.012

    for p_cfg in panel_configs:
        side_sign = -1 if p_cfg['side'] == 'LEFT' else 1
        hook_x = side_sign * (total_width * 0.48)
        
        # 1. 壁固定の金属フック
        hook_mat = Matrix.Translation(Vector((hook_x, 0.01, tassel_z))) @ Matrix.Diagonal(Vector((0.02, 0.04, 0.04, 1.0)))
        bmesh.ops.create_cube(bm, size=1.0, matrix=hook_mat)

        # フック先端の飾り
        knob_mat = Matrix.Translation(Vector((hook_x + (side_sign * 0.02), 0.045, tassel_z)))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=hook_radius * 1.5, matrix=knob_mat)

        # 2. カーテンを束ねる帯紐
        loop_center = Vector((side_sign * (total_width * 0.44), 0.02, tassel_z))
        loop_mat = Matrix.Translation(loop_center) @ Matrix.Rotation(math.radians(90.0), 4, 'X')
        bmesh.ops.create_cone(
            bm,
            cap_ends=False,
            segments=16,
            radius1=0.065,
            radius2=0.065,
            depth=0.028,
            matrix=loop_mat
        )

        # 3. 房飾り
        fringe_mat = Matrix.Translation(Vector((hook_x, 0.04, tassel_z - 0.08))) @ Matrix.Diagonal(Vector((0.018, 0.018, 0.08, 1.0)))
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            cap_tris=False,
            segments=10,
            radius1=0.022,
            radius2=0.006,
            depth=0.10,
            matrix=fringe_mat
        )

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    col_layer = mesh.color_attributes.new(name="Col", type='FLOAT_COLOR', domain='CORNER')
    for loop_data in col_layer.data:
        loop_data.color = (0.0, 0.0, 0.5, 1.0)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    if generate_shapekey:
        obj.shape_key_add(name="Basis", from_mix=False)
        obj.shape_key_add(name="Open", from_mix=False)

    mat_tassel = create_curtain_rod_material(f"{name}_Mat", style=rod_style)
    obj.data.materials.append(mat_tassel)

    return obj


def _build_curtain_rod_and_rings(context, name, total_width, top_z, panel_configs, pleat_count, open_amount=0.0, generate_shapekey=True, rod_style='BRASS'):
    """カーテンロッド（棒）、エンドキャップ装飾、ブラケット、開閉連動リング金具を生成"""
    bm = bmesh.new()

    rod_radius = 0.014
    rod_length = total_width + 0.24

    # 1. メインロッド
    cyl_mat = Matrix.Translation(Vector((0, 0.015, top_z))) @ Matrix.Rotation(math.radians(90.0), 4, 'Y')
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=16,
        radius1=rod_radius,
        radius2=rod_radius,
        depth=rod_length,
        matrix=cyl_mat
    )

    # 2. 両端フィニアル
    for side in (-1, 1):
        finial_x = side * (rod_length * 0.5 + 0.02)
        finial_mat = Matrix.Translation(Vector((finial_x, 0.015, top_z)))
        bmesh.ops.create_icosphere(
            bm,
            subdivisions=2,
            radius=rod_radius * 1.75,
            matrix=finial_mat
        )

    # 3. 壁固定ブラケット
    for side in (-1, 1):
        brk_x = side * (total_width * 0.48)
        brk_mat = Matrix.Translation(Vector((brk_x, -0.01, top_z)))
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=brk_mat @ Matrix.Diagonal(Vector((0.022, 0.055, 0.035, 1.0)))
        )

    # 4. 各ヒダごとのカーテンリング金具
    ring_radius = rod_radius * 1.55
    ring_thick = 0.004
    for p_cfg in panel_configs:
        p_w = p_cfg['width']
        c_x = p_cfg['center_x']
        o_x = p_cfg['outer_x']
        side = p_cfg['side']

        step_x = p_w / float(pleat_count)
        start_rx = (c_x - p_w * 0.5) + (step_x * 0.5)

        comp_w = p_w * 0.22
        comp_step = comp_w / float(pleat_count)

        for i in range(pleat_count):
            rx_closed = start_rx + (i * step_x)
            if side == 'LEFT':
                rx_opened = (o_x + 0.02) + (i * comp_step)
            else:
                rx_opened = (o_x - 0.02) - ((pleat_count - 1 - i) * comp_step)

            rx = rx_closed + (rx_opened - rx_closed) * open_amount

            ring_mat = Matrix.Translation(Vector((rx, 0.015, top_z))) @ Matrix.Rotation(math.radians(90.0), 4, 'X')
            bmesh.ops.create_cone(
                bm,
                cap_ends=False,
                segments=12,
                radius1=ring_radius,
                radius2=ring_radius,
                depth=ring_thick * 2,
                matrix=ring_mat
            )

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    col_layer = mesh.color_attributes.new(name="Col", type='FLOAT_COLOR', domain='CORNER')
    for loop_data in col_layer.data:
        loop_data.color = (0.0, 0.0, 0.5, 1.0)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    context.collection.objects.link(obj)

    if generate_shapekey:
        obj.shape_key_add(name="Basis", from_mix=False)
        obj.shape_key_add(name="Open", from_mix=False)

    mat_rod = create_curtain_rod_material(f"{name}_Mat", style=rod_style)
    obj.data.materials.append(mat_rod)

    return obj


def _run_curtain_wind_simulation(context, curtain_objs, eff_height, wind_strength, wind_direction, bake_to_static):
    """Blender内部のClothシミュレーション ＋ Wind Force Field を実行"""
    scene = context.scene
    saved_frame = scene.frame_current

    dir_vec = Vector(wind_direction).normalized()
    wind_loc = Vector((0.10, -1.20, eff_height * 0.40))
    
    bpy.ops.object.effector_add(type='WIND', location=wind_loc)
    wind_obj = context.active_object
    wind_obj.name = "Temp_Curtain_Wind"
    
    rot_quat = Vector((0, 0, 1)).rotation_difference(dir_vec)
    wind_obj.rotation_euler = rot_quat.to_euler()
    wind_obj.field.strength = max(150.0, wind_strength * 8.0)
    wind_obj.field.noise = 1.2
    wind_obj.field.flow = 1.5

    bpy.ops.object.effector_add(type='TURBULENCE', location=(0.3, -0.4, eff_height * 0.35))
    turb_obj = context.active_object
    turb_obj.name = "Temp_Curtain_Turb"
    turb_obj.field.strength = 40.0
    turb_obj.field.size = 1.5

    for obj in curtain_objs:
        context.view_layer.objects.active = obj
        obj.select_set(True)

        mod = obj.modifiers.new(name="Curtain_Cloth", type='CLOTH')
        c_settings = mod.settings
        c_settings.vertex_group_mass = "Pin"
        c_settings.mass = 0.08
        c_settings.tension_stiffness = 8.0
        c_settings.compression_stiffness = 8.0
        c_settings.shear_stiffness = 3.0
        c_settings.bending_stiffness = 0.35
        c_settings.air_damping = 0.8
        c_settings.quality = 5

        mod.collision_settings.use_self_collision = True
        mod.collision_settings.self_distance_min = 0.008

    sim_frames = 50
    for f in range(1, sim_frames + 1):
        scene.frame_set(f)

    if bake_to_static:
        dg = context.evaluated_depsgraph_get()
        for obj in curtain_objs:
            obj_eval = obj.evaluated_get(dg)
            mesh_eval = bpy.data.meshes.new_from_object(obj_eval)
            
            old_mesh = obj.data
            obj.data = mesh_eval
            obj.modifiers.remove(obj.modifiers["Curtain_Cloth"])
            bpy.data.meshes.remove(old_mesh)

        bpy.data.objects.remove(wind_obj, do_unlink=True)
        bpy.data.objects.remove(turb_obj, do_unlink=True)
        scene.frame_set(saved_frame)


def _combine_curtain_objects(context, created_objs, final_name):
    """複数オブジェクトを1つのStatic Meshにマージ結合し、スマートUV展開"""
    bpy.ops.object.select_all(action='DESELECT')
    for obj in created_objs:
        obj.select_set(True)

    root_obj = created_objs[0]
    root_obj.name = final_name
    context.view_layer.objects.active = root_obj

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.join()

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

    return root_obj
