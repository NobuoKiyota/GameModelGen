# 【ふさこ氏 3Dキャラ制作 第24回】髪のUV展開・猫耳パッキング 完全技術仕様書

本ドキュメントは、YouTubeチュートリアル動画 **『【Blender】髪のUV展開！【キャラクターモデル制作！#24】』**（講師: ふさこ氏、時間: 28分32秒、URL: `https://www.youtube.com/watch?v=caWYi7sJmrM`）の内容を、Blender 3.6+ / 4.x に対応した詳細なステップバイステップ技術仕様として完全体系化したものである。

---

## 0. 本技術仕様の全体俯瞰と核心ポイント

### 0.1 本動画で解決する課題
1. **多重毛束（前髪・横髪・後ろ髪・ツインテール）の効率的シーム分割**:
   - 複雑な立体感を持つ毛束を闇雲に展開すると、ねじれや表裏の重なり、極端な歪みが生じる。
   - **解決策**:
     - 生え際の根元ループ ＋ 表側（見せる側）と裏側（頭皮側）を二分する側面エッジへのシーム配置（`Mark Seam`）。
     - クリース（Crease）がかかっているエッジを `Shift + G > Crease` で一発選択し、シームに一括変換。
     - **不可視メッシュの徹底削除**: 髪内部や頭頂に埋まって絶対に見えない根元面を `X > Faces` で完全消去し、UV島の数とメモリを削減。
2. **【神Tips】表側と裏側の解像度（テクセル密度）差別化**:
   - テクスチャ解像度は有限（通常 2048x2048 または 4096x4096）。全毛束を等倍で並べると、重要な前髪の描き込みエリアが圧迫される。
   - **解決策**:
     - 表側（ハイライトや毛束ラインを描く面）：`Scale: 1.0` で高解像度確保。
     - 裏側（頭皮側・影色で塗りつぶすだけの面）：**`S 0.5` で面積を25%（寸法50%）に縮小**。余った広大なUV空間を主要前髪3本の拡大に再投資する。
3. **曲がった毛束（三日月カーブ）の直線化による専有面積圧縮**:
   - バナナ型や三日月型に湾曲した毛束は、UV正方形の中で対角線上に広大なデッドスペース（使えない隙間）を生み出す。
   - **解決策**: 中心線を `S X 0` 等で直線化し、`P` でピン留めした上で `U > Unwrap`。長方形に近いスリムな島に変形させ、パッキング密度を劇的に向上させる。
4. **猫耳パーツのマテリアル帰属の最適解（表情シェイプキー連動）**:
   - 猫耳を「髪」と「顔」のどちらのマテリアル・テクスチャに統合すべきか？
   - **結論**: 表情シェイプキー（笑顔や照れで耳がピョコッと動く等）で顔メッシュと連動させる場合、顔と猫耳を同一オブジェクト・同一マテリアルにまとめるのが業界標準。そのため、猫耳は前回の「顔テクスチャ（Face UV）」の空きスペースへ統合パッキングする。

---

## 1. チャプター別・詳細ステップバイステップ手順

### Chapter 1: 髪パーツのシーム分割と表裏解像度コントロール (00:00〜12:30)

#### Step 1-1: 髪用チェッカーテクスチャマテリアルの設定
1. 髪オブジェクトを表示し、新規マテリアル `M_Hair_Checker` を作成。
2. シェーダーエディタで `Texture Coordinate`（UV） $\to$ `Mapping` $\to$ `Checker Texture` $\to$ `Base Color` を接続。
3. 3Dビューポートでマテリアルプレビュー（Zキー）にし、チェッカー格子の歪みをリアルタイム確認できるようにする。
   [📸 参考: 01_c1_hair_checker_texture_setup.jpg](../../docs/fusako_24_uv_hair_screenshots/01_c1_hair_checker_texture_setup.jpg)

#### Step 1-2: 前髪センター（板ポリゴン）の展開と直線化
1. センターの前髪（板ポリゴン）を選択。
2. シームを入れずにそのまま `U` > **Unwrap**。
3. `R` で回転させ、中央のエッジラインがほぼ垂直（Y軸平行）になるよう整列。
   [📸 参考: 02_c1_bangs_center_plane_straight_unwrap.jpg](../../docs/fusako_24_uv_hair_screenshots/02_c1_bangs_center_plane_straight_unwrap.jpg)

