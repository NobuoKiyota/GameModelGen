import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\rock_studio_addon.py"
with open(addon_path, 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code, globals())

print("=== Testing Advanced Procedural Shader Generation (v7.6) ===")

species_list = ["OAK", "JAPANESE_MAPLE", "PINE", "WILLOW", "BIRCH"]
for sp in species_list:
    tree = generate_procedural_prop_mesh(
        context=bpy.context,
        target_obj=None,
        category="TREE",
        name=f"Tree_{sp}",
        tree_species=sp,
        tree_has_leaves=True,
        tree_leaf_count=100,
        tree_branch_levels=2,
        tree_mat_mode="PROCEDURAL",
        size_z=4.5,
        seed=333
    )
    mat_names = [m.name for m in tree.data.materials if m]
    print(f"-> Species {sp:15s}: Name={tree.name:15s}, Mats={mat_names}")

print("=== ALL PROCEDURAL SHADERS PASSED! ===")
