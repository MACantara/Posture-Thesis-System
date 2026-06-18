import client from './client';

export interface PostureRecord {
  id: number;
  user_id: number;
  session_id: number | null;
  timestamp: string;
  status: string;
  angle: number;
  duration: number | null;
  notes: string | null;
}

export interface PostureStats {
  total_sessions: number;
  good_posture_count: number;
  average_angle: number;
  improvement_rate: number;
}

export async function getPostureRecords(
  status?: string,
  limit?: number,
  offset?: number
): Promise<PostureRecord[]> {
  const params: Record<string, number | string> = {};
  if (status) params.status = status;
  if (limit) params.limit = limit;
  if (offset) params.offset = offset;
  const response = await client.get('/api/posture/records', { params });
  return response.data;
}

export async function getPostureStats(): Promise<PostureStats> {
  const response = await client.get('/api/posture/stats');
  return response.data;
}
