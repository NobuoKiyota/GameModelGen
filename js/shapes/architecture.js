// =============================================================
// Shape Group: 🏛️ Architecture & Pillars (Columns, Stairs, Structures)
// =============================================================
(function() {
  const CAT = 'architecture';
  ShapeRegistry.registerCategory(CAT, '🏛️ 柱・建築構造');

  // 1. Ancient Greek Pillar
  ShapeRegistry.registerShape(CAT, 'greek_pillar', {
    title: "Greek Pillar (🏛️ 古代神殿の円柱)",
    defaultName: "Pillar_01",
    defaultPattern: "rock",
    params: [
      { id: "height", label: "Pillar Height", min: 2.0, max: 10.0, step: 0.5, val: 5.0 },
      { id: "radius", label: "Column Radius", min: 0.2, max: 1.2, step: 0.05, val: 0.5 },
      { id: "flutes", label: "Flute Grooves", min: 6, max: 24, step: 2, val: 12 },
      { id: "fluteDepth", label: "Flute Depth", min: 0.02, max: 0.2, step: 0.01, val: 0.08 },
      { id: "capSize", label: "Capital Flange", min: 0.1, max: 0.8, step: 0.05, val: 0.35 },
      { id: "heightSegments", label: "Height Segs", min: 8, max: 32, step: 2, val: 16 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let y = 0; y <= p.heightSegments; y++) {
        const v = y / p.heightSegments, py = (v - 0.5) * p.height;
        const isCap = (v < 0.08 || v > 0.92);
        for (let s = 0; s <= p.flutes * 2; s++) {
          const u = s / (p.flutes * 2), angle = u * Math.PI * 2;
          const isFluteIn = (!isCap && s % 2 === 1);
          let r = p.radius;
          if (isCap) r *= (1.0 + p.capSize);
          else if (isFluteIn) r *= (1.0 - p.fluteDepth);
          positions.push(Math.cos(angle) * r, py, Math.sin(angle) * r);
          uvs.push(u * 4.0, v * 2.0);
        }
      }
      const stride = p.flutes * 2 + 1;
      for (let y = 0; y < p.heightSegments; y++) {
        for (let s = 0; s < p.flutes * 2; s++) {
          const a = y * stride + s, b = a + 1, c = (y + 1) * stride + s, d = c + 1;
          indices.push(a, b, d, a, d, c);
        }
      }
      return { positions, uvs, indices };
    }
  });

  // 2. Ruined Broken Pillar
  ShapeRegistry.registerShape(CAT, 'ruined_pillar', {
    title: "Ruined Pillar (🏚️ 崩れた遺跡柱)",
    defaultName: "RuinedPillar_01",
    defaultPattern: "rock",
    params: [
      { id: "height", label: "Height", min: 1.5, max: 8.0, step: 0.5, val: 3.5 },
      { id: "radius", label: "Radius", min: 0.2, max: 1.2, step: 0.05, val: 0.55 },
      { id: "fracture", label: "Break Fracture", min: 0.2, max: 1.5, step: 0.1, val: 0.8 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let y = 0; y <= 8; y++) {
        const v = y / 8, py = v * p.height;
        for (let s = 0; s <= 12; s++) {
          const u = s / 12, angle = u * Math.PI * 2;
          let r = p.radius;
          let brokenY = py;
          if (y === 8) brokenY += (Math.sin(u * Math.PI * 4) + Math.random() * 0.5) * p.fracture;
          positions.push(Math.cos(angle) * r, brokenY, Math.sin(angle) * r);
          uvs.push(u * 3.0, v * 1.5);
        }
      }
      for (let y = 0; y < 8; y++) {
        for (let s = 0; s < 12; s++) {
          const a = y * 13 + s, b = a + 1, c = (y + 1) * 13 + s, d = c + 1;
          indices.push(a, b, d, a, d, c);
        }
      }
      return { positions, uvs, indices };
    }
  });

  // 3. Wooden Pillar & Beam
  ShapeRegistry.registerShape(CAT, 'wooden_pillar', {
    title: "Wooden Pillar (🪵 木造角柱・梁)",
    defaultName: "WoodPillar_01",
    defaultPattern: "wood",
    params: [
      { id: "size", label: "Beam Width", min: 0.2, max: 1.5, step: 0.05, val: 0.5 },
      { id: "height", label: "Beam Height", min: 1.0, max: 8.0, step: 0.5, val: 4.0 },
      { id: "grainWobble", label: "Grain Wobble", min: 0.0, max: 1.0, step: 0.05, val: 0.3 }
    ],
    generator: function(p) {
      const base = new THREE.BoxGeometry(p.size, p.height, p.size, 2, 8, 2);
      const pos = base.getAttribute('position');
      for (let i = 0; i < pos.count; i++) {
        let x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i);
        const knot = Math.sin(y * 4.0) * p.grainWobble * 0.1;
        pos.setXYZ(i, x + knot, y, z + knot);
      }
      return ShapeRegistry.wrapThreeGeometry(() => base)(p);
    }
  });

  // 4. Spiral Stairs
  ShapeRegistry.registerShape(CAT, 'stairs', {
    title: "Spiral Stairs (🪜 螺旋階段)",
    defaultName: "SpiralStairs_01",
    defaultPattern: "rock",
    params: [
      { id: "steps", label: "Step Count", min: 6, max: 36, step: 1, val: 16 },
      { id: "innerRadius", label: "Inner Radius", min: 0.2, max: 2.0, step: 0.1, val: 0.5 },
      { id: "outerRadius", label: "Outer Radius", min: 1.0, max: 5.0, step: 0.2, val: 2.5 },
      { id: "height", label: "Total Height", min: 1.0, max: 8.0, step: 0.5, val: 3.5 },
      { id: "turns", label: "Turns", min: 0.5, max: 3.0, step: 0.25, val: 1.0 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      const totalAngle = p.turns * Math.PI * 2;
      for (let i = 0; i < p.steps; i++) {
        const t = i / p.steps, angle1 = t * totalAngle, angle2 = (t + 1 / p.steps) * totalAngle;
        const yTop = (t + 1 / p.steps) * p.height, vOff = positions.length / 3;
        positions.push(Math.cos(angle1) * p.innerRadius, yTop, Math.sin(angle1) * p.innerRadius); uvs.push(0, 0.85);
        positions.push(Math.cos(angle1) * p.outerRadius, yTop, Math.sin(angle1) * p.outerRadius); uvs.push(1, 0.85);
        positions.push(Math.cos(angle2) * p.innerRadius, yTop, Math.sin(angle2) * p.innerRadius); uvs.push(0, 0.85);
        positions.push(Math.cos(angle2) * p.outerRadius, yTop, Math.sin(angle2) * p.outerRadius); uvs.push(1, 0.85);
        indices.push(vOff, vOff + 1, vOff + 3, vOff, vOff + 3, vOff + 2);
      }
      return { positions, uvs, indices };
    }
  });
})();
