# [2026-09-18/19] Claude Code — procedural_rock_studio「西洋風アーチ扉」DOORプリセット＋破壊アニメーション

## 2026-09-19 追記2: UE向けボーン方式＋レベルシーケンス用セットアップを追加（UE実機は未検証）

ユーザーがBlenderで破壊アニメの見た目に満足し、「UEで再現しレベルシーケンスの任意タイミングで破壊したい」と依頼。方針は**破片ごとに1ボーンのスケルタルメッシュ**（シェイプキーだと回転しながら飛ぶ破片が補間で歪む/縮むため。UEのスタティックメッシュはモーフ非対応でもある）＋**手順書＋UE Pythonセットアップスクリプト**。

- `generate_door_destruction(..., bake_mode='BONES')` が既定に（`'SHAPEKEYS'`は従来動作を残存）。`utils/anim_baker.py` の `bake_object_group_to_armature`: 単一ルート`root`＋破片ごと`Shard_###`ボーン(parent=root)、頂点グループ=ウェイト1.0、毎フレームのlocation/rotation_quaternionをFカーブ直書き。子のbasis = `rest⁻¹ @ delta @ rest`（親rootはbasis固定なのでこの閉形式で決まる）。メッシュ/ボーン/デルタは**Door_Frameのローカル空間**で持ち、ArmatureオブジェクトにDoor_Frameのワールド行列を持たせてBlender上の見た目を維持。
- UIボタン「💥 木っ端微塵に破壊してUE用FBX一括出力」は `<export_folder>/<扉名>_UE/` に3ファイル出力: `_Frame.fbx`(石枠static) / `_LeavesIntact.fbx`(無傷の扉static。破壊メッシュのrestは破片の隙間でヒビ状に見えるため破壊時に入れ替える用) / `_Destruction.fbx`(スケルタル＋ボーンアニメ)。FBXは -Y forward / Z up、`FBX_SCALE_UNITS`、`add_leaf_bones=False`、`use_armature_deform_only=False`（rootを必ず出力）、Armatureは出力時のみ一時的に"Armature"名・原点へ。
- `ue_scripts/setup_door_destruction_sequence.py`: FBXインポート→アクター配置→レベルシーケンス作成→破壊時刻にアニメ配置＋Visibility切替。**各ステップをtry/exceptで囲み失敗時は手動手順をログ出力**（UE Python APIのバージョン差が大きく実機未検証のため）。手順書: `docs/UE_DoorDestruction_Guide.md`。
- 検証(Blenderで実施済み): `test_door_destruction_bones.py` — ボーン変形後の頂点と記録した剛体運動の最大誤差 6e-6 m、rootが1本、FBX再インポートでアーマチュア1/ボーン63/頂点グループ62/Fカーブ有/高さ一致、Door_Frameを移動+回転させても静的FBXが原点直立で出力。UI経由(`test_door_destruction_operator.py`)で3FBX出力、`test_door_destruction_repeat.py`もPASS。
- **未検証**: UEでのインポート結果（ルートボーン名・スケール・軸・アニメ取り込み）、UE Pythonスクリプト全般、Visibilityトラックのキー設定。エラーはOutput Logの文面をもらって修正する前提。
- マテリアルはプロシージャルノードが転送されないため、UEで`<扉名>_Stone_Mat/_Wood_Mat/_Iron_Mat`スロットへ手動割当て（またはAuto PBR Baker）。

## 2026-09-19 追記: 重大バグ修正済み（衝撃フレーム以降に元の姿勢へ固まって戻ってしまう不具合）

ユーザーが家のPCで実際に生成して確認したところ、「タイムラインを0→2→4→5とスクラブすると、5で完全に元の無傷な姿勢に戻ってしまう」不具合を発見・報告。徹底的に再現・原因究明・修正済み（詳細は以下）。**この修正は既にコミット済み・push済み**（`git log` でこのファイルの次のコミットを確認のこと）。

**原因**: `generate_door_destruction()` 内で、剛体シミュレーションを開始する基準フレーム（`cur_frame`）を `scene.frame_current`（＝呼び出した瞬間にユーザーがタイムライン上で見ていたフレーム）から取っていた。ところがBlenderの剛体(Rigid Body)シミュレーションは **`rigidbody_world.point_cache.frame_start`（既定=1）から連続してステップしないと正しく評価されない**（Bulletの内部状態がそこから積み上がっていく）。生成→タイムラインをスクラブして確認→もう一度生成、という普通の使い方をすると、2回目の呼び出し時点で `scene.frame_current` が1以外（例:15）になっており、そこから急に `frame_set()` してシミュレーションを進めると、**衝撃フレーム以降の物理演算の評価結果が初期値（ほぼ無傷の姿勢）に固まったまま変化しなくなる**、という不具合だった。

