import SectionCard from "./SectionCard";
import { formatFeatureLabel, formatFeatureSource } from "../utils/formatters";

function PredictionCard({ prediction }) {
  if (!prediction) {
    return (
      <SectionCard
        eyebrow="Prediction"
        title="Awaiting Selection"
        subtitle="Choose a ticker to see probability, confidence, and the strongest drivers."
      />
    );
  }

  const probabilityPercent = `${Math.round(prediction.probability_beat * 100)}%`;
  const outcomeClass =
    prediction.prediction === "Beat" ? "prediction-card prediction-card--beat" : "prediction-card prediction-card--miss";

  return (
    <SectionCard eyebrow="Prediction" title={`${prediction.ticker} Outlook`} className={outcomeClass}>
      <div className="prediction-card__hero">
        <div>
          <span className="prediction-card__label">Model Call</span>
          <strong>{prediction.prediction}</strong>
        </div>
        <div>
          <span className="prediction-card__label">Probability Of Beat</span>
          <strong>{probabilityPercent}</strong>
        </div>
        <div>
          <span className="prediction-card__label">Confidence</span>
          <strong>{prediction.confidence}</strong>
        </div>
        <div>
          <span className="prediction-card__label">Next Earnings Date</span>
          <strong>{prediction.next_earnings_date}</strong>
        </div>
      </div>
      <div className="prediction-card__meta">
        <span>Feature source</span>
        <strong>{formatFeatureSource(prediction.feature_source)}</strong>
      </div>
      <div className="prediction-card__features">
        {prediction.top_features.map((item) => (
          <div key={item.feature} className="feature-pill">
            <span>{formatFeatureLabel(item.feature)}</span>
            <strong>{item.value}</strong>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

export default PredictionCard;
