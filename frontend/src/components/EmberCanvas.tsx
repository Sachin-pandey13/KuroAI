import { useEffect, useRef } from 'react';
import { useDeviceClass } from '../utils/useDeviceClass';

export default function EmberCanvas() {
  const deviceClass = useDeviceClass();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (deviceClass === 'mobile') return;
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let width = (canvas.width = canvas.parentElement?.clientWidth || window.innerWidth);
    let height = (canvas.height = canvas.parentElement?.clientHeight || 300);

    const handleResize = () => {
      if (!canvas || !canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth;
      height = canvas.height = canvas.parentElement.clientHeight;
    };
    window.addEventListener('resize', handleResize);

    // 50 ember particles rising from bottom
    const embers = Array.from({ length: 50 }, () => ({
      x: Math.random() * width,
      y: height + Math.random() * 50,
      size: 1 + Math.random() * 3,
      vy: -0.8 - Math.random() * 1.2,
      vx: (Math.random() - 0.5) * 0.6,
      opacity: 0.6 + Math.random() * 0.4,
      hue: Math.random() > 0.5 ? '#ff6b35' : '#c0392b', // ember orange or crimson
    }));

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      embers.forEach((e) => {
        e.y += e.vy;
        e.x += e.vx;
        e.opacity -= 0.003;

        if (e.y < -10 || e.opacity <= 0) {
          e.y = height + 10;
          e.x = Math.random() * width;
          e.opacity = 0.6 + Math.random() * 0.4;
        }

        ctx.beginPath();
        ctx.arc(e.x, e.y, e.size, 0, Math.PI * 2);
        ctx.fillStyle = e.hue;
        ctx.shadowColor = e.hue;
        ctx.shadowBlur = 8;
        ctx.globalAlpha = e.opacity;
        ctx.fill();
      });

      ctx.shadowBlur = 0;
      ctx.globalAlpha = 1;
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
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 1,
      }}
    />
  );
}
