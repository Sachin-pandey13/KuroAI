import { useState, useRef, useEffect } from 'react';
import type { Variants } from 'framer-motion';
import { motion, AnimatePresence } from 'framer-motion';
import './ChatInterface.css';

interface Message {
  id: number;
  sender: 'ai' | 'user';
  text: string;
  timestamp: string;
  isError?: boolean;
}

interface ChatInterfaceProps {
  onGoHome: () => void;
  authToken: string | null;
  onGenerationComplete: (data: any) => void;
}

const PROMPT_SUGGESTIONS = [
  { icon: '⚔️', text: 'A lone samurai discovers a cursed blade that grants power but corrupts the soul.' },
  { icon: '🌸', text: 'In a futuristic Tokyo, a girl with no memories wakes up with the power to rewind time.' },
  { icon: '🌊', text: 'Two rival pirates forge an unlikely alliance to find the treasure at the edge of the world.' },
  { icon: '🔮', text: 'An ancient demon is sealed inside a teenager who must learn to control its power.' },
];

const ChatInterface = ({ onGoHome, authToken, onGenerationComplete }: ChatInterfaceProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      sender: 'ai',
      text: 'Hello! I am Kuro, your AI manga creation companion. Describe your story — a setting, a conflict, a character — and I will transform it into a visual manga panel sequence.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [progressLabel, setProgressLabel] = useState('Generating your manga...');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [msgCount, setMsgCount] = useState(1);

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });

  useEffect(() => { scrollToBottom(); }, [messages, isGenerating]);

  // Auto-resize textarea
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (inputValue.trim() && !isGenerating) handleSend();
    }
  };

  const handleSend = async () => {
    const story = inputValue.trim();
    if (!story || isGenerating) return;

    const userMsg: Message = {
      id: Date.now(),
      sender: 'user',
      text: story,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setMsgCount(c => c + 1);
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setIsGenerating(true);

    // Animate progress labels
    const labels = [
      'Analysing your story...',
      'Scripting panels & dialogue...',
      'Generating manga scenes...',
      'Rendering panel artwork...',
      'Assembling your manga...',
    ];
    let labelIdx = 0;
    setProgressLabel(labels[0]);
    const labelInterval = setInterval(() => {
      labelIdx = (labelIdx + 1) % labels.length;
      setProgressLabel(labels[labelIdx]);
    }, 2500);

    try {
      const response = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {})
        },
        body: JSON.stringify({ story })
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      const data = await response.json();

      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'ai',
        text: '✨ Your manga has been generated! Transitioning to the panel builder...',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);

      setTimeout(() => onGenerationComplete(data), 900);

    } catch (err: any) {
      const isNetworkError = err.message === 'Failed to fetch' || err.message.includes('NetworkError');
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'ai',
        isError: true,
        text: isNetworkError
          ? '⚠️ Cannot reach the KuroAI generation server. Make sure the Python API is running on port 8000:\n\ncd kuroai-genai-pipeline\npython -m uvicorn api.main:app --port 8000'
          : `⚠️ Generation failed: ${err.message}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } finally {
      clearInterval(labelInterval);
      setIsGenerating(false);
    }
  };

  const messageVariants: Variants = {
    hidden: { opacity: 0, y: 16, scale: 0.97 },
    visible: {
      opacity: 1, y: 0, scale: 1,
      transition: { type: 'spring', stiffness: 280, damping: 22 }
    }
  };

  const charCount = inputValue.length;
  const MAX_CHARS = 1000;

  return (
    <div className="chat-workspace">
      {/* ── SIDEBAR ── */}
      <div className="chat-sidebar">
        {/* AI Profile */}
        <div className="chat-sidebar-card">
          <div className="sidebar-label">Your Assistant</div>
          <div className="sidebar-ai-profile">
            <div className="sidebar-ai-avatar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
              </svg>
            </div>
            <div>
              <div className="sidebar-ai-name">Kuro AI</div>
              <div className="sidebar-ai-role">Manga Generation Engine</div>
            </div>
          </div>
          <div className="sidebar-status">
            <div className="sidebar-status-dot" />
            Online · Ready to create
          </div>
        </div>

        {/* Prompt Suggestions */}
        <div className="chat-sidebar-card" style={{ flex: 1 }}>
          <div className="sidebar-label">Story Starters</div>
          <div className="prompt-chips">
            {PROMPT_SUGGESTIONS.map((p, i) => (
              <button
                key={i}
                className="prompt-chip"
                onClick={() => {
                  setInputValue(p.text);
                  textareaRef.current?.focus();
                }}
              >
                <span className="prompt-chip-icon">{p.icon}</span>
                {p.text}
              </button>
            ))}
          </div>
        </div>

        {/* Session Stats */}
        <div className="chat-sidebar-card">
          <div className="sidebar-label">Session</div>
          <div className="chat-stats">
            <div className="chat-stat-row">
              <span className="chat-stat-label">Messages sent</span>
              <span className="chat-stat-value">{msgCount}</span>
            </div>
            <div className="chat-stat-row">
              <span className="chat-stat-label">Model</span>
              <span className="chat-stat-value">Kuro Gen 1</span>
            </div>
            <div className="chat-stat-row">
              <span className="chat-stat-label">Status</span>
              <span className="chat-stat-value" style={{ color: isGenerating ? '#ffaa44' : '#00ff88' }}>
                {isGenerating ? 'Generating...' : 'Ready'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* ── MAIN CHAT ── */}
      <div className="chat-container">
        {/* Header */}
        <div className="chat-interface-header">
          <div className="chat-header-left">
            <button className="chat-back-btn" onClick={onGoHome}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
              Back
            </button>
            <div className="chat-header-title">
              <div className="chat-status-dot" style={{ animation: 'statusPulse 2s ease-in-out infinite' }} />
              <div>
                <div className="chat-header-title-text">Kuro AI Assistant</div>
                <div className="chat-header-subtitle">Manga Story Generator</div>
              </div>
            </div>
          </div>
          <div className="chat-header-actions">
            <div className="chat-header-badge">✦ AI Powered</div>
          </div>
        </div>

        {/* Story mode banner */}
        <div className="story-mode-banner">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 20h9M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
          </svg>
          Story Mode — Describe a narrative and Kuro will generate manga panels, dialogue, and scenes
        </div>

        {/* Messages */}
        <div className="chat-history">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                className={`message-wrapper ${msg.sender}`}
                variants={messageVariants}
                initial="hidden"
                animate="visible"
                layout
              >
                {msg.sender === 'ai' && (
                  <div className="message-avatar ai">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                    </svg>
                  </div>
                )}
                <div className="message-content">
                  <div className={`message-bubble${msg.isError ? ' error-bubble' : ''}`}>
                    {msg.text}
                  </div>
                  <div className="message-meta">
                    <span className="message-sender">{msg.sender === 'ai' ? 'Kuro' : 'You'}</span>
                    <span className="message-time">{msg.timestamp}</span>
                  </div>
                </div>
                {msg.sender === 'user' && (
                  <div className="message-avatar user">
                    <img
                      src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${authToken ? 'user' : 'guest'}`}
                      alt="User"
                    />
                  </div>
                )}
              </motion.div>
            ))}

            {/* Generating progress */}
            {isGenerating && (
              <motion.div
                className="message-wrapper ai"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                layout
              >
                <div className="message-avatar ai">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                  </svg>
                </div>
                <div className="message-content">
                  <div className="message-bubble">
                    <div className="generation-progress">
                      <div className="progress-spinner" />
                      <span className="generation-progress-text">{progressLabel}</span>
                    </div>
                  </div>
                  <div className="message-meta">
                    <span className="message-sender">Kuro</span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="chat-input-area">
          <div className="chat-input-wrapper">
            <textarea
              ref={textareaRef}
              className="chat-input"
              value={inputValue}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Describe your story or characters..."
              disabled={isGenerating}
              rows={1}
              maxLength={MAX_CHARS}
            />
            <div className="chat-input-actions">
              {charCount > 0 && (
                <span className={`chat-char-count${charCount > MAX_CHARS * 0.85 ? ' warn' : ''}`}>
                  {charCount}/{MAX_CHARS}
                </span>
              )}
              <motion.button
                className="chat-submit-btn"
                type="button"
                onClick={handleSend}
                disabled={!inputValue.trim() || isGenerating}
                whileHover={(!inputValue.trim() || isGenerating) ? {} : { scale: 1.06 }}
                whileTap={(!inputValue.trim() || isGenerating) ? {} : { scale: 0.94 }}
              >
                {isGenerating ? (
                  <div className="progress-spinner" style={{ width: 16, height: 16 }} />
                ) : (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <line x1="22" y1="2" x2="11" y2="13"/>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                  </svg>
                )}
              </motion.button>
            </div>
          </div>
          <div className="chat-input-hint">
            <kbd>Enter</kbd> to send &nbsp;·&nbsp; <kbd>Shift+Enter</kbd> for new line
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
