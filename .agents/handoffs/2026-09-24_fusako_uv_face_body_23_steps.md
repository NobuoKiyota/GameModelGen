# 【ふさこ氏 3Dキャラ制作 第23回】顔・体のUV展開 完全技術仕様書

本ドキュメントは、YouTubeチュートリアル動画 **『【Blender】顔・体のUV展開！【キャラクターモデル制作！#23】』**（講師: ふさこ氏、時間: 27分29秒、URL: `https://www.youtube.com/watch?v=hwDyavPRVNE`）の内容を、Blender 3.6+ / 4.x に対応した詳細なステップバイステップ技術仕様として完全体系化したものである。

---

## 0. 本技術仕様の全体俯瞰と核心ポイント

### 0.1 本動画で解決する課題
1. **テクスチャ枚数・マテリアル分割の事前設計**:
   - モデリング完了後に無計画にUV展開を始めると、テクセル密度（解像度）のバラつき、ドローコール（描画負荷）の増大、透過テクスチャの混線が生じる。
   - **解決策**:
     - キャラクター全体を **「顔」「髪」「肌（体）」「服インナー」「服アウター」「アクセサリー」「透過（チーク・青ざめ・ハイライト）」** の単位でマテリアル・テクスチャ分割を事前定義。
2. **顔前面投影（Project from View）と側面歪みの解消**:
   - イラスト調セルルックでは、正面顔のテクスチャ描き込みが最重要となるため `Project from View` で正面から歪みなく投影したいが、側頭部や耳周りが強烈に引き伸ばされる。
   - **解決策**:
     - **ピン留め（Pin: `P` キー）と再展開**: 歪みのない正面中心の頂点群を `P` キーで赤くピン留め固定した上で `U > Unwrap` を実行。中心の美しい正面プロポーションを100%維持したまま、側面だけを自然に放射状緩和する。
     - **テクセル密度の意図的コントロール**: 髪で隠れる後頭部や側頭部は手動でUV幅を約半分に圧縮し、描き込みが密な顔面中央の解像度を最大限に節約・確保する。
     - **正中線・リップラインの直線化**: 2Dカーソルを利用して中心軸を `S X 0`、唇のラインを `S Y 0` で直線化し、リップやハイライト描画時の歪みを物理的に排除する。
3. **周辺パーツ（白目・まつ毛・口内ソケット・瞳・歯・舌）の最適展開**:
   - 立体まつ毛の表裏シーム分割と3D並び順に合わせたレイアウト。
   - 口内ソケットの長方形直線化（奥から手前へのグラデーションシェーディング対応）。
   - 瞳（Iris）を右上エリアに巨大確保し、微細なハイライト・アイテクスチャの描き込みに対応。

---

## 1. チャプター別・詳細ステップバイステップ手順

### Chapter 1: UV展開の事前準備と口内モデリング (00:00〜07:05)

#### Step 1-1: マテリアル・テクスチャ分割計画の策定
1. キャラクター全体の質感・シェーダー要件に合わせて、マテリアル（テクスチャ）を以下の単位に整理する。
   - **Face**: 顔肌、白目、瞳、まつ毛、眉、口内、歯、舌
   - **Hair**: 前髪、横髪、後ろ髪、ツインテール、アホ毛
   - **Body**: 首、鎖骨、胸、手、足（素肌露出部）
   - **Inner**: ワンピース、ドロワーズ、靴下
   - **Outer**: パーカー、フード、袖
   - **Accessory**: パッチン留め、羽、ポシェット、バッグ
   - **Transparent**: 目のハイライト、チーク、涙、漫符（透過専用）
   [📸 参考: 01_c1_uv_material_separation_plan.jpg](../../docs/fusako_23_uv_face_body_screenshots/01_c1_uv_material_separation_plan.jpg)

#### Step 1-2: 展開前の前提チェック（スケール適用と不可視メッシュ削除）
1. 全オブジェクトを選択し、`Ctrl + A` > **Rotation & Scale**（回転とスケール）を適用。スケールが `(1.0, 1.0, 1.0)` で均一でないとUVが扁平に歪む。
2. ソリッド化（Solidify）やベベル（Bevel）など、形状を変更するモディファイアを適用（Apply）。
3. ドロワーズや服で完全に隠れて見えない体幹・お尻の不要なポリゴン面を選択して削除（`X > Faces`）。テクスチャ容量とポリゴン数を節約。
   [📸 参考: 02_c1_apply_scale_and_cleanup_mesh.jpg](../../docs/fusako_23_uv_face_body_screenshots/02_c1_apply_scale_and_cleanup_mesh.jpg)

