# ふさこ氏 第17話『ポーチ・バッグのモデリング』スクリーンショットカタログ

本ドキュメントは、ふさこ氏のBlender 3Dキャラクター制作チュートリアル第17話「ポーチ・バッグのモデリング」（16分58秒）の重要操作シーンを高解像度キャプチャした全22枚の画像カタログです。

📖 **対応する詳細モデリング仕様書・操作手順書**:
- [2026-09-24_fusako_bag_pouch_17_steps.md](../../.agents/handoffs/2026-09-24_fusako_bag_pouch_17_steps.md)

---

## スクリーンショット一覧（全22枚）

| No | スクリーンショット（クリックで原寸表示） | タイムスタンプ | チャプター | モデリング操作・トポロジー解説・キー操作 |
|:---|:---|:---|:---|:---|
| 01 | [01_c1_circle_16verts_rx90_bag_base.jpg](./01_c1_circle_16verts_rx90_bag_base.jpg) | 00:00:15 | Ch.1 バッグ前面ベース | `Shift + A` > Mesh > Circle（頂点数16、フィルタイプNothing）を配置。`R X 90` で立ててバッグ本体の前面形状を作成。 |
| 02 | [02_c1_inset_concentric_handle_width.jpg](./02_c1_inset_concentric_handle_width.jpg) | 00:00:50 | Ch.1 持ち手/耳の幅設定 | `F` で面貼り後、`I`（Inset Faces）で同心円状に内側へ面を差し込み、持ち手・耳パーツの基本幅を設定。 |
| 03 | [03_c1_subdivide_v_rip_ez_handle_extrude.jpg](./03_c1_subdivide_v_rip_ez_handle_extrude.jpg) | 00:01:30 | Ch.1 耳/持ち手の切り離し・押し出し | 外周上部のエッジを選択し、右クリック `Subdivide` で頂点を追加。`V` キーで切り離し（Rip）、`E Z` で上方向に押し出して持ち手・耳の骨組みを作成。 |
| 04 | [04_c1_vertex_bevel_round_quad_cleanup.jpg](./04_c1_vertex_bevel_round_quad_cleanup.jpg) | 00:01:50 | Ch.1 頂点ベベルと四角面化 | 角の頂点を選択し `Ctrl + Shift + B`（Vertex Bevel）で丸みを付与。`J` キー（Join Vertices）で対角を繋ぎ、多角形面をすべて四角形（Quad）にトポロジー整理。 |
| 05 | [05_c1_auto_smooth_mark_sharp_edges.jpg](./05_c1_auto_smooth_mark_sharp_edges.jpg) | 00:03:00 | Ch.1 オートスムースとシャープ指定 | オブジェクトを右クリック `Shade Smooth`。法線設定で `Auto Smooth`（30°〜60°）を有効化し、角エッジに右クリック `Mark Sharp` を指定してシャープな輪郭を保持。 |
| 06 | [06_c1_circle_12verts_inset_leaf_flap.jpg](./06_c1_circle_12verts_inset_leaf_flap.jpg) | 00:03:50 | Ch.1 フラップ（葉っぱ）ベース | 新規メッシュとしてCircle（頂点数12）を追加。`S X` で扁平化し、下部頂点を尖らせて葉っぱ形状のフラップを作成。`I` で同心円状にインセット。 |
| 07 | [07_c2_flap_placement_local_scaling.jpg](./07_c2_flap_placement_local_scaling.jpg) | 00:04:40 | Ch.2 フラップ配置とローカル変形 | フラップパーツをバッグ前面の所定位置に配置。トランスフォーム座標系を `Local` に切り替え、傾きに沿って拡縮・移動。 |
| 08 | [08_c2_subdivide_alt_s_flap_bulge.jpg](./08_c2_subdivide_alt_s_flap_bulge.jpg) | 00:06:05 | Ch.2 フラップの厚みと膨らみ出し | 内部エッジにループカット `Ctrl + R` を追加し、中央の頂点を選択して `Alt + S`（Shrink/Fatten：法線方向拡縮）でふっくらとした立体感を付与。 |
| 09 | [09_c2_duplicate_looptools_bridge_double_layer.jpg](./09_c2_duplicate_looptools_bridge_double_layer.jpg) | 00:06:20 | Ch.2 2重フラップとブリッジ | フラップを `Shift + D` で奥側に複製。外周エッジ同士を選択し、`LoopTools > Bridge`（またはエッジメニューの Bridge Edge Loops）で側面を塞ぎ厚みメッシュを形成。 |
| 10 | [10_c2_ctrl_j_join_flap_mark_sharp.jpg](./10_c2_ctrl_j_join_flap_mark_sharp.jpg) | 00:07:05 | Ch.2 フラップ結合とエッジシャープ | フラップと前面パーツを選択して `Ctrl + J` でオブジェクト結合。輪郭のエッジに `Mark Sharp` を適用し、スムースシェーディング時の意図しない影の回り込みを防止。 |
| 11 | [11_c2_cube_subsurf1_feet_placement.jpg](./11_c2_cube_subsurf1_feet_placement.jpg) | 00:07:50 | Ch.2 底部スタッズ/底鋲の作成 | Cubeを配置し、`Subdivision Surface`（レベル1）を適用。底面に小さく配置し、左右対称（`Mirror`）でバッグの底鋲（Feet）を作成。 |
| 12 | [12_c2_ey_depth_extrude_back_inset_seal.jpg](./12_c2_ey_depth_extrude_back_inset_seal.jpg) | 00:09:15 | Ch.2 バッグ奥行き押し出しと背面密閉 | 前面外周エッジ全選択 `Alt + Click` から `E Y` で後ろ方向へ押し出してマチ（奥行き）を形成。背面側エッジを `F` で面貼りし、`I` でインセットして均等な四角形グリッドで塞ぐ。 |
| 13 | [13_c3_cube_zipper_slider_modeling.jpg](./13_c3_cube_zipper_slider_modeling.jpg) | 00:10:10 | Ch.3 ジッパースライダー本体造形 | Cubeからモデリング開始。テーパー（細身化）と上部のループカット、貫通穴のブーリアン/手動押し出しでスライダー（金具本体）を小型ローポリで作成。 |
| 14 | [14_c3_zipper_pull_plate_extrude.jpg](./14_c3_zipper_pull_plate_extrude.jpg) | 00:10:45 | Ch.3 引き手（プルタブ）の作成 | 円柱またはCubeから細長い長方形プレートを作成。上部にリング穴を開け、スライダーの金具に通るように配置。 |
| 15 | [15_c3_face_snapping_align_rotation_target.jpg](./15_c3_face_snapping_align_rotation_target.jpg) | 00:11:15 | Ch.3 面スナップと法線自動追従 | スナップ設定を `Face Project`（面）、`Align Rotation to Target`（ターゲットに回転を整列）をON。ジッパー金具をバッグ側面の曲面にドラッグするだけで、面の法線角度に完全追従して一発配置。 |
| 16 | [16_c3_ctrl_p_parenting_zipper_to_bag.jpg](./16_c3_ctrl_p_parenting_zipper_to_bag.jpg) | 00:12:00 | Ch.3 金具の親子付け（Parenting） | ジッパー金具を選択後、バッグ本体をアクティブ選択（最後に選択）し、`Ctrl + P` > `Keep Transform`（トランスフォーム維持で親子付け）。後からのバッグ位置移動に自動追従させる。 |
| 17 | [17_c3_pochette_collision_avoidance_tweak.jpg](./17_c3_pochette_collision_avoidance_tweak.jpg) | 00:12:45 | Ch.3 16話ペンギンポシェットとの干渉回避 | 前話（16話）で作成したペンギンポシェットと重ならないよう、腰の反対側（あるいは高さをオフセット）へ配置・サイズ微調整。全体のシルエットバランスを確認。 |
| 18 | [18_c4_curve_bezier_shoulder_strap_extrude.jpg](./18_c4_curve_bezier_shoulder_strap_extrude.jpg) | 00:13:30 | Ch.4 カーブによるショルダーストラップ | `Shift + A` > Curve > Bezierを追加。プロパティの `Geometry > Extrude` で幅を持たせ、肩から胴体へ這わせる非破壊ストラップを作成。 |
| 19 | [19_c4_ctrl_t_curve_tilt_alignment.jpg](./19_c4_ctrl_t_curve_tilt_alignment.jpg) | 00:14:00 | Ch.4 カーブ傾き（Tilt）補正 | カーブの各制御点を選択し、`Ctrl + T`（Tilt）で回転角度を微調整。ストラップが衣服・パーカーの表面にぴったり密着するように面の向きを合わせる。 |
| 20 | [20_c4_switch_direction_prevent_twist.jpg](./20_c4_switch_direction_prevent_twist.jpg) | 00:14:50 | Ch.4 カーブ方向反転による捻れ解消 | 【重要Tips】カーブハンドル編集時に全体が不意にクルクル回転してしまうバグ挙動が発生した場合、カーブ全選択 `A` から右クリック > `Switch Direction`（方向反転）を実行して捻れを即座に解消。 |
| 21 | [21_c4_hide_hood_hair_back_strap_path.jpg](./21_c4_hide_hood_hair_back_strap_path.jpg) | 00:15:30 | Ch.4 背面ストラップの経路とフード非表示 | フードや後ろ髪を一時非表示（`H`）にし、背中側のストラップ経路が背中のメッシュに埋まらず、かつ浮きすぎないよう制御点を配置。 |
| 22 | [22_c4_under_pochette_shoulder_bag_complete.jpg](./22_c4_under_pochette_shoulder_bag_complete.jpg) | 00:16:30 | Ch.4 ポーチ・バッグ完成 | ペンギンポシェットとの交差関係を整理（ポシェットの紐の下をくぐらせる）。ポーチ本体、金具、ストラップの全要素が調和した完成ビュー。 |

