# ふさこ氏『Blenderでキャラクターモデル制作！15 | ヘアアクセのモデリング』詳細操作手順書

## 1. 概要・メタデータ

- **動画タイトル**: 『Blenderでキャラクターモデル制作！15 | ヘアアクセのモデリング 〜初級から中級者向けチュートリアル〜』
- **URL**: https://www.youtube.com/watch?v=4xKfONOkV5k
- **動画長**: 17分46秒（1066秒）
- **公開日**: 2023年6月2日
- **対象工程**:
  - Chapter 1: ツインテールリボンのモデリング・顔基準Mirror対称化（00:00〜03:40）
  - Chapter 2: パッチンどめ（ヘアピン）の板金モデリング・ラティス曲面変形（03:40〜09:39）
  - Chapter 3: お花（フラワーアクセサリー）のEmpty+Array放射状円形配列（09:40〜12:34）
  - Chapter 4: おにぎり（三角形センターパーツ）の作成・お花結合・厚み付け（12:35〜15:39）
  - Chapter 5: パッチンどめ・お花の親子付け（Ctrl+P）・Alt+Dリンク配置・コレクション整理（15:40〜17:46）
- **主要モディファイア**: Subdivision Surface（レベル1確定適用）、Mirror（Mirror Object指定）、Solidify（厚み付け）、Lattice（ラティス変形）、Array（Object Offset有効）
- **活用アドオン**: AutoMirror, LoopTools（Relax）, Copy Attributes Menu
- **スクリーンショット集フォルダ**: [docs/fusako_15_hair_accessories_screenshots/](../../docs/fusako_15_hair_accessories_screenshots/)
- **画像カタログ**: [docs/fusako_15_hair_accessories_screenshots/README.md](../../docs/fusako_15_hair_accessories_screenshots/README.md)

---

## 2. 核心トポロジー・アクセサリーモデリングの黄金律

1. **顔基準の左右対称配置（`Mirror Object: Head`）**:
   - リボンのように左右のツインテール根元など、原点から離れた位置にある装飾品は、オブジェクト自体の原点を結び目に置きつつ、`Mirror` モディファイアの `Mirror Object` に顔（`Head`）を指定する。これにより、リボン単体の位置や角度をローカルで自由に編集しながら、左右完全対称に頭部へ配置できる。
2. **頂点ベベル（`Shift + Ctrl + B`）による板金・プレートパーツの角丸め**:
   - パッチン留めやおにぎり型パーツのように、2Dプレートから開始する小物は、角の頂点を選択して `Shift + Ctrl + B`（頂点ベベル）で角を落とす。ポリゴン数を最小限（数点〜十数点）に抑えたまま、工業製品やアクセサリー特有の滑らかなR面を高速生成できる。
3. **ラティス（`Lattice`）による非破壊カーブ曲げ**:
   - 金属や樹脂の薄いヘアピンを直接頂点移動で曲げると、歪みや厚みの不均一が生じやすい。`U=3`（中央に1本ループ）のラティスを作成して `Lattice` モディファイアを付与し、ラティスの中央頂点を `G + Z` で持ち上げることで、平らなメッシュをいつでも非破壊で頭皮・髪の曲面にジャストフィットさせられる。
4. **`Empty` ＋ `Array (Object Offset)` による幾何学的放射状配列**:
   - お花の花びらのように等角度で回転配置するパーツは、ワールド原点に `Empty（Plain Axes）` を追加し、花びらに `Array` モディファイア（`Relative Offset` OFF、`Object Offset` ON、エンプティ指定）をかける。エンプティを `R Z (360 / N)°`（例: 5枚なら72度）回転させることで、完全に均等で幾何学的に正確な放射状配列を即座に構築可能。
5. **親子付け（`Ctrl + P > Keep Transform`）と `Alt + D` リンク複製**:
   - 複数パーツ（クリップ・お花・ラティス）で構成されるアクセサリーは、メインとなるパーツ（お花）を親にして `Ctrl + P > Object (Keep Transform)` でまとめる。配置時は `Alt + D` でリンク複製することで、メッシュデータを共有したまま複数箇所（前髪、サイド等）に配置でき、片方を修正すれば全箇所に即時自動反映される。

---

## 3. チャプター別・詳細操作手順

### Chapter 1: ツインテールリボンのモデリング・対称化（00:00〜03:40）

