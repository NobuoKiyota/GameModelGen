import * as THREE from 'three';
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter.js';
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter.js';
import { buildEllipsoidGeometry } from './geometryBuilder';
import { generateLightmapUv2 } from './uvGenerator';
import { Model3DSettings, ColorCluster, AnchorPoint, ExportOptions } from '../types';

/**
 * Bakes vertex displacement into actual geometry coordinates for 3D export
 */
export function bakeDisplacedGeometry(
  modelSettings: Model3DSettings,
  anchor: AnchorPoint,
  clusters: ColorCluster[],
  clusterMap: Uint8Array | null,
  mapWidth: number,
  mapHeight: number,
  includeUV2: boolean = true
): THREE.BufferGeometry {
  const geom = buildEllipsoidGeometry(modelSettings);
  const posAttr = geom.attributes.position;
  const count = posAttr.count;

  if (modelSettings.displacementEnabled && clusters.length > 0 && clusterMap && mapWidth > 0 && mapHeight > 0) {
    const heightLookup = new Map<number, number>();
    const visLookup = new Map<number, boolean>();
    clusters.forEach((c) => {
      heightLookup.set(c.id, c.height);
      visLookup.set(c.id, c.visible);
    });

    const aspect = mapWidth / mapHeight;
    const scaleZ = Math.max(0.01, modelSettings.scaleZ);
    const scaleX = Math.max(0.01, modelSettings.scaleX);
    const scaleY = Math.max(0.01, modelSettings.scaleY);

    geom.computeVertexNormals();
    const normalAttr = geom.attributes.normal;

    for (let i = 0; i < count; i++) {
      const px = posAttr.getX(i);
      const py = posAttr.getY(i);
      const pz = posAttr.getZ(i);

      const uX = px / scaleX;
      const uY = py / scaleY;
      const uZ = pz / scaleZ;
      const len = Math.hypot(uX, uY, uZ);
      if (len < 0.001) continue;

      const normZ = Math.max(-1, Math.min(1, uZ / len));
      const theta = Math.acos(normZ);
      const phi = Math.atan2(uY, uX);

      const r = (theta / (Math.PI * 0.5)) * 0.5 / Math.max(0.01, modelSettings.coverage);
      let uOffset = r * Math.cos(phi);
      let vOffset = -r * Math.sin(phi);

      if (aspect > 1.0) vOffset *= aspect;
      else if (aspect < 1.0) uOffset /= aspect;

      const projU = anchor.u + uOffset;
      const projV = anchor.v + vOffset;

      if (projU >= 0 && projU <= 1 && projV >= 0 && projV <= 1) {
        const imgX = Math.min(mapWidth - 1, Math.max(0, Math.floor(projU * mapWidth)));
        const imgY = Math.min(mapHeight - 1, Math.max(0, Math.floor(projV * mapHeight)));
        const clusterId = clusterMap[imgY * mapWidth + imgX];

        const isVis = visLookup.get(clusterId) ?? true;
        if (isVis) {
          const hVal = heightLookup.get(clusterId) ?? 0;
          const maxTheta = (Math.PI * 0.5) * modelSettings.coverage;
          const mask = Math.max(0, Math.min(1, (maxTheta - theta) / (maxTheta * 0.15)));
          const totalH = hVal * modelSettings.displacementScale * mask;

          const nx = normalAttr.getX(i);
          const ny = normalAttr.getY(i);
          const nz = normalAttr.getZ(i);

          posAttr.setXYZ(i, px + nx * totalH, py + ny * totalH, pz + nz * totalH);
        }
      }
    }
    posAttr.needsUpdate = true;
    geom.computeVertexNormals();
  }

  if (includeUV2) {
    const uv2Attr = generateLightmapUv2(geom);
    geom.setAttribute('uv2', uv2Attr);
  }

  return geom;
}

/**
 * Builds an ASCII FBX file string with UV and UV2 Lightmap layers for inZOI / UE5 / Unity
 */
