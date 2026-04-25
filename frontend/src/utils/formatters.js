const TOKEN_MAP = {
  eps: "EPS",
  pe: "P/E",
  pre: "Pre",
  earnings: "Earnings",
  revenue: "Revenue",
  analyst: "Analyst",
  beat: "Beat",
  rate: "Rate",
  growth: "Growth",
  margin: "Margin",
  profit: "Profit",
  return: "Return",
  returns: "Returns",
  volatility: "Volatility",
  volume: "Volume",
  news: "News",
  change: "Change",
  direction: "Direction",
  trend: "Trend",
  ratio: "Ratio",
  equity: "Equity",
  debt: "Debt",
  sector: "Sector",
  days: "Days",
  since: "Since",
  last: "Last",
  trailing: "Trailing",
  reported: "Reported",
  revision: "Revision",
  mean: "Average",
  surprise: "Surprise",
  prior: "Prior",
};

function formatToken(token) {
  if (/^\d+[dq]$/i.test(token)) {
    return token.toUpperCase();
  }

  if (/^\d+d$/i.test(token)) {
    return token.toUpperCase();
  }

  return TOKEN_MAP[token] || token.charAt(0).toUpperCase() + token.slice(1);
}

export function formatFeatureLabel(label) {
  if (!label) {
    return "";
  }

  return label
    .split("_")
    .filter(Boolean)
    .map((token) => formatToken(token.toLowerCase()))
    .join(" ");
}

export function formatFeatureSource(source) {
  if (!source) {
    return "";
  }

  if (source === "historical_model_dataset") {
    return "Historical Model Inputs";
  }

  if (source === "live_market_inputs") {
    return "Live Market Inputs";
  }

  if (source === "estimated_inputs") {
    return "Estimated Inputs";
  }

  return source
    .split(/[\s_]+/)
    .filter(Boolean)
    .map((token) => token.charAt(0).toUpperCase() + token.slice(1))
    .join(" ");
}
