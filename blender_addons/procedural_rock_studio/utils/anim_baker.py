import bpy
import os
from mathutils import Vector, Matrix, Quaternion

from .uv_tools import assign_box_uv

def bake_water_modifiers_to_shapekeys(obj, frames_count=60, step=3):
    """水面のモディファイアアニメーションをシェイプキー（Blendshapes）とActionにベイク"""
    if not obj or obj.type != 'MESH':
        return None

    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()

    # 1. 元のベースメッシュ（Basis）の作成
    if not obj.data.shape_keys:
        obj.shape_key_add(name="Basis", from_mix=False)
    
    key_blocks = obj.data.shape_keys.key_blocks
    
    # 2. 各フレームの変形をシェイプキーとして登録
    sampled_frames = list(range(1, frames_count + 1, step))
    if sampled_frames[-1] != frames_count:
        sampled_frames.append(frames_count)

    shape_names = []
    for f in sampled_frames:
        scene.frame_set(f)
        eval_obj = obj.evaluated_get(depsgraph)
        eval_mesh = eval_obj.to_mesh()

        # 新規シェイプキー作成
        sk_name = f"Wave_Frame_{f:03d}"
        sk = obj.shape_key_add(name=sk_name, from_mix=False)
        shape_names.append((f, sk_name))

        # 評価された頂点座標をシェイプキーにコピー
        for vi, v in enumerate(eval_mesh.vertices):
            if vi < len(sk.data):
                sk.data[vi].co = v.co

        eval_obj.to_mesh_clear()

    # 3. アクション（アニメーションキーフレーム）の作成
    if not obj.data.shape_keys.animation_data:
        obj.data.shape_keys.animation_data_create()

    action = bpy.data.actions.new(name=obj.name + "_WaterLoopAction")
    obj.data.shape_keys.animation_data.action = action

    # 4. 各シェイプキーに 0.0 -> 1.0 -> 0.0 のキーフレームを設定
    for idx, (f, sk_name) in enumerate(shape_names):
        sk = key_blocks[sk_name]
        
        # 前のフレームで 0.0
        if idx > 0:
            prev_f = shape_names[idx - 1][0]
            sk.value = 0.0
            sk.keyframe_insert(data_path='value', frame=prev_f)
        else:
            # 最初のキーはループ終端と連動
            sk.value = 0.0
            sk.keyframe_insert(data_path='value', frame=frames_count)

        # 該当フレームで 1.0
        sk.value = 1.0
        sk.keyframe_insert(data_path='value', frame=f)

        # 次のフレームで 0.0
        if idx < len(shape_names) - 1:
            next_f = shape_names[idx + 1][0]
            sk.value = 0.0
            sk.keyframe_insert(data_path='value', frame=next_f)
        else:
            # 最後のキーはフレーム1で 0.0
            sk.value = 0.0
            sk.keyframe_insert(data_path='value', frame=1)

    # 5. モディファイアを削除（シェイプキーで完全に動くため）
    for mod in list(obj.modifiers):
        if mod.type in ('OCEAN', 'WAVE', 'DISPLACE'):
            obj.modifiers.remove(mod)

    # アニメーション範囲の設定
    scene.frame_start = 1
    scene.frame_end = frames_count
    scene.frame_set(1)

    return action


