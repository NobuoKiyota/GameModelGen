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