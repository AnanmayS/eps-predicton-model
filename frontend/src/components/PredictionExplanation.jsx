import SectionCard from "./SectionCard";
import { formatFeatureSource } from "../utils/formatters";

function PredictionExplanation({ prediction }) {
  return (
    <SectionCard
      eyebrow="Explanation"
      title="What This Means"
      subtitle={
        prediction
          ? prediction.explanation
          : "Run a prediction to see a plain-English explanation of what pushed the model toward Beat or Miss."
      }
    >
      {prediction ? (
        <div className="explanation-list">
          <div className="explanation-item">
            Data used for this prediction: <strong>{formatFeatureSource(prediction.feature_source)}</strong>. Live market inputs are preferred when available.
          </div>
          {prediction.explanation_points.map((point) => (
            <div key={point} className="explanation-item">
              {point}
            </div>
          ))}
        </div>
      ) : null}
    </SectionCard>
  );
}

export default PredictionExplanation;
