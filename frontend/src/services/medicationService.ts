import type { Medication } from '../components/MedicationCard';

const INITIAL_MEDICATIONS: Medication[] = [
  {
    id: 'med_1',
    name: 'Albuterol Sulfate Inhaler',
    dose: '90 mcg (2 Puffs)',
    time: '08:00 AM',
    frequency: 'Every 4-6 hours as needed',
    instructions: 'Inhale 2 puffs when you feel short of breath or start coughing. Rinse your mouth with water after use.',
    status: 'taken',
    startDate: '11 Aug 2026',
    duration: '14 Days',
    nextDose: '02:00 PM (Log as needed)',
    purpose: 'Relieves wheezing, chest tightness, and shortness of breath by opening up your airways.',
    modeOfIntake: 'Inhale 2 puffs using your inhaler whenever sudden breathing symptoms start.',
    replacementNotes: 'Use this as your quick-relief rescue inhaler for sudden breathing difficulties.',
    sourceDocument: 'rx_albuterol_90mcg.pdf'
  },
  {
    id: 'med_2',
    name: 'Amoxicillin Oral Capsule',
    dose: '500 mg (1 Capsule)',
    time: '09:00 AM',
    frequency: '3 times daily (Every 8 hours)',
    instructions: 'Take 1 capsule with food or water. Finish all 7 days of medicine even if you feel better.',
    status: 'upcoming',
    startDate: '12 Aug 2026',
    duration: '7 Days',
    nextDose: '02:00 PM',
    purpose: 'Fights off bacterial infections in your lungs, chest, throat, or ears.',
    modeOfIntake: 'Swallow 1 capsule whole with water or meals 3 times a day (every 8 hours).',
    replacementNotes: 'Short-term 7-day antibiotic course to clear your bacterial infection.',
    sourceDocument: '01_patient_medical_record.pdf'
  },
  {
    id: 'med_3',
    name: 'Metformin Oral Tablet',
    dose: '500 mg (1 Tablet)',
    time: '08:30 AM',
    frequency: 'Twice daily with meals',
    instructions: 'Take 1 tablet with breakfast and 1 tablet with dinner to help control your blood sugar.',
    status: 'upcoming',
    startDate: '13 Aug 2026',
    duration: 'Ongoing',
    nextDose: '07:30 PM (Evening Dose)',
    purpose: 'Helps manage your blood sugar levels and improves insulin response for Type 2 Diabetes.',
    modeOfIntake: 'Swallow 1 tablet twice daily with your morning breakfast and evening dinner.',
    replacementNotes: 'Daily prescription to keep your blood sugar steady throughout the day.',
    sourceDocument: '01_patient_medical_record.pdf'
  },
  {
    id: 'med_4',
    name: 'Lisinopril Blood Pressure Tablet',
    dose: '10 mg (1 Tablet)',
    time: '09:00 AM',
    frequency: 'Once daily in the morning',
    instructions: 'Take 1 tablet every morning with a full glass of water for blood pressure management.',
    status: 'taken',
    startDate: '01 Aug 2026',
    duration: 'Ongoing',
    nextDose: 'Tomorrow at 09:00 AM',
    purpose: 'Lowers high blood pressure and helps protect your kidney health.',
    modeOfIntake: 'Swallow 1 tablet every morning with a full glass of water.',
    replacementNotes: 'Daily blood pressure medicine. Try to take it at the same time every morning.',
    sourceDocument: '01_patient_medical_record.pdf'
  }
];

