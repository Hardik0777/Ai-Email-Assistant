# AI Email Automation Assistant

A Gmail Chrome Extension (Manifest V3) with a FastAPI backend for email summarization, smart replies, task extraction and classification.

> Inspired by [Partyboyking0/AI-Email-Extention](https://github.com/Partyboyking0/AI-Email-Extention).

## Status

| Phase | Status |
|---|---|
| 0–1: Extension with 3-tab popup | ✅ Done |
| 2: FastAPI backend + Gemini AI | ✅ Done |
| 3: LangChain LCEL chains | ✅ Done |
| 4: Resume RAG (Gemini embeddings + ChromaDB) | ✅ Done |
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

## Run the backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --port 8001 --reload
```

Put `GEMINI_API_KEY=...` in a `.env` file (copy `.env.example`) to get real AI answers. Without it, the backend uses rule-based fallbacks.

- API docs: http://127.0.0.1:8001/docs
- Tests: `python -m pytest tests`

## Resume RAG

Upload a PDF or DOCX resume from the popup's **Dashboard** tab. The backend:

1. Extracts the text and splits it into sections (Projects, Skills, Education…)
2. Chunks each section (700 characters, 120 overlap) without crossing section boundaries
3. Embeds the chunks with Gemini (`gemini-embedding-001`) and stores them in ChromaDB
4. On **Smart Reply**, retrieves the top 4 chunks for the email and drops weak matches (similarity < 0.55)
5. Writes the reply with only the relevant resume details

The popup shows `RAG used N chunks` or `RAG no resume match`. If ChromaDB can't be installed, a JSON vector store is used automatically.
