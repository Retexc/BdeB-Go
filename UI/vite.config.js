import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwindcss from "@tailwindcss/vite";
console.log("[DEBUG] Using Vite config from", __dirname);

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: {
    proxy: {
      "/admin": {
        target: "http://127.0.0.1:5001",
        changeOrigin: true,
        secure: false,
      },
      "/static": {
        target: "http://127.0.0.1:5001",
        changeOrigin: true,
        secure: false,
      },
      "/api": {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
