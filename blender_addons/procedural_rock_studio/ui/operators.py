import bpy
import os
import random
import shutil
import subprocess

from ..generators.core_orchestrator import generate_procedural_prop_mesh, resolve_prop_parameters
from ..generators.nature_gen import create_grass_field_scene
from ..materials.image_shaders import apply_image_texture_material
from ..utils.texture_utils import get_textures_from_folder
from ..utils.baker import bake_procedural_material_to_pbr
from ..utils.anim_baker import export_animated_water_fbx
from ..utils.sky_lighting import setup_procedural_sky_lighting

def get_next_available_fbx_path(export_dir, base_name):
    os.makedirs(export_dir, exist_ok=True)
    target_path = os.path.join(export_dir, f"{base_name}.fbx")
    if not os.path.exists(target_path):
        return target_path

    idx = 1
    while True:
        candidate_path = os.path.join(export_dir, f"{base_name}_{idx:02d}.fbx")
        if not os.path.exists(candidate_path):
            return candidate_path
        idx += 1


class MESH_OT_bake_prop_textures(bpy.types.Operator):
    """Bake procedural shaders into PBR Image Textures (BaseColor + Normal) for Unity"""
    bl_idname = "mesh.bake_prop_textures"
    bl_label = "Bake Procedural to PBR Textures"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        active_obj = context.active_object
        if not active_obj or active_obj.type != 'MESH':
            self.report({'WARNING'}, "Please select a prop mesh to bake")
            return {'CANCELLED'}

        export_dir = props.export_folder.strip() or r"Z:\MeshCreator\exports"
        tex_out_dir = os.path.join(export_dir, "textures")
        res = int(props.bake_resolution)

        self.report({'INFO'}, f"🔥 PBRベイク開始 ({res}x{res})...")
        baked = bake_procedural_material_to_pbr(
            active_obj,
            output_dir=tex_out_dir,
            res=res,
            bake_diffuse=props.bake_diffuse,
            bake_normal=props.bake_normal
        )

        if baked:
            self.report({'INFO'}, f"✅ ベイク成功! 画像保存先: {tex_out_dir}")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "ベイクに失敗しました。UV展開やマテリアルを確認してください。")
            return {'CANCELLED'}


class MESH_OT_export_selected_fbx(bpy.types.Operator):
    """Export active prop to FBX for Unity with optional Auto-Baking"""
    bl_idname = "mesh.export_selected_fbx"
    bl_label = "1-Click Auto-Increment FBX Export"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        active_obj = context.active_object
        if not active_obj or active_obj.type != 'MESH':
            self.report({'WARNING'}, "Please select a prop mesh to export")
            return {'CANCELLED'}

        export_dir = props.export_folder.strip() or r"Z:\MeshCreator\exports"
        os.makedirs(export_dir, exist_ok=True)

        if props.auto_bake_on_export:
            has_procedural = any(
                mat and mat.use_nodes and not any(n.type == 'TEX_IMAGE' for n in mat.node_tree.nodes)
                for mat in active_obj.data.materials
            )
            if props.prop_category != 'WATER' and has_procedural:
                tex_out_dir = os.path.join(export_dir, "textures")
                res = int(props.bake_resolution)
                bake_procedural_material_to_pbr(
                    active_obj,
                    output_dir=tex_out_dir,
                    res=res,
                    bake_diffuse=props.bake_diffuse,
                    bake_normal=props.bake_normal
                )

        base_name = props.asset_name.strip() or active_obj.name
        final_fbx_path = get_next_available_fbx_path(export_dir, base_name)
        file_name_only = os.path.basename(final_fbx_path)

        for obj in context.scene.objects:
            obj.select_set(False)
        active_obj.select_set(True)
        context.view_layer.objects.active = active_obj

        copied_textures = []
        for mat in active_obj.data.materials:
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image and node.image.filepath:
                        src_img = bpy.path.abspath(node.image.filepath)
                        if os.path.exists(src_img):
                            try:
                                dst_img = os.path.join(export_dir, os.path.basename(src_img))
                                if src_img != dst_img:
                                    shutil.copy2(src_img, dst_img)
                                copied_textures.append(os.path.basename(src_img))
                            except Exception:
                                pass

        bpy.ops.export_scene.fbx(
            filepath=final_fbx_path,
            use_selection=True,
            object_types={'MESH'},
            bake_space_transform=True,
            apply_scale_options='FBX_SCALE_ALL',
            path_mode='COPY',
            embed_textures=True,
            axis_forward='-Z',
            axis_up='Y'
        )

        msg = f"✅ FBX出力完了: {file_name_only}"
        if copied_textures:
            msg += f" (テクスチャ同封: {', '.join(set(copied_textures))})"
        self.report({'INFO'}, msg)
        return {'FINISHED'}


