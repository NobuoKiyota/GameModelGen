import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")
body_arm = bpy.data.objects.get("BodyArm")

print("BodyArm.matrix_world:")
for row in body_arm.matrix_world:
    print(" ", row)

print("\nBodyArm first 5 verts:")
for i in range(5):
    v = body_arm.data.vertices[i]
    w = body_arm.matrix_world @ v.co
    print(f"  v[{i}]: local={v.co} -> world={w}")
