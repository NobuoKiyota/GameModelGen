import React from 'react';
import { TopBar } from './components/TopBar';
import { ImageEditor2D } from './components/ImageEditor2D';
import { Viewport3D } from './components/Viewport3D';
import { ControlPanel } from './components/ControlPanel';
import { AnatomyControlPanel } from './components/AnatomyControlPanel';
import { useJewelryStore } from './store/useJewelryStore';

export const App: React.FC = () => {
  const { studioMode } = useJewelryStore();

  return (
    <div className="flex flex-col w-screen h-screen bg-darkBg text-gray-100 font-sans overflow-hidden">
      {/* Top Header */}
      <TopBar />

      {/* Main Workspace: 3 Panes */}
      <main className="flex flex-1 w-full h-[calc(100vh-3.5rem)] overflow-hidden">
        {/* Left Pane: 2D Image Editor (50% width) */}
        <section className="w-1/2 h-full flex flex-col border-r border-darkBorder relative">
          <div className="h-7 bg-darkPanel/70 border-b border-darkBorder flex items-center justify-between px-3 text-[11px] text-gray-400 shrink-0 select-none">
            <span className="font-semibold text-gray-300 flex items-center gap-1.5">
              2D 画像エディタ (アンカー基準点指定)
            </span>
            <span className="font-mono text-[10px] bg-darkCard px-1.5 py-0.5 rounded border border-darkBorder text-amber-400">
              F-1 Canvas
            </span>
          </div>
          <div className="flex-1 w-full h-full relative overflow-hidden">
            <ImageEditor2D />
          </div>
        </section>

        {/* Center Pane: 3D Realtime Viewport (remaining flex width) */}
        <section className="flex-1 h-full flex flex-col relative">
          <div className="h-7 bg-darkPanel/70 border-b border-darkBorder flex items-center justify-between px-3 text-[11px] text-gray-400 shrink-0 select-none">
            <span className="font-semibold text-gray-300 flex items-center gap-1.5">
              3D リアルタイムプレビュー (極座標投影)
            </span>
            <span className="font-mono text-[10px] bg-darkCard px-1.5 py-0.5 rounded border border-darkBorder text-indigo-400">
              F-4 Three.js
            </span>
          </div>
          <div className="flex-1 w-full h-full relative overflow-hidden">
            <Viewport3D />
          </div>
        </section>

        {/* Right Pane: Parameter Control Panel (Jewelry vs Anatomy Studio) */}
        {studioMode === 'anatomy' ? <AnatomyControlPanel /> : <ControlPanel />}
      </main>
    </div>
  );
};

export default App;