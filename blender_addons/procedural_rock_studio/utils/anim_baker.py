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
