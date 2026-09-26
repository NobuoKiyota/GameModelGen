import bpy

# Disable Mask_Outfit on BodyArm
body_arm = bpy.data.objects.get("BodyArm")
if body_arm:
    mask = body_arm.modifiers.get("Mask_Outfit")
    if mask:
        mask.show_viewport = False
        mask.show_render = False

# Render F01, F08, F15, F23 full body to check if arms penetrate sleeves
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

for f in [1, 8, 15, 23]:
    bpy.context.scene.frame_set(f)
    bpy.context.scene.render.filepath = f"Z:/MeshCreator/AnimeFace/out/renders_test/test_arm_restored_f{f:02d}.png"
    bpy.ops.render.render(write_still=True)
    print(f"Rendered test_arm_restored_f{f:02d}.png")
