import { Bluetooth, Battery, Signal, Thermometer, Activity } from 'lucide-react';
import type { SensorStatus } from '../../api/sensors';

export default function WirelessPanel({ sensors }: { sensors: SensorStatus[] }) {
  const primary = sensors.find((s) => s.online) ?? sensors[0];

  if (!primary) {
    return (
      <div className="card">
        <h3 className="text-sm text-slate-400 mb-4">Bluetooth Connection</h3>
        <p className="text-sm text-slate-500 text-center py-6">No sensors connected.</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="text-sm text-slate-400 mb-4">Bluetooth Connection</h3>
      <div className="flex items-center gap-3 p-4 bg-posture-dark rounded-lg">
        <Bluetooth className={`w-8 h-8 ${primary.online ? 'text-cyan-400' : 'text-slate-600'}`} />
        <div className="flex-1">
          <div className="text-sm text-white font-medium">Bluetooth Low Energy (BLE)</div>
          <div className="text-xs text-slate-400">
            {primary.online ? 'Connected' : 'Disconnected'} · BLE 5.0 · {primary.name}
          </div>
        </div>
        <span className={`text-xs ${primary.online ? 'text-emerald-400' : 'text-red-400'}`}>
          {primary.online ? 'Active' : 'Inactive'}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-4 mt-4">
        <div className="flex items-center gap-2 p-3 bg-posture-dark rounded-lg">
          <Signal className="w-5 h-5 text-cyan-400" />
          <div>
            <div className="text-xs text-slate-400">Signal Strength</div>
            <div className="text-sm text-white font-medium">{primary.signal}%</div>
          </div>
        </div>
        <div className="flex items-center gap-2 p-3 bg-posture-dark rounded-lg">
          <Battery className="w-5 h-5 text-cyan-400" />
          <div>
            <div className="text-xs text-slate-400">Battery</div>
            <div className="text-sm text-white font-medium">{primary.battery}%</div>
          </div>
        </div>
        <div className="flex items-center gap-2 p-3 bg-posture-dark rounded-lg">
          <Thermometer className="w-5 h-5 text-cyan-400" />
          <div>
            <div className="text-xs text-slate-400">Temperature</div>
            <div className="text-sm text-white font-medium">{primary.temperature}°C</div>
          </div>
        </div>
        <div className="flex items-center gap-2 p-3 bg-posture-dark rounded-lg">
          <Activity className="w-5 h-5 text-cyan-400" />
          <div>
            <div className="text-xs text-slate-400">Ping</div>
            <div className="text-sm text-white font-medium">{primary.ping}ms</div>
          </div>
        </div>
      </div>
    </div>
  );
}
