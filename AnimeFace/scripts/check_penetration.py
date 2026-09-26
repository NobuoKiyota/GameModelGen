import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")
bpy.context.scene.frame_set(1)

# Evaluated depsgraph to get deformed mesh coordinates
depsgraph = bpy.context.evaluated_depsgraph_get()

cape_eval = bpy.data.objects.get("Outfit_Cape").evaluated_get(depsgraph)
arm_eval = bpy.data.objects.get("BodyArm").evaluated_get(depsgraph)

cape_mesh = cape_eval.to_mesh()
arm_mesh = arm_eval.to_mesh()

cape_cos = [cape_eval.matrix_world @ v.co for v in cape_mesh.vertices]
arm_cos = [arm_eval.matrix_world @ v.co for v in arm_mesh.vertices]

print(f"Cape evaluated bounds (F01):")
print(f"  X: [{min(c.x for c in cape_cos):.4f}, {max(c.x for c in cape_cos):.4f}]")
print(f"  Y: [{min(c.y for c in cape_cos):.4f}, {max(c.y for c in cape_cos):.4f}]")
print(f"  Z: [{min(c.z for c in cape_cos):.4f}, {max(c.z for c in cape_cos):.4f}]")

print(f"\nBodyArm evaluated bounds (F01):")
print(f"  X: [{min(c.x for c in arm_cos):.4f}, {max(c.x for c in arm_cos):.4f}]")
print(f"  Y: [{min(c.y for c in arm_cos):.4f}, {max(c.y for c in arm_cos):.4f}]")
print(f"  Z: [{min(c.z for c in arm_cos):.4f}, {max(c.z for c in arm_cos):.4f}]")

# Check which arm vertices are in front of cape (y < min cape y at that z/x)
front_penetrations = []
for i, ac in enumerate(arm_cos):
    # find cape vertices near this x and z
    nearby_cape = [cc for cc in cape_cos if abs(cc.x - ac.x) < 0.05 and abs(cc.z - ac.z) < 0.05]
    if nearby_cape:
        min_cape_y = min(cc.y for cc in nearby_cape)
        if ac.y < min_cape_y: # arm is in FRONT of cape!
            front_penetrations.append((i, ac, min_cape_y))

print(f"\nArm vertices penetrating FRONT of cape: {len(front_penetrations)} / {len(arm_cos)}")
for i, ac, mcy in front_penetrations[:10]:
    print(f"  v[{i:2d}]: arm_y={ac.y:.4f} < cape_min_y={mcy:.4f} (diff = {mcy - ac.y:.4f}m) at x={ac.x:.4f}, z={ac.z:.4f}")

cape_eval.to_mesh_clear()
arm_eval.to_mesh_clear()
