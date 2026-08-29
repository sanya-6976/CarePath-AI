import { UserCheck } from 'lucide-react';

export default function OnboardingPage() {
  return (
    <div className="max-w-3xl mx-auto bg-brand-card border border-brand-slate/10 p-6 md:p-8 rounded-2xl shadow-sm text-center flex flex-col items-center gap-6 my-6 animate-in fade-in duration-300">
      <div className="w-12 h-12 bg-brand-lavender-light text-brand-lavender rounded-xl flex items-center justify-center">
        <UserCheck className="w-6 h-6" />
      </div>
      <div>
        <h2 className="font-display text-lg font-bold text-brand-plum mb-2">Onboarding</h2>
        <p className="text-brand-slate text-sm max-w-xs leading-relaxed mx-auto font-light">
          Your onboarding progress and account personalization setup can be reviewed here.
        </p>
      </div>
    </div>
  );
}
