import asyncio

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.ticket import PredictionRequest, PredictionResponse
from app.services.inference_service import run_inference

router = APIRouter(tags=["prediction"])


@router.post("/predict", response_model=PredictionResponse)
async def predict(request: Request, payload: PredictionRequest) -> PredictionResponse:
    state = getattr(request.app.state, "inference_state", None)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not available. Check /health for service status.",
        )

    try:
        return await asyncio.to_thread(run_inference, state, payload)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
