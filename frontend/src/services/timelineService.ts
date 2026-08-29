import { apiClient } from './apiClient';
import type { TimelineEvent } from '../types';

const INITIAL_EVENTS: TimelineEvent[] = [
  {
    id: 'ev_1',
    patient_id: 'demo_patient_id',
    type: 'symptom',
    title: 'Respiratory Symptoms Reported',
    description: 'Dry cough + chest tightness on exertion logged.',
    details: 'Onset noted 3 days prior. Cough presents as non-productive and increases in frequency during late evening hours.',
    timestamp: new Date(Date.now() - 86400000 * 4).toISOString(),
  },
  {
    id: 'ev_2',
    patient_id: 'demo_patient_id',
    type: 'document',
    title: 'CBC Blood Report Uploaded',
    description: 'cbc_blood_report.pdf submitted to library.',
    details: 'Parsed via Docs Agent. Basic metabolic factors and white blood cell levels logged within standard reference metrics.',
    timestamp: new Date(Date.now() - 86400000 * 3).toISOString(),
  },
  {
    id: 'ev_3',
    patient_id: 'demo_patient_id',
    type: 'test',
    title: 'Chest X-Ray Diagnostic PA View',
    description: 'Hyperinflation markings and lower right lobe density.',
    details: 'Parsed via Vision Agent. Highlighting minor right lower lobe density. Suggestions suggest pulmonology correlation.',
    timestamp: new Date(Date.now() - 86400000 * 2).toISOString(),
  },
  {
    id: 'ev_4',
    patient_id: 'demo_patient_id',
    type: 'analysis',
    title: 'AI Analysis Referral Advisory Generated',
    description: 'CarePath AI suggested pulmonologist specialist referral.',
    details: 'Match confidence rated at 94% based on persistent dry symptoms and consolidation findings in lower lung field scan.',
    timestamp: new Date(Date.now() - 86400000 * 1.5).toISOString(),
  },
  {
    id: 'ev_5',
    patient_id: 'demo_patient_id',
    type: 'medication',
    title: 'Therapy Initialized: Albuterol Sulfate HFA',
    description: 'GP prescribed active short-acting beta-agonist inhaler.',
    details: 'Dose: 90mcg (2 puffs inhaled every 4-6 hours as needed). Monitor efficacy over 14-day cycle.',
    timestamp: new Date(Date.now() - 86400000 * 1.2).toISOString(),
  },
  {
    id: 'ev_6',
    patient_id: 'demo_patient_id',
    type: 'doctor',
    title: 'Doctor Bridge Brief Approved by Practitioner',
    description: 'Referral confirmed by Dr. Robert Chen, MD.',
    details: 'Attending physician signed off clinical override. Confirmed pulmonologist consult request for full lung spirometry test.',
    timestamp: new Date(Date.now() - 86400000 * 0.5).toISOString(),
  },
  {
    id: 'ev_7',
    patient_id: 'demo_patient_id',
    type: 'careplan',
    title: 'Pulmonary Care Plan Goals Activated',
    description: 'Action benchmarks generated for Pulmonology consultation.',
    details: 'Include printing consultation brief sheets, completing day-7 recovery check-in logs, and keeping therapeutic inhaler logs.',
    timestamp: new Date(Date.now() - 86400000 * 0.2).toISOString(),
  },
  {
    id: 'ev_8',
    patient_id: 'demo_patient_id',
    type: 'followup',
    title: 'Daily Follow-up Check-in Due',
    description: 'Day-4 recovery progress status report pending.',
    details: 'Assess cough and dyspnea trends relative to inhaler compliance rates.',
    timestamp: new Date().toISOString(),
  }
];

export const timelineService = {
  async getTimeline(patientId: string): Promise<TimelineEvent[]> {
    if (patientId === 'demo_patient_id') {
      const stored = localStorage.getItem('carepath_timeline_events');
      if (!stored) {
        localStorage.setItem('carepath_timeline_events', JSON.stringify(INITIAL_EVENTS));
        return INITIAL_EVENTS;
      }
      return JSON.parse(stored);
    }
    return apiClient.get<TimelineEvent[]>(`/api/v1/timeline/${patientId}`);
  },

  async addTimelineEvent(event: Omit<TimelineEvent, 'id'>): Promise<TimelineEvent> {
    if (event.patient_id === 'demo_patient_id') {
      const stored = localStorage.getItem('carepath_timeline_events');
      const events: TimelineEvent[] = stored ? JSON.parse(stored) : INITIAL_EVENTS;
      const newEvent: TimelineEvent = {
        id: `ev_custom_${Date.now()}`,
        ...event
      };
      const updated = [newEvent, ...events];
      localStorage.setItem('carepath_timeline_events', JSON.stringify(updated));
      window.dispatchEvent(new Event('timeline_updated'));
      return newEvent;
    }
    const result = await apiClient.post<TimelineEvent>('/api/v1/timeline/event', event);
    window.dispatchEvent(new Event('timeline_updated'));
    return result;
  }
};
