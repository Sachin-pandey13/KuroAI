import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './AgentsSection.css';

interface AgentCardData {
  id: string;
  name: string;
  badge: string;
  direction: 'left' | 'right' | 'top' | 'bottom';
  icon: string;
  role: string;
  description: string;
  contractSpec: string;
}

const agentsData: AgentCardData[] = [
  {
    id: 'director',
    name: 'Director Agent',
    badge: 'ORCHESTRATOR',
    direction: 'left',
    icon: '🎬',
    role: 'Pipeline Controller & State Synchronizer',
    description: 'Manages multi-agent execution order, state passing between pipeline stages, and global transaction retries.',
    contractSpec: `class DirectorContract(BaseModel):
    session_id: str
    target_genre: GenreEnum
    max_panel_count: int = 6
    pacing_strategy: PacingEnum`,
  },
  {
    id: 'story',
    name: 'Story Agent',
    badge: 'NARRATIVE',
    direction: 'top',
    icon: '📖',
    role: 'Character Dynamics & Script Synthesis',
    description: 'Generates narrative arcs, character dialogic turns, and emotional beats conditioned on user prompt inputs.',
    contractSpec: `class StoryOutputContract(BaseModel):
    characters: List[CharacterProfile]
    scene_beats: List[SceneBeat]
    dialogue_map: Dict[str, str]`,
  },
  {
    id: 'layout',
    name: 'Layout Agent',
    badge: 'GEOMETRY',
    direction: 'bottom',
    icon: '📐',
    role: 'Manga Panel Geometry & Camera Framing',
    description: 'Synthesizes panel coordinates, gutter dimensions, and camera framing parameters optimized for visual storytelling.',
    contractSpec: `class LayoutContract(BaseModel):
    panel_bounds: List[BoundingBox]
    camera_angles: List[CameraAngle]
    gutter_px: int = 12`,
  },
  {
    id: 'review',
    name: 'Review Agent',
    badge: 'QUALITY GATE',
    direction: 'right',
    icon: '🛡️',
    role: 'Quality Assurance & Anatomical Safety',
    description: 'Runs automated quality assertions across rendered panels, verifying character consistency score ≥ 0.90 before final export.',
    contractSpec: `class ReviewContract(BaseModel):
    consistency_score: float
    anatomical_pass: bool
    text_overlap_detected: bool
    is_approved: bool`,
  },
];

export default function AgentsSection() {
  const [activeModalAgent, setActiveModalAgent] = useState<AgentCardData | null>(null);

  return (
    <section id="agents" className="agents-section" aria-labelledby="agents-title">
      <div className="section-container">
        <div className="section-header">
          <span className="section-eyebrow">// SPECIALIZED AI AGENTS</span>
          <h2 id="agents-title" className="section-title">Multi-Agent Intelligence</h2>
          <p className="section-subtitle">
            Rather than relying on a single monolith model, KuroAI orchestrates 4 specialized AI agents working together like a professional manga studio team.
          </p>
        </div>

        {/* 4 Staggered Manga Panel Cards */}
        <div className="agents-cards-grid">
          {agentsData.map((agent, idx) => {
            const initialPos = {
              left: { x: -60, opacity: 0 },
              right: { x: 60, opacity: 0 },
              top: { y: -60, opacity: 0 },
              bottom: { y: 60, opacity: 0 },
            }[agent.direction];

            return (
              <motion.div
                key={agent.id}
                className="agent-manga-card glass-card"
                initial={initialPos}
                whileInView={{ x: 0, y: 0, opacity: 1 }}
                viewport={{ once: true, margin: '-50px' }}
                transition={{ duration: 0.6, delay: idx * 0.15 }}
                whileHover={{ y: -6, scale: 1.02 }}
              >
                <div className="agent-card-top">
                  <span className="agent-icon">{agent.icon}</span>
                  <span className="agent-badge">{agent.badge}</span>
                </div>
                <h3 className="agent-name">{agent.name}</h3>
                <h4 className="agent-role">{agent.role}</h4>
                <p className="agent-desc">{agent.description}</p>

                <button
                  type="button"
                  className="contract-btn"
                  onClick={() => setActiveModalAgent(agent)}
                >
                  View Contract Spec ➔
                </button>
              </motion.div>
            );
          })}
        </div>

        {/* Contract Spec Modal */}
        <AnimatePresence>
          {activeModalAgent && (
            <motion.div
              className="modal-backdrop"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setActiveModalAgent(null)}
            >
              <motion.div
                className="modal-content glass-card"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={(e) => e.stopPropagation()}
              >
                <div className="modal-header">
                  <h3>{activeModalAgent.name} Contract</h3>
                  <button
                    type="button"
                    className="modal-close-btn"
                    onClick={() => setActiveModalAgent(null)}
                  >
                    ✕
                  </button>
                </div>
                <pre className="modal-code">
                  <code>{activeModalAgent.contractSpec}</code>
                </pre>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
}
