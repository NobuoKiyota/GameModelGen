# ふさこ氏 Blenderキャラクター制作 #29 (SP #02)『顔のペイント』完全技術仕様書

元動画: [Substance Painterでテクスチャペイント！#29 (02) | 顔のペイント 〜初中級者向けチュートリアル〜](https://www.youtube.com/watch?v=tayBUmjCFt8)  
動画ID: `tayBUmjCFt8` / 再生時間: 26分03秒  
対象バージョン: Blender 3.6+ / 4.x、Substance 3D Painter 7.x / 8.x / 9.x / 10.x 対応  
スクリーンショットカタログ: [docs/fusako_29_sp_face_paint_screenshots/README.md](../../docs/fusako_29_sp_face_paint_screenshots/README.md)

---

## 1. 概要と顔パーツテクスチャペイントの設計思想

本チュートリアル（Substance Painter編 第2回）では、キャラクターの命である「顔（瞳、ハイライト、まつ毛、口腔・歯・舌、耳）」のテクスチャペイントを実践します。  
特にアニメ調・セルルックキャラクターにおける「左右非対称ハイライトのハイブリッド構造」「瞳の多層的グラデーション表現」「ジェネレーターを活用した均一なフチ取り（UV Border）」「方向性ブラー（Blur Directional）による喉・舌の自然な奥行き減衰表現」など、プロクオリティのセルテクスチャ技法を網羅します。

[📸 参考: fusako29_01_eye_highlight_hybrid_concept.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_01_eye_highlight_hybrid_concept.jpg)

### 顔ペイントの核心的技術ポイント
1. **瞳ハイライトのハイブリッド設計（メッシュ ＋ 透過テクスチャ）**:
   - 瞳テクスチャ自体はUVを左右対称で重ねて解像度を節約。
   - 左右で位置や大きさが微妙に異なる「白い大粒丸ハイライト」は別メッシュとして作成し、左右非対称の表情・光を表現。
   - 細かいキラキラしたハイライトは透過テクスチャ（Face_Transparent）に描き込む。
2. **【神技】Add generator > UV Border によるフチ取り自動生成**:
   - 瞳の外周ラインやハイライトメッシュのフチを、手描きではなくジェネレーターの `UV Border` で一発自動生成。均一で美しいアニメ風エッジを形成。
3. **【神技】Add filter > Blur Directional（方向性ブラー）**:
   - 歯の奥、舌の奥、口腔内（喉の奥）、耳の毛束など、一方向にのみ影を減衰させたい箇所に適用。角度（0°または90°）を指定し、手描きでは困難な滑らかで破綻のない陰影を瞬時に作成。
4. **近接メッシュへの色飛び防止（Alignment: UV）**:
   - まつ毛やアイラインを描く際、3D空間で隣接する毛束に色が飛ぶ現象を、ブラシの `Alignment` を「UV」に変更することで根絶。
5. **2Dビューの回転とスナップ（Alt+左ドラッグ / Alt+Shift）**:
   - 塗りやすい角度に2Dテクスチャビューを自由に回転させ、作業後は `Alt + Shift` で水平垂直にスナップ復帰。

---

## 2. 瞳ハイライトメッシュの作成とFBX再読み込み

### 2.1 ハイライトメッシュの作成（Blender作業）
1. 瞳オブジェクトを選択し、編集モードに入る。
2. 白い丸ハイライトを配置したい中央付近の面を選択。
3. `Shift+D` で複製し、`G Y` で瞳の表面よりわずかに手前（-Y方向）に引き出す。
4. `S` で適正サイズに縮小。

[📸 参考: fusako29_02_blender_highlight_mesh_duplicate.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_02_blender_highlight_mesh_duplicate.jpg)

### 2.2 メッシュの簡略化とプロポーショナル変形
1. 余分なエッジを1つおきに選択し、`X > Dissolve Edges`（辺を溶解）して頂点数を削減。
2. 完全な円ではなく少し歪んだアニメ調の楕円にするため、プロポーショナル編集（`O`）を使って下絵のハイライト形状に微調整。

[📸 参考: fusako29_03_blender_dissolve_edges_proportional.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_03_blender_dissolve_edges_proportional.jpg)

### 2.3 メッシュの分離とミラー適用・非対称配置
1. 作成したハイライト面を選択し、`P > Selection` で別オブジェクトに分離。
2. `Ctrl+A` でミラーモディファイアを適用して実体化。
3. 左右対称のミラーを解除した状態で、右目・左目それぞれのハイライト位置を手動で少しずらし、自然な非対称ハイライトを形成する。

[📸 参考: fusako29_04_blender_separate_p_mirror_apply.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_04_blender_separate_p_mirror_apply.jpg)

### 2.4 UV配置とFBXエクスポート（F4）
1. 顔のテクスチャ（Faceマテリアル）の空き領域に、ハイライトメッシュのUVアイランドを配置。
2. 全頭部オブジェクトを選択し、`F4 > Export > FBX`（Selected Objects, Mesh）で `Head.fbx` を上書きエクスポート。

[📸 参考: fusako29_05_blender_highlight_uv_export.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_05_blender_highlight_uv_export.jpg)

### 2.5 SPへの再読み込み（Project Configuration）
1. Substance Painter を開き、`Edit > Project Configuration` を選択。
2. 修正した `Head.fbx` を読み込み直す。
3. ポリゴンフィル（`4`）の UV Chunk Fill を使用し、新しく追加されたハイライトメッシュを瞳（Eye）フォルダーのマスクに追加する。

[📸 参考: fusako29_06_sp_project_configuration_reload.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_06_sp_project_configuration_reload.jpg)

---

## 3. 瞳（Iris）の多層グラデーションペイント

### 3.1 ベース暗色とブラーフィルター
1. 瞳フォルダー内に最下層の Fill Layer を作成し、最も暗い深紫色を設定。
2. 1段明るい紫色の Fill Layer を追加し、黒マスク ＋ Paint Layer を追加。
3. 瞳下部をふわりと塗り、黒マスクに `Add filter > Blur` を適用して柔らかい下地グラデーションを作成。

[📸 参考: fusako29_07_eye_base_layer_blur_filter.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_07_eye_base_layer_blur_filter.jpg)

### 3.2 階層的なレイヤー積層と瞳模様の描画
1. レイヤーを順次追加し、明るいハイライト色を積層していく。
2. 3Dビューまたは2Dビューで描きやすい側を選択し、花びら状の放射パターンや星状の光彩を模写。
3. 瞳の高解像度テクスチャ素材がある場合は、下絵に可能な限り寄せて精密に描き込む。

[📸 参考: fusako29_08_eye_gradual_color_stacking.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_08_eye_gradual_color_stacking.jpg)

### 3.3 【神技】Add generator > UV Border による輪郭フチ取り
1. 瞳の外周にクッキリとしたフチを入れるため、新規 Fill Layer（濃紺色）を作成。
2. 黒マスクを追加し、右クリック $\to$ **`Add generator`** を選択。
3. ジェネレーター一覧から **`UV Border`** を選択。
4. **Balance**（フチの太さ幅）と **Contrast**（輪郭のクッキリ度）を調整することで、手描きでは歪みやすい瞳外周の均一なフチ取りが一瞬で完成。

[📸 参考: fusako29_09_uv_border_generator_eye_rim.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_09_uv_border_generator_eye_rim.jpg)

---

## 4. 透過ハイライトと瞳本体の光彩エフェクト

### 4.1 透過テクスチャの確認とライティング回転
1. テクスチャセットリストから「Face_Transparent」を選択。
2. 透過表示を確認するため、キーボードの **`M` キー（Material表示）** に切り替える。
3. 光の反射で見づらい場合は、`Shift + 右ドラッグ` で環境ライトの角度を回転させ、ハイライトが最も見やすい角度に調整。

[📸 参考: fusako29_10_transparent_mat_m_key_view.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_10_transparent_mat_m_key_view.jpg)

### 4.2 通常レイヤーでのキラキラハイライト点描
1. 透過テクスチャでは、マスク方式ではなく通常のペイントレイヤー（筆アイコン）を使用可能。
2. 白（White）と水色（Cyan）のペイントレイヤーを個別に作成。
3. キーボードの `1`（ブラシ）と `2`（消しゴム）を切り替えながら、微細な星状・点状のキラキラハイライトを描画。

[📸 参考: fusako29_11_regular_layer_brush_eraser_toggle.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_11_regular_layer_brush_eraser_toggle.jpg)

### 4.3 瞳本体への大粒ハイライト（Screenレイヤー）
1. 瞳本体（Faceマテリアル）側に戻り、大粒の水色ハイライトを描画。
2. 最下層の透明用 Fill Layer は、不要な色情報をカットするため `Color` チェックをオフにしておく。
3. レイヤーの描画モードを **`Screen`（スクリーン）** に設定し、瞳の地色と美しくブレンド発光させる。

[📸 参考: fusako29_12_eye_body_screen_highlight.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_12_eye_body_screen_highlight.jpg)

### 4.4 消しゴムのエアブラシ化による光彩削り込み
1. キーボードの `2`（消しゴム）を選択。
2. ブラシプロパティで `Basic Soft` などのエアブラシ形状をアサイン。
3. 描いたハイライトの端部を柔らかく削り取ることで、透明感のある繊細なグラデーション光彩を表現。

[📸 参考: fusako29_13_eraser_airbrush_soft_carve.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_13_eraser_airbrush_soft_carve.jpg)
[📸 参考: fusako29_14_eye_lower_screen_glow_adjust.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_14_eye_lower_screen_glow_adjust.jpg)

### 4.5 Environment Map の変更（眩しさ・白飛び低減）
1. 画面右上の Display Settings から `Environment Map` を開く。
2. デフォルトの眩しい環境光から **`Studio Automotive Neutral`** など均一でフラットなスタジオライトに変更。
3. マテリアルビューでの作業視認性が劇的に向上する。

[📸 参考: fusako29_15_environment_map_studio_neutral.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_15_environment_map_studio_neutral.jpg)

### 4.6 ハイライトメッシュのフチ付けと再ベイク
1. メッシュで作成した白丸ハイライトにも、`UV Border` ジェネレーターを適用して薄い輪郭線を追加。
2. 新規メッシュ追加に伴うマテリアル表示の不整合を解消するため、`Bake Mesh Maps` を再実行。

[📸 参考: fusako29_16_highlight_mesh_uv_border_rebake.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_16_highlight_mesh_uv_border_rebake.jpg)

---

## 5. まつ毛・アイラインのペイントと干渉防止

### 5.1 まつ毛のフチ取りと加筆
1. `L` キーで Symmetry をオンにし、まつ毛用フォルダーに濃紺の Fill Layer ＋ 黒マスクを追加。
2. `UV Border` ジェネレーターで外周フチを一括生成後、上にペイントレイヤーを追加して毛先の尖りや抜け感を加筆。

[📸 参考: fusako29_17_eyelash_symmetry_uv_border.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_17_eyelash_symmetry_uv_border.jpg)

### 5.2 近接メッシュへの色飛び防止（Alignment: UV）
1. 3Dビューポートでペイントする際、隣接する小さな毛束にブラシが干渉して色が飛び散る場合がある。
2. ブラシプロパティの `Alignment` を「Tangent Wrap」から **`UV`** に変更。
3. 3D空間の近接度ではなくUV座標基準でストロークが判定されるため、近接メッシュへの誤塗りを完全に防止できる。

[📸 参考: fusako29_18_eyelash_brush_alignment_uv.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_18_eyelash_brush_alignment_uv.jpg)

### 5.3 まつ毛裏面の一括塗りつぶし
1. まつ毛の裏面・側面は影になるため、キーボードの `4`（Polygon Fill）に切り替え。
2. `UV Chunk Fill` モードで裏面メッシュのUV島をクリックし、最暗色で一発塗りつぶし。

[📸 参考: fusako29_19_polygon_fill_eyelash_back.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_19_polygon_fill_eyelash_back.jpg)

---

## 6. 口腔・歯・舌・耳のペイントとBlur Directional

### 6.1 舌（ベロ）の陰影付け
1. 舌のベース色に対し、乗算（Multiply）レイヤーを追加。
2. 奥側を暗くするため、ブラシでざっくりとストロークを配置。

[📸 参考: fusako29_20_tongue_shadow_multiply_layer.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_20_tongue_shadow_multiply_layer.jpg)

### 6.2 【神技】Add filter > Blur Directional による一方向グラデーション
1. 舌や歯の陰影マスクを右クリック $\to$ `Add filter` $\to$ **`Blur Directional`（方向性ブラー）** を選択。
2. **Angle（角度）**: UV島の長手方向（0°または90°）に設定。
3. **Intensity（強度）**: スライダーを引き上げると、ストロークが一方向にのみ滑らかに引き伸ばされ、手描きでは不可能な完璧な奥行き減衰グラデーションが瞬時に形成される。

[📸 参考: fusako29_21_blur_directional_filter_90deg.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_21_blur_directional_filter_90deg.jpg)

### 6.3 口腔内（喉の奥）の陰影ペイント
1. 口腔メッシュフォルダー内で、首の穴や正面から覗き込みながら奥面をペイント。
2. `Blur Directional`（Angle: 90°）を適用し、喉の奥に向かって自然に暗くなるセルアニメ特有の口内表現を完成させる。

[📸 参考: fusako29_22_mouth_throat_shadow_directional.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_22_mouth_throat_shadow_directional.jpg)

### 6.4 2Dビューの回転・スナップと耳のペイント
1. 耳の内側・フチなど細かな塗り分けを行う際、2Dビュー上で作業しやすいように **`Alt + 左ドラッグ`** でテクスチャビューを回転。
2. 元の水平垂直に戻す際は **`Alt + Shift + 左ドラッグ`** で瞬時にスナップリセット。
3. 耳の内側ピンク、毛先の白ハイライト、付け根の暗色を塗り分け。

[📸 参考: fusako29_23_view_2d_rotate_alt_shift_snap.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_23_view_2d_rotate_alt_shift_snap.jpg)

### 6.5 耳毛へのBlur Directional適用と顔ペイント完成
1. 耳毛の房メッシュに数本ストロークを描き、`Blur Directional`（Angle: 90°）を適用して先端へ向かってフェードアウトする毛並みを表現。
2. これにより、顔・瞳・まつ毛・口腔・耳の全フェイステクスチャペイントが完全完成。

[📸 参考: fusako29_24_ear_fur_blur_directional_complete.jpg](../../docs/fusako_29_sp_face_paint_screenshots/fusako29_24_ear_fur_blur_directional_complete.jpg)

---

## 7. トラブルシューティング＆チェックリスト

| 症状 / 課題 | 原因 | 解決策 |
|:---|:---|:---|
| 瞳のハイライトが左右で同じ位置になって不自然 | UVを重ねているため | 左右非対称の大粒白丸ハイライトを別メッシュとして作成し、左右独立配置。 |
| 瞳やまつ毛のフチ取り線がガタガタする | 手描きのストロークブレ | 黒マスクに `Add generator > UV Border` を追加し、Balance/Contrastで自動均一フチ取り。 |
| まつ毛を塗ると近くの小毛束に色が飛ぶ | 3D空間の近接度による誤判定 | ブラシプロパティの `Alignment` を「Tangent Wrap」から **`UV`** に変更。 |
| 口の奥や舌のグラデーションが汚くなる | 通常ブラー（全方向拡散）の使用 | 一方向にのみ減衰する **`Blur Directional`** フィルターを使用し、Angleを90°に設定。 |
| マテリアル表示でテクスチャが白飛びして見えない | 環境光の強烈なスペキュラ | `Display Settings > Environment Map` を「Studio Automotive Neutral」へ変更。 |
| 2Dビューが斜めに回転して元に戻せない | 誤操作による2D回転 | `Alt + Shift + 左ドラッグ` を行うことで、最も近い水平・垂直角度にスナップ復帰。 |
