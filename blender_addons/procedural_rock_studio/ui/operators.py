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
        
        # For CAVE, sanitize name so selecting Floor/Water/Ceiling/Pillars/Debris does not append duplicate suffixes
        prop_name = props.asset_name if not target else target.name
        if cat == "CAVE":
            import re
            prop_name = re.sub(r'(_Floor|_Water|_Ceiling|_Pillars|_Debris)+$', '', prop_name).strip() or "Cave_Dungeon"

        generate_procedural_prop_mesh(
            context=context,
            target_obj=target,
            category=cat,
            name=prop_name,
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
            close_mesh=props.img_disp_close_mesh,
            planar_angle=props.img_disp_planar_angle
        )
        self.report({'INFO'}, f"ゲーム用確定完了（クローズド密閉＆軽量化済み）: {obj.name}")
        return {'FINISHED'}


class MESH_OT_optimize_displace_mesh(bpy.types.Operator):
    """Dissolve unnecessary planar vertices and reconstruct smart UV without texture distortion"""
    bl_idname = "mesh.optimize_displace_mesh"
    bl_label = "⚡ 不要頂点消去 ＆ スマートUV化"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "最適化するメッシュを選択してください")
            return {'CANCELLED'}

        from ..generators.image_displace_gen import optimize_and_smart_uv_clean
        init_v, final_v = optimize_and_smart_uv_clean(
            obj,
            planar_angle=props.img_disp_planar_angle,
            clean_loose=True,
            top_down_uv=True
        )
        reduced = init_v - final_v
        pct = (reduced / max(init_v, 1)) * 100.0
        self.report({'INFO'}, f"不要頂点消去完了: {init_v} ➔ {final_v} 頂点 (削減率: {pct:.1f}%)")
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


class MESH_OT_generate_flask_potion(bpy.types.Operator):
    """Generate Procedural Flask Potion with Glass Container, Surface-Distorted Liquid, and Tilt Compensation"""
    bl_idname = "mesh.generate_flask_potion"
    bl_label = "🧪 液体入りフラスコを生成"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        from ..generators.flask_potion_gen import generate_flask_potion_asset
        name = props.asset_name.strip() or "Potion_Flask"
        obj_glass, obj_liq, obj_cork = generate_flask_potion_asset(
            context=context,
            name=name,
            shape_type=props.flask_shape,
            liquid_level=props.liquid_level,
            flask_tilt_deg=props.flask_tilt,
            liquid_tilt_deg=props.liquid_tilt,
            surface_noise=props.liquid_surface_noise,
            liquid_color=props.liquid_color,
            glow=props.liquid_glow,
            has_cork=props.flask_has_cork,
            scale=props.flask_scale
        )
        self.report({'INFO'}, f"フラスコ・ポーション生成完了: {obj_glass.name}")
        return {'FINISHED'}


class MESH_OT_regenerate_flask_potion(bpy.types.Operator):
    """Regenerate currently selected Potion Flask in-place (keeps location and rotation)"""
    bl_idname = "mesh.regenerate_flask_potion"
    bl_label = "🔄 フラスコを再生成・更新"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        from ..generators.flask_potion_gen import generate_flask_potion_asset, find_flask_root
        active_obj = context.active_object
        target = find_flask_root(active_obj)
        if not target:
            # 選択がなければ新規生成にフォールバック
            return bpy.ops.mesh.generate_flask_potion()

        obj_glass, obj_liq, obj_cork = generate_flask_potion_asset(
            context=context,
            name=target.name,
            shape_type=props.flask_shape,
            liquid_level=props.liquid_level,
            flask_tilt_deg=props.flask_tilt,
            liquid_tilt_deg=props.liquid_tilt,
            surface_noise=props.liquid_surface_noise,
            liquid_color=props.liquid_color,
            glow=props.liquid_glow,
            has_cork=props.flask_has_cork,
            scale=props.flask_scale,
            target_obj=target
        )
        self.report({'INFO'}, f"フラスコを更新しました: {obj_glass.name}")
        return {'FINISHED'}


