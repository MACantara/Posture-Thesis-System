import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import type { ReactNode } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import UserLogin from './pages/UserLogin';
import AdminLogin from './pages/AdminLogin';
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';

function DebugHostInfo() {
  if (typeof window === 'undefined') return null;
  const apiBase = import.meta.env.VITE_API_URL ||
    `${window.location.protocol}//${window.location.hostname}:8000`;
  const wsBase = import.meta.env.VITE_WS_URL ||
    `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.hostname}:8000`;
  return (
    <div className="fixed bottom-2 left-2 z-50 text-[10px] text-slate-500 bg-posture-dark/80 px-2 py-1 rounded font-mono pointer-events-none">
      <div>Host: {window.location.host}</div>
      <div>API: {apiBase}</div>
      <div>WS: {wsBase}</div>
    </div>
  );
}

function ProtectedRoute({ children, role }: { children: ReactNode; role: string }) {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-slate-400">Loading...</div>
      </div>
    );
  }
  if (!user) return <Navigate to="/login" />;
  if (user.role !== role) {
    return <Navigate to={user.role === 'admin' ? '/admin' : '/dashboard'} />;
  }
  return <>{children}</>;
}

function AppRoutes() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-slate-400">Loading...</div>
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <UserLogin />} />
      <Route path="/admin/login" element={user ? <Navigate to="/admin" /> : <AdminLogin />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute role="user">
            <UserDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <ProtectedRoute role="admin">
            <AdminDashboard />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
        <DebugHostInfo />
      </AuthProvider>
    </BrowserRouter>
  );
}
