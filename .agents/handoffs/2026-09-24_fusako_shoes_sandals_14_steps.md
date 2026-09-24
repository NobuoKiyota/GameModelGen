# ふさこ氏『Blenderでキャラクターモデル制作！14 | 靴（サンダル・ブーツ）のモデリング』詳細操作手順書

## 1. 概要・メタデータ

- **動画タイトル**: 『Blenderでキャラクターモデル制作！14 | 靴（サンダル・ブーツ）のモデリング 〜初級から中級者向けチュートリアル〜』
- **URL**: https://www.youtube.com/watch?v=KaTcr7DTKQc
- **動画長**: 23分36秒（1416秒）
- **公開日**: 2023年6月1日
- **対象工程**:
  - Chapter 1: サンダル・靴底・アッパーのモデリング（00:00〜08:21）
  - Chapter 2: 靴下（モコモコ・ギザギザ縁・履き口二重トリム）のモデリング（08:22〜16:04）
  - Chapter 3: ペンギンの羽飾り（靴側面の立体パーツ）のモデリング（16:05〜18:59）
  - Chapter 4: ポンポン（球体ファー飾り）のモデリング・対称化・仕上げ（19:00〜23:36）
- **主要モディファイア**: Mirror（クリッピング有効）、Subdivision Surface（レベル1確定適用）、Solidify
- **活用アドオン**: AutoMirror, LoopTools（Bridge, Relax）, Checker Deselect（Blender標準）
- **スクリーンショット集フォルダ**: [docs/fusako_14_shoes_sandals_screenshots/](../../docs/fusako_14_shoes_sandals_screenshots/)
- **画像カタログ**: [docs/fusako_14_shoes_sandals_screenshots/README.md](../../docs/fusako_14_shoes_sandals_screenshots/README.md)

---

## 2. 核心トポロジー・フットウェア設計の黄金律

1. **足裏からのインセット（`I`）によるインナーソールとアッパーの整合**:
   - 靴底メッシュを `Shift + D + Z` で複製退避した後、上部ベースは `I`（インセット）で外周を1段縮小し、外枠ループを削除して一回り小さいインナーソールを作成。この外周ループからアッパーを上へ押し出すことで、靴底とアッパーの間に自然な「コバ（張り出し）」が生まれ、リアルなサンダル構造になる。
2. **ソールへの「めり込み膨らみ（`Alt + S`）」による接着表現**:
   - アッパー下端をそのまま平面的に靴底に乗せるのではなく、下端近くに `Ctrl + R` でループを追加し、最下部を `Alt + S` で外側に膨らませて靴底にわずかに食い込ませる。これにより、布や革がソールに固定されているテンションとリアルな接地陰影が生まれる。
3. **`Checker Deselect`（チェッカー選択）＋ `G + G` によるジグザグ縁の一発生成**:
   - 靴下の縁や襟元のジグザグ（波形）を作る際、手作業で1頂点ずつ動かすと等間隔が崩れる。ループを `Subdivide`（細分化）した後、`Select > Checker Deselect` で1つ飛ばしに頂点を選択し、`G + G`（エッジスライド）で上へスライドすることで、完全に均等なジグザグ波形を一発で作成可能。生じた五角形面は `Ctrl + T` で三角面化しトポロジーをクリーンに保つ。
4. **履き口の二重トリム架橋（`Shift + D` $\to$ `Alt + S` $\to$ `LoopTools > Bridge`）**:
   - 開口部の縁取りは、面ループを複製して `Alt + S` で内側に凹ませて隙間を作り、両側のエッジループを `LoopTools > Bridge` で架橋する。さらにエッジリングを選択して `Individual Origins`（それぞれの原点）でスケールすることで、縁取りの厚み幅を自在に調整できる。
5. **Cube + Subsurf1適用 + ベベル + `To Sphere` によるポンポン（真球ケージ）の生成**:
   - UV球から作ると極（ポール）に三角面が集まり、Subsurfや変形時にシワが寄る。CubeにSubsurfレベル1を適用して24面の球体ケージを作り、角のエッジを `Ctrl + B` で面取りした後に `Shift + Alt + S`（To Sphere: 1.0）で真球化することで、全方位に均等な四角面グリッドを持つ理想的なファー飾りベースが得られる。

---

## 3. チャプター別・詳細操作手順

### Chapter 1: サンダル・靴底・アッパーのモデリング（00:00〜08:21）

