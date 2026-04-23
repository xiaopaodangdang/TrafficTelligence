import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import TraeSoloBadgePlugin from 'vite-plugin-trae-solo-badge'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), TraeSoloBadgePlugin()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    watch: {
      ignored: ['**/node_modules/**', '**/.pnpm-store/**', '**/.git/**']
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})