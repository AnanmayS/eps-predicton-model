import { useEffect, useState } from "react";
import BacktestChart from "../components/BacktestChart";
import FeatureImportanceChart from "../components/FeatureImportanceChart";
import Hero from "../components/Hero";
import MetricsGrid from "../components/MetricsGrid";
import ModelRigor from "../components/ModelRigor";
import PredictionCard from "../components/PredictionCard";
import PredictionExplanation from "../components/PredictionExplanation";
import SearchPanel from "../components/SearchPanel";
import SectionCard from "../components/SectionCard";
import UpcomingEarnings from "../components/UpcomingEarnings";
import {
  fetchBacktest,
  fetchFeatureImportance,
  fetchHealth,
  fetchMetrics,
  fetchTickers,
  fetchUpcomingEarnings,
  getApiBaseUrl,
  predictTicker,
} from "../api/client";

function DashboardPage() {
  const [healthMessage, setHealthMessage] = useState("");
  const [tickers, setTickers] = useState([]);
  const [tickerInput, setTickerInput] = useState("AAPL");
  const [prediction, setPrediction] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [backtestResults, setBacktestResults] = useState([]);
  const [featureImportance, setFeatureImportance] = useState([]);
  const [upcomingEarnings, setUpcomingEarnings] = useState([]);
  const [loadingPrediction, setLoadingPrediction] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [health, tickersResponse, metricsResponse, backtestResponse, importanceResponse, upcomingResponse] =
          await Promise.all([
            fetchHealth(),
            fetchTickers(),
            fetchMetrics(),
            fetchBacktest(),
            fetchFeatureImportance(),
            fetchUpcomingEarnings(),
          ]);

        const availableTickers = tickersResponse.tickers || [];
        setHealthMessage(health.message);
        setTickers(availableTickers);
        setMetrics(metricsResponse);
        setBacktestResults(backtestResponse.results || []);
        setFeatureImportance(importanceResponse.features || []);
        setUpcomingEarnings(upcomingResponse.results || []);
        const initialTicker = availableTickers[0] || "AAPL";
        setTickerInput(initialTicker);
        const initialPrediction = await predictTicker(initialTicker);
        setPrediction(initialPrediction);
      } catch (loadError) {
        setError(loadError.message);
      }
    }

    loadDashboard();
  }, []);

  async function handlePrediction() {
    const normalizedTicker = tickerInput.trim().toUpperCase();
    if (!normalizedTicker) {
      return;
    }

    setLoadingPrediction(true);
    setError("");
    try {
      const response = await predictTicker(normalizedTicker);
      setPrediction(response);
      setTickerInput(response.ticker);
    } catch (predictionError) {
      setError(predictionError.message);
    } finally {
      setLoadingPrediction(false);
    }
  }

  return (
    <main className="dashboard-shell">
      <div className="dashboard-grid">
        <Hero healthMessage={healthMessage} />
        <div className="dashboard-grid__pair">
          <SearchPanel
            suggestions={tickers}
            tickerInput={tickerInput}
            onTickerChange={setTickerInput}
            onSubmit={handlePrediction}
            loading={loadingPrediction}
          />
          <PredictionCard prediction={prediction} />
        </div>
        <PredictionExplanation prediction={prediction} />
        {error ? (
          <SectionCard
            eyebrow="Connection"
            title="Backend Request Failed"
            subtitle={`Point the frontend to a running API. Current base URL: ${getApiBaseUrl()}`}
          >
            <p className="error-copy">{error}</p>
          </SectionCard>
        ) : null}
        <MetricsGrid metrics={metrics} />
        <ModelRigor metrics={metrics} />
        <div className="dashboard-grid__pair dashboard-grid__pair--charts">
          <BacktestChart results={backtestResults} />
          <FeatureImportanceChart features={featureImportance} />
        </div>
        <UpcomingEarnings rows={upcomingEarnings} />
      </div>
    </main>
  );
}

export default DashboardPage;