1. **靴底平面の追加と底面ビューアライン**:
   - `Shift + S > Cursor to World Origin` で3Dカーソルを原点へ。
   - `Shift + A > Mesh > Plane` を追加。
   - `Ctrl + テンキー7`（底面ビュー）に切り替え、足裏メッシュより一回り大きいサイズに配置。
   [📸 参考: 01_c1_plane_bottom_view_align.jpg](../../docs/fusako_14_shoes_sandals_screenshots/01_c1_plane_bottom_view_align.jpg)
2. **足型シルエットへの頂点成形**:
   - 編集モードで `Ctrl + R` を押し、縦方向に5本のループカットを追加。
   - 頂点を横方向に移動しながら、つま先の丸み、土踏まずのくびれ、かかとの丸みをトレース。
   - 中央にも横ループを追加し、前後にふくらみを持たせる。
   [📸 参考: 02_c1_five_loops_sole_contour.jpg](../../docs/fusako_14_shoes_sandals_screenshots/02_c1_five_loops_sole_contour.jpg)
3. **インナーソールの縮小と靴底の複製退避**:
   - 作成した靴底面を `Shift + D + Z` で少し下方に複製退避。
   - 上側の面を選択し、`I` キーでわずかにインセット。
   - 外周の余分なループを `Alt + 左クリック` で選択し、`X > Edges` で削除して一回り小さいインナーソールを作成。
   [📸 参考: 03_c1_inset_inner_sole_shrink.jpg](../../docs/fusako_14_shoes_sandals_screenshots/03_c1_inset_inner_sole_shrink.jpg)
4. **サンダルアッパーの立ち上げ**:
   - インナーソール外周を選択し、`E + Z` で上方に押し出し。
   - `S + X` で幅を適度に絞り、足の甲を覆う紺色アッパーのベースを立ち上げる。
   [📸 参考: 04_c1_extrude_z_sandal_upper.jpg](../../docs/fusako_14_shoes_sandals_screenshots/04_c1_extrude_z_sandal_upper.jpg)
5. **甲の丸みと天面の面張り**:
   - `Ctrl + R` で中央に横ループを追加し、`G + Z` で足の甲の高さまで持ち上げる。
   - 対向する頂点同士を `F` キーで面張りし、足の甲を覆う曲面を形成。
   [📸 参考: 05_c1_loopcut_instep_round_shape.jpg](../../docs/fusako_14_shoes_sandals_screenshots/05_c1_loopcut_instep_round_shape.jpg)
6. **足首への立ち上がりと幅調整**:
   - 足首側のエッジループを選択し、`E + Z` で上方へ押し出し。
   - `S + X` で足首の太さに合わせ、4点を選択して `F` キーで面を塞ぐ。
   - 最上部ループに `LoopTools > Relax` をかけて滑らかに整流。
   [📸 参考: 06_c1_extrude_ankle_sx_width.jpg](../../docs/fusako_14_shoes_sandals_screenshots/06_c1_extrude_ankle_sx_width.jpg)
7. **ソールへの食い込み膨らみ（`Alt + S`）**:
   - アッパー下端のすぐ上に `Ctrl + R` でループを追加し、`G + G` で下端へ寄せる。
   - 最下端ループを `Alt + S` で外側に膨らませ、靴底ソールへ布が食い込む立体的な接地感を表現。
   [📸 参考: 07_c1_alt_s_bulge_sole_embed.jpg](../../docs/fusako_14_shoes_sandals_screenshots/07_c1_alt_s_bulge_sole_embed.jpg)
8. **ペンギン足型（水かき形状）の成形**:
   - 退避しておいた靴底メッシュを再表示。
   - アノテーションツールでペンギンの水かき（3つ爪のギザギザ形状）を下書き。
   - ナイフ（`K`）や頂点移動で水かきのギザギザ形状へ成形し、不要な頂点を `J` で接続。
   [📸 参考: 08_c1_annotate_penguin_webbed_foot.jpg](../../docs/fusako_14_shoes_sandals_screenshots/08_c1_annotate_penguin_webbed_foot.jpg)
9. **厚底ソールの押し出し**:
   - 靴底の底面を選択し、`E + Z + Z`（グローバルZ方向）で地面の高さまで下方に押し出し。
   - 厚底のプラットフォームソールを形成。
   - `Shift + N` で面の法線を外側へ再計算。
   [📸 参考: 09_c1_extrude_thick_platform_sole.jpg](../../docs/fusako_14_shoes_sandals_screenshots/09_c1_extrude_thick_platform_sole.jpg)

---

### Chapter 2: 靴下（モコモコ・ギザギザ縁・履き口二重トリム）のモデリング（08:22〜16:04）

