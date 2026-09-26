import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h05.blend")
arm = bpy.data.objects.get("Armature_Teacher")

# Show armature in front (X-Ray)
arm.show_in_front = True

# Also hide hair and garments to clearly see bone centering in BodyArm
for obj in bpy.data.objects:
    if "hair" in obj.name.lower() or "outfit" in obj.name.lower():
        obj.hide_render = True

cam = bpy.data.objects.get("CAM_Front") or bpy.data.objects.get("MainCamera")
bpy.context.scene.camera = cam

# Render bone alignment in viewport OpenGL / Workbench or Workbench engine
bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
bpy.context.scene.display.shading.color_type = 'MATERIAL'

bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/renders_test/h05_bone_centering_check.png"
bpy.ops.render.render(write_still=True)
print("Rendered h05_bone_centering_check.png")
