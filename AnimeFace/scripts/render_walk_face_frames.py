import bpy

# Set up Face camera
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

# Render F01 (eyes open, closed mouth smile), F12 (eyes closed, blink peak), F14 (eyes opening)
test_frames = [1, 11, 12, 14, 20]
for f in test_frames:
    bpy.context.scene.frame_set(f)
    bpy.context.scene.render.filepath = f"Z:/MeshCreator/AnimeFace/out/walk_face_f{f:02d}.png"
    bpy.ops.render.render(write_still=True)
    print(f"Rendered walk_face_f{f:02d}.png")
