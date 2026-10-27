import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";
import { copyFileSync, mkdirSync, readdirSync, rmSync } from "fs";

// onnxruntime-web loads its WebAssembly engine at runtime, so ship those files with the extension.
const ORT_FILES = ["ort-wasm-simd-threaded.mjs", "ort-wasm-simd-threaded.wasm"];
const copyOrtWasm = () => ({
  name: "copy-ort-wasm",
  closeBundle() {
    mkdirSync(resolve(__dirname, "dist/ort"), { recursive: true });
    for (const f of ORT_FILES) {
      copyFileSync(resolve(__dirname, "node_modules/onnxruntime-web/dist", f), resolve(__dirname, "dist/ort", f));
    }
    // Vite also emits its own hashed copy of the .wasm, which is never used (wasmPaths points to ort/).
    for (const f of readdirSync(resolve(__dirname, "dist/assets"))) {
      if (f.endsWith(".wasm")) rmSync(resolve(__dirname, "dist/assets", f));
    }
  },
});

// Builds the popup page and the background service worker.
export default defineConfig({
  plugins: [react(), copyOrtWasm()],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        popup: resolve(__dirname, "popup.html"),
        background: resolve(__dirname, "src/background/index.ts"),
      },
      output: { entryFileNames: "[name].js", assetFileNames: "assets/[name][extname]" },
    },
  },
});
