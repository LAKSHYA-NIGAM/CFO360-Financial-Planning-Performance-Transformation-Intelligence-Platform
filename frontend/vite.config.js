import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server proxies /api/* to the Flask backend on :5000 so the frontend
// can call fetch("/api/...") without hardcoding a host — same pattern
// you'd use in production behind a reverse proxy (nginx, etc.).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },
});
