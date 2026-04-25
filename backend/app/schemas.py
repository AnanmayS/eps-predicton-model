from typing import List

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10, examples=["AAPL"])


class FeatureInsight(BaseModel):
    feature: str
    value: str
    importance: float


class PredictionResponse(BaseModel):
    ticker: str
    next_earnings_date: str
    prediction: str
    probability_beat: float
    confidence: str
    top_features: List[FeatureInsight]
    feature_source: str
    explanation: str
    explanation_points: List[str]
