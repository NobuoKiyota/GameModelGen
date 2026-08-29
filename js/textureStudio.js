// =============================================================
// Texture Studio Engine (Procedural Atlas + Drag & Drop Custom Texture)
// =============================================================
window.TextureStudio = {
  customImage: null,
  activeTexture: null,

  themeDefaults: {
    spring: { top: "#2d8832", bot: "#5a351e" },
    autumn: { top: "#d94b18", bot: "#4a2414" },
    sakura: { top: "#f48fb1", bot: "#bcaaa4" },
    winter: { top: "#e0f2fe", bot: "#2c3b4d" },
    desert: { top: "#c2a66b", bot: "#73604f" },
    mystic: { top: "#9333ea", bot: "#24143a" },
    volcano: { top: "#ea580c", bot: "#1c1917" }
  },

  bakeAtlas: function() {
    const texCanvas = document.getElementById('tex-canvas');
    const texCtx = texCanvas.getContext('2d');
    const size = 512, half = size / 2;
    texCanvas.width = size;
    texCanvas.height = size;

    const imgData = texCtx.createImageData(size, size);
    const data = imgData.data;

    const topCol = MeshNoise.hexToRgb(document.getElementById('col-top').value);
    const botCol = MeshNoise.hexToRgb(document.getElementById('col-bot').value);
    const pattern = document.getElementById('tex-pattern').value;

    const noiseScale = parseFloat(document.getElementById('tex-noise-scale').value) || 6.0;
    const noiseStr = parseFloat(document.getElementById('tex-noise-str').value) || 0.5;

    for (let y = 0; y < size; y++) {
      const isTopHalf = (y < half);
      const vLocal = isTopHalf ? (y / half) : ((y - half) / half);
      const baseCol = isTopHalf ? topCol : botCol;

      for (let x = 0; x < size; x++) {
        const idx = (y * size + x) * 4;
        const uLocal = x / size;

        let n = MeshNoise.fbm3D(uLocal * noiseScale, vLocal * noiseScale, isTopHalf ? 1.0 : 0.0, 3) * noiseStr;
        let grain = 0;

        if (pattern === 'straw') {
          grain = Math.sin(uLocal * 80.0 + n * 8.0) * 35.0 + (Math.random() - 0.5) * 20.0;
        } else if (pattern === 'metal') {
          grain = (Math.random() - 0.5) * 40.0;
          n = (Math.sin(uLocal * 60.0) * 0.2 + (Math.random() - 0.5) * 0.2) * noiseStr;
        } else if (pattern === 'water') {
          const c1 = Math.sin(uLocal * 18.0 + vLocal * 12.0) + Math.cos(uLocal * 14.0 - vLocal * 16.0);
          grain = (c1 > 1.2) ? 60 * noiseStr : 0;
        } else if (pattern === 'wood') {
          grain = Math.sin(uLocal * 32.0 + n * 6.0) * 25.0;
        } else {
          grain = Math.sin(uLocal * Math.PI * 32.0 + n * 4.0) * 15.0;
        }

        let r = baseCol.r + n * 50 + grain;
        let g = baseCol.g + n * 50 + grain;
        let b = baseCol.b + n * 50 + grain;

        data[idx] = Math.min(255, Math.max(0, r));
        data[idx+1] = Math.min(255, Math.max(0, g));
        data[idx+2] = Math.min(255, Math.max(0, b));
        data[idx+3] = 255;
      }
    }
    texCtx.putImageData(imgData, 0, 0);

    if (this.customImage) {
      texCtx.save();
      texCtx.globalAlpha = 0.85;
      texCtx.globalCompositeOperation = 'overlay';
      texCtx.drawImage(this.customImage, 0, 0, size, size);
      texCtx.restore();
    }

    return texCanvas;
  },

  initEvents: function(onTextureUpdate) {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewContainer = document.getElementById('custom-tex-preview');
    const texThumb = document.getElementById('tex-thumb');
    const texFilename = document.getElementById('tex-filename');
    const btnClearTex = document.getElementById('btn-clear-tex');

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        this.loadImage(e.dataTransfer.files[0], onTextureUpdate);
      }
    });
    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        this.loadImage(e.target.files[0], onTextureUpdate);
      }
    });

    btnClearTex.addEventListener('click', (e) => {
      e.stopPropagation();
      this.customImage = null;
      previewContainer.style.display = 'none';
      fileInput.value = '';
      if (onTextureUpdate) onTextureUpdate();
    });
  },

  loadImage: function(file, callback) {
    const previewContainer = document.getElementById('custom-tex-preview');
    const texThumb = document.getElementById('tex-thumb');
    const texFilename = document.getElementById('tex-filename');

    const reader = new FileReader();
    reader.onload = (evt) => {
      const img = new Image();
      img.onload = () => {
        this.customImage = img;
        texThumb.src = evt.target.result;
        texFilename.textContent = file.name;
        previewContainer.style.display = 'flex';
        if (callback) callback();
      };
      img.src = evt.target.result;
    };
    reader.readAsDataURL(file);
  }
};
