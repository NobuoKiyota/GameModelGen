// =============================================================
// UI Controller Module
// =============================================================
window.MeshUI = {
  currentTab: 'unity',

  init: function(onUpdateMesh, onUpdateMaterial) {
    this.populateShapeSelect();
    this.bindStaticEvents(onUpdateMesh, onUpdateMaterial);
    this.bindCodeModal();
  },

  populateShapeSelect: function() {
    const shapeSelect = document.getElementById('shape-type');
    shapeSelect.innerHTML = '';

    for (const [catKey, catObj] of Object.entries(ShapeRegistry.categories)) {
      const optGroup = document.createElement('optgroup');
      optGroup.label = catObj.label;

      catObj.shapes.forEach(shapeKey => {
        const config = ShapeRegistry.getConfig(shapeKey);
        if (config) {
          const opt = document.createElement('option');
          opt.value = shapeKey;
          opt.textContent = config.title;
          optGroup.appendChild(opt);
        }
      });
      shapeSelect.appendChild(optGroup);
    }
  },

  buildParamControls: function(onParamChange) {
    const shapeSelect = document.getElementById('shape-type');
    const dynamicParamsContainer = document.getElementById('dynamic-params');
    const assetNameInput = document.getElementById('asset-name');
    const shapeKey = shapeSelect.value;
    const config = ShapeRegistry.getConfig(shapeKey);

    dynamicParamsContainer.innerHTML = '';
    if (!config) return;

    if (config.defaultName && (!assetNameInput.value || assetNameInput.value.includes('_01'))) {
      assetNameInput.value = config.defaultName;
    }
    if (config.defaultPattern) {
      document.getElementById('tex-pattern').value = config.defaultPattern;
    }

    config.params.forEach(p => {
      const group = document.createElement('div');
      group.className = 'control-group';

      group.innerHTML = `
        <label for="param-${p.id}">
          <span>${p.label}</span>
          <span class="val" id="val-${p.id}">${p.val}</span>
        </label>
        <input type="range" id="param-${p.id}" min="${p.min}" max="${p.max}" step="${p.step}" value="${p.val}">
      `;
      const input = group.querySelector('input');
      const valDisplay = group.querySelector(`#val-${p.id}`);
      input.addEventListener('input', () => {
        p.val = parseFloat(input.value) || p.min;
        valDisplay.textContent = p.val;
        if (onParamChange) onParamChange();
      });
      dynamicParamsContainer.appendChild(group);
    });
  },

  getParamValues: function() {
    const shapeSelect = document.getElementById('shape-type');
    const shapeKey = shapeSelect.value;
    const config = ShapeRegistry.getConfig(shapeKey);
    const res = {};
    if (config && config.params) {
      config.params.forEach(p => { res[p.id] = p.val; });
    }
    return res;
  },

  randomizeShapeParams: function(onUpdate) {
    const shapeSelect = document.getElementById('shape-type');
    const shapeKey = shapeSelect.value;
    const config = ShapeRegistry.getConfig(shapeKey);
    if (!config) return;

    config.params.forEach(p => {
      const steps = Math.floor((p.max - p.min) / p.step);
      const randStep = Math.floor(Math.random() * (steps + 1));
      let newVal = p.min + randStep * p.step;
      if (p.step >= 1) newVal = Math.round(newVal);
      else newVal = parseFloat(newVal.toFixed(2));
      p.val = newVal;
    });
    this.buildParamControls(onUpdate);
    if (onUpdate) onUpdate();
  },

  randomizeMaterialParams: function(onUpdate) {
    function randHslToRgb(h, s, l) {
      let r, g, b;
      const hue2rgb = (p, q, t) => {
        if (t < 0) t += 1; if (t > 1) t -= 1;
        if (t < 1/6) return p + (q - p) * 6 * t;
        if (t < 1/2) return q;
        if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
        return p;
      };
      const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
      const p = 2 * l - q;
      r = Math.round(hue2rgb(p, q, h + 1/3) * 255);
      g = Math.round(hue2rgb(p, q, h) * 255);
      b = Math.round(hue2rgb(p, q, h - 1/3) * 255);
      return MeshNoise.rgbToHex(r, g, b);
    }

    const randHueTop = Math.random();
    const randHueBot = (randHueTop + 0.4 + Math.random() * 0.2) % 1.0;

    document.getElementById('col-top').value = randHslToRgb(randHueTop, 0.6 + Math.random() * 0.35, 0.45 + Math.random() * 0.2);
    document.getElementById('col-bot').value = randHslToRgb(randHueBot, 0.35 + Math.random() * 0.35, 0.25 + Math.random() * 0.2);
    document.getElementById('mat-theme-preset').value = 'custom';

    this.syncSliderDisplays();
    if (onUpdate) onUpdate();
  },

  syncSliderDisplays: function() {
    ['tex-tiling-x', 'tex-tiling-y', 'tex-noise-scale', 'tex-noise-str', 'pbr-roughness', 'pbr-metalness'].forEach(id => {
      const input = document.getElementById(id);
      const disp = document.getElementById(`val-${id}`);
      if (input && disp) disp.textContent = input.value;
    });
  },

  bindStaticEvents: function(onUpdateMesh, onUpdateMaterial) {
    const shapeSelect = document.getElementById('shape-type');
    const matThemePresetSelect = document.getElementById('mat-theme-preset');

    ['col-top', 'col-bot', 'tex-pattern', 'tex-tiling-x', 'tex-tiling-y', 'tex-noise-scale', 'tex-noise-str', 'pbr-roughness', 'pbr-metalness'].forEach(id => {
      document.getElementById(id).addEventListener('input', () => {
        this.syncSliderDisplays();
        if (onUpdateMaterial) onUpdateMaterial();
      });
    });

    matThemePresetSelect.addEventListener('change', () => {
      const theme = matThemePresetSelect.value;
      if (TextureStudio.themeDefaults[theme]) {
        document.getElementById('col-top').value = TextureStudio.themeDefaults[theme].top;
        document.getElementById('col-bot').value = TextureStudio.themeDefaults[theme].bot;
      }
      if (onUpdateMaterial) onUpdateMaterial();
    });

    document.getElementById('btn-randomize-shape').addEventListener('click', () => this.randomizeShapeParams(onUpdateMesh));
    document.getElementById('btn-randomize-mat').addEventListener('click', () => this.randomizeMaterialParams(onUpdateMaterial));

    shapeSelect.addEventListener('change', () => {
      this.buildParamControls(onUpdateMesh);
      if (onUpdateMesh) onUpdateMesh();
    });
  },

  bindCodeModal: function() {
    const codeModal = document.getElementById('code-modal');
    const codeOutput = document.getElementById('code-output');

    const updateCodeView = () => {
      if (!window.App || !App.currentGeometryData) return;
      if (this.currentTab === 'unity') codeOutput.textContent = MeshExporter.generateUnityCode(App.currentGeometryData);
      else if (this.currentTab === 'cocos') codeOutput.textContent = MeshExporter.generateCocosCode(App.currentGeometryData);
      else if (this.currentTab === 'json') codeOutput.textContent = MeshExporter.generateJsonData(App.currentGeometryData);
    };

    document.getElementById('btn-show-code').addEventListener('click', () => {
      updateCodeView();
      codeModal.style.display = 'flex';
    });

    document.getElementById('btn-close-modal').addEventListener('click', () => {
      codeModal.style.display = 'none';
    });

    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentTab = btn.dataset.tab;
        updateCodeView();
      });
    });

    document.getElementById('btn-copy-code').addEventListener('click', () => {
      navigator.clipboard.writeText(codeOutput.textContent).then(() => {
        const copyBtn = document.getElementById('btn-copy-code');
        const oldText = copyBtn.textContent;
        copyBtn.textContent = '✅ コピー完了!';
        setTimeout(() => copyBtn.textContent = oldText, 1500);
      });
    });
  },

  updateStats: function(geometryData) {
    const shapeKey = document.getElementById('shape-type').value;
    const config = ShapeRegistry.getConfig(shapeKey);
    if (!config || !geometryData) return;

    const isShared = document.getElementById('mat-mode').value === 'shared';
    document.getElementById('stat-asset').textContent = MeshExporter.getCleanAssetName();
    document.getElementById('stat-shape').textContent = config.title;
    document.getElementById('stat-pattern').textContent = document.getElementById('tex-pattern').value;
    document.getElementById('stat-mat-mode-badge').textContent = isShared ? "Shared Atlas" : "Unique Atlas";
    document.getElementById('stat-mat-mode-badge').style.background = isShared ? "rgba(16, 185, 129, 0.2)" : "rgba(236, 72, 153, 0.2)";
    document.getElementById('stat-mat-mode-badge').style.color = isShared ? "#6ee7b7" : "#f472b6";
    document.getElementById('stat-verts').textContent = (geometryData.positions.length / 3).toLocaleString();
    document.getElementById('stat-tris').textContent = (geometryData.indices.length / 3).toLocaleString();
  }
};
