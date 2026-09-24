# ふさこ氏『Blenderでキャラクターモデル制作！16 | ポシェット（ペンギン）のモデリング』詳細操作手順書

## 1. 概要・メタデータ

- **動画タイトル**: 『Blenderでキャラクターモデル制作！16 | ポシェット（ペンギン）のモデリング 〜初級から中級者向けチュートリアル〜』
- **URL**: https://www.youtube.com/watch?v=hE2osPXH-8s
- **動画長**: 31分03秒（1863秒）
- **公開日**: 2023年6月3日
- **対象工程**:
  - Chapter 1: ポシェット本体の立ち上げ・フタ分離・フリル波形（00:00〜08:53）
  - Chapter 2: スカーフのモデリング・結び目・垂れ布の左右非対称化（08:54〜14:16）
  - Chapter 3: 紐・リボン（ベジェカーブ）・中央留め具・メッシュ化（14:17〜23:29）
  - Chapter 4: ウサ耳/ペンギン耳パーツの作成・背面差し込み（23:30〜28:39）
  - Chapter 5: 親子付け（Ctrl+P）・腰への配置・Copy Attributes Menu（28:40〜31:03）
- **主要モディファイア**: Subdivision Surface（レベル1確定適用）、Mirror（Mirror Object指定）、Solidify（厚み付け、Fill Rim: OFF）、Curve（ベジェカーブベベル）
- **活用アドオン**: AutoMirror, LoopTools（Bridge, Relax）, Copy Attributes Menu
- **スクリーンショット集フォルダ**: [docs/fusako_16_penguin_pochette_screenshots/](../../docs/fusako_16_penguin_pochette_screenshots/)
- **画像カタログ**: [docs/fusako_16_penguin_pochette_screenshots/README.md](../../docs/fusako_16_penguin_pochette_screenshots/README.md)

---

## 2. 核心トポロジー・小物アクセサリー設計の黄金律

1. **ポーチ本体とフタ（フラップ）の `Y` キー分離構造**:
   - 立方体からポーチを作る際、フタ部分を別オブジェクトにするのではなく、編集モードでフタのエッジループを `Y`（メッシュ切り離し）で分離し、`G + Z` で少し上に持ち上げる。同一オブジェクト内でポーチ開口部のリアルな重なり・隙間を破綻なく生成可能。
2. **アクティブ要素中心スケールによる均等半円フリル成形**:
   - フリルの谷頂点をマージしてジグザグにした後、山側の中央頂点をアクティブにしてピボットポイントを `Active Element` に設定。`S` スケールをかけることで、完全な真円弧を描く愛らしい半円フリルを狂いなく均等成形。
3. **ベジェカーブによる紐・リボンの非破壊太さ制御**:
   - 複雑に折れ曲がる紐やリボンはポリゴン押し出しで作らず、`Curve > Bezier` を使用。`Geometry > Bevel > Depth` で太さを数値制御し、`Shift + D` で制御点を複製して輪っかと垂れ紐を高速作成。確定後に `Convert to Mesh` でポリゴン化し、金具の中へ潜り込ませてクリッピング結合。
4. **裏面非表示シェーダー対応の `Solidify (Fill Rim: OFF)`**:
   - ゲームエンジンやVRM（MToon等）の裏面カリング環境下で、リボンのような薄い布パーツの裏面が消えるのを防ぐため、`Solidify` モディファイアを追加。この際 `Fill Rim`（縁を張る）のチェックを外すことで、エッジに不要なポリゴンを増やさずに表面と裏面の両方に法線を向けた軽量描画を実現。
5. **`Copy Attributes Menu`（Ctrl + C）によるモディファイア一括同期**:
   - ポシェットのように多数の独立パーツ（本体、スカーフ、紐、耳等）で構成されるアセットでは、1つの親パーツに `Mirror`（Mirror Object: `Head`）を設定した後、全パーツを選択 $\to$ 親を最後に選択して `Ctrl + C > Copy Selected Modifiers` を実行。全子パーツへ同じ対称化設定が一瞬で完全コピーされ、設定ミスを撲滅。

---

## 3. チャプター別・詳細操作手順

### Chapter 1: ポシェット本体の立ち上げ・フタ・フリル（00:00〜08:53）