#### Step 1-3: Mirror U による主要前髪の非対称ペイント準備
1. 前髪のミラーモディファイアの **Data** パネル > **Mirror U** にチェック。
2. **理由**: 前髪の主要な3本は左右非対称なハイライト・グラデーションを描き込むため、UV島を左右で重ねずに分離してテクスチャ領域に配置する。
   [📸 参考: 03_c1_mirror_u_asymmetric_hair_coloring.jpg](../../docs/fusako_24_uv_hair_screenshots/03_c1_mirror_u_asymmetric_hair_coloring.jpg)

#### Step 1-4: 立体毛束の生え際・表裏シーム分割
1. 前髪サイド・横髪の立体毛束の編集モードに入る。
2. 毛束が生え始める根元の円周エッジループを選択し、`Ctrl + E` > **Mark Seam**。
3. 表側（正面に見える面）と裏側（頭皮側・影側）の境界となる側面エッジを選択し、`Ctrl + E` > **Mark Seam**。
4. 全選択 (`A`) して `U > Unwrap`。表と裏の2枚の短冊状に綺麗に開かれることを確認。
   [📸 参考: 04_c1_hair_root_and_side_seam_mark.jpg](../../docs/fusako_24_uv_hair_screenshots/04_c1_hair_root_and_side_seam_mark.jpg)

#### Step 1-5: 【神技】裏面アイランドの50%縮小 (S 0.5) による解像度節約
1. UVエディタ上で、中央にエッジが入っていない「裏面」の島を選択。
2. `S` > `0.5` を入力してサイズを半分（面積1/4）に縮小。
3. **効果**: 影色でベタ塗りするだけの裏面の無駄なテクスチャ消費を最小限に抑え、表面の描き込み解像度を大幅に増強。
   [📸 参考: 05_c1_back_face_scale_down_half_s05.jpg](../../docs/fusako_24_uv_hair_screenshots/05_c1_back_face_scale_down_half_s05.jpg)

#### Step 1-6: 根元・頭頂内部の不可視メッシュ削除
1. 3Dビューポートで頭皮の内側に入り込んでいる毛束の根元面を選択。
2. どのカメラ角度からも絶対に見えないポリゴン面を `X` > **Faces** で削除。
3. 再度 `U > Unwrap` を実行し、不要な根元キャップのUV島を消去。
   [📸 参考: 06_c1_invisible_root_faces_delete.jpg](../../docs/fusako_24_uv_hair_screenshots/06_c1_invisible_root_faces_delete.jpg)

#### Step 1-7: ツインテールの表裏シーム分割
1. ツインテールオブジェクトを選択。
2. 大きなカール毛束の側面エッジを選択し、`Ctrl + E` > **Mark Seam**。
3. 表側と裏側の2大ブロックに分割して展開。
   [📸 参考: 07_c1_twintails_seam_and_unwrap.jpg](../../docs/fusako_24_uv_hair_screenshots/07_c1_twintails_seam_and_unwrap.jpg)

#### Step 1-8: 毛束割れ（スプリット）の溶接とピン留め
1. 展開時に毛先の間がパックリと裂けてしまった場合、先端の対向する頂点をボックス選択。
2. `S` > `0` で頂点を同位置に重ね、`P` でピン留め。
3. 裂けた部分のピン留めを `Alt + P` で解除し、再度 `U > Unwrap` を実行して自然な一体化毛束に戻す。
   [📸 参考: 08_c1_pin_and_weld_split_hair_island.jpg](../../docs/fusako_24_uv_hair_screenshots/08_c1_pin_and_weld_split_hair_island.jpg)

#### Step 1-9: 後ろ髪のクリース（Crease）からシームへの一括変換
1. 後ろ髪オブジェクトの編集モードに入る。
2. モデリング時にシャープエッジ用につけたクリースエッジを1本選択。
3. `Shift + G` > **Crease**（クリース）を実行し、同一クリース値のエッジを一括選択。
4. `Ctrl + E` > **Mark Seam** でシームに変換。
   [📸 参考: 09_c1_backhair_select_similar_crease.jpg](../../docs/fusako_24_uv_hair_screenshots/09_c1_backhair_select_similar_crease.jpg)

#### Step 1-10: 不要クリースのクリア
1. サイドバー（Nキー）> **Item** > **Edge Data** > **Mean Crease** の数値を `0.0` にスライドしてリセット。
   [📸 参考: 10_c1_clear_crease_weight_to_zero.jpg](../../docs/fusako_24_uv_hair_screenshots/10_c1_clear_crease_weight_to_zero.jpg)

