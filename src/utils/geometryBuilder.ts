import * as THREE from 'three';
import { Model3DSettings } from '../types';

/**
 * Builds an ellipsoid geometry with flattening bottom cutoff and clean undeformed unit coordinates
 */
export function buildEllipsoidGeometry(settings: Model3DSettings): THREE.BufferGeometry {
  const { scaleX, scaleY, scaleZ, cutoff, segments = 192 } = settings;
  const radius = 1.0;

  // Base Sphere
  const geom = new THREE.SphereGeometry(radius, segments, segments);
  geom.rotateX(Math.PI / 2); // Polar apex at Z+

  const posAttr = geom.attributes.position;
  const count = posAttr.count;

  // Store original unscaled unit positions for distortion-free shader texture projection
  const unitPosArray = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    unitPosArray[i * 3] = posAttr.getX(i);
    unitPosArray[i * 3 + 1] = posAttr.getY(i);
    unitPosArray[i * 3 + 2] = posAttr.getZ(i);
  }
  geom.setAttribute('aUnitPos', new THREE.BufferAttribute(unitPosArray, 3));

  // Cutoff range: cutoff=0.0 -> zMin = -1.0, cutoff=1.0 -> zMin = 0.8
  const zCutoffThreshold = -1.0 + cutoff * 1.8;

  for (let i = 0; i < count; i++) {
    let x = posAttr.getX(i);
    let y = posAttr.getY(i);
    let z = posAttr.getZ(i);

    if (z < zCutoffThreshold) {
      z = zCutoffThreshold;
    }

    posAttr.setXYZ(i, x * scaleX, y * scaleY, z * scaleZ);
  }

  posAttr.needsUpdate = true;
  geom.computeVertexNormals();

  return geom;
}