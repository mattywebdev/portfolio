import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
    plugins: [react()],
      build: {
      outDir: "portfolio/static/frontend",
      emptyOutDir: true,
      rollupOptions: {
          input: {
              main: "frontend/src/main.jsx",
          },
          output: {
              entryFileNames: "assets/[name].js",
              chunkFileNames: "assets/[name].js",
              assetFileNames: "assets/[name][extname]",
          },
      },
  },
});