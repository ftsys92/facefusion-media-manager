import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    host: 'my-site.local',
    hmr: false
  },
  plugins: [vue()],
})
