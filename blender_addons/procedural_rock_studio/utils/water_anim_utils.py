import bpy

def setup_water_ocean_animation(obj, wind_speed=1.0, anim_frames=60):
    """Ocean Modifier による微風波浪アニメーション(往復構成でループ対応)"""
    # 既存の波モディファイアを削除
    for mod in list(obj.modifiers):
        if mod.name in ("Wind_Ripple", "Ocean_Wave") or mod.type in ('WAVE', 'OCEAN'):
            obj.modifiers.remove(mod)

    # Ocean Modifier (DISPLACE) の追加
    ocean_mod = obj.modifiers.new(name="Ocean_Wave", type='OCEAN')
    ocean_mod.geometry_mode = 'DISPLACE'
    ocean_mod.resolution = 12
    ocean_mod.spatial_size = int(max(obj.dimensions.x, obj.dimensions.y) * 1.5)

    # 湖・池用の穏やかな微風パラメータ
    ocean_mod.wind_velocity = 4.5 * min(2.5, max(0.4, wind_speed))
    ocean_mod.wave_scale = 0.06 * min(2.0, max(0.3, wind_speed))
    ocean_mod.choppiness = 1.0
    ocean_mod.damping = 0.5 # 波の安定性
    ocean_mod.use_foam = True
    ocean_mod.foam_layer_name = "foam"
    ocean_mod.foam_coverage = 0.25

    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = anim_frames

    # アニメーションデータの作成
    if not obj.animation_data:
        obj.animation_data_create()

    # Time キーフレーム: 開始(frame=1)と終了(frame=anim_frames)を同じtime値にし、
    # 中間フレームでtimeを最大まで進めた「往復(ping-pong)」構成にする。
    # こうすると開始と終了で頂点形状が完全に一致するため、ループ再生時に継ぎ目のカクつきが出ない。
    # (以前は開始→終了で単調増加させていたため、終了直後に開始形状へ瞬間的に巻き戻る不連続が発生していた)
    mid_frame = max(2, min(anim_frames - 1, round(anim_frames / 2)))
    time_delta = 1.2 * min(2.0, max(0.5, wind_speed))

    ocean_mod.time = 1.0
    ocean_mod.keyframe_insert(data_path="time", frame=1)

    ocean_mod.time = 1.0 + time_delta
    ocean_mod.keyframe_insert(data_path="time", frame=mid_frame)

    ocean_mod.time = 1.0
    ocean_mod.keyframe_insert(data_path="time", frame=anim_frames)

    # リニア補間(往復速度を一定にする)。ループ再生はUnity/UE側のWrap Mode設定に委ねるため、
    # Blender側でのフレーム範囲外への外挿は行わない(既定のCONSTANTのままにする)。
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            if 'time' in fcurve.data_path:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = 'LINEAR'