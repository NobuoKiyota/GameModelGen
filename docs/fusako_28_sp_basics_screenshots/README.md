# ふさこ氏 Blenderキャラクター制作 #28 (SP #01)『Substance Painter入門・基本操作』スクリーンショットカタログ

YouTube動画: [Substance Painterでテクスチャペイント！#28 (01) | Substance Painter入門・基本操作 〜初中級者向けチュートリアル〜](https://www.youtube.com/watch?v=RB9jILspXBk)  
詳細仕様書: [2026-09-25_fusako_sp_basics_28_steps.md](../../.agents/handoffs/2026-09-25_fusako_sp_basics_28_steps.md)

---

## スクリーンショット一覧（全24枚）

| No | タイムスタンプ | 画像ファイル（クリックで拡大） | 主な解説・操作内容 |
|:---:|:---:|:---|:---|
| 01 | 00:20 | [fusako28_01_blender_rename_lattice.jpg](./fusako28_01_blender_rename_lattice.jpg) | Blenderでの事前準備：オブジェクトリネームとラティスモディファイア適用・バックアップ |
| 02 | 01:40 | [fusako28_02_eye_highlight_mat_split.jpg](./fusako28_02_eye_highlight_mat_split.jpg) | 瞳ハイライト・表情用透過マテリアル（M_Face_Transparent）の分離 |
| 03 | 02:45 | [fusako28_03_mouth_eye_offset_duplicate.jpg](./fusako28_03_mouth_eye_offset_duplicate.jpg) | 【神Tips】口内パーツ（歯・舌）と瞳の複製引き出し配置（Shift+D Z）で塗りやすさを向上 |
| 04 | 04:15 | [fusako28_04_blender_fbx_export.jpg](./fusako28_04_blender_fbx_export.jpg) | Blenderから頭部モデルのFBXエクスポート設定（Selected Objects, Mesh） |
| 05 | 05:00 | [fusako28_05_sp_new_project_import.jpg](./fusako28_05_sp_new_project_import.jpg) | Substance Painterでの新規プロジェクト作成とテクスチャセットリストの確認 |
| 06 | 05:40 | [fusako28_06_bake_mesh_maps_settings.jpg](./fusako28_06_bake_mesh_maps_settings.jpg) | Bake Mesh Maps設定：512テスト、Normal/IDオフ、Anti-aliasing 4x4設定 |
| 07 | 06:40 | [fusako28_07_bake_b_key_world_normal_check.jpg](./fusako28_07_bake_b_key_world_normal_check.jpg) | Bキーによるベイク結果確認とWorld Space NormalによるUV重なり（Overlapping）検出 |
| 08 | 07:35 | [fusako28_08_project_configuration_reload.jpg](./fusako28_08_project_configuration_reload.jpg) | BlenderでのUV修正 $\to$ SP側「Project Configuration」によるFBX再読み込み |
| 09 | 08:45 | [fusako28_09_bake_2k_resolution_setup.jpg](./fusako28_09_bake_2k_resolution_setup.jpg) | 2048 (2K) 本番ベイク実行と各テクスチャセット解像度設定（Face/Hair: 2048） |
| 10 | 09:15 | [fusako28_10_base_color_only_channels.jpg](./fusako28_10_base_color_only_channels.jpg) | セル調モデルのためのチャンネル整理（Metallic/Roughness/Normal/Height削除、Base Colorのみ） |
| 11 | 09:40 | [fusako28_11_uv_space_neighbor_padding.jpg](./fusako28_11_uv_space_neighbor_padding.jpg) | UV Padding設定を「UV Space Neighbor」へ変更し隣接色の拾い込みを防止 |
| 12 | 10:45 | [fusako28_12_external_window_color_picker.jpg](./fusako28_12_external_window_color_picker.jpg) | 別ウィンドウのイラスト下絵からスポイトで色を直接サンプリング |
| 13 | 11:30 | [fusako28_13_fill_layer_black_mask_paint.jpg](./fusako28_13_fill_layer_black_mask_paint.jpg) | SPの基本ペイント構造：ベタ塗り（Fill Layer） ＋ 黒マスク（Black Mask） ＋ Paint Layer |
| 14 | 13:40 | [fusako28_14_symmetry_l_key_blur_filter.jpg](./fusako28_14_symmetry_l_key_blur_filter.jpg) | LキーによるSymmetry（左右対称）とチークへの「Add Filter > Blur」ぼかし適用 |
| 15 | 14:45 | [fusako28_15_mesh_wireframe_display.jpg](./fusako28_15_mesh_wireframe_display.jpg) | メッシュワイヤーフレーム表示設定（水色カラー・透過度調整） |
| 16 | 16:45 | [fusako28_16_polygon_fill_uv_chunk.jpg](./fusako28_16_polygon_fill_uv_chunk.jpg) | ポリゴンフィル（Polygon Fill: 4）の「UV Chunk Fill」によるまつ毛・白目の一発マスク塗り |
| 17 | 18:40 | [fusako28_17_brush_shortcuts_x_key_toggle.jpg](./fusako28_17_brush_shortcuts_x_key_toggle.jpg) | ブラシツール（1）、消しゴム（2）、マスク描画時のXキー（白黒反転）ショートカット |
| 18 | 20:30 | [fusako28_18_lazy_mouse_stabilizer_d_key.jpg](./fusako28_18_lazy_mouse_stabilizer_d_key.jpg) | Dキーによる手振れ補正（Lazy Mouse Distance）で滑らかな曲線を引く |
| 19 | 22:50 | [fusako28_19_brush_size_texture_alignment_uv.jpg](./fusako28_19_brush_size_texture_alignment_uv.jpg) | 2DビューでのSize Space「Texture」設定とAlignment「UV」設定によるガタつき解消 |
| 20 | 28:15 | [fusako28_20_airbrush_custom_preset_save.jpg](./fusako28_20_airbrush_custom_preset_save.jpg) | ふんわりエアブラシ（Basic Super Soft）のカスタム設定とBrush Preset保存 |
| 21 | 30:15 | [fusako28_21_alpha_blending_opacity_channel.jpg](./fusako28_21_alpha_blending_opacity_channel.jpg) | 透過シェーダー（pbr-metal-rough-with-alpha-blending）とOpacityチャンネル追加 |
| 22 | 32:45 | [fusako28_22_export_template_color_with_alpha.jpg](./fusako28_22_export_template_color_with_alpha.jpg) | エクスポート設定：Output Template「Color with Alpha」の新規プリセット作成 |
| 23 | 34:10 | [fusako28_23_texture_export_execution.jpg](./fusako28_23_texture_export_execution.jpg) | テクスチャエクスポート実行と透過PNG画像の出力確認 |
| 24 | 35:30 | [fusako28_24_blender_standard_color_alpha_node.jpg](./fusako28_24_blender_standard_color_alpha_node.jpg) | Blenderでの読み込み：Color Management「Standard」とAlpha Hashed透過ノード構築 |
