import { Clock, CheckCircle, AlertCircle, XCircle } from 'lucide-react';

interface SessionStatsProps {
  duration: number;
  goodCount: number;
  warningCount: number;
  poorCount: number;
}

export default function SessionStats({ duration, goodCount, warningCount, poorCount }: SessionStatsProps) {
  const total = goodCount + warningCount + poorCount;
  const goodRate = total > 0 ? Math.round((goodCount / total) * 100) : 0;

  const mins = Math.floor(duration / 60);
  const secs = Math.floor(duration % 60);

  return (
    <div className="card">
      <h3 className="text-sm text-slate-400 mb-4">Current Session</h3>
      <div className="grid grid-cols-2 gap-4">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-cyan-400" />
          <div>
            <div className="text-xs text-slate-400">Duration</div>
            <div className="text-lg font-bold text-white">{mins}m {secs}s</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-emerald-400" />
          <div>
            <div className="text-xs text-slate-400">Good Rate</div>
            <div className="text-lg font-bold text-white">{goodRate}%</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-amber-400" />
          <div>
            <div className="text-xs text-slate-400">Warnings</div>
            <div className="text-lg font-bold text-white">{warningCount}</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <XCircle className="w-5 h-5 text-red-400" />
          <div>
            <div className="text-xs text-slate-400">Poor</div>
            <div className="text-lg font-bold text-white">{poorCount}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
