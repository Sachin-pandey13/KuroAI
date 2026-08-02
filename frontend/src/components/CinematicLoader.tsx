import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { getLoaderMode } from '../utils/loaderStrategy';
import './CinematicLoader.css';

interface CinematicLoaderProps {
  onComplete: () => void;
}

const hudLogs = [
  'Initializing Vision Engine...',
  'Loading Story Agents...',
  'Building Context...',
  'Synchronizing Runtime...',
  'SYSTEM READY ◈',
];

const taglineFull = 'GENERATIVE MANGA AI ENGINE';

export default function CinematicLoader({ onComplete }: CinematicLoaderProps) {
  const [skipVisible, setSkipVisible] = useState(false);
  const [hudText, setHudText] = useState('');
  const [taglineTyped, setTaglineTyped] = useState('');

  const containerRef = useRef<HTMLDivElement>(null);
  const sparkRef = useRef<HTMLDivElement>(null);
  const flashRef = useRef<HTMLDivElement>(null);
  const waveRef = useRef<HTMLDivElement>(null);

  const eyeSvgRef = useRef<SVGSVGElement>(null);
  const outlinePathRef = useRef<SVGPathElement>(null);
  const irisFillRef = useRef<SVGCircleElement>(null);
  const ring1Ref = useRef<SVGCircleElement>(null);
  const ring2Ref = useRef<SVGCircleElement>(null);
  const arcsGroupRef = useRef<SVGGroupElement>(null);
  const pupilRef = useRef<SVGCircleElement>(null);
  const eyelidTopRef = useRef<SVGPathElement>(null);
  const eyelidBottomRef = useRef<SVGPathElement>(null);

  const lettersWrapRef = useRef<HTMLDivElement>(null);
  const cursorDotRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const mode = getLoaderMode();

    if (mode === 'skip') {
      onComplete();
      return;
    }

    const timer = setTimeout(() => setSkipVisible(true), 1000);

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({
        onComplete: () => {
          gsap.to(containerRef.current, {
            opacity: 0,
            duration: 0.6,
            ease: 'power2.inOut',
            onComplete,
          });
        },
      });

      if (mode === 'short') {
        // Quick 1.2s intro for returning visitors
        tl.fromTo(
          eyeSvgRef.current,
          { opacity: 0, scale: 0.5 },
          { opacity: 1, scale: 1, duration: 0.5, ease: 'back.out(1.7)' }
        )
        .fromTo(
          lettersWrapRef.current,
          { opacity: 0, y: 15 },
          { opacity: 1, y: 0, duration: 0.4 },
          '-=0.2'
        )
        .to({}, { duration: 0.3 });
      } else {
        // 12-SCENE KUROAI AWAKENING SEQUENCE (10 SECONDS)

        // Scene 1 — Absolute Darkness (0–1s) & Spark Pulse
        tl.fromTo(
          sparkRef.current,
          { opacity: 0, scale: 0.2 },
          { opacity: 1, scale: 1.2, duration: 0.8, ease: 'sine.inOut', delay: 0.2 }
        )
        .to(sparkRef.current, { opacity: 0, scale: 2, duration: 0.3 })

        // Scene 2 — AI Scanning Begins: Calligraphy Ink Line Drawing (1–2s)
        .set(eyeSvgRef.current, { opacity: 1 })
        .fromTo(
          outlinePathRef.current,
          { strokeDasharray: 600, strokeDashoffset: 600 },
          { strokeDashoffset: 0, duration: 1.0, ease: 'power2.out' }
        )

        // Scene 3 — Ink Fills Eye & Red Glow Awakens (2–3s)
        .fromTo(
          irisFillRef.current,
          { opacity: 0, scale: 0.4, transformOrigin: '50% 50%' },
          { opacity: 1, scale: 1, duration: 0.8, ease: 'power3.out' },
          '-=0.3'
        )

        // Scene 4 — Iris Assembly & Concentric Rings (3–4s)
        .fromTo(
          [ring1Ref.current, ring2Ref.current],
          { strokeDasharray: 300, strokeDashoffset: 300 },
          { strokeDashoffset: 0, duration: 0.7, stagger: 0.2, ease: 'power2.inOut' },
          '-=0.4'
        )
        .fromTo(
          arcsGroupRef.current,
          { rotation: 0, opacity: 0, transformOrigin: '50% 50%' },
          { rotation: 360, opacity: 1, duration: 1.0, ease: 'power2.inOut' },
          '-=0.5'
        )

        // Scene 5 — Floating HUD Boot Sequence Text (4–5s)
        .call(() => {
          let logIdx = 0;
          const hudInterval = setInterval(() => {
            if (logIdx < hudLogs.length) {
              setHudText(hudLogs[logIdx]);
              logIdx++;
            } else {
              clearInterval(hudInterval);
            }
          }, 200);
        })
        .to({}, { duration: 1.0 })

        // Scene 6 — Eye Opens Fully (5–6s)
        .to(eyelidTopRef.current, { y: -35, opacity: 0, duration: 0.8, ease: 'power3.inOut' }, '-=0.2')
        .to(eyelidBottomRef.current, { y: 35, opacity: 0, duration: 0.8, ease: 'power3.inOut' }, '-=0.8')

        // Scene 7 — Mouse Eye Pupil Tracking Activation (6–7s)
        .fromTo(
          pupilRef.current,
          { scale: 0.8 },
          { scale: 1.3, duration: 0.6, ease: 'back.out(2)' },
          '-=0.4'
        )
        .to({}, { duration: 0.6 })

        // Scene 8 — Energy Pulse Wave & Chromatic Flash (7–8s)
        .fromTo(
          waveRef.current,
          { opacity: 1, scale: 0.2 },
          { opacity: 0, scale: 4, duration: 0.7, ease: 'power3.out' }
        )
        .fromTo(
          flashRef.current,
          { opacity: 0 },
          { opacity: 0.5, duration: 0.15, yoyo: true, repeat: 1 },
          '-=0.6'
        )

        // Scene 9 — KUROAI Emerges Letter by Letter (8–9s)
        .fromTo(
          '.letter-item',
          { opacity: 0, y: 25, scale: 0.7 },
          { opacity: 1, y: 0, scale: 1, duration: 0.5, stagger: 0.08, ease: 'back.out(1.7)' },
          '-=0.2'
        )

        // Scene 10 — Tagline Types Itself (9–10s)
        .call(() => {
          let charIdx = 0;
          const typeInterval = setInterval(() => {
            if (charIdx <= taglineFull.length) {
              setTaglineTyped(taglineFull.slice(0, charIdx));
              charIdx++;
            } else {
              clearInterval(typeInterval);
            }
          }, 35);
        })
        .to({}, { duration: 1.1 })

        // Scene 12 — Eye Shrinks & Logo Morphs to Navigation
        .to(eyeSvgRef.current, {
          scale: 0.35,
          y: -180,
          opacity: 0,
          duration: 0.6,
          ease: 'power3.inOut',
        });
      }
    }, containerRef);

    // Mouse Tracking during Scene 7
    const handleMouseMove = (e: MouseEvent) => {
      if (!pupilRef.current) return;
      const dx = (e.clientX - window.innerWidth / 2) * 0.05;
      const dy = (e.clientY - window.innerHeight / 2) * 0.05;
      gsap.to(pupilRef.current, { x: dx, y: dy, duration: 0.2 });
    };
    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('mousemove', handleMouseMove);
      ctx.revert();
    };
  }, [onComplete]);

  const handleSkip = () => {
    gsap.to(containerRef.current, {
      opacity: 0,
      duration: 0.3,
      onComplete,
    });
  };

  return (
    <div ref={containerRef} className="cinematic-loader" aria-label="KuroAI Awakening Sequence">
      {/* Chromatic Flash Overlay */}
      <div ref={flashRef} className="flash-overlay" aria-hidden="true" />

      {/* Skip Button */}
      {skipVisible && (
        <button
          type="button"
          onClick={handleSkip}
          className="loader-skip-btn"
          aria-label="Skip awakening sequence"
        >
          Skip Intro ➔
        </button>
      )}

      {/* Scene 1: Crimson Spark */}
      <div ref={sparkRef} className="awakening-spark" aria-hidden="true" />

      {/* Scene 8: Energy Pulse Wave */}
      <div ref={waveRef} className="energy-pulse-wave" aria-hidden="true" />

      {/* Scene 5: Floating HUD Text */}
      <div className="hud-boot-text">{hudText}</div>

      <div className="loader-center-content">
        {/* SVG Eye Symbol */}
        <svg
          ref={eyeSvgRef}
          className="loader-eye-svg"
          viewBox="0 0 200 200"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          {/* Eyelids for Scene 6 */}
          <path
            ref={eyelidTopRef}
            d="M 20,100 Q 100,20 180,100 Z"
            fill="#050505"
            stroke="#c0392b"
            strokeWidth="2"
          />
          <path
            ref={eyelidBottomRef}
            d="M 20,100 Q 100,180 180,100 Z"
            fill="#050505"
            stroke="#c0392b"
            strokeWidth="2"
          />

          {/* Scene 2: Eye Outline Calligraphy */}
          <path
            ref={outlinePathRef}
            d="M 20,100 C 60,40 140,40 180,100 C 140,160 60,160 20,100 Z"
            stroke="#c0392b"
            strokeWidth="3.5"
            fill="none"
          />

          {/* Scene 3: Ink Fill & Iris */}
          <circle
            ref={irisFillRef}
            cx="100"
            cy="100"
            r="42"
            fill="url(#awakeningIrisGrad)"
            stroke="#e74c3c"
            strokeWidth="2"
          />

          {/* Scene 4: Concentric Assembly Rings */}
          <circle ref={ring1Ref} cx="100" cy="100" r="54" stroke="rgba(231, 76, 60, 0.4)" strokeWidth="1.5" strokeDasharray="6 6" fill="none" />
          <circle ref={ring2Ref} cx="100" cy="100" r="32" stroke="rgba(255, 255, 255, 0.6)" strokeWidth="1.5" fill="none" />

          {/* Rotating AI Arcs */}
          <g ref={arcsGroupRef}>
            <path d="M 100,64 A 36 36 0 0 1 131,82" stroke="#fff" strokeWidth="3" strokeLinecap="round" />
            <path d="M 131,118 A 36 36 0 0 1 88,134" stroke="#fff" strokeWidth="3" strokeLinecap="round" />
            <path d="M 69,118 A 36 36 0 0 1 69,82" stroke="#fff" strokeWidth="3" strokeLinecap="round" />
          </g>

          {/* Scene 7: Pupil Mouse Tracker */}
          <circle ref={pupilRef} cx="100" cy="100" r="11" fill="#050505" stroke="#e74c3c" strokeWidth="2.5" />

          <defs>
            <radialGradient id="awakeningIrisGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#e74c3c" />
              <stop offset="60%" stopColor="#c0392b" />
              <stop offset="100%" stopColor="#3d0000" />
            </radialGradient>
          </defs>
        </svg>

        {/* Scene 9 & 10: KUROAI Letters & Typewriter Tagline */}
        <div ref={lettersWrapRef} className="loader-text-wrap">
          <h1 className="loader-brand-title">
            <span className="letter-item">K</span>
            <span className="letter-item">U</span>
            <span className="letter-item">R</span>
            <span className="letter-item">O</span>
            <span className="letter-item accent-red">A</span>
            <span className="letter-item accent-red">I</span>
          </h1>
          <p className="loader-tagline">
            {taglineTyped}
            <span ref={cursorDotRef} className="typing-cursor">_</span>
          </p>
        </div>
      </div>
    </div>
  );
}
