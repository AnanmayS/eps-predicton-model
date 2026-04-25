from __future__ import annotations

import io
import os
from pathlib import Path

import boto3
import joblib


def load_model_from_s3(
    bucket_name: str | None = None,
    object_key: str | None = None,
    region_name: str | None = None,
):
    resolved_bucket = bucket_name or os.getenv("MODEL_BUCKET", "earnings-model-artifacts")
    resolved_key = object_key or os.getenv("MODEL_OBJECT_KEY", "models/xgb_earnings_model.pkl")
    client = boto3.client("s3", region_name=region_name or os.getenv("AWS_REGION", "us-east-1"))

    buffer = io.BytesIO()
    client.download_fileobj(resolved_bucket, resolved_key, buffer)
    buffer.seek(0)
    return joblib.load(buffer)


def load_model_from_local_fallback():
    model_path = Path(__file__).resolve().parents[1] / "backend" / "models" / "xgb_earnings_model.pkl"
    return joblib.load(model_path)
