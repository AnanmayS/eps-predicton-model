import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import SectionCard from "./SectionCard";

function BacktestChart({ results }) {
  return (
    <SectionCard
      eyebrow="Backtesting"
      title="Rolling Out-of-Sample Performance"
      subtitle="Each point retrains on prior quarters and scores the next quarter only."
    >
      <div className="chart-shell">
        <ResponsiveContainer width="100%" height={340}>
          <LineChart data={results} margin={{ top: 8, right: 20, left: 0, bottom: 8 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" />
            <XAxis dataKey="test_quarter" stroke="#7f8aa3" />
            <YAxis stroke="#7f8aa3" domain={[0, 1]} />
            <Tooltip
              contentStyle={{ background: "#0d1324", border: "1px solid rgba(255,255,255,0.08)" }}
            />
            <Legend />
            <Line type="monotone" dataKey="accuracy" stroke="#5eead4" strokeWidth={2.5} dot={false} />
            <Line type="monotone" dataKey="precision" stroke="#60a5fa" strokeWidth={2.5} dot={false} />
            <Line type="monotone" dataKey="recall" stroke="#f59e0b" strokeWidth={2.5} dot={false} />
            <Line type="monotone" dataKey="roc_auc" stroke="#f472b6" strokeWidth={2.5} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </SectionCard>
  );
}

export default BacktestChart;
