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

print("=== Testing Procedural Bush & Shrub Engine (All 4 Types) ===")

bush_types = ["ROUND_BUSH", "WILD_SHRUB", "FERN_CLUMP", "HEDGE_ROW"]
created_objects = []

for btype in bush_types:
    obj = generate_procedural_prop_mesh(
        context=bpy.context,
        target_obj=None,
        category="BUSH",
        name=f"Test_Bush_{btype}",
        bush_type=btype,
        bush_foliage_style="LEAF_CARDS",
        size_x=1.4,
        size_y=1.4,
        size_z=1.0,
        bush_density=16,
        bush_leaf_size=0.32,
        seed=202
    )
    
    verts_count = len(obj.data.vertices)
    faces_count = len(obj.data.polygons)
    mats = [m.name for m in obj.data.materials]
    
    print(f"[{btype}] Verts: {verts_count}, Faces: {faces_count}, Materials: {mats}")
    assert verts_count > 0, f"Error: No vertices for {btype}"
    assert faces_count > 0, f"Error: No faces for {btype}"
    assert len(mats) >= 2, f"Error: Material slots should be >= 2 for {btype}"
    assert mats[0].endswith("_Leaf_Mat"), f"Error: First material should be Leaf_Mat for {btype}"
    assert mats[1].endswith("_Stem_Mat"), f"Error: Second material should be Stem_Mat for {btype}"
    created_objects.append(obj)

print("=== ALL 4 BUSH TYPES TEST PASSED 100% ===")