class MESH_OT_generate_wall_clock(bpy.types.Operator):
    """Generate New Procedural Wall Clock"""
    bl_idname = "mesh.generate_wall_clock"
    bl_label = "＋ 新規壁掛け時計を生成"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        from ..generators.wall_clock_gen import generate_wall_clock_asset
        name = props.asset_name.strip() or "Wall_Clock"
        obj_clock, obj_dial, obj_nums, obj_hour, obj_min, obj_sec, obj_glass = generate_wall_clock_asset(
            context=context,
            name=name,
            shape=props.clock_shape,
            style=props.clock_style,
            hour=props.clock_time_hour,
            minute=props.clock_time_minute,
            second=props.clock_time_minute * 6 % 60,
            show_seconds=props.clock_show_seconds,
            show_glass=props.clock_show_glass,
            diameter=props.clock_diameter,
            scale=1.0,
            target_obj=None
        )
        self.report({'INFO'}, f"新規壁掛け時計を生成しました: {obj_clock.name} ({props.clock_time_hour}:{props.clock_time_minute:02d})")
        return {'FINISHED'}


class MESH_OT_regenerate_wall_clock(bpy.types.Operator):
    """Regenerate currently selected Wall Clock in-place (keeps location and rotation)"""
    bl_idname = "mesh.regenerate_wall_clock"
    bl_label = "🔄 壁掛け時計を再生成・更新"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        from ..generators.wall_clock_gen import generate_wall_clock_asset, find_clock_root
        active_obj = context.active_object
        target = find_clock_root(active_obj)
        if not target:
            # 選択がなければ新規生成にフォールバック
            return bpy.ops.mesh.generate_wall_clock()

        obj_clock, obj_dial, obj_nums, obj_hour, obj_min, obj_sec, obj_glass = generate_wall_clock_asset(
            context=context,
            name=target.name,
            shape=props.clock_shape,
            style=props.clock_style,
            hour=props.clock_time_hour,
            minute=props.clock_time_minute,
            second=props.clock_time_minute * 6 % 60,
            show_seconds=props.clock_show_seconds,
            show_glass=props.clock_show_glass,
            diameter=props.clock_diameter,
            scale=1.0,
            target_obj=target
        )
        self.report({'INFO'}, f"壁掛け時計を更新しました: {obj_clock.name} ({props.clock_time_hour}:{props.clock_time_minute:02d})")
        return {'FINISHED'}


class MESH_OT_generate_speaker(bpy.types.Operator):
    """Generate New Procedural Audio Speaker"""
    bl_idname = "mesh.generate_speaker"
    bl_label = "＋ 新規スピーカーを生成"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        from ..generators.speaker_gen import generate_speaker_asset
        name = props.asset_name.strip() or "Studio_Speaker"
        obj_cabinet, obj_woofer, obj_tweeter, obj_led, obj_grille = generate_speaker_asset(
            context=context,
            name=name,
            style=props.speaker_style,
            cone_color=props.speaker_cone_color,
            has_grille=props.speaker_has_grille,
            led_color=props.speaker_led_color,
            scale=props.speaker_scale,
            target_obj=None
        )
        self.report({'INFO'}, f"新規スピーカーを生成しました: {obj_cabinet.name}")
        return {'FINISHED'}


class MESH_OT_regenerate_speaker(bpy.types.Operator):
    """Regenerate currently selected Speaker in-place (keeps location and rotation)"""
    bl_idname = "mesh.regenerate_speaker"
    bl_label = "🔄 スピーカーを再生成・更新"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        from ..generators.speaker_gen import generate_speaker_asset, find_speaker_root
        active_obj = context.active_object
        target = find_speaker_root(active_obj)
        if not target:
            return bpy.ops.mesh.generate_speaker()

        obj_cabinet, obj_woofer, obj_tweeter, obj_led, obj_grille = generate_speaker_asset(
            context=context,
            name=target.name,
            style=props.speaker_style,
            cone_color=props.speaker_cone_color,
            has_grille=props.speaker_has_grille,
            led_color=props.speaker_led_color,
            scale=props.speaker_scale,
            target_obj=target
        )
        self.report({'INFO'}, f"スピーカーを更新しました: {obj_cabinet.name}")
        return {'FINISHED'}


