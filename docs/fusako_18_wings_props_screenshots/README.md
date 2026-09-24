# ふさこ氏 第18話『羽根などの小物のモデリング（モデリング編最終回）』スクリーンショットカタログ

本ドキュメントは、ふさこ氏のBlender 3Dキャラクター制作チュートリアル第18話「羽根などの小物のモデリング〜初級から中級者向けチュートリアル〜」（34分46秒）の重要操作シーンを高解像度キャプチャした全26枚の画像カタログです。
モデリング編の最終回として、浮遊する羽根、猫のしっぽ、フード飾り（お花・リボン）、フードの曲面整理（Set Flow・V字リダクション）、首と体のトポロジー統合、ショルダーストラップのメッシュ化と服への割り合わせまでを網羅しています。

📖 **対応する詳細モデリング仕様書・操作手順書**:
- [2026-09-24_fusako_wings_props_18_steps.md](../../.agents/handoffs/2026-09-24_fusako_wings_props_18_steps.md)

---

## スクリーンショット一覧（全26枚）

| No | スクリーンショット（クリックで原寸表示） | タイムスタンプ | チャプター | モデリング操作・トポロジー解説・キー操作 |
|:---|:---|:---|:---|:---|
| 01 | [01_c1_circle_12verts_wing_profile.jpg](./01_c1_circle_12verts_wing_profile.jpg) | 00:00:25 | Ch.1 羽の輪郭円弧 | `Shift + A` > Circle（頂点数12）を追加、`R X 90` で正面向きに起立。羽の先端アタリに合わせてスケール調整。 |
| 02 | [02_c1_duplicate_arc_outline_merge.jpg](./02_c1_duplicate_arc_outline_merge.jpg) | 00:01:05 | Ch.1 羽の複数円弧配置とマージ | 円弧を `Shift + D` で複製し各羽先のカーブに配置。不要頂点を削除し、近接頂点を `M` でマージ、`F` でエッジ連結。 |
| 03 | [03_c1_outline_close_fill_inset.jpg](./03_c1_outline_close_fill_inset.jpg) | 00:02:45 | Ch.1 羽外周の面貼りとインセット | 外周ループを `F` で面貼りし、`I`（Inset Faces）で同心円状に内側へ面を差し込み。不要な内部面を削除して枠線を形成。 |
| 04 | [04_c1_gy_depth_step_ridge.jpg](./04_c1_gy_depth_step_ridge.jpg) | 00:03:55 | Ch.1 羽の段差・稜線立体化 | 内側の面を `G Y` で手前に引き出し、エッジを `Subdivide` して `J` キー（Join Vertices）で繋ぎ、羽の立体的な段差・稜線を成形。 |
| 05 | [05_c1_origin_mirror_y_thickness.jpg](./05_c1_origin_mirror_y_thickness.jpg) | 00:04:45 | Ch.1 Y軸ミラーによる厚み成形 | 端点頂点に3Dカーソルを合わせ原点移動（Origin to 3D Cursor）。`Mirror` モディファイア（Axis: Y, Clipping: ON）で前後対称に厚み化。 |
| 06 | [06_c1_ey_rim_extrude_alt_s_bulge.jpg](./06_c1_ey_rim_extrude_alt_s_bulge.jpg) | 00:05:35 | Ch.1 外周押し出しと丸み出し | 外周エッジを `E Y` で押し出してマチを作り、中央エッジを選択して `Alt + S`（Shrink/Fatten）でふっくらとした厚み・丸みを付与。 |
| 07 | [07_c1_auto_smooth_mark_sharp_ridges.jpg](./07_c1_auto_smooth_mark_sharp_ridges.jpg) | 00:07:45 | Ch.1 オートスムースとマークシャープ | `Shade Auto Smooth`（180°）を適用し、羽の稜線や外周の折り返しエッジに `Mark Sharp` を指定してクッキリとした陰影を保持。 |
| 08 | [08_c1_lattice_modifier_u3_setup.jpg](./08_c1_lattice_modifier_u3_setup.jpg) | 00:10:45 | Ch.1 ラティス（Lattice）の追加 | `Shift + A` > Lattice を追加し羽を覆うサイズに縮小。羽オブジェクトに `Lattice` モディファイアを追加し、Latticeプロパティで分割数 `U: 3` に設定。 |
| 09 | [09_c1_lattice_deformation_taper_twist.jpg](./09_c1_lattice_deformation_taper_twist.jpg) | 00:11:30 | Ch.1 ラティス変形による非破壊湾曲 | ラティスの編集モードで端の4頂点を選択し、`R Z` で回転および移動。羽のメッシュトポロジーを崩さずに、斜め後ろへ流れる美しい湾曲とパース変形を実現。 |
| 10 | [10_c1_head_mirror_floating_wings.jpg](./10_c1_head_mirror_floating_wings.jpg) | 00:12:35 | Ch.1 顔基準ミラーと浮遊配置 | ラティス適用後、羽に `Mirror` モディファイア（Mirror Object: `Head`）を追加。頭部両脇にフワッと浮遊する位置関係を確定。 |
| 11 | [11_c2_curve_bezier_tail_path.jpg](./11_c2_curve_bezier_tail_path.jpg) | 00:13:50 | Ch.2 カーブによる猫のしっぽ造形 | `Shift + A` > Curve > Bezierを追加。お尻から垂れ下がる滑らかなS字カーブの経路を敷設。 |
| 12 | [12_c2_tail_bevel_depth_resolution2.jpg](./12_c2_tail_bevel_depth_resolution2.jpg) | 00:15:05 | Ch.2 ベベル太さと8角形断面設定 | カーブプロパティで `Geometry > Bevel > Depth: 0.012`、`Resolution: 2`（断面8角形の軽量ローポリ管）を設定。服との干渉クリアランスを確保。 |
| 13 | [13_c2_backup_convert_to_mesh.jpg](./13_c2_backup_convert_to_mesh.jpg) | 00:15:40 | Ch.2 バックアップとしっぽメッシュ化 | 編集用カーブを `Shift + D` で複製しバックアップコレクションへ退避。本体を右クリック > `Convert to Mesh` でポリゴンメッシュ化。 |
| 14 | [14_c2_uv_sphere_tail_tip_snap.jpg](./14_c2_uv_sphere_tail_tip_snap.jpg) | 00:16:45 | Ch.2 先端UV球と面スナップ吸着 | `UV Sphere`（Segments: 8, Rings: 6, 半径: 0.012）を追加。`Snap: Face Project` ＋ `Align Rotation to Target` でしっぽ終端の傾きに完全吸着配置。 |
| 15 | [15_c2_tail_tip_bridge_set_flow.jpg](./15_c2_tail_tip_bridge_set_flow.jpg) | 00:17:50 | Ch.2 先端Bridge接合とSet Flow | しっぽ本体と球体を `Ctrl + J` 結合し、境界ループ同士を `LoopTools > Bridge` で接合。ループカット追加後に右クリック `Set Flow` で完璧な滑らか丸みを成形。 |
| 16 | [16_c3_circle_10verts_star_flower_base.jpg](./16_c3_circle_10verts_star_flower_base.jpg) | 00:18:50 | Ch.3 お花の星形ベース作成 | Circle（頂点数10）を追加、1頂点飛ばしで交互に選択し `S` キーで内側に縮小して星形を作成。 |
| 17 | [17_c3_flower_vertex_bevel_individual_origins.jpg](./17_c3_flower_vertex_bevel_individual_origins.jpg) | 00:19:20 | Ch.3 花弁の頂点ベベルと個別原点拡大 | `Ctrl + I` で反転し `Ctrl + Shift + B`（Vertex Bevel）で丸め。ピボットを `Individual Origins` に切り替えて各花弁の幅を広げ、自然な5枚花弁を成形。 |
| 18 | [18_c3_flower_inset_gz_core_extrude.jpg](./18_c3_flower_inset_gz_core_extrude.jpg) | 00:20:30 | Ch.3 花芯の立体化と厚み押し出し | `F` で面貼り後、`I` でインセット。中央面を `G Z` で上へ持ち上げて花芯の立体感を作り、全体を `E` で押し出して厚みメッシュ化。 |
| 19 | [19_c3_plane_extrude_flower_ribbon.jpg](./19_c3_plane_extrude_flower_ribbon.jpg) | 00:22:15 | Ch.3 リボン紐の板ポリゴン造形 | お花の編集モード内で `Plane` を追加し、`E` で下方向に押し出して2本の垂れリボン紐を作成。 |
| 20 | [20_c3_hood_flower_accessory_placement.jpg](./20_c3_hood_flower_accessory_placement.jpg) | 00:23:45 | Ch.3 フード飾り配置と顔基準Mirror | フードの側面に飾りを斜め配置。`Mirror` モディファイア（Mirror Object: `Head`）を追加して左右対称に配備。 |
| 21 | [21_c4_hood_set_flow_subdivide.jpg](./21_c4_hood_set_flow_subdivide.jpg) | 00:24:45 | Ch.4 フードのループ追加とSet Flow | フードの硬い部分に `Ctrl + R` でループカットを追加し、右クリック `Set Flow` を実行。手動調整なしで周囲の曲率に沿った滑らかなふくらみを自動補間。 |
| 22 | [22_c4_hood_v_reduction_rotate_edge.jpg](./22_c4_hood_v_reduction_rotate_edge.jpg) | 00:26:15 | Ch.4 V字リダクションとRotate Edge | 下の服と接続するため、不要エッジを `Dissolve Edges` して `Ctrl + T` で三角面化。`Rotate Edge CW` で対角線を回転させて綺麗なV字リダクションを構築。 |
| 23 | [23_c5_collection_hierarchy_cleanup.jpg](./23_c5_collection_hierarchy_cleanup.jpg) | 00:28:30 | Ch.5 コレクション整理と階層削除 | アウトライナーで `Accessories`, `Hair`, `Clothes`, `Body`, `Head` に整理。不要な手・足の一時コレクションを右クリック `Delete Hierarchy` で一括クリーンアップ。 |
| 24 | [24_c6_neck_body_topology_reduction.jpg](./24_c6_neck_body_topology_reduction.jpg) | 00:30:15 | Ch.6 首から体への頂点数リダクション | 首側（11頂点）と体側（7頂点）の差を解消するため、頭部との接合部上端を維持したまま、首の下側エッジをディゾルブして7頂点へスムーズに収束。 |
| 25 | [25_c6_neck_body_auto_merge_connect.jpg](./25_c6_neck_body_auto_merge_connect.jpg) | 00:31:00 | Ch.6 首と体の完全一体化マージ | 首と体を `Ctrl + J` で結合。スナップ先を `Vertex`、`Auto Merge: ON` にして、体の各頂点を首の対応頂点へスナップ移動して完全一体化。 |
| 26 | [26_c7_strap_convert_mesh_topology_match.jpg](./26_c7_strap_convert_mesh_topology_match.jpg) | 00:33:00 | Ch.7 ストラップメッシュ化と服の割り合わせ | ショルダーストラップのカーブを複製バックアップ後 `Convert to Mesh`。服のエッジループ位置に合わせてストラップの分割を整え、全モデリング工程完了！ |

