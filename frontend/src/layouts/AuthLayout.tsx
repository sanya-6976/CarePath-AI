import { Outlet, Link } from 'react-router-dom';
import { Heart } from 'lucide-react';
import loginJourneyBg from '../assets/carepath-login-journey.png';

export default function AuthLayout() {
  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-brand-bg font-sans">
      {/* Left branding pane with healthcare journey illustration */}
      <div 
        className="hidden md:flex md:w-[58%] text-white flex-col justify-between p-12 relative overflow-hidden bg-cover bg-no-repeat border-r border-brand-slate/10"
        style={{ 
          backgroundImage: `url(${loginJourneyBg})`,
          backgroundPosition: 'center center'
        }}
      >
        {/* Darkening gradient overlay to secure typography legibility */}
        <div className="absolute inset-0 bg-gradient-to-r from-brand-plum/90 via-brand-plum/60 to-brand-plum/20 -z-10" />

        {/* Branding Logo (Readable at top-left padding) */}
        <Link to="/" className="flex items-center gap-2.5 group relative z-10">
          <div className="w-10 h-10 rounded-xl bg-brand-lavender flex items-center justify-center text-white transition-transform group-hover:scale-105">
            <Heart className="w-6 h-6 fill-current" />
          </div>
          <div>
            <span className="font-display font-bold text-2xl tracking-tight text-white">CarePath</span>
            <span className="text-brand-lavender-light font-bold text-sm ml-0.5">AI</span>
          </div>
        </Link>

        {/* Emotional visual content group positioned over negative dark space */}
        <div className="max-w-xl mt-[72px] mb-auto relative z-10 flex flex-col gap-[48px] pt-8">
          <h1 className="font-display text-3xl md:text-4xl font-extrabold leading-tight text-white tracking-tight">
            Your healthcare journey,<br />
            <span className="text-brand-lavender-light">clearly mapped.</span>
          </h1>
          <p className="text-white/80 text-sm md:text-base leading-relaxed font-light max-w-[460px]">
            CarePath AI matches symptoms, analyzes medical documents, and charts a personalized, step-by-step path to the right specialist.
          </p>
        </div>

        {/* Regulatory disclaimer in bottom-left */}
        <div className="text-[10px] md:text-xs text-white/50 relative z-10 font-light max-w-sm">
          CarePath AI provides healthcare navigation support. We do not provide medical diagnosis.
        </div>
      </div>

      {/* Right functional form container (42% width on desktop) */}
      <div className="flex-1 md:w-[42%] flex items-center justify-center p-6 md:p-12 bg-brand-bg">
        <div className="w-full max-w-md bg-brand-card rounded-2xl border border-brand-slate/10 p-8 shadow-xs">
          {/* Logo visible only on mobile viewports */}
          <div className="flex md:hidden items-center justify-center gap-2 mb-6">
            <div className="w-9 h-9 rounded-lg bg-brand-lavender flex items-center justify-center text-white">
              <Heart className="w-5 h-5 fill-current" />
            </div>
            <span className="font-display font-bold text-xl text-brand-plum">CarePath AI</span>
          </div>

          {/* Compact Journey Banner visible only on mobile */}
          <div 
            className="block md:hidden w-full h-24 rounded-xl mb-6 bg-cover bg-center relative overflow-hidden border border-brand-slate/10"
            style={{ backgroundImage: `url(${loginJourneyBg})` }}
          >
            <div className="absolute inset-0 bg-brand-plum/50" />
            <div className="absolute inset-0 flex items-center px-4">
              <p className="text-white text-xs font-semibold tracking-tight leading-snug">
                Your healthcare journey, clearly mapped.
              </p>
            </div>
          </div>

          <Outlet />
        </div>
      </div>
    </div>
  );
}
