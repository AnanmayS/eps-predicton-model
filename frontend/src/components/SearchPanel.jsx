import SectionCard from "./SectionCard";

function SearchPanel({ suggestions, tickerInput, onTickerChange, onSubmit, loading }) {
  return (
    <SectionCard
      eyebrow="Inference"
      title="Check Any Ticker"
      subtitle="Enter a U.S. stock ticker. The app uses live market inputs whenever available, then falls back to historical model inputs or estimated inputs so the experience stays reliable."
    >
      <div className="search-panel">
        <div className="search-panel__field">
          <input
            list="ticker-suggestions"
            value={tickerInput}
            placeholder="AAPL, MSFT, JPM, COST..."
            onChange={(event) => onTickerChange(event.target.value.toUpperCase())}
          />
          <datalist id="ticker-suggestions">
            {suggestions.map((ticker) => (
              <option key={ticker} value={ticker} />
            ))}
          </datalist>
          <div className="search-panel__suggestions">
            {suggestions.slice(0, 6).map((ticker) => (
              <button key={ticker} type="button" className="search-chip" onClick={() => onTickerChange(ticker)}>
                {ticker}
              </button>
            ))}
          </div>
        </div>
        <button
          type="button"
          className="search-panel__submit"
          onClick={onSubmit}
          disabled={loading || !tickerInput.trim()}
        >
          {loading ? "Scoring..." : "Predict Beat/Miss"}
        </button>
      </div>
    </SectionCard>
  );
}

export default SearchPanel;