**再現方法**（`test_door_destruction_repeat.py` に回帰テストとして残してある）: 同じBlenderセッション内で `generate_door_destruction()` を1回実行→タイムラインを1,3,5,7,9,15とスクラブして確認→もう一度同じ関数を呼ぶ、という手順で100%再現した。

**修正内容**:
1. `cur_frame = scene.frame_current` → `cur_frame = rw.point_cache.frame_start` に変更（常に1から始める）。これが本質的な修正。
2. ついでに、衝撃の与え方も**キネマティック(直接アニメーション)からダイナミクスへ引き渡す方式をやめ**、「シミュレーション開始前に初期配置を衝撃点から放射状にランダム方向へあらかじめずらしておき、最初の`impact_frames`だけFORCEエフェクターで追加の後押しをする」方式に変更した（kinematic⇄dynamic切り替えを試している最中に別の再現しない不具合にも遭遇したため、より単純でトラブルの少ない方式に倒した）。
3. 剛体ワールド自体も毎回 `world_remove()`→`world_add()` で作り直すようにした（念のための保険。根本原因は上記1だが、これも安全側の変更として残している）。

以降のセクションはこの修正を反映して更新済み。

## 状況
ユーザーからの依頼で `procedural_rock_studio` アドオンに新カテゴリ **DOOR（西洋風アーチ両開き扉）** を追加し、続けて扉パネルを木っ端微塵に砕け散らせる**破壊アニメーション生成機能**を実装した。本セッションで完結しており、次回は動作確認・実機（UE）取り込み確認・さらなる演出調整から再開できる。

**重要**: このセッション中、他ツール（Antigravity/Gemini。`.agents/shared_log.md`参照）が同じリポジトリで別件（チビキャラ・人体スタディ）の作業をしており、無関係なコミット `e3d0289`（`feat(study): complete tutorial 01 head modeling...`）に**DOORプリセット本体（door_gen.py, core_orchestrator.py, image_shaders.py, generators/__init__.py, properties.py等のDOOR部分）が意図せず巻き込まれて既にpush済み**だった。本セッション終了時点でのコミットは**破壊アニメーション機能のみ**を対象にしている（詳細は次項）。

## 現在の状態（コミット区分）

### 既にpush済み（コミット `e3d0289`, 別ツールが巻き込みcommit）
- `blender_addons/procedural_rock_studio/generators/door_gen.py`（新規） — DOORプリセット本体
- `blender_addons/procedural_rock_studio/generators/core_orchestrator.py` — DOORディスパッチ配線
- `blender_addons/procedural_rock_studio/generators/__init__.py` — `generate_western_door` export
- `blender_addons/procedural_rock_studio/materials/image_shaders.py` — `create_door_wood_material` / `create_door_iron_material`
- `properties.py` / `ui/panel.py` / `ui/operators.py` の **DOORプリセット分**（`door_arch_style`〜`door_has_edge_trim`等）
- `test_door_addon.py`, `test_render_door_preset.png`

### 本セッションでこの後コミット＆push（破壊アニメーション機能）
- `blender_addons/procedural_rock_studio/generators/door_destruction_gen.py`（新規）— 破壊アニメ本体
- `blender_addons/procedural_rock_studio/utils/anim_baker.py`（+97行）— `bake_object_group_to_shapekeys`, `export_door_destruction_fbx`
- `properties.py`（+12行）— `door_destruction_shard_count`, `door_destruction_frame_count`
- `ui/panel.py`（+11行）— 「💥 木っ端微塵に破壊してFBX出力」ボタン
- `ui/operators.py`（+61行）— `MESH_OT_generate_door_destruction`
- `ui/__init__.py`（+4/-1行）— 上記オペレーター登録
- `test_door_destruction.py`, `test_door_destruction_operator.py`, `test_render_destruction_f*.png`, `test_render_destruction_grid.png`

