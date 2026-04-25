import SectionCard from "./SectionCard";

function ModelRigor({ metrics }) {
  if (!metrics) {
    return (
      <SectionCard
        eyebrow="Model Evaluation"
        title="Validation Checks"
        subtitle="Loading validation details."
      />
    );
  }

  return (
    <SectionCard
      eyebrow="Model Evaluation"
      title="Validation Checks"
      subtitle="These views show whether the model is learning something useful beyond a simple baseline."
    >
      <div className="rigor-summary">
        {metrics.model_summary?.map((line) => (
          <div key={line} className="explanation-item">
            {line}
          </div>
        ))}
      </div>
      <div className="rigor-tiles">
        <div className="metric-tile">
          <span>Baseline Accuracy</span>
          <strong>{Math.round((metrics.baseline?.accuracy || 0) * 100)}%</strong>
        </div>
        <div className="metric-tile">
          <span>ROC-AUC vs Random</span>
          <strong>{metrics.roc_auc_lift_vs_random_pct_points || 0} pts</strong>
        </div>
        <div className="metric-tile">
          <span>Brier Score</span>
          <strong>{metrics.brier_score}</strong>
        </div>
        <div className="metric-tile">
          <span>Log Loss</span>
          <strong>{metrics.log_loss}</strong>
        </div>
      </div>
      <div className="dashboard-grid__pair dashboard-grid__pair--charts">
        <div className="table-card">
          <h3>Calibration Check</h3>
          <p>Predicted probability versus actual beat rate in each score bucket.</p>
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Bucket</th>
                  <th>Count</th>
                  <th>Predicted</th>
                  <th>Actual</th>
                </tr>
              </thead>
              <tbody>
                {metrics.calibration_bins?.map((row) => (
                  <tr key={row.range}>
                    <td>{row.range}</td>
                    <td>{row.count}</td>
                    <td>{Math.round(row.avg_predicted_probability * 100)}%</td>
                    <td>{Math.round(row.actual_beat_rate * 100)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="table-card">
          <h3>Threshold Trade-Offs</h3>
          <p>Higher thresholds make Beat calls rarer but usually more selective.</p>
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Threshold</th>
                  <th>Precision</th>
                  <th>Recall</th>
                  <th>Beat Call Rate</th>
                </tr>
              </thead>
              <tbody>
                {metrics.threshold_analysis?.map((row) => (
                  <tr key={row.threshold}>
                    <td>{row.threshold}</td>
                    <td>{Math.round(row.precision * 100)}%</td>
                    <td>{Math.round(row.recall * 100)}%</td>
                    <td>{Math.round(row.predicted_beat_rate * 100)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div className="table-card table-card--full">
        <h3>Sector Breakdown</h3>
        <p>Held-out test performance by sector for groups with enough observations.</p>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Sector</th>
                <th>Rows</th>
                <th>Accuracy</th>
                <th>Actual Beat Rate</th>
                <th>Average Model Probability</th>
              </tr>
            </thead>
            <tbody>
              {metrics.sector_breakdown?.map((row) => (
                <tr key={row.sector}>
                  <td>{row.sector}</td>
                  <td>{row.count}</td>
                  <td>{Math.round(row.accuracy * 100)}%</td>
                  <td>{Math.round(row.beat_rate * 100)}%</td>
                  <td>{Math.round(row.avg_probability * 100)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </SectionCard>
  );
}

export default ModelRigor;
