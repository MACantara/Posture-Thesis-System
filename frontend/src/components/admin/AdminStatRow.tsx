import { Users, Activity, TrendingUp, Database } from 'lucide-react';

interface AdminStatRowProps {
  totalUsers: number;
  activeSessions: number;
  avgGoodRate: number;
  totalRecords: number;
}

export default function AdminStatRow({ totalUsers, activeSessions, avgGoodRate, totalRecords }: AdminStatRowProps) {
  const stats = [
    { label: 'Total Users', value: totalUsers, icon: <Users className="w-5 h-5" />, color: 'text-cyan-400' },
    { label: 'Active Sessions', value: activeSessions, icon: <Activity className="w-5 h-5" />, color: 'text-emerald-400' },
    { label: 'Avg Good Rate', value: `${avgGoodRate}%`, icon: <TrendingUp className="w-5 h-5" />, color: 'text-amber-400' },
    { label: 'Total Records', value: totalRecords, icon: <Database className="w-5 h-5" />, color: 'text-cyan-400' },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div key={stat.label} className="card flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <span className={stat.color}>{stat.icon}</span>
            <span className="text-sm text-slate-400">{stat.label}</span>
          </div>
          <span className="text-2xl font-bold text-white">{stat.value}</span>
        </div>
      ))}
    </div>
  );
}
