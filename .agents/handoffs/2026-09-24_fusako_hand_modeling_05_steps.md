# ふさこ氏『手のモデリング/リギング/スキニング（前編）』操作手順・トポロジー仕様書（第5回）

## 1. 動画メタデータ（公式事実）
- **正式タイトル**: 『Blenderでキャラクターモデル制作！05 | 手のモデリング/リギング/スキニング（前編）〜初級から中級者向けチュートリアル〜』
- **URL**: https://www.youtube.com/watch?v=cPrupquhQYQ
- **動画長**: 25分08秒（1508秒）
- **チャンネル**: ふさこ / 3D工房
- **アップロード日**: 2023年5月23日
- **字幕データ**:
  - VTT生データ: `z:\MeshCreator\.agents\handoffs\fusako_05_subtitles_raw.ja.vtt`
  - タイムスタンプ付きテキスト: `z:\MeshCreator\.agents\handoffs\fusako_05_subtitles_timestamped.txt`
- **重要シーン・スクリーンショット集（全20枚）**:
  - 保存フォルダ: [`z:\MeshCreator\docs\fusako_05_hand_screenshots/`](file:///z:/MeshCreator/docs/fusako_05_hand_screenshots/)
  - 画像カタログ: [`z:\MeshCreator\docs\fusako_05_hand_screenshots/README.md`](file:///z:/MeshCreator/docs/fusako_05_hand_screenshots/README.md)

---

## 2. チャプター構成一覧

| # | タイムスタンプ | チャプター名 | 主な対象 | 概要 |
| :--- | :--- | :--- | :--- | :--- |
| **C1** | 00:00 - 02:30 | リファレンス画像と作業環境のセットアップ | 3面参考画像 | 手専用コレクション作成、正面（手の甲）・側面・背面（手の平）の三面図配置、透過度・Front表示設定 |
| **C2** | 02:30 - 07:48 | 中指のベースモデリング | 中指メッシュ | Cube底面削除 $\to$ Subsurf1 $\to$ 即時適用 $\to$ 関節比率（4:3:2） $\to$ シアー（Shear）機能による太さを変えない関節傾斜 |
| **C3** | 07:48 - 11:02 | 単一指ボーン（Armature）のセットアップ | ボーン（3節） | 単一ボーン追加 $\to$ 押し出し3節 $\to$ **【甲側偏芯配置】** $\to$ Unityヒューマノイド命名 $\to$ With Empty Groups 親子付け |
| **C4** | 11:02 - 20:45 | 手動数値入力スキニングと曲げ変形調整 | ウェイト・関節トポロジー | 3本ループ耐破綻トポロジー $\to$ 数値直接入力スキニング $\to$ ゼロウェイト視覚化 $\to$ 腹側の痩せ防止トポロジー修正 |
| **C5** | 20:45 - 25:08 | 原点設定とリンク複製による5本指展開 | 5本指配置 | 指の付け根へ原点移動（Set Origin） $\to$ **【Alt + D リンク複製】** $\to$ 各指のスケール・アーチ配置 $\to$ 親指の回転配置 |

---

## 3. モデリング方針とトポロジー黄金律

### 核心方針: 「1本の完璧な指（モデル＋ボーン＋ウェイト）を作り、リンク複製（Alt + D）で展開する」
1. **「4 : 3 : 2」の関節黄金比率**:
   - 付け根〜第1関節（基節骨） : 第1〜第2関節（中節骨） : 第2関節〜指先（末節骨）の長さを **「4 : 3 : 2」** の比率に設定。人間らしくデフォルメにも適した自然なプロポーションを確立する。
2. **太さを変えない傾斜「シアー（Shear）」**:
   - 関節断面を斜めに傾ける際、通常の回転（`R`）を行うと断面がすぼまって指が細くなる。
   - **シアー（`Shift + Ctrl + Alt + S`）** を使用することで、指の太さ（断面幅）を完全に保ったまま角度だけを傾斜させる。
3. **ボーンの「手の甲側（背面寄り）」偏芯配置**:
   - ボーンを指の断面中心に通すと、曲げたときにゴムホースのように丸く潰れてしまう。
   - **ボーンの軸を「手の甲側（背側）」に寄せて配置** することで、関節を曲げた際に背側がカクッと骨ばり、腹側が肉厚に盛り上がる人間本来の変形が実現する。
4. **手動数値入力スキニング（Weight Painting）**:
   - ブラシによる自動ウェイトや手塗りではなく、頂点グループのウェイト数値を直接入力（0.8, 0.2, 0.5 など）して対称・均等な変形を担保。
   - 曲がる関節部には必ず **「3本のエッジループ」** を通し、メッシュのめり込みや過度な痩せを防ぐ。
5. **「Alt + D（リンク複製）」の極意**:
   - 指を複製する際、通常の `Shift + D` ではなく **`Alt + D`（リンク複製）** を使用。
   - メッシュデータが共有されるため、後からウェイトや関節形状を手直ししても、1本を修正すれば人差し指・中指・薬指・小指・親指すべてに瞬時に反映される。

---

## 4. パーツ別詳細手順

### Part 1: リファレンス画像のセットアップ (00:00〜02:30)
> [📸 参考: 01_c1_reference_images_3views.jpg](../../docs/fusako_05_hand_screenshots/01_c1_reference_images_3views.jpg)
1. アウトライナーでメインコレクションを選択し、新規コレクション（例: `Hand`）を作成。テンキー `3` 等でそのコレクションをアクティブ化。
2. `Shift + A` $\to$ **画像 > 参照（Image > Reference）** を選択。
   - 読み込み設定: **「ビューに整列（Align to View）」のチェックを外す**。
3. 正面図（手の甲）を配置: `R X 90` で正面（-Y）に向ける。`G Y` で少し奥へ下げる。
4. 側面図を配置: `R X 90` $\to$ `R Z 90` で横向き（+X）にする。`G X` で横へずらす。
5. 背面図（手の平）を配置: `R X 90` $\to$ `R Z 180` で手前に向ける。`G Y` で手前へ配置。
6. 各参考画像のプロパティ設定:
   - 「不透明度（Opacity）」を有効化し、作業しやすい薄さ（0.3〜0.5程度）に下げる。
   - 「表示（Side）」を **「前（Front）」** のみに設定（裏側から見たときに邪魔にならないようにする）。

---

### Part 2: 中指のモデリング（02:30〜07:48）
> [📸 参考: 02_c2_middle_finger_cube_open.jpg](../../docs/fusako_05_hand_screenshots/02_c2_middle_finger_cube_open.jpg) / [03_c2_subsurf1_taper_tip.jpg](../../docs/fusako_05_hand_screenshots/03_c2_subsurf1_taper_tip.jpg) / [04_c2_apply_subsurf_ctrl_a.jpg](../../docs/fusako_05_hand_screenshots/04_c2_apply_subsurf_ctrl_a.jpg) / [05_c2_joint_ratio_4_3_2.jpg](../../docs/fusako_05_hand_screenshots/05_c2_joint_ratio_4_3_2.jpg) / [06_c2_joint_shear_angle.jpg](../../docs/fusako_05_hand_screenshots/06_c2_joint_shear_angle.jpg) / [07_c2_flatten_finger_cross_section.jpg](../../docs/fusako_05_hand_screenshots/07_c2_flatten_finger_cross_section.jpg)
1. `Shift + A` $\to$ **メッシュ > 立方体（Cube）** を追加。
2. 編集モードで **一番下の面を選択して `X` $\to$ 面を削除**。
3. 全選択 `A` $\to$ `S Shift + Z` で水平断面を縮小し、縦長の角柱にする。
4. 正面から見ながら中指の位置へ配置。
5. `Ctrl + 1` で `Subdivision Surface`（レベル1）を追加。
6. `Ctrl + R` でループカットを追加し、指先に向かってなだらかに細く、付け根はやや太く調整。
7. 外形が整ったら、オブジェクトモードで `Subdivision Surface` モディファイアを **`Ctrl + A` で即時適用**（実体メッシュ化）。
8. **関節位置の割り出し（4:3:2 比率）**:
   - 付け根から順に「基節骨: 4」「中節骨: 3」「末節骨: 2」となる位置に関節ループを配置。
   - 不要なループは `X` $\to$ **辺を溶解（Dissolve Edges）** で整理。
9. **シアー（Shear）による関節の傾斜付け**:
   - 第1関節、第3関節のエッジループを選択。
   - ツールバーから「シアー」ツール（ショートカット: `Shift + Ctrl + Alt + S`）を選択し、上下にドラッグして傾斜をつける（断面の太さを維持したまま自然な指の関節ラインができる）。
10. `S Y` で指全体の前後（厚み）を調整し、平べったい人間の指の断面にする。

---

### Part 3: ボーンのセットアップと親子付け（07:48〜11:02）
> [📸 参考: 08_c3_add_single_bone_armature.jpg](../../docs/fusako_05_hand_screenshots/08_c3_add_single_bone_armature.jpg) / [09_c3_bone_3joints_dorsal_offset.jpg](../../docs/fusako_05_hand_screenshots/09_c3_bone_3joints_dorsal_offset.jpg) / [10_c3_unity_bone_naming_proximal.jpg](../../docs/fusako_05_hand_screenshots/10_c3_unity_bone_naming_proximal.jpg) / [11_c3_parent_with_empty_groups.jpg](../../docs/fusako_05_hand_screenshots/11_c3_parent_with_empty_groups.jpg)
1. オブジェクトモードで `Shift + A` $\to$ **アーマチュア > 単一ボーン（Armature > Single Bone）** を追加。
2. アーマチュアのプロパティ（緑の走る人アイコン / オレンジの四角アイコン）:
   - 「ビューポート表示」 $\to$ **「最前面（In Front）」にチェック**。
   - 「表示方法」 $\to$ **「ワイヤーフレーム（Wire）」** に設定。
   - **「名前（Names）」にチェック** を入れ、ボーン名を常時可視化。
3. 編集モードに入り、ボーンの根元を指の付け根に配置。
4. `E`（押し出し）で第1関節、第2関節、指先へと押し出し、計3本のボーンチェーンを作成。
5. **解剖学的黄金律（甲側偏芯）**:
   - 横から見て、ボーン全体を `G Y` で **「手の甲側（背面寄り）」** に移動させる。
   - 人間の指の骨は背中側を通っており、ここを軸に回転させることで曲げた時の自然な角張りが生まれる。
6. **ボーン名の命名（Unityヒューマノイド規格準拠）**:
   - `F2` キーでボーン名を変更:
     - 付け根: `Middle_Proximal`（または `Middle_1`）
     - 中間: `Middle_Intermediate`（または `Middle_2`）
     - 先端: `Middle_Distal`（または `Middle_3`）
7. **親子付け**:
   - オブジェクトモードで **指メッシュ $\to$ アーマチュア** の順に複数選択。
   - `Ctrl + P` $\to$ **「空のグループで（With Empty Groups）」** を選択（自動ウェイトではなく手動設定用の頂点グループ枠のみを生成）。

---

### Part 4: 手動数値入力スキニングと曲げ変形調整（11:02〜20:45）
> [📸 参考: 12_c4_3loops_at_joints.jpg](../../docs/fusako_05_hand_screenshots/12_c4_3loops_at_joints.jpg) / [13_c4_vertex_weight_manual_assign.jpg](../../docs/fusako_05_hand_screenshots/13_c4_vertex_weight_manual_assign.jpg) / [14_c4_zero_weights_visualization.jpg](../../docs/fusako_05_hand_screenshots/14_c4_zero_weights_visualization.jpg) / [15_c4_pose_mode_curl_test.jpg](../../docs/fusako_05_hand_screenshots/15_c4_pose_mode_curl_test.jpg) / [16_c4_palm_side_volume_topology_fix.jpg](../../docs/fusako_05_hand_screenshots/16_c4_palm_side_volume_topology_fix.jpg)
1. **耐破綻関節ループ（3本ループの法則）**:
   - 指が曲がる各関節の上下に `Ctrl + R` で1本ずつループを追加（関節1つにつき計3本のエッジループを確保）。
2. **数値直接入力によるスキニング**:
   - 編集モードでループを選択し、「頂点グループ（Vertex Groups）」パネルで数値を指定して「割り当て（Assign）」を実行:
     - **先端（Distal）**: 最先端ループ = `Distal: 1.0`。1つ手前のループ = `Distal: 0.8` / `Intermediate: 0.2`。
     - **第2関節（Intermediate）**: 関節中心ループ = `Distal: 0.5` / `Intermediate: 0.5`。その下 = `Intermediate: 0.8` / `Proximal: 0.2`。
     - **付け根（Proximal）**: 同様に段階的に配分。
3. **ゼロウェイトの視覚化**:
   - `Ctrl + Tab` でウェイトペイントモードに入り、右上のビューポートオーバーレイ $\to$ **「ゼロウェイト（Zero Weights）」を「アクティブ（Active）」** に設定（ウェイト0の部位が黒くハイライトされ、塗り漏れ・意図しない吸着を防止）。
4. **曲げテストとリアルタイム編集**:
   - アーマチュアを選択してポーズモードに入り、`R` で指を90度曲げる。
   - メッシュのモディファイアプロパティで、アーマチュアモディファイアの **「編集モードで表示」「ケージで表示」アイコンをON** にする（曲がった状態のまま編集モードでメッシュ調整が可能）。
5. **指の腹側の痩せ防止トポロジー修正**:
   - 指を深く曲げた際、内側（腹側）が極端に尖って痩せる現象が発生する。
   - 対処: 腹側の過剰なエッジを `X` $\to$ **「辺を溶解（Dissolve Edges）」** で整理し、必要に応じて `M` $\to$ **「中心にマージ」** で頂点を束ね、曲げた時にふっくらとした肉感が残るようトポロジーを整流。

---

### Part 5: 原点設定とリンク複製による5本指展開（20:45〜25:08）
> [📸 参考: 17_c5_set_origin_to_finger_base.jpg](../../docs/fusako_05_hand_screenshots/17_c5_set_origin_to_finger_base.jpg) / [18_c5_alt_d_linked_duplicate_fingers.jpg](../../docs/fusako_05_hand_screenshots/18_c5_alt_d_linked_duplicate_fingers.jpg) / [19_c5_knuckle_arch_placement.jpg](../../docs/fusako_05_hand_screenshots/19_c5_knuckle_arch_placement.jpg) / [20_c5_thumb_90deg_rotation_opposed.jpg](../../docs/fusako_05_hand_screenshots/20_c5_thumb_90deg_rotation_opposed.jpg)
1. **オブジェクト原点（Origin）の最適化**:
   - 指メッシュを選択し、編集モードで **指の付け根（底面中央）の頂点** を選択。
   - `Shift + S` $\to$ **「カーソル $\to$ 選択物（Cursor to Selected）」** で3Dカーソルを付け根に配置。
   - オブジェクトモードに戻り、右クリック $\to$ **原点を設定 > 原点を3Dカーソルへ移動（Set Origin to 3D Cursor）**。
   - アーマチュアも同様に原点を付け根に移動。
   - **効果**: 指の拡大縮小（`S`）や回転（`R`）が付け根を起点に行えるようになる。
2. **リンク複製（Alt + D）による展開**:
   - 通常の複製（`Shift + D`）ではなく、**`Alt + D`（リンク複製）** を使用して指メッシュとボーンを複製。
3. **各指のサイズ・位置調整**:
   - **人差し指**: `S` でわずかに縮小（中指よりやや短い）。
   - **薬指**: 人差し指と同等か、わずかに長め。
   - **小指**: `S` でグッと縮小し、付け根の位置を中指・人差し指より下げる。
4. **手の甲のアーチ形成**:
   - 上から（テンキー7）および正面から見て、中指が一番高く、両端（人差し指・小指）が奥・下に下がる緩やかなアーチ状に指を配置。
5. **親指の配置**:
   - `Alt + D` で複製後、`R` で約90度回転。
   - 正面から見て爪が外側を向き、横から見て爪が見える角度に配置（他の4指と対向する向き）。

---

## 5. 必須テクニック＆ショートカット早見表

| ショートカット / 機能 | 操作名称 | ふさこ氏チュートリアルでの用途 |
| :--- | :--- | :--- |
| `Alt + D` | リンク複製 | メッシュデータを共有したまま指を複製。1本手直しすれば全指に即時自動反映される |
| `Shift + Ctrl + Alt + S` | シアー（Shear） | 指の太さ（断面幅）を一切変えずに、関節の傾斜角度だけを斜めに変形する |
| `Shift + S` $\to$ カーソル $\to$ 選択物 | 3Dカーソル移動 | 指の付け根に正確に3Dカーソルをスナップさせる |
| 右クリック $\to$ 原点を3Dカーソルへ | 原点再配置 | 指のスケールや回転の起点を付け根にし、ポージングやサイズ調整を容易にする |
| `Ctrl + P` $\to$ With Empty Groups | 空のグループで親子付け | 自動ウェイトを介さず、ボーンと同名の空の頂点グループ枠を一括生成する |
| ゼロウェイト視覚化 (Zero Weights) | ウェイト表示設定 | ウェイト値0の頂点を完全な黒で表示し、不要なウェイト付着や塗り漏れを防ぐ |
| モディファイアケージ表示 | ケージプレビュー | ポーズモードで指を曲げた形状を保ったまま、編集モードで頂点を直接スカルプト・調整する |

---

## 6. 本プロジェクト（AnimeFace / 素体パイプライン）との連動・実装指針

1. **Unityヒューマノイド完全互換リグ**:
   - 本手順書で指定された命名規則（`Proximal`, `Intermediate`, `Distal`）および甲側偏芯のボーン構造は、Unity MecanimヒューマノイドアバターのHandボーン仕様と100%合致します。
2. **後編（手の甲・手のひら・手首接合）への接続**:
   - 本手順で作られた5本指の付け根ループ（各8頂点または4頂点）は、次回の「手のひら・手の甲」メッシュとLoopTools Bridge等を用いて接合されます。
   - `Alt + D` でリンクされているため、手のひら側の頂点数に合わせて指の付け根の割りを変更する場合でも、1本の修正ですべて追従します。
