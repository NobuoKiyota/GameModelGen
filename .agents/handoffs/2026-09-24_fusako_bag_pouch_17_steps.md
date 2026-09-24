# ふさこ氏 第17話『ポーチ・バッグ（キャンティーンバッグ）のモデリング』詳細操作手順・トポロジー仕様書

本ドキュメントは、3Dモデラー・ふさこ氏のキャラクターモデリング解説動画第17話「ポーチ・バッグのモデリング」（16分58秒）の詳細手順書である。
腰に提げる円形キャンティーンバッグ本体、フラップ（葉っぱモチーフ飾り）、底鋲（足）、ジッパー金具、およびショルダーストラップの制作工程を記録する。

📸 **対応スクリーンショットカタログ**:
- [docs/fusako_17_bag_pouch_screenshots/README.md](../../docs/fusako_17_bag_pouch_screenshots/README.md)

---

## 目次
1. [Chapter 1: バッグ前面ベースメッシュと持ち手/耳の一体成形](#chapter-1-バッグ前面ベースメッシュと持ち手耳の一体成形)
2. [Chapter 2: フラップ装飾（葉っぱ）・底鋲（足）・マチ（奥行き）押し出し](#chapter-2-フラップ装飾葉っぱ底鋲足マチ奥行き押し出し)
3. [Chapter 3: ジッパー金具の作成と面スナップ吸着・親子付け](#chapter-3-ジッパー金具の作成と面スナップ吸着親子付け)
4. [Chapter 4: ベジェカーブによるショルダーストラップと干渉回避](#chapter-4-ベジェカーブによるショルダーストラップと干渉回避)
5. [トポロジー＆運用 Tips 総括](#トポロジー運用-tips-総括)

---

## Chapter 1: バッグ前面ベースメッシュと持ち手/耳の一体成形

### Step 1-1: 円メッシュの配置と前面起立
- `Shift + A` > Mesh > **Circle** を追加。
- 左下のオペレーターパネルで **Vertices: 16**、**Fill Type: Nothing**（面なし）に設定。
- `Tab` で編集モードに入り、`R X 90` でX軸回りに90度回転させて正面を向かせる。
- `F` キーで面を貼り、法線が裏返っている場合は `Alt + N` > **Flip** で表側を手前に向ける。
- 原画・デザイン画のポーチ外周に合わせて `S` キーでサイズを調整。
[📸 参考: 01_c1_circle_16verts_rx90_bag_base.jpg](../../docs/fusako_17_bag_pouch_screenshots/01_c1_circle_16verts_rx90_bag_base.jpg)

### Step 1-2: 同心円インセットによる持ち手・耳の幅確保
- 前面を選択し、`I`（Inset Faces）で内側へ面を差し込む。
- 上部から生える持ち手（耳状パーツ）の横幅に合う厚みになるようインセット量を決定。
- モディファイアプロパティから **Mirror** モディファイア（X軸、Clipping: ON）を適用して左右対称作業を確立。
[📸 参考: 02_c1_inset_concentric_handle_width.jpg](../../docs/fusako_17_bag_pouch_screenshots/02_c1_inset_concentric_handle_width.jpg)

### Step 1-3: 上部エッジの分割・切り離し（Rip）・上方向押し出し
- 耳が生える上部外周のエッジを選択し、右クリック > **Subdivide** で中央に頂点を追加。
- 中央の頂点を選択し、`V` キーで切り離し（Rip）。`G Y` でほんの少し手前に引き出す。
- 切り離した上部3点のエッジを選択し、`E Z` で真上方向へ押し出して持ち手（耳）の突起を形成。
[📸 参考: 03_c1_subdivide_v_rip_ez_handle_extrude.jpg](../../docs/fusako_17_bag_pouch_screenshots/03_c1_subdivide_v_rip_ez_handle_extrude.jpg)

### Step 1-4: 頂点ベベルによる丸み付けと四角面トポロジー整理
- 持ち手上端の角の頂点を選択し、`Ctrl + Shift + B`（Vertex Bevel）を実行して角を丸める。
- 多角形（N-gon）ができた箇所は、対向する頂点同士を複数選択して `J` キー（Join Vertices）で繋ぎ、すべて四角形（Quad）に分割・整理。
- 外側に向かって軽くハの字に傾け、キャラらしい愛嬌のあるフォルムに整形。
[📸 参考: 04_c1_vertex_bevel_round_quad_cleanup.jpg](../../docs/fusako_17_bag_pouch_screenshots/04_c1_vertex_bevel_round_quad_cleanup.jpg)

### Step 1-5: オートスムースとシャープ指定によるエッジ輪郭保持
- オブジェクトモードで右クリック > **Shade Auto Smooth**（または Normal > Auto Smooth を30°〜60°に設定）。
- 編集モードで、持ち手とバッグ円形の境界エッジや輪郭のエッジを選択し、右クリック > **Mark Sharp** を適用。
- スムースシェーディングによる意図しない陰影の回り込み（黒ずみ）を防止。
[📸 参考: 05_c1_auto_smooth_mark_sharp_edges.jpg](../../docs/fusako_17_bag_pouch_screenshots/05_c1_auto_smooth_mark_sharp_edges.jpg)

---

## Chapter 2: フラップ装飾（葉っぱ）・底鋲（足）・マチ（奥行き）押し出し

### Step 2-1: 葉っぱ型フラップのベース円（12頂点）作成
- `Shift + A` > Mesh > **Circle**（Vertices: 12）を新規追加。
- `F` で面を貼り、`I` で内側にインセット。中央の面を選択して `M` > **At Center** でマージ。
- `R X 90` で立てて正面に向け、`S X` で左右を絞って葉っぱ状の縦長シルエットを作成。
[📸 参考: 06_c1_circle_12verts_inset_leaf_flap.jpg](../../docs/fusako_17_bag_pouch_screenshots/06_c1_circle_12verts_inset_leaf_flap.jpg)

### Step 2-2: フラップの配置とローカル座標系での変形
- トランスフォーム座標系（Transform Orientation）を **Local** に切り替え。
- フラップをバッグ前面の斜め位置へ配置し、ローカル軸に沿って傾きやスケールを調整。
[📸 参考: 07_c2_flap_placement_local_scaling.jpg](../../docs/fusako_17_bag_pouch_screenshots/07_c2_flap_placement_local_scaling.jpg)

### Step 2-3: ループカットと Alt + S による立体的な膨らみ出し
- フラップ内部のエッジに `Ctrl + R` でループカットを追加。
- 膨らませたい中央付近の頂点を選択し、`Alt + S`（Shrink/Fatten：法線方向拡縮）でふっくらとした厚みを持たせる。
[📸 参考: 08_c2_subdivide_alt_s_flap_bulge.jpg](../../docs/fusako_17_bag_pouch_screenshots/08_c2_subdivide_alt_s_flap_bulge.jpg)

### Step 2-4: 面複製と Bridge による二重構造・縁の折り返し成形
- フラップの面全体を選択し、`Shift + D` で奥（-Y方向）へわずかに複製。
- 表と裏の外周ループを両方選択し、`LoopTools > Bridge`（または Edge > Bridge Edge Loops）で側面を繋ぐ。
- 側面の不要なエッジリングを `Ctrl + Alt + Click` で選択し、`X` > **Collapse Edges** で厚みを薄く整え、角を三角面で綺麗に閉じる。`Shift + N` で法線方向を再計算。
[📸 参考: 09_c2_duplicate_looptools_bridge_double_layer.jpg](../../docs/fusako_17_bag_pouch_screenshots/09_c2_duplicate_looptools_bridge_double_layer.jpg)

### Step 2-5: フラップと前面パーツの結合（Ctrl + J）
- フラップパーツとバッグ前面パーツを選択し、`Ctrl + J` で1つのオブジェクトに結合。
- 外周エッジに `Mark Sharp` を追加し、ピボットポイントを **Active Element** にして全体のスケールバランスを微調整。
[📸 参考: 10_c2_ctrl_j_join_flap_mark_sharp.jpg](../../docs/fusako_17_bag_pouch_screenshots/10_c2_ctrl_j_join_flap_mark_sharp.jpg)

### Step 2-6: 底鋲（足）パーツの作成と配置
- `Shift + A` > Mesh > **Cube** を配置し、`Ctrl + 1` で **Subdivision Surface**（Level 1）を付与。
- `S` キーで小さく縮小し、バッグ底部の接地パーツ（鋲・足）として配置。
- `S Y` で厚みを薄くし、サブディビジョンサーフェスを適用（Apply）してからバッグ本体と `Ctrl + J` で結合。
[📸 参考: 11_c2_cube_subsurf1_feet_placement.jpg](../../docs/fusako_17_bag_pouch_screenshots/11_c2_cube_subsurf1_feet_placement.jpg)

### Step 2-7: マチ（奥行き）押し出しと背面グリッドの密閉
- バッグ前面の外周エッジループを `Alt + Click` で全選択。
- `E Y` で後ろ方向へ押し出し、バッグのマチ（奥行き）を形成。
- 背面エッジを選択して `F` で面を貼り、`I`（Inset Faces）で同心円状に内側へ面を差し込む。
- 中央の穴を `M` > **At Center** でマージし、`G X` で中心頂点をクリッピング結合させて背面を完全に密閉。
[📸 参考: 12_c2_ey_depth_extrude_back_inset_seal.jpg](../../docs/fusako_17_bag_pouch_screenshots/12_c2_ey_depth_extrude_back_inset_seal.jpg)

---

## Chapter 3: ジッパー金具の作成と面スナップ吸着・親子付け

### Step 3-1: Cubeからのジッパースライダー本体造形
- `Shift + A` > Mesh > **Cube** を追加。
- `S X` で横幅を縮め、ジッパースライダーの小型直方体を作成。
- 面を削除して内側の空洞を作り、`E` で押し出してローポリ金具のベースをモデリング。
[📸 参考: 13_c3_cube_zipper_slider_modeling.jpg](../../docs/fusako_17_bag_pouch_screenshots/13_c3_cube_zipper_slider_modeling.jpg)

### Step 3-2: 引き手（プルタブ）プレートの作成
- スライダーの下部に長方形プレートをモデリング。
- `Shift + N` で法線方向を揃え、軽量な板ポリゴンでジッパーの引き手（チャーム）を完成させる。
[📸 参考: 14_c3_zipper_pull_plate_extrude.jpg](../../docs/fusako_17_bag_pouch_screenshots/14_c3_zipper_pull_plate_extrude.jpg)

### Step 3-3: 面スナップ（Face Project）＋ Align Rotation による曲面吸着
- スナップツール（`Shift + Tab`）をONにし、スナップ先を **Face Project**（面）に設定。
- **Align Rotation to Target**（ターゲットに回転を整列）にチェックを入れる。
- ジッパー金具をバッグ側面の曲面へドラッグすると、バッグの法線角度に金具のローカル軸が完全自動追従して一発で密着。
- 位置が決まったらスナップをOFFにし、微小な食い込みや傾きを手動で微調整。
[📸 参考: 15_c3_face_snapping_align_rotation_target.jpg](../../docs/fusako_17_bag_pouch_screenshots/15_c3_face_snapping_align_rotation_target.jpg)

### Step 3-4: 金具の親子付け（Parenting）
- ジッパー金具を選択後、バッグ本体を `Shift + Click` で追加選択（バッグ本体がアクティブ）。
- `Ctrl + P` > **Object (Keep Transform)** を実行。
- バッグ本体を移動・回転・拡縮してもジッパー金具が自動追従する状態を構築。
[📸 参考: 16_c3_ctrl_p_parenting_zipper_to_bag.jpg](../../docs/fusako_17_bag_pouch_screenshots/16_c3_ctrl_p_parenting_zipper_to_bag.jpg)

### Step 3-5: 第16話ペンギンポシェットとの干渉回避レイアウト
- 前話で作成したペンギンポシェットを表示し、腰回りでの干渉（クリッピング）をチェック。
- ペンギンポシェットを少し内側・斜め前へ寄せ、キャンティーンバッグを少し外側・後方へオフセット配置。
- 将来の物理ボーン揺れ設定（Spring/Dynamic Bone）を見越して、両者が接触しないクリアランスを確保。
[📸 参考: 17_c3_pochette_collision_avoidance_tweak.jpg](../../docs/fusako_17_bag_pouch_screenshots/17_c3_pochette_collision_avoidance_tweak.jpg)

---

## Chapter 4: ベジェカーブによるショルダーストラップと干渉回避

### Step 4-1: ベジェカーブの配置と Extrude 設定
- `Shift + A` > Curve > **Bezier** を追加。
- オブジェクトデータプロパティ（緑のカーブアイコン）> **Geometry** > **Extrude** を `0.005`〜`0.006` に設定して帯状の厚みを持たせる。
- 3Dビューポートのヘッダーで **Backface Culling**（裏面非表示）を一時的にOFFにし、両面が見える状態で作業。
[📸 参考: 18_c4_curve_bezier_shoulder_strap_extrude.jpg](../../docs/fusako_17_bag_pouch_screenshots/18_c4_curve_bezier_shoulder_strap_extrude.jpg)

### Step 4-2: 制御点の配置と Ctrl + T によるカーブの傾き（Tilt）補正
- カーブの制御点をバッグ側面の金具位置から肩、胸元へ這わせる。
- 各制御点を選択し、`Ctrl + T`（Tilt）で回転角度を微調整。
- ストラップの帯面がパーカーや胸のメッシュ表面に沿って密着するように調整。
[📸 参考: 19_c4_ctrl_t_curve_tilt_alignment.jpg](../../docs/fusako_17_bag_pouch_screenshots/19_c4_ctrl_t_curve_tilt_alignment.jpg)

### Step 4-3: 【重要Tips】Switch Direction によるカーブの捻れ・回転バグ解消
- カーブハンドルを操作中、1つの制御点を動かしただけでストラップ全体が突然クルクルと回転・反転してしまう現象が発生した場合:
  1. 編集モードで `A` キー（全制御点を選択）。
  2. 右クリック > **Switch Direction**（方向反転）を実行。
- カーブの始点と終点の向きが逆転し、数学的なジンバルロック/特異点による捻れが即座に解消される。
[📸 参考: 20_c4_switch_direction_prevent_twist.jpg](../../docs/fusako_17_bag_pouch_screenshots/20_c4_switch_direction_prevent_twist.jpg)

### Step 4-4: フード・後ろ髪の非表示と背面経路の敷設
- 背面作業の邪魔になるフード（パーカー頭部）や後ろ髪を選択し、`H` キーで一時非表示。
- 右クリック > **Subdivide** で背中側の制御点を追加。
- ストラップが背中のメッシュにめり込まず、かつ不自然に浮かない滑らかなラインを描くよう制御点を配置。
[📸 参考: 21_c4_hide_hood_hair_back_strap_path.jpg](../../docs/fusako_17_bag_pouch_screenshots/21_c4_hide_hood_hair_back_strap_path.jpg)

### Step 4-5: ポシェット紐との交差調整と完成
- ペンギンポシェットのストラップとキャンティーンバッグのストラップの上下関係を決定。
- キャンティーンバッグのストラップをポシェットのストラップの下をくぐらせるように制御点高さをオフセット。
- カーブのまま保持しておき、リギング段階でメッシュ変換（`Convert to Mesh`）とウェイト付けを行う構成とする。
[📸 参考: 22_c4_under_pochette_shoulder_bag_complete.jpg](../../docs/fusako_17_bag_pouch_screenshots/22_c4_under_pochette_shoulder_bag_complete.jpg)

---

## トポロジー＆運用 Tips 総括

| 項目 | テクニック / ショートカット | 効能・ゲームモデルへのメリット |
|:---|:---|:---|
| **一体成形トポロジー** | `Circle` $\to$ `Inset` $\to$ `Subdivide` $\to$ `V`（Rip） $\to$ `E Z` | 持ち手や突起を別オブジェクトにせず連続メッシュで成形。無駄な結合頂点・ドローコールを抑制。 |
| **頂点丸めと四角化** | `Ctrl + Shift + B`（Vertex Bevel） $\to$ `J`（Join Vertices） | 多角形面の発生を抑え、サブディビジョンやスキニング時に歪まないトポロジーを維持。 |
| **面法線追従スナップ** | `Snap: Face Project` ＋ `Align Rotation to Target: ON` | 3次曲面上の小物配置をドラッグ1つで完了。法線角度の計算手作業をゼロ化。 |
| **カーブ捻れ解消** | カーブ全選択 `A` $\to$ 右クリック `Switch Direction` | ベジェカーブExtrude時の意図しない回転バグを瞬時にリセット。 |
| **階層ペアレント** | 小物を選択 $\to$ 本体選択 $\to$ `Ctrl + P` > `Keep Transform` | 小物パーツの位置関係を崩さずに本体の移動・スケール変更に追従。 |
