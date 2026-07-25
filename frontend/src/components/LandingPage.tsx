import { useEffect, useRef } from 'react';
import { motion, useScroll, useTransform, useSpring } from 'framer-motion';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import './LandingPage.css';

gsap.registerPlugin(ScrollTrigger);

interface LandingPageProps {
  onTryYours: () => void;
  onOpenAuth: (mode: 'login' | 'signup') => void;
}

const examples = [
  { id: 1, genre: 'Slice of Life', title: 'Quiet Mornings', src: '/slice of life.jpeg', color: '#ff9f43' },
  { id: 2, genre: 'Action', title: 'Neon Pursuit', src: '/action.jpeg', color: '#ff00ff' },
  { id: 3, genre: 'Fantasy', title: 'Crystal Spire', src: '/fantasy.jpeg', color: '#7b2ff7' },
];

const stats = [
  { value: '2M+', label: 'Manga Panels Generated' },
  { value: '50K+', label: 'Active Creators' },
  { value: '99.9%', label: 'Uptime SLA' },
  { value: '< 8s', label: 'Avg. Generation Time' },
];

const features = [
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
      </svg>
    ),
    title: 'Diffusion Pipeline',
    desc: 'State-of-the-art stable diffusion models fine-tuned on 200K manga panels.',
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <circle cx="12" cy="12" r="10" />
        <path d="M12 6v6l4 2" />
      </svg>
    ),
    title: 'Real-time Generation',
    desc: 'Sub-8 second generation time backed by optimized GPU inference clusters.',
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
      </svg>
    ),
    title: 'Genre Intelligence',
    desc: 'Automatic scene, dialogue, and panel layout generation per genre archetype.',
  },
];

