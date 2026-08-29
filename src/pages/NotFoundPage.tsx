
import { Link } from 'react-router-dom';
import { HelpCircle, ArrowLeft } from 'lucide-react';

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-brand-bg flex flex-col items-center justify-center p-6 text-center font-sans">
      <div className="w-16 h-16 bg-brand-lavender-light text-brand-lavender rounded-2xl flex items-center justify-center mb-6">
        <HelpCircle className="w-8 h-8" />
      </div>
      <h1 className="font-display text-4xl font-bold text-brand-plum mb-3">Page Not Found</h1>
      <p className="text-brand-slate text-sm max-w-sm mb-8 leading-relaxed">
        The step or path you are looking for in this healthcare journey doesn't exist or has moved.
      </p>
      <Link 
        to="/" 
        className="inline-flex items-center gap-2 bg-brand-lavender hover:bg-brand-lavender-hover text-white text-sm font-semibold px-6 py-3 rounded-xl transition-all shadow-sm"
      >
        <ArrowLeft className="w-4 h-4" />
        Return to Safety
      </Link>
    </div>
  );
}
