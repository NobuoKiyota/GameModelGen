import bpy

def inspect_blend():
    print("=== INSPECTING ARMS ===")
    for obj in bpy.data.objects:
        if "arm" in obj.name.lower() or "body" in obj.name.lower():
            print(f"Obj: {obj.name}, Type: {obj.type}")
            if obj.type == 'MESH':
                print(f"  verts: {len(obj.data.vertices)}, polys: {len(obj.data.polygons)}")
                print(f"  modifiers: {[m.name + ' (' + m.type + ')' for m in obj.modifiers]}")
                for m in obj.modifiers:
                    if m.type == 'MASK':
                        print(f"    Mask: mode={m.mode}, vg={m.vertex_group}, inv={m.invert_vertex_group}, threshold={m.threshold}")

inspect_blend()
