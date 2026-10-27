from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.llm import LLMUnavailable
from app.services.rag.extract import UnsupportedFile
from app.services.rag.resume import get_rag

router = APIRouter(prefix="/api/resume", tags=["resume"])
MAX_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(413, "File is larger than 5 MB")
    try:
        return await get_rag().ingest(file.filename or "resume", data)
    except UnsupportedFile as exc:
        raise HTTPException(415, str(exc))
    except LLMUnavailable as exc:
        raise HTTPException(503, f"Embedding service unavailable: {exc}")
    except ValueError as exc:
        raise HTTPException(422, str(exc))


@router.get("/status")
def status():
    return get_rag().status()


@router.get("/history")
def history():
    return get_rag().history()


@router.delete("")
def delete():
    get_rag().delete()
    return {"deleted": True}
