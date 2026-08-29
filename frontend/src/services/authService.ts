import { apiClient } from './apiClient';
import type { UserProfile, AuthResponse } from '../types';

export const authService = {
  async register(data: any): Promise<any> {
    return apiClient.post<any>('/api/v1/auth/register', data);
  },

  async login(credentials: any): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>('/api/v1/auth/login', credentials);
  },

  async logout(): Promise<void> {
    return apiClient.post<void>('/api/v1/auth/logout', {});
  },

  async getProfile(): Promise<UserProfile> {
    return apiClient.get<UserProfile>('/api/v1/auth/profile');
  },

  async refreshToken(): Promise<{ token: string }> {
    return apiClient.post<{ token: string }>('/api/v1/auth/refresh', {});
  }
};
