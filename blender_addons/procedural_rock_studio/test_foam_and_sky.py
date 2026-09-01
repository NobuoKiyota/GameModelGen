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
from procedural_rock_studio.utils.sky_lighting import setup_procedural_sky_lighting

print("=== Testing Foam Shader & Nishita Sky Lighting ===")

# 1. Nishita スカイライティングのセットアップ
world = setup_procedural_sky_lighting(bpy.context)
assert world is not None, "Error: World was not created"
assert world.use_nodes, "Error: World does not use nodes"
assert any(n.type == 'TEX_SKY' for n in world.node_tree.nodes), "Error: Sky Texture node missing in World"
print("✅ Nishita Sky World Setup PASSED!")

# 2. 水面メッシュ（Ocean + Foam）の生成
obj = generate_procedural_prop_mesh(
    context=bpy.context,
    target_obj=None,
    category="WATER",
    name="Test_Ocean_Foam",
    water_shape="OCEAN",
    water_color_type="TROPICAL",
    water_wave_strength=0.2,
    water_animate=True,
    water_wind_speed=1.5,
    water_anim_frames=60,
    size_x=10.0,
    size_y=10.0,
    size_z=1.0,
    seed=303
)

# 3. マテリアル内の Foam 合成ノード検証
mat = obj.data.materials[0]
assert mat is not None, "Error: No material on water"
assert any(n.type == 'ATTRIBUTE' and n.attribute_name == 'foam' for n in mat.node_tree.nodes), "Error: Foam Attribute node missing in water shader"
assert any(n.type == 'MIX_SHADER' for n in mat.node_tree.nodes), "Error: Mix Shader missing in water shader"
print("✅ Water Foam Shading Nodes PASSED!")

print("=== ALL FOAM & SKY LIGHTING TESTS PASSED 100% ===")
