import bpy

# Load face_hair blend
bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")
arm1 = bpy.data.objects.get("BodyArm")
cos1 = [tuple(v.co) for v in arm1.data.vertices]

# Load h03 blend
bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")
arm2 = bpy.data.objects.get("BodyArm")
cos2 = [tuple(v.co) for v in arm2.data.vertices]

print(f"arm1 verts: {len(cos1)}, arm2 verts: {len(cos2)}")
diff = 0
for c1, c2 in zip(cos1, cos2):
    d = sum((a - b)**2 for a, b in zip(c1, c2))**0.5
    if d > 1e-4:
        diff += 1
print(f"Vertex position differences: {diff}")
