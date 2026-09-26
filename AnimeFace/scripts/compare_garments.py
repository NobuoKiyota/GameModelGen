import bpy

def inspect_garment(filepath):
    print(f"\n=== INSPECTING GARMENTS: {filepath} ===")
    bpy.ops.wm.open_mainfile(filepath=filepath)
    for name in ["Outfit_Cape", "Outfit_Sleeves", "Outfit_Shirt", "BodyArm"]:
        obj = bpy.data.objects.get(name)
        if not obj: continue
        print(f"[{name}]")
        print(f"  verts: {len(obj.data.vertices)}, polys: {len(obj.data.polygons)}")
        print(f"  modifiers: {[m.name + ' (' + m.type + ')' for m in obj.modifiers]}")
        for m in obj.modifiers:
            if m.type == 'ARMATURE':
                print(f"    Armature: obj={m.object.name if m.object else None}")
            elif m.type == 'SOLIDIFY':
                print(f"    Solidify: thickness={m.thickness}, offset={m.offset}")

inspect_garment("Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")
inspect_garment("Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")
