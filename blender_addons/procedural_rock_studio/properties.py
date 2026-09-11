import bpy
import os
from .utils.texture_utils import get_textures_from_folder

def get_texture_enum_items(self, context):
    props = context.scene.prop_studio_props
    tex_files = get_textures_from_folder(props.texture_folder)
    if not tex_files:
        return [('NONE', "No Textures Found", "No image files found in folder")]
    return [(f, f, f) for f in tex_files]


def update_category_preset(self, context):
    props = context.scene.prop_studio_props
    cat = props.prop_category
    
    name_map = {
        'ROCK': "Rock_Boulder",
        'CRAG': "Crag_Rock",
        'TREE': "Real_Tree",
        'PC_DESK': "Modern_PC_Desk",
        'OFFICE_CHAIR': "Modern_Office_Chair",
        'FLOOR': "Floor_Tile",
        'WALL': "Wall_Block",
        'PILLAR': "Pillar_Column",
        'BEAM': "Timber_Beam",
        'BEAM_ARCH': "Stone_Arch",
        'GRASS': "Grass_Meadow",
        'BOOKSHELF': "Antique_Bookshelf",
        'TABLE': "Antique_Table",
        'CHAIR': "Antique_Chair",
        'CHEST': "Antique_Chest",
        'BED': "Antique_Bed",
        'FENCE': "Wooden_Fence",
        'BUSH': "Bush_Shrub",
        'IMAGE_DISPLACE': "Image_Displace_Asset",
        'CASTLE_WALL': "Castle_Wall",
        'CAVE': "Cave_Dungeon",
        'CAVE_FLOOR': "Cave_Floor"
    }
    props.asset_name = name_map.get(cat, "Prop_Asset")

    if cat == "IMAGE_DISPLACE":
        props.size_x = 2.0
        props.size_y = 2.0
        props.size_z = 0.2
        props.uv_mapping_mode = 'FIT'
    elif cat == "BUSH":
        props.size_x = 1.2
        props.size_y = 1.2
        props.size_z = 0.9
        props.uv_mapping_mode = 'FIT'
    elif cat == "FENCE":
        props.size_x = 4.0
        props.size_y = 0.4
        props.size_z = 1.2
        props.uv_mapping_mode = 'FIT'
    elif cat == "TREE":
        props.size_x = 3.5
        props.size_y = 3.5
        props.size_z = 4.5
        props.uv_mapping_mode = 'FIT'
    elif cat in ("ROCK", "CRAG"):
        props.size_x = 2.2
        props.size_y = 2.0
        props.size_z = 1.6
        props.uv_mapping_mode = 'TILING'
    elif cat == "PC_DESK":
        props.size_x = 1.6
        props.size_y = 0.75
        props.size_z = 0.72
        props.table_shape = 'MONITOR_RISER_DESK'
        props.table_leg_style = 'STEEL_LOOP'
        props.uv_mapping_mode = 'FIT'
    elif cat == "OFFICE_CHAIR":
        props.size_x = 0.62
        props.size_y = 0.60
        props.size_z = 0.96
        props.chair_type = 'OFFICE_TASK_CHAIR'
        props.uv_mapping_mode = 'FIT'
    elif cat == "CHAIR":
        props.size_x = 0.55
        props.size_y = 0.55
        props.size_z = 0.95
        props.chair_type = 'DINING_CHAIR'
        props.uv_mapping_mode = 'FIT'
    elif cat == "CHEST":
        props.size_x = 1.4
        props.size_y = 0.6
        props.size_z = 1.1
        props.chest_tiers = 3
        props.chest_handle_style = 'RING'
        props.uv_mapping_mode = 'FIT'
    elif cat == "BED":
        props.size_x = 1.4
        props.size_y = 2.1
        props.size_z = 1.35
        props.bed_size = 'SINGLE'
        props.uv_mapping_mode = 'FIT'
    elif cat == "BOOKSHELF":
        props.size_x = 1.6
        props.size_y = 0.5
        props.size_z = 2.1
        props.shelf_tiers = 3
        props.column_ornament_style = 'ORNAMENTAL'
        props.uv_mapping_mode = 'FIT'
    elif cat == "WATER":
        props.size_x = 6.0
        props.size_y = 6.0
        props.size_z = 0.8
        props.uv_mapping_mode = 'FIT'
    elif cat == "TABLE":
        props.size_x = 1.8
        props.size_y = 1.0
        props.size_z = 0.78
        props.table_shape = 'RECTANGLE'
        props.table_leg_style = 'ORNAMENTAL'
        props.uv_mapping_mode = 'FIT'
    elif cat == "GRASS":
        props.size_x = 3.0
        props.size_y = 3.0
        props.size_z = 0.3
        props.uv_mapping_mode = 'FIT'
    elif cat == "FLOOR":
        props.size_x = 2.0
        props.size_y = 2.0
        props.size_z = 0.2
        props.uv_mapping_mode = 'FIT'
    elif cat == "WALL":
        props.size_x = 3.0
        props.size_y = 1.0
        props.size_z = 2.5
        props.uv_mapping_mode = 'FIT'
    elif cat == "BEAM":
        props.size_x = 2.4
        props.size_y = 1.5
        props.size_z = 2.0
        props.uv_mapping_mode = 'FIT'
    elif cat == "BEAM_ARCH":
        props.size_x = 3.2
        props.size_y = 0.8
        props.size_z = 3.8
        props.uv_mapping_mode = 'FIT'
    elif cat == "PILLAR":
        props.size_x = 1.2
        props.size_y = 1.2
        props.size_z = 2.5
        props.uv_mapping_mode = 'FIT'

    folder_map = {
        'ROCK': r"Z:\MeshCreator\textures\Rock",
        'CRAG': r"Z:\MeshCreator\textures\Rock",
        'TREE': r"Z:\MeshCreator\textures\Wood",
        'PC_DESK': r"Z:\MeshCreator\textures\Wood",
        'OFFICE_CHAIR': r"Z:\MeshCreator\textures\Wood",
        'FLOOR': r"Z:\MeshCreator\textures\Floor",
        'WALL': r"Z:\MeshCreator\textures\Wall",
        'PILLAR': r"Z:\MeshCreator\textures\Pillar",
        'BEAM': r"Z:\MeshCreator\textures\Wood",
        'BEAM_ARCH': r"Z:\MeshCreator\textures\Wall",
        'GRASS': r"Z:\MeshCreator\textures\Grass",
        'WATER': r"Z:\MeshCreator\textures\Floor",
        'BOOKSHELF': r"Z:\MeshCreator\textures\Wood",
        'TABLE': r"Z:\MeshCreator\textures\Wood",
        'CHAIR': r"Z:\MeshCreator\textures\Wood",
        'CHEST': r"Z:\MeshCreator\textures\Wood",
        'BED': r"Z:\MeshCreator\textures\Wood",
        'FENCE': r"Z:\MeshCreator\textures\Wood",
        'BUSH': r"Z:\MeshCreator\textures\Grass"
    }
    
    target_folder = folder_map.get(cat, r"Z:\MeshCreator\textures\Rock")
    try:
        os.makedirs(target_folder, exist_ok=True)
    except Exception:
        pass
    props.texture_folder = target_folder


def update_displace_realtime(self, context):
    """Strength と Midlevel を選択中オブジェクトの Displace モディファイアにリアルタイム反映"""
    obj = context.active_object
    if not obj or obj.type != 'MESH':
        return
    mod = obj.modifiers.get("Displace_Relief")
    if not mod:
        for m in obj.modifiers:
            if m.type == 'DISPLACE':
                mod = m
                break
    if mod:
        mod.strength = self.img_disp_strength
        mod.mid_level = self.img_disp_midlevel


def update_cutout_realtime(self, context):
    """型抜き（Cutout）＆ 色抜き（Color Keying）を Geometry Nodes でリアルタイム反映"""
    obj = context.active_object
    if not obj or obj.type != 'MESH':
        return
    from .generators.image_displace_gen import setup_or_update_cutout_modifier

    mode_map = {'OR': 0, 'AND': 1, 'COLOR_ONLY': 2, 'HEIGHT_ONLY': 3}
    c_mode = mode_map.get(getattr(self, 'img_disp_cutout_mode', 'OR'), 0)

    setup_or_update_cutout_modifier(
        obj,
        enable=(self.img_disp_enable_cutout or getattr(self, 'img_disp_enable_color_cutout', False)),
        threshold=self.img_disp_cutout_threshold,
        invert=self.img_disp_cutout_invert,
        enable_color=getattr(self, 'img_disp_enable_color_cutout', False),
        key_color=getattr(self, 'img_disp_key_color', (1.0, 1.0, 1.0, 1.0)),
        color_tolerance=getattr(self, 'img_disp_color_tolerance', 0.15),
        cutout_mode=c_mode
    )


def update_subdiv_realtime(self, context):
    """細分化 (Subdivision) レベルをリアルタイム反映"""
    obj = context.active_object
    if not obj or obj.type != 'MESH':
        return
    from .generators.image_displace_gen import setup_or_update_subdiv_modifier
    setup_or_update_subdiv_modifier(obj, level=self.img_disp_subdiv_level)


def update_smooth_realtime(self, context):
    """スムース (Smooth) をリアルタイム反映"""
    obj = context.active_object
    if not obj or obj.type != 'MESH':
        return
    from .generators.image_displace_gen import setup_or_update_smooth_modifier
    setup_or_update_smooth_modifier(obj, factor=self.img_disp_smooth_factor, iterations=self.img_disp_smooth_iter)


def update_solidify_realtime(self, context):
    """面（立方体）化 (Solidify / Voxel) をリアルタイム反映"""
    obj = context.active_object
    if not obj or obj.type != 'MESH':
        return
    from .generators.image_displace_gen import setup_or_update_solidify_modifier
    setup_or_update_solidify_modifier(obj, thickness=self.img_disp_solidify_thickness, style=self.img_disp_block_style)


def update_fence_live_color(self, context):
    """選択中フェンスのマテリアル色・質感をリアルタイム反映"""
    active_obj = context.active_object
    if active_obj:
        from .generators.fence_gen import apply_fence_material_colors
        apply_fence_material_colors(
            active_obj,
            frame_color=self.fence_frame_color,
            body_color=self.fence_body_color,
            metallic=self.fence_metallic,
            roughness=self.fence_roughness,
            weathering=getattr(self, 'fence_wood_weathering', 0.4)
        )



