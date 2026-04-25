from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Dict, List

import numpy as np
import pandas as pd

from ml.config import RAW_DIR, RAW_EVENTS_PATH
from ml.sentiment import build_synthetic_headlines, score_headlines

try:
    import yfinance as yf
except Exception:  # pragma: no cover - optional dependency at runtime
    yf = None


@dataclass(frozen=True)
class TickerProfile:
    ticker: str
    company_name: str
    sector: str
    beat_bias: float
    earnings_volatility: float
    revenue_trend: float


SAMPLE_PROFILES: List[TickerProfile] = [
    TickerProfile("AAPL", "Apple", "Technology", 0.69, 0.028, 0.082),
    TickerProfile("MSFT", "Microsoft", "Technology", 0.72, 0.024, 0.094),
    TickerProfile("NVDA", "NVIDIA", "Technology", 0.78, 0.041, 0.196),
    TickerProfile("AMZN", "Amazon", "Consumer Cyclical", 0.63, 0.035, 0.127),
    TickerProfile("GOOGL", "Alphabet", "Communication Services", 0.66, 0.027, 0.089),
    TickerProfile("META", "Meta Platforms", "Communication Services", 0.68, 0.039, 0.134),
    TickerProfile("TSLA", "Tesla", "Consumer Cyclical", 0.46, 0.062, 0.111),
    TickerProfile("JPM", "JPMorgan Chase", "Financial Services", 0.61, 0.022, 0.052),
    TickerProfile("WMT", "Walmart", "Consumer Defensive", 0.58, 0.019, 0.041),
    TickerProfile("XOM", "Exxon Mobil", "Energy", 0.55, 0.031, 0.064),
]


def _safe_yfinance_snapshot(ticker: str) -> Dict[str, float | str]:
    if yf is None or os.getenv("USE_YFINANCE", "false").lower() != "true":
        return {}

    try:
        asset = yf.Ticker(ticker)
        info = getattr(asset, "info", {}) or {}
        history = asset.history(period="1y", auto_adjust=False)
    except Exception:
        return {}

    snapshot: Dict[str, float | str] = {}
    if info.get("sector"):
        snapshot["sector"] = info["sector"]
    if info.get("trailingPE") is not None:
        snapshot["pe_ratio"] = float(info["trailingPE"])
    if info.get("debtToEquity") is not None:
        snapshot["debt_to_equity"] = float(info["debtToEquity"]) / 100.0
    if info.get("profitMargins") is not None:
        snapshot["profit_margin"] = float(info["profitMargins"])

    if history is not None and not history.empty and "Close" in history:
        returns = history["Close"].pct_change().dropna()
        if not returns.empty:
            snapshot["market_volatility_hint"] = float(returns.std())
        if "Volume" in history:
            snapshot["volume_level_hint"] = float(history["Volume"].tail(20).mean())

    return snapshot


def _quarterly_dates(start_year: int, end_year: int) -> pd.DatetimeIndex:
    return pd.date_range(
        f"{start_year}-01-15",
        f"{end_year}-12-15",
        freq="QS",
    ) + pd.offsets.Day(35)


