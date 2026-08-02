import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import gsap from 'gsap';
import './GenerationDemo.css';

const presetPrompts = [
  'A cybernetic samurai walking through neon Tokyo under torrential rain.',
  'A young sorcerer summoning an ancient dragon atop a crystal spire.',
  'A quiet morning in a Tokyo coffee shop as cherry blossoms fall outside.',
];

const mockPanels = [
  { id: 1, title: 'Panel 1: Wide Shot', desc: 'Rain glistening on neon asphalt', tag: 'SCENE_SETTING' },
  { id: 2, title: 'Panel 2: Medium Close', desc: 'Samurai gripping sword hilt', tag: 'CHARACTER' },
  { id: 3, title: 'Panel 3: Reaction', desc: 'Enemy shadow looms ahead', tag: 'DRAMA' },
  { id: 4, title: 'Panel 4: Action Slash', desc: 'Crimson spark in darkness', tag: 'CLIMAX' },
];

export default function GenerationDemo() {
  const [promptText, setPromptText] = useState(presetPrompts[0]);
  const [statusStep, setStatusStep] = useState<'idle' | 'analyzing' | 'agents' | 'rendering' | 'complete'>('idle');
  const [activeAgentIndex, setActiveAgentIndex] = useState(-1);

  const demoBoxRef = useRef<HTMLDivElement>(null);

  const handleGenerate = () => {
    if (statusStep !== 'idle' && statusStep !== 'complete') return;

    setStatusStep('analyzing');
    setActiveAgentIndex(-1);

    const tl = gsap.timeline();

    // Step 1: Analyzing
    tl.to({}, { duration: 0.8 })
      // Step 2: Agents Activating
      .call(() => {
        setStatusStep('agents');
        let idx = 0;
        const interval = setInterval(() => {
          setActiveAgentIndex(idx);
          idx++;
          if (idx >= 4) clearInterval(interval);
        }, 400);
      })
      .to({}, { duration: 1.8 })
      // Step 3: Panel Rendering
      .call(() => setStatusStep('rendering'))
      .to({}, { duration: 1.5 })
      // Step 4: Complete & Book Flip
      .call(() => setStatusStep('complete'));
  };

  return (
    <section id="demo" className="demo-section washi-strip" aria-labelledby="demo-title">
      <div className="section-container">
        <div className="section-header">
          <span className="section-eyebrow">// LIVE INTERACTIVE CENTERPIECE</span>
          <h2 id="demo-title" className="section-title">Experience the AI Engine</h2>
          <p className="section-subtitle">
            Type your story prompt below or select a preset to trigger the multi-agent generation pipeline in real time.
          </p>
        </div>

        {/* Input Control Console */}
        <div className="demo-console glass-card">
          <div className="preset-buttons">
            <span className="preset-label">PRESETS:</span>
            {presetPrompts.map((preset, idx) => (
              <button
                key={idx}
                type="button"
                className={`preset-chip ${promptText === preset ? 'active' : ''}`}
                onClick={() => setPromptText(preset)}
              >
                Preset {idx + 1}
              </button>
            ))}
          </div>

          <div className="prompt-input-row">
            <input
              type="text"
              className="prompt-input"
              value={promptText}
              onChange={(e) => setPromptText(e.target.value)}
              placeholder="Describe your manga scene..."
            />
            <button
              type="button"
              className="generate-btn"
              disabled={statusStep !== 'idle' && statusStep !== 'complete'}
              onClick={handleGenerate}
            >
              {statusStep === 'idle' || statusStep === 'complete' ? '▶ Generate Manga' : '⚡ Pipeline Running...'}
            </button>
          </div>
        </div>

        {/* Pipeline Execution Display Stage */}
        <div ref={demoBoxRef} className="demo-stage glass-card">
          {/* Status Indicator Bar */}
          <div className="pipeline-status-bar">
            <div className={`status-step ${statusStep === 'analyzing' ? 'active' : ''}`}>
              <span>1</span> NLP Analysis
            </div>
            <div className={`status-step ${statusStep === 'agents' ? 'active' : ''}`}>
              <span>2</span> Agents Active
            </div>
            <div className={`status-step ${statusStep === 'rendering' ? 'active' : ''}`}>
              <span>3</span> SD Panel Render
            </div>
            <div className={`status-step ${statusStep === 'complete' ? 'active' : ''}`}>
              <span>4</span> Book Assembled
            </div>
          </div>

          {/* Active Rendering Area */}
          <div className="stage-workspace">
            {statusStep === 'idle' && (
              <div className="stage-placeholder">
                <div className="placeholder-icon">👁️</div>
                <p>Click <strong>"Generate Manga"</strong> above to observe the multi-agent render sequence.</p>
              </div>
            )}

            {(statusStep === 'analyzing' || statusStep === 'agents') && (
              <div className="stage-agents-active">
                <div className="pulse-core">
                  <div className="core-ring" />
                  <span>AI CORE</span>
                </div>
                <div className="agent-indicator-row">
                  {['Director', 'Story', 'Layout', 'Review'].map((name, i) => (
                    <div
                      key={name}
                      className={`agent-indicator ${activeAgentIndex >= i ? 'lit' : ''}`}
                    >
                      <span className="dot" />
                      {name} Agent
                    </div>
                  ))}
                </div>
              </div>
            )}

            {(statusStep === 'rendering' || statusStep === 'complete') && (
              <div className={`manga-book-container ${statusStep === 'complete' ? 'book-flipped' : ''}`}>
                <div className="manga-grid">
                  {mockPanels.map((p, idx) => (
                    <motion.div
                      key={p.id}
                      className="rendered-panel"
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ duration: 0.4, delay: idx * 0.15 }}
                    >
                      <span className="panel-tag">{p.tag}</span>
                      <div className="panel-art-placeholder">
                        <div className="panel-lines" />
                      </div>
                      <div className="panel-caption">{p.desc}</div>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
