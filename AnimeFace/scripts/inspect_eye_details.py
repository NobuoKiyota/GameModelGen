import bpy

eye_objs = ["DoubleLid", "Eye", "Eyebrow", "Eyelash.001", "Eyelash.002", "Eyelash.003", "Face"]
for name in eye_objs:
    obj = bpy.data.objects.get(name)
    if not obj:
        continue
    print(f"\n--- {name} ---")
    print(f"Location: {obj.location}, Rotation: {obj.rotation_euler}, Scale: {obj.scale}")
    print(f"Modifiers: {[m.name + ' (' + m.type + ')' for m in obj.modifiers]}")
    verts = [v.co for v in obj.data.vertices]
    xs = [v.x for v in verts]
    ys = [v.y for v in verts]
    zs = [v.z for v in verts]
    print(f"X range: [{min(xs):.4f}, {max(xs):.4f}]")
    print(f"Y range: [{min(ys):.4f}, {max(ys):.4f}]")
    print(f"Z range: [{min(zs):.4f}, {max(zs):.4f}]")
    # check vertex groups
    print(f"Vertex groups: {[vg.name for vg in obj.vertex_groups]}")
