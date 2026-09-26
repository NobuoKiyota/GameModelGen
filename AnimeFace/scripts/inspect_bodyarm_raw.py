import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")
body_arm = bpy.data.objects.get("BodyArm")

print("BodyArm raw vertices:")
zs = [v.co.z for v in body_arm.data.vertices]
ys = [v.co.y for v in body_arm.data.vertices]
xs = [v.co.x for v in body_arm.data.vertices]
print(f"  Local Bounds: X=[{min(xs):.4f}, {max(xs):.4f}], Y=[{min(ys):.4f}, {max(ys):.4f}], Z=[{min(zs):.4f}, {max(zs):.4f}]")
print(f"  Local Center Z: {(min(zs)+max(zs))/2:.4f}")
print(f"  scale: {body_arm.scale}")
print(f"  location: {body_arm.location}")

mw = body_arm.matrix_world
wzs = [(mw @ v.co).z for v in body_arm.data.vertices]
print(f"  World Bounds Z: [{min(wzs):.4f}, {max(wzs):.4f}], center={(min(wzs)+max(wzs))/2:.4f}")

arm = bpy.data.objects.get("Armature_Teacher")
print("\nArmature EditBones:")
for b in arm.data.bones:
    if "arm" in b.name.lower() or "shoulder" in b.name.lower():
        print(f"  {b.name}: head={b.head_local}, tail={b.tail_local}")
