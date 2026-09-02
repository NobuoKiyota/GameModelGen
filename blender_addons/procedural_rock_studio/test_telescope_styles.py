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

print("=== Testing All 5 Telescope Styles in Blender 3.6 ===")

styles = [
    "MODERN_REFRACTOR",
    "ANTIQUE_BRASS",
    "SMART_DIGITAL",
    "CASSEGRAIN_POP",
    "TACTICAL_COMPACT"
]

for st in styles:
    root_obj = generate_procedural_prop_mesh(
        context=bpy.context,
        target_obj=None,
        category="TELESCOPE",
        name=f"Test_{st}",
        telescope_style=st,
        telescope_elevation=30.0,
        telescope_azimuth=45.0,
        telescope_tripod_height=1.0,
        telescope_tube_length=0.75,
        seed=100
    )
    
    children = list(root_obj.children_recursive)
    print(f"\n[{st}] Parts count: {len(children)}")
    for c in children:
        verts = len(c.data.vertices) if c.type == 'MESH' else 0
        faces = len(c.data.polygons) if c.type == 'MESH' else 0
        mats = [m.name for m in c.data.materials if m] if c.type == 'MESH' else []
        print(f"  - {c.name}: Verts={verts}, Faces={faces}, Mats={mats}")
    
    assert len(children) == 3, f"Error: {st} does not have exactly 3 parts (Tripod, Mount, OTA)"
    tripod = [c for c in children if "Tripod" in c.name][0]
    mount = [c for c in children if "Mount" in c.name][0]
    ota = [c for c in children if "OTA" in c.name][0]
    
    assert len(tripod.data.vertices) > 50, f"Error: {st} tripod too simple"
    assert len(ota.data.vertices) > 100, f"Error: {st} ota too simple"
    assert len(ota.data.materials) >= 2, f"Error: {st} missing materials"

print("\n=== ALL 5 TELESCOPE STYLES TEST PASSED 100% ===")
