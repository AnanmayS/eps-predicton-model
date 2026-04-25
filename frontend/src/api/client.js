const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export function getApiBaseUrl() {
  return API_BASE_URL;
}

export function fetchHealth() {
  return request("/");
}

export function fetchTickers() {
  return request("/tickers");
}

export function fetchMetrics() {
  return request("/metrics");
}

export function fetchBacktest() {
  return request("/backtest");
}

export function fetchFeatureImportance() {
  return request("/feature-importance");
}

export function fetchUpcomingEarnings() {
  return request("/upcoming-earnings");
}

export function predictTicker(ticker) {
  return request("/predict", {
    method: "POST",
    body: JSON.stringify({ ticker }),
  });
}
