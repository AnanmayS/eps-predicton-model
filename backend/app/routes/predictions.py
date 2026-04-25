from fastapi import APIRouter, HTTPException

from app.schemas import PredictionRequest, PredictionResponse
from ml.predict import predict_ticker

router = APIRouter(tags=["predictions"])


@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    try:
        prediction_payload = predict_ticker(request.ticker.upper())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return PredictionResponse(**prediction_payload)
