import React, { useState } from 'react';
import { 
  FileText, 
  Brain, 
  BookOpen, 
  Activity, 
  Stethoscope, 
  CalendarClock,
  ArrowRight,
  Info,
  ChevronRight
} from 'lucide-react';
import { Link } from 'react-router-dom';

const JOURNEY_STAGES = [
  {
    id: '01',
    title: 'Information provided',
    icon: <FileText className="w-5 h-5" />,
    what_happened: 'CarePath Intake gathered your medical history, current symptoms, and extracted findings from uploaded medical documents or images.',
    why_needed: 'Accurate clinical data is the foundation of any diagnosis. By structuring unstructured data, the AI can cross-reference your exact symptoms.',
    info_used: ['Patient-reported symptoms', 'Uploaded Medical Records', 'Historical timeline'],
    produced: 'A structured clinical payload containing your chief complaint and existing conditions.',
    link: '/upload',
    linkLabel: 'View Uploads'
  },
  {
    id: '02',
    title: 'AI analysis',
    icon: <Brain className="w-5 h-5" />,
    what_happened: 'Multi-agent orchestration routed your data to specialized AI models. Vision analyzed images, while Medical Docs NLP processed text.',
    why_needed: 'Specialized models are more accurate than generalists. The Vision model focuses solely on finding radiological anomalies.',
    info_used: ['Images', 'PDF Reports', 'Clinical Notes'],
    produced: 'Extracted findings (e.g., specific lung opacities, abnormal lab ranges).',
    link: '/analysis/processing',
    linkLabel: 'View Agent Activity'
  },
  {
    id: '03',
    title: 'Evidence reviewed',
    icon: <BookOpen className="w-5 h-5" />,
    what_happened: 'The Evidence Agent retrieved peer-reviewed medical guidelines matching your exact symptom profile.',
    why_needed: 'To ensure the AI does not hallucinate, it must ground its reasoning in real medical literature and standard-of-care pathways.',
    info_used: ['Structured clinical payload', 'Medical vector database'],
    produced: 'A localized context window containing relevant clinical protocols.',
    link: '/records',
    linkLabel: 'View Knowledge Base'
  },
  {
    id: '04',
    title: 'Clinical reasoning',
    icon: <Activity className="w-5 h-5" />,
    what_happened: 'Synthesized your data with the retrieved evidence to form a differential hypothesis. Safety checks ensured no immediate emergency.',
    why_needed: 'To translate raw data into a human-understandable clinical explanation and determine the correct specialist pathway.',
    info_used: ['Evidence context', 'AI Analysis findings', 'Safety protocols'],
    produced: 'A clear explanation, severity score, and differential hypothesis.',
    link: '/analysis',
    linkLabel: 'View Analysis Result'
  },
  {
    id: '05',
    title: 'Recommended specialist',
    icon: <Stethoscope className="w-5 h-5" />,
    what_happened: 'The Referral Agent mapped the clinical reasoning output to the most appropriate medical specialty in your network.',
    why_needed: 'Getting you to the right doctor prevents delays in care and ensures you receive specialized treatment for your specific condition.',
    info_used: ['Differential hypothesis', 'Provider directory'],
    produced: 'A specific specialist recommendation (e.g., Pulmonology).',
    link: '/doctor-bridge',
    linkLabel: 'Find a Doctor'
  },
  {
    id: '06',
    title: 'Follow-up',
    icon: <CalendarClock className="w-5 h-5" />,
    what_happened: 'The Care Plan Agent generated non-medical action items and scheduled subsequent timeline check-ins.',
    why_needed: 'To ensure continuous care tracking and prevent patients from being lost in the system after an initial consultation.',
    info_used: ['Specialist recommendation', 'Standard care protocols'],
    produced: 'A personalized care checklist and reminder schedule.',
    link: '/followup',
    linkLabel: 'View Care Plan'
  }
];

