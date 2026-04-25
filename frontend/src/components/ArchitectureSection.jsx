import SectionCard from "./SectionCard";

const nodes = [
  "Data ingestion",
  "Feature engineering",
  "XGBoost training",
  "Model artifact",
  "FastAPI / Lambda",
  "React dashboard",
];

function ArchitectureSection() {
  return (
    <SectionCard
      eyebrow="Architecture"
      title="End-to-End System Flow"
      subtitle="Structured to resemble an AWS deployment path while staying easy to run locally."
    >
      <div className="architecture-flow">
        {nodes.map((node, index) => (
          <div key={node} className="architecture-flow__item">
            <div className="architecture-node">{node}</div>
            {index < nodes.length - 1 ? <span className="architecture-arrow">→</span> : null}
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

export default ArchitectureSection;
