# Earnings Surprise Prediction Platform

A full-stack machine learning project that predicts whether a public company is likely to beat or miss earnings expectations using leakage-safe pre-earnings features. The project combines a reproducible Python data pipeline, an XGBoost classifier, rolling out-of-sample backtests, a FastAPI inference API, and a React dashboard for explaining predictions in plain English.

## Overview

This project emphasizes applied ML judgment, not just model training:

- uses only information available before the earnings release
- compares model performance against a simple baseline
- includes rolling backtests instead of only a random split
- explains predictions with feature drivers and plain-English summaries
- supports live-first inference with reliable fallbacks when APIs are incomplete

## Problem

Earnings prediction is hard because analyst expectations already incorporate a lot of public information, while many intuitive signals become available only after the event. A useful model has to rely on features that are realistically known ahead of earnings and be evaluated in a time-aware way.

## What The Model Uses

The model is trained on pre-earnings features such as:

- 5-day, 20-day, and 60-day price returns
- rolling pre-earnings volatility
- volume changes
- analyst revision trend
- revenue growth and EPS growth from prior reported periods
- trailing EPS surprise history
- trailing beat rate
- financial ratios such as P/E, debt-to-equity, and profit margin
- sector
- pre-earnings news sentiment

## Leakage Prevention

The pipeline explicitly avoids target leakage:

- no post-earnings price movement is used as a feature
- `reported_eps` is never used as a model input
- trailing statistics are shifted so each row only sees prior quarters
- train/test evaluation is chronological, not random
- rolling backtests retrain on older periods and score future periods only

## Sentiment Analysis

The project now includes a lightweight pre-earnings sentiment feature:

- synthetic training data uses deterministic pre-earnings headline templates and a lexicon-based sentiment score
- live inference attempts to score recent news headlines when available
- when live headlines are unavailable, the app falls back to a stable estimated input so the product still works

This keeps the sentiment signal realistic without pretending to be a full production news-ingestion platform.

## Model Evaluation

The training pipeline saves:

- accuracy
- precision
- recall
- F1 score
- ROC-AUC
- confusion matrix
- baseline accuracy
- calibration buckets
- threshold trade-off analysis
- sector-level breakdown

Artifacts are written to:

- `backend/models/xgb_earnings_model.pkl`
- `backend/reports/metrics.json`
- `backend/reports/feature_importance.csv`
- `backend/reports/backtest_results.csv`

## Product Experience

The dashboard is intentionally simple and focused:

- enter any ticker
- get a Beat/Miss prediction
- see confidence and top feature drivers
- read a plain-English explanation
- review evaluation metrics and rolling backtests
- browse an upcoming earnings watchlist

Inference data preference order:

1. live market inputs
2. historical model inputs
3. estimated inputs

## API Endpoints

- `GET /`
- `GET /tickers`
- `POST /predict`
- `GET /metrics`
- `GET /backtest`
- `GET /feature-importance`
- `GET /upcoming-earnings`

## Screenshots

Add screenshots here after running locally:

- `docs/screenshots/dashboard-overview.png`
- `docs/screenshots/prediction-detail.png`
- `docs/screenshots/model-evaluation.png`

## Limitations

- free market and news APIs are incomplete, so some live inference fields may fall back to estimated inputs
- the historical training set is reproducible, but partially synthetic where free data is limited
- the model is designed for educational use, not live trading
- sentiment analysis is lightweight and not a replacement for a full institutional news pipeline

## Local Setup

### Run with Docker

```bash
docker-compose up --build
```

Frontend: `http://localhost:3000`  
Backend docs: `http://localhost:8000/docs`

### Run Manually

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m ml.bootstrap
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Tests And CI

Backend tests:

```bash
cd backend
pytest
```

Frontend production build:

```bash
cd frontend
npm run build
```

GitHub Actions CI is included at `.github/workflows/ci.yml` and runs:

- backend tests
- frontend production build

## Project Structure

```text
earnings-beat-miss-predictor/
  backend/
    app/
    ml/
    tests/
    data/
    models/
    reports/
  frontend/
    src/
  aws_pipeline/
  docs/screenshots/
  .github/workflows/
  docker-compose.yml
  README.md
```
