import { motion } from 'framer-motion';
import './LandingPage.css';

const LandingPage = ({ onTryYours }) => {
  const examples = [
    {
      id: 1,
      genre: "Slice of Life",
      title: "Quiet Mornings",
      prompt: "A peaceful morning in a sunlit Kyoto cafe, matcha steam gently rising while a calico cat sleeps on the windowsill.",
      imagePlaceholder: "/slice of life.jpeg", 
    },
    {
      id: 2,
      genre: "Action",
      title: "Neon Pursuit",
      prompt: "A cyberpunk bounty hunter leaps across rain-slicked neon rooftops, laser fire illuminating the dense smog below.",
      imagePlaceholder: "/action.jpeg",
    },
    {
      id: 3,
      genre: "Fantasy",
      title: "The Crystal Spire",
      prompt: "An elven mage channels ancient radiant magic to unlock the glowing runes on the massive doors of the Crystal Spire.",
      imagePlaceholder: "/fantasy.jpeg",
    }
  ];

  return (
    <div className="landing-wrapper">
      {/* Background Effect */}
      <div className="background-effect">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
      </div>

      <div className="landing-container">
        {/* Hero Section */}
        <motion.section 
          className="landing-hero"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, ease: "easeOut" }}
        >
          
          <div className="hero-content-wrapper">
            <motion.div 
              className="badge"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              Introducing KuroAi 2.0
            </motion.div>
            
            <motion.h1 
              className="hero-title"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              Unleash the Power of <br />
              <span className="text-gradient">Generative Manga</span>
            </motion.h1>
            
            <motion.p 
              className="hero-subtitle"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              Transform your narrative into breathtaking visual stories with our next-generation AI pipeline.
            </motion.p>
            
            <motion.div 
              className="hero-actions"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <button className="primary-button" onClick={onTryYours}>
                Start Creating Free
                <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M8.14645 3.14645C8.34171 2.95118 8.65829 2.95118 8.85355 3.14645L12.8536 7.14645C13.0488 7.34171 13.0488 7.65829 12.8536 7.85355L8.85355 11.8536C8.65829 12.0488 8.34171 12.0488 8.14645 11.8536C7.95118 11.6583 7.95118 11.3417 8.14645 11.1464L11.2929 8H2.5C2.22386 8 2 7.77614 2 7.5C2 7.22386 2.22386 7 2.5 7H11.2929L8.14645 3.85355C7.95118 3.65829 7.95118 3.34171 8.14645 3.14645Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path>
                </svg>
              </button>
            </motion.div>
          </div>
        </motion.section>

        {/* Examples Gallery */}
        <section className="examples-gallery">
          <div className="gallery-header">
            <motion.h2 
              className="gallery-title"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
            >
              Engineered for Visionaries
            </motion.h2>
            <motion.p
               className="gallery-subtitle"
               initial={{ opacity: 0, y: 30 }}
               whileInView={{ opacity: 1, y: 0 }}
               viewport={{ once: true, margin: "-100px" }}
               transition={{ delay: 0.1 }}
            >
              Explore the possibilities of our advanced rendering engine.
            </motion.p>
          </div>
          
          <div className="cards-grid">
            {examples.map((ex, index) => (
              <motion.div 
                key={ex.id} 
                className="feature-card"
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ y: -10 }}
              >
                <div className="card-image-wrapper">
                  {/* Fallback to gradient if image fails to load */}
                  <img src={ex.imagePlaceholder} alt={ex.title} className="card-image" onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'block'; }} />
                  <div className="image-fallback" style={{ display: 'none', width: '100%', height: '100%', background: 'linear-gradient(45deg, #1a1a2e, #16213e)' }}></div>
                  <div className="card-badge">{ex.genre}</div>
                </div>
                
                <div className="card-content">
                  <h3 className="card-title">{ex.title}</h3>
                  <p className="card-prompt">{ex.prompt}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};

export default LandingPage;
