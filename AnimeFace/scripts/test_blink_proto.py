import bpy
from mathutils import Vector

def add_shape_key_if_needed(obj, name):
    if not obj.data.shape_keys:
        obj.shape_key_add(name="Basis")
    sk = obj.data.shape_keys.key_blocks.get(name)
    if not sk:
        sk = obj.shape_key_add(name=name)
    return sk

# 1. DoubleLid
dl = bpy.data.objects.get("DoubleLid")
if dl:
    sk = add_shape_key_if_needed(dl, "Blink")
    basis = dl.data.shape_keys.key_blocks["Basis"]
    for i, v in enumerate(basis.data):
        # DoubleLid drops down by about 0.055 - 0.060m
        # x is between -0.065 and -0.171
        factor = 1.0
        new_co = Vector(v.co)
        new_co.z -= 0.058
        new_co.y += 0.015
        sk.data[i].co = new_co

# 2. Eyelash.003 (Main upper arch)
el3 = bpy.data.objects.get("Eyelash.003")
if el3:
    sk = add_shape_key_if_needed(el3, "Blink")
    basis = el3.data.shape_keys.key_blocks["Basis"]
    for i, v in enumerate(basis.data):
        new_co = Vector(v.co)
        new_co.z -= 0.075
        new_co.y += 0.025
        sk.data[i].co = new_co

# 3. Eyelash.001 (Outer upper arch)
el1 = bpy.data.objects.get("Eyelash.001")
if el1:
    sk = add_shape_key_if_needed(el1, "Blink")
    basis = el1.data.shape_keys.key_blocks["Basis"]
    for i, v in enumerate(basis.data):
        new_co = Vector(v.co)
        # Closer to outer edge drops a bit less
        # v.co.x ranges -0.175 to -0.157
        t = (v.co.x - (-0.175)) / (-0.157 - (-0.175) + 1e-5) # 0 at outer, 1 at inner
        dz = 0.045 + 0.025 * t
        dy = 0.010 + 0.012 * t
        new_co.z -= dz
        new_co.y += dy
        sk.data[i].co = new_co

# 4. Eyelash.002 (Outer wing)
el2 = bpy.data.objects.get("Eyelash.002")
if el2:
    sk = add_shape_key_if_needed(el2, "Blink")
    basis = el2.data.shape_keys.key_blocks["Basis"]
    # Eyelash.002 has local rotation/location, so modify in local space
    # In world, it should drop by ~0.035m in Z
    mw = el2.matrix_world
    imw = mw.inverted()
    for i, v in enumerate(basis.data):
        wco = mw @ v.co
        wco.z -= 0.035
        wco.y += 0.008
        sk.data[i].co = imw @ wco

# 5. Eye (Retract / flatten)
eye = bpy.data.objects.get("Eye")
if eye:
    sk = add_shape_key_if_needed(eye, "Blink")
    basis = eye.data.shape_keys.key_blocks["Basis"]
    for i, v in enumerate(basis.data):
        new_co = Vector(v.co)
        # Flatten Z towards -0.035 and push back in Y
        new_co.z = -0.035 + (new_co.z - (-0.035)) * 0.05
        new_co.y += 0.025
        sk.data[i].co = new_co

# Set Blink to 1.0 on all
for o in [dl, el1, el2, el3, eye]:
    if o and o.data.shape_keys:
        k = o.data.shape_keys.key_blocks.get("Blink")
        if k:
            k.value = 1.0

# Also test Mouth_Close
face = bpy.data.objects.get("Face")
if face:
    sk = add_shape_key_if_needed(face, "Mouth_Close")
    basis = face.data.shape_keys.key_blocks["Basis"]
    vg_mouth = face.vertex_groups.get("grp_mouth")
    if vg_mouth:
        for v in face.data.vertices:
            w = 0.0
            for g in v.groups:
                if g.group == vg_mouth.index:
                    w = g.weight
                    break
            co = Vector(basis.data[v.index].co)
            if w > 0.01:
                # Lower lip up, upper lip down
                if co.z < -0.1375:
                    lift = 0.0082 * w * min(1.0, (-0.1375 - co.z) / 0.012)
                    co.z += lift
                    co.y -= 0.002 * w
                else:
                    drop = 0.0028 * w * min(1.0, (co.z - (-0.1375)) / 0.010)
                    co.z -= drop
            # Oral cavity closure
            if 474 <= v.index <= 491:
                co.z = -0.1375 + (co.z - (-0.1375)) * 0.1
                co.y -= 0.003
            sk.data[v.index].co = co
    sk.value = 1.0

# Render test closed
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
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/test_blink_v01.png"
bpy.ops.render.render(write_still=True)
print("Rendered test_blink_v01.png")
