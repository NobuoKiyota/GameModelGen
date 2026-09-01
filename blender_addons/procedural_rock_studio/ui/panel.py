import bpy

class VIEW3D_PT_prop_studio_panel(bpy.types.Panel):
    bl_label = "Procedural Prop Studio Pro"
    bl_idname = "VIEW3D_PT_prop_studio_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Prop Studio"

    def draw(self, context):
        layout = self.layout
        props = context.scene.prop_studio_props

        # 🌟 1. Category Selector Box
        box_cat = layout.box()
        box_cat.label(text="Preset Category (プリセット):", icon='ASSET_MANAGER')
        box_cat.prop(props, "prop_category", text="")

        # 🌟 2. Giant Top Action Bar
        box_act = layout.box()
        col_act = box_act.column(align=True)
        col_act.scale_y = 1.4
        col_act.operator("mesh.reroll_selected_prop", text="🎲 形状を再抽選 (Re-Roll)", icon='FILE_REFRESH')
        
        row_sub_act = col_act.row(align=True)
        row_sub_act.operator("mesh.create_new_prop", text="➕ 新規作成", icon='ADD')
        row_sub_act.operator("mesh.apply_random_texture_only", text="🎨 テクスチャ変更", icon='IMAGE_DATA')

        col_exp = box_act.column(align=True)
        col_exp.scale_y = 1.3
        col_exp.operator("mesh.export_selected_fbx", text="📦 一発 FBX 出力 (Unity用・自動+1連番)", icon='EXPORT')

        layout.separator()

        # 🌟 3. Studio Mode Tab Switcher
        row_tabs = layout.row(align=True)
        row_tabs.prop(props, "studio_tab", expand=True)

        layout.separator()

        # 🌟 4. Tab 1: Shape & Dimensions & Specific Controls
        if props.studio_tab == 'SHAPE':
            # Water Specific
            if props.prop_category == 'WATER':
                box_water = layout.box()
                box_water.label(text="Water Settings (水面・池・湖設定):", icon='MOD_OCEAN')
                box_water.prop(props, "water_shape", text="形状プリセット")
                box_water.prop(props, "water_color_type", text="水質カラー")
                box_water.prop(props, "water_wave_strength", text="波の強さ (Bump)", slider=True)
                if props.water_shape == 'POND':
                    box_water.prop(props, "water_include_bed", text="🌿 泥砂利の池底スラブを生成")

            # Tree Specific
            elif props.prop_category == 'TREE':
                box_tree = layout.box()
                box_tree.label(text="Tree Settings (リアル樹木設定):", icon='OUTLINER_OB_LIGHT')
                box_tree.prop(props, "tree_species", text="樹種")
                box_tree.prop(props, "tree_material_mode", text="マテリアル方式")
                box_tree.prop(props, "tree_branch_levels", text="枝分かれ深さ")
                box_tree.prop(props, "tree_curvature", text="枝のうねり・曲がり", slider=True)
                box_tree.prop(props, "tree_has_leaves", text="🍃 葉を付ける")
                if props.tree_has_leaves:
                    box_tree.prop(props, "tree_leaf_style", text="葉のスタイル")
                    box_tree.prop(props, "tree_leaf_count", text="葉の密度")

            # Chair Specific
            elif props.prop_category in ('CHAIR', 'OFFICE_CHAIR'):
                box_chair = layout.box()
                box_chair.label(text="Chair Settings (椅子設定):", icon='PASTEDOWN')
                box_chair.prop(props, "chair_type", text="タイプ")
                if props.chair_type in ('DINING_CHAIR', 'ARMCHAIR', 'ROUND_STOOL', 'SQUARE_STOOL'):
                    box_chair.prop(props, "chair_seat_style", text="座面")
                    if props.chair_type in ('DINING_CHAIR', 'ARMCHAIR'):
                        box_chair.prop(props, "chair_back_style", text="背もたれ")
                    box_chair.prop(props, "chair_leg_layout", text="脚の構造")
                    box_chair.prop(props, "table_leg_style", text="脚の装飾")
                box_chair.prop(props, "rand_furniture_style", text="🎲 スタイルランダム")

            # Table Specific
            elif props.prop_category in ('TABLE', 'PC_DESK'):
                box_tab = layout.box()
                box_tab.label(text="Table / Desk Settings (机・デスク設定):", icon='WORKSPACE')
                box_tab.prop(props, "table_shape", text="天板形状")
                box_tab.prop(props, "table_leg_style", text="脚の形状・フレーム")
                box_tab.prop(props, "rand_furniture_style", text="🎲 スタイルランダム")

            # Chest Specific
            elif props.prop_category == 'CHEST':
                box_chest = layout.box()
                box_chest.label(text="Chest Settings (タンス設定):", icon='FILE_ARCHIVE')
                box_chest.prop(props, "chest_tiers", text="引き出し段数 (2~5段)")
                box_chest.prop(props, "chest_handle_style", text="取っ手金具")
                box_chest.prop(props, "rand_furniture_style", text="🎲 スタイルランダム")

            # Bed Specific
            elif props.prop_category == 'BED':
                box_bed = layout.box()
                box_bed.label(text="Bed Settings (ベッド設定):", icon='COMMUNITY')
                box_bed.prop(props, "bed_size", text="サイズ")
                box_bed.prop(props, "column_ornament_style", text="四隅ポスト装飾")
                box_bed.prop(props, "rand_furniture_style", text="🎲 スタイルランダム")

            # Bookshelf Specific
            elif props.prop_category == 'BOOKSHELF':
                box_shelf = layout.box()
                box_shelf.label(text="Bookshelf Settings (本棚設定):", icon='BOOKMARKS')
                box_shelf.prop(props, "shelf_tiers", text="棚段数 (2~4段)")
                box_shelf.prop(props, "column_ornament_style", text="側柱の装飾")
                box_shelf.prop(props, "rand_furniture_style", text="🎲 スタイルランダム")

            # Fence Specific
            elif props.prop_category == 'FENCE':
                box_fence = layout.box()
                box_fence.label(text="Fence Architecture (柵・防壁タイプ):", icon='SNAP_INCREMENT')
                box_fence.prop(props, "fence_type", text="")
                if props.fence_type == 'POST_AND_RAIL':
                    box_fence.prop(props, "fence_rails_count", text="横木の段数 (Rails)")
                box_fence.prop(props, "fence_post_spacing", text="支柱の間隔 (Spacing)")
                box_fence.prop(props, "fence_decay_jitter", text="経年劣化・歪み (Jitter)", slider=True)

            # Grass Specific
            elif props.prop_category == 'GRASS':
                box_gmode = layout.box()
                box_gmode.label(text="Grass Type (草原タイプ):", icon='OUTLINER_OB_CURVE')
                box_gmode.prop(props, "grass_mode", text="")
                if props.grass_mode == 'MOUND':
                    box_gmode.prop(props, "floor_shape", text="床形状")
                box_gfield = layout.box()
                box_gfield.label(text="🌾 Grass Field Studio (草原一括生成):", icon='OUTLINER_OB_POINTCLOUD')
                row_gf = box_gfield.row(align=True)
                row_gf.scale_y = 1.5
                row_gf.operator("mesh.create_grass_field", text="🌾 草原シーンを生成", icon='PARTICLE_POINT')
                box_gfield.prop(props, "grass_density", text="草の密度 (Hair Count)")
                box_gfield.prop(props, "grass_undulation", text="地面の起伏 (Undulation)")
                box_gfield.prop(props, "grass_weight_noise", text="ウェイトノイズ (密度ムラ)")
                box_gfield.separator()
                box_gfield.label(text="🎮 Unity / FBX ゲーム用変換:", icon='EXPORT')
                box_gfield.operator("mesh.convert_grass_to_game_mesh",
                                    text="🎮 実体化メッシュへ変換 (Make Real)", icon='MESH_DATA')

            # Floor Specific
            elif props.prop_category == 'FLOOR':
                box_fshape = layout.box()
                box_fshape.label(text="Floor Shape (床の形状):", icon='MESH_PLANE')
                box_fshape.prop(props, "floor_shape", text="")

            # Wall Specific
            elif props.prop_category == 'WALL':
                box_wshape = layout.box()
                box_wshape.label(text="Wall Shape (壁の形状):", icon='MESH_CUBE')
                box_wshape.prop(props, "wall_shape", text="")

            # Dimensions Box
            box_dim = layout.box()
            row_dh = box_dim.row(align=True)
            row_dh.label(text="Dimensions (サイズ):", icon='EMPTY_DATA')
            row_dh.prop(props, "rand_dimensions", text="🎲 ランダム")
            
            row_d = box_dim.row(align=True)
            row_d.enabled = not props.rand_dimensions
            if (props.prop_category in ('FLOOR', 'GRASS')) and props.floor_shape in ('CIRCLE', 'HEXAGON'):
                row_d.prop(props, "size_x", text="直径")
                row_d.prop(props, "size_z", text="厚み/高さ")
            else:
                row_d.prop(props, "size_x", text="X (幅)")
                row_d.prop(props, "size_y", text="Y (奥行)")
                row_d.prop(props, "size_z", text="Z (高さ)")

            # Surface / Fractures for Rock & Architecture
            if props.prop_category in ("FLOOR", "WALL"):
                box_scar = layout.box()
                row_sch = box_scar.row(align=True)
                row_sch.label(text="Organic Cracks (有機的亀裂・傷):", icon='MOD_BOOLEAN')
                row_sch.prop(props, "rand_fractures", text="🎲 ランダム")
                col_sc = box_scar.column(align=True)
                col_sc.enabled = not props.rand_fractures
                col_sc.prop(props, "floor_crack_count", text="亀裂・傷の箇所数 (1~20)")
                col_sc.prop(props, "crack_depth", text="亀裂の深さ・太さ", slider=True)
            elif props.prop_category in ("ROCK", "CRAG"):
                box_rock = layout.box()
                box_rock.label(text="Rock Type & Palette (岩石タイプ＆色彩):", icon='COLORSET_03_VEC')
                row_rt = box_rock.row(align=True)
                row_rt.prop(props, "rock_type", text="")
                row_rt.prop(props, "rand_type", text="🎲 形状")
                box_rock.prop(props, "rock_palette", text="🎨 カラーパレット")

                box_surf = layout.box()
                row_sh = box_surf.row(align=True)
                row_sh.label(text="Surface (粗さ・削り):", icon='MOD_SUBSURF')
                row_sh.prop(props, "rand_surface", text="🎲 ランダム")
                col_s = box_surf.column(align=True)
                col_s.enabled = not props.rand_surface
                col_s.prop(props, "roughness", slider=True)
                col_s.prop(props, "chisel_strength", slider=True)

                box_frac = layout.box()
                row_fh = box_frac.row(align=True)
                row_fh.label(text="Fractures (欠け・亀裂):", icon='MOD_BOOLEAN')
                row_fh.prop(props, "rand_fractures", text="🎲 ランダム")
                col_f = box_frac.column(align=True)
                col_f.enabled = not props.rand_fractures
                col_f.prop(props, "big_chunk_cuts")
                col_f.prop(props, "crack_depth", slider=True)

        # 🌟 5. Tab 2: Textures & UV Mapping Mode
        elif props.studio_tab == 'TEX':
            box_map = layout.box()
            box_map.label(text="Texture UV Mapping Mode (貼り方):", icon='UV')
            box_map.prop(props, "uv_mapping_mode", text="")
            if props.uv_mapping_mode == 'TILING':
                box_map.prop(props, "texture_tiling", text="リピート倍率", slider=True)

            box_tex = layout.box()
            box_tex.label(text="PBR Texture Folder (自動連動):", icon='FILE_FOLDER')
            box_tex.prop(props, "texture_folder", text="")
            
            row_tf = box_tex.row(align=True)
            row_tf.prop(props, "use_folder_texture", text="テクスチャ有効")
            row_tf.prop(props, "rand_texture", text="🎲 ランダム")
            
            if props.use_folder_texture and not props.rand_texture:
                box_tex.prop(props, "selected_texture", text="")
            
            box_tex.operator("mesh.apply_random_texture_only", text="🎨 テクスチャのみ再抽選", icon='IMAGE_DATA')

            # 🏔️ 3D Displacement Box
            box_disp = layout.box()
            box_disp.label(text="🏔️ 3D ディスプレイスメント (凹凸立体化):", icon='MOD_DISPLACE')
            box_disp.prop(props, "enable_displacement", text="3D凹凸立体化を有効化")
            if props.enable_displacement:
                col_d = box_disp.column(align=True)
                col_d.prop(props, "displacement_strength", text="凹凸の強さ", slider=True)
                col_d.prop(props, "displacement_midlevel", text="基準高さ", slider=True)
                col_d.prop(props, "displacement_subdiv", text="メッシュ細分化 (0~4)")
                col_d.prop(props, "apply_disp_to_mesh", text="🎮 メッシュへベイク (FBX用)")

        # 🌟 6. Tab 3: Export Settings
        elif props.studio_tab == 'EXPORT':
            # 🔥 Auto PBR Texture Baker Box
            box_bake = layout.box()
            box_bake.label(text="🔥 Auto PBR Baker (Unityベタ塗り解消):", icon='RENDER_STILL')
            box_bake.prop(props, "bake_resolution", text="解像度")
            row_bp = box_bake.row(align=True)
            row_bp.prop(props, "bake_diffuse", text="BaseColor (色)")
            row_bp.prop(props, "bake_normal", text="Normal (法線)")
            box_bake.prop(props, "auto_bake_on_export", text="⚡ FBX出力時に自動ベイクする")
            
            row_bact = box_bake.row(align=True)
            row_bact.scale_y = 1.3
            row_bact.operator("mesh.bake_prop_textures", text="🔥 手動で今すぐベイク", icon='TEXTURE')

            box_exp = layout.box()
            box_exp.label(text="Unity FBX Settings:", icon='EXPORT')
            box_exp.prop(props, "asset_name", text="アセット名")
            box_exp.prop(props, "export_folder", text="")
            box_exp.operator("mesh.open_export_folder", text="📂 保存先フォルダを開く", icon='FOLDER_REDIRECT')
