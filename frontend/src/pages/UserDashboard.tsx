import { useState, useEffect } from 'react';
import { LogOut, User, Activity, Clock, TrendingUp, Gauge } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getPostureRecords, getPostureStats } from '../api/posture';
import { getSensorStatus } from '../api/sensors';
import type { PostureRecord, PostureStats } from '../api/posture';
import type { SensorStatus } from '../api/sensors';
import TabNav from '../components/shared/TabNav';
import StatCard from '../components/dashboard/StatCard';
import PostureDonutChart from '../components/dashboard/PostureDonutChart';
import PostureRecordsTable from '../components/dashboard/PostureRecordsTable';
import Recommendations from '../components/dashboard/Recommendations';
import SensorCards from '../components/dashboard/SensorCards';
import WirelessPanel from '../components/dashboard/WirelessPanel';
import PostureSilhouette from '../components/dashboard/PostureSilhouette';
import JointAngleBars from '../components/dashboard/JointAngleBars';
import SessionStats from '../components/dashboard/SessionStats';

type Tab = 'home' | 'connectivity' | 'posture';

export default function UserDashboard() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<Tab>('home');
  const [records, setRecords] = useState<PostureRecord[]>([]);
  const [stats, setStats] = useState<PostureStats | null>(null);
  const [sensors, setSensors] = useState<SensorStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [r, s, sens] = await Promise.all([
          getPostureRecords('all', 50, 0),
          getPostureStats(),
          getSensorStatus(),
        ]);
        setRecords(r);
        setStats(s);
        setSensors(sens);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const tabs = [
    { key: 'home', label: 'Home' },
    { key: 'connectivity', label: 'Connectivity' },
    { key: 'posture', label: 'Posture Status' },
  ];

  const goodCount = records.filter((r) => r.status === 'good').length;
  const warningCount = records.filter((r) => r.status === 'warning').length;
  const poorCount = records.filter((r) => r.status === 'poor').length;

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <Activity className="w-6 h-6 text-cyan-400" />
          <h1 className="text-2xl font-bold text-white">Posture Dashboard</h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-slate-300">
            <User className="w-5 h-5" />
            <span>{user?.username}</span>
          </div>
          <button
            onClick={logout}
            className="flex items-center gap-2 text-slate-400 hover:text-red-400 transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span>Logout</span>
          </button>
        </div>
      </div>

      <TabNav tabs={tabs} activeTab={activeTab} onTabChange={(t) => setActiveTab(t as Tab)} />

      {loading ? (
        <div className="card text-center py-12">
          <div className="text-slate-400">Loading dashboard data...</div>
        </div>
      ) : (
        <>
          {activeTab === 'home' && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                  label="Total Sessions"
                  value={stats?.total_sessions ?? 0}
                  icon={<Clock className="w-4 h-4" />}
                />
                <StatCard
                  label="Good Posture"
                  value={stats?.good_posture_count ?? 0}
                  icon={<Activity className="w-4 h-4" />}
                  accent="text-emerald-400"
                />
                <StatCard
                  label="Avg Angle"
                  value={`${stats?.average_angle ?? 0}°`}
                  icon={<Gauge className="w-4 h-4" />}
                  accent="text-amber-400"
                />
                <StatCard
                  label="Improvement"
                  value={`${stats?.improvement_rate ?? 0}%`}
                  icon={<TrendingUp className="w-4 h-4" />}
                  accent="text-cyan-400"
                />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <PostureDonutChart good={goodCount} warning={warningCount} poor={poorCount} />
                <Recommendations poorCount={poorCount} warningCount={warningCount} />
              </div>

              <PostureRecordsTable records={records} />
            </div>
          )}

          {activeTab === 'connectivity' && (
            <div className="space-y-6">
              <SensorCards sensors={sensors} />
              <WirelessPanel sensors={sensors} />
            </div>
          )}

          {activeTab === 'posture' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <PostureSilhouette status="idle" />
                <JointAngleBars angle={0} status="idle" />
                <SessionStats duration={0} goodCount={0} warningCount={0} poorCount={0} />
              </div>
              <div className="card">
                <p className="text-slate-400 text-sm text-center py-8">
                  Connect to a sensor session to see real-time posture data.
                  This will be activated in Phase 6 with WebSocket integration.
                </p>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
