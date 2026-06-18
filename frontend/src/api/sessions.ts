import client from './client';

export interface Session {
  id: number;
  user_id: number;
  start_time: string;
  end_time: string | null;
  good_count: number;
  warning_count: number;
  poor_count: number;
  avg_angle: number | null;
}

export async function getSessions(): Promise<Session[]> {
  const response = await client.get('/api/sessions');
  return response.data;
}

export async function startSession(): Promise<{ session_id: number }> {
  const response = await client.post('/api/sessions/start');
  return response.data;
}

export async function endSession(
  sessionId: number,
  goodCount?: number,
  warningCount?: number,
  poorCount?: number,
  avgAngle?: number
): Promise<void> {
  await client.post(`/api/sessions/${sessionId}/end`, {
    good_count: goodCount,
    warning_count: warningCount,
    poor_count: poorCount,
    avg_angle: avgAngle,
  });
}
