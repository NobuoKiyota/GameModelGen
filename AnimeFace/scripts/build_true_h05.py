import bpy
from mathutils import Vector

# Open pristine face_hair model
bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")
arm = bpy.data.objects.get("Armature_Teacher")

# Set rest pose
arm.data.pose_position = 'REST'
bpy.context.view_layer.update()

# 1. Remove all mask modifiers
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        for m in list(obj.modifiers):
            if m.type == 'MASK':
                obj.modifiers.remove(m)
                print(f"Removed Mask modifier from {obj.name}")

# 2. Safely apply all transforms to mesh data
mesh_objs = [
    "BodyBase", "BodyArm", "BodyLeg",
    "Outfit_Shirt", "Outfit_Cape", "Outfit_Sleeves", "Outfit_Belt", "Outfit_Skirt", "Outfit_Boots"
]

for name in mesh_objs:
    obj = bpy.data.objects.get(name)
    if not obj: continue
    
    # Store armature modifier
    arm_mod = None
    for m in obj.modifiers:
        if m.type == 'ARMATURE':
            arm_mod = m
            m.show_viewport = False
            m.show_render = False
    
    # Bake matrix_world into vertices
    mw = obj.matrix_world.copy()
    if mw != mw.identity():
        for v in obj.data.vertices:
            v.co = mw @ v.co
        obj.location = (0, 0, 0)
        obj.rotation_euler = (0, 0, 0)
        obj.scale = (1, 1, 1)
        print(f"Applied transforms to {name}: loc=(0,0,0), scale=(1,1,1)")
    
    if arm_mod:
        arm_mod.show_viewport = True
        arm_mod.show_render = True

bpy.context.view_layer.update()

# 3. Check BodyArm exact center in its new applied space (local = world now!)
body_arm = bpy.data.objects.get("BodyArm")
verts = body_arm.data.vertices

# Measure Right Arm section centers (X < 0)
def get_sec_z(x_min, x_max):
    pts = [v.co for v in verts if x_min <= v.co.x <= x_max]
    return sum(p.z for p in pts) / len(pts)

sh_z = get_sec_z(-0.15, -0.04) # Shoulder
ua_z = get_sec_z(-0.28, -0.15) # UpperArm
fa_z = get_sec_z(-0.42, -0.28) # Forearm
ha_z = get_sec_z(-0.52, -0.42) # Hand

print(f"\nExact section Z centers of BodyArm:")
print(f"  Shoulder Z: {sh_z:.4f}")
print(f"  UpperArm Z: {ua_z:.4f}")
print(f"  Forearm  Z: {fa_z:.4f}")
print(f"  Hand     Z: {ha_z:.4f}")

# 4. Correct EditBone Z positions to match exact arm mesh centers!
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones

for side, sign in [('L', 1), ('R', -1)]:
    sh = eb.get(f"Shoulder.{side}")
    ua = eb.get(f"UpperArm.{side}")
    fa = eb.get(f"Forearm.{side}")
    ha = eb.get(f"Hand.{side}")
    
    # Set heads and tails to exactly follow the arm centers:
    # Shoulder: head Z = sh_z + 0.005, tail Z = ua_z
    # UpperArm: head Z = ua_z, tail Z = (ua_z + fa_z)/2 (elbow)
    # Forearm : head Z = (ua_z + fa_z)/2, tail Z = (fa_z + ha_z)/2 (wrist)
    # Hand    : head Z = (fa_z + ha_z)/2, tail Z = ha_z
    
    elbow_z = (ua_z + fa_z) / 2.0
    wrist_z = (fa_z + ha_z) / 2.0
    
    if sh:
        sh.head.z = sh_z + 0.005
        sh.tail.z = ua_z
        sh.head.y = 0.0
        sh.tail.y = 0.0
    if ua:
        ua.head.z = ua_z
        ua.tail.z = elbow_z
        ua.head.y = 0.0
        ua.tail.y = 0.0
    if fa:
        fa.head.z = elbow_z
        fa.tail.z = wrist_z
        fa.head.y = 0.0
        fa.tail.y = 0.0
    if ha:
        ha.head.z = wrist_z
        ha.tail.z = ha_z
        ha.head.y = 0.0
        ha.tail.y = 0.0

# Remove unused skirt bones
for bname in ["Skirt_B", "Skirt_F", "Skirt_L", "Skirt_R"]:
    b = eb.get(bname)
    if b: eb.remove(b)

bpy.ops.object.mode_set(mode='OBJECT')
print("Successfully centered all arm bones directly inside arm mesh!")

# 5. Add Facial Shape Keys
face = bpy.data.objects.get("Face")
if not face.data.shape_keys: face.shape_key_add(name="Basis")

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

# Blink on Eye, Eyelashes, DoubleLid, Eyebrow
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

# 6. Save as teacher_ac_merged_h05.blend
out_file = "Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h05.blend"
bpy.ops.wm.save_as_mainfile(filepath=out_file)
print(f"Saved true centered model to: {out_file}")
