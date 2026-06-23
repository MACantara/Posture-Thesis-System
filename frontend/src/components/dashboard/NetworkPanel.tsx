import { useState, useEffect } from 'react';
import { Network, RefreshCw, Cpu, Globe, Wifi } from 'lucide-react';
import { getNetworkDevices } from '../../api/sensors';
import type { NetworkScanResult, NetworkDevice } from '../../api/sensors';

export default function NetworkPanel() {
  const [data, setData] = useState<NetworkScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchNetwork = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await getNetworkDevices();
      setData(result);
    } catch (err: any) {
      setError(err?.message || 'Failed to scan network');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNetwork();
  }, []);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Network className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm text-slate-400">Network Devices</h3>
        </div>
        <button
          onClick={fetchNetwork}
          disabled={loading}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-cyan-400 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Scanning...' : 'Rescan'}
        </button>
      </div>

      {error && (
        <div className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2 mb-4">
          {error}
        </div>
      )}

      {/* Local machine info */}
      {data?.local && (
        <div className="flex items-center gap-3 p-4 bg-posture-dark rounded-lg mb-4">
          <Globe className="w-6 h-6 text-cyan-400" />
          <div className="flex-1">
            <div className="text-sm text-white font-medium">
              {data.local.hostname || 'This Machine'}
            </div>
            <div className="text-xs text-slate-400">
              {data.local.ip_addresses.join(', ') || 'No IP'}
              {data.local.network ? ` · Subnet: ${data.local.network}` : ''}
            </div>
          </div>
          <span className="text-xs text-emerald-400">Host</span>
        </div>
      )}

      {/* Discovered devices */}
      <div className="space-y-2">
        {data?.devices.length === 0 && !loading && (
          <div className="text-sm text-slate-500 text-center py-4">
            No devices found on the network.
          </div>
        )}

        {data?.devices.map((device: NetworkDevice) => (
          <div
            key={device.ip}
            className="flex items-center gap-3 p-3 bg-posture-dark rounded-lg"
          >
            {device.is_raspberry_pi ? (
              <Cpu className="w-5 h-5 text-cyan-400" />
            ) : (
              <Wifi className="w-5 h-5 text-slate-400" />
            )}
            <div className="flex-1">
              <div className="text-sm text-white font-medium">
                {device.hostname || device.ip}
                {device.is_raspberry_pi && (
                  <span className="ml-2 text-xs text-cyan-400">Raspberry Pi</span>
                )}
              </div>
              <div className="text-xs text-slate-400">
                {device.ip}
                {Object.keys(device.ports).length > 0 && (
                  <span className="ml-2">
                    · Ports: {Object.entries(device.ports).map(([label, port]) => `${label}:${port}`).join(', ')}
                  </span>
                )}
              </div>
            </div>
            <span className="text-xs text-emerald-400">Online</span>
          </div>
        ))}
      </div>

      {data && data.devices.length > 0 && (
        <div className="mt-4 text-xs text-slate-500">
          {data.devices.length} device{data.devices.length !== 1 ? 's' : ''} discovered on {data.local.network || 'local network'}
        </div>
      )}
    </div>
  );
}
