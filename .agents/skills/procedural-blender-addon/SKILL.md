---
name: procedural-blender-addon
description: >-
  Blenderのモデリング、PBRシェーディング、プロシージャルノイズ生成、およびPython (bpy) による
  Geometry Nodesの自動構築とテクスチャベイク自動化のための総合開発ガイド。
---

# Blender Procedural Addon & Shader Development Guide

Blenderでプロシージャル（数式・アルゴリズム）ベースの形状およびリアルな質感を自動構築し、ゲームエンジン向けに最適化するための技術ガイド。

--------------------------------------------------------------------------------

## 1. Blender コアスキルのインデックス (動画学習の体系化)

### ① モデリング (Modeling)
*   **ポリゴンモデリング**: BMeshを使用した面・辺・頂点の動的生成。
*   **スプライン (Curve) モデリング**: ベジエ・パスカーブの制御点操作と、モデルの変形（カーブモディファイア）。
*   **スカルプトモデリング**: 動的トポロジーを用いた有機的ディテールの追加。
*   **ブーリアン**: `union`, `difference`, `intersect` を用いた幾何結合。
*   **石壁モデリング (Cell Fracture & Subdiv)** (動画 `miUG801VlCA` 準拠): 
    *   面を細分化し、**Cell Fracture（ボロノイ破砕アドオン）** を用いて不規則なブロックに粉砕。
    *   各破片に Subdivision Surface や Bevel を適用することで、目地の詰まったリアルな石垣や崩れた石壁を極めて高速に作成する。
*   **スカルプト不要の崖・岩面モデリング (Modifier Stacking)** (動画 `tCCNi_vx4A4` / `g9T3vDtTAPk` 準拠):
    *   多重細分化したベースメッシュに対し、**Displace（ディスプレイス）モディファイアを複数積層**させる。
    *   `第1層 (大)`: Clouds/Voronoiテクスチャ（スケール大）で崖の全体的なうねりや大きな岩のシルエットを作る。
    *   `第2層 (小)`: Noiseテクスチャ（スケール小・高コントラスト）でエッジの切り立ちや細かな凹凸を適用。
    *   テクスチャ座標を `Object` または `Global` に設定することで、メッシュを動かしてもリアルな崖の切り立ちが崩れず維持される。

### ② シェーディング & テクスチャリング (Shading & Texturing)
*   **PBRマテリアル**: プリンシプルBSDFの `Albedo`, `Roughness`, `Metallic`, `Normal`, `Specular`, `Displacement` の物理的な役割と適切な接続法。
*   **プロシージャルテクスチャ**: ノイズ (Noise)、ボロノイ (Voronoi)、ウェーブ (Wave) などのノードを掛け合わせて複雑な岩肌や木肌を生成する。
*   **完全プロシージャル岩シェーダー (Shader Node Rock)** (動画 `LgOxUB1xhdA` 準拠):
    *   **多重バンプリンク**: 大きいうねり用のバンプと、砂利・風化質感用の細かいノイズバンプを**直列（Normal ➔ Normal）に接続**して多層的な凹凸を表現。
    *   **ColorRampによる風化色の制御**: 凸部（エッジ部）には削れた白い石の色、凹部（溝）には土や苔の暗い色をマッピングし、リアルな表情を作る。
*   **バンプ vs ディスプレイスメント**:
    *   `バンプ`: 法線情報（Normal）の擬似的な影絵表現。Non-Color空間必須。
    *   `ディスプレイスメント`: Cyclesでの `Displacement and Bump` を有効にし、メッシュ頂点自体を実際に凸凹にする非破壊表現。
*   **UVマッピング**: プロシージャルUV座標の生成、`スマートUV投影`による自動展開。

### ③ ライティング & レンダリング (Lighting)
*   **エリア・サンライト & HDRI**: 物理ベースの光源設定と背景HDRI反射の統合。
*   **ボリューメトリック**: 霧や水中の光の筋（Volumetric Absorption/Scatter）の表現。

--------------------------------------------------------------------------------

## 2. アドオン強化用 Python (bpy) コードスニペット集

