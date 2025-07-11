import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
  server: {
    proxy: {
      // when Vue dev server sees /admin/login it forwards to Flask
      '/admin': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: '../src/bdeb_gtfs/static/admin',
    emptyOutDir: true,
  },
  base: '/static/admin/',
})
