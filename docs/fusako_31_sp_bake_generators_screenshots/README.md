# ふさこ氏 Blenderキャラモデリング #31 スクリーンショットカタログ
## 【テクスチャ編04】ベイク方法とジェネレーター・フィルター (Substance 3D Painter)

本フォルダには、YouTube動画「【Blender】キャラクターモデル制作！テクスチャ編04 ベイク方法とジェネレーター・フィルター【3Dモデリング講座】」（動画ID: `QY0WSefAyKM`）から抽出した高解像度解説スクリーンショット（全24枚）を収録しています。

対応する詳細手順仕様書: [2026-09-25_fusako_sp_bake_generators_31_steps.md](../../.agents/handoffs/2026-09-25_fusako_sp_bake_generators_31_steps.md)

---

## 📸 スクリーンショット一覧（全24枚）

| No | タイムスタンプ | 画像リンク（クリックで表示） | 場面・操作内容の解説 |
|:---:|:---:|:---|:---|
| 01 | 00:20 | [fusako31_01_blender_export_body_initial.jpg](./fusako31_01_blender_export_body_initial.jpg) | **【Blender: 初回エクスポート】** 髪・顔を非表示にし、体・服・アクセサリーのメッシュのみ全選択して `body.fbx` としてエクスポート |
| 02 | 00:45 | [fusako31_02_sp_import_initial_model.jpg](./fusako31_02_sp_import_initial_model.jpg) | **【SP: 初期読み込み】** File -> New から `body.fbx` を読み込み。全パーツが密接したデフォルト姿勢 |
| 03 | 01:05 | [fusako31_03_sp_ao_black_artifact_issue.jpg](./fusako31_03_sp_ao_black_artifact_issue.jpg) | **【ベイクの落とし穴①】** ポシェットとアウターの密接面など、近接パーツの接触境界がAOベイクで真っ黒になってしまう問題 |
| 04 | 01:20 | [fusako31_04_sp_symmetry_shadow_bleeding.jpg](./fusako31_04_sp_symmetry_shadow_bleeding.jpg) | **【ベイクの落とし穴②】** 斜めがけ肩紐の影が、左右対称UVパーツの反対側にも不自然に焼き付いてしまう問題 |
| 05 | 01:45 | [fusako31_05_blender_duplicate_collection.jpg](./fusako31_05_blender_duplicate_collection.jpg) | **【Blender: コレクション複製】** 位置を崩さず復元できるよう、ACCやBodyコレクションを右クリック「Duplicate Collection」で退避複製 |
| 06 | 02:15 | [fusako31_06_blender_setup_bake_collection.jpg](./fusako31_06_blender_setup_bake_collection.jpg) | **【Blender: Bake用階層整理】** 専用の `Bake` コレクションを作成し、複製したパーツ群を整理（キーボード「2」等で単独表示） |
| 07 | 02:40 | [fusako31_07_blender_offset_gz_accessories.jpg](./fusako31_07_blender_offset_gz_accessories.jpg) | **【Blender: オフセット分離】** コレクション右クリック「Select Objects」で一括選択し、`G Z` で上方へ大きく引き離して配置 |
| 08 | 03:00 | [fusako31_08_blender_separate_outer_and_tail.jpg](./fusako31_08_blender_separate_outer_and_tail.jpg) | **【Blender: アウター・尻尾の干渉回避】** 接触するアウターや尻尾も離し、AOの相互影が落ちない十分なクリアランスを確保 |
| 09 | 03:25 | [fusako31_09_blender_mirror_object_reference.jpg](./fusako31_09_blender_mirror_object_reference.jpg) | **【Blender: ミラー対称性の維持】** 移動時に中心軸がブレないよう、ミラーモディファイアの「Mirror Object」を中央メッシュに指定 |
| 10 | 03:45 | [fusako31_10_blender_exploded_bake_layout_done.jpg](./fusako31_10_blender_exploded_bake_layout_done.jpg) | **【Blender: 分離配置（Exploded Bake）完成】** 全パーツが相互干渉しない位置に展開された状態で `body.fbx`（分離版）を上書きエクスポート |
| 11 | 04:05 | [fusako31_11_sp_project_config_reload_exploded.jpg](./fusako31_11_sp_project_config_reload_exploded.jpg) | **【SP: プロジェクト再設定】** Edit -> Project Configuration -> File「Select」から分離版FBXを再読み込み |
| 12 | 04:25 | [fusako31_12_sp_bake_mesh_maps_clean_ao.jpg](./fusako31_12_sp_bake_mesh_maps_clean_ao.jpg) | **【SP: メッシュマップベイク】** テクスチャセットセッティング「Bake mesh maps」を実行。ポシェット周囲の不要な黒ずみ影が完全に解消 |
| 13 | 04:40 | [fusako31_13_sp_b_key_world_space_normal_check.jpg](./fusako31_13_sp_b_key_world_space_normal_check.jpg) | **【SP: Bキーによるマップ診断】** `B` キーでベイク済みマップを順送り切替。World Space Normal等でUV重なりや貫通の不具合を視覚チェック |
| 14 | 05:15 | [fusako31_14_sp_bake_settings_4096_resolution.jpg](./fusako31_14_sp_bake_settings_4096_resolution.jpg) | **【SP: 本番ベイク解像度】** 512等の軽量プレビューで破綻がないことを確認後、本番出力用（4096）にサイズ引き上げ |
| 15 | 05:35 | [fusako31_15_sp_antialiasing_subsampling_4x4.jpg](./fusako31_15_sp_antialiasing_subsampling_4x4.jpg) | **【SP: アンチエイリアシング設定】** Subsamplingを `4x4` に設定。不要なNormalやIDのチェックを外し、計算時間を最適化してベイク実行 |
| 16 | 06:05 | [fusako31_16_sp_bake_finished_blender_original.jpg](./fusako31_16_sp_bake_finished_blender_original.jpg) | **【Blender: 通常配置モデルの再エクスポート】** 高解像度ベイク完了後、Blender側で元の正常な位置にあるコレクションを通常FBXエクスポート |
| 17 | 06:35 | [fusako31_17_sp_reload_original_keep_bake_maps.jpg](./fusako31_17_sp_reload_original_keep_bake_maps.jpg) | **【SP: 通常配置モデルの復元】** Project Configurationで通常FBXを再読み込み。綺麗なベイクマップを保持したまま元のポーズで作業可能に！ |
| 18 | 07:15 | [fusako31_18_sp_outer_base_fill_layer.jpg](./fusako31_18_sp_outer_base_fill_layer.jpg) | **【SP: アウター基本色の設定】** Base Color単一チャンネルのFill Layerを作成し、水色の下地色をペイント |
| 19 | 07:35 | [fusako31_19_sp_generator_ao_global_invert.jpg](./fusako31_19_sp_generator_ao_global_invert.jpg) | **【ジェネレーター①: AO】** 暗い色のFill Layer + 黒マスク + `Ambient Occlusion` ジェネレーター。「Global Invert: True」で奥まった窪みに影を投影 |
| 20 | 08:15 | [fusako31_20_sp_ao_contrast_blur_seam_warning.jpg](./fusako31_20_sp_ao_contrast_blur_seam_warning.jpg) | **【AOの重要注意点】** ブラー（Blur）は2Dテクスチャ空間でぼかすため、UVシーム境界でボケが途切れる。ブラーの過度な適用は厳禁 |
| 21 | 09:10 | [fusako31_21_sp_generator_light_screen_blend.jpg](./fusako31_21_sp_generator_light_screen_blend.jpg) | **【ジェネレーター②: Light】** 光源シミュレーション。光源アングルを前面・上方に合わせ、レイヤーブレンド「Screen」で前照灯・環境光効果 |
| 22 | 10:05 | [fusako31_22_sp_generator_world_space_normal.jpg](./fusako31_22_sp_generator_world_space_normal.jpg) | **【ジェネレーター③: World Space Normal】** 上向き（Top to Bottom）や側面の面だけに光・影を通すマスク。立体的な天面ハイライトに最適 |
| 23 | 11:05 | [fusako31_23_sp_generator_uv_border_auto_stitch.jpg](./fusako31_23_sp_generator_uv_border_auto_stitch.jpg) | **【ジェネレーター④: UV Border & Auto Stitch】** UVのシーム境界に沿った線画・縫い目（ステッチ）の自動生成テクニック |
| 24 | 12:15 | [fusako31_24_sp_filter_hsl_passthrough_grading.jpg](./fusako31_24_sp_filter_hsl_passthrough_grading.jpg) | **【フィルター & Pass Through】** レイヤーのブレンドモードを `Pass Through` に変更し、`HSL Perspective` フィルターで全体の色相・彩度・明度を一括調整 |

---
*Generated by Antigravity AI Learning Automation Engine*
