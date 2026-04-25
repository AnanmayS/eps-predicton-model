from __future__ import annotations

from ml.backtest import run_backtest
from ml.config import (
    BACKTEST_RESULTS_PATH,
    FEATURE_IMPORTANCE_PATH,
    INFERENCE_FEATURES_PATH,
    METRICS_PATH,
    MODEL_PATH,
    PROCESSED_FEATURES_PATH,
    RAW_EVENTS_PATH,
)
from ml.feature_engineering import build_feature_dataset
from ml.ingest_data import ingest_dataset
from ml.train_model import train_model


def ensure_pipeline_artifacts(force_rebuild: bool = False) -> None:
    if force_rebuild or not RAW_EVENTS_PATH.exists():
        ingest_dataset()

    if force_rebuild or not PROCESSED_FEATURES_PATH.exists() or not INFERENCE_FEATURES_PATH.exists():
        build_feature_dataset()

    model_outputs_missing = (
        force_rebuild
        or not MODEL_PATH.exists()
        or not METRICS_PATH.exists()
        or not FEATURE_IMPORTANCE_PATH.exists()
    )
    if model_outputs_missing:
        train_model()

    if force_rebuild or not BACKTEST_RESULTS_PATH.exists():
        run_backtest()


if __name__ == "__main__":
    ensure_pipeline_artifacts(force_rebuild=True)
