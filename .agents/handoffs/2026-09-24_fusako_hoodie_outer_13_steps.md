# ふさこ氏『Blenderでキャラクターモデル制作！13 | フード付きアウターのモデリング』詳細操作手順書

## 1. 概要・メタデータ

- **動画タイトル**: 『Blenderでキャラクターモデル制作！13 | フード付きアウターのモデリング 〜初級から中級者向けチュートリアル〜』
- **URL**: https://www.youtube.com/watch?v=7Z9BdqXY6KA
- **動画長**: 38分31秒（2311秒）
- **公開日**: 2023年5月31日
- **対象工程**:
  - Chapter 1: フードの立ち上げ・内外二重構造化（00:00〜04:20）
  - Chapter 2: 身頃（胴体）の作成・ワンピースからの複製・接合（04:20〜13:08）
  - Chapter 3: 前開きトリム（縁取り）・厚み表現・段差ベベル・首周り整理（13:09〜24:34）
  - Chapter 4: フードの耳パーツ（ウサ耳/ケモ耳）作成・一体化・首後ろギャップ（24:35〜33:17）
  - Chapter 5: 袖（ペンギンの羽・萌え袖）モデリング・厚み付け（33:18〜38:31）
- **主要モディファイア**: Mirror（クリッピング有効）、Solidify（厚み付け、Even Thickness有効）、Subdivision Surface（レベル1〜2）
- **活用アドオン**: AutoMirror, LoopTools（Bridge, Relax）, Edge Flow（Set Flow）, Check Tool Box
- **スクリーンショット集フォルダ**: [docs/fusako_13_hoodie_outer_screenshots/](../../docs/fusako_13_hoodie_outer_screenshots/)
- **画像カタログ**: [docs/fusako_13_hoodie_outer_screenshots/README.md](../../docs/fusako_13_hoodie_outer_screenshots/README.md)

---

## 2. 核心トポロジー・衣装設計の黄金律

1. **素体・インナーの頂点数（12頂点）完全整合**:
   - フードの開口部サークルは素体・首元・ワンピースと同じ **12頂点** から開始。これにより、後の身頃接合や首元スナップで頂点が1対1で整合し、ポリゴン割りの歪みや不自然な三角化を完全防止。
2. **重ね着衣装の面複製（`Shift + D` $\to$ `Alt + S` $\to$ `P`）**:
   - アウターの胴体はゼロから作らず、下に着ているワンピースのお腹面を複製し、法線方向へ `Alt + S` で外側に膨らませて分離。素体・ワンピースのトポロジーと完全一致するため、着せ替え時やアニメーション時の衣服突き抜け（クリッピング）を根本防止。
3. **布の二重構造と `LoopTools > Bridge` 架橋**:
   - フードや首元は裏表の二重構造にする。外側ループと内側ループを `LoopTools > Bridge` で一発架橋し、厚みのあるリアルなフード形状を構築。
4. **`Solidify` 適用後の `Individual Origins` による段差ベベル表現**:
   - トリム（前開きの縁取り）に `Solidify` を適用した後、ピボットポイントを `Individual Origins`（それぞれの原点）にしてエッジを `S` 縮小することで、手動で複雑なポリゴンを割ることなく、ふっくらと丸みを帯びた段差ベベルを高速生成。
5. **`V` キー切り裂き（Rip）による重なり・隙間・布ギャップ表現**:
   - フード側面の急激な曲がり、前開きの左右非対称な合わせ目、首後ろのフード切り替え部など、布の重なりやギャップを作りたい箇所は `V` キーでメッシュを切り裂いて段差を作り、陰影と立体感を強調。
6. **ペンギン羽状・萌え袖の `S + Y` 拡張と `Solidify (Even Thickness)`**:
   - 腕メッシュから複製したループを袖口に向けて押し出し、手首の先で `S + Y` で大きく広げてペンギンの羽のような萌え袖を形成。`Solidify` の `Even Thickness`（均一な厚み）をオンにして、急角度な広がりでも薄くペラペラにならないよう補正。

---

## 3. チャプター別・詳細操作手順

### Chapter 1: フードの立ち上げ・内外二重構造化（00:00〜04:20）

