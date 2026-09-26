import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")
arm = bpy.data.objects.get("Armature_Teacher")
arm.data.pose_position = 'POSE'

cam = bpy.data.objects.get("CAM_Front") or bpy.data.objects.get("MainCamera")
bpy.context.scene.camera = cam

bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/renders_test/face_hair_pose_front.png"
bpy.ops.render.render(write_still=True)
print("Rendered face_hair_pose_front.png")
