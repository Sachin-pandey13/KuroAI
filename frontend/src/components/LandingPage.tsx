import { motion } from 'framer-motion';
import FloatingPanelsCanvas from './FloatingPanelsCanvas';
import InkParticles from './InkParticles';
import CursorInk from './CursorInk';
import WhySection from './WhySection';
import PipelineSection from './PipelineSection';
import ArchitectureSection from './ArchitectureSection';
import AgentsSection from './AgentsSection';
import GenerationDemo from './GenerationDemo';
import MetricsSection from './MetricsSection';
import './LandingPage.css';

interface LandingPageProps {
  onTryYours: () => void;
  onOpenAuth: (mode: 'login' | 'signup') => void;
}

export default function LandingPage({ onTryYours, onOpenAuth }: LandingPageProps) {
  return (
    <div className="landing-page-container">
      {/* Background Canvas Layers */}
      <FloatingPanelsCanvas />
      <InkParticles />
      <CursorInk />

      {/* Hero Section */}
      <section className="hero-section" aria-label="Hero Introduction">
        <motion.div
          className="hero-content"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        >
          {/* Eyemark & Brand Label */}
          <div className="hero-badge-row">
            <svg className="hero-eye-svg" viewBox="0 0 100 100" fill="none">
              <path d="M 10,50 C 30,20 70,20 90,50 C 70,80 30,80 10,50 Z" stroke="#c0392b" strokeWidth="6" fill="none" />
              <circle cx="50" cy="50" r="18" fill="#c0392b" />
              <circle cx="50" cy="50" r="6" fill="#050505" />
            </svg>
            <span className="hero-badge-text">KUROAI GENERATIVE MANGA ENGINE</span>
          </div>

          {/* Main Headline */}
          <h1 className="hero-headline">
            Stories Become <span className="accent-red-glow">Manga</span>.
          </h1>

          {/* Subtitle */}
          <p className="hero-subtitle">
            Powered by a multi-agent AI pipeline. Turn natural prompts into publication-ready manga chapters in under 8 seconds.
          </p>

          {/* CTA Row */}
          <div className="hero-cta-row">
            <motion.button
              type="button"
              className="hero-btn-primary"
              onClick={onTryYours}
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.96 }}
            >
              ▶ Begin Creating Free
            </motion.button>

            <motion.a
              href="#architecture"
              className="hero-btn-secondary"
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.96 }}
            >
              Explore Architecture →
            </motion.a>
          </div>

          {/* Scroll Down Cue */}
          <a href="#why" className="scroll-hint-anchor" aria-label="Scroll down to explore">
            <span className="scroll-hint-text">EXPLORE PIPELINE</span>
            <span className="scroll-hint-arrow">↓</span>
          </a>
        </motion.div>
      </section>

      {/* Why KuroAI Section */}
      <WhySection />

      {/* Generation Pipeline Section */}
      <PipelineSection />

      {/* System Architecture Section */}
      <ArchitectureSection />

      {/* Multi-Agent Intelligence Section */}
      <AgentsSection />

      {/* Live Interactive Centerpiece Demo */}
      <GenerationDemo />

      {/* Engineering Metrics Section */}
      <MetricsSection />
    </div>
  );
}
