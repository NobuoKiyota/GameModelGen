import bpy
from mathutils import Matrix

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h05.blend")
sleeves = bpy.data.objects.get("Outfit_Sleeves")
if sleeves:
    mw = sleeves.matrix_world.copy()
    if sleeves.scale != (1.0, 1.0, 1.0) or sleeves.location != (0.0, 0.0, 0.0):
        for v in sleeves.data.vertices:
            v.co = mw @ v.co
        sleeves.location = (0, 0, 0)
        sleeves.rotation_euler = (0, 0, 0)
        sleeves.scale = (1, 1, 1)
        print("Sleeves scale explicitly set to (1,1,1)!")

bpy.ops.wm.save_mainfile()
print("Saved h05.")
