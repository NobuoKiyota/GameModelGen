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
from procedural_rock_studio.generators.dictionary_gen import sample_random_dictionary_specs

print("=== 📖 Testing Procedural Dictionary Engine ===")

# Test 1: Generate Standard Neutral Dictionary
dict_obj = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="DICTIONARY",
    name="Test_Dictionary_Standard",
    size_x=0.16, # Width 16cm
    size_y=0.23, # Height 23cm
    size_z=0.065, # Thickness 6.5cm
    dictionary_rib_count=4,
    dictionary_color_preset='NAVY',
    dictionary_has_ribbon=True,
    seed=101
)

assert dict_obj is not None, "Error: Dictionary root object was not created"
print(f"Created Dictionary: {dict_obj.name}")

verts = len(dict_obj.data.vertices)
faces = len(dict_obj.data.polygons)
materials = [m.name for m in dict_obj.data.materials if m]
print(f"  - Vertices: {verts}")
print(f"  - Faces: {faces}")
print(f"  - Materials ({len(materials)}): {materials}")

assert verts > 200, f"Error: Dictionary mesh too simple ({verts} verts)"
assert faces > 150, f"Error: Dictionary mesh faces too low ({faces} faces)"
assert len(materials) >= 3, f"Error: Expected 3 material slots, got {len(materials)}"
assert "Cover" in materials[0], "Error: Material slot 0 must be Cover"
assert "Pages" in materials[1], "Error: Material slot 1 must be Pages"
assert "Ribbon" in materials[2], "Error: Material slot 2 must be Ribbon"
print("[OK] Test 1: Standard Dictionary generation passed!")

# Test 2: Random specs generator test (Thin, Medium, Giant thickness)
print("\n=== 🎲 Testing Random Variations (3 Seeds) ===")
test_seeds = [42, 999, 2026]
for s in test_seeds:
    specs = sample_random_dictionary_specs(seed=s)
    print(f"\nSeed {s} Specs:")
    print(f"  Width: {specs['width']*100:.1f}cm, Height: {specs['height']*100:.1f}cm, Thickness: {specs['thickness']*100:.1f}cm")
    print(f"  Color: {specs['color_preset']}, Ribs: {specs['rib_count']}, HasRibbon: {specs['has_ribbon']}")

    obj_variant = generate_procedural_prop_mesh(
        context=bpy.context,
        target_obj=None,
        category="DICTIONARY",
        name=f"Dictionary_Variant_Seed_{s}",
        size_x=specs['width'],
        size_y=specs['height'],
        size_z=specs['thickness'],
        dictionary_rib_count=specs['rib_count'],
        dictionary_color_preset=specs['color_preset'],
        dictionary_has_ribbon=specs['has_ribbon'],
        seed=s
    )
    v_count = len(obj_variant.data.vertices)
    f_count = len(obj_variant.data.polygons)
    print(f"  -> Generated {obj_variant.name}: {v_count} verts, {f_count} faces")
    assert v_count > 200

print("\n[OK] Test 2: Random Variations generation passed!")

# Test 3: FBX Export Test
export_path = r"z:\MeshCreator\blender_addons\procedural_rock_studio\Test_Dictionary_Export.fbx"
bpy.ops.object.select_all(action='DESELECT')
dict_obj.select_set(True)
bpy.context.view_layer.objects.active = dict_obj

bpy.ops.export_scene.fbx(
    filepath=export_path,
    use_selection=True,
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_NONE',
    bake_space_transform=False,
    use_space_transform=True,
    axis_forward='-Z',
    axis_up='Y'
)

assert os.path.exists(export_path), "Error: FBX file not created"
fbx_size = os.path.getsize(export_path)
print(f"\n[OK] Test 3: FBX Exported successfully! Size: {fbx_size} bytes -> {export_path}")

print("\n=== 🌟 ALL DICTIONARY ENGINE TESTS PASSED 100% ===")
