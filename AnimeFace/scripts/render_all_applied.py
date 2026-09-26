import bpy

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")
arm = bpy.data.objects.get("Armature_Teacher")
arm.data.pose_position = 'REST'

# 1. Remove Mask modifiers
for name in ["BodyBase", "BodyArm"]:
    obj = bpy.data.objects.get(name)
    if obj:
        for m in list(obj.modifiers):
            if m.type == 'MASK':
                obj.modifiers.remove(m)

# 2. Apply Transform to all mesh objects
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        obj.select_set(False)

# 3. Align arm bones
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones

for side, sign in [('L', 1), ('R', -1)]:
    sh = eb.get(f"Shoulder.{side}")
    ua = eb.get(f"UpperArm.{side}")
    fa = eb.get(f"Forearm.{side}")
    ha = eb.get(f"Hand.{side}")
    
    if sh:
        sh.head.z = -0.250
        sh.tail.z = -0.258
    if ua:
        ua.head.z = -0.258
        ua.tail.z = -0.262
    if fa:
        fa.head.z = -0.262
        fa.tail.z = -0.260
    if ha:
        ha.head.z = -0.260
        ha.tail.z = -0.258

for bname in ["Skirt_B", "Skirt_F", "Skirt_L", "Skirt_R"]:
    b = eb.get(bname)
    if b: eb.remove(b)

bpy.ops.object.mode_set(mode='OBJECT')

# Show all garments & hair
for obj in bpy.data.objects:
    obj.hide_render = False

cam = bpy.data.objects.get("CAM_Front") or bpy.data.objects.get("MainCamera")
bpy.context.scene.camera = cam

bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/renders_test/test_all_applied_garments.png"
bpy.ops.render.render(write_still=True)
print("Rendered test_all_applied_garments.png")
