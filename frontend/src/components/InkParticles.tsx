import { useEffect, useRef } from 'react';
import { useDeviceClass } from '../utils/useDeviceClass';

export default function InkParticles() {
  const deviceClass = useDeviceClass();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (deviceClass === 'mobile') return;
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    const particleCount = deviceClass === 'tablet' ? 35 : 80;

    const particles = Array.from({ length: particleCount }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      size: 1 + Math.random() * 3,
      vy: -0.3 - Math.random() * 0.5,
      oscAmp: 0.2 + Math.random() * 0.6,
      oscSpeed: 0.01 + Math.random() * 0.02,
      phase: Math.random() * Math.PI * 2,
      opacity: 0.1 + Math.random() * 0.2,
      isCrimson: Math.random() > 0.6,
    }));

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      particles.forEach((p) => {
        p.phase += p.oscSpeed;
        p.y += p.vy;
        p.x += Math.sin(p.phase) * p.oscAmp;

        if (p.y < -10) {
          p.y = height + 10;
          p.x = Math.random() * width;
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.isCrimson
          ? `rgba(192, 57, 43, ${p.opacity})`
          : `rgba(245, 240, 232, ${p.opacity * 0.7})`;
        ctx.fill();
      });

      animId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animId);
    };
  }, [deviceClass]);

  if (deviceClass === 'mobile') return null;

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      style={{
        position: 'fixed',
        inset: 0,
        width: '100vw',
        height: '100vh',
        pointerEvents: 'none',
        zIndex: 0,
      }}
    />
  );
}