---

## 技術要点・モデリングの極意（第18話・モデリング編総括）

1. **ラティス（Lattice）による非破壊パース変形**:
   - 平面上で綺麗にトポロジーを整えたメッシュ（羽や装飾品）に対し、直接頂点を回転・歪ませると四角面が崩れやすい。`Lattice` モディファイア（U:3）を噛ませてバウンディングケージごと曲げることで、美しいグリッドを保ったままダイナミックなパース感・湾曲を付与。
2. **カーブからメッシュ化と先端スフィア吸着**:
   - しっぽや触手など、均等な太さの管は `Curve Bezier`（Bevel Depth + Resolution 2）で非破壊作成。
   - メッシュ化後、先端の丸みは断面と同じ頂点数（8角形）の `UV Sphere`（Segments: 8）を面スナップ（Align Rotation）で吸着させ、`Bridge Edge Loops` ＋ `Set Flow` で繋ぐことで完全な真球キャップを接合。
3. **トポロジーリダクション（首11頂点 $\to$ 体7頂点）**:
   - 頭部との接合部（顔の輪郭線）を壊さないよう、上端の頂点ループはディゾルブせず、首の中段〜下段にかけてV字トポロジーで頂点数を削減。
   - `Auto Merge`（自動結合）をONにした頂点スナップで体側メッシュと瞬時に縫合。
4. **ウェイト追従を見据えたストラップの割り合わせ**:
   - ショルダーストラップをメッシュ化する際、下の衣服・胸元の分割ループと同じ位置にエッジを配置しておくことで、将来のボーンスキニング・ウェイト転送時に衣装とストラップが同期して美しく変形し、めり込みを防止。
