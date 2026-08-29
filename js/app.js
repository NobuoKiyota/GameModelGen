// =============================================================
// Main Application & 3D Viewport Engine
// =============================================================
window.App = {
  scene: null,
  camera: null,
  renderer: null,
  controls: null,
  currentMesh: null,
  currentWireMesh: null,
  currentGeometryData: null,
  meshMaterial: null,
  wireMaterial: null,

  init: function() {
    const container = document.getElementById('viewport-container');
    const canvas = document.getElementById('viewport');

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x121214);

    this.camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    this.camera.position.set(4, 4, 6);

    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    this.renderer.setSize(container.clientWidth, container.clientHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
    this.scene.add(ambientLight);
    const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.85);
    dirLight1.position.set(6, 12, 8);
    this.scene.add(dirLight1);
    const dirLight2 = new THREE.DirectionalLight(0x3b82f6, 0.35);
    dirLight2.position.set(-6, -4, -6);
    this.scene.add(dirLight2);

    // Helpers
    const gridHelper = new THREE.GridHelper(12, 24, 0x3b82f6, 0x27272a);
    this.scene.add(gridHelper);
    const axesHelper = new THREE.AxesHelper(2.5);
    this.scene.add(axesHelper);

    // Materials
    this.meshMaterial = new THREE.MeshStandardMaterial({
      roughness: 0.6,
      metalness: 0.05,
      flatShading: false,
      side: THREE.DoubleSide
    });
    this.wireMaterial = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      wireframe: true,
      transparent: true,
      opacity: 0.22
    });

    // Initialize UI & Texture Studio
    MeshUI.init(
      () => this.updateMesh(),
      () => this.updateMaterial()
    );

    TextureStudio.initEvents(() => this.updateMaterial());

    // Export Buttons
    document.getElementById('btn-export-obj').addEventListener('click', () => {
      MeshExporter.exportObjOnly(this.currentGeometryData);
    });
    document.getElementById('btn-export-unity-zip').addEventListener('click', () => {
      MeshExporter.exportUnityZip(this.currentGeometryData);
    });

    // Viewport Display Toggles
    document.getElementById('chk-texture').addEventListener('change', () => this.updateMaterial());
    document.getElementById('chk-flatshading').addEventListener('change', () => this.updateMesh());
    document.getElementById('chk-wireframe').addEventListener('change', (e) => {
      if (this.currentWireMesh) this.currentWireMesh.visible = e.target.checked;
    });
    document.getElementById('mat-mode').addEventListener('change', () => MeshUI.updateStats(this.currentGeometryData));

    window.addEventListener('resize', () => {
      this.camera.aspect = container.clientWidth / container.clientHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(container.clientWidth, container.clientHeight);
    });

    // Initial Run
    MeshUI.syncSliderDisplays();
    MeshUI.buildParamControls(() => this.updateMesh());
    this.updateMesh();
    this.animate();
  },

  createBufferGeometry: function(data) {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(data.positions), 3));
    if (data.uvs && data.uvs.length > 0) {
      geo.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(data.uvs), 2));
    }
    if (data.indices && data.indices.length > 0) {
      geo.setIndex(data.indices);
    }
    geo.computeVertexNormals();
    return geo;
  },

  extractGeometryData: function(geo) {
    geo.computeVertexNormals();
    const posAttr = geo.getAttribute('position');
    const uvAttr = geo.getAttribute('uv');
    const normAttr = geo.getAttribute('normal');
    const indexAttr = geo.getIndex();

    const positions = Array.from(posAttr.array);
    const uvs = uvAttr ? Array.from(uvAttr.array) : [];
    const normals = normAttr ? Array.from(normAttr.array) : [];
    let indices = [];
    if (indexAttr) indices = Array.from(indexAttr.array);
    else for (let i = 0; i < posAttr.count; i++) indices.push(i);

    return { positions, uvs, normals, indices };
  },

  updateMaterial: function() {
    const showTex = document.getElementById('chk-texture').checked;
    const roughVal = parseFloat(document.getElementById('pbr-roughness').value) || 0.6;
    const metalVal = parseFloat(document.getElementById('pbr-metalness').value) || 0.05;
    const tileX = parseFloat(document.getElementById('tex-tiling-x').value) || 1.0;
    const tileY = parseFloat(document.getElementById('tex-tiling-y').value) || 1.0;

    this.meshMaterial.roughness = roughVal;
    this.meshMaterial.metalness = metalVal;

    if (showTex) {
      const canvasElem = TextureStudio.bakeAtlas();
      const activeTexture = new THREE.CanvasTexture(canvasElem);
      activeTexture.wrapS = THREE.RepeatWrapping;
      activeTexture.wrapT = THREE.RepeatWrapping;
      activeTexture.repeat.set(tileX, tileY);
      this.meshMaterial.map = activeTexture;
    } else {
      this.meshMaterial.map = null;
    }
    this.meshMaterial.needsUpdate = true;
  },

  updateMesh: function() {
    try {
      const shapeKey = document.getElementById('shape-type').value;
      const config = ShapeRegistry.getConfig(shapeKey);
      if (!config) return;
      const params = MeshUI.getParamValues();

      if (this.currentMesh) {
        this.scene.remove(this.currentMesh);
        this.currentMesh.geometry.dispose();
      }
      if (this.currentWireMesh) {
        this.scene.remove(this.currentWireMesh);
        this.currentWireMesh.geometry.dispose();
      }

      const rawData = config.generator(params);
      const geo = this.createBufferGeometry(rawData);
      this.currentGeometryData = this.extractGeometryData(geo);

      this.updateMaterial();

      const isFlat = document.getElementById('chk-flatshading').checked;
      this.meshMaterial.flatShading = isFlat;
      this.meshMaterial.needsUpdate = true;

      this.currentMesh = new THREE.Mesh(geo, this.meshMaterial);
      this.scene.add(this.currentMesh);

      this.currentWireMesh = new THREE.Mesh(geo, this.wireMaterial);
      this.currentWireMesh.visible = document.getElementById('chk-wireframe').checked;
      this.scene.add(this.currentWireMesh);

      geo.computeBoundingBox();
      const bb = geo.boundingBox;
      if (bb) {
        const dx = (bb.max.x - bb.min.x).toFixed(2);
        const dy = (bb.max.y - bb.min.y).toFixed(2);
        const dz = (bb.max.z - bb.min.z).toFixed(2);
        document.getElementById('stat-dim').textContent = `${dx} x ${dy} x ${dz}`;
      }

      MeshUI.updateStats(this.currentGeometryData);
    } catch (err) {
      console.error("updateMesh error:", err);
    }
  },

  animate: function() {
    requestAnimationFrame(() => this.animate());
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
};

// Bootstrap application on window load
window.addEventListener('DOMContentLoaded', () => {
  App.init();
});
