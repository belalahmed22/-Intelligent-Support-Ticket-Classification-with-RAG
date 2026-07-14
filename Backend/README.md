# Backend - AI Ticket Classification API

Production-ready FastAPI backend that dynamically discovers, ranks, and loads the best support-ticket classification model from `artifacts/`.

## Features
- Recursive model discovery (`.joblib`, `.pkl`, `.pickle`)
- Dynamic best-model selection based on parsed metrics and fallback timestamps
- Startup model loading with structured logging
- REST endpoints: `/health`, `/predict`, `/model-info`
- Typed request/response schemas with validation
- CORS and environment-based configuration

## Run locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API
- `GET /health`
- `GET /model-info`
- `POST /predict`

Request body:
```json
{
  "title": "Payment failed for my order",
  "description": "My card was charged but the order status is still pending."
}
```