class MESH_OT_open_export_folder(bpy.types.Operator):
    """Open the export folder in Windows Explorer"""
    bl_idname = "mesh.open_export_folder"
    bl_label = "Open Export Folder"

    def execute(self, context):
        props = context.scene.prop_studio_props
        export_dir = props.export_folder.strip() or r"Z:\MeshCreator\exports"
        os.makedirs(export_dir, exist_ok=True)
        try:
            subprocess.Popen(f'explorer "{export_dir}"')
            self.report({'INFO'}, f"Opened: {export_dir}")
        except Exception as e:
            self.report({'WARNING'}, f"Could not open folder: {e}")
        return {'FINISHED'}


class MESH_OT_reroll_selected_prop(bpy.types.Operator):
    """Re-roll and morph the selected prop in-place with new random seed & texture"""
    bl_idname = "mesh.reroll_selected_prop"
    bl_label = "Re-Roll Selected Prop"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass

        props = context.scene.prop_studio_props
        active_obj = context.active_object
        target = active_obj if (active_obj and active_obj.type == 'MESH') else None
        
        props.seed = random.randint(1, 999999)
        p = resolve_prop_parameters(props)
        
        generate_procedural_prop_mesh(
            context=context,
            target_obj=target,
            category=p["category"],
            name=props.asset_name if not target else target.name,
            style=p["style"],
            floor_shape=p["floor_shape"],
            wall_shape=p["wall_shape"],
            grass_mode=p["grass_mode"],
            table_shape=p["table_shape"],
            table_leg_style=p["table_leg_style"],
            chair_type=p["chair_type"],
            chair_seat_style=p["chair_seat_style"],
            chair_back_style=p["chair_back_style"],
            chair_leg_layout=p["chair_leg_layout"],
            chest_tiers=p["chest_tiers"],
            chest_handle_style=p["chest_handle_style"],
            bed_size=p["bed_size"],
            shelf_tiers=p["shelf_tiers"],
            column_style=p["column_style"],
            water_shape=p.get("water_shape", "LAKE"),
            water_color_type=p.get("water_color_type", "TROPICAL"),
            water_wave_strength=p.get("water_wave_strength", 0.12),
            water_include_bed=p.get("water_include_bed", True),
            tree_species=p["tree_species"],
            tree_has_leaves=p["tree_has_leaves"],
            tree_leaf_style=p["tree_leaf_style"],
            tree_leaf_count=p["tree_leaf_count"],
            tree_branch_levels=p["tree_branch_levels"],
            tree_curvature=p["tree_curvature"],
            tree_mat_mode=p["tree_mat_mode"],
            uv_mode=p["uv_mode"],
            size_x=p["size_x"],
            size_y=p["size_y"],
            size_z=p["size_z"],
            roughness=p["roughness"],
            chisel_strength=p["chisel_strength"],
            crack_depth=p["crack_depth"],
            big_chunk_cuts=p["big_chunk_cuts"],
            crack_count=p["crack_count"],
            create_debris=p["create_debris"],
            debris_count=p["debris_count"],
            detail_level=p["detail_level"],
            tex_folder=p.get("tex_folder", r"Z:\MeshCreator\textures\Rock"),
            use_folder_tex=p.get("use_folder_tex", True),
            selected_tex=p.get("selected_tex", ""),
            tex_tiling=p.get("tex_tiling", 1.0),
            enable_disp=p.get("enable_disp", False),
            disp_strength=p.get("disp_strength", 0.15),
            disp_midlevel=p.get("disp_midlevel", 0.5),
            disp_subdiv=p.get("disp_subdiv", 2),
            apply_disp=p.get("apply_disp", True),
            rock_palette=p.get("rock_palette", "AUTO"),
            seed=props.seed
        )
        self.report({'INFO'}, f"🎲 再抽選完了: {props.asset_name}")
        return {'FINISHED'}


