export type StudioMode = 'jewelry' | 'anatomy';
export type AnatomyPartType = 'nose' | 'ear' | 'lips' | 'face_contour';
export type SkinTonePreset = 'fair' | 'natural' | 'tan' | 'deep' | 'sculpt_clay' | 'custom';

export interface ImageInfo {
  url: string;
  width: number;
  height: number;
  name: string;
}

export interface AnchorPoint {
  u: number;
  v: number;
}

export interface Viewport2D {
  zoom: number;
  panX: number;
  panY: number;
}

export interface ColorCluster {
  id: number;
  color: [number, number, number];
  hex: string;
  count: number;
  percentage: number;
  height: number;
  hardness: number;
  visible: boolean;
}

export type RimMaterialType = 'gold' | 'silver' | 'rosegold' | 'black' | 'custom';
export type MaterialPresetType = 'gemstone' | 'gold_polished' | 'silver_chrome' | 'antique_cameo' | 'matte_resin' | 'custom';

export interface ColorGradingSettings {
  brightness: number;
  contrast: number;
  saturation: number;
  hue: number;
  sharpness: number;
}

export interface Model3DSettings {
  scaleX: number;
  scaleY: number;
  scaleZ: number;
  cutoff: number;
  coverage: number;
  segments: number;
  rimMaterial: RimMaterialType;
  customRimColor: string;
  wireframe: boolean;
  autoRotate: boolean;
  lightIntensity: number;
  displacementEnabled: boolean;
  displacementScale: number;
  bevelSmoothness: number;
  preset: MaterialPresetType;
  roughness: number;
  metalness: number;
  clearcoat: number;
  colorGrading: ColorGradingSettings;
}

export interface AnatomySettings {
  partType: AnatomyPartType;
  skinPreset: SkinTonePreset;
  skinColor: string; // Base tone hex
  subsurfaceScattering: number; // SSS redness intensity (0.0 to 1.0)
  skinRoughness: number; // 0.0 to 1.0 (oil / sheen)
  poreBumpIntensity: number; // Micro skin texture
  bridgeHeight: number; // Nose bridge or ear rim prominence (0.2 to 2.0)
  alaWidth: number; // Nostril flare or ear lobe width (0.5 to 2.0)
  symmetry: boolean; // Mirror X displacement
  curvature: number; // Overall organic curvature
  segments: number;
  displacementEnabled: boolean;
  displacementScale: number;
  bevelSmoothness: number;
  coverage: number;
  wireframe: boolean;
  autoRotate: boolean;
}

export interface ProjectSaveData {
  version: string;
  timestamp: string;
  studioMode: StudioMode;
  image: {
    name: string;
    width: number;
    height: number;
    dataUrl: string;
  } | null;
  anchor: AnchorPoint;
  clusters: ColorCluster[];
  clusterCount: number;
  blurRadius: number;
  modelSettings: Model3DSettings;
  anatomySettings: AnatomySettings;
}

export type ExportFormat = 'fbx' | 'glb' | 'obj';

export interface ExportOptions {
  format: ExportFormat;
  includeUV2: boolean;
  includeTexture: boolean;
  includeHeightMap: boolean;
  bakeDisplacement: boolean;
  filename: string;
}