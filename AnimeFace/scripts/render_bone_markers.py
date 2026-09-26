import bpy
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath="Z:/MeshCreator/AnimeFace/out/teacher_ac_merged_h05.blend")
arm = bpy.data.objects.get("Armature_Teacher")

# Create temporary visualization spheres at bone heads/tails to see alignment with BodyArm
def make_marker(name, loc, radius=0.015, color=(0.1, 0.8, 0.2, 1.0)):
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

# Markers along arm bones
markers = []
for side in ['L', 'R']:
    for bname in [f"Shoulder.{side}", f"UpperArm.{side}", f"Forearm.{side}", f"Hand.{side}"]:
        b = arm.data.bones[bname]
        m1 = make_marker(f"M_{bname}_head", b.head_local, radius=0.012, color=(1.0, 0.2, 0.2, 1.0))
        m2 = make_marker(f"M_{bname}_tail", b.tail_local, radius=0.010, color=(0.2, 0.5, 1.0, 1.0))
        markers.extend([m1, m2])

# Hide hair & outfits
for obj in bpy.data.objects:
    if "hair" in obj.name.lower() or "outfit" in obj.name.lower():
        obj.hide_render = True

cam = bpy.data.objects.get("CAM_Front") or bpy.data.objects.get("MainCamera")
bpy.context.scene.camera = cam

bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.filepath = "Z:/MeshCreator/AnimeFace/out/renders_test/h05_bone_markers_front.png"
bpy.ops.render.render(write_still=True)
print("Rendered h05_bone_markers_front.png")
