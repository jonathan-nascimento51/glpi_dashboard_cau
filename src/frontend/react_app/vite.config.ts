import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  // Expose environment variables with NEXT_PUBLIC_ prefix to the client
  envPrefix: 'NEXT_PUBLIC_',
  server: {
    host: '0.0.0.0',
  },
})
