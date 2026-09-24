# ふさこ氏『顔のモデリング後編（第2回）』重要シーン・スクリーンショット集

元動画: [Blenderでキャラクターモデル制作！02 | 顔のモデリング（後編）〜初中級者向けチュートリアル〜](https://www.youtube.com/watch?v=P_NaathNpwk)  
動画長: 32分53秒  
対応仕様書: [`.agents/handoffs/2026-09-21_fusako_head_modeling_02_steps.md`](../../.agents/handoffs/2026-09-21_fusako_head_modeling_02_steps.md)

---

## 📸 スクリーンショット一覧（全17枚）

### 【Phase 1: 目のモデリング】 (00:00 〜 02:36)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 01 | 00:01:00 | [01_p1_eye_mesh_uv_sphere_concave.jpg](./01_p1_eye_mesh_uv_sphere_concave.jpg) | UV球の前面を凹ませてアニメ特有のすり鉢状（凹面）瞳メッシュを作成 |
| 02 | 00:02:15 | [02_p1_eye_pupil_angle_placement.jpg](./02_p1_eye_pupil_angle_placement.jpg) | 瞳の角度・位置を眼窩ソケット内に合わせてMirror配置 |

---

### 【Phase 2: まつ毛・アイリッドのモデリング】 (02:36 〜 12:01)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 03 | 00:03:00 | [03_p2_eyelash_separate_from_eye_rim.jpg](./03_p2_eyelash_separate_from_eye_rim.jpg) | 目の上縁エッジを複製・分離（P）してまつ毛の基礎ラインを作成 |
| 04 | 00:04:30 | [04_p2_eyelash_extrude_rhombus_thickness.jpg](./04_p2_eyelash_extrude_rhombus_thickness.jpg) | 上下前後に押し出してひし形断面の厚みを作成 |
| 05 | 00:06:00 | [05_p2_eyelash_crease_1_subsurf.jpg](./05_p2_eyelash_crease_1_subsurf.jpg) | まつ毛稜線エッジにクリース（Shift+E = 1.0）を設定してシャープ化 |
| 06 | 00:08:30 | [06_p2_eyelash_taper_tip.jpg](./06_p2_eyelash_taper_tip.jpg) | プロポーショナル編集で先端を細く絞り、アニメまつ毛の尖りを形成 |
| 07 | 00:10:30 | [07_p2_lower_eyelash_wing.jpg](./07_p2_lower_eyelash_wing.jpg) | 目尻の跳ね上げと下まつ毛の板ポリゴン追加 |
| 08 | 00:12:30 | [08_p2_eyelid_double_fold_line.jpg](./08_p2_eyelid_double_fold_line.jpg) | 二重まぶたの折り込みライン（アイリッド）のエッジ整流 |

---

### 【Phase 3: 眉毛（アイブロウ）のモデリング】 (12:01 〜 15:00)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 09 | 00:14:00 | [09_p3_eyebrow_plane_mesh.jpg](./09_p3_eyebrow_plane_mesh.jpg) | 平面から押し出しで眉毛の板ポリゴンを作成し、額曲面に沿わせる |

---

### 【Phase 4: 耳（Ear）のモデリングと接続】 (15:00 〜 25:00)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 10 | 00:16:30 | [10_p4_ear_primitive_base.jpg](./10_p4_ear_primitive_base.jpg) | 単独プリミティブから耳の基礎輪郭をモデリング開始 |
| 11 | 00:18:45 | [11_p4_ear_helix_antihelix_curves.jpg](./11_p4_ear_helix_antihelix_curves.jpg) | 耳輪・対耳輪・耳垂（耳たぶ）の凹凸を立体的に彫り込み |
| 12 | 00:21:00 | [12_p4_ear_angle_side_placement.jpg](./12_p4_ear_angle_side_placement.jpg) | 側面から見た耳の傾き・高さ（目〜鼻の間）に配置 |
| 13 | 00:24:00 | [13_p4_ear_connect_to_head_socket.jpg](./13_p4_ear_connect_to_head_socket.jpg) | 顔メッシュの耳開口部と耳の境界を結合し、トポロジーを接続 |

---

### 【Phase 5 & 6: 口腔内パーツとUV展開】 (25:00 〜 32:53)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 14 | 00:26:30 | [14_p5_teeth_tongue_inside_mouth.jpg](./14_p5_teeth_tongue_inside_mouth.jpg) | 口腔内部に配置する上歯・下歯および舌メッシュの作成 |
| 15 | 00:28:45 | [15_p6_face_uv_seams_marking.jpg](./15_p6_face_uv_seams_marking.jpg) | 生え際・顎下・耳裏・正中線に沿ってUVシーム（Mark Seam）を設定 |
| 16 | 00:30:30 | [16_p6_face_uv_editor_unwrap_layout.jpg](./16_p6_face_uv_editor_unwrap_layout.jpg) | UVエディターでの顔面アイランドの歪みのない展開レイアウト |
| 17 | 00:32:00 | [17_p6_head_complete_features_persp.jpg](./17_p6_head_complete_features_persp.jpg) | 目・まつ毛・眉・耳・口腔が揃った頭部完成モデルのパース確認 |
