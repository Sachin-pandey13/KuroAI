import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import gsap from 'gsap';
import './CinematicLoader.css';

const CinematicLoader = ({ onComplete }: { onComplete: () => void }) => {
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState<'loading' | 'reveal'>('loading');
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const loaderRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);

  // WebGL ripple canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d')!;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    let animId: number;
    let t = 0;

    const draw = () => {
      animId = requestAnimationFrame(draw);
      t += 0.015;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const cx = canvas.width / 2;
      const cy = canvas.height / 2;

      for (let r = 0; r < 8; r++) {
        const radius = (r * 120 + (t * 60) % 960);
        const alpha = Math.max(0, 1 - radius / 960) * 0.25;
        ctx.beginPath();
        ctx.arc(cx, cy, radius, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(255, 0, 255, ${alpha})`;
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }

      // Scanning line
      const scanY = ((Math.sin(t * 0.7) + 1) / 2) * canvas.height;
      const gradient = ctx.createLinearGradient(0, scanY - 30, 0, scanY + 30);
      gradient.addColorStop(0, 'transparent');
      gradient.addColorStop(0.5, 'rgba(255, 0, 255, 0.12)');
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, scanY - 30, canvas.width, 60);
    };
    draw();

    return () => cancelAnimationFrame(animId);
  }, []);

  // GSAP progress timeline
  useEffect(() => {
    const tl = gsap.timeline();

    tl.to({ val: 0 }, {
      val: 100,
      duration: 2.8,
      ease: 'power2.inOut',
      onUpdate: function () {
        setProgress(Math.round(this.targets()[0].val));
      },
      onComplete: () => {
        setPhase('reveal');

        // Cinematic curtain reveal
        gsap.to(loaderRef.current, {
          scaleY: 0,
          transformOrigin: 'top center',
          duration: 0.8,
          ease: 'power4.inOut',
          delay: 0.4,
          onComplete: onComplete,
        });
      },
    });

    // Text flicker
    gsap.fromTo(textRef.current,
      { opacity: 0.3 },
      { opacity: 1, duration: 0.3, repeat: 3, yoyo: true, delay: 0.2 }
    );

    return () => { tl.kill(); };
  }, [onComplete]);

  return (
    <motion.div
      ref={loaderRef}
      className="cinematic-loader"
      initial={{ opacity: 1 }}
    >
      <canvas ref={canvasRef} className="loader-canvas" />

      <div className="loader-content">
        {/* Logo */}
        <motion.div
          className="loader-logo"
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ duration: 1, type: 'spring', stiffness: 80 }}
        >
          <svg viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#ff00ff" />
                <stop offset="100%" stopColor="#7b2ff7" />
              </linearGradient>
            </defs>
            <polygon points="30,3 57,18 57,42 30,57 3,42 3,18" stroke="url(#logoGrad)" strokeWidth="2" fill="none" />
            <polygon points="30,12 48,22 48,38 30,48 12,38 12,22" stroke="url(#logoGrad)" strokeWidth="1.5" fill="rgba(255,0,255,0.05)" />
            <circle cx="30" cy="30" r="8" fill="url(#logoGrad)" opacity="0.8" />
          </svg>
        </motion.div>

        {/* Brand name */}
        <div ref={textRef} className="loader-brand">
          {'KuroAi'.split('').map((char, i) => (
            <motion.span
              key={i}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.07, type: 'spring', stiffness: 200 }}
              className="loader-char"
            >
              {char}
            </motion.span>
          ))}
        </div>

        <motion.p
          className="loader-tagline"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          Generative Manga Intelligence
        </motion.p>

        {/* Progress bar */}
        <div className="loader-progress-container">
          <div className="loader-progress-track">
            <motion.div
              className="loader-progress-fill"
              style={{ width: `${progress}%` }}
            />
            <div className="loader-progress-glow" style={{ left: `${progress}%` }} />
          </div>
          <div className="loader-progress-label">
            <span>{progress}%</span>
            <span className="loader-status">
              {progress < 30 ? 'Initializing AI Core...' :
               progress < 60 ? 'Loading Diffusion Models...' :
               progress < 90 ? 'Calibrating Pipelines...' :
               'Ready'}
            </span>
          </div>
        </div>
      </div>

      {/* Corner decorations */}
      {['tl', 'tr', 'bl', 'br'].map((corner) => (
        <div key={corner} className={`loader-corner loader-corner--${corner}`}>
          <svg viewBox="0 0 20 20" fill="none">
            <path d="M0 10 L0 0 L10 0" stroke="#ff00ff" strokeWidth="2" opacity="0.6" />
          </svg>
        </div>
      ))}
    </motion.div>
  );
};

export default CinematicLoader;
