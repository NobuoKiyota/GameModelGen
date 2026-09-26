import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")
arm = bpy.data.objects.get("Armature_Teacher")

print("=== CHECKING REST POSE / EDIT BONES VS MESHES IN face_hair ===")

# Set rest pose
arm.data.pose_position = 'REST'
bpy.context.view_layer.update()

# Let's inspect in rest pose:
depsgraph = bpy.context.evaluated_depsgraph_get()

for obj_name in ["BodyBase", "BodyArm", "Outfit_Shirt", "Outfit_Cape", "Outfit_Sleeves"]:
    obj = bpy.data.objects.get(obj_name)
    if not obj: continue
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    cos = [eval_obj.matrix_world @ v.co for v in mesh.vertices]
    eval_obj.to_mesh_clear()
    
    print(f"\n[{obj_name}] (Rest Pose World Bounds):")
    print(f"  X: [{min(c.x for c in cos):.4f}, {max(c.x for c in cos):.4f}]")
    print(f"  Y: [{min(c.y for c in cos):.4f}, {max(c.y for c in cos):.4f}]")
    print(f"  Z: [{min(c.z for c in cos):.4f}, {max(c.z for c in cos):.4f}]")

# Check bone head/tails in REST pose
print("\n--- BONES in REST POSE ---")
for b in arm.data.bones:
    if any(k in b.name.lower() for k in ["arm", "shoulder", "spine", "chest"]):
        print(f"  {b.name:15s}: head=({b.head_local.x:.4f}, {b.head_local.y:.4f}, {b.head_local.z:.4f})  tail=({b.tail_local.x:.4f}, {b.tail_local.y:.4f}, {b.tail_local.z:.4f})")
