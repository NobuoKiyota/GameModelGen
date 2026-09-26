import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h05.blend")

print("=== VERIFYING FINAL h05 FILE ===")
arm = bpy.data.objects.get("Armature_Teacher")

# 1. Mesh objects check
for name in ["BodyBase", "BodyArm", "BodyLeg", "Outfit_Shirt", "Outfit_Cape", "Outfit_Sleeves", "Face"]:
    obj = bpy.data.objects.get(name)
    masks = [m.name for m in obj.modifiers if m.type == 'MASK']
    print(f"[{name}]: loc={obj.location}, scale={obj.scale}, masks={masks}, verts={len(obj.data.vertices)}")

# 2. Bone centering check
print("\n--- Arm Bones vs BodyArm ---")
ba = bpy.data.objects.get("BodyArm")
zs = [v.co.z for v in ba.data.vertices]
mid_z = (min(zs) + max(zs)) / 2.0
print(f"BodyArm Z range: [{min(zs):.4f}, {max(zs):.4f}], center={mid_z:.4f}")

for bname in ["Shoulder.R", "UpperArm.R", "Forearm.R", "Hand.R"]:
    b = arm.data.bones[bname]
    print(f"  {bname:12s}: head_z={b.head_local.z:.4f}, tail_z={b.tail_local.z:.4f} (diff from arm center: {b.head_local.z - mid_z:+.4f})")

# 3. Shape keys check
face = bpy.data.objects.get("Face")
print(f"\nFace shape keys: {[k.name for k in face.data.shape_keys.key_blocks]}")
