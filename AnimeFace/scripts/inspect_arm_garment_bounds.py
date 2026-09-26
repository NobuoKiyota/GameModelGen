import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")

# Inspect Outfit_Cape vs Outfit_Sleeves vs BodyArm in rest pose
for name in ["Outfit_Cape", "Outfit_Sleeves", "BodyArm"]:
    obj = bpy.data.objects.get(name)
    print(f"\n--- {name} ---")
    mw = obj.matrix_world
    cos = [mw @ v.co for v in obj.data.vertices]
    xs = [c.x for c in cos]
    ys = [c.y for c in cos]
    zs = [c.z for c in cos]
    print(f"  X: [{min(xs):.4f}, {max(xs):.4f}]")
    print(f"  Y: [{min(ys):.4f}, {max(ys):.4f}]")
    print(f"  Z: [{min(zs):.4f}, {max(zs):.4f}]")
