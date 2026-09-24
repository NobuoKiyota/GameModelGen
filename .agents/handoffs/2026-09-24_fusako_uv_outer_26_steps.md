# ふさこ氏 Blenderキャラクター制作 #26『アウターのUV展開』完全技術仕様書

元動画: [Blenderでキャラクターモデル制作！#26 | アウターのUV展開 〜初中級者向けチュートリアル〜](https://www.youtube.com/watch?v=pueKgjxwIyI)  
動画ID: `pueKgjxwIyI` / 再生時間: 18分11秒  
対象バージョン: Blender 3.6+ / 4.x 対応  
スクリーンショットカタログ: [docs/fusako_26_uv_outer_screenshots/README.md](../../docs/fusako_26_uv_outer_screenshots/README.md)

---

## 1. 概要とアウターUV展開の基本戦略

本チュートリアル（UV展開編 第4回）では、複雑な形状と厚みを持つ「アウター（パーカー・ジャケット・フード・袖）」のUV展開を体系的に行います。  
アウター特有の課題である「厚み付け（Solidify）による歪み」「フードの直線ストライプ模様への対応」「重なり合うフチ（前立て・ファスナー）のトポロジー調整」「左右対称パーツのUV重ね（UV Overlapping）によるテクセル解像度向上」を完全攻略します。

[📸 参考: fusako26_01_outer_overview.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_01_outer_overview.jpg)

### アウターUV展開のコア原則
1. **色の切り替わりラインにシームを打つ**: フード外側/内側、袖のツートンカラー境界など、テクスチャの塗り分け線に正確にシームを配置する。
2. **直線の柄・ステッチが入る箇所は長方形格子化（Rectify）**: フード中央や前立てなど、縦横のストライプやステッチが走る部分はTexToolsの `Rectify` ＋ピン留め（`P`）で格子状に整列。
3. **厚み面の歪み解消法（選択縮小＋ピン留め再展開）**: 表面だけを展開・ピン留めしてから厚みを含めて再展開し、表面のメインテクスチャの伸び縮みを完全に防止する。
4. **見えない裏地・インナー面は50%縮小（S 0.5）**: テクセル密度を統一後、影面・裏面を半分の面積にしてUV空間を大幅節約。
5. **左右対称テクスチャのUV重ね（UV Overlapping）**: 左右で同一の柄（無地・対称デザイン）はUVを同一座標に重ね、解像度を2倍稼ぐ。非対称柄のあるパーツのみ独立配置。

---

## 2. フードのUV展開とRectify直線化

### 2.1 フードのシーム設定
1. フードの外側と内側（裏地）で色が切り替わるエッジを選択し、`Ctrl+E > Mark Seam`（マークシーム）。
2. 不要なシームが残っている場合は `Ctrl+E > Clear Seam` でクリアする。
3. 猫耳パーツがついている場合は、フード本体から切り離せるように境界エッジにシームを打つ。

[📸 参考: fusako26_02_hood_seam_marking.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_02_hood_seam_marking.jpg)

### 2.2 猫耳パーツの表裏分割と初期展開
1. 猫耳の表面と裏面を分ける外周エッジにマークシームを入れる。
2. `A` で全選択し、`U > Unwrap`（展開）を実行して形状を確認する。

[📸 参考: fusako26_03_hood_unwrap_check.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_03_hood_unwrap_check.jpg)

### 2.3 フード中央部のTexTools Rectify（長方形格子化）
1. テクスチャで縦のストライプ線や縫い目ラインを描きやすくするため、歪んだUVをまっすぐに補正する。
2. まっすぐに揃えたいフード中央部（エッジループ）の面を選択。
3. TexTools パネルから `Rectify` を実行し、直角の格子状に整列させる。

[📸 参考: fusako26_04_string_rectify.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_04_string_rectify.jpg)

### 2.4 ピン留め（P）と再展開によるリラックス
1. Rectify でまっすぐに整列した頂点群を選択し、`P` キーでピン留め（赤色表示）。
2. その状態で島全体を選択し、再度 `U > Unwrap` を実行。
3. 直線化した中央ラインを基準に、周囲のメッシュが自然なテンションでリラックス（歪み緩和）される。
4. 端部の微妙なズレは、UVエディター上で `S Y 0` や `S X 0` を使って手動で直線化を仕上げる。

[📸 参考: fusako26_05_string_pin_relax.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_05_string_pin_relax.jpg)

### 2.5 猫耳パーツの厚み歪み解消（選択縮小テクニック）
1. 猫耳パーツに厚みがある場合、単純展開するとフチの厚み面によって表面が引っ張られて歪む。
2. 3Dビューポートで猫耳を `L` で選択。
3. `Ctrl + NumPad Minus`（テンキーのマイナス）を押して選択範囲を1段縮小し、厚みフチ面を除外した「表面のみ」を選択。
4. この状態で `U > Unwrap` $\to$ UVエディターで `P`（ピン留め）。
5. 3Dビューポートで `Ctrl+L`（または全選択）して厚み面を含めた状態で再度 `U > Unwrap`。表面のプロポーションを維持したまま厚み面だけが外側に綺麗に展開される。

[📸 参考: fusako26_06_body_shoulder_side_seam.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_06_body_shoulder_side_seam.jpg)

### 2.6 フード裏地の展開
1. フード内側の裏地面は、基本的にベタ塗り（単色）となるため、歪みを極度に神経質にならずに素早く展開する。
2. まっすぐに整列できそうな部分を選択し、`Rectify` $\to$ `P`（ピン留め） $\to$ `U > Unwrap` でスピーディに展開する。

[📸 参考: fusako26_07_sleeve_seam_unwrap.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_07_sleeve_seam_unwrap.jpg)

---

## 3. UV確認用シェーダーの設定と仮パッキング

### 3.1 マテリアルのアサインとシェーダーノード構築
1. マテリアルスロットに新規マテリアル「M_Outer」を作成。
2. インナー用マテリアル（第25話で作成した UV Grid ＋ RGB Curves）のノード群を `Ctrl+C` でコピーし、`Ctrl+V` で貼り付け。
3. RGB Curves ノードで R（赤）と G（緑）の曲線を持ち上げ、黄色（Yellow）のチェッカーグリッドに変更。
4. 他のアウターパーツ（フード、袖、身頃）を選択し、最後にマテリアル設定済みパーツを選択して `Ctrl+L > Link Materials` で一括アサイン。

[📸 参考: fusako26_08_material_color_assign.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_08_material_color_assign.jpg)

### 3.2 歪み・アサインの視覚確認
1. 3Dビューポートをマテリアルプレビューモードにし、黄色いUVグリッドの四角形が正方形を保っているか目視確認する。
2. 引き伸ばしや歪みが発生している箇所を特定し、後工程でシーム追加やピン留め補正を行う。

[📸 参考: fusako26_09_rib_cuff_unwrap.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_09_rib_cuff_unwrap.jpg)

---

## 4. 身頃と袖の展開・Solidifyモディファイア適用

### 4.1 身頃（前身頃・後身頃）の展開
1. 肩の縫い目、脇下の縫い目に沿ってシームを入れる。
2. 前身頃と後身頃が綺麗に左右対称で2枚に分かれるように `U > Unwrap`。

[📸 参考: fusako26_10_solidify_distortion_check.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_10_solidify_distortion_check.jpg)

### 4.2 袖の厚み付け（Solidify）モディファイアの確定適用
1. **重要事前チェック**: 手を「パー」に開いた状態で親指と袖口が貫通していないかポーズを確認し、必要なら頂点を微調整しておく。
2. モディファイアプロパティから、袖の `Solidify` モディファイアを適用（Apply / `Ctrl+A`）。
3. 適用後、袖口の内側と外側を分ける境界エッジループを選択し、`Ctrl+E > Mark Seam`。

[📸 参考: fusako26_11_solidify_rim_seam.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_11_solidify_rim_seam.jpg)

### 4.3 袖のカラー切り替えシーム
1. 袖の上下（紫と白などのツートンカラー境界）に沿ってエッジを選択し、マークシーム。
2. 三角面化している箇所は `Ctrl + クリック`（最短パス選択）を活用して確実にエッジパスを選択する。

[📸 参考: fusako26_12_pocket_seam_marking.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_12_pocket_seam_marking.jpg)

### 4.4 袖の厚み歪み解消プロセス（完全実演）
1. 単純展開すると、Solidifyで生じたフチの厚みメッシュに引っ張られて極端な歪み（扇状の伸び）が発生する。
2. 3Dビューポートで袖パーツを `L` で選択 $\to$ `Ctrl + NumPad Minus` で厚みフチを除外し、表面だけを選択。
3. `U > Unwrap` を実行。

[📸 参考: fusako26_13_pocket_unwrap_relax.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_13_pocket_unwrap_relax.jpg)

4. UVエディターで展開結果を `P` でピン留め。
5. 3Dビューポートで `Ctrl+L` で厚み面を含めて全選択し、再度 `U > Unwrap`。
6. 上側の袖パーツ、下側の袖パーツともにこの手法を適用することで、完全に均一で歪みのないアイランドを生成できる。

[📸 参考: fusako26_14_inner_shrink_pin_unwrap.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_14_inner_shrink_pin_unwrap.jpg)

### 4.5 袖裏地のテクセル縮小と向き揃え
1. `UV > Average Islands Scale` でテクセル実寸を統一。
2. ほとんど見えない袖の内側（裏地）パーツを 3Dビューポートで `L` 選択。
3. UVエディター上で `S 0.5`（50%縮小）を実行。
4. 各パーツの上下左右の向きを揃え、`UV > Pack Islands`（※`Rotate` のチェックを外す）を実行して向きを維持したまま仮パッキングする。

[📸 参考: fusako26_15_uv_island_rotation_align.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_15_uv_island_rotation_align.jpg)

---

## 5. 前立て・ファスナー（ジッパー）のトポロジー調整と展開

### 5.1 重なり部分のシームとトポロジー問題の検出
1. アウター前面のファスナーや前立ての重なり合うフチ部分にシームを入れる。
2. 展開した際、不自然に歪んだり余分なスペースを占有してしまう場合は、メッシュトポロジー（エッジの流れ）に原因がある。

[📸 参考: fusako26_16_zipper_seam_unwrap.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_16_zipper_seam_unwrap.jpg)

### 5.2 エッジ回転（Rotate Edge CW）と頂点結合（J）によるトポロジー改善
1. メッシュの対角線エッジを選択し、`右クリック > Rotate Edge CW`（時計回りにエッジ回転）を実行して流れを縫い目方向に合わせる。
2. 不自然な頂点配置がある箇所は、エッジを細分化（`Subdivide`）し、頂点同士を選択して `J` キー（頂点パスを連結）で綺麗な四角形ポリゴンフローを再構築する。
3. 不要になったエッジは `X > Dissolve Edges`（辺を溶解）で整理。

[📸 参考: fusako26_17_zipper_straighten_grid.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_17_zipper_straighten_grid.jpg)

### 5.3 曲がり角のシーム追加と直線化
1. 長く折れ曲がったフチメッシュは、曲がり角にシームを追加して「横ライン」「縦ライン」に分割する。
2. 各パーツが直線的な帯状になり、UV領域の無駄なデッドスペースが大幅に削減される。

[📸 参考: fusako26_18_hood_lining_unwrap.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_18_hood_lining_unwrap.jpg)

### 5.4 TexTools Rectify と目視微調整
1. 直線帯状になったパーツを選択し、TexTools の `Rectify` で格子状に整列 $\to$ `P`（ピン留め） $\to$ 再展開。
2. UVエディターと3Dビューポートを見比べながら、伸び縮みが最小限になるようにエッジ位置を微調整する。

[📸 参考: fusako26_19_textools_rectify_relax.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_19_textools_rectify_relax.jpg)

---

## 6. 全体パッキングと左右対称UV重ね（UV Overlapping）

### 6.1 UV Average Islands Scale の実行
1. アウターを構成する全メッシュパーツを `A` で全選択。
2. UVエディターのメニューから `UV > Average Islands Scale`（アイランドの平均スケール）を実行し、3Dモデルの実寸とUV比率を1:1に揃える。

[📸 参考: fusako26_20_average_island_scale.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_20_average_island_scale.jpg)

### 6.2 裏地・インナー面の一括50%縮小
1. ピボットポイントをキーボードの `.`（ピリオド）から「それぞれの原点（Individual Origins）」に変更。
2. 島選択モードにし、フード裏地、袖裏地、身頃裏地などの「見えない裏地面」を一括選択。
3. `S 0.5` を入力して各島の中心を基準に50%縮小。
4. `UV > Pack Islands` で大まかに四角いUV境界内に収める。

[📸 参考: fusako26_21_uv_pack_layout_init.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_21_uv_pack_layout_init.jpg)

### 6.3 左右非対称パーツと左右対称パーツの選定
1. **左右非対称パーツ（独立UV）**:
   - 厚みフチの一部や、左右で異なる柄・エンブレム・ジッパー金具が付くパーツ。
2. **左右対称パーツ（UV重ね Overlapping）**:
   - 身頃の左右、袖の左右など、同一テクスチャで解像度を稼ぎたいメインパーツ。

[📸 参考: fusako26_22_symmetry_overlap_prep.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_22_symmetry_overlap_prep.jpg)

### 6.4 UV同期選択を活用した結合・整列
1. UVエディター左上の「UV選択の同期（UV Sync Selection）」アイコンをオンにする。
2. 対称となるパーツのエッジを選択して対応関係を確認。
3. 一旦同期をオフにし、TexTools の整列機能（左寄せ・右寄せ・下寄せ）を活用して、左右対称の島を完全に重ね合わせる。
4. エッジが重複して描画乱れが起きないよう、境界の頂点位置を精密に合わせる。

[📸 参考: fusako26_23_symmetry_overlap_align.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_23_symmetry_overlap_align.jpg)

### 6.5 テクスチャ解像度の優先度再調整と最終レイアウト
1. **セーター柄・編み込み模様の入るパーツ**: 書き込み密度が高いため、手動で少し拡大（`S 1.1〜1.2`）してテクセル解像度をブースト。
2. **袖の無地パーツ**: 書き込みが少ないため、若干縮小してスペースを譲る。
3. 0〜1の正方形テクスチャ枠内に無駄な余白（デッドスペース）が生じないよう、パズルのように綺麗に配置を完了する。

[📸 参考: fusako26_24_final_outer_uv_layout.jpg](../../docs/fusako_26_uv_outer_screenshots/fusako26_24_final_outer_uv_layout.jpg)

---

## 7. トラブルシューティング＆チェックリスト

| 症状 / 課題 | 原因 | 解決策 |
|:---|:---|:---|
| フードのストライプ模様が歪む | 単純展開による曲線変形 | TexTools `Rectify` で格子化後、`P` でピン留めしてから `U > Unwrap`。 |
| 袖口の厚み面を展開すると表面が伸びる | Solidifyモディファイアによる拘束 | `Ctrl + NumPad Minus` で表面のみ選択展開 $\to$ `P` ピン留め $\to$ 全選択再展開。 |
| ファスナー周りのUVが扇状に広がる | 四角ポリゴン対角線の向きの不一致 | `右クリック > Rotate Edge CW` または `Subdivide` ＋ `J` でトポロジーを整列。 |
| フチの帯がUV領域を圧迫する | 1本の長いループとして展開されている | 角（コーナー）にシームを追加し、縦・横の直線帯に分割してデッドスペースを撲滅。 |
| 左右対称パーツを重ねるとテクスチャが反転する | UVアイランドの表裏向き（Flip） | 左右反転している側を UVエディター上で `S X -1`（X軸反転）してから整列・重ね合わせ。 |
