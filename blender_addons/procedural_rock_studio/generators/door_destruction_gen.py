import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

from ..utils.anim_baker import bake_object_group_to_shapekeys


def _duplicate_object(context, src_obj, new_name=None):
    """srcを複製し、親子関係を解除した独立オブジェクトとして返す(ワールド変換は維持)。"""
    bpy.ops.object.select_all(action='DESELECT')
    src_obj.select_set(True)
    context.view_layer.objects.active = src_obj
    bpy.ops.object.duplicate(linked=False)
    dup = context.view_layer.objects.active
    mw = dup.matrix_world.copy()
    dup.parent = None
    dup.matrix_world = mw
    if new_name:
        dup.name = new_name
    return dup


def _split_wood_and_iron(context, leaf_dup):
    """
    マテリアル境界で木部/鉄部を別オブジェクトに分離する（bpy.ops.mesh.separate(type='MATERIAL')を再利用）。
    separate後は各オブジェクトのマテリアルスロットが1つに圧縮され face.material_index は
    常に0にリナンバーされるため、スロット0のマテリアル名（"_Wood_Mat"/"_Iron_Mat"）で判定する。
    """
    bpy.ops.object.select_all(action='DESELECT')
    leaf_dup.select_set(True)
    context.view_layer.objects.active = leaf_dup
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='MATERIAL')
    bpy.ops.object.mode_set(mode='OBJECT')

    candidates = [leaf_dup] + [o for o in context.selected_objects if o != leaf_dup]
    wood_obj, iron_obj = None, None
    for o in candidates:
        if not o.data.materials or o.data.materials[0] is None:
            continue
        mat_name = o.data.materials[0].name
        if "_Wood_Mat" in mat_name:
            wood_obj = o
        elif "_Iron_Mat" in mat_name:
            iron_obj = o
    return wood_obj, iron_obj


def _setup_passive_collider(obj, friction=0.6, restitution=0.05):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.object_add()
    obj.rigid_body.type = 'PASSIVE'
    obj.rigid_body.collision_shape = 'MESH'
    obj.rigid_body.friction = friction
    obj.rigid_body.restitution = restitution


def _setup_active_shard(obj, mass=0.4, friction=0.15, restitution=0.20, linear_damping=0.02, angular_damping=0.03):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.rigidbody.object_add()
    rb = obj.rigid_body
    rb.type = 'ACTIVE'
    rb.collision_shape = 'CONVEX_HULL'
    rb.collision_margin = 0.001
    rb.mass = mass
    rb.friction = friction
    rb.restitution = restitution
    rb.linear_damping = linear_damping
    rb.angular_damping = angular_damping


