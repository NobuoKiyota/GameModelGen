# GameModelGen / PhotoToJewelry3D

**PhotoToJewelry3D & Anatomy Sculpt Studio**  
静止画（写真・イラスト）から近似色クラスタリング・ディスプレイスメント・極座標投影を用いて、inZOI / Unreal Engine / Unity 互換の UV2 対応 3D モデル（FBX / GLB / OBJ）を高速生成する Web 3D 制作ツール。

---

## 🌟 主な機能

### 1. 💎 ジュエリー & カボションモード (Jewelry Studio)
- **2D 画像解析 & アンカー指定**: D&D / ファイル選択による画像読み込み、ホイールズーム、ドラッグパン、投影中心点（Anchor）配置。
- **CIELAB k-means++ 高速クラスタリング**: Web Worker による近似色クラスタリングと半透明カラー分布図オーバーレイ。
- **3D リアルタイム変形**:
  - 楕円体（Scale X/Y/Z）変形および底面平坦化（Cutoff 0%〜90%）。
  - 各カラーグループの「高さ（Offset: -1.0〜+1.0）」に応じた動的頂点ディスプレイスメント & Sobel 法線摂動（Bump mapping）。
  - 超広角 300% 投影ラッピング（Coverage 30%〜300%）。
- **PBR 質感 & カラーグレーディング**:
  - 宝石/ガラス、鏡面ゴールド、クロムシルバー、カメオ彫刻、マット樹脂のワンクリックプリセット。
  - 光沢度（Roughness）、メタリック感、クリアコートガラス光沢、彩度・コントラスト・明度・色相・シャープネス調整。

### 2. 👤 人体・顔パーツ造形モード (Anatomy Studio)
- **部位別専用ベース形状**:
  - 👃 **鼻 (Nose Bridge)**: 鼻筋の山型稜線、鼻尖、小鼻（Ala）の広がり。
  - 👂 **耳 (Ear Concha)**: 外耳輪（Helix）、耳甲介のC字型窪み、耳たぶ。
  - 👄 **唇 (Lips & Bow)**: 人中からキューピッド弓、上下唇のふくらみカーブ。
  - 🧑 **顔面曲面 (Facial Contour)**: 頬・額・顎などの滑らかな有機ドーム。
- **肌質 PBR & SSS（表面下散乱）**:
  - 光が皮膚内部で赤く透ける SSS（Subsurface Scattering）表現。
  - スキントーンプリセット（Fair, Natural, Tan, Deep, クレイ彫刻）。
  - 左右対称（Symmetry）ミラー変形 & 毛穴キメ微細バンプ。

### 3. 🎯 3D/2D スポイト・ピッキング & 領域ハイライト
- 3D プレビュー上または 2D 画像上をクリックするだけで、該当ピクセルのカラーグループを特定して右パネル一覧へ自動スクロール＆選択。
- 選択中グループの領域だけが鮮やかに発光するスマートオーバーレイ表示。

### 4. 📦 inZOI 互換エクスポート & プロジェクト保存
- **inZOI 互換 UV2 (Lightmap UV)**: 重なりのない（Non-overlapping）展開アトリビュートを自動付与。
- **ベイクド 3D エクスポート**:
  - FBX（inZOI / UE5 / Unity 向け）
  - GLB / GLTF（Web / Blender 向け）
  - OBJ（汎用 3D ツール向け）
  - ディフューズ画像（PNG）& ハイトマップ（PNG）同時出力。
- **プロジェクト保存 & 復元**: 全設定状態を `.p3j` / JSON ファイルとしてダウンロード・再読み込み。

---

## 🚀 開発・起動方法

```bash
# 依存パッケージのインストール
npm install

# 開発サーバーの起動 (Vite)
npm run dev

# プロダクションビルド
npm run build
```

---

## 🛠️ 技術スタック
- **Frontend**: React 18 + TypeScript + Vite
- **3D Graphics**: Three.js + Custom GLSL Shaders (Polar projection, Vertex displacement, PBR, SSS)
- **State Management**: Zustand
- **Styling**: Tailwind CSS + Lucide Icons
- **Image Processing**: HTML5 Canvas API + Web Worker (CIELAB color space + k-means++)
- **Exporters**: FBX (Custom ASCII with UV2), GLTFExporter, OBJExporter
