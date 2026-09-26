import bpy

arm = bpy.data.objects.get("Armature_Teacher")
# Clear pose (reset all bones to zero)
for pb in arm.pose.bones:
    pb.rotation_euler = (0, 0, 0)
    pb.rotation_quaternion = (1, 0, 0, 0)
    pb.location = (0, 0, 0)

# Unhide BodyArm and remove Mask_Outfit
body_arm = bpy.data.objects.get("BodyArm")
if body_arm:
    m = body_arm.modifiers.get("Mask_Outfit")
    if m:
        body_arm.modifiers.remove(m)

# Render rest pose front and persp45
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
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/renders_test/test_tpose_rest.png"
bpy.ops.render.render(write_still=True)
print("Rendered test_tpose_rest.png")
