import { useRef, useEffect } from 'react';
import * as THREE from 'three';

const ParticleCanvas = () => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const w = window.innerWidth;
    const h = window.innerHeight;

    // Scene setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, w / h, 0.1, 1000);
    camera.position.z = 5;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(w, h);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);
    mountRef.current.appendChild(renderer.domElement);

    // GLSL Shader Material for particles
    const vertexShader = `
      attribute float aSize;
      attribute float aAlpha;
      attribute vec3 aColor;
      uniform float uTime;
      varying float vAlpha;
      varying vec3 vColor;

      void main() {
        vAlpha = aAlpha;
        vColor = aColor;
        vec3 pos = position;
        float wave = sin(pos.x * 0.5 + uTime * 0.3) * 0.2;
        float wave2 = cos(pos.y * 0.4 + uTime * 0.2) * 0.15;
        pos.z += wave + wave2;
        vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
        gl_PointSize = aSize * (300.0 / -mvPosition.z);
        gl_Position = projectionMatrix * mvPosition;
      }
    `;

    const fragmentShader = `
      varying float vAlpha;
      varying vec3 vColor;

      void main() {
        vec2 uv = gl_PointCoord - vec2(0.5);
        float dist = length(uv);
        if (dist > 0.5) discard;
        float alpha = smoothstep(0.5, 0.0, dist) * vAlpha;
        gl_FragColor = vec4(vColor, alpha);
      }
    `;

    // Particle geometry
    const count = 3000;
    const positions = new Float32Array(count * 3);
    const sizes = new Float32Array(count);
    const alphas = new Float32Array(count);
    const colors = new Float32Array(count * 3);

    const palette = [
      new THREE.Color('#ff00ff'),
      new THREE.Color('#7b2ff7'),
      new THREE.Color('#ff006e'),
      new THREE.Color('#ffffff'),
      new THREE.Color('#a855f7'),
    ];

    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 20;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 20;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 10;
      sizes[i] = Math.random() * 2 + 0.5;
      alphas[i] = Math.random() * 0.6 + 0.1;
      const c = palette[Math.floor(Math.random() * palette.length)];
      colors[i * 3] = c.r;
      colors[i * 3 + 1] = c.g;
      colors[i * 3 + 2] = c.b;
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));
    geometry.setAttribute('aAlpha', new THREE.BufferAttribute(alphas, 1));
    geometry.setAttribute('aColor', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms: { uTime: { value: 0 } },
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });

    const particles = new THREE.Points(geometry, material);
    scene.add(particles);

    // Mouse parallax
    let mouseX = 0, mouseY = 0;
    const onMouseMove = (e: MouseEvent) => {
      mouseX = (e.clientX / w - 0.5) * 0.5;
      mouseY = (e.clientY / h - 0.5) * 0.5;
    };
    window.addEventListener('mousemove', onMouseMove);

    // Animation loop
    let animId: number;
    const clock = new THREE.Clock();
    const animate = () => {
      animId = requestAnimationFrame(animate);
      const t = clock.getElapsedTime();
      material.uniforms.uTime.value = t;
      particles.rotation.y = t * 0.03 + mouseX;
      particles.rotation.x = Math.sin(t * 0.02) * 0.1 - mouseY;
      renderer.render(scene, camera);
    };
    animate();

    // Resize
    const onResize = () => {
      const nw = window.innerWidth;
      const nh = window.innerHeight;
      camera.aspect = nw / nh;
      camera.updateProjectionMatrix();
      renderer.setSize(nw, nh);
    };
    window.addEventListener('resize', onResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('resize', onResize);
      renderer.dispose();
      geometry.dispose();
      material.dispose();
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
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 0,
        pointerEvents: 'none',
      }}
    />
  );
};

export default ParticleCanvas;
