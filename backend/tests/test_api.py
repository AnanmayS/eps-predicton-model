from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_predict_endpoint_returns_explanation_and_source() -> None:
    response = client.post("/predict", json={"ticker": "AAPL"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["ticker"] == "AAPL"
    assert "prediction" in payload
    assert "feature_source" in payload
    assert payload["explanation"]
    assert payload["explanation_points"]


def test_upcoming_earnings_endpoint_returns_rows() -> None:
    response = client.get("/upcoming-earnings")
    assert response.status_code == 200

    payload = response.json()
    assert "results" in payload
    assert len(payload["results"]) > 0
    assert "ticker" in payload["results"][0]
