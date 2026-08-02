import { motion } from 'framer-motion';
import EmberCanvas from './EmberCanvas';
import './Footer.css';

const Footer = () => {
  const year = new Date().getFullYear();

  return (
    <footer className="app-footer">
      {/* Floating Ember Particle Layer */}
      <EmberCanvas />

      {/* Burn Edge Line Accent */}
      <div className="burn-edge-line" aria-hidden="true" />

      <div className="footer-content">
        {/* Brand Column */}
        <div className="footer-brand">
          <div className="footer-logo-row">
            <svg className="footer-eye-svg" viewBox="0 0 100 100" fill="none">
              <path d="M 10,50 C 30,20 70,20 90,50 C 70,80 30,80 10,50 Z" stroke="#c0392b" strokeWidth="6" fill="none" />
              <circle cx="50" cy="50" r="18" fill="#c0392b" />
              <circle cx="50" cy="50" r="6" fill="#050505" />
            </svg>
            <span className="footer-brand-name">
              KURO<span className="accent-red">AI</span>
            </span>
          </div>
          <p className="footer-tagline">
            Generative Multi-Agent Manga Engine. Transform story ideas into publication-ready manga art.
          </p>
        </div>

        {/* Links Column */}
        <div className="footer-links-group">
          <div className="footer-col">
            <h4>NAVIGATION</h4>
            <a href="#why">Why KuroAI</a>
            <a href="#features">Features</a>
            <a href="#architecture">Architecture</a>
            <a href="#pipeline">Pipeline</a>
          </div>

          <div className="footer-col">
            <h4>ENGINEERING</h4>
            <a href="https://github.com/Sachin-pandey13/KuroAI" target="_blank" rel="noopener noreferrer">
              GitHub Repository ↗
            </a>
            <a href="#metrics">25/25 Health Gate</a>
            <a href="#agents">Agent Contracts</a>
          </div>
        </div>
      </div>

      <div className="footer-bottom-bar">
        <p className="footer-copy">
          &copy; {year} KuroAI Engineering. Open-source under MIT License.
        </p>
      </div>
    </footer>
  );
};

export default Footer;
