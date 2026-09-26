import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")
arm = bpy.data.objects.get("Armature_Teacher")

# Check what actions exist in this blend file!
print("=== ACTIONS ===")
for act in bpy.data.actions:
    print(f"Action: {act.name}")

if arm.animation_data and arm.animation_data.action:
    print(f"Active action on armature: {arm.animation_data.action.name}")
