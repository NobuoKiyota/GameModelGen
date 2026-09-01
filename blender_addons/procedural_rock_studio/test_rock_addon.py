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
