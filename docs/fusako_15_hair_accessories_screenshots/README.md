# ふさこ氏チュートリアル第15話『ヘアアクセのモデリング』重要シーン・スクリーンショットカタログ

本フォルダには、ふさこ氏によるBlenderキャラクターモデル制作チュートリアル第15話『ヘアアクセのモデリング 〜初級から中級者向けチュートリアル〜』（動画長: 17分46秒）から抽出した、モデリング・トポロジー上の重要キーフレーム高解像度スクリーンショット（全24枚）を収録しています。

詳細な手順仕様書は [2026-09-24_fusako_hair_accessories_15_steps.md](../../.agents/handoffs/2026-09-24_fusako_hair_accessories_15_steps.md) を参照してください。

---

## スクリーンショット一覧・トポロジー解説

| No | タイムスタンプ | 画像リンク (相対パス) | 工程・チャプター | 使用ショートカット / 機能 | 解説・モデリングのポイント |
| :---: | :---: | :--- | :--- | :--- | :--- |
| 01 | 00:00:20 | [./01_c1_cube_subsurf1_ribbon_knot.jpg](./01_c1_cube_subsurf1_ribbon_knot.jpg) | C1: リボンモデリング | `Shift + A > Cube`, `Ctrl + 1` | 立方体にSubsurf1を追加し、リボン中央の結び目パーツを小さく配置。 |
| 02 | 00:00:55 | [./02_c1_rx45_ribbon_wing_extrude.jpg](./02_c1_rx45_ribbon_wing_extrude.jpg) | C1: リボンモデリング | `Shift + D`, `R X 45°`, `S` 拡大 | 結び目を複製し、X軸45度回転・拡大してリボンの広がる羽パーツの根元を作成。 |
| 03 | 00:01:25 | [./03_c1_ex_extrude_delete_inner_faces.jpg](./03_c1_ex_extrude_delete_inner_faces.jpg) | C1: リボンモデリング | `E + X`, `X > Faces` | 外側へ押し出し羽を伸ばし、内側の不要な重なり面を削除してクリーン化。 |
| 04 | 00:02:15 | [./04_c1_apply_subsurf_automirror_symmetry.jpg](./04_c1_apply_subsurf_automirror_symmetry.jpg) | C1: リボンモデリング | Subsurf適用, `AutoMirror` | Subsurfを確定適用後、AutoMirrorでX軸対称化し、左右均等なリボン形状を完成。 |
| 05 | 00:03:20 | [./05_c1_mirror_face_target_twintail_align.jpg](./05_c1_mirror_face_target_twintail_align.jpg) | C1: リボンモデリング | Mirrorモディファイア (顔基準) | MirrorObjectに顔メッシュを指定し、左右両サイドのツインテール根元に対称配置。 |
| 06 | 00:03:55 | [./06_c1_plane_sy_scale_triangle_silhouette.jpg](./06_c1_plane_sy_scale_triangle_silhouette.jpg) | C2: パッチンどめ | `Shift + A > Plane`, `Ctrl + R`, `S + Y` | 平面から開始し、ループ追加後右端を `S + Y` で絞り込んで三角形シルエットを形成。 |
| 07 | 00:04:35 | [./07_c2_vertex_bevel_round_corners.jpg](./07_c2_vertex_bevel_round_corners.jpg) | C2: パッチンどめ | `Shift + Ctrl + B` (頂点ベベル) | パッチン留めの角頂点を選択し、頂点ベベルで丸みを帯びたプレートへ成形。 |
| 08 | 00:04:55 | [./08_c2_inset_delete_inner_face_frame.jpg](./08_c2_inset_delete_inner_face_frame.jpg) | C2: パッチンどめ | `I` (インセット), `X > Faces` | 全面インセットで内枠を作り、中央の面を削除して開口フレームを造形。 |
| 09 | 00:05:40 | [./09_c2_ex_extrude_pin_gz_offset.jpg](./09_c2_ex_extrude_pin_gz_offset.jpg) | C2: パッチンどめ | `E + X`, `G + Z` (下オフセット) | ピン足エッジを押し出し、髪を挟むクリップの立体的な段差オフセットを成形。 |
| 10 | 00:06:55 | [./10_c2_solidify_clip_thickness.jpg](./10_c2_solidify_clip_thickness.jpg) | C2: パッチンどめ | `Solidify` モディファイア | クリップ全体に薄い金属プレートの厚み（`Thickness: 0.002m`）を非破壊付与。 |
| 11 | 00:07:30 | [./11_c2_add_lattice_u3_setup.jpg](./11_c2_add_lattice_u3_setup.jpg) | C2: パッチンどめ | `Shift + A > Lattice`, `U=3` | パッチン留めを覆うラティスを追加し、U解像度を3（中央に1本ループ）に設定。 |
| 12 | 00:07:55 | [./12_c2_lattice_modifier_gz_curve_bend.jpg](./12_c2_lattice_modifier_gz_curve_bend.jpg) | C2: パッチンどめ | Latticeモディファイア, `G + Z` | 中央ラティス頂点を持ち上げ、髪の曲面に沿った滑らかなパッチン反りカーブを生成。 |
| 13 | 00:08:25 | [./13_c2_clip_hole_cutout_mark_sharp.jpg](./13_c2_clip_hole_cutout_mark_sharp.jpg) | C2: パッチンどめ | `Ctrl + R`, `Ctrl + B`, 面削除 | クリップ中央にスリット穴を開口。側面エッジに `Mark Sharp` を付与しパキッと描画。 |
| 14 | 00:09:45 | [./14_c3_circle_8verts_petal_base.jpg](./14_c3_circle_8verts_petal_base.jpg) | C3: お花アクセサリー | `Shift + A > Circle` (頂点数8) | 花びら1枚のベースとなる8頂点サークルを追加し、花弁の卵形へ縮小・配置。 |
| 15 | 00:10:15 | [./15_c3_add_empty_array_object_offset.jpg](./15_c3_add_empty_array_object_offset.jpg) | C3: お花アクセサリー | `Shift + A > Empty`, `Array` | 原点にエンプティを配置し、花びらに `Array`（Object Offset有効、エンプティ指定）を追加。 |
| 16 | 00:10:45 | [./16_c3_rz_72deg_array_5petals_flower.jpg](./16_c3_rz_72deg_array_5petals_flower.jpg) | C3: お花アクセサリー | `Count: 5`, `R Z 72°` (`360/5`) | エンプティを72度回転させ、花びら5枚の完璧な円形放射状配列を構築。 |
| 17 | 00:11:35 | [./17_c3_s0_merge_inset_bulge_petals.jpg](./17_c3_s0_merge_inset_bulge_petals.jpg) | C3: お花アクセサリー | 3Dカーソル中心 `S 0`, `I`, `G + Z` | 花びら根元をカーソル中心で結合し、面張り $\to$ インセット $\to$ 持ち上げでぷっくり成形。 |
| 18 | 00:12:40 | [./18_c4_circle_3verts_subdivide_triangle.jpg](./18_c4_circle_3verts_subdivide_triangle.jpg) | C4: おにぎりパーツ | `Circle` (頂点数3), `Subdivide` | 3頂点サークルに細分化（Smoothness調整）を施し、角の丸いおにぎり型ベースを生成。 |
| 19 | 00:13:10 | [./19_c4_vertex_bevel_inset_center_part.jpg](./19_c4_vertex_bevel_inset_center_part.jpg) | C4: おにぎりパーツ | `Shift + Ctrl + B`, `I`, `Merge Center` | 端点3点をベベル面取り後、面張り $\to$ インセット $\to$ 中心マージで立体パーツ化。 |
| 20 | 00:14:10 | [./20_c4_apply_array_join_solidify_flower.jpg](./20_c4_apply_array_join_solidify_flower.jpg) | C4: おにぎりパーツ | Array適用, `Ctrl + J`, `Solidify` | 花びら配列を適用しおにぎりと結合。`Solidify` で厚みを付け花飾り全体が完成。 |
| 21 | 00:15:15 | [./21_c5_align_clip_flower_lattice_scale.jpg](./21_c5_align_clip_flower_lattice_scale.jpg) | C5: 配置・親子付け | `S` スケール, 位置合わせ | パッチン留めとお花パーツ、ラティスのサイズ感を下絵に合わせて調整。 |
| 22 | 00:15:45 | [./22_c5_ctrl_p_keep_transform_parenting.jpg](./22_c5_ctrl_p_keep_transform_parenting.jpg) | C5: 配置・親子付け | `Ctrl + P > Object (Keep Transform)` | お花をアクティブ親にしてクリップ・ラティスを親子付けし、一体移動・回転を可能化。 |
| 23 | 00:16:30 | [./23_c5_alt_d_linked_duplicate_bangs_placement.jpg](./23_c5_alt_d_linked_duplicate_bangs_placement.jpg) | C5: 配置・親子付け | `Alt + D` (リンク複製), 髪への吸着配置 | 前髪に乗せ、`Alt + D` でメッシュデータを共有したまま反対側・別角度へリンク配置。 |
| 24 | 00:17:15 | [./24_c5_accessories_collection_organize_complete.jpg](./24_c5_accessories_collection_organize_complete.jpg) | C5: 配置・親子付け | 新規コレクション `Accessories`, `M` 移動 | アウトライナーに `Accessories` コレクションを作成し、全パーツを分類格納して完成。 |
