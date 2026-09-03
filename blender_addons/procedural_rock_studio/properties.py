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
        'BEAM_ARCH': "Beam_Arch",
        'GRASS': "Grass_Meadow",
        'BOOKSHELF': "Antique_Bookshelf",
        'TABLE': "Antique_Table",
        'CHAIR': "Antique_Chair",
        'CHEST': "Antique_Chest",
        'BED': "Antique_Bed",
        'FENCE': "Wooden_Fence",
        'BUSH': "Bush_Shrub"
    }
    props.asset_name = name_map.get(cat, "Prop_Asset")

    if cat == "BUSH":
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
    elif cat in ("BEAM", "BEAM_ARCH"):
        props.size_x = 2.4
        props.size_y = 1.5
        props.size_z = 2.0
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
        'BEAM_ARCH': r"Z:\MeshCreator\textures\Wood",
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


class PropStudioProperties(bpy.types.PropertyGroup):
    prop_category: bpy.props.EnumProperty(
        name="Category",
        items=[
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
            ('PILLAR', "🏛️ 柱・石柱 (Pillar / Column)", "textures/Pillar/ と自動連動"),
            ('BEAM', "🪵 梁・丸太支柱 (Timber Log Beam)", "textures/Wood/ と自動連動（シリンダー丸太梁）"),
            ('BEAM_ARCH', "🪵🏛️ 梁アーチ (Beam Arch)", "textures/Wood/ と自動連動（シリンダー丸太アーチ）")
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

    # ── PILLAR & COLUMN Properties ──
    pillar_type: bpy.props.EnumProperty(
        name="Pillar Type",
        items=[
            ('GOTHIC_CLUSTERED', "ゴシック束ね柱 (Gothic Clustered)", "【yR3hx1l7nn8準拠】中央主柱＋6~8本の小柱Colonnettes束ね構造"),
            ('ROMAN_FLUTED', "ギリシャ・ローマ溝彫り円柱 (Roman Fluted)", "【o6qQAKKbPRo準拠】16~24本フルーティング溝＋ドーリア式柱頭"),
            ('RUINED_ANCIENT', "古代遺跡の崩壊石柱 (Ruined Ancient)", "上部斜め欠損・崩壊ドラム石積み＋ひび割れ侵食"),
            ('SQUARE_MONUMENT', "西洋角柱・モニュメント (Square Monument)", "【b8g8j-7KWYM準拠】面取り多段角柱＋コーニス天頂装飾")
        ],
        default='GOTHIC_CLUSTERED'
    )
    pillar_mat_type: bpy.props.EnumProperty(
        name="Pillar Material",
        items=[
            ('MARBLE', "白大理石 (Polished Marble)", "高級感のある筋模様と光沢"),
            ('ANCIENT_STONE', "古代砂岩 (Ancient Sandstone)", "風化した砂利感と微細バンプ"),
            ('MOSSY_RUINS', "苔むした遺跡 (Mossy Ruins)", "石肌に生える緑の苔")
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
        name="縦溝の数 (Flutes)", default=18, min=8, max=32,
        description="ローマ円柱の縦溝（フルーティング）数"
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