class MESH_OT_generate_fence_preset(bpy.types.Operator):
    bl_idname = "mesh.generate_fence_preset"
    bl_label = "➕ 実用フェンスを生成"
    bl_description = "十字の鉄線、X字の鉄線、木板打ち付け(横/縦)の実用フェンスを一発出力"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass

        props = context.scene.prop_studio_props
        from ..generators.fence_gen import generate_fence_preset_asset

        name_map = {
            'WIRE_CROSS': "Fence_WireCross",
            'WIRE_X': "Fence_WireX",
            'WOOD_HORIZ': "Fence_WoodHoriz",
            'WOOD_VERT': "Fence_WoodVert"
        }
        name = name_map.get(props.fence_preset_type, "Fence_Asset")

        use_custom = (props.fence_color_preset != 'PRESET_DEFAULT')
        f_col = props.fence_frame_color if use_custom else None
        b_col = props.fence_body_color if use_custom else None
        met   = props.fence_metallic if use_custom else None
        rgh   = props.fence_roughness if use_custom else None

        obj_fence = generate_fence_preset_asset(
            context=context,
            name=name,
            preset_type=props.fence_preset_type,
            length=props.fence_length,
            height=props.fence_height,
            post_spacing=props.fence_post_spacing,
            slat_gap=props.fence_slat_gap,
            scale=props.fence_scale,
            frame_color=f_col,
            body_color=b_col,
            metallic=met,
            roughness=rgh,
            top_style=props.fence_wood_top_style,
            wood_jitter=props.fence_wood_jitter,
            wood_wear=props.fence_wood_wear,
            wood_weathering=props.fence_wood_weathering,
            target_obj=None
        )
        self.report({'INFO'}, f"新規フェンスを生成しました: {obj_fence.name}")
        return {'FINISHED'}


class MESH_OT_regenerate_fence_preset(bpy.types.Operator):
    bl_idname = "mesh.regenerate_fence_preset"
    bl_label = "🔄 フェンスを再生成・更新"
    bl_description = "選択中のフェンスのトランスフォーム・位置を保ったままスタイルや寸法を再構築"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass

        props = context.scene.prop_studio_props
        from ..generators.fence_gen import generate_fence_preset_asset, find_fence_root

        active_obj = context.active_object
        target = find_fence_root(active_obj)
        if not target:
            # 何も選択されていない、またはフェンス以外の場合は新規生成へ
            return bpy.ops.mesh.generate_fence_preset()

        name_map = {
            'WIRE_CROSS': "Fence_WireCross",
            'WIRE_X': "Fence_WireX",
            'WOOD_HORIZ': "Fence_WoodHoriz",
            'WOOD_VERT': "Fence_WoodVert"
        }
        name = name_map.get(props.fence_preset_type, target.name)

        use_custom = (props.fence_color_preset != 'PRESET_DEFAULT')
        f_col = props.fence_frame_color if use_custom else None
        b_col = props.fence_body_color if use_custom else None
        met   = props.fence_metallic if use_custom else None
        rgh   = props.fence_roughness if use_custom else None

        obj_fence = generate_fence_preset_asset(
            context=context,
            name=name,
            preset_type=props.fence_preset_type,
            length=props.fence_length,
            height=props.fence_height,
            post_spacing=props.fence_post_spacing,
            slat_gap=props.fence_slat_gap,
            scale=props.fence_scale,
            frame_color=f_col,
            body_color=b_col,
            metallic=met,
            roughness=rgh,
            top_style=props.fence_wood_top_style,
            wood_jitter=props.fence_wood_jitter,
            wood_wear=props.fence_wood_wear,
            wood_weathering=props.fence_wood_weathering,
            target_obj=target
        )
        self.report({'INFO'}, f"フェンスを更新しました: {obj_fence.name}")
        return {'FINISHED'}



