# ふさこ氏 Blenderキャラクター制作 #30 (SP #03)『髪のペイント』完全技術仕様書

元動画: [Substance Painterでテクスチャペイント！#30 (03) | 髪のペイント 〜初中級者向けチュートリアル〜](https://www.youtube.com/watch?v=3a7os-XHBTU)  
動画ID: `3a7os-XHBTU` / 再生時間: 18分19秒  
対象バージョン: Blender 3.6+ / 4.x、Substance 3D Painter 7.x / 8.x / 9.x / 10.x 対応  
スクリーンショットカタログ: [docs/fusako_30_sp_hair_paint_screenshots/README.md](../../docs/fusako_30_sp_hair_paint_screenshots/README.md)

---

## 1. 概要と髪ペイントにおけるプロシージャル×手描きの融合

本チュートリアル（Substance Painter編 第3回）では、アニメ調3Dキャラクターモデルで最も情報量と印象を左右する「髪（Hair）」のテクスチャペイントを体系的に学習します。  
手描きによる毛束の陰影・ハイライト表現に加え、SPならではの強力なジェネレーター「3D Distance」を用いた立体グラデーション制御、裏面のない板ポリゴン前髪に対する「UV Border ＋ Blur ＋ Histogram Scan」による美麗なアウトライン線画自動生成など、作業効率と品質を劇的に高めるプロのテクニックを網羅します。

[📸 参考: fusako30_01_hair_paint_intro.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_01_hair_paint_intro.jpg)

### 髪ペイントの核心的技術ポイント
1. **【神技】Add generator > 3D Distance による球体立体グラデーション**:
   - 3D空間上の中心球（Position XYZ, Radius, Contrast）を基準にプロシージャルなマスクグラデーションを生成。
   - 頭頂部の天使の輪（トップライト）、毛先フェード、および手描き影レイヤーの上部フェードアウト（Darken合成）に絶大な威力を発揮。
2. **【神技】板ポリ前髪のアウトライン線画ピクセルジャギー根絶レシピ**:
   - 背面法アウトラインが使えない板ポリ前髪に対し、テクスチャ線画を生成。
   - `UV Border`（0.04） $\to$ `Add filter > Blur` でぼかし $\to$ `Add filter > Histogram Scan` でエッジを滑らかに再引き締め！
   - 手描き特有の歪みやピクセル階段（ジャギー）のない、極めて滑らかなアニメ輪郭線を実現。
3. **髪の多層セルシェーディング構造**:
   - ベースカラー（頭頂部ピンク〜毛先フェードの3D Distance）
   - 1号影（毛束の大きな落ち影）
   - 2号影（重なり合う奥深い溝の濃色影）
   - 内側・頭皮側（裏面）の紫ベタ（Polygon FillのUV Chunk Fillで一括アサイン）
   - ハイライト（ツヤと天使の輪）
4. **後ろ髪（資料のない部位）のペイント戦略**:
   - 後頭部は左右独立展開だが、初期段階は `L`（Symmetry）で対称にベース影を配置し、後から非対称の毛流れやアクセントを加筆。
5. **Blenderへのテクスチャ再インポートとAuto Reloadアドオン**:
   - SPエクスポート後、Blender側で複数画像をワンクリックまたはタイマーで自動更新。

---

## 2. 3D Distance ジェネレーターの基本と活用法

### 2.1 3D Distance ジェネレーターの追加と確認
1. テクスチャセットリストから「Hair」を選択。
2. 明るいハイライト色の Fill Layer を作成し、黒マスクを追加。
3. 黒マスクを右クリック $\to$ **`Add generator`** $\to$ **`3D Distance`** を選択。
4. `C` キーを押してマスク表示に切り替え、3D空間上の球体グラデーションを確認。

[📸 参考: fusako30_02_3d_distance_generator_intro.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_02_3d_distance_generator_intro.jpg)

### 2.2 パラメータ調整による球体制御
1. **Radius（半径）**: 球の大きさを調整。
2. **Contrast（コントラスト）**: 境界のボケ具合（クッキリ〜ふんわり）を調整。
3. **Position X / Y / Z**: 球の中心位置を頭頂部や毛先へ移動。
4. これにより、3Dモデルの凹凸やUVアイランドの継ぎ目を意識することなく、空間基準の完全なグラデーションが生成される。

[📸 参考: fusako30_03_3d_distance_params_adjust.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_03_3d_distance_params_adjust.jpg)
[📸 参考: fusako30_04_top_light_tip_gradient_concept.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_04_top_light_tip_gradient_concept.jpg)

---

## 3. 髪の基本陰影・裏面塗り分けと影フェードアウト

### 3.1 1号影・ハイライトの初期ペイント
1. 髪の影用 Fill Layer（中間紫色）を作成し、黒マスク ＋ Paint Layer を追加。
2. 前髪やサイドの毛束に沿ってざっくりと落ち影を描く。
3. ハイライト用 Fill Layer も同様に追加し、毛束の山部分にツヤを配置。

[📸 参考: fusako30_06_hair_shadow_1_stroke.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_06_hair_shadow_1_stroke.jpg)
[📸 参考: fusako30_07_hair_highlight_layer_prep.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_07_hair_highlight_layer_prep.jpg)

### 3.2 髪の内側・裏面のポリゴンフィル（UV Chunk Fill）
1. 髪の内側（頭皮側・裏面）は濃い紫色で塗りつぶす。
2. キーボードの `4`（Polygon Fill）を選択し、一番右の `UV Chunk Fill` モードを選択。
3. 裏面にあたるUV島を順次クリックし、一括でマスクを塗り分ける。

[📸 参考: fusako30_08_hair_inner_polygon_fill.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_08_hair_inner_polygon_fill.jpg)

### 3.3 2号影の追加と 3D Distance による影フェードアウト
1. さらに奥まった箇所に深みを与えるため、2号影（最深部シャドウ）の Fill Layer を追加。
2. 毛束の奥をペイント。
3. **【神Tips】影の上部フェードアウト**:
   - 手描きした影マスクの上に `Add generator > 3D Distance` を追加。
   - `Invert: True` に設定し、頭頂部付近が黒くなるように調整。
   - ジェネレーターのブレンドモードを **`Darken`（比較暗）** または `Multiply`（乗算）に変更。
   - 手描きした影が、頭頂部に向かって自然にふわっと薄く消える美しいアニメ調減衰が自動完成する。

[📸 参考: fusako30_09_hair_shadow_2_depth.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_09_hair_shadow_2_depth.jpg)
[📸 参考: fusako30_10_shadow_mask_3d_distance_invert.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_10_shadow_mask_3d_distance_invert.jpg)
[📸 参考: fusako30_11_shadow_mask_darken_blend.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_11_shadow_mask_darken_blend.jpg)

---

## 4. 板ポリ前髪のアウトライン線画ピクセルジャギー根絶レシピ

### 4.1 線画の課題とUV Borderの適用
1. 前髪など裏面のないペラペラの板ポリゴンは、UnityやBlenderの背面法アウトラインシェーダーが効かない。
2. そのためテクスチャ内に線画を描く必要があるが、手描きや単純なUV Borderだけではピクセルのガタつき（ジャギー）が目立ってしまう。
3. 濃紺色の線画用 Fill Layer を作成し、黒マスクに `Add generator > UV Border` を追加（Balance: 0.04程度）。

[📸 参考: fusako30_05_flat_hair_outline_challenge.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_05_flat_hair_outline_challenge.jpg)
[📸 参考: fusako30_12_flat_hair_uv_border_init.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_12_flat_hair_uv_border_init.jpg)

### 4.2 【秘伝レシピ】Blur ＋ Histogram Scan によるエッジ再引き締め
1. UV Border の上に **`Add filter > Blur`** を追加し、わずかに数値を上げてジャギーをぼかす。
2. その上にさらに **`Add filter > Histogram Scan`** を追加。
3. `Position` スライダーを調整すると、ぼやけたグラデーションが滑らかなアンチエイリアス曲線として再引き締めされ、**ガタガタしたピクセル感が完全に消失した美麗なベクター調のアウトライン** が生成される！

[📸 参考: fusako30_13_uv_border_blur_filter.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_13_uv_border_blur_filter.jpg)
[📸 参考: fusako30_14_histogram_scan_clean_edge.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_14_histogram_scan_clean_edge.jpg)

### 4.3 前髪以外の不要線マスク除外と手作業仕上げ
1. このままでは全UV島のフチに線が出てしまうため、すぐ上に新規レイヤーを追加。
2. キーボードの `4`（Polygon Fill）で一旦全島を黒塗りし、前髪の必要な島だけを白塗りにする。
3. レイヤーのブレンドモードを **`Multiply`（乗算）** または `Darken` にして前髪部分のみに限定。
4. 最上層に Paint Layer を追加し、頭頂部の不要な境界線を消去し、毛先の尖りや線の入り抜きを手作業で微調整する（`D` キーの手振れ補正を活用）。

[📸 参考: fusako30_15_polygon_fill_mask_cleanup.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_15_polygon_fill_mask_cleanup.jpg)
[📸 参考: fusako30_16_multiply_blend_outline_extract.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_16_multiply_blend_outline_extract.jpg)
[📸 参考: fusako30_17_hand_painted_line_refinement.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_17_hand_painted_line_refinement.jpg)

---

## 5. ベースカラーの立体グラデーションと全体仕上げ

### 5.1 髪ベース色の上下グラデーション（3D Distance）
1. 髪のベースカラーにおいて、前髪下部・頭頂部・毛先の微妙な色相変化を表現。
2. ベース色のFill Layerの上に、明るいピンクのFill Layerを追加。
3. 黒マスクに `3D Distance` を追加し、Position Z（高さ）を調整して上部のみをほんのり明るくグラデーション。
4. 毛先にも同様に `3D Distance`（Invert True）でわずかに暗い色をフェードイン。

[📸 参考: fusako30_18_front_hair_detail_polishing.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_18_front_hair_detail_polishing.jpg)
[📸 参考: fusako30_19_base_hair_3d_distance_gradient.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_19_base_hair_3d_distance_gradient.jpg)
[📸 参考: fusako30_20_front_hair_complete_view.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_20_front_hair_complete_view.jpg)

### 5.2 後ろ髪のペイント（対称から非対称への移行）
1. 設定資料のない後ろ髪は、周囲のテイストと整合するように想像を膨らませてペイント。
2. 最初は `L` キーで Symmetry をオンにし、左右対称に大きな毛束の陰影・ハイライトを配置。
3. その後 Symmetry をオフにし、手作業で毛流れに左右非対称のニュアンスや遊びを加えて自然な仕上がりに導く。

[📸 参考: fusako30_21_back_hair_symmetry_to_asymmetry.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_21_back_hair_symmetry_to_asymmetry.jpg)
[📸 参考: fusako30_22_hair_paint_overall_finishing.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_22_hair_paint_overall_finishing.jpg)

---

## 6. エクスポートとBlender「Auto Reload」連携

### 6.1 テクスチャエクスポート
1. `File > Export Textures`（`Ctrl+Shift+E`）を開く。
2. 透過ハイライト（Face_Transparent）には「Color with Alpha」を適用。
3. Face、Hairなどの通常テクスチャには「Document Channels + Normal + AO with Alpha」を指定してエクスポート。

[📸 参考: fusako30_23_texture_export_global_settings.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_23_texture_export_global_settings.jpg)

### 6.2 Blenderでの一括自動更新（Auto Reloadアドオン）
1. Blender側で更新画像が複数枚ある場合、1枚ずつ画像エディターでリロードするのは非効率。
2. 無料アドオン **「Auto Reload」** を導入。
3. Nパネルの Auto Reload タブから `Reload Images` を押すだけで、Blenderプロジェクト内の全テクスチャが一瞬で最新状態に更新される（タイマー自動監視も可能）。

[📸 参考: fusako30_24_blender_auto_reload_addon_import.jpg](../../docs/fusako_30_sp_hair_paint_screenshots/fusako30_24_blender_auto_reload_addon_import.jpg)

---

## 7. トラブルシューティング＆チェックリスト

| 症状 / 課題 | 原因 | 解決策 |
|:---|:---|:---|
| 板ポリゴン前髪のアウトライン線画がガタガタする | UV Borderのピクセル階段 | `UV Border` ＋ `Blur` ＋ **`Histogram Scan`** の合わせ技で滑らかに再引き締め。 |
| 髪の影が頭頂部まで濃く残って重苦しい | 手描き影が一律の濃さ | 影マスクに **`3D Distance`（Invert: True）** を追加し、ブレンドモード `Darken` で上部をフェードアウト。 |
| 天使の輪や頭頂部ハイライトが歪む | UV展開の歪みに依存 | UVに依存しない3D空間基準の **`3D Distance`** ジェネレーターで球体ハイライトを配置。 |
| まつ毛や前髪の裏側が透けたり色抜けする | 裏面の塗り残し | キーボード `4`（Polygon Fill）の `UV Chunk Fill` で裏面アイランドを一発塗りつぶし。 |
| SPでテクスチャ更新するたびにBlender再読み込みが面倒 | Blender標準の手動リロード | **「Auto Reload」** アドオンを導入し、`Reload Images` で全テクスチャを一括更新。 |
