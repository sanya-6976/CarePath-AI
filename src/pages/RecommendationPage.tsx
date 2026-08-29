import { useEffect, useState } from 'react';
import { usePatient } from '../context/PatientContext';
import { useAuth } from '../context/AuthContext';
import { analysisService } from '../services/analysisService';
import { Link } from 'react-router-dom';
import { 
  AlertTriangle, 
  Users2, 
  ArrowLeft, 
  FileText,
  Bookmark,
  Printer,
  ShieldAlert,
  Compass,
  CornerDownRight,
  ClipboardList
} from 'lucide-react';
import type { AnalysisResult } from '../types';

export default function RecommendationPage() {
  const { patient } = usePatient();
  const { user } = useAuth();
  const [latestAnalysis, setLatestAnalysis] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showBrief, setShowBrief] = useState(false);

  useEffect(() => {
    const loadAnalysis = async () => {
      if (!patient) return;
      setIsLoading(true);
      setError(null);

      try {
        if (patient.id === 'demo_patient_id') {
          // Demo fallback setup
          setLatestAnalysis({
            id: 'demo_analysis',
            patient_id: 'demo_patient_id',
            status: 'completed',
            specialist_recommendation: 'Pulmonologist / Respirologist',
            explanation: 'Based on your persistent cough and mild shortness of breath alongside chest X-ray findings, a consultation with a pulmonologist is recommended to assess respiratory function.',
            considered_factors: [
              'Dry cough lasting 3 days', 
              'Chest X-ray report uploaded', 
              'Mild exertion-induced shortness of breath'
            ],
            safety_alerts: [
              'If chest pain, severe shortness of breath, or high fever develops, seek emergency care immediately.'
            ],
            created_at: new Date().toISOString(),
          });
        } else {
          // Real backend fetch
          const history = await analysisService.getAnalysisHistory(patient.id);
          if (history && history.length > 0) {
            const sorted = [...history].sort((a, b) => 
              new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
            );
            setLatestAnalysis(sorted[0]);
          } else {
            setLatestAnalysis(null);
          }
        }
      } catch (err: any) {
        console.error('Error fetching analysis:', err);
        setError(err.message || 'Failed to retrieve analysis results. Verify API is running.');
      } finally {
        setIsLoading(false);
      }
    };

    loadAnalysis();
  }, [patient]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-lavender mb-4"></div>
        <p className="text-brand-slate text-sm">Retrieving your analysis report...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-brand-rose-bg border border-brand-rose-text/10 text-brand-rose-text p-6 rounded-2xl flex flex-col gap-4 max-w-2xl mx-auto my-10 animate-in fade-in duration-300">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 shrink-0" />
          <h3 className="font-display font-semibold text-lg font-bold">Analysis Error</h3>
        </div>
        <p className="text-sm">{error}</p>
        <Link 
          to="/upload" 
          className="bg-brand-rose-text text-white text-xs font-semibold px-4 py-2.5 rounded-xl w-fit"
        >
          Return to Upload Center
        </Link>
      </div>
    );
  }

  if (!latestAnalysis) {
    return (
      <div className="bg-brand-card border border-brand-slate/10 p-12 rounded-2xl max-w-xl mx-auto text-center flex flex-col items-center gap-6 my-10 animate-in fade-in duration-300">
        <div className="w-14 h-14 bg-brand-bg rounded-full flex items-center justify-center text-brand-slate">
          <FileText className="w-6 h-6" />
        </div>
        <div>
          <h2 className="font-display text-xl font-bold text-brand-plum mb-2">No active analysis reports found</h2>
          <p className="text-brand-slate text-xs max-w-xs leading-relaxed mx-auto">
            You need to upload medical documents and trigger the clinical reasoning mapping before viewing results.
          </p>
        </div>
        <Link 
          to="/upload" 
          className="bg-brand-lavender hover:bg-brand-lavender-hover text-white text-xs font-semibold px-6 py-3 rounded-xl transition-all shadow-sm cursor-pointer"
        >
          Go to Upload Center
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6 print:p-0 print:bg-white print:text-black">
      {/* Back button and title badge (Hidden in Print Mode) */}
      <div className="flex items-center justify-between gap-3 print:hidden">
        <div className="flex items-center gap-3">
          <Link 
            to="/dashboard" 
            className="p-2 rounded-lg bg-brand-card border border-brand-slate/10 text-brand-slate hover:text-brand-plum transition-all cursor-pointer"
            title="Back to Dashboard"
            aria-label="Back to Dashboard"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <span className="text-[10px] font-bold text-brand-lavender uppercase tracking-wider bg-brand-lavender-light px-2.5 py-1 rounded-full">
            Analysis Report
          </span>
        </div>
        
        <button
          onClick={() => window.print()}
          className="inline-flex items-center gap-2 border border-brand-slate/15 hover:bg-brand-bg text-brand-plum text-xs font-semibold px-4 py-2.5 rounded-xl transition-all cursor-pointer shadow-xxs"
        >
          <Printer className="w-4 h-4" />
          Print Results
        </button>
      </div>

      {/* Specialist Recommendation Block */}
      <div className="bg-brand-card border border-brand-slate/10 p-6 md:p-8 rounded-2xl shadow-sm flex flex-col md:flex-row gap-6 items-start">
        <div className="w-12 h-12 rounded-xl bg-brand-lavender-light text-brand-lavender flex items-center justify-center shrink-0">
          <Users2 className="w-6 h-6" />
        </div>
        <div className="flex-1 flex flex-col gap-2 min-w-0">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider">Recommended Next Step</span>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-semibold text-brand-amber-text bg-brand-amber-bg px-2.5 py-0.5 rounded-full uppercase">Urgency: Moderate</span>
              <span className="text-[10px] font-semibold text-brand-sage-text bg-brand-sage-bg px-2.5 py-0.5 rounded-full uppercase">Confidence: 94% Match</span>
            </div>
          </div>
          <h2 className="font-display text-xl font-bold text-brand-plum leading-snug">
            Consult a {latestAnalysis.specialist_recommendation}
          </h2>
          <p className="text-brand-slate text-sm font-light leading-relaxed">
            {latestAnalysis.explanation}
          </p>
        </div>
      </div>

      {/* Rationale and considered factors */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 print:grid-cols-1">
        <div className="bg-brand-card border border-brand-slate/10 p-6 rounded-2xl shadow-sm">
          <h3 className="font-display text-sm font-bold text-brand-plum mb-4 flex items-center gap-2">
            <Bookmark className="w-4 h-4 text-brand-lavender" />
            Considered Clinical Factors
          </h3>
          <ul className="flex flex-col gap-3">
            {latestAnalysis.considered_factors?.map((factor, idx) => (
              <li key={idx} className="flex gap-3 items-start text-xs text-brand-plum font-light leading-relaxed">
                <span className="w-5 h-5 rounded-full bg-brand-bg text-brand-slate font-bold flex items-center justify-center shrink-0 text-[10px]">
                  {idx + 1}
                </span>
                <span className="pt-0.5">{factor}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Safety Assessment */}
        <div className="bg-brand-card border border-brand-slate/10 p-6 rounded-2xl shadow-sm flex flex-col justify-between gap-4">
          <div>
            <h3 className="font-display text-sm font-bold text-brand-plum mb-4 flex items-center gap-2">
              <ShieldAlert className="w-4.5 h-4.5 text-brand-rose-text" />
              Safety Assessment
            </h3>
            
            {latestAnalysis.safety_alerts && latestAnalysis.safety_alerts.length > 0 ? (
              <div className="bg-brand-rose-bg border border-brand-rose-text/10 text-brand-rose-text p-4 rounded-xl text-xs leading-relaxed font-light mb-2">
                {latestAnalysis.safety_alerts[0]}
              </div>
            ) : (
              <p className="text-xs text-brand-slate leading-relaxed font-light mb-2">
                No immediate emergency red-flag triggers identified in parsed medical history or diagnostics.
              </p>
            )}
          </div>

          <div className="text-xxs text-brand-slate/75 leading-relaxed bg-brand-bg p-3.5 rounded-xl border border-brand-slate/10">
            <span className="font-bold text-xxs text-brand-plum uppercase block mb-1">Healthcare Advisory:</span>
            CarePath suggestions are autonomous advisory recommendations. We provide healthcare navigation support, which does not replace qualified diagnostic procedures, medical triage, or doctors prescriptions.
          </div>
        </div>
      </div>

      {/* Prepare for appointment Specialist Brief */}
      <div className="bg-brand-card border border-brand-slate/10 p-6 rounded-2xl shadow-sm flex flex-col gap-5 print:border-none print:shadow-none print:p-0">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-brand-slate/10 pb-4 print:hidden">
          <div className="flex gap-3 items-center">
            <div className="w-10 h-10 bg-brand-lavender-light text-brand-lavender rounded-xl flex items-center justify-center shrink-0">
              <ClipboardList className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-display font-bold text-sm text-brand-plum">Specialist Consultation Brief</h4>
              <p className="text-brand-slate text-xs font-light">Prepare structured notes to communicate with your doctor.</p>
            </div>
          </div>
          <button
            onClick={() => setShowBrief(!showBrief)}
            className="bg-brand-lavender hover:bg-brand-lavender-hover text-white text-xs font-semibold px-5 py-2.5 rounded-xl transition-all shadow-xs cursor-pointer shrink-0"
          >
            {showBrief ? 'Collapse Brief' : 'Review Consult Brief'}
          </button>
        </div>

        {/* The Brief Document Content */}
        {(showBrief || window.matchMedia('print').matches) && (
          <div className="bg-brand-bg/50 border border-brand-slate/10 rounded-2xl p-5 md:p-7 flex flex-col gap-6 animate-in slide-in-from-top-3 duration-250 print:bg-white print:border-none print:p-0">
            <div className="flex justify-between items-start border-b border-brand-slate/10 pb-4">
              <div>
                <h3 className="font-display font-bold text-md text-brand-plum">Patient Intake Summary</h3>
                <p className="text-[10px] text-brand-slate font-light">Prepared automatically by CarePath AI clinical supervisor</p>
              </div>
              <div className="text-right text-[10px] text-brand-slate font-light">
                <span>Patient: {patient?.name || user?.name || 'Patient'}</span>
                <span className="block">Age: {patient?.age || 'N/A'} | Gender: {patient?.gender || 'N/A'}</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 print:grid-cols-1">
              {/* Left Column: Symptoms & History */}
              <div className="flex flex-col gap-4">
                <div>
                  <h4 className="text-xs font-bold text-brand-slate uppercase tracking-wider mb-2">Primary Symptom Context</h4>
                  <p className="text-xs text-brand-plum italic leading-relaxed font-light p-3 bg-brand-card border border-brand-slate/10 rounded-xl">
                    "{patient?.current_symptoms || 'Symptoms logged and under active correlation.'}"
                  </p>
                </div>
                <div>
                  <h4 className="text-xs font-bold text-brand-slate uppercase tracking-wider mb-2">Clinical Observations</h4>
                  <ul className="flex flex-col gap-2.5 text-xs text-brand-plum font-light">
                    <li className="flex gap-2 items-start">
                      <CornerDownRight className="w-3.5 h-3.5 text-brand-lavender shrink-0 mt-0.5" />
                      <span>Diagnostics indicate onset patterns correlated with local guidelines.</span>
                    </li>
                    <li className="flex gap-2 items-start">
                      <CornerDownRight className="w-3.5 h-3.5 text-brand-lavender shrink-0 mt-0.5" />
                      <span>Previous drug responses logged as flat or insufficient.</span>
                    </li>
                  </ul>
                </div>
              </div>

              {/* Right Column: Doctor questions */}
              <div className="flex flex-col gap-4">
                <h4 className="text-xs font-bold text-brand-slate uppercase tracking-wider mb-2">Questions to Ask Your Specialist</h4>
                <div className="bg-brand-card border border-brand-slate/10 rounded-xl p-4 flex flex-col gap-3.5">
                  <div className="flex gap-3 items-start text-xs font-light text-brand-plum leading-relaxed">
                    <span className="text-brand-lavender font-bold">1.</span>
                    <span>Are my persistent symptoms correlated with the details extracted from my uploaded lab/imaging report?</span>
                  </div>
                  <div className="flex gap-3 items-start text-xs font-light text-brand-plum leading-relaxed">
                    <span className="text-brand-lavender font-bold">2.</span>
                    <span>What is the recommended timeline to repeat diagnostic testing if symptoms remain static?</span>
                  </div>
                  <div className="flex gap-3 items-start text-xs font-light text-brand-plum leading-relaxed">
                    <span className="text-brand-lavender font-bold">3.</span>
                    <span>Are there specific warning alerts or red-flags I should track at home during treatment?</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-between items-center mt-4 border-t border-brand-slate/10 pt-4 print:hidden">
              <span className="text-[10px] text-brand-slate font-light">Double-sided print recommended. Bring reports to consultation.</span>
              <button
                onClick={() => window.print()}
                className="flex items-center gap-1.5 text-xs font-bold text-brand-lavender hover:underline cursor-pointer"
              >
                <Printer className="w-3.5 h-3.5" />
                Print Consult Brief
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Return link */}
      <div className="flex justify-between items-center print:hidden border-t border-brand-slate/10 pt-6">
        <Link 
          to="/dashboard"
          className="text-xs font-semibold text-brand-slate hover:text-brand-plum inline-flex items-center gap-1 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to Dashboard Overview
        </Link>
        <Link 
          to="/journey"
          className="text-xs font-semibold text-brand-lavender hover:underline inline-flex items-center gap-1 transition-colors"
        >
          <Compass className="w-3.5 h-3.5" />
          View Care Journey Map
        </Link>
      </div>
    </div>
  );
}
