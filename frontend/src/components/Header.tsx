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

const Header = ({ onGoHome, isLoggedIn, username, onLogout, onLoginClick }: HeaderProps) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const headerRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // GSAP magnetic effect on CTA buttons
  const handleMagnet = (e: React.MouseEvent<HTMLButtonElement>) => {
    const btn = e.currentTarget;
    const rect = btn.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = (e.clientX - cx) * 0.3;
    const dy = (e.clientY - cy) * 0.3;
    gsap.to(btn, { x: dx, y: dy, duration: 0.3, ease: 'power2.out' });
  };
  const handleMagnetLeave = (e: React.MouseEvent<HTMLButtonElement>) => {
    gsap.to(e.currentTarget, { x: 0, y: 0, duration: 0.5, ease: 'elastic.out(1, 0.5)' });
  };

  return (
    <header ref={headerRef} className={`app-header ${scrolled ? 'scrolled' : ''}`}>
      <div className="header-content">
        {/* Brand */}
        <motion.div
          className="brand"
          onClick={onGoHome}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="logo-icon">
            <svg viewBox="0 0 36 36" fill="none">
              <defs>
                <linearGradient id="hLogoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#ff00ff" /><stop offset="100%" stopColor="#7b2ff7" />
                </linearGradient>
              </defs>
              <polygon points="18,2 34,11 34,25 18,34 2,25 2,11" stroke="url(#hLogoGrad)" strokeWidth="1.5" fill="none" />
              <circle cx="18" cy="18" r="6" fill="url(#hLogoGrad)" opacity="0.9" />
            </svg>
          </div>
          <div className="brand-name fire-text">
            {'KuroAi'.split('').map((letter, index) => (
              <span key={index} style={{ animationDelay: `${index * 0.1}s` }}>{letter}</span>
            ))}
          </div>
        </motion.div>

        {/* Nav links (desktop) */}
        <nav className="header-nav">
          {['Features', 'Gallery', 'Pricing'].map(item => (
            <button key={item} className="nav-link" onClick={onGoHome}>{item}</button>
          ))}
        </nav>

        {/* Right section */}
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
                      <motion.li whileHover={{ x: 5 }}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
                        </svg>
                        Settings
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
        </motion.div>
      </div>
    </header>
  );
};

export default Header;