#### Step 1-3: 上の歯のモデリング（平面押し出し法）
1. `Shift + S` > **Cursor to World Origin**（原点配置）。
2. `Shift + A` > **Mesh > Plane** を追加。
3. 編集モードで `I`（インセット）後、中心面を削除。
4. `S Y 0` で直線を揃え、**Mirror** モディファイア（X軸、クリッピングON）を追加。
5. `Ctrl + 1` で **Subdivision Surface**（レベル1）を追加。
6. 前面エッジを下向きに押し出し (`E`)、U字型のアーチ状の歯並びを形成。
   [📸 参考: 03_c1_teeth_upper_model_plane_extrude.jpg](../../docs/fusako_23_uv_face_body_screenshots/03_c1_teeth_upper_model_plane_extrude.jpg)

#### Step 1-4: 下の歯の反転配置
1. 作成した上の歯を `Shift + D` で複製し、`Z` 軸方向に下げる。
2. `S` > `Z` > `-1` で上下を反転させ、下の歯の形状を瞬時に作成。
   [📸 参考: 04_c1_teeth_lower_duplicate_sz_minus1.jpg](../../docs/fusako_23_uv_face_body_screenshots/04_c1_teeth_lower_duplicate_sz_minus1.jpg)

#### Step 1-5: 舌のモデリング（立方体サブサーフ法）
1. `Shift + A` > **Mesh > Cube** を追加。
2. `S Z` で薄く押しつぶし、後方の面を削除。
3. **Mirror** モディファイアと **Subdivision Surface**（レベル1）を追加。
4. 前方に押し出し (`E`)、スプーン状の緩やかな曲面舌を作成。
   [📸 参考: 05_c1_tongue_model_cube_subsurf.jpg](../../docs/fusako_23_uv_face_body_screenshots/05_c1_tongue_model_cube_subsurf.jpg)

#### Step 1-6: 口内パーツのスケール調整と配置
1. 歯と舌を選択し、口内ソケットに入るサイズまで縮小 (`S`)。
2. アニメ調モデルの基準に倣い、口を大きく開けた時だけチラッと見えるコンパクトなサイズ感で配置。
3. `M` キーで管理用の `Head` コレクションへ移動。
   [📸 参考: 06_c1_mouth_parts_scale_fit_in_head.jpg](../../docs/fusako_23_uv_face_body_screenshots/06_c1_mouth_parts_scale_fit_in_head.jpg)

---

### Chapter 2: 顔肌（Face）のUV展開と歪み解消・ピン留め (07:05〜17:30)

#### Step 2-1: 正面ビューからの視点投影展開 (Project from View)
1. 顔オブジェクトを選択し、テンキー `1` で完全な正面視点（Front Orthographic）にする。
2. 編集モードで顔前面のメッシュ面を選択。
3. `U` > **Project from View**（視点から投影）を実行。
   [📸 参考: 07_c2_face_project_from_view.jpg](../../docs/fusako_23_uv_face_body_screenshots/07_c2_face_project_from_view.jpg)

#### Step 2-2: チェッカーテクスチャによる歪み可視化シェーダー構築
1. シェーダーエディタを開く。
2. `Shift + A` > **Texture > Checker Texture** を追加。
3. `Ctrl + T`（Node Wrangler）で **Texture Coordinate**（UV出力） $\to$ **Mapping** $\to$ **Checker Texture** を自動接続。
4. カラー出力をプリンシプルBSDFの **Base Color** に接続。
5. Scale を 20〜30 に上げてチェッカーの格子を細かく表示。
   [📸 参考: 08_c2_checker_texture_shader_setup.jpg](../../docs/fusako_23_uv_face_body_screenshots/08_c2_checker_texture_shader_setup.jpg)

#### Step 2-3: 側面・耳周りのチェッカーストレッチ（伸び）の確認
1. 3Dビューポートでマテリアルプレビュー（Zキー）を確認。
2. 正面は綺麗な正方形格子だが、側頭部やエラ、耳の付け根が極端に引き伸ばされて長方形・シワ状になっている課題を確認。
   [📸 参考: 09_c2_checker_stretch_display_issue.jpg](../../docs/fusako_23_uv_face_body_screenshots/09_c2_checker_stretch_display_issue.jpg)

#### Step 2-4: 正面中心頂点のピン留め (Pin: Pキー)
1. UVエディタのヘッダーで **UV Sync Selection**（UV選択同期）をONにする。
2. 歪みのない「目・鼻・口の周囲」の正面中心頂点ループを選択。
3. `P` キーを押下して **Pin**（ピン留め）を実行。固定された頂点が赤くマーキングされる。
   [📸 参考: 10_c2_pin_center_vertices_p_key.jpg](../../docs/fusako_23_uv_face_body_screenshots/10_c2_pin_center_vertices_p_key.jpg)

