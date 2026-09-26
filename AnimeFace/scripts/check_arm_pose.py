import bpy

arm = bpy.data.objects.get("Armature") or bpy.data.objects.get("Armature_Teacher")
print("Armature name:", arm.name)

# Check pose at frame 1
bpy.context.scene.frame_set(1)
pbones = arm.pose.bones
for bname in ["UpperArm.L", "Forearm.L", "UpperArm.R", "Forearm.R", "Shoulder.L", "Shoulder.R"]:
    pb = pbones.get(bname)
    if pb:
        print(f"{bname}: rot_mode={pb.rotation_mode}, euler={pb.rotation_euler}, quat={pb.rotation_quaternion}")
