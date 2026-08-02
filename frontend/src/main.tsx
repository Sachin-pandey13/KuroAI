import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { GoogleOAuthProvider } from '@react-oauth/google'
import Lenis from 'lenis'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import './index.css'
import App from './App'

gsap.registerPlugin(ScrollTrigger);

// Initialize Lenis smooth scroll for non-reduced-motion environments
if (typeof window !== 'undefined' && !window.matchMedia('(prefers-reduced-motion: reduce)').matches && window.innerWidth >= 768) {
  const lenis = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    touchMultiplier: 2,
  });

  lenis.on('scroll', ScrollTrigger.update);

  gsap.ticker.add((time) => {
    lenis.raf(time * 1000);
  });

  gsap.ticker.lagSmoothing(0);
}

const rootEl = document.getElementById('root');
if (!rootEl) throw new Error('Root element not found');

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

createRoot(rootEl).render(
  <StrictMode>
    <GoogleOAuthProvider clientId={googleClientId}>
      <App />
    </GoogleOAuthProvider>
  </StrictMode>,
)

