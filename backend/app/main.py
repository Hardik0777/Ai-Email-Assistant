import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.config import settings
from app.routes import email, resume, users
from app.services import kv
from app.services.metrics import LATENCY, REQUESTS
from app.services.rag.resume import get_rag

app = FastAPI(title="AI Email Assistant API", version="0.5.0")

# Allow calls from the Chrome extension.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"chrome-extension://.*",
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def record_metrics(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    # Use the route template (/api/reply), not the raw URL, to keep metric labels few.
    route = request.scope.get("route")
    path = getattr(route, "path", "unmatched")
    LATENCY.labels(path=path).observe(time.perf_counter() - start)
    REQUESTS.labels(method=request.method, path=path, status=response.status_code).inc()
    return response


app.include_router(email.router)
app.include_router(users.router)
app.include_router(resume.router)


@app.get("/")
def root():
    return {"name": "AI Email Assistant API", "docs": "/docs"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "ai_enabled": bool(settings.gemini_api_key),
        "cache": kv.kv.name,
        "vector_store": get_rag().store.name,
    }


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
