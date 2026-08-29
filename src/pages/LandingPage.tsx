import { Link } from 'react-router-dom';
import { ArrowRight, Activity, Eye, Compass, Users2, RefreshCw, Heart } from 'lucide-react';
import heroBg from '../assets/hero-bg.png';
import SplitText from '../components/SplitText';

export default function LandingPage() {
  const steps = [
    {
      icon: Activity,
      title: 'Symptoms',
      desc: 'Describe what you feel. Log history, onset, and severity of symptoms in natural language.',
      color: 'bg-brand-amber-bg text-brand-amber-text'
    },
    {
      icon: Eye,
      title: 'Understanding',
      desc: 'Upload medical reports, prescriptions, or imaging. CarePath parses raw data and structures it.',
      color: 'bg-brand-lavender-light text-brand-lavender'
    },
    {
      icon: Compass,
      title: 'Care Journey',
      desc: 'See your diagnostic events chronologically mapped out on an interactive, living journey map.',
      color: 'bg-brand-sage-bg text-brand-sage-text'
    },
    {
      icon: Users2,
      title: 'Specialist Recommendation',
      desc: 'Receive evidence-backed guidance on exactly which medical specialty to consult next and why.',
      color: 'bg-brand-lavender-light text-brand-lavender'
    },
    {
      icon: RefreshCw,
      title: 'Follow-up Tracker',
      desc: 'Keep track of clinical check-ins, recovery symptoms, and scheduled consultations over time.',
      color: 'bg-brand-rose-bg text-brand-rose-text'
    }
  ];

  return (
    <div className="w-full flex flex-col items-center animate-in fade-in duration-500">
      {/* 1. FULL-WIDTH HERO BACKGROUND IMAGE SECTION */}
      <div 
        className="w-full text-center flex flex-col items-center justify-between pt-2 md:pt-3 pb-8 md:pb-12 px-6 relative bg-center bg-no-repeat min-h-[70vh] md:min-h-[80vh]"
        style={{ 
          backgroundImage: `url(${heroBg})`,
          backgroundSize: '100% 100%'
        }}
      >
        {/* Radial gradient overlay: centered around the text area, leaving bottom landscape clear */}
        <div 
          className="absolute inset-0 -z-10" 
          style={{
            background: 'radial-gradient(circle at center 18%, rgba(250, 248, 245, 0.92) 0%, rgba(250, 248, 245, 0.65) 55%, rgba(250, 248, 245, 0.1) 100%)'
          }}
        />

        {/* Top/Middle Group: Hero Content */}
        <div className="max-w-3xl flex flex-col items-center mt-0">
          {/* Decorative Badge */}
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-brand-lavender-light text-brand-lavender text-xs font-semibold tracking-wide uppercase mb-5">
            <Heart className="w-3.5 h-3.5 fill-current" />
            Autonomous Healthcare Navigator
          </div>

          <h1 className="font-display font-bold text-5xl md:text-7xl tracking-tight leading-tight mb-5 max-w-3xl">
            <SplitText
              text="Right Guidance."
              className="text-brand-plum inline-block"
              delay={35}
              duration={0.8}
              ease="power3.out"
              splitType="chars"
              tag="span"
            />
            <br />
            <SplitText
              text="Right Specialist."
              className="text-brand-plum inline-block"
              delay={35}
              duration={0.8}
              ease="power3.out"
              splitType="chars"
              tag="span"
            />
            <br />
            <SplitText
              text="Right Time."
              className="text-brand-lavender inline-block"
              delay={35}
              duration={0.8}
              ease="power3.out"
              splitType="chars"
              tag="span"
            />
          </h1>

          <p className="text-brand-slate text-lg md:text-xl font-light leading-relaxed max-w-2xl">
            CarePath AI is an autonomous, multi-agent healthcare navigation system that translates symptoms, reports, and prescriptions into a living map of your recovery.
          </p>
        </div>

        {/* Bottom Group: CTA Buttons inside the Hero image container */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center w-full sm:w-auto mt-12 md:mt-16 z-10">
          <Link
            to="/signup"
            className="flex items-center justify-center gap-2 bg-brand-lavender hover:bg-brand-lavender-hover text-white text-base font-semibold px-8 py-4 rounded-2xl shadow-md hover:-translate-y-0.5 transition-all w-full sm:w-auto group"
          >
            Start Your Care Journey
            <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
          </Link>
          <Link
            to="/login"
            className="flex items-center justify-center bg-brand-card hover:bg-brand-bg text-brand-plum border border-brand-slate/15 text-base font-semibold px-8 py-4 rounded-2xl transition-all w-full sm:w-auto"
          >
            Sign In
          </Link>
        </div>
      </div>

      {/* 2. MAIN CONTENT AREA (BELOW BACKGROUND IMAGE) */}
      <div className="w-full max-w-6xl px-6 flex flex-col items-center mt-16">
        {/* Visual Journey Guide */}
        <div className="w-full mb-24">
          <div className="text-center mb-16">
            <h2 className="font-display text-3xl font-bold text-brand-plum mb-3">How CarePath Maps Your Path</h2>
            <p className="text-brand-slate text-md max-w-lg mx-auto font-light">
              From your first symptom description to final follow-ups, CarePath guides you step-by-step.
            </p>
          </div>

          {/* Step Cards with Connecting Line on Desktop */}
          <div className="relative grid grid-cols-1 md:grid-cols-5 gap-6">
            {/* Connector Line */}
            <div className="hidden md:block absolute top-1/2 left-4 right-4 h-0.5 bg-brand-slate/10 -translate-y-8 -z-10" />

            {steps.map((step, idx) => {
              const Icon = step.icon;
              return (
                <div 
                  key={step.title}
                  className="bg-brand-card border border-brand-slate/10 p-6 rounded-2xl flex flex-col items-center text-center shadow-sm relative group hover:border-brand-lavender/30 transition-all duration-200"
                >
                  <div className="absolute -top-3.5 left-6 bg-brand-plum text-white text-xs font-bold w-7 h-7 rounded-full flex items-center justify-center">
                    {idx + 1}
                  </div>
                  <div className={`w-14 h-14 rounded-2xl ${step.color} flex items-center justify-center mb-5 mt-2`}>
                    <Icon className="w-7 h-7" />
                  </div>
                  <h3 className="font-display font-semibold text-lg text-brand-plum mb-2">{step.title}</h3>
                  <p className="text-brand-slate text-xs leading-relaxed font-light">{step.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Clinical Disclaimer Box */}
        <div className="max-w-3xl w-full bg-brand-card border border-brand-slate/10 p-6 rounded-2xl shadow-sm text-center mb-12">
          <p className="text-brand-slate text-xs font-light leading-relaxed">
            <span className="font-semibold text-brand-plum">Disclaimer:</span> CarePath AI provides navigation, timeline tracking, and educational guidance. It is an agentic advisory tool and does not diagnose disease, write medical prescriptions, or replace human doctors or emergency medical services. Always consult with qualified medical practitioners for diagnostic decisions.
          </p>
        </div>
      </div>
    </div>
  );
}
