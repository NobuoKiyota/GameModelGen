# ふさこ氏 Blenderキャラクター制作 #28 (SP #01)『Substance Painter入門・基本操作』完全技術仕様書

元動画: [Substance Painterでテクスチャペイント！#28 (01) | Substance Painter入門・基本操作 〜初中級者向けチュートリアル〜](https://www.youtube.com/watch?v=RB9jILspXBk)  
動画ID: `RB9jILspXBk` / 再生時間: 36分47秒  
対象バージョン: Blender 3.6+ / 4.x、Substance 3D Painter 7.x / 8.x / 9.x / 10.x 対応  
スクリーンショットカタログ: [docs/fusako_28_sp_basics_screenshots/README.md](../../docs/fusako_28_sp_basics_screenshots/README.md)

---

## 1. 概要とテクスチャ制作パイプラインの全体像

本チュートリアルより、新章「Substance Painter テクスチャペイント編（全7回）」がスタートします。  
第28話では、Blenderでモデリング・UV展開が完了したキャラクターモデルをSubstance Painter（以下SP）へエクスポートし、セルルック（アニメ調）モデルに特化した初期設定、ベイク、レイヤー・マスク構成、ブラシ設定、透過テクスチャ作成、そしてBlenderへの再インポートと色味再現シェーダー構築までの一連のパイプラインを網羅的に習得します。

[📸 参考: fusako28_01_blender_rename_lattice.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_01_blender_rename_lattice.jpg)

### セルルック向けSP制作のコア原則
1. **オブジェクトとマテリアルの命名整理**: SPの「メッシュマスク」や「テクスチャセットリスト」でパーツ管理を容易にするため、Blender側でリネーム（Face, Hair, Body等）を徹底する。
2. **【神Tips】塗りづらいパーツの複製引き出し配置**: 口内の「歯」「舌」や重なり合う「瞳ハイライト」は、`Shift+D > Z` で上空にオフセット配置したオブジェクトを用意し、塗りやすさとルック確認を両立させる。
3. **PBRチャンネルの無効化（Base Color単一化）**: セル調キャラクターでは Metallic, Roughness, Normal, Height は原則不要。チャンネルを削除してBase Colorのみとし、UV Padding を「UV Space Neighbor」に設定して隣接色の拾い込みを防止する。
4. **基本レイヤー構造（ベタ塗り ＋ 黒マスク ＋ ペイント）**: 直接ペイントではなく、色ごとに「Fill Layer ＋ Black Mask ＋ Paint Layer」を構築し、後からの色変更やぼかし（Blur）調整を非破壊で行う。
5. **Blenderでの色味再現（Color Management: Standard）**: SPとBlenderで色味が薄くくすんで見える現象を解消するため、BlenderのView Transformを「Filmic」から「Standard」に変更する。

---

## 2. Blender側の事前準備とFBXエクスポート

### 2.1 オブジェクトのリネームとラティスモディファイア適用
1. アウトライナーで散らかったオブジェクト名を整理（例: Head, Face, Hair, Ribbon, Clip等）。
2. ラティス（Lattice）等の変形モディファイアを適用する前に、念のため `Shift+D` で複製し `M` キーでバックアップ用コレクションに退避。
3. 対象パーツのラティスモディファイアを `Ctrl+A` で適用し、左右パーツを `Ctrl+J` で結合して整理。

[📸 参考: fusako28_01_blender_rename_lattice.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_01_blender_rename_lattice.jpg)

### 2.2 瞳ハイライト・透過マテリアルの分離
1. 瞳のハイライトなど、半透明・透過を扱うパーツを選択。
2. マテリアルスロットの数字アイコンをクリックして複製（新規マテリアル化）し、「M_Face_Transparent」等と命名。
3. プレビュー用カラー（オレンジ系など）を設定して区別し、UVマップの領域を広めに確保する。

[📸 参考: fusako28_02_eye_highlight_mat_split.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_02_eye_highlight_mat_split.jpg)

### 2.3 【神Tips】口内パーツ・瞳の複製引き出し配置
1. **口内パーツ（歯・舌）**: 口の中に埋まった状態だとSPの3Dビューで極めて塗りづらい。
   - 歯と舌を選択し、`Shift+D > Z` で頭の上空へ持ち上げて複製配置する。
2. **瞳・ハイライト**: 重なり合った状態だと奥のパーツが塗りにくい。
   - 瞳を `Shift+D > Z` で上空へ持ち上げ、ハイライトはさらに横（`G X`）にずらして配置。
   - これにより「奥まって塗りにくいパーツの専用ペイント用」と「元の位置で見た目を確認するルック用」が同時に存在し、SP内での作業効率が劇的に向上する。

[📸 参考: fusako28_03_mouth_eye_offset_duplicate.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_03_mouth_eye_offset_duplicate.jpg)

### 2.4 頭部FBXのエクスポート
1. エクスポート対象となる頭部パーツ（Headコレクション）を全選択（`A`）。
2. `File > Export > FBX (.fbx)` を選択。
3. エクスポート設定:
   - **Include**: `Selected Objects`（選択したオブジェクト）にチェック。
   - **Object Types**: `Mesh`（メッシュ）のみを選択。
4. ファイル名を「Head.fbx」として保存。

[📸 参考: fusako28_04_blender_fbx_export.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_04_blender_fbx_export.jpg)

---

## 3. Substance Painterの初期セットアップとメッシュベイク

### 3.1 新規プロジェクト作成とテクスチャセット確認
1. Substance Painter を起動し、`File > New`（新規プロジェクト）を開く。
2. `Select` から先ほどエクスポートした `Head.fbx` を読み込み、`OK` をクリック。
3. 画面右上の「Texture Set List（テクスチャセットリスト）」を確認。
   - Blenderで割り当てたマテリアル名（Face, Face_Transparent, Hair等）が正確にリスト化されていることを確認する。

[📸 参考: fusako28_05_sp_new_project_import.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_05_sp_new_project_import.jpg)

### 3.2 Bake Mesh Maps の設定（テストベイク）
1. 「Texture Set Settings」タブを開き、下段の `Bake Mesh Maps` をクリック。
2. ベイク設定:
   - **Output Size**: 初期確認用として軽量な `512` を選択。
   - **Bake Maps**: セルルックでは不要な `Normal` と `ID` のチェックを外す。
   - **Anti-aliasing**: `Subsampling 4x4` に設定（AOベイク時のジャギー・チラつきノイズを抑制）。
3. `Bake all texture sets` を実行。

[📸 参考: fusako28_06_bake_mesh_maps_settings.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_06_bake_mesh_maps_settings.jpg)

### 3.3 ベイク結果の診断とUV重なり（Overlapping）検出
1. 3Dビューポート上で `B` キーを押すと、ベイクされた各マップ（AO, Curvature, Position, World Space Normal等）を順次切り替え表示できる。
2. **UV重なりの検出**:
   - `World Space Normal` 表示にすると、左右対称でUVを重ねたパーツ（サイドヘアやツインテールなど）で急激に色が変わる。
   - 重ねる意図のないパーツで色の反転や不自然な境界線が出ている場合、UVの重なりミスを即座に発見できる。

[📸 参考: fusako28_07_bake_b_key_world_normal_check.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_07_bake_b_key_world_normal_check.jpg)

### 3.4 【重要】BlenderでのUV修正とSP再読み込み（Project Configuration）
1. UVミスを発見した場合は、Blender側に戻ってUVを修正し、再度FBXを上書きエクスポート。
2. SP側で `Edit > Project Configuration` を開く。
3. `Select` から修正後のFBXを選択して `OK`。
4. **結果**: 描画レイヤーやペイント内容を保持したまま、モデルとUVだけが最新データに再読み込みされる（※ベイクは再実行が必要）。

[📸 参考: fusako28_08_project_configuration_reload.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_08_project_configuration_reload.jpg)

### 3.5 2K本番ベイクとテクスチャ解像度設定
1. テスト確認完了後、`Bake Mesh Maps` で Output Size を `2048 (2K)` に設定して本番ベイクを実行。
2. Texture Set Settings の解像度をパーツごとに設定:
   - Face: `2048`
   - Hair: `2048`
   - Face_Transparent: `1024`

[📸 参考: fusako28_09_bake_2k_resolution_setup.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_09_bake_2k_resolution_setup.jpg)

---

## 4. セルルック向けチャンネル整理と基本ペイント

### 4.1 Base Color のみにチャンネルを整理
1. セルルックモデルでは光沢や凹凸は不要なため、Texture Set Settings の「Channels」から以下を削除（`×` ボタン）:
   - `Metallic`, `Roughness`, `Normal`, `Height` を削除し、**`Base Color` のみ** にする（全テクスチャセットで実施）。
2. 表示モードを `C` キーで「Base Color」に切り替える（ライティングの影響を受けないフラット表示）。

[📸 参考: fusako28_10_base_color_only_channels.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_10_base_color_only_channels.jpg)

### 4.2 UV Space Neighbor によるパディング設定
1. 各テクスチャセットの `UV Padding` 設定を確認。
2. デフォルトの「3D Space Neighbor」から **「UV Space Neighbor」** に変更。
3. 3D空間ではなくUV空間の隣接距離でパディング（塗り足し）が行われるため、セル調のアウトライン境界で不要な色を拾うトラブルを防止できる。

[📸 参考: fusako28_11_uv_space_neighbor_padding.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_11_uv_space_neighbor_padding.jpg)

### 4.3 画面外からのスポイトカラーサンプリング
1. ベタ塗りレイヤー（Fill Layer）のカラー選択で、スポイトアイコンをドラッグ。
2. サブスタンスペインターのウィンドウ外（ブラウザ、イラストビューア、別モニターの下絵画像など）へドラッグして離すことで、外部画像から直接正確な色を抽出可能。

[📸 参考: fusako28_12_external_window_color_picker.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_12_external_window_color_picker.jpg)

### 4.4 SP基本塗り構造：Fill Layer ＋ Black Mask ＋ Paint Layer
1. デフォルトの空レイヤーを削除。
2. 新規 **Fill Layer（ベタ塗りレイヤー）** を追加し、ベース色を設定。
3. レイヤーを右クリック $\to$ **`Add black mask`（黒マスクを追加）**。
4. 黒マスクを右クリック $\to$ **`Add paint`（ペイントを追加）**。
5. ペイントレイヤー上で白ブラシを使って塗ることで、非破壊で色を浮き上がらせる。色を変えたい時はFill Layerの色を変更するだけで瞬時に全反映される。

[📸 参考: fusako28_13_fill_layer_black_mask_paint.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_13_fill_layer_black_mask_paint.jpg)

### 4.5 左右対称ペイントとブラーフィルター（チーク表現）
1. `L` キーで Symmetry（左右対称）をオンにし、中央基準線を有効化。
2. ほっぺのチーク部分をくるくるとペイント。
3. 黒マスクを右クリック $\to$ `Add filter` $\to$ フィルターから **`Blur`** を選択。
4. Blur intensity スライダーを調整することで、ふんわりとした柔らかいグラデーションチークを生成。

[📸 参考: fusako28_14_symmetry_l_key_blur_filter.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_14_symmetry_l_key_blur_filter.jpg)

### 4.6 メッシュワイヤーフレーム表示設定
1. 画面右上のディスプレイ設定（モニターアイコン）から「Mesh wireframe」にチェック。
2. 色を見やすい水色（Cyan）に設定し、不透明度を調整することで、ポリゴンの流れを確認しながら正確にペイント可能。

[📸 参考: fusako28_15_mesh_wireframe_display.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_15_mesh_wireframe_display.jpg)

### 4.7 ポリゴンフィル（Polygon Fill: 4）の UV Chunk Fill
1. まつ毛や白目など、UV島全体を同一色で塗りつぶしたい場合に使用。
2. キーボードの `4` を押して Polygon Fill ツールに切り替え。
3. プロパティ一番右の **「UV Chunk Fill」** アイコンを選択。
4. 対象のUV島をクリックするだけで、島全体が一瞬でマスク塗りつぶしされる。

[📸 参考: fusako28_16_polygon_fill_uv_chunk.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_16_polygon_fill_uv_chunk.jpg)

---

## 5. ブラシテクニックとカスタムエアブラシの作成

### 5.1 ブラシショートカットと X キー反転
- `1` : ペイントブラシ
- `2` : 消しゴム
- `3` : プロジェクション
- `4` : ポリゴンフィル
- `[` / `]` : ブラシサイズ変更
- **`X` キー（神ショートカット）**: マスクペイント中に `X` を押すと、描画色（白）と消去色（黒）が一瞬で反転。消しゴムツールに持ち替えることなくスムーズに修正可能。

[📸 参考: fusako28_17_brush_shortcuts_x_key_toggle.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_17_brush_shortcuts_x_key_toggle.jpg)

### 5.2 手振れ補正（Lazy Mouse Distance: Dキー）
1. 口のリップラインやまつ毛などの繊細な線を引く際、手の震えで線がガタつくのを防止。
2. `D` キーを押して手振れ補正（Lazy Mouse）をオンにする。
3. グレーの円形ガイドが表示され、カーソルの軌跡を滑らかに追従・補正した美麗なストロークが引ける。

[📸 参考: fusako28_18_lazy_mouse_stabilizer_d_key.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_18_lazy_mouse_stabilizer_d_key.jpg)

### 5.3 2Dビューでのブラシサイズとガタつき対策
- **ブラシサイズが激しく変動する問題**: ブラシプロパティの `Size Space` を「Object」から **「Texture」** に変更。
- **ストロークがガタつく問題**: ブラシプロパティの `Alignment` を「Tangent Wrap」から **「UV」** に変更（※3Dビューで塗る時は Tangent Wrap が適正）。

[📸 参考: fusako28_19_brush_size_texture_alignment_uv.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_19_brush_size_texture_alignment_uv.jpg)

### 5.4 カスタムエアブラシ（Basic Super Soft）の作成とプリセット保存
1. ブラシ一覧から `Basic Soft` を選択。
2. プロパティ調整:
   - Flow（筆圧検知ON、値を極小に）
   - Stroke Opacity（極小に）
3. ブラシプレビュー上で右クリック $\to$ **`Create brush preset`** を実行。
4. プリセット名を「Basic Super Soft」とリネームして保存。アニメ調の繊細な影グラデーション塗りに常用可能。

[📸 参考: fusako28_20_airbrush_custom_preset_save.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_20_airbrush_custom_preset_save.jpg)

---

## 6. 透過テクスチャ作成とエクスポート・Blender連携

### 6.1 透過シェーダー設定と Opacity チャンネルの追加
1. 瞳ハイライト（Face_Transparent）を選択。
2. 画面右側の丸いシェーダーアイコンをクリックし、シェーダーを **`pbr-metal-rough-with-alpha-blending`** に切り替える。
3. Texture Set Settings の Channels で `+` を押し、**`Opacity`** チャンネルを追加。
4. 最下層の Fill Layer で Opacity を `0`（完全透明）に設定し、その上のレイヤーでハイライトをペイント。

[📸 参考: fusako28_21_alpha_blending_opacity_channel.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_21_alpha_blending_opacity_channel.jpg)

### 6.2 エクスポート設定：Output Template「Color with Alpha」作成
1. `File > Export Textures`（`Ctrl+Shift+E`）を開く。
2. 「Output templates」タブを開き、`PBR Metallic Roughness` を選択して複製アイコンをクリック。
3. テンプレート名を「Color with Alpha」に変更。
4. 1段目の「RGB + A」スロットのみを残し、他スロットを削除。
   - RGBに `Base Color (RGB)`、Aに `Opacity (A)` をアサイン。

[📸 参考: fusako28_22_export_template_color_with_alpha.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_22_export_template_color_with_alpha.jpg)

### 6.3 テクスチャのエクスポート実行
1. 「Settings」タブで出力フォルダを指定。
2. ファイル形式: `PNG` / 8-bit。
3. 通常マテリアル（Face, Hair）には「Document Channels + Alpha」等を指定し、透過マテリアルには「Color with Alpha」を指定してエクスポート。

[📸 参考: fusako28_23_texture_export_execution.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_23_texture_export_execution.jpg)

### 6.4 Blenderへの読み込みと色味・透過シェーダー構築
1. **色味くすみ解消（最重要）**:
   - Blenderのレンダープロパティ $\to$ `Color Management` $\to$ `View Transform` を「Filmic」から **「Standard」** に変更。SPと完全に同一の鮮やかな発色になる。
2. **透過ハイライトのシェーダーノード構成**:
   - `Emission`（Colorにテクスチャカラーを接続）
   - `Transparent BSDF`
   - `Mix Shader`（上がTransparent、下がEmission、FacにテクスチャのAlphaを接続）
   - マテリアルプロパティの Settings $\to$ Blend Mode を **`Alpha Hashed`**（または Alpha Clip）に設定。

[📸 参考: fusako28_24_blender_standard_color_alpha_node.jpg](../../docs/fusako_28_sp_basics_screenshots/fusako28_24_blender_standard_color_alpha_node.jpg)

---

## 7. トラブルシューティング＆チェックリスト

| 症状 / 課題 | 原因 | 解決策 |
|:---|:---|:---|
| 口の中や瞳の奥が狭くて塗れない | オブジェクトの重なり | `Shift+D > Z` で上空にオフセット配置し、塗り用とルック確認用を分離する。 |
| ベイク後にUVの継ぎ目で急に色が変わる | UVの重複（Overlapping） | `B` キーの World Space Normal で反転箇所を確認し、BlenderでUV修正後再読み込み。 |
| 境界線付近で隣のUV島の色が滲み出る | パディング設定の不一致 | UV Padding を「3D Space Neighbor」から **「UV Space Neighbor」** に変更。 |
| 2Dビューでブラシサイズが激しく変わる | ブラシが3Dサイズに追従している | ブラシの `Size Space` を「Object」から **「Texture」** に変更。 |
| 2Dビューでストロークが波打つ・ガタつく | 座標系アライメントの不一致 | ブラシの `Alignment` を「Tangent Wrap」から **「UV」** に変更。 |
| Blenderにテクスチャを貼ると色が白くくすむ | カラーマネジメントのFilmic変換 | レンダー設定の `Color Management > View Transform` を **「Standard」** に変更。 |
