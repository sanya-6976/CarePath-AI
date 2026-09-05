import { apiClient } from './apiClient';

export interface CompanionMessage {
  role: 'user' | 'assistant';
  content: string;
  language?: string;
}

export const companionService = {
  chat: (payload: {
    message: string;
    conversation_id?: string;
    language: 'en' | 'hi' | 'hl';
    page_context?: string;
    use_carepath_history: boolean;
    simple_medical_terms?: boolean;
  }) =>
    apiClient.post<{
      conversation_id: string;
      answer: string;
      language: string;
      used_carepath_history: boolean;
      intent?: string;
      clinical_handoff?: boolean;
    }>('/api/v1/companion/chat', payload),

  savePreferences: (payload: {
    language: 'en' | 'hi' | 'hl';
    voice_responses: boolean;
    use_carepath_history: boolean;
    simple_medical_terms: boolean;
  }) =>
    apiClient.put('/api/v1/companion/preferences', payload),
};
