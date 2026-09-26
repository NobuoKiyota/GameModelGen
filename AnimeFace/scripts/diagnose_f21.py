import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h04.blend")
bpy.context.scene.frame_set(21)
depsgraph = bpy.context.evaluated_depsgraph_get()

print("=== CHECKING FRAME 21 IN H04 ===")
arm = bpy.data.objects.get("Armature_Teacher")

# Check pose bones at frame 21
for bname in ["UpperArm.L", "Forearm.L", "UpperArm.R", "Forearm.R"]:
    pb = arm.pose.bones.get(bname)
    mw = arm.matrix_world @ pb.matrix
    head_w = mw.translation
    tail_w = mw @ pb.tail
    print(f"PoseBone {bname}: head_w={head_w}, euler={pb.rotation_euler}")

# Check BodyArm evaluated vertices at frame 21
arm_obj = bpy.data.objects.get("BodyArm")
eval_arm = arm_obj.evaluated_get(depsgraph)
am = eval_arm.to_mesh()
cos = [eval_arm.matrix_world @ v.co for v in am.vertices]
eval_arm.to_mesh_clear()

print(f"\nBodyArm evaluated bounds at F21:")
print(f"  X: [{min(c.x for c in cos):.4f}, {max(c.x for c in cos):.4f}]")
print(f"  Y: [{min(c.y for c in cos):.4f}, {max(c.y for c in cos):.4f}]")
print(f"  Z: [{min(c.z for c in cos):.4f}, {max(c.z for c in cos):.4f}]")

# Check all objects for extreme vertex positions (that black polygon!)
print("\n--- CHECKING EXTREME VERTICES (Black polygon artifact) ---")
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        e_obj = obj.evaluated_get(depsgraph)
        m = e_obj.to_mesh()
        wcos = [e_obj.matrix_world @ v.co for v in m.vertices]
        e_obj.to_mesh_clear()
        if wcos:
            max_z = max(c.z for c in wcos)
            min_z = min(c.z for c in wcos)
            max_y = max(c.y for c in wcos)
            min_y = min(c.y for c in wcos)
            if max_z > 0.5 or min_z < -1.5 or max_y > 1.0 or min_y < -1.0:
                print(f"  ALERT: {obj.name} has wild coords! Z=[{min_z:.2f}, {max_z:.2f}], Y=[{min_y:.2f}, {max_y:.2f}]")
            else:
                print(f"  {obj.name:15s}: Z=[{min_z:.2f}, {max_z:.2f}], Y=[{min_y:.2f}, {max_y:.2f}]")
