// =============================================================
// Shape Group: 🌾 Straw, Thatch, Crops & Flora Props
// =============================================================
(function() {
  const CAT = 'props';
  ShapeRegistry.registerCategory(CAT, '🌾 藁・低木・農業プロップ');

  // 1. Haystack (藁山)
  ShapeRegistry.registerShape(CAT, 'haystack', {
    title: "Haystack (🌾 藁山)",
    defaultName: "Haystack_01",
    defaultPattern: "straw",
    params: [
      { id: "height", label: "Height", min: 1.0, max: 5.0, step: 0.2, val: 2.5 },
      { id: "radius", label: "Base Radius", min: 0.8, max: 4.0, step: 0.2, val: 2.0 },
      { id: "roughness", label: "Straw Roughness", min: 0.0, max: 1.5, step: 0.1, val: 0.6 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let y = 0; y <= 6; y++) {
        const v = y / 6, py = v * p.height;
        const r = (1.0 - Math.pow(v, 1.4)) * p.radius;
        for (let s = 0; s <= 12; s++) {
          const u = s / 12, angle = u * Math.PI * 2;
          const wobble = (Math.sin(u * Math.PI * 12 + v * 8) * 0.1) * p.roughness;
          positions.push(Math.cos(angle) * (r + wobble), py, Math.sin(angle) * (r + wobble));
          uvs.push(u * 3.0, 0.58 + v * 0.38);
        }
      }
      for (let y = 0; y < 6; y++) {
        for (let s = 0; s < 12; s++) {
          const r1 = y * 13, r2 = (y + 1) * 13;
          indices.push(r1 + s, r1 + s + 1, r2 + s + 1, r1 + s, r2 + s + 1, r2 + s);
        }
      }
      const tip = positions.length / 3;
      positions.push(0, p.height + 0.2, 0); uvs.push(0.5, 0.95);
      for (let s = 0; s < 12; s++) indices.push(6 * 13 + s, 6 * 13 + s + 1, tip);
      return { positions, uvs, indices };
    }
  });

  // 2. Straw Bale (藁束・俵・ロール)
  ShapeRegistry.registerShape(CAT, 'straw_bale', {
    title: "Straw Bale (📦 藁束・俵)",
    defaultName: "StrawBale_01",
    defaultPattern: "straw",
    params: [
      { id: "width", label: "Width", min: 0.5, max: 3.0, step: 0.1, val: 1.2 },
      { id: "height", label: "Height", min: 0.4, max: 2.0, step: 0.1, val: 0.8 },
      { id: "length", label: "Length", min: 0.8, max: 4.0, step: 0.2, val: 2.0 },
      { id: "roughness", label: "Roughness", min: 0.0, max: 1.0, step: 0.1, val: 0.4 }
    ],
    generator: function(p) {
      const base = new THREE.BoxGeometry(p.width, p.height, p.length, 4, 4, 4);
      const pos = base.getAttribute('position');
      for (let i = 0; i < pos.count; i++) {
        let x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i);
        const disp = (Math.random() - 0.5) * p.roughness * 0.15;
        pos.setXYZ(i, x + disp, y + disp, z + disp);
      }
      return ShapeRegistry.wrapThreeGeometry(() => base)(p);
    }
  });

  // 3. Bush / Shrub (低木・草むら)
  ShapeRegistry.registerShape(CAT, 'bush_clump', {
    title: "Bush / Shrub (🌿 低木・草むら)",
    defaultName: "Bush_01",
    defaultPattern: "foliage",
    params: [
      { id: "radius", label: "Bush Radius", min: 0.5, max: 3.0, step: 0.1, val: 1.5 },
      { id: "clusters", label: "Clusters", min: 1, max: 6, step: 1, val: 4 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let c = 0; c < p.clusters; c++) {
        const angle = (c / p.clusters) * Math.PI * 2;
        const dist = (c === 0) ? 0 : p.radius * 0.45;
        const cx = Math.cos(angle) * dist, cz = Math.sin(angle) * dist;
        const cGeo = new THREE.IcosahedronGeometry(p.radius * (c === 0 ? 0.9 : 0.7), 1);
        const cPos = cGeo.getAttribute('position'), vOff = positions.length / 3;
        for (let i = 0; i < cPos.count; i++) {
          let vx = cPos.getX(i), vy = cPos.getY(i), vz = cPos.getZ(i);
          positions.push(cx + vx, vy * 0.85 + p.radius * 0.7, cz + vz);
          uvs.push((vx + 1) * 0.5, 0.58 + (vy + 1) * 0.5 * 0.38);
        }
        const cIdx = cGeo.getIndex();
        for (let i = 0; i < cIdx.count; i++) indices.push(vOff + cIdx.getX(i));
      }
      return { positions, uvs, indices };
    }
  });
})();
