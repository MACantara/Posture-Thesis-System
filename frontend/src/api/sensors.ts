import client from './client';

export interface SensorStatus {
  name: string;
  online: boolean;
  battery: number;
  signal: number;
  temperature: number;
  ping: number;
}

export async function getSensorStatus(): Promise<SensorStatus[]> {
  const response = await client.get('/api/sensors/status');
  return response.data;
}
