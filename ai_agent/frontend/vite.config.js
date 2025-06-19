import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Bind to all network interfaces
    port: 5173,
    allowedHosts: ['anytime-fitness-stg.dxfactor.com'],
  },
  preview: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['anytime-fitness-stg.dxfactor.com'],
  },
})