1. **リボン結び目の追加**:
   - `Shift + A > Mesh > Cube` を追加。
   - `S` キーでリボンの結び目サイズまで大幅に縮小し、ツインテール根元の位置へ移動。
   - `Ctrl + 1` で `Subdivision Surface`（レベル1）を追加。
   [📸 参考: 01_c1_cube_subsurf1_ribbon_knot.jpg](../../docs/fusako_15_hair_accessories_screenshots/01_c1_cube_subsurf1_ribbon_knot.jpg)
2. **リボンの羽（ループ）の立ち上げ**:
   - 結び目メッシュを編集モードで `Shift + D` 複製し、`G + X` で外側に移動。
   - `R X 45°` で斜めに回転させ、`S` で大きく拡大。
   - 結び目と重なる端点をマージし、外側へ向けて `E + X` で羽を押し出し。
   [📸 参考: 02_c1_rx45_ribbon_wing_extrude.jpg](../../docs/fusako_15_hair_accessories_screenshots/02_c1_rx45_ribbon_wing_extrude.jpg)
3. **内側不要面の削除**:
   - 羽の内部に埋まる不要な面を選択し、`X > Faces` で削除。
   - `S + Z` で縦幅を広げ、ふっくらとしたリボンの膨らみを作成。
   [📸 参考: 03_c1_ex_extrude_delete_inner_faces.jpg](../../docs/fusako_15_hair_accessories_screenshots/03_c1_ex_extrude_delete_inner_faces.jpg)
4. **Subsurf確定適用とAutoMirror**:
   - 外形が決まったら、`Subdivision Surface` モディファイアを `Ctrl + A` で確定適用。
   - `AutoMirror` を実行してX軸対称化し、綺麗なリボン結び目と羽を完成。
   - 右クリック `Shade Smooth` を適用。
   [📸 参考: 04_c1_apply_subsurf_automirror_symmetry.jpg](../../docs/fusako_15_hair_accessories_screenshots/04_c1_apply_subsurf_automirror_symmetry.jpg)
5. **顔基準Mirrorモディファイアの追加**:
   - オブジェクトモードでリボンに `Mirror` モディファイアを追加。
   - `Mirror Object` のスポイトで顔オブジェクト（`Head`）を選択。
   - 左右両サイドのツインテール根元に完全対称配置。
   [📸 参考: 05_c1_mirror_face_target_twintail_align.jpg](../../docs/fusako_15_hair_accessories_screenshots/05_c1_mirror_face_target_twintail_align.jpg)

---

### Chapter 2: パッチンどめ（ヘアピン）の板金・ラティス曲面変形（03:40〜09:39）

1. **平面ベースと三角形シルエット成形**:
   - `Shift + A > Mesh > Plane` を追加。テンキー7（真上ビュー）に切り替え。
   - `S` で縮小、`S + Y` で奥行きを狭める。
   - `Ctrl + R` で中央に縦ループを追加し、右端の頂点を `S + Y` で絞り込んで先細りの三角形シルエットを形成。
   [📸 参考: 06_c1_plane_sy_scale_triangle_silhouette.jpg](../../docs/fusako_15_hair_accessories_screenshots/06_c1_plane_sy_scale_triangle_silhouette.jpg)
2. **頂点ベベル（Shift + Ctrl + B）による角丸め**:
   - 角の頂点を選択し、`Shift + Ctrl + B`（頂点ベベル）を実行。
   - パッチン留め特有の丸みを帯びた角を形成。
   [📸 参考: 07_c2_vertex_bevel_round_corners.jpg](../../docs/fusako_15_hair_accessories_screenshots/07_c2_vertex_bevel_round_corners.jpg)
3. **インセット（I）と開口枠作成**:
   - 全選択（`A`）し、`I` キーで内側へインセット。
   - 右端の頂点同士を `Merge at Center` で結合。
   - 中央の内側の面を `X > Faces` で削除し、外枠フレームを残す。
   [📸 参考: 08_c2_inset_delete_inner_face_frame.jpg](../../docs/fusako_15_hair_accessories_screenshots/08_c2_inset_delete_inner_face_frame.jpg)
4. **ピン足の押し出しと立体オフセット**:
   - 左端の辺を選択し、`E + X` で内側へ押し出し。
   - `G + Z` で少し下方にオフセットし、髪を挟む金属板の重なり段差を造形。
   [📸 参考: 09_c2_ex_extrude_pin_gz_offset.jpg](../../docs/fusako_15_hair_accessories_screenshots/09_c2_ex_extrude_pin_gz_offset.jpg)
5. **`Solidify` モディファイアによる厚み付け**:
   - オブジェクトモードで `Solidify` モディファイアを追加。
   - `Thickness: 0.002m` を設定し、薄い板金の厚みを付与。
   [📸 参考: 10_c2_solidify_clip_thickness.jpg](../../docs/fusako_15_hair_accessories_screenshots/10_c2_solidify_clip_thickness.jpg)
