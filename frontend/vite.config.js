import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In development the API runs on :8000; proxying /api keeps requests same-origin.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": process.env.API_URL || "http://localhost:8000",
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.js",
  },
});
