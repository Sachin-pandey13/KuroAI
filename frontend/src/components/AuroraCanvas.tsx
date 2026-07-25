import { useRef, useEffect } from 'react';
import * as THREE from 'three';

const vertexShader = /* glsl */`
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const fragmentShader = /* glsl */`
  varying vec2 vUv;
  uniform float uTime;
  uniform vec2 uResolution;

  // Hash / noise
  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
  }

  float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(
      mix(hash(i + vec2(0,0)), hash(i + vec2(1,0)), u.x),
      mix(hash(i + vec2(0,1)), hash(i + vec2(1,1)), u.x),
      u.y
    );
  }

  float fbm(vec2 p) {
    float v = 0.0;
    float a = 0.5;
    vec2 shift = vec2(100.0);
    mat2 rot = mat2(cos(0.5), sin(0.5), -sin(0.5), cos(0.5));
    for (int i = 0; i < 5; i++) {
      v += a * noise(p);
      p = rot * p * 2.0 + shift;
      a *= 0.5;
    }
    return v;
  }

  void main() {
    vec2 uv = vUv;
    float t = uTime * 0.12;

    // Warped coordinates for aurora bands
    vec2 q = vec2(fbm(uv + t * 0.3), fbm(uv + vec2(1.0)));
    vec2 r = vec2(
      fbm(uv + 1.0 * q + vec2(1.7, 9.2) + 0.15 * t),
      fbm(uv + 1.0 * q + vec2(8.3, 2.8) + 0.126 * t)
    );

    float f = fbm(uv + r);

    // Aurora vertical bands — sweep across upper portion
    float bandY = uv.y;
    float auroraMask = smoothstep(0.55, 0.95, bandY) * smoothstep(1.0, 0.7, bandY);
    auroraMask += smoothstep(0.35, 0.65, bandY) * 0.4;
    auroraMask = clamp(auroraMask, 0.0, 1.0);

    // Animated horizontal shimmer
    float shimmer = sin(uv.x * 6.0 + t * 2.0) * 0.5 + 0.5;
    shimmer *= sin(uv.x * 13.0 - t * 1.5) * 0.3 + 0.7;
    shimmer = pow(shimmer, 1.5);

    // Color palette: deep purple → pink → magenta
    vec3 col1 = vec3(0.24, 0.04, 0.55); // deep purple
    vec3 col2 = vec3(0.55, 0.08, 0.60); // violet-magenta
    vec3 col3 = vec3(0.90, 0.05, 0.50); // pink-magenta
    vec3 col4 = vec3(1.00, 0.35, 0.80); // bright pink

    vec3 aurora = mix(col1, col2, clamp(f * 2.0, 0.0, 1.0));
    aurora = mix(aurora, col3, clamp(f * f * 4.0, 0.0, 1.0));
    aurora = mix(aurora, col4, clamp(pow(f, 5.0) * 6.0, 0.0, 1.0));
    aurora *= shimmer;

    // Subtle second aurora layer (teal-ish violet for depth)
    vec2 q2 = vec2(fbm(uv * 1.5 + t * 0.2 + 3.0), fbm(uv * 1.5 + vec2(5.2, 1.3)));
    float f2 = fbm(uv * 1.2 + q2 * 0.8);
    float band2 = smoothstep(0.40, 0.70, bandY) * smoothstep(0.85, 0.50, bandY) * 0.5;
    vec3 layer2 = vec3(0.18, 0.05, 0.65) * f2 * band2;

    // Combine on pure black
    vec3 finalColor = vec3(0.0);
    finalColor += aurora * auroraMask * 0.55;
    finalColor += layer2 * 0.35;

    // Very subtle base glow (keeps it from being totally flat at bottom)
    float baseGlow = smoothstep(1.0, 0.0, bandY) * 0.04;
    finalColor += vec3(0.12, 0.02, 0.22) * baseGlow;

    // Ensure black base
    finalColor = clamp(finalColor, 0.0, 1.0);

    gl_FragColor = vec4(finalColor, 1.0);
  }
`;

const AuroraCanvas = () => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const w = window.innerWidth;
    const h = window.innerHeight;

    const renderer = new THREE.WebGLRenderer({ antialias: false, alpha: false });
    renderer.setSize(w, h);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    mountRef.current.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

    const geometry = new THREE.PlaneGeometry(2, 2);
    const material = new THREE.ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms: {
        uTime: { value: 0 },
        uResolution: { value: new THREE.Vector2(w, h) },
      },
    });

    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    let animId: number;
    const clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      material.uniforms.uTime.value = clock.getElapsedTime();
      renderer.render(scene, camera);
    };
    animate();

    const onResize = () => {
      const nw = window.innerWidth;
      const nh = window.innerHeight;
      renderer.setSize(nw, nh);
      material.uniforms.uResolution.value.set(nw, nh);
    };
    window.addEventListener('resize', onResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', onResize);
      geometry.dispose();
      material.dispose();
      renderer.dispose();
      if (mountRef.current && renderer.domElement.parentNode === mountRef.current) {
        mountRef.current.removeChild(renderer.domElement);
      }
    };
  }, []);

  return (
    <div
      ref={mountRef}
      style={{
        position: 'fixed',
        top: 0, left: 0,
        width: '100%',
        height: '100%',
        zIndex: 0,
        pointerEvents: 'none',
      }}
    />
  );
};

export default AuroraCanvas;
