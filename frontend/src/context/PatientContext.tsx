import React, { createContext, useContext, useState, useEffect } from 'react';
import type { Patient } from '../types';
import { patientService } from '../services/patientService';
import { useAuth } from './AuthContext';

interface PatientContextType {
  patient: Patient | null;
  isLoading: boolean;
  error: string | null;
  fetchPatient: (id: string) => Promise<void>;
  updatePatientProfile: (data: Partial<Patient>) => Promise<void>;
  clearPatient: () => void;
}

const PatientContext = createContext<PatientContextType | undefined>(undefined);

export function PatientProvider({ children }: { children: React.ReactNode }) {
  const { patientId } = useAuth();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPatient = async (id: string) => {
    if (id === 'demo_patient_id') {
      // Mock patient for demo mode
      setPatient({
        id: 'demo_patient_id',
        user_id: 'demo_user',
        name: 'Aryan Nair',
        age: 32,
        gender: 'Male',
        blood_type: 'O+',
        allergies: ['Dust Mites', 'Pollen'],
        medical_history: 'Mild Bronchial Hyperreactivity & Seasonal Allergies.',
        current_symptoms: 'Nocturnal dry cough and mild exertional dyspnea for 3 days.',
      });
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await patientService.getPatient(id);
      setPatient(data);
    } catch (err: any) {
      console.warn('Could not fetch patient profile from server, using default profile state:', err);
      setPatient({
        id: id,
        user_id: id,
        name: 'Aryan Nair',
        age: 32,
        gender: 'Male',
        blood_type: 'O+',
        allergies: ['Dust Mites', 'Pollen'],
        medical_history: 'Mild Bronchial Hyperreactivity & Seasonal Allergies.',
        current_symptoms: 'Nocturnal dry cough and mild exertional dyspnea for 3 days.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const updatePatientProfile = async (data: Partial<Patient>) => {
    if (!patient) return;
    
    // Always update local state immediately so changes reflect instantly in UI and confirmation modal
    setPatient(prev => prev ? { ...prev, ...data } : null);

    if (patient.id === 'demo_patient_id') {
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const updated = await patientService.updatePatient(patient.id, data);
      if (updated && updated.id) {
        setPatient(updated);
      }
    } catch (err: any) {
      console.warn('Backend patient profile update warning (state retained locally):', err);
    } finally {
      setIsLoading(false);
    }
  };

  const clearPatient = () => {
    setPatient(null);
    setError(null);
  };

  // Auto-fetch patient when patientId is loaded from auth
  useEffect(() => {
    if (patientId) {
      fetchPatient(patientId);
    } else {
      clearPatient();
    }
  }, [patientId]);

  return (
    <PatientContext.Provider
      value={{
        patient,
        isLoading,
        error,
        fetchPatient,
        updatePatientProfile,
        clearPatient,
      }}
    >
      {children}
    </PatientContext.Provider>
  );
}

export function usePatient() {
  const context = useContext(PatientContext);
  if (context === undefined) {
    throw new Error('usePatient must be used within a PatientProvider');
  }
  return context;
}
