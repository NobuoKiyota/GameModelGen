import bpy

print("=== INSPECT EYE & MOUTH OBJECTS ===")
for obj in bpy.data.objects:
    if any(k in obj.name.lower() for k in ["eye", "face", "lid", "mouth", "brow"]):
        print(f"Obj: {obj.name}, Type: {obj.type}, Parent: {obj.parent.name if obj.parent else None}")
        if obj.type == 'MESH':
            print(f"  verts: {len(obj.data.vertices)}, shape_keys: {obj.data.shape_keys}")
            if obj.data.shape_keys:
                print(f"  keys: {[k.name for k in obj.data.shape_keys.key_blocks]}")
