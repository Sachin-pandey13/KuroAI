import { motion } from 'framer-motion';
import './Footer.css';

const Footer = () => {
  const year = new Date().getFullYear();

  return (
    <motion.footer
      className="app-footer"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5, duration: 0.8 }}
    >
      <div className="footer-content">
        {/* Brand */}
        <div className="footer-brand">
          <svg viewBox="0 0 28 28" fill="none" className="footer-logo">
            <defs>
              <linearGradient id="fLogoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#ff00ff" />
                <stop offset="100%" stopColor="#7b2ff7" />
              </linearGradient>
            </defs>
            <polygon points="14,2 26,8 26,20 14,26 2,20 2,8" stroke="url(#fLogoGrad)" strokeWidth="1.5" fill="none" />
            <circle cx="14" cy="14" r="4.5" fill="url(#fLogoGrad)" opacity="0.85" />
          </svg>
          <span className="footer-brand-name">KuroAi</span>
        </div>

        {/* Center */}
        <p className="footer-copy">
          &copy; {year} Kuro Storycraft. All rights reserved.
        </p>

        {/* Links */}
        <div className="footer-links">
          <a href="#">Privacy</a>
          <span className="footer-dot" />
          <a href="#">Terms</a>
          <span className="footer-dot" />
          <a href="#">GitHub</a>
        </div>
      </div>
    </motion.footer>
  );
};

export default Footer;
