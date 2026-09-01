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

print("=== Testing Procedural Wooden Fence Engine (All 4 Types) ===")

fence_types = ["POST_AND_RAIL", "PICKET", "CROSS_BRACE", "PALISADE"]
created_objects = []

for ftype in fence_types:
    obj = generate_procedural_prop_mesh(
        context=bpy.context,
        target_obj=None,
        category="FENCE",
        name=f"Test_Fence_{ftype}",
        fence_type=ftype,
        size_x=5.0,
        size_y=0.4,
        size_z=1.3,
        fence_rails_count=3,
        fence_post_spacing=1.5,
        fence_decay_jitter=0.04,
        seed=101
    )
    
    verts_count = len(obj.data.vertices)
    faces_count = len(obj.data.polygons)
    mats = [m.name for m in obj.data.materials]
    
    print(f"[{ftype}] Verts: {verts_count}, Faces: {faces_count}, Materials: {mats}")
    assert verts_count > 0, f"Error: No vertices for {ftype}"
    assert faces_count > 0, f"Error: No faces for {ftype}"
    assert len(mats) >= 2, f"Error: Material slots should be >= 2 for {ftype}"
    assert mats[0].endswith("_Wood_Mat"), f"Error: First material should be Wood_Mat for {ftype}"
    assert mats[1].endswith("_Rope_Mat"), f"Error: Second material should be Rope_Mat for {ftype}"
    created_objects.append(obj)

print("=== ALL 4 FENCE TYPES TEST PASSED 100% ===")
