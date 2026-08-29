import { create, StateCreator } from 'zustand';
import * as THREE from 'three';
import {
  ImageInfo,
  AnchorPoint,
  Viewport2D,
  ColorCluster,
  Model3DSettings,
  MaterialPresetType,
  ColorGradingSettings,
  StudioMode,
  AnatomySettings,
  AnatomyPartType,
  SkinTonePreset,
} from '../types';
import { ClusterWorkerInput, ClusterWorkerOutput } from '../workers/clusterWorker';
import { generateHeightMapData } from '../utils/heightMapGenerator';

export interface JewelryState {
  // Studio Mode: Jewelry vs Anatomy
  studioMode: StudioMode;
  setStudioMode: (mode: StudioMode) => void;

  image: ImageInfo | null;
  setImage: (img: ImageInfo | null) => void;
  originalImage: ImageInfo | null;
  originalAnchor: AnchorPoint;
  imageRotation: number;

  anchor: AnchorPoint;
  setAnchor: (anchor: AnchorPoint) => void;
  resetAnchor: () => void;

  viewport2D: Viewport2D;
  setViewport2D: (viewport: Partial<Viewport2D>) => void;
  resetViewport2D: () => void;

  // Phase 2: Clustering
  clusterCount: number;
  setClusterCount: (count: number) => void;
  blurRadius: number;
  setBlurRadius: (blur: number) => void;
  isClustering: boolean;
  setIsClustering: (isClustering: boolean) => void;
  clusters: ColorCluster[];
  setClusters: (clusters: ColorCluster[]) => void;
  updateCluster: (id: number, partial: Partial<ColorCluster>) => void;
  clusterMap: Uint8Array | null;
  clusterMapWidth: number;
  clusterMapHeight: number;
  setClusterMap: (map: Uint8Array | null, width?: number, height?: number) => void;
  clusterOverlayUrl: string | null;
  setClusterOverlayUrl: (url: string | null) => void;
  showClusterOverlay: boolean;
  setShowClusterOverlay: (show: boolean) => void;
  overlayOpacity: number;
  setOverlayOpacity: (opacity: number) => void;
  runClustering: () => Promise<void>;
  refreshOverlay: () => void;

  // Interactive Selection & Eye-Dropper
  selectedClusterId: number | null;
  setSelectedClusterId: (id: number | null) => void;
  hoveredClusterId: number | null;
  setHoveredClusterId: (id: number | null) => void;
  selectClusterAtUv: (u: number, v: number) => number | null;

  // Heightmap & Displacement
  heightMapTexture: THREE.DataTexture | null;
  heightMapUrl: string | null;
  rebuildHeightMap: () => void;

  // 3D Model Settings (Jewelry Studio)
  modelSettings: Model3DSettings;
  updateModelSettings: (settings: Partial<Model3DSettings>) => void;
  updateColorGrading: (grading: Partial<ColorGradingSettings>) => void;
  applyMaterialPreset: (preset: MaterialPresetType) => void;
  resetModelSettings: () => void;

  // Anatomy & Organic Studio Settings
  anatomySettings: AnatomySettings;
  updateAnatomySettings: (settings: Partial<AnatomySettings>) => void;
  applySkinTonePreset: (preset: SkinTonePreset) => void;
  setAnatomyPart: (part: AnatomyPartType) => void;

  rotateImageAbsolute: (angle: number) => Promise<void>;

  activeTab: 'image' | 'cluster' | '3d';
  setActiveTab: (tab: 'image' | 'cluster' | '3d') => void;
}

const OVERLAY_PALETTE: Array<[number, number, number]> = [
  [239, 68, 68], [59, 130, 246], [16, 185, 129], [245, 158, 11],
  [168, 85, 247], [236, 72, 153], [6, 182, 212], [132, 204, 22],
  [249, 115, 22], [99, 102, 241], [20, 184, 166], [217, 70, 239],
  [161, 98, 7], [100, 116, 139], [190, 24, 93], [4, 120, 87],
];

const defaultColorGrading: ColorGradingSettings = {
  brightness: 0.0,
  contrast: 1.0,
  saturation: 1.05,
  hue: 0.0,
  sharpness: 0.5,
};