def update_fence_color_preset(self, context):
    """フェンスカラープリセットの切り替え"""
    cp = self.fence_color_preset
    ptype = self.fence_preset_type

    if cp == 'PRESET_DEFAULT':
        if ptype == 'WIRE_CROSS':
            self.fence_frame_color = (0.05, 0.05, 0.05, 1.0)
            self.fence_body_color  = (0.06, 0.06, 0.06, 1.0)
            self.fence_metallic = 0.25
            self.fence_roughness = 0.35
        elif ptype == 'WIRE_X':
            self.fence_frame_color = (0.08, 0.38, 0.22, 1.0)
            self.fence_body_color  = (0.08, 0.42, 0.24, 1.0)
            self.fence_metallic = 0.15
            self.fence_roughness = 0.40
        else: # WOOD
            self.fence_frame_color = (0.18, 0.12, 0.08, 1.0)
            self.fence_body_color  = (0.42, 0.25, 0.15, 1.0)
            self.fence_metallic = 0.0
            self.fence_roughness = 0.60
    elif cp == 'SILVER':
        self.fence_frame_color = (0.65, 0.67, 0.70, 1.0)
        self.fence_body_color  = (0.75, 0.77, 0.80, 1.0)
        self.fence_metallic = 0.85
        self.fence_roughness = 0.25
    elif cp == 'BLACK':
        self.fence_frame_color = (0.03, 0.03, 0.03, 1.0)
        self.fence_body_color  = (0.05, 0.05, 0.05, 1.0)
        self.fence_metallic = 0.20
        self.fence_roughness = 0.35
    elif cp == 'WHITE':
        self.fence_frame_color = (0.88, 0.89, 0.90, 1.0)
        self.fence_body_color  = (0.92, 0.92, 0.93, 1.0)
        self.fence_metallic = 0.10
        self.fence_roughness = 0.30
    elif cp == 'GREEN':
        self.fence_frame_color = (0.08, 0.38, 0.22, 1.0)
        self.fence_body_color  = (0.08, 0.42, 0.24, 1.0)
        self.fence_metallic = 0.10
        self.fence_roughness = 0.40
    elif cp == 'WOOD_BROWN':
        self.fence_frame_color = (0.16, 0.10, 0.06, 1.0)
        self.fence_body_color  = (0.40, 0.23, 0.13, 1.0)
        self.fence_metallic = 0.0
        self.fence_roughness = 0.65

    update_fence_live_color(self, context)