1. **参考画像読み込みと前準備**:
   - 正面および側面の参考画像エンプティを、パーカー・アウター着用状態のリファレンス画像に切り替える。
   - 作業の邪魔になる髪オブジェクトをアウトライナーで一時非表示（`H` キー）にする。
   [📸 参考: 01_c1_reference_overlay_hoodie.jpg](../../docs/fusako_13_hoodie_outer_screenshots/01_c1_reference_overlay_hoodie.jpg)
2. **12頂点円（Circle）の配置**:
   - 3Dカーソルをワールド原点に置き、`Shift + A > Mesh > Circle` を追加。
   - オペレーターパネルで `Vertices` を **12** に設定。
   - `Tab` キーで編集モードに入り、`S` で顔の大きさに縮小、`G + Z` で頭部上部へ移動。
   [📸 参考: 02_c1_circle_12verts_hood_base.jpg](../../docs/fusako_13_hoodie_outer_screenshots/02_c1_circle_12verts_hood_base.jpg)
3. **顔周りの開口部ライン成形**:
   - プロポーショナル編集（`O` キー、スムーズ）を有効化。
   - 側面ビュー（テンキー3）で `R` 回転させ、前側を顎下へ下げ、後側を後頭部へ引き下げる。
   - 正面ビュー（テンキー1）で顔の輪郭を包むような卵形の開口部を作成。
   - `N` パネルの `AutoMirror` を実行し、X軸対称（Mirrorモディファイア、Clipping=ON）を設定。
   [📸 参考: 03_c1_proportional_hood_opening_align.jpg](../../docs/fusako_13_hoodie_outer_screenshots/03_c1_proportional_hood_opening_align.jpg)
4. **フード外側ラインの拡張**:
   - 開口部エッジループを選択し、`E` キーで押し出し直後に `Alt + S` で外側へ大きく膨らませる。
   - `G` キーで後頭部〜背中側へ後退させ、頭部全体をふんわり包み込むフード外殻の形状を大まかに作る。
   - 中央ラインの頂点がクリッピングでX=0に吸着していることを確認。
   [📸 参考: 04_c1_extrude_alt_s_outer_line.jpg](../../docs/fusako_13_hoodie_outer_screenshots/04_c1_extrude_alt_s_outer_line.jpg)
5. **内側受け口の押し出し**:
   - 開口部の内側エッジループを選択し、`E + Z` で下方に押し出し。
   - `Alt + S` で内側へ絞り込み、首元へ潜り込む内布の受け口を作る。
   [📸 参考: 05_c1_extrude_down_alt_s_inward.jpg](../../docs/fusako_13_hoodie_outer_screenshots/05_c1_extrude_down_alt_s_inward.jpg)
6. **内外ループのBridge架橋**:
   - 外側の下端ループと内側の下端ループを `Alt + 左クリック` ＋ `Shift + Alt + 左クリック` で両方選択。
   - 右クリック `LoopTools > Bridge` を実行し、面を張って袋状の二重布構造を完成。
   - 背中側の頂点を前に寄せて服の表面に近づけるよう微調整。
   [📸 参考: 06_c1_looptools_bridge_hood_double_layer.jpg](../../docs/fusako_13_hoodie_outer_screenshots/06_c1_looptools_bridge_hood_double_layer.jpg)

---

### Chapter 2: 身頃（胴体）の作成・ワンピースからの複製・接合（04:20〜13:08）

1. **ワンピース腹部面の複製と分離**:
   - ワンピースオブジェクトを選択し編集モードに入る。
   - 面選択モード（`3`）で、お腹まわりのエッジループを `Alt + 左クリック` で選択。
   - `Ctrl + テンキー+`（選択範囲拡大）で胴体中央〜腰の面を広く選択。
   - `Shift + D` で複製し、即座に `Esc` で移動キャンセル。
   - `Alt + S` で法線外側へわずかに膨らませる（ワンピースとの貫通回避）。
   - `P > Selection` で別オブジェクトとして分離。
   [📸 参考: 07_c2_duplicate_dress_belly_faces.jpg](../../docs/fusako_13_hoodie_outer_screenshots/07_c2_duplicate_dress_belly_faces.jpg)
2. **フードと胴体の結合**:
   - オブジェクトモードで、フードと複製した胴体を選択し、`Ctrl + J` で1つのオブジェクトに結合。
   - 形状把握を容易にするため、右クリック `Shade Flat`（フラットシェード）に切り替える。
   [📸 参考: 08_c2_ctrl_j_join_hood_and_body.jpg](../../docs/fusako_13_hoodie_outer_screenshots/08_c2_ctrl_j_join_hood_and_body.jpg)
