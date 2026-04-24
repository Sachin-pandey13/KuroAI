import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ChatInterface.css';

interface Message {
  id: number;
  sender: 'ai' | 'user';
  text: string;
  timestamp: string;
}

interface ChatInterfaceProps {
  onGoHome: () => void;
  authToken: string | null;
  onGenerationComplete: (data: any) => void;
}

const ChatInterface = ({ onGoHome, authToken, onGenerationComplete }: ChatInterfaceProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      sender: 'ai',
      text: 'Hello! I am Kuro, your AI storytelling companion. What magical tale shall we weave today?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const newUserMsg: Message = {
      id: Date.now(),
      sender: 'user',
      text: inputValue.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setInputValue('');
    setIsTyping(true);

    const fetchManga = async () => {
      try {
        // Route directly to Python FastAPI backend
        const response = await fetch('http://localhost:8000/api/generate', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {})
          },
          body: JSON.stringify({ story: newUserMsg.text })
        });
        
        if (!response.ok) {
           throw new Error(`Error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Notify parent to transition to Interactive Template Builder!
        onGenerationComplete(data);
        
      } catch (err: any) {
        setMessages((prev) => [...prev, {
          id: Date.now() + 1,
          sender: 'ai',
          text: `I'm sorry, my magic faltered. Ensure the KuroAI backend is running. (${err.message})`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }]);
      } finally {
        setIsTyping(false);
      }
    };
    
    fetchManga();
  };

  const messageVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.95 },
    visible: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: { type: 'spring', stiffness: 250, damping: 20 }
    }
  };

  return (
    <div className="chat-container glass-card">
      {/* Back Button Header */}
      <div className="chat-interface-header">
        <button className="chat-back-btn" onClick={onGoHome}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
          Back
        </button>
        <div className="chat-header-title">
          <div className="chat-status-dot"></div>
          Kuro AI Assistant
        </div>
      </div>

      <div className="chat-history">
        <AnimatePresence initial={false}>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              className={`message-wrapper ${message.sender}`}
              variants={messageVariants}
              initial="hidden"
              animate="visible"
              layout
            >
              {message.sender === 'ai' && (
                <div className="message-avatar ai">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                  </svg>
                </div>
              )}
              
              <div className="message-content">
                <div className="message-bubble">
                  {message.text}
                </div>
                <div className="message-time">{message.timestamp}</div>
              </div>

              {message.sender === 'user' && (
                <div className="message-avatar user">
                  <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="User" />
                </div>
              )}
            </motion.div>
          ))}
          
          {isTyping && (
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
                  <div className="message-bubble typing-indicator">
                    <motion.span animate={{ opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 1.4, delay: 0 }}>.</motion.span>
                    <motion.span animate={{ opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 1.4, delay: 0.2 }}>.</motion.span>
                    <motion.span animate={{ opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 1.4, delay: 0.4 }}>.</motion.span>
                  </div>
                </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <form onSubmit={handleSendMessage} className="chat-form">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your story here..."
            className="chat-input"
            disabled={isTyping}
          />
          <motion.button 
            type="submit" 
            className="chat-submit-btn"
            disabled={!inputValue.trim() || isTyping}
            whileHover={(!inputValue.trim() || isTyping) ? {} : { scale: 1.05 }}
            whileTap={(!inputValue.trim() || isTyping) ? {} : { scale: 0.95 }}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </motion.button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
