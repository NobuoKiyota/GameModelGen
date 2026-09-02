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

print("=== Testing Procedural Pillar Engine (All 4 Types) ===")

types = [
    ("GOTHIC_CLUSTERED", "MARBLE"),
    ("ROMAN_FLUTED", "ANCIENT_STONE"),
    ("RUINED_ANCIENT", "MOSSY_RUINS"),
    ("SQUARE_MONUMENT", "MARBLE")
]

for p_type, mat_type in types:
    obj = generate_procedural_prop_mesh(
        context=bpy.context,
        target_obj=None,
        category="PILLAR",
        name=f"Test_Pillar_{p_type}",
        pillar_type=p_type,
        pillar_mat_type=mat_type,
        pillar_height=4.0,
        pillar_radius=0.4,
        pillar_colonnettes=6,
        pillar_flutes=18,
        seed=101
    )
    
    verts_count = len(obj.data.vertices)
    faces_count = len(obj.data.polygons)
    mats = [m.name for m in obj.data.materials if m]
    mods = [m.name for m in obj.modifiers]
    
    print(f"[{p_type}] Verts: {verts_count}, Faces: {faces_count}, Mats: {mats}, Mods: {mods}")
    assert verts_count >= 32, f"Error: {p_type} has too few vertices"
    assert faces_count >= 20, f"Error: {p_type} has too few faces"
    assert len(mats) > 0, f"Error: {p_type} has no material"

print("=== ALL 4 PILLAR TYPES TEST PASSED 100% ===")
