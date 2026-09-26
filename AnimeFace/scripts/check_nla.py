import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")
arm = bpy.data.objects.get("Armature_Teacher")

for t in arm.animation_data.nla_tracks:
    print(f"Track: {t.name}, is_solo={t.is_solo}, mute={t.mute}")
    for s in t.strips:
        print(f"  Strip: {s.name}, action={s.action.name if s.action else None}, start={s.frame_start}, end={s.frame_end}")
