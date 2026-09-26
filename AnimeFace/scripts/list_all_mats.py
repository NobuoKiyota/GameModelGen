import bpy

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        mats = [m.name for m in obj.data.materials if m]
        print(f"Obj: {obj.name:20s} -> Mats: {mats}")
