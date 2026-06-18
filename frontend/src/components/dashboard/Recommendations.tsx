import { Lightbulb } from 'lucide-react';

interface RecommendationsProps {
  poorCount: number;
  warningCount: number;
}

export default function Recommendations({ poorCount, warningCount }: RecommendationsProps) {
  const tips: string[] = [];

  if (poorCount > 10) {
    tips.push('Consider taking a 5-minute break every hour to stretch your back and shoulders.');
  }
  if (warningCount > 15) {
    tips.push('Your posture tends to drift — try recalibrating the sensor for better accuracy.');
  }
  if (poorCount + warningCount < 5) {
    tips.push('Excellent posture today! Keep up the great work.');
  }
  if (tips.length === 0) {
    tips.push('Maintain a neutral spine position and keep your screen at eye level.');
  }

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-3">
        <Lightbulb className="w-5 h-5 text-amber-400" />
        <h3 className="text-sm text-slate-400">Recommendations</h3>
      </div>
      <ul className="space-y-2">
        {tips.map((tip, i) => (
          <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
            <span className="text-cyan-400 mt-0.5">•</span>
            <span>{tip}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
