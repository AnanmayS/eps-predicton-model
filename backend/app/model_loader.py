from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache

import joblib
import pandas as pd

from ml.bootstrap import ensure_pipeline_artifacts
from ml.config import (
    BACKTEST_RESULTS_PATH,
    FEATURE_IMPORTANCE_PATH,
    INFERENCE_FEATURES_PATH,
    METRICS_PATH,
    MODEL_PATH,
)


@dataclass
class ArtifactStore:
    model: object
    metrics: dict
    backtest_results: pd.DataFrame
    feature_importance: pd.DataFrame
    inference_features: pd.DataFrame


@lru_cache(maxsize=1)
def get_artifact_store() -> ArtifactStore:
    ensure_pipeline_artifacts()

    with open(METRICS_PATH, "r", encoding="utf-8") as metrics_file:
        metrics = json.load(metrics_file)

    return ArtifactStore(
        model=joblib.load(MODEL_PATH),
        metrics=metrics,
        backtest_results=pd.read_csv(BACKTEST_RESULTS_PATH),
        feature_importance=pd.read_csv(FEATURE_IMPORTANCE_PATH),
        inference_features=pd.read_csv(INFERENCE_FEATURES_PATH),
    )