def generate_door_destruction(
    context,
    leaf_obj_l,
    leaf_obj_r,
    frame_obj=None,
    shard_count=20,
    frame_count=70,
    sample_step=2,
    impact_strength=1.0,
    impact_frames=4,
    subdivide_cuts=2,
    seed=0,
    name="Door_Destruction"
):
    """
    Door_Leaf_L / Door_Leaf_R を木っ端微塵に砕け散らせ、その様子をシェイプキー(頂点キャッシュ的)
    アニメーションとして1つの結合メッシュに焼き付ける。UnrealEngineへFBX(bake_anim)で持ち込む用途。

    - 木部(wood material)のみを Cell Fracture で破片化し、Rigid Body で物理シミュレーション
    - 鉄金具(iron material: 帯金具・鋲・縁取り・取っ手)は木部のように細切れにはせず、
      左右リーフそれぞれ1つの塊のまま吹き飛ばす（現実の鍛鉄帯が紙吹雪のように砕け散ることはないため）
    - Door_Frame（石造アーチ）は破壊対象に含めず、破片の衝突コライダー(PASSIVE)としてのみ使用
    - impact_strength: 衝撃点からの飛散距離の強さ（目安0.5〜2.0）。密着した破片は摩擦で
      固まって動かないため、最初の impact_frames の間だけキネマティックで強制的に弾き飛ばし、
      以降はRigid Bodyの重力・衝突に引き渡して自然に落下・転がらせる
    """
    rng = random.Random(seed)
    scene = context.scene
    saved_frame = scene.frame_current

    # 0. Cell Fracture アドオンの有効化（bpy.ops は属性アクセス時点では存在チェックにならないため、
    #    hasattr判定はせず常に addon_enable を試みる。既に有効な場合は無害な no-op）
    try:
        bpy.ops.preferences.addon_enable(module="object_fracture_cell")
    except Exception as e:
        raise RuntimeError(f"Cell Fracture アドオン(object_fracture_cell)を有効化できませんでした: {e}")

    if frame_obj is None:
        frame_obj = leaf_obj_l.parent

    tracked_objects = []   # 破片オブジェクトのリスト。結合順を固定するため追加順を保持
    passive_objs = []

    # 1. 一時床コライダー
    bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
    floor_obj = context.active_object
    floor_obj.name = "Temp_Destruction_Floor"
    _setup_passive_collider(floor_obj, friction=0.7, restitution=0.05)
    passive_objs.append(floor_obj)

    # 2. 石枠(Door_Frame)を衝突コライダーとして追加（破壊対象には含めない）
    if frame_obj is not None:
        _setup_passive_collider(frame_obj, friction=0.5, restitution=0.05)
        passive_objs.append(frame_obj)

    impact_centers = []

    for leaf_obj, side_name in ((leaf_obj_l, "L"), (leaf_obj_r, "R")):
        if leaf_obj is None:
            continue
        leaf_dup = _duplicate_object(context, leaf_obj, new_name=f"{name}_{side_name}_Dup")

        # 破片の頂点密度を確保するため、木部の押し出しソリッドを軽くサブディビジョン
        bpy.ops.object.select_all(action='DESELECT')
        leaf_dup.select_set(True)
        context.view_layer.objects.active = leaf_dup
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        for _ in range(max(0, subdivide_cuts)):
            bpy.ops.mesh.subdivide(number_cuts=1, smoothness=0.0)
        bpy.ops.object.mode_set(mode='OBJECT')

        wood_obj, iron_obj = _split_wood_and_iron(context, leaf_dup)
        if wood_obj is None:
            continue

        bbox_world = [wood_obj.matrix_world @ Vector(c) for c in wood_obj.bound_box]
        center = sum(bbox_world, Vector()) / 8.0
        impact_centers.append(center)

        # 3. 木部をCell Fractureで破片化
        bpy.ops.object.select_all(action='DESELECT')
        wood_obj.select_set(True)
        context.view_layer.objects.active = wood_obj
        bpy.ops.object.add_fracture_cell_objects(
            source={'VERT_OWN'},
            source_limit=max(4, shard_count),
            source_noise=0.20,
            cell_scale=(1.0, 1.0, 1.0),
            recursion=0,
            use_smooth_faces=False,
            use_sharp_edges=True,
            use_sharp_edges_apply=True,
            use_data_match=True,
            use_island_split=True,
            margin=0.008,
            material_index=0,
            use_interior_vgroup=False,
            mass_mode='UNIFORM',
            mass=0.4,
            use_recenter=True,
            use_remove_original=True,
            collection_name="",
            use_debug_points=False,
            use_debug_redraw=False,
            use_debug_bool=False,
        )
        wood_shards = [o for o in context.selected_objects if o.type == 'MESH']
        for shard in wood_shards:
            shard.name = f"{name}_{side_name}_Shard_{len(tracked_objects):03d}"
            _setup_active_shard(shard, mass=rng.uniform(0.25, 0.55))
            tracked_objects.append(shard)

        # Cell Fractureは(level=0の)元オブジェクトを自動削除しないため、明示的に削除する
        if wood_obj.name in bpy.data.objects:
            bpy.data.objects.remove(wood_obj, do_unlink=True)

        # 4. 鉄金具は左右それぞれ1塊のまま剛体に（細切れにしない）
        if iron_obj is not None:
            iron_obj.name = f"{name}_{side_name}_IronAssembly"
            _setup_active_shard(iron_obj, mass=3.2, friction=0.4, restitution=0.20,
                                linear_damping=0.05, angular_damping=0.08)
            tracked_objects.append(iron_obj)

    if not tracked_objects:
        scene.frame_set(saved_frame)
        raise RuntimeError("破片オブジェクトが生成されませんでした")

    # 5. 初期(frame=1)姿勢を記録（シェイプキーのBasis=破壊前の組み上がった状態として使う）
    context.view_layer.update()
    initial_matrices = {o: o.matrix_world.copy() for o in tracked_objects}

    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    rw = scene.rigidbody_world
    orig_substeps = rw.substeps_per_frame
    orig_iters = rw.solver_iterations
    rw.substeps_per_frame = 20
    rw.solver_iterations = 20

    cur_frame = scene.frame_current
    release_frame = cur_frame + max(1, impact_frames)

    # 6. 密着したまま組み上がった破片は摩擦・噛み合いで固まって動かないため、
    # Rigid Body自体の物理演算ではなく、まず「キネマティック(直接アニメーション)」で
    # 衝撃点から放射状に強制的に弾き飛ばし、release_frameでダイナミクスへ引き渡して
    # 重力・床/石枠との衝突による自然な落下・転がりを続けさせる
    impact_point = sum(impact_centers, Vector()) / max(1, len(impact_centers))
    impact_point.y -= 0.35  # 扉の少し手前（外側）から打ち破られたイメージ

    for o in tracked_objects:
        bbox_world = [o.matrix_world @ Vector(c) for c in o.bound_box]
        obj_center = sum(bbox_world, Vector()) / 8.0
        outward = obj_center - impact_point
        dist = max(0.05, outward.length)
        outward = outward / dist
        # 衝撃点から一様に押すだけだと近隣の破片同士が同じ方向へまとまって動き、
        # 密着したまま「塊」に見えてしまうため、ランダム方向を大きく混ぜてバラバラの
        # 飛散方向にする（本物の木っ端微塵の破片飛散に近づける）
        rand_dir = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.2, 1.0))).normalized()
        outward = (outward * 0.35 + rand_dir * 0.65).normalized()

        rb = o.rigid_body
        rb.kinematic = True
        o.keyframe_insert(data_path="rigid_body.kinematic", frame=cur_frame)
        o.keyframe_insert(data_path="location", frame=cur_frame)
        o.keyframe_insert(data_path="rotation_euler", frame=cur_frame)

        # キネマティック→ダイナミクス引き渡し時の瞬間速度が暴走しないよう移動量は抑えつつ、
        # 近い/遠いによる差を小さくして「全体が均等に吹き飛ぶ」ようにする
        # （あとはRigid Bodyの重力・衝突・摩擦が自然に運動を続けてくれる）
        explosion_dist = impact_strength * (0.55 + rng.uniform(0.0, 0.45))
        explosion_dist = min(explosion_dist, 1.3)  # 極端な飛び過ぎを防ぐ上限
        o.location = o.location + outward * explosion_dist
        o.rotation_euler.x += math.radians(rng.uniform(-160, 160))
        o.rotation_euler.y += math.radians(rng.uniform(-160, 160))
        o.rotation_euler.z += math.radians(rng.uniform(-160, 160))
        o.keyframe_insert(data_path="location", frame=release_frame)
        o.keyframe_insert(data_path="rotation_euler", frame=release_frame)

        rb.kinematic = False
        o.keyframe_insert(data_path="rigid_body.kinematic", frame=release_frame)

    # 7. シミュレーション実行 & サンプリング
    sampled = {}  # frame_index(0開始) -> {obj: matrix_world}
    sampled[0] = dict(initial_matrices)

    dg = context.evaluated_depsgraph_get()
    for f in range(cur_frame + 1, cur_frame + frame_count + 1):
        scene.frame_set(f)
        rel = f - cur_frame
        if rel % sample_step == 0 or rel == frame_count:
            dg = context.evaluated_depsgraph_get()
            sampled[rel] = {o: o.evaluated_get(dg).matrix_world.copy() for o in tracked_objects}

    # 8. 後始末：剛体コンポーネント除去、姿勢をframe=1に戻す
    for o in tracked_objects + passive_objs:
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        context.view_layer.objects.active = o
        try:
            bpy.ops.rigidbody.object_remove()
        except Exception:
            pass
    for o in tracked_objects:
        o.matrix_world = initial_matrices[o]

    bpy.data.objects.remove(floor_obj, do_unlink=True)
    if frame_obj is not None:
        # フレーム自体はシーンに残す(破壊対象ではないため削除しない)
        pass
    rw.substeps_per_frame = orig_substeps
    rw.solver_iterations = orig_iters
    scene.frame_set(saved_frame)

    # 9. 結合(intact姿勢のまま) → シェイプキー焼き付け
    # bpy.ops.object.join() は内部の結合順序が選択順と一致する保証がないため使わず、
    # 自前のbmeshで「orderリストの順序どおり」に頂点・面をワールド座標のまま積み上げる
    # （どの頂点範囲がどの元オブジェクトかを100%確定させるため）
    order = list(tracked_objects)

    combined_bm = bmesh.new()
    combined_materials = []
    mat_to_slot = {}
    vertex_ranges = []
    offset = 0

    for o in order:
        src_mesh = o.data
        mw = initial_matrices[o]
        vmap = {}
        for v in src_mesh.vertices:
            nv = combined_bm.verts.new(mw @ v.co)
            vmap[v.index] = nv
        combined_bm.verts.ensure_lookup_table()

        src_mat = o.data.materials[0] if o.data.materials else None
        if src_mat not in mat_to_slot:
            mat_to_slot[src_mat] = len(combined_materials)
            combined_materials.append(src_mat)
        slot_idx = mat_to_slot[src_mat]

        for poly in src_mesh.polygons:
            try:
                f = combined_bm.faces.new([vmap[vi] for vi in poly.vertices])
                f.material_index = slot_idx
                f.smooth = poly.use_smooth
            except ValueError:
                pass  # 縮退/重複面はスキップ

        vc = len(src_mesh.vertices)
        vertex_ranges.append((o, offset, offset + vc))
        offset += vc

    combined_bm.normal_update()
    combined_mesh = bpy.data.meshes.new(f"{name}_Mesh")
    combined_bm.to_mesh(combined_mesh)
    combined_bm.free()

    combined_obj = bpy.data.objects.new(name, combined_mesh)
    context.collection.objects.link(combined_obj)
    for m in combined_materials:
        combined_mesh.materials.append(m)
    # ワールド空間の座標をそのまま頂点に書き込んだので、オブジェクト変換は単位行列のまま運用する
    combined_obj.matrix_world = Matrix.Identity(4)
    bpy.ops.object.select_all(action='DESELECT')
    combined_obj.select_set(True)
    context.view_layer.objects.active = combined_obj

    for o in order:
        bpy.data.objects.remove(o, do_unlink=True)

    frames_sorted = sorted(sampled.keys())
    action = bake_object_group_to_shapekeys(
        combined_obj,
        vertex_ranges=vertex_ranges,
        sampled_frames=frames_sorted,
        sampled_transforms=sampled,
        frame_offset=1
    )

    scene.frame_start = 1
    scene.frame_end = max(frames_sorted) + 1
    scene.frame_set(1)

    return combined_obj, action