### A. ChuckCG流：モディファイア積層による崖・岩の自動生成 (Modifier Stack)
スカルプトを使用せず、モディファイアの自動積層とプロシージャルテクスチャ座標の制御によって、リアルな崖を1クリックで生成するコード：
```python
import bpy

def apply_procedural_cliff_modifiers(obj, scale_large=0.4, strength_large=0.25, scale_small=0.08, strength_small=0.06):
    """Subdivision + Displace(大) + Displace(小) をスタックし、リアルな岩肌を形成"""
    if not obj or obj.type != 'MESH':
        return
        
    bpy.context.view_layer.objects.active = obj
    
    # 1. ベースの細分化 (Subdivision)
    subdiv = obj.modifiers.new(name="Cliff_Subdiv", type='SUBSURF')
    subdiv.subdivision_type = 'SIMPLE'
    subdiv.levels = 3
    subdiv.render_levels = 4
    
    # 2. ディスプレイス(大) - 大きなうねり用
    tex_large = bpy.data.textures.new(name=obj.name + "_DispLarge", type='CLOUDS')
    tex_large.noise_scale = scale_large
    tex_large.noise_depth = 2
    
    disp_large = obj.modifiers.new(name="Disp_Large", type='DISPLACE')
    disp_large.texture = tex_large
    disp_large.texture_coords = 'LOCAL'
    disp_large.strength = strength_large
    
    # 3. ディスプレイス(小) - エッジ・細部用
    tex_small = bpy.data.textures.new(name=obj.name + "_DispSmall", type='NOISE')
    # Noiseテクスチャはスケールが固定のため、マッピング等で制御するか、Cloudsの極小スケールで代用
    tex_small_clouds = bpy.data.textures.new(name=obj.name + "_DispSmallClouds", type='CLOUDS')
    tex_small_clouds.noise_scale = scale_small
    tex_small_clouds.noise_depth = 4
    
    disp_small = obj.modifiers.new(name="Disp_Small", type='DISPLACE')
    disp_small.texture = tex_small_clouds
    disp_small.texture_coords = 'LOCAL'
    disp_small.strength = strength_small
    
    # スムースシェードの適用
    bpy.ops.object.shade_smooth()
```