const defaultModelSettings: Model3DSettings = {
  scaleX: 1.0,
  scaleY: 1.0,
  scaleZ: 0.55,
  cutoff: 0.5,
  coverage: 0.95,
  segments: 192,
  rimMaterial: 'gold',
  customRimColor: '#d4af37',
  wireframe: false,
  autoRotate: false,
  lightIntensity: 1.2,
  displacementEnabled: true,
  displacementScale: 0.35,
  bevelSmoothness: 0.5,
  preset: 'gemstone',
  roughness: 0.12,
  metalness: 0.2,
  clearcoat: 0.85,
  colorGrading: defaultColorGrading,
};

const defaultAnatomySettings: AnatomySettings = {
  partType: 'nose',
  skinPreset: 'natural',
  skinColor: '#f2cdb3',
  subsurfaceScattering: 0.45,
  skinRoughness: 0.35,
  poreBumpIntensity: 0.3,
  bridgeHeight: 1.0,
  alaWidth: 1.0,
  symmetry: true,
  curvature: 1.0,
  segments: 192,
  displacementEnabled: true,
  displacementScale: 0.35,
  bevelSmoothness: 0.8,
  coverage: 1.0,
  wireframe: false,
  autoRotate: false,
};

const storeCreator: StateCreator<JewelryState> = (set, get) => ({
  studioMode: 'jewelry',
  setStudioMode: (studioMode: StudioMode) => set({ studioMode }),

  image: null,
  originalImage: null,
  originalAnchor: { u: 0.5, v: 0.5 },
  imageRotation: 0,
  setImage: (image: ImageInfo | null) => {
    set({
      image,
      originalImage: image,
      originalAnchor: { u: 0.5, v: 0.5 },
      imageRotation: 0,
      anchor: { u: 0.5, v: 0.5 },
      viewport2D: { zoom: 1, panX: 0, panY: 0 },
      clusters: [],
      clusterMap: null,
      clusterMapWidth: 0,
      clusterMapHeight: 0,
      clusterOverlayUrl: null,
      selectedClusterId: null,
      hoveredClusterId: null,
      heightMapTexture: null,
      heightMapUrl: null,
    });
    if (image) {
      setTimeout(() => get().runClustering(), 50);
    }
  },

  anchor: { u: 0.5, v: 0.5 },
  setAnchor: (anchor: AnchorPoint) => {
    const { imageRotation, originalImage, image } = get();
    const u = Math.max(0, Math.min(1, anchor.u));
    const v = Math.max(0, Math.min(1, anchor.v));
    
    let originalAnchor = { u, v };
    
    if (imageRotation !== 0 && originalImage && image) {
      const rad = -(imageRotation * Math.PI) / 180;
      const cos = Math.cos(rad);
      const sin = Math.sin(rad);

      const xRot = (u - 0.5) * image.width;
      const yRot = (v - 0.5) * image.height;

      const xOrig = xRot * cos - yRot * sin;
      const yOrig = xRot * sin + yRot * cos;

      originalAnchor = {
        u: Math.max(0, Math.min(1, 0.5 + xOrig / originalImage.width)),
        v: Math.max(0, Math.min(1, 0.5 + yOrig / originalImage.height)),
      };
    } else {
      originalAnchor = { u, v };
    }

    set({
      anchor: { u, v },
      originalAnchor,
    });
  },
  resetAnchor: () => set({ anchor: { u: 0.5, v: 0.5 } }),

  viewport2D: { zoom: 1, panX: 0, panY: 0 },
  setViewport2D: (partial: Partial<Viewport2D>) => set((state) => ({
    viewport2D: { ...state.viewport2D, ...partial }
  })),
  resetViewport2D: () => set({ viewport2D: { zoom: 1, panX: 0, panY: 0 } }),

  clusterCount: 6,
  setClusterCount: (clusterCount: number) => set({ clusterCount }),
  blurRadius: 1,
  setBlurRadius: (blurRadius: number) => set({ blurRadius }),
  isClustering: false,
  setIsClustering: (isClustering: boolean) => set({ isClustering }),
  clusters: [],
  setClusters: (clusters: ColorCluster[]) => set({ clusters }),
  updateCluster: (id: number, partial: Partial<ColorCluster>) => {
    set((state) => ({
      clusters: state.clusters.map((c) => (c.id === id ? { ...c, ...partial } : c))
    }));
    get().refreshOverlay();
    get().rebuildHeightMap();
  },
  clusterMap: null,
  clusterMapWidth: 0,
  clusterMapHeight: 0,
  setClusterMap: (clusterMap: Uint8Array | null, clusterMapWidth = 0, clusterMapHeight = 0) =>
    set({ clusterMap, clusterMapWidth, clusterMapHeight }),
  clusterOverlayUrl: null,
  setClusterOverlayUrl: (clusterOverlayUrl: string | null) => set({ clusterOverlayUrl }),
  showClusterOverlay: true,
  setShowClusterOverlay: (showClusterOverlay: boolean) => set({ showClusterOverlay }),
  overlayOpacity: 0.65,
  setOverlayOpacity: (overlayOpacity: number) => set({ overlayOpacity }),

  selectedClusterId: null,
  setSelectedClusterId: (selectedClusterId: number | null) => {
    set({ selectedClusterId });
    get().refreshOverlay();
  },
  hoveredClusterId: null,
  setHoveredClusterId: (hoveredClusterId: number | null) => {
    set({ hoveredClusterId });
    get().refreshOverlay();
  },

  selectClusterAtUv: (u: number, v: number) => {
    const { clusterMap, clusterMapWidth, clusterMapHeight } = get();
    if (!clusterMap || clusterMapWidth <= 0 || clusterMapHeight <= 0) return null;
    if (u < 0 || u > 1 || v < 0 || v > 1) return null;

    const x = Math.min(clusterMapWidth - 1, Math.max(0, Math.floor(u * clusterMapWidth)));
    const y = Math.min(clusterMapHeight - 1, Math.max(0, Math.floor(v * clusterMapHeight)));
    const idx = y * clusterMapWidth + x;
    const clusterId = clusterMap[idx];

    set({ selectedClusterId: clusterId });
    get().refreshOverlay();
    return clusterId;
  },

  heightMapTexture: null,
  heightMapUrl: null,
  rebuildHeightMap: () => {
    const { clusters, clusterMap, clusterMapWidth, clusterMapHeight, modelSettings, studioMode, anatomySettings } = get();
    if (!clusters || !clusterMap || clusterMapWidth <= 0 || clusterMapHeight <= 0 || clusters.length === 0) return;

    const smoothness = studioMode === 'anatomy' ? anatomySettings.bevelSmoothness : modelSettings.bevelSmoothness;
    const sharpness = studioMode === 'anatomy' ? 0.2 : modelSettings.colorGrading.sharpness;

    const { texture, dataUrl } = generateHeightMapData(
      clusters,
      clusterMap,
      clusterMapWidth,
      clusterMapHeight,
      smoothness,
      sharpness
    );
    set({
      heightMapTexture: texture,
      heightMapUrl: dataUrl,
    });
  },

  runClustering: async () => {
    const { image, clusterCount, blurRadius } = get();
    if (!image) return;

    set({ isClustering: true });

    try {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      await new Promise<void>((resolve, reject) => {
        img.onload = () => resolve();
        img.onerror = reject;
        img.src = image.url;
      });

      const maxDim = 1024;
      let w = img.naturalWidth;
      let h = img.naturalHeight;
      if (w > maxDim || h > maxDim) {
        const ratio = Math.min(maxDim / w, maxDim / h);
        w = Math.round(w * ratio);
        h = Math.round(h * ratio);
      }

      const canvas = document.createElement('canvas');
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      if (!ctx) throw new Error('Canvas 2D context creation failed');

      ctx.drawImage(img, 0, 0, w, h);
      const imageData = ctx.getImageData(0, 0, w, h);

      const worker = new Worker(new URL('../workers/clusterWorker.ts', import.meta.url), {
        type: 'module',
      });

      const workerPromise = new Promise<ClusterWorkerOutput>((resolve, reject) => {
        worker.onmessage = (e: MessageEvent<ClusterWorkerOutput>) => {
          resolve(e.data);
          worker.terminate();
        };
        worker.onerror = (err) => {
          reject(err);
          worker.terminate();
        };
      });

      const input: ClusterWorkerInput = {
        imageData,
        k: clusterCount,
        blurRadius,
      };
      worker.postMessage(input);

      const result = await workerPromise;
      const { clusters, clusterMap, width, height } = result;

      set({
        clusters,
        clusterMap,
        clusterMapWidth: width,
        clusterMapHeight: height,
        isClustering: false,
      });

      get().refreshOverlay();
      get().rebuildHeightMap();
    } catch (err) {
      console.error('Clustering error:', err);
      set({ isClustering: false });
    }
  },

  refreshOverlay: () => {
    const { clusters, clusterMap, clusterMapWidth, clusterMapHeight, selectedClusterId, hoveredClusterId } = get();
    if (!clusters || !clusterMap || clusterMapWidth <= 0 || clusterMapHeight <= 0) return;

    const activeFocusId = selectedClusterId ?? hoveredClusterId;
    renderOverlayImage(
      clusters,
      clusterMap,
      clusterMapWidth,
      clusterMapHeight,
      activeFocusId,
      (url) => {
        set({ clusterOverlayUrl: url });
      }
    );
  },

  modelSettings: defaultModelSettings,
  updateModelSettings: (settings: Partial<Model3DSettings>) => {
    set((state) => ({
      modelSettings: { ...state.modelSettings, ...settings }
    }));
    if (settings.bevelSmoothness !== undefined) {
      get().rebuildHeightMap();
    }
  },

  updateColorGrading: (grading: Partial<ColorGradingSettings>) => {
    set((state) => ({
      modelSettings: {
        ...state.modelSettings,
        colorGrading: { ...state.modelSettings.colorGrading, ...grading }
      }
    }));
    if (grading.sharpness !== undefined) {
      get().rebuildHeightMap();
    }
  },

  applyMaterialPreset: (preset: MaterialPresetType) => {
    const presets: Record<MaterialPresetType, Partial<Model3DSettings>> = {
      gemstone: { preset: 'gemstone', roughness: 0.1, metalness: 0.15, clearcoat: 0.9, rimMaterial: 'gold' },
      gold_polished: { preset: 'gold_polished', roughness: 0.12, metalness: 0.95, clearcoat: 0.6, rimMaterial: 'gold' },
      silver_chrome: { preset: 'silver_chrome', roughness: 0.08, metalness: 0.98, clearcoat: 0.7, rimMaterial: 'silver' },
      antique_cameo: { preset: 'antique_cameo', roughness: 0.45, metalness: 0.05, clearcoat: 0.2, rimMaterial: 'gold' },
      matte_resin: { preset: 'matte_resin', roughness: 0.85, metalness: 0.0, clearcoat: 0.0, rimMaterial: 'black' },
      custom: { preset: 'custom' },
    };
    const target = presets[preset];
    if (target) {
      get().updateModelSettings(target);
    }
  },

  resetModelSettings: () => set({ modelSettings: defaultModelSettings }),

  // Anatomy State Actions
  anatomySettings: defaultAnatomySettings,
  updateAnatomySettings: (settings: Partial<AnatomySettings>) => {
    set((state) => ({
      anatomySettings: { ...state.anatomySettings, ...settings }
    }));
    if (settings.bevelSmoothness !== undefined) {
      get().rebuildHeightMap();
    }
  },

  applySkinTonePreset: (preset: SkinTonePreset) => {
    const skinTones: Record<SkinTonePreset, { skinColor: string; sss: number; roughness: number } > = {
      fair: { skinColor: '#fae3d9', sss: 0.55, roughness: 0.32 },
      natural: { skinColor: '#f2cdb3', sss: 0.45, roughness: 0.38 },
      tan: { skinColor: '#d69e76', sss: 0.4, roughness: 0.4 },
      deep: { skinColor: '#8a5338', sss: 0.3, roughness: 0.42 },
      sculpt_clay: { skinColor: '#cfb9a5', sss: 0.1, roughness: 0.75 },
      custom: { skinColor: '#f2cdb3', sss: 0.45, roughness: 0.35 },
    };
    const tone = skinTones[preset];
    if (tone) {
      get().updateAnatomySettings({
        skinPreset: preset,
        skinColor: tone.skinColor,
        subsurfaceScattering: tone.sss,
        skinRoughness: tone.roughness,
      });
    }
  },

  setAnatomyPart: (partType: AnatomyPartType) => {
    get().updateAnatomySettings({ partType });
  },

  rotateImageAbsolute: async (angle: number) => {
    const { originalImage, originalAnchor } = get();
    if (!originalImage) return;

    const normalizedAngle = ((angle % 360) + 360) % 360;

    set({ isClustering: true, imageRotation: normalizedAngle });

    try {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      await new Promise<void>((resolve, reject) => {
        img.onload = () => resolve();
        img.onerror = reject;
        img.src = originalImage.url;
      });

      const rad = (normalizedAngle * Math.PI) / 180;
      const absSin = Math.abs(Math.sin(rad));
      const absCos = Math.abs(Math.cos(rad));
      const w = img.naturalWidth;
      const h = img.naturalHeight;
      const newW = w * absCos + h * absSin;
      const newH = w * absSin + h * absCos;

      const canvas = document.createElement('canvas');
      canvas.width = Math.round(newW);
      canvas.height = Math.round(newH);

      const ctx = canvas.getContext('2d');
      if (!ctx) throw new Error('Failed to get 2D context');

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      ctx.translate(canvas.width / 2, canvas.height / 2);
      ctx.rotate(rad);
      ctx.drawImage(img, -w / 2, -h / 2);

      const rotatedUrl = canvas.toDataURL();

      const xOrig = (originalAnchor.u - 0.5) * w;
      const yOrig = (originalAnchor.v - 0.5) * h;

      const xRot = xOrig * Math.cos(rad) - yOrig * Math.sin(rad);
      const yRot = xOrig * Math.sin(rad) + yOrig * Math.cos(rad);

      const newAnchor = {
        u: Math.max(0, Math.min(1, 0.5 + xRot / canvas.width)),
        v: Math.max(0, Math.min(1, 0.5 + yRot / canvas.height)),
      };

      set({
        image: {
          url: rotatedUrl,
          width: canvas.width,
          height: canvas.height,
          name: originalImage.name,
        },
        anchor: newAnchor,
        clusters: [],
        clusterMap: null,
        clusterMapWidth: 0,
        clusterMapHeight: 0,
        clusterOverlayUrl: null,
        selectedClusterId: null,
        hoveredClusterId: null,
        heightMapTexture: null,
        heightMapUrl: null,
      });

      await get().runClustering();
    } catch (err) {
      console.error('Failed to rotate image absolutely:', err);
      set({ isClustering: false });
    }
  },

  activeTab: '3d',
  setActiveTab: (activeTab: 'image' | 'cluster' | '3d') => set({ activeTab }),
});

