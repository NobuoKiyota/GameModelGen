import * as THREE from 'three';

/**
 * Generates non-overlapping UV2 (Lightmap UVs) compliant with inZOI / UE5
 * Unfolds the upper dome in the top half [0, 0.5] and bottom flat section in bottom half [0.5, 1.0]
 */
export function generateLightmapUv2(geometry: THREE.BufferGeometry): THREE.BufferAttribute {
  const posAttr = geometry.attributes.position;
  const count = posAttr.count;
  const uv2Array = new Float32Array(count * 2);

  // Determine bounding box for normalization
  geometry.computeBoundingBox();
  const box = geometry.boundingBox || new THREE.Box3(
    new THREE.Vector3(-1, -1, -1),
    new THREE.Vector3(1, 1, 1)
  );
  const sizeX = Math.max(0.001, box.max.x - box.min.x);
  const sizeY = Math.max(0.001, box.max.y - box.min.y);

  for (let i = 0; i < count; i++) {
    const x = posAttr.getX(i);
    const y = posAttr.getY(i);
    const z = posAttr.getZ(i);

    // Normalized XY in [0, 1]
    const nx = (x - box.min.x) / sizeX;
    const ny = (y - box.min.y) / sizeY;

    if (z >= 0) {
      // Top dome: placed in [0..1, 0..0.5] with small margin
      const u2 = nx * 0.96 + 0.02;
      const v2 = (ny * 0.46 + 0.02);
      uv2Array[i * 2] = u2;
      uv2Array[i * 2 + 1] = v2;
    } else {
      // Bottom flat/back area: placed in [0..1, 0.5..1.0] with small margin
      const u2 = nx * 0.96 + 0.02;
      const v2 = (ny * 0.46 + 0.52);
      uv2Array[i * 2] = u2;
      uv2Array[i * 2 + 1] = v2;
    }
  }

  return new THREE.BufferAttribute(uv2Array, 2);
}