// =============================================================
// Shape Group: 📐 Primitives & Math Geometries
// =============================================================
(function() {
  const CAT_MATH = 'math';
  const CAT_PRIM = 'primitives';
  ShapeRegistry.registerCategory(CAT_PRIM, '📐 基本幾何学・多面体');
  ShapeRegistry.registerCategory(CAT_MATH, '🌀 数学・連続曲線');

  // Primitives
  ShapeRegistry.registerShape(CAT_PRIM, 'pipe', {
    title: "Pipe (パイプ / シリンダー)",
    defaultName: "Pipe_01",
    defaultPattern: "metal",
    params: [
      { id: "radius", label: "Radius", min: 0.1, max: 3.0, step: 0.05, val: 1.0 },
      { id: "height", label: "Height", min: 0.2, max: 5.0, step: 0.1, val: 2.0 },
      { id: "radialSegments", label: "Sides", min: 3, max: 64, step: 1, val: 24 }
    ],
    generator: ShapeRegistry.wrapThreeGeometry((p) => new THREE.CylinderGeometry(p.radius, p.radius, p.height, p.radialSegments, 4, true))
  });

  ShapeRegistry.registerShape(CAT_PRIM, 'capsule', {
    title: "Capsule (カプセル)",
    defaultName: "Capsule_01",
    defaultPattern: "grid",
    params: [
      { id: "radius", label: "Radius", min: 0.2, max: 2.0, step: 0.05, val: 0.8 },
      { id: "length", label: "Length", min: 0.5, max: 5.0, step: 0.1, val: 2.0 },
      { id: "radialSegments", label: "Sides", min: 6, max: 32, step: 1, val: 16 }
    ],
    generator: ShapeRegistry.wrapThreeGeometry((p) => new THREE.CylinderGeometry(p.radius, p.radius, p.length, p.radialSegments, 4, true))
  });

  ShapeRegistry.registerShape(CAT_PRIM, 'rounded_box', {
    title: "Box (角丸キューブ)",
    defaultName: "Box_01",
    defaultPattern: "grid",
    params: [
      { id: "width", label: "Width", min: 0.5, max: 4.0, step: 0.1, val: 2.0 },
      { id: "height", label: "Height", min: 0.5, max: 4.0, step: 0.1, val: 2.0 },
      { id: "depth", label: "Depth", min: 0.5, max: 4.0, step: 0.1, val: 2.0 },
      { id: "segments", label: "Subdivs", min: 1, max: 12, step: 1, val: 4 }
    ],
    generator: ShapeRegistry.wrapThreeGeometry((p) => new THREE.BoxGeometry(p.width, p.height, p.depth, p.segments, p.segments, p.segments))
  });

  ShapeRegistry.registerShape(CAT_PRIM, 'icosphere', {
    title: "Icosphere (アイコサスフィア)",
    defaultName: "Icosphere_01",
    defaultPattern: "rock",
    params: [
      { id: "radius", label: "Radius", min: 0.5, max: 3.0, step: 0.1, val: 1.5 },
      { id: "detail", label: "Detail", min: 0, max: 4, step: 1, val: 2 }
    ],
    generator: ShapeRegistry.wrapThreeGeometry((p) => new THREE.IcosahedronGeometry(p.radius, p.detail))
  });

  ShapeRegistry.registerShape(CAT_PRIM, 'dodecahedron', {
    title: "Dodecahedron (正十二面体)",
    defaultName: "Dodecahedron_01",
    defaultPattern: "metal",
    params: [
      { id: "radius", label: "Radius", min: 0.5, max: 3.0, step: 0.1, val: 1.5 },
      { id: "detail", label: "Detail", min: 0, max: 3, step: 1, val: 0 }
    ],
    generator: ShapeRegistry.wrapThreeGeometry((p) => new THREE.DodecahedronGeometry(p.radius, p.detail))
  });

  ShapeRegistry.registerShape(CAT_PRIM, 'octahedron', {
    title: "Octahedron (正八面体)",
    defaultName: "Octahedron_01",
    defaultPattern: "metal",
    params: [
      { id: "radius", label: "Radius", min: 0.5, max: 3.0, step: 0.1, val: 1.5 },
      { id: "detail", label: "Detail", min: 0, max: 3, step: 1, val: 0 }
    ],
    generator: ShapeRegistry.wrapThreeGeometry((p) => new THREE.OctahedronGeometry(p.radius, p.detail))
  });

  ShapeRegistry.registerShape(CAT_PRIM, 'fan', {
    title: "Fan Arc (扇形 / リングアーク)",
    defaultName: "Fan_01",
    defaultPattern: "metal",
    params: [
      { id: "innerRadius", label: "Inner R", min: 0.0, max: 3.0, step: 0.1, val: 0.5 },
      { id: "outerRadius", label: "Outer R", min: 1.0, max: 5.0, step: 0.1, val: 2.5 },
      { id: "angle", label: "Arc Angle", min: 15, max: 360, step: 5, val: 90 },
      { id: "segments", label: "Sides", min: 6, max: 48, step: 2, val: 18 }
    ],
    generator: ShapeRegistry.wrapThreeGeometry((p) => new THREE.RingGeometry(p.innerRadius, p.outerRadius, p.segments, 2, 0, p.angle * (Math.PI / 180)))
  });

  ShapeRegistry.registerShape(CAT_PRIM, 'star', {
    title: "Star Prism (星型多角柱)",
    defaultName: "Star_01",
    defaultPattern: "metal",
    params: [
      { id: "points", label: "Points", min: 3, max: 12, step: 1, val: 5 },
      { id: "outerRadius", label: "Radius", min: 0.8, max: 4.0, step: 0.1, val: 2.0 },
      { id: "height", label: "Height", min: 0.1, max: 4.0, step: 0.1, val: 0.8 }
    ],
    generator: ShapeRegistry.wrapThreeGeometry((p) => new THREE.CylinderGeometry(p.outerRadius, p.outerRadius, p.height, p.points * 2))
  });

  ShapeRegistry.registerShape(CAT_PRIM, 'crystal', {
    title: "Crystal Cluster (クリスタル / 鉱石)",
    defaultName: "Crystal_01",
    defaultPattern: "metal",
    params: [
      { id: "crystals", label: "Count", min: 1, max: 12, step: 1, val: 5 },
      { id: "height", label: "Height", min: 1.0, max: 6.0, step: 0.2, val: 3.2 },
      { id: "radius", label: "Radius", min: 0.2, max: 1.5, step: 0.05, val: 0.6 },
      { id: "clusterSpread", label: "Spread", min: 0.2, max: 2.5, step: 0.1, val: 1.1 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let c = 0; c < p.crystals; c++) {
        const angle = (c / p.crystals) * Math.PI * 2 + (c * 1.618);
        const dist = (c === 0) ? 0 : p.clusterSpread * 0.6;
        const cx = Math.cos(angle) * dist, cz = Math.sin(angle) * dist;
        const cH = p.height * (c === 0 ? 1.0 : 0.7), cR = p.radius * (c === 0 ? 1.0 : 0.6);
        const vOff = positions.length / 3;
        for (let s = 0; s <= 6; s++) {
          const u = s / 6, a = u * Math.PI * 2;
          positions.push(cx + Math.cos(a) * cR, 0, cz + Math.sin(a) * cR); uvs.push(u, 0.25);
          positions.push(cx + Math.cos(a) * cR, cH * 0.75, cz + Math.sin(a) * cR); uvs.push(u, 0.65);
        }
        for (let s = 0; s < 6; s++) {
          const a = vOff + s * 2, b = a + 1, d = a + 3;
          indices.push(a, b, d, a, d, a + 2);
        }
        const tipIndex = positions.length / 3;
        positions.push(cx, cH, cz); uvs.push(0.5, 0.95);
        for (let s = 0; s < 6; s++) indices.push(vOff + s * 2 + 1, vOff + (s + 1) * 2 + 1, tipIndex);
      }
      return { positions, uvs, indices };
    }
  });

  // Continuous Math Curves
  ShapeRegistry.registerShape(CAT_MATH, 'spiral', {
    title: "Spiral Tube (螺旋スパイラル)",
    defaultName: "Spiral_01",
    defaultPattern: "metal",
    params: [
      { id: "radius", label: "Base R", min: 0.5, max: 4.0, step: 0.1, val: 1.8 },
      { id: "tubeRadius", label: "Tube R", min: 0.05, max: 0.8, step: 0.02, val: 0.2 },
      { id: "height", label: "Height", min: 0.5, max: 8.0, step: 0.2, val: 3.5 },
      { id: "turns", label: "Turns", min: 1.0, max: 8.0, step: 0.5, val: 3.0 },
      { id: "segments", label: "Length Segs", min: 16, max: 96, step: 4, val: 48 },
      { id: "tubeSegments", label: "Tube Segs", min: 4, max: 16, step: 1, val: 8 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let i = 0; i <= p.segments; i++) {
        const v = i / p.segments, theta = v * p.turns * Math.PI * 2;
        const cx = Math.cos(theta) * p.radius, cz = Math.sin(theta) * p.radius, cy = (v - 0.5) * p.height;
        for (let s = 0; s <= p.tubeSegments; s++) {
          const u = s / p.tubeSegments, phi = u * Math.PI * 2;
          positions.push(cx + Math.cos(phi) * p.tubeRadius, cy + Math.sin(phi) * p.tubeRadius, cz + Math.sin(phi) * p.tubeRadius);
          uvs.push(u * 2.0, 0.58 + v * 0.38);
        }
      }
      const stride = p.tubeSegments + 1;
      for (let i = 0; i < p.segments; i++) {
        for (let s = 0; s < p.tubeSegments; s++) {
          const a = i * stride + s, b = a + 1, c = (i + 1) * stride + s, d = c + 1;
          indices.push(a, b, d, a, d, c);
        }
      }
      return { positions, uvs, indices };
    }
  });

  ShapeRegistry.registerShape(CAT_MATH, 'torus_knot', {
    title: "Torus Knot (トーラス結び目)",
    defaultName: "TorusKnot_01",
    defaultPattern: "metal",
    params: [
      { id: "radius", label: "Radius", min: 0.5, max: 3.0, step: 0.1, val: 1.2 },
      { id: "tube", label: "Tube R", min: 0.05, max: 0.8, step: 0.02, val: 0.35 },
      { id: "tubularSegments", label: "Tubular Segs", min: 16, max: 128, step: 4, val: 64 },
      { id: "radialSegments", label: "Radial Segs", min: 4, max: 24, step: 1, val: 8 },
      { id: "p", label: "P", min: 1, max: 8, step: 1, val: 2 },
      { id: "q", label: "Q", min: 1, max: 8, step: 1, val: 3 }
    ],
    generator: ShapeRegistry.wrapThreeGeometry((p) => new THREE.TorusKnotGeometry(p.radius, p.tube, p.tubularSegments, p.radialSegments, p.p, p.q))
  });

  ShapeRegistry.registerShape(CAT_MATH, 'mobius', {
    title: "Möbius Strip (メビウスの帯)",
    defaultName: "Mobius_01",
    defaultPattern: "metal",
    params: [
      { id: "radius", label: "Radius", min: 0.8, max: 4.0, step: 0.1, val: 1.8 },
      { id: "width", label: "Width", min: 0.2, max: 2.0, step: 0.1, val: 0.8 },
      { id: "segments", label: "Segs", min: 16, max: 64, step: 2, val: 36 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let i = 0; i <= p.segments; i++) {
        const u = (i / p.segments) * Math.PI * 2;
        for (let j = 0; j <= 4; j++) {
          const v = ((j / 4) - 0.5) * p.width;
          positions.push((p.radius + v * Math.cos(u * 0.5)) * Math.cos(u), v * Math.sin(u * 0.5), (p.radius + v * Math.cos(u * 0.5)) * Math.sin(u));
          uvs.push(u / (Math.PI * 2) * 2.0, 0.58 + (j / 4) * 0.38);
        }
      }
      for (let i = 0; i < p.segments; i++) {
        for (let j = 0; j < 4; j++) {
          const a = i * 5 + j, b = a + 1, c = (i + 1) * 5 + j, d = c + 1;
          indices.push(a, b, d, a, d, c);
        }
      }
      return { positions, uvs, indices };
    }
  });

  ShapeRegistry.registerShape(CAT_MATH, 'ribbon', {
    title: "Ribbon Trail (リボン / スプライン)",
    defaultName: "Ribbon_01",
    defaultPattern: "metal",
    params: [
      { id: "length", label: "Length", min: 2.0, max: 12.0, step: 0.5, val: 6.0 },
      { id: "width", label: "Width", min: 0.2, max: 2.5, step: 0.1, val: 1.0 },
      { id: "waves", label: "Waves", min: 0.5, max: 4.0, step: 0.25, val: 1.5 },
      { id: "amplitude", label: "Amp", min: 0.0, max: 2.0, step: 0.1, val: 0.6 },
      { id: "segments", label: "Segs", min: 12, max: 64, step: 2, val: 32 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let i = 0; i <= p.segments; i++) {
        const v = i / p.segments, pz = (v - 0.5) * p.length, waveY = Math.sin(v * Math.PI * 2 * p.waves) * p.amplitude;
        positions.push(-p.width * 0.5, waveY, pz); uvs.push(0, 0.58 + v * 0.38);
        positions.push(p.width * 0.5, waveY, pz); uvs.push(1, 0.58 + v * 0.38);
      }
      for (let i = 0; i < p.segments; i++) {
        indices.push(i * 2, i * 2 + 1, (i + 1) * 2 + 1, i * 2, (i + 1) * 2 + 1, (i + 1) * 2);
      }
      return { positions, uvs, indices };
    }
  });
})();
