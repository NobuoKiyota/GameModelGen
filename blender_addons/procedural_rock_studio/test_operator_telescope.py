import bpy
import sys
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

addon_parent = r"z:\MeshCreator\blender_addons"
if addon_parent not in sys.path:
    sys.path.insert(0, addon_parent)

from procedural_rock_studio import rock_studio_addon
rock_studio_addon.register()

props = bpy.context.scene.prop_studio_props
props.prop_category = 'TELESCOPE'

styles = [
    "MODERN_REFRACTOR",
    "ANTIQUE_BRASS",
    "SMART_DIGITAL",
    "CASSEGRAIN_POP",
    "TACTICAL_COMPACT"
]

print("=== Testing Operator Execution with Different Telescope Styles ===")

for st in styles:
    props.telescope_style = st
    props.asset_name = f"MyTelescope_{st}"
    
    # オペレーター実行
    bpy.ops.mesh.create_new_prop()
    
    # シーン内のオブジェクトを確認
    root = bpy.context.scene.objects.get(f"MyTelescope_{st}")
    assert root is not None, f"Error: Root {props.asset_name} not found"
    
    children = list(root.children_recursive)
    ota = [c for c in children if "OTA" in c.name][0]
    mats = [m.name for m in ota.data.materials if m]
    print(f"[{st}] Generated successfully via Operator! Children: {len(children)}, OTA Mats: {mats}")
    
    if st == "ANTIQUE_BRASS":
        assert any("Brass" in m for m in mats), f"Error: {st} did not get Brass material! Got: {mats}"
    elif st == "CASSEGRAIN_POP":
        assert any("Teal" in m for m in mats), f"Error: {st} did not get Teal material! Got: {mats}"
    elif st == "SMART_DIGITAL":
        assert any("Carbon" in m or "LED" in m for m in mats or [m.name for c in children for m in c.data.materials]), f"Error: {st} missing Carbon/LED! Got: {mats}"

print("=== ALL OPERATOR STYLE TESTS PASSED 100%! ===")