1. **サンダル上端からの靴下ベース立ち上げ**:
   - サンダルの上端ループを `Alt + 左クリック` で選択し、`Shift + D + Z` で上に複製。
   - `S` キーで少し拡大し、`LoopTools > Relax` で角を落として円形に整流。
   [📸 参考: 10_c2_duplicate_top_loop_sock_base.jpg](../../docs/fusako_14_shoes_sandals_screenshots/10_c2_duplicate_top_loop_sock_base.jpg)
2. **下方押し出しとモコモコ膨らみ成形**:
   - `E + Z` で下方に押し出し。
   - `Alt + S` で外側にボリューミーに膨らませ、足首を覆うモコモコした靴下のボリュームを作る。
   [📸 参考: 11_c2_extrude_down_alt_s_fluffy.jpg](../../docs/fusako_14_shoes_sandals_screenshots/11_c2_extrude_down_alt_s_fluffy.jpg)
3. **天面の受け口インセット・面張り**:
   - 最上部ループを選択し、`F` で面張り $\to$ `I` で内側へインセット。
   - `E` で下方に押し込んで足が入る受け口ソケットを形成。
   - 中間ループを `Ctrl + B` で面取りし、柔らかいクッション感を付与。
   [📸 参考: 12_c2_top_face_inset_extrude_socket.jpg](../../docs/fusako_14_shoes_sandals_screenshots/12_c2_top_face_inset_extrude_socket.jpg)
4. **裾ループの細分化（Subdivide）**:
   - ギザギザ縁を作る準備として、最下端ループとそのすぐ上のループを選択。
   - 右クリック `Subdivide`（細分化）を実行し、頂点数を倍増。
   [📸 参考: 13_c2_hem_subdivide_preparation.jpg](../../docs/fusako_14_shoes_sandals_screenshots/13_c2_hem_subdivide_preparation.jpg)
5. **チェッカー選択（Checker Deselect）**:
   - 最下端ループを一周選択した状態で、上部メニュー `Select > Checker Deselect` を実行。
   - 1つ飛ばしで頂点が選択されている状態を作る（中心線は避けるようOffsetを調整）。
   [📸 参考: 14_c2_checker_deselect_one_skip.jpg](../../docs/fusako_14_shoes_sandals_screenshots/14_c2_checker_deselect_one_skip.jpg)
6. **エッジスライドによるジグザグ縁の一発生成**:
   - 選択された1つ飛ばし頂点を、`G + G`（エッジスライド）で上方へスライド。
   - 均等で愛らしいジグザグの裾波形が一発で完成。
   [📸 参考: 15_c2_gg_slide_zigzag_hem_pattern.jpg](../../docs/fusako_14_shoes_sandals_screenshots/15_c2_gg_slide_zigzag_hem_pattern.jpg)
7. **多角形面の三角面化（Ctrl + T）**:
   - ギザギザ変形によって生じた五角形面を一周選択し、`Ctrl + T` を実行。
   - V字の三角面としてクリーンに整流。
   [📸 参考: 16_c2_ctrl_t_triangulate_v_crease.jpg](../../docs/fusako_14_shoes_sandals_screenshots/16_c2_ctrl_t_triangulate_v_crease.jpg)
8. **サンダル履き口の面ループ複製**:
   - サンダルアッパーの履き口面ループを選択し、`Shift + D` で複製 $\to$ `Alt + S` で内側へ凹ませて厚みの隙間を作成。
   [📸 参考: 17_c2_duplicate_sandal_cuff_alt_s.jpg](../../docs/fusako_14_shoes_sandals_screenshots/17_c2_duplicate_sandal_cuff_alt_s.jpg)
9. **Bridgeによる履き口二重トリム架橋**:
   - 外側ループと内側凹ませループを選択し、右クリック `LoopTools > Bridge` を実行。
   - ふっくらと折り返したリアルな布トリムを構築。
   [📸 参考: 18_c2_looptools_bridge_double_cuff.jpg](../../docs/fusako_14_shoes_sandals_screenshots/18_c2_looptools_bridge_double_cuff.jpg)
10. **`Individual Origins` による厚み幅スケーリング**:
    - トリムのエッジリングを選択し、ピボットポイントを `Individual Origins`（それぞれの原点）に設定。
    - `S` キーでスケールすることで、布の厚み幅を自在に微調整。
    [📸 参考: 19_c2_individual_origins_cuff_scale.jpg](../../docs/fusako_14_shoes_sandals_screenshots/19_c2_individual_origins_cuff_scale.jpg)

---

