import { motion } from 'framer-motion';
import './Footer.css';

const Footer = () => {
  return (
    <motion.footer 
      className="app-footer"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5, duration: 0.8 }}
    >
      <div className="footer-content">
        <div className="footer-left">
          <p>&copy; {new Date().getFullYear()} Kuro Storycraft. All rights reserved.</p>
        </div>
        <div className="footer-right">
          <a href="#">Privacy Policy</a>
          <span className="dot">•</span>
          <a href="#">Terms of Service</a>
        </div>
      </div>
    </motion.footer>
  );
};

export default Footer;
