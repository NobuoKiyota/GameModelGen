import bpy
from mathutils import Vector
import numpy as np

face = bpy.data.objects.get("Face")
mesh = face.data

# Basis & Blink shape key for Face
if not mesh.shape_keys:
    face.shape_key_add(name="Basis")
sk_face = mesh.shape_keys.key_blocks.get("Blink")
if not sk_face:
    sk_face = face.shape_key_add(name="Blink")

basis_face = mesh.shape_keys.key_blocks["Basis"]

# Lower lid reference function: given x in [-0.18, -0.06], returns target Z
# Eye center around x = -0.125, z = -0.048
# Corner inner x = -0.065, z = -0.024
# Corner outer x = -0.175, z = -0.015
def get_lower_lid_z(x):
    # Quadratic fit: z = a*(x - x0)^2 + z0
    # x0 = -0.125, z0 = -0.046
    # at x = -0.065: z0 + a*(0.06)^2 = -0.024 -> a * 0.0036 = 0.022 -> a ≈ 6.1
    # at x = -0.175: z0 + a*(0.05)^2 = -0.046 + 6.1*0.0025 = -0.031 (close to outer)
    dx = x - (-0.125)
    return -0.046 + 5.8 * (dx ** 2)

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
        # If vertex is in upper eyelid region (z > -0.02)
        target_z = get_lower_lid_z(co.x)
        if co.z > target_z:
            # Drop upper lid to lower lid
            # The closer to the rim (higher z originally, up to ~0.05), the more it drops
            # Upper rim is around z in [0.02, 0.055]
            drop_factor = min(1.0, max(0.0, (co.z - (-0.02)) / (0.052 - (-0.02))))
            # Move towards target_z
            new_z = co.z - (co.z - target_z) * drop_factor * 1.05
            # Push slightly forward in Y to follow facial contour
            new_y = co.y - 0.004 * drop_factor
            co.z = new_z
            co.y = new_y
        elif co.z < target_z and co.z > -0.07:
            # Lower lid lifts slightly (1~2mm)
            co.z += 0.003 * w

    sk_face.data[v.index].co = co

sk_face.value = 1.0

# Render closed face
cam = bpy.data.objects.get("FaceCam") or bpy.data.objects.get("Camera")
if not cam:
    cam_data = bpy.data.cameras.new("FaceCam")
    cam = bpy.data.objects.new("FaceCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
cam.location = (0.0, -0.65, 0.0)
cam.rotation_euler = (1.5708, 0.0, 0.0)
bpy.context.scene.camera = cam

# Unhide all eyelashes
for name in ["DoubleLid", "Eyelash.001", "Eyelash.002", "Eyelash.003"]:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.hide_render = False

bpy.context.scene.render.resolution_x = 800
bpy.context.scene.render.resolution_y = 800
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/test_blink_v02.png"
bpy.ops.render.render(write_still=True)
print("Rendered test_blink_v02.png")
