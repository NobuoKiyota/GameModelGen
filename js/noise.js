// =============================================================
// Math & Noise Functions
// =============================================================
window.MeshNoise = {
  fbm3D: function(x, y, z, octaves = 3, lacunarity = 2.0, gain = 0.5, seed = 0) {
    let total = 0, amp = 1.0, freq = 1.0, maxAmp = 0;
    for (let i = 0; i < octaves; i++) {
      const s = seed + i * 17.13;
      const n = Math.sin((x * freq + s) * 1.5) * Math.cos((y * freq + s * 1.2) * 1.5) * Math.sin((z * freq + s * 0.7) * 1.5) +
                Math.cos((x * freq * 0.7 - y * freq * 0.5 + s) * 2.0) * 0.5;
      total += n * amp;
      maxAmp += amp;
      amp *= gain;
      freq *= lacunarity;
    }
    return total / maxAmp;
  },

  hexToRgb: function(hex) {
    const bigint = parseInt(hex.replace('#', ''), 16);
    return { r: (bigint >> 16) & 255, g: (bigint >> 8) & 255, b: bigint & 255 };
  },

  rgbToHex: function(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  }
};
