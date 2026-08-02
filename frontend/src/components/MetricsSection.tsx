import { motion } from 'framer-motion';
import './MetricsSection.css';

const metrics = [
  { value: '279+', label: 'Automated Tests', sub: 'Core & Integration pass rate' },
  { value: '25/25', label: 'Health Gate Audit', sub: 'Repo audit pass score' },
  { value: '100%', label: 'CI/CD Pass Rate', sub: 'Deterministic green main' },
  { value: '5', label: 'CI Workflows', sub: 'Modular GitHub Actions' },
];

const techStack = [
  { name: 'React 19', category: 'Frontend Core' },
  { name: 'TypeScript', category: 'Type Safety' },
  { name: 'GSAP 3', category: 'Timelines' },
  { name: 'Framer Motion', category: 'UI Animations' },
  { name: 'Python 3.11', category: 'Backend Engine' },
  { name: 'PyTorch / Diffusers', category: 'ML Pipeline' },
  { name: 'Docker / Compose', category: 'Containers' },
  { name: 'GitHub Actions', category: 'CI/CD Gate' },
];

export default function MetricsSection() {
  return (
    <section id="metrics" className="metrics-section" aria-labelledby="metrics-title">
      <div className="section-container">
        <div className="section-header">
          <span className="section-eyebrow">// ENGINEERING EXCELLENCE</span>
          <h2 id="metrics-title" className="section-title">Production Metrics & Tech Stack</h2>
          <p className="section-subtitle">
            KuroAI is built with software engineering rigor — backed by 100% green CI/CD, zero-failure health audit gates, and modular test isolation.
          </p>
        </div>

        {/* 4 Metric Counters */}
        <div className="metrics-grid">
          {metrics.map((m, idx) => (
            <motion.div
              key={m.label}
              className="metric-card glass-card"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: idx * 0.1 }}
            >
              <div className="metric-val">{m.value}</div>
              <div className="metric-lbl">{m.label}</div>
              <div className="metric-sub">{m.sub}</div>
            </motion.div>
          ))}
        </div>

        {/* Built With Tech Stack Strip */}
        <div className="tech-stack-wrap glass-card">
          <div className="tech-stack-header">
            <h3>BUILT WITH MODERN ENGINEERING STACK</h3>
          </div>
          <div className="tech-chips-grid">
            {techStack.map((tech) => (
              <div key={tech.name} className="tech-chip">
                <span className="chip-name">{tech.name}</span>
                <span className="chip-cat">{tech.category}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
