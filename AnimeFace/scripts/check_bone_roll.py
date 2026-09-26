import bpy
from mathutils import Vector, Euler, Matrix

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")
arm = bpy.data.objects.get("Armature_Teacher")

# Edit bone orientation
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
for bname in ["UpperArm.L", "Forearm.L", "UpperArm.R", "Forearm.R"]:
    eb = arm.data.edit_bones[bname]
    print(f"EditBone {bname}: roll={eb.roll:.4f}, head={eb.head}, tail={eb.tail}, vector={eb.vector}")

bpy.ops.object.mode_set(mode='POSE')
