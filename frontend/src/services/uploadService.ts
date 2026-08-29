import { apiClient } from './apiClient';

export const uploadService = {
  async uploadDocument(file: File, category: string, patientId?: string): Promise<any> {
    return apiClient.uploadDocument<any>('/api/v1/upload/document', file, category, patientId);
  },

  async uploadImage(file: File, patientId?: string): Promise<any> {
    return apiClient.uploadDocument<any>('/api/v1/upload/image', file, 'Imaging/Scan', patientId);
  },

  async uploadReport(file: File, patientId?: string): Promise<any> {
    return apiClient.uploadDocument<any>('/api/v1/upload/report', file, 'Medical Report', patientId);
  },

  async uploadPrescription(file: File, patientId?: string): Promise<any> {
    return apiClient.uploadDocument<any>('/api/v1/upload/prescription', file, 'Prescription', patientId);
  }
};
