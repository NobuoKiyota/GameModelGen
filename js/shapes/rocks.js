// =============================================================
// Shape Group: 🪨 Rocks, Cliffs, Walls & Stones
// =============================================================
(function() {
  const CAT = 'rocks';
  ShapeRegistry.registerCategory(CAT, '🪨 岩・壁・石垣・石造');

  // 1. Chiseled Procedural Rock
  ShapeRegistry.registerShape(CAT, 'rock', {
    title: "Pro Rock (プロシージャル岩)",
    defaultName: "Rock_01",
    defaultPattern: "rock",
    params: [
      { id: "radius", label: "Radius", min: 0.5, max: 3.5, step: 0.1, val: 1.5 },
      { id: "detail", label: "Detail", min: 0, max: 3, step: 1, val: 1 },
      { id: "roughness", label: "Roughness", min: 0.1, max: 1.8, step: 0.05, val: 0.75 },
      { id: "octaves", label: "Octaves", min: 1, max: 4, step: 1, val: 3 },
      { id: "chisel", label: "Chisel", min: 0.0, max: 1.0, step: 0.1, val: 0.6 },
      { id: "groundCut", label: "Ground Cut", min: 0.0, max: 0.6, step: 0.05, val: 0.15 },
      { id: "seed", label: "Seed", min: 1, max: 100, step: 1, val: 14 },
      { id: "scaleX", label: "Scale X", min: 0.4, max: 2.5, step: 0.05, val: 1.2 },
      { id: "scaleY", label: "Scale Y", min: 0.3, max: 2.5, step: 0.05, val: 0.95 },
      { id: "scaleZ", label: "Scale Z", min: 0.4, max: 2.5, step: 0.05, val: 1.1 }
    ],
    generator: function(p) {
      const baseGeo = new THREE.IcosahedronGeometry(p.radius, p.detail);
      const pos = baseGeo.getAttribute('position');
      const uvs = [];
      for (let i = 0; i < pos.count; i++) {
        let vx = pos.getX(i), vy = pos.getY(i), vz = pos.getZ(i);
        const dist = Math.sqrt(vx * vx + vy * vy + vz * vz);
        const nx = vx / dist, ny = vy / dist, nz = vz / dist;
        let fbm = MeshNoise.fbm3D(nx * 3.0, ny * 3.0, nz * 3.0, p.octaves, 2.0, 0.55, p.seed);
        if (p.chisel > 0.01) fbm = Math.abs(fbm);
        const disp = (fbm * 2.0 - 1.0) * p.roughness * p.radius * 0.4;
        let finalY = (vy + ny * disp) * p.scaleY;
        if (p.groundCut > 0.01 && finalY < -p.radius * (1.0 - p.groundCut)) {
          finalY = -p.radius * (1.0 - p.groundCut);
        }
        pos.setXYZ(i, (vx + nx * disp) * p.scaleX, finalY, (vz + nz * disp) * p.scaleZ);
        uvs.push((nx + 1) * 0.5 * 2.0, 0.58 + ny * 0.3);
      }
      const flatGeo = baseGeo.toNonIndexed();
      flatGeo.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(uvs), 2));
      return ShapeRegistry.wrapThreeGeometry(() => flatGeo)(p);
    }
  });

  // 2. Cliff Rock Wall
  ShapeRegistry.registerShape(CAT, 'rock_wall', {
    title: "Cliff Rock Wall (崖の岩壁)",
    defaultName: "RockWall_01",
    defaultPattern: "rock",
    params: [
      { id: "width", label: "Wall Width", min: 2.0, max: 12.0, step: 0.5, val: 6.0 },
      { id: "height", label: "Wall Height", min: 2.0, max: 10.0, step: 0.5, val: 4.5 },
      { id: "roughness", label: "Roughness", min: 0.1, max: 2.5, step: 0.1, val: 0.9 },
      { id: "seed", label: "Seed", min: 1, max: 50, step: 1, val: 8 },
      { id: "segX", label: "Segs X", min: 8, max: 32, step: 2, val: 18 },
      { id: "segY", label: "Segs Y", min: 8, max: 32, step: 2, val: 18 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let y = 0; y <= p.segY; y++) {
        const vy = y / p.segY, py = vy * p.height;
        for (let x = 0; x <= p.segX; x++) {
          const vx = x / p.segX, px = (vx - 0.5) * p.width;
          const noise = MeshNoise.fbm3D(vx * 4, vy * 4, p.seed, 3) * p.roughness;
          positions.push(px, py, noise);
          uvs.push(vx * 3.0, vy * 3.0);
        }
      }
      const stride = p.segX + 1;
      for (let y = 0; y < p.segY; y++) {
        for (let x = 0; x < p.segX; x++) {
          const a = y * stride + x, b = a + 1, c = (y + 1) * stride + x, d = c + 1;
          indices.push(a, b, d, a, d, c);
        }
      }
      return { positions, uvs, indices };
    }
  });

  // 3. Stone Masonry Wall
  ShapeRegistry.registerShape(CAT, 'stone_wall', {
    title: "Stone Masonry Wall (石積み壁・石垣)",
    defaultName: "StoneWall_01",
    defaultPattern: "rock",
    params: [
      { id: "width", label: "Wall Width", min: 2.0, max: 10.0, step: 0.5, val: 5.0 },
      { id: "height", label: "Wall Height", min: 1.0, max: 6.0, step: 0.5, val: 2.5 },
      { id: "rows", label: "Stone Rows", min: 2, max: 8, step: 1, val: 4 },
      { id: "columns", label: "Stone Columns", min: 4, max: 16, step: 1, val: 8 },
      { id: "brickDepth", label: "Stone Relief", min: 0.02, max: 0.3, step: 0.02, val: 0.1 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      const rowH = p.height / p.rows;
      for (let r = 0; r <= p.rows; r++) {
        const py = r * rowH;
        for (let c = 0; c <= p.columns; c++) {
          const u = c / p.columns, px = (u - 0.5) * p.width;
          const isIndent = (r % 2 === 0 && c % 2 === 0);
          const pz = isIndent ? -p.brickDepth : p.brickDepth;
          positions.push(px, py, pz);
          uvs.push(u * 4.0, (r / p.rows) * 4.0);
        }
      }
      const stride = p.columns + 1;
      for (let r = 0; r < p.rows; r++) {
        for (let c = 0; c < p.columns; c++) {
          const a = r * stride + c, b = a + 1, cd = (r + 1) * stride + c, d = cd + 1;
          indices.push(a, b, d, a, d, cd);
        }
      }
      return { positions, uvs, indices };
    }
  });

  // 4. Stepping Stone
  ShapeRegistry.registerShape(CAT, 'stepping_stone', {
    title: "Stepping Stone (平らな敷石・飛び石)",
    defaultName: "StepStone_01",
    defaultPattern: "rock",
    params: [
      { id: "radiusX", label: "Radius X", min: 0.4, max: 2.5, step: 0.1, val: 1.2 },
      { id: "radiusZ", label: "Radius Z", min: 0.4, max: 2.5, step: 0.1, val: 0.9 },
      { id: "thickness", label: "Thickness", min: 0.05, max: 0.8, step: 0.05, val: 0.2 },
      { id: "irregularity", label: "Irregularity", min: 0.0, max: 0.6, step: 0.05, val: 0.25 },
      { id: "seed", label: "Seed", min: 1, max: 50, step: 1, val: 5 },
      { id: "segments", label: "Sides", min: 6, max: 24, step: 1, val: 12 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let y = 0; y <= 2; y++) {
        const v = y / 2, py = (v - 0.5) * p.thickness;
        for (let s = 0; s <= p.segments; s++) {
          const u = s / p.segments, angle = u * Math.PI * 2;
          const wobble = MeshNoise.fbm3D(Math.cos(angle) * 3, Math.sin(angle) * 3, p.seed, 2) * p.irregularity;
          const rx = (p.radiusX + wobble), rz = (p.radiusZ + wobble);
          positions.push(Math.cos(angle) * rx, py, Math.sin(angle) * rz);
          uvs.push((Math.cos(angle) + 1) * 0.5 * 2.0, (y === 2) ? 0.85 : 0.25);
        }
      }
      const stride = p.segments + 1;
      for (let y = 0; y < 2; y++) {
        for (let s = 0; s < p.segments; s++) {
          const a = y * stride + s, b = a + 1, c = (y + 1) * stride + s, d = c + 1;
          indices.push(a, b, d, a, d, c);
        }
      }
      const botC = positions.length / 3; positions.push(0, -p.thickness * 0.5, 0); uvs.push(0.5, 0.25);
      const topC = positions.length / 3; positions.push(0, p.thickness * 0.5, 0); uvs.push(0.5, 0.85);
      for (let s = 0; s < p.segments; s++) {
        indices.push(s + 1, s, botC);
        indices.push(2 * stride + s, 2 * stride + s + 1, topC);
      }
      return { positions, uvs, indices };
    }
  });

  // 5. Spire Rock / Stalagmite
  ShapeRegistry.registerShape(CAT, 'spire_rock', {
    title: "Spire Rock (尖塔岩・鍾乳石)",
    defaultName: "SpireRock_01",
    defaultPattern: "rock",
    params: [
      { id: "height", label: "Spire Height", min: 2.0, max: 12.0, step: 0.5, val: 6.0 },
      { id: "baseRadius", label: "Base Radius", min: 0.4, max: 2.5, step: 0.1, val: 1.2 },
      { id: "twist", label: "Twist", min: 0.0, max: 2.0, step: 0.1, val: 0.5 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let y = 0; y <= 8; y++) {
        const v = y / 8, py = v * p.height;
        const r = (1.0 - Math.pow(v, 0.85)) * p.baseRadius;
        for (let s = 0; s <= 6; s++) {
          const u = s / 6, angle = u * Math.PI * 2;
          const twist = Math.sin(v * Math.PI * 2) * p.twist;
          positions.push(Math.cos(angle + twist) * r, py, Math.sin(angle + twist) * r);
          uvs.push(u * 2.0, 0.25 + v * 0.6);
        }
      }
      for (let y = 0; y < 8; y++) {
        for (let s = 0; s < 6; s++) {
          const r1 = y * 7, r2 = (y + 1) * 7;
          indices.push(r1 + s, r1 + s + 1, r2 + s + 1, r1 + s, r2 + s + 1, r2 + s);
        }
      }
      const tip = positions.length / 3;
      positions.push(0, p.height + 0.1, 0); uvs.push(0.5, 0.95);
      for (let s = 0; s < 6; s++) indices.push(8 * 7 + s, 8 * 7 + s + 1, tip);
      return { positions, uvs, indices };
    }
  });
})();
