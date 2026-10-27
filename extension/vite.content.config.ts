import { defineConfig } from "vite";
import { resolve } from "path";

// Content scripts can't use ES module imports, so build this one as a single IIFE file.
export default defineConfig({
  build: {
    outDir: "dist",
    emptyOutDir: false,
    lib: { entry: resolve(__dirname, "src/content/gmail.ts"), name: "gmail", formats: ["iife"], fileName: () => "content.js" },
  },
});