1. **Cube追加と腰位置へのスケール配置**:
   - `Shift + A > Mesh > Cube` を追加。
   - `S` キーでポシェットサイズに縮小し、アウター腰の指定位置へ移動。
   - `AutoMirror` でX軸対称化し、`Ctrl + 1` で `Subdivision Surface`（レベル1）を追加。
   [📸 参考: 01_c1_cube_base_pochette_placement.jpg](../../docs/fusako_16_penguin_pochette_screenshots/01_c1_cube_base_pochette_placement.jpg)
2. **フタ（フラップ）の切り離しと持ち上げ**:
   - フタとなる上部の面を選択し、`Y` キーでメッシュを切り離し。
   - `G + Z` で少し上に持ち上げ、フタと本体の間に隙間を作って開口部の厚みを表現。
   [📸 参考: 02_c1_y_rip_flap_cover_gz.jpg](../../docs/fusako_16_penguin_pochette_screenshots/02_c1_y_rip_flap_cover_gz.jpg)
3. **側面のインセットによるマチ成形**:
   - 側面の面を選択し、`I` キーでインセット（`Boundary: OFF`）。
   - `G + X` で少し内側に凹ませ、バッグ特有のマチ（奥行き・縫い目）を造形。
   [📸 参考: 03_c1_inset_side_depth_gusset.jpg](../../docs/fusako_16_penguin_pochette_screenshots/03_c1_inset_side_depth_gusset.jpg)
4. **Subsurf確定適用とポリゴン最適化**:
   - `Subdivision Surface` モディファイアを `Ctrl + A` で確定適用。
   - 余分なエッジリングを `Alt + Ctrl + 左クリック` で選択し、`X > Collapse Edge Loops`（辺ループを溶解・統合）でポリゴン数を軽量化。
   [📸 参考: 04_c1_collapse_edge_loops_optimize.jpg](../../docs/fusako_16_penguin_pochette_screenshots/04_c1_collapse_edge_loops_optimize.jpg)
5. **前面フリルの分割と色分けマーキング**:
   - 前面メッシュに縦ループを追加して5等分。
   - `Mark Sharp` を交互に設定し、フリルの谷と山を水色・赤色のラインで色分け視認化。
   [📸 参考: 05_c1_mark_sharp_frill_color_segments.jpg](../../docs/fusako_16_penguin_pochette_screenshots/05_c1_mark_sharp_frill_color_segments.jpg)
6. **インセットと谷頂点マージによるジグザグ骨格**:
   - フリルの面を選択し、`I` キーでインセット。
   - 谷となる頂点同士を選択し、`Merge at Center` で結合してジグザグ波形を形成。
   [📸 参考: 06_c1_inset_valley_merge_zigzag.jpg](../../docs/fusako_16_penguin_pochette_screenshots/06_c1_inset_valley_merge_zigzag.jpg)
7. **アクティブ要素中心スケールによる半円フリル成形**:
   - 各フリルの弧の中心頂点をアクティブにし、ピボットポイントを `Active Element` に設定。
   - `S` スケールで均等に広げ、綺麗な半円スカラップフリルを完成。
   [📸 参考: 07_c1_active_element_scale_round_frill.jpg](../../docs/fusako_16_penguin_pochette_screenshots/07_c1_active_element_scale_round_frill.jpg)

---

### Chapter 2: スカーフのモデリング（08:54〜14:16）

1. **ポシェット上部面からのスカーフ複製・分離**:
   - ポシェット上部の面を選択し、`Shift + D` で複製 $\to$ `P > Selection` で別オブジェクト分離。
   - `G + Y` で手前に引き出し、ポシェットの上に巻かれたスカーフのベースを作成。
   [📸 参考: 08_c2_duplicate_faces_scarf_base.jpg](../../docs/fusako_16_penguin_pochette_screenshots/08_c2_duplicate_faces_scarf_base.jpg)
2. **スカーフ結び目パーツの作成**:
   - `Shift + A > Mesh > Cube` を追加し、結び目サイズに縮小。
   - 上下の面を `X > Faces` で削除し、布が通る筒状パーツを成形。
   [📸 参考: 09_c2_cube_extrude_open_scarf_knot.jpg](../../docs/fusako_16_penguin_pochette_screenshots/09_c2_cube_extrude_open_scarf_knot.jpg)
