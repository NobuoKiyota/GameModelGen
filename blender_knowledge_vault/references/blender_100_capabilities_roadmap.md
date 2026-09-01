# 🗺️ Blender 全機能・ワークフロー完全ロードマップ ＆ 実践パラメータ集
> **基準動画**: 『【初心者必見】Blenderで出来ること100選！Blenderって何ができるの？』（`59zBPXisTms` / 2:08〜）  
> **本書の目的**: 単なる機能名だけでなく、**「実際にBlenderのどこを操作し、どんな具体的な数値を設定するか」** を完全網羅した実践レシピ集。

---

## 🏛️ 1. モデリング（3D形状生成手法）

### 01. ポリゴンモデリング (Polygon Modeling)
- **操作場所**: Edit Mode（`Tab` キー）
- **何をいじるか / 具体例**:
  - **押し出し (Extrude)**: `E` キー → `Z` 方向に `1.5m` など（壁や柱の作成）
  - **面差し込み (Inset)**: `I` キー → `Thickness: 0.05m`（窓枠や縁取りの作成）
  - **ベベル (Bevel Modifier / Ctrl+B)**: `Width: 0.015m〜0.03m`, `Segments: 3〜4`, `Shape: 0.5`（角を落としてハイライトを乗せる）
  - **ループカット (Loop Cut)**: `Ctrl+R` → 分割数 `2〜4`

### 02. スプライン/カーブモデリング (Curve Modeling)
- **操作場所**: Object Data Properties（カーブアイコン 🧬）
- **何をいじるか / 具体例**:
  - **ジオメトリ・ベベル (Bevel Depth)**: `Depth: 0.04m〜0.15m`, `Resolution: 4〜8`（パイプ・ロープ・木の幹を一発生成）
  - **先細り制御 (Radius)**: 制御点を選んで `Alt+S` → 根元 `1.0` から先端 `0.2`（木の枝やツルの先細り）
  - **押し出し (Extrude)**: `Extrude: 0.2m`（リボン状・帯状メッシュの作成）

### 03. スカルプトモデリング (Sculpt Modeling)
- **操作場所**: Sculpt Mode（上部タブ）
- **何をいじるか / 具体例**:
  - **Dyntopo（動的トポロジー）**: `Detail Size: 8.0px`, `Refine Method: Subdivide Collapse`（頂点を自動増減させながら彫刻）
  - **Clay Strips ブラシ**: `Strength: 0.4`, `Radius: 45px`（筋肉や岩の段差の盛り上げ）
  - **Scrape / Flatten ブラシ**: `Strength: 0.6`（岩の平らな割れ目・ファセット面の作成）

### 04. ブーリアンモデリング (Boolean Modifier)
- **操作場所**: Modifier Properties（スパナアイコン 🔧）
- **何をいじるか / 具体例**:
  - **Solver（計算方式）**: `Exact`（高精度・穴あけ）または `Fast`（高速・ゲーム用ローポリ）
  - **Operation**: `Difference`（穴あけ・削り出し）, `Union`（完全結合）, `Intersect`（重なり部分のみ抽出）
  - **Overlap Tolerance**: `0.0001m`（面が完全に重なった際のチラつき防止）

### 05. テクスチャ/ディスプレイスモデリング (Displace Modifier)
- **操作場所**: Modifier Properties → Displace
- **何をいじるか / 具体例**:
  - **Strength（変位の強さ）**: `0.15〜0.3m`（岩石の隆起量）
  - **Midlevel（基準面）**: `0.5`（0.5より明るい部分が隆起、暗い部分が窪む）
  - **Texture**: `Clouds / Voronoi`, `Size: 0.45〜0.8`（有機的な岩肌・地形の凹凸生成）

### 06. テキストモデリング (3D Text)
- **操作場所**: Object Data Properties → Geometry
- **何をいじるか / 具体例**:
  - **Extrude（厚み）**: `0.05m`（文字の立体押し出し）
  - **Bevel Depth / Resolution**: `Depth: 0.005m`, `Resolution: 3`（文字のフチを丸めて光沢を出す）

### 07. ミラーモデリング (Mirror Modifier)
- **操作場所**: Modifier Properties → Mirror
- **何をいじるか / 具体例**:
  - **Axis**: `X`（左右対称）
  - **Clipping**: `ON`（中央の境界頂点が離れずに自動吸着・結合する）
  - **Merge Limit**: `0.001m`

---

## 🎨 2. シェーディング ＆ テクスチャリング

### 08. PBRマテリアル (Principled BSDF)
- **操作場所**: Shader Editor
- **何をいじるか / 具体例**:
  - **Roughness（粗さ）**: 水面 `0.02〜0.05`, 金属/磨き石 `0.2`, 木材 `0.5〜0.6`, 泥/岩石 `0.8〜0.9`
  - **Metallic（金属度）**: 非金属（岩・木・水）`0.0`, 金属（鉄・金）`1.0`
  - **IOR（屈折率）**: 空気 `1.0`, 水 `1.333`, ガラス `1.5〜1.52`, ダイヤモンド `2.42`
  - **Transmission Weight（透過）**: 不透明プロップ `0.0`, 水面/ガラス `0.85〜1.0`

