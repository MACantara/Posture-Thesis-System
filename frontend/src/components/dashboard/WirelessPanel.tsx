import { useState, useEffect } from 'react';
import { Bluetooth, Battery, Signal, Thermometer, Activity, Cpu } from 'lucide-react';
import type { SensorStatus, BluetoothAdapterStatus } from '../../api/sensors';
import { getBluetoothStatus } from '../../api/sensors';

export default function WirelessPanel({ sensors }: { sensors: SensorStatus[] }) {
  const primary = sensors.find((s) => s.online) ?? sensors[0];
  const [btAdapter, setBtAdapter] = useState<BluetoothAdapterStatus | null>(null);

  useEffect(() => {
    getBluetoothStatus()
      .then(setBtAdapter)
      .catch(() => setBtAdapter(null));
  }, []);

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

      {/* Pi Built-in Bluetooth Adapter Status */}
      <div className="flex items-center gap-3 p-4 bg-posture-dark rounded-lg mb-3">
        <Cpu className={`w-6 h-6 ${btAdapter?.online ? 'text-cyan-400' : 'text-slate-600'}`} />
        <div className="flex-1">
          <div className="text-sm text-white font-medium">Raspberry Pi Built-in Bluetooth</div>
          <div className="text-xs text-slate-400">
            {btAdapter?.online ? 'Adapter UP' : 'Adapter DOWN'} · Bluetooth 4.2/BLE
            {btAdapter?.address ? ` · ${btAdapter.address}` : ''}
          </div>
        </div>
        <span className={`text-xs ${btAdapter?.online ? 'text-emerald-400' : 'text-red-400'}`}>
          {btAdapter?.online ? 'Active' : 'Inactive'}
        </span>
      </div>

      {/* Sensor Connection */}
      <div className="flex items-center gap-3 p-4 bg-posture-dark rounded-lg">
        <Bluetooth className={`w-8 h-8 ${primary.online ? 'text-cyan-400' : 'text-slate-600'}`} />
        <div className="flex-1">
          <div className="text-sm text-white font-medium">Bluetooth Low Energy (BLE)</div>
          <div className="text-xs text-slate-400">
            {primary.online ? 'Connected' : 'Disconnected'} · BLE 4.2 · {primary.name}
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

      {btAdapter && (
        <div className="mt-4 flex items-center gap-2 text-xs text-slate-400">
          <Bluetooth className="w-3.5 h-3.5" />
          <span>
            {btAdapter.connected_devices} device{btAdapter.connected_devices !== 1 ? 's' : ''} connected to Pi Bluetooth
          </span>
        </div>
      )}
    </div>
  );
}
