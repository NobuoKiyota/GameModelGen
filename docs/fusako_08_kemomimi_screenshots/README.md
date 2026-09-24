# ふさこ氏『手足の接合＆ケモ耳のモデリング（第8回）』重要シーン・スクリーンショット集

元動画: [Blenderでキャラクターモデル制作！08 | 手足の接合＆ケモ耳のモデリング〜初級から中級者向けチュートリアル〜](https://www.youtube.com/watch?v=t2Gsg-e0C18)  
動画長: 27分08秒  
対応仕様書: [`.agents/handoffs/2026-09-24_fusako_body_integration_kemomimi_08_steps.md`](../../.agents/handoffs/2026-09-24_fusako_body_integration_kemomimi_08_steps.md)

---

## 📸 スクリーンショット一覧（全24枚）

### 【Chapter 1: 手のボーン対称化（Symmetrize）とミラーセットアップ】 (00:00 〜 03:55)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 01 | 00:00:45 | [`01_c1_hand_scale_placement.jpg`](./01_c1_hand_scale_placement.jpg) | 手メッシュとボーンを体へ配置し、ポーズ初期化（Alt+R, Alt+G）でTポーズに戻す |
| 02 | 00:02:25 | [`02_c1_bone_autoname_left_right.jpg`](./02_c1_bone_autoname_left_right.jpg) | ボーン編集モードで全選択 $\to$ 右クリック $\to$ Names > AutoName Left/Right（.L付与） |
| 03 | 00:02:42 | [`03_c1_bone_symmetrize_right.jpg`](./03_c1_bone_symmetrize_right.jpg) | **【黄金律】右クリック $\to$ Symmetrize（対称化）で反対側（.R）ボーンを一発自動生成** |
| 04 | 00:03:00 | [`04_c1_hand_mirror_modifier.jpg`](./04_c1_hand_mirror_modifier.jpg) | 手メッシュのトランスフォームを適用し、Mirrorモディファイアを追加 |
| 05 | 00:03:36 | [`05_c1_parent_with_empty_groups_r.jpg`](./05_c1_parent_with_empty_groups_r.jpg) | **【超重要Tips】Ctrl+P $\to$ With Empty Groups再実行で.R頂点グループを一括追加・両腕連動** |

---

### 【Chapter 2: 足と脚の接合】 (03:55 〜 05:10)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 06 | 00:04:16 | [`06_c2_foot_join_to_body_ctrl_j.jpg`](./06_c2_foot_join_to_body_ctrl_j.jpg) | 足メッシュをメインへ移動し、体メッシュと `Ctrl + J` で統合 |
| 07 | 00:04:53 | [`07_c2_ankle_looptools_bridge.jpg`](./07_c2_ankle_looptools_bridge.jpg) | **【黄金律】LoopTools > Bridgeで足首と脚部の8頂点ループ同士を四角面一発架橋** |

---

### 【Chapter 3: 手と腕の接合】 (05:10 〜 07:35)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 08 | 00:05:30 | [`08_c3_wrist_reduce_to_8verts.jpg`](./08_c3_wrist_reduce_to_8verts.jpg) | 手首側の不要エッジを溶解・整理して腕側と同じ **「8頂点」** に完全整合 |
| 09 | 00:06:26 | [`09_c3_arm_join_ctrl_j.jpg`](./09_c3_arm_join_ctrl_j.jpg) | 手と体を `Ctrl + J` で統合 |
| 10 | 00:06:46 | [`10_c3_wrist_looptools_bridge.jpg`](./10_c3_wrist_looptools_bridge.jpg) | **【黄金律】LoopTools > Bridgeで手首と腕の8頂点を四角面一発架橋** |
| 11 | 00:07:26 | [`11_c3_wrist_curvature_relax.jpg`](./11_c3_wrist_curvature_relax.jpg) | 接合部の不自然な膨らみ・凹凸を `Alt + S` で滑らかに整流 |

---

### 【Chapter 4: 膝・脇・胴体ディテール】 (07:35 〜 13:10)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 12 | 00:08:03 | [`12_c4_knee_inset_patella.jpg`](./12_c4_knee_inset_patella.jpg) | 膝前面を `I`（インセット）して膝蓋骨（膝小僧）の台座を作成 |
| 13 | 00:08:43 | [`13_c4_knee_alts_bump.jpg`](./13_c4_knee_alts_bump.jpg) | 膝の出っ張りを `Alt + S` で盛り上げ、カクッとしたメリハリを形成 |
| 14 | 00:10:45 | [`14_c4_armpit_knife_topology.jpg`](./14_c4_armpit_knife_topology.jpg) | 脇下にループカット＋ナイフツールで切り込み、自然な脇のくぼみを作成 |
| 15 | 00:12:00 | [`15_c4_belly_subdivide_smoothness.jpg`](./15_c4_belly_subdivide_smoothness.jpg) | 胴体リング選択 $\to$ Subdivide（Smoothness調整）で胸〜お腹〜お尻の柔らかな肉感を増強 |

---

### 【Chapter 5: ケモ耳（猫耳）モデリング】 (13:10 〜 27:08)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 16 | 00:13:52 | [`16_c5_kemomimi_plane_base.jpg`](./16_c5_kemomimi_plane_base.jpg) | メッシュ平面（Plane）から猫耳の三角ポリゴンを開始 |
| 17 | 00:14:54 | [`17_c5_kemomimi_crease_subsurf.jpg`](./17_c5_kemomimi_crease_subsurf.jpg) | 三角断面押し出し＋クリース＋Subsurfで耳のベース形状を作成 |
| 18 | 00:16:28 | [`18_c5_solidify_modifier.jpg`](./18_c5_solidify_modifier.jpg) | Solidifyモディファイアで耳全体に厚みを付与 |
| 19 | 00:17:24 | [`19_c5_solidify_vertex_weight_gradient.jpg`](./19_c5_solidify_vertex_weight_gradient.jpg) | **【黄金律】ウェイトペイントグラデーションで「根元厚・先端薄」の厚みを自動制御** |
| 20 | 00:19:18 | [`20_c5_ear_fur_rhombus_cube.jpg`](./20_c5_ear_fur_rhombus_cube.jpg) | 45度回転Cubeから耳毛（内側の毛束）の基本パーツを作成 |
| 21 | 00:21:37 | [`21_c5_ear_fur_clusters_placement.jpg`](./21_c5_ear_fur_clusters_placement.jpg) | 毛束を複製・ランダム回転させて耳の内側にぶっ刺し配置 |
| 22 | 00:23:45 | [`22_c5_solidify_apply_inner_face_cleanup.jpg`](./22_c5_solidify_apply_inner_face_cleanup.jpg) | Solidify適用後の耳内側の不要面を削除し軽量化 |
| 23 | 00:24:58 | [`23_c5_ear_tip_fluff_extrude.jpg`](./23_c5_ear_tip_fluff_extrude.jpg) | 耳外縁をSubdivide＋`E` 押し出しで先端の尖り毛束を作成 |
| 24 | 00:26:46 | [`24_c5_kemomimi_complete_persp.jpg`](./24_c5_kemomimi_complete_persp.jpg) | 手足接合素体＋ケモ耳が完成した全体パース確認 |
