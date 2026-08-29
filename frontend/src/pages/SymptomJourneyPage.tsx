import { Activity } from 'lucide-react';

export default function SymptomJourneyPage() {
  return (
    <div className="max-w-3xl mx-auto bg-brand-card border border-brand-slate/10 p-6 md:p-8 rounded-2xl shadow-sm text-center flex flex-col items-center gap-6 my-6 animate-in fade-in duration-300">
      <div className="w-12 h-12 bg-brand-lavender-light text-brand-lavender rounded-xl flex items-center justify-center">
        <Activity className="w-6 h-6" />
      </div>
      <div>
        <h2 className="font-display text-lg font-bold text-brand-plum mb-2">Symptom Log</h2>
        <p className="text-brand-slate text-sm max-w-xs leading-relaxed mx-auto font-light">
          Your active symptom registration wizard and clinical onset timelines will display here.
        </p>
      </div>
    </div>
  );
}