3. **垂れ布の押し出しとふんわり膨らみ**:
   - 結び目下端のエッジを選択し、`E` キーで下方に押し出し。
   - 中間に `Ctrl + R` でループを追加し、`Alt + S` で外側にふんわり膨らませて布のボリュームを表現。
   [📸 参考: 10_c2_scarf_tail_extrude_alt_s.jpg](../../docs/fusako_16_penguin_pochette_screenshots/10_c2_scarf_tail_extrude_alt_s.jpg)
4. **Mirror適用と左右非対称微調整**:
   - スカーフの `Mirror` モディファイアを `Ctrl + A` で適用。
   - 左右の垂れ布の長さ・角度をわずかにずらし、自然で躍動感のある布の表情を付与。
   [📸 参考: 11_c2_asymmetrical_scarf_tails_tweak.jpg](../../docs/fusako_16_penguin_pochette_screenshots/11_c2_asymmetrical_scarf_tails_tweak.jpg)

---

### Chapter 3: 紐・リボン（カーブを活用した紐モデリング）（14:17〜23:29）

1. **ベジェカーブの追加と太さ設定**:
   - 3Dカーソルをポシェット正面に合わせ、`Shift + A > Curve > Bezier` を追加。
   - オブジェクトデータプロパティの `Geometry > Bevel > Depth` を `0.003m` に設定し、均一な丸紐を生成。
   [📸 参考: 12_c3_curve_bezier_bevel_depth_cord.jpg](../../docs/fusako_16_penguin_pochette_screenshots/12_c3_curve_bezier_bevel_depth_cord.jpg)
2. **輪っかと垂れ紐のカーブ編集**:
   - カーブ編集モードで、`Shift + D` で制御点を複製。
   - リボンの左右のループ（輪っか）と下に垂れる2本の紐を流線形に配置。
   [📸 参考: 13_c3_curve_loop_and_tail_shaping.jpg](../../docs/fusako_16_penguin_pochette_screenshots/13_c3_curve_loop_and_tail_shaping.jpg)
3. **中央留め具金具の配置**:
   - `Shift + A > Mesh > Cube` を追加し、リボン結び目の留め具金具として配置。
   - スリット穴をインセット・押し出しで造形。
   [📸 参考: 14_c3_cube_central_metal_fastener.jpg](../../docs/fusako_16_penguin_pochette_screenshots/14_c3_cube_central_metal_fastener.jpg)
4. **メッシュ変換（Convert to Mesh）**:
   - カーブ形状が完成したら、オブジェクトモードで右クリック `Convert to > Mesh` を実行。
   - カーブがクリーンな円柱ポリゴンメッシュに変換される。
   [📸 参考: 15_c3_convert_to_mesh_curve_cord.jpg](../../docs/fusako_16_penguin_pochette_screenshots/15_c3_convert_to_mesh_curve_cord.jpg)
5. **端点の金具潜り込みとクリッピングマージ**:
   - 紐の端点ループを選択し、金具の内部へ押し込み。
   - `AutoMirror` のクリッピングを有効化し、中央で完全溶接。
   [📸 参考: 16_c3_cord_ends_tuck_clipping_merge.jpg](../../docs/fusako_16_penguin_pochette_screenshots/16_c3_cord_ends_tuck_clipping_merge.jpg)
6. **`Solidify (Fill Rim: OFF)` による裏面描画最適化**:
   - リボンの板ポリ部分に `Solidify` を追加し、`Fill Rim` のチェックを外す。
   - ゲームシェーダー（両面描画）での厚み破綻を防止。
   [📸 参考: 17_c3_solidify_fill_rim_off_shading.jpg](../../docs/fusako_16_penguin_pochette_screenshots/17_c3_solidify_fill_rim_off_shading.jpg)
7. **ポシェット本体の厚み付け**:
   - ポシェット本体とフタに `Solidify`（`Thickness: 0.002m`）を適用。
   [📸 参考: 18_c3_solidify_pochette_body_thickness.jpg](../../docs/fusako_16_penguin_pochette_screenshots/18_c3_solidify_pochette_body_thickness.jpg)

---

### Chapter 4: ウサ耳/ペンギン耳パーツの作成・背面差し込み（23:30〜28:39）

