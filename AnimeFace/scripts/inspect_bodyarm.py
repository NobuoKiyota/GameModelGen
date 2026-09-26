import bpy

obj = bpy.data.objects.get("BodyArm")
print("BodyArm details:")
print("Modifiers:")
for m in obj.modifiers:
    print(f"  {m.name}: type={m.type}, show_viewport={m.show_viewport}, show_render={m.show_render}")

print("\nVertex groups:")
for vg in obj.vertex_groups:
    print(f"  {vg.name}")

if "Arm_Visible" in obj.vertex_groups:
    vg = obj.vertex_groups["Arm_Visible"]
    assigned = [v.index for v in obj.data.vertices if any(g.group == vg.index and g.weight > 0.1 for g in v.groups)]
    print(f"\nArm_Visible vertices ({len(assigned)}): {assigned}")
