import bpy
from mathutils import Vector

def add_shape_key_if_needed(obj, name):
    if not obj.data.shape_keys:
        obj.shape_key_add(name="Basis")
    sk = obj.data.shape_keys.key_blocks.get(name)
    if not sk:
        sk = obj.shape_key_add(name=name)
    return sk

# --- 1. FACE: Blink & Mouth_Close ---
face = bpy.data.objects.get("Face")
mesh = face.data
if not mesh.shape_keys:
    face.shape_key_add(name="Basis")

# 1-a. Mouth_Close
sk_mouth = add_shape_key_if_needed(face, "Mouth_Close")
basis_face = mesh.shape_keys.key_blocks["Basis"]
vg_mouth = face.vertex_groups.get("grp_mouth")

if vg_mouth:
    for v in mesh.vertices:
        w = 0.0
        for g in v.groups:
            if g.group == vg_mouth.index:
                w = g.weight
                break
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

# 1-b. Blink
sk_face_blink = add_shape_key_if_needed(face, "Blink")

def get_lower_lid_z(x):
    dx = x - (-0.125)
    return -0.048 + 5.8 * (dx ** 2)

vg_eye = face.vertex_groups.get("grp_eye")
for v in mesh.vertices:
    w = 0.0
    if vg_eye:
        for g in v.groups:
            if g.group == vg_eye.index:
                w = g.weight
                break
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
    sk_face_blink.data[v.index].co = co

# --- 2. EYE: Retract & Flatten ---
eye = bpy.data.objects.get("Eye")
if eye:
    sk_eye = add_shape_key_if_needed(eye, "Blink")
    basis_eye = eye.data.shape_keys.key_blocks["Basis"]
    for i, v in enumerate(basis_eye.data):
        new_co = Vector(v.co)
        new_co.z = -0.035 + (new_co.z - (-0.035)) * 0.02
        new_co.y += 0.035
        sk_eye.data[i].co = new_co

# --- 3. EYELASHES ---
el3 = bpy.data.objects.get("Eyelash.003")
if el3:
    sk_el3 = add_shape_key_if_needed(el3, "Blink")
    basis_el3 = el3.data.shape_keys.key_blocks["Basis"]
    for i, v in enumerate(basis_el3.data):
        new_co = Vector(v.co)
        new_co.z -= 0.088
        new_co.y += 0.018
        sk_el3.data[i].co = new_co

el1 = bpy.data.objects.get("Eyelash.001")
if el1:
    sk_el1 = add_shape_key_if_needed(el1, "Blink")
    basis_el1 = el1.data.shape_keys.key_blocks["Basis"]
    for i, v in enumerate(basis_el1.data):
        new_co = Vector(v.co)
        t = (v.co.x - (-0.175)) / (-0.157 - (-0.175) + 1e-5)
        dz = 0.052 + 0.028 * t
        dy = 0.008 + 0.010 * t
        new_co.z -= dz
        new_co.y += dy
        sk_el1.data[i].co = new_co

el2 = bpy.data.objects.get("Eyelash.002")
if el2:
    sk_el2 = add_shape_key_if_needed(el2, "Blink")
    basis_el2 = el2.data.shape_keys.key_blocks["Basis"]
    mw = el2.matrix_world
    imw = mw.inverted()
    for i, v in enumerate(basis_el2.data):
        wco = mw @ v.co
        wco.z -= 0.038
        wco.y += 0.005
        sk_el2.data[i].co = imw @ wco

# DoubleLid
dl = bpy.data.objects.get("DoubleLid")
if dl:
    sk_dl = add_shape_key_if_needed(dl, "Blink")
    basis_dl = dl.data.shape_keys.key_blocks["Basis"]
    for i, v in enumerate(basis_dl.data):
        new_co = Vector(v.co)
        new_co.z -= 0.072
        new_co.y += 0.016
        sk_dl.data[i].co = new_co

# Eyebrow
eb = bpy.data.objects.get("Eyebrow")
if eb:
    sk_eb = add_shape_key_if_needed(eb, "Blink")
    basis_eb = eb.data.shape_keys.key_blocks["Basis"]
    for i, v in enumerate(basis_eb.data):
        new_co = Vector(v.co)
        new_co.z -= 0.004
        sk_eb.data[i].co = new_co

# --- 4. KEYFRAME ANIMATION ON SHAPE KEYS ---
# Blink objects
blink_objs = [face, eye, el1, el2, el3, dl, eb]

# Set keyframes across 30-frame walk cycle (F1 to F30)
# F1..F10: Blink = 0.0
# F11: Blink = 0.35
# F12: Blink = 1.0 (Eyes fully closed)
# F13: Blink = 0.70
# F14: Blink = 0.15
# F15..F30: Blink = 0.0
# Mouth_Close: Constantly 0.85 (soft pleasant closed smile) throughout loop
blink_keys = [
    (1, 0.0),
    (10, 0.0),
    (11, 0.35),
    (12, 1.0),
    (13, 0.70),
    (14, 0.15),
    (15, 0.0),
    (30, 0.0),
    (31, 0.0),
]

for obj in blink_objs:
    if not obj or not obj.data.shape_keys:
        continue
    sk = obj.data.shape_keys.key_blocks.get("Blink")
    if not sk:
        continue
    for frame, val in blink_keys:
        sk.value = val
        sk.keyframe_insert("value", frame=frame)
    # Set default value to 0.0
    sk.value = 0.0

if face and face.data.shape_keys:
    sk_m = face.data.shape_keys.key_blocks.get("Mouth_Close")
    if sk_m:
        # Subtle gentle smile breathing: 0.82 to 0.88 across walk loop
        for f in range(1, 32):
            import math
            val = 0.85 + 0.05 * math.sin((f - 1) / 30.0 * 2.0 * math.pi)
            sk_m.value = val
            sk_m.keyframe_insert("value", frame=f)
        sk_m.value = 0.85

# --- 5. CLEAN UP UNUSED SKIRT BONES ---
arm = bpy.data.objects.get("Armature")
if arm:
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    for bname in ["Skirt_B", "Skirt_F", "Skirt_L", "Skirt_R"]:
        ebone = arm.data.edit_bones.get(bname)
        if ebone:
            arm.data.edit_bones.remove(ebone)
            print(f"Removed unused bone: {bname}")
    bpy.ops.object.mode_set(mode='OBJECT')

# Save to teacher_ac_merged_h03.blend
bpy.ops.wm.save_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h03.blend")
print("Saved updated model with facial shape keys and animation to teacher_ac_merged_h03.blend")
