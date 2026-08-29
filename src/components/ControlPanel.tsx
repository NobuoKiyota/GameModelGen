import React, { useState } from 'react';
import { useJewelryStore } from '../store/useJewelryStore';
import { ClusterList } from './ClusterList';
import { RimMaterialType, MaterialPresetType } from '../types';
import { Crosshair, Sliders, Palette, RefreshCw, Loader2, Box, RotateCcw, Mountain, Sparkles, SunMedium, Wand2 } from 'lucide-react';

export const ControlPanel: React.FC = () => {
  const {
    image,
    anchor,
    setAnchor,
    resetAnchor,
    clusterCount,
    setClusterCount,
    blurRadius,
    setBlurRadius,
    isClustering,
    runClustering,
    clusters,
    modelSettings,
    updateModelSettings,
    updateColorGrading,
    applyMaterialPreset,
    resetModelSettings,
  } = useJewelryStore();

  const [activeSubTab, setActiveSubTab] = useState<'shape' | 'material' | 'clusters'>('shape');

  return (
    <aside className="w-92 h-full bg-darkPanel border-l border-darkBorder flex flex-col shrink-0 overflow-hidden">
      {/* Panel Header with Sub-Tabs */}
      <div className="p-3 border-b border-darkBorder flex flex-col gap-2 shrink-0 bg-darkPanel">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-amber-400" />
            <h2 className="text-sm font-bold text-gray-200">パラメータ調整</h2>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-darkCard border border-darkBorder text-amber-400 font-semibold">
            High-End 3D
          </span>
        </div>

        {/* Sub-Tabs */}
        <div className="grid grid-cols-3 gap-1 bg-darkBg p-1 rounded-lg border border-darkBorder text-xs">
          <button
            onClick={() => setActiveSubTab('shape')}
            className={`py-1 rounded font-medium transition-all flex items-center justify-center gap-1 cursor-pointer ${
              activeSubTab === 'shape'
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold shadow-sm'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            <Box className="w-3 h-3" />
            形状・段差
          </button>
          <button
            onClick={() => setActiveSubTab('material')}
            className={`py-1 rounded font-medium transition-all flex items-center justify-center gap-1 cursor-pointer ${
              activeSubTab === 'material'
                ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-bold shadow-sm'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            <Sparkles className="w-3 h-3" />
            質感・色調
          </button>
          <button
            onClick={() => setActiveSubTab('clusters')}
            className={`py-1 rounded font-medium transition-all flex items-center justify-center gap-1 cursor-pointer ${
              activeSubTab === 'clusters'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold shadow-sm'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            <Palette className="w-3 h-3" />
            カラー層
          </button>
        </div>
      </div>

      {/* Tab Contents */}
      <div className="p-4 space-y-5 flex-1 overflow-y-auto">
        {/* TAB 1: SHAPE & DISPLACEMENT */}
        {activeSubTab === 'shape' && (
          <>
            {/* 1. 凹凸ディスプレイスメント */}
            <section className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                  <Mountain className="w-3.5 h-3.5 text-amber-400" />
                  段差・凹凸ディスプレイスメント
                </h3>
                <button
                  onClick={() => updateModelSettings({ displacementEnabled: !modelSettings.displacementEnabled })}
                  className={`text-[10px] px-2 py-0.5 rounded font-semibold transition-colors cursor-pointer ${
                    modelSettings.displacementEnabled
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                      : 'bg-darkCard text-gray-500 border border-darkBorder'
                  }`}
                >
                  {modelSettings.displacementEnabled ? 'ON' : 'OFF'}
                </button>
              </div>

              <div className="space-y-2.5 bg-darkCard p-3 rounded-lg border border-darkBorder text-xs">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-24 shrink-0">凹凸強度 (Scale)</span>
                  <input
                    type="range"
                    min="0.0"
                    max="1.5"
                    step="0.05"
                    value={modelSettings.displacementScale}
                    onChange={(e) => updateModelSettings({ displacementScale: parseFloat(e.target.value) })}
                    className="flex-1 accent-amber-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-amber-300 w-10 text-right font-semibold">
                    {modelSettings.displacementScale.toFixed(2)}
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-24 shrink-0">滑らかさ (Smooth)</span>
                  <input
                    type="range"
                    min="0.0"
                    max="2.0"
                    step="0.1"
                    value={modelSettings.bevelSmoothness}
                    onChange={(e) => updateModelSettings({ bevelSmoothness: parseFloat(e.target.value) })}
                    className="flex-1 accent-indigo-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-indigo-300 w-10 text-right font-semibold">
                    {modelSettings.bevelSmoothness.toFixed(1)}
                  </span>
                </div>
              </div>
            </section>

            {/* 2. 3D 楕円体 & 形状設定 */}
            <section className="space-y-3 pt-2 border-t border-darkBorder/60">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                  <Box className="w-3.5 h-3.5 text-amber-400" />
                  3D 楕円体・形状調整
                </h3>
                <button
                  onClick={resetModelSettings}
                  className="text-[11px] text-amber-400 hover:text-amber-300 transition-colors flex items-center gap-1 cursor-pointer"
                  title="形状を初期値にリセット"
                >
                  <RotateCcw className="w-3 h-3" />
                  リセット
                </button>
              </div>

              <div className="space-y-2.5 bg-darkCard p-3 rounded-lg border border-darkBorder text-xs">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-20 shrink-0">幅 (Scale X)</span>
                  <input
                    type="range"
                    min="0.3"
                    max="2.5"
                    step="0.05"
                    value={modelSettings.scaleX}
                    onChange={(e) => updateModelSettings({ scaleX: parseFloat(e.target.value) })}
                    className="flex-1 accent-amber-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-amber-300 w-10 text-right font-semibold">
                    {modelSettings.scaleX.toFixed(2)}
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-20 shrink-0">縦 (Scale Y)</span>
                  <input
                    type="range"
                    min="0.3"
                    max="2.5"
                    step="0.05"
                    value={modelSettings.scaleY}
                    onChange={(e) => updateModelSettings({ scaleY: parseFloat(e.target.value) })}
                    className="flex-1 accent-amber-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-amber-300 w-10 text-right font-semibold">
                    {modelSettings.scaleY.toFixed(2)}
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-20 shrink-0">厚み (Scale Z)</span>
                  <input
                    type="range"
                    min="0.1"
                    max="1.8"
                    step="0.05"
                    value={modelSettings.scaleZ}
                    onChange={(e) => updateModelSettings({ scaleZ: parseFloat(e.target.value) })}
                    className="flex-1 accent-amber-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-amber-300 w-10 text-right font-semibold">
                    {modelSettings.scaleZ.toFixed(2)}
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2 pt-1 border-t border-darkBorder/40">
                  <span className="text-gray-400 w-20 shrink-0">底面平坦化</span>
                  <input
                    type="range"
                    min="0.0"
                    max="0.9"
                    step="0.05"
                    value={modelSettings.cutoff}
                    onChange={(e) => updateModelSettings({ cutoff: parseFloat(e.target.value) })}
                    className="flex-1 accent-indigo-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-indigo-300 w-10 text-right font-semibold">
                    {(modelSettings.cutoff * 100).toFixed(0)}%
                  </span>
                </div>

                {/* Coverage: Extended to 300% */}
                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-20 shrink-0">投影範囲 (広角)</span>
                  <input
                    type="range"
                    min="0.3"
                    max="3.0"
                    step="0.05"
                    value={modelSettings.coverage}
                    onChange={(e) => updateModelSettings({ coverage: parseFloat(e.target.value) })}
                    className="flex-1 accent-indigo-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-indigo-300 w-10 text-right font-semibold">
                    {(modelSettings.coverage * 100).toFixed(0)}%
                  </span>
                </div>

                {/* Mesh Segments Resolution */}
                <div className="flex items-center justify-between gap-2 pt-1 border-t border-darkBorder/40">
                  <span className="text-gray-400 w-20 shrink-0">分割解像度</span>
                  <div className="flex items-center gap-1 flex-1 justify-end">
                    {[
                      { val: 128, label: '標準' },
                      { val: 192, label: '高精細' },
                      { val: 256, label: '極上' },
                    ].map((s) => (
                      <button
                        key={s.val}
                        onClick={() => updateModelSettings({ segments: s.val })}
                        className={`px-2 py-0.5 rounded text-[10px] font-mono transition-all cursor-pointer ${
                          modelSettings.segments === s.val
                            ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 font-bold'
                            : 'bg-darkPanel text-gray-400 border border-darkBorder hover:text-gray-200'
                        }`}
                      >
                        {s.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </section>
          </>
        )}

        {/* TAB 2: MATERIAL & COLOR GRADING */}
        {activeSubTab === 'material' && (
          <>
            {/* 1. 質感プリセットセレクタ */}
            <section className="space-y-3">
              <h3 className="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                <Wand2 className="w-3.5 h-3.5 text-amber-400" />
                質感プリセット (PBR)
              </h3>
              <div className="grid grid-cols-3 gap-1.5">
                {[
                  { id: 'gemstone', label: '💎 宝石/ガラス' },
                  { id: 'gold_polished', label: '👑 鏡面ゴールド' },
                  { id: 'silver_chrome', label: '✨ クロムシルバー' },
                  { id: 'antique_cameo', label: '🏺 カメオ/彫刻' },
                  { id: 'matte_resin', label: '🎨 マット樹脂' },
                  { id: 'custom', label: '⚙️ カスタム' },
                ].map((p) => (
                  <button
                    key={p.id}
                    onClick={() => applyMaterialPreset(p.id as MaterialPresetType)}
                    className={`py-2 px-1 rounded text-[10px] font-medium border text-center transition-all cursor-pointer ${
                      modelSettings.preset === p.id
                        ? 'border-amber-400 bg-amber-400/15 text-amber-200 font-bold shadow-sm'
                        : 'border-darkBorder bg-darkCard text-gray-400 hover:text-gray-200'
                    }`}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </section>

            {/* 2. PBR 表面光沢・反射スライダー */}
            <section className="space-y-3 pt-2 border-t border-darkBorder/60">
              <h3 className="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                <SunMedium className="w-3.5 h-3.5 text-indigo-400" />
                光沢・反射コントロール
              </h3>

              <div className="space-y-2.5 bg-darkCard p-3 rounded-lg border border-darkBorder text-xs">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-24 shrink-0">光沢度 (ツヤ)</span>
                  <input
                    type="range"
                    min="0.0"
                    max="1.0"
                    step="0.02"
                    value={1.0 - modelSettings.roughness}
                    onChange={(e) => updateModelSettings({ roughness: 1.0 - parseFloat(e.target.value), preset: 'custom' })}
                    className="flex-1 accent-amber-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-amber-300 w-10 text-right font-semibold">
                    {((1.0 - modelSettings.roughness) * 100).toFixed(0)}%
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-24 shrink-0">メタリック感</span>
                  <input
                    type="range"
                    min="0.0"
                    max="1.0"
                    step="0.05"
                    value={modelSettings.metalness}
                    onChange={(e) => updateModelSettings({ metalness: parseFloat(e.target.value), preset: 'custom' })}
                    className="flex-1 accent-indigo-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-indigo-300 w-10 text-right font-semibold">
                    {(modelSettings.metalness * 100).toFixed(0)}%
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-24 shrink-0">クリアコート光沢</span>
                  <input
                    type="range"
                    min="0.0"
                    max="1.0"
                    step="0.05"
                    value={modelSettings.clearcoat}
                    onChange={(e) => updateModelSettings({ clearcoat: parseFloat(e.target.value), preset: 'custom' })}
                    className="flex-1 accent-indigo-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-indigo-300 w-10 text-right font-semibold">
                    {(modelSettings.clearcoat * 100).toFixed(0)}%
                  </span>
                </div>

                {/* Rim Material Selection */}
                <div className="pt-2 border-t border-darkBorder/40">
                  <span className="text-[11px] text-gray-400 block mb-1.5">台座/リム金属マテリアル</span>
                  <div className="grid grid-cols-4 gap-1.5">
                    {[
                      { id: 'gold', label: 'Gold', color: '#d4af37' },
                      { id: 'silver', label: 'Silver', color: '#c0c5cc' },
                      { id: 'rosegold', label: 'Rose', color: '#e8a598' },
                      { id: 'black', label: 'Black', color: '#2b2d35' },
                    ].map((item) => (
                      <button
                        key={item.id}
                        onClick={() => updateModelSettings({ rimMaterial: item.id as RimMaterialType })}
                        className={`py-1 px-1 rounded flex items-center justify-center gap-1 text-[10px] font-semibold border transition-all cursor-pointer ${
                          modelSettings.rimMaterial === item.id
                            ? 'border-amber-400 bg-amber-400/15 text-gray-100 shadow-sm'
                            : 'border-darkBorder bg-darkPanel text-gray-400 hover:text-gray-200'
                        }`}
                      >
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                        {item.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </section>

            {/* 3. カラーグレーディング & シャープネス */}
            <section className="space-y-3 pt-2 border-t border-darkBorder/60">
              <h3 className="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                <Palette className="w-3.5 h-3.5 text-amber-400" />
                色味調整 & シャープネス
              </h3>

              <div className="space-y-2.5 bg-darkCard p-3 rounded-lg border border-darkBorder text-xs">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-24 shrink-0">彩度 (Saturation)</span>
                  <input
                    type="range"
                    min="0.0"
                    max="2.5"
                    step="0.05"
                    value={modelSettings.colorGrading.saturation}
                    onChange={(e) => updateColorGrading({ saturation: parseFloat(e.target.value) })}
                    className="flex-1 accent-amber-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-amber-300 w-10 text-right font-semibold">
                    {modelSettings.colorGrading.saturation.toFixed(2)}x
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-24 shrink-0">コントラスト</span>
                  <input
                    type="range"
                    min="0.5"
                    max="2.0"
                    step="0.05"
                    value={modelSettings.colorGrading.contrast}
                    onChange={(e) => updateColorGrading({ contrast: parseFloat(e.target.value) })}
                    className="flex-1 accent-indigo-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-indigo-300 w-10 text-right font-semibold">
                    {modelSettings.colorGrading.contrast.toFixed(2)}x
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-24 shrink-0">明度 (Brightness)</span>
                  <input
                    type="range"
                    min="-0.4"
                    max="0.4"
                    step="0.02"
                    value={modelSettings.colorGrading.brightness}
                    onChange={(e) => updateColorGrading({ brightness: parseFloat(e.target.value) })}
                    className="flex-1 accent-indigo-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-indigo-300 w-10 text-right font-semibold">
                    {modelSettings.colorGrading.brightness > 0 ? `+${modelSettings.colorGrading.brightness.toFixed(2)}` : modelSettings.colorGrading.brightness.toFixed(2)}
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-24 shrink-0">色相 (Hue)</span>
                  <input
                    type="range"
                    min="-180"
                    max="180"
                    step="5"
                    value={modelSettings.colorGrading.hue}
                    onChange={(e) => updateColorGrading({ hue: parseFloat(e.target.value) })}
                    className="flex-1 accent-indigo-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-indigo-300 w-10 text-right font-semibold">
                    {modelSettings.colorGrading.hue}°
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2 pt-1 border-t border-darkBorder/40">
                  <span className="text-gray-400 w-24 shrink-0">シャープネス</span>
                  <input
                    type="range"
                    min="0.0"
                    max="2.0"
                    step="0.1"
                    value={modelSettings.colorGrading.sharpness}
                    onChange={(e) => updateColorGrading({ sharpness: parseFloat(e.target.value) })}
                    className="flex-1 accent-emerald-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-emerald-300 w-10 text-right font-semibold">
                    {modelSettings.colorGrading.sharpness.toFixed(1)}
                  </span>
                </div>
              </div>
            </section>
          </>
        )}

        {/* TAB 3: CLUSTERS & ANCHOR */}
        {activeSubTab === 'clusters' && (
          <>
            {/* Anchor Coordinates */}
            <section className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
                  <Crosshair className="w-3.5 h-3.5 text-amber-400" />
                  中心点 (Anchor Pivot)
                </h3>
                <button
                  onClick={resetAnchor}
                  className="text-[11px] text-amber-400 hover:text-amber-300 transition-colors cursor-pointer"
                >
                  中央にリセット
                </button>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="bg-darkCard p-2.5 rounded-lg border border-darkBorder">
                  <span className="text-[10px] font-medium text-gray-400 block mb-1">Anchor X (U)</span>
                  <div className="flex items-center justify-between">
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.005"
                      value={anchor.u}
                      onChange={(e) => setAnchor({ u: parseFloat(e.target.value), v: anchor.v })}
                      className="w-20 accent-amber-400 cursor-pointer"
                    />
                    <span className="text-xs font-mono font-bold text-amber-300">
                      {(anchor.u * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>

                <div className="bg-darkCard p-2.5 rounded-lg border border-darkBorder">
                  <span className="text-[10px] font-medium text-gray-400 block mb-1">Anchor Y (V)</span>
                  <div className="flex items-center justify-between">
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.005"
                      value={anchor.v}
                      onChange={(e) => setAnchor({ u: anchor.u, v: parseFloat(e.target.value) })}
                      className="w-20 accent-amber-400 cursor-pointer"
                    />
                    <span className="text-xs font-mono font-bold text-amber-300">
                      {(anchor.v * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            </section>

            {/* Clustering Settings */}
            <section className="space-y-3 pt-2 border-t border-darkBorder/60">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
                  <Palette className="w-3.5 h-3.5 text-indigo-400" />
                  近似色クラスタリング (F-2)
                </h3>
              </div>

              <div className="space-y-3 bg-darkCard p-3 rounded-lg border border-darkBorder">
                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-gray-400">クラスタ数 (K)</span>
                    <span className="font-mono text-indigo-300 font-bold">{clusterCount} 色</span>
                  </div>
                  <input
                    type="range"
                    min="2"
                    max="16"
                    value={clusterCount}
                    onChange={(e) => setClusterCount(parseInt(e.target.value))}
                    className="w-full accent-indigo-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-gray-400">平滑化フィルタ (Blur)</span>
                    <span className="font-mono text-indigo-300 font-bold">{blurRadius} px</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="5"
                    step="1"
                    value={blurRadius}
                    onChange={(e) => setBlurRadius(parseInt(e.target.value))}
                    className="w-full accent-indigo-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                </div>

                <button
                  disabled={!image || isClustering}
                  onClick={() => runClustering()}
                  className={`w-full py-2 px-3 rounded-md text-xs font-bold flex items-center justify-center gap-2 shadow-md transition-all cursor-pointer ${
                    !image
                      ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
                      : isClustering
                      ? 'bg-indigo-600/50 text-indigo-200 cursor-wait'
                      : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/20'
                  }`}
                >
                  {isClustering ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      CIELAB 解析中...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="w-3.5 h-3.5" />
                      クラスタリング再実行
                    </>
                  )}
                </button>
              </div>
            </section>

            {/* Cluster Groups */}
            {clusters.length > 0 && (
              <section className="pt-2 border-t border-darkBorder/60">
                <ClusterList />
              </section>
            )}
          </>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-darkBorder text-[10px] text-gray-500 text-center font-mono shrink-0">
        PhotoToJewelry3D - PBR Jewelry Studio
      </div>
    </aside>
  );
};