"""v01の目印(頭頂/首の付け根)が下絵の実際の頭部輪郭と一致しているかを
正射影カメラで正面から撮って画像化し、目視確認するための検証スクリプト。
Blender_HumanStudy/v01_reference_only.blend を開いた状態で実行する。
"""
import bpy
import math

scene = bpy.context.scene

cam_data = bpy.data.cameras.new("CheckCam")
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 1.2
cam_obj = bpy.data.objects.new("CheckCam", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (0, 2.0, 0)
cam_obj.rotation_euler = (math.radians(90), 0, math.radians(180))
scene.camera = cam_obj

light_data = bpy.data.lights.new("L", type='SUN')
light_data.energy = 3.0
light_obj = bpy.data.objects.new("L", light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.rotation_euler = (math.radians(60), 0, math.radians(30))

for m in ["Marker_HeadTop", "Marker_NeckBase", "Marker_HeadCenter"]:
    o = bpy.data.objects.get(m)
    if o:
        # 注意: object.scaleで拡大すると、メッシュ頂点に焼き込んだ中心オフセット(z)まで
        # ワールド原点基準で一緒に引き伸ばされ、マーカーが画面外に飛ぶ(検証スクリプトの
        # バグとして一度踏んだ)。半径を変えたい場合はメッシュ頂点を中心基準で編集すること。
        o.location.y = 0.36  # Ref_Front(y=0.35)より手前に出してカメラから見えるようにする(確認用の一時的な変更、保存はしない)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 800
scene.render.resolution_y = 1200
scene.render.filepath = r"Z:\MeshCreator\Blender_HumanStudy\v01_check_front.png"
bpy.ops.render.render(write_still=True)
print("Saved check render:", scene.render.filepath)
