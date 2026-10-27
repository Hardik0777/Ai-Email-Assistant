from fastapi import APIRouter

from app.schemas import ActionResponse, EmailRequest
from app.services import email_ai

router = APIRouter(prefix="/api", tags=["email"])


@router.post("/summarize", response_model=ActionResponse)
async def summarize(email: EmailRequest):
    return await email_ai.summarize(email)


@router.post("/reply", response_model=ActionResponse)
async def reply(email: EmailRequest):
    return await email_ai.reply(email)


@router.post("/tasks", response_model=ActionResponse)
async def tasks(email: EmailRequest):
    return await email_ai.tasks(email)


@router.post("/classify", response_model=ActionResponse)
async def classify(email: EmailRequest):
    return await email_ai.classify(email)
