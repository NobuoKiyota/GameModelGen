import bpy
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")

print("=== DETAILED OBJECT TRANSFORM & MESH CENTERS ===")
for obj_name in ["BodyBase", "BodyArm", "BodyLeg", "Outfit_Shirt", "Outfit_Cape", "Outfit_Sleeves", "Face"]:
    obj = bpy.data.objects.get(obj_name)
    if not obj: continue
    print(f"\n[{obj_name}]")
    print(f"  loc: ({obj.location.x:.4f}, {obj.location.y:.4f}, {obj.location.z:.4f})")
    print(f"  scale: ({obj.scale.x:.4f}, {obj.scale.y:.4f}, {obj.scale.z:.4f})")
    mw = obj.matrix_world
    wcos = [mw @ v.co for v in obj.data.vertices]
    print(f"  World bounds:")
    print(f"    X: [{min(c.x for c in wcos):.4f}, {max(c.x for c in wcos):.4f}]")
    print(f"    Y: [{min(c.y for c in wcos):.4f}, {max(c.y for c in wcos):.4f}]")
    print(f"    Z: [{min(c.z for c in wcos):.4f}, {max(c.z for c in wcos):.4f}]")
