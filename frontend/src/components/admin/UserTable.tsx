import { Search } from 'lucide-react';
import type { UserWithStats } from '../../api/users';

interface UserTableProps {
  users: UserWithStats[];
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

const AVATAR_COLORS = [
  'bg-cyan-500', 'bg-emerald-500', 'bg-amber-500', 'bg-purple-500',
  'bg-pink-500', 'bg-blue-500', 'bg-red-500', 'bg-indigo-500',
];

function getInitials(username: string): string {
  return username.slice(0, 2).toUpperCase();
}

function getAvatarColor(username: string): string {
  const index = username.charCodeAt(0) % AVATAR_COLORS.length;
  return AVATAR_COLORS[index];
}

export default function UserTable({ users, searchQuery, onSearchChange }: UserTableProps) {
  const filtered = users.filter(
    (u) =>
      u.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (u.location?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false)
  );

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-4">
        <Search className="w-4 h-4 text-slate-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search users by name or location..."
          className="flex-1 bg-transparent text-slate-200 placeholder-slate-500 focus:outline-none text-sm"
        />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-slate-400 border-b border-posture-border">
              <th className="text-left py-2 px-3">User</th>
              <th className="text-left py-2 px-3">Location</th>
              <th className="text-left py-2 px-3">Role</th>
              <th className="text-left py-2 px-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={4} className="text-center py-8 text-slate-500">
                  No users found
                </td>
              </tr>
            ) : (
              filtered.map((user) => (
                <tr key={user.id} className="border-b border-posture-border/50 hover:bg-posture-dark/50 cursor-pointer">
                  <td className="py-3 px-3">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-8 h-8 rounded-full ${getAvatarColor(user.username)} flex items-center justify-center text-xs font-bold text-white`}
                      >
                        {getInitials(user.username)}
                      </div>
                      <span className="text-slate-200">{user.username}</span>
                    </div>
                  </td>
                  <td className="py-3 px-3 text-slate-400">{user.location || '—'}</td>
                  <td className="py-3 px-3">
                    <span
                      className={`px-2 py-0.5 rounded text-xs ${
                        user.role === 'admin'
                          ? 'bg-cyan-500/20 text-cyan-400'
                          : 'bg-slate-500/20 text-slate-400'
                      }`}
                    >
                      {user.role}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <span className="inline-flex items-center gap-1.5 text-xs text-emerald-400">
                      <span className="w-2 h-2 rounded-full bg-emerald-500" />
                      Active
                    </span>
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
