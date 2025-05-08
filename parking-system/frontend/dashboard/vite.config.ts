import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173, // React dev server port
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // Flask server port
        changeOrigin: true, // To avoid CORS issues
        rewrite: (path) => path.replace(/^\/api/, '') // Remove /api prefix
      },
    },
  },
});
