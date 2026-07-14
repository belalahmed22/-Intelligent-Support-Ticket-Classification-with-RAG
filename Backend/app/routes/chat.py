import asyncio

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.ticket import ChatRequest, ChatResponse
from app.services.chat_service import run_chat

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, payload: ChatRequest) -> ChatResponse:
    state = getattr(request.app.state, "inference_state", None)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not available. Check /health for service status.",
        )

    try:
        reply, examples_used = await asyncio.to_thread(run_chat, state, payload.message)
        return ChatResponse(
            reply=reply,
            model_used="Qwen2.5-1.5B-Instruct + Hybrid_RAG",
            examples_used=examples_used,
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
