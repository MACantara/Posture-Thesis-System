import { Bluetooth, Wifi } from 'lucide-react';

export default function WirelessPanel() {
  return (
    <div className="card">
      <h3 className="text-sm text-slate-400 mb-4">Wireless Connections</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="flex items-center gap-3 p-3 bg-posture-dark rounded-lg">
          <Bluetooth className="w-6 h-6 text-cyan-400" />
          <div>
            <div className="text-sm text-white font-medium">Bluetooth</div>
            <div className="text-xs text-slate-400">Connected · BLE 5.0</div>
          </div>
          <span className="ml-auto text-xs text-emerald-400">Active</span>
        </div>
        <div className="flex items-center gap-3 p-3 bg-posture-dark rounded-lg">
          <Wifi className="w-6 h-6 text-cyan-400" />
          <div>
            <div className="text-sm text-white font-medium">WiFi</div>
            <div className="text-xs text-slate-400">Connected · 2.4 GHz</div>
          </div>
          <span className="ml-auto text-xs text-emerald-400">Active</span>
        </div>
      </div>
    </div>
  );
}
