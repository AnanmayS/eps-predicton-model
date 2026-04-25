from fastapi import APIRouter

from ml.predict import get_available_tickers

router = APIRouter(tags=["tickers"])


@router.get("/tickers")
def list_tickers() -> dict:
    return {"tickers": get_available_tickers()}
