// =============================================================
// Shape Group: ✨ Game Effects & UI (Slash, Tornado, Beam, Lightning, Magic Circle, Spectrum)
// =============================================================
(function() {
  const CAT = 'effects';
  ShapeRegistry.registerCategory(CAT, '✨ ゲームエフェクト・UI');

  // 1. Slash Trail Arc
  ShapeRegistry.registerShape(CAT, 'slash', {
    title: "Slash Trail (スラッシュ・トレイル)",
    defaultName: "SlashTrail_01",
    defaultPattern: "metal",
    params: [
      { id: "innerRadius", label: "Inner R", min: 0.1, max: 3.0, step: 0.1, val: 1.5 },
      { id: "outerRadius", label: "Outer R", min: 0.5, max: 5.0, step: 0.1, val: 2.8 },
      { id: "arcAngle", label: "Arc Angle", min: 30, max: 360, step: 5, val: 160 },
      { id: "segments", label: "Segs", min: 8, max: 64, step: 2, val: 32 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      const totalRad = p.arcAngle * (Math.PI / 180);
      for (let i = 0; i <= p.segments; i++) {
        const u = i / p.segments, angle = u * totalRad;
        positions.push(Math.cos(angle) * p.innerRadius, 0, Math.sin(angle) * p.innerRadius);
        uvs.push(0, 0.25);
        positions.push(Math.cos(angle) * p.outerRadius, 0, Math.sin(angle) * p.outerRadius);
        uvs.push(1, 0.85);
      }
      for (let i = 0; i < p.segments; i++) {
        indices.push(i * 2, i * 2 + 1, (i + 1) * 2 + 1, i * 2, (i + 1) * 2 + 1, (i + 1) * 2);
      }
      return { positions, uvs, indices };
    }
  });

  // 2. Tornado Vortex
  ShapeRegistry.registerShape(CAT, 'tornado', {
    title: "Tornado Vortex (トルネード・竜巻)",
    defaultName: "Tornado_01",
    defaultPattern: "water",
    params: [
      { id: "bottomRadius", label: "Bot Radius", min: 0.1, max: 2.0, step: 0.1, val: 0.3 },
      { id: "topRadius", label: "Top Radius", min: 1.0, max: 6.0, step: 0.2, val: 3.2 },
      { id: "height", label: "Height", min: 2.0, max: 10.0, step: 0.5, val: 5.0 },
      { id: "rotations", label: "Turns", min: 1.0, max: 6.0, step: 0.5, val: 2.5 },
      { id: "radialSegments", label: "Radial Segs", min: 8, max: 32, step: 2, val: 16 },
      { id: "heightSegments", label: "Height Segs", min: 8, max: 32, step: 2, val: 16 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let y = 0; y <= p.heightSegments; y++) {
        const v = y / p.heightSegments, py = v * p.height, r = p.bottomRadius + (p.topRadius - p.bottomRadius) * Math.pow(v, 1.3);
        const twistAngle = v * p.rotations * Math.PI * 2;
        for (let s = 0; s <= p.radialSegments; s++) {
          const u = s / p.radialSegments, angle = u * Math.PI * 2 + twistAngle;
          positions.push(Math.cos(angle) * r, py, Math.sin(angle) * r);
          uvs.push(u * 2.0, 0.58 + v * 0.38);
        }
      }
      const stride = p.radialSegments + 1;
      for (let y = 0; y < p.heightSegments; y++) {
        for (let s = 0; s < p.radialSegments; s++) {
          const a = y * stride + s, b = a + 1, c = (y + 1) * stride + s, d = c + 1;
          indices.push(a, b, d, a, d, c);
        }
      }
      return { positions, uvs, indices };
    }
  });

  // 3. Light Beam
  ShapeRegistry.registerShape(CAT, 'beam', {
    title: "Light Beam (ライトビーム / 光線)",
    defaultName: "Beam_01",
    defaultPattern: "metal",
    params: [
      { id: "radius", label: "Radius", min: 0.1, max: 3.0, step: 0.1, val: 0.6 },
      { id: "length", label: "Length", min: 2.0, max: 20.0, step: 1.0, val: 8.0 },
      { id: "taper", label: "Taper", min: 0.1, max: 2.0, step: 0.1, val: 1.0 },
      { id: "radialSegments", label: "Radial Segs", min: 4, max: 32, step: 2, val: 16 },
      { id: "heightSegments", label: "Height Segs", min: 2, max: 16, step: 1, val: 4 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let y = 0; y <= p.heightSegments; y++) {
        const v = y / p.heightSegments, py = (v - 0.5) * p.length, curR = p.radius * (1.0 - (1.0 - p.taper) * v);
        for (let s = 0; s <= p.radialSegments; s++) {
          const u = s / p.radialSegments, angle = u * Math.PI * 2;
          positions.push(Math.cos(angle) * curR, py, Math.sin(angle) * curR);
          uvs.push(u * 2.0, 0.58 + v * 0.38);
        }
      }
      const stride = p.radialSegments + 1;
      for (let y = 0; y < p.heightSegments; y++) {
        for (let s = 0; s < p.radialSegments; s++) {
          const a = y * stride + s, b = a + 1, c = (y + 1) * stride + s, d = c + 1;
          indices.push(a, b, d, a, d, c);
        }
      }
      return { positions, uvs, indices };
    }
  });

  // 4. Lightning Bolt
  ShapeRegistry.registerShape(CAT, 'lightning', {
    title: "Lightning Bolt (ライトニング・雷)",
    defaultName: "Lightning_01",
    defaultPattern: "metal",
    params: [
      { id: "length", label: "Length", min: 2.0, max: 12.0, step: 0.5, val: 6.0 },
      { id: "thickness", label: "Thickness", min: 0.05, max: 0.6, step: 0.02, val: 0.15 },
      { id: "jaggedness", label: "Noise", min: 0.1, max: 1.5, step: 0.1, val: 0.6 },
      { id: "segments", label: "Segs", min: 8, max: 32, step: 2, val: 16 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      let curX = 0, curZ = 0;
      for (let i = 0; i <= p.segments; i++) {
        const v = i / p.segments, py = (1.0 - v) * p.length;
        if (i > 0 && i < p.segments) {
          curX += (Math.random() - 0.5) * p.jaggedness;
          curZ += (Math.random() - 0.5) * p.jaggedness;
        }
        for (let s = 0; s <= 4; s++) {
          const u = s / 4, angle = u * Math.PI * 2;
          positions.push(curX + Math.cos(angle) * p.thickness, py, curZ + Math.sin(angle) * p.thickness);
          uvs.push(u, 0.85);
        }
      }
      for (let i = 0; i < p.segments; i++) {
        for (let s = 0; s < 4; s++) {
          const a = i * 5 + s, b = a + 1, c = (i + 1) * 5 + s, d = c + 1;
          indices.push(a, b, d, a, d, c);
        }
      }
      return { positions, uvs, indices };
    }
  });

  // 5. Magic Circle
  ShapeRegistry.registerShape(CAT, 'magic_circle', {
    title: "Magic Circle (マジックサークル)",
    defaultName: "MagicCircle_01",
    defaultPattern: "metal",
    params: [
      { id: "innerRadius", label: "Inner R", min: 0.2, max: 3.0, step: 0.1, val: 1.0 },
      { id: "outerRadius", label: "Outer R", min: 1.0, max: 6.0, step: 0.2, val: 3.5 },
      { id: "ringLayers", label: "Rings", min: 1, max: 6, step: 1, val: 3 },
      { id: "segments", label: "Segs", min: 12, max: 64, step: 2, val: 32 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let r = 0; r <= p.ringLayers; r++) {
        const vr = r / p.ringLayers, curRadius = p.innerRadius + (p.outerRadius - p.innerRadius) * vr;
        for (let s = 0; s <= p.segments; s++) {
          const u = s / p.segments, angle = u * Math.PI * 2;
          positions.push(Math.cos(angle) * curRadius, 0, Math.sin(angle) * curRadius);
          uvs.push(u * 2.0, 0.75);
        }
      }
      const stride = p.segments + 1;
      for (let r = 0; r < p.ringLayers; r++) {
        for (let s = 0; s < p.segments; s++) {
          const a = r * stride + s, b = a + 1, c = (r + 1) * stride + s, d = c + 1;
          indices.push(a, b, d, a, d, c);
        }
      }
      return { positions, uvs, indices };
    }
  });

  // 6. Audio Spectrum Visualizer
  ShapeRegistry.registerShape(CAT, 'audio_spectrum', {
    title: "Audio Spectrum (オーディオ波形)",
    defaultName: "Spectrum_01",
    defaultPattern: "metal",
    params: [
      { id: "bars", label: "Bars", min: 8, max: 48, step: 2, val: 24 },
      { id: "radius", label: "Radius", min: 1.0, max: 6.0, step: 0.2, val: 2.8 },
      { id: "barWidth", label: "Bar Width", min: 0.05, max: 0.5, step: 0.02, val: 0.18 },
      { id: "barMaxHeight", label: "Peak Amp", min: 0.5, max: 5.0, step: 0.2, val: 2.2 }
    ],
    generator: function(p) {
      const positions = [], uvs = [], indices = [];
      for (let i = 0; i < p.bars; i++) {
        const u = i / p.bars, angle = u * Math.PI * 2;
        const freqAmp = Math.abs(Math.sin(u * Math.PI * 4.0)) * p.barMaxHeight;
        const px = Math.cos(angle) * p.radius, pz = Math.sin(angle) * p.radius, bw = p.barWidth * 0.5, vOff = positions.length / 3;
        positions.push(px - bw, 0, pz - bw); uvs.push(0, 0.25);
        positions.push(px + bw, 0, pz + bw); uvs.push(1, 0.25);
        positions.push(px - bw, freqAmp, pz - bw); uvs.push(0, 0.85);
        positions.push(px + bw, freqAmp, pz + bw); uvs.push(1, 0.85);
        indices.push(vOff, vOff + 1, vOff + 3, vOff, vOff + 3, vOff + 2);
      }
      return { positions, uvs, indices };
    }
  });
})();
