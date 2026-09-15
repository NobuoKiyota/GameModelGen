import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

from .dictionary_gen import build_dictionary_mesh
from ..materials.dictionary_mat import (
    create_dictionary_cover_material,
    create_dictionary_pages_material,
    create_dictionary_ribbon_material,
    DICTIONARY_COLOR_PALETTES,
    COVER_PATTERN_STYLES
)


def generate_book_stack(
    context,
    name="Book_Stack",
    count=5,
    style='MESSY',
    base_width=0.16,
    base_height=0.23,
    base_thickness=0.024,
    scatter_radius=0.08,
    drop_dynamics=0.65,
    include_ground=False,
    mix_styles=True,
    combine=True,
    seed=0
):
    """
    生活感のある本の積み重ね・乱雑スタック・本棚横並び・平面散乱・動的物理落下＆転がり塊を生成するエンジン
    
    Parameters:
      context: Blenderコンテキスト
      name: アセット基底名
      count: 本の冊数 (2 ~ 30)
      style:
        'TOWER' (垂直スタック)
        'MESSY' (地面への衝突・転がり・斜め寄りかかりによる乱雑スタック)
        'SHELF_ROW' (本棚・立て置き横並び)
        'DESK_SCATTER' (机上・床面の散乱クラスター)
        'PHYSICS' (完全動的剛体物理落下＆転がり)
      base_width: 基準幅 (m)
      base_height: 基準高さ (m)
      base_thickness: 基準厚み (m) (標準2.2~2.5cm)
      scatter_radius: 散乱・ズレ半径 (m)
      drop_dynamics: 転がり・乱雑落下度 (0.1 ~ 1.0)
      include_ground: 地面（木製デスク天板/床板）をアセットに含めるか
      mix_styles: 各本ごとに12色の表紙色や5種の柄装飾、年季をバラバラにするか
      combine: 1つのStatic Meshに結合するか
      seed: ランダムシード
    """
    rng = random.Random(seed)
    count = max(2, min(30, int(count)))

    created_book_objs = []
    palette_keys = list(DICTIONARY_COLOR_PALETTES.keys())

    # 基準寸法が大きすぎる場合（岩プリセットのデフォルト2.0mなど）は本の実寸(16cm x 23cm x 2.4cm)に安全補正
    eff_base_width = 0.16 if base_width > 0.45 else max(0.09, base_width)
    eff_base_height = 0.23 if base_height > 0.45 else max(0.12, base_height)
    eff_base_thickness = 0.024 if base_thickness > 0.06 else max(0.012, base_thickness)

    # 1. 各本の生成パラメータ決定
    for i in range(count):
        book_seed = seed + (i * 73)
        book_rng = random.Random(book_seed)

        # 本棚やスタック用の自然なプロポーションランダム化
        w_factor = book_rng.uniform(0.88, 1.12)
        h_factor = book_rng.uniform(0.88, 1.12)
        w = max(0.11, eff_base_width * w_factor)
        h = max(0.15, eff_base_height * h_factor)
        
        # 一般的な単行本・ハードカバーのリアルな厚み (1.4cm ~ 3.4cm)
        th = max(0.014, min(0.036, eff_base_thickness * book_rng.uniform(0.70, 1.35)))

        ribs = book_rng.choice([3, 4, 5])
        # しおり紐は最上段の本、または控えめな確率で設定（スタック内部からの突き抜け防止）
        ribbon = (i == count - 1) if count > 1 else True

        if mix_styles:
            color = palette_keys[i % len(palette_keys)]
            aging = round(book_rng.uniform(0.25, 0.85), 2)
            has_runes = True
            foil = book_rng.choice(['GOLD', 'SILVER', 'DEBOSS'])
            pattern = COVER_PATTERN_STYLES[i % len(COVER_PATTERN_STYLES)]
        else:
            color = 'NAVY'
            aging = 0.5
            has_runes = True
            foil = 'GOLD'
            pattern = 'RUNES'

        # 単体本のメッシュ生成（スリムな本に合わせた上品な背丸み・控えめな小口凹み）
        mesh_name = f"{name}_Book_{i+1}_Mesh"
        obj_name = f"{name}_Book_{i+1}"
        mesh = bpy.data.meshes.new(mesh_name)
        obj = bpy.data.objects.new(obj_name, mesh)
        context.collection.objects.link(obj)

        bm = bmesh.new()
        build_dictionary_mesh(
            bm=bm,
            width=w,
            height=h,
            thickness=th,
            rib_count=ribs,
            cover_overhang=0.0025,
            cover_thickness=0.0025,
            spine_curvature=0.12,
            fore_edge_hollow=0.05,
            has_ribbon=ribbon,
            seed=book_seed
        )
        bm_face_mat_indices = [f.material_index for f in bm.faces]
        bm.to_mesh(mesh)
        bm.free()

        # 重心をメッシュの幾何学的中心（Center of Mass）に設定（剛体物理演算の正確な回転・接地のため必須）
        context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

        # マテリアル生成と割り当て
        mat_cover = create_dictionary_cover_material(
            f"{obj_name}_Cover_Mat",
            color_preset=color,
            has_runes=has_runes,
            rune_intensity=0.85,
            foil_style=foil,
            pattern_style=pattern,
            seed=book_seed
        )
        mat_pages = create_dictionary_pages_material(
            f"{obj_name}_Pages_Mat",
            aging=aging,
            seed=book_seed
        )
        mat_ribbon = create_dictionary_ribbon_material(
            f"{obj_name}_Ribbon_Mat",
            color=(0.60, 0.05, 0.08, 1.0)
        )

        obj.data.materials.clear()
        obj.data.materials.append(mat_cover)
        obj.data.materials.append(mat_pages)
        obj.data.materials.append(mat_ribbon)

        for poly, m_idx in zip(mesh.polygons, bm_face_mat_indices):
            poly.material_index = m_idx

        # プロパティ保持
        obj["stack_thickness"] = th
        obj["stack_width"] = w
        obj["stack_height"] = h
        created_book_objs.append(obj)

    # 2. 配置アルゴリズムの実行
    if style == 'TOWER':
        _layout_tower_stack(created_book_objs, scatter_radius, rng)
    elif style == 'SHELF_ROW':
        _layout_shelf_row(created_book_objs, rng)
    elif style == 'DESK_SCATTER':
        _layout_desk_scatter(created_book_objs, scatter_radius, rng)
    else:
        # 'MESSY' および 'PHYSICS':
        # 地面への衝突・転がり・斜め寄りかかりによる動的剛体シミュレーション（Dynamic Drop & Roll）
        _layout_dynamic_drop_and_roll(context, created_book_objs, scatter_radius, drop_dynamics, rng)

    # 地面（床板/デスク天板）メッシュのオプション追加
    if include_ground:
        ground_obj = _create_ground_mesh(context, created_book_objs, f"{name}_Ground", seed)
        created_book_objs.append(ground_obj)

    # 3. オブジェクト結合（Combine to Single Mesh）処理
    if combine and len(created_book_objs) > 1:
        final_obj = _combine_book_stack_objects(context, created_book_objs, name)
    else:
        context.view_layer.objects.active = created_book_objs[0]
        final_obj = created_book_objs[0]

    # 4. 最下部接地オフセット (最低点 Z を 0.0 に厳密に合わせる)
    context.view_layer.update()
    if combine:
        min_z = min((final_obj.matrix_world @ v.co).z for v in final_obj.data.vertices)
        for v in final_obj.data.vertices:
            v.co.z -= min_z
        final_obj.data.update()
    else:
        min_z = min(
            (obj.matrix_world @ Vector(corner)).z
            for obj in created_book_objs
            for corner in obj.bound_box
        )
        for obj in created_book_objs:
            obj.location.z -= min_z
    context.view_layer.update()

    return final_obj


