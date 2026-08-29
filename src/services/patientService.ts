import { apiClient } from './apiClient';
import type { Patient } from '../types';

export const patientService = {
  async createPatient(data: Omit<Patient, 'id' | 'user_id'>): Promise<Patient> {
    return apiClient.post<Patient>('/api/v1/patients', data);
  },

  async getPatient(id: string): Promise<Patient> {
    return apiClient.get<Patient>(`/api/v1/patients/${id}`);
  },

  async updatePatient(id: string, data: Partial<Patient>): Promise<Patient> {
    return apiClient.put<Patient>(`/api/v1/patients/${id}`, data);
  },

  async deletePatient(id: string): Promise<void> {
    return apiClient.delete<void>(`/api/v1/patients/${id}`);
  },

  async getPatients(): Promise<Patient[]> {
    return apiClient.get<Patient[]>('/api/v1/patients');
  }
};