export const useJewelryStore = create<JewelryState>(storeCreator);

function renderOverlayImage(
  clusters: ColorCluster[],
  clusterMap: Uint8Array,
  width: number,
  height: number,
  activeFocusId: number | null,
  callback: (url: string) => void
) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const imgData = ctx.createImageData(width, height);
  const data = imgData.data;
  const clusterVisibility = new Map<number, boolean>();
  const clusterColors = new Map<number, [number, number, number]>();

  clusters.forEach((c, idx) => {
    clusterVisibility.set(c.id, c.visible);
    const palColor = OVERLAY_PALETTE[idx % OVERLAY_PALETTE.length];
    clusterColors.set(c.id, palColor);
  });

  const len = clusterMap.length;
  const hasFocus = activeFocusId !== null;

  for (let i = 0; i < len; i++) {
    const clusterId = clusterMap[i];
    const isVisible = clusterVisibility.get(clusterId) ?? true;
    const outIdx = i * 4;

    if (!isVisible) {
      data[outIdx + 3] = 0;
      continue;
    }

    const rgb = clusterColors.get(clusterId) || [200, 200, 200];

    if (hasFocus) {
      if (clusterId === activeFocusId) {
        data[outIdx] = Math.min(255, rgb[0] + 40);
        data[outIdx + 1] = Math.min(255, rgb[1] + 40);
        data[outIdx + 2] = Math.min(255, rgb[2] + 40);
        data[outIdx + 3] = 255;
      } else {
        data[outIdx] = Math.round(rgb[0] * 0.25);
        data[outIdx + 1] = Math.round(rgb[1] * 0.25);
        data[outIdx + 2] = Math.round(rgb[2] * 0.25);
        data[outIdx + 3] = 50;
      }
    } else {
      data[outIdx] = rgb[0];
      data[outIdx + 1] = rgb[1];
      data[outIdx + 2] = rgb[2];
      data[outIdx + 3] = 255;
    }
  }

  ctx.putImageData(imgData, 0, 0);
  callback(canvas.toDataURL());
}