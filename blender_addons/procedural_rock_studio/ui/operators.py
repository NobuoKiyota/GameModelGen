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

        self.report({'INFO'}, f"[BAKE] PBR bake starting ({res}x{res})...")
        baked = bake_procedural_material_to_pbr(
            active_obj,
            output_dir=tex_out_dir,
            res=res,
            bake_diffuse=props.bake_diffuse,
            bake_normal=props.bake_normal
        )

        if baked:
            self.report({'INFO'}, f"Bake succeeded! Saved to: {tex_out_dir}")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Bake failed. Check UV unwrap or material.")
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

        # WATERカテゴリでOcean Modifierアニメーションが有効な場合、通常のFBXエクスポートでは
        # モディファイアの変形(リアルタイムプロシージャル評価)がベイクされずアニメーションが失われる。
        # FBXは頂点変形アニメーションをシェイプキー(BlendShape)としてしか持ち運べないため、
        # この条件に該当する場合は専用のシェイプキーベイク付きエクスポートへ自動的に切り替える。
        # (以前は専用ボタン「アニメーション付き水面FBXを出力」を押し忘れると、Ocean Modifierが
        # モディファイアスタックに残ったまま静的な1フレーム分だけがエクスポートされ、Unity側で
        # 波が全く動かない結果になっていた)
        is_animated_water = (
            props.prop_category == 'WATER'
            and props.water_animate
            and any(m.type == 'OCEAN' for m in active_obj.modifiers)
        )
        if is_animated_water:
            base_name = props.asset_name.strip() or active_obj.name
            final_fbx_path = get_next_available_fbx_path(export_dir, base_name + "_Animated")
            try:
                export_animated_water_fbx(active_obj, final_fbx_path, frames_count=props.water_anim_frames)
                self.report({'INFO'}, f"Animated water FBX export complete (Ocean Modifier auto-baked to shape keys): {os.path.basename(final_fbx_path)}")
                return {'FINISHED'}
            except Exception as e:
                self.report({'ERROR'}, f"Animated water export error: {str(e)}")
                return {'CANCELLED'}

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

        msg = f"FBX export complete: {file_name_only}"
        if copied_textures:
            msg += f" (textures copied: {', '.join(set(copied_textures))})"
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
        
        # カテゴリパラメータを kwargs として完全伝達
        params = dict(p)
        cat = params.pop("category", "ROCK")
        seed_val = params.pop("seed", props.seed)
        
        generate_procedural_prop_mesh(
            context=context,
            target_obj=target,
            category=cat,
            name=props.asset_name if not target else target.name,
            seed=seed_val,
            **params
        )
        self.report({'INFO'}, f"Re-roll complete: {props.asset_name}")
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
        
        params = dict(p)
        cat = params.pop("category", "ROCK")
        seed_val = params.pop("seed", props.seed)
        
        generate_procedural_prop_mesh(
            context=context,
            target_obj=None,
            category=cat,
            name=props.asset_name,
            seed=seed_val,
            **params
        )
        self.report({'INFO'}, f"Created: {props.asset_name}")
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
            self.report({'INFO'}, f"Grass field scene created: {terrain_obj.name} (density={props.grass_density}, seed={seed})")
        except Exception as e:
            self.report({'ERROR'}, f"Grass field generation error: {str(e)}")
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
            self.report({'ERROR'}, "No object selected")
            return {'CANCELLED'}
        has_particle = any(m.type == 'PARTICLE_SYSTEM' for m in obj.modifiers)
        if not has_particle:
            self.report({'WARNING'}, "Selected object has no Hair Particle System")
            return {'CANCELLED'}
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.particle.disconnect_hair()
            bpy.ops.object.convert(target='MESH')
            self.report({'INFO'}, "Converted to game mesh. Ready for FBX export.")
        except Exception as e:
            self.report({'ERROR'}, f"Conversion error: {str(e)}")
            return {'CANCELLED'}
        return {'FINISHED'}


class MESH_OT_export_animated_water_fbx(bpy.types.Operator):
    """Bake Water Wave animation into Shape Keys and export FBX for Unity/UE"""
    bl_idname = "mesh.export_animated_water_fbx"
    bl_label = "Export Animated Water FBX"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "Please select a water surface object")
            return {'CANCELLED'}

        export_dir = props.export_folder.strip() or r"Z:\MeshCreator\exports"
        base_name = props.asset_name.strip() or obj.name
        final_fbx_path = get_next_available_fbx_path(export_dir, base_name + "_Animated")

        self.report({'INFO'}, f"Baking water wave animation... ({props.water_anim_frames} frames)")
        try:
            export_animated_water_fbx(obj, final_fbx_path, frames_count=props.water_anim_frames)
            self.report({'INFO'}, f"Animated FBX export complete: {os.path.basename(final_fbx_path)}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Export error: {str(e)}")
            return {'CANCELLED'}


class MESH_OT_setup_water_sky_lighting(bpy.types.Operator):
    """Setup Nishita Physical Sky Texture & Eevee Refraction for Photorealistic Water Lighting"""
    bl_idname = "mesh.setup_water_sky_lighting"
    bl_label = "Setup Sky & Sun Light (Nishita Sky)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            setup_procedural_sky_lighting(context)
            self.report({'INFO'}, "Nishita physical sky & Eevee refraction/reflection enabled.")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Sky setup error: {str(e)}")
            return {'CANCELLED'}


