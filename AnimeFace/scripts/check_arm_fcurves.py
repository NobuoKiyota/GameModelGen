import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")
act = bpy.data.actions.get("Anim_Walk")

print(f"Action: {act.name}")
for fc in act.fcurves:
    if any(k in fc.data_path.lower() for k in ["arm", "shoulder", "hand"]):
        vals = [f"F{int(kp.co[0])}:{kp.co[1]:.3f}" for kp in fc.keyframe_points]
        print(f"  {fc.data_path}[{fc.array_index}]: {', '.join(vals)}")
