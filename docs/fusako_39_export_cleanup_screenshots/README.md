# ふさこ氏『Blenderでキャラクターモデル制作！』第39話 スクリーンショットカタログ
## 01 | エクスポート前のオブジェクトとウェイト修正【エクスポート・法線調整編】

本カタログは、YouTubeチュートリアル動画 **ふさこ氏『01 | エクスポート前のオブジェクトとウェイト修正』**（動画ID: `twg9e8ySFss`）から抽出した高解像度スクリーンショット（全24枚）のインデックスです。

詳細な操作手順、ショートカットキー、設定パラメータ、理論的背景については、以下の仕様書を参照してください：
- **詳細技術仕様書**: [`.agents/handoffs/2026-09-25_fusako_export_cleanup_39_steps.md`](../../.agents/handoffs/2026-09-25_fusako_export_cleanup_39_steps.md)

---

### スクリーンショット一覧（全24枚）

| No | タイムスタンプ | 画像ファイル名（クリックで表示） | 場面・工程タイトル | 主な解説・技術ポイント |
|:---:|:---:|:---|:---|:---|
| 01 | 00:15 | [fusako39_01_blender_unity_export_object_merge_policy.jpg](./fusako39_01_blender_unity_export_object_merge_policy.jpg) | Unityエクスポート前のオブジェクト統合方針 | ドローコール削減とパフォーマンス最適化のため、数十個のオブジェクトを部位ごとに統合する原則 |
| 02 | 00:45 | [fusako39_02_blender_modifier_apply_before_merge_rules.jpg](./fusako39_02_blender_modifier_apply_before_merge_rules.jpg) | モディファイア適用の鉄則 | `Ctrl+J` で統合すると親のモディファイアしか残らないため、ミラーやデータ転送は事前に確定適用 |
| 03 | 01:10 | [fusako39_03_blender_ctrl_a_shortcut_on_modifier_panel.jpg](./fusako39_03_blender_ctrl_a_shortcut_on_modifier_panel.jpg) | パネル上のCtrl+Aによる高速モディファイア適用 | モディファイアの上にマウスカーソルを置いて `Ctrl+A` を押すことで、素早く確定適用する時短技 |
| 04 | 01:45 | [fusako39_04_blender_solidify_outline_remove_for_unity.jpg](./fusako39_04_blender_solidify_outline_remove_for_unity.jpg) | 【最重要】Solidify（背面法輪郭線）の削除 | Unity toonシェーダー側で輪郭線を生成するため、BlenderのSolidifyモディファイアは適用せず削除 |
| 05 | 02:15 | [fusako39_05_blender_outliner_audit_ctrl_j_clothes_merge.jpg](./fusako39_05_blender_outliner_audit_ctrl_j_clothes_merge.jpg) | アウトライナー点検と服オブジェクト統合 | 矢印キーで全オブジェクトの残存モディファイアを点検し、服パーツを `Ctrl+J` で統合 |
| 06 | 05:00 | [fusako39_06_blender_vertex_weights_panel_head_neck_check.jpg](./fusako39_06_blender_vertex_weights_panel_head_neck_check.jpg) | Vertex Weightsパネルでの不要ウェイト点検 | Nパネル `Item > Vertex Weights` で首元頂点に不要なHeadボーン等のウェイトが乗っていないか確認 |
| 07 | 05:40 | [fusako39_07_blender_vertex_group_remove_unwanted_weights.jpg](./fusako39_07_blender_vertex_group_remove_unwanted_weights.jpg) | 頂点グループからのRemove実行 | 不要なボーンの頂点グループを選択し、`Remove` ボタンで影響度を完全ゼロ化 |
| 08 | 06:20 | [fusako39_08_blender_vertex_mask_v_weight_paint_smooth.jpg](./fusako39_08_blender_vertex_mask_v_weight_paint_smooth.jpg) | 頂点マスク（V）とウェイトペイントスムーズ | `V` キーで頂点マスクを有効化し、選択頂点のみに `Smooth` をかけて肩・首の連動を滑らか化 |
| 09 | 07:15 | [fusako39_09_blender_shoes_drawers_inner_merge_ctrl_j.jpg](./fusako39_09_blender_shoes_drawers_inner_merge_ctrl_j.jpg) | 靴・ドロワーズ・インナーワンピの統合 | ウェイト転送モディファイアを適用後、インナー衣服と靴を `Ctrl+J` で1オブジェクトに集約 |
| 10 | 07:50 | [fusako39_10_blender_wrist_boundary_merge_by_distance.jpg](./fusako39_10_blender_wrist_boundary_merge_by_distance.jpg) | 手首接合部のMキー（Merge by Distance）溶着 | 分離していた手と腕を統合後、接合部頂点を全選択して `M > Merge by Distance` で水密メッシュ化 |
| 11 | 08:30 | [fusako39_11_blender_outer_sleeve_dual_data_transfer_apply.jpg](./fusako39_11_blender_outer_sleeve_dual_data_transfer_apply.jpg) | アウター袖の二重データ転送の適用 | 体追従用と揺れ物用の2つのデータ転送モディファイアを確定適用し、変形カクつきを点検 |
| 12 | 09:40 | [fusako39_12_blender_vertex_weights_copy_inner_outer_fix.jpg](./fusako39_12_blender_vertex_weights_copy_inner_outer_fix.jpg) | 【神技】袖内側・外側ウェイトの完全一致コピー | `Vertex Weights` パネルで調整頂点 $\to$ 対象頂点を選択し `Copy`。二重構造の貫通を根絶 |
| 13 | 11:00 | [fusako39_13_blender_hood_crease_mask_weight_smooth.jpg](./fusako39_13_blender_hood_crease_mask_weight_smooth.jpg) | フード下降時のシワ崩れスムーズ補正 | フードを下げた際に変形が崩れる領域を頂点マスク選択し、ウェイトペイントのスムーズで整地 |
| 14 | 16:15 | [fusako39_14_blender_special_parts_weight_mirror_setup.jpg](./fusako39_14_blender_special_parts_weight_mirror_setup.jpg) | 特殊表情パーツ（ハート目・青ざめ）のウェイト設定 | ハート目・キラキラ目・青ざめメッシュにHeadボーンのウェイト（1.0）を指定し追従を確認 |
| 15 | 16:30 | [fusako39_15_blender_apply_modifier_keep_shapekeys_face_parts.jpg](./fusako39_16_blender_face_teeth_eyes_special_ctrl_j_merge.jpg) | Keep Shapekeysアドオンによる顔パーツ適用 | シェイプキーを持つ口内・歯・舌・耳・ハート目のミラーモディファイアを安全に確定適用 |
| 16 | 17:30 | [fusako39_16_blender_face_teeth_eyes_special_ctrl_j_merge.jpg](./fusako39_16_blender_face_teeth_eyes_special_ctrl_j_merge.jpg) | 顔・口内・瞳・特殊表情パーツのCtrl+J一括統合 | 全顔面パーツを選択し、最後にメイン顔を選択して `Ctrl+J`。シェイプキーの正常動作を確認 |
| 17 | 18:15 | [fusako39_17_blender_alt_r_alt_g_pose_reset_accessory_transfer.jpg](./fusako39_17_blender_alt_r_alt_g_pose_reset_accessory_transfer.jpg) | ポーズ初期化（Alt+R/G）と小物ウェイト転送 | ポーズが傾いたまま転送すると歪むため、必ず `Alt+R`, `Alt+G` でレスト位置に戻して適用 |
| 18 | 19:35 | [fusako39_18_blender_pochette_data_transfer_nearest_face.jpg](./fusako39_18_blender_pochette_data_transfer_nearest_face.jpg) | ポシェットのデータ転送（Nearest Face Interpolated） | アウターからポシェットへの頂点グループ転送（最近接面の補間）を設定・適用 |
| 19 | 21:30 | [fusako39_19_blender_accessory_modifiers_apply_lattice_cleanup.jpg](./fusako39_19_blender_accessory_modifiers_apply_lattice_cleanup.jpg) | 小物モディファイア適用と不要ラティス退避 | ポシェット紐や羽のモディファイアを適用後、不要になったラティスオブジェクトを隔離削除 |
| 20 | 23:05 | [fusako39_20_blender_add_custom_split_normals_data_preservation.jpg](./fusako39_20_blender_add_custom_split_normals_data_preservation.jpg) | 【神技】Add Custom Split Normals Data実行 | 統合時にオートスムース角が消えるのを防ぐため、カスタム分割法線データに焼き込み変換 |
| 21 | 23:35 | [fusako39_21_blender_mark_sharp_preserved_ctrl_j_merge.jpg](./fusako39_21_blender_mark_sharp_preserved_ctrl_j_merge.jpg) | マークシャープ法線を完全保持した小物統合 | パッチン留めと髪リボンを `Ctrl+J` で統合しても、美しいエッジの陰影が100%保持される |
| 22 | 24:10 | [fusako39_22_blender_unity_naming_convention_f2_rename.jpg](./fusako39_22_blender_unity_naming_convention_f2_rename.jpg) | Unity向け命名規則（F2、キャラ名_部位名） | 他アセットとの衝突を防ぐため、オブジェクト名を `Chara_Face`, `Chara_Body` 等にリネーム |
| 23 | 25:40 | [fusako39_23_blender_ground_contact_gz_root_bone_origin_fix.jpg](./fusako39_23_blender_ground_contact_gz_root_bone_origin_fix.jpg) | 足裏接地（GZ）とルートボーン原点配置 | 足裏がZ=0に接地するよう全体を引き上げ、ルートボーンのHead Zをピタリ `0.0` に設定 |
| 24 | 25:45 | [fusako39_24_blender_ctrl_a_all_transforms_normalization.jpg](./fusako39_24_blender_ctrl_a_all_transforms_normalization.jpg) | 全トランスフォーム適用（All Transforms正規化） | 全選択して `Ctrl+A > All Transforms`。位置(0,0,0)、回転(0,0,0)、スケール(1,1,1)に確定 |
