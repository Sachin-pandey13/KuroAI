import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import gsap from 'gsap';
import './Header.css';

interface HeaderProps {
  onGoHome: () => void;
  isLoggedIn: boolean;
  username: string;
  onLogout: () => void;
  onLoginClick: (mode: 'login' | 'signup') => void;
}

const navLinks = [
  { label: 'Why KuroAI', href: '#why' },
  { label: 'Features', href: '#features' },
  { label: 'Architecture', href: '#architecture' },
  { label: 'Pipeline', href: '#pipeline' },
  { label: 'Agents', href: '#agents' },
  { label: 'Metrics', href: '#metrics' },
];

const Header = ({ onGoHome, isLoggedIn, username, onLogout, onLoginClick }: HeaderProps) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const headerRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 80);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleNavClick = (href: string) => {
    setMobileMenuOpen(false);
    onGoHome(); // Ensure we are on landing view
    setTimeout(() => {
      const el = document.querySelector(href);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);
  };

  // GSAP magnetic effect on CTA buttons
  const handleMagnet = (e: React.MouseEvent<HTMLButtonElement | HTMLAnchorElement>) => {
    const btn = e.currentTarget;
    const rect = btn.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = (e.clientX - cx) * 0.3;
    const dy = (e.clientY - cy) * 0.3;
    gsap.to(btn, { x: dx, y: dy, duration: 0.3, ease: 'power2.out' });
  };

  const handleMagnetLeave = (e: React.MouseEvent<HTMLButtonElement | HTMLAnchorElement>) => {
    gsap.to(e.currentTarget, { x: 0, y: 0, duration: 0.5, ease: 'elastic.out(1, 0.5)' });
  };

  return (
    <header ref={headerRef} className={`app-header ${scrolled ? 'scrolled' : ''}`}>
      <div className="header-content">
        {/* Brand */}
        <motion.div
          className="brand"
          onClick={() => {
            onGoHome();
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          role="button"
          tabIndex={0}
          aria-label="KuroAI Home"
        >
          {/* Logo Eye Symbol */}
          <svg className="logo-icon-svg" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M 10,50 C 30,20 70,20 90,50 C 70,80 30,80 10,50 Z" stroke="#c0392b" strokeWidth="6" fill="none" />
            <circle cx="50" cy="50" r="18" fill="#c0392b" />
            <path d="M 50,34 A 16 16 0 0 1 66,42" stroke="#fff" strokeWidth="3" strokeLinecap="round" />
            <circle cx="50" cy="50" r="6" fill="#050505" />
          </svg>
          <div className="brand-name">
            KURO<span className="accent-red">AI</span>
          </div>
        </motion.div>

        {/* Nav links (desktop) */}
        <nav className="header-nav" aria-label="Main Navigation">
          {navLinks.map((item) => (
            <button
              key={item.label}
              className="nav-link"
              onClick={() => handleNavClick(item.href)}
            >
              {item.label}
            </button>
          ))}
          <a
            href="https://github.com/Sachin-pandey13/KuroAI"
            target="_blank"
            rel="noopener noreferrer"
            className="nav-link github-link"
          >
            GitHub ↗
          </a>
        </nav>

        {/* Right Section */}
        <motion.div
          className="header-right-section"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          {isLoggedIn ? (
            <div
              className="user-profile-container"
              onMouseEnter={() => setIsDropdownOpen(true)}
              onMouseLeave={() => setIsDropdownOpen(false)}
            >
              <div className="user-greeting">
                <span className="greeting-text">Hi, {username}</span>
              </div>
              <div className="avatar">
                <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${username}`} alt="User Profile" />
              </div>
              <AnimatePresence>
                {isDropdownOpen && (
                  <motion.div
                    className="profile-dropdown"
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ul>
                      <motion.li whileHover={{ x: 5 }}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
                        </svg>
                        Profile
                      </motion.li>
                      <li className="divider" />
                      <motion.li className="logout" onClick={onLogout} whileHover={{ x: 5 }}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" />
                        </svg>
                        Log Out
                      </motion.li>
                    </ul>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ) : (
            <div className="auth-cta-row">
              <motion.button
                className="login-btn-ghost"
                onClick={() => onLoginClick('login')}
                onMouseMove={handleMagnet}
                onMouseLeave={handleMagnetLeave}
                whileTap={{ scale: 0.97 }}
              >
                Sign In
              </motion.button>
              <motion.button
                className="login-btn"
                onClick={() => onLoginClick('signup')}
                onMouseMove={handleMagnet}
                onMouseLeave={handleMagnetLeave}
                whileTap={{ scale: 0.97 }}
              >
                Get Started
              </motion.button>
            </div>
          )}

          {/* Mobile Menu Toggle */}
          <button
            type="button"
            className="mobile-menu-btn"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
          >
            <span className={`hamburger ${mobileMenuOpen ? 'open' : ''}`} />
          </button>
        </motion.div>
      </div>

      {/* Mobile Menu Drawer */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            className="mobile-drawer"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="mobile-drawer-inner">
              {navLinks.map((item) => (
                <button
                  key={item.label}
                  className="mobile-nav-link"
                  onClick={() => handleNavClick(item.href)}
                >
                  {item.label}
                </button>
              ))}
              <a
                href="https://github.com/Sachin-pandey13/KuroAI"
                target="_blank"
                rel="noopener noreferrer"
                className="mobile-nav-link github-link"
              >
                GitHub Repository ↗
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
};

export default Header;
