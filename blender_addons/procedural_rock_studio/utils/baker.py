import bpy
import os

def apply_baked_pbr_material(obj, baked_textures):
    """ベイクした BaseColor / Normal テクスチャを標準 PBR マテリアルとしてアタッチ"""
    mat_name = f"{obj.name}_Baked_PBR_Mat"
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (650, 0)
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (350, 0)
    node_bsdf.inputs['Roughness'].default_value = 0.6
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    # 1. BaseColor Texture
    if 'BaseColor' in baked_textures:
        tex_path = baked_textures['BaseColor']
        img = bpy.data.images.load(tex_path, check_existing=True)
        node_col = nodes.new(type='ShaderNodeTexImage')
        node_col.location = (50, 100)
        node_col.image = img
        links.new(node_col.outputs['Color'], node_bsdf.inputs['Base Color'])

    # 2. Normal Map Texture (Non-Color)
    if 'Normal' in baked_textures:
        tex_path = baked_textures['Normal']
        img = bpy.data.images.load(tex_path, check_existing=True)
        img.colorspace_settings.name = 'Non-Color'
        node_norm_tex = nodes.new(type='ShaderNodeTexImage')
        node_norm_tex.location = (-200, -150)
        node_norm_tex.image = img
        node_norm_map = nodes.new(type='ShaderNodeNormalMap')
        node_norm_map.location = (80, -150)
        node_norm_map.inputs['Strength'].default_value = 1.0
        links.new(node_norm_tex.outputs['Color'], node_norm_map.inputs['Color'])
        links.new(node_norm_map.outputs['Normal'], node_bsdf.inputs['Normal'])

    # オブジェクトのマテリアルを差し替え
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return mat


def bake_procedural_material_to_pbr(obj, output_dir, res=1024, bake_diffuse=True, bake_normal=True):
    """プロシージャルシェーダーを Cycles で一発画像ベイク (BaseColor + Tangent Normal)"""
    if not obj or obj.type != 'MESH':
        return {}

    scene = bpy.context.scene
    old_engine = scene.render.engine
    scene.render.engine = 'CYCLES'
    scene.cycles.bake_type = 'DIFFUSE'
    scene.cycles.samples = 16
    try:
        scene.cycles.use_denoising = False
    except Exception:
        pass

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    os.makedirs(output_dir, exist_ok=True)
    base_name = obj.name
    baked_textures = {}

    # 1. BaseColor
    if bake_diffuse:
        diff_img_name = f"{base_name}_BaseColor"
        diff_img = bpy.data.images.new(diff_img_name, width=res, height=res, alpha=True)
        
        bake_nodes = []
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
                node.image = diff_img
                mat.node_tree.nodes.active = node
                bake_nodes.append((mat, node))
        
        try:
            bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, use_clear=True, margin=4)
            diff_path = os.path.join(output_dir, f"{diff_img_name}.png")
            diff_img.filepath_raw = diff_path
            diff_img.file_format = 'PNG'
            diff_img.save()
            baked_textures['BaseColor'] = diff_path
        except Exception as e:
            print("DIFFUSE BAKE ERROR:", e)
        finally:
            for mat, node in bake_nodes:
                try:
                    mat.node_tree.nodes.remove(node)
                except Exception:
                    pass

    # 2. Normal Map
    if bake_normal:
        norm_img_name = f"{base_name}_Normal"
        norm_img = bpy.data.images.new(norm_img_name, width=res, height=res, alpha=False)
        try:
            norm_img.colorspace_settings.name = 'Non-Color'
        except Exception:
            pass

        bake_nodes = []
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
                node.image = norm_img
                mat.node_tree.nodes.active = node
                bake_nodes.append((mat, node))

        try:
            bpy.ops.object.bake(type='NORMAL', normal_space='TANGENT', use_clear=True, margin=4)
            norm_path = os.path.join(output_dir, f"{norm_img_name}.png")
            norm_img.filepath_raw = norm_path
            norm_img.file_format = 'PNG'
            norm_img.save()
            baked_textures['Normal'] = norm_path
        except Exception as e:
            print("NORMAL BAKE ERROR:", e)
        finally:
            for mat, node in bake_nodes:
                try:
                    mat.node_tree.nodes.remove(node)
                except Exception:
                    pass

    # レンダラー復帰
    scene.render.engine = old_engine

    # マテリアル差し替え
    if baked_textures:
        apply_baked_pbr_material(obj, baked_textures)

    return baked_textures