class MESH_OT_create_new_prop(bpy.types.Operator):
    """Create a brand new procedural prop object"""
    bl_idname = "mesh.create_new_prop"
    bl_label = "Create New Prop"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass

        props = context.scene.prop_studio_props
        props.seed = random.randint(1, 999999) if props.auto_random else props.seed
        p = resolve_prop_parameters(props)
        
        generate_procedural_prop_mesh(
            context=context,
            target_obj=None,
            category=p["category"],
            name=props.asset_name,
            style=p["style"],
            floor_shape=p["floor_shape"],
            wall_shape=p["wall_shape"],
            grass_mode=p["grass_mode"],
            table_shape=p["table_shape"],
            table_leg_style=p["table_leg_style"],
            chair_type=p["chair_type"],
            chair_seat_style=p["chair_seat_style"],
            chair_back_style=p["chair_back_style"],
            chair_leg_layout=p["chair_leg_layout"],
            chest_tiers=p["chest_tiers"],
            chest_handle_style=p["chest_handle_style"],
            bed_size=p["bed_size"],
            shelf_tiers=p["shelf_tiers"],
            column_style=p["column_style"],
            water_shape=p.get("water_shape", "LAKE"),
            water_color_type=p.get("water_color_type", "TROPICAL"),
            water_wave_strength=p.get("water_wave_strength", 0.12),
            water_include_bed=p.get("water_include_bed", True),
            tree_species=p["tree_species"],
            tree_has_leaves=p["tree_has_leaves"],
            tree_leaf_style=p["tree_leaf_style"],
            tree_leaf_count=p["tree_leaf_count"],
            tree_branch_levels=p["tree_branch_levels"],
            tree_curvature=p["tree_curvature"],
            tree_mat_mode=p["tree_mat_mode"],
            uv_mode=p["uv_mode"],
            size_x=p["size_x"],
            size_y=p["size_y"],
            size_z=p["size_z"],
            roughness=p["roughness"],
            chisel_strength=p["chisel_strength"],
            crack_depth=p["crack_depth"],
            big_chunk_cuts=p["big_chunk_cuts"],
            crack_count=p["crack_count"],
            create_debris=p["create_debris"],
            debris_count=p["debris_count"],
            detail_level=p["detail_level"],
            tex_folder=p.get("tex_folder", r"Z:\MeshCreator\textures\Rock"),
            use_folder_tex=p.get("use_folder_tex", True),
            selected_tex=p.get("selected_tex", ""),
            tex_tiling=p.get("tex_tiling", 1.0),
            enable_disp=p.get("enable_disp", False),
            disp_strength=p.get("disp_strength", 0.15),
            disp_midlevel=p.get("disp_midlevel", 0.5),
            disp_subdiv=p.get("disp_subdiv", 2),
            apply_disp=p.get("apply_disp", True),
            rock_palette=p.get("rock_palette", "AUTO"),
            seed=props.seed
        )
        self.report({'INFO'}, f"✨ 新規作成完了: {props.asset_name}")
        return {'FINISHED'}


class MESH_OT_apply_random_texture_only(bpy.types.Operator):
    """Apply random texture from folder to selected object without changing geometry"""
    bl_idname = "mesh.apply_random_texture_only"
    bl_label = "Random Texture Only"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        active_obj = context.active_object
        if not active_obj or active_obj.type != 'MESH':
            self.report({'WARNING'}, "Please select a mesh object first")
            return {'CANCELLED'}

        tex_files = get_textures_from_folder(props.texture_folder)
        if not tex_files:
            self.report({'WARNING'}, f"No texture files found in {props.texture_folder}")
            return {'CANCELLED'}

        chosen_tex = random.choice(tex_files)
        full_path = os.path.join(props.texture_folder, chosen_tex)
        apply_image_texture_material(
            active_obj, full_path,
            scale=1.0 if props.uv_mapping_mode == 'FIT' else props.texture_tiling,
            bump_strength=0.35,
            is_transparent=(props.prop_category == 'GRASS' and props.grass_mode == 'TUFT')
        )
        
        self.report({'INFO'}, f"Applied Texture: {chosen_tex}")
        return {'FINISHED'}


