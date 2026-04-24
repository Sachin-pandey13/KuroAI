import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './Header.css';

interface HeaderProps {
  onGoHome: () => void;
  isLoggedIn: boolean;
  username: string;
  onLogout: () => void;
  onLoginClick: () => void;
}

const Header = ({ onGoHome, isLoggedIn, username, onLogout, onLoginClick }: HeaderProps) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  return (
    <header className="app-header">
      <div className="header-content">
        <motion.div 
          className="brand"
          onClick={onGoHome}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
          </div>
          <div className="brand-name fire-text">
            {"KuroAi".split("").map((letter, index) => (
              <span key={index} style={{ animationDelay: `${index * 0.1}s` }}>
                {letter}
              </span>
            ))}
          </div>
        </motion.div>

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
                      <motion.li whileHover={{ x: 5, backgroundColor: 'rgba(255,255,255,0.1)' }}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                          <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                        Profile
                      </motion.li>
                      <motion.li whileHover={{ x: 5, backgroundColor: 'rgba(255,255,255,0.1)' }}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="12" cy="12" r="3"></circle>
                          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                        </svg>
                        Settings
                      </motion.li>
                      <li className="divider"></li>
                      <motion.li className="logout" onClick={onLogout} whileHover={{ x: 5, backgroundColor: 'rgba(239, 68, 68, 0.1)' }}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                          <polyline points="16 17 21 12 16 7"></polyline>
                          <line x1="21" y1="12" x2="9" y2="12"></line>
                        </svg>
                        Log Out
                      </motion.li>
                    </ul>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ) : (
            <motion.button 
              className="login-btn"
              onClick={onLoginClick}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Sign In
            </motion.button>
          )}
        </motion.div>
      </div>
    </header>
  );
};

export default Header;
