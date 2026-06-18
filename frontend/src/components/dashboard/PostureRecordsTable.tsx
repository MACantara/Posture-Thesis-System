import { useState } from 'react';
import type { PostureRecord } from '../../api/posture';

const STATUS_COLORS: Record<string, string> = {
  good: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  warning: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  poor: 'bg-red-500/20 text-red-400 border-red-500/30',
};

type FilterTab = 'all' | 'good' | 'warning' | 'poor';

export default function PostureRecordsTable({ records }: { records: PostureRecord[] }) {
  const [filter, setFilter] = useState<FilterTab>('all');

  const filtered = filter === 'all' ? records : records.filter((r) => r.status === filter);

  const tabs: { key: FilterTab; label: string }[] = [
    { key: 'all', label: 'All Records' },
    { key: 'good', label: 'Good Posture' },
    { key: 'warning', label: 'Warnings' },
    { key: 'poor', label: 'Poor Posture' },
  ];

  return (
    <div className="card">
      <div className="flex gap-2 mb-4 flex-wrap">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filter === tab.key
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200 border border-transparent'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-slate-400 border-b border-posture-border">
              <th className="text-left py-2 px-3">Timestamp</th>
              <th className="text-left py-2 px-3">Status</th>
              <th className="text-right py-2 px-3">Angle</th>
              <th className="text-right py-2 px-3">Duration</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={4} className="text-center py-8 text-slate-500">
                  No records found
                </td>
              </tr>
            ) : (
              filtered.slice(0, 20).map((record) => (
                <tr key={record.id} className="border-b border-posture-border/50 hover:bg-posture-dark/50">
                  <td className="py-2 px-3 text-slate-300">
                    {new Date(record.timestamp).toLocaleString()}
                  </td>
                  <td className="py-2 px-3">
                    <span className={`inline-block px-2 py-0.5 rounded text-xs border ${STATUS_COLORS[record.status] || ''}`}>
                      {record.status}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-right text-slate-300">{record.angle}°</td>
                  <td className="py-2 px-3 text-right text-slate-400">
                    {record.duration ? `${record.duration}s` : '—'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
