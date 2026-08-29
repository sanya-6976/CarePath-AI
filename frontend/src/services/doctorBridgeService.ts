export interface DoctorQuestion {
  id: string;
  text: string;
  relevance: string;
  isAsked: boolean;
  isCustom?: boolean;
}

export interface DoctorReview {
  isReviewed: boolean;
  reviewedBy: string;
  reviewedDate: string;
  recommendation: string; // Confirm or Modify
  originalRecommendation: string;
  modifiedSpecialist?: string;
  doctorNote: string;
  doctorRecommendations: string[];
  followUpDate: string;
}

const INITIAL_QUESTIONS: DoctorQuestion[] = [
  {
    id: 'q_1',
    text: 'My dry cough has persisted for over 3 days without improvement. Does this suggest a bacterial trigger or bronchitis?',
    relevance: 'Evaluating symptom duration helps distinguish temporary viral irritation from acute lower respiratory tract triggers.',
    isAsked: false
  },
  {
    id: 'q_2',
    text: 'My chest X-ray reports minor lower lobe consolidation. What does this consolidate indicating for my recovery timeline?',
    relevance: 'Discussing imaging density parameters clarifies if targeted pulmonary care or antibiotics are warranted.',
    isAsked: false
  },
  {
    id: 'q_3',
    text: 'The Albuterol bronchodilator treatment has not resolved my shortness of breath. Should we evaluate alternative routing?',
    relevance: 'Determining bronchodilator efficacy informs the doctor whether to step up controller therapies or switch agent classes.',
    isAsked: false
  }
];

export const doctorBridgeService = {
  getQuestions(): DoctorQuestion[] {
    const storedDocsRaw = localStorage.getItem('carepath_uploaded_docs');
    const storedDocs = storedDocsRaw ? JSON.parse(storedDocsRaw) : [];

    const dynamicQuestions: DoctorQuestion[] = [];

    storedDocs.forEach((doc: any, idx: number) => {
      const docName = doc.name;
      const conds = doc.result?.extracted?.conditions || [];
      const meds = doc.result?.extracted?.medicines || [];
      const meas = doc.result?.extracted?.measurements || [];

      if (conds.length > 0) {
        dynamicQuestions.push({
          id: `q_doc_cond_${idx}`,
          text: `In document '${docName}', diagnoses of ${conds.join(', ')} were noted. What long-term monitoring or diagnostic follow-ups do you recommend for these conditions?`,
          relevance: `Cross-referenced directly from uploaded document '${docName}'.`,
          isAsked: false
        });
      }

      if (meds.length > 0) {
        dynamicQuestions.push({
          id: `q_doc_med_${idx}`,
          text: `My prescription in '${docName}' lists ${meds.join(', ')}. Are any dosage adjustments or drug interaction checks needed based on my current symptoms?`,
          relevance: `Cross-referenced directly from prescribed medications in '${docName}'.`,
          isAsked: false
        });
      }

      if (meas.length > 0) {
        dynamicQuestions.push({
          id: `q_doc_meas_${idx}`,
          text: `Lab findings in '${docName}' recorded ${meas.join('; ')}. Do these values require repeat laboratory testing or lifestyle modifications?`,
          relevance: `Cross-referenced directly from diagnostic measurements in '${docName}'.`,
          isAsked: false
        });
      }
    });

    const stored = localStorage.getItem('carepath_doctor_questions');
    if (!stored) {
      const finalQ = dynamicQuestions.length > 0 ? dynamicQuestions : INITIAL_QUESTIONS;
      localStorage.setItem('carepath_doctor_questions', JSON.stringify(finalQ));
      return finalQ;
    }

    const currentList: DoctorQuestion[] = JSON.parse(stored);
    const combined = [...dynamicQuestions, ...currentList];
    const uniqueMap = new Map<string, DoctorQuestion>();
    combined.forEach(q => {
      if (!uniqueMap.has(q.text)) {
        uniqueMap.set(q.text, q);
      }
    });

    return Array.from(uniqueMap.values());
  },

  saveQuestions(questions: DoctorQuestion[]): void {
    localStorage.setItem('carepath_doctor_questions', JSON.stringify(questions));
  },

  addQuestion(text: string): DoctorQuestion[] {
    const questions = this.getQuestions();
    const newQuestion: DoctorQuestion = {
      id: `q_custom_${Date.now()}`,
      text,
      relevance: 'Custom patient-added discussion point.',
      isAsked: false,
      isCustom: true
    };
    const updated = [...questions, newQuestion];
    this.saveQuestions(updated);
    return updated;
  },

  toggleQuestionAsked(id: string): DoctorQuestion[] {
    const questions = this.getQuestions();
    const updated = questions.map(q => q.id === id ? { ...q, isAsked: !q.isAsked } : q);
    this.saveQuestions(updated);
    return updated;
  },

  getReview(): DoctorReview | null {
    const stored = localStorage.getItem('carepath_doctor_review');
    return stored ? JSON.parse(stored) : null;
  },

  submitReview(review: DoctorReview): void {
    localStorage.setItem('carepath_doctor_review', JSON.stringify(review));
    window.dispatchEvent(new Event('doctor_review_updated'));
  },

  resetReview(): void {
    localStorage.removeItem('carepath_doctor_review');
    localStorage.removeItem('carepath_doctor_questions');
    window.dispatchEvent(new Event('doctor_review_updated'));
  }
};
