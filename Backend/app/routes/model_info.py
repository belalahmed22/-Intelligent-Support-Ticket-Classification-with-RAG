from fastapi import APIRouter, Request

from app.schemas.ticket import ModelInfoResponse

router = APIRouter(tags=["model"])


@router.get("/model-info", response_model=ModelInfoResponse)
async def model_info(request: Request) -> ModelInfoResponse:
    state = getattr(request.app.state, "inference_state", None)
    if not state:
        return ModelInfoResponse(selected_model="none", model_path="", metrics={})

    return ModelInfoResponse(
        selected_model=state.runtime.classifier.name,
        model_path=state.runtime.classifier.path,
        vectorizer_used=state.runtime.vectorizer.name,
        response_model_used=state.runtime.response_model.name,
        metrics={
            "response_mode": state.runtime.response_mode,
            "classifier_metrics": state.runtime.classifier.metrics,
            "vectorizer_metrics": state.runtime.vectorizer.metrics,
            "response_metrics": state.runtime.response_model.metrics,
            "rag_enabled": state.runtime.rag_runtime is not None,
        },
    )
