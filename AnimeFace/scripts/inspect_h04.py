import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h04.blend")

print("=== INSPECTING H04 BLEND ===")
arm = bpy.data.objects.get("Armature_Teacher")
print("Armature:", arm.name if arm else None)
if arm and arm.animation_data:
    print("  Action:", arm.animation_data.action.name if arm.animation_data.action else None)
    print("  NLA tracks:", [t.name for t in arm.animation_data.nla_tracks])

print("\nActions in h04:")
for a in bpy.data.actions:
    print(f"  {a.name}")

print("\nBodyBase in h04:")
bb = bpy.data.objects.get("BodyBase")
if bb:
    print(f"  verts: {len(bb.data.vertices)}, modifiers: {[m.name + ' (' + m.type + ')' for m in bb.modifiers]}")

print("\nBodyArm in h04:")
ba = bpy.data.objects.get("BodyArm")
if ba:
    print(f"  verts: {len(ba.data.vertices)}, modifiers: {[m.name + ' (' + m.type + ')' for m in ba.modifiers]}")
    zs = [v.co.z for v in ba.data.vertices]
    print(f"  local Z bounds: [{min(zs):.4f}, {max(zs):.4f}], center={(min(zs)+max(zs))/2:.4f}")
    wzs = [(ba.matrix_world @ v.co).z for v in ba.data.vertices]
    print(f"  world Z bounds: [{min(wzs):.4f}, {max(wzs):.4f}], center={(min(wzs)+max(wzs))/2:.4f}")

print("\nArm bones in h04:")
for bname in ["Shoulder.R", "UpperArm.R", "Forearm.R", "Hand.R"]:
    b = arm.data.bones.get(bname)
    if b:
        print(f"  {bname:12s}: head={b.head_local}, tail={b.tail_local}")
