"""v01の側面下絵(Ref_Side)側でも、頭頂/首の付け根マーカーが輪郭と一致しているか確認する。"""
import bpy
import math

scene = bpy.context.scene

cam_data = bpy.data.cameras.new("CheckCamSide")
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 1.2
cam_obj = bpy.data.objects.new("CheckCamSide", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (2.0, 0, 0)
cam_obj.rotation_euler = (math.radians(90), 0, math.radians(90))
scene.camera = cam_obj

light_data = bpy.data.lights.new("L2", type='SUN')
light_data.energy = 3.0
light_obj = bpy.data.objects.new("L2", light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.rotation_euler = (math.radians(60), 0, math.radians(30))

for m in ["Marker_HeadTop", "Marker_NeckBase", "Marker_HeadCenter"]:
    o = bpy.data.objects.get(m)
    if o:
        o.location.x = 0.36  # Ref_Side(x=0.35)より手前(カメラ側)に出す

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 800
scene.render.resolution_y = 1200
scene.render.filepath = r"Z:\MeshCreator\Blender_HumanStudy\v01_check_side.png"
bpy.ops.render.render(write_still=True)
print("Saved check render:", scene.render.filepath)
