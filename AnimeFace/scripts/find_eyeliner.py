import bpy

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        mats = [m.name for m in obj.data.materials if m]
        if any("eye" in m.lower() or "lash" in m.lower() or "line" in m.lower() or "dark" in m.lower() or "brow" in m.lower() for m in mats):
            print(f"Obj: {obj.name}, Mats: {mats}")
