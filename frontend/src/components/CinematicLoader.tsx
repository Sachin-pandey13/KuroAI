import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { getLoaderMode } from '../utils/loaderStrategy';
import './CinematicLoader.css';

interface CinematicLoaderProps {
  onComplete: () => void;
}

export default function CinematicLoader({ onComplete }: CinematicLoaderProps) {
  const [skipVisible, setSkipVisible] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const eyeSvgRef = useRef<SVGSVGElement>(null);
  const arcsGroupRef = useRef<SVGGroupElement>(null);
  const irisRef = useRef<SVGCircleElement>(null);
  const pupilRef = useRef<SVGCircleElement>(null);
  const textContainerRef = useRef<HTMLDivElement>(null);
  const glowRingRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const mode = getLoaderMode();

    if (mode === 'skip') {
      onComplete();
      return;
    }

    // Show skip button after 1s
    const timer = setTimeout(() => setSkipVisible(true), 1000);

    const timelineDuration = mode === 'short' ? 1.0 : 3.6;

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({
        onComplete: () => {
          // Exit curtain animation
          gsap.to(containerRef.current, {
            scaleY: 0,
            transformOrigin: 'top center',
            duration: 0.7,
            ease: 'power4.inOut',
            onComplete: () => {
              onComplete();
            },
          });
        },
      });

      if (mode === 'short') {
        // Quick 1s loader for returning visitors
        tl.fromTo(
          glowRingRef.current,
          { opacity: 0, scale: 0.5 },
          { opacity: 1, scale: 1, duration: 0.4, ease: 'back.out(1.7)' }
        )
        .fromTo(
          textContainerRef.current,
          { opacity: 0, y: 15 },
          { opacity: 1, y: 0, duration: 0.4 },
          '-=0.2'
        )
        .to({}, { duration: 0.3 }); // pause
      } else {
        // Full cinematic 3.6s eye opening intro
        // t=0: Glow blooms
        tl.fromTo(
          glowRingRef.current,
          { opacity: 0, scale: 0.2 },
          { opacity: 0.8, scale: 1.5, duration: 0.8, ease: 'power2.out' }
        )
        // t=0.8: SVG Eye iris fades in & eyelid opens
        .fromTo(
          eyeSvgRef.current,
          { opacity: 0, scale: 0.6 },
          { opacity: 1, scale: 1, duration: 0.8, ease: 'power3.out' },
          '-=0.4'
        )
        // t=1.2: Tomoe-inspired 3 AI arcs rotate
        .fromTo(
          arcsGroupRef.current,
          { rotation: 0, transformOrigin: '50% 50%' },
          { rotation: 360, duration: 1.4, ease: 'power2.inOut' },
          '-=0.4'
        )
        // Pupil expands slightly
        .fromTo(
          pupilRef.current,
          { r: 8 },
          { r: 16, duration: 0.6, ease: 'back.out(2)' },
          '-=1.0'
        )
        // t=2.4: Eye scales up into camera (zoom impact)
        .to(eyeSvgRef.current, {
          scale: 6,
          opacity: 0,
          duration: 0.6,
          ease: 'power4.in',
        })
        // Ring collapses & KuroAI logo text reveals
        .fromTo(
          textContainerRef.current,
          { opacity: 0, scale: 0.85, y: 20 },
          { opacity: 1, scale: 1, y: 0, duration: 0.5, ease: 'power3.out' },
          '-=0.2'
        )
        .to({}, { duration: 0.4 }); // slight pause at end
      }
    }, containerRef);

    return () => {
      clearTimeout(timer);
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
    <div ref={containerRef} className="cinematic-loader" aria-label="Loading KuroAI">
      {/* Skip button for Accessibility */}
      {skipVisible && (
        <button
          type="button"
          onClick={handleSkip}
          className="loader-skip-btn"
          aria-label="Skip introduction"
        >
          Skip Intro ➔
        </button>
      )}

      {/* Red Radial Background Glow */}
      <div ref={glowRingRef} className="loader-glow-ring" aria-hidden="true" />

      <div className="loader-center-content">
        {/* Custom AI Vision Eye SVG Symbol */}
        <svg
          ref={eyeSvgRef}
          className="loader-eye-svg"
          viewBox="0 0 200 200"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          {/* Eyelid / Outer Frame */}
          <path
            d="M 20,100 C 60,40 140,40 180,100 C 140,160 60,160 20,100 Z"
            stroke="rgba(192, 57, 43, 0.6)"
            strokeWidth="2.5"
            fill="rgba(10, 10, 10, 0.85)"
          />

          {/* Concentric Glowing Outer Ring */}
          <circle cx="100" cy="100" r="50" stroke="rgba(231, 76, 60, 0.4)" strokeWidth="1.5" strokeDasharray="4 4" />
          
          {/* Iris Base */}
          <circle ref={irisRef} cx="100" cy="100" r="38" fill="url(#irisGradient)" stroke="#c0392b" strokeWidth="2" />

          {/* 3 Abstract Rotating Arc Segments (Original AI-Eye Geometry) */}
          <g ref={arcsGroupRef}>
            <path
              d="M 100,68 A 32 32 0 0 1 128,84"
              stroke="#fff"
              strokeWidth="3.5"
              strokeLinecap="round"
              opacity="0.9"
            />
            <path
              d="M 128,116 A 32 32 0 0 1 90,131"
              stroke="#fff"
              strokeWidth="3.5"
              strokeLinecap="round"
              opacity="0.9"
            />
            <path
              d="M 72,116 A 32 32 0 0 1 72,84"
              stroke="#fff"
              strokeWidth="3.5"
              strokeLinecap="round"
              opacity="0.9"
            />
          </g>

          {/* Central AI Pupil */}
          <circle ref={pupilRef} cx="100" cy="100" r="10" fill="#050505" stroke="#e74c3c" strokeWidth="2" />
          <circle cx="96" cy="96" r="3" fill="#ffffff" opacity="0.8" />

          {/* Gradients */}
          <defs>
            <radialGradient id="irisGradient" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#e74c3c" />
              <stop offset="70%" stopColor="#c0392b" />
              <stop offset="100%" stopColor="#5c0000" />
            </radialGradient>
          </defs>
        </svg>

        {/* KuroAI Wordmark & Subtitle */}
        <div ref={textContainerRef} className="loader-text-wrap">
          <h1 className="loader-brand-title">
            KURO<span className="accent-red">AI</span>
          </h1>
          <p className="loader-tagline">Generative Manga AI Engine</p>
        </div>
      </div>
    </div>
  );
}
