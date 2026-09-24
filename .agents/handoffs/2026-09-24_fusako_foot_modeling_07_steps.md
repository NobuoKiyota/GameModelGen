# ふさこ氏『足のモデリング』操作手順・トポロジー仕様書（第7回）

## 1. 動画メタデータ（公式事実）
- **正式タイトル**: 『Blenderでキャラクターモデル制作！07 | 足のモデリング〜初級から中級者向けチュートリアル〜』
- **URL**: https://www.youtube.com/watch?v=zZl3Lhosbcw
- **動画長**: 24分46秒（1486秒）
- **チャンネル**: ふさこ / 3D工房
- **アップロード日**: 2023年5月25日
- **字幕データ**:
  - VTT生データ: `z:\MeshCreator\.agents\handoffs\fusako_07_subtitles_raw.ja.vtt`
  - タイムスタンプ付きテキスト: `z:\MeshCreator\.agents\handoffs\fusako_07_subtitles_timestamped.txt`
- **重要シーン・スクリーンショット集（全24枚）**:
  - 保存フォルダ: [`z:\MeshCreator\docs\fusako_07_foot_screenshots/`](file:///z:/MeshCreator/docs/fusako_07_foot_screenshots/)
  - 画像カタログ: [`z:\MeshCreator\docs\fusako_07_foot_screenshots/README.md`](file:///z:/MeshCreator/docs/fusako_07_foot_screenshots/README.md)

---

## 2. チャプター構成一覧

| # | タイムスタンプ | チャプター名 | 主な対象 | 概要 |
| :--- | :--- | :--- | :--- | :--- |
| **C1** | 00:00 - 02:15 | 参考画像と作業環境セットアップ | 側面・底面参考画像 | 足専用コレクション作成、側面図・底面図（Ctrl+Numpad 7）の配置、透過度・Front表示設定 |
| **C2** | 02:15 - 07:15 | 足首・かかと・甲・足裏ベース | 足本体メッシュ | 体の足首8頂点ループ分離（P） $\to$ E押し出し $\to$ かかとのAlt+S膨らみ $\to$ 土踏まずくぼみ $\to$ 底面張り |
| **C3** | 07:15 - 13:10 | 足指（5本指）のモデリング | 5本足指メッシュ | サークル8頂点 $\to$ 小指作成 $\to$ 複製 $\to$ **【親指のおにぎり三角成形】** $\to$ 指間マージ結合 |
| **C4** | 13:10 - 18:30 | 足指と足甲・足裏の接合 | 統合メッシュ（Ctrl+J） | 指背側・腹側E押し出し $\to$ **【3頂点マージによる頂点減衰】** $\to$ Ctrl+J統合 $\to$ 頂点スナップ＋面張り（F） |
| **C5** | 18:30 - 24:46 | 土踏まず・かかと・くるぶしの整流 | 足全体仕上げ | 土踏まずのGZ引き上げ $\to$ かかとSX拡大 $\to$ スムースツール均等化 $\to$ **【内高外低のくるぶし形成】** |

---

## 3. モデリング方針とトポロジー黄金律

### 核心方針: 「8頂点足首からの展開、親指のおにぎり断面、そして頂点減衰マージ」
1. **第4回（脚部シリンダー）との8頂点完全整合**:
   - 第4回で作成した脚部の最下端ループは「8頂点」で構成されている。
   - この8頂点ループを `P`（分離）して足首モデリングを開始するため、**将来の脚部と足部の接合時に1本の二重頂点もなく1対1の四角面で完全に溶接（Remove Doubles / Merge by Distance）** できる。
2. **足の親指の「おにぎり三角（三角〜四角形）断面」**:
   - 手の指とは異なり、足の親指は断面が円筒形ではなく、上面（爪側）がやや平らで、内側が垂直に切り立ち、底面が丸い **「おにぎり型（三角〜四角形）」** をしている。
   - ループカット後に `S X` や頂点移動でこの特徴的な断面を作ることで、アニメデフォルメでも足指の説得力が飛躍的に向上する。
3. **多頂点（5本指）から少頂点（足甲）への「頂点減衰マージ」**:
   - 5本の指から伸びるエッジループ（計数十頂点）をそのまま足の甲に流すとポリゴン過多でガタつく。
   - **「3頂点を中心にマージ（Merge at Center）」** して三角〜四角形の収束トポロジーを形成し、指付け根から足の甲に向かってエッジ数を綺麗に減衰させる。
4. **解剖学的黄金律「くるぶしの高さの非対称性（内高外低）」**:
   - 人間の足首は、**内くるぶし（脛骨側）が高く、外くるぶし（腓骨側）が低い**。
   - 両側を同じ高さにせず、内側を少し上に、外側を少し下にずらして膨らませることで、美しい足首のシルエットが完成する。
5. **土踏まず（縦アーチ）の立体形成**:
   - 足裏底面はフラットにせず、内側の中央部を `G Z` で上方に持ち上げ、地面から浮いた「土踏まず」のアーチを確実に確保する。

---

## 4. パーツ別詳細手順

### Part 1: リファレンス画像と作業環境のセットアップ (00:00〜02:15)
1. `Shift + S` $\to$ **「カーソル $\to$ ワールド原点」** で3Dカーソルを中心に配置。
2. アウトライナーで新規コレクション（例: `Collection 4 / Foot`）を作成し、キーボード `4` でアクティブ化。
3. `Shift + A` $\to$ **画像 > 参照（Image > Reference）** を追加。
   - 側面図を配置: `R X 90` $\to$ `R Z 90` で横向き（+X方向）にする。
   - プロパティで不透明度（Opacity）を下げ、サイド表示を「フロント」に設定。
4. 底面図（足裏ビュー）を配置:
   - `Shift + D` で複製し、`Ctrl + Numpad 7`（下から見上げるビュー）で足裏の位置へ配置。
   - [📸 参考: 01_c1_reference_images_side_sole.jpg](../../docs/fusako_07_foot_screenshots/01_c1_reference_images_side_sole.jpg)

---

### Part 2: 足首・かかと・甲・足裏のベースモデリング (02:15〜07:15)
1. **足首ループの分離**:
   - 体メッシュの足首最下端のエッジループ（8頂点）を `Alt + 左クリック` で選択。
   - **`P` $\to$ 「選択物（Selection）」** で別オブジェクトに分離し、足コレクションへ移動。
   - [📸 参考: 02_c2_separate_ankle_loop_p.jpg](../../docs/fusako_07_foot_screenshots/02_c2_separate_ankle_loop_p.jpg)
2. **足首の立ち下げと法線確認**:
   - 全選択 `A` $\to$ **`E`（押し出し）** でくるぶし下まで真下に伸ばす。
   - ビューポートオーバーレイで「面の向き（Face Orientation）」を確認。赤くなっている場合は全選択 `A` $\to$ **`Shift + N`（法線の再計算）** で青（外向き）に直す。
   - [📸 参考: 03_c2_ankle_extrude_down.jpg](../../docs/fusako_07_foot_screenshots/03_c2_ankle_extrude_down.jpg)
3. **足の甲の前方押し出し**:
   - 前面側のエッジを選択し、**`E`（押し出し） $\to$ `S`（拡大）** をかけながら足の甲〜指付け根手前まで伸ばす。
   - [📸 参考: 04_c2_foot_bridge_extrude_forward.jpg](../../docs/fusako_07_foot_screenshots/04_c2_foot_bridge_extrude_forward.jpg)
4. **かかとの形成**:
   - `Ctrl + R` でかかと側にループカットを追加し、**`Alt + S` で後方に膨らませて丸み** を作る。
   - [📸 参考: 05_c2_heel_loop_alts_fatten.jpg](../../docs/fusako_07_foot_screenshots/05_c2_heel_loop_alts_fatten.jpg)
   - 下絵（底面図）を見ながら、かかと後端と指付け根前端の位置を合わせる。
   - [📸 参考: 06_c2_sole_side_profile_view.jpg](../../docs/fusako_07_foot_screenshots/06_c2_sole_side_profile_view.jpg)
5. **側面の面張りと土踏まず**:
   - 足首、甲、かかとの間の隙間を 4頂点ずつ選択して **`F`（面張り）** で塞ぐ。
   - [📸 参考: 07_c2_bridge_faces_sides.jpg](../../docs/fusako_07_foot_screenshots/07_c2_bridge_faces_sides.jpg)
   - 底面から見て、土踏まず側をプロポーショナル編集（`O`）で内側にくぼませる。
   - [📸 参考: 08_c2_arch_proportional_edit.jpg](../../docs/fusako_07_foot_screenshots/08_c2_arch_proportional_edit.jpg)
   - 足裏の底面全体を四角面で閉じる。
   - [📸 参考: 09_c2_sole_bottom_face_fill.jpg](../../docs/fusako_07_foot_screenshots/09_c2_sole_bottom_face_fill.jpg)

---

### Part 3: 足の指（5本指）のモデリング (07:15〜13:10)
1. **小指の作成（サークル8頂点）**:
   - `Shift + A` $\to$ **メッシュ > 円（Circle）** を追加（頂点数: **`8`**）。
   - `R X 90` で正面に向け、小指の付け根位置へ配置。
   - [📸 参考: 10_c3_toe_circle_8verts.jpg](../../docs/fusako_07_foot_screenshots/10_c3_toe_circle_8verts.jpg)
2. **指先端への押し出しと整流**:
   - `E` で押し出しつつ `S` で縮小、関節部で `R` により軽く回転をかけながら指先まで伸ばす。
   - [📸 参考: 11_c3_toe_extrude_taper_joints.jpg](../../docs/fusako_07_foot_screenshots/11_c3_toe_extrude_taper_joints.jpg)
   - 先端を面張りし、**メッシュ > 頂点 > 頂点をスムーズに（Smooth Vertices）** を実行。
   - 上面（爪側）を少し平らに、下面（腹側）を `Alt + S` でふっくら丸く整流。
   - [📸 参考: 12_c3_toe_tip_smooth_vertices.jpg](../../docs/fusako_07_foot_screenshots/12_c3_toe_tip_smooth_vertices.jpg)
3. **他指の複製と親指のおにぎり三角成形**:
   - `Shift + D` で複製し、薬指・中指・人差し指・親指を順次配置。
   - **親指の特有形状**: 親指の断面エッジを選択し、`S X` で広げ、上面と内側を整えて **「おにぎり型（三角〜四角形断面）」** に成形。
   - [📸 参考: 13_c3_big_toe_onigiri_triangle.jpg](../../docs/fusako_07_foot_screenshots/13_c3_big_toe_onigiri_triangle.jpg)
4. **指の角度アーチと指間マージ**:
   - 足裏から見て、小指に向かって指が短くなるよう各指の付け根を `R` で回転整流。
   - [📸 参考: 14_c3_toes_angle_alignment.jpg](../../docs/fusako_07_foot_screenshots/14_c3_toes_angle_alignment.jpg)
   - 隣接する指同士の近接頂点を選択し、**`M` $\to$ 「中心に（At Center）」** でマージして指間の股を結合。
   - [📸 参考: 15_c3_toes_merge_between_digits.jpg](../../docs/fusako_07_foot_screenshots/15_c3_toes_merge_between_digits.jpg)

---

### Part 4: 足指と足甲・足裏の接合 (13:10〜18:30)
1. **指背側エッジの押し出しと頂点減衰**:
   - 指の上面（背側）エッジを選択し、足甲に向かって `E` で押し出し。
   - [📸 参考: 16_c4_toes_bridge_extrude_to_foot.jpg](../../docs/fusako_07_foot_screenshots/16_c4_toes_bridge_extrude_to_foot.jpg)
   - 頂点数が多すぎるため、隣り合う **3頂点を選んで `M` $\to$ 「中心にマージ」** を行い、エッジ数を段階的に集約（頂点減衰）。
   - [📸 参考: 17_c4_reduce_verts_merge_center.jpg](../../docs/fusako_07_foot_screenshots/17_c4_reduce_verts_merge_center.jpg)
2. **足裏側エッジの整理**:
   - 指の底面（腹側）エッジも同様に押し出し、`G G`（スライド）と `F`（面張り）で 4辺から 2辺へ集約して足裏メッシュへ歩み寄らせる。
   - [📸 参考: 18_c4_toes_sole_extrude_bridge.jpg](../../docs/fusako_07_foot_screenshots/18_c4_toes_sole_extrude_bridge.jpg)
3. **オブジェクト統合とスナップ接合**:
   - 足本体と指メッシュを選択し、**`Ctrl + J` で1つのオブジェクトに統合**。
   - [📸 参考: 19_c4_join_foot_and_toes_ctrl_j.jpg](../../docs/fusako_07_foot_screenshots/19_c4_join_foot_and_toes_ctrl_j.jpg)
   - 小指外側・親指内側の境界頂点から順に頂点スナップ＋マージ、隙間を四角面（`F`）で塞いで完全接合。
   - [📸 参考: 20_c4_snap_automerge_toes_to_foot.jpg](../../docs/fusako_07_foot_screenshots/20_c4_snap_automerge_toes_to_foot.jpg)

---

### Part 5: 土踏まず・かかと・くるぶしの整流と仕上げ (18:30〜24:46)
1. **土踏まず（縦アーチ）の立体形成**:
   - 足裏内側の頂点を選択し、**`G Z` で上方に持ち上げて** 綺麗なドーム状の土踏まずアーチを作成。
   - [📸 参考: 21_c5_sole_arch_lift_gz.jpg](../../docs/fusako_07_foot_screenshots/21_c5_sole_arch_lift_gz.jpg)
2. **スムースツールによる表面均等化**:
   - 左ツールバーの **「スムース（Smooth）」ツール** を選択し、ギザギザした表面をふんわりとなめらかに均等化。
   - [📸 参考: 22_c5_smooth_tool_brush.jpg](../../docs/fusako_07_foot_screenshots/22_c5_smooth_tool_brush.jpg)
   - 後ろから見て、かかとがしっかりと地面を捉えるよう `S X` で横幅を確保。
3. **足指の内向き自然アーチ**:
   - 薬指・小指をプロポーショナル編集（`O`）で少し内側（親指方向）に傾斜させ、リラックスした足指の自然な佇まいを付与。
   - [📸 参考: 23_c5_toes_curl_inward_arch.jpg](../../docs/fusako_07_foot_screenshots/23_c5_toes_curl_inward_arch.jpg)
4. **くるぶしの高さ違い（内高外低）の形成**:
   - **内くるぶし（親指側）**: 少し高い位置をループカット＋Alt+Sで膨らませる。
   - **外くるぶし（小指側）**: 少し低い位置を膨らませる。
   - 解剖学に基づいた左右非対称のくるぶしラインを完成させ、全体のシルエットを整流。
   - [📸 参考: 24_c5_ankle_malleolus_asymmetry.jpg](../../docs/fusako_07_foot_screenshots/24_c5_ankle_malleolus_asymmetry.jpg)

---

## 5. 必須テクニック＆ショートカット早見表

| ショートカット / 機能 | 操作名称 | 本チュートリアルでの用途 |
| :--- | :--- | :--- |
| `Ctrl + Numpad 7` | 下面ビュー（底面図） | 足の裏（土踏まず・足指の並び・かかとの幅）を真下から確認する |
| `P` $\to$ Selection | 選択物の分離 | 体の足首8頂点ループを別オブジェクトに切り離して足パーツを開始する |
| `Shift + N` | 面の法線再計算 | 押し出し時に反転したメッシュの裏表を外向き（正常）に一括修正する |
| `M` $\to$ At Center | 中心にマージ | 指同士の股の結合や、3頂点を束ねて足甲へのエッジ数を減衰させる |
| `Alt + S` | 法線方向に収縮/膨張 | かかとの丸み、足指の腹、くるぶしの出っ張りをふっくら肉厚にする |
| `G G` | 頂点/辺スライド | 形状を崩さずにエッジをずらし、四角面の密度を均等に整える |
| スムースツール | 頂点スムージング | 足の甲や土踏まずのガタついた頂点をドラッグ操作で滑らかに整流する |

---

## 6. 本プロジェクト（AnimeFace / 素体パイプライン）との連動・実装指針

1. **第4回（脚部メッシュ）との完全結合**:
   - 本仕様書で作られた足首の開口部は、第4回（Part 2）の脚部最下端（8頂点）と1対1で完全一致します。
   - 足首同士を `Ctrl + J` で統合後、全選択して `M` $\to$ **By Distance（距離でマージ）** を実行するだけで、完全に継ぎ目のない一体型素体になります。
2. **靴・ソックスモデリングの土台下絵**:
   - 本素体足メッシュの土踏まず・かかと・くるぶしの輪郭は、将来の靴（スニーカー・ローファー・ブーツ）やソックスをモデリングする際の完璧なフィット下地（シュリンクラップ/押し出しのベース）として機能します。
