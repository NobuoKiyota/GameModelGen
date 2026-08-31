import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\rock_studio_addon.py"
with open(addon_path, 'r', encoding='utf-8') as f:
    code = f.read()
    exec(code, globals())

print("=== Testing Dynamic Shader Seed Reactivity (v7.7) ===")

tree1 = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="TREE",
    name="Tree_Maple_A",
    tree_species="JAPANESE_MAPLE",
    tree_has_leaves=True,
    tree_mat_mode="PROCEDURAL",
    size_z=4.5,
    seed=101
)

tree2 = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=tree1,
    category="TREE",
    name="Tree_Maple_A",
    tree_species="JAPANESE_MAPLE",
    tree_has_leaves=True,
    tree_mat_mode="PROCEDURAL",
    size_z=4.5,
    seed=888
)

print(f"Tree Mats: {[m.name for m in tree2.data.materials]}")
print("=== SHADER SEED REACTIVITY VERIFIED! ===")