class MESH_OT_apply_fence_colors(bpy.types.Operator):
    bl_idname = "mesh.apply_fence_colors"
    bl_label = "🎨 カラーを即時反映"
    bl_description = "メッシュを再構築せず、現在選択中のフェンスのマテリアル色・質感を瞬時に塗り替えます"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        active_obj = context.active_object
        from ..generators.fence_gen import apply_fence_material_colors

        ok = apply_fence_material_colors(
            active_obj,
            frame_color=props.fence_frame_color,
            body_color=props.fence_body_color,
            metallic=props.fence_metallic,
            roughness=props.fence_roughness,
            weathering=props.fence_wood_weathering
        )
        if ok:
            self.report({'INFO'}, "選択中フェンスのマテリアル色を更新しました")
        else:
            self.report({'WARNING'}, "フェンスオブジェクトが選択されていません")
        return {'FINISHED'}


# ==============================================================================
# Nature Biome Scatter Operators (Geometry Nodes 自己完結型)
# ==============================================================================

class MESH_OT_regenerate_biome_scatter(bpy.types.Operator):
    bl_idname = "mesh.regenerate_biome_scatter"
    bl_label = "🔄 再生成・更新 (選択中を更新)"
    bl_description = "選択中のバイオームテレイン（または直前のテレイン）を、現在のパラメータでその場更新・再生成します（重複堆積しません）"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        from ..generators.nature_gen import create_biome_scatter_scene

        active_obj = context.active_object
        target = None
        if active_obj and active_obj.type == 'MESH' and ("BiomeScatter" in active_obj.modifiers or "_Terrain" in active_obj.name):
            target = active_obj

        name = target.name.replace("_Terrain", "") if target else (props.asset_name.strip() or "Nature_Biome")

        terrain_obj, biome_col = create_biome_scatter_scene(
            context=context,
            name=name,
            seed=props.seed,
            biome_type=props.biome_type,
            terrain_size_x=props.biome_terrain_size,
            terrain_size_y=props.biome_terrain_size,
            undulation=props.biome_undulation,
            density=props.biome_density,
            min_dist=props.biome_min_dist,
            include_fern=props.biome_include_fern,
            include_shrub=props.biome_include_shrub,
            include_pebbles=props.biome_include_pebble,
            target_obj=target
        )

        context.view_layer.objects.active = terrain_obj
        terrain_obj.select_set(True)
        self.report({'INFO'}, f"バイオームを更新しました: {terrain_obj.name}")
        return {'FINISHED'}


class MESH_OT_create_biome_scatter(bpy.types.Operator):
    bl_idname = "mesh.create_biome_scatter"
    bl_label = "➕ 新規バイオームを生成"
    bl_description = "草株・リアルシダ・小低木・クローバー・小石が調和した自然環境をGeometry Nodesで自動生成します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        base_name = props.asset_name.strip() or "Nature_Biome"

        # 既存オブジェクトとの重複を避けるための連番付与
        name = base_name
        counter = 1
        while (name + "_Terrain") in bpy.data.objects:
            name = f"{base_name}_{counter:02d}"
            counter += 1

        from ..generators.nature_gen import create_biome_scatter_scene

        terrain_obj, biome_col = create_biome_scatter_scene(
            context=context,
            name=name,
            seed=props.seed,
            biome_type=props.biome_type,
            terrain_size_x=props.biome_terrain_size,
            terrain_size_y=props.biome_terrain_size,
            undulation=props.biome_undulation,
            density=props.biome_density,
            min_dist=props.biome_min_dist,
            include_fern=props.biome_include_fern,
            include_shrub=props.biome_include_shrub,
            include_pebbles=props.biome_include_pebble,
            target_obj=None
        )

        context.view_layer.objects.active = terrain_obj
        terrain_obj.select_set(True)
        self.report({'INFO'}, f"新規バイオーム自然環境を生成しました: {terrain_obj.name}")
        return {'FINISHED'}


