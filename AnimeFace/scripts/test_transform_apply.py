import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")
arm = bpy.data.objects.get("Armature_Teacher")
arm.data.pose_position = 'REST'

# In background mode, set context
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        obj.select_set(False)

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        print(f"[{obj.name:15s}]: loc=({obj.location.x:.3f}, {obj.location.y:.3f}, {obj.location.z:.3f}), scale=({obj.scale.x:.3f}, {obj.scale.y:.3f}, {obj.scale.z:.3f})")

# Check BodyArm bounds
ba = bpy.data.objects.get("BodyArm")
zs = [v.co.z for v in ba.data.vertices]
xs = [v.co.x for v in ba.data.vertices]
ys = [v.co.y for v in ba.data.vertices]
print(f"\nBodyArm applied local bounds:")
print(f"  X: [{min(xs):.4f}, {max(xs):.4f}]")
print(f"  Y: [{min(ys):.4f}, {max(ys):.4f}]")
print(f"  Z: [{min(zs):.4f}, {max(zs):.4f}], center={(min(zs)+max(zs))/2:.4f}")
