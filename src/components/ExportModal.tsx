import React, { useState } from 'react';
import { useJewelryStore } from '../store/useJewelryStore';
import { export3DModel } from '../utils/meshExporter';
import { ExportFormat, ExportOptions } from '../types';
import { Download, X, Box, CheckCircle2, Layers, Image as ImageIcon, Loader2 } from 'lucide-react';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ExportModal: React.FC<ExportModalProps> = ({ isOpen, onClose }) => {
  const {
    image,
    anchor,
    clusters,
    clusterMap,
    clusterMapWidth,
    clusterMapHeight,
    modelSettings,
    heightMapUrl,
  } = useJewelryStore();

  const [format, setFormat] = useState<ExportFormat>('fbx');
  const [filename, setFilename] = useState('jewelry_asset');
  const [includeUV2, setIncludeUV2] = useState(true);
  const [includeTexture, setIncludeTexture] = useState(true);
  const [includeHeightMap, setIncludeHeightMap] = useState(true);
  const [isExporting, setIsExporting] = useState(false);

  if (!isOpen) return null;

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const options: ExportOptions = {
        format,
        includeUV2,
        includeTexture,
        includeHeightMap,
        bakeDisplacement: true,
        filename,
      };

      await export3DModel(
        options,
        modelSettings,
        anchor,
        clusters,
        clusterMap,
        clusterMapWidth,
        clusterMapHeight,
        image?.url,
        heightMapUrl
      );
      setTimeout(() => {
        setIsExporting(false);
        onClose();
      }, 600);
    } catch (err) {
      console.error('Export Failed:', err);
      setIsExporting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-fadeIn">
      <div className="w-full max-w-md bg-darkPanel border border-darkBorder rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-darkBorder bg-darkCard/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Box className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-gray-100">3Dモデル エクスポート</h3>
              <p className="text-[11px] text-gray-400">inZOI / UE5 / Unity / Blender 互換出力</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-darkBorder text-gray-400 hover:text-white transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 space-y-4 text-xs text-gray-300">
          {/* Format Selector */}
          <div className="space-y-1.5">
            <label className="font-semibold text-gray-200 block">ファイル形式</label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'fbx', label: 'FBX', tag: 'inZOI / UE5' },
                { id: 'glb', label: 'GLB / GLTF', tag: 'Web / Blender' },
                { id: 'obj', label: 'OBJ', tag: '汎用 3D' },
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setFormat(item.id as ExportFormat)}
                  className={`p-2.5 rounded-xl border flex flex-col items-center gap-1 transition-all cursor-pointer ${
                    format === item.id
                      ? 'border-amber-400 bg-amber-400/15 text-amber-300 font-bold shadow-md shadow-amber-500/10'
                      : 'border-darkBorder bg-darkCard text-gray-400 hover:text-gray-200'
                  }`}
                >
                  <span className="text-xs font-mono font-bold">{item.label}</span>
                  <span className="text-[9px] text-gray-400">{item.tag}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Filename Input */}
          <div className="space-y-1.5">
            <label className="font-semibold text-gray-200 block">ファイル名</label>
            <div className="flex items-center gap-2 bg-darkCard border border-darkBorder rounded-lg px-3 py-2">
              <input
                type="text"
                value={filename}
                onChange={(e) => setFilename(e.target.value)}
                className="flex-1 bg-transparent text-gray-100 font-mono text-xs outline-none"
                placeholder="jewelry_asset"
              />
              <span className="text-gray-500 font-mono text-xs">.{format}</span>
            </div>
          </div>

          {/* Export Options Checklist */}
          <div className="space-y-2.5 pt-2 border-t border-darkBorder/60">
            <span className="font-semibold text-gray-200 block">出力オプション</span>

            <label className="flex items-center justify-between p-2.5 rounded-lg bg-darkCard border border-darkBorder hover:border-gray-500 transition-colors cursor-pointer">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-indigo-400" />
                <div>
                  <span className="font-semibold text-gray-200 block">inZOI 重複なし UV2 自動生成</span>
                  <span className="text-[10px] text-gray-400">ライトマップ用セカンドUVアトリビュートを付与</span>
                </div>
              </div>
              <input
                type="checkbox"
                checked={includeUV2}
                onChange={(e) => setIncludeUV2(e.target.checked)}
                className="w-4 h-4 accent-amber-400 rounded cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between p-2.5 rounded-lg bg-darkCard border border-darkBorder hover:border-gray-500 transition-colors cursor-pointer">
              <div className="flex items-center gap-2">
                <ImageIcon className="w-4 h-4 text-amber-400" />
                <div>
                  <span className="font-semibold text-gray-200 block">ディフューズ テクスチャ画像同梱</span>
                  <span className="text-[10px] text-gray-400">カラー画像を PNG ファイルとして同時出力</span>
                </div>
              </div>
              <input
                type="checkbox"
                checked={includeTexture}
                onChange={(e) => setIncludeTexture(e.target.checked)}
                className="w-4 h-4 accent-amber-400 rounded cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between p-2.5 rounded-lg bg-darkCard border border-darkBorder hover:border-gray-500 transition-colors cursor-pointer">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <div>
                  <span className="font-semibold text-gray-200 block">ハイトマップ (凹凸テクスチャ) 同梱</span>
                  <span className="text-[10px] text-gray-400">グレースケール段差マップを PNG 出力</span>
                </div>
              </div>
              <input
                type="checkbox"
                checked={includeHeightMap}
                onChange={(e) => setIncludeHeightMap(e.target.checked)}
                className="w-4 h-4 accent-amber-400 rounded cursor-pointer"
              />
            </label>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-darkBorder bg-darkCard/30 flex items-center justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold text-gray-400 hover:text-gray-200 transition-colors cursor-pointer"
          >
            キャンセル
          </button>
          <button
            disabled={isExporting}
            onClick={handleExport}
            className="px-5 py-2 rounded-lg text-xs font-bold bg-amber-500 hover:bg-amber-400 text-darkBg flex items-center gap-2 shadow-lg shadow-amber-500/20 transition-all cursor-pointer"
          >
            {isExporting ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ベイク＆エクスポート中...
              </>
            ) : (
              <>
                <Download className="w-3.5 h-3.5" />
                ダウンロード
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};