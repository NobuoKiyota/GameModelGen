import bpy
from mathutils import Vector

# Load base model (face_hair blend has pristine raw meshes)
bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")
arm = bpy.data.objects.get("Armature_Teacher")

# 1. REMOVE ANY MASK MODIFIERS from all body meshes
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        for m in list(obj.modifiers):
            if m.type == 'MASK':
                obj.modifiers.remove(m)
                print(f"Removed Mask modifier from {obj.name}")

# 2. APPLY ALL TRANSFORMS on body and outfit meshes to align origins and scales perfectly
# First set armature to REST pose so meshes are in rest shape
arm.data.pose_position = 'REST'
bpy.context.view_layer.update()

for obj_name in ["BodyBase", "BodyArm", "BodyLeg", "Outfit_Shirt", "Outfit_Cape", "Outfit_Sleeves", "Outfit_Belt", "Outfit_Skirt", "Outfit_Boots"]:
    obj = bpy.data.objects.get(obj_name)
    if obj:
        # Bake transform into mesh vertices
        mw = obj.matrix_world
        # If matrix is not identity, apply it
        if mw != mw.identity():
            mesh = obj.data
            for v in mesh.vertices:
                v.co = mw @ v.co
            obj.location = (0, 0, 0)
            obj.rotation_euler = (0, 0, 0)
            obj.scale = (1, 1, 1)
            print(f"Applied transforms on {obj_name}")

bpy.context.view_layer.update()

# 3. ALIGN ARM EDIT BONES TO EXACT MESH CROSS-SECTION CENTERS
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones

# Symmetric bone positions matching BodyArm cross-section centers
# Shoulder head: X=±0.040, Z=-0.265
# Shoulder tail / UpperArm head: X=±0.145, Z=-0.276
# UpperArm tail / Forearm head: X=±0.280, Z=-0.279
# Forearm tail / Hand head: X=±0.415, Z=-0.265
# Hand tail: X=±0.510, Z=-0.258

for side, sign in [('L', 1), ('R', -1)]:
    sh = eb.get(f"Shoulder.{side}")
    ua = eb.get(f"UpperArm.{side}")
    fa = eb.get(f"Forearm.{side}")
    ha = eb.get(f"Hand.{side}")
    
    if sh:
        sh.head = Vector((sign * 0.040, 0.0, -0.265))
        sh.tail = Vector((sign * 0.145, 0.0, -0.276))
        sh.roll = 0.0
    if ua:
        ua.head = Vector((sign * 0.145, 0.0, -0.276))
        ua.tail = Vector((sign * 0.280, 0.0, -0.279))
        ua.roll = 0.0
    if fa:
        fa.head = Vector((sign * 0.280, 0.0, -0.279))
        fa.tail = Vector((sign * 0.415, 0.0, -0.265))
        fa.roll = 0.0
    if ha:
        ha.head = Vector((sign * 0.415, 0.0, -0.265))
        ha.tail = Vector((sign * 0.510, 0.0, -0.258))
        ha.roll = 0.0

# Also remove unused skirt bones
for bname in ["Skirt_B", "Skirt_F", "Skirt_L", "Skirt_R"]:
    b = eb.get(bname)
    if b:
        eb.remove(b)

bpy.ops.object.mode_set(mode='OBJECT')
print("Aligned all arm bones to exact mesh centers.")

# 4. TRANSFER FACIAL SHAPE KEYS (Mouth_Close, Blink)
# Load shape keys from h03 or script
import sys
# Facial shape keys script logic
face = bpy.data.objects.get("Face")
if not face.data.shape_keys:
    face.shape_key_add(name="Basis")

# Mouth_Close
sk_mouth = face.data.shape_keys.key_blocks.get("Mouth_Close") or face.shape_key_add(name="Mouth_Close")
basis_face = face.data.shape_keys.key_blocks["Basis"]
vg_mouth = face.vertex_groups.get("grp_mouth")
if vg_mouth:
    for v in face.data.vertices:
        w = 0.0
        for g in v.groups:
            if g.group == vg_mouth.index: w = g.weight; break
        co = Vector(basis_face.data[v.index].co)
        if w > 0.01:
            if co.z < -0.1375:
                lift = 0.0082 * w * min(1.0, (-0.1375 - co.z) / 0.012)
                co.z += lift
                co.y -= 0.002 * w
            else:
                drop = 0.0028 * w * min(1.0, (co.z - (-0.1375)) / 0.010)
                co.z -= drop
        if 474 <= v.index <= 491:
            co.z = -0.1375 + (co.z - (-0.1375)) * 0.1
            co.y -= 0.003
        sk_mouth.data[v.index].co = co

# Blink
sk_blink = face.data.shape_keys.key_blocks.get("Blink") or face.shape_key_add(name="Blink")
def get_lower_lid_z(x):
    dx = x - (-0.125)
    return -0.048 + 5.8 * (dx ** 2)

vg_eye = face.vertex_groups.get("grp_eye")
for v in face.data.vertices:
    w = 0.0
    if vg_eye:
        for g in v.groups:
            if g.group == vg_eye.index: w = g.weight; break
    co = Vector(basis_face.data[v.index].co)
    if w > 0.05:
        target_z = get_lower_lid_z(co.x)
        if co.z > target_z:
            drop_factor = min(1.0, max(0.0, (co.z - (-0.02)) / (0.052 - (-0.02))))
            new_z = co.z - (co.z - target_z) * drop_factor * 1.12
            new_y = co.y - 0.003 * drop_factor
            co.z = new_z
            co.y = new_y
        elif co.z < target_z and co.z > -0.07:
            co.z += 0.0035 * w
    sk_blink.data[v.index].co = co

