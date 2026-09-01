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
from procedural_rock_studio.utils.anim_baker import export_animated_water_fbx

print("=== Testing Animated Water & FBX Exporter ===")

# 1. 水面メッシュ（湖）の生成（アニメーション付き）
obj = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="WATER",
    name="Test_Lake_Animated",
    water_shape="LAKE",
    water_color_type="TROPICAL",
    water_wave_strength=0.15,
    water_animate=True,
    water_wind_speed=1.2,
    water_anim_frames=48,
    size_x=5.0,
    size_y=5.0,
    size_z=0.5,
    seed=101
)

print(f"Generated Water: {obj.name}, Verts: {len(obj.data.vertices)}, Modifiers: {[m.name for m in obj.modifiers]}")
assert len(obj.data.vertices) > 0, "Error: No vertices in water mesh"
assert any(m.type in ('WAVE', 'OCEAN') for m in obj.modifiers), "Error: No wave modifier found on water mesh"

# 2. シェイプキーベイク ＆ アニメーションFBX出力
export_dir = r"z:\MeshCreator\exports\test_water"
os.makedirs(export_dir, exist_ok=True)
out_fbx = os.path.join(export_dir, "Test_Lake_Loop.fbx")

export_animated_water_fbx(obj, out_fbx, frames_count=48)

assert os.path.exists(out_fbx), f"Error: FBX file was not generated at {out_fbx}"
fbx_size = os.path.getsize(out_fbx)
print(f"✅ Animated FBX Export Success! Size: {fbx_size} bytes, Path: {out_fbx}")
assert fbx_size > 5000, "Error: FBX file is too small, animation likely missing"

# 3. シェイプキーの検証
assert obj.data.shape_keys is not None, "Error: Shape keys were not created"
shape_count = len(obj.data.shape_keys.key_blocks)
print(f"Shape Keys Baked: {shape_count} keys")
assert shape_count >= 10, "Error: Too few shape keys baked"

print("=== ALL ANIMATED WATER TESTS PASSED 100% ===")
