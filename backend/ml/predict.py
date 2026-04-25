from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta
import hashlib
import io
import os
from typing import Any

import numpy as np
import pandas as pd

from app.model_loader import get_artifact_store
from ml.config import FEATURE_COLUMNS
from ml.sentiment import score_headlines

try:
    import yfinance as yf
except Exception:  # pragma: no cover - optional runtime dependency
    yf = None


SECTOR_CHOICES = [
    "Technology",
    "Financial Services",
    "Healthcare",
    "Consumer Cyclical",
    "Communication Services",
    "Industrials",
    "Energy",
    "Consumer Defensive",
]

FRIENDLY_FEATURE_NAMES = {
    "analyst_revision_trend": "analyst estimate revision trend",
    "return_20d_pre_earnings": "recent 20-day stock momentum",
    "return_60d_pre_earnings": "longer 60-day stock momentum",
    "volatility_20d_pre_earnings": "pre-earnings volatility",
    "volume_change_20d_pre_earnings": "recent trading volume change",
    "news_sentiment_pre_earnings": "pre-earnings news sentiment",
    "revenue_growth_last_reported": "last reported revenue growth",
    "eps_growth_last_reported": "last reported EPS growth",
    "eps_surprise_mean_4q": "average EPS surprise over the last four quarters",
    "prior_eps_surprise": "most recent EPS surprise",
    "trailing_beat_rate_4q": "recent earnings beat rate",
    "debt_to_equity": "debt-to-equity ratio",
    "profit_margin": "profit margin",
    "pe_ratio": "P/E ratio",
    "days_since_last_earnings": "time since the last earnings report",
    "sector": "sector backdrop",
}

FRIENDLY_SOURCE_NAMES = {
    "live_market_inputs": "live market inputs",
    "historical_model_dataset": "historical model inputs",
    "estimated_inputs": "estimated inputs",
}