const LandingPage = ({ onTryYours, onOpenAuth }: LandingPageProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const heroRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const statsRef = useRef<HTMLDivElement>(null);
  const featuresRef = useRef<HTMLDivElement>(null);
  const galleryRef = useRef<HTMLDivElement>(null);
  const floatRefs = useRef<(HTMLDivElement | null)[]>([]);

  const { scrollY } = useScroll();
  const heroY = useTransform(scrollY, [0, 600], [0, -120]);
  const heroOpacity = useTransform(scrollY, [0, 400], [1, 0]);
  const smoothHeroY = useSpring(heroY, { stiffness: 100, damping: 20 });

  // GSAP ScrollTrigger animations
  useEffect(() => {
    const ctx = gsap.context(() => {
      // Stats counter animation
      if (statsRef.current) {
        gsap.from('.stat-card', {
          opacity: 0,
          y: 60,
          stagger: 0.12,
          duration: 0.8,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: statsRef.current,
            start: 'top 80%',
            toggleActions: 'play none none reverse',
          },
        });
      }

      // Features reveal
      if (featuresRef.current) {
        gsap.from('.feature-item', {
          opacity: 0,
          x: -50,
          stagger: 0.15,
          duration: 0.9,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: featuresRef.current,
            start: 'top 75%',
          },
        });
      }

      // Gallery parallax levitation
      floatRefs.current.forEach((el, i) => {
        if (!el) return;
        gsap.to(el, {
          y: (i % 2 === 0 ? -30 : 30),
          duration: 2.5 + i * 0.3,
          repeat: -1,
          yoyo: true,
          ease: 'sine.inOut',
          delay: i * 0.4,
        });
      });

      // Gallery scroll reveal with 3D tilt
      if (galleryRef.current) {
        gsap.from('.gallery-card', {
          opacity: 0,
          rotateY: -15,
          y: 80,
          stagger: 0.15,
          duration: 1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: galleryRef.current,
            start: 'top 80%',
          },
        });
      }

      // Title word-by-word reveal
      if (titleRef.current) {
        const words = titleRef.current.querySelectorAll('.word');
        gsap.from(words, {
          opacity: 0,
          y: 80,
          rotateX: -30,
          stagger: 0.08,
          duration: 0.9,
          ease: 'power4.out',
          delay: 0.3,
        });
      }
    }, containerRef);

    return () => ctx.revert();
  }, []);

  // 3D card tilt on mouse move
  const handleCardMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const card = e.currentTarget;
    const rect = card.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const rx = ((e.clientY - cy) / rect.height) * 16;
    const ry = -((e.clientX - cx) / rect.width) * 16;
    gsap.to(card, { rotateX: rx, rotateY: ry, duration: 0.3, ease: 'power2.out', transformPerspective: 800 });
  };

  const handleCardMouseLeave = (e: React.MouseEvent<HTMLDivElement>) => {
    gsap.to(e.currentTarget, { rotateX: 0, rotateY: 0, duration: 0.5, ease: 'elastic.out(1, 0.5)' });
  };

  return (
    <div className="landing-page" ref={containerRef}>

      {/* ── HERO ─────────────────────────────────────────── */}
      <section className="lp-hero" ref={heroRef}>
        <motion.div className="lp-hero-inner" style={{ y: smoothHeroY, opacity: heroOpacity }}>
          <motion.div
            className="lp-badge"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
          >
            <span className="lp-badge-dot" />
            Introducing KuroAi 2.0 — Now with Gen-5 Diffusion
          </motion.div>

          <h1 className="lp-title" ref={titleRef}>
            {'Unleash the'.split(' ').map((w, i) => (
              <span key={i} className="word">{w}{' '}</span>
            ))}
            <br />
            <span className="lp-title-gradient">
              {'Power of'.split(' ').map((w, i) => (
                <span key={i} className="word">{w}{' '}</span>
              ))}
            </span>
            <br />
            {'Generative Manga'.split(' ').map((w, i) => (
              <span key={i} className="word lp-title-outline">{w}{' '}</span>
            ))}
          </h1>

          <motion.p
            className="lp-subtitle"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            Transform your narrative into breathtaking visual manga with our next-generation
            <br className="desktop-br" /> AI pipeline — from story to panel in under 8 seconds.
          </motion.p>

          <motion.div
            className="lp-cta-row"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
          >
            <motion.button
              className="lp-btn-primary"
              onClick={onTryYours}
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.97 }}
            >
              <span>Start Creating Free</span>
              <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 10h12M12 4l6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </motion.button>

            <motion.button
              className="lp-btn-ghost"
              onClick={() => onOpenAuth('login')}
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.97 }}
            >
              Sign In
            </motion.button>
          </motion.div>

          <motion.div
            className="lp-rating"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.1 }}
          >
            <div className="lp-stars">
              {[1,2,3,4,5].map(i => (
                <svg key={i} viewBox="0 0 16 16" fill={i <= 4 ? '#FFD700' : 'none'} stroke="#FFD700" strokeWidth="1">
                  <path d="M8 1l1.85 3.75L14 5.5l-3 2.9.7 4.1L8 10.4l-3.7 2.1.7-4.1-3-2.9 4.15-.75L8 1z" />
                </svg>
              ))}
            </div>
            <span className="lp-rating-text"><strong>4.8</strong> from 12K+ creators</span>
          </motion.div>
        </motion.div>

        {/* Floating gallery cards behind hero text */}
        <div className="lp-hero-gallery">
          {examples.map((ex, i) => (
            <div
              key={ex.id}
              className={`lp-float-card lp-float-card--${i}`}
              ref={el => { floatRefs.current[i] = el; }}
            >
              <img src={ex.src} alt={ex.title} onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
              <div className="lp-float-card-badge" style={{ background: ex.color + '22', color: ex.color, borderColor: ex.color + '44' }}>
                {ex.genre}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── STATS ────────────────────────────────────────── */}
      <section className="lp-stats" ref={statsRef}>
        <div className="lp-stats-grid">
          {stats.map((s) => (
            <div key={s.label} className="stat-card glass-card">
              <div className="stat-value">{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── FEATURES ─────────────────────────────────────── */}
      <section className="lp-features" ref={featuresRef}>
        <div className="lp-section-header">
          <motion.span
            className="lp-section-eyebrow"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            Why KuroAi
          </motion.span>
          <motion.h2
            className="lp-section-title"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            Engineered for Visionaries
          </motion.h2>
        </div>
        <div className="lp-features-grid">
          {features.map((f) => (
            <div key={f.title} className="feature-item glass-card">
              <div className="fi-icon">{f.icon}</div>
              <h3 className="fi-title">{f.title}</h3>
              <p className="fi-desc">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── GALLERY ──────────────────────────────────────── */}
      <section className="lp-gallery" ref={galleryRef}>
        <div className="lp-section-header">
          <motion.span className="lp-section-eyebrow" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
            Gallery
          </motion.span>
          <motion.h2 className="lp-section-title" initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
            Explore Genres
          </motion.h2>
        </div>
        <div className="lp-gallery-grid">
          {examples.map((ex, i) => (
            <div
              key={ex.id}
              className="gallery-card"
              onMouseMove={handleCardMouseMove}
              onMouseLeave={handleCardMouseLeave}
              style={{ '--card-accent': ex.color } as React.CSSProperties}
            >
              <div className="gc-image-wrap">
                <img src={ex.src} alt={ex.title}
                  onError={(e) => {
                    const t = e.target as HTMLImageElement;
                    t.style.display = 'none';
                    (t.nextSibling as HTMLElement).style.display = 'block';
                  }}
                />
                <div className="gc-fallback" style={{ display: 'none', background: `linear-gradient(135deg, #1a1a2e, ${ex.color}22)` }} />
                <div className="gc-overlay" />
                <div className="gc-badge" style={{ background: ex.color + '22', color: ex.color }}>{ex.genre}</div>
              </div>
              <div className="gc-content">
                <h3 className="gc-title">{ex.title}</h3>
                <button className="gc-cta" onClick={onTryYours}>Try this style →</button>
              </div>
              <div className="gc-border-glow" style={{ '--glow-color': ex.color } as React.CSSProperties} />
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA BANNER ───────────────────────────────────── */}
      <section className="lp-cta-banner">
        <motion.div
          className="lp-cta-inner glass-card"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="lp-cta-title">Ready to create your manga?</h2>
          <p className="lp-cta-sub">Join 50,000+ creators generating stunning visual stories with AI.</p>
          <div className="lp-cta-btns">
            <motion.button className="lp-btn-primary" onClick={() => onOpenAuth('signup')} whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}>
              Get Started Free
            </motion.button>
            <motion.button className="lp-btn-ghost" onClick={onTryYours} whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}>
              Try Demo
            </motion.button>
          </div>
        </motion.div>
      </section>

    </div>
  );
};

export default LandingPage;
