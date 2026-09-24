# ふさこ氏『Blenderでキャラクターモデル制作！#22』重要シーン・スクリーンショット集

本ディレクトリには、YouTubeチュートリアル動画 **『【Blender】髪や揺れ物のスキニング！【キャラクターモデル制作！#22】』**（講師: ふさこ氏、時間: 17分57秒、URL: `https://www.youtube.com/watch?v=2B7ofTckPic`）の解説工程に対応する高解像度スクリーンショット（全24枚）を保存しています。

本動画に対応する詳細な手順解説・トラブルシューティングは、以下の仕様書を参照してください。
👉 **[リギング編 第4回 詳細技術仕様書（ステップバイステップ解説）](../../.agents/handoffs/2026-09-24_fusako_rigging_skinning_hair_22_steps.md)**

---

## 収録スクリーンショット一覧（全24枚）

### Chapter 1: 袖（Sleeve）の貫通防止回転とプロキシスキニング (00:00〜09:15)

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー表示） | シーン解説・操作ポイント |
| :---: | :---: | :--- | :--- |
| 01 | 00:00:28 | [01_c1_arm_down_penetration_problem.jpg](./01_c1_arm_down_penetration_problem.jpg) | **腕下げ時の貫通課題**: 腕を下げた際に袖が体幹（脇・胴体）へ深く入り込む物理演算上の破綻を確認。 |
| 02 | 00:00:55 | [02_c1_shoulder_loop_cursor_pivot.jpg](./02_c1_shoulder_loop_cursor_pivot.jpg) | **肩ピボットの設定**: 肩に近い袖ループを選択し、`Shift + S > Cursor to Selected` で回転中心を配置。 |
| 03 | 00:01:25 | [03_c1_rotate_sleeve_backward_rx.jpg](./03_c1_rotate_sleeve_backward_rx.jpg) | **袖の事前回転 (`R X`)**: 腕を下ろした時に袖が体の後ろ側へ逃げるよう、あらかじめ角度を後ろ向きに回転。 |
| 04 | 00:01:55 | [04_c1_duplicate_sleeve_proxy_mesh.jpg](./04_c1_duplicate_sleeve_proxy_mesh.jpg) | **袖プロキシの作成**: 袖口先端メッシュ面を `Shift + D` で複製し、`P > Selection` で別オブジェクトに分離。 |
| 05 | 00:02:25 | [05_c1_sleeve_bone_create_from_lowerarm.jpg](./05_c1_sleeve_bone_create_from_lowerarm.jpg) | **袖ボーンの追加**: 前腕ボーン (`LowerArm`) を `Shift + D` で複製し、`Sleeve.L` / `Sleeve.R` を作成。 |
| 06 | 00:03:05 | [06_c1_sleeve_bone_parent_lowerarm_keep_offset.jpg](./06_c1_sleeve_bone_parent_lowerarm_keep_offset.jpg) | **前腕への親子付け**: `Sleeve` $\to$ `LowerArm` の順に選択し、`Ctrl + P > Keep Offset` で階層接続。 |
| 07 | 00:03:35 | [07_c1_proxy_vertex_group_sleeve_assign.jpg](./07_c1_proxy_vertex_group_sleeve_assign.jpg) | **プロキシ頂点割当**: プロキシメッシュに `Sleeve.L` 頂点グループを作成し、全頂点に Weight 1.0 をアサイン。 |
| 08 | 00:04:15 | [08_c1_sleeve_data_transfer_modifier.jpg](./08_c1_sleeve_data_transfer_modifier.jpg) | **Data Transfer モディファイア適用**: 袖本体にモディファイア追加（Nearest Face Interpolated / Generate Data Layers）。 |
| 09 | 00:04:50 | [09_c1_sleeve_mask_vertex_group_create.jpg](./09_c1_sleeve_mask_vertex_group_create.jpg) | **袖マスク頂点グループの作成**: 袖口先端のみを選択し、転送範囲を限定するマスクグループを作成・アサイン。 |
| 10 | 00:05:05 | [10_c1_data_transfer_vertex_group_limit.jpg](./10_c1_data_transfer_vertex_group_limit.jpg) | **転送範囲の制限**: Data Transfer の頂点グループ制限にマスクを指定し、袖口のみが揺れ動く挙動を確認。 |
| 11 | 00:05:35 | [11_c1_weight_smooth_active_group_expand.jpg](./11_c1_weight_smooth_active_group_expand.jpg) | **ウェイトのスムーズ減衰**: ウェイトペイントで `Weights > Smooth`（Active Group, Expand）でなだらかに拡散。 |
| 12 | 00:06:45 | [12_c1_subtract_armpit_thumb_penetration_fix.jpg](./12_c1_subtract_armpit_thumb_penetration_fix.jpg) | **脇下・親指の貫通防止**: 不要な脇下や手の親指周辺のウェイトを `Subtract`（引き算ブラシ）で除去。 |
| 13 | 00:07:55 | [13_c1_modifier_order_data_transfer_solidify.jpg](./13_c1_modifier_order_data_transfer_solidify.jpg) | **モディファイア積層順の極意**: `Data Transfer` $\to$ `Solidify` の順に配置し、布の表裏で同一ウェイトを完全保持。 |
| 14 | 00:08:45 | [14_c1_elbow_loopcut_and_twist_fix.jpg](./14_c1_elbow_loopcut_and_twist_fix.jpg) | **肘曲げ時の貫通防止**: 肘部分にループカット（`Ctrl + R`）を追加し、ねじれ・引きつれをトポロジー修正。 |

