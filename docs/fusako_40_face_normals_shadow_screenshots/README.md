# ふさこ氏『Blenderでキャラクターモデル制作！』第40話 スクリーンショットカタログ
## 02 | 顔の法線調整と前髪の影つけ【チュートリアル完結記念・最終回】

本カタログは、YouTubeチュートリアル動画 **ふさこ氏『02 | 顔の法線調整と前髪の影つけ』**（動画ID: `WtaMWiaDDLY`）から抽出した高解像度スクリーンショット（全24枚）のインデックスです。

詳細な操作手順、ショートカットキー、設定パラメータ、理論的背景については、以下の仕様書を参照してください：
- **詳細技術仕様書**: [`.agents/handoffs/2026-09-25_fusako_face_normals_shadow_40_steps.md`](../../.agents/handoffs/2026-09-25_fusako_face_normals_shadow_40_steps.md)

---

### スクリーンショット一覧（全24枚）

| No | タイムスタンプ | 画像ファイル名（クリックで表示） | 場面・工程タイトル | 主な解説・技術ポイント |
|:---:|:---:|:---|:---|:---|
| 01 | 00:15 | [fusako40_01_blender_bangs_shadow_mesh_concept_duplicate.jpg](./fusako40_01_blender_bangs_shadow_mesh_concept_duplicate.jpg) | 前髪の落ち影板ポリの構想と複製 | イラスト調のアニメ落ち影を再現するため、前髪メッシュから面を選択して複製（Shift+D, P分離） |
| 02 | 00:35 | [fusako40_02_blender_alt_s_shrink_shadow_plane_fit.jpg](./fusako40_02_blender_alt_s_shrink_shadow_plane_fit.jpg) | Alt+Sによる収縮と隙間挟み込み | `Alt+S` でわずかに収縮させ、前髪と額の狭い隙間にぴったり収まるようにフィット配置 |
| 03 | 01:15 | [fusako40_03_blender_shadow_mesh_mirror_simplify.jpg](./fusako40_03_blender_shadow_mesh_mirror_simplify.jpg) | 前髪影のミラー設定と形状軽量化 | 不要な厚みポリゴンを削除して軽量化し、片側メッシュにミラーモディファイアを適用 |
| 04 | 02:40 | [fusako40_04_blender_shadow_subtle_peeking_placement.jpg](./fusako40_04_blender_shadow_subtle_peeking_placement.jpg) | 前髪下端からチラ見えする絶妙配置 | 正面ビューから見て前髪の下端からわずかに影がのぞくよう、頂点を丁寧に微調整 |
| 05 | 03:45 | [fusako40_05_blender_shadow_mesh_mirror_apply_merge.jpg](./fusako40_05_blender_shadow_mesh_mirror_apply_merge.jpg) | 影メッシュの確定（ミラー適用・統合） | 形状確定後、ミラーモディファイアを適用して前髪オブジェクトに `Ctrl+J` で統合 |
| 06 | 09:05 | [fusako40_06_blender_unity_toon_shader_material_separation_plan.jpg](./fusako40_06_blender_unity_toon_shader_material_separation_plan.jpg) | Unityトゥーンシェーダー向けマテリアル分割方針 | 前髪越し透過、アウトライン有無、影無効化を制御するためマテリアルスロットを細分化 |
| 07 | 09:30 | [fusako40_07_blender_hair_bang_and_back_material_assign.jpg](./fusako40_07_blender_hair_bang_and_back_material_assign.jpg) | Hair_Bang（前髪）とHair_Back（後髪）の分割 | 前髪部分を `L` キー選択し、透過制御用の別マテリアル `M_Hair_Bang` にアサイン |
| 08 | 10:30 | [fusako40_08_blender_transparent_shader_node_hookup.jpg](./fusako40_08_blender_transparent_shader_node_hookup.jpg) | シェーダーノードでの透過テクスチャ直結 | Principled BSDFのBaseColorとAlphaにテクスチャを直結し、Blend Modeを透過設定 |
| 09 | 11:15 | [fusako40_09_blender_brows_material_separation_front_render.jpg](./fusako40_09_blender_brows_material_separation_front_render.jpg) | 眉毛（Brows）マテリアル分割 | 前髪越しに透かして最前面に描画するため、眉毛メッシュを独立スロット `M_Brows` に分割 |
| 10 | 12:05 | [fusako40_10_blender_eyes_material_separation_no_outline.jpg](./fusako40_10_blender_eyes_material_separation_no_outline.jpg) | 瞳・白目（Eyes）マテリアル分割 | アウトラインを消し、落ち影を無効化するため瞳メッシュを独立スロット `M_Eyes` に分割 |
| 11 | 14:10 | [fusako40_11_blender_face_normal_adjustment_rationale.jpg](./fusako40_11_blender_face_normal_adjustment_rationale.jpg) | 顔の法線調整の目的解説（アニメ陰影の平坦化） | 鼻や口の立体凹凸による汚いギザギザ影を消し、美しいセルルック陰影にする理論 |
| 12 | 14:30 | [fusako40_12_blender_face_duplicate_shift_d_x_prep.jpg](./fusako40_12_blender_face_duplicate_shift_d_x_prep.jpg) | 顔メッシュの横複製（Shift+D X） | 法線転送のソース（転送元）を作成するため、顔メッシュを横に複製してアーマチュアを削除 |
| 13 | 14:45 | [fusako40_13_blender_cast_modifier_sphere_factor_1.jpg](./fusako40_13_blender_cast_modifier_sphere_factor_1.jpg) | Castモディファイア（Sphere, Factor 1.0） | 複製した顔に `Cast` モディファイアを追加し、形状を完全な球体（Sphere）に変形 |
| 14 | 15:00 | [fusako40_14_blender_affect_only_origins_center_sphere.jpg](./fusako40_14_blender_affect_only_origins_center_sphere.jpg) | Affect Only Originsによる原点の中心移動 | 原点移動モードをONにし、オブジェクト原点を顔の中心に合わせることで真球に変形 |
| 15 | 15:20 | [fusako40_15_blender_data_transfer_custom_normals_setup.jpg](./fusako40_15_blender_data_transfer_custom_normals_setup.jpg) | Data Transferモディファイアの法線転送設定 | 元顔にデータ転送を追加し、`Custom Normals`（カスタム法線）をONに設定 |
| 16 | 15:35 | [fusako40_16_blender_mapping_topology_smooth_normal_check.jpg](./fusako40_16_blender_mapping_topology_smooth_normal_check.jpg) | Mapping Topologyによる球体法線転送確認 | 同一トポロジーで球体法線が転送され、顔の陰影がぬるっと滑らかになったことを確認 |
| 17 | 16:00 | [fusako40_17_blender_vertex_group_custom_normal_ear_exclude.jpg](./fusako40_17_blender_vertex_group_custom_normal_ear_exclude.jpg) | 頂点グループによる耳・まつ毛の法線転送除外 | 耳やまつ毛の立体感が消えないよう、頂点グループ `Custom_Normal` で肌・白目のみに制限 |
| 18 | 16:45 | [fusako40_18_blender_interactive_origin_tweak_anime_shadow.jpg](./fusako40_18_blender_interactive_origin_tweak_anime_shadow.jpg) | 球体原点の微調整による極上セルルックの追求 | 球体顔の原点を上下前後に微調整し、光が当たった際の理想的なアニメ顔陰影を追い込む |
| 19 | 17:00 | [fusako40_19_blender_data_transfer_apply_cleanup.jpg](./fusako40_19_blender_data_transfer_apply_cleanup.jpg) | データ転送モディファイアの確定適用 | 理想の陰影になった状態でデータ転送を適用（Apply）し、転送元メッシュを隔離退避 |
| 20 | 18:45 | [fusako40_20_blender_hem_phys_bone_parent_to_spine.jpg](./fusako40_20_blender_hem_phys_bone_parent_to_spine.jpg) | 裾揺れ物ボーン統括親（Hem_Phys）のセットアップ | 裾揺れ物ボーン群の親ボーン `Hem_Phys` を新規追加し、Spineボーンに `Keep Offset` で親子付け |
| 21 | 19:45 | [fusako40_21_blender_hair_phys_bone_parent_to_head.jpg](./fusako40_21_blender_hair_phys_bone_parent_to_head.jpg) | 髪揺れ物ボーン統括親（Hair_Phys）のセットアップ | 髪揺れ物ボーン群の親ボーン `Hair_Phys` を新規追加し、Headボーンに親子付け |
| 22 | 20:35 | [fusako40_22_blender_armature_pose_wing_flutter_prep.jpg](./fusako40_22_blender_armature_pose_wing_flutter_prep.jpg) | アーマチュア変形による羽のポーズ付け | ポーズモードで羽ボーンを動かし、まばたき時に連動させたい羽の傾き姿勢を作成 |
| 23 | 20:50 | [fusako40_23_blender_save_as_shapekey_from_armature_pose.jpg](./fusako40_23_blender_save_as_shapekey_from_armature_pose.jpg) | 【神技】Save as Shape Keyによるポーズのシェイプキー化 | Armatureモディファイアのメニューから `Save as Shape Key` を押し、ポーズを変形キーに一発変換 |
| 24 | 21:40 | [fusako40_24_blender_wing_shapekey_verified_unity_ready.jpg](./fusako40_24_blender_wing_shapekey_verified_unity_ready.jpg) | 羽シェイプキー動作確認とUnityエクスポート前準備完了！ | 生成された羽上下シェイプキーをテスト動作し、全工程の完了を確認！UnityへGO！ |