6. **ラティス（Lattice）のセットアップ**:
   - `Shift + A > Lattice` を追加。パッチン留めを覆うサイズに `S` で拡大。
   - オブジェクトデータプロパティで `Resolution U` を **3** に設定（中央に1本分割線が入る）。
   [📸 参考: 11_c2_add_lattice_u3_setup.jpg](../../docs/fusako_15_hair_accessories_screenshots/11_c2_add_lattice_u3_setup.jpg)
7. **ラティスによる曲面カーブ曲げ**:
   - パッチン留めに `Lattice` モディファイアを追加し、作成したラティスオブジェクトを指定。
   - ラティスの編集モードで中央の頂点を選択し、`G + Z` で上方に持ち上げる。
   - パッチン留めが髪の曲面にフィットする美しい弓形カーブに滑らかに変形。
   [📸 参考: 12_c2_lattice_modifier_gz_curve_bend.jpg](../../docs/fusako_15_hair_accessories_screenshots/12_c2_lattice_modifier_gz_curve_bend.jpg)
8. **中央スリット開口とマークシャープ**:
   - パッチン留め中央に `Ctrl + R` でループ追加 $\to$ `Ctrl + B` で幅を広げ、面を削除してスリット穴を開口。
   - 側面エッジに `Ctrl + E > Mark Sharp` を付与し、`Auto Smooth: 180°` で側面をくっきりシャープ描画。
   [📸 参考: 13_c2_clip_hole_cutout_mark_sharp.jpg](../../docs/fusako_15_hair_accessories_screenshots/13_c2_clip_hole_cutout_mark_sharp.jpg)

---

### Chapter 3: お花（フラワーアクセサリー）の放射状円形配列（09:40〜12:34）

1. **花びら1枚のベースサークル**:
   - `Shift + A > Mesh > Circle`（頂点数8）を追加。
   - `S` で縮小し、花びら1枚の卵形形状に成形して `G + Y` でオフセット配置。
   [📸 参考: 14_c3_circle_8verts_petal_base.jpg](../../docs/fusako_15_hair_accessories_screenshots/14_c3_circle_8verts_petal_base.jpg)
2. **エンプティの追加とArray Object Offset**:
   - 3Dカーソルを原点に置き、`Shift + A > Empty > Plain Axes` を追加。
   - 花びらメッシュに `Array` モディファイアを追加。
   - `Relative Offset` のチェックを外し、`Object Offset` をオンにして追加したエンプティを指定。
   [📸 参考: 15_c3_add_empty_array_object_offset.jpg](../../docs/fusako_15_hair_accessories_screenshots/15_c3_add_empty_array_object_offset.jpg)
3. **エンプティ72度回転による5枚配列**:
   - `Array` の `Count` を **5** に設定。
   - エンプティを選択し、`R Z 72°`（`360 / 5`）回転。
   - 5枚の花びらが均等に並んだ美しいフラワー形状が自動生成される。
   [📸 参考: 16_c3_rz_72deg_array_5petals_flower.jpg](../../docs/fusako_15_hair_accessories_screenshots/16_c3_rz_72deg_array_5petals_flower.jpg)
4. **根元マージとぷっくりインセット成形**:
   - 3Dカーソル中心で花びらの根元頂点を `S 0` で中心に揃え、`Merge by Distance` で溶接。
   - 全選択 `F` で面張り $\to$ `I` で内側へインセット $\to$ `G + Z` で少し持ち上げ、ふっくらした立体感のある花びらを造形。
   [📸 参考: 17_c3_s0_merge_inset_bulge_petals.jpg](../../docs/fusako_15_hair_accessories_screenshots/17_c3_s0_merge_inset_bulge_petals.jpg)

---

### Chapter 4: おにぎりパーツ作成・お花結合・厚み付け（12:35〜15:39）

1. **3頂点サークルとおにぎりベース**:
   - `Shift + A > Mesh > Circle`（頂点数3）を追加。
   - 右クリック `Subdivide`（細分化）を実行し、`Smoothness` を調整して角の丸い正三角形（おにぎり型）ベースを作成。
   [📸 参考: 18_c4_circle_3verts_subdivide_triangle.jpg](../../docs/fusako_15_hair_accessories_screenshots/18_c4_circle_3verts_subdivide_triangle.jpg)
