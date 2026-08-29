// Color conversion utilities: RGB <-> CIELAB <-> HEX

export function rgbToHex(r: number, g: number, b: number): string {
  const toHex = (n: number) => {
    const hex = Math.max(0, Math.min(255, Math.round(n))).toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  };
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

export function hexToRgb(hex: string): [number, number, number] {
  let cleaned = hex.replace('#', '');
  if (cleaned.length === 3) {
    cleaned = cleaned.split('').map(c => c + c).join('');
  }
  const num = parseInt(cleaned, 16);
  return [(num >> 16) & 255, (num >> 8) & 255, num & 255];
}

// RGB [0..255] -> XYZ -> CIELAB
export function rgbToLab(r: number, g: number, b: number): [number, number, number] {
  let r1 = r / 255;
  let g1 = g / 255;
  let b1 = b / 255;

  r1 = r1 > 0.04045 ? Math.pow((r1 + 0.055) / 1.055, 2.4) : r1 / 12.92;
  g1 = g1 > 0.04045 ? Math.pow((g1 + 0.055) / 1.055, 2.4) : g1 / 12.92;
  b1 = b1 > 0.04045 ? Math.pow((b1 + 0.055) / 1.055, 2.4) : b1 / 12.92;

  let x = (r1 * 0.4124 + g1 * 0.3576 + b1 * 0.1805) / 0.95047;
  let y = (r1 * 0.2126 + g1 * 0.7152 + b1 * 0.0722) / 1.00000;
  let z = (r1 * 0.0193 + g1 * 0.1192 + b1 * 0.9505) / 1.08883;

  x = x > 0.008856 ? Math.pow(x, 1 / 3) : 7.787 * x + 16 / 116;
  y = y > 0.008856 ? Math.pow(y, 1 / 3) : 7.787 * y + 16 / 116;
  z = z > 0.008856 ? Math.pow(z, 1 / 3) : 7.787 * z + 16 / 116;

  const L = 116 * y - 16;
  const a = 500 * (x - y);
  const bLab = 200 * (y - z);
  return [L, a, bLab];
}

// CIELAB Delta E (Euclidean distance in Lab space)
export function labDistance(lab1: [number, number, number], lab2: [number, number, number]): number {
  const dL = lab1[0] - lab2[0];
  const da = lab1[1] - lab2[1];
  const db = lab1[2] - lab2[2];
  return Math.sqrt(dL * dL + da * da + db * db);
}