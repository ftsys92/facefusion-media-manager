import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    host: 'phh.internal',
    hmr: false
  },
  plugins: [vue()],
})
