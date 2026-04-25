from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def health_check() -> dict:
    return {
        "status": "ok",
        "service": "Earnings Beat/Miss Predictor API",
        "message": "Model artifacts are ready and the inference service is healthy.",
    }
