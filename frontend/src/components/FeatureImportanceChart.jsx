import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import SectionCard from "./SectionCard";
import { formatFeatureLabel } from "../utils/formatters";

function FeatureImportanceChart({ features }) {
  return (
    <SectionCard
      eyebrow="Interpretability"
      title="Top Predictive Features"
      subtitle="Permutation importance from the held-out evaluation slice."
    >
      <div className="chart-shell">
        <ResponsiveContainer width="100%" height={340}>
          <BarChart data={features} layout="vertical" margin={{ top: 8, right: 16, left: 16, bottom: 8 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" horizontal={false} />
            <XAxis type="number" stroke="#7f8aa3" />
            <YAxis
              type="category"
              dataKey="feature"
              width={180}
              stroke="#dce6ff"
              tickFormatter={formatFeatureLabel}
              tick={{ fontSize: 12 }}
            />
            <Tooltip
              cursor={{ fill: "rgba(123, 220, 181, 0.08)" }}
              contentStyle={{ background: "#0d1324", border: "1px solid rgba(255,255,255,0.08)" }}
              formatter={(value) => [Number(value).toFixed(4), "Importance"]}
              labelFormatter={formatFeatureLabel}
            />
            <Bar dataKey="importance" fill="url(#featureGradient)" radius={[0, 8, 8, 0]} />
            <defs>
              <linearGradient id="featureGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#5eead4" />
                <stop offset="100%" stopColor="#60a5fa" />
              </linearGradient>
            </defs>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </SectionCard>
  );
}

export default FeatureImportanceChart;
