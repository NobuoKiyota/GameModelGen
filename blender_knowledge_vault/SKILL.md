---
name: blender-master-cookbook
description: Blender 3.6+ Python API, Procedural 3D Modeling, PBR & Procedural Shaders, Hair Particle Scattering, and Game Asset (Unity/UE) Pipeline Knowledge Vault. Activate whenever generating, modifying, or designing Blender procedural models, shaders, particle systems, or game-ready FBX export pipelines.
---

# 📚 Blender Master Cookbook & Knowledge Vault

Blender 3.6+ における **プロシージャル3Dモデリング、シェーダーネットワーク、パーティクル散布、Unity/UE向けゲーム最適化、および Blender Python API の実践ノウハウ** を体系化した永続ナレッジベースです。
ゼロからネットや動画を再調査することなく、実証済みのベストプラクティスを組み合わせて高品質なアセットを即座に生成・応用できます。

---

## 🧭 リファレンス・目次 (Knowledge Index)

1. [📐 幾何モデリング レシピ集 (Geometry Recipes)](references/geometry_recipes.md)
   - Sacoche Ito式 凸包ランダム岩石（Convex Hull Solid Rock / Crag）
   - Mdesign式 多重サイン波プロポーショナル起伏地面（Terrain Ground）
   - UV縦展開（Y=0〜1）対応 5点先細り草ブレード（Grass Blade & Tuft）
   - クラシック装飾柱（ろくろ挽き・ツイスト・キャピタル台座）
   - 近代PCデスク・アンティーク家具・チェスト・ベッドのプロシージャル構造

2. [🎨 PBR ＆ プロシージャルシェーダー (Shader Engine)](references/shader_recipes.md)
   - Wave Texture ＋ Noise によるシード連動の縦木目（樹皮シェーダー）
   - UV.Y → ColorRamp ＋ Object Info Random ＋ Translucent（リアル草シェーダー）
   - ambientCG / Poly Haven フルセット自動検知 ＆ Cycles Displacement
   - Noise × Voronoi による土・枯草・苔の Tri-Color 地面シェーダー

3. [🌾 パーティクル ＆ 散布システム (Scattering & Realization)](references/particle_scattering.md)
   - Hair Particle ＋ Collection Render によるマルチブレード自動散布
   - ノイズ数式による頂点グループ（Grass_Density）の自動プロシージャルペイント
   - Blender 3.6 対応のパーティクル実体化（`disconnect_hair` → `convert(MESH)`）

4. [🎮 Unity / Unreal Engine ゲームパイプライン (Game Pipeline & Audio)](references/game_pipeline_audio.md)
   - FBX エクスポート時の標準軸設定（-Z forward, Y up）とスケールベイク
   - マテリアルスロット分離による **足音・接触音（Footstep / Surface Switch）** 連携
   - Alpha Clip（カットアウト）テクスチャの同封エクスポート仕様

5. [⚠️ Blender Python API 虎の巻 (Pitfalls & Best Practices)](references/blender_api_mastery.md)
   - UV 投影後の **`OBJECT` モード復帰の鉄則**
   - ヘッドレス環境（`--background`）における `modifier_apply` と `temp_override`
   - Sapling Tree Gen の中間メッシュ（`treemesh`）パージと複素数スケール回避
   - Bmesh の安全な作成・書き出し・解放ライフサイクル

---

## 🔄 知識の追加・アップデート指針
- 新しい YouTube 講座、論文、アドオンの技法を実装・検証した際は、検証済みコードスニペットとともに上記各ファイルに追記して Git コミットすること。
- 他のワークスペースや別 PC 環境でも、リポジトリを `git pull` することで常に最新の職人技を呼び出し可能。
