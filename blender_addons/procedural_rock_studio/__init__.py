bl_info = {
    "name": "Procedural Prop Studio Pro (Modular)",
    "author": "Antigravity & User",
    "version": (2, 5, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Prop Studio",
    "description": "Modular Procedural Generation for Photorealistic Rocks, Architecture, Furniture & Nature with 1-Click Unity FBX & Texture Baker",
    "category": "Add Mesh",
}

import bpy
from .properties import PropStudioProperties
from .ui import classes as ui_classes

classes = (
    PropStudioProperties,
    *ui_classes,
)

def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception:
            pass
    bpy.types.Scene.prop_studio_props = bpy.props.PointerProperty(type=PropStudioProperties)

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    if hasattr(bpy.types.Scene, "prop_studio_props"):
        del bpy.types.Scene.prop_studio_props

if __name__ == "__main__":
    register()
