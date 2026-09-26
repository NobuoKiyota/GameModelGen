import bpy
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")

# Remove Mask_Outfit from BodyArm
body_arm = bpy.data.objects.get("BodyArm")
if body_arm:
    m = body_arm.modifiers.get("Mask_Outfit")
    if m:
        body_arm.modifiers.remove(m)

arm = bpy.data.objects.get("Armature_Teacher")

# Mute NLA tracks temporarily to test pose directly
for t in arm.animation_data.nla_tracks:
    t.mute = True

# Test pose: natural arm alongside body inside cape
pb_sh_l = arm.pose.bones["Shoulder.L"]
pb_uarm_l = arm.pose.bones["UpperArm.L"]
pb_farm_l = arm.pose.bones["Forearm.L"]

pb_sh_r = arm.pose.bones["Shoulder.R"]
pb_uarm_r = arm.pose.bones["UpperArm.R"]
pb_farm_r = arm.pose.bones["Forearm.R"]

# Test different shoulder and upperarm rotations
# UpperArm down: X around -0.95
# Let's test combinations of UpperArm Z and Shoulder to see penetration
best_pen = 999
best_angles = None

for u_x in [-1.0, -0.95, -0.90]:
    for u_z in [-0.15, -0.05, 0.0, 0.05, 0.15]:
        for f_z in [-0.10, 0.0, 0.10]:
            pb_sh_l.rotation_euler = (0, 0, 0)
            pb_uarm_l.rotation_euler = (u_x, 0, u_z)
            pb_farm_l.rotation_euler = (0, 0, f_z)
            
            pb_sh_r.rotation_euler = (0, 0, 0)
            pb_uarm_r.rotation_euler = (u_x, 0, -u_z)
            pb_farm_r.rotation_euler = (0, 0, -f_z)
            
            bpy.context.view_layer.update()
            depsgraph = bpy.context.evaluated_depsgraph_get()
            cape_eval = bpy.data.objects.get("Outfit_Cape").evaluated_get(depsgraph)
            arm_eval = bpy.data.objects.get("BodyArm").evaluated_get(depsgraph)
            
            cm = cape_eval.to_mesh()
            am = arm_eval.to_mesh()
            c_cos = [cape_eval.matrix_world @ v.co for v in cm.vertices]
            a_cos = [arm_eval.matrix_world @ v.co for v in am.vertices]
            
            # Count penetrations: arm vertices where arm_y < min nearby cape_y or arm_y > max nearby cape_y
            pen_count = 0
            for ac in a_cos:
                nearby = [cc for cc in c_cos if abs(cc.x - ac.x) < 0.04 and abs(cc.z - ac.z) < 0.04]
                if nearby:
                    min_y = min(c.y for c in nearby)
                    max_y = max(c.y for c in nearby)
                    if ac.y < min_y - 0.005 or ac.y > max_y + 0.005:
                        pen_count += 1
            
            cape_eval.to_mesh_clear()
            arm_eval.to_mesh_clear()
            
            if pen_count < best_pen:
                best_pen = pen_count
                best_angles = (u_x, u_z, f_z)
                print(f"New best: pen={pen_count}, angles=u_x:{u_x}, u_z:{u_z}, f_z:{f_z}")

print(f"\nOptimal angles: {best_angles} with penetration: {best_pen}")
