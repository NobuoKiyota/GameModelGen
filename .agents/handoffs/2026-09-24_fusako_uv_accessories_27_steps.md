# ふさこ氏 Blenderキャラクター制作 #27『ヘアアクセなど小物のUV展開』完全技術仕様書

元動画: [Blenderでキャラクターモデル制作！#27 | ヘアアクセなど小物のUV展開 〜初中級者向けチュートリアル〜](https://www.youtube.com/watch?v=p4N6kfBLOVc)  
動画ID: `p4N6kfBLOVc` / 再生時間: 39分00秒  
対象バージョン: Blender 3.6+ / 4.x 対応  
スクリーンショットカタログ: [docs/fusako_27_uv_accessories_screenshots/README.md](../../docs/fusako_27_uv_accessories_screenshots/README.md)

---

## 1. 概要と小物UV展開・UV展開編総まとめ

本チュートリアル（UV展開編 第5回・完結回）では、キャラクターモデル制作における多種多様なアクセサリー・小物類（リボン、羽、パッチン留め、フードボタン、尻尾、ポシェット、キャンティーンバッグ、各種紐類）のUV展開を行い、全5回にわたるUV展開プロセスを完全に完成させます。

[📸 参考: fusako27_01_accessories_material_init.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_01_accessories_material_init.jpg)

### 小物UV展開の重要ポイント
1. **小物専用カラー識別マテリアルの構築**: 水色（Cyan）のUV Gridシェーダーを一括アサインし、他パーツ（顔・髪・服・アウター）との混同を防止。
2. **2重ミラーモディファイアの階層的適用**: 左右対称用とワールド配置用で2重にかかっているミラーのうち、1段目のみを適用してUVを展開する。
3. **リンク複製（Alt+D）オブジェクトのSingle User化**: Solidify適用時に警告が出るため、確実にリンクを解除して適用する。
4. **【神Tips】Magic UVアドオンによるUVコピー＆ペースト**: 対称・同一構造のパーツ（パッチン留めなど）において、一方のUV展開・シーム・ピン留めをもう一方へ100%自動複製。
5. **類似選択（Shift+G > Sharpness）によるシーム一括作成**: マークシャープを打ったエッジを一発でマークシーム化。
6. **不均等スケール警告とCtrl+A Scale適用**: UV比率の歪みを防ぐための全オブジェクトスケール統一。
7. **Display Stretch（Area）機能によるテクセル密度・歪み診断**: UVエディター上で青〜水色表示（適正値）を目視確認。
8. **長い紐パーツの分割と裏地50%縮小（S 0.5）**: 肩紐などをコーナーで分割し、裏地を極小化してUV領域を節約。
9. **主要書き込みパーツ（ポシェット・おにぎり・顔）の優先拡大**: テクスチャ書き込みが多い島を手動で拡大し、最終テクスチャ品質を最大化。

---

## 2. 小物専用マテリアルの設定とリボンの展開

### 2.1 小物マテリアルのアサイン
1. アウトライナーで「Accessories」コレクションを表示。
2. 既存のHairマテリアルを複製し、名前を「M_Accessories」に変更。
3. シェーダーエディターで RGB Curves の B（青）と G（緑）を引き上げ、水色（Cyan）のチェッカーグリッドに変更。
4. コレクション内の全小物オブジェクトを選択し、最後に設定済みオブジェクトをアクティブ選択して `Ctrl+L > Link Materials` で一括アサイン。

[📸 参考: fusako27_01_accessories_material_init.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_01_accessories_material_init.jpg)

### 2.2 リボン（2重ミラー）の展開
1. リボンは形状自体の左右対称用ミラーと、頭部左右配置用ミラーの2重構成になっている。
2. 形状自体の1段目ミラーモディファイアのみを適用（`Ctrl+A`）。
3. 表と裏を分ける外周エッジに `Ctrl+E > Mark Seam`。
4. `U > Unwrap` で展開する。

[📸 参考: fusako27_02_ribbon_mirror_seam.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_02_ribbon_mirror_seam.jpg)

---

## 3. パッチン留めの展開とMagic UVによるコピー＆ペースト

### 3.1 リンク複製（Alt+D）の解除とSolidify適用
1. `Alt+D` で複製されたオブジェクトにモディファイアを適用しようとすると「Make Object Data Single User」警告が出る。
2. 警告をクリックしてシングルユーザー化（リンク解除）してから `Solidify` モディファイアを適用。

[📸 参考: fusako27_03_clip_solidify_single_user.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_03_clip_solidify_single_user.jpg)

### 3.2 花飾りの厚み歪み解消
1. 花飾りパーツの表裏境界にシームを入れる。
2. 表面を選択し、`Ctrl + NumPad Minus` で厚み面を除外 $\to$ `U > Unwrap` $\to$ `P`（ピン留め）。
3. `Ctrl+L` で厚み面を含めて全選択し、再展開（`U > Unwrap`）。

[📸 参考: fusako27_04_clip_shrink_pin_unwrap.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_04_clip_shrink_pin_unwrap.jpg)

### 3.3 パッチン留め本体のシーム追加と手動直線補正
1. パッチン留め本体のフチと厚み境界にマークシーム。
2. 展開後、歪みが残る箇所は UVエディター上で `S Y 0` や `S X 0`、TexTools の整列機能を使って直線化し、ピン留めして再展開する。

[📸 参考: fusako27_05_clip_seam_manual_straighten.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_05_clip_seam_manual_straighten.jpg)

### 3.4 【神技】Magic UVアドオンによるUVコピー＆ペースト
1. **コピー元**: 綺麗にUV展開が完了したパッチン留めを全選択（`A`）。
2. `U > Copy/Paste UV > Copy UV Map` を実行。

[📸 参考: fusako27_06_magic_uv_copy_uv_map.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_06_magic_uv_copy_uv_map.jpg)

3. **ペースト先**: 反対側の未展開パッチン留めを選択（Solidify適用済み）。
4. 全選択して `U > Copy/Paste UV > Paste UV Map` を実行。
5. **結果**: シームの配置、展開形状、ピン留め状態が完全に自動再現される。
6. ペースト後は UVエディター上で `G X` または `G Y` で少しずらし、重なりを回避する。

[📸 参考: fusako27_07_magic_uv_paste_uv_map.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_07_magic_uv_paste_uv_map.jpg)

---

## 4. フードボタン・尻尾・キャンティーンバッグの展開

### 4.1 ボタンと尻尾（Tail）の展開
1. ボタンは表裏シームを入れ、選択縮小＋ピン留め展開。
2. 尻尾は下面の見えないラインに沿ってシームを入れ、TexTools `Rectify` で格子化してピン留め再展開。

[📸 参考: fusako27_08_button_tail_seam_unwrap.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_08_button_tail_seam_unwrap.jpg)

### 4.2 キャンティーンバッグ：Shift+G によるシャープ辺一発シーム化
1. マークシャープが設定されているエッジを1本選択。
2. `Shift + G > Sharpness`（シャープ）を実行。モデル上のすべてのマークシャープエッジが一括選択される。
3. `Ctrl + E > Mark Seam` で一発シーム化。
4. ミラーモディファイアを適用し、側面にもシームを追加。

[📸 参考: fusako27_09_shift_g_select_sharp_edges.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_09_shift_g_select_sharp_edges.jpg)

### 4.3 不均等スケール警告と Ctrl+A Scale 適用
1. 展開時に「オブジェクトのスケールが均一ではありません」と警告が出た場合、3D空間とUVの比率が狂ってしまう。
2. オブジェクトモードで `Ctrl + A > Scale`（全トランスフォーム / スケール適用）を実行。
3. 再度展開すると、正しい比率でアイランドが生成される。

[📸 参考: fusako27_10_scale_apply_fix.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_10_scale_apply_fix.jpg)

### 4.4 ジッパー・メインパーツの展開と整列
1. ジッパーの奥側エッジにシームを配置。
2. 表面のみ選択してピン留め展開。
3. TexTools の垂直整列（Align Vertical）・水平整列（Align Horizontal）で直角格子に整え、メインパーツと `Ctrl + J` でオブジェクト結合。

[📸 参考: fusako27_11_zipper_pin_unwrap.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_11_zipper_pin_unwrap.jpg)
[📸 参考: fusako27_12_zipper_textools_align_join.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_12_zipper_textools_align_join.jpg)

### 4.5 肩紐のSolidify適用前展開と表裏分離
1. 紐メッシュは Solidify 適用前に展開し、縦ループを選択して TexTools で直角化しておくと歪みが出ない。
2. `Ctrl + A` で Solidify 適用後、外周ループにシーム追加。
3. 表面を選択縮小してピン留め再展開し、裏面UVを `G X` で横にずらして分離。メインパーツと `Ctrl + J` で結合。

[📸 参考: fusako27_13_strap_pre_unwrap_straighten.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_13_strap_pre_unwrap_straighten.jpg)
[📸 参考: fusako27_14_strap_solidify_shrink_pin.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_14_strap_solidify_shrink_pin.jpg)

---

## 5. ウサギポシェットの展開とテクスチャ歪み診断

### 5.1 ウサギポシェットのシームと展開
1. 表・裏・蓋・側面・耳の各境界にマークシームを入れる。
2. 2段あるミラーモディファイアのうち、上段ミラーのみ適用。
3. 側面や耳の厚み部分に対し、選択縮小＋ピン留め再展開を適用して歪みを根絶。

[📸 参考: fusako27_15_rabbit_pouch_seam_prep.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_15_rabbit_pouch_seam_prep.jpg)
[📸 参考: fusako27_16_rabbit_pouch_shrink_pin_unwrap.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_16_rabbit_pouch_shrink_pin_unwrap.jpg)

### 5.2 ポシェット紐のRectify格子化とスケール調整
1. ポシェット紐の中央・ループ部分にシームを入れ、TexTools `Rectify` で格子化。
2. 3Dビューポートの正方形グリッドを目視しながら、UVエディター上で `S Y` で縦横比率を適正に調整。
3. 全パーツを `Ctrl + J` で結合し、裏地パーツを `S 0.5` 縮小。

[📸 参考: fusako27_17_pouch_strap_rectify_scale.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_17_pouch_strap_rectify_scale.jpg)
[📸 参考: fusako27_18_pouch_join_inner_s05.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_18_pouch_join_inner_s05.jpg)
[📸 参考: fusako27_19_ribbon_pouch_pack_layout.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_19_ribbon_pouch_pack_layout.jpg)

### 5.3 【神Tips】Display Stretch（歪み診断）の活用法
1. UVエディターの右側パネル（オーバーレイ / 表示設定）から **`Display Stretch`（ストレッチ表示）** を有効化。
2. モードを **`Area`（面積）** または `Angle`（角度）に切り替える。
3. **診断基準**:
   - **水色〜青色**: 歪みがなく、3Dメッシュとテクセル面積が完全に一致している理想状態。
   - **緑〜黄色〜赤色**: 引き伸ばされ、または縮小されすぎて歪みが生じている状態。
4. この診断を見ながら、スケール適用漏れや異常なアイランドを瞬時に特定・修正する。

[📸 参考: fusako27_20_display_stretch_distortion_view.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_20_display_stretch_distortion_view.jpg)

---

## 6. 全小物パッキング・テクセル解像度最適化・UV編完結

### 6.1 長い肩紐の分割シーム追加
1. キャンティーンバッグの肩紐など、極端に長いパーツはUV領域を対角線状に横断してデッドスペースを生む。
2. 目立たない肩頂点付近にシームを追加して前後に分割。
3. アイランドがコンパクトな長方形になり、パッキング効率が劇的に向上する。

[📸 参考: fusako27_21_shoulder_strap_split_seam.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_21_shoulder_strap_split_seam.jpg)

### 6.2 塗りやすさを考慮した上下向き揃え
1. キャンティーンバッグの顔・耳パーツ、ポシェットなど、ペイント時に上下関係が重要なパーツは、3D空間の見た目と一致するように回転（`R 90` / `R 180`）して向きを揃える。
2. UV Sync Selection（同期選択）を活用して対応する面を確認しながら配置。

[📸 参考: fusako27_22_canteen_bag_align_orientation.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_22_canteen_bag_align_orientation.jpg)

### 6.3 テクセル密度の優先度ブースト（Priority Boost）
1. 全パーツを選択して `UV > Average Islands Scale` を実行。
2. **書き込み優先度が高いパーツ（拡大 `S 1.1〜1.3`）**:
   - 顔付きキャンティーンバッグ、おにぎり柄、ポシェット蓋など、細かい模様・ロゴが入る面。
3. **優先度が低いパーツ（縮小 `S 0.5〜0.8`）**:
   - 見えない裏地、内側メッシュ、単色ベタ塗りの金具など。
4. 空いた隙間に無駄なく敷き詰める。

[📸 参考: fusako27_23_scale_match_priority_boost.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_23_scale_match_priority_boost.jpg)

### 6.4 全モデルUV展開の完全完成
1. 全コレクション（顔・髪・素体・服・アウター・小物）の非表示を解除。
2. 各マテリアル（赤・緑・青・黄・水色）のUV Gridが歪みなく正方形で表示されていることを3Dビューポートで最終確認。
3. これにより、全5回にわたるUV展開フェーズが完全完了し、次フェーズ「Substance Painter テクスチャペイント編」への完全な準備が整った。

[📸 参考: fusako27_24_final_all_characters_uv_complete.jpg](../../docs/fusako_27_uv_accessories_screenshots/fusako27_24_final_all_characters_uv_complete.jpg)

---

## 7. トラブルシューティング＆チェックリスト

| 症状 / 課題 | 原因 | 解決策 |
|:---|:---|:---|
| モディファイア適用時に警告が出る | `Alt+D` によるリンク複製 | メッセージをクリックして `Make Single User`（リンク解除）してから適用。 |
| 対称パーツのシーム・展開をもう一度やるのが面倒 | 手動再作業の無駄 | **Magic UV** の `Copy UV Map` $\to$ `Paste UV Map` でシーム・形状を100%自動複製。 |
| マークシャープをシームにするのが大変 | 1本ずつ選択している | `Shift + G > Sharpness` で全シャープエッジを一括選択して `Ctrl+E > Mark Seam`。 |
| UVアイランドが異常に伸び縮みして展開される | オブジェクトの不均等スケール | オブジェクトモードで `Ctrl + A > Scale` を実行してスケールを `(1, 1, 1)` に適用。 |
| UVの歪みが目視で判断しづらい | チェッカーの目視限界 | UVエディターの `Display Stretch > Area` をオンにし、青色（適正）になっているか診断。 |
| 長い紐パーツがUV領域を圧迫する | 1本の長い島になっている | 肩の目立たない位置にシームを追加して分割し、直線状に整列。 |
