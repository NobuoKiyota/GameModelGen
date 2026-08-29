// =============================================================
// Shape Group: 🌊 Terrain & Water (Waterfall, Lake, Canyon, Arch, Cliff)
// =============================================================
(function() {
  const CAT = 'terrain';
  ShapeRegistry.registerCategory(CAT, '🌊 水景・高度地形・巨岩');

  // 1. Waterfall
  ShapeRegistry.registerShape(CAT, 'waterfall', {
    title: "Waterfall (滝・カスケード)",
    defaultName: "Waterfall_01",
    defaultPattern: "water",
    params: [
      { id: "height", label: "Drop Height", min: 2.0, max: 15.0, step: 0.5, val: 7.0 },
      { id: "topWidth", label: "Top Width", min: 0.5, max: 4.0, step: 0.1, val: 1.5 },
      { id: "botWidth", label: "Bot Width", min: 1.0, max: 8.0, step: 0.2, val: 4.5 },
      { id: "curvature", label: "Curvature", min: 0.5, max: 6.0, step: 0.2, val: 2.5 },
      { id: "segY", label: "Segs Y", min: 16, max: 64, step: 2, val: 36 },
      { id: "segX", label: "Segs X", min: 6, max: 32, step: 2, val: 18 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let y = 0; y <= p.segY; y++) {
        const v = y / p.segY, py = (1.0 - v) * p.height;
        const curWidth = p.topWidth + (p.botWidth - p.topWidth) * Math.pow(v, 1.2);
        for (let x = 0; x <= p.segX; x++) {
          const u = x / p.segX, px = (u - 0.5) * curWidth;
          positions.push(px, py, Math.pow(v, 1.8) * p.curvature);
          uvs.push(u * 2.0, (v < 0.15 || v > 0.85) ? 0.85 : 0.25);
        }
      }
      const stride = p.segX + 1;
      for (let y = 0; y < p.segY; y++) {
        for (let x = 0; x < p.segX; x++) {
          const a = y * stride + x;
          indices.push(a, a + 1, a + stride + 1, a, a + stride + 1, a + stride);
        }
      }
      return { positions, uvs, indices };
    }
  });

  // 2. Lake Basin
  ShapeRegistry.registerShape(CAT, 'lake_basin', {
    title: "Lake Basin (湖・クレーター湖)",
    defaultName: "LakeBasin_01",
    defaultPattern: "water",
    params: [
      { id: "lakeRadius", label: "Lake Radius", min: 1.0, max: 6.0, step: 0.2, val: 2.8 },
      { id: "basinRadius", label: "Rim Radius", min: 2.0, max: 10.0, step: 0.5, val: 5.5 },
      { id: "lakeDepth", label: "Lake Depth", min: 0.5, max: 4.0, step: 0.1, val: 1.5 },
      { id: "rimHeight", label: "Rim Height", min: 0.0, max: 5.0, step: 0.2, val: 2.2 },
      { id: "radialSteps", label: "Radial Steps", min: 8, max: 36, step: 2, val: 18 },
      { id: "segments", label: "Segs", min: 12, max: 64, step: 2, val: 32 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let r = 0; r <= p.radialSteps; r++) {
        const v = r / p.radialSteps, curR = p.basinRadius * v;
        for (let s = 0; s <= p.segments; s++) {
          const u = s / p.segments, angle = u * Math.PI * 2;
          let py = curR < p.lakeRadius
            ? -p.lakeDepth * (1.0 - Math.pow(curR / p.lakeRadius, 2))
            : Math.sin((curR - p.lakeRadius) / (p.basinRadius - p.lakeRadius) * Math.PI) * p.rimHeight;
          positions.push(Math.cos(angle) * curR, py, Math.sin(angle) * curR);
          uvs.push(u * 2.0, 0.25);
        }
      }
      const stride = p.segments + 1;
      for (let r = 0; r < p.radialSteps; r++) {
        for (let s = 0; s < p.segments; s++) {
          const a = r * stride + s;
          indices.push(a, a + 1, a + stride + 1, a, a + stride + 1, a + stride);
        }
      }
      return { positions, uvs, indices };
    }
  });

  // 3. River Canyon
  ShapeRegistry.registerShape(CAT, 'river_canyon', {
    title: "River Canyon (蛇行渓谷・川)",
    defaultName: "RiverCanyon_01",
    defaultPattern: "water",
    params: [
      { id: "length", label: "Length", min: 4.0, max: 16.0, step: 0.5, val: 8.0 },
      { id: "valleyWidth", label: "Valley Width", min: 2.0, max: 10.0, step: 0.2, val: 5.0 },
      { id: "riverWidth", label: "River Width", min: 0.5, max: 4.0, step: 0.1, val: 1.4 },
      { id: "canyonDepth", label: "Depth", min: 0.5, max: 5.0, step: 0.2, val: 2.0 },
      { id: "meanders", label: "Meanders", min: 0.5, max: 4.0, step: 0.25, val: 1.5 },
      { id: "meanderAmp", label: "Amp", min: 0.0, max: 3.5, step: 0.1, val: 1.4 },
      { id: "segments", label: "Segs", min: 16, max: 64, step: 2, val: 36 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let i = 0; i <= p.segments; i++) {
        const v = i / p.segments, pz = (v - 0.5) * p.length;
        const curveX = Math.sin(v * Math.PI * 2 * p.meanders) * p.meanderAmp;
        for (let j = 0; j <= 8; j++) {
          const u = j / 8, localX = (u - 0.5) * p.valleyWidth, px = curveX + localX;
          const py = Math.abs(localX) < p.riverWidth * 0.5 ? -p.canyonDepth : 0;
          positions.push(px, py, pz);
          uvs.push(u * 2.0, 0.25);
        }
      }
      for (let i = 0; i < p.segments; i++) {
        for (let j = 0; j < 8; j++) {
          const a = i * 9 + j;
          indices.push(a, a + 1, a + 10, a, a + 10, a + 9);
        }
      }
      return { positions, uvs, indices };
    }
  });

  // 4. Rock Arch
  ShapeRegistry.registerShape(CAT, 'rock_arch', {
    title: "Rock Arch (洞窟・岩石アーチ)",
    defaultName: "RockArch_01",
    defaultPattern: "rock",
    params: [
      { id: "archSpan", label: "Span", min: 1.5, max: 6.0, step: 0.2, val: 3.2 },
      { id: "archHeight", label: "Height", min: 1.0, max: 5.0, step: 0.2, val: 2.5 },
      { id: "archDepth", label: "Depth", min: 1.0, max: 5.0, step: 0.2, val: 2.5 },
      { id: "rockThickness", label: "Thickness", min: 0.4, max: 2.5, step: 0.1, val: 1.1 },
      { id: "segments", label: "Segs", min: 8, max: 32, step: 2, val: 18 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let z = 0; z <= 6; z++) {
        const pz = (z / 6 - 0.5) * p.archDepth;
        for (let i = 0; i <= p.segments; i++) {
          const u = i / p.segments, theta = u * Math.PI;
          positions.push(Math.cos(theta) * p.archSpan * 0.5, Math.sin(theta) * p.archHeight, pz);
          uvs.push(u * 3.0, 0.25);
          positions.push(Math.cos(theta) * (p.archSpan * 0.5 + p.rockThickness), Math.sin(theta) * (p.archHeight + p.rockThickness), pz);
          uvs.push(u * 3.0, 0.85);
        }
      }
      const ringStride = (p.segments + 1) * 2;
      for (let z = 0; z < 6; z++) {
        for (let i = 0; i < p.segments; i++) {
          const a = z * ringStride + i * 2, b = a + 1, c = a + 2, d = a + 3;
          indices.push(a, b, d, a, d, c);
        }
      }
      return { positions, uvs, indices };
    }
  });

  // 5. Terraced Cliff
  ShapeRegistry.registerShape(CAT, 'terraced_cliff', {
    title: "Terraced Cliff (断層崖・テラス岩盤)",
    defaultName: "TerracedCliff_01",
    defaultPattern: "rock",
    params: [
      { id: "width", label: "Width", min: 2.0, max: 10.0, step: 0.5, val: 6.0 },
      { id: "height", label: "Height", min: 2.0, max: 10.0, step: 0.5, val: 5.0 },
      { id: "tiers", label: "Tiers", min: 2, max: 8, step: 1, val: 4 },
      { id: "stepDepth", label: "Step Depth", min: 0.2, max: 1.5, step: 0.05, val: 0.6 },
      { id: "segments", label: "Segs", min: 6, max: 32, step: 2, val: 16 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let t = 0; t <= p.tiers; t++) {
        const vt = t / p.tiers, py = vt * p.height, pz = -vt * p.stepDepth * p.tiers;
        for (let s = 0; s <= p.segments; s++) {
          const u = s / p.segments, px = (u - 0.5) * p.width;
          positions.push(px, py, pz);
          uvs.push(u * 3.0, (t % 2 === 0) ? 0.85 : 0.25);
        }
      }
      const stride = p.segments + 1;
      for (let t = 0; t < p.tiers; t++) {
        for (let s = 0; s < p.segments; s++) {
          const a = t * stride + s;
          indices.push(a, a + 1, a + stride + 1, a, a + stride + 1, a + stride);
        }
      }
      return { positions, uvs, indices };
    }
  });

  // 6. Noise Terrain
  ShapeRegistry.registerShape(CAT, 'noise', {
    title: "Noise Terrain (ノイズ地形)",
    defaultName: "Terrain_01",
    defaultPattern: "rock",
    params: [
      { id: "width", label: "Width", min: 1.0, max: 10.0, step: 0.5, val: 5.0 },
      { id: "depth", label: "Depth", min: 1.0, max: 10.0, step: 0.5, val: 5.0 },
      { id: "segX", label: "Segs X", min: 4, max: 64, step: 2, val: 32 },
      { id: "segZ", label: "Segs Z", min: 4, max: 64, step: 2, val: 32 }
    ],
    generator: ShapeRegistry.wrapThreeGeometry((p) => new THREE.PlaneGeometry(p.width, p.depth, p.segX, p.segZ))
  });
})();
