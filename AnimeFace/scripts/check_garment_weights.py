import bpy

print("=== CHECKING WEIGHTS OF CAPE, SLEEVES, BODYARM ===")

def check_vg(name):
    obj = bpy.data.objects.get(name)
    if not obj:
        print(f"Obj {name} not found")
        return
    print(f"\n[{name}]")
    arm_vgs = [vg.name for vg in obj.vertex_groups if any(k in vg.name.lower() for k in ["arm", "hand", "shoulder"])]
    print(f"  Arm vertex groups: {arm_vgs}")
    for vg_name in arm_vgs:
        vg = obj.vertex_groups.get(vg_name)
        cnt = sum(1 for v in obj.data.vertices if any(g.group == vg.index and g.weight > 0.01 for g in v.groups))
        print(f"    {vg_name}: {cnt} vertices")

check_vg("BodyArm")
check_vg("Outfit_Sleeves")
check_vg("Outfit_Cape")
check_vg("Outfit_Shirt")
