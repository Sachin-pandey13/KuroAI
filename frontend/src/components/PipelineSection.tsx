import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './PipelineSection.css';

const pipelineStages = [
  {
    id: 'story',
    step: '01',
    title: 'Story Idea',
    subtitle: 'Natural Narrative Input',
    desc: 'Input raw story prompts, character descriptions, or genre themes. The system ingests natural language text without requiring complex prompt engineering.',
    codeSnippet: `story_input = "A lone samurai wanders through a neon-lit cybernetic Tokyo during heavy rain..."`,
    icon: '✍️',
  },
  {
    id: 'analysis',
    step: '02',
    title: 'Prompt Analysis',
    subtitle: 'NLP & Archetype Extraction',
    desc: 'The NLP Parser extracts emotional tone, lighting cues, setting archetypes, and camera perspective parameters automatically.',
    codeSnippet: `parsed_scene = {
  "genre": "Cyberpunk Samurai",
  "mood": "Melancholic",
  "lighting": "Neon reflections on wet asphalt",
  "camera": "Low angle tracking shot"
}`,
    icon: '🧠',
  },
  {
    id: 'storyboard',
    step: '03',
    title: 'Storyboard Layout',
    subtitle: 'Manga Geometry Engine',
    desc: 'Generates dynamic multi-panel grid layouts matching traditional manga pacing — splash panels, action slashes, and dialogue gutters.',
    codeSnippet: `layout_grid = engine.allocate_panels(
  aspect_ratio="16:9",
  panel_count=4,
  pacing="climax_build"
)`,
    icon: '📐',
  },
  {
    id: 'panels',
    step: '04',
    title: 'Panel Synthesis',
    subtitle: 'Stable Diffusion Generation',
    desc: 'Fine-tuned Stable Diffusion 2.1 model fine-tuned on 200,000 manga panels renders character art, background details, and screentones.',
    codeSnippet: `sd_pipeline.render_panel(
  prompt=parsed_scene.to_sd_prompt(),
  steps=28,
  guidance_scale=7.5,
  seed=42
)`,
    icon: '🎨',
  },
  {
    id: 'agents',
    step: '05',
    title: 'Agent Review',
    subtitle: 'Multi-Agent Validation',
    desc: 'The Review Agent inspects line work, character consistency across panels, and anatomical correctness before approving the page.',
    codeSnippet: `review_result = review_agent.inspect(
  rendered_panels,
  consistency_threshold=0.92
)`,
    icon: '🛡️',
  },
  {
    id: 'manga',
    step: '06',
    title: 'Manga Book Export',
    subtitle: 'Typesetting & Assembly',
    desc: 'Typesets dialogue balloons in authentic manga typography and compiles publication-ready PDF or high-res PNG chapters.',
    codeSnippet: `export_book(
  pages=rendered_pages,
  format="PDF",
  dpi=300,
  include_cover=True
)`,
    icon: '📖',
  },
];

export default function PipelineSection() {
  const [activeStage, setActiveStage] = useState(0);

  return (
    <section id="pipeline" className="pipeline-section" aria-labelledby="pipeline-title">
      <div className="section-container">
        <div className="section-header">
          <span className="section-eyebrow">// STEP-BY-STEP EXECUTION</span>
          <h2 id="pipeline-title" className="section-title">The Generation Pipeline</h2>
          <p className="section-subtitle">
            Explore how KuroAI transforms a single prompt into publication-quality manga pages.
          </p>
        </div>

        {/* Interactive Stage Tabs */}
        <div className="pipeline-nav-tabs" role="tablist" aria-label="Pipeline Stages">
          {pipelineStages.map((stage, idx) => (
            <button
              key={stage.id}
              role="tab"
              aria-selected={activeStage === idx}
              aria-controls={`panel-${stage.id}`}
              className={`pipeline-tab-btn ${activeStage === idx ? 'active' : ''}`}
              onClick={() => setActiveStage(idx)}
            >
              <span className="tab-step">{stage.step}</span>
              <span className="tab-title">{stage.title}</span>
            </button>
          ))}
        </div>

        {/* Stage Content Card */}
        <div className="pipeline-content-area">
          <AnimatePresence mode="wait">
            {pipelineStages.map(
              (stage, idx) =>
                activeStage === idx && (
                  <motion.div
                    key={stage.id}
                    id={`panel-${stage.id}`}
                    role="tabpanel"
                    className="pipeline-stage-card glass-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="stage-info">
                      <div className="stage-icon-badge">{stage.icon}</div>
                      <span className="stage-num-badge">STAGE {stage.step} / 06</span>
                      <h3 className="stage-heading">{stage.title}</h3>
                      <h4 className="stage-subheading">{stage.subtitle}</h4>
                      <p className="stage-desc">{stage.desc}</p>
                    </div>

                    <div className="stage-code-block">
                      <div className="code-header">
                        <span className="code-dot red" />
                        <span className="code-dot yellow" />
                        <span className="code-dot green" />
                        <span className="code-title">kuroai_pipeline_stage_{stage.step}.py</span>
                      </div>
                      <pre className="code-content">
                        <code>{stage.codeSnippet}</code>
                      </pre>
                    </div>
                  </motion.div>
                )
            )}
          </AnimatePresence>
        </div>

        {/* Next / Prev Controls */}
        <div className="pipeline-controls">
          <button
            type="button"
            className="ctrl-btn"
            disabled={activeStage === 0}
            onClick={() => setActiveStage((prev) => Math.max(0, prev - 1))}
          >
            ← Previous Stage
          </button>
          <div className="pipeline-dots">
            {pipelineStages.map((_, i) => (
              <span
                key={i}
                className={`dot ${activeStage === i ? 'active' : ''}`}
                onClick={() => setActiveStage(i)}
              />
            ))}
          </div>
          <button
            type="button"
            className="ctrl-btn"
            disabled={activeStage === pipelineStages.length - 1}
            onClick={() => setActiveStage((prev) => Math.min(pipelineStages.length - 1, prev + 1))}
          >
            Next Stage →
          </button>
        </div>
      </div>
    </section>
  );
}
