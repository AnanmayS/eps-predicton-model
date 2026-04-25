from __future__ import annotations

import json
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

from ml.config import (
    CATEGORICAL_FEATURES,
    DATE_COLUMN,
    FEATURE_COLUMNS,
    FEATURE_IMPORTANCE_PATH,
    METRICS_PATH,
    MODEL_PATH,
    MODELS_DIR,
    NUMERIC_FEATURES,
    PROCESSED_FEATURES_PATH,
    REPORTS_DIR,
    TARGET_COLUMN,
)


def build_model_pipeline() -> Pipeline:
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, NUMERIC_FEATURES),
            ("categorical", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )

    classifier = XGBClassifier(
        n_estimators=250,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.85,
        min_child_weight=2,
        reg_alpha=0.1,
        reg_lambda=1.2,
        random_state=42,
        eval_metric="logloss",
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )


def chronological_split(df: pd.DataFrame, train_fraction: float = 0.8) -> Tuple[pd.DataFrame, pd.DataFrame]:
    ordered = df.sort_values(DATE_COLUMN).reset_index(drop=True)
    unique_dates = sorted(pd.to_datetime(ordered[DATE_COLUMN]).dt.normalize().unique())
    split_index = max(1, int(len(unique_dates) * train_fraction))
    split_index = min(split_index, len(unique_dates) - 1)
    cutoff_date = unique_dates[split_index]

    train_df = ordered[ordered[DATE_COLUMN] < cutoff_date].copy()
    test_df = ordered[ordered[DATE_COLUMN] >= cutoff_date].copy()

    if train_df.empty or test_df.empty:
        fallback_index = max(1, min(len(ordered) - 1, int(len(ordered) * train_fraction)))
        train_df = ordered.iloc[:fallback_index].copy()
        test_df = ordered.iloc[fallback_index:].copy()

    return train_df, test_df


def choose_classification_threshold(train_df: pd.DataFrame) -> float:
    if len(train_df) < 30:
        return 0.5

    validation_fraction = 0.2
    ordered = train_df.sort_values(DATE_COLUMN).reset_index(drop=True)
    split_index = max(1, int(len(ordered) * (1 - validation_fraction)))
    split_index = min(split_index, len(ordered) - 1)

    fit_df = ordered.iloc[:split_index].copy()
    validation_df = ordered.iloc[split_index:].copy()
    if fit_df.empty or validation_df.empty:
        return 0.5

    pipeline = build_model_pipeline()
    pipeline.fit(fit_df[FEATURE_COLUMNS], fit_df[TARGET_COLUMN])
    validation_probabilities = pipeline.predict_proba(validation_df[FEATURE_COLUMNS])[:, 1]

    candidate_thresholds = [round(value, 2) for value in np.arange(0.35, 0.71, 0.05)]
    best_threshold = 0.5
    best_score = -1.0

    for threshold in candidate_thresholds:
        predictions = (validation_probabilities >= threshold).astype(int)
        score = accuracy_score(validation_df[TARGET_COLUMN], predictions)
        if score > best_score or (score == best_score and abs(threshold - 0.5) < abs(best_threshold - 0.5)):
            best_score = score
            best_threshold = threshold

    return best_threshold