#### Step 1-11: 後ろ髪ブロックシームの追加
1. 重なり合う後ろ髪の毛束ブロックの境界エッジにシームを追加し、各房が独立して綺麗に開くように分割。
   [📸 参考: 11_c1_backhair_lock_bundle_seam.jpg](../../docs/fusako_24_uv_hair_screenshots/09_c1_backhair_select_similar_crease.jpg)

#### Step 1-12: 後ろ髪上面・側面の展開チェック
1. 後ろ髪の外側（見える面）を選択し、`U > Unwrap`。
2. 各ブロックが重なり合わずに綺麗に長方形・短冊状に展開されることを確認。
   [📸 参考: 12_c1_backhair_top_seam_and_unwrap.jpg](../../docs/fusako_24_uv_hair_screenshots/12_c1_backhair_top_seam_and_unwrap.jpg)

#### Step 1-13: スナップ（頂点吸着）によるUV頂点結合
1. `Shift + Tab` でUVスナップをON（Snap to: Vertex）。
2. 近接したエッジ同士を吸着結合し、UV島を整理。
   [📸 参考: 13_c1_snap_and_weld_overlapping_uv.jpg](../../docs/fusako_24_uv_hair_screenshots/13_c1_snap_and_weld_overlapping_uv.jpg)

---

### Chapter 2: 髪UVのパズルパッキングとカーブ直線化 (12:30〜22:45)

#### Step 2-1: Modified Edges によるミラー反転側UVの可視化
1. UVエディタのオーバーレイメニュー > **Modified Edges** にチェック。
2. ミラーモディファイアで生成される反対側のUV島をゴースト表示し、島同士の重なりをチェック。
   [📸 参考: 14_c2_modified_edges_overlay_check.jpg](../../docs/fusako_24_uv_hair_screenshots/14_c2_modified_edges_overlay_check.jpg)

#### Step 2-2: 全髪オブジェクトの複数同時編集モード
1. オブジェクトモードで前髪、横髪、後ろ髪、ツインテールをすべて `Shift` 選択。
2. `Tab` キーを押して全オブジェクト同時に編集モードへ入る。
3. `A`（全選択）で髪全体のすべてのUV島をUVエディタ上に一括表示。
   [📸 参考: 15_c2_all_hair_objects_multi_edit.jpg](../../docs/fusako_24_uv_hair_screenshots/15_c2_all_hair_objects_multi_edit.jpg)

#### Step 2-3: Average Islands Scale によるテクセル密度の均一化
1. UVエディタ上で全選択 (`A`)。
2. **UV > Average Islands Scale**（アイランドの平均スケール）を実行。
3. 3Dメッシュの物理的表面積比率に合わせて、全UV島のスケールが自動的に均一化される。
   [📸 参考: 16_c2_average_islands_scale_apply.jpg](../../docs/fusako_24_uv_hair_screenshots/16_c2_average_islands_scale_apply.jpg)

#### Step 2-4: 【極意】三日月カーブ毛束の直線化 (`S X 0`) による省スペース化
1. **課題**: 三日月型やS字型に湾曲した毛束は、バウンディングボックス内に広大な無駄スペース（デッドスペース）を作る。
2. **解決手順**:
   - カーブした毛束の中央エッジループを選択。
   - `S` > `X` > `0` で垂直一直線に揃える。
   - 直線化した頂点を `P` キーでピン留め。
   - 再度 `U > Unwrap` を実行。毛束全体がスリムな長方形に整列し、専有面積が約半分に圧縮される。
   [📸 参考: 17_c2_straighten_curved_hair_island_sx0.jpg](../../docs/fusako_24_uv_hair_screenshots/17_c2_straighten_curved_hair_island_sx0.jpg)

#### Step 2-5: 主要前髪3本のUV拡大配置
1. 視線が集中し、最も描き込み密度の高い「主要前髪3本」の島を選択。
2. 空いたスペースを活用して約1.2〜1.5倍に拡大配置。
   [📸 参考: 18_c2_enlarge_high_detail_bangs_islands.jpg](../../docs/fusako_24_uv_hair_screenshots/18_c2_enlarge_high_detail_bangs_islands.jpg)

