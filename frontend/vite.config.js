import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The dev server proxies API calls to the FastAPI backend so the website
// always talks to the agent through the API (matching the product design).
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/health': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