def evaluate_predictions(
    y_true: pd.Series,
    probabilities: np.ndarray,
    threshold: float,
) -> Dict[str, float | list[list[int]]]:
    predictions = (probabilities >= threshold).astype(int)
    roc_auc = roc_auc_score(y_true, probabilities) if y_true.nunique() > 1 else None
    metrics: Dict[str, float | list[list[int]]] = {
        "accuracy": round(float(accuracy_score(y_true, predictions)), 4),
        "precision": round(float(precision_score(y_true, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, predictions, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, predictions, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc), 4) if roc_auc is not None else None,
        "confusion_matrix": confusion_matrix(y_true, predictions).tolist(),
        "support": int(len(y_true)),
        "positive_rate": round(float(np.mean(y_true)), 4),
    }
    return metrics


def compute_baseline_metrics(y_true: pd.Series, reference_positive_rate: float) -> dict:
    majority_class = int(reference_positive_rate >= 0.5)
    baseline_predictions = np.full(len(y_true), majority_class)
    baseline_accuracy = accuracy_score(y_true, baseline_predictions)
    return {
        "strategy": "predict training-period majority class",
        "majority_class": "Beat" if majority_class == 1 else "Miss",
        "accuracy": round(float(baseline_accuracy), 4),
    }


def compute_calibration_bins(y_true: pd.Series, probabilities: np.ndarray, bins: int = 5) -> list[dict]:
    calibration_frame = pd.DataFrame({"actual": y_true.to_numpy(), "probability": probabilities})
    calibration_frame["bin"] = pd.cut(
        calibration_frame["probability"],
        bins=np.linspace(0, 1, bins + 1),
        include_lowest=True,
    )

    results: list[dict] = []
    for interval, group in calibration_frame.groupby("bin", observed=False):
        if group.empty:
            continue
        results.append(
            {
                "range": f"{interval.left:.1f}-{interval.right:.1f}",
                "count": int(len(group)),
                "avg_predicted_probability": round(float(group["probability"].mean()), 4),
                "actual_beat_rate": round(float(group["actual"].mean()), 4),
            }
        )
    return results


def compute_threshold_analysis(y_true: pd.Series, probabilities: np.ndarray) -> list[dict]:
    thresholds = [0.4, 0.5, 0.6, 0.7]
    rows: list[dict] = []
    for threshold in thresholds:
        predictions = (probabilities >= threshold).astype(int)
        rows.append(
            {
                "threshold": threshold,
                "precision": round(float(precision_score(y_true, predictions, zero_division=0)), 4),
                "recall": round(float(recall_score(y_true, predictions, zero_division=0)), 4),
                "f1_score": round(float(f1_score(y_true, predictions, zero_division=0)), 4),
                "predicted_beat_rate": round(float(predictions.mean()), 4),
            }
        )
    return rows


def compute_sector_breakdown(
    test_features: pd.DataFrame,
    y_true: pd.Series,
    probabilities: np.ndarray,
) -> list[dict]:
    sector_frame = test_features[["sector"]].copy()
    sector_frame["actual"] = y_true.to_numpy()
    sector_frame["probability"] = probabilities
    sector_frame["prediction"] = (probabilities >= 0.5).astype(int)

    rows: list[dict] = []
    for sector, group in sector_frame.groupby("sector"):
        if len(group) < 4:
            continue
        rows.append(
            {
                "sector": sector,
                "count": int(len(group)),
                "accuracy": round(float(accuracy_score(group["actual"], group["prediction"])), 4),
                "beat_rate": round(float(group["actual"].mean()), 4),
                "avg_probability": round(float(group["probability"].mean()), 4),
            }
        )
    return sorted(rows, key=lambda row: row["count"], reverse=True)


def build_model_summary(metrics: dict) -> list[str]:
    summary = [
        f"On the held-out time-based test set, the model was correct {metrics['accuracy'] * 100:.1f}% of the time.",
        f"It achieved an ROC-AUC of {metrics['roc_auc'] * 100:.1f}% and an F1 score of {metrics['f1_score'] * 100:.1f}%.",
        f"The majority-class baseline reached {metrics['baseline']['accuracy'] * 100:.1f}% accuracy, while the model produced a stronger probability ranking with ROC-AUC {metrics['roc_auc_lift_vs_random_pct_points']:.1f} points above random chance.",
    ]
    return summary


def train_model(data_path: str | None = None) -> dict:
    source_path = PROCESSED_FEATURES_PATH if data_path is None else data_path
    df = pd.read_csv(source_path)
    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN])
    train_df, test_df = chronological_split(df)

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]

    pipeline = build_model_pipeline()
    pipeline.fit(X_train, y_train)
    classification_threshold = choose_classification_threshold(train_df)

    probabilities = pipeline.predict_proba(X_test)[:, 1]
    metrics = evaluate_predictions(y_test, probabilities, classification_threshold)
    baseline = compute_baseline_metrics(y_test, float(y_train.mean()))
    metrics["baseline"] = baseline
    metrics["lift_vs_baseline_accuracy_pct_points"] = round(
        (metrics["accuracy"] - baseline["accuracy"]) * 100,
        2,
    )
    metrics["roc_auc_lift_vs_random_pct_points"] = round(
        ((metrics["roc_auc"] or 0.5) - 0.5) * 100,
        2,
    )
    metrics["brier_score"] = round(float(brier_score_loss(y_test, probabilities)), 4)
    metrics["log_loss"] = round(float(log_loss(y_test, probabilities, labels=[0, 1])), 4)
    metrics["calibration_bins"] = compute_calibration_bins(y_test, probabilities)
    metrics["threshold_analysis"] = compute_threshold_analysis(y_test, probabilities)
    metrics["sector_breakdown"] = compute_sector_breakdown(X_test, y_test, probabilities)
    metrics.update(
        {
            "train_rows": int(len(train_df)),
            "test_rows": int(len(test_df)),
            "train_start": train_df[DATE_COLUMN].min().date().isoformat(),
            "train_end": train_df[DATE_COLUMN].max().date().isoformat(),
            "test_start": test_df[DATE_COLUMN].min().date().isoformat(),
            "test_end": test_df[DATE_COLUMN].max().date().isoformat(),
            "classification_threshold": classification_threshold,
        }
    )
    metrics["model_summary"] = build_model_summary(metrics)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    with open(METRICS_PATH, "w", encoding="utf-8") as metrics_file:
        json.dump(metrics, metrics_file, indent=2)

    scoring_metric = "roc_auc" if y_test.nunique() > 1 else "accuracy"
    importance = permutation_importance(
        pipeline,
        X_test,
        y_test,
        n_repeats=10,
        random_state=42,
        scoring=scoring_metric,
    )
    importance_frame = (
        pd.DataFrame(
            {
                "feature": FEATURE_COLUMNS,
                "importance": importance.importances_mean,
                "importance_std": importance.importances_std,
            }
        )
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )
    importance_frame.to_csv(FEATURE_IMPORTANCE_PATH, index=False)

    return metrics


if __name__ == "__main__":
    train_model()