3. **背中中央の面張りとクアッド整流**:
   - 背中側で近接している頂点同士を `F` キーで面張り。
   - ループスライド（`G + G`）で内側に寄せ、`Ctrl + R` でループカットを1本追加して4点クアッド面を形成。
   [📸 参考: 09_c2_f_face_loop_cut_quad_topology.jpg](../../docs/fusako_13_hoodie_outer_screenshots/09_c2_f_face_loop_cut_quad_topology.jpg)
4. **ランダムカラー表示の有効化**:
   - 重なり合う服のパーツが増えてきたため、画面右上の `Viewport Shading` ドロップダウンから `Color > Random` を選択。
   - オブジェクトごとに異なるカラーが割り振られ、パーツの境界が鮮明に識別可能となる。
   [📸 参考: 10_c2_random_color_viewport_overlay.jpg](../../docs/fusako_13_hoodie_outer_screenshots/10_c2_random_color_viewport_overlay.jpg)
5. **フード側面の切り裂きと隙間作成**:
   - フード側面と身頃の境界で角張った無理な接続になっている部分を選択。
   - `V` キーで切り裂いてメッシュを分離し、`Alt + S` で膨らませて隙間（空間）を開ける。
   [📸 参考: 11_c2_v_rip_hood_edge_alt_s_gap.jpg](../../docs/fusako_13_hoodie_outer_screenshots/11_c2_v_rip_hood_edge_alt_s_gap.jpg)
6. **LoopTools Bridgeによる滑らかな架橋**:
   - 隙間の両側のエッジループを選択し、右クリック `LoopTools > Bridge` を実行。
   - 急な折れ曲がりがなくなり、首から肩にかけて自然に流れる布の曲面が完成。
   [📸 参考: 12_c2_looptools_bridge_smooth_junction.jpg](../../docs/fusako_13_hoodie_outer_screenshots/12_c2_looptools_bridge_smooth_junction.jpg)
7. **布のしわと凹凸の造形**:
   - フード内側や側面に `Ctrl + R` でループを追加。
   - 前側は `Alt + S` で少し内側に凹ませ、後ろ側は外側に膨らませることで、重力と布のたるみによるリアルなしわを表現。
   [📸 参考: 13_c2_cloth_wrinkles_alt_s_indents.jpg](../../docs/fusako_13_hoodie_outer_screenshots/13_c2_cloth_wrinkles_alt_s_indents.jpg)
8. **裾ループの下方延長**:
   - アウターの裾がワンピースの上にかぶさるよう、最下端ループのすぐ近くに `Ctrl + R` でループを追加。
   - 最下端ループを選択し、`G + G`（エッジスライド）で下方へ延長。
   - 中央が少し持ち上がったカーブになるよう、頂点を `G + Z` で微調整。
   [📸 参考: 14_c2_extend_hem_downward_gg.jpg](../../docs/fusako_13_hoodie_outer_screenshots/14_c2_extend_hem_downward_gg.jpg)

---

### Chapter 3: 前開きトリム（縁取り）・厚み表現・段差ベベル（13:09〜24:34）

1. **前開きトリム用の平行ループ追加**:
   - 前面の開口部（ファスナー・合わせ目）の縁取りを作るため、`Ctrl + R` でループを追加し、`E` キーを押して開口部エッジと完全平行になるように幅を揃えて配置。
   [📸 参考: 15_c3_front_trim_parallel_loops_ctrl_r.jpg](../../docs/fusako_13_hoodie_outer_screenshots/15_c3_front_trim_parallel_loops_ctrl_r.jpg)
2. **トリム面の分離と `Solidify` モディファイア**:
   - 今作ったトリムの面ループを選択し、`P > Selection` で別オブジェクトとして分離。
   - `Solidify` モディファイアを追加し、`Thickness: 0.005m`、`Offset: 1.0`（外側に押し出し）を設定。
   [📸 参考: 16_c3_separate_trim_solidify_modifier.jpg](../../docs/fusako_13_hoodie_outer_screenshots/16_c3_separate_trim_solidify_modifier.jpg)