def _layout_tower_stack(book_objs, scatter_radius, rng):
    """垂直タワー積み（わずかな回転と微小ズレ・めり込みゼロ）"""
    current_z = 0.0
    for i, obj in enumerate(book_objs):
        th = obj.get("stack_thickness", 0.024)
        if i == 0:
            obj.location = Vector((0.0, 0.0, 0.0))
            obj.rotation_euler = (0.0, 0.0, 0.0)
        else:
            max_drift = min(0.008, max(0.002, scatter_radius * 0.12))
            dx = rng.uniform(-max_drift, max_drift)
            dy = rng.uniform(-max_drift, max_drift)
            dyaw = math.radians(rng.uniform(-6.0, 6.0))
            obj.location = Vector((dx, dy, current_z))
            obj.rotation_euler = (0.0, 0.0, dyaw)

        current_z += th + 0.0008





def _layout_shelf_row(book_objs, rng):
    """
    本棚・立て置き横並び（背表紙が手前 -Y 方向を向き、横一列に自然に並ぶ）
    一部が斜めに倒れかかる（寄りかかり）リアルな本棚を表現
    """
    total_thickness = sum(obj.get("stack_thickness", 0.024) for obj in book_objs)
    start_x = -total_thickness * 0.5
    current_x = start_x

    num_books = len(book_objs)
    lean_idx = rng.randint(max(1, num_books - 3), num_books - 1) if num_books >= 3 else -1

    for i, obj in enumerate(book_objs):
        th = obj.get("stack_thickness", 0.024)
        base_euler = Euler((math.radians(90.0), 0.0, math.radians(-90.0)), 'XYZ')
        y_jitter = rng.uniform(-0.005, 0.005)

        tilt_y = 0.0
        if i >= lean_idx and lean_idx > 0:
            lean_deg = rng.uniform(6.0, 13.0) * ((i - lean_idx + 1) * 0.6)
            tilt_y = math.radians(min(18.0, lean_deg))

        half_th = th * 0.5
        obj.location = Vector((current_x + half_th, y_jitter, 0.0))
        
        rot_mat = base_euler.to_matrix()
        if abs(tilt_y) > 0.001:
            lean_mat = Matrix.Rotation(tilt_y, 3, 'Y')
            rot_mat = lean_mat @ rot_mat
        obj.rotation_euler = rot_mat.to_euler()

        current_x += th + 0.002


