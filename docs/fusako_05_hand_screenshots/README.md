# ふさこ氏『手のモデリング/リギング/スキニング前編（第5回）』重要シーン・スクリーンショット集

元動画: [Blenderでキャラクターモデル制作！05 | 手のモデリング/リギング/スキニング（前編）〜初級から中級者向けチュートリアル〜](https://www.youtube.com/watch?v=cPrupquhQYQ)  
動画長: 25分08秒  
対応仕様書: [`.agents/handoffs/2026-09-24_fusako_hand_modeling_05_steps.md`](../../.agents/handoffs/2026-09-24_fusako_hand_modeling_05_steps.md)

---

## 📸 スクリーンショット一覧（全20枚）

### 【Chapter 1: リファレンス画像と作業環境のセットアップ】 (00:00 〜 02:30)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 01 | 00:01:00 | `01_c1_reference_images_3views.jpg` | 手の甲（正面）・側面・手の平（背面）の3面参考画像の読み込み・配置 |

---

### 【Chapter 2: 中指のベースモデリング】 (02:30 〜 07:48)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 02 | 00:02:45 | `02_c2_middle_finger_cube_open.jpg` | Cubeを追加し底面を削除、縦長の角柱として配置 |
| 03 | 00:03:30 | `03_c2_subsurf1_taper_tip.jpg` | Subsurfレベル1を追加し、指先に向かって徐々に細くなるよう調整 |
| 04 | 00:04:40 | `04_c2_apply_subsurf_ctrl_a.jpg` | **【重要】モディファイア上で `Ctrl + A` を実行し、Subsurfを即時適用（実体化）** |
| 05 | 00:05:15 | `05_c2_joint_ratio_4_3_2.jpg` | **【黄金律】根元から「基節: 4」「中節: 3」「末節: 2」の関節比率でループ配置** |
| 06 | 00:06:25 | `06_c2_joint_shear_angle.jpg` | **【黄金律】シアー（Shear: Shift+Ctrl+Alt+S）で太さを変えずに関節を傾斜** |
| 07 | 00:07:30 | `07_c2_flatten_finger_cross_section.jpg` | `S Y` で前後厚みを薄くし、人間の指らしい平たい断面に調整 |

---

### 【Chapter 3: 単一指ボーンのセットアップ】 (07:48 〜 11:02)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 08 | 00:08:20 | `08_c3_add_single_bone_armature.jpg` | 単一ボーンを追加し、最前面（In Front）・Names・ワイヤー表示を設定 |
| 09 | 00:09:20 | `09_c3_bone_3joints_dorsal_offset.jpg` | **【解剖学的黄金律】ボーン軸を指中心ではなく手の甲側（背面寄り）に配置** |
| 10 | 00:10:05 | `10_c3_unity_bone_naming_proximal.jpg` | Unity規格命名（`Middle_Proximal`, `Intermediate`, `Distal`） |
| 11 | 00:10:45 | `11_c3_parent_with_empty_groups.jpg` | メッシュとボーンを `Ctrl + P` $\to$ With Empty Groups で親子付け |

---

### 【Chapter 4: 手動数値入力スキニングと曲げ変形調整】 (11:02 〜 20:45)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 12 | 00:11:30 | `12_c4_3loops_at_joints.jpg` | **【耐破綻トポロジー】曲がる関節部に計3本のエッジループを確保** |
| 13 | 00:12:15 | `13_c4_vertex_weight_manual_assign.jpg` | 頂点グループパネルで数値を直接入力（0.8, 0.2, 0.5等）して手動割り当て |
| 14 | 00:13:00 | `14_c4_zero_weights_visualization.jpg` | ビューポートオーバーレイで「Zero Weights」をアクティブにし、未塗りを視覚化 |
| 15 | 00:14:30 | `15_c4_pose_mode_curl_test.jpg` | ポーズモードで指を曲げ、ケージ表示で編集モードからリアルタイム変形検証 |
| 16 | 00:16:40 | `16_c4_palm_side_volume_topology_fix.jpg` | 指の腹側（内側）の痩せ・凹みを防ぐエッジ溶解と頂点マージ |

---

### 【Chapter 5: 原点設定とリンク複製による5本指展開】 (20:45 〜 25:08)

| No | タイムスタンプ | 画像ファイル名 | 解説・重要ポイント |
| :---: | :---: | :--- | :--- |
| 17 | 00:21:20 | `17_c5_set_origin_to_finger_base.jpg` | 指付け根に3Dカーソルを合わせ、原点を付け根に再配置（Set Origin） |
| 18 | 00:22:00 | `18_c5_alt_d_linked_duplicate_fingers.jpg` | **【黄金律】`Alt + D`（リンク複製）で人差し指・薬指・小指を展開** |
| 19 | 00:23:40 | `19_c5_knuckle_arch_placement.jpg` | 中指を頂点とする手の甲の山なりアーチに指を配置 |
| 20 | 00:24:20 | `20_c5_thumb_90deg_rotation_opposed.jpg` | 親指を `Alt + D` で複製し、90度回転させて対向配置 |