class MESH_OT_convert_scatter_to_game_mesh(bpy.types.Operator):
    bl_idname = "mesh.convert_scatter_to_game_mesh"
    bl_label = "🎮 ゲーム用実体メッシュへ変換 (Make Real)"
    bl_description = "選択中テレインのGeometry Nodes散布インスタンスを実体メッシュとして確定し、Unity/UE向けFBX出力可能にします"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "散布モディファイアを持つ地面テレインを選択してください")
            return {'CANCELLED'}

        from ..generators.nature_gen import convert_scatter_to_game_mesh

        ok = convert_scatter_to_game_mesh(context, obj)
        if ok:
            v_cnt = len(obj.data.vertices)
            p_cnt = len(obj.data.polygons)
            self.report({'INFO'}, f"ゲーム用実体メッシュへ変換完了: {obj.name} ({v_cnt}頂点 / {p_cnt}ポリゴン)")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "有効な散布 Geometry Nodes モディファイアが見つかりませんでした")
            return {'CANCELLED'}


# ==============================================================================
# Castle Stone Wall Operators (Geometry Nodes 散布型城壁)
# ==============================================================================

class MESH_OT_regenerate_castle_wall(bpy.types.Operator):
    bl_idname = "mesh.regenerate_castle_wall"
    bl_label = "🔄 再生成・更新 (選択中を更新)"
    bl_description = "選択中の城壁（または直前の城壁）を、現在のパラメータでその場更新・再生成します（重複堆積しません）"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        from ..generators.castle_wall_gen import create_castle_wall_scene

        active_obj = context.active_object
        target = None
        if active_obj and active_obj.type == 'MESH' and ("CastleWallScatter" in active_obj.modifiers or "_Core" in active_obj.name):
            target = active_obj

        name = target.name.replace("_Core", "") if target else (props.asset_name.strip() or "Castle_Wall")

        wall_obj, stone_col = create_castle_wall_scene(
            context=context,
            name=name,
            seed=props.seed,
            wall_shape=props.castle_wall_shape,
            wall_style=props.castle_wall_style,
            stone_aspect=props.castle_wall_stone_aspect,
            stone_roundness=props.castle_wall_stone_roundness,
            stone_chipping=props.castle_wall_stone_chipping,
            length=props.castle_wall_length,
            height=props.castle_wall_height,
            thickness=props.castle_wall_thickness,
            crenels=props.castle_wall_has_crenels,
            density=props.castle_wall_density,
            min_dist=props.castle_wall_min_dist,
            jitter=props.castle_wall_jitter,
            batter=props.castle_wall_batter,
            roughness=props.castle_wall_roughness,
            target_obj=target
        )

        context.view_layer.objects.active = wall_obj
        wall_obj.select_set(True)
        self.report({'INFO'}, f"城壁を更新しました: {wall_obj.name}")
        return {'FINISHED'}


class MESH_OT_reroll_castle_wall(bpy.types.Operator):
    """Re-roll castle wall shape, stone blocks, and scatter with a new random seed"""
    bl_idname = "mesh.reroll_castle_wall"
    bl_label = "🎲 形状・石材を全再抽選 (Re-Roll All)"
    bl_description = "壁面の形状（起伏・出っ張り・傾き）、石材アセットの削り形状、散布配置を新しいシードで完全再抽選します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        props.seed = random.randint(1, 999999)
        return bpy.ops.mesh.regenerate_castle_wall()


class MESH_OT_create_castle_wall(bpy.types.Operator):
    bl_idname = "mesh.create_castle_wall"
    bl_label = "➕ 新規城壁を生成"
    bl_description = "立体石材散布型の本格中世城壁・石垣・銃眼胸壁をGeometry Nodesで自動生成します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        base_name = props.asset_name.strip() or "Castle_Wall"

        name = base_name
        counter = 1
        while (name + "_Core") in bpy.data.objects:
            name = f"{base_name}_{counter:02d}"
            counter += 1

        from ..generators.castle_wall_gen import create_castle_wall_scene

        wall_obj, stone_col = create_castle_wall_scene(
            context=context,
            name=name,
            seed=props.seed,
            wall_shape=props.castle_wall_shape,
            wall_style=props.castle_wall_style,
            stone_aspect=props.castle_wall_stone_aspect,
            stone_roundness=props.castle_wall_stone_roundness,
            stone_chipping=props.castle_wall_stone_chipping,
            length=props.castle_wall_length,
            height=props.castle_wall_height,
            thickness=props.castle_wall_thickness,
            crenels=props.castle_wall_has_crenels,
            density=props.castle_wall_density,
            min_dist=props.castle_wall_min_dist,
            jitter=props.castle_wall_jitter,
            batter=props.castle_wall_batter,
            roughness=props.castle_wall_roughness,
            target_obj=None
        )

        context.view_layer.objects.active = wall_obj
        wall_obj.select_set(True)
        self.report({'INFO'}, f"新規城壁を生成しました: {wall_obj.name}")
        return {'FINISHED'}


