import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")
body_arm = bpy.data.objects.get("BodyArm")
print("BodyArm location:", body_arm.location)
print("BodyArm rotation:", body_arm.rotation_euler)
print("BodyArm scale:", body_arm.scale)
arm = bpy.data.objects.get("Armature_Teacher")

# Check edit bones vs pose bones
print("\nEdit bones:")
for eb in arm.data.bones:
    if "arm" in eb.name.lower() or "hand" in eb.name.lower() or "shoulder" in eb.name.lower():
        print(f"  {eb.name}: head={eb.head_local}, tail={eb.tail_local}")

print("\nPose bones:")
for pb in arm.pose.bones:
    if "arm" in pb.name.lower() or "hand" in pb.name.lower() or "shoulder" in pb.name.lower():
        print(f"  {pb.name}: rot={pb.rotation_euler}, quat={pb.rotation_quaternion}, loc={pb.location}")
