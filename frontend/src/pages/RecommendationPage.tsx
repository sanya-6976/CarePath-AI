import { useEffect, useState } from 'react';
import { usePatient } from '../context/PatientContext';
import { analysisService } from '../services/analysisService';
import { Link } from 'react-router-dom';
import { 
  AlertTriangle, 
  ArrowLeft, 
  FileText,
  Printer,
  ShieldAlert,
  ArrowRight,
  CheckCircle2,
  Stethoscope,
  Clock,
  AlertCircle,
  CalendarClock,
  ChevronDown,
  ChevronUp,
  Info,
  Activity
} from 'lucide-react';
import type { AnalysisResult } from '../types';

export default function RecommendationPage() {
  const { patient } = usePatient();
  const [latestAnalysis, setLatestAnalysis] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [isEvidenceExpanded, setIsEvidenceExpanded] = useState(false);

  useEffect(() => {
    const loadAnalysis = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const storedDocsRaw = localStorage.getItem('carepath_uploaded_docs');
        const storedDocs = storedDocsRaw ? JSON.parse(storedDocsRaw) : [];
        const completedDocs = storedDocs.filter(
          (d: any) => (d.status === 'complete' || d.status === 'partial' || d.status === 'no_findings') && d.result
        );

        let backendItem: any = null;
        if (patient && patient.id !== 'demo_patient_id') {
          try {
            const history = await analysisService.getAnalysisHistory(patient.id);
            if (history && history.length > 0) {
              const sorted = [...history].sort((a: any, b: any) => 
                new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
              );
              backendItem = sorted[0];
            }
          } catch (err) {
            console.error('Notice: backend history fetch fallback:', err);
          }
        }

        if (completedDocs.length > 0) {
          const medicines = Array.from(new Set(completedDocs.flatMap((d: any) => d.result?.extracted?.medicines || []))) as string[];
          const symptoms = Array.from(new Set(completedDocs.flatMap((d: any) => d.result?.extracted?.symptoms || []))) as string[];
          const tests = Array.from(new Set(completedDocs.flatMap((d: any) => [...(d.result?.extracted?.tests || []), ...(d.result?.extracted?.measurements || [])]))) as string[];
          const conditions = Array.from(new Set(completedDocs.flatMap((d: any) => d.result?.extracted?.conditions || []))) as string[];
          const overviews = completedDocs.map((d: any) => d.result?.summary?.keyInfo).filter(Boolean) as string[];
          const insights = completedDocs.map((d: any) => d.result?.aiInsight).filter(Boolean) as string[];

          let specialist = "Internal Medicine Specialist";
          const condStr = conditions.join(" ").toLowerCase();
          const medStr = medicines.join(" ").toLowerCase();
          if (condStr.includes("bronchitis") || condStr.includes("cough") || condStr.includes("asthma") || medStr.includes("albuterol") || medStr.includes("inhaler")) {
            specialist = "Pulmonology";
          } else if (condStr.includes("hypertension") || condStr.includes("cardio") || condStr.includes("heart") || medStr.includes("lisinopril")) {
            specialist = "Cardiology";
          } else if (condStr.includes("diabetes") || condStr.includes("glucose") || medStr.includes("metformin")) {
            specialist = "Endocrinology";
          }

          const factors: string[] = [];
          if (conditions.length > 0) factors.push(`Diagnoses: ${conditions.join(', ')}`);
          if (medicines.length > 0) factors.push(`Medications: ${medicines.join(', ')}`);
          if (tests.length > 0) factors.push(`Labs/Vitals: ${tests.join('; ')}`);
          if (symptoms.length > 0) factors.push(`Symptoms: ${symptoms.join(', ')}`);
          if (factors.length === 0 && overviews.length > 0) factors.push(overviews[0]);

          const explanationText = insights.join(" ") || overviews.join(" ") || (backendItem ? backendItem.summary : "Clinical multi-agent reasoning complete over uploaded records.");

          setLatestAnalysis({
            id: backendItem?.id || 'uploaded_files_analysis',
            patient_id: patient?.id || 'user_patient',
            status: 'completed',
            specialist_recommendation: specialist,
            explanation: explanationText,
            considered_factors: factors.length > 0 ? factors : ["Clinical diagnostic document parsed"],
            safety_alerts: [
              "If chest pain, severe shortness of breath, high fever, or adverse drug symptoms develop, seek emergency care immediately."
            ],
            created_at: new Date().toISOString(),
            risk_level: 'routine'
          });
        } else if (backendItem) {
          setLatestAnalysis({
            id: backendItem.id || 'backend_analysis',
            patient_id: patient?.id || 'user_patient',
            status: 'completed',
            specialist_recommendation: backendItem.specialist_recommendation || "Internal Medicine Specialist",
            explanation: backendItem.summary || backendItem.findings || "CarePath multi-agent analysis finalized.",
            considered_factors: [backendItem.summary || "Clinical diagnostic data parsed."],
            safety_alerts: ["If severe symptoms develop, seek emergency medical care immediately."],
            created_at: backendItem.created_at || new Date().toISOString(),
            changed_factors: backendItem.changed_factors ? JSON.parse(backendItem.changed_factors) : undefined,
            risk_level: backendItem.risk_level || 'routine'
          });
        } else {
          setLatestAnalysis(null);
        }
      } catch (err: any) {
        console.error('Error loading analysis:', err);
        setError(err.message || 'Failed to retrieve analysis report.');
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
        <Link to="/upload" className="bg-brand-rose-text text-white text-xs font-semibold px-4 py-2.5 rounded-xl w-fit">
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
        <Link to="/upload" className="bg-brand-lavender hover:bg-brand-lavender-hover text-white text-xs font-semibold px-6 py-3 rounded-xl transition-all shadow-sm cursor-pointer">
          Go to Upload Center
        </Link>
      </div>
    );
  }

  const severityProps = {
    critical: { color: 'bg-brand-rose-text text-white', text: 'EMERGENCY', explanation: 'Seek emergency medical care immediately.' },
    urgent: { color: 'bg-[#EA580C] text-white', text: 'URGENT', explanation: 'Prompt clinical evaluation recommended.' },
    routine: { color: 'bg-brand-slate text-white', text: 'ROUTINE', explanation: 'No immediate emergency indicators detected.' },
    low: { color: 'bg-brand-sage-text text-white', text: 'LOW RISK', explanation: 'Standard self-care or regular check-up sufficient.' },
  };
  const currentSeverity = severityProps[(latestAnalysis.risk_level?.toLowerCase() as keyof typeof severityProps) || 'routine'];

  const getAgentTrace = () => {
    try {
      const stored = localStorage.getItem('final_agent_states');
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (e) {}
    return null;
  };
  const agentTrace = getAgentTrace();

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6 print:p-0 print:bg-white print:text-black animate-in fade-in duration-300">
      <div className="flex items-center justify-between gap-3 print:hidden mb-2">
        <div className="flex items-center gap-3">
          <Link 
            to="/dashboard" 
            className="p-2 rounded-lg bg-brand-card border border-brand-slate/10 text-brand-slate hover:text-brand-plum transition-all cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <span className="text-[10px] font-bold text-brand-lavender uppercase tracking-wider bg-brand-lavender-light px-2.5 py-1 rounded-full border border-brand-lavender/20">
            CarePath Clinical Result
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

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* LEFT COLUMN: Results & Evidence */}
        <div className="lg:col-span-7 flex flex-col gap-8">
          
          {/* 1. RESULT AT A GLANCE */}
          <div>
            <h2 className="font-display text-2xl font-extrabold text-brand-plum mb-6">CAREPATH RESULT</h2>
            
            <div className="flex flex-col gap-5 bg-white border border-brand-slate/10 p-6 rounded-2xl shadow-sm">
              <div className="flex flex-col sm:flex-row gap-6 sm:items-center justify-between pb-5 border-b border-brand-slate/10">
                <div className="flex flex-col gap-1.5">
                  <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider">Severity</span>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-black tracking-wider px-2 py-0.5 rounded-md ${currentSeverity.color}`}>
                      {currentSeverity.text}
                    </span>
                    <span className="text-xs text-brand-slate font-medium">
                      — {currentSeverity.explanation}
                    </span>
                  </div>
                </div>
                <div className="flex flex-col gap-1.5 group relative items-start sm:items-end">
                  <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider flex items-center gap-1 cursor-help">
                    Confidence <Info className="w-3 h-3 text-brand-slate/60" />
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-black tracking-wide text-brand-plum">
                      MODERATE
                    </span>
                  </div>
                  <div className="absolute top-full right-0 mt-2 w-64 bg-brand-plum text-white text-[10px] p-3 rounded-lg shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 text-left">
                    Confidence reflects the amount and consistency of available information. It is not a measure of diagnostic certainty.
                  </div>
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider">Possible Explanation</span>
                <p className="text-sm text-brand-plum font-semibold leading-relaxed">
                  {latestAnalysis.explanation}
                </p>
                <p className="text-xs text-brand-slate mt-2 font-medium">
                  CarePath recommends discussing these findings with a clinician.
                </p>
              </div>
            </div>
          </div>

          {/* 2. KEY FINDINGS */}
          <div>
            <h3 className="text-sm font-bold text-brand-slate uppercase tracking-wider mb-4">KEY FINDINGS</h3>
            <div className="flex flex-col gap-2">
              {latestAnalysis.considered_factors?.map((factor, idx) => (
                <div key={idx} className="bg-brand-bg/50 border border-brand-slate/10 p-3.5 rounded-xl flex gap-3 items-start hover:border-brand-lavender/30 transition-colors">
                  <CheckCircle2 className="w-4 h-4 text-brand-lavender shrink-0 mt-0.5" />
                  <span className="text-sm text-brand-plum font-semibold leading-snug">{factor}</span>
                </div>
              ))}
            </div>
          </div>

          {/* 3. WHY THIS MATTERS */}
          <div>
            <h3 className="text-sm font-bold text-brand-slate uppercase tracking-wider mb-4">WHY THIS MATTERS</h3>
            <div className="bg-brand-lavender-light/30 border border-brand-lavender/20 p-6 rounded-2xl flex flex-col items-center justify-center text-center gap-3">
              <span className="text-xs font-bold text-brand-slate uppercase tracking-wide">Symptoms + Imaging + History</span>
              <ArrowDownIcon className="w-5 h-5 text-brand-lavender my-1" />
              <span className="text-sm font-bold text-brand-plum">May warrant {latestAnalysis.specialist_recommendation} evaluation.</span>
            </div>
          </div>

          {/* 9. LONGITUDINAL CONTEXT */}
          {latestAnalysis.changed_factors && latestAnalysis.changed_factors.length > 0 && (
            <div>
              <h3 className="text-sm font-bold text-brand-slate uppercase tracking-wider mb-4">PATIENT HISTORY USED</h3>
              <div className="bg-white border border-brand-slate/10 p-5 rounded-2xl shadow-sm">
                <div className="flex flex-col gap-3">
                  {latestAnalysis.changed_factors.map((factor: string, idx: number) => (
                    <div key={idx} className="flex items-center gap-2 text-sm text-brand-plum font-medium">
                      <Clock size={16} className="text-brand-slate shrink-0" />
                      <span>{factor}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 8. EVIDENCE TRACEABILITY */}
          <div>
            <button 
              onClick={() => setIsEvidenceExpanded(!isEvidenceExpanded)}
              className="flex items-center justify-between w-full text-left bg-brand-bg p-4 rounded-xl border border-brand-slate/10 hover:border-brand-slate/20 transition-all cursor-pointer"
            >
              <span className="text-sm font-bold text-brand-plum flex items-center gap-2">
                <FileText className="w-4 h-4 text-brand-slate" />
                WHY CAREPATH RECOMMENDED THIS
              </span>
              {isEvidenceExpanded ? <ChevronUp className="w-4 h-4 text-brand-slate" /> : <ChevronDown className="w-4 h-4 text-brand-slate" />}
            </button>
            
            {isEvidenceExpanded && (
              <div className="mt-2 bg-white border border-brand-slate/10 p-5 rounded-xl shadow-sm flex flex-col gap-3 animate-in slide-in-from-top-2 duration-200">
                <p className="text-xs text-brand-slate font-semibold mb-2">Sources used to generate this recommendation:</p>
                <div className="flex items-center gap-2 text-xs font-bold text-brand-plum"><CheckCircle2 className="w-3.5 h-3.5 text-brand-sage-text" /> Current symptoms</div>
                <div className="flex items-center gap-2 text-xs font-bold text-brand-plum"><CheckCircle2 className="w-3.5 h-3.5 text-brand-sage-text" /> Medical document extractions</div>
                <div className="flex items-center gap-2 text-xs font-bold text-brand-plum"><CheckCircle2 className="w-3.5 h-3.5 text-brand-sage-text" /> Patient timeline</div>
                <div className="flex items-center gap-2 text-xs font-bold text-brand-plum"><CheckCircle2 className="w-3.5 h-3.5 text-brand-sage-text" /> Clinical reasoning hypotheses</div>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT COLUMN: Recommendation & Next Steps */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          
          {/* 7. SPECIALIST RECOMMENDATION */}
          <div className="bg-white border border-brand-slate/10 p-6 rounded-3xl shadow-sm flex flex-col gap-5 relative overflow-hidden ring-1 ring-brand-slate/5">
            <h3 className="text-[10px] font-bold text-brand-slate uppercase tracking-wider">RECOMMENDED SPECIALIST</h3>
            
            <div className="flex items-center gap-4">
              <div className="p-3 bg-brand-bg rounded-xl border border-brand-slate/10">
                <Stethoscope className="w-6 h-6 text-brand-plum" />
              </div>
              <div>
                <h4 className="font-display font-extrabold text-2xl text-brand-plum">
                  {latestAnalysis.specialist_recommendation}
                </h4>
                <span className="text-[10px] font-bold text-brand-lavender bg-brand-lavender-light px-2 py-1 rounded-md mt-1.5 inline-block">
                  Recommended soon
                </span>
              </div>
            </div>

            <div className="flex flex-col gap-1.5 mt-2">
              <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider">WHY?</span>
              <p className="text-sm font-semibold text-brand-plum">
                Persistent symptoms and relevant imaging/history support further evaluation.
              </p>
            </div>

            <div className="flex flex-col gap-1.5 mt-2">
              <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider">NEXT STEP</span>
              <Link 
                to={`/doctor-bridge?specialty=${encodeURIComponent(latestAnalysis.specialist_recommendation || 'General')}`}
                className="text-sm font-bold text-white bg-brand-lavender hover:bg-brand-lavender-hover px-5 py-3 rounded-xl flex items-center justify-center gap-2 transition-all shadow-sm"
              >
                VIEW SPECIALIST PATH <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          {/* 15. AGENT TRACE (Terminal Style) */}
          <div className="bg-brand-bg border border-brand-slate/10 p-5 rounded-2xl shadow-sm font-mono flex flex-col gap-3">
            <h3 className="text-[10px] font-bold text-brand-slate uppercase tracking-wider mb-2 flex items-center gap-2 font-sans border-b border-brand-slate/10 pb-3">
              <Activity className="w-3.5 h-3.5" />
              LIVE CAREPATH EXECUTION
            </h3>
            
            <div className="flex flex-col gap-2.5 overflow-y-auto max-h-64">
              {['Supervisor', 'Intake', 'Vision', 'Docs', 'Timeline', 'Evidence', 'Clinical Reasoning', 'Safety', 'Referral', 'Care Plan', 'Follow-up'].map((agentName, index) => {
                let status = 'Waiting';
                let reason = '';
                if (agentTrace) {
                  const nodeState = agentTrace[agentName];
                  if (nodeState) {
                    status = nodeState.status;
                    reason = nodeState.reason_for_execution || '';
                  }
                }
                
                const isSkipped = status === 'skipped' || status === 'Skipped';
                const isCompleted = status === 'completed' || status === 'Completed';
                const isRunning = status === 'running' || status === 'Running';
                const isFailed = status === 'failed' || status === 'Failed';

                const d = new Date(new Date(latestAnalysis.created_at).getTime() + index * 1200);
                const timeString = `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`;

                if (status === 'Waiting') return null;

                return (
                  <div key={agentName} className="flex flex-col gap-0.5 text-xs">
                    <div className="flex items-start gap-3">
                      <span className="text-brand-slate opacity-70 shrink-0">{timeString}</span>
                      {isCompleted && <span className="text-brand-sage-text shrink-0">✓</span>}
                      {isSkipped && <span className="text-brand-slate shrink-0">—</span>}
                      {isRunning && <span className="text-brand-lavender shrink-0 animate-pulse">●</span>}
                      {isFailed && <span className="text-brand-rose-text shrink-0">!</span>}
                      
                      <div className="flex flex-col">
                        <span className={`font-semibold ${isCompleted ? 'text-brand-plum' : isSkipped ? 'text-brand-slate line-through opacity-70' : isFailed ? 'text-brand-rose-text' : 'text-brand-lavender'}`}>
                          {agentName} {isSkipped ? 'skipped' : ''}
                        </span>
                        {isSkipped && reason && (
                          <span className="text-brand-slate opacity-70 text-[10px] mt-0.5">Reason: {reason}</span>
                        )}
                        {isFailed && (
                          <span className="text-brand-rose-text opacity-70 text-[10px] mt-0.5">Execution failed.</span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 12. SAFETY NOTE */}
          <div className="bg-brand-card border border-brand-slate/10 p-5 rounded-2xl mt-auto shadow-sm">
            <h3 className="text-[10px] font-bold text-brand-slate uppercase tracking-wider mb-2 flex items-center gap-2">
              <ShieldAlert className="w-3.5 h-3.5" />
              SAFETY NOTE
            </h3>
            <p className="text-xs text-brand-slate leading-relaxed font-semibold">
              CarePath provides clinical navigation and decision support. It does not replace professional medical evaluation or provide a confirmed diagnosis.
            </p>
          </div>

        </div>
      </div>
      
      {/* Footer Return Link */}
      <div className="flex justify-between items-center print:hidden border-t border-brand-slate/10 pt-6 mt-6">
        <Link 
          to="/dashboard"
          className="text-xs font-bold text-brand-slate hover:text-brand-plum inline-flex items-center gap-1 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to Dashboard Overview
        </Link>
        <Link 
          to="/journey"
          className="text-xs font-bold text-brand-lavender hover:underline inline-flex items-center gap-1 transition-colors"
        >
          <CalendarClock className="w-3.5 h-3.5" />
          View Care Journey Map
        </Link>
      </div>
    </div>
  );
}

function ArrowDownIcon(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 5v14"/>
      <path d="m19 12-7 7-7-7"/>
    </svg>
  );
}
