from __future__ import annotations

import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score

from ml.config import BACKTEST_RESULTS_PATH, DATE_COLUMN, FEATURE_COLUMNS, PROCESSED_FEATURES_PATH, REPORTS_DIR, TARGET_COLUMN
from ml.train_model import build_model_pipeline


def run_backtest(data_path: str | None = None) -> pd.DataFrame:
    source_path = PROCESSED_FEATURES_PATH if data_path is None else data_path
    df = pd.read_csv(source_path)
    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN])
    df["earnings_quarter"] = df[DATE_COLUMN].dt.to_period("Q").astype(str)

    unique_quarters = sorted(df["earnings_quarter"].unique())
    results: list[dict] = []

    minimum_training_quarters = 8
    for quarter_index in range(minimum_training_quarters, len(unique_quarters)):
        test_quarter = unique_quarters[quarter_index]
        train_quarters = unique_quarters[:quarter_index]

        train_df = df[df["earnings_quarter"].isin(train_quarters)].copy()
        test_df = df[df["earnings_quarter"] == test_quarter].copy()

        if train_df.empty or test_df.empty:
            continue

        model = build_model_pipeline()
        model.fit(train_df[FEATURE_COLUMNS], train_df[TARGET_COLUMN])
        probabilities = model.predict_proba(test_df[FEATURE_COLUMNS])[:, 1]
        predictions = (probabilities >= 0.5).astype(int)

        auc = roc_auc_score(test_df[TARGET_COLUMN], probabilities) if test_df[TARGET_COLUMN].nunique() > 1 else None
        results.append(
            {
                "test_quarter": test_quarter,
                "train_rows": int(len(train_df)),
                "test_rows": int(len(test_df)),
                "accuracy": round(float(accuracy_score(test_df[TARGET_COLUMN], predictions)), 4),
                "precision": round(float(precision_score(test_df[TARGET_COLUMN], predictions, zero_division=0)), 4),
                "recall": round(float(recall_score(test_df[TARGET_COLUMN], predictions, zero_division=0)), 4),
                "roc_auc": round(float(auc), 4) if auc is not None else None,
            }
        )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    results_frame = pd.DataFrame(results)
    results_frame.to_csv(BACKTEST_RESULTS_PATH, index=False)
    return results_frame


if __name__ == "__main__":
    run_backtest()
