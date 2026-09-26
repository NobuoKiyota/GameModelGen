import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")
arm = bpy.data.objects.get("Armature_Teacher")

# Check if there is an NLA track or other animation data!
print("arm.animation_data:", arm.animation_data)
if arm.animation_data:
    print("  action:", arm.animation_data.action)
    print("  nla_tracks:", len(arm.animation_data.nla_tracks))
    for t in arm.animation_data.nla_tracks:
        print(f"    track: {t.name}, strips={[s.name for s in t.strips]}")

# Check all pose bones
pb = arm.pose.bones["UpperArm.L"]
print("Initial UpperArm.L:", pb.rotation_euler)
pb.rotation_euler = (-0.95, 0, 0)
bpy.context.view_layer.update()
print("After set UpperArm.L:", pb.rotation_euler)

# Also check BodyArm modifiers:
body_arm = bpy.data.objects.get("BodyArm")
print("BodyArm modifiers:", [m.name for m in body_arm.modifiers])
for m in body_arm.modifiers:
    if m.type == 'ARMATURE':
        print(f"  Armature modifier: target={m.object.name if m.object else None}")
