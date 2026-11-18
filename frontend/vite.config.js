import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    // npm run dev: chuyển /api/* sang `sam local start-api` (giống CloudFront /api/* → API GW)
    proxy: {
      '/api': 'http://127.0.0.1:3000',
    },
  },
})
