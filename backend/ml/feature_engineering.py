from __future__ import annotations

import pandas as pd

from ml.config import (
    DATE_COLUMN,
    FEATURE_COLUMNS,
    INFERENCE_FEATURES_PATH,
    PROCESSED_DIR,
    PROCESSED_FEATURES_PATH,
    RAW_EVENTS_PATH,
)


def build_feature_dataset(raw_path: str | None = None) -> pd.DataFrame:
    source_path = RAW_EVENTS_PATH if raw_path is None else raw_path
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(source_path)
    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN])
    df = df.sort_values(["ticker", DATE_COLUMN]).reset_index(drop=True)

    df["eps_surprise"] = (df["reported_eps"] - df["estimated_eps"]) / df["estimated_eps"].abs().clip(lower=0.05)
    grouped = df.groupby("ticker", group_keys=False)
    shifted_surprise = grouped["eps_surprise"].shift(1)
    shifted_beat = grouped["beat_miss"].shift(1)

    df["prior_eps_surprise"] = shifted_surprise.fillna(0.0)
    df["eps_surprise_mean_4q"] = (
        shifted_surprise.groupby(df["ticker"])
        .rolling(window=4, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
        .fillna(0.0)
    )
    df["trailing_beat_rate_4q"] = (
        shifted_beat.groupby(df["ticker"])
        .rolling(window=4, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
        .fillna(0.5)
    )
    previous_event_date = grouped[DATE_COLUMN].shift(1)
    df["days_since_last_earnings"] = (
        (df[DATE_COLUMN] - previous_event_date).dt.days.fillna(90).clip(lower=45, upper=140)
    )
    df["sector"] = df["sector"].fillna("Unknown")

    train_ready = df[["ticker", DATE_COLUMN, "estimated_eps", "beat_miss", *FEATURE_COLUMNS]].copy()
    train_ready.to_csv(PROCESSED_FEATURES_PATH, index=False)

    inference_snapshot = (
        df.sort_values([DATE_COLUMN, "ticker"])
        .groupby("ticker", as_index=False)
        .tail(1)
        .copy()
    )
    inference_snapshot[DATE_COLUMN] = inference_snapshot[DATE_COLUMN] + pd.Timedelta(days=90)
    inference_snapshot["estimated_eps"] = inference_snapshot["estimated_eps"] * 1.03
    inference_snapshot["analyst_revision_trend"] = inference_snapshot["analyst_revision_trend"].clip(-0.85, 0.85)
    inference_snapshot["volume_change_20d_pre_earnings"] = (
        inference_snapshot["volume_change_20d_pre_earnings"] * 0.95
    )
    inference_snapshot = inference_snapshot[["ticker", DATE_COLUMN, "estimated_eps", *FEATURE_COLUMNS]]
    inference_snapshot.to_csv(INFERENCE_FEATURES_PATH, index=False)

    return train_ready


if __name__ == "__main__":
    build_feature_dataset()
