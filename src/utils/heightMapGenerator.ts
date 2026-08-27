import * as THREE from 'three';
import { ColorCluster } from '../types';

/**
 * Generates a high-fidelity grayscale heightmap with advanced multi-pass smoothing and sharpening
 */
export function generateHeightMapData(
  clusters: ColorCluster[],
  clusterMap: Uint8Array,
  width: number,
  height: number,
  bevelSmoothness: number = 0.5,
  sharpness: number = 0.5
): { texture: THREE.DataTexture; dataUrl: string } {
  const pixelCount = width * height;
  const heightLookup = new Map<number, number>();
  const visibilityLookup = new Map<number, boolean>();
  const hardnessLookup = new Map<number, number>();

  clusters.forEach((c) => {
    heightLookup.set(c.id, c.height);
    visibilityLookup.set(c.id, c.visible);
    hardnessLookup.set(c.id, c.hardness);
  });

  // 1. Initial raw float map [-1.0, 1.0] -> [0.0, 1.0]
  const raw = new Float32Array(pixelCount);
  for (let i = 0; i < pixelCount; i++) {
    const clusterId = clusterMap[i];
    const isVisible = visibilityLookup.get(clusterId) ?? true;
    if (!isVisible) {
      raw[i] = 0.5;
    } else {
      const h = heightLookup.get(clusterId) ?? 0;
      raw[i] = Math.max(0, Math.min(1, (h + 1.0) * 0.5));
    }
  }

  // 2. Multi-pass separable Gaussian/Box smoothing
  let current = new Float32Array(raw);
  const passes = Math.max(0, Math.round(bevelSmoothness * 3));
  const temp = new Float32Array(pixelCount);

  for (let p = 0; p < passes; p++) {
    const r = Math.max(1, p + 1);
    // Horizontal pass
    for (let y = 0; y < height; y++) {
      const rowOffset = y * width;
      for (let x = 0; x < width; x++) {
        let sum = 0;
        let count = 0;
        for (let dx = -r; dx <= r; dx++) {
          const px = Math.min(width - 1, Math.max(0, x + dx));
          sum += current[rowOffset + px];
          count++;
        }
        temp[rowOffset + x] = sum / count;
      }
    }
    // Vertical pass
    for (let x = 0; x < width; x++) {
      for (let y = 0; y < height; y++) {
        let sum = 0;
        let count = 0;
        for (let dy = -r; dy <= r; dy++) {
          const py = Math.min(height - 1, Math.max(0, y + dy));
          sum += temp[py * width + x];
          count++;
        }
        current[y * width + x] = sum / count;
      }
    }
  }

  // 3. Optional unsharp masking / edge sharpening
  const finalHeights = new Float32Array(pixelCount);
  if (sharpness > 0) {
    const sharpAmount = sharpness * 0.8;
    for (let i = 0; i < pixelCount; i++) {
      const diff = raw[i] - current[i];
      finalHeights[i] = Math.max(0, Math.min(1, current[i] + diff * sharpAmount));
    }
  } else {
    finalHeights.set(current);
  }

  // 4. Pack into RGBA byte buffer
  const byteData = new Uint8Array(pixelCount * 4);
  for (let i = 0; i < pixelCount; i++) {
    const val = Math.round(finalHeights[i] * 255);
    const outIdx = i * 4;
    byteData[outIdx] = val;     // R
    byteData[outIdx + 1] = val; // G
    byteData[outIdx + 2] = val; // B
    byteData[outIdx + 3] = 255; // A
  }

  const texture = new THREE.DataTexture(
    byteData,
    width,
    height,
    THREE.RGBAFormat,
    THREE.UnsignedByteType
  );
  texture.wrapS = THREE.ClampToEdgeWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;
  texture.minFilter = THREE.LinearFilter;
  texture.magFilter = THREE.LinearFilter;
  texture.needsUpdate = true;

  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  let dataUrl = '';
  if (ctx) {
    const imgData = ctx.createImageData(width, height);
    imgData.data.set(byteData);
    ctx.putImageData(imgData, 0, 0);
    dataUrl = canvas.toDataURL();
  }

  return { texture, dataUrl };
}