import React, { useState } from 'react';
import { useJewelryStore } from '../store/useJewelryStore';
import { ClusterList } from './ClusterList';
import { AnatomyPartType, SkinTonePreset } from '../types';
import { User, Sliders, Palette, Mountain, Sparkles, SplitSquareVertical } from 'lucide-react';

export const AnatomyControlPanel: React.FC = () => {
  const {
    anatomySettings,
    updateAnatomySettings,
    applySkinTonePreset,
    setAnatomyPart,
  } = useJewelryStore();

  const [activeSubTab, setActiveSubTab] = useState<'part' | 'skin' | 'clusters'>('part');

  return (
    <aside className="w-92 h-full bg-darkPanel border-l border-darkBorder flex flex-col shrink-0 overflow-hidden">
      {/* Header */}
      <div className="p-3 border-b border-darkBorder flex flex-col gap-2 shrink-0 bg-darkPanel">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <User className="w-4 h-4 text-rose-400" />
            <h2 className="text-sm font-bold text-gray-200">人体パーツ・解剖造形</h2>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/15 border border-rose-500/30 text-rose-300 font-semibold">
            Anatomy Studio
          </span>
        </div>

        {/* Sub-Tabs */}
        <div className="grid grid-cols-3 gap-1 bg-darkBg p-1 rounded-lg border border-darkBorder text-xs">
          <button
            onClick={() => setActiveSubTab('part')}
            className={`py-1 rounded font-medium transition-all flex items-center justify-center gap-1 cursor-pointer ${
              activeSubTab === 'part'
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold shadow-sm'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            <Sliders className="w-3 h-3" />
            パーツ形状
          </button>
          <button
            onClick={() => setActiveSubTab('skin')}
            className={`py-1 rounded font-medium transition-all flex items-center justify-center gap-1 cursor-pointer ${
              activeSubTab === 'skin'
                ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-bold shadow-sm'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            <Sparkles className="w-3 h-3" />
            肌質・SSS
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

      {/* Tab Content */}
      <div className="p-4 space-y-5 flex-1 overflow-y-auto">
        {/* TAB 1: PART SHAPES */}
        {activeSubTab === 'part' && (
          <>
            <section className="space-y-4">
              {/* 1. 人体パーツグループ */}
              <div className="space-y-2">
                <h4 className="text-[11px] font-bold text-rose-300 flex items-center gap-1">
                  👤 人体・顔パーツ
                </h4>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: 'nose', label: '👃 鼻 (Nose Bridge)', desc: '鼻筋・鼻尖・小鼻' },
                    { id: 'ear', label: '👂 耳 (Ear Concha)', desc: '耳輪・軟骨・耳甲介' },
                    { id: 'lips', label: '👄 唇 (Lips & Bow)', desc: 'キューピッド弓・口唇' },
                    { id: 'face_contour', label: '🧑 顔面曲面 (Contour)', desc: '頬・額・顎の有機曲面' },
                    { id: 'eye', label: '👁️ 目 (Eye & Lid)', desc: '眼球ドーム・まぶた皺' },
                    { id: 'breast', label: '🍒 乳房 (Breast)', desc: 'なだらかな膨らみ・乳頭' },
                    { id: 'penis', label: '🍆 男性器 (Penis)', desc: 'シャフト・亀頭の起伏' },
                    { id: 'vulva', label: '🐚 女性器 (Vulva)', desc: '大陰唇・縦スリットの谷' },
                  ].map((item) => (
                    <button
                      key={item.id}
                      onClick={() => setAnatomyPart(item.id as AnatomyPartType)}
                      className={`p-2 rounded-xl border flex flex-col items-start gap-0.5 transition-all text-left cursor-pointer ${
                        anatomySettings.partType === item.id
                          ? 'border-rose-400 bg-rose-500/15 text-rose-200 font-bold shadow-md shadow-rose-500/10'
                          : 'border-darkBorder bg-darkCard text-gray-400 hover:text-gray-200'
                      }`}
                    >
                      <span className="text-[11px] font-bold">{item.label}</span>
                      <span className="text-[9px] text-gray-400 leading-tight">{item.desc}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* 2. 自然物・景観グループ */}
              <div className="space-y-2 pt-2 border-t border-darkBorder/40">
                <h4 className="text-[11px] font-bold text-emerald-300 flex items-center gap-1">
                  🌿 自然物・景観
                </h4>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: 'rock', label: '🪨 岩 (Rock)', desc: 'ゴツゴツした岩肌・突起' },
                    { id: 'wall', label: '🧱 壁 (Wall)', desc: 'レンガ・石垣調のタイルの溝' },
                    { id: 'grass', label: '🌱 草 (Grass)', desc: '針状突起の集まった芝生' },
                    { id: 'tree', label: '🪵 木 (Tree/Bark)', desc: '樹皮状の縦スジ木肌' },
                    { id: 'terrain', label: '🏔️ 地形 (Terrain)', desc: '砂丘やなだらかな波の干渉' },
                    { id: 'puddle', label: '💧 水たまり (Puddle)', desc: '中心が平たく窪むお皿状' },
                  ].map((item) => (
                    <button
                      key={item.id}
                      onClick={() => setAnatomyPart(item.id as AnatomyPartType)}
                      className={`p-2 rounded-xl border flex flex-col items-start gap-0.5 transition-all text-left cursor-pointer ${
                        anatomySettings.partType === item.id
                          ? 'border-emerald-400 bg-emerald-500/15 text-emerald-200 font-bold shadow-md shadow-emerald-500/10'
                          : 'border-darkBorder bg-darkCard text-gray-400 hover:text-gray-200'
                      }`}
                    >
                      <span className="text-[11px] font-bold">{item.label}</span>
                      <span className="text-[9px] text-gray-400 leading-tight">{item.desc}</span>
                    </button>
                  ))}
                </div>
              </div>
            </section>

            {/* 2. 左右対称 (Symmetry) & 形状パラメータ */}
            <section className="space-y-3 pt-2 border-t border-darkBorder/60">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                  <SplitSquareVertical className="w-3.5 h-3.5 text-rose-400" />
                  左右対称・骨格プロポーション
                </h3>
                <button
                  onClick={() => updateAnatomySettings({ symmetry: !anatomySettings.symmetry })}
                  className={`text-[10px] px-2 py-0.5 rounded font-semibold transition-colors cursor-pointer ${
                    anatomySettings.symmetry
                      ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                      : 'bg-darkCard text-gray-500 border border-darkBorder'
                  }`}
                >
                  {anatomySettings.symmetry ? '対称ミラー ON' : '非対称 OFF'}
                </button>
              </div>

              <div className="space-y-2.5 bg-darkCard p-3 rounded-lg border border-darkBorder text-xs">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-24 shrink-0">隆起・高さ (Bridge)</span>
                  <input
                    type="range"
                    min="0.3"
                    max="2.5"
                    step="0.05"
                    value={anatomySettings.bridgeHeight}
                    onChange={(e) => updateAnatomySettings({ bridgeHeight: parseFloat(e.target.value) })}
                    className="flex-1 accent-rose-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-rose-300 w-10 text-right font-semibold">
                    {anatomySettings.bridgeHeight.toFixed(2)}x
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-24 shrink-0">幅・張り出し (Width)</span>
                  <input
                    type="range"
                    min="0.4"
                    max="2.2"
                    step="0.05"
                    value={anatomySettings.alaWidth}
                    onChange={(e) => updateAnatomySettings({ alaWidth: parseFloat(e.target.value) })}
                    className="flex-1 accent-rose-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-rose-300 w-10 text-right font-semibold">
                    {anatomySettings.alaWidth.toFixed(2)}x
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2 pt-1 border-t border-darkBorder/40">
                  <span className="text-gray-400 w-24 shrink-0">有機湾曲 (Curve)</span>
                  <input
                    type="range"
                    min="0.2"
                    max="2.0"
                    step="0.05"
                    value={anatomySettings.curvature}
                    onChange={(e) => updateAnatomySettings({ curvature: parseFloat(e.target.value) })}
                    className="flex-1 accent-indigo-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-indigo-300 w-10 text-right font-semibold">
                    {anatomySettings.curvature.toFixed(2)}
                  </span>
                </div>
              </div>
            </section>

            {/* 3. 有機ディスプレイスメント & スムージング */}
            <section className="space-y-3 pt-2 border-t border-darkBorder/60">
              <h3 className="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                <Mountain className="w-3.5 h-3.5 text-rose-400" />
                有機ディスプレイスメント (段差成形)
              </h3>

              <div className="space-y-2.5 bg-darkCard p-3 rounded-lg border border-darkBorder text-xs">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-24 shrink-0">成形強度 (Scale)</span>
                  <input
                    type="range"
                    min="0.0"
                    max="1.5"
                    step="0.05"
                    value={anatomySettings.displacementScale}
                    onChange={(e) => updateAnatomySettings({ displacementScale: parseFloat(e.target.value) })}
                    className="flex-1 accent-rose-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-rose-300 w-10 text-right font-semibold">
                    {anatomySettings.displacementScale.toFixed(2)}
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-24 shrink-0">有機スムージング</span>
                  <input
                    type="range"
                    min="0.0"
                    max="2.0"
                    step="0.1"
                    value={anatomySettings.bevelSmoothness}
                    onChange={(e) => updateAnatomySettings({ bevelSmoothness: parseFloat(e.target.value) })}
                    className="flex-1 accent-indigo-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-indigo-300 w-10 text-right font-semibold">
                    {anatomySettings.bevelSmoothness.toFixed(1)}
                  </span>
                </div>
              </div>
            </section>
          </>
        )}

        {/* TAB 2: SKIN & SSS SHADER */}
        {activeSubTab === 'skin' && (
          <>
            {/* 1. スキントーンプリセット */}
            <section className="space-y-3">
              <h3 className="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-rose-400" />
                肌色・トーンプリセット
              </h3>
              <div className="grid grid-cols-3 gap-1.5">
                {[
                  { id: 'fair', label: '🌸 Fair (色白)' },
                  { id: 'natural', label: '☀️ Natural (標準)' },
                  { id: 'tan', label: '🏖️ Tan (小麦色)' },
                  { id: 'deep', label: '🍫 Deep (褐色)' },
                  { id: 'sculpt_clay', label: '🏺 クレイ彫刻' },
                  { id: 'custom', label: '⚙️ カスタム' },
                ].map((p) => (
                  <button
                    key={p.id}
                    onClick={() => applySkinTonePreset(p.id as SkinTonePreset)}
                    className={`py-2 px-1 rounded text-[10px] font-medium border text-center transition-all cursor-pointer ${
                      anatomySettings.skinPreset === p.id
                        ? 'border-rose-400 bg-rose-400/15 text-rose-200 font-bold shadow-sm'
                        : 'border-darkBorder bg-darkCard text-gray-400 hover:text-gray-200'
                    }`}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </section>

            {/* 2. SSS 散乱 & 皮膚質感 */}
            <section className="space-y-3 pt-2 border-t border-darkBorder/60">
              <h3 className="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-rose-400" />
                SSS 表面下散乱 & 皮膚光沢
              </h3>

              <div className="space-y-2.5 bg-darkCard p-3 rounded-lg border border-darkBorder text-xs">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-24 shrink-0">SSS 赤み透け (Scatter)</span>
                  <input
                    type="range"
                    min="0.0"
                    max="1.0"
                    step="0.05"
                    value={anatomySettings.subsurfaceScattering}
                    onChange={(e) => updateAnatomySettings({ subsurfaceScattering: parseFloat(e.target.value), skinPreset: 'custom' })}
                    className="flex-1 accent-rose-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-rose-300 w-10 text-right font-semibold">
                    {(anatomySettings.subsurfaceScattering * 100).toFixed(0)}%
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2">
                  <span className="text-gray-400 w-24 shrink-0">皮膚光沢・皮脂感</span>
                  <input
                    type="range"
                    min="0.0"
                    max="1.0"
                    step="0.05"
                    value={1.0 - anatomySettings.skinRoughness}
                    onChange={(e) => updateAnatomySettings({ skinRoughness: 1.0 - parseFloat(e.target.value), skinPreset: 'custom' })}
                    className="flex-1 accent-amber-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-amber-300 w-10 text-right font-semibold">
                    {((1.0 - anatomySettings.skinRoughness) * 100).toFixed(0)}%
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2 pt-1 border-t border-darkBorder/40">
                  <span className="text-gray-400 w-24 shrink-0">毛穴・キメ微細バンプ</span>
                  <input
                    type="range"
                    min="0.0"
                    max="1.0"
                    step="0.05"
                    value={anatomySettings.poreBumpIntensity}
                    onChange={(e) => updateAnatomySettings({ poreBumpIntensity: parseFloat(e.target.value) })}
                    className="flex-1 accent-indigo-400 cursor-pointer h-1.5 bg-darkPanel rounded"
                  />
                  <span className="font-mono text-indigo-300 w-10 text-right font-semibold">
                    {(anatomySettings.poreBumpIntensity * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </section>
          </>
        )}

        {/* TAB 3: CLUSTERS */}
        {activeSubTab === 'clusters' && (
          <section className="space-y-3">
            <ClusterList />
          </section>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-darkBorder text-[10px] text-gray-500 text-center font-mono shrink-0">
        Anatomy Studio - Organic 3D Generator
      </div>
    </aside>
  );
};