class MESH_OT_convert_castle_wall_to_game_mesh(bpy.types.Operator):
    bl_idname = "mesh.convert_castle_wall_to_game_mesh"
    bl_label = "🎮 ゲーム用実体メッシュへ変換 (Make Real)"
    bl_description = "選択中城壁の石材散布インスタンスを実体メッシュとして確定し、Unity/UE向けFBX出力可能にします"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "城壁オブジェクトを選択してください")
            return {'CANCELLED'}

        from ..generators.castle_wall_gen import convert_castle_wall_to_game_mesh

        ok = convert_castle_wall_to_game_mesh(context, obj)
        if ok:
            v_cnt = len(obj.data.vertices)
            p_cnt = len(obj.data.polygons)
            self.report({'INFO'}, f"ゲーム用実体メッシュへ変換完了: {obj.name} ({v_cnt}頂点 / {p_cnt}ポリゴン)")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "有効な城壁 Geometry Nodes モディファイアが見つかりませんでした")
            return {'CANCELLED'}


# ==============================================================================
# 🪨 Cave Operators (新・岩棚テラス＆水流トレンチ洞窟フロア基盤)
# ==============================================================================

class MESH_OT_regenerate_cave(bpy.types.Operator):
    """Regenerate currently active Cave in-place without object accumulation"""
    bl_idname = "mesh.regenerate_cave"
    bl_label = "🔄 洞窟フロアを更新・再生成"
    bl_description = "現在のパラメータで洞窟の岩棚床面・水流をその場更新します（重複堆積しません）"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        from ..generators.cave_gen import create_procedural_cave_scene

        active_obj = context.active_object
        target = None
        if active_obj and active_obj.type == 'MESH' and any(s in active_obj.name for s in ["_Floor", "_Water", "_Ceiling", "_Pillars", "_Debris"]):
            target = active_obj

        import re
        name = re.sub(r'(_Floor|_Water|_Ceiling|_Pillars|_Debris)+$', '', target.name).strip() if target else (props.asset_name.strip() or "Cave")

        is_floor_mode = (props.prop_category == 'CAVE_FLOOR')

        floor_obj, water_obj, ceil_obj, pillar_obj, debris_obj = create_procedural_cave_scene(
            context=context,
            name=name,
            seed=props.seed,
            path_type=random.choice(['S_CURVE', 'STRAIGHT', 'Z_CRANK', 'CHAMBER_HALL']) if props.cave_path_type == 'RANDOM' else props.cave_path_type,
            rock_style=props.cave_rock_style,
            water_type=props.cave_water_type,
            has_river=props.cave_has_river,
            puddle_count=props.cave_puddle_count,
            puddle_scale=props.cave_puddle_scale,
            floor_width=props.cave_floor_width,
            floor_length=props.cave_floor_length,
            river_width=props.cave_river_width,
            river_depth=props.cave_river_depth,
            terrace_steps=props.cave_terrace_steps,
            roughness=props.cave_roughness,
            ceiling_height=props.cave_ceiling_height,
            ceiling_overhang=props.cave_ceiling_overhang,
            ceiling_fissure=props.cave_ceiling_fissure,
            ceiling_roughness=props.cave_ceiling_roughness,
            generate_ceiling=False if is_floor_mode else props.cave_generate_ceiling,
            generate_pillars=False if is_floor_mode else props.cave_generate_pillars,
            pillar_count=props.cave_pillar_count,
            generate_stalactites=False if is_floor_mode else props.cave_generate_stalactites,
            stalactite_density=props.cave_stalactite_density,
            generate_boulders=False if is_floor_mode else props.cave_generate_boulders,
            boulder_count=props.cave_boulder_count,
            add_moss=props.cave_add_moss,
            moss_amount=props.cave_moss_amount,
            setup_lights=props.cave_setup_lights,
            light_intensity=props.cave_light_intensity,
            target_obj=target
        )

        context.view_layer.objects.active = floor_obj
        floor_obj.select_set(True)
        w_msg = f" ＆ 水面: {water_obj.name}" if water_obj else " (川なし)"
        self.report({'INFO'}, f"洞窟フロアを更新しました: {name} (床面: {floor_obj.name}{w_msg})")
        return {'FINISHED'}


