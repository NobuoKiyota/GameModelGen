import * as THREE from 'three';

export const JewelryShader = {
  uniforms: {
    uTexture: { value: null as THREE.Texture | null },
    uHasTexture: { value: 0.0 },
    uHeightMap: { value: null as THREE.Texture | null },
    uHasHeightMap: { value: 0.0 },
    uDisplacementScale: { value: 0.35 },
    uAnchor: { value: new THREE.Vector2(0.5, 0.5) },
    uCoverage: { value: 1.0 },
    uAspectRatio: { value: 1.0 },
    uRimType: { value: 0 },
    uCustomRimColor: { value: new THREE.Color('#d4af37') },
    uLightDir: { value: new THREE.Vector3(0.5, 0.8, 1.0).normalize() },
    uLightColor: { value: new THREE.Color('#ffffff') },
    uAmbientColor: { value: new THREE.Color('#2a2d3d') },
    uRoughness: { value: 0.15 },
    uMetalness: { value: 0.2 },
    uClearcoat: { value: 0.8 },
    uBrightness: { value: 0.0 },
    uContrast: { value: 1.0 },
    uSaturation: { value: 1.0 },
    uHue: { value: 0.0 },
  },

  vertexShader: `
    attribute vec3 aUnitPos; // Undeformed unit sphere coordinate

    varying vec3 vNormal;
    varying vec3 vPosition;
    varying vec3 vViewPosition;
    varying vec2 vUv;
    varying vec2 vProjectedUv;
    varying float vCoverageMask;
    varying float vHeightValue;

    uniform sampler2D uHeightMap;
    uniform float uHasHeightMap;
    uniform float uDisplacementScale;
    uniform vec2 uAnchor;
    uniform float uCoverage;
    uniform float uAspectRatio;

    const float PI = 3.141592653589793;

    void main() {
      vUv = uv;

      // Use undeformed unit sphere coordinate to calculate polar UV mapping
      vec3 uPos = aUnitPos;
      if (length(uPos) < 0.001) {
        uPos = normalize(position);
      }

      // Angular distance from top apex (0, 0, 1)
      float cosTheta = clamp(uPos.z, -1.0, 1.0);
      float theta = acos(cosTheta); // 0 (apex) to PI (bottom pole)

      // Azimuth angle in XY plane
      float phi = atan(uPos.y, uPos.x);

      // Map theta to radius based on coverage (coverage = 1.0 maps hemisphere theta <= PI/2 to radius <= 0.5)
      float r = (theta / (PI * 0.5)) * 0.5 / max(0.01, uCoverage);

      float uOffset = r * cos(phi);
      float vOffset = -r * sin(phi);

      // Aspect ratio correction
      if (uAspectRatio > 1.0) {
        vOffset *= uAspectRatio;
      } else if (uAspectRatio < 1.0) {
        uOffset /= uAspectRatio;
      }

      vProjectedUv = uAnchor + vec2(uOffset, vOffset);

      // Coverage mask: 1.0 inside front dome, smooth transition near boundary
      // If coverage is 1.0, covers full front hemisphere (theta <= PI*0.5)
      float maxTheta = (PI * 0.5) * uCoverage;
      vCoverageMask = smoothstep(maxTheta, maxTheta * 0.85, theta);

      // Displacement
      float h = 0.0;
      bool inBounds = vProjectedUv.x >= 0.0 && vProjectedUv.x <= 1.0 &&
                      vProjectedUv.y >= 0.0 && vProjectedUv.y <= 1.0;

      if (uHasHeightMap > 0.5 && inBounds) {
        float rawH = texture2D(uHeightMap, vProjectedUv).r;
        h = (rawH - 0.5) * 2.0; // [-1.0, 1.0]
      }

      h *= vCoverageMask * uDisplacementScale;
      vHeightValue = h;

      vec3 displacedPosition = position + normal * h;
      vPosition = displacedPosition;

      vNormal = normalize(normalMatrix * normal);
      vec4 mvPosition = modelViewMatrix * vec4(displacedPosition, 1.0);
      vViewPosition = -mvPosition.xyz;
      gl_Position = projectionMatrix * mvPosition;
    }
  `,

  fragmentShader: `
    varying vec3 vNormal;
    varying vec3 vPosition;
    varying vec3 vViewPosition;
    varying vec2 vUv;
    varying vec2 vProjectedUv;
    varying float vCoverageMask;
    varying float vHeightValue;

    uniform sampler2D uTexture;
    uniform float uHasTexture;
    uniform sampler2D uHeightMap;
    uniform float uHasHeightMap;
    uniform float uDisplacementScale;
    uniform int uRimType;
    uniform vec3 uCustomRimColor;
    uniform vec3 uLightDir;
    uniform vec3 uLightColor;
    uniform vec3 uAmbientColor;
    uniform float uRoughness;
    uniform float uMetalness;
    uniform float uClearcoat;
    uniform float uBrightness;
    uniform float uContrast;
    uniform float uSaturation;
    uniform float uHue;

    vec3 getRimColor(int rimType) {
      if (rimType == 0) return vec3(0.92, 0.76, 0.32); // 18K Gold
      if (rimType == 1) return vec3(0.88, 0.90, 0.94); // Platinum / Silver
      if (rimType == 2) return vec3(0.94, 0.68, 0.60); // Rose Gold
      if (rimType == 3) return vec3(0.15, 0.16, 0.19); // Gunmetal Black
      return uCustomRimColor;
    }

    vec3 rgb2hsv(vec3 c) {
      vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
      vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
      vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
      float d = q.x - min(q.w, q.y);
      float e = 1.0e-10;
      return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
    }

    vec3 hsv2rgb(vec3 c) {
      vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
      vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
      return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
    }

    vec3 applyColorGrading(vec3 color) {
      color = (color - 0.5) * uContrast + 0.5 + uBrightness;
      vec3 hsv = rgb2hsv(max(vec3(0.0), color));
      hsv.x = fract(hsv.x + uHue / 360.0);
      hsv.y = clamp(hsv.y * uSaturation, 0.0, 1.0);
      return clamp(hsv2rgb(hsv), 0.0, 1.0);
    }

    void main() {
      vec3 N = normalize(vNormal);

      // Normal perturbation based on heightmap gradient
      if (uHasHeightMap > 0.5 && uDisplacementScale > 0.001) {
        vec2 texelSize = vec2(1.0 / 512.0);
        float hL = texture2D(uHeightMap, vProjectedUv - vec2(texelSize.x, 0.0)).r;
        float hR = texture2D(uHeightMap, vProjectedUv + vec2(texelSize.x, 0.0)).r;
        float hD = texture2D(uHeightMap, vProjectedUv - vec2(0.0, texelSize.y)).r;
        float hU = texture2D(uHeightMap, vProjectedUv + vec2(0.0, texelSize.y)).r;

        vec3 bumpNormal = normalize(vec3((hL - hR) * uDisplacementScale * 4.0, (hD - hU) * uDisplacementScale * 4.0, 1.0));
        N = normalize(mix(N, bumpNormal, vCoverageMask * 0.75));
      }

      vec3 V = normalize(vViewPosition);
      vec3 L = normalize(uLightDir);
      vec3 H = normalize(L + V);

      float NdotL = max(dot(N, L), 0.0);
      float NdotH = max(dot(N, H), 0.0);
      float NdotV = max(dot(N, V), 0.0);

      float shininess = mix(128.0, 4.0, uRoughness);
      float spec = pow(NdotH, shininess) * (1.0 - uRoughness * 0.7);
      float fresnel = pow(1.0 - NdotV, 3.0);
      float clearcoatSpec = pow(NdotH, 128.0) * uClearcoat * 1.5;

      vec4 rawTex = vec4(0.5, 0.5, 0.5, 1.0);
      bool inBounds = vProjectedUv.x >= 0.0 && vProjectedUv.x <= 1.0 &&
                      vProjectedUv.y >= 0.0 && vProjectedUv.y <= 1.0;

      if (uHasTexture > 0.5 && inBounds) {
        rawTex = texture2D(uTexture, vProjectedUv);
      } else {
        rawTex = vec4(getRimColor(uRimType), 1.0);
      }

      vec3 gradedColor = applyColorGrading(rawTex.rgb);
      vec3 rimColor = getRimColor(uRimType);

      float blendFactor = inBounds ? vCoverageMask : 0.0;
      vec3 baseAlbedo = mix(rimColor, gradedColor, blendFactor);

      vec3 diffuse = baseAlbedo * (uAmbientColor + uLightColor * NdotL);
      vec3 specularColor = mix(vec3(0.04), baseAlbedo, uMetalness);
      vec3 specular = uLightColor * (spec * specularColor + clearcoatSpec * vec3(1.0));
      vec3 rimGlow = mix(rimColor, vec3(1.0), 0.5) * fresnel * (0.3 + uClearcoat * 0.3);

      vec3 finalColor = diffuse + specular + rimGlow;
      gl_FragColor = vec4(finalColor, 1.0);
    }
  `
};