### B. りりそん流：完全プロシージャル岩シェーダーの構築 (Shader Node Rock)
テクスチャ画像を使わず、Blender内部のノイズと多層バンプを繋ぎ合わせてリアルな質感を作るノード構築スクリプト：
```python
def build_procedural_rock_material(mat_name):
    """Noise + Voronoi + 直列多層バンプによる完全プロシージャル岩マテリアル"""
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Output & Principled BSDF
    node_out = nodes.new('ShaderNodeOutputMaterial')
    node_out.location = (600, 0)
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.location = (300, 0)
    node_bsdf.inputs['Roughness'].default_value = 0.9  # 岩は反射を抑えてざらざらに
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    
    # Texture Coordinate & Mapping
    node_coord = nodes.new('ShaderNodeTexCoord')
    node_coord.location = (-900, 0)
    node_map = nodes.new('ShaderNodeMapping')
    node_map.location = (-700, 0)
    links.new(node_coord.outputs['Object'], node_map.inputs['Vector'])
    
    # 1. 大きな岩肌のうねり (Noise Texture)
    node_noise_large = nodes.new('ShaderNodeTexNoise')
    node_noise_large.location = (-450, 150)
    node_noise_large.inputs['Scale'].default_value = 3.5
    node_noise_large.inputs['Detail'].default_value = 6.0
    node_noise_large.inputs['Distortion'].default_value = 1.2
    links.new(node_map.outputs['Vector'], node_noise_large.inputs['Vector'])
    
    # 2. 細かい砂利の質感 (Voronoi & Fine Noise)
    node_noise_fine = nodes.new('ShaderNodeTexNoise')
    node_noise_fine.location = (-450, -150)
    node_noise_fine.inputs['Scale'].default_value = 35.0
    node_noise_fine.inputs['Detail'].default_value = 8.0
    links.new(node_map.outputs['Vector'], node_noise_fine.inputs['Vector'])
    
    # 3. カラーランプによる風化グラデーション
    node_ramp = nodes.new('ShaderNodeValToRGB')
    node_ramp.location = (-150, 150)
    node_ramp.color_ramp.elements[0].color = (0.15, 0.14, 0.12, 1.0) # 谷：湿った暗いグレー
    node_ramp.color_ramp.elements[1].color = (0.42, 0.40, 0.38, 1.0) # 基本：標準の岩石色
    
    # 新しいストップを追加して凸部の風化を表現
    elem = node_ramp.color_ramp.elements.new(0.75)
    elem.color = (0.65, 0.64, 0.60, 1.0) # 凸部：削れて白っぽくなった石
    
    links.new(node_noise_large.outputs['Fac'], node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])
    
    # 4. 直列多層バンプ (Bump 1: 大 ➔ Bump 2: 小)
    node_bump_large = nodes.new('ShaderNodeBump')
    node_bump_large.location = (-150, -150)
    node_bump_large.inputs['Strength'].default_value = 0.45
    node_bump_large.inputs['Distance'].default_value = 0.08
    links.new(node_noise_large.outputs['Fac'], node_bump_large.inputs['Height'])
    
    node_bump_fine = nodes.new('ShaderNodeBump')
    node_bump_fine.location = (80, -150)
    node_bump_fine.inputs['Strength'].default_value = 0.18
    node_bump_fine.inputs['Distance'].default_value = 0.015
    # 大バンプのNormalを小バンプのNormalに入力して合成 (直列接続)
    links.new(node_bump_large.outputs['Normal'], node_bump_fine.inputs['Normal'])
    links.new(node_noise_fine.outputs['Fac'], node_bump_fine.inputs['Height'])
    
    # 最終出力をPrincipled BSDFに接続
    links.new(node_bump_fine.outputs['Normal'], node_bsdf.inputs['Normal'])
    
    return mat
```

### C. Geometry Nodes (ジオメトリノード) のPython自動構築
非破壊で形状をスライダー変更可能にするためのノードベース構築手法：
```python
def setup_geometry_nodes(obj):
    # ジオメトリノードモディファイアの追加
    gn_mod = obj.modifiers.new(name="OrganicGen", type='NODES')
    node_group = bpy.data.node_groups.new(name="OrganicGroup", type='GeometryNodeTree')
    gn_mod.node_group = node_group
    
    nodes = node_group.nodes
    links = node_group.links
    
    # 入出力ノードの配置
    node_in = nodes.new('NodeGroupInput')
    node_out = nodes.new('NodeGroupOutput')
    
    # ノイズによる変形（Set Position ノード）
    node_set_pos = nodes.new('GeometryNodeSetPosition')
    node_noise = nodes.new('ShaderNodeTexNoise')
    node_noise.inputs['Scale'].default_value = 5.0
    
    # 接続
    links.new(node_in.outputs[0], node_set_pos.inputs['Geometry'])
    links.new(node_noise.outputs['Color'], node_set_pos.inputs['Offset'])
    links.new(node_set_pos.outputs['Geometry'], node_out.inputs[0])
```

### D. ゲームエンジン向けテクスチャベイク自動化
プロシージャルな見た目を、Unity/UE用の画像として自動的にエクスポートする仕組み：
```python
def bake_procedural_to_texture(obj, mat, image_name="Baked_Diffuse", target_type='DIFFUSE'):
    nodes = mat.node_tree.nodes
    
    # ベイク先画像を作成
    img = bpy.data.images.new(image_name, width=2048, height=2048)
    
    # ベイク用画像ノードを作成して選択状態にする
    node_img = nodes.new('ShaderNodeTexImage')
    node_img.image = img
    node_img.select = True
    nodes.active = node_img # アクティブノードにする (ベイク対象の指定)
    
    # Cyclesでベイク実行
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.ops.object.bake(type=target_type, margin=16)
    
    # 保存
    img.filepath_raw = f"//textures/{image_name}.png"
    img.save()
```
