import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGoogleLogin } from '@react-oauth/google';
import './AuthModal.css';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAuthSuccess: (token: string, username: string) => void;
  initialMode?: 'login' | 'signup';
}

const AuthModal = ({ isOpen, onClose, onAuthSuccess, initialMode = 'login' }: AuthModalProps) => {
  const [mode, setMode] = useState<'login' | 'signup'>(initialMode);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const overlayRef = useRef<HTMLDivElement>(null);
  const API_BASE = 'http://localhost:8080/api/auth';
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

  const loginWithGoogle = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      setLoading(true);
      setError('');
      try {
        const res = await fetch(`https://www.googleapis.com/oauth2/v3/userinfo?access_token=${tokenResponse.access_token}`);
        if (!res.ok) throw new Error('Failed to fetch user profile from Google');
        const userInfo = await res.json();
        await selectGoogleAccount(userInfo.email, userInfo.name || userInfo.given_name);
      } catch (err: any) {
        setError(err.message || 'Google login failed');
        setLoading(false);
      }
    },
    onError: (error) => {
      console.error(error);
      setError('Google authentication was cancelled or failed.');
    }
  });

  const handleSocialLogin = (provider: string) => {
    if (provider === 'Google') {
      if (!googleClientId || googleClientId.includes('YOUR_GOOGLE_CLIENT_ID')) {
        setError('Google Client ID is not configured. Please define VITE_GOOGLE_CLIENT_ID in your frontend/.env file.');
        return;
      }
      loginWithGoogle();
    } else {
      setError('GitHub authentication is currently in sandbox. Please use Google sign-in.');
    }
  };

  const selectGoogleAccount = async (accountEmail: string, displayName: string) => {
    setLoading(true);
    setError('');
    const derivedUsername = displayName.replace(/\s+/g, '_') || accountEmail.split('@')[0];
    const derivedPassword = `GoogleAuthSecretPassword123!`;

    try {
      // 1. Try register silently
      await fetch(`${API_BASE}/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: derivedUsername,
          email: accountEmail,
          password: derivedPassword
        })
      });

      // 2. Perform signin
      const signinRes = await fetch(`${API_BASE}/signin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: derivedUsername,
          password: derivedPassword
        })
      });
      const data = await signinRes.json();
      if (!signinRes.ok) throw new Error(data.message || 'Google authentication failed');

      onAuthSuccess(data.token, data.username);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to authenticate with Google');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { setMode(initialMode); setError(''); }, [initialMode, isOpen]);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [onClose]);

  const resetForm = () => { setUsername(''); setEmail(''); setPassword(''); setError(''); };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const endpoint = mode === 'login' ? `${API_BASE}/signin` : `${API_BASE}/signup`;
      const body = mode === 'login' ? { username, password } : { username, email, password };
      const response = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || 'Authentication failed');
      if (mode === 'login') { onAuthSuccess(data.token, data.username); onClose(); }
      else { setMode('login'); resetForm(); }
    } catch (err: any) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          ref={overlayRef}
          className="auth-modal-overlay"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          onClick={(e) => { if (e.target === overlayRef.current) onClose(); }}
        >
          <motion.div
            className="auth-modal"
            initial={{ opacity: 0, scale: 0.88, y: 40 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.88, y: 40 }}
            transition={{ duration: 0.35, type: 'spring', stiffness: 200, damping: 25 }}
          >
            <div className="am-glow am-glow-1" />
            <div className="am-glow am-glow-2" />

            <button className="am-close" onClick={onClose} aria-label="Close">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" />
              </svg>
            </button>

            <div className="am-logomark">
              <svg viewBox="0 0 36 36" fill="none">
                <defs>
                  <linearGradient id="amGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#ff00ff" /><stop offset="100%" stopColor="#7b2ff7" />
                  </linearGradient>
                </defs>
                <polygon points="18,2 34,11 34,25 18,34 2,25 2,11" stroke="url(#amGrad)" strokeWidth="1.5" fill="none" />
                <circle cx="18" cy="18" r="6" fill="url(#amGrad)" opacity="0.9" />
              </svg>
            </div>

            <div className="am-tabs">
              <button className={`am-tab ${mode === 'login' ? 'active' : ''}`} onClick={() => { setMode('login'); setError(''); }}>Sign In</button>
              <button className={`am-tab ${mode === 'signup' ? 'active' : ''}`} onClick={() => { setMode('signup'); setError(''); }}>Sign Up</button>
              <div className={`am-tab-indicator ${mode === 'signup' ? 'right' : ''}`} />
            </div>

            <AnimatePresence mode="wait">
              <motion.div key={mode} initial={{ opacity: 0, x: mode === 'signup' ? 20 : -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: mode === 'signup' ? -20 : 20 }} transition={{ duration: 0.2 }} className="am-heading">
                <h2>{mode === 'login' ? 'Welcome Back' : 'Create Account'}</h2>
                <p>{mode === 'login' ? 'Sign in to continue your creative journey' : 'Join thousands of manga creators using KuroAi'}</p>
              </motion.div>
            </AnimatePresence>

            <form onSubmit={handleSubmit} className="am-form">
              <div className="am-field">
                <label htmlFor="am-username">Username</label>
                <div className="am-input-wrap">
                  <svg className="am-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
                  </svg>
                  <input id="am-username" type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="your_username" required autoComplete="username" />
                </div>
              </div>

              <AnimatePresence>
                {mode === 'signup' && (
                  <motion.div className="am-field" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.25 }} style={{ overflow: 'hidden' }}>
                    <label htmlFor="am-email">Email</label>
                    <div className="am-input-wrap">
                      <svg className="am-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" /><polyline points="22,6 12,13 2,6" />
                      </svg>
                      <input id="am-email" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" required={mode === 'signup'} />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="am-field">
                <label htmlFor="am-password">Password</label>
                <div className="am-input-wrap">
                  <svg className="am-field-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                  <input id="am-password" type={showPassword ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required minLength={6} />
                  <button type="button" className="am-show-pw" onClick={() => setShowPassword(!showPassword)} tabIndex={-1}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      {showPassword ? <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24M1 1l22 22" strokeLinecap="round" /> : <><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" /></>}
                    </svg>
                  </button>
                </div>
              </div>

              {mode === 'login' && <div className="am-forgot"><a href="#">Forgot password?</a></div>}

              <AnimatePresence>
                {error && (
                  <motion.div className="am-error" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" /></svg>
                    {error}
                  </motion.div>
                )}
              </AnimatePresence>

              <motion.button type="submit" className="am-submit" disabled={loading} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}>
                {loading ? <span className="am-spinner" /> : <>{mode === 'login' ? 'Sign In →' : 'Create Account →'}</>}
              </motion.button>
            </form>

            <div className="am-divider"><span>or continue with</span></div>
            <div className="am-socials">
              {['Google', 'GitHub'].map(provider => (
                <button key={provider} className="am-social-btn" type="button" onClick={() => handleSocialLogin(provider)}>
                  {provider === 'Google' && <svg viewBox="0 0 24 24" width="18" fill="currentColor"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>}
                  {provider === 'GitHub' && <svg viewBox="0 0 24 24" width="18" fill="currentColor"><path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/></svg>}
                  {provider}
                </button>
              ))}
            </div>
            <p className="am-terms">By continuing, you agree to our <a href="#">Terms</a> and <a href="#">Privacy Policy</a></p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default AuthModal;
