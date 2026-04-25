import json

import pandas as pd

from ml.bootstrap import ensure_pipeline_artifacts
from ml.config import METRICS_PATH, PROCESSED_FEATURES_PATH


def test_processed_features_include_sentiment_and_are_not_null() -> None:
    ensure_pipeline_artifacts()
    dataset = pd.read_csv(PROCESSED_FEATURES_PATH)

    assert "news_sentiment_pre_earnings" in dataset.columns
    assert dataset["news_sentiment_pre_earnings"].notna().all()


def test_metrics_report_contains_rigor_sections() -> None:
    ensure_pipeline_artifacts()

    with open(METRICS_PATH, "r", encoding="utf-8") as metrics_file:
        metrics = json.load(metrics_file)

    assert "baseline" in metrics
    assert "calibration_bins" in metrics
    assert "threshold_analysis" in metrics
    assert "sector_breakdown" in metrics
    assert "model_summary" in metrics