class MESH_OT_generate_image_displace(bpy.types.Operator):
    """Generate 3D Displaced Mesh from 2D Image (Real-time Preview)"""
    bl_idname = "mesh.generate_image_displace"
    bl_label = "2D画像から立体プレビュー生成"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        img_path = bpy.path.abspath(props.img_disp_path).strip()
        if not img_path or not os.path.isfile(img_path):
            self.report({'WARNING'}, "有効な画像ファイルを指定してください (PNG/JPG/EXR)")
            return {'CANCELLED'}

        from ..generators.image_displace_gen import generate_image_displace_asset
        name = props.asset_name.strip() or "Image_Displace_Asset"
        obj = generate_image_displace_asset(
            context=context,
            image_path=img_path,
            name=name,
            shape_type=props.img_disp_shape,
            depth=props.img_disp_solidify_thickness,
            strength=props.img_disp_strength,
            midlevel=props.img_disp_midlevel,
            subdiv_level=props.img_disp_subdiv_level,
            smooth_factor=props.img_disp_smooth_factor,
            smooth_iter=props.img_disp_smooth_iter,
            solidify_thickness=props.img_disp_solidify_thickness,
            block_style=props.img_disp_block_style,
            enable_cutout=props.img_disp_enable_cutout,
            cutout_threshold=props.img_disp_cutout_threshold,
            cutout_invert=props.img_disp_cutout_invert,
            enable_color_cutout=props.img_disp_enable_color_cutout,
            key_color=props.img_disp_key_color,
            color_tolerance=props.img_disp_color_tolerance,
            cutout_mode={'OR': 0, 'AND': 1, 'COLOR_ONLY': 2, 'HEIGHT_ONLY': 3}.get(props.img_disp_cutout_mode, 0),
            resolution=props.img_disp_resolution,
            close_mesh=props.img_disp_close_mesh,
            decimate_ratio=props.img_disp_decimate_ratio,
            material_style=props.img_disp_mat_style,
            auto_apply=False
        )
        context.view_layer.objects.active = obj
        obj.select_set(True)
        self.report({'INFO'}, f"画像立体化プレビュー生成完了: {obj.name}")
        return {'FINISHED'}


class MESH_OT_bake_game_ready_displace(bpy.types.Operator):
    """Bake and Solidify into Game-Ready Closed Solid Mesh with Decimation"""
    bl_idname = "mesh.bake_game_ready_displace"
    bl_label = "🎮 ゲーム用確定 (裏面密閉 & 軽量化)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "立体化されたメッシュを選択してください")
            return {'CANCELLED'}

        from ..generators.image_displace_gen import finalize_game_ready_displace
        finalize_game_ready_displace(
            obj,
            depth=props.img_disp_solidify_thickness,
            decimate_ratio=props.img_disp_decimate_ratio,
            close_mesh=props.img_disp_close_mesh
        )
        self.report({'INFO'}, f"ゲーム用確定完了（クローズド密閉＆軽量化済み）: {obj.name}")
        return {'FINISHED'}


class MESH_OT_import_clipboard_image(bpy.types.Operator):
    """Import image directly from Windows Clipboard (Ctrl+C / Screenshots) and generate 3D mesh"""
    bl_idname = "mesh.import_clipboard_image"
    bl_label = "📋 クリップボードから貼り付け (Ctrl+V)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        from ..utils.clipboard_utils import save_clipboard_image
        img_path = save_clipboard_image()

        if not img_path or not os.path.isfile(img_path):
            self.report({'WARNING'}, "クリップボードに有効な画像データが見つかりませんでした (Ctrl+Cで画像をコピーしてください)")
            return {'CANCELLED'}

        props.img_disp_path = img_path
        self.report({'INFO'}, f"クリップボード画像を取り込みました: {os.path.basename(img_path)}")

        # 即座に立体プレビューを生成
        bpy.ops.mesh.generate_image_displace()
        return {'FINISHED'}


class MESH_OT_import_dropped_image(bpy.types.Operator):
    """Detect and import dragged/dropped Empty Image or active Image in Blender"""
    bl_idname = "mesh.import_dropped_image"
    bl_label = "🎯 ドロップ画像から取得"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        from ..utils.clipboard_utils import get_active_or_latest_dropped_image
        img_path = get_active_or_latest_dropped_image(context)

        if not img_path or not os.path.isfile(img_path):
            self.report({'WARNING'}, "ドロップされた下絵画像が見つかりませんでした。画像をBlenderにドラッグしてください")
            return {'CANCELLED'}

        props.img_disp_path = img_path
        self.report({'INFO'}, f"ドロップ画像を検出しました: {os.path.basename(img_path)}")

        # 即座に立体プレビューを生成
        bpy.ops.mesh.generate_image_displace()
        return {'FINISHED'}


class MESH_OT_auto_detect_background_color(bpy.types.Operator):
    """Auto detect background color from image corner pixel"""
    bl_idname = "mesh.auto_detect_background_color"
    bl_label = "🪄 背景色を自動取得"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        img_path = bpy.path.abspath(props.img_disp_path).strip()
        if not img_path or not os.path.isfile(img_path):
            self.report({'WARNING'}, "有効な画像ファイルを先に指定してください")
            return {'CANCELLED'}

        from ..generators.image_displace_gen import detect_image_corner_color
        r, g, b = detect_image_corner_color(img_path)
        props.img_disp_key_color = (r, g, b, 1.0)
        self.report({'INFO'}, f"背景色を自動検出しました: R={r:.2f}, G={g:.2f}, B={b:.2f}")
        return {'FINISHED'}
