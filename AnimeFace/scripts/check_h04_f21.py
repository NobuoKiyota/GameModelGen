import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h04.blend")
bpy.context.scene.frame_set(21)

print("=== CHECKING FRAME 21 IN H04 ===")
for obj_name in ["BodyBase", "BodyArm", "Outfit_Cape", "Outfit_Shirt", "Outfit_Sleeves"]:
    obj = bpy.data.objects.get(obj_name)
    if obj:
        print(f"[{obj_name}]")
        print(f"  hide_viewport: {obj.hide_viewport}, hide_render: {obj.hide_render}")
        print(f"  modifiers: {[m.name + ' (' + m.type + ')' for m in obj.modifiers]}")

# Render Frame 21 exactly as seen in viewport
cam = bpy.data.objects.get("FullCam") or bpy.data.objects.get("Camera")
if not cam:
    cam_data = bpy.data.cameras.new("FullCam")
    cam = bpy.data.objects.new("FullCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
cam.location = (0.0, -2.4, -0.15)
cam.rotation_euler = (1.5708, 0.0, 0.0)
bpy.context.scene.camera = cam

bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/renders_test/h04_frame21_current.png"
bpy.ops.render.render(write_still=True)
print("Rendered h04_frame21_current.png")
