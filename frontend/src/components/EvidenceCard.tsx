import React, { useState } from 'react';
import { ChevronDown, FileText, CheckCircle, Brain, Info } from 'lucide-react';

export interface EvidenceSource {
  title: string;
  relevance: string;
}

interface EvidenceCardProps {
  recommendation: string;
  confidence: number;
  reasons: string[];
  patientInfo: string[];
  sources: EvidenceSource[];
}

export default function EvidenceCard({ 
  recommendation, 
  confidence, 
  reasons, 
  patientInfo, 
  sources 
}: EvidenceCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-brand-card border border-brand-slate/10 rounded-2xl p-5 md:p-6 shadow-xs flex flex-col gap-4 transition-all">
      {/* Header Info */}
      <div className="flex items-center justify-between border-b border-brand-slate/5 pb-3">
        <div>
          <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider block">Recommended Specialist</span>
          <h3 className="font-display font-extrabold text-md md:text-lg text-brand-plum mt-0.5">{recommendation}</h3>
        </div>
        <div className="text-right">
          <span className="text-[10px] font-bold text-brand-slate uppercase block">Match Confidence</span>
          <span className="text-xs font-bold text-brand-sage-text bg-brand-sage-bg border border-brand-sage-text/10 px-2.5 py-0.75 rounded-full mt-1.5 inline-block">
            {confidence}%
          </span>
        </div>
      </div>

      {/* Suggested checklist */}
      <div>
        <h4 className="text-xs font-bold text-brand-plum mb-2.5 uppercase tracking-wide">Why CarePath Suggested This</h4>
        <ul className="flex flex-col gap-2">
          {reasons.map((reason, index) => (
            <li key={index} className="flex items-start gap-2.5 text-xs text-brand-plum font-light leading-relaxed">
              <CheckCircle className="w-4 h-4 text-brand-sage-text shrink-0 mt-0.5" />
              <span>{reason}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Expandable Why am I seeing this? */}
      <div className="border-t border-brand-slate/5 pt-3">
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center justify-between w-full text-xs font-semibold text-brand-lavender hover:text-brand-lavender-hover transition-all cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-brand-lavender rounded-lg px-1 py-0.5"
        >
          <span className="flex items-center gap-1.5">
            <Info className="w-3.5 h-3.5" />
            Why am I seeing this?
          </span>
          <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`} />
        </button>

        {expanded && (
          <div className="mt-3.5 flex flex-col gap-4 bg-brand-bg/50 p-4 rounded-xl border border-brand-slate/10 animate-in fade-in slide-in-from-top-1 duration-200">
            {/* Patient Information Section */}
            <div>
              <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider block mb-1.5">Your Patient Profile Parameters</span>
              <ul className="list-disc pl-4 text-[11px] text-brand-plum font-light flex flex-col gap-1">
                {patientInfo.map((info, idx) => (
                  <li key={idx} className="leading-relaxed">{info}</li>
                ))}
              </ul>
            </div>

            {/* AI Interpretation (Clearly demarcated from diagnose) */}
            <div className="bg-brand-lavender-light/35 border-l-2 border-brand-lavender p-3.5 rounded-r-xl flex gap-2">
              <Brain className="w-4 h-4 text-brand-lavender shrink-0 mt-0.5" />
              <div>
                <span className="text-[10px] font-bold text-brand-lavender uppercase tracking-wider block mb-0.5">CarePath Interpretation</span>
                <p className="text-[11px] text-brand-plum font-light leading-relaxed">
                  CarePath noticed potentially relevant correlations within your symptoms and medical documents. This is a navigation guideline. Consider discussing this with your doctor to establish an official diagnosis and treatment plan.
                </p>
              </div>
            </div>

            {/* Evidence Sources */}
            <div>
              <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider block mb-2">Clinical Evidence Sources & Relevance</span>
              <div className="flex flex-col gap-3">
                {sources.map((src, index) => (
                  <div key={index} className="flex gap-2.5 items-start">
                    <FileText className="w-4 h-4 text-brand-slate shrink-0 mt-0.5" />
                    <div>
                      <span className="text-xxs font-bold text-brand-plum block leading-tight">{src.title}</span>
                      <span className="text-[10px] text-brand-slate font-light leading-relaxed mt-0.5 block">{src.relevance}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
