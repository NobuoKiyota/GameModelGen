import React from 'react';
import { Box, Layers, Sparkles } from 'lucide-react';
import { useJewelryStore } from '../store/useJewelryStore';

export const Preview3DPlaceholder: React.FC = () => {
  const { image } = useJewelryStore();

  return (
    <div className="relative w-full h-full bg-[#0d0f16] flex flex-col items-center justify-center p-6 text-center overflow-hidden">
      <div 
        className="absolute inset-0 opacity-[0.05] pointer-events-none"
        style={{
          backgroundImage: 'linear-gradient(to right, #6366f1 1px, transparent 1px), linear-gradient(to bottom, #6366f1 1px, transparent 1px)',
          backgroundSize: '40px 40px',
        }}
      />

      <div className="relative z-10 max-w-sm flex flex-col items-center">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mb-4 shadow-xl shadow-indigo-500/10">
          <Box className="w-8 h-8" />
        </div>
        <h3 className="text-base font-semibold text-gray-200 mb-1">Three.js 3Dビューポート</h3>
        <p className="text-xs text-gray-400 leading-relaxed mb-4">
          Phase 3 で楕円球体メッシュおよび極座標テクスチャ投影、Phase 4 でディスプレイスメント（凹凸段差）がリアルタイム表示されます。
        </p>

        {image ? (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
            <Sparkles className="w-3.5 h-3.5" />
            画像読み込み完了 ({image.width} × {image.height})
          </div>
        ) : (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-800 border border-gray-700 text-gray-400 text-xs">
            <Layers className="w-3.5 h-3.5" />
            左パネルで画像を開いてください
          </div>
        )}
      </div>
    </div>
  );
};