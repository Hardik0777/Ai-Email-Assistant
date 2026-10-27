# AI Email Automation Assistant

![CI](https://github.com/Hardik0777/Ai-Email-Assistant/actions/workflows/ci.yml/badge.svg)

A Gmail Chrome Extension (Manifest V3) with a FastAPI backend for email summarization, smart replies, task extraction and classification.

## Status

| Phase | Status |
|---|---|
| 0–1: Extension with 3-tab popup | ✅ Done |
| 2: FastAPI backend + Gemini AI | ✅ Done |
| 3: LangChain LCEL chains | ✅ Done |
| 4: Resume RAG (Gemini embeddings + ChromaDB) | ✅ Done |
| 5: Redis cache + rate limiting, Prometheus, Docker, CI | ✅ Done |
| 6: ONNX classifier running in the browser (onnxruntime-web) | ✅ Done |

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

## Production features

- **Response caching:** identical requests are served from cache (Redis, or in-memory if Redis isn't running). Only real AI answers are cached, never fallbacks. Replies are re-generated after a new resume upload.
- **Rate limiting:** 30 requests per client per minute on the AI routes; extra requests get `429 Too Many Requests` with a `Retry-After` header.
- **Prometheus metrics** at `/metrics`: request counts and latency per route, AI results by source (llm / fallback), cache hits and misses, rate-limit rejections.
- **Health check** at `/health` reports whether AI is enabled and which cache and vector store are active.

### Full stack with Docker

```bash
docker compose -f infra/docker-compose.yml up --build
```

Starts the API (Python 3.12, with ChromaDB), Redis, and Prometheus at http://localhost:9090.

### CI

GitHub Actions runs the backend tests and builds the extension on every push (`.github/workflows/ci.yml`).

## On-device classifier (ONNX)

**Classify** runs a model **inside the browser** first, with no server, no API call, and the email never leaving your machine. Only when the model is less than 60% confident does it ask the backend AI.

- **Features:** hashing trick over words, word pairs and 4-character pieces (4,096 dims), log-scaled and L2-normalised. Identical code in Python (`ml/featurize.py`) and TypeScript (`extension/src/shared/featurize.ts`).
- **Model:** multinomial logistic regression (scikit-learn), exported with `skl2onnx` (~100 KB), run with `onnxruntime-web` (WebAssembly).
- **Data:** the public SMS Spam Collection (real spam and normal messages) plus generated emails for Urgent, Opportunity and Meeting, assembled from phrase banks. The test set uses phrases held out from training.

| Evaluation | Accuracy | Macro F1 |
|---|---|---|
| Held-out test set (610 emails, unseen phrasing) | 79.8% | 0.73 |
| Hand-written realistic emails (20) | 80% | 0.77 |

Known weakness: Urgent recall is low on unfamiliar wording, which is why low-confidence predictions are passed to the backend AI.

**Parity check:** `ml/evaluation/check_parity.mjs` runs all 630 evaluation emails through the TypeScript featurizer and `onnxruntime-web` and checks they match Python exactly (CI runs this on every push).

```bash
pip install -r ml/requirements.txt
python ml/data/build_dataset.py        # downloads SMS data, builds train/test CSVs
python ml/training/train_classifier.py # trains, evaluates, exports extension/public/models/classifier/model.onnx
```