def generate_synthetic_earnings_data(
    start_year: int = 2018,
    end_year: int = 2025,
    random_seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(random_seed)
    event_dates = _quarterly_dates(start_year, end_year)
    rows: list[dict] = []

    for profile in SAMPLE_PROFILES:
        live_snapshot = _safe_yfinance_snapshot(profile.ticker)
        sector = str(live_snapshot.get("sector", profile.sector))
        pe_ratio_anchor = float(live_snapshot.get("pe_ratio", 20 + rng.normal(0, 6)))
        debt_to_equity_anchor = float(
            live_snapshot.get("debt_to_equity", max(0.12, 0.8 + rng.normal(0, 0.35)))
        )
        profit_margin_anchor = float(
            live_snapshot.get("profit_margin", np.clip(0.12 + rng.normal(0, 0.06), 0.02, 0.42))
        )
        market_volatility_hint = float(
            live_snapshot.get("market_volatility_hint", profile.earnings_volatility)
        )

        last_revenue_growth = profile.revenue_trend
        last_eps_growth = profile.revenue_trend * 0.85
        last_surprise = rng.normal(0.03, 0.06)

        for idx, earnings_date in enumerate(event_dates):
            seasonality = np.sin(idx / 3.0) * 0.03
            macro_noise = rng.normal(0, 0.018)
            sentiment = np.clip((profile.beat_bias - 0.5) * 2.2 + seasonality + macro_noise, -0.9, 0.9)

            estimate_base = 0.9 + idx * 0.025 + rng.normal(0, 0.08)
            estimated_eps = max(0.2, estimate_base + last_eps_growth * 1.35)

            revenue_growth = np.clip(
                0.55 * last_revenue_growth + 0.45 * (profile.revenue_trend + rng.normal(0, 0.04)),
                -0.18,
                0.35,
            )
            eps_growth = np.clip(
                0.45 * last_eps_growth + 0.55 * (revenue_growth + rng.normal(0, 0.05)),
                -0.25,
                0.42,
            )

            analyst_revision_trend = np.clip(
                0.28 * sentiment + 0.22 * revenue_growth + rng.normal(0, 0.14),
                -1.0,
                1.0,
            )
            synthetic_headlines = build_synthetic_headlines(profile.ticker, sentiment + rng.normal(0, 0.15))
            news_sentiment = np.clip(
                0.55 * score_headlines(synthetic_headlines) + 0.45 * sentiment + rng.normal(0, 0.06),
                -1.0,
                1.0,
            )
            return_5d = np.clip(0.35 * analyst_revision_trend + rng.normal(0, 0.045), -0.16, 0.18)
            return_20d = np.clip(0.55 * analyst_revision_trend + rng.normal(0, 0.08), -0.28, 0.32)
            return_60d = np.clip(0.8 * revenue_growth + rng.normal(0, 0.12), -0.34, 0.44)
            volatility_20d = np.clip(
                market_volatility_hint * (1.2 + abs(rng.normal(0, 0.3))) + (1 - profile.beat_bias) * 0.01,
                0.012,
                0.16,
            )
            volume_change_20d = np.clip(
                0.65 * abs(analyst_revision_trend) + rng.normal(0.0, 0.22),
                -0.35,
                1.75,
            )
            pe_ratio = max(5.0, pe_ratio_anchor + rng.normal(0, 2.8))
            debt_to_equity = np.clip(debt_to_equity_anchor + rng.normal(0, 0.12), 0.05, 3.5)
            profit_margin = np.clip(profit_margin_anchor + rng.normal(0, 0.025), 0.01, 0.55)
            pre_earnings_signal = (
                0.32 * analyst_revision_trend
                + 0.2 * last_surprise
                + 0.16 * revenue_growth
                + 0.12 * eps_growth
                + 0.12 * news_sentiment
                + 0.12 * return_20d
                + 0.08 * return_60d
                - 0.1 * volatility_20d
                - 0.06 * debt_to_equity
                + 0.06 * profit_margin
            )
            surprise_signal = 0.02 * sentiment + 0.22 * pre_earnings_signal + rng.normal(0, 0.028)
            reported_eps = max(0.05, estimated_eps * (1 + surprise_signal))
            beat_miss = int(reported_eps >= estimated_eps)

            rows.append(
                {
                    "ticker": profile.ticker,
                    "company_name": profile.company_name,
                    "sector": sector,
                    "earnings_date": earnings_date.date().isoformat(),
                    "estimated_eps": round(estimated_eps, 4),
                    "reported_eps": round(reported_eps, 4),
                    "beat_miss": beat_miss,
                    "return_5d_pre_earnings": round(return_5d, 4),
                    "return_20d_pre_earnings": round(return_20d, 4),
                    "return_60d_pre_earnings": round(return_60d, 4),
                    "volatility_20d_pre_earnings": round(volatility_20d, 4),
                    "volume_change_20d_pre_earnings": round(volume_change_20d, 4),
                    "news_sentiment_pre_earnings": round(news_sentiment, 4),
                    "revenue_growth_last_reported": round(last_revenue_growth, 4),
                    "eps_growth_last_reported": round(last_eps_growth, 4),
                    "analyst_revision_trend": round(analyst_revision_trend, 4),
                    "pe_ratio": round(pe_ratio, 4),
                    "debt_to_equity": round(debt_to_equity, 4),
                    "profit_margin": round(profit_margin, 4),
                }
            )

            last_revenue_growth = revenue_growth
            last_eps_growth = eps_growth
            last_surprise = surprise_signal

    dataset = pd.DataFrame(rows).sort_values(["earnings_date", "ticker"]).reset_index(drop=True)
    return dataset


def ingest_dataset(output_path: str | None = None) -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dataset = generate_synthetic_earnings_data()
    target_path = RAW_EVENTS_PATH if output_path is None else output_path
    dataset.to_csv(target_path, index=False)
    return dataset


if __name__ == "__main__":
    ingest_dataset()
