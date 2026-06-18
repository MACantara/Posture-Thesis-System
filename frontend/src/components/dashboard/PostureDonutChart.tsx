import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

interface PostureDonutChartProps {
  good: number;
  warning: number;
  poor: number;
}

export default function PostureDonutChart({ good, warning, poor }: PostureDonutChartProps) {
  const total = good + warning + poor;
  const data = [
    { name: 'Good', value: good, color: '#10b981' },
    { name: 'Warning', value: warning, color: '#f59e0b' },
    { name: 'Poor', value: poor, color: '#ef4444' },
  ].filter((d) => d.value > 0);

  const goodPercent = total > 0 ? Math.round((good / total) * 100) : 0;

  return (
    <div className="card flex flex-col items-center">
      <h3 className="text-sm text-slate-400 mb-4">Posture Distribution</h3>
      <div className="relative w-full h-48">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={3}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-3xl font-bold text-white">{goodPercent}%</span>
          <span className="text-xs text-slate-400">Good Posture</span>
        </div>
      </div>
      <div className="flex gap-4 mt-4">
        {data.map((d) => (
          <div key={d.name} className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: d.color }} />
            <span className="text-xs text-slate-400">{d.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
