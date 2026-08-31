import bpy
import bmesh
import math
import random
import os

def apply_geometry_displacement(obj, disp_image_path=None, strength=0.15, midlevel=0.5,
                               subdivisions=2, apply_modifier=True):
    """Displace Modifier ＋ Subdivision Surface でメッシュ実ジオメトリを凸凹立体化"""
    if not obj or obj.type != 'MESH':
        return
    
    ctx = bpy.context
    if ctx.view_layer:
        ctx.view_layer.objects.active = obj
        obj.select_set(True)

    # 1. 細分化 (Subdivision Surface)
    if subdivisions > 0:
        subsurf = obj.modifiers.new(name="Disp_Subsurf", type='SUBSURF')
        subsurf.subdivision_type = 'SIMPLE'
        subsurf.levels = min(3, subdivisions)
        subsurf.render_levels = min(3, subdivisions)
        if apply_modifier:
            try:
                bpy.ops.object.modifier_apply(modifier=subsurf.name)
            except Exception:
                try:
                    with ctx.temp_override(active_object=obj, object=obj, selected_objects=[obj]):
                        bpy.ops.object.modifier_apply(modifier=subsurf.name)
                except Exception:
                    pass

    # 2. ディスプレイスメントテクスチャ作成
    tex_disp = bpy.data.textures.new(name=obj.name + "_GeoDispTex", type='IMAGE' if (disp_image_path and os.path.exists(disp_image_path)) else 'CLOUDS')
    if disp_image_path and os.path.exists(disp_image_path):
        try:
            img = bpy.data.images.load(disp_image_path, check_existing=True)
            img.colorspace_settings.name = 'Non-Color'
            tex_disp.image = img
        except Exception:
            tex_disp.type = 'CLOUDS'
            tex_disp.noise_scale = 0.35
    else:
        tex_disp.noise_scale = 0.35
        tex_disp.noise_depth = 3

    # 3. Displace Modifier 適用
    disp_mod = obj.modifiers.new(name="Disp_Geometry", type='DISPLACE')
    disp_mod.texture = tex_disp
    disp_mod.texture_coords = 'UV' if len(obj.data.uv_layers) > 0 else 'LOCAL'
    disp_mod.strength = strength
    disp_mod.mid_level = midlevel

    if apply_modifier:
        try:
            bpy.ops.object.modifier_apply(modifier=disp_mod.name)
        except Exception:
            try:
                with ctx.temp_override(active_object=obj, object=obj, selected_objects=[obj]):
                    bpy.ops.object.modifier_apply(modifier=disp_mod.name)
            except Exception:
                pass


def project_box_uvs(obj, tex_tiling=1.0):
    """キューブ投影によるUVアンラップ"""
    if not obj or obj.type != 'MESH':
        return
    ctx = bpy.context
    if ctx.view_layer:
        ctx.view_layer.objects.active = obj
        obj.select_set(True)
    try:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.cube_project(cube_size=tex_tiling, correct_aspect=True, clip_to_bounds=False, scale_to_bounds=False)
        bpy.ops.object.mode_set(mode='OBJECT')
    except Exception:
        if ctx.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass
