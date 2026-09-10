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
            # Speaker Specific
            if props.prop_category == 'SPEAKER':
                box_spk = layout.box()
                box_spk.label(text="🔊 スタジオモニター・スピーカー設定:", icon='SPEAKER')
                box_spk.prop(props, "speaker_style", text="様式")
                box_spk.prop(props, "speaker_cone_color", text="コーン色")
                box_spk.prop(props, "speaker_scale", text="スケール")

                box_opt = box_spk.box()
                box_opt.label(text="パーツ・イルミネーション設定:", icon='LIGHT')
                box_opt.prop(props, "speaker_has_grille", text="保護サランネット (Grille)")
                box_opt.prop(props, "speaker_led_color", text="電源LED色")

                col_btn = box_spk.column(align=True)
                col_btn.scale_y = 1.3
                col_btn.operator("mesh.regenerate_speaker", text="🔄 再生成・更新 (選択中を更新)", icon='FILE_REFRESH')
                col_btn.operator("mesh.generate_speaker", text="＋ 新規スピーカーを生成", icon='ADD')

            # Wall Clock Specific
            elif props.prop_category == 'CLOCK':
                box_clock = layout.box()
                box_clock.label(text="🕰️ ローマ数字・壁掛け時計設定:", icon='TIME')
                box_clock.prop(props, "clock_shape", text="外枠形状")
                box_clock.prop(props, "clock_style", text="質感")
                box_clock.prop(props, "clock_diameter", text="直径 (m)")

                box_time = box_clock.box()
                box_time.label(text="⏰ 時刻設定 (時・分):", icon='PREVIEW_RANGE')
                row_t = box_time.row(align=True)
                row_t.prop(props, "clock_time_hour", text="時")
                row_t.prop(props, "clock_time_minute", text="分")

                box_opt = box_clock.box()
                box_opt.label(text="パーツ表示設定:", icon='HIDE_OFF')
                row_opt = box_opt.row(align=True)
                row_opt.prop(props, "clock_show_seconds", text="秒針")
                row_opt.prop(props, "clock_show_glass", text="風防ガラス")

                col_btn = box_clock.column(align=True)
                col_btn.scale_y = 1.3
                col_btn.operator("mesh.regenerate_wall_clock", text="🔄 再生成・更新 (選択中を更新)", icon='FILE_REFRESH')
                col_btn.operator("mesh.generate_wall_clock", text="＋ 新規壁掛け時計を生成", icon='ADD')

            # Flask & Potion Specific
            elif props.prop_category == 'FLASK':
                box_flask = layout.box()
                box_flask.label(text="🧪 魔法フラスコ・ポーション設定:", icon='MATERIAL')
                box_flask.prop(props, "flask_shape", text="形状")
                box_flask.prop(props, "flask_scale", text="スケール")
                box_flask.prop(props, "flask_has_cork", text="コルク栓を付ける")

                # 傾き設定
                box_tilt = box_flask.box()
                box_tilt.label(text="📐 容器の傾き & 液面の水平補正:", icon='ORIENTATION_LOCAL')
                box_tilt.prop(props, "flask_tilt", text="フラスコ傾き (度)", slider=True)
                box_tilt.prop(props, "liquid_tilt", text="液面水平補正 (度)", slider=True)

                # 液体設定
                box_liq = box_flask.box()
                box_liq.label(text="🌊 液体 & 表面歪み設定:", icon='MOD_OCEAN')
                box_liq.prop(props, "liquid_level", text="液面の高さ", slider=True)
                box_liq.prop(props, "liquid_surface_noise", text="表面波・歪み", slider=True)
                box_liq.prop(props, "liquid_color", text="液体の色")
                box_liq.prop(props, "liquid_glow", text="発光の強さ", slider=True)

                col_btn = box_flask.column(align=True)
                col_btn.scale_y = 1.3
                col_btn.operator("mesh.regenerate_flask_potion", text="🔄 再生成・更新 (選択中を更新)", icon='FILE_REFRESH')
                col_btn.operator("mesh.generate_flask_potion", text="＋ 新規フラスコを生成", icon='ADD')

            # Image Displace Studio Specific
            elif props.prop_category == 'IMAGE_DISPLACE':
                box_disp = layout.box()
                box_disp.label(text="Image Displace Studio (2D画像立体化):", icon='IMAGE_DATA')
                box_disp.prop(props, "img_disp_path", text="画像ファイル")
                row_quick = box_disp.row(align=True)
                row_quick.scale_y = 1.2
                row_quick.operator("mesh.import_clipboard_image", text="📋 クリップボードから貼り付け", icon='PASTEDOWN')
                row_quick.operator("mesh.import_dropped_image", text="🎯 ドロップ画像から取得", icon='IMPORT')
                box_disp.prop(props, "img_disp_shape", text="立体形状")
                box_disp.prop(props, "img_disp_mat_style", text="マテリアル質感")

                box_param = box_disp.box()
                box_param.label(text="🎛️ リアルタイム変位＆細分化 (Live Displace):", icon='MOD_DISPLACE')
                box_param.prop(props, "img_disp_subdiv_level", text="細分化レベル (Subdiv)")
                row_live = box_param.row(align=True)
                row_live.prop(props, "img_disp_strength", text="Strength (強さ)", slider=True)
                row_live.prop(props, "img_disp_midlevel", text="Midlevel (基準面)", slider=True)

                box_sm = box_disp.box()
                box_sm.label(text="🌊 スムース段差補正 (Smooth):", icon='MOD_SMOOTH')
                row_sm = box_sm.row(align=True)
                row_sm.prop(props, "img_disp_smooth_factor", text="強度 (Factor)", slider=True)
                row_sm.prop(props, "img_disp_smooth_iter", text="反復 (Iter)")

                box_cut = box_disp.box()
                box_cut.label(text="✂️ 型抜き＆色抜き (Live Cutout):", icon='SCULPTMODE_HLT')
                
                # 1. 高さ型抜き
                box_cut.prop(props, "img_disp_enable_cutout", text="同階層（高さ）を型抜き")
                if props.img_disp_enable_cutout:
                    row_cut = box_cut.row(align=True)
                    row_cut.prop(props, "img_disp_cutout_threshold", text="高さ閾値", slider=True)
                    row_cut.prop(props, "img_disp_cutout_invert", text="反転")

                # 2. 類似色型抜き
                box_cut.prop(props, "img_disp_enable_color_cutout", text="🎨 指定色で型抜き (Color Cutout)")
                if props.img_disp_enable_color_cutout:
                    box_col = box_cut.box()
                    row_col = box_col.row(align=True)
                    row_col.prop(props, "img_disp_key_color", text="対象色")
                    row_col.operator("mesh.auto_detect_background_color", text="🪄 自動取得", icon='COLOR')
                    box_col.prop(props, "img_disp_color_tolerance", text="色の許容差", slider=True)

                # 3. 両方ONの場合の併用モード
                if props.img_disp_enable_cutout and props.img_disp_enable_color_cutout:
                    box_cut.prop(props, "img_disp_cutout_mode", text="併用方式")

                box_cube = box_disp.box()
                box_cube.label(text="🧊 面・立体ブロック化 (Solidify / Cube):", icon='MESH_CUBE')
                box_cube.prop(props, "img_disp_solidify_thickness", text="厚み (Thickness)", slider=True)
                box_cube.prop(props, "img_disp_block_style", text="立体様式")

                box_opt = box_disp.box()
                box_opt.label(text="ゲーム最適化 & 超軽量化設定:", icon='MOD_DECIM')
                box_opt.prop(props, "img_disp_planar_angle", text="平面溶解の角度 (Angle)", slider=True)
                box_opt.prop(props, "img_disp_decimate_ratio", text="軽量化比率 (Decimate)", slider=True)
                box_opt.prop(props, "img_disp_close_mesh", text="裏面・底面を完全密閉 (Closed Solid)")

                row_opt_btn = box_opt.row(align=True)
                row_opt_btn.scale_y = 1.2
                row_opt_btn.operator("mesh.optimize_displace_mesh", text="⚡ 不要頂点消去 ＆ スマートUV化", icon='UV')

                col_btn = box_disp.column(align=True)
                col_btn.scale_y = 1.3
                col_btn.operator("mesh.generate_image_displace", text="🖼️ 2D画像から立体プレビュー生成", icon='MOD_DISPLACE')
                col_btn.operator("mesh.bake_game_ready_displace", text="🎮 ゲーム用確定 (裏面密閉 & 超軽量化)", icon='CHECKMARK')

            # Water Specific
            elif props.prop_category == 'WATER':
                box_water = layout.box()
                box_water.label(text="Water Settings (水面・池・湖設定):", icon='MOD_OCEAN')
                box_water.prop(props, "water_shape", text="形状プリセット")
                box_water.prop(props, "water_color_type", text="水質カラー")
                box_water.prop(props, "water_wave_strength", text="波の強さ (Bump)", slider=True)
                if props.water_shape == 'POND':
                    box_water.prop(props, "water_include_bed", text="🌿 泥砂利の池底スラブを生成")
                
                box_anim = layout.box()
                box_anim.label(text="🌊 湖面の微風アニメーション (Wind Animation):", icon='ANIM')
                box_anim.prop(props, "water_animate", text="微風アニメーションを有効化")
                if props.water_animate:
                    box_anim.prop(props, "water_wind_speed", text="風の強さ (Speed)")
                    box_anim.prop(props, "water_anim_frames", text="ループフレーム数")
                    box_anim.operator("mesh.export_animated_water_fbx", text="🎮 アニメーション付き水面FBXを出力", icon='EXPORT')

                box_sky = layout.box()
                box_sky.label(text="🌅 フォトリアル環境光 (Lighting & Sky):", icon='LIGHT_SUN')
                box_sky.operator("mesh.setup_water_sky_lighting", text="🌅 空と太陽光を自動セット (Nishita Sky)", icon='WORLD')

            # Pillar Specific
            elif props.prop_category == 'PILLAR':
                box_pillar = layout.box()
                box_pillar.label(text="Pillar Settings (柱・列柱設定):", icon='MOD_SOLIDIFY')
                box_pillar.prop(props, "pillar_type", text="様式タイプ")
                box_pillar.prop(props, "pillar_mat_type", text="石材マテリアル")
                if props.pillar_type == 'GOTHIC_CLUSTERED':
                    box_pillar.prop(props, "pillar_colonnettes", text="小柱の数 (Colonnettes)")
                elif props.pillar_type == 'CLASSIC_FLUTED':
                    box_pillar.prop(props, "pillar_flutes", text="縦溝の数 (Flutes)")
                    box_pillar.prop(props, "pillar_entasis", text="エンタシス (Entasis)", slider=True)
            # Telescope Specific
            elif props.prop_category == 'TELESCOPE':
                box_tel = layout.box()
                box_tel.label(text="Telescope Settings (天体望遠鏡設定):", icon='CAMERA_DATA')
                box_tel.prop(props, "telescope_style", text="スタイル様式")
                box_tel.prop(props, "telescope_elevation_angle", text="🔭 仰角 (Elevation)", slider=True)
                box_tel.prop(props, "telescope_azimuth_angle", text="🧭 方位角 (Azimuth)", slider=True)
                box_tel.prop(props, "telescope_tripod_height", text="三脚の高さ")
                box_tel.prop(props, "telescope_tube_length", text="鏡筒の長さ")

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

            # Bush Specific
            elif props.prop_category == 'BUSH':
                box_bush = layout.box()
                box_bush.label(text="🌿 低木・茂み・シダ設定 (Bush & Foliage):", icon='OUTLINER_OB_CURVE')
                box_bush.prop(props, "bush_type", text="タイプ")
                box_bush.prop(props, "bush_density", text="密度 (Density)")
                box_bush.prop(props, "bush_leaf_size", text="葉サイズ (Size)")
                if props.bush_type == 'FERN_CLUMP':
                    box_bush.prop(props, "bush_include_fiddleheads", text="🌀 ゼンマイ新芽を付ける")

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

            # Bush Specific
            elif props.prop_category == 'BUSH':
                box_bush = layout.box()
                box_bush.label(text="Bush & Shrub Settings (低木・茂み設定):", icon='FORCE_FORCE')
                box_bush.prop(props, "bush_type", text="")
                box_bush.prop(props, "bush_foliage_style", text="葉スタイル")
                box_bush.prop(props, "bush_density", text="密度 (Density)")
                box_bush.prop(props, "bush_leaf_size", text="葉サイズ (Leaf Size)")

            # Fence Specific
            elif props.prop_category == 'FENCE':
                box_fence = layout.box()
                box_fence.label(text="🚧 実用フェンス・金網プリセット (Modern & Wood):", icon='SNAP_INCREMENT')
                box_fence.prop(props, "fence_preset_type", text="様式")

                # 寸法・形状パラメータ
                box_dim = box_fence.box()
                box_dim.label(text="📐 フェンス寸法 & スパン設定:", icon='ARROW_LEFTRIGHT')
                box_dim.prop(props, "fence_length", text="全長 (m)")
                box_dim.prop(props, "fence_height", text="高さ (m)")
                box_dim.prop(props, "fence_post_spacing", text="支柱スパン (m)")
                if props.fence_preset_type in ('WOOD_HORIZ', 'WOOD_VERT'):
                    box_dim.prop(props, "fence_slat_gap", text="木板の隙間 (m)")
                box_dim.prop(props, "fence_scale", text="スケール")

                # 🪵 木板リアル化 & 経年劣化設定 (WOOD_HORIZ / WOOD_VERT 用)
                if props.fence_preset_type in ('WOOD_HORIZ', 'WOOD_VERT'):
                    box_wood = box_fence.box()
                    box_wood.label(text="🪵 木板リアル化 & 経年劣化 (Realism):", icon='MOD_EDGESPLIT')
                    if props.fence_preset_type == 'WOOD_VERT':
                        box_wood.prop(props, "fence_wood_top_style", text="上部形状")
                    box_wood.prop(props, "fence_wood_jitter", text="ゆがみ・反り", slider=True)
                    box_wood.prop(props, "fence_wood_wear", text="角欠け・劣化", slider=True)
                    box_wood.prop(props, "fence_wood_weathering", text="木目・汚し", slider=True)

                # 🎨 カラー・質感設定 (支柱・鉄線・板の色分け)
                box_color = box_fence.box()

                box_color.label(text="🎨 カラー & 質感設定 (支柱・鉄線・木板):", icon='COLOR')
                box_color.prop(props, "fence_color_preset", text="パレット")
                row_col = box_color.row(align=True)
                row_col.prop(props, "fence_frame_color", text="支柱色")
                row_col.prop(props, "fence_body_color", text="鉄線/板色")
                row_mat = box_color.row(align=True)
                row_mat.prop(props, "fence_metallic", text="金属感", slider=True)
                row_mat.prop(props, "fence_roughness", text="粗さ", slider=True)
                box_color.operator("mesh.apply_fence_colors", text="🎨 選択中フェンスに色を即時反映", icon='RESTRICT_COLOR_ON')

                # 一発生成 & 再生成ボタン（その場更新）
                col_btn = box_fence.column(align=True)
                col_btn.scale_y = 1.3
                col_btn.operator("mesh.regenerate_fence_preset", text="🔄 再生成・更新 (選択中を更新)", icon='FILE_REFRESH')
                col_btn.operator("mesh.generate_fence_preset", text="➕ 新規フェンスを生成", icon='ADD')


                # 従来のクラシック木製柵（サブ設定）
                box_legacy = box_fence.box()
                box_legacy.label(text="🪵 クラシック牧場柵・防壁 (Legacy):", icon='DECORATE')
                box_legacy.prop(props, "fence_type", text="様式")
                if props.fence_type == 'POST_AND_RAIL':
                    box_legacy.prop(props, "fence_rails_count", text="横木の段数")
                box_legacy.prop(props, "fence_post_spacing", text="支柱の間隔")
                box_legacy.prop(props, "fence_decay_jitter", text="経年劣化・歪み", slider=True)


            # Grass & Biome Specific
            elif props.prop_category == 'GRASS':
                # 🌟 1. 内蔵バイオームスキャッター (Geometry Nodes 自己完結型)
                box_biome = layout.box()
                box_biome.label(text="🌿 リアル自然・バイオーム散布 (Nature Biome Scatter):", icon='NODETREE')
                box_biome.prop(props, "biome_type", text="バイオーム")

                box_b_param = box_biome.box()
                box_b_param.label(text="📐 散布・テレイン設定 (Poisson Disk):", icon='MOD_PARTICLES')
                row_bp1 = box_b_param.row(align=True)
                row_bp1.prop(props, "biome_density", text="密度 (Density)")
                row_bp1.prop(props, "biome_min_dist", text="最小離隔 (m)")
                row_bp2 = box_b_param.row(align=True)
                row_bp2.prop(props, "biome_terrain_size", text="規模 (m)")
                row_bp2.prop(props, "biome_undulation", text="起伏 (Undulation)")

                box_b_assets = box_biome.box()
                box_b_assets.label(text="🌱 アセット混入設定:", icon='GROUP')
                row_ba = box_b_assets.row(align=True)
                row_ba.prop(props, "biome_include_fern", text="シダ・新芽")
                row_ba.prop(props, "biome_include_shrub", text="小低木")
                row_ba.prop(props, "biome_include_pebble", text="小石")

                col_b_btn = box_biome.column(align=True)
                col_b_btn.scale_y = 1.3
                col_b_btn.operator("mesh.regenerate_biome_scatter", text="🔄 再生成・更新 (選択中を更新)", icon='FILE_REFRESH')
                col_b_btn.operator("mesh.create_biome_scatter", text="➕ 新規バイオームを生成", icon='ADD')
                col_b_btn.separator()
                col_b_btn.operator("mesh.convert_scatter_to_game_mesh", text="🎮 ゲーム用実体メッシュへ変換 (Make Real)", icon='CHECKMARK')

                # 🌟 2. 従来のヘアパーティクル式 草原（サブ設定）
                box_legacy = layout.box()
                box_legacy.label(text="🌾 クラシック草原パーティクル (Legacy Hair):", icon='OUTLINER_OB_POINTCLOUD')
                box_legacy.prop(props, "grass_mode", text="草タイプ")
                if props.grass_mode == 'MOUND':
                    box_legacy.prop(props, "terrain_type", text="地形")
                    box_legacy.prop(props, "floor_shape", text="床形状")
                box_legacy.prop(props, "grass_density", text="草の本数 (Count)")
                box_legacy.prop(props, "grass_undulation", text="起伏 (Undulation)")
                box_legacy.operator("mesh.create_grass_field", text="🌾 クラシック草原を生成", icon='PARTICLE_DATA')
                box_legacy.operator("mesh.convert_grass_to_game_mesh", text="🎮 実体化メッシュへ変換", icon='MESH_DATA')

            # Floor Specific
            elif props.prop_category == 'FLOOR':
                box_fshape = layout.box()
                box_fshape.label(text="Floor Shape (床の形状):", icon='MESH_PLANE')
                box_fshape.prop(props, "floor_shape", text="")
                if props.floor_shape == 'COBBLESTONE':
                    box_fshape.prop(props, "cobble_stone_size", text="石の大きさ (Stone Size)")
                    box_fshape.prop(props, "cobble_grout_depth", text="目地の深さ (Grout Depth)")
                    box_fshape.prop(props, "cobble_jitter", text="歪み・凹凸 (Jitter)", slider=True)

            # Wall Specific
            elif props.prop_category == 'WALL':
                box_wshape = layout.box()
                box_wshape.label(text="Wall Shape (壁の形状):", icon='MESH_CUBE')
                box_wshape.prop(props, "wall_shape", text="")
                if props.wall_shape == 'COBBLE_WALL':
                    box_wshape.prop(props, "cobble_stone_size", text="石の大きさ (Stone Size)")
                    box_wshape.prop(props, "cobble_jitter", text="突出・歪み (Jitter)", slider=True)

            # Castle Wall (Stone Scatter) Specific
            elif props.prop_category == 'CASTLE_WALL':
                box_cwall = layout.box()
                box_cwall.label(text="🏰 中世城壁・石積み壁 (Castle Stone Wall):", icon='MOD_BUILD')
                box_cwall.prop(props, "castle_wall_shape", text="城壁形状")
                box_cwall.prop(props, "castle_wall_style", text="石積み様式")

                # 寸法設定
                box_cw_dim = box_cwall.box()
                box_cw_dim.label(text="📐 城壁寸法 & 胸壁設定:", icon='ARROW_LEFTRIGHT')
                row_cw1 = box_cw_dim.row(align=True)
                row_cw1.prop(props, "castle_wall_length", text="長さ (m)")
                row_cw1.prop(props, "castle_wall_height", text="高さ (m)")
                row_cw1.prop(props, "castle_wall_thickness", text="厚み (m)")
                if props.castle_wall_shape in ('STRAIGHT', 'BATTLEMENT'):
                    box_cw_dim.prop(props, "castle_wall_has_crenels", text="🛡️ 銃眼胸壁 (Crenels / 狭間) を付ける")

                # 土台メッシュ形状設定（歪み・傾き・出っ張り）
                box_cw_base = box_cwall.box()
                box_cw_base.label(text="🏔️ 土台の自然な起伏・歪み設定:", icon='MOD_DISPLACE')
                row_cwb = box_cw_base.row(align=True)
                row_cwb.prop(props, "castle_wall_batter", text="裾広がり傾斜 (Batter)", slider=True)
                row_cwb.prop(props, "castle_wall_roughness", text="出っ張り・うねり", slider=True)

                # 散布設定
                box_cw_scat = box_cwall.box()
                box_cw_scat.label(text="🧱 石材散布設定 (Poisson Disk):", icon='MOD_PARTICLES')
                row_cws = box_cw_scat.row(align=True)
                row_cws.prop(props, "castle_wall_density", text="石材密度")
                row_cws.prop(props, "castle_wall_min_dist", text="最小間隔 (m)")
                box_cw_scat.prop(props, "castle_wall_jitter", text="凹凸・飛び出し (Jitter)", slider=True)

                # 操作ボタン
                col_cw_btn = box_cwall.column(align=True)
                col_cw_btn.scale_y = 1.3
                col_cw_btn.operator("mesh.regenerate_castle_wall", text="🔄 再生成・更新 (選択中を更新)", icon='FILE_REFRESH')
                col_cw_btn.operator("mesh.create_castle_wall", text="➕ 新規城壁を生成", icon='ADD')
                col_cw_btn.separator()
                col_cw_btn.operator("mesh.convert_castle_wall_to_game_mesh", text="🎮 ゲーム用実体メッシュへ変換 (Make Real)", icon='CHECKMARK')

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
