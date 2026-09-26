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

# Basis
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

# 1-b. Blink (Face eye lid closure)
sk_face_blink = add_shape_key_if_needed(face, "Blink")

def get_lower_lid_z(x):
    # Eye curve
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
            new_z = co.z - (co.z - target_z) * drop_factor * 1.12 # slightly deeper
            new_y = co.y - 0.003 * drop_factor
            co.z = new_z
            co.y = new_y
        elif co.z < target_z and co.z > -0.07:
            # lower lid lifts slightly
            co.z += 0.0035 * w
    sk_face_blink.data[v.index].co = co

# --- 2. EYE: Retract & Flatten ---
eye = bpy.data.objects.get("Eye")
if eye:
    sk_eye = add_shape_key_if_needed(eye, "Blink")
    basis_eye = eye.data.shape_keys.key_blocks["Basis"]
    for i, v in enumerate(basis_eye.data):
        new_co = Vector(v.co)
        # Pull back and flatten
        new_co.z = -0.035 + (new_co.z - (-0.035)) * 0.02
        new_co.y += 0.035
        sk_eye.data[i].co = new_co

# --- 3. EYELASHES ---
# Eyelash.003 (Main arch)
el3 = bpy.data.objects.get("Eyelash.003")
if el3:
    sk_el3 = add_shape_key_if_needed(el3, "Blink")
    basis_el3 = el3.data.shape_keys.key_blocks["Basis"]
    for i, v in enumerate(basis_el3.data):
        new_co = Vector(v.co)
        new_co.z -= 0.088
        new_co.y += 0.018
        sk_el3.data[i].co = new_co

# Eyelash.001 (Outer wing lash)
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

# Eyelash.002 (Outer wing tip)
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
        new_co.z -= 0.004 # 4mm relax drop
        sk_eb.data[i].co = new_co

# --- TEST RENDER: Closed Eyes + Closed Mouth ---
for o in [face, eye, el1, el2, el3, dl, eb]:
    if o and o.data.shape_keys:
        k = o.data.shape_keys.key_blocks.get("Blink")
        if k: k.value = 1.0
if face and face.data.shape_keys:
    k = face.data.shape_keys.key_blocks.get("Mouth_Close")
    if k: k.value = 1.0

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
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/test_blink_v03_closed.png"
bpy.ops.render.render(write_still=True)
print("Rendered test_blink_v03_closed.png")

# --- TEST RENDER: Open Eyes + Closed Mouth ---
for o in [face, eye, el1, el2, el3, dl, eb]:
    if o and o.data.shape_keys:
        k = o.data.shape_keys.key_blocks.get("Blink")
        if k: k.value = 0.0
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/test_blink_v03_open.png"
bpy.ops.render.render(write_still=True)
print("Rendered test_blink_v03_open.png")