3. **`Individual Origins` による段差ベベル強調**:
   - `Solidify` モディファイアを `Ctrl + A` で確定適用。
   - 縁のエッジを選択し、キーボードの `.`（ピリオド）から `Individual Origins`（それぞれの原点）に切り替える。
   - `S` キーで各エッジを少し縮小することで、境界にふっくらとした立体的な段差ベベルを形成。
   [📸 参考: 17_c3_individual_origins_s_bevel_step.jpg](../../docs/fusako_13_hoodie_outer_screenshots/17_c3_individual_origins_s_bevel_step.jpg)
4. **`V` 切り裂きによる左右非対称の前開き重ね合わせ**:
   - 前開きの重なりエッジを選択し、`V` キーで切り裂き。
   - 一方の面を `G + X` で横へずらして重なりを作り、不要な中間ループは `X > Dissolve Edges`（辺を溶解）で削除。
   - 端の開口部を `F` キーで面張りして密閉。
   [📸 参考: 18_c3_v_rip_asymmetrical_front_overlap.jpg](../../docs/fusako_13_hoodie_outer_screenshots/18_c3_v_rip_asymmetrical_front_overlap.jpg)
5. **マークシャープによる境界線の陰影強調**:
   - 重なりの段差エッジを選択し、`Ctrl + E > Mark Sharp`（シャープをマーク）を設定。
   - プロパティパネルで `Auto Smooth`（自動スムーズ）を `180°` に設定し、シャープエッジの境界をくっきり描画。
   [📸 参考: 19_c3_mark_sharp_trim_overlap_edges.jpg](../../docs/fusako_13_hoodie_outer_screenshots/19_c3_mark_sharp_trim_overlap_edges.jpg)
6. **袖口・首周りの布厚み密閉**:
   - 袖口や首元の開口部ループを選択し、`I` キーで面差し込み（インセット）を行い、内側の不要面を `X > Faces` で削除。
   - 奥側の頂点を `Shift + Tab`（スナップ有効、Vertex/Active）で素体・ワンピースの頂点にスナップ密着させ、隙間からの肌見えを防止。
   [📸 参考: 20_c3_inset_cuff_collar_cloth_thickness.jpg](../../docs/fusako_13_hoodie_outer_screenshots/20_c3_inset_cuff_collar_cloth_thickness.jpg)

---

### Chapter 4: フードの耳パーツ作成・一体化・首後ろギャップ（24:35〜33:17）

1. **後頭部エッジからの耳ベース立ち上げ**:
   - フード後頭部のエッジを選択し、`Shift + D` で複製 $\to$ `P` で分離。
   - `E + Z` で下方に押し出し、`Ctrl + R` で中間ループを追加。
   [📸 参考: 21_c4_duplicate_hood_edge_ear_base.jpg](../../docs/fusako_13_hoodie_outer_screenshots/21_c4_duplicate_hood_edge_ear_base.jpg)
2. **先端の丸めと外ハネ成形**:
   - 耳の先端3頂点を選択し、`Vertex > Smooth Vertices`（頂点をスムーズ化）で角を丸める。
   - プロポーショナル編集を使い、先に向かって外側に跳ねる（外ハネ）愛らしい垂れ耳形状へ成形。
   - `E` キーで厚みを押し出し、立体的な板状パーツにする。
   [📸 参考: 22_c4_smooth_vertices_ear_tip_curl.jpg](../../docs/fusako_13_hoodie_outer_screenshots/22_c4_smooth_vertices_ear_tip_curl.jpg)
3. **フード側の受け口分割（Subdivide Smoothness）**:
   - フード側の接続予定エッジを選択し、右クリック `Subdivide` を実行。
   - 左下のパネルで `Smoothness: 1.5` に設定し、なだらかな接続ベースを形成。
   [📸 参考: 23_c4_subdivide_smoothness_hood_socket.jpg](../../docs/fusako_13_hoodie_outer_screenshots/23_c4_subdivide_smoothness_hood_socket.jpg)
4. **耳とフードの結合・頂点マージ一体化**:
   - 耳パーツとフードを選択し、`Ctrl + J` で結合。
   - 互いの対向する面を `X > Faces` で削除し、近接する頂点同士を `Merge at Center`（中心にマージ）で一体化。
   - 生じた五角形面を `Ctrl + T` で三角面化し、トポロジーエラーを解消。
   [📸 参考: 24_c4_ctrl_j_join_ears_merge_at_center.jpg](../../docs/fusako_13_hoodie_outer_screenshots/24_c4_ctrl_j_join_ears_merge_at_center.jpg)