2. **頂点ベベルとおにぎり立体化**:
   - 端の3頂点を選択し、`Shift + Ctrl + B` で角を丸める。
   - `F` で面張り $\to$ `I` でインセット $\to$ `Merge at Center` で中心にマージ。
   - お花の中央の高さに配置。
   [📸 参考: 19_c4_vertex_bevel_inset_center_part.jpg](../../docs/fusako_15_hair_accessories_screenshots/19_c4_vertex_bevel_inset_center_part.jpg)
3. **Array確定・おにぎり結合・Solidify**:
   - 花びらの `Array` モディファイアを `Ctrl + A` で確定適用。
   - おにぎりパーツとお花を選択し、`Ctrl + J` で結合。
   - `Solidify` モディファイアを追加して厚みを付与。
   - `Shade Auto Smooth` でエッジを綺麗に整流。
   [📸 参考: 20_c4_apply_array_join_solidify_flower.jpg](../../docs/fusako_15_hair_accessories_screenshots/20_c4_apply_array_join_solidify_flower.jpg)

---

### Chapter 5: 親子付け・リンク配置・コレクション整理（15:40〜17:46）

1. **サイズ合わせとスケール調整**:
   - パッチン留めとお花、ラティスを選択し、キャラクターの頭部・下絵に合わせた大きさに `S` でスケール調整。
   [📸 参考: 21_c5_align_clip_flower_lattice_scale.jpg](../../docs/fusako_15_hair_accessories_screenshots/21_c5_align_clip_flower_lattice_scale.jpg)
2. **親子付け（Ctrl + P > Keep Transform）**:
   - ラティス、パッチン留め、お花の順に選択（お花がアクティブ親）。
   - `Ctrl + P > Object (Keep Transform)` を実行。
   - お花を移動・回転・スケールするだけで、クリップとラティスが完全に一体となって追従する構造を構築。
   [📸 参考: 22_c5_ctrl_p_keep_transform_parenting.jpg](../../docs/fusako_15_hair_accessories_screenshots/22_c5_ctrl_p_keep_transform_parenting.jpg)
3. **髪への吸着配置とAlt+Dリンク複製**:
   - 前髪の毛束表面にふんわり乗るように配置。
   - 全体を選択し、`Alt + D` でリンク複製。
   - 2個目のアクセサリーとして反対側のサイドヘアや角度を変えた位置に配置（メッシュデータを共有しているため容量削減＆一括修正が可能）。
   [📸 参考: 23_c5_alt_d_linked_duplicate_bangs_placement.jpg](../../docs/fusako_15_hair_accessories_screenshots/23_c5_alt_d_linked_duplicate_bangs_placement.jpg)
4. **Accessoriesコレクションへの整理**:
   - アウトライナーで新コレクション `Accessories` を作成。
   - リボン、パッチン留め、お花、ラティスをすべて `M` キーで新コレクションへ移動・格納し、整理完了。
   [📸 参考: 24_c5_accessories_collection_organize_complete.jpg](../../docs/fusako_15_hair_accessories_screenshots/24_c5_accessories_collection_organize_complete.jpg)

---

## 4. プロシージャル・アドオン実装向けパラメトリック仕様

今後の自動生成スクリプト・アドオン化において制御すべきパラメータ：

| パラメータ名 | 推奨値 / 単位 | 説明 |
| :--- | :--- | :--- |
| `ribbon_wing_angle` | 40〜50 deg | リボンの羽のX軸回転角度 |
| `ribbon_wing_scale` | 1.8〜2.4倍 | 結び目に対する羽の拡大比率 |
| `clip_length` | 0.04〜0.06 m | パッチン留めの全長 |
| `clip_width` | 0.015〜0.022 m | パッチン留めの最大幅 |
| `clip_solidify_thickness` | 0.0015〜0.0025 m | パッチン留めの板金厚み |
| `lattice_bend_z` | 0.005〜0.010 m | ラティス中央頂点のGZ持ち上げ量（反り曲率） |
| `flower_petal_count` | 5 | お花の花びら枚数（回転角度 = `360 / petal_count`） |
| `flower_solidify_thickness` | 0.002〜0.004 m | お花パーツの厚み |

---

## 5. 参考リソース

- 元動画: [YouTube - ふさこ氏 第15話](https://www.youtube.com/watch?v=4xKfONOkV5k)
- 字幕テキスト: [fusako_15_subtitles_timestamped.txt](fusako_15_subtitles_timestamped.txt)
- 生字幕VTT: [fusako_15_subtitles_raw.ja.vtt](fusako_15_subtitles_raw.ja.vtt)
- スクリーンショット集カタログ: [README.md](../../docs/fusako_15_hair_accessories_screenshots/README.md)
