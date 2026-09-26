import bpy
import math

# Load h03
bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")

# 1. RESTORE BODYARM COMPLETELY
body_arm = bpy.data.objects.get("BodyArm")
if body_arm:
    # Remove Mask_Outfit modifier so full arms (shoulder to hand) are 100% visible always
    mask = body_arm.modifiers.get("Mask_Outfit")
    if mask:
        body_arm.modifiers.remove(mask)
        print("Removed Mask_Outfit modifier from BodyArm.")

# Verify BodyArm vertices
print(f"BodyArm vertices: {len(body_arm.data.vertices)}, polys: {len(body_arm.data.polygons)}")

# 2. ADJUST ARM POSE IN ANIM_WALK SO ARMS FIT NATURALLY INSIDE CAPE
arm = bpy.data.objects.get("Armature_Teacher")

# We update Anim_Walk action keyframes for arms
# UpperArm: hang naturally down along body (x ≈ -0.92, slight natural swing)
# Forearm: relaxed (x ≈ 0, y ≈ 0, z ≈ 0)
# Shoulder: neutral (0, 0, 0)
pb_sh_l = arm.pose.bones.get("Shoulder.L")
pb_sh_r = arm.pose.bones.get("Shoulder.R")
pb_uarm_l = arm.pose.bones.get("UpperArm.L")
pb_uarm_r = arm.pose.bones.get("UpperArm.R")
pb_farm_l = arm.pose.bones.get("Forearm.L")
pb_farm_r = arm.pose.bones.get("Forearm.R")
pb_hand_l = arm.pose.bones.get("Hand.L")
pb_hand_r = arm.pose.bones.get("Hand.R")

for f in range(1, 32):
    t = (f - 1) / 30.0 * 2.0 * math.pi
    # Subtle swing: swing along walk cycle
    swing_z = 0.04 * math.sin(t) # very subtle front-back swing
    
    # Left Arm
    pb_sh_l.rotation_euler = (0.0, 0.0, 0.0)
    pb_uarm_l.rotation_euler = (-0.92, 0.0, -swing_z)
    pb_farm_l.rotation_euler = (0.0, 0.0, 0.0)
    pb_hand_l.rotation_euler = (0.0, 0.0, 0.0)
    
    # Right Arm
    pb_sh_r.rotation_euler = (0.0, 0.0, 0.0)
    pb_uarm_r.rotation_euler = (-0.92, 0.0, swing_z)
    pb_farm_r.rotation_euler = (0.0, 0.0, 0.0)
    pb_hand_r.rotation_euler = (0.0, 0.0, 0.0)
    
    # Keyframe insertion
    for pb in [pb_sh_l, pb_sh_r, pb_uarm_l, pb_uarm_r, pb_farm_l, pb_farm_r, pb_hand_l, pb_hand_r]:
        pb.keyframe_insert("rotation_euler", frame=f)

# Save to NEW file: teacher_ac_merged_h04.blend
out_file = "Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h04.blend"
bpy.ops.wm.save_as_mainfile(filepath=out_file)
print(f"Successfully created NEW blender file: {out_file}")

# 3. VERIFICATION RENDERS
# 3-a. Render BodyArm alone (like user's image 1) to prove full arms are back
# Hide garments temporarily
garments = ["Outfit_Cape", "Outfit_Shirt", "Outfit_Sleeves", "Outfit_Skirt", "Outfit_Belt", "Outfit_Boots"]
for gname in garments:
    g = bpy.data.objects.get(gname)
    if g:
        g.hide_render = True

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

# Render T-pose (Rest position) of restored BodyArm
arm.data.pose_position = 'REST'
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/renders_test/h04_bodyarm_rest_tpose.png"
bpy.ops.render.render(write_still=True)
print("Rendered h04_bodyarm_rest_tpose.png")

# 3-b. Render full body walk cycle F01 and F12 with garments visible
for gname in garments:
    g = bpy.data.objects.get(gname)
    if g:
        g.hide_render = False

arm.data.pose_position = 'POSE'
for f in [1, 12]:
    bpy.context.scene.frame_set(f)
    bpy.context.scene.render.filepath = f"Z:/MeshCreator/AnimeFace/out/renders_test/h04_walk_f{f:02d}.png"
    bpy.ops.render.render(write_still=True)
    print(f"Rendered h04_walk_f{f:02d}.png")