## DOORプリセットの概要（既push分）
- カテゴリ `DOOR`。`Door_Frame`（石造アーチ開口、`build_procedural_stone_arch_bmesh`再利用＋`build_roman_fluted_pillar`の溝彫り円柱を前面に融合）＋`Door_Leaf_L`/`Door_Leaf_R`（蝶番原点の子オブジェクト）。
- 扉パネルは「矩形部(Box)＋アーチカーブ追従キャップ(輪郭→押し出しの単一ソリッド、smooth判定つき)」の低ポリ構成（ユーザー要望で板1枚ずつのCube積みから変更済み）。
- 板の継ぎ目は幾何ではなく `create_door_wood_material` のWaveテクスチャ・バンプで表現。
- 縁取り金属フレーム（`add_edge_trim_bmesh`）が外周を一周し、木材とは別の`iron`マテリアルスロット。
- 経年劣化（`door_damage`/`door_weathering`/`door_moss_amount`）は高さマスク×Noiseで実際に機能する汚し表現（`_add_height_dirt_mask`）。

## 破壊アニメーション機能の概要（本セッション新規）
`generators/door_destruction_gen.py` の `generate_door_destruction(context, leaf_obj_l, leaf_obj_r, frame_obj=None, shard_count=20, frame_count=70, sample_step=2, impact_strength=1.0, impact_frames=4, subdivide_cuts=2, seed=0, name=...)`:

1. `Door_Leaf_L`/`Door_Leaf_R` を複製し、`bpy.ops.mesh.separate(type='MATERIAL')` で木部/鉄部に分離
2. 木部のみ **Cell Fracture**（Blender同梱アドオン `object_fracture_cell`、`bpy.ops.preferences.addon_enable()`で有効化）で破片化
3. 鉄金具（帯金具・鋲・縁取り・取っ手）は左右それぞれ1塊のまま剛体に（細切れにしない）
4. 密着した破片は摩擦で固まって動かないため、**シミュレーション開始前に初期配置を衝撃点から放射状にランダム方向へあらかじめずらし**、さらに最初の`impact_frames`だけFORCEエフェクターで外向きに押す。全破片は最初からACTIVE(非キネマティック)のままで、kinematic⇄dynamic切り替えは使わない（後述のバグ修正で採用した方式）
5. `sample_step`間隔でフレームをサンプリングし、各破片の`matrix_world`を記録（シミュレーションの基準フレームは必ず`rigidbody_world.point_cache.frame_start`から）
6. `bpy.ops.object.join()`は使わず（内部の結合順序保証がないため）、`order`リストの順序どおり自前bmeshで頂点・面をワールド座標のまま積み上げて1メッシュに結合（`vertex_ranges`で「どの頂点範囲がどの元オブジェクトか」を100%確定）
7. `utils/anim_baker.py`の`bake_object_group_to_shapekeys`で、各サンプルフレームを1シェイプキーとして焼き付け（既存の水面ループ焼き付け関数を非ループ版に一般化したもの）
8. `export_door_destruction_fbx`でFBX出力（`bake_anim=True`）

UI: DOORカテゴリパネルの「💥 破壊アニメーション」ボックスから、`Door_Frame`または`Door_Leaf`を選択して「💥 木っ端微塵に破壊してFBX出力」ボタンを実行。

## 動作確認方法（次回セッションでまず実行推奨）

**重要な注意**: このアドオンは `Z:\MeshCreator\blender_addons\procedural_rock_studio`（ソース）と `C:\Users\kiyot\AppData\Roaming\Blender Foundation\Blender\3.6\scripts\addons\procedural_rock_studio`（インストール先）の**2箇所に存在**する。Blenderは`--background`でもインストール先を自動ロードし`sys.modules`キャッシュがソース側を上書きするため、**ソースを編集したら必ずインストール先にもコピーし`__pycache__`を両方削除してからテストすること**（過去のプロジェクトメモリ`project_meshcreator_chibi_technical_gotchas`にも同種の教訓あり）。

```bash
SRC="/z/MeshCreator/blender_addons/procedural_rock_studio"
DST="/c/Users/kiyot/AppData/Roaming/Blender Foundation/Blender/3.6/scripts/addons/procedural_rock_studio"
cp -r "$SRC"/* "$DST"/
find "$SRC" "$DST" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
"/c/Program Files/Blender Foundation/Blender 3.6/blender.exe" --background --factory-startup --python "Z:/MeshCreator/test_door_destruction_operator.py"
```

- `test_door_addon.py`: DOORプリセット単体（アーチ形状3種＋開閉プレビュー）をレンダリング確認
- `test_door_destruction.py`: 破壊アニメ本体関数を直接呼び出し、frame 1/8/16/30をレンダリング確認
- `test_door_destruction_operator.py`: 実際のUIオペレーター経由（`bpy.ops.mesh.generate_door_destruction()`）でFBX出力まで確認

