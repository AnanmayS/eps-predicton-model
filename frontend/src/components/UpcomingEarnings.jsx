import SectionCard from "./SectionCard";
import { formatFeatureSource } from "../utils/formatters";

function UpcomingEarnings({ rows }) {
  return (
    <SectionCard
      eyebrow="Upcoming Earnings"
      title="Watchlist"
      subtitle="A simple view of upcoming names and the current model call for each one."
    >
      <div className="table-shell">
        <table>
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Date</th>
              <th>Call</th>
              <th>Beat Probability</th>
              <th>Confidence</th>
              <th>Data</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.ticker}-${row.earnings_date}`}>
                <td>{row.ticker}</td>
                <td>{row.earnings_date}</td>
                <td>{row.prediction}</td>
                <td>{Math.round(row.probability_beat * 100)}%</td>
                <td>{row.confidence}</td>
                <td>{formatFeatureSource(row.feature_source)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SectionCard>
  );
}

export default UpcomingEarnings;
