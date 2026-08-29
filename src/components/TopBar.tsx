import React, { useRef, useState } from 'react';
import { useJewelryStore } from '../store/useJewelryStore';
import { ExportModal } from './ExportModal';
import { Gem, Download, FolderOpen, Save, RefreshCw, Layers, User } from 'lucide-react';

export const TopBar: React.FC = () => {
  const {
    studioMode,
    setStudioMode,
    image,
    setImage,
    anchor,
    setAnchor,
    clusters,
    clusterCount,
    setClusterCount,
    blurRadius,
    setBlurRadius,
    setClusters,
    modelSettings,
    updateModelSettings,
    anatomySettings,
    updateAnatomySettings,
    resetAnchor,
    resetViewport2D,
  } = useJewelryStore();

  const fileInputRef = useRef<HTMLInputElement>(null);
  const projectInputRef = useRef<HTMLInputElement>(null);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      setImage({
        url,
        width: img.naturalWidth,
        height: img.naturalHeight,
        name: file.name,
      });
    };
    img.src = url;
  };

  const handleReset = () => {
    resetAnchor();
    resetViewport2D();
  };

  // Project JSON Save
  const handleSaveProject = () => {
    const projectData = {
      version: '1.1.0',
      timestamp: new Date().toISOString(),
      studioMode,
      image: image ? { name: image.name, width: image.width, height: image.height, dataUrl: image.url } : null,
      anchor,
      clusters,
      clusterCount,
      blurRadius,
      modelSettings,
      anatomySettings,
    };

    const blob = new Blob([JSON.stringify(projectData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${image?.name.replace(/\.[^/.]+$/, '') || '3d_sculpt_project'}.p3j`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Project JSON Load
  const handleLoadProject = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target?.result as string);
        if (data.studioMode) setStudioMode(data.studioMode);
        if (data.image) {
          setImage({
            url: data.image.dataUrl,
            width: data.image.width,
            height: data.image.height,
            name: data.image.name,
          });
        }
        if (data.anchor) setAnchor(data.anchor);
        if (data.clusters) setClusters(data.clusters);
        if (data.clusterCount) setClusterCount(data.clusterCount);
        if (data.blurRadius) setBlurRadius(data.blurRadius);
        if (data.modelSettings) updateModelSettings(data.modelSettings);
        if (data.anatomySettings) updateAnatomySettings(data.anatomySettings);
      } catch (err) {
        console.error('Failed to load project file:', err);
        alert('プロジェクトファイルの読み込みに失敗しました。');
      }
    };
    reader.readAsText(file);
  };

  return (
    <>
      <header className="h-14 bg-darkPanel border-b border-darkBorder flex items-center justify-between px-4 z-40 select-none shrink-0">
        {/* Left: Brand & Studio Mode Tabs */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-amber-500 to-amber-300 flex items-center justify-center shadow-lg shadow-amber-500/20 text-darkBg">
              <Gem className="w-4 h-4 fill-darkBg stroke-darkBg" />
            </div>
            <div>
              <h1 className="font-bold text-xs tracking-wide text-gray-100">3D Sculpt Studio</h1>
            </div>
          </div>

          {/* Studio Mode Switcher Tabs */}
          <div className="flex items-center p-0.5 rounded-lg bg-darkBg border border-darkBorder text-xs">
            <button
              onClick={() => setStudioMode('jewelry')}
              className={`px-3 py-1 rounded-md font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                studioMode === 'jewelry'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30 shadow-sm'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              <Gem className="w-3.5 h-3.5 text-amber-400" />
              💎 ジュエリー・鉱石
            </button>
            <button
              onClick={() => setStudioMode('anatomy')}
              className={`px-3 py-1 rounded-md font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                studioMode === 'anatomy'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30 shadow-sm'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              <User className="w-3.5 h-3.5 text-rose-400" />
              👤 人体・顔パーツ (鼻/耳/唇)
            </button>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="image/*"
            className="hidden"
          />
          <input
            type="file"
            ref={projectInputRef}
            onChange={handleLoadProject}
            accept=".p3j,.json"
            className="hidden"
          />

          <button
            onClick={() => fileInputRef.current?.click()}
            className="px-3 py-1.5 text-xs font-semibold bg-darkCard hover:bg-darkBorder text-gray-200 rounded-lg border border-darkBorder transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <FolderOpen className="w-3.5 h-3.5 text-amber-400" />
            画像を開く
          </button>

          <button
            onClick={handleReset}
            className="px-3 py-1.5 text-xs font-semibold bg-darkCard hover:bg-darkBorder text-gray-300 rounded-lg border border-darkBorder transition-colors flex items-center gap-1.5 cursor-pointer"
            title="2Dビューと中心点を初期位置にリセット"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            リセット
          </button>

          <div className="h-5 w-px bg-darkBorder mx-1" />

          <button
            onClick={() => projectInputRef.current?.click()}
            className="px-2.5 py-1.5 text-xs font-semibold bg-darkCard hover:bg-darkBorder text-gray-300 rounded-lg border border-darkBorder transition-colors flex items-center gap-1.5 cursor-pointer"
            title="保存したプロジェクト(.p3j)を読み込む"
          >
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            読込
          </button>

          <button
            onClick={handleSaveProject}
            className="px-2.5 py-1.5 text-xs font-semibold bg-darkCard hover:bg-darkBorder text-gray-300 rounded-lg border border-darkBorder transition-colors flex items-center gap-1.5 cursor-pointer"
            title="現在の設定状態をプロジェクトファイル(.p3j)として保存"
          >
            <Save className="w-3.5 h-3.5 text-indigo-400" />
            保存
          </button>

          <div className="h-5 w-px bg-darkBorder mx-1" />

          <button
            onClick={() => setIsExportModalOpen(true)}
            className="px-4 py-1.5 text-xs font-bold bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-darkBg rounded-lg shadow-lg shadow-amber-500/20 transition-all flex items-center gap-1.5 cursor-pointer active:scale-95"
          >
            <Download className="w-3.5 h-3.5 stroke-[2.5]" />
            3Dエクスポート (FBX/GLB)
          </button>
        </div>
      </header>

      <ExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
      />
    </>
  );
};