import bpy
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")
arm = bpy.data.objects.get("Armature_Teacher")
pb_u = arm.pose.bones["UpperArm.L"]
pb_f = arm.pose.bones["Forearm.L"]

# UpperArm down
pb_u.rotation_euler = (-0.95, 0.0, 0.0)

# Check Forearm rotations
for axis in ['X', 'Y', 'Z']:
    for angle_deg in [-45, 0, 45]:
        rad = angle_deg * 3.14159 / 180.0
        pb_f.rotation_euler = (rad if axis=='X' else 0, rad if axis=='Y' else 0, rad if axis=='Z' else 0)
        bpy.context.view_layer.update()
        mw = arm.matrix_world @ pb_f.matrix
        tail_w = mw @ Vector((0, pb_f.length, 0))
        print(f"Forearm.L {axis}={angle_deg:3d} deg -> tail: x={tail_w.x:.4f}, y={tail_w.y:.4f}, z={tail_w.z:.4f}")
