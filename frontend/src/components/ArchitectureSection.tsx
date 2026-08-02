import { useState } from 'react';
import { motion } from 'framer-motion';
import './ArchitectureSection.css';

interface NodeInfo {
  id: string;
  name: string;
  role: string;
  inputs: string;
  outputs: string;
  spec: string;
}

const architectureNodes: NodeInfo[] = [
  {
    id: 'user',
    name: 'User Prompt',
    role: 'Natural Language Input Interface',
    inputs: 'Raw text prompt / theme choice',
    outputs: 'Raw Intent Payload',
    spec: 'REST / WebSocket JSON API',
  },
  {
    id: 'director',
    name: 'Director Agent',
    role: 'Pipeline Orchestrator & Controller',
    inputs: 'Raw Intent Payload',
    outputs: 'Pacing Contract & Scene Breakdowns',
    spec: 'backend/orchestration/director.py',
  },
  {
    id: 'story',
    name: 'Story Agent',
    role: 'Narrative Arc & Character Logic',
    inputs: 'Scene Breakdowns',
    outputs: 'Script & Character State Dicts',
    spec: 'backend/agents/story_agent.py',
  },
  {
    id: 'dialogue',
    name: 'Dialogue Agent',
    role: 'Manga Script Typesetting Engine',
    inputs: 'Script & Character Speech',
    outputs: 'Balloon Coordinates & Vector Text',
    spec: 'backend/agents/dialogue_agent.py',
  },
  {
    id: 'layout',
    name: 'Layout Agent',
    role: 'Manga Panel Geometry Synthesizer',
    inputs: 'Scene Beats & Emotion Tags',
    outputs: 'SVG Panel Bounds & Gutter Spec',
    spec: 'backend/agents/layout_agent.py',
  },
  {
    id: 'review',
    name: 'Review Agent',
    role: 'Quality Assurance & Safety Gate',
    inputs: 'Rendered Panels & Dialogue Overlay',
    outputs: 'Validation Score (0-1.0) & Pass/Fail Signal',
    spec: 'backend/agents/review_agent.py',
  },
  {
    id: 'output',
    name: 'Manga Output',
    role: 'Final PDF / High-Res PNG Chapter',
    inputs: 'Validated Manga Page Objects',
    outputs: '300 DPI Export Artifact',
    spec: 'backend/export/pdf_exporter.py',
  },
];

export default function ArchitectureSection() {
  const [selectedNode, setSelectedNode] = useState<NodeInfo>(architectureNodes[1]);

  return (
    <section id="architecture" className="architecture-section washi-strip" aria-labelledby="arch-title">
      <div className="section-container">
        <div className="section-header">
          <span className="section-eyebrow">// MULTI-AGENT ARCHITECTURE</span>
          <h2 id="arch-title" className="section-title">System Architecture</h2>
          <p className="section-subtitle">
            KuroAI uses an event-driven multi-agent system where dedicated AI micro-agents collaborate asynchronously to produce cohesive manga chapters.
          </p>
        </div>

        <div className="architecture-interactive-layout">
          {/* Node Selection Diagram */}
          <div className="diagram-canvas glass-card">
            <div className="diagram-flow">
              {architectureNodes.map((node) => (
                <motion.div
                  key={node.id}
                  className={`arch-node ${selectedNode.id === node.id ? 'active-node' : ''}`}
                  onClick={() => setSelectedNode(node)}
                  whileHover={{ scale: 1.04 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="node-icon">◈</div>
                  <div className="node-name">{node.name}</div>
                  <span className="node-spec-tag">{node.spec.split('/').pop()}</span>
                </motion.div>
              ))}
            </div>

            {/* SVG Data Flow Animation Overlay */}
            <svg className="flow-lines-svg" aria-hidden="true">
              <defs>
                <linearGradient id="flowGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#c0392b" />
                  <stop offset="100%" stopColor="#e74c3c" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          {/* Detailed Node Inspector Card */}
          <motion.div
            key={selectedNode.id}
            className="node-inspector-card glass-card"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="inspector-header">
              <span className="inspector-badge">INSPECTING COMPONENT</span>
              <h3 className="inspector-title">{selectedNode.name}</h3>
              <p className="inspector-role">{selectedNode.role}</p>
            </div>

            <div className="inspector-details">
              <div className="detail-item">
                <span className="detail-label">INPUTS</span>
                <span className="detail-value">{selectedNode.inputs}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">OUTPUTS</span>
                <span className="detail-value">{selectedNode.outputs}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">IMPLEMENTATION</span>
                <code className="detail-code">{selectedNode.spec}</code>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
