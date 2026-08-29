import { apiClient } from './apiClient';
import type { FollowUp } from '../types';

export const followupService = {
  async createFollowUp(data: { patient_id: string; check_in_date: string; symptoms_logged?: string }): Promise<FollowUp> {
    return apiClient.post<FollowUp>('/api/v1/followup', data);
  },

  async getFollowUps(patientId: string): Promise<FollowUp[]> {
    return apiClient.get<FollowUp[]>(`/api/v1/followup/${patientId}`);
  },

  async updateFollowUp(id: string, data: Partial<FollowUp>): Promise<FollowUp> {
    return apiClient.put<FollowUp>(`/api/v1/followup/${id}`, data);
  }
};