export default function CareJourneyPage() {
  const [activeStage, setActiveStage] = useState(JOURNEY_STAGES[0]);

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6 animate-in fade-in duration-300">
      <div className="flex flex-col gap-2 mb-2">
        <span className="text-[10px] font-bold text-brand-lavender uppercase tracking-wider w-fit bg-brand-lavender-light px-2.5 py-1 rounded-full border border-brand-lavender/20">
          Traceability Map
        </span>
        <h1 className="font-display text-3xl font-extrabold text-brand-plum">Your Care Journey</h1>
        <p className="text-sm text-brand-slate max-w-2xl font-medium">
          Understand exactly how CarePath AI processed your information, step by step. Every action is transparent and traceable.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Interactive Flow Diagram */}
        <div className="lg:col-span-5 flex flex-col gap-2">
          {JOURNEY_STAGES.map((stage, idx) => {
            const isActive = activeStage.id === stage.id;
            const isLast = idx === JOURNEY_STAGES.length - 1;
            
            return (
              <div key={stage.id} className="flex flex-col relative group">
                <div 
                  onClick={() => setActiveStage(stage)}
                  className={`flex items-center gap-4 p-4 rounded-2xl border transition-all cursor-pointer relative z-10 ${
                    isActive 
                      ? 'bg-white border-brand-lavender shadow-md ring-1 ring-brand-lavender/20' 
                      : 'bg-brand-card border-brand-slate/10 hover:border-brand-lavender/40 hover:bg-white'
                  }`}
                >
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 transition-colors ${
                    isActive ? 'bg-brand-lavender text-white shadow-sm' : 'bg-brand-bg text-brand-slate'
                  }`}>
                    {stage.icon}
                  </div>
                  
                  <div className="flex-1">
                    <span className="text-[10px] font-bold text-brand-slate/70 uppercase tracking-wider">Stage {stage.id}</span>
                    <h3 className={`font-display font-bold text-base ${isActive ? 'text-brand-plum' : 'text-brand-slate'}`}>
                      {stage.title}
                    </h3>
                  </div>

                  <div className="shrink-0 text-brand-slate">
                    <ChevronRight className={`w-5 h-5 transition-transform ${isActive ? 'translate-x-1 text-brand-lavender' : ''}`} />
                  </div>
                </div>

                {/* Vertical connecting line */}
                {!isLast && (
                  <div className="w-0.5 h-6 bg-brand-slate/15 ml-10 my-1 z-0 relative">
                    {/* Animated pulse if previous step is active (simulating flow) */}
                    {isActive && (
                      <div className="absolute top-0 left-0 w-full h-full bg-brand-lavender animate-[shimmer_1.5s_infinite] origin-top" />
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Dynamic Detail Panel */}
        <div className="lg:col-span-7 lg:sticky lg:top-6">
          <div className="bg-white border border-brand-slate/10 rounded-3xl p-8 shadow-sm flex flex-col gap-8 animate-in slide-in-from-right-4 duration-300 relative overflow-hidden">
            
            {/* Background Accent */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-brand-lavender/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 pointer-events-none" />

            <div className="flex items-center gap-4 relative z-10">
              <div className="w-14 h-14 bg-brand-lavender text-white rounded-2xl flex items-center justify-center shadow-sm">
                {activeStage.icon}
              </div>
              <div>
                <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider">Stage {activeStage.id} Deep Dive</span>
                <h2 className="font-display text-2xl font-extrabold text-brand-plum">{activeStage.title}</h2>
              </div>
            </div>

            <div className="grid gap-6 relative z-10">
              
              <div className="flex flex-col gap-2">
                <h3 className="text-[10px] font-bold text-brand-slate uppercase tracking-wider flex items-center gap-1.5">
                  <Info className="w-3.5 h-3.5" /> What happened?
                </h3>
                <p className="text-sm text-brand-plum font-semibold leading-relaxed bg-brand-bg p-4 rounded-xl border border-brand-slate/5">
                  {activeStage.what_happened}
                </p>
              </div>

              <div className="flex flex-col gap-2">
                <h3 className="text-[10px] font-bold text-brand-slate uppercase tracking-wider">Why was this step needed?</h3>
                <p className="text-sm text-brand-slate font-medium leading-relaxed px-1">
                  {activeStage.why_needed}
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4 border-t border-brand-slate/10">
                <div className="flex flex-col gap-3">
                  <h3 className="text-[10px] font-bold text-brand-slate uppercase tracking-wider">Information Used</h3>
                  <ul className="flex flex-col gap-2">
                    {activeStage.info_used.map((info, i) => (
                      <li key={i} className="flex items-start gap-2 text-xs font-semibold text-brand-plum">
                        <ArrowRight className="w-3.5 h-3.5 text-brand-slate shrink-0 mt-0.5" />
                        {info}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="flex flex-col gap-3">
                  <h3 className="text-[10px] font-bold text-brand-lavender uppercase tracking-wider">What was produced?</h3>
                  <div className="bg-brand-lavender-light/30 border border-brand-lavender/20 p-4 rounded-xl text-xs font-bold text-brand-plum leading-relaxed h-full">
                    {activeStage.produced}
                  </div>
                </div>
              </div>

            </div>

            <div className="mt-4 pt-6 border-t border-brand-slate/10 relative z-10 flex justify-end">
              <Link 
                to={activeStage.link}
                className="bg-brand-lavender hover:bg-brand-lavender-hover text-white text-sm font-semibold px-6 py-3 rounded-xl transition-all shadow-sm flex items-center gap-2"
              >
                {activeStage.linkLabel}
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}
