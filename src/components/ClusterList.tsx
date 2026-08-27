import React, { useEffect, useRef } from 'react';
import { useJewelryStore } from '../store/useJewelryStore';
import { Eye, EyeOff, Layers, Sparkles, Crosshair } from 'lucide-react';

const OVERLAY_PALETTE_HEX = [
  '#ef4444', '#3b82f6', '#10b981', '#f59e0b',
  '#a855f7', '#ec4899', '#06b6d4', '#84cc16',
  '#f97316', '#6366f1', '#14b8a6', '#d946ef',
  '#a16207', '#64748b', '#be185d', '#047857',
];

export const ClusterList: React.FC = () => {
  const {
    clusters,
    updateCluster,
    selectedClusterId,
    setSelectedClusterId,
    setHoveredClusterId,
  } = useJewelryStore();

  const activeItemRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (selectedClusterId !== null && activeItemRef.current) {
      activeItemRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [selectedClusterId]);

  if (clusters.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
          <Layers className="w-3.5 h-3.5 text-amber-400" />
          検出されたカラーグループ ({clusters.length}色)
        </h4>
        {selectedClusterId !== null && (
          <button
            onClick={() => setSelectedClusterId(null)}
            className="text-[10px] text-amber-400 hover:text-amber-300 font-mono transition-colors cursor-pointer"
          >
            選択解除
          </button>
        )}
      </div>

      <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
        {clusters.map((cluster, idx) => {
          const badgeColor = OVERLAY_PALETTE_HEX[idx % OVERLAY_PALETTE_HEX.length];
          const isSelected = selectedClusterId === cluster.id;

          return (
            <div
              key={cluster.id}
              ref={isSelected ? activeItemRef : null}
              onMouseEnter={() => setHoveredClusterId(cluster.id)}
              onMouseLeave={() => setHoveredClusterId(null)}
              onClick={() => setSelectedClusterId(isSelected ? null : cluster.id)}
              className={`p-2.5 rounded-lg border transition-all cursor-pointer ${
                isSelected
                  ? 'bg-amber-500/15 border-amber-400 shadow-lg shadow-amber-500/10 ring-1 ring-amber-400/50'
                  : cluster.visible
                  ? 'bg-darkCard/80 border-darkBorder hover:border-gray-500'
                  : 'bg-darkCard/30 border-darkBorder/40 opacity-50'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div
                    className="w-4 h-4 rounded-full border border-white/20 shadow-sm shrink-0 flex items-center justify-center text-[10px] font-bold text-white"
                    style={{ backgroundColor: badgeColor }}
                  >
                    {idx + 1}
                  </div>

                  <label
                    onClick={(e) => e.stopPropagation()}
                    className="w-5 h-5 rounded cursor-pointer border border-white/30 overflow-hidden relative shadow-inner inline-block shrink-0"
                    style={{ backgroundColor: cluster.hex }}
                    title="代表色の変更"
                  >
                    <input
                      type="color"
                      value={cluster.hex}
                      onChange={(e) => updateCluster(cluster.id, { hex: e.target.value })}
                      className="opacity-0 absolute inset-0 w-full h-full cursor-pointer"
                    />
                  </label>

                  <div className="flex flex-col">
                    <span className="text-xs font-mono font-bold text-gray-200">
                      {cluster.hex.toUpperCase()}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                  {isSelected && (
                    <span className="text-[9px] font-bold text-amber-300 bg-amber-500/20 px-1.5 py-0.5 rounded border border-amber-500/30 flex items-center gap-1">
                      <Crosshair className="w-2.5 h-2.5" /> 選択中
                    </span>
                  )}
                  <span className="text-[11px] font-mono text-gray-400 bg-darkPanel px-1.5 py-0.5 rounded border border-darkBorder">
                    {cluster.percentage.toFixed(1)}%
                  </span>
                  <button
                    onClick={() => updateCluster(cluster.id, { visible: !cluster.visible })}
                    className={`p-1 rounded hover:bg-darkBorder transition-colors cursor-pointer ${
                      cluster.visible ? 'text-gray-300 hover:text-white' : 'text-gray-600'
                    }`}
                    title={cluster.visible ? 'このグループを非表示' : 'このグループを表示'}
                  >
                    {cluster.visible ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              <div
                className="space-y-1.5 pt-1 border-t border-darkBorder/40 text-[11px]"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 shrink-0 w-16">高さ (Offset)</span>
                  <input
                    type="range"
                    min="-1.0"
                    max="1.0"
                    step="0.05"
                    value={cluster.height}
                    onChange={(e) => updateCluster(cluster.id, { height: parseFloat(e.target.value) })}
                    className="flex-1 accent-amber-400 cursor-pointer h-1.5 bg-darkPanel rounded-lg"
                  />
                  <span className="font-mono text-amber-300 w-10 text-right font-semibold">
                    {cluster.height > 0 ? `+${cluster.height.toFixed(2)}` : cluster.height.toFixed(2)}
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 shrink-0 w-16">硬さ (Hard)</span>
                  <input
                    type="range"
                    min="0.0"
                    max="1.0"
                    step="0.05"
                    value={cluster.hardness}
                    onChange={(e) => updateCluster(cluster.id, { hardness: parseFloat(e.target.value) })}
                    className="flex-1 accent-indigo-400 cursor-pointer h-1.5 bg-darkPanel rounded-lg"
                  />
                  <span className="font-mono text-indigo-300 w-10 text-right font-semibold">
                    {cluster.hardness.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="p-2 rounded bg-indigo-500/10 border border-indigo-500/20 text-[10px] text-indigo-300/80 flex items-center gap-1.5">
        <Sparkles className="w-3.5 h-3.5 shrink-0 text-indigo-400" />
        グループをクリック、または 3D / 2D 画面をクリックすると対象色が光ってジャンプします
      </div>
    </div>
  );
};