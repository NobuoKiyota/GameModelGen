// =============================================================
// Exporter Module (OBJ, MTL, Unity Package ZIP, C# Script, Cocos TS)
// =============================================================
window.MeshExporter = {
  getCleanAssetName: function() {
    const raw = document.getElementById('asset-name').value.trim();
    const shapeSelect = document.getElementById('shape-type');
    const name = raw || shapeSelect.value;
    return name.replace(/[^a-zA-Z0-9_-]/g, '_');
  },

  getMaterialAndTextureNames: function(assetName) {
    const isShared = document.getElementById('mat-mode').value === 'shared';
    const pat = document.getElementById('tex-pattern').value;
    if (isShared) {
      return {
        mtlFileName: `Shared_${pat}_Mat.mtl`,
        mtlName: `Shared_${pat}_Mat`,
        texFileName: `Shared_${pat}_Albedo.png`
      };
    } else {
      return {
        mtlFileName: `${assetName}.mtl`,
        mtlName: `${assetName}_Mat`,
        texFileName: `${assetName}_Albedo.png`
      };
    }
  },

  generateObjContent: function(assetName, geometryData) {
    const { positions, normals, uvs, indices } = geometryData;
    const { mtlFileName, mtlName } = this.getMaterialAndTextureNames(assetName);

    let obj = `# 3D Procedural Mesh with Computed Normals & Atlas UVs\n`;
    obj += `mtllib ${mtlFileName}\n`;
    obj += `o ${assetName}\n`;
    obj += `g ${assetName}_Geometry\n`;
    obj += `usemtl ${mtlName}\n\n`;

    for (let i = 0; i < positions.length; i += 3) {
      obj += `v ${positions[i].toFixed(6)} ${positions[i+1].toFixed(6)} ${positions[i+2].toFixed(6)}\n`;
    }
    for (let i = 0; i < uvs.length; i += 2) {
      obj += `vt ${uvs[i].toFixed(6)} ${uvs[i+1].toFixed(6)}\n`;
    }
    for (let i = 0; i < normals.length; i += 3) {
      obj += `vn ${normals[i].toFixed(6)} ${normals[i+1].toFixed(6)} ${normals[i+2].toFixed(6)}\n`;
    }
    obj += `s 1\n`;
    for (let i = 0; i < indices.length; i += 3) {
      const a = indices[i] + 1, b = indices[i+1] + 1, c = indices[i+2] + 1;
      obj += `f ${a}/${a}/${a} ${b}/${b}/${b} ${c}/${c}/${c}\n`;
    }
    return obj;
  },

  generateMtlContent: function(assetName) {
    const { mtlName, texFileName } = this.getMaterialAndTextureNames(assetName);
    const roughVal = parseFloat(document.getElementById('pbr-roughness').value) || 0.6;
    const metalVal = parseFloat(document.getElementById('pbr-metalness').value) || 0.05;

    let mtl = `# Material Definition for Unity Standard / URP Lit Shader\n`;
    mtl += `newmtl ${mtlName}\n`;
    mtl += `Ka 1.000 1.000 1.000\n`;
    mtl += `Kd 1.000 1.000 1.000\n`;
    mtl += `Ks ${metalVal.toFixed(3)} ${metalVal.toFixed(3)} ${metalVal.toFixed(3)}\n`;
    mtl += `Ns ${((1.0 - roughVal) * 100).toFixed(1)}\n`;
    mtl += `d 1.0\n`;
    mtl += `illum 2\n`;
    mtl += `map_Kd ${texFileName}\n`;
    return mtl;
  },

  exportObjOnly: function(geometryData) {
    if (!geometryData) return;
    const assetName = this.getCleanAssetName();
    const objContent = this.generateObjContent(assetName, geometryData);
    const blob = new Blob([objContent], { type: 'text/plain' });
    saveAs(blob, `${assetName}.obj`);
  },

  exportUnityZip: function(geometryData) {
    if (!geometryData) return;
    const assetName = this.getCleanAssetName();
    const { mtlFileName, texFileName } = this.getMaterialAndTextureNames(assetName);
    const zip = new JSZip();

    zip.file(`${assetName}.obj`, this.generateObjContent(assetName, geometryData));
    zip.file(mtlFileName, this.generateMtlContent(assetName));

    const canvasElem = TextureStudio.bakeAtlas();
    canvasElem.toBlob((blob) => {
      zip.file(texFileName, blob);
      zip.generateAsync({ type: "blob" }).then((zipBlob) => {
        saveAs(zipBlob, `${assetName}_UnityPackage.zip`);
      });
    });
  },

  generateUnityCode: function(geometryData) {
    if (!geometryData) return '';
    const assetName = this.getCleanAssetName();
    const { positions, normals, uvs, indices } = geometryData;

    let vStr = "", nStr = "", uvStr = "", triStr = "        ";
    for (let i = 0; i < positions.length; i += 3) {
      vStr += `        new Vector3(${positions[i].toFixed(4)}f, ${positions[i+1].toFixed(4)}f, ${positions[i+2].toFixed(4)}f),\n`;
    }
    for (let i = 0; i < normals.length; i += 3) {
      nStr += `        new Vector3(${normals[i].toFixed(4)}f, ${normals[i+1].toFixed(4)}f, ${normals[i+2].toFixed(4)}f),\n`;
    }
    for (let i = 0; i < uvs.length; i += 2) {
      uvStr += `        new Vector2(${uvs[i].toFixed(4)}f, ${uvs[i+1].toFixed(4)}f),\n`;
    }
    for (let i = 0; i < indices.length; i++) {
      triStr += `${indices[i]}, `;
      if ((i + 1) % 12 === 0) triStr += "\n        ";
    }

    return `using UnityEngine;

[RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
public class Mesh_${assetName} : MonoBehaviour
{
    void Start()
    {
        Mesh mesh = new Mesh();
        mesh.name = "${assetName}_Mesh";

        Vector3[] vertices = new Vector3[]
        {
${vStr}        };

        Vector3[] normals = new Vector3[]
        {
${nStr}        };

        Vector2[] uv = new Vector2[]
        {
${uvStr}        };

        int[] triangles = new int[]
        {
${triStr}
        };

        mesh.vertices = vertices;
        mesh.normals = normals;
        mesh.uv = uv;
        mesh.triangles = triangles;
        mesh.RecalculateBounds();

        GetComponent<MeshFilter>().mesh = mesh;
    }
}`;
  },

  generateCocosCode: function(geometryData) {
    if (!geometryData) return '';
    const assetName = this.getCleanAssetName();
    const { positions, normals, uvs, indices } = geometryData;

    return `import { _decorator, Component, MeshRenderer, utils, primitives } from 'cc';
const { ccclass } = _decorator;

@ccclass('Mesh_${assetName}')
export class Mesh_${assetName} extends Component {
    start() {
        const positions = [${positions.map(p => p.toFixed(4)).join(', ')}];
        const normals = [${normals.map(n => n.toFixed(4)).join(', ')}];
        const uvs = [${uvs.map(u => u.toFixed(4)).join(', ')}];
        const indices = [${indices.join(', ')}];

        const geometry: primitives.IGeometry = {
            positions: positions,
            normals: normals,
            indices: indices,
            uvs: uvs,
            doubleSided: true
        };

        const mesh = utils.MeshUtils.createMesh(geometry);
        mesh.name = '${assetName}_Mesh';
        const meshRenderer = this.getComponent(MeshRenderer) || this.addComponent(MeshRenderer);
        meshRenderer.mesh = mesh;
    }
}`;
  },

  generateJsonData: function(geometryData) {
    if (!geometryData) return '{}';
    return JSON.stringify({
      assetName: this.getCleanAssetName(),
      pattern: document.getElementById('tex-pattern').value,
      topColor: document.getElementById('col-top').value,
      bottomColor: document.getElementById('col-bot').value,
      ...geometryData
    }, null, 2);
  }
};
