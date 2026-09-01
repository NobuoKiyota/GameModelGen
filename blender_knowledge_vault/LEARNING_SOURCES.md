# 📚 Blender プロ技法 学習元ソース・チュートリアル マスターインデックス (Learning Sources)

本ドキュメントは、本プロジェクト（`GameModelGen / MeshCreator`）が学習・実装した **Blender チュートリアル動画、論文、技術記事の一次情報（URL・著者・核心技術）** を永久保存するためのマスターインデックスです。

すべての AI エージェントは、新機能の実装・改良時にこの一次情報を参照し、パラメータやアルゴリズムの忠実な再現を行ってください。

---

## 1. 🌾 草原・草地プロシージャルスタジオ (v7.8)

*   **URL**: [https://www.youtube.com/watch?v=nVjq7rn97h0](https://www.youtube.com/watch?v=nVjq7rn97h0)
*   **著者・チャンネル**: Mdesign 様
*   **動画タイトル**: 『【Blender】リアルな草原の作り方』
*   **学習・実装した核心技術**:
    1.  **地形モデリング**: 多重サイン波（FBM的合成）による自然な丘陵起伏地面（プロポーショナル編集相当の自動生成）。
    2.  **草ブレード幾何学**: UV.Y（`0.0 根元` 〜 `1.0 先端`）を縦展開した 5 点先細り草ブレードモデリング。
    3.  **草シェーダー**: 根元〜先端のカラーランプグラデーション ＋ `Object Info (Random)` による色相の揺らぎ ＋ `Translucent BSDF`（半透明SSS / 逆光透過光）の合成。
    4.  **パーティクル散布**: `Hair Particle` ＋ `Collection Render` による複数ブレード形状のランダム散布 ＆ パーリンノイズ頂点グループ（`Grass_Density`）自動ペイント。
    5.  **ゲームエンジン最適化**: `disconnect_hair` → `convert(MESH)` による Unity/UE 向け実ポリゴンメッシュ変換。

---

## 2. 🏔️ PBRディスプレイスメント ＆ 3D凹凸立体化 (v7.9)

*   **URL**: [https://www.youtube.com/watch?v=M_AoNzdC4gI](https://www.youtube.com/watch?v=M_AoNzdC4gI)
*   **著者・チャンネル**: Mdesign 様
*   **動画タイトル**: 『【Blender】テクスチャで凸凹を表現する』
*   **学習・実装した核心技術**:
    1.  **自動認識**: PBR テクスチャセット（`_Color`, `_NormalGL`, `_Displacement`, `_AmbientOcclusion`, `_Roughness`）のプレフィックス自動検知とノード自動配線。
    2.  **Cycles Displacement**: `ShaderNodeDisplacement` ノード ＆ `material.cycles.displacement_method = 'BOTH'`（ディスプレイスメントとバンプの両立）。
    3.  **実メッシュ頂点変位**: `Subdivision Surface`（シンプル細分化）＋ `Displace Modifier`（Displacement 画像連動）による 3D リアル凹凸のジオメトリ立体化。

---

## 3. 🌊 リアル水面・水域スタジオ (v8.0) ── 4大水面講座

### ① 映画「Flow」風 アニメーション水面
*   **URL**: [https://www.youtube.com/watch?v=yRXMe-1N6_Y](https://www.youtube.com/watch?v=yRXMe-1N6_Y)
*   **動画タイトル**: 『初心者でも簡単！Blenderでできる美しい水のアニメーションの作り方』
*   **学習・実装技術**:
    *   `Transmission: 1.0`（完全透過）＋ `Roughness: 0.05`。
    *   **物理屈折率 `IOR: 1.333`**（純水の屈折率を厳密適用）。
    *   **`ShaderNodeVolumeAbsorption`**: 水深に応じた深い青緑色の光減衰（Density: 0.5〜1.5, Color: `#0A4D68`）。

### ② フォトリアル海洋 (Ocean Simulation)
*   **URL**: [https://www.youtube.com/watch?v=vSgWZG2ugf0](https://www.youtube.com/watch?v=vSgWZG2ugf0)
*   **動画タイトル**: 『【Blender】フォトリアルな海の作り方！手軽にサクッと作れます【海洋】【Ocean】』
*   **学習・実装技術**:
    *   **`Ocean Modifier`**: `Choppiness`（波の鋭さ・尖り）の調整。
    *   **白波泡（Foam）の生成**: `use_foam = True` により、波頭の砕け散る白波属性（`foam_layer_name = 'foam'`）を生成し、プリンシプルBSDFにミックスしてリアルな白波を表現。

### ③ 大海原・深海シェーダー
*   **URL**: [https://www.youtube.com/watch?v=un5N3cbUWJM](https://www.youtube.com/watch?v=un5N3cbUWJM)
*   **動画タイトル**: 『[blender]リアルな海の作り方』
*   **学習・実装技術**:
    *   深海色（Deep Ocean Navy `#020B1A`）と浅瀬・波頭のエメラルドグリーンのカラーパレット設計。
    *   Eevee レンダラーでのスクリーンスペース屈折（Screen Space Refraction）とマテリアルブレンド設定。

### ④ フォトリアル湖・池・水たまり (Chuck CG)
*   **URL**: [https://www.youtube.com/watch?v=0SJ-__0gK_k](https://www.youtube.com/watch?v=0SJ-__0gK_k)
*   **著者・チャンネル**: Chuck CG 様
*   **動画タイトル**: 『How To Create Realistic Water in Blender』
*   **学習・実装技術**:
    *   湖・池・泉・水たまりの有機的スラブ幾何学（すり鉢状の池底）。
    *   **二重波紋 Bump リンク**: 細かいさざ波（`Noise Texture Scale: 16.0`）とうねり（`Voronoi Texture Scale: 4.0`）を直列（Normal ➔ Normal）に繋ぐ水面微細凹凸。
    *   水面（`Water_Surface_Mat`）と池底スラブ（`Water_Bed_Mat`）の独立マテリアルによる二層構造。

---

## 4. 🪨 岩石・プロシージャルモデリング基礎

*   **著者・チャンネル**: Sacoche Ito 3D 様
*   **学習・実装技術**:
    *   **凸包（Convex Hull）アルゴリズム**: ランダム散布した頂点群から凸包メッシュを生成し、ボロノイ破砕やベベルを組み合わせることで、100% 隙間のないソリッドな巨石・岩石を生成する手法。

---

## 5. 🌲 リアル樹木モデリング・シェーディング（現在拡充中）

*   **課題と今後の拡張計画**:
    1.  **L-System / フラクタル階層分岐**: 幹 ➔ 主枝（Level 1）➔ 側枝（Level 2）➔ 小枝（Level 3）の 3〜4 段階の再帰的分岐構造。
    2.  **葉っぱカード（Foliage Leaf Cards / Clusters）**: 単一板ポリの単純配置を廃止し、テクスチャ付き枝葉クラスター ＋ アルファ抜き ＋ ドーム状配置。
    3.  **樹冠法線転送（Tree Canopy Normal Transfer）**: 樹冠全体の法線を球状・外向きに整え、板ポリの角や平坦な陰影を解消してふんわりとした自然な陰影を実現。
