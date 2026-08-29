import { apiClient } from './apiClient';
import type { AppNotification } from '../types';

export const notificationService = {
  async getNotifications(): Promise<AppNotification[]> {
    return apiClient.get<AppNotification[]>('/api/v1/notifications');
  },

  async markAsRead(id: string): Promise<AppNotification> {
    return apiClient.put<AppNotification>(`/api/v1/notifications/${id}/read`, {});
  }
};
