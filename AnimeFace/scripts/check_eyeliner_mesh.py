import bpy

# Check visibility of each
for name in ["Face", "DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003", "Eye"]:
    obj = bpy.data.objects.get(name)
    if obj:
        print(f"{name}: hide_render={obj.hide_render}, hide_viewport={obj.hide_viewport}")

# Hide Eyelash.001, 002, 003, DoubleLid and render to see what remains on Face
for name in ["DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003"]:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.hide_render = True

cam = bpy.data.objects.get("FaceCam") or bpy.data.objects.get("Camera")
if not cam:
    cam_data = bpy.data.cameras.new("FaceCam")
    cam = bpy.data.objects.new("FaceCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
cam.location = (0.0, -0.65, 0.0)
cam.rotation_euler = (1.5708, 0.0, 0.0)
bpy.context.scene.camera = cam

bpy.context.scene.render.resolution_x = 800
bpy.context.scene.render.resolution_y = 800
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/test_face_no_lashes.png"
bpy.ops.render.render(write_still=True)
print("Rendered test_face_no_lashes.png")
