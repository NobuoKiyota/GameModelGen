import bpy
import sys
import os

addon_parent = r"z:\MeshCreator\blender_addons"
if addon_parent not in sys.path:
    sys.path.insert(0, addon_parent)

from procedural_rock_studio import rock_studio_addon
rock_studio_addon.register()

from procedural_rock_studio.generators.core_orchestrator import generate_procedural_prop_mesh

bpy.ops.wm.read_factory_settings(use_empty=True)

print("=== Testing Repeated Telescope Generation (Zero Duplication) ===")

# 1回目の生成
obj1 = generate_procedural_prop_mesh(
    context=bpy.context, category="TELESCOPE", name="Telescope_Test", seed=1
)
count1 = len(bpy.data.objects)
print(f"1st Generation: {count1} objects in scene")

# 2回目の生成（子オブジェクトを選択した状態を模倣）
ota_child = [c for c in obj1.children_recursive if "OTA" in c.name][0]
bpy.context.view_layer.objects.active = ota_child
ota_child.select_set(True)

obj2 = generate_procedural_prop_mesh(
    context=bpy.context, target_obj=ota_child, category="TELESCOPE", name="Telescope_Test", seed=2
)
count2 = len(bpy.data.objects)
print(f"2nd Generation: {count2} objects in scene")

# 3回目の生成
obj3 = generate_procedural_prop_mesh(
    context=bpy.context, target_obj=obj2, category="TELESCOPE", name="Telescope_Test", seed=3
)
count3 = len(bpy.data.objects)
print(f"3rd Generation: {count3} objects in scene")

assert count1 == count2 == count3 == 4, f"Error: Object duplication detected! Expected 4, got {count1}, {count2}, {count3}"
print("✅ ZERO DUPLICATION TEST PASSED 100%!")