def bake_object_group_to_shapekeys(combined_obj, vertex_ranges, sampled_frames, sampled_transforms, frame_offset=1):
    """
    複数オブジェクトを結合してできた1つのメッシュに対し、各元オブジェクトのフレーム別
    ワールド変換の差分をシェイプキー(頂点キャッシュ的)アニメーションとして焼き付ける。
    水面ループ用の bake_water_modifiers_to_shapekeys と同じ「各サンプルフレームに1つずつ
    シェイプキーを作り、そのフレームで1.0・前後フレームで0.0にする」方式だが、
    末尾をフレーム1へ戻すループ処理はせず、一回きりの再生（破壊アニメ向け）にしている。

    combined_obj: bpy.ops.object.join() 済みで、かつ transform_apply 済み（matrix_worldが単位行列）のメッシュ
    vertex_ranges: [(元オブジェクト, 開始頂点index, 終了頂点index), ...]（結合前に記録したもの）
    sampled_frames: 昇順のフレーム番号(相対値)リスト。先頭は破壊前(Basis)の姿勢を表す
    sampled_transforms: {フレーム番号(相対値): {元オブジェクト: matrix_world}}
    frame_offset: シーン上でキーフレームを打ち始めるフレーム番号（通常1）
    """
    mesh = combined_obj.data
    if not mesh.shape_keys:
        combined_obj.shape_key_add(name="Basis", from_mix=False)

    basis_frame = sampled_frames[0]
    basis_transforms = sampled_transforms[basis_frame]
    basis_coords = [v.co.copy() for v in mesh.vertices]

    if not mesh.shape_keys.animation_data:
        mesh.shape_keys.animation_data_create()
    action = bpy.data.actions.new(name=combined_obj.name + "_DestructionAction")
    mesh.shape_keys.animation_data.action = action

    key_blocks = mesh.shape_keys.key_blocks
    shape_names = []
    for f in sampled_frames[1:]:
        sk_name = f"Break_{f:04d}"
        sk = combined_obj.shape_key_add(name=sk_name, from_mix=False)
        transforms = sampled_transforms[f]
        for obj, start, end in vertex_ranges:
            m0 = basis_transforms.get(obj)
            mf = transforms.get(obj)
            if m0 is None or mf is None:
                continue
            delta = mf @ m0.inverted()
            for i in range(start, end):
                sk.data[i].co = delta @ basis_coords[i]
        shape_names.append((f, sk_name))

    # 各シェイプキーは自分のフレームで1.0、隣接フレームで0.0になるようキーフレーム化（頂点キャッシュ的挙動）
    for idx, (f, sk_name) in enumerate(shape_names):
        sk = key_blocks[sk_name]

        if idx == 0:
            sk.value = 0.0
            sk.keyframe_insert(data_path='value', frame=frame_offset)
        else:
            prev_f = shape_names[idx - 1][0]
            sk.value = 0.0
            sk.keyframe_insert(data_path='value', frame=frame_offset + prev_f)

        sk.value = 1.0
        sk.keyframe_insert(data_path='value', frame=frame_offset + f)

        if idx < len(shape_names) - 1:
            next_f = shape_names[idx + 1][0]
            sk.value = 0.0
            sk.keyframe_insert(data_path='value', frame=frame_offset + next_f)
        # 最後のシェイプキーは1.0を保持したまま（砕け散った後の状態で静止）

    for fc in action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'

    return action


def export_animated_water_fbx(obj, fbx_filepath, frames_count=60):
    """水面ループアニメーション付き FBX エクスポート（Unity/UE 完全対応）"""
    # 選択とアクティブ化
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # ディレクトリ作成
    os.makedirs(os.path.dirname(os.path.abspath(fbx_filepath)), exist_ok=True)

    # シェイプキーアニメーションベイク
    bake_water_modifiers_to_shapekeys(obj, frames_count=frames_count, step=3)

    # FBX エクスポート
    bpy.ops.export_scene.fbx(
        filepath=fbx_filepath,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        mesh_smooth_type='FACE',
        bake_anim=True,
        bake_anim_use_all_actions=True,
        bake_anim_use_nla_strips=False,
        bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0
    )
    return fbx_filepath


