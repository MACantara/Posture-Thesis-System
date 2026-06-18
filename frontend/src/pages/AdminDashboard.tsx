import { useState, useEffect } from 'react';
import { LogOut, Shield } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getAllUsers } from '../api/users';
import type { UserWithStats } from '../api/users';
import AdminStatRow from '../components/admin/AdminStatRow';
import UserTable from '../components/admin/UserTable';
import LocationMap from '../components/admin/LocationMap';

export default function AdminDashboard() {
  const { user, logout } = useAuth();
  const [users, setUsers] = useState<UserWithStats[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchUsers() {
      try {
        const u = await getAllUsers();
        setUsers(u);
      } catch (err) {
        console.error('Failed to fetch users:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchUsers();
  }, []);

  const totalUsers = users.length;
  const activeSessions = 0;
  const avgGoodRate = 0;
  const totalRecords = 0;

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <Shield className="w-6 h-6 text-cyan-400" />
          <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-slate-300">{user?.username}</span>
          <button
            onClick={logout}
            className="flex items-center gap-2 text-slate-400 hover:text-red-400 transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span>Logout</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="card text-center py-12">
          <div className="text-slate-400">Loading admin data...</div>
        </div>
      ) : (
        <div className="space-y-6">
          <AdminStatRow
            totalUsers={totalUsers}
            activeSessions={activeSessions}
            avgGoodRate={avgGoodRate}
            totalRecords={totalRecords}
          />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <UserTable
                users={users}
                searchQuery={searchQuery}
                onSearchChange={setSearchQuery}
              />
            </div>
            <LocationMap users={users} />
          </div>
        </div>
      )}
    </div>
  );
}
