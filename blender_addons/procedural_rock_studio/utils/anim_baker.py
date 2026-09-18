import bpy
import os

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


def export_door_destruction_fbx(obj, fbx_filepath):
    """扉破壊アニメーション(シェイプキー焼き付け済みメッシュ)をFBXエクスポート（Unreal Engine持ち込み用）"""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    os.makedirs(os.path.dirname(os.path.abspath(fbx_filepath)), exist_ok=True)

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
