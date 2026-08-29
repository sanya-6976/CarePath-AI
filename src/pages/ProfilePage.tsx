import React, { useState, useEffect } from 'react';
import { usePatient } from '../context/PatientContext';
import { AlertCircle, CheckCircle2, User, Save, Heart, ShieldAlert, X, Sparkles } from 'lucide-react';

export default function ProfilePage() {
  const { patient, updatePatientProfile, isLoading, error } = usePatient();
  
  const [name, setName] = useState('');
  const [age, setAge] = useState<number>(30);
  const [gender, setGender] = useState('Male');
  const [bloodType, setBloodType] = useState('O+');
  const [allergiesInput, setAllergiesInput] = useState('');
  const [medicalHistory, setMedicalHistory] = useState('');
  const [currentSymptoms, setCurrentSymptoms] = useState('');
  
  const [showSuccessModal, setShowSuccessModal] = useState<boolean>(false);

  // Sync state with patient context
  useEffect(() => {
    if (patient) {
      setName(patient.name || '');
      setAge(patient.age || 30);
      setGender(patient.gender || 'Male');
      setBloodType(patient.blood_type || 'O+');
      setAllergiesInput(patient.allergies?.join(', ') || '');
      setMedicalHistory(patient.medical_history || '');
      setCurrentSymptoms(patient.current_symptoms || '');
    }
  }, [patient]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const allergies = allergiesInput
      .split(',')
      .map((item) => item.trim())
      .filter((item) => item.length > 0);

    try {
      await updatePatientProfile({
        name,
        age: Number(age),
        gender,
        blood_type: bloodType,
        allergies,
        medical_history: medicalHistory,
        current_symptoms: currentSymptoms,
      });
      setShowSuccessModal(true);
    } catch (err) {
      console.error('Failed to update patient profile:', err);
    }
  };

  const parsedAllergies = allergiesInput
    .split(',')
    .map((item) => item.trim())
    .filter((item) => item.length > 0);

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-6 relative">

      {error && (
        <div className="bg-brand-rose-bg border border-brand-rose-text/10 text-brand-rose-text p-4 rounded-xl text-sm flex items-center gap-2.5 shadow-sm">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-brand-card border border-brand-slate/10 p-6 md:p-8 rounded-2xl shadow-sm flex flex-col gap-6">
        {/* Core demographic information */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex flex-col gap-1.5 md:col-span-2">
            <label className="text-xs font-semibold text-brand-slate px-0.5">Full Name</label>
            <div className="relative">
              <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-brand-slate" />
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-brand-bg border border-brand-slate/15 rounded-xl pl-10 pr-4 py-3 text-sm focus:border-brand-lavender focus:ring-1 focus:ring-brand-lavender outline-none transition-all"
                required
              />
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-brand-slate px-0.5">Age</label>
            <input
              type="number"
              value={age}
              onChange={(e) => setAge(Number(e.target.value))}
              min="0"
              max="130"
              className="w-full bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-3 text-sm focus:border-brand-lavender focus:ring-1 focus:ring-brand-lavender outline-none transition-all"
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-brand-slate px-0.5">Gender</label>
            <select
              value={gender}
              onChange={(e) => setGender(e.target.value)}
              className="w-full bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-3 text-sm focus:border-brand-lavender focus:ring-1 focus:ring-brand-lavender outline-none transition-all"
            >
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
              <option value="Prefer not to say">Prefer not to say</option>
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-brand-slate px-0.5">Blood Type</label>
            <input
              type="text"
              placeholder="e.g. O+, A-"
              value={bloodType}
              onChange={(e) => setBloodType(e.target.value)}
              className="w-full bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-3 text-sm focus:border-brand-lavender focus:ring-1 focus:ring-brand-lavender outline-none transition-all"
            />
          </div>
        </div>

        {/* Medical details fields */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold text-brand-slate px-0.5">Allergies (comma-separated)</label>
          <input
            type="text"
            placeholder="e.g. Penicillin, Peanuts, Pollen"
            value={allergiesInput}
            onChange={(e) => setAllergiesInput(e.target.value)}
            className="w-full bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-3 text-sm focus:border-brand-lavender focus:ring-1 focus:ring-brand-lavender outline-none transition-all"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold text-brand-slate px-0.5">Medical History Summary</label>
          <textarea
            rows={3}
            placeholder="Brief description of past surgeries, chronic illnesses, active medications..."
            value={medicalHistory}
            onChange={(e) => setMedicalHistory(e.target.value)}
            className="w-full bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-3 text-sm focus:border-brand-lavender focus:ring-1 focus:ring-brand-lavender outline-none transition-all resize-none"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold text-brand-slate px-0.5">Active Symptoms & Concerns</label>
          <textarea
            rows={4}
            placeholder="How are you feeling? Detail symptoms, onset, severity, what triggers them..."
            value={currentSymptoms}
            onChange={(e) => setCurrentSymptoms(e.target.value)}
            className="w-full bg-brand-bg border border-brand-slate/15 rounded-xl px-4 py-3 text-sm focus:border-brand-lavender focus:ring-1 focus:ring-brand-lavender outline-none transition-all resize-none"
          />
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={isLoading}
          className="bg-brand-lavender hover:bg-brand-lavender-hover disabled:bg-brand-lavender/50 text-white font-semibold text-sm py-3 rounded-xl transition-all shadow-sm flex items-center justify-center gap-2 mt-4 cursor-pointer"
        >
          {isLoading ? 'Saving Changes...' : 'Save Patient Context'}
          <Save className="w-4 h-4" />
        </button>
      </form>

      {/* Centered Profile Updated Dialog Modal */}
      {showSuccessModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-md animate-in fade-in duration-200">
          <div 
            className="bg-brand-card border border-brand-slate/20 rounded-3xl p-6 md:p-8 max-w-md w-full shadow-2xl flex flex-col items-center text-center relative animate-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close Button */}
            <button
              type="button"
              onClick={() => setShowSuccessModal(false)}
              className="absolute top-4 right-4 p-2 text-brand-slate hover:text-brand-plum hover:bg-brand-bg rounded-full transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Glowing Icon Badge */}
            <div className="w-16 h-16 bg-brand-sage-bg border border-brand-sage-text/20 text-brand-sage-text rounded-2xl flex items-center justify-center mb-4 shadow-sm relative">
              <CheckCircle2 className="w-8 h-8" />
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-brand-sage-text rounded-full flex items-center justify-center text-white">
                <Sparkles className="w-2.5 h-2.5" />
              </div>
            </div>

            {/* Modal Title & Message */}
            <h3 className="font-display text-2xl font-bold text-brand-plum mb-2">Profile Updated!</h3>
            <p className="text-sm text-brand-slate leading-relaxed mb-6">
              Your patient profile and clinical context have been successfully saved to your CarePath health graph.
            </p>

            {/* Profile Snapshot Summary */}
            <div className="w-full bg-brand-bg/80 border border-brand-slate/10 rounded-2xl p-4 mb-6 flex flex-col gap-2.5 text-left text-xs">
              <div className="flex justify-between items-center pb-2 border-b border-brand-slate/10">
                <span className="font-semibold text-brand-slate">Patient Name:</span>
                <span className="font-bold text-brand-plum">{name || 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="font-semibold text-brand-slate">Demographics:</span>
                <span className="text-brand-plum">{age} yrs • {gender}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="font-semibold text-brand-slate">Blood Group:</span>
                <span className="text-brand-plum font-semibold">{bloodType || 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="font-semibold text-brand-slate">Active Allergies:</span>
                <span className="text-brand-plum">{parsedAllergies.length > 0 ? parsedAllergies.join(', ') : 'None listed'}</span>
              </div>
            </div>

            {/* Action Button */}
            <button
              type="button"
              onClick={() => setShowSuccessModal(false)}
              className="w-full bg-brand-lavender hover:bg-brand-lavender-hover text-white font-semibold py-3 px-6 rounded-xl transition-all shadow-md shadow-brand-lavender/25 flex items-center justify-center gap-2 cursor-pointer"
            >
              Continue to Workspace
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
