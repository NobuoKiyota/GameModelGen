import bpy

# Set up close-up camera for face
cam = bpy.data.objects.get("Camera")
if not cam:
    cam_data = bpy.data.cameras.new("FaceCam")
    cam = bpy.data.objects.new("FaceCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)

cam.location = (0.0, -0.65, 0.0)
cam.rotation_euler = (1.5708, 0.0, 0.0) # Look forward at face (face Z is around 0.0)
bpy.context.scene.camera = cam

# Set render settings
bpy.context.scene.render.resolution_x = 800
bpy.context.scene.render.resolution_y = 800
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/face_closeup_default.png"

bpy.ops.render.render(write_still=True)
print("Rendered default face close-up.")
