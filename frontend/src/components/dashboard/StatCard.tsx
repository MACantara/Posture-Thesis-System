interface StatCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  accent?: string;
}

export default function StatCard({ label, value, icon, accent = 'text-cyan-400' }: StatCardProps) {
  return (
    <div className="card flex flex-col gap-2">
      <div className="flex items-center gap-2">
        {icon && <span className={accent}>{icon}</span>}
        <span className="text-sm text-slate-400">{label}</span>
      </div>
      <span className="text-2xl font-bold text-white">{value}</span>
    </div>
  );
}
