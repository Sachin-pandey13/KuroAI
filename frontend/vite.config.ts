import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: ['three', 'gsap', 'gsap/ScrollTrigger', 'framer-motion', 'lenis'],
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/three')) {
            return 'three';
          }
          if (id.includes('node_modules/gsap')) {
            return 'gsap';
          }
          if (id.includes('node_modules/framer-motion')) {
            return 'framer-motion';
          }
        },
      },
    },
  },
})
