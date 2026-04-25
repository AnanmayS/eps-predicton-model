function Hero({ healthMessage }) {
  return (
    <section className="hero">
      <div className="hero__copy">
        <span className="eyebrow">Applied ML Project</span>
        <h1>Earnings Beat/Miss Predictor</h1>
        <p>
          A full-stack machine learning project that predicts whether a company is likely to beat
          or miss earnings expectations using only pre-earnings market and financial signals.
        </p>
        <div className="hero__highlights hero__highlights--compact">
          <div>
            <strong>Time-aware features</strong>
            <span>Built from data available before earnings</span>
          </div>
          <div>
            <strong>Leakage-safe model</strong>
            <span>No post-earnings information used</span>
          </div>
          <div>
            <strong>Practical evaluation</strong>
            <span>Backtests, calibration, and plain-English explanations</span>
          </div>
        </div>
      </div>
      <div className="hero__panel">
        <div className="status-chip">
          <span className="status-chip__dot" />
          {healthMessage || "Checking backend health..."}
        </div>
        <div className="hero__stat-grid hero__stat-grid--simple">
          <div>
            <span>Prediction target</span>
            <strong>Beat vs Miss</strong>
          </div>
          <div>
            <span>Model</span>
            <strong>XGBoost classifier</strong>
          </div>
          <div>
            <span>Coverage</span>
            <strong>Live-first ticker lookup</strong>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Hero;
