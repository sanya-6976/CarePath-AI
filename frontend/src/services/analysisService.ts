import { apiClient } from './apiClient';
import type { AnalysisResult } from '../types';
export const analysisService = {
  async startAnalysis(patientId: string): Promise<AnalysisResult> {
    return apiClient.post<AnalysisResult>('/api/v1/analysis/start', { patient_id: patientId });
  },

  async getAnalysis(analysisId: string): Promise<AnalysisResult> {
    return apiClient.get<AnalysisResult>(`/api/v1/analysis/${analysisId}`);
  },

  async getAnalysisHistory(patientId: string): Promise<AnalysisResult[]> {
    return apiClient.get<AnalysisResult[]>(`/api/v1/analysis/history/${patientId}`);
  }
};