---

## 技術要点・モデリングの極意（第17話）

1. **同心円インセットと `V` 切り離しによる一体成形**:
   - バッグ本体から伸びる持ち手や耳パーツを別パーツにせず、Circleインセット $\to$ 上部エッジ `Subdivide` $\to$ `V`（Rip）切り離し $\to$ `E Z` 押し出しで一体成形することにより、ポリゴン数の節約と自然なトポロジー接続を両立。
2. **面スナップ（Face Project）＋ `Align Rotation to Target`**:
   - 複雑な3次曲面を描くバッグ側面に小物（ジッパー、リベット、金具など）を配置する際、この設定を有効にすることで、面の法線方向（Normal）にオブジェクトのローカル軸が一発で吸着。手作業での3軸回転合わせが完全に不要化。
3. **カーブの捻れトラブル対処（`Switch Direction`）**:
   - ベジェカーブの `Extrude` で帯状リボンやストラップを作成中、特定ハンドルを動かすと全体が90度〜180度反転してしまう現象は、カーブの始点・終点ベクトルの特異点によるもの。`Switch Direction`（方向反転）で安定した軸方向に切り替える。
4. **親子付け（Parenting）の階層整理**:
   - ジッパー金具や底鋲など、バッグ本体と一体で動くべき装飾パーツは `Ctrl + P`（Keep Transform）で本体にペアレント化しておくことで、キャラクターポージングや衣装調整時の位置ずれを恒久的に防ぐ。
