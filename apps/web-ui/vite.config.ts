import { copyFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages serves project sites from /<repo>/, so the bundle needs a base
// path baked in at build time. Root-serving hosts (Vercel, Netlify, local
// preview) leave VITE_BASE_PATH unset and get "/".
const BASE_PATH = process.env.VITE_BASE_PATH ?? "/";

/**
 * GitHub Pages has no SPA rewrite rule: a deep link like /simulate/tfidf hits
 * the static file server, misses, and gets 404.html. Serving a copy of
 * index.html there lets React Router take over on the client. `.nojekyll`
 * stops Pages from running Jekyll, which would strip files it considers
 * private.
 */
function githubPagesSpaFallback(): Plugin {
  return {
    name: "github-pages-spa-fallback",
    apply: "build",
    closeBundle() {
      const outDir = resolve(__dirname, "dist");
      copyFileSync(resolve(outDir, "index.html"), resolve(outDir, "404.html"));
      writeFileSync(resolve(outDir, ".nojekyll"), "");
    },
  };
}

export default defineConfig({
  base: BASE_PATH,
  plugins: [react(), githubPagesSpaFallback()],
  server: {
    port: 5173,
    host: "0.0.0.0",
  },
  build: {
    chunkSizeWarningLimit: 550,
    rollupOptions: {
      output: {
        manualChunks: {
          react: ["react", "react-dom", "react-router-dom"],
          state: ["@reduxjs/toolkit", "react-redux", "axios", "clsx"],
          charts: ["recharts"],
          flow: ["@xyflow/react"],
        },
      },
    },
  },
});