export const medicationService = {
  getMedications(): Medication[] {
    const storedDocsRaw = localStorage.getItem('carepath_uploaded_docs');
    const storedDocs = storedDocsRaw ? JSON.parse(storedDocsRaw) : [];
    
    // Filter uploaded documents that contain parsed medicines
    const docsWithMeds = storedDocs.filter(
      (d: any) => d.result?.extracted?.medicines && d.result.extracted.medicines.length > 0
    );

    const uploadedMedsList: Medication[] = [];

    docsWithMeds.forEach((doc: any, docIdx: number) => {
      const medicines: string[] = doc.result.extracted.medicines;
      const instructions: string[] = doc.result.extracted.instructions || [];
      const uploadDate = doc.uploadedAt ? new Date(doc.uploadedAt).toLocaleDateString() : 'Recent Upload';

      medicines.forEach((medName: string, medIdx: number) => {
        const lowerName = medName.toLowerCase();
        
        let dose = 'As Prescribed';
        let time = '09:00 AM';
        let frequency = 'Daily';
        let timingAdvice = 'Take as directed on your prescription label.';
        let nextDose = '09:00 AM Tomorrow';

        let purpose = 'Prescribed by your doctor to manage your health condition and symptoms.';
        let modeOfIntake = 'Take by mouth with water according to your prescription directions.';
        let replacementNotes = `Extracted from '${doc.name}'. Saved in your active medication list.`;

        if (lowerName.includes('500mg') || lowerName.includes('500 mg')) dose = '500 mg (1 Capsule/Tablet)';
        else if (lowerName.includes('90mcg') || lowerName.includes('90 mcg') || lowerName.includes('inhaler') || lowerName.includes('puff')) dose = '90 mcg (2 Puffs)';
        else if (lowerName.includes('10mg') || lowerName.includes('10 mg')) dose = '10 mg (1 Tablet)';
        else if (lowerName.includes('650mg') || lowerName.includes('650 mg')) dose = '650 mg (1 Tablet)';

        if (lowerName.includes('albuterol') || lowerName.includes('inhaler') || lowerName.includes('puff') || lowerName.includes('sulfate')) {
          time = '08:00 AM';
          frequency = 'Every 4-6 hours as needed';
          timingAdvice = 'Inhale 2 puffs when you feel short of breath or start coughing. Rinse your mouth with water after use.';
          nextDose = 'Log dose as needed';
          purpose = 'Relieves wheezing, chest tightness, and shortness of breath by opening up your airways.';
          modeOfIntake = 'Inhale 2 puffs using your inhaler whenever sudden breathing symptoms start.';
          replacementNotes = 'Use this as your quick-relief rescue inhaler for sudden breathing difficulties.';
        } else if (lowerName.includes('metformin') || lowerName.includes('diabetes') || lowerName.includes('glucose')) {
          time = '08:30 AM';
          frequency = 'Twice Daily (Morning & Evening)';
          timingAdvice = 'Take 1 tablet with meals (breakfast & dinner) to avoid stomach upset.';
          nextDose = '07:30 PM (Evening Dose)';
          purpose = 'Helps manage your blood sugar levels and improves insulin response for Type 2 Diabetes.';
          modeOfIntake = 'Swallow 1 tablet twice daily with your morning breakfast and evening dinner.';
          replacementNotes = 'Daily prescription to keep your blood sugar steady throughout the day.';
        } else if (lowerName.includes('lisinopril') || lowerName.includes('pressure') || lowerName.includes('hypertension')) {
          time = '09:00 AM';
          frequency = 'Once Daily in the Morning';
          timingAdvice = 'Take 1 tablet every morning with a full glass of water for blood pressure management.';
          nextDose = '09:00 AM Tomorrow';
          purpose = 'Lowers high blood pressure and helps protect your kidney health.';
          modeOfIntake = 'Swallow 1 tablet every morning with a full glass of water.';
          replacementNotes = 'Daily blood pressure medicine. Try to take it at the same time every morning.';
        } else if (lowerName.includes('amoxicillin') || lowerName.includes('antibiotic')) {
          time = '09:00 AM';
          frequency = 'Three Times Daily (Every 8 Hours)';
          timingAdvice = 'Take 1 capsule with food or water. Finish all 7 days of medicine even if you feel better.';
          nextDose = '02:00 PM (Afternoon Dose)';
          purpose = 'Fights off bacterial infections in your lungs, chest, throat, or ears.';
          modeOfIntake = 'Swallow 1 capsule whole with water or meals 3 times a day (every 8 hours).';
          replacementNotes = 'Short-term 7-day antibiotic course to clear your bacterial infection.';
        } else if (lowerName.includes('paracetamol') || lowerName.includes('acetaminophen')) {
          time = '10:00 AM';
          frequency = 'Every 6-8 hours as needed';
          timingAdvice = 'Take 1 tablet with water when needed for fever or pain. Do not exceed 4 tablets in 24 hours.';
          nextDose = '04:00 PM (As needed)';
          purpose = 'Reduces fever and eases headaches, body aches, or pain.';
          modeOfIntake = 'Swallow 1 tablet with water as needed when you have pain or fever.';
          replacementNotes = 'Take as needed for pain or fever relief.';
        } else if (instructions[medIdx]) {
          timingAdvice = instructions[medIdx];
          modeOfIntake = instructions[medIdx];
        }

        uploadedMedsList.push({
          id: `med_up_${docIdx}_${medIdx}_${medName.replace(/\s+/g, '_')}`,
          name: medName,
          dose: dose,
          time: time,
          frequency: frequency,
          instructions: timingAdvice,
          status: medIdx === 0 ? 'taken' : 'upcoming',
          startDate: uploadDate,
          duration: 'Prescribed Course',
          nextDose: nextDose,
          purpose: purpose,
          modeOfIntake: modeOfIntake,
          replacementNotes: replacementNotes,
          sourceDocument: doc.name
        });
      });
    });

    function sanitizeMed(m: Medication): Medication {
      let purpose = m.purpose || '';
      let modeOfIntake = m.modeOfIntake || m.instructions || '';
      let replacementNotes = m.replacementNotes || '';

      if (purpose.includes('bronchial spasms') || purpose.includes('smooth airway muscles')) {
        purpose = 'Relieves wheezing, chest tightness, and shortness of breath by opening up your airways.';
      }
      if (modeOfIntake.includes('Inhaled aerosol') || modeOfIntake.includes('via MDI inhaler')) {
        modeOfIntake = 'Inhale 2 puffs using your inhaler whenever sudden breathing symptoms start.';
      }
      if (replacementNotes.includes('Active rescue inhaler replacing prior oral bronchodilator') || replacementNotes.includes('rapid airway symptom relief')) {
        replacementNotes = 'Use this as your quick-relief rescue inhaler for sudden breathing difficulties.';
      }

      if (purpose.includes('bacterial respiratory tract') || purpose.includes('ENT infections')) {
        purpose = 'Fights off bacterial infections in your lungs, chest, throat, or ears.';
      }
      if (modeOfIntake.includes('Oral capsule') || modeOfIntake.includes('swallowed whole')) {
        modeOfIntake = 'Swallow 1 capsule whole with water or meals 3 times a day (every 8 hours).';
      }

      if (purpose.includes('blood glucose levels') || purpose.includes('insulin sensitivity')) {
        purpose = 'Helps manage your blood sugar levels and improves insulin response for Type 2 Diabetes.';
      }
      if (purpose.includes('systemic blood pressure') || purpose.includes('Hypertension')) {
        purpose = 'Lowers high blood pressure and helps protect your kidney health.';
      }

      return {
        ...m,
        purpose: purpose || 'Prescribed by your doctor to manage your health condition and symptoms.',
        modeOfIntake: modeOfIntake || m.instructions || 'Take by mouth with water according to your prescription directions.',
        replacementNotes: replacementNotes || 'Follow your prescribed schedule and keep taking as directed.'
      };
    }

    const storedMeds = localStorage.getItem('carepath_medications');
    const userModifiedList: Medication[] = storedMeds ? JSON.parse(storedMeds) : [];

    const combined = [...uploadedMedsList, ...userModifiedList, ...INITIAL_MEDICATIONS];
    const uniqueMap = new Map<string, Medication>();
    combined.forEach(m => {
      const key = m.name.toLowerCase().trim();
      if (!uniqueMap.has(key)) {
        uniqueMap.set(key, sanitizeMed(m));
      }
    });

    return Array.from(uniqueMap.values());
  },

  saveMedications(meds: Medication[]): void {
    localStorage.setItem('carepath_medications', JSON.stringify(meds));
  },

  markAsTaken(id: string): Medication[] {
    const meds = this.getMedications();
    const updated = meds.map(m => m.id === id ? { ...m, status: 'taken' as const } : m);
    this.saveMedications(updated);
    
    window.dispatchEvent(new Event('medication_updated'));
    
    return updated;
  },

  getAdherenceSummary() {
    const meds = this.getMedications();
    const total = meds.length;
    const taken = meds.filter(m => m.status === 'taken').length;
    const missed = meds.filter(m => m.status === 'missed').length;
    
    const historicalTotal = 24;
    const historicalTaken = 21;
    const historicalMissed = 3;
    
    const overallTaken = historicalTaken + taken;
    const overallTotal = historicalTotal + total;
    const percentage = Math.round((overallTaken / overallTotal) * 100);

    return {
      percentage,
      missed: historicalMissed + missed,
      taken: overallTaken,
      total: overallTotal
    };
  }
};
