import bpy
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")
arm = bpy.data.objects.get("Armature_Teacher")
pb_r = arm.pose.bones["UpperArm.R"]

for axis in ['X', 'Y', 'Z']:
    for angle_deg in [-70, -45, 0, 45, 70]:
        rad = angle_deg * 3.14159 / 180.0
        pb_r.rotation_euler = (rad if axis=='X' else 0, rad if axis=='Y' else 0, rad if axis=='Z' else 0)
        bpy.context.view_layer.update()
        mw = arm.matrix_world @ pb_r.matrix
        tail_w = mw @ Vector((0, pb_r.length, 0))
        print(f"UpperArm.R {axis}={angle_deg:3d} deg -> tail_z={tail_w.z:.4f}, tail_y={tail_w.y:.4f}, tail_x={tail_w.x:.4f}")
