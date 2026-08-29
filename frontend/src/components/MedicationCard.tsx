import React from 'react';
import { Pill, Check, Clock, AlertTriangle, CalendarRange, Target, Activity, RefreshCw, FileText } from 'lucide-react';

export interface Medication {
  id: string;
  name: string;
  dose: string;
  time: string;
  frequency: string;
  instructions: string;
  status: 'taken' | 'upcoming' | 'missed';
  startDate: string;
  duration: string;
  nextDose: string;
  // Clinical LLM Extraction & Analysis fields
  purpose?: string;
  modeOfIntake?: string;
  replacementNotes?: string;
  sourceDocument?: string;
}

interface MedicationCardProps {
  key?: React.Key;
  medication: Medication;
  onMarkAsTaken?: (id: string) => void;
  showDetails?: boolean;
}

export default function MedicationCard({ 
  medication, 
  onMarkAsTaken, 
  showDetails = true 
}: MedicationCardProps) {
  const getStatusStyles = () => {
    switch (medication.status) {
      case 'taken':
        return 'bg-brand-sage-bg text-brand-sage-text border-brand-sage-text/10';
      case 'missed':
        return 'bg-brand-rose-bg text-brand-rose-text border-brand-rose-text/10';
      default:
        return 'bg-brand-bg text-brand-plum border-brand-slate/15';
    }
  };

  const getStatusIcon = () => {
    switch (medication.status) {
      case 'taken':
        return <Check className="w-3 h-3" />;
      case 'missed':
        return <AlertTriangle className="w-3 h-3 text-brand-rose-text" />;
      default:
        return <Clock className="w-3 h-3" />;
    }
  };

  return (
    <div className={`bg-brand-card border border-brand-slate/10 rounded-2xl p-5 shadow-xs transition-all hover:border-brand-lavender/20 flex flex-col gap-4 ${
      medication.status === 'taken' ? 'opacity-90 bg-brand-bg/10' : ''
    }`}>
      {/* Header Row */}
      <div className="flex items-start justify-between gap-4">
        {/* Left: Icon & Name */}
        <div className="flex gap-3.5 min-w-0">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
            medication.status === 'taken' 
              ? 'bg-brand-sage-bg text-brand-sage-text' 
              : medication.status === 'missed'
              ? 'bg-brand-rose-bg text-brand-rose-text'
              : 'bg-brand-lavender-light text-brand-lavender'
          }`}>
            <Pill className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="font-display font-bold text-sm text-brand-plum truncate">{medication.name}</h4>
              {medication.sourceDocument && (
                <span className="text-[9px] font-bold text-brand-lavender bg-brand-lavender-light px-2 py-0.5 rounded-full flex items-center gap-1 shrink-0">
                  <FileText className="w-2.5 h-2.5" />
                  {medication.sourceDocument}
                </span>
              )}
            </div>
            <span className="text-[10px] text-brand-slate font-medium block mt-0.5">
              {medication.dose} &bull; Scheduled {medication.time} &bull; {medication.frequency}
            </span>
          </div>
        </div>

        {/* Right: Status Indicator & Log Action */}
        <div className="flex flex-col items-end gap-2 shrink-0">
          <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.75 rounded-full text-[9px] font-bold border uppercase tracking-wider ${getStatusStyles()}`}>
            {getStatusIcon()}
            <span>{medication.status}</span>
          </span>

          {medication.status === 'upcoming' && onMarkAsTaken && (
            <button
              onClick={() => onMarkAsTaken(medication.id)}
              className="text-[10px] font-bold text-white bg-brand-lavender hover:bg-brand-lavender-hover px-3 py-1.5 rounded-lg shadow-xxs transition-all cursor-pointer active:scale-98"
            >
              Mark taken
            </button>
          )}
        </div>
      </div>

      {/* Structured Clinical Analysis Grid (In-Place Details) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 bg-brand-bg/40 border border-brand-slate/10 p-3.5 rounded-xl text-xxs text-brand-plum leading-relaxed font-light">
        {/* 1. Main Purpose / Why Given */}
        <div className="flex flex-col gap-1">
          <span className="font-bold text-brand-plum flex items-center gap-1.5 text-[10px] uppercase tracking-wider">
            <Target className="w-3.5 h-3.5 text-brand-lavender shrink-0" />
            Main Purpose (Why Given)
          </span>
          <p className="text-brand-slate font-light leading-relaxed">
            {medication.purpose || 'Prescribed for primary symptom and disease management.'}
          </p>
        </div>

        {/* 2. Mode of Intake */}
        <div className="flex flex-col gap-1">
          <span className="font-bold text-brand-plum flex items-center gap-1.5 text-[10px] uppercase tracking-wider">
            <Activity className="w-3.5 h-3.5 text-brand-sage-text shrink-0" />
            Mode of Intake & Administration
          </span>
          <p className="text-brand-slate font-light leading-relaxed">
            {medication.modeOfIntake || medication.instructions}
          </p>
        </div>

        {/* 3. Regimen & Replacement Notes */}
        <div className="flex flex-col gap-1">
          <span className="font-bold text-brand-plum flex items-center gap-1.5 text-[10px] uppercase tracking-wider">
            <RefreshCw className="w-3.5 h-3.5 text-brand-amber-text shrink-0" />
            Regimen & Replacement Status
          </span>
          <p className="text-brand-slate font-light leading-relaxed">
            {medication.replacementNotes || 'Active therapy maintained from uploaded prescription records.'}
          </p>
        </div>
      </div>

      {/* Treatment Timeline & Next Scheduled Dose */}
      {showDetails && (
        <div className="border-t border-brand-slate/5 pt-3 grid grid-cols-2 gap-4 text-xxs text-brand-slate leading-relaxed font-light">
          <div>
            <span className="font-bold text-brand-plum block mb-0.5">Treatment Course</span>
            <span className="flex items-center gap-1 mt-0.5">
              <CalendarRange className="w-3.5 h-3.5 text-brand-slate/60 shrink-0" />
              Started {medication.startDate} &bull; {medication.duration}
            </span>
          </div>
          <div>
            <span className="font-bold text-brand-plum block mb-0.5">Next Scheduled Dose</span>
            <span className="flex items-center gap-1 mt-0.5">
              <Clock className="w-3.5 h-3.5 text-brand-slate/60 shrink-0" />
              {medication.nextDose}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
