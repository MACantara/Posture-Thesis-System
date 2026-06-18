import client from './client';

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: string;
  username: string;
}

export interface UserOut {
  id: number;
  username: string;
  role: string;
  location: string | null;
  created_at: string;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await client.post('/api/auth/login', { username, password });
  return response.data;
}

export async function getCurrentUser(): Promise<UserOut> {
  const response = await client.get('/api/auth/me');
  return response.data;
}
