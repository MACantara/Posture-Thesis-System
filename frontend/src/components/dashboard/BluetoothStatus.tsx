import { useState, useEffect } from 'react';
import { Bluetooth, BluetoothConnected } from 'lucide-react';
import { getConnectionStatus } from '../../api/sensors';
import type { ConnectionStatus } from '../../api/sensors';

export default function BluetoothStatus() {
  const [status, setStatus] = useState<ConnectionStatus | null>(null);

  useEffect(() => {
    let mounted = true;

    async function check() {
      try {
        const s = await getConnectionStatus();
        if (mounted) setStatus(s);
      } catch {
        if (mounted) setStatus(null);
      }
    }

    check();
    const interval = setInterval(check, 5000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const connected = status?.connected ?? false;

  return (
    <div
      className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium ${
        connected
          ? 'bg-emerald-500/20 text-emerald-400'
          : 'bg-red-500/20 text-red-400'
      }`}
    >
      {connected ? (
        <BluetoothConnected className="w-4 h-4" />
      ) : (
        <Bluetooth className="w-4 h-4" />
      )}
      <span>{connected ? 'Bluetooth Connected' : 'Bluetooth Disconnected'}</span>
    </div>
  );
}
