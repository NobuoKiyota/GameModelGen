import React, { useRef, useState, useEffect, useCallback } from 'react';
import { useJewelryStore } from '../store/useJewelryStore';
import { UploadCloud, ZoomIn, ZoomOut, Maximize2, Crosshair, HelpCircle, Eye, EyeOff, Loader2, Pipette, RotateCw } from 'lucide-react';

export const ImageEditor2D: React.FC = () => {
  const {
    image,
    setImage,
    anchor,
    setAnchor,
    viewport2D,
    setViewport2D,
    resetViewport2D,
    resetAnchor,
    isClustering,
    clusters,
    clusterOverlayUrl,
    showClusterOverlay,
    setShowClusterOverlay,
    overlayOpacity,
    setOverlayOpacity,
    selectClusterAtUv,
    selectedClusterId,
    rotateImageAbsolute,
    imageRotation,
  } = useJewelryStore();

  const [tempRotation, setTempRotation] = useState<number>(0);

  useEffect(() => {
    if (image) {
      setTempRotation(imageRotation);
    } else {
      setTempRotation(0);
    }
  }, [image, imageRotation]);

  const containerRef = useRef<HTMLDivElement>(null);
  const [isDraggingPan, setIsDraggingPan] = useState(false);
  const [isDraggingAnchor, setIsDraggingAnchor] = useState(false);
  const dragStartRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const panStartRef = useRef<{ panX: number; panY: number }>({ panX: 0, panY: 0 });

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
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
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const getNormalizedCoords = useCallback(
    (clientX: number, clientY: number) => {
      if (!containerRef.current || !image) return null;
      const rect = containerRef.current.getBoundingClientRect();
      const mouseX = clientX - rect.left;
      const mouseY = clientY - rect.top;

      const cx = rect.width / 2;
      const cy = rect.height / 2;

      const aspect = image.width / image.height;
      let drawW = rect.width * 0.85;
      let drawH = drawW / aspect;
      if (drawH > rect.height * 0.85) {
        drawH = rect.height * 0.85;
        drawW = drawH * aspect;
      }

      const imgCenterX = cx + viewport2D.panX;
      const imgCenterY = cy + viewport2D.panY;
      const curW = drawW * viewport2D.zoom;
      const curH = drawH * viewport2D.zoom;

      const imgLeft = imgCenterX - curW / 2;
      const imgTop = imgCenterY - curH / 2;

      const u = (mouseX - imgLeft) / curW;
      const v = (mouseY - imgTop) / curH;

      return { u, v, imgLeft, imgTop, curW, curH };
    },
    [image, viewport2D]
  );

  const handleWheel = (e: React.WheelEvent) => {
    if (!image) return;
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
    const newZoom = Math.max(0.2, Math.min(10, viewport2D.zoom * zoomFactor));
    setViewport2D({ zoom: newZoom });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!image) return;

    const coords = getNormalizedCoords(e.clientX, e.clientY);
    if (!coords) return;

    const anchorScreenX = coords.imgLeft + anchor.u * coords.curW;
    const anchorScreenY = coords.imgTop + anchor.v * coords.curH;
    const containerRect = containerRef.current?.getBoundingClientRect();
    if (!containerRect) return;

    const mouseX = e.clientX - containerRect.left;
    const mouseY = e.clientY - containerRect.top;
    const distToAnchor = Math.hypot(mouseX - anchorScreenX, mouseY - anchorScreenY);

    if (distToAnchor <= 20) {
      setIsDraggingAnchor(true);
    } else if (e.button === 1 || e.shiftKey || e.altKey) {
      setIsDraggingPan(true);
      dragStartRef.current = { x: e.clientX, y: e.clientY };
      panStartRef.current = { panX: viewport2D.panX, panY: viewport2D.panY };
    } else if (e.button === 0) {
      if (e.detail === 2) {
        if (coords.u >= 0 && coords.u <= 1 && coords.v >= 0 && coords.v <= 1) {
          setAnchor({ u: coords.u, v: coords.v });
        }
        return;
      }

      // Single click: Pick cluster under cursor
      if (coords.u >= 0 && coords.u <= 1 && coords.v >= 0 && coords.v <= 1) {
        selectClusterAtUv(coords.u, coords.v);
      }

      setIsDraggingPan(true);
      dragStartRef.current = { x: e.clientX, y: e.clientY };
      panStartRef.current = { panX: viewport2D.panX, panY: viewport2D.panY };
    }
  };

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (isDraggingAnchor) {
        const coords = getNormalizedCoords(e.clientX, e.clientY);
        if (coords) {
          setAnchor({
            u: Math.max(0, Math.min(1, coords.u)),
            v: Math.max(0, Math.min(1, coords.v)),
          });
        }
      } else if (isDraggingPan) {
        const dx = e.clientX - dragStartRef.current.x;
        const dy = e.clientY - dragStartRef.current.y;
        setViewport2D({
          panX: panStartRef.current.panX + dx,
          panY: panStartRef.current.panY + dy,
        });
      }
    },
    [isDraggingAnchor, isDraggingPan, getNormalizedCoords, setAnchor, setViewport2D]
  );

  const handleMouseUp = useCallback(() => {
    setIsDraggingAnchor(false);
    setIsDraggingPan(false);
  }, []);

  const handlePaste = useCallback(
    (e: ClipboardEvent) => {
      const items = e.clipboardData?.items;
      if (!items) return;

      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if (item.type.startsWith('image/')) {
          const file = item.getAsFile();
          if (!file) continue;

          const url = URL.createObjectURL(file);
          const img = new Image();
          img.onload = () => {
            setImage({
              url,
              width: img.naturalWidth,
              height: img.naturalHeight,
              name: file.name || `clipboard-${Date.now()}.png`,
            });
          };
          img.src = url;
          e.preventDefault();
          break;
        }
      }
    },
    [setImage]
  );

  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    window.addEventListener('paste', handlePaste);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('paste', handlePaste);
    };
  }, [handleMouseMove, handleMouseUp, handlePaste]);

  return (
    <div
      ref={containerRef}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      className="relative w-full h-full bg-[#0a0c12] overflow-hidden flex items-center justify-center select-none cursor-grab active:cursor-grabbing"
    >
      <div 
        className="absolute inset-0 opacity-[0.07] pointer-events-none"
        style={{
          backgroundImage: 'radial-gradient(#8f9bb3 1px, transparent 1px)',
          backgroundSize: '24px 24px'
        }}
      />

      {!image ? (
        <div className="flex flex-col items-center justify-center p-8 text-center max-w-sm border-2 border-dashed border-darkBorder rounded-2xl bg-darkCard/40 backdrop-blur-sm pointer-events-auto">
          <div className="w-14 h-14 rounded-full bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mb-4 text-amber-400">
            <UploadCloud className="w-7 h-7" />
          </div>
          <h3 className="text-base font-semibold text-gray-200 mb-1">画像をドラッグ＆ドロップ</h3>
          <p className="text-xs text-gray-400 mb-4 leading-relaxed">
            ペンダントトップ、指輪、カボションなどの正面画像をドロップして解析を開始
          </p>
          <label className="px-4 py-2 text-xs font-medium bg-amber-500 hover:bg-amber-400 text-darkBg rounded-lg cursor-pointer transition-colors shadow-lg shadow-amber-500/20 font-bold">
            ファイルを選択
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => {
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
              }}
            />
          </label>
        </div>
      ) : (
        <>
          <div
            className="absolute transition-transform duration-75 will-change-transform pointer-events-none"
            style={{
              transform: `translate(${viewport2D.panX}px, ${viewport2D.panY}px) scale(${viewport2D.zoom})`,
            }}
          >
            <div 
              className="relative shadow-2xl border border-darkBorder/60 rounded-sm bg-black/40 overflow-visible will-change-transform"
              style={{ transform: `rotate(${tempRotation - imageRotation}deg)` }}
            >
              <img
                src={image.url}
                alt={image.name}
                className="max-w-[80vw] max-h-[70vh] object-contain block pointer-events-none"
                draggable={false}
              />

              {/* Cluster Distribution Overlay Map */}
              {showClusterOverlay && clusterOverlayUrl && (
                <img
                  src={clusterOverlayUrl}
                  alt="Cluster Overlay"
                  className="absolute inset-0 w-full h-full object-fill pointer-events-none transition-opacity duration-150 mix-blend-screen"
                  style={{ opacity: overlayOpacity }}
                />
              )}

              {/* Anchor Target */}
              <div
                className="absolute transform -translate-x-1/2 -translate-y-1/2 pointer-events-auto cursor-move z-20 group"
                style={{
                  left: `${anchor.u * 100}%`,
                  top: `${anchor.v * 100}%`,
                }}
                title="中心点 (3D投影の極) - ドラッグして移動"
              >
                <div className="relative flex items-center justify-center">
                  <div className="w-10 h-10 rounded-full border border-amber-400/60 bg-amber-400/10 animate-pulse" />
                  <div className="absolute w-5 h-5 rounded-full border-2 border-amber-400 bg-amber-500/30 shadow-[0_0_12px_rgba(245,158,11,0.8)] group-hover:scale-125 transition-transform" />
                  <div className="absolute w-1.5 h-1.5 rounded-full bg-amber-300 shadow-[0_0_6px_#fff]" />
                  <div className="absolute w-12 h-px bg-gradient-to-r from-transparent via-amber-400 to-transparent" />
                  <div className="absolute h-12 w-px bg-gradient-to-b from-transparent via-amber-400 to-transparent" />

                  <div className="absolute -top-7 left-1/2 -translate-x-1/2 px-1.5 py-0.5 rounded bg-darkPanel/90 border border-amber-500/40 text-[10px] text-amber-300 font-mono whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none shadow-md">
                    ({(anchor.u * 100).toFixed(1)}%, {(anchor.v * 100).toFixed(1)}%)
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Top-Right: Overlay HUD Controls */}
          {clusters.length > 0 && (
            <div className="absolute top-4 right-4 z-30 flex items-center gap-2 bg-darkPanel/90 border border-darkBorder backdrop-blur-md px-3 py-1.5 rounded-lg shadow-xl text-xs">
              <button
                onClick={() => setShowClusterOverlay(!showClusterOverlay)}
                className={`flex items-center gap-1.5 px-2 py-1 rounded text-[11px] font-medium transition-colors cursor-pointer ${
                  showClusterOverlay
                    ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                    : 'bg-darkCard text-gray-400 border border-darkBorder hover:text-gray-200'
                }`}
                title="クラスタ分布図オーバーレイの表示/非表示"
              >
                {showClusterOverlay ? <Eye className="w-3.5 h-3.5 text-indigo-400" /> : <EyeOff className="w-3.5 h-3.5" />}
                分布オーバーレイ
              </button>

              {showClusterOverlay && (
                <div className="flex items-center gap-1.5 border-l border-darkBorder pl-2">
                  <span className="text-[10px] text-gray-400">不透明度</span>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.05"
                    value={overlayOpacity}
                    onChange={(e) => setOverlayOpacity(parseFloat(e.target.value))}
                    className="w-16 accent-indigo-400 cursor-pointer h-1.5 bg-darkBorder rounded"
                  />
                  <span className="text-[10px] font-mono text-indigo-300 w-7 text-right">
                    {Math.round(overlayOpacity * 100)}%
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Top-Left: Status HUD */}
          <div className="absolute top-4 left-4 z-30 flex items-center gap-2 bg-darkPanel/80 border border-darkBorder backdrop-blur-md px-3 py-1.5 rounded-lg shadow-md text-[11px] text-gray-400">
            {isClustering ? (
              <span className="flex items-center gap-1.5 text-amber-300 font-medium animate-pulse">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Web Workerで色クラスタ解析中...
              </span>
            ) : selectedClusterId !== null ? (
              <span className="flex items-center gap-1.5 text-amber-300 font-bold animate-pulse">
                <Pipette className="w-3.5 h-3.5 text-amber-400" />
                グループ #{selectedClusterId + 1} をハイライト中 (画像クリックで別色を選択)
              </span>
            ) : (
              <span className="flex items-center gap-1.5">
                <HelpCircle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                クリック: カラー層ピッキング | ドラッグ: パン | ホイール: ズーム | 🟡中心点調整
              </span>
            )}
          </div>

          {/* Bottom-Left Controls */}
          <div className="absolute bottom-4 left-4 z-30 flex items-center gap-1.5 bg-darkPanel/90 border border-darkBorder backdrop-blur-md px-2.5 py-1.5 rounded-lg shadow-xl text-xs text-gray-300">
            <button
              onClick={() => setViewport2D({ zoom: Math.min(10, viewport2D.zoom * 1.25) })}
              className="p-1 hover:bg-darkBorder rounded text-gray-300 hover:text-white transition-colors cursor-pointer"
              title="ズームイン"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewport2D({ zoom: Math.max(0.2, viewport2D.zoom * 0.8) })}
              className="p-1 hover:bg-darkBorder rounded text-gray-300 hover:text-white transition-colors cursor-pointer"
              title="ズームアウト"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <button
              onClick={resetViewport2D}
              className="p-1 hover:bg-darkBorder rounded text-gray-300 hover:text-white transition-colors cursor-pointer"
              title="表示倍率をリセット"
            >
              <Maximize2 className="w-3.5 h-3.5" />
            </button>
            <div className="h-3 w-px bg-darkBorder mx-1" />
            <button
              onClick={resetAnchor}
              className="flex items-center gap-1 px-1.5 py-0.5 hover:bg-darkBorder rounded text-[11px] text-amber-400 font-medium transition-colors cursor-pointer"
              title="アンカーを中心(50%, 50%)に戻す"
            >
              <Crosshair className="w-3.5 h-3.5" />
              中央
            </button>
            <div className="h-3 w-px bg-darkBorder mx-1" />
            <div className="flex items-center gap-1.5 px-1.5">
              <RotateCw className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
              <span className="text-[10px] text-gray-400 shrink-0">回転</span>
              <input
                type="range"
                min="0"
                max="360"
                step="1"
                value={tempRotation}
                disabled={isClustering}
                onChange={(e) => setTempRotation(parseInt(e.target.value))}
                onMouseUp={() => {
                  if (tempRotation !== imageRotation) {
                    rotateImageAbsolute(tempRotation);
                  }
                }}
                onTouchEnd={() => {
                  if (tempRotation !== imageRotation) {
                    rotateImageAbsolute(tempRotation);
                  }
                }}
                onKeyUp={(e) => {
                  if (e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === 'ArrowUp' || e.key === 'ArrowDown') {
                    rotateImageAbsolute(tempRotation);
                  }
                }}
                className="w-24 accent-indigo-400 cursor-pointer h-1.5 bg-darkBorder rounded disabled:opacity-50"
              />
              <span className="text-[10px] font-mono text-indigo-300 w-8 text-right font-semibold">
                {tempRotation}°
              </span>
            </div>
            <span className="text-[11px] font-mono text-gray-400 ml-1">
              {Math.round(viewport2D.zoom * 100)}%
            </span>
          </div>
        </>
      )}
    </div>
  );
};