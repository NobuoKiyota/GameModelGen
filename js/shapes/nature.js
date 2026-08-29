// =============================================================
// Shape Group: 🌲 Nature & Trees (Plants, Palms, Trees, Flora)
// =============================================================
(function() {
  const CAT = 'nature';
  ShapeRegistry.registerCategory(CAT, '🌲 木・植物・自然');

  // 1. Solid Pine Tree
  ShapeRegistry.registerShape(CAT, 'pine_tree', {
    title: "Solid Pine Tree (針葉樹・松の木)",
    defaultName: "PineTree_01",
    defaultPattern: "foliage",
    params: [
      { id: "trunkHeight", label: "Trunk Height", min: 1.0, max: 6.0, step: 0.2, val: 2.6 },
      { id: "trunkRadius", label: "Trunk Radius", min: 0.1, max: 0.8, step: 0.02, val: 0.26 },
      { id: "trunkFlare", label: "Root Flare", min: 0.0, max: 1.5, step: 0.1, val: 0.6 },
      { id: "foliageLayers", label: "Leaf Layers", min: 2, max: 7, step: 1, val: 4 },
      { id: "foliageRadius", label: "Bottom Width", min: 1.0, max: 4.5, step: 0.1, val: 2.2 },
      { id: "foliageDroop", label: "Leaf Droop", min: 0.0, max: 1.5, step: 0.05, val: 0.5 },
      { id: "foliageTaper", label: "Top Taper", min: 0.2, max: 0.8, step: 0.05, val: 0.35 },
      { id: "layerHeight", label: "Layer Height", min: 0.5, max: 2.5, step: 0.1, val: 1.3 },
      { id: "segments", label: "Radial Sides", min: 4, max: 16, step: 1, val: 7 }
    ],
    generator: function(p) {
      const { trunkRadius, trunkHeight, trunkFlare, foliageLayers, foliageRadius, foliageDroop, foliageTaper, layerHeight, segments } = p;
      const positions = [], uvs = [], indices = [];
      const trunkTopR = trunkRadius * 0.6;

      for (let y = 0; y <= 2; y++) {
        const v = y / 2, py = v * trunkHeight, r = v === 0 ? trunkRadius * (1.0 + trunkFlare) : (v === 0.5 ? trunkRadius : trunkTopR);
        for (let s = 0; s <= segments; s++) {
          const u = s / segments, angle = u * Math.PI * 2;
          positions.push(Math.cos(angle) * r, py, Math.sin(angle) * r);
          uvs.push(u * 2.0, v * 0.42);
        }
      }
      for (let y = 0; y < 2; y++) {
        for (let s = 0; s < segments; s++) {
          const r1 = y * (segments + 1), r2 = (y + 1) * (segments + 1);
          indices.push(r1 + s, r1 + s + 1, r2 + s + 1, r1 + s, r2 + s + 1, r2 + s);
        }
      }

      let currentY = trunkHeight * 0.45;
      for (let l = 0; l < foliageLayers; l++) {
        const layerRatio = l / foliageLayers, curR = foliageRadius * (1.0 - layerRatio * (1.0 - foliageTaper)), coneH = layerHeight * 1.3;
        const vOffset = positions.length / 3;

        for (let s = 0; s <= segments; s++) {
          const u = s / segments, angle = u * Math.PI * 2, droopSag = Math.sin(u * Math.PI * 8) * 0.05 - foliageDroop * 0.4;
          positions.push(Math.cos(angle) * curR, currentY + droopSag, Math.sin(angle) * curR);
          uvs.push(u * 3.0, 0.58 + layerRatio * 0.15);
        }

        const tipIndex = positions.length / 3;
        positions.push(0, currentY + coneH, 0); uvs.push(0.5, 0.95);
        const underIndex = positions.length / 3;
        positions.push(0, currentY - 0.1, 0); uvs.push(0.5, 0.65);

        for (let s = 0; s < segments; s++) {
          indices.push(vOffset + s, vOffset + s + 1, tipIndex);
          indices.push(vOffset + s + 1, vOffset + s, underIndex);
        }
        currentY += layerHeight * 0.65;
      }
      return { positions, uvs, indices };
    }
  });

  // 2. Round Tree
  ShapeRegistry.registerShape(CAT, 'round_tree', {
    title: "Round Tree (広葉樹・モコモコの木)",
    defaultName: "RoundTree_01",
    defaultPattern: "foliage",
    params: [
      { id: "trunkHeight", label: "Trunk Height", min: 1.0, max: 5.0, step: 0.2, val: 2.2 },
      { id: "trunkRadius", label: "Trunk Radius", min: 0.1, max: 0.8, step: 0.05, val: 0.3 },
      { id: "crownRadius", label: "Crown Radius", min: 1.0, max: 4.0, step: 0.1, val: 1.9 },
      { id: "bumps", label: "Bumpiness", min: 0.0, max: 0.6, step: 0.02, val: 0.25 },
      { id: "detail", label: "Detail", min: 1, max: 3, step: 1, val: 1 },
      { id: "segments", label: "Sides", min: 4, max: 16, step: 1, val: 6 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let y = 0; y <= 2; y++) {
        const py = y * (p.trunkHeight / 2), r = p.trunkRadius * (1.0 - y * 0.25);
        for (let s = 0; s <= p.segments; s++) {
          const u = s / p.segments, angle = u * Math.PI * 2;
          positions.push(Math.cos(angle) * r, py, Math.sin(angle) * r);
          uvs.push(u * 2.0, (y / 2) * 0.42);
        }
      }
      for (let y = 0; y < 2; y++) {
        for (let s = 0; s < p.segments; s++) {
          const r1 = y * (p.segments + 1), r2 = (y + 1) * (p.segments + 1);
          indices.push(r1 + s, r1 + s + 1, r2 + s + 1, r1 + s, r2 + s + 1, r2 + s);
        }
      }
      const crownGeo = new THREE.IcosahedronGeometry(p.crownRadius, p.detail);
      const cPos = crownGeo.getAttribute('position'), cOffset = positions.length / 3;
      for (let i = 0; i < cPos.count; i++) {
        let vx = cPos.getX(i), vy = cPos.getY(i), vz = cPos.getZ(i);
        const dist = Math.sqrt(vx * vx + vy * vy + vz * vz);
        const nx = vx / dist, ny = vy / dist, nz = vz / dist;
        const disp = (Math.sin(nx * 4.0) * Math.cos(ny * 4.0) * Math.sin(nz * 4.0)) * p.bumps * p.crownRadius;
        positions.push(vx + nx * disp, vy + ny * disp + p.trunkHeight + p.crownRadius * 0.65, vz + nz * disp);
        uvs.push((nx + 1) * 0.5, 0.58 + (ny + 1) * 0.5 * 0.38);
      }
      const cIdx = crownGeo.getIndex();
      for (let i = 0; i < cIdx.count; i++) indices.push(cOffset + cIdx.getX(i));
      return { positions, uvs, indices };
    }
  });

  // 3. Palm Tree
  ShapeRegistry.registerShape(CAT, 'palm_tree', {
    title: "Palm Tree (🌴 ヤシの木)",
    defaultName: "PalmTree_01",
    defaultPattern: "foliage",
    params: [
      { id: "trunkHeight", label: "Trunk Height", min: 2.0, max: 8.0, step: 0.5, val: 5.0 },
      { id: "trunkRadius", label: "Trunk Radius", min: 0.1, max: 0.6, step: 0.02, val: 0.25 },
      { id: "trunkBend", label: "Trunk Curve", min: 0.0, max: 3.0, step: 0.2, val: 1.2 },
      { id: "fronds", label: "Frond Count", min: 4, max: 12, step: 1, val: 7 },
      { id: "frondLength", label: "Frond Length", min: 1.5, max: 5.0, step: 0.2, val: 3.2 },
      { id: "frondWidth", label: "Frond Width", min: 0.4, max: 1.5, step: 0.1, val: 0.9 },
      { id: "frondDroop", label: "Frond Droop", min: 0.2, max: 2.0, step: 0.1, val: 1.0 },
      { id: "trunkSegments", label: "Trunk Segs", min: 4, max: 16, step: 1, val: 8 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let y = 0; y <= p.trunkSegments; y++) {
        const v = y / p.trunkSegments, py = v * p.trunkHeight;
        const curveX = Math.sin(v * Math.PI * 0.5) * p.trunkBend;
        const r = p.trunkRadius * (1.2 - v * 0.4);
        for (let s = 0; s <= 8; s++) {
          const u = s / 8, angle = u * Math.PI * 2;
          positions.push(curveX + Math.cos(angle) * r, py, Math.sin(angle) * r);
          uvs.push(u * 2.0, v * 0.42);
        }
      }
      for (let y = 0; y < p.trunkSegments; y++) {
        for (let s = 0; s < 8; s++) {
          const r1 = y * 9, r2 = (y + 1) * 9;
          indices.push(r1 + s, r1 + s + 1, r2 + s + 1, r1 + s, r2 + s + 1, r2 + s);
        }
      }
      const topX = Math.sin(Math.PI * 0.5) * p.trunkBend, topY = p.trunkHeight;
      for (let f = 0; f < p.fronds; f++) {
        const fAngle = (f / p.fronds) * Math.PI * 2;
        const vOff = positions.length / 3;
        for (let i = 0; i <= 6; i++) {
          const t = i / 6, dist = t * p.frondLength, sag = Math.pow(t, 2.0) * p.frondDroop;
          const fx = topX + Math.cos(fAngle) * dist, fy = topY - sag + (1.0 - t) * 0.5, fz = Math.sin(fAngle) * dist;
          const fw = Math.sin(t * Math.PI) * p.frondWidth;
          const perpX = -Math.sin(fAngle) * fw * 0.5, perpZ = Math.cos(fAngle) * fw * 0.5;
          positions.push(fx - perpX, fy, fz - perpZ); uvs.push(0, 0.75);
          positions.push(fx + perpX, fy, fz + perpZ); uvs.push(1, 0.75);
        }
        for (let i = 0; i < 6; i++) {
          const a = vOff + i * 2, b = a + 1, c = a + 2, d = a + 3;
          indices.push(a, b, d, a, d, c);
        }
      }
      return { positions, uvs, indices };
    }
  });

  // 4. Dead Spooky Tree
  ShapeRegistry.registerShape(CAT, 'dead_tree', {
    title: "Dead Spooky Tree (💀 枯れ木・怪樹)",
    defaultName: "DeadTree_01",
    defaultPattern: "wood",
    params: [
      { id: "trunkHeight", label: "Trunk Height", min: 2.0, max: 6.0, step: 0.5, val: 3.5 },
      { id: "trunkRadius", label: "Trunk Radius", min: 0.1, max: 0.6, step: 0.02, val: 0.28 },
      { id: "gnarledness", label: "Gnarled Noise", min: 0.0, max: 1.5, step: 0.1, val: 0.5 },
      { id: "branches", label: "Branch Count", min: 3, max: 8, step: 1, val: 5 },
      { id: "branchSpread", label: "Branch Spread", min: 1.0, max: 4.0, step: 0.2, val: 2.2 },
      { id: "seed", label: "Random Seed", min: 1, max: 50, step: 1, val: 7 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let y = 0; y <= 6; y++) {
        const v = y / 6, py = v * p.trunkHeight;
        const gnar = MeshNoise.fbm3D(v * 4, 0, p.seed, 3) * p.gnarledness;
        const r = p.trunkRadius * (1.3 - v * 0.5);
        for (let s = 0; s <= 6; s++) {
          const u = s / 6, angle = u * Math.PI * 2;
          positions.push(Math.cos(angle) * r + gnar, py, Math.sin(angle) * r);
          uvs.push(u * 2.0, v * 0.42);
        }
      }
      for (let y = 0; y < 6; y++) {
        for (let s = 0; s < 6; s++) {
          const r1 = y * 7, r2 = (y + 1) * 7;
          indices.push(r1 + s, r1 + s + 1, r2 + s + 1, r1 + s, r2 + s + 1, r2 + s);
        }
      }
      for (let b = 0; b < p.branches; b++) {
        const bAngle = (b / p.branches) * Math.PI * 2 + (b * 1.3);
        const startY = p.trunkHeight * (0.6 + (b % 3) * 0.15);
        const vOff = positions.length / 3;
        for (let i = 0; i <= 4; i++) {
          const t = i / 4, bLen = t * p.branchSpread, bLift = Math.sin(t * 1.5) * 1.2;
          const bx = Math.cos(bAngle) * bLen, by = startY + bLift, bz = Math.sin(bAngle) * bLen;
          const br = p.trunkRadius * 0.3 * (1.0 - t * 0.7);
          for (let s = 0; s <= 4; s++) {
            const u = s / 4, angle = u * Math.PI * 2;
            positions.push(bx + Math.cos(angle) * br, by, bz + Math.sin(angle) * br);
            uvs.push(u, 0.35);
          }
        }
        for (let i = 0; i < 4; i++) {
          for (let s = 0; s < 4; s++) {
            const a = vOff + i * 5 + s, c = vOff + (i + 1) * 5 + s;
            indices.push(a, a + 1, c + 1, a, c + 1, c);
          }
        }
      }
      return { positions, uvs, indices };
    }
  });

  // 5. Bamboo Stem
  ShapeRegistry.registerShape(CAT, 'bamboo', {
    title: "Bamboo Stem (🎍 竹・竹林)",
    defaultName: "Bamboo_01",
    defaultPattern: "foliage",
    params: [
      { id: "height", label: "Total Height", min: 2.0, max: 10.0, step: 0.5, val: 6.0 },
      { id: "radius", label: "Stem Radius", min: 0.05, max: 0.4, step: 0.02, val: 0.15 },
      { id: "nodes", label: "Node Count", min: 3, max: 12, step: 1, val: 7 },
      { id: "nodeBulge", label: "Node Bulge", min: 0.05, max: 0.6, step: 0.05, val: 0.25 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      const segH = p.height / p.nodes;
      for (let n = 0; n <= p.nodes; n++) {
        const yBase = n * segH;
        for (let sub = 0; sub <= 2; sub++) {
          const py = yBase + (sub === 1 ? 0.05 : 0);
          const isNodeRing = (sub === 1);
          const r = isNodeRing ? p.radius * (1.0 + p.nodeBulge) : p.radius;
          for (let s = 0; s <= 8; s++) {
            const u = s / 8, angle = u * Math.PI * 2;
            positions.push(Math.cos(angle) * r, py, Math.sin(angle) * r);
            uvs.push(u * 2.0, (n / p.nodes) * 0.42 + (isNodeRing ? 0.58 : 0));
          }
        }
      }
      const totalRings = (p.nodes + 1) * 3;
      for (let r = 0; r < totalRings - 1; r++) {
        for (let s = 0; s < 8; s++) {
          const r1 = r * 9, r2 = (r + 1) * 9;
          indices.push(r1 + s, r1 + s + 1, r2 + s + 1, r1 + s, r2 + s + 1, r2 + s);
        }
      }
      return { positions, uvs, indices };
    }
  });

  // 6. Desert Cactus
  ShapeRegistry.registerShape(CAT, 'cactus', {
    title: "Desert Cactus (🌵 サボテン)",
    defaultName: "Cactus_01",
    defaultPattern: "foliage",
    params: [
      { id: "height", label: "Height", min: 1.5, max: 6.0, step: 0.5, val: 3.5 },
      { id: "radius", label: "Radius", min: 0.2, max: 1.0, step: 0.05, val: 0.5 },
      { id: "ribs", label: "Rib Count", min: 4, max: 12, step: 1, val: 6 },
      { id: "ribDepth", label: "Rib Depth", min: 0.05, max: 0.4, step: 0.02, val: 0.18 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let y = 0; y <= 8; y++) {
        const v = y / 8, py = v * p.height;
        for (let s = 0; s <= p.ribs * 2; s++) {
          const u = s / (p.ribs * 2), angle = u * Math.PI * 2;
          const isRibOut = (s % 2 === 0);
          const r = isRibOut ? p.radius : p.radius * (1.0 - p.ribDepth);
          positions.push(Math.cos(angle) * r, py, Math.sin(angle) * r);
          uvs.push(u * 2.0, 0.58 + v * 0.38);
        }
      }
      const stride = p.ribs * 2 + 1;
      for (let y = 0; y < 8; y++) {
        for (let s = 0; s < p.ribs * 2; s++) {
          const r1 = y * stride, r2 = (y + 1) * stride;
          indices.push(r1 + s, r1 + s + 1, r2 + s + 1, r1 + s, r2 + s + 1, r2 + s);
        }
      }
      const topCenter = positions.length / 3;
      positions.push(0, p.height + p.radius * 0.6, 0); uvs.push(0.5, 0.95);
      const lastRing = 8 * stride;
      for (let s = 0; s < p.ribs * 2; s++) {
        indices.push(lastRing + s, lastRing + s + 1, topCenter);
      }
      return { positions, uvs, indices };
    }
  });

  // 7. Mushroom
  ShapeRegistry.registerShape(CAT, 'mushroom', {
    title: "Mushroom (キノコ)",
    defaultName: "Mushroom_01",
    defaultPattern: "foliage",
    params: [
      { id: "stemHeight", label: "Stem Height", min: 1.0, max: 5.0, step: 0.2, val: 2.2 },
      { id: "stemRadius", label: "Stem Radius", min: 0.1, max: 0.8, step: 0.02, val: 0.25 },
      { id: "stemBend", label: "Stem Curve", min: -1.5, max: 1.5, step: 0.1, val: 0.4 },
      { id: "capRadius", label: "Cap Radius", min: 0.5, max: 3.5, step: 0.1, val: 1.5 },
      { id: "capHeight", label: "Cap Height", min: 0.3, max: 2.5, step: 0.1, val: 1.0 },
      { id: "radialSegments", label: "Sides", min: 4, max: 24, step: 1, val: 12 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let y = 0; y <= 6; y++) {
        const v = y / 6, py = v * p.stemHeight, curveX = Math.sin(v * Math.PI * 0.5) * p.stemBend, curR = p.stemRadius * (1.2 - v * 0.4);
        for (let s = 0; s <= p.radialSegments; s++) {
          const u = s / p.radialSegments, angle = u * Math.PI * 2;
          positions.push(curveX + Math.cos(angle) * curR, py, Math.sin(angle) * curR);
          uvs.push(u * 2.0, v * 0.42);
        }
      }
      for (let y = 0; y < 6; y++) {
        for (let s = 0; s < p.radialSegments; s++) {
          const r1 = y * (p.radialSegments + 1), r2 = (y + 1) * (p.radialSegments + 1);
          indices.push(r1 + s, r1 + s + 1, r2 + s + 1, r1 + s, r2 + s + 1, r2 + s);
        }
      }
      const capOff = positions.length / 3, capCurveX = Math.sin(Math.PI * 0.5) * p.stemBend, capBaseY = p.stemHeight;
      for (let r = 0; r <= 4; r++) {
        const v = r / 4, theta = v * Math.PI * 0.5, py = capBaseY + Math.sin(theta) * p.capHeight, ringR = Math.cos(theta) * p.capRadius;
        for (let s = 0; s <= p.radialSegments; s++) {
          const u = s / p.radialSegments, angle = u * Math.PI * 2;
          positions.push(capCurveX + Math.cos(angle) * ringR, py, Math.sin(angle) * ringR);
          uvs.push(u * 2.0, 0.58 + v * 0.38);
        }
      }
      for (let r = 0; r < 4; r++) {
        for (let s = 0; s < p.radialSegments; s++) {
          const r1 = capOff + r * (p.radialSegments + 1), r2 = capOff + (r + 1) * (p.radialSegments + 1);
          indices.push(r1 + s, r1 + s + 1, r2 + s + 1, r1 + s, r2 + s + 1, r2 + s);
        }
      }
      return { positions, uvs, indices };
    }
  });
})();
