import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: ['three', 'gsap', 'gsap/ScrollTrigger', 'framer-motion'],
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          three: ['three'],
          gsap: ['gsap'],
          'framer-motion': ['framer-motion'],
        },
      },
    },
  },
})
