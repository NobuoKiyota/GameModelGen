import bpy

# Load h03
bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")

# Remove Mask_Outfit
body_arm = bpy.data.objects.get("BodyArm")
if body_arm:
    m = body_arm.modifiers.get("Mask_Outfit")
    if m:
        body_arm.modifiers.remove(m)

# Let's check how the arm looks when Shoulder is slightly back (y > 0)
# and UpperArm hangs naturally down
arm = bpy.data.objects.get("Armature_Teacher")

# Let's test on frame 1
# Shoulder.L: slightly back so arm enters cape sleeve opening naturally
# e.g. Shoulder.L: rot_euler = (0, 0, 0)
# UpperArm.L: hang down with slight outward angle: x = -0.90, z = -0.05
# Forearm.L: straight down or slight bend
for side, sign in [('L', 1), ('R', -1)]:
    pb_sh = arm.pose.bones[f"Shoulder.{side}"]
    pb_u = arm.pose.bones[f"UpperArm.{side}"]
    pb_f = arm.pose.bones[f"Forearm.{side}"]
    pb_h = arm.pose.bones[f"Hand.{side}"]
    
    pb_sh.rotation_euler = (0.0, 0.0, 0.0)
    pb_u.rotation_euler = (-0.92, 0.0, sign * 0.05)
    pb_f.rotation_euler = (0.0, 0.0, 0.0)
    pb_h.rotation_euler = (0.0, 0.0, 0.0)

# Unmute tracks or test without NLA
for t in arm.animation_data.nla_tracks:
    t.mute = True

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
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/renders_test/test_arm_straight_down.png"
bpy.ops.render.render(write_still=True)
print("Rendered test_arm_straight_down.png")
