import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h05.blend")

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

# 1. Test Rest Pose: Body alone (verify BodyBase is 100% visible, not missing!)
arm = bpy.data.objects.get("Armature_Teacher")
arm.data.pose_position = 'REST'

for obj in bpy.data.objects:
    if "outfit" in obj.name.lower():
        obj.hide_render = True
    else:
        obj.hide_render = False

bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/renders_test/h05_verify_body_rest.png"
bpy.ops.render.render(write_still=True)
print("Rendered h05_verify_body_rest.png")

# 2. Test Walk Animation: Pose mode, F01, F12 (blink), F20
arm.data.pose_position = 'POSE'
for obj in bpy.data.objects:
    obj.hide_render = False

for f in [1, 12, 20]:
    bpy.context.scene.frame_set(f)
    bpy.context.scene.render.filepath = f"Z:/MeshCreator/AnimeFace/out/renders_test/h05_verify_walk_f{f:02d}.png"
    bpy.ops.render.render(write_still=True)
    print(f"Rendered h05_verify_walk_f{f:02d}.png")
