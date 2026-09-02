import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_parent = r"z:\MeshCreator\blender_addons"
if addon_parent not in sys.path:
    sys.path.insert(0, addon_parent)

from procedural_rock_studio import rock_studio_addon
rock_studio_addon.register()

from procedural_rock_studio.generators.core_orchestrator import generate_procedural_prop_mesh

print("=== Testing Procedural Astronomical Telescope Engine ===")

root_obj = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="TELESCOPE",
    name="Test_Telescope",
    telescope_elevation=35.0,
    telescope_azimuth=60.0,
    telescope_tripod_height=1.1,
    telescope_tube_length=0.8,
    seed=42
)

assert root_obj is not None, "Error: Root object was not created"
print(f"Root object: {root_obj.name}, Type: {root_obj.type}")

children = list(root_obj.children_recursive)
print(f"Generated parts count: {len(children)}")
for c in children:
    verts = len(c.data.vertices) if c.type == 'MESH' else 0
    faces = len(c.data.polygons) if c.type == 'MESH' else 0
    mats = [m.name for m in c.data.materials if m] if c.type == 'MESH' else []
    print(f"  - {c.name}: Type={c.type}, Verts={verts}, Faces={faces}, Mats={mats}, Parent={c.parent.name if c.parent else None}")

# 階層とパーツの検証
tripod = [c for c in children if "Tripod" in c.name]
mount = [c for c in children if "Mount" in c.name]
ota = [c for c in children if "OTA" in c.name]

assert len(tripod) > 0, "Error: Tripod part missing"
assert len(mount) > 0, "Error: Mount part missing"
assert len(ota) > 0, "Error: OTA part missing"

assert len(tripod[0].data.vertices) > 100, "Error: Tripod mesh too simple"
assert len(ota[0].data.vertices) > 200, "Error: OTA mesh too simple"
assert len(ota[0].data.materials) >= 4, "Error: OTA missing 4 PBR materials"

print("=== ALL TELESCOPE ENGINE TESTS PASSED 100% ===")
