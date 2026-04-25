import SectionCard from "./SectionCard";

const metricConfig = [
  { key: "accuracy", label: "Accuracy" },
  { key: "precision", label: "Precision" },
  { key: "recall", label: "Recall" },
  { key: "f1_score", label: "F1 Score" },
  { key: "roc_auc", label: "ROC-AUC" },
];

function MetricsGrid({ metrics }) {
  return (
    <SectionCard
      eyebrow="Validation"
      title="Model Metrics"
      subtitle="Held-out chronological test results from the most recent segment of the training set."
    >
      <div className="metrics-grid">
        {metricConfig.map(({ key, label }) => (
          <div key={key} className="metric-tile">
            <span>{label}</span>
            <strong>{metrics ? `${Math.round((metrics[key] || 0) * 100)}%` : "--"}</strong>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

export default MetricsGrid;
