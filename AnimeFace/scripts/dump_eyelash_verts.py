import bpy

objs = ["Eyelash.001", "Eyelash.002", "Eyelash.003", "DoubleLid"]
for name in objs:
    obj = bpy.data.objects.get(name)
    print(f"\n=== {name} ===")
    mw = obj.matrix_world
    for i, v in enumerate(obj.data.vertices):
        wco = mw @ v.co
        print(f"  v[{i:2d}]: local=({v.co.x:.4f}, {v.co.y:.4f}, {v.co.z:.4f})  world=({wco.x:.4f}, {wco.y:.4f}, {wco.z:.4f})")