### Chapter 3: ペンギンの羽飾り（靴側面の立体パーツ）（16:05〜18:59）

1. **靴側面からの羽ベース面複製**:
   - 靴側面の面を選択し、`Shift + D + X` で外側に少し複製・分離。
   - `Vertex > Smooth Vertices` で角を丸め、流線形の羽のアウトラインを作成。
   [📸 参考: 20_c3_duplicate_side_faces_wings.jpg](../../docs/fusako_14_shoes_sandals_screenshots/20_c3_duplicate_side_faces_wings.jpg)
2. **羽の押し出し厚み付けと反り配置**:
   - `E` キーで外側へ厚みを押し出し。
   - 先端を `S` で少しすぼめ、全体を少し外側へ反らせる（靴本体と完全密着させず浮かせる）ことで、立体的な跳ね感を演出。
   - 靴の内側側面にも同様の手順で羽パーツを作成。
   [📸 参考: 21_c3_extrude_wing_thickness_curl.jpg](../../docs/fusako_14_shoes_sandals_screenshots/21_c3_extrude_wing_thickness_curl.jpg)

---

### Chapter 4: ポンポン（球体ファー飾り）のモデリング・対称化・仕上げ（19:00〜23:36）

1. **Cube + Subsurf1適用からの角ベベル面取り**:
   - `Shift + A > Mesh > Cube` を追加。
   - `Subdivision Surface`（レベル1）モディファイアを追加し、即座に `Ctrl + A` で適用。
   - 角のエッジをすべて選択し、`Ctrl + B` で面取り（ベベル）を適用して均等なケージを生成。
   [📸 参考: 22_c4_cube_subsurf1_apply_bevel.jpg](../../docs/fusako_14_shoes_sandals_screenshots/22_c4_cube_subsurf1_apply_bevel.jpg)
2. **`To Sphere` による真球化成形**:
   - 全選択（`A`）し、`Shift + Alt + S`（To Sphere）を押して数値 `1.0` を入力。
   - 極（ポール）の歪みがない完璧な球体ポンポンメッシュを完成。
   [📸 参考: 23_c4_to_sphere_pom_pom_shaping.jpg](../../docs/fusako_14_shoes_sandals_screenshots/23_c4_to_sphere_pom_pom_shaping.jpg)
3. **甲への配置・結合・対称化**:
   - ポンポンを `S` で縮小し、靴の甲の紐位置へ配置。
   - 靴オブジェクトと `Ctrl + J` で結合。
   - `Mirror` モディファイア（Clipping=ON）で左右両足に対称展開。
   - 靴から覗く足の指の角度や太さ（`S + Shift + Z`）を微調整し、靴・サンダル・ブーツ全体が完成。
   [📸 参考: 24_c4_pom_pom_placement_mirror_complete.jpg](../../docs/fusako_14_shoes_sandals_screenshots/24_c4_pom_pom_placement_mirror_complete.jpg)

---

## 4. プロシージャル・アドオン実装向けパラメトリック仕様

今後の自動生成スクリプト・アドオン化において制御すべきパラメータ：

| パラメータ名 | 推奨値 / 単位 | 説明 |
| :--- | :--- | :--- |
| `sole_length_margin` | 1.05〜1.10 | 足裏サイズに対する靴底の拡大率 |
| `inner_sole_inset` | 0.004〜0.008 m | 靴底からアッパーインナーソールへの `I` インセット量（コバ幅） |
| `platform_sole_thickness` | 0.025〜0.040 m | 厚底ソールの `E + Z + Z` 押し出し厚み |
| `sock_fluffy_bulge` | 0.010〜0.015 m | 靴下の `Alt + S` モコモコ膨らみ量 |
| `zigzag_amplitude` | 0.008〜0.012 m | `Checker Deselect` 頂点の `G + G` スライド移動量 |
| `cuff_bridge_thickness` | 0.004〜0.006 m | 履き口トリムの二重架橋厚み |
| `pom_pom_radius` | 0.015〜0.022 m | 甲のファー飾りポンポンの半径 |

---

## 5. 参考リソース

- 元動画: [YouTube - ふさこ氏 第14話](https://www.youtube.com/watch?v=KaTcr7DTKQc)
- 字幕テキスト: [fusako_14_subtitles_timestamped.txt](fusako_14_subtitles_timestamped.txt)
- 生字幕VTT: [fusako_14_subtitles_raw.ja.vtt](fusako_14_subtitles_raw.ja.vtt)
- スクリーンショット集カタログ: [README.md](../../docs/fusako_14_shoes_sandals_screenshots/README.md)
