import React, { useState, useEffect } from 'react';
import { medicationService } from '../services/medicationService';
import MedicationCard, { Medication } from '../components/MedicationCard';
import { Pill, Activity, AlertCircle, TrendingUp, CheckCircle, Clock } from 'lucide-react';

export default function MedicationsPage() {
  const [medications, setMedications] = useState<Medication[]>([]);
  const [adherence, setAdherence] = useState({ percentage: 0, missed: 0, taken: 0, total: 0 });

  const loadMedData = () => {
    const meds = medicationService.getMedications();
    setMedications(meds);
    setAdherence(medicationService.getAdherenceSummary());
  };

  useEffect(() => {
    loadMedData();

    // Listen for medication updates from other views (e.g. Dashboard)
    window.addEventListener('medication_updated', loadMedData);
    return () => {
      window.removeEventListener('medication_updated', loadMedData);
    };
  }, []);

  const handleMarkAsTaken = (id: string) => {
    medicationService.markAsTaken(id);
    loadMedData();
  };

  const resetDailyTracker = () => {
    if (window.confirm('Reset the daily medication logs for testing purposes?')) {
      const meds = medicationService.getMedications();
      const reset = meds.map(m => m.id === 'med_2' || m.id === 'med_3' ? { ...m, status: 'upcoming' as const } : m);
      medicationService.saveMedications(reset);
      loadMedData();
    }
  };

  const upcomingMeds = medications.filter(m => m.status === 'upcoming');
  const loggedMeds = medications.filter(m => m.status === 'taken');
  const missedMeds = medications.filter(m => m.status === 'missed');

  return (
    <div className="flex flex-col gap-8 animate-in fade-in duration-300">
      {/* Adherence Summary Panel */}
      <div className="bg-brand-card border border-brand-slate/10 p-6 md:p-8 rounded-3xl shadow-sm grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        
        {/* Left Side: Circular Adherence Meter */}
        <div className="flex flex-col items-center justify-center text-center gap-3 border-r border-brand-slate/10 pr-0 md:pr-6 md:border-r">
          <div className="relative w-28 h-28 flex items-center justify-center">
            {/* SVG circle track */}
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="56"
                cy="56"
                r="46"
                className="stroke-brand-bg fill-none"
                strokeWidth="8"
              />
              <circle
                cx="56"
                cy="56"
                r="46"
                className="stroke-brand-lavender fill-none transition-all duration-500"
                strokeWidth="8"
                strokeDasharray={2 * Math.PI * 46}
                strokeDashoffset={2 * Math.PI * 46 * (1 - adherence.percentage / 100)}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center">
              <span className="font-display font-extrabold text-2xl text-brand-plum leading-none">{adherence.percentage}%</span>
              <span className="text-[9px] font-bold text-brand-slate uppercase mt-1 tracking-wider">Adherence</span>
            </div>
          </div>
          <p className="text-xxs text-brand-slate max-w-[160px] font-light leading-relaxed">
            Overall dosing compliance based on logs.
          </p>
        </div>

        {/* Middle: Breakdown Stats */}
        <div className="grid grid-cols-2 gap-4 flex-1">
          <div className="bg-brand-bg/50 border border-brand-slate/5 p-4 rounded-2xl flex flex-col justify-between min-h-[90px]">
            <span className="text-[10px] font-bold text-brand-slate uppercase block mb-1">Taken Doses</span>
            <div>
              <span className="font-display font-extrabold text-xl text-brand-sage-text">{adherence.taken}</span>
              <span className="text-xxs text-brand-slate block mt-0.5">Successful check-ins</span>
            </div>
          </div>
          
          <div className="bg-brand-bg/50 border border-brand-slate/5 p-4 rounded-2xl flex flex-col justify-between min-h-[90px]">
            <span className="text-[10px] font-bold text-brand-slate uppercase block mb-1">Missed Doses</span>
            <div>
              <span className="font-display font-extrabold text-xl text-brand-rose-text">{adherence.missed}</span>
              <span className="text-xxs text-brand-slate block mt-0.5">Alert exceptions logged</span>
            </div>
          </div>
        </div>

        {/* Right Side: Quick Action Advice */}
        <div className="bg-brand-lavender-light/35 border border-brand-lavender/10 p-5 rounded-2xl flex gap-3 h-full justify-center flex-col">
          <div className="flex items-center gap-1.5 text-brand-lavender font-bold text-xs uppercase tracking-wider">
            <TrendingUp className="w-4 h-4" />
            <span>Adherence Insight</span>
          </div>
          <p className="text-xxs text-brand-plum leading-relaxed font-light mt-1.5">
            CarePath suggests logging dose intakes within 15 minutes of schedule warnings. Maintaining above 85% compliance supports optimal pulmonary therapy responses.
          </p>
        </div>
      </div>

      {/* Grid: Active Medications & Sidebars */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Left: Medications List (2 Cols) */}
        <div className="lg:col-span-2 flex flex-col gap-5">
          <div className="flex items-center justify-between border-b border-brand-slate/10 pb-3">
            <h3 className="font-display font-bold text-sm text-brand-plum flex items-center gap-2">
              <Pill className="w-4.5 h-4.5 text-brand-lavender" />
              Active Medication Treatment
            </h3>
            <span className="text-[10px] text-brand-slate font-light">
              Showing {medications.length} active courses
            </span>
          </div>

          <div className="flex flex-col gap-4">
            {medications.map(med => (
              <MedicationCard
                key={med.id}
                medication={med}
                onMarkAsTaken={handleMarkAsTaken}
                showDetails={true}
              />
            ))}
          </div>
        </div>

        {/* Right Sidebar: Today's Status & Warnings */}
        <div className="flex flex-col gap-6">
          {/* Dosing Warnings / Alerts */}
          {missedMeds.length > 0 && (
            <div className="bg-brand-rose-bg border border-brand-rose-text/15 p-5 rounded-3xl flex flex-col gap-3 shadow-xxs">
              <div className="flex items-center gap-2 text-brand-rose-text font-bold text-xs">
                <AlertCircle className="w-4.5 h-4.5" />
                <span>MISSED DOSES WARNING</span>
              </div>
              <p className="text-xxs text-brand-rose-text leading-relaxed font-light">
                CarePath noticed you missed {missedMeds.length} scheduled dose(s) today. Please resume your schedule or consult your physician if you experience adverse respiratory setbacks.
              </p>
              <div className="flex flex-col gap-2 mt-1">
                {missedMeds.map(m => (
                  <div key={m.id} className="text-xxs font-bold text-brand-plum flex justify-between bg-brand-card p-2 rounded-lg border border-brand-rose-text/10">
                    <span>{m.name}</span>
                    <span className="text-brand-rose-text">Scheduled {m.time}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Reset Daily Logs Action */}
          <button
            onClick={resetDailyTracker}
            className="w-full text-center text-xxs font-bold text-brand-lavender hover:text-brand-lavender-hover border border-brand-lavender/20 py-2.5 rounded-xl bg-brand-lavender-light/10 transition-all cursor-pointer shadow-xxs"
          >
            Reset Logs
          </button>

          {/* Today's Schedule Overview */}
          <div className="bg-brand-card border border-brand-slate/10 p-5 rounded-3xl shadow-sm flex flex-col gap-4">
            <h4 className="font-display text-xs font-bold tracking-wider text-brand-slate uppercase border-b border-brand-slate/10 pb-2 flex items-center gap-2">
              <Clock className="w-4 h-4 text-brand-lavender" />
              Today's Schedule Checklist
            </h4>

            {upcomingMeds.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-6 text-center">
                <CheckCircle className="w-8 h-8 text-brand-sage-text mb-2" />
                <p className="text-xxs text-brand-slate font-light">All doses for today have been logged successfully!</p>
              </div>
            ) : (
              <div className="flex flex-col gap-3">
                {upcomingMeds.map(med => (
                  <div key={med.id} className="flex items-center justify-between border-b border-brand-slate/5 pb-2.5 last:border-0 last:pb-0">
                    <div>
                      <span className="text-xs font-bold text-brand-plum block leading-tight">{med.name}</span>
                      <span className="text-xxs text-brand-slate font-light mt-0.5 block">{med.dose} &bull; {med.time}</span>
                    </div>
                    <button
                      onClick={() => handleMarkAsTaken(med.id)}
                      className="text-[10px] font-bold text-brand-lavender hover:bg-brand-lavender-light border border-brand-lavender/25 px-2.5 py-1 rounded-lg cursor-pointer transition-all shrink-0"
                    >
                      Log Taken
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