## 既知の制限・チューニングメモ
- **shard_countは目安値**: Cell Fractureの`source_limit`パラメータは要求した破片数を厳密には守らない（テストではshard_count=8指定で実際は33〜35個生成された）。多めに出る前提でUI側のデフォルト（16/枚）を設定している。
- **密集した破片が「塊」のまま残りやすい**: 木部の中心付近の破片は隣接破片との摩擦・噛み合いで動きにくい。現状は「初期配置の事前ずらし＋方向にランダム性を強く混ぜる＋FORCEエフェクター」方式。完全な粉々描写には`shard_count`や`impact_strength`（関数引数、現状UIには未露出）をさらに強めるか、`frame_count`を伸ばす余地がある。
- **同一セッション内での2回目以降の呼び出しに関する重大バグは修正済み**（本ファイル冒頭の追記参照）。もし今後また似た「途中で動かなくなる」系の不具合が出たら、まず `rw.point_cache.frame_start` を基準にしているか、剛体シミュレーションが `point_cache.frame_start` から連続してステップされているかを疑うこと。
- **ボーン(Armature)方式は未実装**: 現状はシェイプキー（頂点キャッシュ的）方式でFBXベイクしている。UE側のファイルサイズ・取り回しは破片ごとに1ボーンのスケルタルメッシュ方式の方が優れるはずだが、既存の水面ベイク資産(`anim_baker.py`)を流用してスコープを抑えるため今回は見送った。将来の改善候補。
- **UE実機での取り込み確認は未実施**（ローカル環境にUnreal Engineがないため）。FBXファイル自体は正常出力されること（約2.5MB）のみ確認済み。
- `bpy.ops.<category>.<op>` は属性アクセス時点では存在チェックにならない（`hasattr`が常にTrueを返す）ため、Cell Fracture等オプションアドオンの有効化チェックは`hasattr`を使わず常に`addon_enable`を試みる実装にしてある。
- `bpy.ops.mesh.separate(type='MATERIAL')` 後は各オブジェクトのマテリアルスロットが1つに圧縮され、`polygon.material_index`は常に0にリナンバーされる（元のスロット番号は保持されない）。木部/鉄部の判定は`material_index`ではなく`obj.data.materials[0].name`（"_Wood_Mat"/"_Iron_Mat"）で行っている。
- Cell Fractureの`use_remove_original=True`は**再帰分割(recursion>0)時のみ**元オブジェクトを削除する仕様で、通常利用(recursion=0)では削除されない。破片化後は明示的に`bpy.data.objects.remove()`で削除する必要がある。

## Q&A（ユーザーからの質問への回答）
- **Q: この粉々になるのはUEのアニメーション側でやるもの？**
  A: いいえ。砕け散る物理シミュレーション（Cell Fracture + Rigid Body）は**すべてBlender側（この生成処理）で事前に計算・焼き付け済み**。UEは計算を一切行わず、FBXに入っている**シェイプキー（モーフターゲット）アニメーションをただ再生するだけ**。UEのChaos Destructionのようなランタイム破壊システムは使っていない。UE側では「Morph Target Animation」として通常の頂点アニメと同じ扱いになる想定（UE実機での確認は未実施、上記参照）。

## 次にやるとよいこと
1. `door_destruction_shard_count`/`frame_count`をUIから大きめに振って、粉々具合の見え方を実機（Blender GUI）で確認・好みに調整
2. 可能であればUE側にFBXを持ち込み、シェイプキーアニメーションが正しく再生されるか確認
3. 余裕があればボーン(Armature)方式へのアップグレードを検討（破片ごとに1ボーン、`bpy.ops.rigidbody.bake_to_keyframes`でオブジェクトアニメをベイクし、ボーンへ転写する方式）
4. 参考画像2（ガラス入りファンライトの洗練ドア）を別スタイルとして追加したい場合は`door_gen.py`に手を入れる（今回は`build_procedural_stone_arch_bmesh`の設計上スコープ外にした旨、会話ログ参照）

## 参照
- DOORプリセットレンダー確認画像: `Z:\MeshCreator\test_render_door_preset.png`
- 破壊アニメ確認画像: `Z:\MeshCreator\test_render_destruction_grid.png`（フレーム1/8/16/30の4分割）
- 出力FBX例: `Z:\MeshCreator\exports\OpDoor_Frame_Destruction.fbx`
