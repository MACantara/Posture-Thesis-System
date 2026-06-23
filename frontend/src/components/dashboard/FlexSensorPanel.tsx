import { useState, useEffect } from 'react';
import { Activity, Zap, Ruler, Gauge } from 'lucide-react';
import { getFlexSensorData } from '../../api/sensors';
import type { FlexSensorData } from '../../api/sensors';

export default function FlexSensorPanel() {
  const [data, setData] = useState<FlexSensorData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = () => {
      getFlexSensorData()
        .then(setData)
        .catch(() => setData(null))
        .finally(() => setLoading(false));
    };
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm text-slate-400">Flex Sensor 4.5"</h3>
        </div>
        <div className="text-sm text-slate-500">Reading sensor...</div>
      </div>
    );
  }

  if (!data || !data.online) {
    return (
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="w-5 h-5 text-slate-600" />
          <h3 className="text-sm text-slate-400">Flex Sensor 4.5"</h3>
        </div>
        <div className="flex items-center gap-3 p-4 bg-posture-dark rounded-lg">
          <div className="flex-1">
            <div className="text-sm text-white font-medium">SparkFun SEN-08606</div>
            <div className="text-xs text-slate-400">
              {data?.error || 'Sensor not connected'}
            </div>
          </div>
          <span className="text-xs text-red-400">Offline</span>
        </div>
      </div>
    );
  }

  const bendPercent = Math.min((data.bend_angle / 90) * 100, 100);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm text-slate-400">Flex Sensor 4.5"</h3>
        </div>
        <span className="text-xs text-emerald-400">Online</span>
      </div>

      {/* Bend angle gauge */}
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-2">
          <Gauge className="w-4 h-4 text-cyan-400" />
          <span className="text-xs text-slate-400">Bend Angle</span>
        </div>
        <div className="flex items-end gap-2">
          <span className="text-3xl font-bold text-white">{data.bend_angle.toFixed(1)}</span>
          <span className="text-sm text-slate-400 mb-1">degrees</span>
        </div>
        <div className="mt-2 h-2 bg-posture-dark rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-cyan-500 to-cyan-300 rounded-full transition-all"
            style={{ width: `${bendPercent}%` }}
          />
        </div>
      </div>

      {/* Raw data grid */}
      <div className="grid grid-cols-3 gap-3">
        <div className="flex items-center gap-2 p-3 bg-posture-dark rounded-lg">
          <Zap className="w-4 h-4 text-cyan-400" />
          <div>
            <div className="text-xs text-slate-400">Voltage</div>
            <div className="text-sm text-white font-medium">{data.voltage.toFixed(3)}V</div>
          </div>
        </div>
        <div className="flex items-center gap-2 p-3 bg-posture-dark rounded-lg">
          <Ruler className="w-4 h-4 text-cyan-400" />
          <div>
            <div className="text-xs text-slate-400">Resistance</div>
            <div className="text-sm text-white font-medium">
              {data.resistance > 1000
                ? `${(data.resistance / 1000).toFixed(1)}kΩ`
                : `${data.resistance.toFixed(0)}Ω`}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2 p-3 bg-posture-dark rounded-lg">
          <Activity className="w-4 h-4 text-cyan-400" />
          <div>
            <div className="text-xs text-slate-400">Raw ADC</div>
            <div className="text-sm text-white font-medium">{data.raw_adc}</div>
          </div>
        </div>
      </div>

      <div className="mt-4 text-xs text-slate-500">
        SparkFun SEN-08606{data.adc_type ? ` via ${data.adc_type.toUpperCase()}` : ''} · Updates every 2s
      </div>
    </div>
  );
}
