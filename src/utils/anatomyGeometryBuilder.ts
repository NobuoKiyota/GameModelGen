import * as THREE from 'three';
import { AnatomySettings } from '../types';

/**
 * Builds specialized anatomical base meshes for nose, ear, lips, and facial contours
 */
export function buildAnatomyGeometry(settings: AnatomySettings): THREE.BufferGeometry {
  const { partType, bridgeHeight, alaWidth, curvature, segments = 192 } = settings;

  // Base grid mesh on XY plane spanning [-1, 1]
  const geom = new THREE.PlaneGeometry(2.0, 2.0, segments, segments);
  const posAttr = geom.attributes.position;
  const count = posAttr.count;

  const unitPosArray = new Float32Array(count * 3);

  for (let i = 0; i < count; i++) {
    let x = posAttr.getX(i);
    let y = posAttr.getY(i);
    let z = 0.0;

    if (partType === 'nose') {
      // Nose bridge and tip: Narrow top bridge, wide lower nostrils (Ala)
      const t = (y + 1.0) * 0.5; // 0 (bottom nostrils) to 1 (top glabella)
      const bridgeWidth = 0.15 + (1.0 - t) * (0.35 * alaWidth);
      const xDist = Math.abs(x) / Math.max(0.01, bridgeWidth);

      // Pyramidal ridge with rounded bridge crest
      const ridge = Math.max(0, 1.0 - Math.pow(xDist, 1.6));
      // Tip bulbous bump near y = -0.3
      const tipDist = Math.hypot(x * 1.5, (y + 0.3) * 1.8);
      const tipBulb = Math.max(0, 1.0 - tipDist * 1.5) * 0.4;

      z = (ridge * (0.6 + t * 0.2) + tipBulb) * bridgeHeight * curvature;

      // Soft perimeter falloff
      const edgeDist = Math.hypot(x, y);
      const falloff = Math.max(0, 1.0 - Math.pow(edgeDist * 0.9, 2.0));
      z *= falloff;
    } else if (partType === 'ear') {
      // Ear C-shaped outer helix and inner concha hollow
      const earRadius = 0.75 * alaWidth;
      const r = Math.hypot(x * 1.2, y);
      const helixRing = Math.exp(-Math.pow(r - earRadius, 2.0) * 18.0) * 0.6;
      const conchaHollow = -Math.exp(-Math.pow(Math.hypot(x + 0.1, y), 2.0) * 10.0) * 0.4;
      const lobe = Math.exp(-Math.pow(Math.hypot(x, y + 0.7), 2.0) * 12.0) * 0.35;

      z = (helixRing + conchaHollow + lobe) * bridgeHeight * curvature;
    } else if (partType === 'lips') {
      // Lips cupid's bow and lower lip fullness
      const lipWidth = 0.8 * alaWidth;
      const uLip = Math.exp(-Math.pow(Math.hypot(x / lipWidth, (y - 0.15) * 3.0), 2.0) * 4.0) * 0.35;
      const lLip = Math.exp(-Math.pow(Math.hypot(x / lipWidth, (y + 0.25) * 2.5), 2.0) * 4.0) * 0.45;
      const philtrum = (1.0 - Math.abs(x) * 4.0) * Math.max(0, y) * 0.15;

      z = (uLip + lLip + philtrum) * bridgeHeight * curvature;
    } else if (partType === 'eye') {
      // Eye: eyeball dome, eyelid folds
      const eyeR = Math.hypot(x / (0.6 * alaWidth), y * 1.5);
      const eyeDome = Math.max(0, 1.0 - Math.pow(eyeR, 2.0)) * 0.25;

      // Eyelid creases (upper and lower folds)
      const xFactor = Math.max(0, 1.0 - Math.pow(x / (0.7 * alaWidth), 2.0));
      const upperLid = Math.exp(-Math.pow(y - 0.15, 2.0) * 35.0) * xFactor * 0.12;
      const lowerLid = Math.exp(-Math.pow(y + 0.15, 2.0) * 35.0) * xFactor * 0.08;

      z = (eyeDome + upperLid + lowerLid) * bridgeHeight * curvature;
    } else if (partType === 'breast') {
      // Breast: smooth dome and local nipple peak
      const breastR = Math.hypot(x, y);
      const breastBase = Math.max(0, 1.0 - Math.pow(breastR / (0.85 * alaWidth), 2.0));
      const breastDome = Math.pow(breastBase, 1.8) * 0.55;
      
      const nipple = Math.exp(-Math.pow(breastR, 2.0) * 55.0) * 0.12;

      z = (breastDome + nipple) * bridgeHeight * curvature;
    } else if (partType === 'penis') {
      // Penis: cylindrical shaft and glans dome
      const shaftWidth = 0.22 * alaWidth;
      const shaftRidge = Math.max(0, 1.0 - Math.pow(x / shaftWidth, 2.0));
      const shaftLength = Math.max(0, 1.0 - Math.pow((y + 0.25) / 0.65, 6.0));
      const shaft = shaftRidge * shaftLength * 0.32;

      const glansY = 0.45;
      const glansDist = Math.hypot(x, y - glansY);
      const glans = Math.max(0, 1.0 - Math.pow(glansDist / (0.32 * alaWidth), 2.0)) * 0.42;

      // Corona groove (indentation between glans and shaft)
      const coronaGroove = -Math.exp(-Math.pow(y - 0.28, 2.0) * 65.0) * Math.max(0, 1.0 - Math.pow(x / 0.3, 2.0)) * 0.06;

      z = Math.max(0, shaft + glans + coronaGroove) * bridgeHeight * curvature;

      // Soft perimeter falloff
      const edgeDist = Math.hypot(x, y);
      const falloff = Math.max(0, 1.0 - Math.pow(edgeDist * 0.9, 2.0));
      z *= falloff;
    } else if (partType === 'vulva') {
      // Vulva: mons pubis, labia majora hills, central cleft
      const vulvaBase = Math.max(0, 1.0 - Math.pow(Math.hypot(x / (0.75 * alaWidth), y), 2.0)) * 0.12;

      const labiaX = 0.14 * alaWidth;
      const labiaYScale = 2.0;
      const labiaLeft = Math.exp(-Math.pow(x + labiaX, 2.0) * 32.0 - Math.pow(y * labiaYScale, 2.0) * 1.5);
      const labiaRight = Math.exp(-Math.pow(x - labiaX, 2.0) * 32.0 - Math.pow(y * labiaYScale, 2.0) * 1.5);
      const labia = (labiaLeft + labiaRight) * 0.28;

      const cleft = -Math.exp(-Math.pow(x, 2.0) * 120.0 - Math.pow(y * 1.4, 2.0) * 2.0) * 0.12;

      const mons = Math.exp(-Math.pow(x, 2.0) * 4.0 - Math.pow(y - 0.6, 2.0) * 3.0) * 0.32;

      z = (vulvaBase + labia + cleft + mons) * bridgeHeight * curvature;

      // Soft perimeter falloff
      const edgeDist = Math.hypot(x, y);
      const falloff = Math.max(0, 1.0 - Math.pow(edgeDist * 0.95, 2.0));
      z *= falloff;
    } else if (partType === 'rock') {
      // Rock: bumpy dome with combined sine-wave noise
      const rockR = Math.hypot(x / (0.8 * alaWidth), y * 1.1);
      const baseDome = Math.max(0, 1.0 - Math.pow(rockR, 2.0)) * 0.42;
      const noise = (Math.sin(x * 12.0) * Math.cos(y * 12.0) * 0.05) + 
                    (Math.sin(x * 24.0 + y * 12.0) * 0.02) + 
                    (Math.cos(y * 36.0 - x * 10.0) * 0.01);
      z = (baseDome + noise * Math.max(0, 1.0 - rockR)) * bridgeHeight * curvature;

      const edgeDist = Math.hypot(x, y);
      const falloff = Math.max(0, 1.0 - Math.pow(edgeDist * 0.95, 2.0));
      z *= falloff;
    } else if (partType === 'wall') {
      // Wall: brick/tile pattern grid
      const brickW = 0.5 * alaWidth;
      const brickH = 0.35;
      const brickX = Math.abs(Math.sin((x / brickW) * Math.PI));
      const brickY = Math.abs(Math.sin((y / brickH) * Math.PI));
      const border = Math.pow(brickX * brickY, 0.15);
      z = (0.15 + border * 0.18) * bridgeHeight * curvature;

      const edgeDist = Math.hypot(x, y);
      const falloff = Math.max(0, 1.0 - Math.pow(edgeDist * 0.95, 2.0));
      z *= falloff;
    } else if (partType === 'grass') {
      // Grass: fine spike-like protrusions
      const freq = 22.0 * (1.0 / alaWidth);
      const blade = Math.max(0, Math.sin(x * freq) * Math.sin(y * freq)) * 0.15;
      z = (0.05 + blade) * bridgeHeight * curvature;

      const edgeDist = Math.hypot(x, y);
      const falloff = Math.max(0, 1.0 - Math.pow(edgeDist * 0.95, 2.0));
      z *= falloff;
    } else if (partType === 'tree') {
      // Tree: vertical bark ridges
      const barkPattern = Math.sin(x * 16.0 + Math.sin(y * 6.0) * 1.5) * 0.14;
      z = (0.22 + barkPattern) * bridgeHeight * curvature;

      const edgeDist = Math.hypot(x, y);
      const falloff = Math.max(0, 1.0 - Math.pow(edgeDist * 0.95, 2.0));
      z *= falloff;
    } else if (partType === 'terrain') {
      // Terrain: gentle rolling hills/dunes
      const wave1 = Math.sin(x * 2.5 * (1.0 / alaWidth) + y * 1.5) * 0.18;
      const wave2 = Math.cos(x * 5.0 * (1.0 / alaWidth) - y * 3.5) * 0.08;
      z = (0.2 + wave1 + wave2) * bridgeHeight * curvature;

      const edgeDist = Math.hypot(x, y);
      const falloff = Math.max(0, 1.0 - Math.pow(edgeDist * 0.95, 2.0));
      z *= falloff;
    } else if (partType === 'puddle') {
      // Puddle: negative flat-ish bowl with small rim
      const distP = Math.hypot(x / alaWidth, y);
      const outerRim = Math.max(0, 1.0 - Math.pow(distP * 1.05, 2.0)) * 0.22;
      const innerHollow = Math.max(0, 1.0 - Math.pow(distP * 1.55, 2.0)) * 0.28;
      z = (outerRim - innerHollow) * bridgeHeight * curvature;

      const edgeDist = Math.hypot(x, y);
      const falloff = Math.max(0, 1.0 - Math.pow(edgeDist * 0.98, 2.0));
      z *= falloff;
    } else {
      // Facial Contour: Smooth organic dome
      const dist = Math.hypot(x * (1.0 / alaWidth), y);
      z = Math.max(0, 1.0 - Math.pow(dist * 0.85, 2.0)) * 0.5 * bridgeHeight * curvature;
    }

    posAttr.setXYZ(i, x, y, z);

    // Store normalized unit coordinate for shader projection
    unitPosArray[i * 3] = x;
    unitPosArray[i * 3 + 1] = y;
    unitPosArray[i * 3 + 2] = z;
  }

  geom.setAttribute('aUnitPos', new THREE.BufferAttribute(unitPosArray, 3));
  posAttr.needsUpdate = true;
  geom.computeVertexNormals();

  return geom;
}