#### Step 2-5: ピン留め状態での再展開 (Unwrap) による側面緩和
1. 全選択 (`A`) し、`U` > **Unwrap**（展開）を実行。
2. **効果**: 赤くピン留めされた中心エリアの美しい正面形状は1ミリも動かず、側頭部や顎下の頂点だけが外側へ向かって自然に放射状に緩和展開され、チェッカーの伸びが一瞬で解消される。
   [📸 参考: 11_c2_pin_unwrap_side_expand.jpg](../../docs/fusako_23_uv_face_body_screenshots/11_c2_pin_unwrap_side_expand.jpg)

#### Step 2-6: 側頭部・こめかみのUV幅圧縮による解像度節約
1. こめかみや耳の後ろは髪の毛で隠れてほとんどテクスチャを描き込まない領域である。
2. UV Sync をOFFにし、側頭部の頂点ループを選択。
3. `G` キーで内側へ幅を狭めて圧縮。
4. 顔面中央（目元・頬・口）の専有面積比率が高まり、テクスチャ解像度が有効活用される。
   [📸 参考: 12_c2_compress_side_temple_uv_space.jpg](../../docs/fusako_23_uv_face_body_screenshots/12_c2_compress_side_temple_uv_space.jpg)

#### Step 2-7: 中心軸頂点の垂直一直線化 (`S X 0`)
1. 正中線上の1頂点を選択し、`Shift + S` > **Cursor to Selected**（2Dカーソルを吸着）。
2. ピボットポイントを **2D Cursor** に変更。
3. 顔の中心軸（額から鼻、顎先）の全頂点を選択。
4. `S` > `X` > `0` を実行。中心線が完全な垂直一直線に揃い、左右対称描画時のズレが根絶される。
   [📸 参考: 13_c2_align_center_axis_sx0_cursor.jpg](../../docs/fusako_23_uv_face_body_screenshots/13_c2_align_center_axis_sx0_cursor.jpg)

#### Step 2-8: 唇リップラインの水平直線化 (`S Y 0`)
1. ピボットポイントを **Bounding Box Center**（バウンディングボックス中心）に戻す。
2. 上唇・下唇の境界エッジループを選択。
3. `S` > `Y` > `0` で水平に一直線化。
4. **効果**: テクスチャペイント時に唇のハイライトやシャドウを描く際、斜めエッジのジャギーや歪みが生じなくなる。
   [📸 参考: 14_c2_flatten_mouth_lip_line_sy0.jpg](../../docs/fusako_23_uv_face_body_screenshots/14_c2_flatten_mouth_lip_line_sy0.jpg)

#### Step 2-9: 後頭部シームのクリアと頭部一体展開
1. 前後で分割していた頭部シームを `Ctrl + E` > **Clear Seam** で解除。
2. 前後一体のメッシュとして `U > Unwrap` を実行。
   [📸 参考: 15_c2_clear_back_head_seam_unwrap.jpg](../../docs/fusako_23_uv_face_body_screenshots/15_c2_clear_back_head_seam_unwrap.jpg)

#### Step 2-10: 後頭部UVの50%圧縮
1. 髪の毛で100%隠れる後頭部エリアの端部頂点を選択し、内側に折り返すように約半分に圧縮。
2. 圧縮した端部頂点を `P` でピン留めし、再展開。顔前面の解像度を奪わずに頭部全体を1つの島に収める。
   [📸 参考: 16_c2_compress_back_head_half_size.jpg](../../docs/fusako_23_uv_face_body_screenshots/16_c2_compress_back_head_half_size.jpg)

#### Step 2-11: Display Stretch オーバーレイによる歪み検証
1. UVエディタのヘッダー右端 > **Overlays** > **Display Stretch** にチェック。
2. 青色（歪みゼロ）〜シアン（許容範囲内）であることを確認。緑や赤の極端な歪み領域が存在しないことを目視確認。
   [📸 参考: 17_c2_display_stretch_overlay_heat_map.jpg](../../docs/fusako_23_uv_face_body_screenshots/17_c2_display_stretch_overlay_heat_map.jpg)

#### Step 2-12: Mirror U による左右展開と中心スナップ (X=0.5)
1. ミラーモディファイアの **Data** パネル > **Mirror U** にチェック。
2. UVエディタのオーバーレイ > **Modified Edges** をONにし、反転側のUV島を表示。
3. サイドバー（Nキー）> **View** > **2D Cursor** の Location X を `0.5` に設定。
4. 中心軸頂点を 2Dカーソル（X=0.5）にスナップ吸着（`S X 0`）。左右の顔が中央で美しく結合される。
   [📸 参考: 18_c2_mirror_u_modified_edges_display.jpg](../../docs/fusako_23_uv_face_body_screenshots/18_c2_mirror_u_modified_edges_display.jpg)

---

### Chapter 3: 目・口内・まつ毛・歯・舌のUV展開と配置 (17:30〜27:30)