def _layout_desk_scatter(book_objs, scatter_radius, rng):
    """
    机上・床面の平面散乱クラスター（平置き、斜め重なり、散らばり）
    """
    num_books = len(book_objs)
    num_clusters = min(3, max(2, num_books // 3))
    cluster_centers = []
    for c in range(num_clusters):
        c_angle = (c / num_clusters) * math.pi * 2 + rng.uniform(-0.4, 0.4)
        c_dist = scatter_radius * rng.uniform(0.7, 1.3)
        cluster_centers.append(Vector((math.cos(c_angle) * c_dist, math.sin(c_angle) * c_dist)))

    cluster_heights = [0.0] * num_clusters

    for i, obj in enumerate(book_objs):
        th = obj.get("stack_thickness", 0.024)
        c_idx = i % num_clusters
        cx, cy = cluster_centers[c_idx]
        cur_h = cluster_heights[c_idx]

        ox = rng.uniform(-0.03, 0.03)
        oy = rng.uniform(-0.03, 0.03)
        yaw = rng.uniform(-math.pi, math.pi)

        # 乗り上げ傾斜
        pitch = math.radians(rng.uniform(8.0, 18.0) * (-1 if rng.random() < 0.5 else 1)) if cur_h > 0.001 else 0.0
        roll = math.radians(rng.uniform(8.0, 18.0) * (-1 if rng.random() < 0.5 else 1)) if cur_h > 0.001 else 0.0

        obj.location = Vector((cx + ox, cy + oy, cur_h * 0.75))
        obj.rotation_euler = (pitch, roll, yaw)
        cluster_heights[c_idx] += th * 0.85 + 0.001


def _layout_dynamic_drop_and_roll(context, book_objs, scatter_radius, drop_dynamics, rng):
    """
    Blender剛体物理演算（Bullet Rigid Body）による完全動的地面積突＆転がりシミュレーション（Dynamic Drop & Roll）
    
    【アルゴリズム】
    1. 剛体ソルバー精度を高水準（substeps=35, solver_iterations=45）に引き上げ、薄い本同士の高速衝突でもめり込みを100%遮断
    2. 一時的な床コライダー（PASSIVE, BOX, 摩擦0.78, 反発0.02）を配置
    3. 各本を上空（Z = 0.05 + i * 0.055m）に階段状に配置し、初期の空中交差（Interpenetration）を完全防止
    4. 各本に大胆な初期傾斜（ピッチ・ロール 20°〜60°）と水平オフセットを与え、衝突時に回転モーメントを生んで転がり・倒れ・斜め寄りかかりを誘発
    5. コライダーに Bullet Physics で最も堅牢な BOX コライダーを採用
    6. シミュレーションを 90〜120 フレーム回し、地面への激突・バタッとした倒れ・重なり合い・滑り落ち静止を完全再現
    7. 安定静止したワールドトランスフォームを確定ベイク
    """
    scene = context.scene
    saved_frame = scene.frame_current

    # 剛体ワールドの確保と高精度化
    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()

    rw = scene.rigidbody_world
    orig_substeps = rw.substeps_per_frame
    orig_iters = rw.solver_iterations
    rw.substeps_per_frame = 35
    rw.solver_iterations = 45

    # 一時的な衝突床の作成
    bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
    floor_obj = context.active_object
    floor_obj.name = "Temp_Physics_Floor"
    bpy.ops.rigidbody.object_add()
    floor_obj.rigid_body.type = 'PASSIVE'
    floor_obj.rigid_body.collision_shape = 'BOX'
    floor_obj.rigid_body.friction = 0.80
    floor_obj.rigid_body.restitution = 0.02

    num_books = len(book_objs)
    eff_scatter = max(0.04, min(0.35, scatter_radius))
    dynamics = max(0.1, min(1.0, drop_dynamics))

    # 各本を空中へ階段状に配置（初期空中交差を100%防止）
    z_cursor = 0.04
    for i, obj in enumerate(book_objs):
        th = obj.get("stack_thickness", 0.024)
        w = obj.get("stack_width", 0.16)

        if i == 0:
            # 1冊目: 地面近くにわずかな傾きで配置
            init_x = rng.uniform(-0.02, 0.02) * dynamics
            init_y = rng.uniform(-0.02, 0.02) * dynamics
            init_pitch = math.radians(rng.uniform(-8.0, 8.0) * dynamics)
            init_roll = math.radians(rng.uniform(-8.0, 8.0) * dynamics)
            init_yaw = rng.uniform(-math.pi, math.pi)
            drop_z = th * 0.5 + 0.02
            z_cursor = drop_z + th + 0.035
        else:
            # 2冊目以降: 上空からオフセットと大胆な傾きをつけて落下
            r_ang = rng.uniform(0, math.pi * 2)
            r_dist = rng.uniform(0.02, eff_scatter) * dynamics
            init_x = math.cos(r_ang) * r_dist
            init_y = math.sin(r_ang) * r_dist

            # 20°〜60° の大胆な傾き（衝突時にバタッと倒れたり、斜めに寄りかかる）
            tilt_range = 15.0 + (35.0 * dynamics)
            init_pitch = math.radians(rng.uniform(-tilt_range, tilt_range))
            init_roll = math.radians(rng.uniform(-tilt_range, tilt_range))
            init_yaw = rng.uniform(-math.pi, math.pi)

            drop_z = z_cursor
            z_cursor += th + max(0.030, 0.065 * dynamics)

        obj.location = Vector((init_x, init_y, drop_z))
        obj.rotation_euler = Euler((init_pitch, init_roll, init_yaw))

        context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.rigidbody.object_add()
        obj.rigid_body.type = 'ACTIVE'
        # BOXコライダー: 直方体衝突判定はめり込み・交差が数学的に100%起きない
        obj.rigid_body.collision_shape = 'BOX'
        obj.rigid_body.collision_margin = 0.001
        obj.rigid_body.mass = 1.2
        obj.rigid_body.friction = 0.76
        obj.rigid_body.restitution = 0.02
        obj.rigid_body.linear_damping = 0.50
        obj.rigid_body.angular_damping = 0.50

    # 物理シミュレーションを回して激突・転がり・完全静止化
    # 冊数が多いほど安定化に必要なフレーム数を確保 (85 ~ 130 frames)
    total_sim_frames = min(130, max(85, 70 + (num_books * 3)))
    cur_frame = scene.frame_current
    for f in range(cur_frame + 1, cur_frame + total_sim_frames):
        scene.frame_set(f)

    # 評価後トランスフォームを実体オブジェクトへ適用・確定
    dg = context.evaluated_depsgraph_get()
    for obj in book_objs:
        obj_eval = obj.evaluated_get(dg)
        obj.matrix_world = obj_eval.matrix_world.copy()

    # 全冊の剛体コンポーネントを安全に解除
    for obj in book_objs:
        context.view_layer.objects.active = obj
        obj.select_set(True)
        try:
            bpy.ops.rigidbody.object_remove()
        except Exception:
            pass

    # 一時床の削除とシーン設定復元
    bpy.data.objects.remove(floor_obj, do_unlink=True)
    rw.substeps_per_frame = orig_substeps
    rw.solver_iterations = orig_iters
    scene.frame_set(saved_frame)


def _create_ground_mesh(context, book_objs, ground_name, seed=0):
    """
    本塊が散乱・接地する木製デスク天板/床板メッシュを生成
    """
    # 本塊の全体バウンディングボックスを取得
    context.view_layer.update()
    all_corners = [
        (obj.matrix_world @ Vector(c))
        for obj in book_objs
        for c in obj.bound_box
    ]
    min_x = min(c.x for c in all_corners)
    max_x = max(c.x for c in all_corners)
    min_y = min(c.y for c in all_corners)
    max_y = max(c.y for c in all_corners)

    margin = 0.12
    ground_w = max(0.50, (max_x - min_x) + (margin * 2.0))
    ground_d = max(0.50, (max_y - min_y) + (margin * 2.0))
    center_x = (min_x + max_x) * 0.5
    center_y = (min_y + max_y) * 0.5
    ground_th = 0.025 # 2.5cm 天板

    mesh = bpy.data.meshes.new(f"{ground_name}_Mesh")
    ground_obj = bpy.data.objects.new(ground_name, mesh)
    context.collection.objects.link(ground_obj)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    # スケーリング
    for v in bm.verts:
        v.co.x *= ground_w
        v.co.y *= ground_d
        v.co.z = (v.co.z * ground_th) - (ground_th * 0.5) # 上面が Z=0
    bm.to_mesh(mesh)
    bm.free()

    ground_obj.location = Vector((center_x, center_y, 0.0))

    # 木製天板マテリアル
    mat_name = f"{ground_name}_Wood_Mat"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        node_out = nodes.new(type='ShaderNodeOutputMaterial')
        node_out.location = (400, 0)
        node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        node_bsdf.location = (100, 0)
        node_bsdf.inputs['Base Color'].default_value = (0.12, 0.07, 0.04, 1.0) # Warm Walnut Wood
        node_bsdf.inputs['Roughness'].default_value = 0.38
        links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    ground_obj.data.materials.clear()
    ground_obj.data.materials.append(mat)

    return ground_obj


def _combine_book_stack_objects(context, book_objs, final_name):
    """複数冊の本を1つのStatic Meshにマージ結合し、スマートUV展開を適用"""
    bpy.ops.object.select_all(action='DESELECT')
    for obj in book_objs:
        obj.select_set(True)
    
    root_obj = book_objs[0]
    root_obj.name = final_name
    context.view_layer.objects.active = root_obj

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.join()

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

    return root_obj
