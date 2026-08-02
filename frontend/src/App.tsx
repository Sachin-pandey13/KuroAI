import { useState, useCallback } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import Header from './components/Header';
import Footer from './components/Footer';
import ChatInterface from './components/ChatInterface';
import LandingPage from './components/LandingPage';
import TemplatePage from './components/TemplatePage';
import AuthPage from './components/AuthPage';
import CinematicLoader from './components/CinematicLoader';
import AuroraCanvas from './components/AuroraCanvas';
import AuthModal from './components/AuthModal';
import './index.css';

interface TemplateData {
  title?: string;
  pages: string[];
  scenes: Array<{ dialogue: Array<{ speaker: string; text: string }> }>;
}

function App() {
  const [loaded, setLoaded] = useState(false);
  const [currentView, setCurrentView] = useState<string>('landing');
  const [templateData, setTemplateData] = useState<TemplateData | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(localStorage.getItem('kuroai_token'));
  const [username, setUsername] = useState<string>(localStorage.getItem('kuroai_user') || '');
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState<'login' | 'signup'>('login');

  const handleGoHome = () => setCurrentView('landing');

  const handleLogin = useCallback((token: string, user: string) => {
    localStorage.setItem('kuroai_token', token);
    localStorage.setItem('kuroai_user', user);
    setAuthToken(token);
    setUsername(user);
    setCurrentView('landing');
    setAuthModalOpen(false);
  }, []);

  const handleLogout = useCallback(() => {
    localStorage.removeItem('kuroai_token');
    localStorage.removeItem('kuroai_user');
    setAuthToken(null);
    setUsername('');
    setCurrentView('landing');
  }, []);

  const openAuth = useCallback((mode: 'login' | 'signup') => {
    setAuthModalMode(mode);
    setAuthModalOpen(true);
  }, []);

  const handleTryYours = useCallback(() => {
    if (authToken) {
      setCurrentView('chat');
    } else {
      openAuth('signup');
    }
  }, [authToken, openAuth]);

  // Show cinematic loader first
  if (!loaded) {
    return <CinematicLoader onComplete={() => setLoaded(true)} />;
  }

  return (
    <>
      {/* Skip to Content for Keyboard Accessibility */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      {/* Aurora WebGL shader background */}
      <AuroraCanvas />

      {/* Auth Modal (portal-style popup) */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={handleLogin}
        initialMode={authModalMode}
      />

      <div className="app-layout">
        <Header
          onGoHome={handleGoHome}
          isLoggedIn={!!authToken}
          username={username}
          onLogout={handleLogout}
          onLoginClick={openAuth}
        />

        <main className="main-content">
          <AnimatePresence mode="wait">
            {currentView === 'auth' && (
              <motion.div
                key="auth"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, y: -50 }}
                transition={{ duration: 0.5 }}
                style={{ width: '100%', display: 'flex', justifyContent: 'center' }}
              >
                <AuthPage onAuthSuccess={handleLogin} onGoHome={handleGoHome} />
              </motion.div>
            )}

            {currentView === 'landing' && (
              <motion.div
                key="landing"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0, y: -30 }}
                transition={{ duration: 0.5 }}
                style={{ width: '100%' }}
              >
                <LandingPage onTryYours={handleTryYours} onOpenAuth={openAuth} />
              </motion.div>
            )}

            {currentView === 'chat' && (
              <motion.div
                key="chat"
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -50 }}
                transition={{ duration: 0.5 }}
                style={{ width: '100%', display: 'flex', justifyContent: 'center' }}
              >
                <ChatInterface
                  onGoHome={handleGoHome}
                  authToken={authToken}
                  onGenerationComplete={(data: TemplateData) => {
                    setTemplateData(data);
                    setCurrentView('template');
                  }}
                />
              </motion.div>
            )}

            {currentView === 'template' && templateData && (
              <motion.div
                key="template"
                initial={{ opacity: 0, scale: 1.05 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.6 }}
                style={{ width: '100%', display: 'flex', justifyContent: 'center' }}
              >
                <TemplatePage storyData={templateData} onGoHome={() => setCurrentView('chat')} />
              </motion.div>
            )}
          </AnimatePresence>
        </main>

        <Footer />
      </div>
    </>
  );
}

export default App;
