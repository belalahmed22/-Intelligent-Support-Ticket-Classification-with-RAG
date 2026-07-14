from typing import Any

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=5, max_length=5000)


class PredictionResponse(BaseModel):
    category: str
    priority: str
    confidence: float
    agent_solution: str
    customer_reply: str
    model_used: str
    vectorizer_used: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str | None = None
    vectorizer_name: str | None = None
    response_model_name: str | None = None
    response_mode: str | None = None
    qwen_ready: bool = False


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reply: str
    model_used: str
    examples_used: int


class ModelInfoResponse(BaseModel):
    selected_model: str
    model_path: str
    vectorizer_used: str | None = None
    response_model_used: str | None = None
    metrics: dict[str, Any]
