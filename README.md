# AI Email Automation Assistant

A Gmail Chrome Extension (Manifest V3) with a FastAPI backend for email summarization, smart replies, task extraction and classification.

> Inspired by [Partyboyking0/AI-Email-Extention](https://github.com/Partyboyking0/AI-Email-Extention).

## Status

| Phase | Status |
|---|---|
| 0–1: Extension with 3-tab popup | ✅ Done |
| 2: FastAPI backend | ⏳ Next |
| 3: LangChain AI layer | ⏳ |
| 4: Resume RAG | ⏳ |
| 5: Redis, metrics, Docker, tests | ⏳ |
| 6: ONNX in-browser classifier | ⏳ |

## Run the extension

```bash
npm --prefix extension install
npm run build:extension
```

1. Open `chrome://extensions` and turn on **Developer mode**.
2. Click **Load unpacked** and select `extension/dist`.
3. Open Gmail (refresh it), open an email, then click the extension icon.

Without the backend running, every action uses a local rule-based fallback, shown as "Backend fallback".

## Structure

```
extension/   MV3 Chrome extension (React + TypeScript + Vite)
backend/     FastAPI application
ml/          Training and ONNX export scripts
infra/       Docker Compose, Prometheus
docs/        Design notes
```