class PropStudioProperties(bpy.types.PropertyGroup):

    prop_category: bpy.props.EnumProperty(
        name="Category",
        items=[
            ('SPEAKER', "🔊 スタジオモニター・スピーカー (Audio Speaker)", "DTM/3Dオーディオ・ベベルキャビネット・ウーファー・ツイーター・LED・グリル"),
            ('CLOCK', "🕰️ ローマ数字・壁掛け時計 (Wall Clock)", "モールディング外枠・3Dローマ数字立体刻印・時刻連動回転針・風防ガラス"),
            ('FLASK', "🧪 魔法フラスコ・ポーション (Potion Flask)", "透過屈折ガラス容器・色変更・表面波歪み・傾き水平追従液体"),
            ('IMAGE_DISPLACE', "🖼️ 2D画像立体化 (Image Displace Studio)", "2D画像から3Dレリーフ・コイン・地形を半自動立体化（アスペクト比自動同期＆クローズド密閉）"),
            ('BUSH', "🌿 低木・茂み・シダ (Bush / Shrub / Fern)", "textures/Grass/ と自動連動（丸型低木/野生の藪/シダ株/生垣・球状法線転送）"),
            ('TELESCOPE', "🔭 天体望遠鏡 (Astronomical Telescope)", "Celestron StarSense風（三脚・経緯台・鏡筒・接眼部・スマホドック・可動ピボット）"),
            ('FENCE', "🪵 木製の柵・フェンス・砦 (Wooden Fence / Palisade)", "textures/Wood/ と自動連動（牧場横木/先端尖りピケット/X筋交い/丸太防壁）"),

            ('WATER', "💧 水面・池・湖 (Water / Lake / Ocean)", "湖・池・四角プール・泉・大海原（物理屈折IOR 1.333＆二重波紋）"),
            ('TREE', "🌳 リアル樹木・自然木 (Real Tree / Sapling)", "textures/Wood/ と自動連動（オーク/針葉樹/柳/ヤシ/白樺/紅葉・幹枝葉生成）"),
            ('PC_DESK', "🖥️ 近代PCデスク (Modern PC Desk)", "textures/Wood/ と自動連動（モニタースタンド付き・スチール口の字脚・L字型）"),
            ('OFFICE_CHAIR', "💺 近代オフィスチェア (Modern Office Chair)", "textures/Wood/ と自動連動（5本足キャスター＆ガスシリンダー＆シェル）"),
            ('TABLE', "🪑 アンティーク机 (Antique Table)", "textures/Wood/ と自動連動（四角/角丸/楕円＆アンティーク4本脚）"),
            ('CHAIR', "💺 アンティーク椅子 (Antique Chair)", "textures/Wood/ と自動連動（革張り座面/埋め込み背板/1本脚/X脚）"),
            ('BOOKSHELF', "📚 本棚・収納棚 (Bookshelf / Rack)", "textures/Wood/ と自動連動（2~4段棚＆対称装飾柱）"),
            ('CHEST', "🚪 チェスト・タンス (Chest of Drawers)", "textures/Wood/ と自動連動（2~5段引き出し＆取っ手金具）"),
            ('BED', "🛏️ アンティークベッド (Antique Bedframe)", "textures/Wood/ と自動連動（四隅装飾柱＆ヘッドボード＆マットレス）"),
            ('CRAG', "🏔️ 険岩・ごつごつ岩 (Jagged Crags)", "textures/Rock/ と自動連動（Convex Hull多面体＆鋭利な稜線岩）"),
            ('ROCK', "🪨 丸岩・巨石 (Round Boulder / Soft Rock)", "textures/Rock/ と自動連動（自然な丸みを持つ丸岩・河原の石）"),
            ('GRASS', "🌿 草原・草地 (Grassland / Meadow)", "textures/Grass/ と自動連動（草地丘陵スラブ＆十字草むら）"),
            ('FLOOR', "🟫 床・タイル (Floor / Tile)", "textures/Floor/ と自動連動（正方形・円形・六角形＆有機的亀裂）"),
            ('WALL', "🧱 壁・城壁 (Wall / Ruins)", "textures/Wall/ と自動連動（直線・L字・円弧・▲三角切妻壁）"),
            ('CASTLE_WALL', "🏰 城壁・石積み壁 (Castle Stone Wall)", "動画の散布手法を応用した立体石材ブロック積みの城壁・石垣・銃眼胸壁"),
            ('CAVE_FLOOR', "🪨 洞窟床・新テレイン (Cave Floor / Terrain)", "なだらかな自然傾斜・大地の厚みスラブ・水たまり・岩肌スタイルを持つ新・床フォーマット"),
            ('CAVE', "🪨 洞窟・岩窟ジオラマ (Procedural Cave)", "一本道・S字・Y字分岐・大空洞を持つリアルな洞窟システム（地面・天井分離）"),
            ('PILLAR', "🏛️ 柱・石柱 (Pillar / Column)", "textures/Pillar/ と自動連動"),
            ('BEAM', "🪵 梁・丸太支柱 (Timber Log Beam)", "textures/Wood/ と自動連動（シリンダー丸太梁）"),
            ('BEAM_ARCH', "🏛️ 建築アーチ・回廊 (Stone Arch / Colonnade)", "ローマ半円/ゴシック尖頭・要石・多段モールディング・連続列廊・ヴォールト天井")
        ],
        default='WATER',
        update=update_category_preset
    )

    studio_tab: bpy.props.EnumProperty(
        name="Studio Tab",
        items=[
            ('SHAPE', "📐 形状", "形状・寸法・家具パーツ設定"),
            ('TEX', "🎨 テクスチャ", "PBRテクスチャ連動・UVフィット設定"),
            ('EXPORT', "📦 出力", "Unity FBXエクスポート設定")
        ],
        default='SHAPE'
    )

    # Water Specific
    water_shape: bpy.props.EnumProperty(
        name="水面形状 (Water Shape)",
        items=[
            ('LAKE', "🏞️ 湖・大水面 (Lake)", "不規則な自然海岸線と穏やかな大波うねり"),
            ('POND', "🌿 自然池・湧水池 (Pond)", "有機的曲線を持つ池＋池底スラブ構造（泥砂利）"),
            ('SQUARE', "🔲 四角・プール・水路 (Square)", "近代建築プール・ダンジョン水路・四角水面"),
            ('CIRCLE', "🔘 円形・泉・水たまり (Circle)", "円形の泉・噴水・水たまり"),
            ('OCEAN', "🌊 大海原 (Ocean)", "Ocean Modifier によるリアルな海洋波浪シミュレーション")
        ],
        default='LAKE'
    )
    water_color_type: bpy.props.EnumProperty(
        name="水質カラー (Water Color)",
        items=[
            ('TROPICAL', "🏝️ 南国エメラルドシアン (Tropical Cyan)", "映画Flow風 澄み切ったエメラルドブルー"),
            ('DEEP_OCEAN', "🌊 ディープオーシャン (Deep Ocean Navy)", "深海・荒波の重厚な紺碧"),
            ('POND_GREEN', "🌿 リバー・ポンド (Natural Pond Green)", "水草や泥底が似合う自然な緑褐色"),
            ('CRYSTAL', "💎 クリスタルクリア (Pure Crystal)", "プール・水槽用の無色透明")
        ],
        default='TROPICAL'
    )
    water_wave_strength: bpy.props.FloatProperty(name="波の強さ (Wave Strength)", default=0.12, min=0.0, max=1.0, description="水面のさざ波・うねりBump強度")
    water_include_bed: bpy.props.BoolProperty(name="池底スラブを生成 (Include Bed Slab)", default=True, description="池（POND）生成時に泥砂利の池底スラブを同時に生成するか")
    water_animate: bpy.props.BoolProperty(name="湖面の微風アニメーション (Wind Loop Animation)", default=True, description="再生時(Space)に湖面がそよ風でゆらゆら動くループアニメーションを生成")
    water_wind_speed: bpy.props.FloatProperty(name="風の強さ (Wind Speed)", default=1.0, min=0.2, max=5.0, description="そよ風〜強風の速度")
    water_anim_frames: bpy.props.IntProperty(name="ループフレーム数 (Frames)", default=60, min=24, max=240, description="1サイクルのループフレーム数")

    # Tree Specific
    tree_species: bpy.props.EnumProperty(
        name="樹種 (Tree Species)",
        items=[
            ('OAK', "🌳 オーク・カシ (Oak / Deciduous)", "どっしりとした大木・自然な枝分かれの広葉樹"),
            ('PINE', "🌲 パイン・マツ (Pine / Conifer)", "上に向かって三角錐状に広がる常緑針葉樹"),
            ('WILLOW', "🌿 シダレヤナギ (Weeping Willow)", "下に向かって優雅に垂れ下がる枝"),
            ('PALM', "🌴 ヤシの木 (Palm Tree)", "南国・ビーチの放射状大葉を持つヤシの木"),
            ('BIRCH', "⚪ シラカバ (Birch)", "すらりと伸びる白い幹の落葉樹"),
            ('JAPANESE_MAPLE', "🍁 モミジ・カエデ (Japanese Maple)", "繊細で風情ある和風の枝ぶり")
        ],
        default='OAK'
    )
    tree_has_leaves: bpy.props.BoolProperty(name="🍃 葉を付ける (Foliage)", default=True, description="葉（リーフクラスタ）を生成するか（OFFで冬の枯れ木・枝のみ）")
    tree_leaf_style: bpy.props.EnumProperty(
        name="葉の表現スタイル",
        items=[
            ('QUAD_CROSS', "🍃 十字リーフ (Cross Billboard)", "ゲーム向け最適化十字ビルボード葉（アルファ透過連動）"),
            ('CANOPY_VOLUME', "🌳 ボリューム樹冠 (Canopy Volume)", "アニメ調・スタイライズドローポリ樹冠クラスタ")
        ],
        default='QUAD_CROSS'
    )
    tree_leaf_count: bpy.props.IntProperty(name="葉の密度 (Leaf Density)", default=120, min=20, max=400, description="生成する葉クラスタの数量")
    tree_branch_levels: bpy.props.IntProperty(name="枝分かれ階層 (Branch Levels)", default=2, min=1, max=3, description="枝分かれの深さ (1:主枝のみ, 2:小枝あり, 3:細枝)")
    tree_curvature: bpy.props.FloatProperty(name="枝のうねり・曲がり度", default=0.6, min=0.0, max=1.0, description="幹や枝の自然なくねり・重力による垂れ下がり具合")
    tree_material_mode: bpy.props.EnumProperty(
        name="樹木マテリアル方式",
        items=[
            ('PROCEDURAL', "🎨 プロシージャルPBR (動画準拠)", "Wave Texture縦木目樹皮 ＆ 葉ごとのランダム色相・半透明シェーダー"),
            ('IMAGE_TEXTURE', "🖼️ 外部画像テクスチャ (Image Texture)", "Wood/Grassフォルダの画像ファイルを使用")
        ],
        default='PROCEDURAL',
        description="マテリアルの生成方式"
    )

    # Chair specific
    chair_type: bpy.props.EnumProperty(
        name="椅子タイプ",
        items=[
            ('OFFICE_TASK_CHAIR', "💺 近代オフィスチェア (Modern Office Task Chair)", "5本足キャスター＆ガスシリンダー＆エルゴノミクス背もたれ"),
            ('MODERN_SHELL_CHAIR', "🪑 北欧風シェルチェア (Modern Shell Chair)", "イームズ風一体成型シェル座面＆ハの字脚"),
            ('DINING_CHAIR', "💺 背もたれチェア (Dining Chair)", "クラシックな背もたれ付き椅子"),
            ('ARMCHAIR', "🛋️ アームチェア (Armchair)", "肘掛け付きアンティークチェア"),
            ('ROUND_STOOL', "⚪ 丸スツール (Round Stool)", "円形座面の腰掛け"),
            ('SQUARE_STOOL', "🔲 角スツール (Square Stool)", "四角座面の腰掛け")
        ],
        default='OFFICE_TASK_CHAIR'
    )
    chair_seat_style: bpy.props.EnumProperty(
        name="座面スタイル",
        items=[
            ('CUSHION', "🛋️ 革張り・ふっくらクッション (Cushion)", "ふくらみのある革張り/ファブリック座面"),
            ('WOOD_FLAT', "🪵 フラット木製座面 (Wood Flat)", "クラシックな木製座面")
        ],
        default='CUSHION'
    )
    chair_back_style: bpy.props.EnumProperty(
        name="背もたれ形状",
        items=[
            ('SOLID', "🪵 埋め込み装飾背板 (Solid Panel)", "隙間のない重厚なアンティーク彫刻背板"),
            ('SPINDLE', "🪑 縦格子スピンドル (Spindles)", "座面と笠木を直結するクラシック格子"),
            ('OVAL', "🔘 楕円メダリオン (Oval Medallion)", "貴族風の楕円背もたれ")
        ],
        default='SOLID'
    )
    chair_leg_layout: bpy.props.EnumProperty(
        name="脚の配置構造",
        items=[
            ('FOUR_LEGS', "🦿 4本脚 (Four Legs)", "スタンダードな4本脚"),
            ('PEDESTAL_ONE', "🏛️ 1本中央台座脚 (Pedestal)", "中央の太いろくろ挽き柱＋広がるフット"),
            ('X_CROSS', "⚔️ Xクロス交差脚 (X-Cross)", "交差したスタイリッシュなX脚"),
            ('TRIPOD_THREE', "📐 3本脚 (Tripod 3-Legs)", "丸スツール等に最適な三脚")
        ],
        default='FOUR_LEGS'
    )

    # Chest specific
    chest_tiers: bpy.props.IntProperty(name="引き出し段数", default=3, min=2, max=5, description="チェストの引き出し段数 (2段〜5段)")
    chest_handle_style: bpy.props.EnumProperty(
        name="取っ手金具",
        items=[
            ('RING', "リング金具 (Ring Handle)", "アンティークなドロップリング金具"),
            ('KNOB', "丸ノブ (Round Knob)", "クラシックな丸型つまみ"),
            ('BAR', "水平バー (Bar Handle)", "水平ハンドルバー")
        ],
        default='RING'
    )

    # Bed specific
    bed_size: bpy.props.EnumProperty(
        name="ベッドサイズ",
        items=[
            ('SINGLE', "シングル (Single: 1.2m)", "幅 1.2m のベッド"),
            ('DOUBLE', "ダブル (Double: 1.6m)", "幅 1.6m のベッド"),
            ('KING', "キング (King: 2.0m)", "幅 2.0m の広々ベッド")
        ],
        default='SINGLE'
    )

    # Bookshelf specific
    shelf_tiers: bpy.props.IntProperty(name="棚の段数", default=3, min=2, max=4, description="本棚の棚板段数 (2段, 3段, 4段)")
    column_ornament_style: bpy.props.EnumProperty(
        name="柱装飾",
        items=[
            ('ORNAMENTAL', "アンティーク・ろくろ挽き (Turned)", "ビーズ・リング・コーンを重ねたクラシック装飾柱"),
            ('TWISTED', "螺旋・ツイスト (Twisted)", "スパイラル状のひねり装飾柱"),
            ('REINFORCED', "補強台座付き (Reinforced)", "上下にキャピタル台座を持つ柱"),
            ('SIMPLE', "シンプル角柱/円柱 (Simple)", "クリーンなストレート柱")
        ],
        default='ORNAMENTAL'
    )

    # Table specific
    table_shape: bpy.props.EnumProperty(
        name="天板形状",
        items=[
            ('MODERN_DESK', "🖥️ 近代PCデスク (Modern PC Desk)", "すっきりとしたストレートモダン天板"),
            ('MONITOR_RISER_DESK', "🖥️ モニタースタンド付きデスク (Monitor Riser Desk)", "液晶ディスプレイ棚・ライザー付きPCデスク"),
            ('L_SHAPED_CORNER', "📐 L字スタジオデスク (L-Shaped Corner Desk)", "広々としたL字型コーナースタジオデスク"),
            ('RECTANGLE', "🔲 スタンダード四角 (Rectangle)", "標準の長方形天板"),
            ('ROUNDED_RECT', "🔘 角丸長方形 (Rounded Rect)", "四隅が滑らかに丸まった天板"),
            ('OVAL', "⬭ 楕円 (Oval / Ellipse)", "美しい楕円形天板")
        ],
        default='MODERN_DESK'
    )
    table_leg_style: bpy.props.EnumProperty(
        name="脚の形状",
        items=[
            ('STEEL_LOOP', "⬛ 口の字スチール脚 (Steel Loop Legs)", "スタイリッシュなブラックスチール角パイプ脚"),
            ('STEEL_PIPE', "🔩 丸スチールパイプ脚 (Steel Round Pipe)", "スリムな丸パイプ脚＋補強ビーム"),
            ('ORNAMENTAL', "アンティーク・ろくろ挽き (Turned)", "球体ビーズ・リング・コーンの4本脚"),
            ('TWISTED', "螺旋・ツイスト (Twisted)", "スパイラルひねりの4本脚"),
            ('REINFORCED', "補強台座付き (Reinforced)", "上下に段差リング・台座を持つ4本脚"),
            ('SIMPLE', "シンプル (Simple)", "プレーンな4本脚")
        ],
        default='STEEL_LOOP'
    )
    rand_furniture_style: bpy.props.BoolProperty(name="🎲 家具スタイルガチャ", default=True)

    grass_mode: bpy.props.EnumProperty(
        name="Grass Type",
        items=[
            ('MOUND', "🌿 草地ベース床 (Meadow Mound Slab)", "自然な緩やかな起伏を持つ草地スラブ（足場）"),
            ('TUFT', "🌾 草の束・草むら (Grass Tuft Clump)", "風に揺らすための十字クロス草メッシュ（ビルボード）")
        ],
        default='MOUND'
    )

    terrain_type: bpy.props.EnumProperty(
        name="地形タイプ (Terrain Type)",
        items=[
            ('MEADOW', "🌿 なだらかな草原 (Meadow)", "自然な丘陵起伏と緑豊かな草地・土の混在"),
            ('ROCKY', "🪨 岩盤露出地 (Rocky Ground)", "シャープな稜線起伏と岩盤・砂利・粗い土"),
            ('FLAT_DIRT', "🟫 平坦な土・グラウンド (Flat Dirt)", "緩やかな微細凹凸と乾燥した土肌")
        ],
        default='MEADOW'
    )

    uv_mapping_mode: bpy.props.EnumProperty(
        name="UV Mode",
        items=[
            ('FIT', "🔲 1枚全面フィット (Fit to Object)", "オブジェクトのサイズ全体に1枚絵としてフィット（反復ループなし）"),
            ('TILING', "🔁 タイル反復 (Tiling Repeat)", "レンガや敷石のようにテクスチャを反復リピート")
        ],
        default='FIT'
    )

    floor_shape: bpy.props.EnumProperty(
        name="Floor Shape",
        items=[
            ('COBBLESTONE', "🪨 ヨーロッパ風石畳 (Cobblestone)", "サコッシュ伊藤氏技法による1石ずつ立体化した本格石畳"),
            ('SQUARE', "🔲 正方形スラブ (Square)", "Clean flat square slab"),
            ('CIRCLE', "⚪ 円形・丸 (Circle / Round)", "Clean round circular slab / pedestal"),
            ('HEXAGON', "⬡ 六角形 (Hexagon)", "Hexagonal pavement tile"),
            ('HEX_PAVER', "⬡ 六角敷石 (Hex Paver)", "整然とした六角タイル舗装")
        ],
        default='COBBLESTONE'
    )

    wall_shape: bpy.props.EnumProperty(
        name="Wall Shape",
        items=[
            ('COBBLE_WALL', "🧱 古城の立体石積み壁 (Cobble Wall)", "不規則な石ブロックが立体的に飛び出す古城風石積み壁"),
            ('STRAIGHT', "🧱 直線壁 (Straight Wall)", "Clean straight stone wall"),
            ('TRIANGLE', "🔺 三角壁・切妻壁 (Triangle / Gable)", "Triangular gable wall for roofs & slopes"),
            ('L_SHAPE', "🧱 L字コーナー壁 (L-Corner Wall)", "L-shaped corner wall block"),
            ('CURVED', "🧱 円弧・カーブ壁 (Curved Wall)", "Curved arched wall segment")
        ],
        default='COBBLE_WALL'
    )

    cobble_stone_size: bpy.props.FloatProperty(
        name="石の大きさ (Stone Size)",
        default=0.35, min=0.1, max=1.2,
        description="敷石・石積みブロックの1石あたりの平均サイズ"
    )
    cobble_grout_depth: bpy.props.FloatProperty(
        name="目地の深さ (Grout Depth)",
        default=0.035, min=0.005, max=0.15,
        description="石と石の間の目地（溝）の深さ"
    )
    cobble_jitter: bpy.props.FloatProperty(
        name="不揃い・歪み度 (Stone Jitter)",
        default=0.45, min=0.0, max=1.0,
        description="石の傾き・高さのばらつき・不規則多角形化の強さ"
    )

    asset_name: bpy.props.StringProperty(name="Name", default="Rock_Asset")
    export_folder: bpy.props.StringProperty(name="Export Folder", subtype='DIR_PATH', default=r"Z:\MeshCreator\exports")

    rock_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ('JAGGED_CRAG', "🏔️ Jagged Crag (ごつごつ鋭岩)", "多面体スライスカットによる荒々しい鋭利な岩"),
            ('COLUMNAR_CLIFF', "🧱 Columnar Cliff (柱状断崖岩)", "水平・垂直の鋭角テラス段差を持つ巨岩"),
            ('VOLCANIC_SPIKE', "🌋 Volcanic Spike (溶岩・尖角岩)", "上に向かって尖るスパイク状の鋭利な岩"),
            ('FRACTURED', "🪨 Fractured (大破砕・巨岩)", "Heavily fractured rock with large broken chunks"),
            ('SHARP', "🔪 Sharp Slate (鋭利な割れ石)", "Chiseled slate rock"),
            ('BOULDER', "🥔 Boulder (丸岩・巨石)", "Weathered rounded massive boulder")
        ],
        default='JAGGED_CRAG'
    )
    rand_type: bpy.props.BoolProperty(name="🎲 形状ランダム", default=True)

    rock_palette: bpy.props.EnumProperty(
        name="Color Palette",
        items=[
            ('AUTO', "🎲 ランダム抽選 (Auto Random)", "Randomize rock palette per generation"),
            ('MOSSY_FOREST', "🌿 苔むした岩 (Mossy Forest)", "Dark grey with top-side green moss"),
            ('RED_SANDSTONE', "🏜️ 赤砂岩 (Red Sandstone)", "Vibrant terracotta & canyon strata"),
            ('GRANITE', "🪨 花崗岩 (Speckled Granite)", "White, black & mineral flecked stone"),
            ('VOLCANIC_BASALT', "🌋 溶岩玄武岩 (Volcanic Basalt)", "Charcoal black with sulfur & ash accents"),
            ('WHITE_LIMESTONE', "🏔️ 白石灰岩 (White Limestone)", "Bright cream limestone with water streaks"),
            ('SLATE_BLUE', "💎 青粘板岩 (Slate Blue)", "Deep slate blue with quartz veins")
        ],
        default='AUTO'
    )

    size_x: bpy.props.FloatProperty(name="X (幅/スパン)", default=1.8, min=0.2, max=20.0)
    size_y: bpy.props.FloatProperty(name="Y (厚み/奥行)", default=1.0, min=0.1, max=20.0)
    size_z: bpy.props.FloatProperty(name="Z (高さ)", default=0.78, min=0.05, max=20.0)
    rand_dimensions: bpy.props.BoolProperty(name="🎲 サイズランダム", default=True)

    roughness: bpy.props.FloatProperty(name="Roughness (粗さ)", default=0.75, min=0.0, max=2.0)
    chisel_strength: bpy.props.FloatProperty(name="Chisel (削り角)", default=0.85, min=0.0, max=1.5)
    rand_surface: bpy.props.BoolProperty(name="🎲 粗さランダム", default=True)

    big_chunk_cuts: bpy.props.IntProperty(name="Big Chunks (大きな欠け数)", default=2, min=0, max=5)
    crack_depth: bpy.props.FloatProperty(name="Crack Depth (亀裂・傷の深さ)", default=0.6, min=0.0, max=1.5)
    floor_crack_count: bpy.props.IntProperty(name="亀裂・傷の箇所数", default=6, min=0, max=20)
    rand_fractures: bpy.props.BoolProperty(name="🎲 亀裂ランダム", default=True)

    create_debris: bpy.props.BoolProperty(name="Create Debris (周囲の破片・小石)", default=False)
    debris_count: bpy.props.IntProperty(name="Shard Count", default=4, min=1, max=20)

    texture_folder: bpy.props.StringProperty(name="Texture Folder", subtype='DIR_PATH', default=r"Z:\MeshCreator\textures\Rock")
    use_folder_texture: bpy.props.BoolProperty(name="Use Folder Textures", default=True)
    rand_texture: bpy.props.BoolProperty(name="🎲 テクスチャをランダム抽選", default=True)
    selected_texture: bpy.props.EnumProperty(name="Select Texture", items=get_texture_enum_items)
    texture_tiling: bpy.props.FloatProperty(name="Tiling (リピート倍率)", default=1.0, min=0.1, max=10.0)

    detail_level: bpy.props.IntProperty(name="Quality", default=2, min=1, max=3)
    seed: bpy.props.IntProperty(name="Seed", default=42, min=0)
    auto_random: bpy.props.BoolProperty(name="Auto Random", default=True)

    grass_density: bpy.props.IntProperty(
        name="Grass Density", default=5000, min=100, max=50000,
        description="Hair Particle の本数"
    )
    grass_undulation: bpy.props.FloatProperty(
        name="Undulation", default=0.30, min=0.0, max=2.0,
        description="地面の起伏強さ"
    )
    grass_weight_noise: bpy.props.FloatProperty(
        name="Weight Noise Scale", default=2.5, min=0.1, max=10.0,
        description="ウェイトペイントのノイズスケール"
    )

    enable_displacement: bpy.props.BoolProperty(
        name="3D凹凸立体化 (Displacement)",
        default=True,
        description="テクスチャのハイトマップやノイズで実際のメッシュ表面を立体的に凸凹変形"
    )
    displacement_strength: bpy.props.FloatProperty(
        name="凹凸の強さ (Strength)",
        default=0.15, min=0.0, max=1.0,
        description="ディスプレイスメントの凹凸押し出し量"
    )
    displacement_midlevel: bpy.props.FloatProperty(
        name="基準高さ (Midlevel)",
        default=0.5, min=0.0, max=1.0,
        description="ディスプレイスメントの基準高さ (0.5 = 中間)"
    )
    displacement_subdiv: bpy.props.IntProperty(
        name="メッシュ細分化 (Subdivisions)",
        default=2, min=0, max=4,
        description="リアルジオメトリ凹凸のための細分化レベル"
    )
    apply_disp_to_mesh: bpy.props.BoolProperty(
        name="メッシュへベイク (Apply to Mesh)",
        default=True,
        description="Displace モディファイアを適用してUnity/FBXエクスポート可能な実メッシュにする"
    )

    bake_resolution: bpy.props.EnumProperty(
        name="ベイク解像度",
        items=[
            ('512', "512 x 512 (軽量)", "モバイル・ローポリ向け"),
            ('1024', "1024 x 1024 (標準・推奨)", "Unity標準品質"),
            ('2048', "2048 x 2048 (高精細)", "近景・ヒーローアセット向け")
        ],
        default='1024'
    )
    auto_bake_on_export: bpy.props.BoolProperty(
        name="FBX出力時に自動ベイク (Unityベタ塗り防止)",
        default=True,
        description="プロシージャルマテリアルをBaseColor/Normal画像に自動焼き付けしてFBXと同封出力"
    )
    bake_diffuse: bpy.props.BoolProperty(name="BaseColor (色・木目・草)", default=True)
    bake_normal: bpy.props.BoolProperty(name="Normal Map (凹凸法線)", default=True)

    # ── FENCE Properties ──
    fence_type: bpy.props.EnumProperty(
        name="Fence Type",
        items=[
            ('POST_AND_RAIL', "牧場横木 (Post & Rail)", "シンプルな2〜3段横木のスタンダード柵"),
            ('PICKET', "先端尖り (Picket Fence)", "先端山型の縦板が並ぶピケットフェンス"),
            ('CROSS_BRACE', "X字筋交い (Cross Brace)", "X字斜め補強された頑丈な防護柵"),
            ('PALISADE', "丸太砦・防壁 (Log Palisade)", "先端を尖らせた丸太の密集防壁＋結束ロープ")
        ],
        default='POST_AND_RAIL'
    )
    fence_rails_count: bpy.props.IntProperty(
        name="Rails Count", default=2, min=1, max=4,
        description="横木の段数 (Post & Rail用)"
    )
    fence_post_spacing: bpy.props.FloatProperty(
        name="Post Spacing", default=1.8, min=0.8, max=4.0,
        description="支柱の間隔 (m)"
    )
    fence_decay_jitter: bpy.props.FloatProperty(
        name="経年劣化・歪み (Decay Jitter)", default=0.03, min=0.0, max=0.12,
        description="支柱や板の微細な傾き・手作り感の揺らぎ"
    )

    # ── BUSH & SHRUB Properties ──
    bush_type: bpy.props.EnumProperty(
        name="Bush Type",
        items=[
            ('ROUND_BUSH', "丸型低木 (Round Bush)", "ふんわり丸型ドーム低木（庭園・公園・森）"),
            ('WILD_SHRUB', "野生の藪 (Wild Shrub)", "細枝が四方に広がる自然な茂み・雑木"),
            ('FERN_CLUMP', "シダの株 (Fern Clump)", "放射状にアーチを描く羽状複葉のシダ"),
            ('HEDGE_ROW', "生垣ブロック (Hedge Row)", "境界・道沿いに長く連なる生垣")
        ],
        default='ROUND_BUSH'
    )
    bush_foliage_style: bpy.props.EnumProperty(
        name="Foliage Style",
        items=[
            ('LEAF_CARDS', "葉クラスタカード (Leaf Cards)", "ゲーム用最適化（十字カード＆球状法線）"),
            ('VOLUME_CANOPY', "ふんわりボリューム (Volume Canopy)", "アニメ・スタイライズド用有機的Icosphere")
        ],
        default='LEAF_CARDS'
    )
    bush_density: bpy.props.IntProperty(
        name="Density (密度)", default=18, min=4, max=50,
        description="葉カード/枝の散布枚数"
    )
    bush_leaf_size: bpy.props.FloatProperty(
        name="Leaf Size (葉サイズ)", default=0.35, min=0.15, max=0.8,
        description="葉カードのサイズ (m)"
    )
    bush_include_fiddleheads: bpy.props.BoolProperty(
        name="ゼンマイ新芽 (Fiddleheads)",
        default=True,
        description="シダ植物の中心からクルリと巻いた新芽（ゼンマイ）を生やす"
    )

    # ── PILLAR & COLUMN Properties ──
    pillar_type: bpy.props.EnumProperty(
        name="Pillar Type",
        items=[
            ('CLASSIC_FLUTED', "🏛️ 神殿円柱 (Classic Fluted)", "16~24本フルーティング縦溝彫り＋エンタシス胴張り＋クラシック柱頭＆基壇"),
            ('GOTHIC_CLUSTERED', "⛪ ゴシック束ね柱 (Gothic Clustered)", "中央主柱＋小柱Colonnettes束ね構造＋結束リング"),
            ('STONE_DRUM', "🪨 ドラム石積み柱 (Stone Drum)", "円盤状の石ブロック積み重ね＋深い目地溝＋風化ジッター"),
            ('TWISTED_SOLOMONIC', "🌀 ソロモン螺旋柱 (Twisted Solomonic)", "バロック様式の優美な螺旋ねじれ装飾柱"),
            ('SQUARE_MONUMENT', "🏛️ 西洋角柱・モニュメント (Square Monument)", "面取り多段角柱＋コーニス天頂装飾")
        ],
        default='CLASSIC_FLUTED'
    )
    pillar_mat_type: bpy.props.EnumProperty(
        name="Pillar Material",
        items=[
            ('MARBLE', "白大理石 (Polished Marble)", "高級感のある筋模様と光沢＋足元の微小汚れ"),
            ('ANCIENT_STONE', "古代砂岩 (Ancient Sandstone)", "風化した砂利感と微細バンプ＋足元の土汚れ"),
            ('MOSSY_RUINS', "苔むした遺跡 (Mossy Ruins)", "足元から這い上がる緑の苔と風化石")
        ],
        default='MARBLE'
    )
    pillar_height: bpy.props.FloatProperty(
        name="Height (柱の高さ)", default=4.0, min=1.0, max=20.0,
        description="柱の全高 (m)"
    )
    pillar_radius: bpy.props.FloatProperty(
        name="Radius (柱の太さ)", default=0.4, min=0.1, max=3.0,
        description="主柱の半径 (m)"
    )
    pillar_colonnettes: bpy.props.IntProperty(
        name="小柱の数 (Colonnettes)", default=6, min=4, max=12,
        description="ゴシック束ね柱の周囲小柱数"
    )
    pillar_flutes: bpy.props.IntProperty(
        name="縦溝の数 (Flutes)", default=16, min=8, max=32,
        description="神殿円柱の縦溝（フルーティング）数"
    )
    pillar_entasis: bpy.props.FloatProperty(
        name="エンタシス (Entasis)", default=0.08, min=0.0, max=0.25,
        description="柱中央の滑らかな膨らみ度"
    )

    # ── TELESCOPE Properties ──
    telescope_style: bpy.props.EnumProperty(
        name="Telescope Style",
        items=[
            ('MODERN_REFRACTOR', "🔭 近代屈折式 (Modern Refractor)", "王道のロング鏡筒＋先太りフード＋2段伸縮アルミ三脚"),
            ('ANTIQUE_BRASS', "🏛️ アンティーク真鍮 (Antique Brass)", "磨き真鍮ゴールド＋扇形ギア＋優雅な3本脚卓上スタンド"),
            ('SMART_DIGITAL', "🚀 最先端スマート望遠鏡 (Smart Digital)", "未来派シリンダー＋十字スパイダー＋LED発光＋カーボン三脚"),
            ('CASSEGRAIN_POP', "🎨 カセグレン・ポップ (Cassegrain Pop)", "ずんぐり太短鏡筒＋前面補正板＆副鏡＋ティールブルー"),
            ('TACTICAL_COMPACT', "📸 タクティカル卓上 (Tactical Compact)", "太鏡筒＋ローレット溝フード＋3ウェイ雲台＋3段レバー脚")
        ],
        default='MODERN_REFRACTOR'
    )
    telescope_elevation_angle: bpy.props.FloatProperty(
        name="仰角 (Elevation)", default=25.0, min=0.0, max=90.0,
        description="鏡筒の上下チルト角度 (度)"
    )
    telescope_azimuth_angle: bpy.props.FloatProperty(
        name="方位角 (Azimuth)", default=45.0, min=0.0, max=360.0,
        description="架台の水平回転角度 (度)"
    )
    telescope_tripod_height: bpy.props.FloatProperty(
        name="三脚の高さ (Tripod Height)", default=1.0, min=0.3, max=1.8,
        description="三脚の全高 (m)"
    )
    telescope_tube_length: bpy.props.FloatProperty(
        name="鏡筒の長さ (Tube Length)", default=0.75, min=0.3, max=1.5,
        description="望遠鏡の鏡筒の長さ (m)"
    )

    # ── IMAGE DISPLACE STUDIO Properties ──
    img_disp_path: bpy.props.StringProperty(
        name="画像ファイル", subtype='FILE_PATH', default="",
        description="立体化する2D画像 (PNG/JPG/EXR)"
    )
    img_disp_shape: bpy.props.EnumProperty(
        name="立体形状",
        items=[
            ('SLAB_RELIEF', "🔲 レリーフ石板 (Slab Relief)", "アスペクト比同期の四角形レリーフ・額縁"),
            ('COIN_MEDAL', "🔘 コイン/メダル (Coin Medal)", "円形コイン・メダル・紋章ディスク")
        ],
        default='SLAB_RELIEF'
    )
    img_disp_subdiv_level: bpy.props.IntProperty(
        name="細分化レベル (Subdiv)", default=1, min=0, max=4,
        update=update_subdiv_realtime,
        description="メッシュの細分化解像度レベル（リアルタイム連動）"
    )
    img_disp_strength: bpy.props.FloatProperty(
        name="隆起の強さ (Strength)", default=0.20, min=-3.0, max=3.0,
        update=update_displace_realtime,
        description="Displace の凸凹の深さ・強さ（リアルタイム連動）"
    )
    img_disp_midlevel: bpy.props.FloatProperty(
        name="基準面 (Midlevel)", default=0.50, min=0.0, max=1.0,
        update=update_displace_realtime,
        description="基準面の高さレベル（リアルタイム連動）"
    )
    img_disp_smooth_factor: bpy.props.FloatProperty(
        name="スムース強度 (Factor)", default=0.30, min=0.0, max=1.0,
        update=update_smooth_realtime,
        description="ジャギー・等高線段差を滑らかに溶かす強度（リアルタイム連動）"
    )
    img_disp_smooth_iter: bpy.props.IntProperty(
        name="スムース反復回数 (Iterations)", default=2, min=1, max=10,
        update=update_smooth_realtime,
        description="スムースの反復適用回数（リアルタイム連動）"
    )
    img_disp_solidify_thickness: bpy.props.FloatProperty(
        name="面(立方体)の厚み (Thickness)", default=0.15, min=0.01, max=2.0,
        update=update_solidify_realtime,
        description="直方体ブロック・コインの厚み（リアルタイム連動）"
    )
    img_disp_block_style: bpy.props.EnumProperty(
        name="立体ブロック様式",
        items=[
            ('SOLID_SLAB', "🧱 直方体ブロック (Solid Slab)", "均一な厚みを持つソリッド直方体ブロック"),
            ('VOXEL_BLOCKS', "🧊 キューブボクセル (Voxel Blocks)", "マインクラフト・ドット絵調の立方体キューブ集合体")
        ],
        default='SOLID_SLAB',
        update=update_solidify_realtime
    )
    img_disp_enable_cutout: bpy.props.BoolProperty(
        name="✂️ 同階層を型抜き (Cutout)", default=False,
        update=update_cutout_realtime,
        description="平坦な背景面をリアルタイム削除してレリーフ図柄だけを型抜きする"
    )
    img_disp_cutout_threshold: bpy.props.FloatProperty(
        name="型抜き閾値 (Threshold)", default=0.02, min=-1.0, max=1.0,
        update=update_cutout_realtime,
        description="この高さ以下の背景ポリゴンをリアルタイム削除（リアルタイム連動）"
    )
    img_disp_cutout_invert: bpy.props.BoolProperty(
        name="型抜き反転 (Invert)", default=False,
        update=update_cutout_realtime,
        description="型抜きの対象を反転（浮き彫り/彫り込み）"
    )
    img_disp_enable_color_cutout: bpy.props.BoolProperty(
        name="🎨 指定色で型抜き (Color Cutout)", default=False,
        update=update_cutout_realtime,
        description="指定した背景色や透明部分をリアルタイムに型抜き（消去）する"
    )
    img_disp_key_color: bpy.props.FloatVectorProperty(
        name="対象色 (Key Color)", subtype='COLOR', size=4,
        default=(1.0, 1.0, 1.0, 1.0), min=0.0, max=1.0,
        update=update_cutout_realtime,
        description="型抜き（消去）する背景色"
    )
    img_disp_color_tolerance: bpy.props.FloatProperty(
        name="色の許容差 (Tolerance)", default=0.15, min=0.0, max=1.0,
        update=update_cutout_realtime,
        description="指定色との類似度の許容範囲（大きいほど広い色を型抜き）"
    )
    img_disp_cutout_mode: bpy.props.EnumProperty(
        name="型抜き併用モード",
        items=[
            ('OR', "色 または 高さ (OR)", "指定色に近い、または高さが低い部分を消去"),
            ('AND', "色 かつ 高さ (AND)", "指定色であり、かつ高さが低い部分を消去"),
            ('COLOR_ONLY', "色抜きのみ (Color Only)", "画像の色差・透明度だけで型抜き"),
            ('HEIGHT_ONLY', "高さ型抜きのみ (Height Only)", "高さ閾値だけで型抜き")
        ],
        default='OR',
        update=update_cutout_realtime
    )
    img_disp_resolution: bpy.props.IntProperty(
        name="細分化解像度 (Resolution)", default=96, min=16, max=256,
        description="ベースグリッドの分割解像度"
    )
    img_disp_close_mesh: bpy.props.BoolProperty(
        name="裏面底面を密閉 (Closed Solid)", default=True,
        description="裏面・側面を閉じてUnity/UE用の完全ソリッドにする"
    )
    img_disp_decimate_ratio: bpy.props.FloatProperty(
        name="軽量化比率 (Decimate)", default=0.5, min=0.05, max=1.0,
        description="ゲーム向けポリゴン削減率 (1.0で削減なし)"
    )
    img_disp_planar_angle: bpy.props.FloatProperty(
        name="平面溶解の角度 (Angle)", default=2.5, min=0.1, max=20.0,
        description="この角度以内の平坦な面・底面・側面にある不要な頂点をすべて溶解・消去 (度)"
    )
    img_disp_mat_style: bpy.props.EnumProperty(
        name="マテリアル質感",
        items=[
            ('ORIGINAL_COLOR', "🎨 元画像カラー (Original Color)", "画像のカラーテクスチャをそのまま表面にマッピング"),
            ('MARBLE', "🏛️ 白大理石 (Marble)", "高級感のある筋模様と光沢"),
            ('ANCIENT_STONE', "🪨 古代砂岩 (Ancient Sandstone)", "風化した砂粒感と土汚れ"),
            ('MOSSY_RUINS', "🌿 苔むした遺跡 (Mossy Ruins)", "足元から這い上がる緑苔")
        ],
        default='ORIGINAL_COLOR'
    )

    # ── FLASK & POTION STUDIO Properties ──
    flask_shape: bpy.props.EnumProperty(
        name="フラスコ形状",
        items=[
            ('CONICAL', "🔺 三角フラスコ (Erlenmeyer Flask)", "実験室やポーション定番の錐形フラスコ"),
            ('ROUND', "🔮 丸底ポーション (Round Flask)", "ファンタジーRPG定番の球形ポーションボトル")
        ],
        default='CONICAL'
    )
    flask_has_cork: bpy.props.BoolProperty(
        name="コルク栓を付ける", default=True,
        description="フラスコの口元に木製コルク栓を生成"
    )
    flask_tilt: bpy.props.FloatProperty(
        name="容器の傾き (Tilt °)", default=0.0, min=-45.0, max=45.0,
        description="フラスコ容器自体の傾き角度 (度)"
    )
    liquid_level: bpy.props.FloatProperty(
        name="液面の高さ (Level)", default=0.55, min=0.10, max=0.90,
        description="容器内部の液体の量・高さ比率"
    )
    liquid_tilt: bpy.props.FloatProperty(
        name="液面の傾き補正 (Tilt °)", default=0.0, min=-45.0, max=45.0,
        description="容器の傾きに合わせて液面を水平に保つ微調整角度 (度)"
    )
    liquid_surface_noise: bpy.props.FloatProperty(
        name="液面の波・表面歪み", default=0.02, min=0.0, max=0.10,
        description="静止画でもトロンとした表面張力やゆらぎを出す微小ノイズ歪み"
    )
    liquid_color: bpy.props.FloatVectorProperty(
        name="液体の色", subtype='COLOR', size=4,
        default=(0.9, 0.15, 0.25, 1.0), min=0.0, max=1.0,
        description="ポーション液体のカラー"
    )
    liquid_glow: bpy.props.FloatProperty(
        name="液体の発光 (Glow)", default=0.25, min=0.0, max=2.0,
        description="暗闇でほんのり光るファンタジーポーションの発光強度"
    )
    flask_scale: bpy.props.FloatProperty(
        name="スケール (Scale)", default=1.0, min=0.1, max=5.0,
        description="フラスコの全体サイズ倍率"
    )

    # ── WALL CLOCK Properties ──
    clock_shape: bpy.props.EnumProperty(
        name="外枠形状",
        items=[
            ('ROUND', "⚪ クラシック丸型 (Classic Round)", "円形モールディング木製/真鍮フレーム"),
            ('OCTAGON', "🛑 八角形 (Vintage Octagon)", "アンティーク洋館・ボンボン時計風の八角形フレーム")
        ],
        default='ROUND'
    )
    clock_style: bpy.props.EnumProperty(
        name="マテリアル質感",
        items=[
            ('ANTIQUE_WOOD', "🪵 アンティーク木製 (Antique Mahogany)", "高級感のある濃色マホガニー・ウォールナット"),
            ('VINTAGE_BRASS', "🎷 ヴィンテージ真鍮 (Vintage Brass)", "経年変化の味わいがあるアンティークゴールド真鍮"),
            ('MODERN_BLACK', "🖤 モダンブラック (Modern Black)", "シックな黒フレーム ＆ アイボリー文字盤")
        ],
        default='ANTIQUE_WOOD'
    )
    clock_time_hour: bpy.props.IntProperty(
        name="時 (Hour)", default=10, min=1, max=12,
        description="時針が指す時刻（1〜12）"
    )
    clock_time_minute: bpy.props.IntProperty(
        name="分 (Minute)", default=10, min=0, max=59,
        description="分針が指す時刻（0〜59分）"
    )
    clock_show_seconds: bpy.props.BoolProperty(
        name="秒針を表示", default=True,
        description="細身の秒針とセンターピンを表示"
    )
    clock_show_glass: bpy.props.BoolProperty(
        name="前面風防ガラス", default=True,
        description="文字盤を覆うドーム型透明ガラス"
    )
    clock_diameter: bpy.props.FloatProperty(
        name="直径 (m)", default=0.45, min=0.15, max=2.0,
        description="壁掛け時計の直径サイズ (m)"
    )

    # ── SPEAKER Properties ──
    speaker_style: bpy.props.EnumProperty(
        name="スピーカー様式",
        items=[
            ('STUDIO_BLACK', "🖤 スタジオモニター黒 (Studio Monitor Black)", "定番のマットブラックキャビネット"),
            ('STUDIO_WHITE', "🤍 スタジオモニター白 (Studio Monitor White)", "スタイリッシュなオールホワイト"),
            ('VINTAGE_WOOD', "🪵 クラシック木製 (Vintage Walnut)", "高級オーディオ風ウォールナット木目")
        ],
        default='STUDIO_BLACK'
    )
    speaker_cone_color: bpy.props.EnumProperty(
        name="ウーファーコーン色",
        items=[
            ('WHITE_CONE', "⚪ ホワイトコーン (Yamaha HS調)", "視認性の高いクラシック白コーン"),
            ('BLACK_CONE', "⚫ ブラックコーン (Polypropylene)", "シックな同色ブラック"),
            ('YELLOW_KEVLAR', "🟡 イエローケブラー (KRK調)", "高剛性アラミド繊維調の黄色コーン")
        ],
        default='WHITE_CONE'
    )
    speaker_has_grille: bpy.props.BoolProperty(
        name="保護サランネット (Grille)", default=False,
        description="前面を覆う保護布メッシュグリル"
    )
    speaker_led_color: bpy.props.FloatVectorProperty(
        name="電源LED色", subtype='COLOR', size=4,
        default=(0.1, 0.6, 1.0, 1.0), min=0.0, max=1.0,
        description="電源ONを示す発光LEDの色"
    )
    speaker_scale: bpy.props.FloatProperty(
        name="スケール (Scale)", default=1.0, min=0.2, max=5.0,
        description="スピーカー全体のサイズ倍率"
    )

    # ── PRACTICAL FENCE PRESET Properties ──
    fence_preset_type: bpy.props.EnumProperty(
        name="フェンス様式",
        items=[
            ('WIRE_CROSS', "➕ 十字の鉄線 (Grid Wire)", "公園・空港・高速沿いの直交ワイヤー格子フェンス（画像1準拠）"),
            ('WIRE_X', "❌ X字の鉄線 (Chain-Link)", "グラウンド・立ち入り禁止区域の45度斜め金網フェンス（画像3準拠）"),
            ('WOOD_HORIZ', "🪵 木板打ち付け・横 (Horizontal Slat)", "横方向にスリットを空けて打ち付けた目隠しウッドフェンス（画像2準拠）"),
            ('WOOD_VERT', "🪵 木板打ち付け・縦 (Vertical Picket)", "縦方向に整然と並べたウッドフェンス")
        ],
        default='WIRE_CROSS'
    )
    fence_length: bpy.props.FloatProperty(
        name="全長 (Length)", default=4.0, min=1.0, max=50.0,
        description="フェンスの全長 (m)"
    )
    fence_height: bpy.props.FloatProperty(
        name="高さ (Height)", default=1.5, min=0.5, max=5.0,
        description="フェンスの全高 (m)"
    )
    fence_post_spacing: bpy.props.FloatProperty(
        name="支柱スパン (Span)", default=2.0, min=0.8, max=5.0,
        description="支柱と支柱の間隔 (m)"
    )
    fence_slat_gap: bpy.props.FloatProperty(
        name="木板の隙間 (Gap)", default=0.015, min=0.005, max=0.10,
        description="木板同士のスリット隙間 (m)"
    )
    fence_scale: bpy.props.FloatProperty(
        name="スケール (Scale)", default=1.0, min=0.2, max=5.0,
        description="全体のサイズ倍率"
    )

    # ── FENCE COLOR & MATERIAL Properties ──
    fence_color_preset: bpy.props.EnumProperty(
        name="カラーパレット",
        items=[
            ('PRESET_DEFAULT', "🎨 スタイル推奨色", "各フェンス様式の標準カラー（黒/緑/木）"),
            ('SILVER', "⚪ 亜鉛メッキシルバー", "スチール製・金属感のある銀色パイプ＆ワイヤー"),
            ('BLACK', "⚫ パウダーコート黒", "シックで高級感のあるマットブラック"),
            ('WHITE', "🤍 安全ホワイト", "公園・学校・住宅街の白塗装"),
            ('GREEN', "🟢 ビニール被覆グリーン", "グラウンド・テニスコート用防錆緑"),
            ('WOOD_BROWN', "🪵 ウォールナット木目", "落ち着いた深みのあるダークブラウン"),
            ('CUSTOM', "🛠️ カスタム色指定", "支柱と鉄線/木板の色を個別に自由に調整")
        ],
        default='PRESET_DEFAULT',
        update=update_fence_color_preset
    )
    fence_frame_color: bpy.props.FloatVectorProperty(
        name="支柱・フレーム色",
        subtype='COLOR',
        size=4,
        default=(0.05, 0.05, 0.05, 1.0),
        min=0.0, max=1.0,
        description="支柱パイプおよび外枠レールの色",
        update=update_fence_live_color
    )
    fence_body_color: bpy.props.FloatVectorProperty(
        name="鉄線・金網・木板色",
        subtype='COLOR',
        size=4,
        default=(0.06, 0.06, 0.06, 1.0),
        min=0.0, max=1.0,
        description="鉄線格子、チェーンリンク金網、または木板スラットの色",
        update=update_fence_live_color
    )
    fence_metallic: bpy.props.FloatProperty(
        name="金属感 (Metallic)",
        default=0.25, min=0.0, max=1.0,
        description="マテリアルの金属反射度",
        update=update_fence_live_color
    )
    fence_roughness: bpy.props.FloatProperty(
        name="粗さ (Roughness)",
        default=0.35, min=0.0, max=1.0,
        description="マテリアル表面の微細な粗さ・ツヤ",
        update=update_fence_live_color
    )

    # ── WOOD FENCE REALISM & WEATHERING Properties ──
    fence_wood_top_style: bpy.props.EnumProperty(
        name="上部形状スタイル",
        items=[
            ('POINTED', "🔺 先端尖り (Pointed / Picket)", "ピケット風のクラシックな山型45度カット"),
            ('ROUNDED', "⚪ 丸型アーチ (Rounded / Dome)", "柔らかく親しみやすい半円ドームカット"),
            ('DOG_EAR', "🐕 ドッグイヤー (Dog-Ear)", "欧米フェンス定番の左右45度角落とし"),
            ('FLAT', "⬛ 直線平ら (Square / Flat)", "直線スクエアカット")
        ],
        default='POINTED',
        description="木板上端のカット形状（尖り・丸み・ドッグイヤー・平ら）"
    )
    fence_wood_jitter: bpy.props.FloatProperty(
        name="ゆがみ・反り (Warp & Jitter)",
        default=0.35, min=0.0, max=1.0,
        description="板ごとの厚みムラ、前後の段差、微細な傾きの度合い（揃いすぎを解消）"
    )
    fence_wood_wear: bpy.props.FloatProperty(
        name="角欠け・劣化 (Edge Chips)",
        default=0.25, min=0.0, max=1.0,
        description="板の角やエッジに現れる経年劣化・角欠けの度合い"
    )
    fence_wood_weathering: bpy.props.FloatProperty(
        name="木目・汚し (Wood Weathering)",
        default=0.40, min=0.0, max=1.0,
        description="プロシージャル木目の年輪感および風化・雨だれ汚れの度合い",
        update=update_fence_live_color
    )

    # ── NATURE BIOME SCATTER Properties ──
    biome_type: bpy.props.EnumProperty(
        name="バイオーム種別",
        items=[
            ('MEADOW', "🌿 なだらかな野原 (Meadow Grassland)", "草株＋クローバー＋シダが広がる明るい草原"),
            ('FOREST_FLOOR', "🌲 鬱蒼とした森林の地面 (Forest Undergrowth)", "シダ群生＋低木＋苔むした小石が豊かな林床"),
            ('ROCKY_WASTELAND', "🪨 岩場・荒野 (Rocky Wasteland)", "岩石＋疎らな草株＋小低木が散らばる乾燥地")
        ],
        default='MEADOW',
        description="散布する植物と地面のバイオーム生態系プリセット"
    )
    biome_density: bpy.props.FloatProperty(
        name="散布密度 (Density)",
        default=45.0, min=5.0, max=150.0,
        description="地面1平方メートルあたりの散布ポイント密度（Poisson Disk分布）"
    )
    biome_min_dist: bpy.props.FloatProperty(
        name="最小間隔 (Min Distance)",
        default=0.14, min=0.04, max=0.8,
        description="植物同士のポリゴン重なりを防止する最小離隔距離"
    )
    biome_include_fern: bpy.props.BoolProperty(
        name="シダ・新芽を含む",
        default=True,
        description="羽状複葉とゼンマイ新芽を持つリアルシダ株を混入"
    )
    biome_include_shrub: bpy.props.BoolProperty(
        name="小低木を含む",
        default=True,
        description="立体広葉を持つ小低木・藪をアクセントとして混入"
    )
    biome_include_pebble: bpy.props.BoolProperty(
        name="小石を含む",
        default=True,
        description="地面に自然なローポリ丸小石を点在"
    )
    biome_terrain_size: bpy.props.FloatProperty(
        name="テレイン規模 (Size)",
        default=10.0, min=2.0, max=50.0,
        description="生成する地面テレインの一辺の長さ（メートル）"
    )
    biome_undulation: bpy.props.FloatProperty(
        name="地面の起伏 (Undulation)",
        default=0.45, min=0.0, max=2.0,
        description="FBMフラクタルによる地面の高低差・うねりの強さ"
    )

    # ── CASTLE WALL (Stone Scatter) Properties ──
    castle_wall_shape: bpy.props.EnumProperty(
        name="城壁形状",
        items=[
            ('RANDOM', "🎲 ランダム形状 (Random Shape)", "直線・L字・塔・折れ曲がり・城門等を自動抽選"),
            ('STRAIGHT', "⬛ 直線城壁 (Straight Wall)", "中世城塞の標準的なカーテンウォール"),
            ('BATTLEMENT', "🛡️ 銃眼胸壁 (Battlement / Parapet)", "凸凹の戦闘用狭間（銃眼）を持つ防衛城壁"),
            ('TOWER_CURVED', "🗼 監視塔・円弧壁 (Tower / Curved)", "半円柱・円形タワーの強固な曲面石壁"),
            ('CORNER_L', "🧱 L字コーナー壁 (Corner Bastion)", "90度コーナーの要塞堡塁壁"),
            ('CRANK_Z', "⚡ クランク折れ曲がり壁 (Crank / Z-Wall)", "段差・ジグザグの要塞防衛壁"),
            ('GATE_ARCH', "⛩️ 城門アーチ壁 (Gate Arch)", "アーチ開口部を持つ通行用城門壁")
        ],
        default='STRAIGHT',
        description="城壁・石垣の基礎構造形状"
    )
    castle_wall_style: bpy.props.EnumProperty(
        name="石積み様式",
        items=[
            ('ASHLAR', "切石積み (Ashlar Blocks)", "整然と手削りされた重厚な角ブロック石積み"),
            ('RUBBLE', "野面・乱積み丸石 (Rubble / Cobble)", "自然な角丸の石を巧みに組んだ野趣あふれる古城石垣"),
            ('SLATE', "薄板スレート積み (Dry Stone / Slate)", "薄く平たい板石を幾重にも積み重ねた石垣"),
            ('CYCLOPEAN', "巨石積み (Cyclopean / Megalith)", "巨大で不揃いな巨石が噛み合う古代・要塞石垣")
        ],
        default='ASHLAR',
        description="散布する石材ブロックの加工様式"
    )
    castle_wall_stone_aspect: bpy.props.EnumProperty(
        name="石材プロポーション",
        items=[
            ('STANDARD', "標準ブロック (Standard)", "中世城壁の標準的な比率 (幅:高=2:1)"),
            ('WIDE', "横長切石 (Wide Ashlar)", "横幅が広いワイドな長方形ブロック (幅:高=3:1)"),
            ('SQUARE', "正方形・角石 (Square Block)", "縦横比が正方形に近い厚手の石材"),
            ('FLAT', "極薄スレート (Flat Slab)", "薄く平べったい積層板石 (幅:高=4:1)")
        ],
        default='STANDARD',
        description="石材ブロック自体の縦横比プロポーション"
    )
    castle_wall_stone_roundness: bpy.props.FloatProperty(
        name="石の丸み・面取り (Roundness)",
        default=0.035, min=0.005, max=0.15,
        description="石材ブロックの角の面取り・丸みの強さ"
    )
    castle_wall_stone_chipping: bpy.props.FloatProperty(
        name="チゼル欠け・荒さ (Chipping)",
        default=0.016, min=0.0, max=0.06,
        description="手削りによる石材表面の微小な欠け・チゼル凹凸"
    )
    castle_wall_randomize_dimensions: bpy.props.BoolProperty(
        name="Re-Roll時に寸法もランダム化",
        default=False,
        description="再抽選時に壁の長さ・高さ・厚みも自動でバリエーション生成"
    )
    castle_wall_length: bpy.props.FloatProperty(
        name="壁の長さ (Length)",
        default=6.0, min=2.0, max=50.0,
        description="城壁の全長（メートル）"
    )
    castle_wall_height: bpy.props.FloatProperty(
        name="壁の高さ (Height)",
        default=3.5, min=1.0, max=20.0,
        description="城壁の高さ（メートル）"
    )
    castle_wall_thickness: bpy.props.FloatProperty(
        name="壁の厚み (Thickness)",
        default=1.2, min=0.4, max=5.0,
        description="城壁の奥行き厚み（メートル）"
    )
    castle_wall_has_crenels: bpy.props.BoolProperty(
        name="銃眼・狭間を付ける",
        default=True,
        description="城壁天面に兵士が身を隠す凸凹の銃眼胸壁（Crenels）を設置"
    )
    castle_wall_density: bpy.props.FloatProperty(
        name="石材密度 (Density)",
        default=22.0, min=5.0, max=60.0,
        description="壁表面1平方メートルあたりの石材ブロック配置密度"
    )
    castle_wall_min_dist: bpy.props.FloatProperty(
        name="石材最小間隔 (Min Distance)",
        default=0.22, min=0.05, max=0.6,
        description="石材ブロック同士の過度な重なりを防ぐ最小離隔距離"
    )
    castle_wall_jitter: bpy.props.FloatProperty(
        name="凹凸・不揃い (Jitter)",
        default=0.04, min=0.0, max=0.15,
        description="手積みによる石材の前後段差・飛び出しの度合い"
    )
    castle_wall_batter: bpy.props.FloatProperty(
        name="裾広がり傾斜 (Batter)",
        default=0.18, min=0.0, max=0.6,
        description="下部が末広がりになる石垣・城壁特有の傾斜率（台形スロープ）"
    )
    castle_wall_roughness: bpy.props.FloatProperty(
        name="土台のうねり・出っ張り (Roughness)",
        default=0.14, min=0.0, max=0.45,
        description="土台メッシュ自体の波打ち・傾き・荒削りな出っ張りの度合い"
    )

    # ── CAVE (Dungeon / Cave System) Properties ──
    # ── CAVE Path & Rock Style Properties ──
    cave_path_type: bpy.props.EnumProperty(
        name="洞窟ルート形状",
        items=[
            ('S_CURVE', "〰️ S字蛇行 (S-Curve)", "自然な蛇行カーブと起伏を持つ洞窟ルート"),
            ('STRAIGHT', "➖ 直線・見通し坑道 (Straight)", "奥行きを見通せる直進トンネル（微細な岩盤の歪み付き）"),
            ('Z_CRANK', "⚡ クランク折れ曲がり (Z-Crank)", "急角度で折れ曲がる防衛要塞・断層クレバス型ルート"),
            ('CHAMBER_HALL', "🏛️ 大空洞・ドーム広間 (Chamber Hall)", "入口が狭く中央が巨大な円形ドームに広がる大空間"),
            ('RANDOM', "🎲 ランダム抽選 (Random Route)", "Re-Roll時にルート形状を自動抽選")
        ],
        default='S_CURVE',
        description="洞窟全体の骨格ルート・形状"
    )
    cave_rock_style: bpy.props.EnumProperty(
        name="岩肌スタイル",
        items=[
            ('SLATE', "🪨 暗黒泥岩・スレート (Dark Slate)", "濡れた漆黒〜暗灰色の板状岩盤（地下水路・ダンジョン）"),
            ('LIMESTONE', "🏛️ 石灰岩・カルスト (Limestone Karst)", "白〜淡黄色の溶食岩肌＆エメラルド水面（鍾乳洞・地底湖）"),
            ('SANDSTONE', "🏜️ 赤色砂岩・キャニオン (Red Sandstone)", "赤褐色〜オレンジの鮮やかな水平地層バンド（渓谷洞窟）"),
            ('BASALT', "🌋 玄武岩・火山岩 (Basalt Volcanic)", "漆黒・黒曜石のような角張った荒削り火山岩盤")
        ],
        default='SLATE',
        description="洞窟全体の岩質・色調・シェーダー質感"
    )

    cave_water_type: bpy.props.EnumProperty(
        name="水面タイプ (Water Mode)",
        items=[
            ('PUDDLES', "💧 点在する水たまり・湧水池 (Puddles & Pools)", "床の窪みや岩棚に点在するリアルな水たまり・湧水池を生成"),
            ('RIVER', "🌊 地下水脈・河川 (Subterranean River)", "洞窟中央を貫通する一本の地下河川を生成"),
            ('BOTH', "🌊💧 河川 ＋ 水たまり (River + Puddles)", "中央の河川と、高台テラスに点在する水たまりの両方を生成"),
            ('NONE', "🏜️ 完全乾燥 (Dry Cave)", "水面を一切生成しない乾燥した洞窟")
        ],
        default='PUDDLES',
        description="洞窟内に配置する水の形態"
    )
    cave_puddle_count: bpy.props.IntProperty(
        name="水たまり数 (Puddle Count)",
        default=6, min=1, max=24,
        description="洞窟の床面テラスに点在する水たまりの個数"
    )
    cave_puddle_scale: bpy.props.FloatProperty(
        name="水たまり規模 (Puddle Scale)",
        default=2.4, min=0.5, max=10.0,
        description="点在する水たまりの標準直径（メートル）"
    )
    cave_has_river: bpy.props.BoolProperty(
        name="🌊 川・水流を生成 (Has River)",
        default=True,
        description="後方互換用プロパティ"
    )
    cave_river_width: bpy.props.FloatProperty(
        name="川幅 (River Width)",
        default=4.5, min=1.5, max=20.0,
        description="中央の水流（川床）の横幅（メートル）"
    )
    cave_river_depth: bpy.props.FloatProperty(
        name="水流の谷の深さ (River Depth)",
        default=1.3, min=0.3, max=6.0,
        description="川底が岩盤から掘り下げられる深さ（メートル）"
    )
    cave_terrace_steps: bpy.props.IntProperty(
        name="岩棚の段数 (Terrace Steps)",
        default=4, min=1, max=10,
        description="両岸の歩行可能な平坦岩棚・階段状テラスの段数"
    )
    cave_floor_width: bpy.props.FloatProperty(
        name="洞窟床の全幅 (Floor Width)",
        default=18.0, min=6.0, max=60.0,
        description="洞窟全体の左右の広がり幅（メートル）"
    )
    cave_floor_length: bpy.props.FloatProperty(
        name="洞窟の全長 (Length)",
        default=35.0, min=10.0, max=120.0,
        description="洞窟フロアの奥行き・全長（メートル）"
    )
    cave_roughness: bpy.props.FloatProperty(
        name="岩盤の起伏・断層 (Roughness)",
        default=0.8, min=0.1, max=2.0,
        description="ボロノイ断層・岩肌のゴツゴツしたスラブ感の強さ"
    )
    cave_randomize_shape: bpy.props.BoolProperty(
        name="Re-Roll時に幅・段差も自動抽選",
        default=False,
        description="再抽選時に川幅や岩棚の段数・起伏もランダムに自動変化"
    )
    # ── CAVE Step 2 (Ceiling & Cliff Walls) Properties ──
    cave_generate_ceiling: bpy.props.BoolProperty(
        name="🏛️ 天井・断崖壁を生成 (Ceiling & Cliffs)",
        default=True,
        description="頭上に覆い被さる角張った断崖側壁と天井岩盤スラブ（別オブジェクト）を生成"
    )
    cave_ceiling_height: bpy.props.FloatProperty(
        name="天井高 (Ceiling Height)",
        default=6.5, min=2.5, max=25.0,
        description="洞窟床面から天井岩盤までの高さ（メートル）"
    )
    cave_ceiling_overhang: bpy.props.FloatProperty(
        name="せり出し度 (Overhang)",
        default=0.85, min=0.3, max=1.0,
        description="左右の断崖壁から中央頭上へ張り出す岩盤アーチのせり出し度合い"
    )
    cave_ceiling_fissure: bpy.props.FloatProperty(
        name="天井の亀裂・天窓 (Fissure)",
        default=0.3, min=0.0, max=6.0,
        description="天井中央の割れ目・光が差し込む天窓スリットの幅（0で完全密閉）"
    )
    cave_ceiling_roughness: bpy.props.FloatProperty(
        name="天井岩盤の起伏 (Ceiling Roughness)",
        default=0.9, min=0.1, max=2.0,
        description="天井・断崖岩壁のボロノイ断層・ゴツゴツしたスラブ感の強さ"
    )
    # ── CAVE Lighting Properties ──
    cave_setup_lights: bpy.props.BoolProperty(
        name="💡 洞窟ライトを自動配置 (Auto Lights)",
        default=True,
        description="洞窟内部が見えやすくなるよう、たいまつ風ポイントライト群と天窓光を自動配置・追従"
    )
    cave_light_intensity: bpy.props.FloatProperty(
        name="ライト明るさ倍率 (Light Intensity)",
        default=1.0, min=0.1, max=5.0,
        description="洞窟ライト群の光量・エネルギー倍率"
    )
    # ── CAVE Step 3: Speleothems & Debris Properties ──
    cave_generate_pillars: bpy.props.BoolProperty(
        name="🏛️ 天地貫通の岩柱 (Pillars)",
        default=True,
        description="天井から床までを力強く繋ぎ止める巨大な鍾乳石柱・侵食岩柱を生成"
    )
    cave_pillar_count: bpy.props.IntProperty(
        name="岩柱の本数 (Pillar Count)",
        default=4, min=0, max=12,
        description="洞窟内に配置する岩柱の本数"
    )
    cave_generate_stalactites: bpy.props.BoolProperty(
        name="🧊 鍾乳石・石筍 (Speleothems)",
        default=True,
        description="天井から垂れ下がるツララ状鍾乳石と、床から立ち上がる石筍クラスタを生成"
    )
    cave_stalactite_density: bpy.props.FloatProperty(
        name="鍾乳石密度 (Density)",
        default=1.0, min=0.2, max=3.0,
        description="鍾乳石・石筍クラスタの群生密度倍率"
    )
    cave_generate_boulders: bpy.props.BoolProperty(
        name="🪨 崩落巨石・瓦礫 (Debris)",
        default=True,
        description="川岸や岩棚に散乱する崩落巨石・岩石瓦礫群を生成"
    )
    cave_boulder_count: bpy.props.IntProperty(
        name="巨石・瓦礫数 (Debris Count)",
        default=16, min=0, max=40,
        description="洞窟内に散布する崩落岩の個数"
    )
    # ── CAVE Step 4: Moss & Vegetation Properties ──
    cave_add_moss: bpy.props.BoolProperty(
        name="🌿 苔を生やす (Add Moss)",
        default=True,
        description="湿った岩棚や水際、岩柱の根本にベルベット調の深緑の苔をプロシージャル生成"
    )
    cave_moss_amount: bpy.props.FloatProperty(
        name="苔の量 (Moss Amount)",
        default=0.6, min=0.0, max=1.0,
        description="岩肌を覆う苔の面積・密度"
    )

    # ── ARCH (Stone Arch & Colonnade) Properties ──
    arch_style: bpy.props.EnumProperty(
        name="アーチ様式 (Arch Style)",
        items=[
            ('ROMAN_ROUND', "🏛️ ローマ半円アーチ (Roman Round)", "古代ローマ・ルネサンス建築の正円アーチ"),
            ('GOTHIC_POINTED', "⛪ ゴシック尖頭アーチ (Gothic Pointed)", "二心円弧で上部に鋭利な頂点を持つゴシック様式"),
            ('HORSESHOE', "🕌 蹄鉄形アーチ (Horseshoe Arch)", "開口部がやや絞り込まれたイスラム・ムーア様式"),
            ('SEGMENTAL', "🌉 偏平・欠円アーチ (Segmental Arch)", "半円より低い緩やかな円弧・橋梁や低天井用")
        ],
        default='ROMAN_ROUND'
    )
    arch_structure_type: bpy.props.EnumProperty(
        name="構造タイプ (Structure Type)",
        items=[
            ('SINGLE', "🚪 単体アーチ門 (Single Archway)", "モジュラー壁と繋がる単体のアーチ開口部"),
            ('COLONNADE', "🏛️ 連続アーチ回廊 (Colonnade / Arcade)", "柱とアーチが横に等間隔で連なる連続列廊"),
            ('VAULT_CEILING', "🛖 ヴォールト天井 (Vault Ceiling)", "アーチを奥行きに押し出した天井スラブ")
        ],
        default='SINGLE'
    )
    arch_span_count: bpy.props.IntProperty(
        name="連数 (Span Count)",
        default=3, min=2, max=8,
        description="連続回廊（Colonnade）におけるアーチの連数"
    )
    arch_has_keystone: bpy.props.BoolProperty(
        name="🏛️ 要石を配置 (Keystone)",
        default=True,
        description="アーチ最頂部に楔（くさび）形状の要石を突出配置"
    )
    arch_keystone_scale: bpy.props.FloatProperty(
        name="要石サイズ (Keystone Scale)",
        default=1.25, min=1.0, max=2.0,
        description="要石の突出・拡大倍率"
    )
    arch_molding_tiers: bpy.props.IntProperty(
        name="モールディング段数 (Molding Tiers)",
        default=2, min=1, max=4,
        description="アーチ内周・外周の多段ステップ装飾"
    )
    arch_pillar_shape: bpy.props.EnumProperty(
        name="支柱形状 (Pillar Shape)",
        items=[
            ('SQUARE_PIER', "🧱 角柱・ピアー (Square Pier)", "重厚な角柱支柱＋柱頭モールディング"),
            ('OCTAGONAL', "💎 八角柱 (Octagonal Pier)", "角を落としたクラシックな八角柱"),
            ('ROUND_COLUMN', "🏛️ 円柱・コラム (Round Column)", "クラシックな円柱＋ベース台座")
        ],
        default='SQUARE_PIER'
    )
    arch_pillar_width: bpy.props.FloatProperty(
        name="柱の太さ (Pillar Width)",
        default=0.55, min=0.15, max=2.5,
        unit='LENGTH',
        description="アーチを支える柱の太さ・直径 (m)"
    )
    arch_column_height: bpy.props.FloatProperty(
        name="柱の長さ・高さ (Column Height)",
        default=2.2, min=0.5, max=10.0,
        unit='LENGTH',
        description="柱身（シャフト）の垂直方向の長さ・高さ (m)"
    )
    arch_has_spandrel: bpy.props.BoolProperty(
        name="🧱 上部スパンドレル壁 (Spandrel Wall)",
        default=True,
        description="アーチ上部を水平に塞ぎ、壁や天井とフラットに接合できる形状にする"
    )
    arch_has_pedestal: bpy.props.BoolProperty(
        name="🏛️ 柱脚台座 (Pedestal Base)",
        default=True,
        description="柱の下部に重厚な台座ブロックを配置"
    )


