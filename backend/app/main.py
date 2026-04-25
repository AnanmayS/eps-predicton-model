import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import analytics, health, predictions, tickers

app = FastAPI(
    title="Earnings Beat/Miss Predictor API",
    version="1.0.0",
    description="Predicts whether a company is likely to beat or miss earnings expectations.",
)

frontend_origin = [
    value.strip()
    for value in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if value.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(tickers.router)
app.include_router(predictions.router)
app.include_router(analytics.router)
