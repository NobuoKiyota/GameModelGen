# ふさこ氏『足のモデリング（第7回）』重要シーン・スクリーンショット集

元動画: [Blenderでキャラクターモデル制作！07 | 足のモデリング〜初級から中級者向けチュートリアル〜](https://www.youtube.com/watch?v=zZl3Lhosbcw)  
動画長: 24分46秒  
対応仕様書: [`.agents/handoffs/2026-09-24_fusako_foot_modeling_07_steps.md`](../../.agents/handoffs/2026-09-24_fusako_foot_modeling_07_steps.md)

---

## 📸 スクリーンショット一覧（全24枚）

### 【Chapter 1: 参考画像と作業環境セットアップ】 (00:00 〜 02:15)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 01 | 00:00:30 | [`01_c1_reference_images_side_sole.jpg`](./01_c1_reference_images_side_sole.jpg) | 足の側面図・底面図（足裏ビュー: Ctrl+Numpad 7）参考画像の配置とセットアップ |

---

### 【Chapter 2: 足首・かかと・甲・足裏のベースモデリング】 (02:15 〜 07:15)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 02 | 00:02:25 | [`02_c2_separate_ankle_loop_p.jpg`](./02_c2_separate_ankle_loop_p.jpg) | 体メッシュの足首下端ループ（8頂点）を `P` で別オブジェクトに分離 |
| 03 | 00:03:00 | [`03_c2_ankle_extrude_down.jpg`](./03_c2_ankle_extrude_down.jpg) | `E` で足首下まで押し出し。Shift+N で面の向き（法線）を外向きに再計算 |
| 04 | 00:03:45 | [`04_c2_foot_bridge_extrude_forward.jpg`](./04_c2_foot_bridge_extrude_forward.jpg) | 前方へ `E` 押し出し、足の甲から指の付け根手前まで伸ばす |
| 05 | 00:04:15 | [`05_c2_heel_loop_alts_fatten.jpg`](./05_c2_heel_loop_alts_fatten.jpg) | かかと側にループカットを追加し、`Alt + S` で膨らませて丸みを形成 |
| 06 | 00:04:40 | [`06_c2_sole_side_profile_view.jpg`](./06_c2_sole_side_profile_view.jpg) | 底面図を見ながらかかと・指付け根の位置を下絵の輪郭に合わせる |
| 07 | 00:05:40 | [`07_c2_bridge_faces_sides.jpg`](./07_c2_bridge_faces_sides.jpg) | 足首〜足甲〜かかとの側面を四角面（`F`）で順次面張り |
| 08 | 00:06:20 | [`08_c2_arch_proportional_edit.jpg`](./08_c2_arch_proportional_edit.jpg) | 土踏まずのくぼみをプロポーショナル編集（`O`）で内側に整流 |
| 09 | 00:06:55 | [`09_c2_sole_bottom_face_fill.jpg`](./09_c2_sole_bottom_face_fill.jpg) | 足底（足裏）の開口部を四角面で綺麗に面張り |

---

### 【Chapter 3: 足の指（5本指）のモデリング】 (07:15 〜 13:10)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 10 | 00:07:25 | [`10_c3_toe_circle_8verts.jpg`](./10_c3_toe_circle_8verts.jpg) | **【黄金律】メッシュ円（Circle）頂点数「8」から小指の作成を開始** |
| 11 | 00:08:25 | [`11_c3_toe_extrude_taper_joints.jpg`](./11_c3_toe_extrude_taper_joints.jpg) | 関節で回転を入れながら先端へ `E` 押し出し、指先をすぼめる |
| 12 | 00:09:10 | [`12_c3_toe_tip_smooth_vertices.jpg`](./12_c3_toe_tip_smooth_vertices.jpg) | 爪側を平らに、腹側を丸く整流（Smooth Vertices & Alt+S） |
| 13 | 00:10:15 | [`13_c3_big_toe_onigiri_triangle.jpg`](./13_c3_big_toe_onigiri_triangle.jpg) | **【黄金律】親指はおにぎり三角（三角〜四角形断面）に成形** |
| 14 | 00:11:30 | [`14_c3_toes_angle_alignment.jpg`](./14_c3_toes_angle_alignment.jpg) | 5本の指を足裏から見て緩やかなアーチを描くよう角度・長さを回転整流 |
| 15 | 00:12:30 | [`15_c3_toes_merge_between_digits.jpg`](./15_c3_toes_merge_between_digits.jpg) | 指と指の近接頂点を `M` でマージし、指間の股を結合 |

---

### 【Chapter 4: 足指と足甲・足裏の接合】 (13:10 〜 18:30)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 16 | 00:13:30 | [`16_c4_toes_bridge_extrude_to_foot.jpg`](./16_c4_toes_bridge_extrude_to_foot.jpg) | 指の背側エッジループを選択し、足甲に向かって `E` 押し出し |
| 17 | 00:14:15 | [`17_c4_reduce_verts_merge_center.jpg`](./17_c4_reduce_verts_merge_center.jpg) | **【トポロジー整流】3頂点を中心にマージ（Merge at Center）して頂点数を減衰** |
| 18 | 00:15:15 | [`18_c4_toes_sole_extrude_bridge.jpg`](./18_c4_toes_sole_extrude_bridge.jpg) | 指の足裏側エッジを押し出し、4辺から2辺へ整理して足底へ歩み寄り |
| 19 | 00:16:00 | [`19_c4_join_foot_and_toes_ctrl_j.jpg`](./19_c4_join_foot_and_toes_ctrl_j.jpg) | 足本体メッシュと指メッシュを選択し、`Ctrl + J` で1つのオブジェクトに統合 |
| 20 | 00:16:45 | [`20_c4_snap_automerge_toes_to_foot.jpg`](./20_c4_snap_automerge_toes_to_foot.jpg) | 外側（小指・親指）の確実なラインから頂点スナップ＋マージ、面張り（F）で結合 |

---

### 【Chapter 5: 土踏まず・かかと・くるぶしの整流と仕上げ】 (18:30 〜 24:46)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 21 | 00:18:45 | [`21_c5_sole_arch_lift_gz.jpg`](./21_c5_sole_arch_lift_gz.jpg) | 土踏まずの頂点を `G Z` で上へ引き上げ、立体的なアーチ構造を形成 |
| 22 | 00:20:05 | [`22_c5_smooth_tool_brush.jpg`](./22_c5_smooth_tool_brush.jpg) | スムースツールを使って足表面のガタつきをふんわり均等化 |
| 23 | 00:22:45 | [`23_c5_toes_curl_inward_arch.jpg`](./23_c5_toes_curl_inward_arch.jpg) | 薬指・小指をプロポーショナル編集で内向きに軽く傾斜させ、自然な指並びに整流 |
| 24 | 00:23:45 | [`24_c5_ankle_malleolus_asymmetry.jpg`](./24_c5_ankle_malleolus_asymmetry.jpg) | **【解剖学的黄金律】内くるぶし（高）と外くるぶし（低）の非対称な膨らみ形成と完成形状** |
