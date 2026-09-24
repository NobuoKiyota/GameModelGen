# ふさこ氏 第18話『羽根などの小物のモデリング（モデリング編最終回）』詳細操作手順・トポロジー仕様書

本ドキュメントは、3Dモデラー・ふさこ氏のキャラクターモデリング解説動画第18話「羽根などの小物のモデリング〜初級から中級者向けチュートリアル〜」（34分46秒）の詳細手順書である。
本話をもってキャラクターの全モデリング工程が完了となる。頭部両脇の浮遊羽根、猫のしっぽ（先端UV球スナップ）、フードの飾り（お花・リボン）、フードの曲面整理（Set Flow・V字リダクション）、コレクション階層整理、首と体のトポロジー統合（11頂点から7頂点へのリダクションとマージ）、ショルダーストラップのメッシュ化と服への割り合わせまでを詳細に記録する。

📸 **対応スクリーンショットカタログ**:
- [docs/fusako_18_wings_props_screenshots/README.md](../../docs/fusako_18_wings_props_screenshots/README.md)

---

## 目次
1. [Chapter 1: 浮遊する羽根のモデリングとラティス（Lattice）変形](#chapter-1-浮遊する羽根のモデリングとラティスlattice変形)
2. [Chapter 2: 猫のしっぽ（尻尾）のカーブ造形と先端球体スナップ接合](#chapter-2-猫のしっぽ尻尾のカーブ造形と先端球体スナップ接合)
3. [Chapter 3: フード飾り（5弁花・リボン紐）のモデリング](#chapter-3-フード飾り5弁花リボン紐のモデリング)
4. [Chapter 4: フードの曲面補間（Set Flow）とV字トポロジーリダクション](#chapter-4-フードの曲面補間set-flowとv字トポロジーリダクション)
5. [Chapter 5: コレクション整理と不要ヒエラルキーのクリーンアップ](#chapter-5-コレクション整理と不要ヒエラルキーのクリーンアップ)
6. [Chapter 6: 首と体のトポロジー統合（11頂点 $\to$ 7頂点マージ）](#chapter-6-首と体のトポロジー統合11頂点--7頂点マージ)
7. [Chapter 7: ショルダーストラップのメッシュ化と服の割り合わせ完成](#chapter-7-ショルダーストラップのメッシュ化と服の割り合わせ完成)
8. [トポロジー＆運用 Tips 総括](#トポロジー運用-tips-総括)

---

## Chapter 1: 浮遊する羽根のモデリングとラティス（Lattice）変形

### Step 1-1: 円弧（12頂点）による羽の輪郭ライン配置
- `Shift + S` > **Cursor to World Origin**（カーソルを原点に）。
- `Shift + A` > Mesh > **Circle**（Vertices: 12）を追加。
- `Tab` で編集モードに入り、`R X 90` で正面を向かせる。
- 下絵の羽の輪郭弧に合わせてスケールを縮小・配置。不要な下半分等の頂点を削除して弧を抽出。
[📸 参考: 01_c1_circle_12verts_wing_profile.jpg](../../docs/fusako_18_wings_props_screenshots/01_c1_circle_12verts_wing_profile.jpg)

### Step 1-2: 円弧の複製・羽先端のシルエット形成
- 弧を `L` でリンク選択し、`Shift + D` で複製して隣接する羽先のカーブ位置へ配置。
- 近接する端点頂点同士を選択し、`M` > **At Center** でマージ。
- 頂点間が不足している箇所は右クリック > **Subdivide** で頂点を追加し、`F` キーでエッジを繋いで均等な外周輪郭ループを完成。
[📸 参考: 02_c1_duplicate_arc_outline_merge.jpg](../../docs/fusako_18_wings_props_screenshots/02_c1_duplicate_arc_outline_merge.jpg)

### Step 1-3: 外周の面貼りとインセットによる段差境界作成
- 外周ループを全選択し、`F` キーで面を貼る。
- `I`（Inset Faces）で同心円状に内側へ面を差し込む。
- 中央の不要な面を削除（または内側に残す）し、羽の外縁フレームを形成。
[📸 参考: 03_c1_outline_close_fill_inset.jpg](../../docs/fusako_18_wings_props_screenshots/03_c1_outline_close_fill_inset.jpg)

### Step 1-4: 手前への引き出しと稜線トポロジー成形
- 内側の面やエッジを選択し、`G Y` で手前方向に引き出して立体的な段差を形成。
- エッジを右クリック > **Subdivide** で分割し、対向する頂点を `J` キー（Join Vertices）で繋ぎ、羽の中央を走るシャープな稜線（尾根）を構築。
[📸 参考: 04_c1_gy_depth_step_ridge.jpg](../../docs/fusako_18_wings_props_screenshots/04_c1_gy_depth_step_ridge.jpg)

### Step 1-5: 3Dカーソル原点移動と Y軸 Mirror による前後対称化
- 羽の先端（または根元）の頂点を選択し、`Shift + S` > **Cursor to Selected**。
- オブジェクトモードで右クリック > **Set Origin > Origin to 3D Cursor**。
- **Mirror** モディファイアを追加し、**Axis: Y**（XはOFF）、**Clipping: ON** に設定。前後対称な厚みメッシュを非破壊で生成。
[📸 参考: 05_c1_origin_mirror_y_thickness.jpg](../../docs/fusako_18_wings_props_screenshots/05_c1_origin_mirror_y_thickness.jpg)

### Step 1-6: 外周押し出し（E Y）と Alt + S による丸み出し
- 一旦ミラーをOFFにし、全体を `G Y` で少し手前にオフセットしてからミラーをONに戻してマチ（厚みの隙間）を作る。
- 外周エッジループを選択し、`E Y` で押し出して側面を塞ぐ。
- 内側のエッジを選択し、`Alt + S`（Shrink/Fatten）で法線方向にふっくらと膨らませて愛らしい丸みを持たせる。
[📸 参考: 06_c1_ey_rim_extrude_alt_s_bulge.jpg](../../docs/fusako_18_wings_props_screenshots/06_c1_ey_rim_extrude_alt_s_bulge.jpg)

### Step 1-7: オートスムースとマークシャープによる境界線の強調
- オブジェクトモードで右クリック > **Shade Auto Smooth**（Angle: 180°）。
- 編集モードで、羽の稜線や羽同士の分かれ目エッジを選択し、右クリック > **Mark Sharp** を適用。
- セル調・アニメ調のクッキリとした稜線ハイライトを維持。
[📸 参考: 07_c1_auto_smooth_mark_sharp_ridges.jpg](../../docs/fusako_18_wings_props_screenshots/07_c1_auto_smooth_mark_sharp_ridges.jpg)

### Step 1-8: ラティス（Lattice）の追加とバウンディング設定
- `Shift + A` > **Lattice** を追加し、羽全体を包み込むサイズに `S` で調整。
- 羽オブジェクトに **Lattice** モディファイアを追加し、作成したLatticeオブジェクトを指定。
- ラティスのオブジェクトデータプロパティで、分割数を **U: 3**（V: 2, W: 2）に設定。
[📸 参考: 08_c1_lattice_modifier_u3_setup.jpg](../../docs/fusako_18_wings_props_screenshots/08_c1_lattice_modifier_u3_setup.jpg)

### Step 1-9: ラティス制御点変形による非破壊湾曲・パース付け
- ラティスを選択して編集モードに入り、端の4頂点を選択。
- `R Z` で回転させ、`G` で斜め後ろへ引くことで、羽のメッシュグリッドを崩さずに先端が後方へ美しく流れる3次元カーブを非破壊付与。
[📸 参考: 09_c1_lattice_deformation_taper_twist.jpg](../../docs/fusako_18_wings_props_screenshots/09_c1_lattice_deformation_taper_twist.jpg)

### Step 1-10: 顔基準ミラーによる頭部両脇への浮遊配置
- ラティスモディファイアを適用（Apply）または保持。
- 羽オブジェクトに **Mirror** モディファイアを追加し、**Mirror Object: `Head`**（顔オブジェクト）を指定。
- 頭の両脇にフワフワと浮遊する左右対称な羽アクセサリーが完成。
[📸 参考: 10_c1_head_mirror_floating_wings.jpg](../../docs/fusako_18_wings_props_screenshots/10_c1_head_mirror_floating_wings.jpg)

---

## Chapter 2: 猫のしっぽ（尻尾）のカーブ造形と先端球体スナップ接合

### Step 2-1: ベジェカーブによるしっぽの経路敷設
- `Shift + S` > **Cursor to World Origin**。
- `Shift + A` > Curve > **Bezier** を追加。
- `R Z 90` で向きを合わせ、`S X 0` で一度直進化。
- 側面から見ながら、お尻から下に向かって垂れ下がる滑らかなS字ラインを制御点編集で敷設。
[📸 参考: 11_c2_curve_bezier_tail_path.jpg](../../docs/fusako_18_wings_props_screenshots/11_c2_curve_bezier_tail_path.jpg)

### Step 2-2: ベベル深度と解像度（8角形断面）の設定
- カーブデータプロパティ > **Geometry** > **Bevel** に移動。
- **Depth: 0.012**（しっぽの太さ、直径0.024m）、**Resolution: 2** に設定。
- これにより断面が正確に **8角形** の軽量ローポリチューブとなる。
- 上のワンピース衣装が揺れた際に干渉しないよう、服から少し離れたクリアランスを確保。
[📸 参考: 12_c2_tail_bevel_depth_resolution2.jpg](../../docs/fusako_18_wings_props_screenshots/12_c2_tail_bevel_depth_resolution2.jpg)

### Step 2-3: バックアップ複製とメッシュ変換
- 編集用カーブを `Shift + D` で複製し、`M` キーでバックアップ用コレクションへ移動して退避。
- 本体カーブを右クリック > **Convert to Mesh** でポリゴンメッシュに変換。
- 先端の終端エッジを選択し、`F` で面を貼る（スナップ用ターゲット面）。
[📸 参考: 13_c2_backup_convert_to_mesh.jpg](../../docs/fusako_18_wings_props_screenshots/13_c2_backup_convert_to_mesh.jpg)

### Step 2-4: UVスフィア（8×6）の作成と面スナップ吸着
- `Shift + A` > Mesh > **UV Sphere**（Segments: 8, Rings: 6, 半径: 0.012 = 直径0.024）を追加。
- スナップツール（`Shift + Tab`）をONにし、**Face Project**、**Align Rotation to Target: ON** に設定。
- UVスフィアをしっぽ先端の蓋面へドラッグ。しっぽの終端角度・傾きに完全自動追従して一発吸着。
[📸 参考: 14_c2_uv_sphere_tail_tip_snap.jpg](../../docs/fusako_18_wings_props_screenshots/14_c2_uv_sphere_tail_tip_snap.jpg)

### Step 2-5: Bridge接合と Set Flow による真球キャップ整形
- スナップ用の蓋面および球体の内側半分を削除。
- しっぽ本体と球体を選択して `Ctrl + J` で結合。
- 双方の境界エッジループ（8頂点同士）を選択し、`LoopTools > Bridge`（または Edge > Bridge Edge Loops）で隙間なく接合。
- 接続部にループカット `Ctrl + R` を追加し、右クリック > **Set Flow** を実行して完璧な球状丸みを成形。
[📸 参考: 15_c2_tail_tip_bridge_set_flow.jpg](../../docs/fusako_18_wings_props_screenshots/15_c2_tail_tip_bridge_set_flow.jpg)

---

## Chapter 3: フード飾り（5弁花・リボン紐）のモデリング

### Step 3-1: 10頂点サークルからの星形ベース成形
- `Shift + A` > Mesh > **Circle**（Vertices: 10）を追加。
- テンキー `7`（上面図）で、1頂点飛ばしで交互に5頂点を選択。
- `S` キーで内側に縮小し、綺麗な五角星形を作成。
[📸 参考: 16_c3_circle_10verts_star_flower_base.jpg](../../docs/fusako_18_wings_props_screenshots/16_c3_circle_10verts_star_flower_base.jpg)

### Step 3-2: 頂点ベベルと個別原点（Individual Origins）による花弁成形
- `Ctrl + I` で選択範囲を反転（外側の先端頂点を選択）。
- `Ctrl + Shift + B`（Vertex Bevel）で先端を丸める。
- ピボットポイントを **Individual Origins**（個々の原点）に切り替え、各花弁のエッジを個別にスケール拡大。
- 再度 `Ctrl + Shift + B` を軽くかけ、滑らかな5枚花弁の輪郭を完成。
[📸 参考: 17_c3_flower_vertex_bevel_individual_origins.jpg](../../docs/fusako_18_wings_props_screenshots/17_c3_flower_vertex_bevel_individual_origins.jpg)

### Step 3-3: 面張りとインセット・花芯の立体化・厚み押し出し
- 全選択して `F` で面を貼り、`I`（Inset Faces）で内側に面を差し込む。
- インセットした中央の面を選択し、`G Z` で上方向に持ち上げて立体的な花芯を形成。
- 全選択 `A` から `E` キーで下方向へ押し出し、適度な厚みを持たせる。
- 右クリック > **Shade Auto Smooth** を適用し、側面エッジがパッキリ立つよう調整。
[📸 参考: 18_c3_flower_inset_gz_core_extrude.jpg](../../docs/fusako_18_wings_props_screenshots/18_c3_flower_inset_gz_core_extrude.jpg)

### Step 3-4: Planeからの垂れリボン紐モデリング
- お花の編集モード内で `Shift + S` > **Cursor to Selected**。
- `Shift + A` > Mesh > **Plane** を追加し、`R X 90` で立てる。
- `E` キーで下方向に押し出し、途中にループカットを追加して軽くハの字に広がる2本のリボン紐（板ポリゴン）を作成。
- 面が裏返っている場合は `Shift + N` で法線方向を再計算。
[📸 参考: 19_c3_plane_extrude_flower_ribbon.jpg](../../docs/fusako_18_wings_props_screenshots/19_c3_plane_extrude_flower_ribbon.jpg)

### Step 3-5: フード側面への配置と顔基準Mirror
- お花とリボンをフードの耳元・側頭部付近へ移動・回転して配置。
- **Mirror** モディファイアを追加し、**Mirror Object: `Head`** を指定して左右対称に配備。
[📸 参考: 20_c3_hood_flower_accessory_placement.jpg](../../docs/fusako_18_wings_props_screenshots/20_c3_hood_flower_accessory_placement.jpg)

---

## Chapter 4: フードの曲面補間（Set Flow）とV字トポロジーリダクション

### Step 4-1: ループ追加と Set Flow による滑らか曲面化
- フードの角張っている部分に `Ctrl + R` でループカットを追加。
- 追加したエッジを選択した状態で右クリック > **Set Flow** を実行。
- 周囲の曲率（曲面フロー）を自動計算し、手動で引っ張ることなく自然で柔らかな丸みを即座に付与。
[📸 参考: 21_c4_hood_set_flow_subdivide.jpg](../../docs/fusako_18_wings_props_screenshots/21_c4_hood_set_flow_subdivide.jpg)

### Step 4-2: V字リダクションと Rotate Edge による頂点数整合
- フードの首回り・裾部分で、下の服と頂点数を合わせるためのトポロジー調整を実施。
- 不要な縦エッジを選択し、`X` > **Dissolve Edges** で溶解。
- 残った四角面を `Ctrl + T` で三角面化し、対角エッジを選択して右クリック > **Rotate Edge CW**（時計回りに回転）を実行。
- 頂点数を2本から1本へ減らす綺麗な「V字リダクション」を形成し、下の服と1対1で接続できる状態を構築。
[📸 参考: 22_c4_hood_v_reduction_rotate_edge.jpg](../../docs/fusako_18_wings_props_screenshots/22_c4_hood_v_reduction_rotate_edge.jpg)

---

## Chapter 5: コレクション整理と不要ヒエラルキーのクリーンアップ

### Step 5-1: アウトライナーのコレクション分類とゴミ削除
- アウトライナー（Outliner）で散乱したオブジェクトを機能別にコレクション分類:
  - `Head`（頭部、顔、目、眉）
  - `Hair`（前髪、後ろ髪、ツインテール、アホ毛）
  - `Body`（体、首、手、足）
  - `Clothes`（パーカー、フード、ドロワーズ、靴、サンダル）
  - `Accessories`（ポシェット、バッグ、羽、しっぽ、髪飾り）
  - `Backup`（カーブ変換前のバックアップ）
- モデリング検証用に使っていた「手」「足」の一時コレクションを選択し、右クリック > **Delete Hierarchy** で中身ごと一括完全消去。
[📸 参考: 23_c5_collection_hierarchy_cleanup.jpg](../../docs/fusako_18_wings_props_screenshots/23_c5_collection_hierarchy_cleanup.jpg)

---

## Chapter 6: 首と体のトポロジー統合（11頂点 $\to$ 7頂点マージ）

### Step 6-1: 首の下側トポロジーリダクション（11頂点 $\to$ 7頂点）
- これまで別オブジェクトだった首と体を一体化する。
- 体側の首接合部は **7頂点**、首オブジェクトは **11頂点** であり頂点数が合わない。
- 顔との接合部である首上端の頂点ループはディゾルブせず（隙間・黒ずみ防止）、首の下部エッジを選択して `Dissolve Edges`。
- `J` キーでV字状に対角を繋ぎ、首の最下部ループを正確に7頂点へ削減。
[📸 参考: 24_c6_neck_body_topology_reduction.jpg](../../docs/fusako_18_wings_props_screenshots/24_c6_neck_body_topology_reduction.jpg)

### Step 6-2: 頂点スナップ＋Auto Mergeによる首と体の完全一体化
- 首オブジェクトと体オブジェクトを選択し、`Ctrl + J` でオブジェクト結合。
- スナップツール（`Shift + Tab`）をONにし、スナップ先を **Vertex**（頂点）に設定。
- 3Dビューポート右上の **Auto Merge**（自動結合アイコン）をONにする。
- 体側の開口部頂点を首側の対応する各頂点へドラッグして重ねるだけで、瞬時にマージ結合完了。首と胴体が滑らかな1枚メッシュに統合される。
[📸 参考: 25_c6_neck_body_auto_merge_connect.jpg](../../docs/fusako_18_wings_props_screenshots/25_c6_neck_body_auto_merge_connect.jpg)

---

## Chapter 7: ショルダーストラップのメッシュ化と服の割り合わせ完成

### Step 7-1: ストラップの Convert to Mesh と服のエッジループ合わせ
- 第17話でカーブのまま保留していたショルダーストラップを `Shift + D` で複製し、`Backup` コレクションへ退避。
- 本体カーブを右クリック > **Convert to Mesh** でポリゴンメッシュに変換。
- 編集モードで、下のパーカー・胸元のエッジループとストラップのエッジ位置が一致するように頂点をスライド（`G G`）。
- 将来のスキニング・ボーンウェイト設定時に、服とストラップが完全に同期して美しく曲がり、めり込みや剥がれが起きないトポロジーを確立。
- 全身のシルエットを多角的に点検し、**全モデリング工程がここに完全完了！**
[📸 参考: 26_c7_strap_convert_mesh_topology_match.jpg](../../docs/fusako_18_wings_props_screenshots/26_c7_strap_convert_mesh_topology_match.jpg)

---

## トポロジー＆運用 Tips 総括

| 項目 | テクニック / ショートカット | 効能・ゲームモデルへのメリット |
|:---|:---|:---|
| **ラティス変形（Lattice）** | `Lattice` モディファイア（U:3） | メッシュグリッドを崩さずに湾曲・パースを非破壊付与。 |
| **真球キャップ接合** | 8角形管 $\to$ 8セグメント `UV Sphere` $\to$ `Bridge` $\to$ `Set Flow` | しっぽ・触手等の先端を破綻なく完全な真球で塞ぐ。 |
| **星形花弁成形** | 10頂点サークル $\to$ 1点飛ばし `S` $\to$ `Ctrl + Shift + B` $\to$ `Individual Origins` | 均等で愛らしいアニメ調5弁花を高速・正確に成形。 |
| **曲面自動補間（Set Flow）** | ループ追加 $\to$ 右クリック `Set Flow` | 周囲の曲率に沿った丸みを自動計算。手動頂点移動の手間を削減。 |
| **トポロジーリダクション** | `Dissolve Edges` $\to$ `Ctrl + T` $\to$ `Rotate Edge CW` | 頂点数の異なるパーツ（首11頂点 $\to$ 体7頂点等）を四角面主体のV字接続で綺麗に縫合。 |
| **ウェイト追従エッジ合わせ** | 重なり合う小物メッシュのエッジを下の服のエッジループ位置に揃える | スキニング時のウェイト転送（Data Transfer）精度を極大化し、アニメーション時のめり込みを防止。 |