5. **首後ろ切り替え部の布段差ギャップ**:
   - フードと身頃が切り替わる首後ろのエッジを選択し、`V` キーで切り裂き。
   - `G + Z` で少し上に持ち上げ、両エッジ間に `F` キーで面を張って、布が折り重なる厚みギャップを造形。
   [📸 参考: 25_c4_v_rip_back_neck_thickness_gap.jpg](../../docs/fusako_13_hoodie_outer_screenshots/25_c4_v_rip_back_neck_thickness_gap.jpg)

---

### Chapter 5: 袖（ペンギンの羽・萌え袖）モデリング・厚み付け（33:18〜38:31）

1. **腕メッシュからの袖ベース複製**:
   - 腕メッシュを選択し、肩口から上腕にかけての面ループを `Shift + D` 複製 $\to$ `P` 分離。
   - 右クリック `LoopTools > Relax` で滑らかにし、`S + X` でフラット化。
   - 肩開きデザインに合わせて、最下部頂点をアクティブにして少し外側へ傾斜。
2. **羽状・萌え袖の押し出し拡張**:
   - `E + X` で腕の長さに沿って横へ押し出し（指先がチラリと見える萌え袖の長さに設定）。
   - `S + X + 0` で袖口ループを垂直に揃える。
   - プロポーショナル編集をオンにし、袖口を `S + Y` で大きく広げてペンギンの羽のようなワイドスリーブを形成。
   - 手をパーに広げても袖の内側に収まる余裕を持たせる。
3. **ボリューム膨らみと中間ループ**:
   - 袖の中間に `Ctrl + R` でループを追加し、一番盛り上がるラインを `Alt + S` で外側にボリューミーに膨張。
   - 下側も少し垂れ下がるように `Alt + S` と `G + Z` で調整。
4. **`Solidify`（厚み付け）と完成**:
   - `Solidify` モディファイアを追加（`Thickness: 0.004〜0.02m`）。
   - 急角度な広がりによる厚みの減少を防ぐため、**`Even Thickness`（均一な厚み）に必ずチェックを入れる**。
   - オブジェクトモードで右クリック `Shade Smooth` を適用。
   - これにより、フード・耳・身頃・トリム・ペンギン萌え袖が揃ったアウター全体が完成。
   [📸 参考: 26_c5_penguin_wings_extrude_solidify.jpg](../../docs/fusako_13_hoodie_outer_screenshots/26_c5_penguin_wings_extrude_solidify.jpg)

---

## 4. プロシージャル・アドオン実装向けパラメトリック仕様

今後の自動生成スクリプト・アドオン化において制御すべきパラメータ：

| パラメータ名 | 推奨値 / 単位 | 説明 |
| :--- | :--- | :--- |
| `hood_opening_vertices` | 12 | フード開口部サークル頂点数（素体・首元と完全一致） |
| `hood_outer_bulge` | 0.06〜0.10 m | フード外殻の `Alt + S` 膨らみ量 |
| `body_belly_offset` | 0.005 m | ワンピース面からの `Alt + S` 浮かせ量（貫通防止） |
| `front_trim_width` | 0.02〜0.03 m | 前開きトリムの均等平行ループ幅 |
| `trim_solidify_thickness` | 0.005 m | トリムの `Solidify` 厚み |
| `trim_bevel_scale` | 0.90〜0.95 | `Individual Origins` でのエッジ縮小率（段差ベベル） |
| `ear_tip_curl_angle` | 15〜25 deg | 耳パーツ先端の外ハネ傾斜角度 |
| `sleeve_flare_y` | 1.8〜2.5倍 | 袖口の `S + Y` ペンギン羽状拡大率 |
| `sleeve_solidify_thickness` | 0.004〜0.008 m | 袖の `Solidify` 厚み（Even Thickness=True） |

---

## 5. 参考リソース

- 元動画: [YouTube - ふさこ氏 第13話](https://www.youtube.com/watch?v=7Z9BdqXY6KA)
- 字幕テキスト: [fusako_13_subtitles_timestamped.txt](fusako_13_subtitles_timestamped.txt)
- 生字幕VTT: [fusako_13_subtitles_raw.ja.vtt](fusako_13_subtitles_raw.ja.vtt)
- スクリーンショット集カタログ: [README.md](../../docs/fusako_13_hoodie_outer_screenshots/README.md)
