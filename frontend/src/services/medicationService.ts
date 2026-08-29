import type { Medication } from '../components/MedicationCard';

const INITIAL_MEDICATIONS: Medication[] = [
  {
    id: 'med_1',
    name: 'Albuterol Sulfate Inhaler',
    dose: '90 mcg (2 Puffs)',
    time: '08:00 AM',
    frequency: 'Every 4-6 hours as needed',
    instructions: 'Inhale 2 puffs for shortness of breath or persistent dry cough. Rinse mouth with water after use.',
    status: 'taken',
    startDate: '11 Aug 2026',
    duration: '14 Days',
    nextDose: '02:00 PM (Log as needed)',
    purpose: 'Relieves bronchial spasms, wheezing, and acute shortness of breath by relaxing smooth airway muscles.',
    modeOfIntake: 'Inhaled aerosol (2 puffs via MDI inhaler as needed for respiratory symptoms).',
    replacementNotes: 'Active rescue inhaler replacing prior oral bronchodilator for rapid airway symptom relief.',
    sourceDocument: 'rx_albuterol_90mcg.pdf'
  },
  {
    id: 'med_2',
    name: 'Amoxicillin Oral Capsule',
    dose: '500 mg (1 Capsule)',
    time: '09:00 AM',
    frequency: 'Three times daily (Every 8 hours)',
    instructions: 'Take with food or water. Finish the entire prescribed course of medication.',
    status: 'upcoming',
    startDate: '12 Aug 2026',
    duration: '7 Days',
    nextDose: '02:00 PM',
    purpose: 'Treats active bacterial respiratory tract and ENT infections.',
    modeOfIntake: 'Oral capsule (1 capsule 3 times daily swallowed whole with water or meals).',
    replacementNotes: 'Short-term 7-day targeted antibiotic course replacing empirical antimicrobial therapy.',
    sourceDocument: '01_patient_medical_record.pdf'
  },
  {
    id: 'med_3',
    name: 'Metformin Oral Tablet',
    dose: '500 mg (1 Tablet)',
    time: '08:30 AM',
    frequency: 'Twice daily with meals',
    instructions: 'Take 1 tablet with breakfast and dinner to support blood glucose control.',
    status: 'upcoming',
    startDate: '13 Aug 2026',
    duration: 'Ongoing',
    nextDose: '07:30 PM (Evening Dose)',
    purpose: 'Controls blood glucose levels and improves insulin sensitivity for Type 2 Diabetes Mellitus.',
    modeOfIntake: 'Oral tablet (1 tablet twice daily with morning & evening meals).',
    replacementNotes: 'First-line antihyperglycemic therapy maintained from physician prescription.',
    sourceDocument: '01_patient_medical_record.pdf'
  },
  {
    id: 'med_4',
    name: 'Lisinopril Blood Pressure Tablet',
    dose: '10 mg (1 Tablet)',
    time: '09:00 AM',
    frequency: 'Once daily in the morning',
    instructions: 'Take 1 tablet every morning with or without food for blood pressure management.',
    status: 'taken',
    startDate: '01 Aug 2026',
    duration: 'Ongoing',
    nextDose: 'Tomorrow at 09:00 AM',
    purpose: 'Lowers systemic blood pressure and protects kidney function in Hypertension.',
    modeOfIntake: 'Oral tablet (1 tablet daily in the morning with a full glass of water).',
    replacementNotes: 'Maintained first-line ACE inhibitor therapy for consistent blood pressure control.',
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
        let timingAdvice = 'Take as directed on prescription label.';
        let nextDose = '09:00 AM Tomorrow';

        let purpose = 'Prescribed for clinical symptom management and condition control.';
        let modeOfIntake = 'Oral administration with water.';
        let replacementNotes = `Extracted from uploaded document '${doc.name}'. Active prescription maintained in care plan.`;

        if (lowerName.includes('500mg') || lowerName.includes('500 mg')) dose = '500 mg (1 Capsule/Tablet)';
        else if (lowerName.includes('90mcg') || lowerName.includes('90 mcg') || lowerName.includes('inhaler') || lowerName.includes('puff')) dose = '90 mcg (2 Puffs)';
        else if (lowerName.includes('10mg') || lowerName.includes('10 mg')) dose = '10 mg (1 Tablet)';
        else if (lowerName.includes('650mg') || lowerName.includes('650 mg')) dose = '650 mg (1 Tablet)';

        if (lowerName.includes('albuterol') || lowerName.includes('inhaler') || lowerName.includes('puff') || lowerName.includes('sulfate')) {
          time = '08:00 AM';
          frequency = 'Every 4-6 hours as needed';
          timingAdvice = 'Inhale 2 puffs for shortness of breath or cough. Rinse mouth with water after use.';
          nextDose = 'Log dose as needed';
          purpose = 'Relieves bronchial spasms, wheezing, and acute shortness of breath by relaxing smooth airway muscles.';
          modeOfIntake = 'Inhaled aerosol (2 puffs via MDI inhaler as needed for respiratory symptoms).';
          replacementNotes = 'Active rescue inhaler replacing prior oral bronchodilator for rapid airway symptom relief.';
        } else if (lowerName.includes('metformin') || lowerName.includes('diabetes') || lowerName.includes('glucose')) {
          time = '08:30 AM';
          frequency = 'Twice Daily (Morning & Evening)';
          timingAdvice = 'Take 1 tablet with meals (breakfast & dinner) to minimize stomach upset.';
          nextDose = '07:30 PM (Evening Dose)';
          purpose = 'Controls blood glucose levels and improves insulin sensitivity for Type 2 Diabetes Mellitus.';
          modeOfIntake = 'Oral tablet (1 tablet twice daily with morning & evening meals).';
          replacementNotes = 'First-line antihyperglycemic therapy maintained from physician prescription.';
        } else if (lowerName.includes('lisinopril') || lowerName.includes('pressure') || lowerName.includes('hypertension')) {
          time = '09:00 AM';
          frequency = 'Once Daily in the Morning';
          timingAdvice = 'Take 1 tablet every morning with or without food. Maintain consistent daily timing.';
          nextDose = '09:00 AM Tomorrow';
          purpose = 'Lowers systemic blood pressure and protects kidney function in Hypertension.';
          modeOfIntake = 'Oral tablet (1 tablet daily in the morning with a full glass of water).';
          replacementNotes = 'Maintained first-line ACE inhibitor therapy for consistent blood pressure control.';
        } else if (lowerName.includes('amoxicillin') || lowerName.includes('antibiotic')) {
          time = '09:00 AM';
          frequency = 'Three Times Daily (Every 8 Hours)';
          timingAdvice = 'Take with food or water. Complete the full prescribed course even if symptoms improve.';
          nextDose = '02:00 PM (Afternoon Dose)';
          purpose = 'Treats active bacterial respiratory tract and ENT infections.';
          modeOfIntake = 'Oral capsule (1 capsule 3 times daily swallowed whole with water or meals).';
          replacementNotes = 'Short-term 7-day targeted antibiotic course replacing empirical antimicrobial therapy.';
        } else if (lowerName.includes('paracetamol') || lowerName.includes('acetaminophen')) {
          time = '10:00 AM';
          frequency = 'Every 6-8 hours as needed';
          timingAdvice = 'Take 1 tablet with water for fever or pain relief. Do not exceed 4,000 mg daily.';
          nextDose = '04:00 PM (As needed)';
          purpose = 'Reduces mild-to-moderate fever and relieves acute pain.';
          modeOfIntake = 'Oral tablet (1 tablet with water as needed).';
          replacementNotes = 'As-needed symptom relief replacing prior NSAID therapy to minimize stomach irritation.';
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

    const storedMeds = localStorage.getItem('carepath_medications');
    const userModifiedList: Medication[] = storedMeds ? JSON.parse(storedMeds) : [];

    const combined = [...uploadedMedsList, ...userModifiedList, ...INITIAL_MEDICATIONS];
    const uniqueMap = new Map<string, Medication>();
    combined.forEach(m => {
      const key = m.name.toLowerCase().trim();
      if (!uniqueMap.has(key)) {
        uniqueMap.set(key, m);
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
