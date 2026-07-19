import { fileURLToPath, URL } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'

import { defineConfig } from 'vite'
import Uni from '@uni-helper/plugin-uni'

const sharedRoot = fileURLToPath(new URL('../shared', import.meta.url))

function sharedStaticPlugin() {
  return {
    name: 'shared-static-fallback',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const url = req.url?.split('?')[0] || ''
        if (!url.startsWith('/shared/')) return next()
        const rel = decodeURIComponent(url.slice('/shared/'.length))
        const filePath = path.join(sharedRoot, rel)
        if (!filePath.startsWith(sharedRoot) || !fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
          return next()
        }
        const ext = path.extname(filePath).toLowerCase()
        const mime =
          ext === '.png'
            ? 'image/png'
            : ext === '.jpg' || ext === '.jpeg'
              ? 'image/jpeg'
              : ext === '.webp'
                ? 'image/webp'
                : 'application/octet-stream'
        res.setHeader('Content-Type', mime)
        fs.createReadStream(filePath).pipe(res)
      })
    },
  }
}

function sharedProxyBypass(req) {
  const url = req.url?.split('?')[0] || ''
  if (!url.startsWith('/shared/')) return
  const rel = decodeURIComponent(url.slice('/shared/'.length))
  const filePath = path.join(sharedRoot, rel)
  if (filePath.startsWith(sharedRoot) && fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    return filePath
  }
}

export default defineConfig({
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  plugins: [Uni(), sharedStaticPlugin()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/shared': {
        target: 'http://localhost:3001',
        changeOrigin: true,
        bypass: sharedProxyBypass,
      },
      '/health': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      },
      '/ws-backend': {
        target: 'ws://localhost:3001',
        ws: true,
        changeOrigin: true,
        rewrite: () => '/',
      },
    },
  },
})


