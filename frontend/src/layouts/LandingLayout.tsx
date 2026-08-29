import { Outlet, Link } from 'react-router-dom';
import { Heart } from 'lucide-react';

export default function LandingLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-brand-bg font-sans">
      {/* Top Header */}
      <header className="sticky top-0 z-40 bg-brand-bg/85 backdrop-blur-md border-b border-brand-slate/10 px-6 py-4 transition-all">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-brand-lavender flex items-center justify-center text-white transition-transform group-hover:scale-105">
              <Heart className="w-5 h-5 fill-current" />
            </div>
            <div>
              <span className="font-display font-bold text-xl tracking-tight text-brand-plum">CarePath</span>
              <span className="text-brand-lavender font-bold text-sm ml-0.5">AI</span>
            </div>
          </Link>

          <nav className="flex items-center gap-6">
            <Link 
              to="/login" 
              className="text-brand-slate hover:text-brand-plum font-medium text-sm transition-colors"
            >
              Sign In
            </Link>
            <Link 
              to="/signup" 
              className="bg-brand-lavender hover:bg-brand-lavender-hover text-white px-4 py-2 rounded-xl text-sm font-semibold shadow-sm transition-all hover:-translate-y-0.5"
            >
              Start Your Journey
            </Link>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col justify-start items-center">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-brand-plum text-white/60 py-12 px-6 border-t border-brand-plum/10">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <Heart className="w-4 h-4 text-brand-lavender-light fill-current" />
            <span className="font-display font-medium text-white">CarePath AI</span>
            <span className="text-xs">© {new Date().getFullYear()}</span>
          </div>
          <div className="text-xs text-center md:text-right max-w-md">
            CarePath AI is a healthcare navigation system. We do not diagnose, treat, or replace professional medical advice.
          </div>
        </div>
      </footer>
    </div>
  );
}
