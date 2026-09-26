import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")
act = bpy.data.actions.get("Anim_Walk")
print("Action attributes:", dir(act))
if hasattr(act, 'layers'):
    for l in act.layers:
        print(f"Layer: {l.name}, strips: {len(l.strips)}")
        for s in l.strips:
            print(f"  Strip: {s.name}, channelbags: {len(s.channelbags)}")
            for cb in s.channelbags:
                print(f"    CB: {cb.name}, curves: {len(cb.curves)}")
                for c in cb.curves:
                    if any(k in c.channel.name.lower() for k in ["arm", "shoulder"]):
                        print(f"      channel: {c.channel.name}")
