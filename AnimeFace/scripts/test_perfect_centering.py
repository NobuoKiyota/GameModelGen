import bpy
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")
arm = bpy.data.objects.get("Armature_Teacher")
arm.data.pose_position = 'REST'

# 1. Remove Mask modifiers from BodyBase and BodyArm
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

# 3. Fine-tune Arm EditBones to match exact BodyArm center (Z ≈ -0.260)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones

for side, sign in [('L', 1), ('R', -1)]:
    sh = eb.get(f"Shoulder.{side}")
    ua = eb.get(f"UpperArm.{side}")
    fa = eb.get(f"Forearm.{side}")
    ha = eb.get(f"Hand.{side}")
    
    # Perfectly centered:
    # Shoulder: head Z = -0.250, tail Z = -0.258
    # UpperArm: head Z = -0.258, tail Z = -0.262 (elbow)
    # Forearm : head Z = -0.262, tail Z = -0.260 (wrist)
    # Hand    : head Z = -0.260, tail Z = -0.258
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

# Remove unused skirt bones
for bname in ["Skirt_B", "Skirt_F", "Skirt_L", "Skirt_R"]:
    b = eb.get(bname)
    if b: eb.remove(b)

bpy.ops.object.mode_set(mode='OBJECT')

# 4. Render markers along the newly centered arm bones
def make_marker(name, loc, radius=0.012, color=(0.1, 0.9, 0.2, 1.0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc)
    sphere = bpy.context.active_object
    sphere.name = name
    mat = bpy.data.materials.new(name=f"Mat_{name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
    sphere.data.materials.append(mat)
    return sphere

for side in ['L', 'R']:
    for bname in [f"Shoulder.{side}", f"UpperArm.{side}", f"Forearm.{side}", f"Hand.{side}"]:
        b = arm.data.bones[bname]
        make_marker(f"M_{bname}_head", b.head_local, radius=0.010, color=(1.0, 0.2, 0.2, 1.0))
        make_marker(f"M_{bname}_tail", b.tail_local, radius=0.008, color=(0.2, 0.5, 1.0, 1.0))

# Hide hair and outfits to clearly see bone markers vs BodyBase and BodyArm
for obj in bpy.data.objects:
    if "hair" in obj.name.lower() or "outfit" in obj.name.lower():
        obj.hide_render = True

cam = bpy.data.objects.get("CAM_Front") or bpy.data.objects.get("MainCamera")
bpy.context.scene.camera = cam

bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/renders_test/test_bone_perfect_centering.png"
bpy.ops.render.render(write_still=True)
print("Rendered test_bone_perfect_centering.png")
