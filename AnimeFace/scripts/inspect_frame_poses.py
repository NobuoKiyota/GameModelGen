import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")
arm = bpy.data.objects.get("Armature_Teacher")

print("=== POSE BONES ACROSS WALK CYCLE ===")
for f in [1, 8, 15, 23, 30]:
    bpy.context.scene.frame_set(f)
    print(f"\n[Frame {f}]")
    for bname in ["UpperArm.L", "Forearm.L", "Shoulder.L"]:
        pb = arm.pose.bones.get(bname)
        print(f"  {bname}: rot_euler=({pb.rotation_euler.x:.3f}, {pb.rotation_euler.y:.3f}, {pb.rotation_euler.z:.3f})")
