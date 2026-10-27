from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import email, users

app = FastAPI(title="AI Email Assistant API", version="0.2.0")

# Allow calls from the Chrome extension.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"chrome-extension://.*",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(email.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"name": "AI Email Assistant API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "ai_enabled": bool(settings.gemini_api_key)}