### 09. プロシージャル・シェーダーノード構築
- **操作場所**: Shader Editor
- **何をいじるか / 具体例**:
  - **Noise Texture**: `Scale: 3.5〜6.0`, `Detail: 4.0〜6.0`, `Roughness: 0.55`, `Distortion: 0.2`（自然なまだら模様）
  - **ColorRamp**: 濃い色（Pos 0.2）と明るい色（Pos 0.7）でハイライト・陰影コントラストを強調
  - **Bump ノード**: `Strength: 0.15〜0.3`, `Distance: 0.05m`（頂点を増やさずにリアルな岩肌・木目を表現）
  - **Attribute ノード**: `Name: "foam"` → 波頭の白波マスクを抽出

---

## 💡 3. ライティング ＆ 環境光

### 20〜24. ライト各種パラメータ
- **Point Light**: `Power: 40W〜100W`, `Radius: 0.15m`（柔らかい影）
- **Spot Light**: `Power: 200W`, `Spot Size: 45°`, `Blend: 0.25`（光の境界のぼかし）
- **Area Light**: `Power: 150W`, `Size: 1.0m × 1.0m`（スタジオ窓光・均一な陰影）
- **Sun Light**: `Strength: 3.0〜5.0`, `Angle: 0.5°〜1.5°`（太陽の見かけの大きさによる影のボケ具合）

### 25. Nishita 物理大気スカイ (Sky Texture)
- **操作場所**: World Properties → Surface → Sky Texture (NISHITA)
- **何をいじるか / 具体例**:
  - **Sun Elevation（太陽高度）**: `15.0°〜20.0°`（朝夕の美しい斜光・水面反射）
  - **Sun Rotation（太陽方位）**: `45.0°`
  - **Air Density（空気密度）**: `1.0`, **Dust Density（チリ）**: `1.0`, **Ozone Density（オゾン青み）**: `1.0`
  - **Sun Intensity**: `1.0`

---

## 🎬 4. アニメーション ＆ ゲーム出力

### 31〜33. アニメーション曲線 ＆ ループ制御
- **操作場所**: Graph Editor / Dope Sheet
- **何をいじるか / 具体例**:
  - **Interpolation（補間）**: `LINEAR`（等速進行・水面ループ用）または `BEZIER`（有機的な加減速）
  - **Extrapolation（外挿）**: `LINEAR`（タイムラインを何フレームに伸ばしても等速で進み続ける）
  - **Ocean Modifier の Time**: 1フレーム `1.0` → 60フレーム `2.2`（速度 `0.02/frame` = 穏やかなさざ波）

### 36. Unity向けシェイプキー・アニメーションベイク (anim_baker)
- **操作場所**: Python / アドオン
- **何をいじるか / 具体例**:
  - **サンプリング間隔 (Step)**: `step=3〜4`（60フレームを18〜20個のシェイプキー `Wave_Frame_XXX` に圧縮ベイク）
  - **Action のキーフレーム**: 各シェイプキーに `0.0 -> 1.0 -> 0.0` を打って重なりブレンド
  - **FBX Export 設定**: `bake_anim=True`, `bake_anim_use_all_actions=True`, `bake_anim_step=1.0`

---

## 🌊 5. 物理波浪シミュレーション (Ocean Modifier)

### 37. 海洋モディファイアの設定パラメータ完全一覧
- **Geometry Mode**: `DISPLACE`（メッシュを変形）
- **Resolution（解像度）**: プレビュー `12`, レンダー `16`（波のきめ細かさ）
- **Spatial Size（空間サイズ）**: `メッシュ幅 × 1.5`（波の波長スケール）
- **Wind Velocity（風速）**: 穏やかな湖 `4.0〜5.0m/s`, 荒海 `15.0〜30.0m/s`
- **Wave Scale（波の高さ）**: 湖面 `0.05〜0.08m`, 海洋 `0.5〜1.5m`
- **Choppiness（波頭の尖り具合）**: `1.0〜1.4`（数値を上げると波の先端が尖り、白波が立つ）
- **Damping（波の減衰）**: `0.5`（反射波の抑制）
- **Foam（白波・泡）**: `use_foam = True`, `foam_coverage = 0.25〜0.3`, `foam_layer_name = "foam"`

---

## 🌿 6. パーティクル・スキャッター (Hair Particle System)

### 38. 草木・茂みの散布パラメータ
- **Type**: `HAIR`, **Advanced**: `ON`
- **Emission Count（散布数）**: 低木ブレード `120〜250本`, 芝生フィールド `2,000〜5,000本`
- **Hair Length（長さ）**: `0.35m〜0.5m`
- **Render As**: `Collection`（先細りブレード集）または `Object`
- **Scale / Scale Randomness**: `Scale: 0.8〜1.2`, `Scale Random: 0.35`（自然な大きさのバラつき）
- **Rotation**: `Orientation: Normal-Tangent`, `Randomize: 0.25`, `Phase: 0.5`, `Phase Random: 0.8`
