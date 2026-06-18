import { MapPin } from 'lucide-react';
import type { UserWithStats } from '../../api/users';

interface LocationMapProps {
  users: UserWithStats[];
}

export default function LocationMap({ users }: LocationMapProps) {
  const locationCounts = users.reduce((acc, user) => {
    const loc = user.location || 'Unknown';
    acc[loc] = (acc[loc] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const locations = Object.entries(locationCounts).sort((a, b) => b[1] - a[1]);

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <MapPin className="w-5 h-5 text-cyan-400" />
        <h3 className="text-sm text-slate-400">User Distribution by Location</h3>
      </div>
      <div className="space-y-3">
        {locations.map(([location, count]) => (
          <div key={location} className="flex items-center gap-3">
            <div className="relative flex items-center justify-center">
              <span className="w-3 h-3 rounded-full bg-cyan-500 animate-pulse" />
              <span className="absolute w-6 h-6 rounded-full bg-cyan-500/20" />
            </div>
            <span className="text-sm text-slate-300 flex-1">{location}</span>
            <span className="text-sm font-bold text-white">{count}</span>
            <span className="text-xs text-slate-500">users</span>
          </div>
        ))}
      </div>
    </div>
  );
}
