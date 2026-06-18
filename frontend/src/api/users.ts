import client from './client';

export interface UserWithStats {
  id: number;
  username: string;
  role: string;
  location: string | null;
  created_at: string;
}

export async function getAllUsers(): Promise<UserWithStats[]> {
  const response = await client.get('/api/users');
  return response.data;
}

export async function getUserById(id: number): Promise<UserWithStats> {
  const response = await client.get(`/api/users/${id}`);
  return response.data;
}

export async function updateUser(id: number, fields: Record<string, unknown>): Promise<UserWithStats> {
  const response = await client.patch(`/api/users/${id}`, fields);
  return response.data;
}
