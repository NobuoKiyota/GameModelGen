import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h05.blend")
sleeves = bpy.data.objects.get("Outfit_Sleeves")
if sleeves:
    bpy.context.view_layer.objects.active = sleeves
    sleeves.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    sleeves.select_set(False)
    print("Outfit_Sleeves applied:", sleeves.scale)

bpy.ops.wm.save_mainfile()
print("Saved h05.")
