import * as THREE from 'three';

export const AnatomyShader = {
  uniforms: {
    uTexture: { value: null as THREE.Texture | null },
    uHasTexture: { value: 0.0 },
    uHeightMap: { value: null as THREE.Texture | null },
    uHasHeightMap: { value: 0.0 },
    uDisplacementScale: { value: 0.35 },
    uAnchor: { value: new THREE.Vector2(0.5, 0.5) },
    uCoverage: { value: 1.0 },
    uAspectRatio: { value: 1.0 },
    uSkinBaseColor: { value: new THREE.Color('#f5d0b5') },
    uSubsurfaceColor: { value: new THREE.Color('#ff4d4d') }, // Blood red scatter
    uSubsurfaceIntensity: { value: 0.45 },
    uSkinRoughness: { value: 0.38 },
    uPoreBump: { value: 0.3 },
    uSymmetry: { value: 0.0 }, // 1.0 for mirror symmetry
    uLightDir: { value: new THREE.Vector3(0.5, 0.8, 1.0).normalize() },
    uLightColor: { value: new THREE.Color('#ffffff') },
    uAmbientColor: { value: new THREE.Color('#382824') },
  },

  vertexShader: `
    attribute vec3 aUnitPos;
    varying vec3 vNormal;
    varying vec3 vPosition;
    varying vec3 vViewPosition;
    varying vec2 vUv;
    varying vec2 vProjectedUv;
    varying float vHeightValue;

    uniform sampler2D uHeightMap;
    uniform float uHasHeightMap;
    uniform float uDisplacementScale;
    uniform vec2 uAnchor;
    uniform float uCoverage;
    uniform float uAspectRatio;
    uniform float uSymmetry;

    void main() {
      vUv = uv;

      vec3 uPos = aUnitPos;
      float uX = uPos.x;
      if (uSymmetry > 0.5) {
        uX = abs(uX); // Mirror X coordinate
      }

      float scaleFactor = 0.5 / max(0.01, uCoverage);
      float uOffset = uX * scaleFactor;
      float vOffset = -uPos.y * scaleFactor;

      if (uAspectRatio > 1.0) vOffset *= uAspectRatio;
      else if (uAspectRatio < 1.0) uOffset /= uAspectRatio;

      vProjectedUv = uAnchor + vec2(uOffset, vOffset);

      float h = 0.0;
      bool inBounds = vProjectedUv.x >= 0.0 && vProjectedUv.x <= 1.0 &&
                      vProjectedUv.y >= 0.0 && vProjectedUv.y <= 1.0;

      if (uHasHeightMap > 0.5 && inBounds) {
        float rawH = texture2D(uHeightMap, vProjectedUv).r;
        h = (rawH - 0.5) * 2.0;
      }

      h *= uDisplacementScale;
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
    varying float vHeightValue;

    uniform sampler2D uTexture;
    uniform float uHasTexture;
    uniform sampler2D uHeightMap;
    uniform float uHasHeightMap;
    uniform float uDisplacementScale;
    uniform vec3 uSkinBaseColor;
    uniform vec3 uSubsurfaceColor;
    uniform float uSubsurfaceIntensity;
    uniform float uSkinRoughness;
    uniform float uPoreBump;
    uniform vec3 uLightDir;
    uniform vec3 uLightColor;
    uniform vec3 uAmbientColor;

    // Procedural skin pore micro-noise
    float hash(vec2 p) {
      p = fract(p * vec2(123.34, 456.21));
      p += dot(p, p + 45.32);
      return fract(p.x * p.y);
    }

    void main() {
      vec3 N = normalize(vNormal);

      // Micro skin pore bump perturbation
      if (uPoreBump > 0.01) {
        float pore = (hash(vUv * 300.0) - 0.5) * uPoreBump * 0.15;
        N = normalize(N + vec3(pore, pore, 0.0));
      }

      vec3 V = normalize(vViewPosition);
      vec3 L = normalize(uLightDir);
      vec3 H = normalize(L + V);

      float NdotL = dot(N, L);
      float NdotV = max(dot(N, V), 0.0);
      float NdotH = max(dot(N, H), 0.0);

      // SSS Wrap Lighting (Subsurface Scattering approximation)
      float wrap = 0.4;
      float sssDiffuse = max(0.0, (NdotL + wrap) / (1.0 + wrap));

      // Backlight scattering for thin cartilage (nose/ear)
      float sssBack = pow(clamp(dot(-V, L), 0.0, 1.0), 3.0) * uSubsurfaceIntensity;

      // Skin Dual-Lobe Specular (Oily sheen + soft skin highlight)
      float spec1 = pow(NdotH, 64.0) * (1.0 - uSkinRoughness) * 0.8;
      float spec2 = pow(NdotH, 16.0) * 0.15;
      float fresnel = pow(1.0 - NdotV, 4.0) * 0.25;

      vec4 rawTex = vec4(uSkinBaseColor, 1.0);
      bool inBounds = vProjectedUv.x >= 0.0 && vProjectedUv.x <= 1.0 &&
                      vProjectedUv.y >= 0.0 && vProjectedUv.y <= 1.0;

      if (uHasTexture > 0.5 && inBounds) {
        rawTex = texture2D(uTexture, vProjectedUv);
      }

      vec3 albedo = rawTex.rgb;
      vec3 sssColor = mix(albedo, uSubsurfaceColor, uSubsurfaceIntensity * 0.6);

      vec3 diffuse = mix(albedo * max(NdotL, 0.0), sssColor * sssDiffuse, uSubsurfaceIntensity);
      vec3 ambient = albedo * uAmbientColor;
      vec3 specular = uLightColor * (spec1 + spec2 + fresnel);
      vec3 backscatter = uSubsurfaceColor * sssBack;

      vec3 finalColor = diffuse + ambient + specular + backscatter;
      gl_FragColor = vec4(finalColor, 1.0);
    }
  `
};