class MESH_OT_create_grass_field(bpy.types.Operator):
    """草原シーン一括生成"""
    bl_idname = "mesh.create_grass_field"
    bl_label = "Create Grass Field Scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        seed = random.randint(0, 99999) if props.auto_random else props.seed
        name = "GrassField_{:05d}".format(seed)
        try:
            terrain_obj, grass_col = create_grass_field_scene(
                context, name=name, seed=seed,
                terrain_size_x=props.size_x,
                terrain_size_y=props.size_y,
                blade_height=props.size_z,
                grass_density=props.grass_density,
                undulation=props.grass_undulation,
                weight_noise_scale=props.grass_weight_noise
            )
            self.report({'INFO'}, f"🌾 草原シーン生成完了: {terrain_obj.name} (density={props.grass_density}, seed={seed})")
        except Exception as e:
            self.report({'ERROR'}, f"草原生成エラー: {str(e)}")
            return {'CANCELLED'}
        return {'FINISHED'}


class MESH_OT_convert_grass_to_game_mesh(bpy.types.Operator):
    """Hair Particle をゲーム用実メッシュへ変換"""
    bl_idname = "mesh.convert_grass_to_game_mesh"
    bl_label = "Convert Grass Particles to Game Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj is None:
            self.report({'ERROR'}, "オブジェクトが選択されていません")
            return {'CANCELLED'}
        has_particle = any(m.type == 'PARTICLE_SYSTEM' for m in obj.modifiers)
        if not has_particle:
            self.report({'WARNING'}, "選択オブジェクトに Hair Particle System がありません")
            return {'CANCELLED'}
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.particle.disconnect_hair()
            bpy.ops.object.convert(target='MESH')
            self.report({'INFO'}, "🎮 ゲーム用メッシュ変換完了。FBX エクスポートが可能です。")
        except Exception as e:
            self.report({'ERROR'}, f"変換エラー: {str(e)}")
            return {'CANCELLED'}
        return {'FINISHED'}


class MESH_OT_export_animated_water_fbx(bpy.types.Operator):
    """Bake Water Wave animation into Shape Keys and export FBX for Unity/UE"""
    bl_idname = "mesh.export_animated_water_fbx"
    bl_label = "🎮 アニメーション付き水面FBXを出力"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "水面オブジェクトを選択してください")
            return {'CANCELLED'}

        export_dir = props.export_folder.strip() or r"Z:\MeshCreator\exports"
        base_name = props.asset_name.strip() or obj.name
        final_fbx_path = get_next_available_fbx_path(export_dir, base_name + "_Animated")

        self.report({'INFO'}, f"🌊 水面波アニメーションをベイク中... ({props.water_anim_frames}フレーム)")
        try:
            export_animated_water_fbx(obj, final_fbx_path, frames_count=props.water_anim_frames)
            self.report({'INFO'}, f"✅ アニメーションFBX出力完了: {os.path.basename(final_fbx_path)}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"エクスポートエラー: {str(e)}")
            return {'CANCELLED'}


class MESH_OT_setup_water_sky_lighting(bpy.types.Operator):
    """Setup Nishita Physical Sky Texture & Eevee Refraction for Photorealistic Water Lighting"""
    bl_idname = "mesh.setup_water_sky_lighting"
    bl_label = "🌅 空と太陽光を自動セット (Nishita Sky)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            setup_procedural_sky_lighting(context)
            self.report({'INFO'}, "🌅 Nishita 物理大気スカイ ＆ Eevee 屈折・反射を有効化しました！")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"スカイ設定エラー: {str(e)}")
            return {'CANCELLED'}


