import { useEffect, useRef } from 'react';
import { useDeviceClass } from '../utils/useDeviceClass';

export default function FloatingPanelsCanvas() {
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

    // Generate 14 floating manga panels
    const panels = Array.from({ length: 14 }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      w: 120 + Math.random() * 160,
      h: 160 + Math.random() * 220,
      angle: (Math.random() - 0.5) * 0.2, // subtle tilt
      vx: (Math.random() - 0.5) * 0.25,
      vy: (Math.random() - 0.5) * 0.2,
      vAngle: (Math.random() - 0.5) * 0.0005,
      opacity: 0.02 + Math.random() * 0.035, // subliminal opacity
    }));

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      panels.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;
        p.angle += p.vAngle;

        // Wrap edges
        if (p.x < -p.w) p.x = width + p.w;
        if (p.x > width + p.w) p.x = -p.w;
        if (p.y < -p.h) p.y = height + p.h;
        if (p.y > height + p.h) p.y = -p.h;

        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.angle);

        // Panel Border
        ctx.strokeStyle = `rgba(245, 240, 232, ${p.opacity * 1.5})`;
        ctx.lineWidth = 1.5;
        ctx.strokeRect(-p.w / 2, -p.h / 2, p.w, p.h);

        // Panel Background Fill
        ctx.fillStyle = `rgba(192, 57, 43, ${p.opacity * 0.3})`;
        ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);

        // Internal Halftone Grid Line
        ctx.strokeStyle = `rgba(255, 255, 255, ${p.opacity * 0.4})`;
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        ctx.moveTo(-p.w / 2, 0);
        ctx.lineTo(p.w / 2, 0);
        ctx.stroke();

        ctx.restore();
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
