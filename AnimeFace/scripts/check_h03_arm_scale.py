import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")
body_arm = bpy.data.objects.get("BodyArm")
print("h03 BodyArm location:", body_arm.location)
print("h03 BodyArm rotation:", body_arm.rotation_euler)
print("h03 BodyArm scale:", body_arm.scale)
