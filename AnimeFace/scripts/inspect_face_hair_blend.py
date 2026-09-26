import bpy

print("=== merged_face_hair objects ===")
for obj in bpy.data.objects:
    print(f"Obj: {obj.name:25s} type={obj.type} parent={obj.parent.name if obj.parent else None}")
    if obj.type == 'MESH':
        print(f"  modifiers: {[m.name for m in obj.modifiers]}")