1. **耳ベースの立ち上げ**:
   - スカーフ上端のエッジを選択し、`Shift + D` で複製。
   - `E + Z` で上方に押し出し、ウサ耳の板状ベースを立ち上げ。
   [📸 参考: 19_c4_duplicate_edge_rabbit_ears_base.jpg](../../docs/fusako_16_penguin_pochette_screenshots/19_c4_duplicate_edge_rabbit_ears_base.jpg)
2. **先端スムーズと厚み押し出し**:
   - 先端頂点を選択し、`Vertex > Smooth Vertices` で丸める。
   - `E` キーで厚みを押し出し、立体的な耳パーツを成形。
   [📸 参考: 20_c4_smooth_vertices_ear_thickness.jpg](../../docs/fusako_16_penguin_pochette_screenshots/20_c4_smooth_vertices_ear_thickness.jpg)
3. **ポシェット背面への差し込み配置**:
   - 耳の底面を削除し、ポシェット背面のフタ裏に潜り込ませて違和感なく一体化。
   [📸 参考: 21_c4_embed_ears_into_pochette_back.jpg](../../docs/fusako_16_penguin_pochette_screenshots/21_c4_embed_ears_into_pochette_back.jpg)

---

### Chapter 5: 親子付け・腰への配置・Copy Attributes Menu（28:40〜31:03）

1. **全パーツの親子付け（Ctrl + P > Keep Transform）**:
   - 耳、紐、留め具、スカーフ、ポシェット本体を選択（ポシェット本体がアクティブ親）。
   - `Ctrl + P > Object (Keep Transform)` を実行し、本体を動かすだけで全パーツが追従する構造を構築。
   [📸 参考: 22_c5_ctrl_p_parenting_keep_transform.jpg](../../docs/fusako_16_penguin_pochette_screenshots/22_c5_ctrl_p_parenting_keep_transform.jpg)
2. **キャラクター腰への配置と顔基準Mirror**:
   - ポシェット全体をキャラクターのアウター腰部分に配置。
   - ポシェット本体に `Mirror` モディファイアを追加し、`Mirror Object` に顔（`Head`）を指定。
   [📸 参考: 23_c5_waist_placement_mirror_face_target.jpg](../../docs/fusako_16_penguin_pochette_screenshots/23_c5_waist_placement_mirror_face_target.jpg)
3. **Copy Attributes Menu（Ctrl + C）による一括コピー**:
   - 全子パーツを選択後、ポシェット本体を最後に選択（アクティブ）。
   - `Ctrl + C > Copy Selected Modifiers` を実行し、顔基準の `Mirror` モディファイアを全パーツへ一括同期適用。
   - これにより、ポシェット装飾品全体のモデリングが完全完了。
   [📸 参考: 24_c5_copy_attributes_menu_mirror_copy.jpg](../../docs/fusako_16_penguin_pochette_screenshots/24_c5_copy_attributes_menu_mirror_copy.jpg)

---

## 4. プロシージャル・アドオン実装向けパラメトリック仕様

今後の自動生成スクリプト・アドオン化において制御すべきパラメータ：

| パラメータ名 | 推奨値 / 単位 | 説明 |
| :--- | :--- | :--- |
| `pochette_width` | 0.06〜0.09 m | ポシェット本体の幅 |
| `pochette_height` | 0.05〜0.08 m | ポシェット本体の高さ |
| `pochette_depth` | 0.03〜0.05 m | ポシェットのマチ（奥行き） |
| `frill_segments` | 5 | 前面スカラップフリルの枚数 |
| `cord_bevel_depth` | 0.0025〜0.004 m | ベジェカーブ紐の半径太さ |
| `scarf_solidify_thickness` | 0.002 m | スカーフの厚み |
| `pochette_solidify_thickness` | 0.0025 m | ポシェット本体の厚み |

---

## 5. 参考リソース

- 元動画: [YouTube - ふさこ氏 第16話](https://www.youtube.com/watch?v=hE2osPXH-8s)
- 字幕テキスト: [fusako_16_subtitles_timestamped.txt](fusako_16_subtitles_timestamped.txt)
- 生字幕VTT: [fusako_16_subtitles_raw.ja.vtt](fusako_16_subtitles_raw.ja.vtt)
- スクリーンショット集カタログ: [README.md](../../docs/fusako_16_penguin_pochette_screenshots/README.md)