class MESH_OT_reroll_cave(bpy.types.Operator):
    """Re-roll cave terrace, river path, and rock roughness with a new random seed"""
    bl_idname = "mesh.reroll_cave"
    bl_label = "🎲 洞窟フロアを再抽選 (Re-Roll)"
    bl_description = "水流の蛇行・岩棚の段差・ボロノイ断層を新しいシードで完全再抽選します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        props.seed = random.randint(1, 999999)
        if getattr(props, 'cave_randomize_shape', False):
            props.cave_river_width = round(random.uniform(3.0, 6.0), 1)
            props.cave_river_depth = round(random.uniform(0.9, 1.8), 2)
            props.cave_terrace_steps = random.randint(3, 6)
        return bpy.ops.mesh.regenerate_cave()


class MESH_OT_create_cave(bpy.types.Operator):
    """Create a new procedural cave floor with terraced rock cliffs and optional river"""
    bl_idname = "mesh.create_cave"
    bl_label = "➕ 新規洞窟フロアを生成"
    bl_description = "切り立った岩棚テラスと蛇行水流トレンチを持つリアルな洞窟フロア基盤を新規生成します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.prop_studio_props
        base_name = props.asset_name.strip() or "Cave"

        name = base_name
        counter = 1
        while (name + "_Floor") in bpy.data.objects:
            name = f"{base_name}_{counter:02d}"
            counter += 1

        from ..generators.cave_gen import create_procedural_cave_scene

        is_floor_mode = (props.prop_category == 'CAVE_FLOOR')

        floor_obj, water_obj, ceil_obj, pillar_obj, debris_obj = create_procedural_cave_scene(
            context=context,
            name=name,
            seed=props.seed,
            path_type=random.choice(['S_CURVE', 'STRAIGHT', 'Z_CRANK', 'CHAMBER_HALL']) if props.cave_path_type == 'RANDOM' else props.cave_path_type,
            rock_style=props.cave_rock_style,
            water_type=props.cave_water_type,
            has_river=props.cave_has_river,
            puddle_count=props.cave_puddle_count,
            puddle_scale=props.cave_puddle_scale,
            floor_width=props.cave_floor_width,
            floor_length=props.cave_floor_length,
            river_width=props.cave_river_width,
            river_depth=props.cave_river_depth,
            terrace_steps=props.cave_terrace_steps,
            roughness=props.cave_roughness,
            ceiling_height=props.cave_ceiling_height,
            ceiling_overhang=props.cave_ceiling_overhang,
            ceiling_fissure=props.cave_ceiling_fissure,
            ceiling_roughness=props.cave_ceiling_roughness,
            generate_ceiling=False if is_floor_mode else props.cave_generate_ceiling,
            generate_pillars=False if is_floor_mode else props.cave_generate_pillars,
            pillar_count=props.cave_pillar_count,
            generate_stalactites=False if is_floor_mode else props.cave_generate_stalactites,
            stalactite_density=props.cave_stalactite_density,
            generate_boulders=False if is_floor_mode else props.cave_generate_boulders,
            boulder_count=props.cave_boulder_count,
            add_moss=props.cave_add_moss,
            moss_amount=props.cave_moss_amount,
            setup_lights=props.cave_setup_lights,
            light_intensity=props.cave_light_intensity,
            target_obj=None
        )

        context.view_layer.objects.active = floor_obj
        floor_obj.select_set(True)
        w_msg = f", 水面: {water_obj.name}" if water_obj else ""
        self.report({'INFO'}, f"新規洞窟フロアを生成しました: {name} (床面: {floor_obj.name}{w_msg})")
        return {'FINISHED'}




