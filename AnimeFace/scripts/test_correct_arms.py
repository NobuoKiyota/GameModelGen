import bpy
import math

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")

# 1. Remove Mask_Outfit from BodyArm (RESTORE FULL ARMS!)
body_arm = bpy.data.objects.get("BodyArm")
if body_arm:
    m = body_arm.modifiers.get("Mask_Outfit")
    if m:
        body_arm.modifiers.remove(m)
        print("Removed Mask_Outfit from BodyArm: full arms restored!")

arm = bpy.data.objects.get("Armature_Teacher")
act = bpy.data.actions.get("Anim_Walk")

# Test natural arm swing based on proper down-pose:
# UpperArm.L: z = -0.85 (down), x = 0.06 + 0.10 * sin(...)
# UpperArm.R: z = +0.85 (down), x = 0.06 - 0.10 * sin(...)
# Shoulder: (0, 0, 0)
# Forearm.L: (0, -0.25, 0)
# Forearm.R: (0, 0.25, 0)

pb_uarm_l = arm.pose.bones.get("UpperArm.L")
pb_uarm_r = arm.pose.bones.get("UpperArm.R")
pb_farm_l = arm.pose.bones.get("Forearm.L")
pb_farm_r = arm.pose.bones.get("Forearm.R")
pb_sh_l = arm.pose.bones.get("Shoulder.L")
pb_sh_r = arm.pose.bones.get("Shoulder.R")

for f in range(1, 32):
    t = (f - 1) / 30.0 * 2.0 * math.pi
    swing = 0.08 * math.sin(t) # subtle natural arm swing
    
    # Left arm (opposite to right leg)
    pb_sh_l.rotation_euler = (0.0, 0.0, 0.0)
    pb_uarm_l.rotation_euler = (0.05 + swing, 0.0, -0.85)
    pb_farm_l.rotation_euler = (0.0, -0.25, 0.0)
    
    # Right arm
    pb_sh_r.rotation_euler = (0.0, 0.0, 0.0)
    pb_uarm_r.rotation_euler = (0.05 - swing, 0.0, 0.85)
    pb_farm_r.rotation_euler = (0.0, 0.25, 0.0)
    
    # insert keyframes
    pb_sh_l.keyframe_insert("rotation_euler", frame=f)
    pb_uarm_l.keyframe_insert("rotation_euler", frame=f)
    pb_farm_l.keyframe_insert("rotation_euler", frame=f)
    pb_sh_r.keyframe_insert("rotation_euler", frame=f)
    pb_uarm_r.keyframe_insert("rotation_euler", frame=f)
    pb_farm_r.keyframe_insert("rotation_euler", frame=f)

# Render test frames: F01, F08, F15, F23
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
    bpy.context.scene.render.filepath = f"Z:/MeshCreator/AnimeFace/out/renders_test/test_correct_arms_f{f:02d}.png"
    bpy.ops.render.render(write_still=True)
    print(f"Rendered test_correct_arms_f{f:02d}.png")
