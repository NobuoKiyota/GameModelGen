import bpy

def setup_water_ocean_animation(obj, wind_speed=1.0, anim_frames=60):
    """【動画 vSgWZG2ugf0 7:58準拠】Ocean Modifier によるリアルな微風波浪アニメーション"""
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

    # Time キーフレーム（動画 7:58 準拠: 超ゆったり進行）
    # フレーム1 で Time=1.0, 終端フレーム で Time=2.2 (速度 0.02/frame)
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = anim_frames

    # アニメーションデータの作成
    if not obj.animation_data:
        obj.animation_data_create()
    
    # Time アニメーション
    ocean_mod.time = 1.0
    ocean_mod.keyframe_insert(data_path="time", frame=1)
    
    time_delta = 1.2 * min(2.0, max(0.5, wind_speed))
    ocean_mod.time = 1.0 + time_delta
    ocean_mod.keyframe_insert(data_path="time", frame=anim_frames)

    # リニア補間に設定（スムーズなループ）
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            if 'time' in fcurve.data_path:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = 'LINEAR'
