import { rgbToLab, labDistance, rgbToHex } from '../utils/colorUtils';

export interface ClusterWorkerInput {
  imageData: ImageData;
  k: number;
  blurRadius: number;
  maxIterations?: number;
}

export interface ClusterWorkerOutput {
  clusters: Array<{
    id: number;
    color: [number, number, number];
    hex: string;
    count: number;
    percentage: number;
    height: number;
    hardness: number;
    visible: boolean;
  }>;
  clusterMap: Uint8Array;
  width: number;
  height: number;
}

function applyBlur(src: Uint8ClampedArray, width: number, height: number, radius: number): Uint8ClampedArray {
  if (radius <= 0) return new Uint8ClampedArray(src);
  const r = Math.round(radius);
  const dst = new Uint8ClampedArray(src.length);

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      let rSum = 0, gSum = 0, bSum = 0, aSum = 0, count = 0;
      for (let dy = -r; dy <= r; dy++) {
        const py = Math.min(height - 1, Math.max(0, y + dy));
        for (let dx = -r; dx <= r; dx++) {
          const px = Math.min(width - 1, Math.max(0, x + dx));
          const idx = (py * width + px) * 4;
          rSum += src[idx];
          gSum += src[idx + 1];
          bSum += src[idx + 2];
          aSum += src[idx + 3];
          count++;
        }
      }
      const outIdx = (y * width + x) * 4;
      dst[outIdx] = rSum / count;
      dst[outIdx + 1] = gSum / count;
      dst[outIdx + 2] = bSum / count;
      dst[outIdx + 3] = aSum / count;
    }
  }
  return dst;
}

self.onmessage = (e: MessageEvent<ClusterWorkerInput>) => {
  const { imageData, k, blurRadius, maxIterations = 15 } = e.data;
  const { width, height, data } = imageData;
  const pixelCount = width * height;

  const smoothed = blurRadius > 0 ? applyBlur(data, width, height, blurRadius) : data;

  const step = Math.max(1, Math.floor(Math.sqrt(pixelCount / 30000)));
  const samplesLab: Array<[number, number, number]> = [];
  const samplesRgb: Array<[number, number, number]> = [];

  for (let y = 0; y < height; y += step) {
    for (let x = 0; x < width; x += step) {
      const idx = (y * width + x) * 4;
      if (smoothed[idx + 3] < 30) continue;
      const r = smoothed[idx];
      const g = smoothed[idx + 1];
      const b = smoothed[idx + 2];
      samplesRgb.push([r, g, b]);
      samplesLab.push(rgbToLab(r, g, b));
    }
  }

  if (samplesLab.length === 0) {
    self.postMessage({ clusters: [], clusterMap: new Uint8Array(pixelCount), width, height });
    return;
  }

  const actualK = Math.min(k, samplesLab.length);

  const centersLab: Array<[number, number, number]> = [];
  const centersRgb: Array<[number, number, number]> = [];

  const firstIdx = Math.floor(Math.random() * samplesLab.length);
  centersLab.push([...samplesLab[firstIdx]]);
  centersRgb.push([...samplesRgb[firstIdx]]);

  while (centersLab.length < actualK) {
    const distances: number[] = [];
    let totalDistSq = 0;
    for (let i = 0; i < samplesLab.length; i++) {
      let minDist = Infinity;
      for (const c of centersLab) {
        const d = labDistance(samplesLab[i], c);
        if (d < minDist) minDist = d;
      }
      const dSq = minDist * minDist;
      distances.push(dSq);
      totalDistSq += dSq;
    }

    let target = Math.random() * totalDistSq;
    let chosen = 0;
    for (let i = 0; i < distances.length; i++) {
      target -= distances[i];
      if (target <= 0) {
        chosen = i;
        break;
      }
    }
    centersLab.push([...samplesLab[chosen]]);
    centersRgb.push([...samplesRgb[chosen]]);
  }

  for (let iter = 0; iter < maxIterations; iter++) {
    const clusterCounts = new Array(actualK).fill(0);
    const sumL = new Array(actualK).fill(0);
    const sumA = new Array(actualK).fill(0);
    const sumB = new Array(actualK).fill(0);
    const sumR = new Array(actualK).fill(0);
    const sumG = new Array(actualK).fill(0);
    const sumBlue = new Array(actualK).fill(0);

    for (let i = 0; i < samplesLab.length; i++) {
      const lab = samplesLab[i];
      let bestCluster = 0;
      let bestDist = Infinity;
      for (let c = 0; c < actualK; c++) {
        const dist = labDistance(lab, centersLab[c]);
        if (dist < bestDist) {
          bestDist = dist;
          bestCluster = c;
        }
      }

      clusterCounts[bestCluster]++;
      sumL[bestCluster] += lab[0];
      sumA[bestCluster] += lab[1];
      sumB[bestCluster] += lab[2];
      sumR[bestCluster] += samplesRgb[i][0];
      sumG[bestCluster] += samplesRgb[i][1];
      sumBlue[bestCluster] += samplesRgb[i][2];
    }

    let maxShift = 0;
    for (let c = 0; c < actualK; c++) {
      if (clusterCounts[c] > 0) {
        const newLab: [number, number, number] = [
          sumL[c] / clusterCounts[c],
          sumA[c] / clusterCounts[c],
          sumB[c] / clusterCounts[c],
        ];
        const shift = labDistance(centersLab[c], newLab);
        if (shift > maxShift) maxShift = shift;
        centersLab[c] = newLab;
        centersRgb[c] = [
          Math.round(sumR[c] / clusterCounts[c]),
          Math.round(sumG[c] / clusterCounts[c]),
          Math.round(sumBlue[c] / clusterCounts[c]),
        ];
      }
    }

    if (maxShift < 0.5) break;
  }

  const clusterMap = new Uint8Array(pixelCount);
  const fullCounts = new Array(actualK).fill(0);

  for (let i = 0; i < pixelCount; i++) {
    const idx = i * 4;
    const r = smoothed[idx];
    const g = smoothed[idx + 1];
    const b = smoothed[idx + 2];
    const lab = rgbToLab(r, g, b);

    let bestCluster = 0;
    let bestDist = Infinity;
    for (let c = 0; c < actualK; c++) {
      const dist = labDistance(lab, centersLab[c]);
      if (dist < bestDist) {
        bestDist = dist;
        bestCluster = c;
      }
    }

    clusterMap[i] = bestCluster;
    fullCounts[bestCluster]++;
  }

  const clusterResult = centersRgb.map((rgb, id) => {
    const lab = centersLab[id];
    const count = fullCounts[id] || 0;
    const percentage = (count / pixelCount) * 100;
    return {
      id,
      color: rgb,
      hex: rgbToHex(rgb[0], rgb[1], rgb[2]),
      count,
      percentage,
      luminance: lab[0],
      height: parseFloat(((lab[0] / 100) * 0.6 - 0.1).toFixed(2)),
      hardness: 0.8,
      visible: true,
    };
  });

  const output: ClusterWorkerOutput = {
    clusters: clusterResult,
    clusterMap,
    width,
    height,
  };

  // Send response back to main thread
  (self as unknown as Worker).postMessage(output);
};