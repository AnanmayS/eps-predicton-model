from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from ml.predict import predict_ticker  # noqa: E402


def lambda_handler(event: dict, _context: object) -> dict:
    body = event.get("body")
    payload = json.loads(body) if isinstance(body, str) else (body or {})
    ticker = str(payload.get("ticker", "")).upper()

    if not ticker:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "ticker is required"}),
        }

    response = predict_ticker(ticker)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response),
    }


handler = lambda_handler
