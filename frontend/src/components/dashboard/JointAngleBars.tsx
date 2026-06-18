interface JointAngleBarsProps {
  angle: number;
  status: string;
}

export default function JointAngleBars({ angle, status }: JointAngleBarsProps) {
  const maxAngle = 45;
  const percent = Math.min((angle / maxAngle) * 100, 100);

  const barColor = status === 'good' ? '#10b981' : status === 'warning' ? '#f59e0b' : '#ef4444';

  return (
    <div className="card">
      <h3 className="text-sm text-slate-400 mb-4">Joint Angle</h3>
      <div className="space-y-4">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-400">Spine Deviation</span>
            <span className="text-white font-medium">{angle.toFixed(1)}°</span>
          </div>
          <div className="h-3 bg-posture-dark rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-300"
              style={{ width: `${percent}%`, backgroundColor: barColor }}
            />
          </div>
        </div>
        <div className="flex gap-2 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="text-slate-400">Good (0-10°)</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-amber-500" />
            <span className="text-slate-400">Warning (10-20°)</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-red-500" />
            <span className="text-slate-400">Poor (20°+)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