#### Step 2-6: ブリード防止マージン確保と髪UVパッキング完了
1. UV島同士が近すぎると、ミップマップ生成時やゲームエンジン内で隣の色がにじむ（カラーブリード）。
2. 各島間に適正なマージン（8〜16ピクセル相当の隙間）を空けてパズル状に敷き詰め、髪UVが完全完了。
   [📸 参考: 19_c2_hair_uv_packing_margin_spacing.jpg](../../docs/fusako_24_uv_hair_screenshots/19_c2_hair_uv_packing_margin_spacing.jpg)

---

### Chapter 3: 猫耳のUV展開と顔テクスチャへの統合パズル (22:45〜28:30)

#### Step 3-1: 猫耳の表裏シーム分割展開
1. 猫耳オブジェクトの編集モードに入る。
2. 外側の毛（表）と内耳のピンク面（裏）の境界エッジに `Mark Seam`。
3. `U > Unwrap` で展開。
   [📸 参考: 20_c3_kemomimi_outer_inner_seam_mark.jpg](../../docs/fusako_24_uv_hair_screenshots/20_c3_kemomimi_outer_inner_seam_mark.jpg)

#### Step 3-2: 内耳毛束の Rectify 直角格子化
1. 内耳から飛び出している細かな毛束を選択。
2. TexTools アドオンの **Rectify**（四角化）を実行。
3. 三角面で崩れる箇所は綺麗に開いた頂点を `P` ピン留めして再展開し、長方形に整列。
   [📸 参考: 21_c3_rectify_inner_ear_fluff_tufts.jpg](../../docs/fusako_24_uv_hair_screenshots/21_c3_rectify_inner_ear_fluff_tufts.jpg)

#### Step 3-3: Sort H による毛束島の一列自動整列
1. UVエディタを島選択モード（Island Selection）にする。
2. 内耳の毛束の島を全選択。
3. TexTools > **Sort H**（水平ソート）を実行。全毛束が一瞬で横一列に綺麗に整列する。
   [📸 参考: 22_c3_sort_horizontal_align_tufts.jpg](../../docs/fusako_23_uv_face_body_screenshots/22_c3_eyelashes_layout_order_matching_3d.jpg)

#### Step 3-4: 猫耳の「顔マテリアル」への統合と一括選択
1. 表情シェイプキー（感情変化による耳のピクピク動作）を顔オブジェクトと一体制御するため、猫耳のマテリアルを `M_Face` に変更。
2. 顔、白目、瞳、口内、歯、舌、猫耳をすべて選択して編集モードへ入る。
   [📸 参考: 23_c3_face_and_ears_multi_selection.jpg](../../docs/fusako_24_uv_hair_screenshots/23_c3_face_and_ears_multi_selection.jpg)

#### Step 3-5: 顔・耳パーツの最終統合パッキング完了
1. 猫耳の外殻および内耳の毛束島を、顔UV正方形の空きスペース（右上・上部）へ干渉なくパズル配置。
2. 顔テクスチャ（Face 1枚）および髪テクスチャ（Hair 1枚）のUV展開とパッキングが100%美しく完了。
   [📸 参考: 24_c3_final_face_and_ears_uv_layout.jpg](../../docs/fusako_24_uv_hair_screenshots/24_c3_final_face_and_ears_uv_layout.jpg)

---

## 2. 実装チェックリスト（トラブルシューティング）

| 現象 | 主な原因 | 確実な解決策 |
| :--- | :--- | :--- |
| 毛束のUVが三日月型に曲がってスペースを圧迫する | 毛束の自然なカーブ形状のまま展開されている | 中心エッジを `S X 0` で垂直直線化し、`P` ピン留めして再展開する。 |
| 髪のテクスチャ解像度が足りず前髪がボケる | 見えない裏側まで等倍でUV面積を消費している | 頭皮側の裏面島を `S 0.5` で50%縮小し、主要前髪を1.5倍に拡大する。 |
| テクスチャペイント時に隣の毛束の色がにじむ | UV島同士の間隔（マージン）が狭すぎる | 各島の間に最低8〜16ピクセル相当のマージンを確保してパッキングする。 |
| クリースをつけたエッジを再度探すのが大変 | 編集モードで手動選択しようとしている | `Shift + G > Crease` で同一クリースエッジを一発選択し `Mark Seam` する。 |
| 猫耳の表情シェイプキーが顔と別れて動かせない | 猫耳が顔と別マテリアル・別オブジェクトになっている | 猫耳のマテリアルを顔（Face）に統合し、1枚のテクスチャ内にパッキングする。 |
