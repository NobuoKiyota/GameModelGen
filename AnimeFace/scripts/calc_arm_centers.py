import bpy
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_face_hair.blend")
body_arm = bpy.data.objects.get("BodyArm")
mw = body_arm.matrix_world

# Get all vertices in world coordinates
w_verts = [mw @ v.co for v in body_arm.data.vertices]

# Calculate cross-section centers along X axis (Right arm: X < 0)
# Shoulder: X ~ -0.14
# UpperArm mid: X ~ -0.21
# Elbow: X ~ -0.28
# Forearm mid: X ~ -0.35
# Wrist: X ~ -0.42
# Hand tip: X ~ -0.51

def get_section_center(x_target, tol=0.03):
    pts = [v for v in w_verts if abs(v.x - x_target) <= tol]
    if not pts:
        return None
    return Vector((
        sum(p.x for p in pts) / len(pts),
        sum(p.y for p in pts) / len(pts),
        sum(p.z for p in pts) / len(pts)
    ))

print("=== ACCURATE ARM MESH CENTERS (Right Arm X < 0) ===")
print("Shoulder base (X=-0.06):", get_section_center(-0.06))
print("Shoulder head (X=-0.14):", get_section_center(-0.14))
print("UpperArm mid  (X=-0.21):", get_section_center(-0.21))
print("Elbow joint   (X=-0.28):", get_section_center(-0.28))
print("Forearm mid   (X=-0.35):", get_section_center(-0.35))
print("Wrist joint   (X=-0.42):", get_section_center(-0.42))
print("Hand center   (X=-0.48):", get_section_center(-0.48))
