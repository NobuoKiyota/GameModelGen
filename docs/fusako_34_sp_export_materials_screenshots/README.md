# ふさこ氏 Blenderキャラモデリング #34 スクリーンショットカタログ
## 【テクスチャ編07・完結】エクスポートと質感の調整 (Substance 3D Painter & Blender)

本フォルダには、YouTube動画「【Blender】キャラクターモデル制作！テクスチャ編07 エクスポートと質感の調整【3Dモデリング講座】」（動画ID: `hApZwvlJO4s`）から抽出した高解像度解説スクリーンショット（全24枚）を収録しています。

対応する詳細手順仕様書: [2026-09-25_fusako_sp_export_materials_34_steps.md](../../.agents/handoffs/2026-09-25_fusako_sp_export_materials_34_steps.md)

---

## 📸 スクリーンショット一覧（全24枚）

| No | タイムスタンプ | 画像リンク（クリックで表示） | 場面・操作内容の解説 |
|:---:|:---:|:---|:---|
| 01 | 00:15 | [fusako34_01_sp_file_export_textures_png.jpg](./fusako34_01_sp_file_export_textures_png.jpg) | **【SP: エクスポート設定】** File -> Export Textures から出力先フォルダ、PNG形式を指定して一括書き出し |
| 02 | 00:40 | [fusako34_02_blender_image_texture_node_open.jpg](./fusako34_02_blender_image_texture_node_open.jpg) | **【Blender: テクスチャ読み込み】** 各マテリアルのシェーダーエディタで画像テクスチャノードにエクスポート画像を割り当て |
| 03 | 00:55 | [fusako34_03_blender_node_wrangler_direct_output.jpg](./fusako34_03_blender_node_wrangler_direct_output.jpg) | **【Blender: ノード直結表示】** Node Wrangler（Shift+Ctrlクリック）で画像テクスチャをMaterial Outputに直接接続 |
| 04 | 01:25 | [fusako34_04_blender_viewport_texture_check.jpg](./fusako34_04_blender_viewport_texture_check.jpg) | **【Blender: 塗り残し・アラ点検】** ビューポートでテクスチャの塗り残しや色味を点検（必要時SPに戻って修正） |
| 05 | 01:55 | [fusako34_05_blender_duplicate_collection_safety.jpg](./fusako34_05_blender_duplicate_collection_safety.jpg) | **【Blender: コレクション複製・退避】** SP再出力に備え、作業用コレクションを Duplicate Collection で安全に複製保存 |
| 06 | 02:30 | [fusako34_06_blender_outline_material_emission.jpg](./fusako34_06_blender_outline_material_emission.jpg) | **【背面法アウトライン①: マテリアル作成】** Principled BSDF を Emission（放射）に変更し陰影の影響を受けないフラット線に設定 |
| 07 | 02:45 | [fusako34_07_blender_backface_culling_color_pick.jpg](./fusako34_07_blender_backface_culling_color_pick.jpg) | **【背面法アウトライン②: 必須設定】** 色を濃い紫に設定し、マテリアル設定で `Backface Culling`（裏面非表示）にチェック |
| 08 | 03:00 | [fusako34_08_blender_solidify_thickness_flip_offset.jpg](./fusako34_08_blender_solidify_thickness_flip_offset.jpg) | **【背面法アウトライン③: Solidify】** Thicknessをマイナス値（-0.005等）、Flip Normals ON、Material Offsetを1に設定 |
| 09 | 03:25 | [fusako34_09_blender_vertex_group_edge_scale_setup.jpg](./fusako34_09_blender_vertex_group_edge_scale_setup.jpg) | **【頂点グループマスク①】** アウトライン太さ制御用頂点グループ `edge_scale` を作成し、SolidifyのVertex Groupに割り当て |
| 10 | 03:55 | [fusako34_10_blender_remove_eye_white_from_outline.jpg](./fusako34_10_blender_remove_eye_white_from_outline.jpg) | **【頂点グループマスク②: 目の除外】** 目の白目メッシュを選択し、edge_scaleグループから `Remove`（ウェイト0化） |
| 11 | 04:15 | [fusako34_11_blender_select_loop_inner_region_mouth.jpg](./fusako34_11_blender_select_loop_inner_region_mouth.jpg) | **【頂点グループマスク③: 口内の一発除外】** `Select Loop Inner-Region` で口の奥を一発全選択してedge_scaleから除外 |
| 12 | 04:45 | [fusako34_12_blender_ctrl_l_link_materials.jpg](./fusako34_12_blender_ctrl_l_link_materials.jpg) | **【効率化①: マテリアル一括リンク】** 複数オブジェクト選択 $\to$ `Ctrl + L`（Link Materials）でアウトラインマテリアルを一括共有 |
| 13 | 05:00 | [fusako34_13_blender_ctrl_c_copy_solidify_modifier.jpg](./fusako34_13_blender_ctrl_c_copy_solidify_modifier.jpg) | **【効率化②: モディファイア一括コピー】** `Ctrl + C`（Copy Attributes） $\to$ Copy Selected Modifiers でSolidifyを一瞬で全パーツ展開 |
| 14 | 05:40 | [fusako34_14_blender_batch_outline_applied_all.jpg](./fusako34_14_blender_batch_outline_applied_all.jpg) | **【全パーツアウトライン展開完了】** 体・服・アクセサリーの全パーツに均一なセルルック線画が反映された状態 |
| 15 | 06:10 | [fusako34_15_blender_scene_world_background_color.jpg](./fusako34_15_blender_scene_world_background_color.jpg) | **【背景環境調整】** Scene Worldにチェックを入れ、ワールド背景色を明るくして線画の視認性を最大化 |
| 16 | 07:45 | [fusako34_16_blender_hair_outline_branch_artifact.jpg](./fusako34_16_blender_hair_outline_branch_artifact.jpg) | **【髪アウトラインの落とし穴】** 毛束の枝分かれや谷間部分で線画が黒く汚く交差・重なってしまう問題 |
| 17 | 08:50 | [fusako34_17_blender_hair_vertex_group_clean_outline.jpg](./fusako34_17_blender_hair_vertex_group_clean_outline.jpg) | **【髪線画ノイズの解消】** 枝分かれ根元の頂点ウェイトを小さく/ゼロにし、不自然な黒い塊を綺麗に解消 |
| 18 | 09:20 | [fusako34_18_blender_proportion_review_reference_side.jpg](./fusako34_18_blender_proportion_review_reference_side.jpg) | **【バランス最終調整の準備】** 正面リファレンス画像を横に複製配置し、不透明度を調整して比較準備 |
| 19 | 10:10 | [fusako34_19_blender_armature_pose_x_symmetry_match.jpg](./fusako34_19_blender_armature_pose_x_symmetry_match.jpg) | **【ポーズ合わせ】** アーマチュアのポーズモードでX軸対称をONにし、元絵の立ち姿と同じポーズを取らせて比較 |
| 20 | 10:45 | [fusako34_20_blender_proportional_edit_leg_length.jpg](./fusako34_20_blender_proportional_edit_leg_length.jpg) | **【足・プロポーション微調整】** プロポーショナル編集で足の長さや太さを元絵のプロポーションにピタリと整合 |
| 21 | 12:00 | [fusako34_21_blender_sleeve_volume_hands_adjustment.jpg](./fusako34_21_blender_sleeve_volume_hands_adjustment.jpg) | **【袖・服のボリューム調整】** 萌え袖の手先の隠れ具合、袖の膨らみ、首元の開き具合を徹底的にリファイン |
| 22 | 13:45 | [fusako34_22_blender_pochette_strap_separate_local_rot.jpg](./fusako34_22_blender_pochette_strap_separate_local_rot.jpg) | **【小物の角度調整】** 肩紐を `P` で一時分離し、本体のみローカル軸（Orientation: Normal）で反時計回りに傾き調整 |
| 23 | 14:15 | [fusako34_23_blender_final_balance_weight_transfer_note.jpg](./fusako34_23_blender_final_balance_weight_transfer_note.jpg) | **【ウェイト転送の同期注意点】** 足位置変更に伴い、ウェイト転送用素体メッシュも同期修正する重要ルール |
| 24 | 14:45 | [fusako34_24_blender_sp_texture_series_completed.jpg](./fusako34_24_blender_sp_texture_series_completed.jpg) | **【テクスチャ編完結・シェイプキー編へ】** テクスチャ・線画・最終プロポーションが完璧に整い、表情シェイプキー制作へ進出 |

---
*Generated by Antigravity AI Learning Automation Engine*
