import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Allow requests from your Azure frontend hostname
    host: '0.0.0.0',  // Makes Vite listen on all interfaces
    port: 5173,
    strictPort: true,
    allowedHosts: [
      'edu-frontend.politeglacier-cb73354c.eastus.azurecontainerapps.io' 
    ],
  },
})