def _normalize_date_value(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    if isinstance(value, (list, tuple, np.ndarray, pd.Index)):
        if len(value) == 0:
            return None
        value = value[0]

    try:
        parsed = pd.to_datetime(value)
    except Exception:
        return None

    if pd.isna(parsed):
        return None

    if isinstance(parsed, pd.Series):
        parsed = parsed.iloc[0]
    if isinstance(parsed, pd.DatetimeIndex):
        if len(parsed) == 0:
            return None
        parsed = parsed[0]

    return parsed.date().isoformat()


def _extract_next_earnings_date(asset: Any) -> str | None:
    try:
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            calendar_data = getattr(asset, "calendar", None)
    except Exception:
        calendar_data = None

    if isinstance(calendar_data, dict):
        for key in ("Earnings Date", "earningsDate"):
            normalized = _normalize_date_value(calendar_data.get(key))
            if normalized:
                return normalized

    if isinstance(calendar_data, pd.DataFrame) and not calendar_data.empty:
        if "Earnings Date" in calendar_data.columns:
            normalized = _normalize_date_value(calendar_data["Earnings Date"].iloc[0])
            if normalized:
                return normalized
        if "Value" in calendar_data.columns:
            earnings_rows = calendar_data.index.astype(str).str.contains("Earnings", case=False, regex=False)
            if earnings_rows.any():
                normalized = _normalize_date_value(calendar_data.loc[earnings_rows, "Value"].iloc[0])
                if normalized:
                    return normalized

    try:
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            earnings_dates = asset.get_earnings_dates(limit=1)
    except Exception:
        earnings_dates = None

    if isinstance(earnings_dates, pd.DataFrame) and not earnings_dates.empty:
        normalized = _normalize_date_value(earnings_dates.index[0])
        if normalized:
            return normalized

    return None


def get_available_tickers() -> list[str]:
    store = get_artifact_store()
    return sorted(store.inference_features["ticker"].unique().tolist())


def _ticker_seed(ticker: str) -> int:
    digest = hashlib.sha256(ticker.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _format_feature_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    if pd.isna(value):
        return "n/a"
    return f"{float(value):.4f}"


def _confidence_label(probability: float) -> str:
    certainty = max(probability, 1 - probability)
    if certainty >= 0.74:
        return "High"
    if certainty >= 0.62:
        return "Medium"
    return "Low"


def _describe_feature_direction(feature_name: str, raw_value: Any) -> str:
    if pd.isna(raw_value):
        return "was unavailable"

    numeric_value = None
    try:
        numeric_value = float(raw_value)
    except (TypeError, ValueError):
        numeric_value = None

    if feature_name == "sector":
        return f"points to the {raw_value} sector"
    if feature_name == "analyst_revision_trend" and numeric_value is not None:
        return "has been moving up" if numeric_value > 0 else "has been moving down"
    if feature_name == "news_sentiment_pre_earnings" and numeric_value is not None:
        return "has been positive" if numeric_value > 0 else "has been negative"
    if feature_name in {"return_20d_pre_earnings", "return_60d_pre_earnings", "return_5d_pre_earnings"} and numeric_value is not None:
        return "has been positive" if numeric_value > 0 else "has been negative"
    if feature_name == "volatility_20d_pre_earnings" and numeric_value is not None:
        return "has been elevated" if numeric_value > 0.05 else "has stayed relatively calm"
    if feature_name == "trailing_beat_rate_4q" and numeric_value is not None:
        return "has been strong" if numeric_value >= 0.5 else "has been weak"
    if feature_name in {"revenue_growth_last_reported", "eps_growth_last_reported"} and numeric_value is not None:
        return "has been positive" if numeric_value > 0 else "has been negative"
    if feature_name == "debt_to_equity" and numeric_value is not None:
        return "looks elevated" if numeric_value > 1 else "looks moderate"
    if numeric_value is not None:
        return f"came in at {numeric_value:.2f}"
    return f"came in at {raw_value}"


def _build_explanation(
    ticker: str,
    prediction: str,
    probability_beat: float,
    confidence: str,
    top_features: list[dict],
    feature_source: str,
    sentiment_value: float | None,
) -> tuple[str, list[str]]:
    if prediction == "Beat":
        summary = (
            f"The model leans Beat for {ticker} because the strongest pre-earnings signals look supportive. "
            f"It estimates about a {probability_beat * 100:.0f}% chance of beating expectations, which is a {confidence.lower()}-confidence call."
        )
    else:
        summary = (
            f"The model leans Miss for {ticker} because the strongest pre-earnings signals look softer than usual. "
            f"It estimates about a {(1 - probability_beat) * 100:.0f}% chance of not beating expectations, which is a {confidence.lower()}-confidence call."
        )

    reasons: list[str] = []
    for feature in top_features[:3]:
        raw_name = feature["feature"]
        friendly_name = FRIENDLY_FEATURE_NAMES.get(raw_name, raw_name.replace("_", " "))
        reasons.append(
            f"{friendly_name[:1].upper() + friendly_name[1:]} {_describe_feature_direction(raw_name, feature['raw_value'])}."
        )

    if sentiment_value is not None:
        if sentiment_value >= 0.2:
            sentiment_reason = "Recent pre-earnings news sentiment was positive, which supported the model's outlook."
        elif sentiment_value <= -0.2:
            sentiment_reason = "Recent pre-earnings news sentiment was negative, which weighed on the model's outlook."
        else:
            sentiment_reason = "Recent pre-earnings news sentiment looked mixed, so it was not a strong directional signal."
        reasons.append(sentiment_reason)

    reasons.append(
        f"This prediction used {FRIENDLY_SOURCE_NAMES.get(feature_source, feature_source)}."
    )
    return summary, reasons


def _build_fallback_feature_row(ticker: str) -> pd.DataFrame:
    store = get_artifact_store()
    numeric_reference = store.inference_features.drop(
        columns=["ticker", "earnings_date", "estimated_eps", "sector"],
        errors="ignore",
    ).median(numeric_only=True)
    seed = _ticker_seed(ticker)
    rng = np.random.default_rng(seed)

    row = {
        "ticker": ticker,
        "earnings_date": (datetime.utcnow().date() + timedelta(days=30)).isoformat(),
        "estimated_eps": round(
            float(store.inference_features["estimated_eps"].median()) * (0.8 + rng.uniform(0.0, 0.6)),
            4,
        ),
        "sector": SECTOR_CHOICES[seed % len(SECTOR_CHOICES)],
        "return_5d_pre_earnings": float(
            np.clip(numeric_reference["return_5d_pre_earnings"] + rng.normal(0, 0.03), -0.18, 0.18)
        ),
        "return_20d_pre_earnings": float(
            np.clip(numeric_reference["return_20d_pre_earnings"] + rng.normal(0, 0.05), -0.3, 0.3)
        ),
        "return_60d_pre_earnings": float(
            np.clip(numeric_reference["return_60d_pre_earnings"] + rng.normal(0, 0.08), -0.4, 0.45)
        ),
        "volatility_20d_pre_earnings": float(
            np.clip(numeric_reference["volatility_20d_pre_earnings"] + abs(rng.normal(0, 0.01)), 0.01, 0.16)
        ),
        "volume_change_20d_pre_earnings": float(
            np.clip(numeric_reference["volume_change_20d_pre_earnings"] + rng.normal(0, 0.18), -0.35, 1.75)
        ),
        "news_sentiment_pre_earnings": float(
            np.clip(numeric_reference["news_sentiment_pre_earnings"] + rng.normal(0, 0.14), -1.0, 1.0)
        ),
        "revenue_growth_last_reported": float(
            np.clip(numeric_reference["revenue_growth_last_reported"] + rng.normal(0, 0.04), -0.2, 0.35)
        ),
        "eps_growth_last_reported": float(
            np.clip(numeric_reference["eps_growth_last_reported"] + rng.normal(0, 0.05), -0.25, 0.42)
        ),
        "analyst_revision_trend": float(
            np.clip(numeric_reference["analyst_revision_trend"] + rng.normal(0, 0.18), -1.0, 1.0)
        ),
        "pe_ratio": float(np.clip(numeric_reference["pe_ratio"] + rng.normal(0, 4.0), 5.0, 60.0)),
        "debt_to_equity": float(
            np.clip(numeric_reference["debt_to_equity"] + rng.normal(0, 0.18), 0.05, 3.5)
        ),
        "profit_margin": float(np.clip(numeric_reference["profit_margin"] + rng.normal(0, 0.04), 0.01, 0.55)),
        "prior_eps_surprise": float(
            np.clip(numeric_reference["prior_eps_surprise"] + rng.normal(0, 0.03), -0.25, 0.3)
        ),
        "eps_surprise_mean_4q": float(
            np.clip(numeric_reference["eps_surprise_mean_4q"] + rng.normal(0, 0.025), -0.2, 0.25)
        ),
        "trailing_beat_rate_4q": float(
            np.clip(numeric_reference["trailing_beat_rate_4q"] + rng.normal(0, 0.12), 0.0, 1.0)
        ),
        "days_since_last_earnings": float(
            np.clip(numeric_reference["days_since_last_earnings"] + rng.normal(0, 8.0), 45.0, 140.0)
        ),
    }

    return pd.DataFrame([row])


def _build_live_feature_row(ticker: str) -> pd.DataFrame | None:
    if yf is None or os.getenv("ENABLE_LIVE_MARKET_DATA", "true").lower() != "true":
        return None

    try:
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            asset = yf.Ticker(ticker)
            history = asset.history(period="9mo", auto_adjust=False)
            info = getattr(asset, "info", {}) or {}
    except Exception:
        return None

    if history is None or history.empty or "Close" not in history.columns:
        return None

    history = history.dropna(subset=["Close"]).copy()
    if len(history) < 70:
        return None

    close = history["Close"]
    volume = history["Volume"] if "Volume" in history.columns else pd.Series(index=history.index, dtype=float)
    returns = close.pct_change()
    trailing_pe = float(info.get("trailingPE") or 20.0)
    news_items = getattr(asset, "news", None) or []
    headlines = [item.get("title", "") for item in news_items if isinstance(item, dict)]
    news_sentiment = score_headlines(headlines)
    if not headlines and len(close) >= 21:
        news_sentiment = float(np.clip((close.iloc[-1] / close.iloc[-21] - 1) * 1.5, -1.0, 1.0))
    next_earnings_date = _extract_next_earnings_date(asset) or (
        datetime.utcnow().date() + timedelta(days=30)
    ).isoformat()

    return pd.DataFrame(
        [
            {
                "ticker": ticker,
                "earnings_date": next_earnings_date,
                "estimated_eps": round(max(0.05, float(close.iloc[-1]) / max(trailing_pe, 5.0)), 4),
                "return_5d_pre_earnings": float(close.iloc[-1] / close.iloc[-6] - 1),
                "return_20d_pre_earnings": float(close.iloc[-1] / close.iloc[-21] - 1),
                "return_60d_pre_earnings": float(close.iloc[-1] / close.iloc[-61] - 1),
                "volatility_20d_pre_earnings": float(returns.tail(20).std() or 0.03),
                "volume_change_20d_pre_earnings": float(
                    (volume.tail(20).mean() / max(volume.tail(60).mean(), 1.0)) - 1
                )
                if not volume.empty and volume.notna().any()
                else 0.0,
                "news_sentiment_pre_earnings": news_sentiment,
                "revenue_growth_last_reported": 0.06,
                "eps_growth_last_reported": 0.05,
                "analyst_revision_trend": float(
                    np.clip((close.iloc[-1] / close.iloc[-21] - 1) * 2.5, -1.0, 1.0)
                ),
                "pe_ratio": trailing_pe,
                "debt_to_equity": float((info.get("debtToEquity") or 80.0) / 100.0),
                "profit_margin": float(info.get("profitMargins") or 0.12),
                "prior_eps_surprise": 0.02,
                "eps_surprise_mean_4q": 0.015,
                "trailing_beat_rate_4q": 0.55,
                "days_since_last_earnings": 90.0,
                "sector": str(info.get("sector") or "Unknown"),
            }
        ]
    )


def _get_feature_row_for_ticker(ticker: str) -> tuple[pd.DataFrame, str]:
    store = get_artifact_store()
    live_feature_row = _build_live_feature_row(ticker)
    if live_feature_row is not None:
        return live_feature_row, "live_market_inputs"

    sample_feature_row = store.inference_features.loc[store.inference_features["ticker"] == ticker]
    if not sample_feature_row.empty:
        return sample_feature_row.iloc[[0]].copy(), "historical_model_dataset"

    return _build_fallback_feature_row(ticker), "estimated_inputs"


def predict_ticker(ticker: str) -> dict:
    store = get_artifact_store()
    normalized_ticker = ticker.strip().upper()
    if not normalized_ticker:
        raise ValueError("Ticker is required.")

    feature_row, feature_source = _get_feature_row_for_ticker(normalized_ticker)
    feature_row = feature_row[["ticker", "earnings_date", "estimated_eps", *FEATURE_COLUMNS]].copy()
    model_input = feature_row.drop(columns=["ticker", "earnings_date", "estimated_eps"], errors="ignore")

    probability_beat = float(store.model.predict_proba(model_input)[:, 1][0])
    classification_threshold = float(store.metrics.get("classification_threshold", 0.5))
    prediction = "Beat" if probability_beat >= classification_threshold else "Miss"

    top_features_frame = store.feature_importance.sort_values("importance", ascending=False).head(5)
    top_features = []
    for _, feature_row_meta in top_features_frame.iterrows():
        feature_name = feature_row_meta["feature"]
        feature_value = feature_row.iloc[0][feature_name] if feature_name in feature_row.columns else None
        top_features.append(
            {
                "feature": feature_name,
                "value": _format_feature_value(feature_value),
                "raw_value": feature_value,
                "importance": round(float(feature_row_meta["importance"]), 4),
            }
        )

    confidence = _confidence_label(probability_beat)
    sentiment_value = None
    if "news_sentiment_pre_earnings" in feature_row.columns:
        try:
            sentiment_value = float(feature_row.iloc[0]["news_sentiment_pre_earnings"])
        except (TypeError, ValueError):
            sentiment_value = None
    explanation, explanation_points = _build_explanation(
        normalized_ticker,
        prediction,
        probability_beat,
        confidence,
        top_features,
        feature_source,
        sentiment_value,
    )

    return {
        "ticker": normalized_ticker,
        "next_earnings_date": str(feature_row.iloc[0]["earnings_date"]),
        "prediction": prediction,
        "probability_beat": round(probability_beat, 4),
        "confidence": confidence,
        "top_features": [
            {key: value for key, value in feature.items() if key != "raw_value"} for feature in top_features
        ],
        "feature_source": feature_source,
        "explanation": explanation,
        "explanation_points": explanation_points,
    }


def list_upcoming_earnings(limit: int = 8) -> list[dict]:
    store = get_artifact_store()
    upcoming_rows = (
        store.inference_features.sort_values(["earnings_date", "ticker"]).head(limit).copy()
    )

    rows: list[dict] = []
    for _, row in upcoming_rows.iterrows():
        prediction = predict_ticker(str(row["ticker"]))
        rows.append(
            {
                "ticker": str(row["ticker"]),
                "earnings_date": str(row["earnings_date"]),
                "prediction": prediction["prediction"],
                "probability_beat": prediction["probability_beat"],
                "confidence": prediction["confidence"],
                "feature_source": prediction["feature_source"],
                "sector": str(row.get("sector", "Unknown")),
            }
        )
    return rows
