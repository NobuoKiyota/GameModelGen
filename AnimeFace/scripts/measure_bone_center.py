import bpy
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")
arm = bpy.data.objects.get("Armature_Teacher")
body_arm = bpy.data.objects.get("BodyArm")

print("=== BODYARM VS EDIT BONES IN REST POSE (face_hair) ===")

# Matrix world of both
mw_b = body_arm.matrix_world
mw_a = arm.matrix_world

# UpperArm.R: edit bone in world coords
eb_u = arm.data.bones["UpperArm.R"]
head_w = mw_a @ eb_u.head_local
tail_w = mw_a @ eb_u.tail_local
mid_bone = (head_w + tail_w) / 2.0

print(f"UpperArm.R bone in world:")
print(f"  Head: {head_w}")
print(f"  Tail: {tail_w}")
print(f"  Mid : {mid_bone}")

# BodyArm vertices around UpperArm.R (X in range [-0.28, -0.14])
mw_v = [mw_b @ v.co for v in body_arm.data.vertices]
uarm_verts = [v for v in mw_v if -0.28 <= v.x <= -0.14]

if uarm_verts:
    avg_y = sum(v.y for v in uarm_verts) / len(uarm_verts)
    avg_z = sum(v.z for v in uarm_verts) / len(uarm_verts)
    print(f"\nBodyArm mesh in range X in [-0.28, -0.14] ({len(uarm_verts)} verts):")
    print(f"  Center Y: {avg_y:.4f} (bone mid Y: {mid_bone.y:.4f}, diff: {avg_y - mid_bone.y:.4f})")
    print(f"  Center Z: {avg_z:.4f} (bone mid Z: {mid_bone.z:.4f}, diff: {avg_z - mid_bone.z:.4f})")

# Forearm.R: edit bone in world coords
eb_f = arm.data.bones["Forearm.R"]
f_head_w = mw_a @ eb_f.head_local
f_tail_w = mw_a @ eb_f.tail_local
f_mid_bone = (f_head_w + f_tail_w) / 2.0

print(f"\nForearm.R bone in world:")
print(f"  Head: {f_head_w}")
print(f"  Tail: {f_tail_w}")
print(f"  Mid : {f_mid_bone}")

farm_verts = [v for v in mw_v if -0.42 <= v.x <= -0.28]
if farm_verts:
    f_avg_y = sum(v.y for v in farm_verts) / len(farm_verts)
    f_avg_z = sum(v.z for v in farm_verts) / len(farm_verts)
    print(f"\nBodyArm mesh in range X in [-0.42, -0.28] ({len(farm_verts)} verts):")
    print(f"  Center Y: {f_avg_y:.4f} (bone mid Y: {f_mid_bone.y:.4f}, diff: {f_avg_y - f_mid_bone.y:.4f})")
    print(f"  Center Z: {f_avg_z:.4f} (bone mid Z: {f_mid_bone.z:.4f}, diff: {f_avg_z - f_mid_bone.z:.4f})")
