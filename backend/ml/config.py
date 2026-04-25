from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

RAW_EVENTS_PATH = RAW_DIR / "earnings_events.csv"
PROCESSED_FEATURES_PATH = PROCESSED_DIR / "model_features.csv"
INFERENCE_FEATURES_PATH = PROCESSED_DIR / "inference_features.csv"
MODEL_PATH = MODELS_DIR / "xgb_earnings_model.pkl"
METRICS_PATH = REPORTS_DIR / "metrics.json"
FEATURE_IMPORTANCE_PATH = REPORTS_DIR / "feature_importance.csv"
BACKTEST_RESULTS_PATH = REPORTS_DIR / "backtest_results.csv"

TARGET_COLUMN = "beat_miss"
DATE_COLUMN = "earnings_date"

NUMERIC_FEATURES = [
    "return_5d_pre_earnings",
    "return_20d_pre_earnings",
    "return_60d_pre_earnings",
    "volatility_20d_pre_earnings",
    "volume_change_20d_pre_earnings",
    "news_sentiment_pre_earnings",
    "revenue_growth_last_reported",
    "eps_growth_last_reported",
    "analyst_revision_trend",
    "pe_ratio",
    "debt_to_equity",
    "profit_margin",
    "prior_eps_surprise",
    "eps_surprise_mean_4q",
    "trailing_beat_rate_4q",
    "days_since_last_earnings",
]

CATEGORICAL_FEATURES = ["sector"]

FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES
