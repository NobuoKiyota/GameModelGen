# ふさこ氏チュートリアル第16話『ポシェットのモデリング』重要シーン・スクリーンショットカタログ

本フォルダには、ふさこ氏によるBlenderキャラクターモデル制作チュートリアル第16話『ポシェット（ペンギン）のモデリング 〜初級から中級者向けチュートリアル〜』（動画長: 31分03秒）から抽出した、モデリング・トポロジー上の重要キーフレーム高解像度スクリーンショット（全24枚）を収録しています。

詳細な手順仕様書は [2026-09-24_fusako_penguin_pochette_16_steps.md](../../.agents/handoffs/2026-09-24_fusako_penguin_pochette_16_steps.md) を参照してください。

---

## スクリーンショット一覧・トポロジー解説

| No | タイムスタンプ | 画像リンク (相対パス) | 工程・チャプター | 使用ショートカット / 機能 | 解説・モデリングのポイント |
| :---: | :---: | :--- | :--- | :--- | :--- |
| 01 | 00:00:45 | [./01_c1_cube_base_pochette_placement.jpg](./01_c1_cube_base_pochette_placement.jpg) | C1: ポシェット立ち上げ | `Shift + A > Cube`, `AutoMirror` | Cubeから開始し、腰のポシェット位置へ配置・縮小。AutoMirrorでX軸対称化。 |
| 02 | 00:01:25 | [./02_c1_y_rip_flap_cover_gz.jpg](./02_c1_y_rip_flap_cover_gz.jpg) | C1: ポシェット立ち上げ | `Y` (切り裂き), `G + Z` | フタ（フラップ）部分を `Y` で切り離し、上へ持ち上げて二重構造の開口部を作成。 |
| 03 | 00:02:15 | [./03_c1_inset_side_depth_gusset.jpg](./03_c1_inset_side_depth_gusset.jpg) | C1: ポシェット立ち上げ | `I` (Boundary: OFF), `G + X` | 側面をインセットして内側に凹ませ、バッグ特有のマチと立体感を成形。 |
| 04 | 00:03:05 | [./04_c1_collapse_edge_loops_optimize.jpg](./04_c1_collapse_edge_loops_optimize.jpg) | C1: ポシェット立ち上げ | `Subsurf` 適用, Collapse Edge Loops | Subsurf1を適用後、余分なエッジリングをコラプス（溶解統合）してポリゴン最適化。 |
| 05 | 00:05:45 | [./05_c1_mark_sharp_frill_color_segments.jpg](./05_c1_mark_sharp_frill_color_segments.jpg) | C1: ポシェット立ち上げ | `Mark Sharp` (色分けマーキング) | 前面メッシュを5等分し、マークシャープで交互に色分けしてフリル波形を可視化。 |
| 06 | 00:06:45 | [./06_c1_inset_valley_merge_zigzag.jpg](./06_c1_inset_valley_merge_zigzag.jpg) | C1: ポシェット立ち上げ | `I` (インセット), 谷頂点マージ | フリル面をインセット後、谷の頂点同士を中心マージしてジグザグ骨格を生成。 |
| 07 | 00:07:45 | [./07_c1_active_element_scale_round_frill.jpg](./07_c1_active_element_scale_round_frill.jpg) | C1: ポシェット立ち上げ | Active Element, `S` スケール | 円弧中心をアクティブにしてスケールし、綺麗な半円フリルを均等造形。 |
| 08 | 00:09:05 | [./08_c2_duplicate_faces_scarf_base.jpg](./08_c2_duplicate_faces_scarf_base.jpg) | C2: スカーフモデリング | `Shift + D`, `P` 分離, `G + Y` | ポシェット上部面を複製・分離し、手前に引き出して首巻きスカーフのベースを作成。 |
| 09 | 00:11:50 | [./09_c2_cube_extrude_open_scarf_knot.jpg](./09_c2_cube_extrude_open_scarf_knot.jpg) | C2: スカーフモデリング | `Cube`, 上下開放, 押し出し | 立方体から上下の面を削除し、スカーフの布を通す筒状の結び目パーツを成形。 |
| 10 | 00:12:45 | [./10_c2_scarf_tail_extrude_alt_s.jpg](./10_c2_scarf_tail_extrude_alt_s.jpg) | C2: スカーフモデリング | `E` 下押し出し, `Alt + S` 膨らみ | 結び目から下がるスカーフの垂れ布を押し出し、`Alt + S` でふんわり膨らませる。 |
| 11 | 00:13:55 | [./11_c2_asymmetrical_scarf_tails_tweak.jpg](./11_c2_asymmetrical_scarf_tails_tweak.jpg) | C2: スカーフモデリング | Mirror適用, 左右非対称調整 | Mirrorモディファイアを適用後、左右の垂れ布の長さと角度をずらして自然な動きを付与。 |
| 12 | 00:14:30 | [./12_c3_curve_bezier_bevel_depth_cord.jpg](./12_c3_curve_bezier_bevel_depth_cord.jpg) | C3: 紐・リボン（カーブ） | `Curve Bezier`, `Bevel Depth` | ベジェカーブを追加し、ベベル深度（0.003m）で均一な丸紐の太さを設定。 |
| 13 | 00:15:55 | [./13_c3_curve_loop_and_tail_shaping.jpg](./13_c3_curve_loop_and_tail_shaping.jpg) | C3: 紐・リボン（カーブ） | カーブ編集, 輪っか・垂れ紐複製 | `Shift + D` でカーブ制御点を複製し、リボンの左右の輪っかと垂れ紐を成形。 |
| 14 | 00:17:40 | [./14_c3_cube_central_metal_fastener.jpg](./14_c3_cube_central_metal_fastener.jpg) | C3: 紐・リボン（カーブ） | `Cube`, 金具スリットインセット | リボンの結び目金具となるキューブを配置し、紐が通るスリット開口を造形。 |
| 15 | 00:18:55 | [./15_c3_convert_to_mesh_curve_cord.jpg](./15_c3_convert_to_mesh_curve_cord.jpg) | C3: 紐・リボン（カーブ） | `Convert to Mesh` | カーブ形状が確定後、右クリックからメッシュへ変換してポリゴン化。 |
| 16 | 00:20:10 | [./16_c3_cord_ends_tuck_clipping_merge.jpg](./16_c3_cord_ends_tuck_clipping_merge.jpg) | C3: 紐・リボン（カーブ） | 金具穴への押し込み, クリッピング | 紐の端点を金具の内部へ潜り込ませ、中央クリッピングで完全溶接マージ。 |
| 17 | 00:22:30 | [./17_c3_solidify_fill_rim_off_shading.jpg](./17_c3_solidify_fill_rim_off_shading.jpg) | C3: 紐・リボン（カーブ） | `Solidify` (`Fill Rim: OFF`) | 裏面描画シェーダー向けにリムなしSolidifyを設定し、板ポリの厚み表現を最適化。 |
| 18 | 00:23:45 | [./18_c3_solidify_pochette_body_thickness.jpg](./18_c3_solidify_pochette_body_thickness.jpg) | C3: 紐・リボン（カーブ） | `Solidify` (ポシェット本体) | ポシェット本体とフタに厚み付けモディファイアを適用。 |
| 19 | 00:26:45 | [./19_c4_duplicate_edge_rabbit_ears_base.jpg](./19_c4_duplicate_edge_rabbit_ears_base.jpg) | C4: 耳パーツ作成 | `Shift + D`, `E + Z` 上押し出し | スカーフ上端エッジを複製し、上方に押し出してウサ耳のベースを立ち上げ。 |
| 20 | 00:27:15 | [./20_c4_smooth_vertices_ear_thickness.jpg](./20_c4_smooth_vertices_ear_thickness.jpg) | C4: 耳パーツ作成 | `Smooth Vertices`, `E` 厚み押し出し | 先端をスムーズで丸め、`E` で厚みを押し出してふっくらした立体耳に成形。 |
| 21 | 00:28:15 | [./21_c4_embed_ears_into_pochette_back.jpg](./21_c4_embed_ears_into_pochette_back.jpg) | C4: 耳パーツ作成 | ポシェット背面への差し込み | 底面を削除し、ポシェット背面のフタ裏へ潜り込ませて違和感なく一体化。 |
| 22 | 00:28:50 | [./22_c5_ctrl_p_parenting_keep_transform.jpg](./22_c5_ctrl_p_parenting_keep_transform.jpg) | C5: 配置・親子付け | `Ctrl + P > Keep Transform` | 全パーツを選択し、ポシェット本体をアクティブ親にして一括親子付け。 |
| 23 | 00:29:45 | [./23_c5_waist_placement_mirror_face_target.jpg](./23_c5_waist_placement_mirror_face_target.jpg) | C5: 配置・親子付け | 腰への吸着配置, `Mirror Object: Head` | キャラクター腰に配置し、Mirrorモディファイアの対象に顔を指定して対称化。 |
| 24 | 00:30:20 | [./24_c5_copy_attributes_menu_mirror_copy.jpg](./24_c5_copy_attributes_menu_mirror_copy.jpg) | C5: 配置・親子付け | `Copy Attributes Menu` (`Ctrl + C`) | `Ctrl + C > Copy Selected Modifiers` で全パーツに顔基準Mirrorを一括コピー適用。 |
