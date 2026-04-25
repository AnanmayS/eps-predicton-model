from fastapi import APIRouter

from app.model_loader import get_artifact_store
from ml.predict import list_upcoming_earnings

router = APIRouter(tags=["analytics"])


@router.get("/metrics")
def metrics() -> dict:
    return get_artifact_store().metrics


@router.get("/backtest")
def backtest() -> dict:
    records = get_artifact_store().backtest_results.to_dict(orient="records")
    return {"results": records}


@router.get("/feature-importance")
def feature_importance() -> dict:
    records = (
        get_artifact_store()
        .feature_importance.sort_values("importance", ascending=False)
        .head(12)
        .to_dict(orient="records")
    )
    return {"features": records}


@router.get("/upcoming-earnings")
def upcoming_earnings() -> dict:
    return {"results": list_upcoming_earnings()}