def bake_object_group_to_armature(combined_obj, vertex_ranges, sampled_frames, sampled_transforms,
                                  frame_offset=1, root_name="root", name_prefix="Shard"):
    """
    複数オブジェクトを結合したメッシュの各頂点範囲を、破片ごとに1本のボーンへ100%ウェイトで割り当て、
    各フレームの剛体運動をそのままボーンアニメーションとして焼き付ける（UEスケルタルメッシュ向け）。
    シェイプキー方式と違い、回転しながら飛ぶ破片がサンプル間の補間で歪む/縮むことがない。

    combined_obj の頂点座標と sampled_transforms の行列は「同じ空間」であること（呼び出し側で揃える）。
    sampled_frames[0] は破壊前の組み上がった姿勢（=rest姿勢）。
    ボーンは単一ルート `root`（UEのスケルトンは根が1本必須）＋各破片 `Shard_###`（parent=root）。
    戻り値: (armature_obj, action)
    """
    mesh = combined_obj.data
    basis_frame = sampled_frames[0]
    basis_transforms = sampled_transforms[basis_frame]

    arm_data = bpy.data.armatures.new(f"{combined_obj.name}_ArmatureData")
    arm_obj = bpy.data.objects.new(f"{combined_obj.name}_Armature", arm_data)
    bpy.context.collection.objects.link(arm_obj)

    # 破片ごとのボーン位置（頂点範囲の重心）
    centers = []
    for obj, start, end in vertex_ranges:
        c = Vector((0.0, 0.0, 0.0))
        n = max(1, end - start)
        for i in range(start, end):
            c += mesh.vertices[i].co
        centers.append(c / n)

    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    root_bone = arm_data.edit_bones.new(root_name)
    root_bone.head = Vector((0.0, 0.0, 0.0))
    root_bone.tail = Vector((0.0, 0.0, 0.1))
    bone_names = []
    for idx, c in enumerate(centers):
        bname = f"{name_prefix}_{idx:03d}"
        eb = arm_data.edit_bones.new(bname)
        eb.head = c
        eb.tail = c + Vector((0.0, 0.0, 0.05))
        eb.parent = root_bone
        eb.use_connect = False
        bone_names.append(bname)
    bpy.ops.object.mode_set(mode='OBJECT')

    # 頂点グループ（破片=ボーン、ウェイト1.0）＋Armatureモディファイア
    for bname, (obj, start, end) in zip(bone_names, vertex_ranges):
        vg = combined_obj.vertex_groups.new(name=bname)
        vg.add(list(range(start, end)), 1.0, 'REPLACE')
    mod = combined_obj.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm_obj
    combined_obj.parent = arm_obj

    # アニメーション（毎フレーム: location + rotation_quaternion）
    # 親(root)は基底姿勢固定なので、子のbasis = 子のrest^-1 @ (delta @ 子のrest)
    rest_mats = [arm_data.bones[bn].matrix_local.copy() for bn in bone_names]
    action = bpy.data.actions.new(name=f"{combined_obj.name}_BoneAction")
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = action

    frames = list(sampled_frames)
    fcurves = {}
    for bname in bone_names:
        pb = arm_obj.pose.bones[bname]
        pb.rotation_mode = 'QUATERNION'
        for prop, count in (("location", 3), ("rotation_quaternion", 4)):
            for comp in range(count):
                fc = action.fcurves.new(f'pose.bones["{bname}"].{prop}', index=comp, action_group=bname)
                fc.keyframe_points.add(len(frames))
                fcurves[(bname, prop, comp)] = fc

    prev_q = {}
    for fi, rel in enumerate(frames):
        transforms = sampled_transforms[rel]
        scene_frame = float(frame_offset + rel)
        for bname, (obj, start, end), rest in zip(bone_names, vertex_ranges, rest_mats):
            m0 = basis_transforms[obj]
            mf = transforms[obj]
            delta = mf @ m0.inverted()
            basis = rest.inverted() @ delta @ rest
            loc, quat, _scale = basis.decompose()
            pq = prev_q.get(bname)
            if pq is not None and pq.dot(quat) < 0.0:
                quat = Quaternion((-quat.w, -quat.x, -quat.y, -quat.z))
            prev_q[bname] = quat
            for comp in range(3):
                fc = fcurves[(bname, "location", comp)]
                fc.keyframe_points[fi].co = (scene_frame, loc[comp])
            for comp in range(4):
                fc = fcurves[(bname, "rotation_quaternion", comp)]
                fc.keyframe_points[fi].co = (scene_frame, quat[comp])

    for fc in fcurves.values():
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
        fc.update()

    return arm_obj, action


def _find_and_rename_conflicting(name):
    """`name` を使っている既存オブジェクトを一時退避リネームし、(obj, 元名) を返す。無ければ None。"""
    other = bpy.data.objects.get(name)
    if other is None:
        return None
    old = other.name
    other.name = old + "__tmp_export_rename"
    return other, old


