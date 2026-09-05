import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Spring Boot Endpoints (Auth, Users, relational Cases, Investigations)
      '/api/auth': {
        target: 'http://127.0.0.1:8080',
        timeout: 300000,
        changeOrigin: true
      },
      '/api/cases': {
        target: 'http://127.0.0.1:8080',
        timeout: 300000,
        changeOrigin: true
      },
      '/api/v1/investigations': {
        target: 'http://127.0.0.1:8080',
        timeout: 300000,
        changeOrigin: true
      },
      // Python AI/Graph Service Endpoints
      '/api/v1': {
        target: 'http://127.0.0.1:8000',
        timeout: 300000,
        changeOrigin: true
      }
    }
  }
})
