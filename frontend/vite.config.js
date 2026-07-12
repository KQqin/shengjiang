import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import Uni from '@uni-helper/plugin-uni'

export default defineConfig({
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  plugins: [Uni()],
  server: {
    port: 5173,
    proxy: {
      '/shared': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      },
    },
  },
})