def export_door_destruction_fbx(obj, fbx_filepath):
    """
    扉破壊アニメーションをFBXエクスポート（Unreal Engine持ち込み用）。
    - obj がArmature付き(ボーン方式)なら、スケルタルメッシュ＋ボーンアニメとして出力する
      （軸は Blender既定=-Y forward/Z up, Armatureオブジェクトは一時的に "Armature" 名・原点へ移して出力）
    - Armatureが無ければ従来どおりシェイプキーアニメとして出力する
    """
    os.makedirs(os.path.dirname(os.path.abspath(fbx_filepath)), exist_ok=True)
    arm_obj = obj.parent if (obj.parent and obj.parent.type == 'ARMATURE') else None

    common = dict(
        filepath=fbx_filepath,
        use_selection=True,
        global_scale=1.0,
        axis_forward='-Y',
        axis_up='Z',
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        use_armature_deform_only=False,
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_all_actions=False,
        bake_anim_use_nla_strips=False,
        bake_anim_force_startend_keying=True,
        bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0,
    )

    if arm_obj is None:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.export_scene.fbx(apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE',
                                 object_types={'MESH'}, **common)
        return fbx_filepath

    # スケルタルメッシュ: FBX_SCALE_NONE だとArmature/Meshノードが100倍スケールになり、UEはメッシュ頂点には
    # 反映するがボーン位置には反映しない(骨が1/100になり破片が原点を軸に潰れる)。そのため
    # 頂点・ボーン・移動カーブを実寸(cm)へ焼き込んだ複製を、ノードスケール1(apply_unit_scale=False+UNITS)で出力する
    # （元データは変更しない）。
    scale = 100.0
    orig_name = obj.name
    obj.name = orig_name + "__orig_export"
    conflict = _find_and_rename_conflicting("Armature")
    coll = bpy.context.collection

    mesh_dup = obj.copy()
    mesh_dup.data = obj.data.copy()
    mesh_dup.data.transform(Matrix.Scale(scale, 4))
    mesh_dup.name = orig_name
    coll.objects.link(mesh_dup)

    arm_dup = arm_obj.copy()
    arm_dup.data = arm_obj.data.copy()
    arm_dup.name = "Armature"
    coll.objects.link(arm_dup)
    arm_dup.parent = None
    arm_dup.matrix_world = Matrix.Identity(4)

    mesh_dup.parent = arm_dup
    mesh_dup.matrix_parent_inverse = Matrix.Identity(4)
    mesh_dup.matrix_basis = Matrix.Identity(4)
    for m in mesh_dup.modifiers:
        if m.type == 'ARMATURE':
            m.object = arm_dup

    bpy.ops.object.select_all(action='DESELECT')
    arm_dup.select_set(True)
    bpy.context.view_layer.objects.active = arm_dup
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in arm_dup.data.edit_bones:
        eb.head = eb.head * scale
        eb.tail = eb.tail * scale
    bpy.ops.object.mode_set(mode='OBJECT')

    src_action = arm_obj.animation_data.action if arm_obj.animation_data else None
    action_dup = None
    if src_action is not None:
        action_dup = src_action.copy()
        for fc in action_dup.fcurves:
            if fc.data_path.endswith(".location"):
                for kp in fc.keyframe_points:
                    kp.co = (kp.co[0], kp.co[1] * scale)
                    kp.handle_left = (kp.handle_left[0], kp.handle_left[1] * scale)
                    kp.handle_right = (kp.handle_right[0], kp.handle_right[1] * scale)
                fc.update()
        arm_dup.animation_data_create()
        arm_dup.animation_data.action = action_dup

    try:
        bpy.ops.object.select_all(action='DESELECT')
        mesh_dup.select_set(True)
        arm_dup.select_set(True)
        bpy.context.view_layer.objects.active = arm_dup
        bpy.ops.export_scene.fbx(apply_unit_scale=False, apply_scale_options='FBX_SCALE_UNITS',
                                 object_types={'ARMATURE', 'MESH'}, **common)
    finally:
        mesh_data, arm_data = mesh_dup.data, arm_dup.data
        bpy.data.objects.remove(mesh_dup, do_unlink=True)
        bpy.data.objects.remove(arm_dup, do_unlink=True)
        if mesh_data.users == 0:
            bpy.data.meshes.remove(mesh_data)
        if arm_data.users == 0:
            bpy.data.armatures.remove(arm_data)
        if action_dup is not None and action_dup.users == 0:
            bpy.data.actions.remove(action_dup)
        obj.name = orig_name
        if conflict:
            conflict[0].name = conflict[1]
    return fbx_filepath


def export_door_static_fbx(objects, fbx_filepath, origin_matrix=None):
    """
    複数のメッシュオブジェクトを結合した複製を、`origin_matrix`(通常はDoor_Frameのワールド行列)の
    ローカル空間・原点基準で、スタティックメッシュとしてFBX出力する（UE向け）。元オブジェクトは変更しない。
    """
    os.makedirs(os.path.dirname(os.path.abspath(fbx_filepath)), exist_ok=True)
    inv = origin_matrix.inverted() if origin_matrix is not None else Matrix.Identity(4)

    bpy.ops.object.select_all(action='DESELECT')
    dups = []
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.duplicate(linked=False)
    dups = list(bpy.context.selected_objects)
    for d in dups:
        mw = d.matrix_world.copy()
        d.parent = None
        d.matrix_world = inv @ mw
    bpy.ops.object.select_all(action='DESELECT')
    for d in dups:
        d.select_set(True)
    bpy.context.view_layer.objects.active = dups[0]
    if len(dups) > 1:
        bpy.ops.object.join()
    target = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    # Door_Frameローカル空間の座標のままボックス投影UVを付ける（破壊メッシュと同じ規則）
    assign_box_uv(target.data)

    try:
        bpy.ops.export_scene.fbx(
            filepath=fbx_filepath,
            use_selection=True,
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_NONE',
            axis_forward='-Y',
            axis_up='Z',
            mesh_smooth_type='FACE',
            add_leaf_bones=False,
            bake_anim=False,
            object_types={'MESH'},
        )
    finally:
        mesh_data = target.data
        bpy.data.objects.remove(target, do_unlink=True)
        if mesh_data.users == 0:
            bpy.data.meshes.remove(mesh_data)
    return fbx_filepath