export function buildFbxString(mesh: THREE.Mesh, includeUV2: boolean = true): string {
  const geom = mesh.geometry as THREE.BufferGeometry;
  const posAttr = geom.attributes.position;
  const normalAttr = geom.attributes.normal;
  const uvAttr = geom.attributes.uv;
  const uv2Attr = geom.attributes.uv2;
  const indexAttr = geom.index;

  const count = posAttr.count;

  const verticesArr: string[] = [];
  for (let i = 0; i < count; i++) {
    verticesArr.push(
      `${(posAttr.getX(i) * 100).toFixed(4)},${(posAttr.getY(i) * 100).toFixed(4)},${(posAttr.getZ(i) * 100).toFixed(4)}`
    );
  }

  const indicesArr: number[] = [];
  if (indexAttr) {
    for (let i = 0; i < indexAttr.count; i += 3) {
      const a = indexAttr.getX(i);
      const b = indexAttr.getX(i + 1);
      const c = indexAttr.getX(i + 2);
      indicesArr.push(a, b, -(c + 1));
    }
  } else {
    for (let i = 0; i < count; i += 3) {
      indicesArr.push(i, i + 1, -(i + 2 + 1));
    }
  }

  const normalsArr: string[] = [];
  for (let i = 0; i < count; i++) {
    normalsArr.push(
      `${normalAttr.getX(i).toFixed(4)},${normalAttr.getY(i).toFixed(4)},${normalAttr.getZ(i).toFixed(4)}`
    );
  }

  const uvsArr: string[] = [];
  if (uvAttr) {
    for (let i = 0; i < uvAttr.count; i++) {
      uvsArr.push(`${uvAttr.getX(i).toFixed(4)},${uvAttr.getY(i).toFixed(4)}`);
    }
  }

  const uv2sArr: string[] = [];
  if (includeUV2 && uv2Attr) {
    for (let i = 0; i < uv2Attr.count; i++) {
      uv2sArr.push(`${uv2Attr.getX(i).toFixed(4)},${uv2Attr.getY(i).toFixed(4)}`);
    }
  }

  const fbxContent = `; FBX 7.4.0 project file generated by PhotoToJewelry3D
; inZOI / UE5 / Unity / Blender Compatible
; --------------------------------------------------
FBXHeaderExtension: {
	FBXHeaderVersion: 1003
	FBXVersion: 7400
}

Definitions: {
	Version: 100
	Count: 2
	ObjectType: "Model" {
		Count: 1
	}
	ObjectType: "Geometry" {
		Count: 1
	}
}

Objects: {
	Geometry: 1000, "Geometry::JewelryMesh", "Mesh" {
		Vertices: *${verticesArr.length * 3} {
			a: ${verticesArr.join(',')}
		}
		PolygonVertexIndex: *${indicesArr.length} {
			a: ${indicesArr.join(',')}
		}
		GeometryVersion: 124
		LayerElementNormal: 0 {
			Version: 101
			Name: ""
			MappingInformationType: "ByVertice"
			ReferenceInformationType: "Direct"
			Normals: *${normalsArr.length * 3} {
				a: ${normalsArr.join(',')}
			}
		}
		LayerElementUV: 0 {
			Version: 101
			Name: "UVMap"
			MappingInformationType: "ByVertice"
			ReferenceInformationType: "Direct"
			UV: *${uvsArr.length * 2} {
				a: ${uvsArr.join(',')}
			}
		}
${
  includeUV2 && uv2sArr.length > 0
    ? `		LayerElementUV: 1 {
			Version: 101
			Name: "LightmapUV2"
			MappingInformationType: "ByVertice"
			ReferenceInformationType: "Direct"
			UV: *${uv2sArr.length * 2} {
				a: ${uv2sArr.join(',')}
			}
		}`
    : ''
}
		Layer: 0 {
			Version: 100
			LayerElement: {
				Type: "LayerElementNormal"
				TypedIndex: 0
			}
			LayerElement: {
				Type: "LayerElementUV"
				TypedIndex: 0
			}
${
  includeUV2 && uv2sArr.length > 0
    ? `			LayerElement: {
				Type: "LayerElementUV"
				TypedIndex: 1
			}`
    : ''
}
		}
	}

	Model: 2000, "Model::${mesh.name || 'JewelryAsset'}", "Mesh" {
		Version: 232
		Properties70: {
			P: "InheritType", "enum", "", "",1
		}
	}
}

Connections: {
	; Model to Root
	C: "OO", 2000, 0
	; Geometry to Model
	C: "OO", 1000, 2000
}
`;

  return fbxContent;
}

/**
 * Exports baked 3D mesh and textures based on user options
 */
export async function export3DModel(
  options: ExportOptions,
  modelSettings: Model3DSettings,
  anchor: AnchorPoint,
  clusters: ColorCluster[],
  clusterMap: Uint8Array | null,
  mapWidth: number,
  mapHeight: number,
  imageDataUrl?: string | null,
  heightMapDataUrl?: string | null
): Promise<void> {
  const geom = bakeDisplacedGeometry(
    modelSettings,
    anchor,
    clusters,
    clusterMap,
    mapWidth,
    mapHeight,
    options.includeUV2
  );

  const material = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: modelSettings.roughness,
    metalness: modelSettings.metalness,
  });

  const mesh = new THREE.Mesh(geom, material);
  mesh.name = options.filename || 'JewelryModel';

  const baseName = options.filename.replace(/\.[^/.]+$/, '') || 'jewelry_model';

  if (options.format === 'fbx') {
    const fbxString = buildFbxString(mesh, options.includeUV2);
    downloadFile(fbxString, `${baseName}.fbx`, 'text/plain');
  } else if (options.format === 'glb') {
    const exporter = new GLTFExporter();
    exporter.parse(
      mesh,
      (gltf) => {
        downloadFile(gltf as ArrayBuffer, `${baseName}.glb`, 'model/gltf-binary');
      },
      (err) => console.error('GLTF Export Error:', err),
      { binary: true }
    );
  } else if (options.format === 'obj') {
    const exporter = new OBJExporter();
    const result = exporter.parse(mesh);
    downloadFile(result, `${baseName}.obj`, 'text/plain');
  }

  if (options.includeTexture && imageDataUrl) {
    downloadDataUrl(imageDataUrl, `${baseName}_diffuse.png`);
  }

  if (options.includeHeightMap && heightMapDataUrl) {
    downloadDataUrl(heightMapDataUrl, `${baseName}_heightmap.png`);
  }
}

function downloadFile(content: ArrayBuffer | string, filename: string, mimeType: string) {
  const blob = typeof content === 'string' ? new Blob([content], { type: mimeType }) : new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function downloadDataUrl(dataUrl: string, filename: string) {
  const a = document.createElement('a');
  a.href = dataUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
