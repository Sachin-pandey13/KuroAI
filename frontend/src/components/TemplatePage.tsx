import React, { useRef } from 'react';
import Draggable from 'react-draggable';
import html2canvas from 'html2canvas';
import { motion } from 'framer-motion';
import './TemplatePage.css';

interface Dialogue {
  speaker: string;
  text: string;
}

interface StoryData {
  title?: string;
  pages: string[];
  scenes: Array<{ dialogue: Dialogue[] }>;
}

interface DraggableBubbleProps {
  dlg: Dialogue;
}

const DraggableBubble = ({ dlg }: DraggableBubbleProps) => {
  const nodeRef = useRef<HTMLDivElement>(null);
  return (
    <Draggable nodeRef={nodeRef as any} bounds="parent">
      <div ref={nodeRef} className="speech-bubble">
        <div className="bubble-speaker">{dlg.speaker}</div>
        <div className="bubble-text">{dlg.text}</div>
      </div>
    </Draggable>
  );
};

interface TemplatePageProps {
  storyData: StoryData;
  onGoHome: () => void;
}

const TemplatePage = ({ storyData, onGoHome }: TemplatePageProps) => {
  const templateRef = useRef<HTMLDivElement>(null);

  const handleDownload = async () => {
    if (templateRef.current) {
      await new Promise(r => setTimeout(r, 100));
      
      const canvas = await html2canvas(templateRef.current, {
        useCORS: true,
        backgroundColor: '#ffffff'
      });
      
      const image = canvas.toDataURL("image/png", 1.0);
      const link = document.createElement('a');
      link.download = `${storyData.title || 'Manga_Page'}.png`;
      link.href = image;
      link.click();
    }
  };

  return (
    <div className="template-page-container">
      <div className="template-header">
        <button className="back-btn" onClick={onGoHome}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
          Back to Chat
        </button>
        <h2 className="story-title">{storyData.title}</h2>
        <motion.button 
          className="download-btn"
          onClick={handleDownload}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          Export PNG
        </motion.button>
      </div>

      <div className="instructions">
        <p><strong>Interactive Mode:</strong> Drag the speech bubbles over the panels to arrange your perfect manga page!</p>
      </div>

      <div className="template-workspace">
        <div className="manga-canvas" ref={templateRef}>
          {storyData.pages.map((imgSrc, idx) => {
             const scene = storyData.scenes[idx] || { dialogue: [] };
             const dialogues = scene.dialogue || [];
             
             return (
               <div key={`panel-${idx}`} className="manga-panel-container">
                 <img src={imgSrc} alt={`Scene ${idx + 1}`} className="manga-panel-img" />
                 
                 {dialogues.map((dlg, dIdx) => (
                   <DraggableBubble key={`dlg-${idx}-${dIdx}`} dlg={dlg} />
                 ))}
               </div>
             );
          })}
        </div>
      </div>
    </div>
  );
};

export default TemplatePage;
