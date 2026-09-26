import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h05.blend")
arm = bpy.data.objects.get("Armature_Teacher")
arm.data.pose_position = 'REST'

cam = bpy.data.objects.get("CAM_Front") or bpy.data.objects.get("MainCamera")
bpy.context.scene.camera = cam

bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 720

# 1. Body alone (no outfits, with hair)
for obj in bpy.data.objects:
    if "outfit" in obj.name.lower():
        obj.hide_render = True
    else:
        obj.hide_render = False

bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/renders_test/h05_final_body_rest.png"
bpy.ops.render.render(write_still=True)
print("Rendered h05_final_body_rest.png")

# 2. Full Outfit (all visible)
for obj in bpy.data.objects:
    obj.hide_render = False

bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/renders_test/h05_final_outfit_rest.png"
bpy.ops.render.render(write_still=True)
print("Rendered h05_final_outfit_rest.png")
