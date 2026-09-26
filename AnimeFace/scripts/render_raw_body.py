import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")

# Remove mask modifiers
for name in ["BodyBase", "BodyArm"]:
    obj = bpy.data.objects.get(name)
    if obj:
        for m in list(obj.modifiers):
            if m.type == 'MASK':
                obj.modifiers.remove(m)

# Hide all outfits
for obj in bpy.data.objects:
    if "outfit" in obj.name.lower():
        obj.hide_render = True

# Set REST pose
arm = bpy.data.objects.get("Armature_Teacher")
arm.data.pose_position = 'REST'

cam = bpy.data.objects.get("CAM_Front") or bpy.data.objects.get("MainCamera")
bpy.context.scene.camera = cam

bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/renders_test/test_face_hair_raw_body.png"
bpy.ops.render.render(write_still=True)
print("Rendered test_face_hair_raw_body.png")
