import { motion } from 'framer-motion';
import './WhySection.css';

export default function WhySection() {
  return (
    <section id="why" className="why-section washi-strip" aria-labelledby="why-title">
      <div className="section-container">
        <div className="section-header">
          <span className="section-eyebrow">// PARADIGM SHIFT</span>
          <h2 id="why-title" className="section-title">Why KuroAI?</h2>
          <p className="section-subtitle">
            Traditional manga creation requires days of manual scripting, panel breakdown, and drafting. KuroAI turns narrative into publication-ready art in seconds.
          </p>
        </div>

        <div className="comparison-grid">
          {/* Traditional Column */}
          <motion.div
            className="comparison-card traditional-card"
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6 }}
          >
            <div className="card-badge badge-traditional">TRADITIONAL WORKFLOW</div>
            <h3 className="card-heading">Manual Production</h3>
            <ul className="timeline-list">
              <li className="timeline-item strike">
                <span className="step-num">01</span>
                <div>
                  <h4>Idea & Scripting</h4>
                  <p>Hours drafting storylines and dialogue bubbles.</p>
                </div>
              </li>
              <li className="timeline-item strike">
                <span className="step-num">02</span>
                <div>
                  <h4>Storyboard Roughs</h4>
                  <p>Manual panel geometry & camera perspective framing.</p>
                </div>
              </li>
              <li className="timeline-item strike">
                <span className="step-num">03</span>
                <div>
                  <h4>Character Inking</h4>
                  <p>Tedious redraws across varying angles and poses.</p>
                </div>
              </li>
              <li className="timeline-item strike">
                <span className="step-num">04</span>
                <div>
                  <h4>Toning & Finishing</h4>
                  <p>Days spent on screentones and background details.</p>
                </div>
              </li>
            </ul>
            <div className="time-badge badge-slow">⏱ 40+ Hours / Chapter</div>
          </motion.div>

          {/* KuroAI Column */}
          <motion.div
            className="comparison-card kuroai-card glass-card"
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="card-badge badge-kuroai">KUROAI MULTI-AGENT ENGINE</div>
            <h3 className="card-heading accent-title">Automated AI Pipeline</h3>
            <ul className="timeline-list">
              <li className="timeline-item active-step">
                <span className="step-num accent-num">01</span>
                <div>
                  <h4>Natural Prompt Input</h4>
                  <p>Single paragraph narrative description.</p>
                </div>
              </li>
              <li className="timeline-item active-step">
                <span className="step-num accent-num">02</span>
                <div>
                  <h4>Multi-Agent Orchestration</h4>
                  <p>Director, Story, Layout & Review agents execute in parallel.</p>
                </div>
              </li>
              <li className="timeline-item active-step">
                <span className="step-num accent-num">03</span>
                <div>
                  <h4>Diffusion Panel Rendering</h4>
                  <p>200K-fine-tuned Stable Diffusion panel synthesis.</p>
                </div>
              </li>
              <li className="timeline-item active-step">
                <span className="step-num accent-num">04</span>
                <div>
                  <h4>Publication Book Assembly</h4>
                  <p>PDF/PNG export with dialogue typesetting.</p>
                </div>
              </li>
            </ul>
            <div className="time-badge badge-fast">⚡ &lt; 8 Seconds / Chapter</div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
