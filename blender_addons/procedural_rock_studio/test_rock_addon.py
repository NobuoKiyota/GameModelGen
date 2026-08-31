import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\rock_studio_addon.py"
with open(addon_path, 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code, globals())

print("=== Testing Full Native Sapling Suite (v7.4.1) ===")

species_list = ["OAK", "JAPANESE_MAPLE", "PINE", "WILLOW", "BIRCH"]
for sp in species_list:
    tree = generate_procedural_prop_mesh(
        context=bpy.context,
        target_obj=None,
        category="TREE",
        name=f"Tree_{sp}",
        tree_species=sp,
        tree_has_leaves=True,
        tree_leaf_count=120,
        tree_branch_levels=2,
        size_z=4.5,
        seed=random.randint(1, 9999)
    )
    print(f"-> Species {sp:15s}: Name={tree.name:15s}, Verts={len(tree.data.vertices):6d}, Polys={len(tree.data.polygons):6d}, Mats={len(tree.data.materials)}")

print("=== ALL SPECIES PASSED BEAUTIFULLY! ===")
