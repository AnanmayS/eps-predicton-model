import SectionCard from "./SectionCard";

function RecentPredictionsTable({ rows }) {
  return (
    <SectionCard
      eyebrow="Inference Log"
      title="Recent Predictions"
      subtitle="Sample prediction responses generated from the dashboard for quick comparison."
    >
      <div className="table-shell">
        <table>
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Prediction</th>
              <th>Probability</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.ticker}>
                <td>{row.ticker}</td>
                <td>{row.prediction}</td>
                <td>{Math.round(row.probability_beat * 100)}%</td>
                <td>{row.confidence}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SectionCard>
  );
}

export default RecentPredictionsTable;
