interface PostureSilhouetteProps {
  status: 'good' | 'warning' | 'poor' | 'idle';
}

const STATUS_COLORS: Record<string, { glow: string; fill: string; label: string }> = {
  good: { glow: '#10b981', fill: '#10b98140', label: 'Good Posture' },
  warning: { glow: '#f59e0b', fill: '#f59e0b40', label: 'Warning' },
  poor: { glow: '#ef4444', fill: '#ef444440', label: 'Poor Posture' },
  idle: { glow: '#64748b', fill: '#64748b30', label: 'Idle' },
};

export default function PostureSilhouette({ status }: PostureSilhouetteProps) {
  const config = STATUS_COLORS[status] || STATUS_COLORS.idle;

  return (
    <div className="card flex flex-col items-center">
      <h3 className="text-sm text-slate-400 mb-4">Posture Status</h3>
      <div className="relative w-48 h-64 flex items-center justify-center">
        <svg viewBox="0 0 100 130" className="w-full h-full">
          {/* Head */}
          <circle
            cx="50" cy="15" r="10"
            fill={config.fill}
            stroke={config.glow}
            strokeWidth="2"
            style={{ filter: `drop-shadow(0 0 4px ${config.glow})`, transition: 'all 0.5s ease' }}
          />
          {/* Spine */}
          <line
            x1="50" y1="25" x2="50" y2="80"
            stroke={config.glow}
            strokeWidth="3"
            strokeLinecap="round"
            style={{ filter: `drop-shadow(0 0 3px ${config.glow})`, transition: 'all 0.5s ease' }}
          />
          {/* Shoulders */}
          <line
            x1="30" y1="35" x2="70" y2="35"
            stroke={config.glow}
            strokeWidth="3"
            strokeLinecap="round"
            style={{ transition: 'all 0.5s ease' }}
          />
          {/* Arms */}
          <line x1="30" y1="35" x2="25" y2="60" stroke={config.glow} strokeWidth="2.5" strokeLinecap="round" opacity="0.7" />
          <line x1="70" y1="35" x2="75" y2="60" stroke={config.glow} strokeWidth="2.5" strokeLinecap="round" opacity="0.7" />
          {/* Hips */}
          <line
            x1="35" y1="80" x2="65" y2="80"
            stroke={config.glow}
            strokeWidth="3"
            strokeLinecap="round"
            style={{ transition: 'all 0.5s ease' }}
          />
          {/* Legs */}
          <line x1="40" y1="80" x2="38" y2="115" stroke={config.glow} strokeWidth="2.5" strokeLinecap="round" opacity="0.7" />
          <line x1="60" y1="80" x2="62" y2="115" stroke={config.glow} strokeWidth="2.5" strokeLinecap="round" opacity="0.7" />
        </svg>
      </div>
      <span className="text-lg font-semibold mt-2" style={{ color: config.glow, transition: 'color 0.5s ease' }}>
        {config.label}
      </span>
    </div>
  );
}
