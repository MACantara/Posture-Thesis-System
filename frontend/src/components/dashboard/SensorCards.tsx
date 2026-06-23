import { Battery, Bluetooth, Thermometer, Activity } from 'lucide-react';
import type { SensorStatus } from '../../api/sensors';

export default function SensorCards({ sensors }: { sensors: SensorStatus[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {sensors.map((sensor) => (
        <div key={sensor.name} className="card">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-white">{sensor.name}</span>
            <span
              className={`px-2 py-0.5 rounded text-xs ${
                sensor.online
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : 'bg-red-500/20 text-red-400'
              }`}
            >
              {sensor.online ? 'Online' : 'Offline'}
            </span>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Battery className="w-4 h-4 text-slate-400" />
              <div className="flex-1">
                <div className="h-1.5 bg-posture-dark rounded-full overflow-hidden">
                  <div
                    className="h-full bg-cyan-500 rounded-full transition-all"
                    style={{ width: `${sensor.battery}%` }}
                  />
                </div>
              </div>
              <span className="text-xs text-slate-400 w-8 text-right">{sensor.battery}%</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Bluetooth className="w-4 h-4 text-slate-400" />
              <span className="text-slate-300">Signal: {sensor.signal}%</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Thermometer className="w-4 h-4 text-slate-400" />
              <span className="text-slate-300">{sensor.temperature}°C</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Activity className="w-4 h-4 text-slate-400" />
              <span className="text-slate-300">Ping: {sensor.ping}ms</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
