import Header from './components/Header';
import Footer from './components/Footer';
import ChatInterface from './components/ChatInterface';
import LandingPage from './components/LandingPage';
import TemplatePage from './components/TemplatePage';
import AuthPage from './components/AuthPage';
import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import './index.css';

interface TemplateData {
  title?: string;
  pages: string[];
  scenes: Array<{
    dialogue: Array<{ speaker: string; text: string }>;
  }>;
}

function App() {
  const [currentView, setCurrentView] = useState<string>('landing');
  const [templateData, setTemplateData] = useState<TemplateData | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(localStorage.getItem('kuroai_token'));
  const [username, setUsername] = useState<string>(localStorage.getItem('kuroai_user') || '');

  const handleGoHome = () => setCurrentView('landing');

  const handleLogin = (token: string, user: string) => {
    localStorage.setItem('kuroai_token', token);
    localStorage.setItem('kuroai_user', user);
    setAuthToken(token);
    setUsername(user);
    setCurrentView('landing');
  };

  const handleLogout = () => {
    localStorage.removeItem('kuroai_token');
    localStorage.removeItem('kuroai_user');
    setAuthToken(null);
    setUsername('');
    setCurrentView('landing');
  };

  return (
    <>
      {/* Background elements */}
      <div className="background-container">
        <div className="bg-blob blob-1"></div>
        <div className="bg-blob blob-2"></div>
      </div>
      
      <div className="app-layout">
        <Header 
          onGoHome={handleGoHome} 
          isLoggedIn={!!authToken} 
          username={username}
          onLogout={handleLogout}
          onLoginClick={() => setCurrentView('auth')}
        />
        
        <main className="main-content">
          <AnimatePresence mode="wait">
            {currentView === 'auth' && (
              <motion.div 
                key="auth"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, y: -50 }}
                transition={{ duration: 0.5, ease: "easeInOut" }}
                style={{ width: '100%', display: 'flex', justifyContent: 'center' }}
              >
                <AuthPage onAuthSuccess={handleLogin} onGoHome={handleGoHome} />
              </motion.div>
            )}

            {currentView === 'landing' && (
              <motion.div 
                key="landing"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, y: -50 }}
                transition={{ duration: 0.5, ease: "easeInOut" }}
                style={{ width: '100%' }}
              >
                <LandingPage onTryYours={() => {
                  if (authToken) {
                    setCurrentView('chat');
                  } else {
                    setCurrentView('auth');
                  }
                }} />
              </motion.div>
            )}
            
            {currentView === 'chat' && (
              <motion.div 
                key="chat"
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -50 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
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
                transition={{ duration: 0.6, ease: "easeOut" }}
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
