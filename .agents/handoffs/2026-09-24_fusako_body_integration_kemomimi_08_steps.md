# ふさこ氏『手足の接合＆ケモ耳のモデリング』操作手順・トポロジー仕様書（第8回）

## 1. 動画メタデータ（公式事実）
- **正式タイトル**: 『Blenderでキャラクターモデル制作！08 | 手足の接合＆ケモ耳のモデリング〜初級から中級者向けチュートリアル〜』
- **URL**: https://www.youtube.com/watch?v=t2Gsg-e0C18
- **動画長**: 27分08秒（1628秒）
- **チャンネル**: ふさこ / 3D工房
- **アップロード日**: 2023年5月26日
- **字幕データ**:
  - VTT生データ: `z:\MeshCreator\.agents\handoffs\fusako_08_subtitles_raw.ja.vtt`
  - タイムスタンプ付きテキスト: `z:\MeshCreator\.agents\handoffs\fusako_08_subtitles_timestamped.txt`
- **重要シーン・スクリーンショット集（全24枚）**:
  - 保存フォルダ: [`z:\MeshCreator\docs\fusako_08_kemomimi_screenshots/`](file:///z:/MeshCreator/docs/fusako_08_kemomimi_screenshots/)
  - 画像カタログ: [`z:\MeshCreator\docs\fusako_08_kemomimi_screenshots/README.md`](file:///z:/MeshCreator/docs/fusako_08_kemomimi_screenshots/README.md)

---

## 2. チャプター構成一覧

| # | タイムスタンプ | チャプター名 | 主な対象 | 概要 |
| :--- | :--- | :--- | :--- | :--- |
| **C1** | 00:00 - 03:55 | 手のボーン対称化とミラーセットアップ | 手・ボーン | ポーズ初期化 $\to$ **【AutoName Left/Right ＋ Symmetrize】** $\to$ Mirror $\to$ **【With Empty Groups再実行で.R自動生成】** |
| **C2** | 03:55 - 05:10 | 足と脚の接合 | 脚部・足部メッシュ | 足をメインへ移動 $\to$ 体とCtrl+J統合 $\to$ **【LoopTools Bridgeで足首8頂点一発架橋】** |
| **C3** | 05:10 - 07:35 | 手と腕の接合 | 腕部・手首メッシュ | 手首不要エッジ整理で8頂点化 $\to$ Ctrl+J統合 $\to$ **【LoopTools Bridgeで手首8頂点一発架橋】** $\to$ Alt+S整流 |
| **C4** | 07:35 - 13:10 | 膝・脇・胴体ディテール | 素体ディテール | 膝前面インセット（膝蓋骨形成） $\to$ 脇下くぼみ（ナイフカット） $\to$ リングSubdivideでお腹・お尻の肉感増強 |
| **C5** | 13:10 - 27:08 | ケモ耳（猫耳）モデリング | 猫耳・耳毛パーツ | 平面から耳ベース作成 $\to$ **【Solidify＋頂点ウェイトグラデーションによる厚み制御】** $\to$ 45度Cube毛束ぶっ刺し |

---

## 3. モデリング方針とトポロジー黄金律

### 核心方針: 「8頂点Bridge接合、Symmetrize＋With Empty Groups、Solidifyウェイト厚み制御」
1. **四肢末端の「8頂点LoopTools Bridge」完全統合**:
   - 第4回で作成した腕（8頂点）と脚（8頂点）に対し、第6回の手首（10頂点から不要辺を整理して8頂点化）および第7回の足首（8頂点）を、アドオン **`LoopTools > Bridge`** で1対1の四角面架橋。
   - ねじれ（Twist）をゼロに合わせることで、破綻・歪みのない完全な一体型ベース素体（Headless Body）が完成する。
2. **アーマチュアの「Symmetrize」と頂点グループの「With Empty Groups連動」**:
   - 左手（`.L`）のボーンチェーンを編集モードで `Names > AutoName Left/Right` $\to$ **`Symmetrize`（対称化）** することで、右手（`.R`）ボーンが一瞬で幾何学的対称に生成される。
   - 手メッシュにMirrorモディファイアを適用した際、右手側をボーンに連動させるため、メッシュ $\to$ ボーンを選択して **`Ctrl + P` $\to$ 「With Empty Groups」を再実行** する。これにより `.R` 側の頂点グループが即座に一括追加され、両腕が完全対称に駆動する。
3. **Solidify（ソリッド化）の「頂点ウェイトグラデーション制御」**:
   - ケモ耳の肉厚を均一な厚みにしてしまうと、アニメ調の軽やかさが失われる。
   - 頂点グループを作成し、ウェイトペイントで **「根元 = 1.0（厚い） $\to$ 先端 = 0.0（薄い）」** のグラデーションを塗って Solidify モディファイアの「頂点グループ」に指定。これにより、付け根がふっくらと立ち上がり、耳先がシュッと尖る理想的な厚み変化が完全非破壊で実現する。
4. **膝小僧（膝蓋骨）のインセットトポロジー**:
   - 単なる円筒ではなく、膝前面の4面を `I`（インセット）して中央を `Alt + S` で前方に突き出させることで、曲げた時にカクッと骨ばるリアルな膝関節トポロジーを形成する。

---

## 4. パーツ別詳細手順

### Part 1: 手のボーン対称化（Symmetrize）とミラーセットアップ (00:00〜03:55)
1. **手の移動とポーズ初期化**:
   - キーボード `3` で手コレクションへ移動し、手メッシュとアーマチュアを選択。
   - `M` キーでメインコレクション（Collection 1）へ移動。
   - ポーズモードに入り、全選択 `A` $\to$ **`Alt + R`（回転クリア）＋ `Alt + G`（位置クリア）** でTポーズにリセット。
   - [📸 参考: 01_c1_hand_scale_placement.jpg](../../docs/fusako_08_kemomimi_screenshots/01_c1_hand_scale_placement.jpg)
2. **ボーンの自動命名と対称化（Symmetrize）**:
   - アーマチュアを選択し、編集モードに入る。
   - 全選択 `A` $\to$ 右クリック $\to$ **名前 > 左右の自動ネーム（Names > AutoName Left/Right）**（ボーン末尾に `.L` が付与）。
   - [📸 参考: 02_c1_bone_autoname_left_right.jpg](../../docs/fusako_08_kemomimi_screenshots/02_c1_bone_autoname_left_right.jpg)
   - 再度右クリック $\to$ **対称化（Symmetrize）** を実行（反対側の右手ボーン `.R` が完全対称に自動生成）。
   - [📸 参考: 03_c1_bone_symmetrize_right.jpg](../../docs/fusako_08_kemomimi_screenshots/03_c1_bone_symmetrize_right.jpg)
3. **手のMirrorモディファイアと右腕頂点グループの生成**:
   - オブジェクトモードで手メッシュを選択し、`Ctrl + A` $\to$ 「全トランスフォーム」を適用。
   - モディファイアに **Mirror（X軸）** を追加し、アーマチュアモディファイアの上に配置。
   - [📸 参考: 04_c1_hand_mirror_modifier.jpg](../../docs/fusako_08_kemomimi_screenshots/04_c1_hand_mirror_modifier.jpg)
   - 手メッシュ $\to$ アーマチュアの順に複数選択し、**`Ctrl + P` $\to$ 「空のグループで（With Empty Groups）」** を実行。
   - **効果**: メッシュ側に `.R` の頂点グループが一括自動追加され、右腕のボーンを動かしても右手メッシュが正常に追従するようになる。
   - [📸 参考: 05_c1_parent_with_empty_groups_r.jpg](../../docs/fusako_08_kemomimi_screenshots/05_c1_parent_with_empty_groups_r.jpg)

---

### Part 2: 足と脚の接合 (03:55〜05:10)
1. **足メッシュの移動と統合**:
   - キーボード `4` で足コレクションへ移動し、足メッシュを `M` キーでメインコレクションへ移動。
   - 足メッシュ $\to$ 体メッシュの順に選択し、**`Ctrl + J` で統合**。
   - [📸 参考: 06_c2_foot_join_to_body_ctrl_j.jpg](../../docs/fusako_08_kemomimi_screenshots/06_c2_foot_join_to_body_ctrl_j.jpg)
2. **LoopTools Bridgeによる架橋**:
   - 編集モードで脚部下端の8頂点ループ、および足首上端の8頂点ループを `Shift + Alt + 左クリック` で同時選択。
   - 右クリック $\to$ **LoopTools > Bridge（ブリッジ）** を実行（ねじれが発生した場合は左下パネルの「Twist」を調整）。
   - 8頂点同士が完璧な四角面で架橋される。
   - [📸 参考: 07_c2_ankle_looptools_bridge.jpg](../../docs/fusako_08_kemomimi_screenshots/07_c2_ankle_looptools_bridge.jpg)

---

### Part 3: 手と腕の接合 (05:10〜07:35)
1. **手首開口部の8頂点化**:
   - 腕側が「8頂点」であるのに対し、手首側が10頂点になっている場合、手首内側の不要なエッジを選択し、`X` $\to$ 「辺を溶解（Dissolve Edges）」または「崩壊（Collapse）」を実行して **正確に「8頂点」** に揃える。
   - [📸 参考: 08_c3_wrist_reduce_to_8verts.jpg](../../docs/fusako_08_kemomimi_screenshots/08_c3_wrist_reduce_to_8verts.jpg)
2. **統合とBridge架橋**:
   - 手メッシュと体メッシュを選択し、**`Ctrl + J` で統合**。
   - [📸 参考: 09_c3_arm_join_ctrl_j.jpg](../../docs/fusako_08_kemomimi_screenshots/09_c3_arm_join_ctrl_j.jpg)
   - 腕下端の8頂点ループと手首上端の8頂点ループを選択し、右クリック $\to$ **LoopTools > Bridge** を実行。
   - [📸 参考: 10_c3_wrist_looptools_bridge.jpg](../../docs/fusako_08_kemomimi_screenshots/10_c3_wrist_looptools_bridge.jpg)
   - 接合部のくびれ・凹凸を `Alt + S` でふっくら均等に整流。
   - [📸 参考: 11_c3_wrist_curvature_relax.jpg](../../docs/fusako_08_kemomimi_screenshots/11_c3_wrist_curvature_relax.jpg)

---

### Part 4: 膝・脇・胴体ディテール (07:35〜13:10)
1. **膝蓋骨（膝小僧）の形成**:
   - 膝前面の面を選択し、**`I`（インセット）** を実行。
   - [📸 参考: 12_c4_knee_inset_patella.jpg](../../docs/fusako_08_kemomimi_screenshots/12_c4_knee_inset_patella.jpg)
   - 中央頂点を `Alt + S` で前方に盛り上げ、カクッとした膝の立体感を作る。
   - [📸 参考: 13_c4_knee_alts_bump.jpg](../../docs/fusako_08_kemomimi_screenshots/13_c4_knee_alts_bump.jpg)
2. **脇下のくぼみ形成**:
   - 脇下にループカットを追加し、ナイフツール（`K`）でエッジを切り込んで内側をくぼませ、外側を膨らませる。
   - [📸 参考: 14_c4_armpit_knife_topology.jpg](../../docs/fusako_08_kemomimi_screenshots/14_c4_armpit_knife_topology.jpg)
3. **お腹・ウエストの肉感増強**:
   - 胴体の横ループを `Ctrl + Alt + 左クリック` でリング選択し、右クリック $\to$ **細分化（Subdivide）**。左下の「スムースネス（Smoothness）」を上げて自然な膨らみを持たせる。
   - [📸 参考: 15_c4_belly_subdivide_smoothness.jpg](../../docs/fusako_08_kemomimi_screenshots/15_c4_belly_subdivide_smoothness.jpg)

---

### Part 5: ケモ耳（猫耳）モデリング (13:10〜27:08)
1. **外耳（耳ベース）の作成**:
   - `Shift + A` $\to$ **メッシュ > 平面（Plane）** を追加。
   - `R X 90` で正面に向け、上辺を `E Y` で前に押し出して三角断面にする。
   - [📸 参考: 16_c5_kemomimi_plane_base.jpg](../../docs/fusako_08_kemomimi_screenshots/16_c5_kemomimi_plane_base.jpg)
   - 稜線エッジにクリース（`Shift + E = 1.0`）を設定し、`Ctrl + 1` で Subsurf を追加。頭部にぶっ刺し配置。
   - [📸 参考: 17_c5_kemomimi_crease_subsurf.jpg](../../docs/fusako_08_kemomimi_screenshots/17_c5_kemomimi_crease_subsurf.jpg)
2. **Solidify ＋ 頂点ウェイトグラデーション**:
   - 耳に **Solidify（ソリッド化）** モディファイアを追加。
   - [📸 参考: 18_c5_solidify_modifier.jpg](../../docs/fusako_08_kemomimi_screenshots/18_c5_solidify_modifier.jpg)
   - 新規頂点グループ `Ear_Weight` を作成。
   - ウェイトペイントモードに入り、`Alt + 左ドラッグ` で根元（1.0）から先端（0.0）へのグラデーションを塗る。
   - Solidifyモディファイアの「頂点グループ」に指定し、根元が厚く先端が薄い自然な耳肉厚を生成。
   - [📸 参考: 19_c5_solidify_vertex_weight_gradient.jpg](../../docs/fusako_08_kemomimi_screenshots/19_c5_solidify_vertex_weight_gradient.jpg)
3. **耳毛（内側の毛束）の作成と配置**:
   - Cubeの側面を削除し、`R X 45` でひし形断面にした毛束パーツを作成。
   - [📸 参考: 20_c5_ear_fur_rhombus_cube.jpg](../../docs/fusako_08_kemomimi_screenshots/20_c5_ear_fur_rhombus_cube.jpg)
   - `Shift + D` で複製し、ランダムに向きを変えながら耳の内側にぶっ刺し配置。
   - [📸 参考: 21_c5_ear_fur_clusters_placement.jpg](../../docs/fusako_08_kemomimi_screenshots/21_c5_ear_fur_clusters_placement.jpg)
4. **仕上げ**:
   - Solidify適用後、耳内側の不要面を削除。
   - [📸 参考: 22_c5_solidify_apply_inner_face_cleanup.jpg](../../docs/fusako_08_kemomimi_screenshots/22_c5_solidify_apply_inner_face_cleanup.jpg)
   - 耳外縁を細分化し、先端の尖った毛束を `E` 押し出しで形成。
   - [📸 参考: 23_c5_ear_tip_fluff_extrude.jpg](../../docs/fusako_08_kemomimi_screenshots/23_c5_ear_tip_fluff_extrude.jpg)
   - Mirrorモディファイアで左右対称配置し、全体の完成パースを確認。
   - [📸 参考: 24_c5_kemomimi_complete_persp.jpg](../../docs/fusako_08_kemomimi_screenshots/24_c5_kemomimi_complete_persp.jpg)

---

## 5. 必須テクニック＆ショートカット早見表

| ショートカット / 機能 | 操作名称 | 本チュートリアルでの用途 |
| :--- | :--- | :--- |
| `Alt + R` / `Alt + G` | ポーズクリア | ボーンの回転・位置を初期化し、正確なTポーズに戻す |
| 右クリック $\to$ Names > AutoName | 左右自動ネーミング | ボーン末尾に `.L` / `.R` を自動付与し、対称化の準備をする |
| 右クリック $\to$ Symmetrize | 対称化 | 左半身のボーン構造から右半身のボーンを完全幾何対称に一発生成する |
| `Ctrl + P` $\to$ With Empty Groups | 空のグループで再ペアレント | Mirrorモディファイア追加時、反対側（.R）の頂点グループを一括自動生成する |
| `LoopTools > Bridge` | ブリッジ架橋 | 手首（8頂点）と腕（8頂点）、足首（8頂点）と脚（8頂点）を四角面で完全溶接する |
| ウェイトグラデーション塗 | Alt + 左ドラッグ | リニアなウェイト減衰を塗り、Solidifyの厚みを根本から先端へ無段階変化させる |

---

## 6. 本プロジェクト（AnimeFace / 素体パイプライン）との連動・実装指針

1. **ベース素体（Headless Body）の完全完成**:
   - 本仕様書により、胴体（第4回）、腕（第4回）、手（第5・6回）、脚（第4回）、足（第7回）が1つのオブジェクトとして完全に一体化しました。
   - 首元開口部（8〜12頂点）は、頭部（第1回 / `v04J` / AnimeFace）と同一規格となっており、将来の頭体統合も `LoopTools Bridge` またはマージで即座に接合可能です。
2. **獣耳・アクセサリーパイプライン**:
   - 本仕様書の Part 5（Solidify＋ウェイトグラデーション）は、猫耳・狐耳・ウサギ耳などのケモ耳パーツだけでなく、リボン・襟・スカートの裾などの厚み制御にも全く同じ手法が転用可能です。
