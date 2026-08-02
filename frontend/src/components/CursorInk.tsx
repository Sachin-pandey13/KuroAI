import { useEffect, useRef } from 'react';
import { useDeviceClass } from '../utils/useDeviceClass';
import { useReducedMotion } from '../utils/useReducedMotion';
import './CursorInk.css';

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  opacity: number;
  color: string;
}

interface SpeedLine {
  x: number;
  y: number;
  angle: number;
  length: number;
  opacity: number;
}

export default function CursorInk() {
  const deviceClass = useDeviceClass();
  const prefersReducedMotion = useReducedMotion();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const cursorRingRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (deviceClass === 'mobile' || deviceClass === 'tablet' || prefersReducedMotion) {
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    let mouseX = -100;
    let mouseY = -100;
    let targetX = -100;
    let targetY = -100;
    let lastMouseX = -100;
    let lastMouseY = -100;

    const particles: Particle[] = [];
    const speedLines: SpeedLine[] = [];

    const handleMouseMove = (e: MouseEvent) => {
      const { clientX, clientY } = e;

      // Speed calculation
      const dx = clientX - lastMouseX;
      const dy = clientY - lastMouseY;
      const dist = Math.hypot(dx, dy);

      mouseX = clientX;
      mouseY = clientY;

      // High velocity triggers manga speed lines
      if (dist > 35 && lastMouseX !== -100) {
        const angle = Math.atan2(dy, dx);
        for (let i = 0; i < 4; i++) {
          speedLines.push({
            x: clientX + (Math.random() - 0.5) * 20,
            y: clientY + (Math.random() - 0.5) * 20,
            angle: angle + (Math.random() - 0.5) * 0.4,
            length: 30 + Math.random() * 40,
            opacity: 0.8,
          });
        }
      }

      // Ink droplet trail
      if (Math.random() < 0.6) {
        particles.push({
          x: clientX,
          y: clientY,
          vx: (Math.random() - 0.5) * 1.5,
          vy: 0.5 + Math.random() * 1.2,
          size: 1.5 + Math.random() * 3.5,
          opacity: 0.8,
          color: Math.random() > 0.4 ? '#c0392b' : '#f5f0e8',
        });
      }

      lastMouseX = clientX;
      lastMouseY = clientY;
    };

    window.addEventListener('mousemove', handleMouseMove, { passive: true });

    let animId: number;

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Smooth lag lerp for cursor ring
      targetX += (mouseX - targetX) * 0.2;
      targetY += (mouseY - targetY) * 0.2;

      if (cursorRingRef.current) {
        cursorRingRef.current.style.transform = `translate3d(${targetX}px, ${targetY}px, 0)`;
      }

      // Draw Ink Droplet Particles
      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.opacity -= 0.02;

        if (p.opacity <= 0) {
          particles.splice(i, 1);
          continue;
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.opacity;
        ctx.fill();
      }

      // Draw Speed Lines
      for (let i = speedLines.length - 1; i >= 0; i--) {
        const s = speedLines[i];
        s.opacity -= 0.04;

        if (s.opacity <= 0) {
          speedLines.splice(i, 1);
          continue;
        }

        ctx.save();
        ctx.translate(s.x, s.y);
        ctx.rotate(s.angle);
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(-s.length, 0);
        ctx.strokeStyle = '#c0392b';
        ctx.lineWidth = 2;
        ctx.globalAlpha = s.opacity;
        ctx.stroke();
        ctx.restore();
      }

      ctx.globalAlpha = 1;
      animId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animId);
    };
  }, [deviceClass, prefersReducedMotion]);

  if (deviceClass === 'mobile' || deviceClass === 'tablet' || prefersReducedMotion) {
    return null;
  }

  return (
    <>
      {/* Canvas for Ink Splatters and Speed Lines */}
      <canvas
        ref={canvasRef}
        className="cursor-ink-canvas"
        aria-hidden="true"
      />

      {/* Crimson Glow Ring Lag Follower */}
      <div ref={cursorRingRef} className="cursor-glow-ring" aria-hidden="true" />
    </>
  );
}
