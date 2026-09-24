# ふさこ氏チュートリアル第14話『靴（サンダル・ブーツ）のモデリング』重要シーン・スクリーンショットカタログ

本フォルダには、ふさこ氏によるBlenderキャラクターモデル制作チュートリアル第14話『靴（サンダル・ブーツ）のモデリング 〜初級から中級者向けチュートリアル〜』（動画長: 23分36秒）から抽出した、モデリング・トポロジー上の重要キーフレーム高解像度スクリーンショット（全24枚）を収録しています。

詳細な手順仕様書は [2026-09-24_fusako_shoes_sandals_14_steps.md](../../.agents/handoffs/2026-09-24_fusako_shoes_sandals_14_steps.md) を参照してください。

---

## スクリーンショット一覧・トポロジー解説

| No | タイムスタンプ | 画像リンク (相対パス) | 工程・チャプター | 使用ショートカット / 機能 | 解説・モデリングのポイント |
| :---: | :---: | :--- | :--- | :--- | :--- |
| 01 | 00:00:15 | [./01_c1_plane_bottom_view_align.jpg](./01_c1_plane_bottom_view_align.jpg) | C1: サンダル・靴底 | `Shift + A > Plane`, `Ctrl + Num7` | 3Dカーソル原点配置後、底面ビューで足裏より一回り大きい平面を追加。 |
| 02 | 00:00:30 | [./02_c1_five_loops_sole_contour.jpg](./02_c1_five_loops_sole_contour.jpg) | C1: サンダル・靴底 | `Ctrl + R` (5分割), `G` | 平面に5本の縦ループを追加し、頂点を移動して足型シルエットへ成形。 |
| 03 | 00:01:45 | [./03_c1_inset_inner_sole_shrink.jpg](./03_c1_inset_inner_sole_shrink.jpg) | C1: サンダル・靴底 | `Shift + D + Z`, `I`, `X > Edges` | 靴底を下に複製退避後、`I` インセットで外周を1段縮小しインナーソールを作成。 |
| 04 | 00:02:40 | [./04_c1_extrude_z_sandal_upper.jpg](./04_c1_extrude_z_sandal_upper.jpg) | C1: サンダル・靴底 | `E + Z`, `S + X` | インナーソール外周を上へ押し出し、`S + X` で幅を絞り足の甲を覆うアッパーを成形。 |
| 05 | 00:03:25 | [./05_c1_loopcut_instep_round_shape.jpg](./05_c1_loopcut_instep_round_shape.jpg) | C1: サンダル・靴底 | `Ctrl + R`, `F`, `G + Z` | 中間に横ループを追加し、甲の盛り上がりに合わせて丸みカーブを形成。 |
| 06 | 00:04:30 | [./06_c1_extrude_ankle_sx_width.jpg](./06_c1_extrude_ankle_sx_width.jpg) | C1: サンダル・靴底 | `E + Z`, `S + X`, `F` | 足首方向へ上方に押し出し、4点選択 `F` でアッパー天面を密閉。 |
| 07 | 00:05:40 | [./07_c1_alt_s_bulge_sole_embed.jpg](./07_c1_alt_s_bulge_sole_embed.jpg) | C1: サンダル・靴底 | `Ctrl + R`, `G + G`, `Alt + S` | 下端近くにループを追加し、`Alt + S` で外側に膨らませてソールへの食い込みを造形。 |
| 08 | 00:06:45 | [./08_c1_annotate_penguin_webbed_foot.jpg](./08_c1_annotate_penguin_webbed_foot.jpg) | C1: サンダル・靴底 | Annotate（下書き）, ナイフ/移動 | 靴底メッシュにペンギンの足（水かき形状）をアノテーション下書きし頂点成形。 |
| 09 | 00:07:45 | [./09_c1_extrude_thick_platform_sole.jpg](./09_c1_extrude_thick_platform_sole.jpg) | C1: サンダル・靴底 | `E + Z + Z` (地面方向), `Shift + N` | 靴底の底面を地面まで垂直に押し出し、厚底ソールを形成（法線外側再計算）。 |
| 10 | 00:08:40 | [./10_c2_duplicate_top_loop_sock_base.jpg](./10_c2_duplicate_top_loop_sock_base.jpg) | C2: 靴下・ギザギザ縁 | `Shift + D + Z`, `S`, `LoopTools Relax` | サンダル上端ループを上に複製し、`S` 拡大と `Relax` で滑らかな靴下ベースを生成。 |
| 11 | 00:09:15 | [./11_c2_extrude_down_alt_s_fluffy.jpg](./11_c2_extrude_down_alt_s_fluffy.jpg) | C2: 靴下・ギザギザ縁 | `E + Z`, `Alt + S` | 下方へ押し出し、`Alt + S` で外側にボリューミーに膨らませてモコモコ感を付与。 |
| 12 | 00:09:35 | [./12_c2_top_face_inset_extrude_socket.jpg](./12_c2_top_face_inset_extrude_socket.jpg) | C2: 靴下・ギザギザ縁 | `F`, `I`, `E`, `Ctrl + B` | 天面を `F` 面張り $\to$ `I` インセット $\to$ `E` 下方押し出しで足首受け口を密閉成形。 |
| 13 | 00:10:15 | [./13_c2_hem_subdivide_preparation.jpg](./13_c2_hem_subdivide_preparation.jpg) | C2: 靴下・ギザギザ縁 | `Shift + Alt + 左クリック`, `Subdivide` | ギザギザの解像度を確保するため、最下端とその上のループを細分化。 |
| 14 | 00:11:00 | [./14_c2_checker_deselect_one_skip.jpg](./14_c2_checker_deselect_one_skip.jpg) | C2: 靴下・ギザギザ縁 | `Select > Checker Deselect` | 1つ飛ばしで頂点を一括選択（チェッカー選択）し、波形頂点を抽出。 |
| 15 | 00:11:15 | [./15_c2_gg_slide_zigzag_hem_pattern.jpg](./15_c2_gg_slide_zigzag_hem_pattern.jpg) | C2: 靴下・ギザギザ縁 | `G + G` (エッジスライド) | 選択された1つ飛ばし頂点を `G + G` で上方へスライドし、ジグザグ縁を一発生成。 |
| 16 | 00:11:35 | [./16_c2_ctrl_t_triangulate_v_crease.jpg](./16_c2_ctrl_t_triangulate_v_crease.jpg) | C2: 靴下・ギザギザ縁 | `Ctrl + T` (三角面化) | ギザギザによって生じた多角形面を `Ctrl + T` でV字三角面化しトポロジー整流。 |
| 17 | 00:12:25 | [./17_c2_duplicate_sandal_cuff_alt_s.jpg](./17_c2_duplicate_sandal_cuff_alt_s.jpg) | C2: 靴下・ギザギザ縁 | `Shift + D`, `Alt + S` (内側凹ませ) | サンダル開口部の面ループを複製し、内側に凹ませて縁取りの隙間を形成。 |
| 18 | 00:13:10 | [./18_c2_looptools_bridge_double_cuff.jpg](./18_c2_looptools_bridge_double_cuff.jpg) | C2: 靴下・ギザギザ縁 | `LoopTools > Bridge` (Twist調整) | 二重ループ間をBridgeで架橋し、ふっくらした履き口のトリム縁取りを完成。 |
| 19 | 00:14:55 | [./19_c2_individual_origins_cuff_scale.jpg](./19_c2_individual_origins_cuff_scale.jpg) | C2: 靴下・ギザギザ縁 | `.` (Individual Origins), `S` | エッジリングを選択し、それぞれの原点でスケールして厚み幅を自在に微調整。 |
| 20 | 00:16:15 | [./20_c3_duplicate_side_faces_wings.jpg](./20_c3_duplicate_side_faces_wings.jpg) | C3: ペンギン羽飾り | `Shift + D + X`, `Smooth Vertices` | 靴側面から面を複製し、頂点スムーズで丸みを帯びた羽シルエットへ整流。 |
| 21 | 00:17:20 | [./21_c3_extrude_wing_thickness_curl.jpg](./21_c3_extrude_wing_thickness_curl.jpg) | C3: ペンギン羽飾り | `E` (厚み押し出し), 反り角度調整 | `E` で厚み押し出しを行い、本体からわずかに反るように配置して立体感を演出。 |
| 22 | 00:19:10 | [./22_c4_ポンポン飾り・仕上げ | `Cube`, `Subsurf 1` 適用, `Ctrl + B` | 立方体にSubsurf1を適用し、角のエッジを面取り（ベベル）してケージを均等化。 |
| 23 | 00:19:50 | [./23_c4_to_sphere_pom_pom_shaping.jpg](./23_c4_to_sphere_pom_pom_shaping.jpg) | C4: ポンポン飾り・仕上げ | `Shift + Alt + S` (To Sphere: 1.0) | メッシュ全体を真球化（球状に変形）し、愛らしい球体ポンポンを高速生成。 |
| 24 | 00:21:00 | [./24_c4_pom_pom_placement_mirror_complete.jpg](./24_c4_pom_pom_placement_mirror_complete.jpg) | C4: ポンポン飾り・仕上げ | `Ctrl + J`, `Mirror` モディファイア | 靴の甲にポンポンを配置、靴と結合してMirrorで左右両足へ対称化し完成。 |
