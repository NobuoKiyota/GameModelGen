# ふさこ氏『手のモデリング/リギング/スキニング後編（第6回）』重要シーン・スクリーンショット集

元動画: [Blenderでキャラクターモデル制作！06 | 手のモデリング/リギング/スキニング（後編）〜初級から中級者向けチュートリアル〜](https://www.youtube.com/watch?v=kbQzguK_p18)  
動画長: 36分43秒  
対応仕様書: [`.agents/handoffs/2026-09-24_fusako_hand_modeling_06_steps.md`](../../.agents/handoffs/2026-09-24_fusako_hand_modeling_06_steps.md)

---

## 📸 スクリーンショット一覧（全35枚）

### 【Chapter 1: 掌（手のひら）のベースモデリング】 (00:00 〜 05:00)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 01 | 00:00:25 | [01_c1_palm_cube_open_tube.jpg](./01_c1_palm_cube_open_tube.jpg) | 立方体を追加し、上下面を削除して4面の筒として配置 |
| 02 | 00:01:40 | [02_c1_palm_little_finger_loop.jpg](./02_c1_palm_little_finger_loop.jpg) | 小指側側面のループカット追加とAlt+Sでのふくらみ調整 |
| 03 | 00:02:20 | [03_c1_palm_index_finger_loop.jpg](./03_c1_palm_index_finger_loop.jpg) | 人差し指のセンターラインにつながる縦ループの配置 |
| 04 | 00:03:00 | [04_c1_palm_middle_ring_loops.jpg](./04_c1_palm_middle_ring_loops.jpg) | 中指・薬指のラインに合わせたループカットの追加 |
| 05 | 00:04:10 | [05_c1_hypothenar_alts_fatten.jpg](./05_c1_hypothenar_alts_fatten.jpg) | 横から見た小指球（小指付け根の膨らみ）をAlt+Sで肉厚化 |
| 06 | 00:04:35 | [06_c1_thenar_alts_fatten.jpg](./06_c1_thenar_alts_fatten.jpg) | 母指球（親指付け根のふくらみ）の形成 |

---

### 【Chapter 2: 親指の独立化と手のひらへの接続】 (05:00 〜 10:00)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 07 | 00:05:15 | [07_c2_thumb_make_single_user.jpg](./07_c2_thumb_make_single_user.jpg) | **【重要】親指メッシュのリンク解除（Make Single User）**。共有数「5」をクリック |
| 08 | 00:06:30 | [08_c2_thumb_base_delete_fatten.jpg](./08_c2_thumb_base_delete_fatten.jpg) | 親指底面ループを削除し、腹側をAlt+Sで手のひらの断面に合わせて大きく膨らませる |
| 09 | 00:07:45 | [09_c2_thumb_vertex_snap_approach.jpg](./09_c2_thumb_vertex_snap_approach.jpg) | 頂点スナップをONにし、親指と手のひらの頂点を互いに歩み寄らせる |
| 10 | 00:08:20 | [10_c2_thumb_face_fill_f.jpg](./10_c2_thumb_face_fill_f.jpg) | 隙間の4頂点を選択し、`F`（面張り）で母指球と接続 |
| 11 | 00:09:30 | [11_c2_thumb_webbing_topology.jpg](./11_c2_thumb_webbing_topology.jpg) | 親指と人差し指の間の水かきトポロジーを整流 |

---

### 【Chapter 3: リンク解除・ボーンリネーム・オブジェクト統合】 (10:00 〜 15:00)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 12 | 00:11:45 | [12_c3_make_single_user_obj_data.jpg](./12_c3_make_single_user_obj_data.jpg) | **【重要】Object > Relations > Make Single User > Object & Data で全指のリンクを一括解除** |
| 13 | 00:12:25 | [13_c3_armature_single_user.jpg](./13_c3_armature_single_user.jpg) | アーマチュアも同様にシングルユーザー化 |
| 14 | 00:13:20 | [14_c3_bone_rename_index_proximal.jpg](./14_c3_bone_rename_index_proximal.jpg) | ボーン名をUnityヒューマノイド規格（`Index_Proximal` 等）へF2でリネーム |
| 15 | 00:13:40 | [15_c3_vgroup_auto_sync_check.jpg](./15_c3_vgroup_auto_sync_check.jpg) | **【Tips】ボーンのリネームに連動して頂点グループ名も自動更新されたことを確認** |
| 16 | 00:14:40 | [16_c3_armatures_apply_all_transforms.jpg](./16_c3_armatures_apply_all_transforms.jpg) | **【必須】全ボーンのトランスフォームを適用（Ctrl + A > All Transforms）** |
| 17 | 00:14:55 | [17_c3_armatures_join_ctrl_j.jpg](./17_c3_armatures_join_ctrl_j.jpg) | 全指のボーンを `Ctrl + J` で1つのアーマチュアに統合 |

---

### 【Chapter 4: 指と手のひらの接合と手首の形成】 (15:00 〜 24:00)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 18 | 00:16:15 | [18_c4_finger_base_shear_arch.jpg](./18_c4_finger_base_shear_arch.jpg) | 指の付け根ループをシアー（Shear）で中指が高い山なりアーチに傾斜 |
| 19 | 00:16:40 | [19_c4_snap_automerge_fingers_to_palm.jpg](./19_c4_snap_automerge_fingers_to_palm.jpg) | 頂点スナップ＋Auto Mergeで手のひらと指の付け根頂点を吸着結合 |
| 20 | 00:17:30 | [20_c4_merge_by_distance.jpg](./20_c4_merge_by_distance.jpg) | `M` > By Distance（距離でマージ）で二重頂点を完全溶接 |
| 21 | 00:18:00 | [21_c4_knife_cuts_on_palm.jpg](./21_c4_knife_cuts_on_palm.jpg) | ナイフツール（`K`）で手のひら・手の甲に接続用の割りを追加 |
| 22 | 00:19:15 | [22_c4_fill_webbing_faces.jpg](./22_c4_fill_webbing_faces.jpg) | 指と指の間の水かき面を `F` で綺麗に四角面穴埋め |
| 23 | 00:20:30 | [23_c4_wrist_extrude_sz0_level.jpg](./23_c4_wrist_extrude_sz0_level.jpg) | 手首開口部ループを選択し、`E` 押し出し $\to$ `S Z 0` で水平に揃えて伸ばす |
| 24 | 00:22:45 | [24_c4_wrist_cross_section_oval.jpg](./24_c4_wrist_cross_section_oval.jpg) | 手首断面を滑らかな楕円形に整流 |

---

### 【Chapter 5: 手のひら・前腕ボーン追加とスキニング】 (24:00 〜 36:43)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 25 | 00:24:55 | [25_c5_add_hand_lowerarm_bones.jpg](./25_c5_add_hand_lowerarm_bones.jpg) | 手首から手のひらへ `Hand`、手首から腕へ `LowerArm` ボーンを追加 |
| 26 | 00:25:35 | [26_c5_bone_parenting_keep_offset.jpg](./26_c5_bone_parenting_keep_offset.jpg) | 各指 `Proximal` $\to$ `Hand` $\to$ `LowerArm` を Keep Offset で親子付け |
| 27 | 00:26:35 | [27_c5_create_vgroups_hand_lowerarm.jpg](./27_c5_create_vgroups_hand_lowerarm.jpg) | メッシュに頂点グループ `Hand` と `LowerArm` を作成 |
| 28 | 00:27:45 | [28_c5_assign_hand_half_weight.jpg](./28_c5_assign_hand_half_weight.jpg) | 指の付け根ループに `Hand: 0.5` / `Proximal: 0.5` を半々で割り当て |
| 29 | 00:28:45 | [29_c5_pose_mode_finger_curl_test.jpg](./29_c5_pose_mode_finger_curl_test.jpg) | ポーズモードで指を曲げ、変形具合をリアルタイム検証 |
| 30 | 00:31:00 | [30_c5_vertex_mask_blur_brush.jpg](./30_c5_vertex_mask_blur_brush.jpg) | 頂点マスク（`V`）を有効にし、ブラーブラシでウェイトを滑らかにぼかす |
| 31 | 00:31:30 | [31_c5_weights_smooth_filter.jpg](./31_c5_weights_smooth_filter.jpg) | **【重要】Weights > Smooth フィルターで数学的にウェイトをグラデーション化** |
| 32 | 00:32:35 | [32_c5_auto_normalize_checkbox.jpg](./32_c5_auto_normalize_checkbox.jpg) | **【重要】「Auto Normalize（自動正規化）」をONにして合計ウェイト1.0を維持** |
| 33 | 00:34:20 | [33_c5_lowerarm_wrist_weight.jpg](./33_c5_lowerarm_wrist_weight.jpg) | 手首・前腕への `LowerArm` ウェイトの配分 |
| 34 | 00:35:45 | [34_c5_webbing_tri_quad_retarget.jpg](./34_c5_webbing_tri_quad_retarget.jpg) | 水かき部のシワを防ぐため、頂点連結（`J`）で三角形/四角形の流れを整流 |
| 35 | 00:36:20 | [35_c5_hand_complete_pose_persp.jpg](./35_c5_hand_complete_pose_persp.jpg) | 手・指・手首・ボーン・ウェイトが一体化した完成パース |