---

### Chapter 2: 尻尾（Tail）のボーン配置とウェイトスムーズ (09:15〜14:30)

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー表示） | シーン解説・操作ポイント |
| :---: | :---: | :--- | :--- |
| 15 | 09:35 | [15_c2_tail_local_view_cursor_root.jpg](./15_c2_tail_local_view_cursor_root.jpg) | **尻尾の単体表示**: `/` キーでローカルビューに入り、根元ループの中心に 3D Cursor を配置。 |
| 16 | 10:10 | [16_c2_tail_bone_chain_extrude.jpg](./16_c2_tail_bone_chain_extrude.jpg) | **尻尾ボーンチェーンの作成**: 単一ボーン追加後、`E` で6節押し出して `Tail.001`〜`Tail.006` を作成。 |
| 17 | 10:35 | [17_c2_tail_automatic_weights_check.jpg](./17_c2_tail_automatic_weights_check.jpg) | **自動ウェイト後の関節カクつき確認**: `With Automatic Weights` 適用後、個別回転で多重関節の折れ曲がりを確認。 |
| 18 | 11:05 | [18_c2_cage_display_vertex_selection.jpg](./18_c2_cage_display_vertex_selection.jpg) | **ケージ表示での関節頂点選択**: Armatureモディファイアのケージ表示ONで、カクつく関節リング頂点を選択。 |
| 19 | 11:35 | [19_c2_weight_smooth_deform_pose_bones.jpg](./19_c2_weight_smooth_deform_pose_bones.jpg) | **Deform Pose Bones スムーズ**: 頂点マスク（`V`）＋ `Weights > Smooth`（Subset: Deform Pose Bones）で滑らか化。 |
| 20 | 12:40 | [20_c2_vertex_weights_copy_loop_unify.jpg](./20_c2_vertex_weights_copy_loop_unify.jpg) | **円周ループのウェイト統一 (Copy)**: ループ内外のウェイト差による痩せを **Vertex Weights > Copy** で一括均一化。 |
| 21 | 13:40 | [21_c2_limit_total_4_bones_unity_vrm.jpg](./21_c2_limit_total_4_bones_unity_vrm.jpg) | **【実機必須】Limit Total (4ボーン制限)**: Unity/VRM規格に合わせ、`Weights > Limit Total (Limit: 4)` を実行。 |

---

### Chapter 3: アーマチュア統合とボーン階層親子付け (14:30〜17:57)

| No | タイムスタンプ | 画像ファイル名（クリックでプレビュー表示） | シーン解説・操作ポイント |
| :---: | :---: | :--- | :--- |
| 22 | 14:55 | [22_c3_clear_keep_transform_join_armature.jpg](./22_c3_clear_keep_transform_join_armature.jpg) | **親子関係解除とアーマチュア統合**: `Alt + P > Clear and Keep Transformation` 後、本体と `Ctrl + J` で統合。 |
| 23 | 15:35 | [23_c3_parent_tail_and_skirt_to_hips_spine.jpg](./23_c3_parent_tail_and_skirt_to_hips_spine.jpg) | **ボーン階層接続**: `Tail` 根元を `Hips`、スカート最上段ボーンを `Spine` に `Ctrl + P > Keep Offset` で親子付け。 |
| 24 | 16:45 | [24_c3_skirt_mask_top_loop_remove_complete.jpg](./24_c3_skirt_mask_top_loop_remove_complete.jpg) | **体幹連動とリギング完結**: スカート最上段ループをマスクから外し、全身ポーズ連動チェックを完了。 |