# Eye, Eyelashes, DoubleLid, Eyebrow blink keys
eye = bpy.data.objects.get("Eye")
if eye:
    if not eye.data.shape_keys: eye.shape_key_add(name="Basis")
    sk_eye = eye.data.shape_keys.key_blocks.get("Blink") or eye.shape_key_add(name="Blink")
    basis_eye = eye.data.shape_keys.key_blocks["Basis"]
    for i, v in enumerate(basis_eye.data):
        new_co = Vector(v.co)
        new_co.z = -0.035 + (new_co.z - (-0.035)) * 0.02
        new_co.y += 0.035
        sk_eye.data[i].co = new_co

el3 = bpy.data.objects.get("Eyelash.003")
if el3:
    if not el3.data.shape_keys: el3.shape_key_add(name="Basis")
    sk_el3 = el3.data.shape_keys.key_blocks.get("Blink") or el3.shape_key_add(name="Blink")
    basis_el3 = el3.data.shape_keys.key_blocks["Basis"]
    for i, v in enumerate(basis_el3.data):
        new_co = Vector(v.co)
        new_co.z -= 0.088
        new_co.y += 0.018
        sk_el3.data[i].co = new_co

el1 = bpy.data.objects.get("Eyelash.001")
if el1:
    if not el1.data.shape_keys: el1.shape_key_add(name="Basis")
    sk_el1 = el1.data.shape_keys.key_blocks.get("Blink") or el1.shape_key_add(name="Blink")
    basis_el1 = el1.data.shape_keys.key_blocks["Basis"]
    for i, v in enumerate(basis_el1.data):
        new_co = Vector(v.co)
        t = (v.co.x - (-0.175)) / (-0.157 - (-0.175) + 1e-5)
        new_co.z -= (0.052 + 0.028 * t)
        new_co.y += (0.008 + 0.010 * t)
        sk_el1.data[i].co = new_co

el2 = bpy.data.objects.get("Eyelash.002")
if el2:
    if not el2.data.shape_keys: el2.shape_key_add(name="Basis")
    sk_el2 = el2.data.shape_keys.key_blocks.get("Blink") or el2.shape_key_add(name="Blink")
    basis_el2 = el2.data.shape_keys.key_blocks["Basis"]
    mw_el = el2.matrix_world
    imw_el = mw_el.inverted()
    for i, v in enumerate(basis_el2.data):
        wco = mw_el @ v.co
        wco.z -= 0.038
        wco.y += 0.005
        sk_el2.data[i].co = imw_el @ wco

dl = bpy.data.objects.get("DoubleLid")
if dl:
    if not dl.data.shape_keys: dl.shape_key_add(name="Basis")
    sk_dl = dl.data.shape_keys.key_blocks.get("Blink") or dl.shape_key_add(name="Blink")
    basis_dl = dl.data.shape_keys.key_blocks["Basis"]
    for i, v in enumerate(basis_dl.data):
        new_co = Vector(v.co)
        new_co.z -= 0.072
        new_co.y += 0.016
        sk_dl.data[i].co = new_co

eb_obj = bpy.data.objects.get("Eyebrow")
if eb_obj:
    if not eb_obj.data.shape_keys: eb_obj.shape_key_add(name="Basis")
    sk_eb = eb_obj.data.shape_keys.key_blocks.get("Blink") or eb_obj.shape_key_add(name="Blink")
    basis_eb = eb_obj.data.shape_keys.key_blocks["Basis"]
    for i, v in enumerate(basis_eb.data):
        new_co = Vector(v.co)
        new_co.z -= 0.004
        sk_eb.data[i].co = new_co

# 5. OPTIMIZE OUTFIT_SHIRT SOLIDIFY to avoid cape penetration
shirt = bpy.data.objects.get("Outfit_Shirt")
if shirt:
    s_mod = shirt.modifiers.get("Solidify")
    if s_mod:
        s_mod.thickness = 0.003
        s_mod.offset = -1.0

# 6. SAVE TO NEW FILE: teacher_ac_merged_h05.blend
out_file = "Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h05.blend"
bpy.ops.wm.save_as_mainfile(filepath=out_file)
print(f"Saved cleaned and fully aligned model to: {out_file}")

# 7. RENDER VERIFICATION
# Render front view of Armature + BodyBase + BodyArm to see bone centered in arm
cam = bpy.data.objects.get("CAM_Front") or bpy.data.objects.get("MainCamera")
bpy.context.scene.camera = cam

bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 720

# Render with outfits hidden (Rest pose body)
for obj in bpy.data.objects:
    if "outfit" in obj.name.lower():
        obj.hide_render = True

arm.data.pose_position = 'REST'
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/renders_test/h05_rest_body.png"
bpy.ops.render.render(write_still=True)
print("Rendered h05_rest_body.png")

# Render with outfits shown (Rest pose full)
for obj in bpy.data.objects:
    if "outfit" in obj.name.lower():
        obj.hide_render = False

bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/renders_test/h05_rest_outfits.png"
bpy.ops.render.render(write_still=True)
print("Rendered h05_rest_outfits.png")