#### Step 3-1: 白目（Sclera）メッシュの正面投影展開
1. 白目オブジェクトを選択し、テンキー `1`（正面ビュー）。
2. `U` > **Project from View** で正面投影。視線方向からの歪みがない状態で展開。
   [📸 参考: 19_c3_sclera_white_eye_project_view.jpg](../../docs/fusako_23_uv_face_body_screenshots/19_c3_sclera_white_eye_project_view.jpg)

#### Step 3-2: 口内ソケットの直線格子化展開 (Rectify)
1. 口内ソケットのメッシュを選択。
2. TexTools アドオンの **Rectify**（または手動でループを選択し `S X 0`、`S Y 0` で直角化）。
3. 綺麗な長方形グリッドに展開することで、奥（暗い赤）から手前（明るいピンク）へのグラデーションシェーディングの塗りが極めて容易になる。
   [📸 参考: 20_c3_mouth_interior_rectify_straight.jpg](../../docs/fusako_23_uv_face_body_screenshots/20_c3_mouth_interior_rectify_straight.jpg)

#### Step 3-3: 立体まつ毛の表裏シーム分割展開
1. まつ毛メッシュの外周エッジを選択し、`Ctrl + E` > **Mark Seam**。
2. 前面と背面が2枚の板として綺麗に分離するようにシームを配置。
3. `U > Unwrap` で展開。中央にエッジが入っている方が前面（テクスチャ描き込み面）となる。
   [📸 参考: 21_c3_eyelashes_mark_seam_front_back.jpg](../../docs/fusako_23_uv_face_body_screenshots/21_c3_eyelashes_mark_seam_front_back.jpg)

#### Step 3-4: まつ毛の3D並び順に合わせたレイアウト
1. UVエディタ上でまつ毛の各島を選択し、3Dビューでの並び順（目頭・中央・目尻）と一致するように横並びに配置。
2. 直感的に「どれがどのまつ毛か」が一目で判別でき、ペイント作業時の混乱を防止。
   [📸 参考: 22_c3_eyelashes_layout_order_matching_3d.jpg](../../docs/fusako_23_uv_face_body_screenshots/22_c3_eyelashes_layout_order_matching_3d.jpg)

#### Step 3-5: 瞳とハイライトの分離と高解像度配置
1. 瞳メッシュ内のハイライト面を選択し、`P` > **Selection** で別オブジェクトに分離（透過テクスチャ用として確保）。
2. 残った瞳（Iris）メッシュのUV島を、テクスチャ領域の右上エリアに大きく拡大して配置。キャラクターの命である瞳の微細なグラデーション・ハイライト描き込みのための最大テクセル密度を確保。
   [📸 参考: 23_c3_separate_eye_highlight_iris_uv.jpg](../../docs/fusako_23_uv_face_body_screenshots/23_c3_separate_eye_highlight_iris_uv.jpg)

#### Step 3-6: 歯・舌の統合と顔テクスチャ正方形内への集約完了
1. 歯と舌を `Ctrl + J` で1つのオブジェクトに統合。
2. 白目、まつ毛、口内ソケット、歯、舌のUV島を、顔テクスチャの正方形（UV 0.0〜1.0）の空きスペース（右上・上部）へ干渉しないように効率よくパズル配置して完了。
   [📸 参考: 24_c3_teeth_tongue_join_head_uv_layout.jpg](../../docs/fusako_23_uv_face_body_screenshots/24_c3_teeth_tongue_join_head_uv_layout.jpg)

---

## 2. 実装チェックリスト（トラブルシューティング）

| 現象 | 主な原因 | 確実な解決策 |
| :--- | :--- | :--- |
| UV展開すると形が横や縦にペチャンコにつぶれる | オブジェクトのスケールが `(1.0, 1.0, 1.0)` になっていない | オブジェクトモードで `Ctrl + A > Scale` を適用してから再展開する。 |
| 正面投影（Project from View）で耳や側頭部が激しく伸びる | 視線と直交する面ほどテクセルが薄くなるため | 正面中心の歪みのない頂点を `P` でピン留めし、`U > Unwrap` で側面を自然放射展開させる。 |
| 口紅やリップラインを描くと斜めのジャギー・歪みが出る | リップ境界エッジがUV上で波打っている | 境界エッジループを選択し、`S Y 0` で水平一直線化する。 |
| ミラーの反対側のUVが重なっていて左右別々に描けない | ミラーモディファイアの「Mirror U」が無効 | Mirrorモディファイアの **Mirror U** にチェックを入れ、中心をX=0.5にスナップする。 |
| 口内の陰影を塗るとテクスチャが歪んで曲がる | 口内ソケットが扇形に歪んで展開されている | TexTools の **Rectify** または手動 `S X 0` / `S Y 0` で綺麗な長方形グリッドに直角化する。 |
