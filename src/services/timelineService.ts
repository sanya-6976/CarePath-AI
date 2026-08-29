import { apiClient } from './apiClient';
import type { TimelineEvent } from '../types';

export const timelineService = {
  async getTimeline(patientId: string): Promise<TimelineEvent[]> {
    return apiClient.get<TimelineEvent[]>(`/api/v1/timeline/${patientId}`);
  },

  async addTimelineEvent(event: Omit<TimelineEvent, 'id'>): Promise<TimelineEvent> {
    return apiClient.post<TimelineEvent>('/api/v1/timeline/event', event);
  }
};
