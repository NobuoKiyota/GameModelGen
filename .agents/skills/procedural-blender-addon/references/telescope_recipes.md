# 🔭 プロシージャル天体望遠鏡（Celestron StarSense Explorer LT風）完全技術レシピ

## 🎯 1. 独立階層構造（Parent-Child Hierarchy）

- `Telescope_Root` (Empty / 原点)
  - `Telescope_Tripod` (三脚本体: 2段伸縮レッグ、ロックバックル、三角スプレッダー、丸穴トレイ、中央支柱)
    - `Telescope_Mount` (架台 / 水平360°回転パンベース、フォークアーム、高度微動固定部、オレンジ固定ノブ)
      - `Telescope_OTA` (鏡筒本体: メインシリンダー、先太り対物フード、オレンジリング、90度天頂プリズム、アイピース、スマホドック、高度微動ロッド)

---

## 🎨 2. 4大プロシージャル PBR マテリアル

1. **`Mat_Telescope_Silver` (サテン・アルミ鏡筒)**:
   - Base Color: `(0.78, 0.80, 0.83, 1.0)`, Metallic: `0.88`, Roughness: `0.22`
2. **`Mat_Telescope_Black` (マットブラック三脚・マウント・接眼部)**:
   - Base Color: `(0.09, 0.10, 0.11, 1.0)`, Metallic: `0.20`, Roughness: `0.42`
3. **`Mat_Celestron_Orange` (セレストロン・シグネチャーオレンジ)**:
   - Base Color: `(0.90, 0.32, 0.0, 1.0)`, Metallic: `0.0`, Roughness: `0.30`
4. **`Mat_Telescope_Lens` (対物・接眼光学ガラス)**:
   - Base Color: `(0.83, 0.92, 0.95, 1.0)`, Transmission: `0.95`, IOR: `1.52`, Roughness: `0.02`

---

## 🎮 3. 可動ピボット仕様
- **水平方位角 (Azimuth)**: `Telescope_Mount` の Z 軸回転 (`0°〜360°`)
- **上下仰角 (Elevation)**: `Telescope_OTA` の X 軸チルト回転 (`0°〜90°`)
