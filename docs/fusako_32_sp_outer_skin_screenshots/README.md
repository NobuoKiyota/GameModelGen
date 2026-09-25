# ふさこ氏 Blenderキャラモデリング #32 スクリーンショットカタログ
## 【テクスチャ編05】アウターや肌のペイント (Substance 3D Painter)

本フォルダには、YouTube動画「【Blender】キャラクターモデル制作！テクスチャ編05 アウターや肌のペイント【3Dモデリング講座】」（動画ID: `FbRFGbE8VdU`）から抽出した高解像度解説スクリーンショット（全24枚）を収録しています。

対応する詳細手順仕様書: [2026-09-25_fusako_sp_outer_skin_32_steps.md](../../.agents/handoffs/2026-09-25_fusako_sp_outer_skin_32_steps.md)

---

## 📸 スクリーンショット一覧（全24枚）

| No | タイムスタンプ | 画像リンク（クリックで表示） | 場面・操作内容の解説 |
|:---:|:---:|:---|:---|
| 01 | 00:15 | [fusako32_01_sp_texture_set_size_basecolor_only.jpg](./fusako32_01_sp_texture_set_size_basecolor_only.jpg) | **【SP: 初期チャンネル設定】** テクスチャセットサイズ指定、Metallic/Roughness/Normal/Heightを削除し、Base Color単一化・UV Space Neighbor設定 |
| 02 | 00:35 | [fusako32_02_sp_reference_eyedropper_fill_layers.jpg](./fusako32_02_sp_reference_eyedropper_fill_layers.jpg) | **【SP: カラー採取とベタ塗り】** 別窓にキャラ立ち絵を用意し、スポイトツールで固有色を採取してパーツ別Fill Layerにアサイン |
| 03 | 01:20 | [fusako32_03_sp_base_colors_all_parts_done.jpg](./fusako32_03_sp_base_colors_all_parts_done.jpg) | **【SP: 全パーツ下地色塗り分け完了】** 体・服・アクセサリーの全テクスチャセットへの基本ベタ塗りレイヤー構築完了状態 |
| 04 | 01:50 | [fusako32_04_sp_inner_hide_outer_l_symmetry.jpg](./fusako32_04_sp_inner_hide_outer_l_symmetry.jpg) | **【SP: インナーペイント準備】** 邪魔なアウターメッシュを一時非表示にし、`L` キーで左右対称（Symmetry）ペイントを有効化 |
| 05 | 03:15 | [fusako32_05_sp_skin_shadow_rough_pass.jpg](./fusako32_05_sp_skin_shadow_rough_pass.jpg) | **【肌の影ペイント①】** Basic Softブラシを使用し、太ももや膝裏など足の落ち影の第一段階をざっくりと塗る |
| 06 | 03:30 | [fusako32_06_sp_skin_darken_blend_gradient_brush.jpg](./fusako32_06_sp_skin_darken_blend_gradient_brush.jpg) | **【肌の影ペイント②: 秘技Darken】** 新規ペイントレイヤーを追加しブレンドモードを `Darken`（比較暗）に設定。黒ブラシで加筆して自然な階調を生成 |
| 07 | 04:05 | [fusako32_07_sp_skin_soft_fade_eraser_technique.jpg](./fusako32_07_sp_skin_soft_fade_eraser_technique.jpg) | **【肌の影ペイント③: 消しゴム的フェード】** SPのぼかしブラシを使わず、柔らかい黒ブラシで削り込んで滑らかなアニメ調グラデーションを完成 |
| 08 | 05:05 | [fusako32_08_sp_outer_stripe_guide_motivation.jpg](./fusako32_08_sp_outer_stripe_guide_motivation.jpg) | **【ストライプ線の課題】** アウターの等間隔ボーダー・ストライプ線を手描きだけで均一に引く難しさとプロシージャルガイドの必要性 |
| 09 | 05:25 | [fusako32_09_sp_outer_fill_mask_fill_setup.jpg](./fusako32_09_sp_outer_fill_mask_fill_setup.jpg) | **【ガイドレイヤー構築】** 視認しやすい色のFill Layerを作成し、黒マスク（Black mask）に `Fill`（塗りつぶし）エフェクトを追加 |
| 10 | 05:45 | [fusako32_10_sp_line_stripes_bend0_rot90.jpg](./fusako32_10_sp_line_stripes_bend0_rot90.jpg) | **【Line Stripesテクスチャ】** Grayscaleに `Line Stripes` を適用。Bend: 0で直線化し、Rotation: 90度で水平方向に整流 |
| 11 | 06:15 | [fusako32_11_sp_2d_view_gizmo_scale_stripes.jpg](./fusako32_11_sp_2d_view_gizmo_scale_stripes.jpg) | **【2Dビューでのギズモ操作】** 2Dテクスチャビュー上で薄い四角ギズモの角をドラッグし、縦9本など元絵の比率に等間隔スケール調整 |
| 12 | 06:55 | [fusako32_12_sp_brush_straight_line_shift_ctrl.jpg](./fusako32_12_sp_brush_straight_line_shift_ctrl.jpg) | **【完全な直線描画ショートカット】** Alignment: UV、Shiftクリック（点線ガイド）＋ `Ctrl`（角度スナップ固定）で寸分違わぬ真直ぐなラインを描画 |
| 13 | 07:15 | [fusako32_13_sp_guide_draw_clean_polygon_fill.jpg](./fusako32_13_sp_guide_draw_clean_polygon_fill.jpg) | **【直線清書とクリーンアップ】** ガイドを薄く表示して線をなぞり、はみ出した不要領域は `Polygon Fill`（黒）で一発クリーンアップ |
| 14 | 08:30 | [fusako32_14_sp_sweater_knit_pattern_intro.jpg](./fusako32_14_sp_sweater_knit_pattern_intro.jpg) | **【セーター三つ編み模様の課題】** 複雑なニット編み込み模様を均等かつ破綻なく描くためのプロシージャルガイド設計 |
| 15 | 08:50 | [fusako32_15_sp_fabric_texture_in_fill_mask.jpg](./fusako32_15_sp_fabric_texture_in_fill_mask.jpg) | **【Fabricテクスチャの選択】** テクスチャライブラリから `Fabric`（編み目テクスチャ）を検索し、FillエフェクトのGrayscaleにドラッグ＆ドロップ |
| 16 | 09:25 | [fusako32_16_sp_repeat_vertically_shift_aspect.jpg](./fusako32_16_sp_repeat_vertically_shift_aspect.jpg) | **【縦方向リピートとアスペクト維持】** Repeatを `Repeat Vertically`（縦のみ反復）に変更し、`Shift` を押しながらギズモで縦横比を保ってリサイズ |
| 17 | 09:50 | [fusako32_17_sp_gizmo_rotation_knit_alignment.jpg](./fusako32_17_sp_gizmo_rotation_knit_alignment.jpg) | **【ギズモ回転による向き合わせ】** 枠外ドラッグで180度回転させ、編み目の下向き・上向きの毛流れをアウターの形状にピタリと整合 |
| 18 | 10:20 | [fusako32_18_sp_sweater_rough_sketch_layer.jpg](./fusako32_18_sp_sweater_rough_sketch_layer.jpg) | **【編み目の下書きレイヤー】** 筆圧感知をOFFにしたBasic Hardブラシで、ガイドの編み目節に沿って大まかなラインを下書きスケッチ |
| 19 | 11:15 | [fusako32_19_sp_sweater_final_interlocking_lines.jpg](./fusako32_19_sp_sweater_final_interlocking_lines.jpg) | **【本番ペイント: 左右交互の編み込み】** 下書きを薄くし、左上から右下・右上から左下へと交互に絡み合う美しいニットの清書ラインを描画 |
| 20 | 12:05 | [fusako32_20_sp_sweater_pattern_clean_result.jpg](./fusako32_20_sp_sweater_pattern_clean_result.jpg) | **【下書き・ガイド非表示で完成】** ガイドレイヤーと下書きを非表示にし、手描き感と幾何学的整列が調和したセーター模様が完成 |
| 21 | 12:35 | [fusako32_21_sp_brush_stitches_small_dotted.jpg](./fusako32_21_sp_brush_stitches_small_dotted.jpg) | **【ステッチブラシの活用】** ブラシライブラリから `Stitches Small` を選択し、等間隔の点線・縫い目をスムーズにストローク描画 |
| 22 | 13:10 | [fusako32_22_sp_stitches_lines3_parallel_solid.jpg](./fusako32_22_sp_stitches_lines3_parallel_solid.jpg) | **【平行3本実線化の裏技】** Linesを3本に設定し、Spacing（間隔）を極小に詰めることで「完全に平行な3本の実線」を一筆で描く神テクニック |
| 23 | 15:30 | [fusako32_23_sp_uv_border_generator_outer_edge.jpg](./fusako32_23_sp_uv_border_generator_outer_edge.jpg) | **【UV Borderによるフチ線自動生成】** アウター裾や袖口のシーム境界線に `UV Border` ジェネレーターを適用し均一なパイピング線を生成 |
| 24 | 15:50 | [fusako32_24_sp_darken_mask_clean_unwanted_borders.jpg](./fusako32_24_sp_darken_mask_clean_unwanted_borders.jpg) | **【Darkenレイヤーによる不要フチ消去】** ブレンドモード `Darken` のペイントレイヤーを重ね、黒ブラシで襟元などの不要なフチ線のみを消去して完成 |

---
*Generated by Antigravity AI Learning Automation Engine*
