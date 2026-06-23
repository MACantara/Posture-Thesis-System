import client from './client';

export interface SensorStatus {
  name: string;
  online: boolean;
  battery: number;
  signal: number;
  temperature: number;
  ping: number;
}

export interface ConnectionStatus {
  connected: boolean;
  name: string;
  type: string;
}

export async function getSensorStatus(): Promise<SensorStatus[]> {
  const response = await client.get('/api/sensors/status');
  return response.data;
}

export async function getConnectionStatus(): Promise<ConnectionStatus> {
  const response = await client.get('/api/sensors/connection');
  return response.data;
}
