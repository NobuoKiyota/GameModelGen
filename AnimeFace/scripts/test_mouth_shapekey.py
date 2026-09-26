import bpy

face = bpy.data.objects['Face']

# Ensure Basis shape key
if not face.data.shape_keys:
    face.shape_key_add(name="Basis")

# Add or get Mouth_Close shape key
sk_mouth = face.data.shape_keys.key_blocks.get("Mouth_Close")
if not sk_mouth:
    sk_mouth = face.shape_key_add(name="Mouth_Close")

# Set target coordinates for closed mouth
# Target meeting line Z is around -0.1375 to -0.1360
# Lips meeting coordinates:
lip_mods = {
    # Lower lip: lift up to meet upper lip
    32:  {'z': +0.0080, 'y': -0.0010}, # center lower
    218: {'z': +0.0079, 'y': -0.0010}, # mid lower
    31:  {'z': +0.0065, 'y': -0.0005}, # side lower
    # Upper lip: slight downward adjustment to meet
    26:  {'z': -0.0028, 'y': -0.0005}, # center upper
    203: {'z': -0.0028, 'y': -0.0005}, # mid upper
    27:  {'z': -0.0025, 'y': -0.0005}, # side upper
    # Chin/under lip: slight lift
    39:  {'z': +0.0025, 'y': 0.0},
    219: {'z': +0.0025, 'y': 0.0},
    38:  {'z': +0.0020, 'y': 0.0},
    # Inner mouth cavity top: pull down
    474: {'z': -0.0060, 'y': 0.0},
    475: {'z': -0.0060, 'y': 0.0},
    476: {'z': -0.0060, 'y': 0.0},
    # Inner mouth cavity bottom: pull up
    482: {'z': +0.0065, 'y': 0.0},
    481: {'z': +0.0065, 'y': 0.0},
    480: {'z': +0.0030, 'y': 0.0},
    491: {'z': +0.0060, 'y': 0.0},
    490: {'z': +0.0060, 'y': 0.0},
    483: {'z': -0.0050, 'y': 0.0},
    484: {'z': -0.0050, 'y': 0.0},
}

basis = face.data.shape_keys.key_blocks['Basis']

# Reset all shape key points to Basis first
for i in range(len(face.data.vertices)):
    sk_mouth.data[i].co = basis.data[i].co

# Apply modifications
for vi, deltas in lip_mods.items():
    co = basis.data[vi].co.copy()
    if 'z' in deltas:
        co.z += deltas['z']
    if 'y' in deltas:
        co.y += deltas['y']
    if 'x' in deltas:
        co.x += deltas['x']
    sk_mouth.data[vi].co = co

# Test render with Mouth_Close = 1.0
sk_mouth.value = 1.0

scene = bpy.context.scene
scene.frame_set(1)
cam_front = bpy.data.objects.get('CAM_Front') or bpy.data.objects.get('MainCamera')
if cam_front:
    scene.camera = cam_front

scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/test_mouth_closed.png"
bpy.ops.render.render(write_still=True)
print("Rendered test_mouth_closed.png!")

# Render with Mouth_Close = 0.0 (open smile)
sk_mouth.value = 0.0
scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/test_mouth_open.png"
bpy.ops.render.render(write_still=True)
print("Rendered test_mouth_open.png!")
