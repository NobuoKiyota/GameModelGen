import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")

# Remove Mask_Outfit from BodyArm
body_arm = bpy.data.objects.get("BodyArm")
if body_arm:
    m = body_arm.modifiers.get("Mask_Outfit")
    if m:
        body_arm.modifiers.remove(m)

arm = bpy.data.objects.get("Armature_Teacher")
# Temporarily detach action so it doesn't overwrite pose
if arm.animation_data:
    arm.animation_data.action = None

for side in ['L', 'R']:
    pb_sh = arm.pose.bones.get(f"Shoulder.{side}")
    pb_u = arm.pose.bones.get(f"UpperArm.{side}")
    pb_f = arm.pose.bones.get(f"Forearm.{side}")
    pb_h = arm.pose.bones.get(f"Hand.{side}")
    
    pb_sh.rotation_euler = (0, 0, 0)
    pb_u.rotation_euler = (-0.95, 0, 0)
    pb_f.rotation_euler = (0, 0, 0)
    pb_h.rotation_euler = (0, 0, 0)

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
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/renders_test/test_arms_no_action.png"
bpy.ops.render.render(write_still=True)
print("Rendered test_arms_no_action.png")
