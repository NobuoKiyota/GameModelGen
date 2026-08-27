import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { useJewelryStore } from '../store/useJewelryStore';
import { buildEllipsoidGeometry } from '../utils/geometryBuilder';
import { buildAnatomyGeometry } from '../utils/anatomyGeometryBuilder';
import { JewelryShader } from '../shaders/jewelryShader';
import { AnatomyShader } from '../shaders/anatomyShader';
import { RotateCcw, Play, Pause, Box, Mountain, Pipette } from 'lucide-react';

export const Viewport3D: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const {
    studioMode,
    image,
    anchor,
    modelSettings,
    updateModelSettings,
    anatomySettings,
    updateAnatomySettings,
    heightMapTexture,
    selectClusterAtUv,
    selectedClusterId,
  } = useJewelryStore();

  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const meshRef = useRef<THREE.Mesh | null>(null);
  const materialRef = useRef<THREE.ShaderMaterial | null>(null);
  const textureRef = useRef<THREE.Texture | null>(null);

  const pointerDownPosRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#0d0f16');
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(
      45,
      container.clientWidth / container.clientHeight,
      0.1,
      100
    );
    camera.position.set(0, 0, 3.2);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxDistance = 10;
    controls.minDistance = 0.8;
    controlsRef.current = controls;

    // Studio 3-Point Lighting
    const keyLight = new THREE.DirectionalLight(0xfff8ee, 1.5);
    keyLight.position.set(2.5, 3.5, 4);
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x8fa8ff, 0.7);
    fillLight.position.set(-3.5, -1, 2.5);
    scene.add(fillLight);

    const rimLight = new THREE.DirectionalLight(0xffffff, 1.0);
    rimLight.position.set(0, -3.5, -3);
    scene.add(rimLight);

    const ambientLight = new THREE.AmbientLight(0x282c3c, 0.9);
    scene.add(ambientLight);

    const shaderDef = studioMode === 'anatomy' ? AnatomyShader : JewelryShader;
    const uniforms = THREE.UniformsUtils.clone(shaderDef.uniforms);
    const material = new THREE.ShaderMaterial({
      uniforms,
      vertexShader: shaderDef.vertexShader,
      fragmentShader: shaderDef.fragmentShader,
      side: THREE.DoubleSide,
    });
    materialRef.current = material;

    const geom = studioMode === 'anatomy'
      ? buildAnatomyGeometry(anatomySettings)
      : buildEllipsoidGeometry(modelSettings);
    const mesh = new THREE.Mesh(geom, material);
    scene.add(mesh);
    meshRef.current = mesh;

    let animationFrameId: number;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      controls.update();
      const isRotate = studioMode === 'anatomy'
        ? useJewelryStore.getState().anatomySettings.autoRotate
        : useJewelryStore.getState().modelSettings.autoRotate;
      if (meshRef.current && isRotate) {
        meshRef.current.rotation.z += 0.005;
      }
      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!container || !camera || !renderer) return;
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    };
    const resizeObserver = new ResizeObserver(handleResize);
    resizeObserver.observe(container);

    return () => {
      cancelAnimationFrame(animationFrameId);
      resizeObserver.disconnect();
      controls.dispose();
      renderer.dispose();
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, [studioMode]);

  // 3D Eye-Dropper Raycast Click
  const handlePointerDown = (e: React.PointerEvent) => {
    pointerDownPosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handlePointerUp = (e: React.PointerEvent) => {
    const dx = Math.abs(e.clientX - pointerDownPosRef.current.x);
    const dy = Math.abs(e.clientY - pointerDownPosRef.current.y);
    if (dx > 5 || dy > 5) return;
    if (!containerRef.current || !cameraRef.current || !meshRef.current || !image) return;

    const rect = containerRef.current.getBoundingClientRect();
    const mouse = new THREE.Vector2(
      ((e.clientX - rect.left) / rect.width) * 2 - 1,
      -((e.clientY - rect.top) / rect.height) * 2 + 1
    );

    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(mouse, cameraRef.current);
    const intersects = raycaster.intersectObject(meshRef.current);

    if (intersects.length > 0) {
      const hit = intersects[0];
      const localPoint = hit.point.clone();
      meshRef.current.worldToLocal(localPoint);

      if (studioMode === 'anatomy') {
        const uX = anatomySettings.symmetry ? Math.abs(localPoint.x) : localPoint.x;
        const scaleFactor = 0.5 / Math.max(0.01, anatomySettings.coverage);
        let uOffset = uX * scaleFactor;
        let vOffset = -localPoint.y * scaleFactor;
        const aspect = image.width / image.height;
        if (aspect > 1.0) vOffset *= aspect;
        else if (aspect < 1.0) uOffset /= aspect;
        selectClusterAtUv(anchor.u + uOffset, anchor.v + vOffset);
      } else {
        const uX = localPoint.x / Math.max(0.01, modelSettings.scaleX);
        const uY = localPoint.y / Math.max(0.01, modelSettings.scaleY);
        const uZ = localPoint.z / Math.max(0.01, modelSettings.scaleZ);
        const unitDir = new THREE.Vector3(uX, uY, uZ).normalize();

        const cosTheta = THREE.MathUtils.clamp(unitDir.z, -1.0, 1.0);
        const theta = Math.acos(cosTheta);
        const phi = Math.atan2(unitDir.y, unitDir.x);

        const r = (theta / (Math.PI * 0.5)) * 0.5 / Math.max(0.01, modelSettings.coverage);
        let uOffset = r * Math.cos(phi);
        let vOffset = -r * Math.sin(phi);

        const aspect = image.width / image.height;
        if (aspect > 1.0) vOffset *= aspect;
        else if (aspect < 1.0) uOffset /= aspect;

        selectClusterAtUv(anchor.u + uOffset, anchor.v + vOffset);
      }
    }
  };

  // Geometry updates
  useEffect(() => {
    if (!meshRef.current) return;
    const newGeom = studioMode === 'anatomy'
      ? buildAnatomyGeometry(anatomySettings)
      : buildEllipsoidGeometry(modelSettings);
    meshRef.current.geometry.dispose();
    meshRef.current.geometry = newGeom;
  }, [
    studioMode,
    modelSettings.scaleX,
    modelSettings.scaleY,
    modelSettings.scaleZ,
    modelSettings.cutoff,
    modelSettings.segments,
    anatomySettings.partType,
    anatomySettings.bridgeHeight,
    anatomySettings.alaWidth,
    anatomySettings.curvature,
    anatomySettings.segments,
  ]);

  useEffect(() => {
    if (!materialRef.current) return;
    if (image) {
      const loader = new THREE.TextureLoader();
      loader.load(image.url, (tex) => {
        tex.colorSpace = THREE.SRGBColorSpace;
        tex.wrapS = THREE.ClampToEdgeWrapping;
        tex.wrapT = THREE.ClampToEdgeWrapping;
        tex.minFilter = THREE.LinearMipmapLinearFilter;
        tex.magFilter = THREE.LinearFilter;
        textureRef.current = tex;

        if (materialRef.current) {
          materialRef.current.uniforms.uTexture.value = tex;
          materialRef.current.uniforms.uHasTexture.value = 1.0;
          materialRef.current.uniforms.uAspectRatio.value = image.width / image.height;
          materialRef.current.needsUpdate = true;
        }
      });
    } else {
      materialRef.current.uniforms.uHasTexture.value = 0.0;
    }
  }, [image, studioMode]);

  useEffect(() => {
    if (!materialRef.current) return;
    const isDisplace = studioMode === 'anatomy' ? anatomySettings.displacementEnabled : modelSettings.displacementEnabled;
    const dispScale = studioMode === 'anatomy' ? anatomySettings.displacementScale : modelSettings.displacementScale;

    if (heightMapTexture && isDisplace) {
      materialRef.current.uniforms.uHeightMap.value = heightMapTexture;
      materialRef.current.uniforms.uHasHeightMap.value = 1.0;
      materialRef.current.uniforms.uDisplacementScale.value = dispScale;
    } else {
      materialRef.current.uniforms.uHasHeightMap.value = 0.0;
      materialRef.current.uniforms.uDisplacementScale.value = 0.0;
    }
    materialRef.current.needsUpdate = true;
  }, [
    heightMapTexture,
    studioMode,
    modelSettings.displacementEnabled,
    modelSettings.displacementScale,
    anatomySettings.displacementEnabled,
    anatomySettings.displacementScale,
  ]);

  useEffect(() => {
    if (!materialRef.current) return;
    const u = materialRef.current.uniforms;
    u.uAnchor.value.set(anchor.u, anchor.v);

    if (studioMode === 'anatomy') {
      u.uCoverage.value = anatomySettings.coverage;
      u.uSkinBaseColor.value.set(anatomySettings.skinColor);
      u.uSubsurfaceIntensity.value = anatomySettings.subsurfaceScattering;
      u.uSkinRoughness.value = anatomySettings.skinRoughness;
      u.uPoreBump.value = anatomySettings.poreBumpIntensity;
      u.uSymmetry.value = anatomySettings.symmetry ? 1.0 : 0.0;
      materialRef.current.wireframe = anatomySettings.wireframe;
    } else {
      u.uCoverage.value = modelSettings.coverage;
      const rimMap = { gold: 0, silver: 1, rosegold: 2, black: 3, custom: 4 };
      u.uRimType.value = rimMap[modelSettings.rimMaterial] ?? 0;
      u.uCustomRimColor.value.set(modelSettings.customRimColor);
      materialRef.current.wireframe = modelSettings.wireframe;
      u.uRoughness.value = modelSettings.roughness;
      u.uMetalness.value = modelSettings.metalness;
      u.uClearcoat.value = modelSettings.clearcoat;
      const cg = modelSettings.colorGrading;
      u.uBrightness.value = cg.brightness;
      u.uContrast.value = cg.contrast;
      u.uSaturation.value = cg.saturation;
      u.uHue.value = cg.hue;
    }
  }, [
    studioMode,
    anchor,
    modelSettings,
    anatomySettings,
  ]);

  const resetCamera = () => {
    if (!cameraRef.current || !controlsRef.current) return;
    cameraRef.current.position.set(0, 0, 3.2);
    cameraRef.current.lookAt(0, 0, 0);
    controlsRef.current.target.set(0, 0, 0);
    controlsRef.current.update();
    if (meshRef.current) {
      meshRef.current.rotation.set(0, 0, 0);
    }
  };

  const setViewAngle = (view: 'front' | 'side' | 'top' | 'isometric') => {
    if (!cameraRef.current || !controlsRef.current) return;
    if (view === 'front') cameraRef.current.position.set(0, 0, 3.2);
    if (view === 'side') cameraRef.current.position.set(3.2, 0, 0);
    if (view === 'top') cameraRef.current.position.set(0, 3.2, 0);
    if (view === 'isometric') cameraRef.current.position.set(2.2, 2.0, 2.2);
    cameraRef.current.lookAt(0, 0, 0);
    controlsRef.current.target.set(0, 0, 0);
    controlsRef.current.update();
  };

  const isDisplace = studioMode === 'anatomy' ? anatomySettings.displacementEnabled : modelSettings.displacementEnabled;
  const isRotate = studioMode === 'anatomy' ? anatomySettings.autoRotate : modelSettings.autoRotate;
  const isWire = studioMode === 'anatomy' ? anatomySettings.wireframe : modelSettings.wireframe;

  const toggleDisplace = () => {
    if (studioMode === 'anatomy') {
      updateAnatomySettings({ displacementEnabled: !anatomySettings.displacementEnabled });
    } else {
      updateModelSettings({ displacementEnabled: !modelSettings.displacementEnabled });
    }
  };

  const toggleRotate = () => {
    if (studioMode === 'anatomy') {
      updateAnatomySettings({ autoRotate: !anatomySettings.autoRotate });
    } else {
      updateModelSettings({ autoRotate: !modelSettings.autoRotate });
    }
  };

  const toggleWire = () => {
    if (studioMode === 'anatomy') {
      updateAnatomySettings({ wireframe: !anatomySettings.wireframe });
    } else {
      updateModelSettings({ wireframe: !modelSettings.wireframe });
    }
  };

  return (
    <div
      className="relative w-full h-full bg-[#0d0f16] overflow-hidden select-none"
      onPointerDown={handlePointerDown}
      onPointerUp={handlePointerUp}
    >
      <div ref={containerRef} className="w-full h-full cursor-crosshair active:cursor-grabbing" />

      {/* Top HUD Controls */}
      <div className="absolute top-4 left-4 z-20 flex items-center gap-1.5 bg-darkPanel/85 border border-darkBorder backdrop-blur-md px-2.5 py-1.5 rounded-lg shadow-xl text-xs text-gray-300">
        <button
          onClick={() => setViewAngle('front')}
          className="px-2 py-0.5 rounded hover:bg-darkBorder text-[11px] font-medium text-gray-300 hover:text-white transition-colors cursor-pointer"
        >
          正面
        </button>
        <button
          onClick={() => setViewAngle('isometric')}
          className="px-2 py-0.5 rounded hover:bg-darkBorder text-[11px] font-medium text-gray-300 hover:text-white transition-colors cursor-pointer"
        >
          斜め
        </button>
        <button
          onClick={() => setViewAngle('side')}
          className="px-2 py-0.5 rounded hover:bg-darkBorder text-[11px] font-medium text-gray-300 hover:text-white transition-colors cursor-pointer"
        >
          側面
        </button>
        <div className="h-3 w-px bg-darkBorder mx-1" />
        <button
          onClick={resetCamera}
          className="p-1 hover:bg-darkBorder rounded text-gray-300 hover:text-white transition-colors cursor-pointer"
          title="視点を正面にリセット"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Top-Right HUD Controls */}
      <div className="absolute top-4 right-4 z-20 flex items-center gap-2 bg-darkPanel/85 border border-darkBorder backdrop-blur-md px-3 py-1.5 rounded-lg shadow-xl text-xs">
        <button
          onClick={toggleDisplace}
          className={`flex items-center gap-1.5 px-2 py-1 rounded text-[11px] font-medium transition-colors cursor-pointer ${
            isDisplace
              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
              : 'bg-darkCard text-gray-400 border border-darkBorder hover:text-gray-200'
          }`}
          title="段差凹凸ディスプレイスメントのON/OFF"
        >
          <Mountain className="w-3.5 h-3.5" />
          凹凸変形
        </button>

        <button
          onClick={toggleRotate}
          className={`flex items-center gap-1.5 px-2 py-1 rounded text-[11px] font-medium transition-colors cursor-pointer ${
            isRotate
              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
              : 'bg-darkCard text-gray-400 border border-darkBorder hover:text-gray-200'
          }`}
          title="モデルの自動回転"
        >
          {isRotate ? <Pause className="w-3 h-3 text-amber-400" /> : <Play className="w-3 h-3" />}
          自動回転
        </button>

        <button
          onClick={toggleWire}
          className={`flex items-center gap-1.5 px-2 py-1 rounded text-[11px] font-medium transition-colors cursor-pointer ${
            isWire
              ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
              : 'bg-darkCard text-gray-400 border border-darkBorder hover:text-gray-200'
          }`}
          title="ワイヤーフレーム表示の切り替え"
        >
          <Box className="w-3.5 h-3.5" />
          枠線
        </button>
      </div>

      {/* Bottom Info Bar */}
      <div className="absolute bottom-4 left-4 z-20 flex items-center gap-2 bg-darkPanel/85 border border-darkBorder backdrop-blur-md px-3 py-1.5 rounded-lg shadow-md text-[11px] text-gray-400 font-mono">
        {selectedClusterId !== null ? (
          <span className="text-amber-300 font-bold flex items-center gap-1.5 animate-pulse">
            <Pipette className="w-3.5 h-3.5 text-amber-400" />
            グループ #{selectedClusterId + 1} 選択中
          </span>
        ) : (
          <span className="text-gray-300 flex items-center gap-1.5">
            <Pipette className="w-3.5 h-3.5 text-indigo-400" />
            3D画面クリックで該当カラー層へジャンプ
          </span>
        )}
        <span className="text-gray-600">|</span>
        <span>モード: {studioMode.toUpperCase()}</span>
      </div>
    </div>
  );
};