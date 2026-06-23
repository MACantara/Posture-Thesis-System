import client from './client';

export interface SensorStatus {
  name: string;
  online: boolean;
  battery: number;
  signal: number;
  temperature: number;
  ping: number;
}

export interface BluetoothAdapterStatus {
  name: string;
  online: boolean;
  address: string | null;
  up: boolean;
  connected_devices: number;
}

export async function getSensorStatus(): Promise<SensorStatus[]> {
  const response = await client.get('/api/sensors/status');
  return response.data;
}

export async function getBluetoothStatus(): Promise<BluetoothAdapterStatus> {
  const response = await client.get('/api/sensors/bluetooth');
  return response.data;
}

export interface HardwareDetection {
  i2c: { name: string; address: string; bus: number; interface: string }[];
  gpio: { name: string; pin: number; interface: string; type: string }[];
  ble: { name: string; address: string | null; interface: string }[];
}

export async function getHardwareDetection(): Promise<HardwareDetection> {
  const response = await client.get('/api/sensors/detect');
  return response.data;
}
