import React, { useEffect, useState } from 'react';
import { usePatient } from '../context/PatientContext';
import { followupService } from '../services/followupService';
import { Link } from 'react-router-dom';
import { 
  CheckCircle, 
  AlertCircle, 
  PlusCircle, 
  Activity,
  FileCheck,
  TrendingUp,
  ShieldAlert,
  ChevronRight
} from 'lucide-react';
import type { FollowUp } from '../types';

export default function FollowUpPage() {
  const { patient } = usePatient();
  const [followups, setFollowups] = useState<FollowUp[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // New check-in form state
  const [symptomsLogged, setSymptomsLogged] = useState('');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const fetchFollowups = async () => {
    if (!patient) return;
    setIsLoading(true);
    setError(null);
    try {
      if (patient.id === 'demo_patient_id') {
        setFollowups([
          {
            id: '1',
            patient_id: 'demo_patient_id',
            check_in_date: new Date(Date.now() - 86400000 * 3).toISOString(),
            status: 'completed',
            symptoms_logged: 'Dry cough persistent. No shortness of breath.',
            notes: 'Resting well, using inhaler occasionally.',
            created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
          },
          {
            id: '2',
            patient_id: 'demo_patient_id',
            check_in_date: new Date().toISOString(),
            status: 'completed',
            symptoms_logged: 'Cough improved. Felt slight shortness of breath after climbing stairs.',
            notes: 'Scheduled Pulmonology appointment for next week.',
            created_at: new Date().toISOString(),
          }
        ]);
      } else {
        const data = await followupService.getFollowUps(patient.id);
        const sorted = [...data].sort((a, b) => 
          new Date(b.check_in_date).getTime() - new Date(a.check_in_date).getTime()
        );
        setFollowups(sorted);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to fetch follow-ups. Ensure local API is active.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchFollowups();
  }, [patient]);

  const handleSubmitCheckin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!patient || !symptomsLogged) return;
    setIsSubmitting(true);
    setSuccessMsg(null);

    const payload = {
      patient_id: patient.id,
      check_in_date: new Date().toISOString(),
      symptoms_logged: symptomsLogged,
      notes: notes,
      status: 'completed' as const
    };

    try {
      if (patient.id === 'demo_patient_id') {
        const newLog: FollowUp = {
          id: String(followups.length + 1),
          created_at: new Date().toISOString(),
          ...payload
        };
        setFollowups(prev => [newLog, ...prev]);
      } else {
        await followupService.createFollowUp(payload);
        await fetchFollowups();
      }
      setSymptomsLogged('');
      setNotes('');
      setSuccessMsg('Check-in logged successfully.');
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      console.error(err);
      alert(err.message || 'Failed to submit follow-up check-in.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Automated Escalation Risk Detection
  const hasPersistentSymptoms = followups.some(f => 
    f.symptoms_logged?.toLowerCase().includes('persistent') || 
    f.symptoms_logged?.toLowerCase().includes('no improvement') || 
    f.symptoms_logged?.toLowerCase().includes('worse')
  );

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      
      {/* Alert Messaging */}
      {successMsg && (
        <div className="bg-brand-sage-bg border border-brand-sage-text/10 text-brand-sage-text p-4 rounded-xl text-xs flex items-center gap-2 animate-in fade-in duration-300">
          <CheckCircle className="w-5 h-5 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {error && (
        <div className="bg-brand-rose-bg border border-brand-rose-text/10 text-brand-rose-text p-4 rounded-xl text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
          <button onClick={fetchFollowups} className="text-xs font-bold underline cursor-pointer">Retry</button>
        </div>
      )}

      {/* Escalation Prompt */}
      {hasPersistentSymptoms && (
        <div className="bg-brand-amber-bg border border-brand-amber-text/15 text-brand-amber-text p-4.5 rounded-2xl flex items-start gap-3.5 text-xs leading-relaxed animate-in slide-in-from-top-4 duration-300 shadow-xxs">
          <ShieldAlert className="w-5 h-5 text-brand-amber-text shrink-0 mt-0.5 animate-pulse" />
          <div className="flex-1">
            <span className="font-bold">Escalation Recommendation: </span>
            Symptom progression ledger notes limited recovery response or persistent cough/tightness patterns. We advise reviewing your Specialist Brief and completing your recommended specialist referral consultation.
            <div className="mt-2.5">
              <Link 
                to="/analysis"
                className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-brand-lavender bg-brand-lavender-light hover:bg-brand-lavender/10 px-3 py-1.5 rounded-lg transition-all"
              >
                Go to Specialist Referrals
                <ChevronRight className="w-3 h-3" />
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Checkpoints Visualizer Header */}
      <div className="bg-brand-card border border-brand-slate/10 p-5 rounded-2xl shadow-sm">
        <h3 className="font-display text-xs font-bold tracking-wider text-brand-slate uppercase mb-4 flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-brand-lavender" />
          Recovery Milestones
        </h3>
        
        {/* Recovery Journey Ribbon checkpoints */}
        <div className="flex items-center justify-between gap-2 max-w-xl">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-brand-sage-bg text-brand-sage-text flex items-center justify-center text-[10px] font-bold border border-brand-sage-text/15">✓</div>
            <span className="text-xs text-brand-slate">Treatment Start</span>
          </div>
          <div className="h-px bg-brand-slate/20 flex-1" />
          <div className="flex items-center gap-2">
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold border ${followups.length > 0 ? 'bg-brand-sage-bg text-brand-sage-text border-brand-sage-text/15' : 'bg-brand-bg text-brand-slate border-brand-slate/20'}`}>{followups.length > 0 ? '✓' : '2'}</div>
            <span className="text-xs text-brand-slate">Day 3 Check</span>
          </div>
          <div className="h-px bg-brand-slate/20 flex-1" />
          <div className="flex items-center gap-2">
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold border ${followups.length > 1 ? 'bg-brand-sage-bg text-brand-sage-text border-brand-sage-text/15' : 'bg-brand-bg text-brand-slate border-brand-slate/20'}`}>{followups.length > 1 ? '✓' : '3'}</div>
            <span className="text-xs text-brand-slate">Day 7 Check</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Form panel */}
        <div className="bg-brand-card border border-brand-slate/10 p-6 rounded-2xl shadow-sm md:col-span-1 h-fit">
          <h3 className="font-display font-semibold text-sm text-brand-plum mb-4 flex items-center gap-2">
            <PlusCircle className="w-4 h-4 text-brand-lavender" />
            How are you doing?
          </h3>

          <form onSubmit={handleSubmitCheckin} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
              <label className="text-xxs font-semibold text-brand-slate">Active Symptoms Today</label>
              <textarea
                rows={3}
                placeholder="Log cough, breathing, congestion, fatigue..."
                value={symptomsLogged}
                onChange={(e) => setSymptomsLogged(e.target.value)}
                className="w-full bg-brand-bg border border-brand-slate/15 rounded-xl px-3 py-2.5 text-xs focus:border-brand-lavender focus:ring-1 focus:ring-brand-lavender outline-none resize-none transition-all font-light"
                required
              />
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-xxs font-semibold text-brand-slate">Notes / Updates</label>
              <textarea
                rows={3}
                placeholder="e.g. Appointment scheduled, rested well, inhaler doses..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full bg-brand-bg border border-brand-slate/15 rounded-xl px-3 py-2.5 text-xs focus:border-brand-lavender focus:ring-1 focus:ring-brand-lavender outline-none resize-none transition-all font-light"
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="bg-brand-lavender hover:bg-brand-lavender-hover text-white text-xs font-semibold py-2.5 rounded-xl transition-all shadow-sm flex items-center justify-center cursor-pointer"
            >
              Submit Check-in
            </button>
          </form>
        </div>

        {/* History panel */}
        <div className="bg-brand-card border border-brand-slate/10 p-6 rounded-2xl shadow-sm md:col-span-2">
          <h3 className="font-display font-semibold text-sm text-brand-plum mb-6 flex items-center gap-2">
            <Activity className="w-4 h-4 text-brand-lavender" />
            Follow-up History Logs
          </h3>

          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-lavender"></div>
            </div>
          ) : followups.length === 0 ? (
            <div className="text-center py-10 flex flex-col items-center gap-3">
              <FileCheck className="w-8 h-8 text-brand-slate/40" />
              <p className="text-xs text-brand-slate font-light">No check-ins logged yet. Keep your path updated.</p>
            </div>
          ) : (
            <div className="flex flex-col gap-5">
              {followups.map((log) => (
                <div key={log.id} className="border-b border-brand-slate/10 pb-4 last:border-0 last:pb-0">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xxs font-bold text-brand-sage-text bg-brand-sage-bg px-2.5 py-0.5 rounded-full">
                      Logged Check-in
                    </span>
                    <span className="text-xxs text-brand-slate/75 font-light">
                      {new Date(log.check_in_date).toLocaleDateString(undefined, { 
                        month: 'short', 
                        day: 'numeric',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>

                  <div className="flex flex-col gap-2 pl-1">
                    <div>
                      <span className="text-xxs font-bold text-brand-slate uppercase block">Symptoms Status</span>
                      <p className="text-xs text-brand-plum leading-relaxed font-light mt-0.5">
                        {log.symptoms_logged}
                      </p>
                    </div>

                    {log.notes && (
                      <div>
                        <span className="text-xxs font-bold text-brand-slate uppercase block">Additional Notes</span>
                        <p className="text-xs text-brand-slate leading-relaxed font-light mt-0.5 italic">
                          {log.notes}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
