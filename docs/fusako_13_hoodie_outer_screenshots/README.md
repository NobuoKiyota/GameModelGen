# ふさこ氏チュートリアル第13話『フード付きアウターのモデリング』重要シーン・スクリーンショットカタログ

本フォルダには、ふさこ氏によるBlenderキャラクターモデル制作チュートリアル第13話『フード付きアウターのモデリング 〜初級から中級者向けチュートリアル〜』（動画長: 38分31秒）から抽出した、モデリング・トポロジー上の重要キーフレーム高解像度スクリーンショット（全26枚）を収録しています。

詳細な手順仕様書は [2026-09-24_fusako_hoodie_outer_13_steps.md](../../.agents/handoffs/2026-09-24_fusako_hoodie_outer_13_steps.md) を参照してください。

---

## スクリーンショット一覧・トポロジー解説

| No | タイムスタンプ | 画像リンク (相対パス) | 工程・チャプター | 使用ショートカット / 機能 | 解説・モデリングのポイント |
| :---: | :---: | :--- | :--- | :--- | :--- |
| 01 | 00:00:25 | [./01_c1_reference_overlay_hoodie.jpg](./01_c1_reference_overlay_hoodie.jpg) | C1: フード立ち上げ | 画像エンプティ切り替え | 正面・側面にパーカー着用リファレンス画像を読み込み、髪メッシュを非表示化。 |
| 02 | 00:00:48 | [./02_c1_circle_12verts_hood_base.jpg](./02_c1_circle_12verts_hood_base.jpg) | C1: フード立ち上げ | `Shift + A > Circle` (頂点数12) | 素体・ワンピースのトポロジーに合わせた12頂点円からフード開口部を開始。 |
| 03 | 00:01:22 | [./03_c1_proportional_hood_opening_align.jpg](./03_c1_proportional_hood_opening_align.jpg) | C1: フード立ち上げ | `O` (プロポーショナル), `R`, `S`, `G` | 顔周りの輪郭に合わせて前下げ・後ろ下げのざっくりした傾斜形状を作成。 |
| 04 | 00:02:08 | [./04_c1_extrude_alt_s_outer_line.jpg](./04_c1_extrude_alt_s_outer_line.jpg) | C1: フード立ち上げ | `E`, `Alt + S`, `G` | 外側へ押し出し `Alt + S` で大きく広げ、後頭部〜背中への膨らみラインを形成。 |
| 05 | 00:03:06 | [./05_c1_extrude_down_alt_s_inward.jpg](./05_c1_extrude_down_alt_s_inward.jpg) | C1: フード立ち上げ | `E + Z`, `Alt + S` (内側) | 内側ループを下へ押し出し、`Alt + S` で内側へ絞り込んで首元の受け口を成形。 |
| 06 | 00:03:45 | [./06_c1_looptools_bridge_hood_double_layer.jpg](./06_c1_looptools_bridge_hood_double_layer.jpg) | C1: フード立ち上げ | `LoopTools > Bridge` | フードの内外エッジループを選択し、Bridgeで架橋して袋状の二重布構造を完成。 |
| 07 | 00:04:45 | [./07_c2_duplicate_dress_belly_faces.jpg](./07_c2_duplicate_dress_belly_faces.jpg) | C2: 身頃の作成 | `Shift + D`, `Alt + S`, `P` | ワンピースのお腹面を選択・複製し、`Alt + S` で外側に膨らませて別オブジェクト分離。 |
| 08 | 00:05:08 | [./08_c2_ctrl_j_join_hood_and_body.jpg](./08_c2_ctrl_j_join_hood_and_body.jpg) | C2: 身頃の作成 | `Ctrl + J`, `Shade Flat` | フードと胴体を結合。視認性確保のため一時的にフラットシェードで作業。 |
| 09 | 00:05:40 | [./09_c2_f_face_loop_cut_quad_topology.jpg](./09_c2_f_face_loop_cut_quad_topology.jpg) | C2: 身頃の作成 | `F`, `G + G`, `Ctrl + R` | 背中中央で近接する頂点を `F` で面張りし、ループスライドとカットで4点クアッド化。 |
| 10 | 00:06:45 | [./10_c2_random_color_viewport_overlay.jpg](./10_c2_random_color_viewport_overlay.jpg) | C2: 身頃の作成 | Viewport Overlays: `Color > Random` | オブジェクトが増えた際の重なり視認性を高めるため、ランダムカラー表示を有効化。 |
| 11 | 00:08:45 | [./11_c2_v_rip_hood_edge_alt_s_gap.jpg](./11_c2_v_rip_hood_edge_alt_s_gap.jpg) | C2: 身頃の作成 | `V` (切り裂き), `Alt + S` | フード側面の急激な折れ曲がり部分を `V` で切り離し、`Alt + S` で隙間を開けて空間確保。 |
| 12 | 00:09:05 | [./12_c2_looptools_bridge_smooth_junction.jpg](./12_c2_looptools_bridge_smooth_junction.jpg) | C2: 身頃の作成 | `LoopTools > Bridge` | 開けた隙間の両側ループをBridgeで再接続し、滑らかな接続曲面へ整流。 |
| 13 | 00:10:20 | [./13_c2_cloth_wrinkles_alt_s_indents.jpg](./13_c2_cloth_wrinkles_alt_s_indents.jpg) | C2: 身頃の作成 | `Ctrl + R`, `Alt + S` | 内側ループを凹ませ、後方を膨らませることでリアルな布のたわみとしわを造形。 |
| 14 | 00:12:15 | [./14_c2_extend_hem_downward_gg.jpg](./14_c2_extend_hem_downward_gg.jpg) | C2: 身頃の作成 | `Ctrl + R`, `G + G` | アウターの裾ループを追加し、頂点スライドで下方へ延長して着丈を調整。 |
| 15 | 00:13:20 | [./15_c3_front_trim_parallel_loops_ctrl_r.jpg](./15_c3_front_trim_parallel_loops_ctrl_r.jpg) | C3: 前開き・トリム | `Ctrl + R`, `E` (平行揃え) | 前開きトリム（縁取り）用に均等幅の平行ループをカット追加。 |
| 16 | 00:14:15 | [./16_c3_separate_trim_solidify_modifier.jpg](./16_c3_separate_trim_solidify_modifier.jpg) | C3: 前開き・トリム | `P` (分離), `Solidify` | トリム面を分離し、`Solidify`（Thickness: 0.005m, Offset: +1.0）で外側に厚み付け。 |
| 17 | 00:15:00 | [./17_c3_individual_origins_s_bevel_step.jpg](./17_c3_individual_origins_s_bevel_step.jpg) | C3: 前開き・トリム | `.` (Individual Origins), `S` | モディファイア適用後、それぞれの原点でエッジを縮小し、ふっくらした段差ベベル感を強調。 |
| 18 | 00:15:50 | [./18_c3_v_rip_asymmetrical_front_overlap.jpg](./18_c3_v_rip_asymmetrical_front_overlap.jpg) | C3: 前開き・トリム | `V`, `G + X`, `X > Dissolve Edges` | `V` で前開きエッジを切り裂き、片側を横にずらして重なりを作り、不要エッジを溶解。 |
| 19 | 00:18:00 | [./19_c3_mark_sharp_trim_overlap_edges.jpg](./19_c3_mark_sharp_trim_overlap_edges.jpg) | C3: 前開き・トリム | `Ctrl + E > Mark Sharp`, `Auto Smooth 180°` | 重なり段差のエッジにマークシャープを付与し、セル調のくっきりした境界陰影を表現。 |
| 20 | 00:19:55 | [./20_c3_inset_cuff_collar_cloth_thickness.jpg](./20_c3_inset_cuff_collar_cloth_thickness.jpg) | C3: 前開き・トリム | `I` (インセット), `Face Delete`, 頂点スナップ | 袖口・首元の開口部を面差し込みして厚みを作り、奥の頂点を素体へスナップ密着。 |
| 21 | 00:24:55 | [./21_c4_duplicate_hood_edge_ear_base.jpg](./21_c4_duplicate_hood_edge_ear_base.jpg) | C4: フードの耳パーツ | `Shift + D`, `P`, `E + Z` | フード後頭部のエッジを複製・分離し、下方に押し出して耳の根元を生成。 |
| 22 | 00:25:40 | [./22_c4_smooth_vertices_ear_tip_curl.jpg](./22_c4_smooth_vertices_ear_tip_curl.jpg) | C4: フードの耳パーツ | `Vertex > Smooth Vertices`, `R`, `G` | 先端頂点をスムースで丸め、プロポーショナル編集で外ハネの愛らしい垂れ耳形状へ成形。 |
| 23 | 00:27:00 | [./23_c4_subdivide_smoothness_hood_socket.jpg](./23_c4_subdivide_smoothness_hood_socket.jpg) | C4: フードの耳パーツ | `Subdivide` (Smoothness: 1.5) | フード側に受け口となる分割を追加し、なだらかな接続ベースを形成。 |
| 24 | 00:28:15 | [./24_c4_ctrl_j_join_ears_merge_at_center.jpg](./24_c4_ctrl_j_join_ears_merge_at_center.jpg) | C4: フードの耳パーツ | `Ctrl + J`, `Merge at Center`, `Ctrl + T` | フードと耳を結合し、不要面を削除して頂点マージで溶接。五角形面を三角化で整流。 |
| 25 | 00:31:30 | [./25_c4_v_rip_back_neck_thickness_gap.jpg](./25_c4_v_rip_back_neck_thickness_gap.jpg) | C4: フードの耳パーツ | `V`, `G + Z`, `F` | 首後ろの切り替え境界を `V` 切り裂きで持ち上げ、`F` で面を張って布の段差ギャップを造形。 |
| 26 | 00:35:00 | [./26_c5_penguin_wings_extrude_solidify.jpg](./26_c5_penguin_wings_extrude_solidify.jpg) | C5: ペンギン羽状・萌え袖 | `E + X`, `S + Y`, `Alt + S`, `Solidify` | 腕メッシュから複製したループを羽状・萌え袖へ押し出し拡大。`Solidify`（Even: ON）で完成。 |
