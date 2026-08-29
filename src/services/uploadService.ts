import { apiClient } from './apiClient';
import type { MedicalRecord } from '../types';

export const uploadService = {
  async uploadImage(file: File): Promise<MedicalRecord> {
    return apiClient.postFile<MedicalRecord>('/api/v1/upload/image', file);
  },

  async uploadReport(file: File): Promise<MedicalRecord> {
    return apiClient.postFile<MedicalRecord>('/api/v1/upload/report', file);
  },

  async uploadPrescription(file: File): Promise<MedicalRecord> {
    return apiClient.postFile<MedicalRecord>('/api/v1/upload/prescription', file);
  }
};
