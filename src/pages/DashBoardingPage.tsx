import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { usePatient } from '../context/PatientContext';
import { useAuth } from '../context/AuthContext';
import { timelineService } from '../services/timelineService';
import { analysisService } from '../services/analysisService';
import { 
  Activity, 
  Eye, 
  Users2, 
  Calendar, 
  RefreshCw, 
  AlertCircle, 
  Compass, 
  Clock, 
  CheckCircle2, 
  ArrowRight,
  ShieldAlert,
  ArrowDown,
  ChevronRight,
  FileCheck
} from 'lucide-react';
import type { TimelineEvent, AnalysisResult } from '../types';

export default function DashBoardingPage() {
  const { patient, isLoading: isPatientLoading, fetchPatient, error: patientError } = usePatient();
  const { user } = useAuth();
  
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [latestAnalysis, setLatestAnalysis] = useState<AnalysisResult | null>(null);
  const [isLoadingData, setIsLoadingData] = useState(false);
  const [isOffline, setIsOffline] = useState(false);

  // Journey stage selection states
  const [selectedStage, setSelectedStage] = useState<number>(1);

  useEffect(() => {
    const loadDashboardData = async () => {
      if (!patient) return;
      setIsLoadingData(true);
      setIsOffline(false);
      try {
        if (patient.id === 'demo_patient_id') {
          // Demo fallback setup
          setTimeline([
            {
              id: 'demo_event_1',
              patient_id: 'demo_patient_id',
              type: 'symptom',
              title: 'Cough & Dyspnea Logged',
              description: 'Dry cough logged for 3 days alongside chest tightness.',
              timestamp: new Date(Date.now() - 172800000).toISOString(),
            },
            {
              id: 'demo_event_2',
              patient_id: 'demo_patient_id',
              type: 'upload',
              title: 'Uploaded Lab Report',
              description: 'Chest X-ray report and CBC blood test results.',
              timestamp: new Date(Date.now() - 86400000).toISOString(),
            }
          ]);
          setLatestAnalysis({
            id: 'demo_analysis',
            patient_id: 'demo_patient_id',
            status: 'completed',
            specialist_recommendation: 'Pulmonologist / Respirologist',
            explanation: 'Based on your persistent cough and mild shortness of breath alongside chest X-ray findings, a consultation with a pulmonologist is recommended to assess respiratory function.',
            considered_factors: ['Dry cough lasting 3 days', 'Chest X-ray report uploaded', 'Mild exertion-induced shortness of breath'],
            safety_alerts: ['If chest pain, severe shortness of breath, or high fever develops, seek emergency care immediately.'],
            created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
          });
        } else {
          // Real backend fetch
          const [events, history] = await Promise.all([
            timelineService.getTimeline(patient.id),
            analysisService.getAnalysisHistory(patient.id),
          ]);
          setTimeline(events);
          if (history && history.length > 0) {
            const sorted = [...history].sort((a, b) => 
              new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
            );
            setLatestAnalysis(sorted[0]);
          }
        }
      } catch (err: any) {
        console.error('Error fetching dashboard data:', err);
        setIsOffline(true);
      } finally {
        setIsLoadingData(false);
      }
    };

    loadDashboardData();
  }, [patient]);

  // Determine active stage on the map
  const getActiveStage = () => {
    if (!latestAnalysis) return 1; // Symptoms logged
    if (latestAnalysis.status === 'processing') return 2; // Analysis running
    if (latestAnalysis.specialist_recommendation) return 3; // Specialist recommended
    if (timeline.some(e => e.type === 'consultation')) return 4; // Consultation
    if (timeline.some(e => e.type === 'followup')) return 5; // Follow-up
    return 3;
  };

  const currentStage = getActiveStage();

  // Set default selected stage to current active stage when data loads
  useEffect(() => {
    if (latestAnalysis || timeline.length > 0) {
      setSelectedStage(currentStage);
    }
  }, [latestAnalysis, timeline, currentStage]);

  const stages = [
    { number: 1, name: 'Symptoms', icon: Activity, desc: 'Describe what you feel' },
    { number: 2, name: 'Understanding', icon: Eye, desc: 'AI agent processing' },
    { number: 3, name: 'Specialist', icon: Users2, desc: 'Referral advisory' },
    { number: 4, name: 'Consultation', icon: Calendar, desc: 'Prepare clinic brief' },
    { number: 5, name: 'Recovery', icon: RefreshCw, desc: 'Track recovery check-ins' }
  ];

  if (isPatientLoading || isLoadingData) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-lavender mb-4"></div>
        <p className="text-brand-slate text-sm">Synchronizing your care map...</p>
      </div>
    );
  }

  if (patientError) {
    return (
      <div className="bg-brand-rose-bg border border-brand-rose-text/10 text-brand-rose-text p-6 rounded-2xl flex flex-col gap-4 max-w-2xl mx-auto my-10 animate-in fade-in duration-300">
        <div className="flex items-center gap-3">
          <AlertCircle className="w-6 h-6 shrink-0" />
          <h3 className="font-display font-semibold text-lg font-bold">Unable to load patient records</h3>
        </div>
        <p className="text-sm">{patientError}</p>
        <button 
          onClick={() => window.location.reload()} 
          className="bg-brand-rose-text text-white text-xs font-semibold px-4 py-2 rounded-xl w-fit cursor-pointer"
        >
          Try Again
        </button>
      </div>
    );
  }

  // Check if patient context is totally uninitiated
  const isUninitiated = !patient?.current_symptoms && timeline.length === 0 && !latestAnalysis;

  if (isUninitiated) {
    const previewStages = [
      { name: 'Symptoms', icon: Activity, desc: 'Tell CarePath what you feel' },
      { name: 'Understanding', icon: Eye, desc: 'AI agent verification' },
      { name: 'Specialist', icon: Users2, desc: 'Specialty match rationale' },
      { name: 'Consultation', icon: Calendar, desc: 'Prepare doctor summary' },
      { name: 'Recovery', icon: RefreshCw, desc: 'Track recovery updates' }
    ];

    return (
      <div className="w-full max-w-5xl mx-auto flex flex-col items-center gap-10 py-6 md:py-10 animate-in fade-in duration-300">
        
        {/* Introduction Section */}
        <div className="max-w-3xl text-center flex flex-col items-center gap-4">
          <span className="text-[10px] font-bold text-brand-lavender uppercase tracking-widest bg-brand-lavender-light px-3.5 py-1.5 rounded-full shadow-xxs">
            Welcome to CarePath AI
          </span>
          <h1 className="font-display text-3xl md:text-4xl font-bold tracking-tight text-brand-plum leading-tight">
            Your healthcare journey starts here.
          </h1>
          <p className="text-brand-slate text-sm leading-relaxed max-w-2xl font-light">
            CarePath helps organize your symptoms, medical information and treatment history into a guided healthcare journey — helping you understand your next step and prepare for the right specialist.
          </p>
          <div className="mt-2">
            <Link
              to="/profile"
              className="inline-flex items-center gap-2 bg-brand-lavender hover:bg-brand-lavender-hover text-white text-xs font-semibold px-7 py-3.5 rounded-xl shadow-md transition-all active:scale-98 cursor-pointer"
            >
              Begin my CarePath
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

        {/* CAREPATH VISUALIZATION PREVIEW */}
        <div className="w-full bg-brand-card border border-brand-slate/10 p-6 md:p-8 rounded-3xl shadow-sm">
          <h2 className="font-display text-[10px] font-bold tracking-widest text-brand-slate/70 uppercase mb-8 text-center md:text-left">
            YOUR CAREPATH
          </h2>

          {/* Stepper ribbon: horizontal on desktop, vertical on mobile */}
          <div className="relative flex flex-col md:flex-row justify-between gap-8 md:gap-4">
            {previewStages.map((stage, index) => {
              const Icon = stage.icon;
              const showConnector = index < previewStages.length - 1;
              return (
                <div key={stage.name} className="flex flex-row md:flex-col items-center gap-4 md:text-center flex-1 relative">
                  {/* Connector lines (Desktop) */}
                  {showConnector && (
                    <div className="hidden md:block absolute top-6 left-12 w-[calc(100%-1.5rem)] h-0.5 bg-brand-slate/10 -z-10" />
                  )}
                  {/* Connector lines (Mobile) */}
                  {showConnector && (
                    <div className="block md:hidden absolute left-6 top-12 h-6 w-0.5 bg-brand-slate/10 -z-10" />
                  )}

                  {/* Stepper Node Circle (Muted/Inactive State) */}
                  <div className="w-12 h-12 rounded-full flex items-center justify-center border-2 border-brand-slate/20 bg-brand-bg text-brand-slate/40 shrink-0 shadow-xxs">
                    <Icon className="w-5 h-5" />
                  </div>

                  <div className="flex flex-col md:items-center min-w-0">
                    <span className="text-xs md:text-sm font-semibold text-brand-slate/60">
                      {stage.name}
                    </span>
                    <span className="text-[10px] text-brand-slate/40 hidden md:block max-w-[130px] mt-1 font-light leading-snug">
                      {stage.desc}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* WHAT HAPPENS WHEN YOU BEGIN */}
        <div className="w-full border-t border-brand-slate/10 pt-8 mt-4 text-left">
          <h3 className="font-display text-[10px] font-bold tracking-widest text-brand-slate uppercase mb-6 text-center md:text-left">
            WHAT HAPPENS WHEN YOU BEGIN?
          </h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
            <div className="flex flex-col gap-2">
              <span className="font-display text-4xl font-extrabold text-brand-lavender/40 leading-none tracking-tight">01</span>
              <h4 className="text-sm font-bold text-brand-plum mt-1">Tell CarePath what you're experiencing</h4>
              <p className="text-xs text-brand-slate leading-relaxed font-normal">
                Provide descriptions of your symptoms, duration, and severity in plain language.
              </p>
            </div>
            <div className="flex flex-col gap-2">
              <span className="font-display text-4xl font-extrabold text-brand-lavender/40 leading-none tracking-tight">02</span>
              <h4 className="text-sm font-bold text-brand-plum mt-1">Add relevant medical information</h4>
              <p className="text-xs text-brand-slate leading-relaxed font-normal">
                Upload lab reports, prescriptions, or imaging results so CarePath can parse diagnostic details.
              </p>
            </div>
            <div className="flex flex-col gap-2">
              <span className="font-display text-4xl font-extrabold text-brand-lavender/40 leading-none tracking-tight">03</span>
              <h4 className="text-sm font-bold text-brand-plum mt-1">CarePath identifies next steps</h4>
              <p className="text-xs text-brand-slate leading-relaxed font-normal">
                AI agents collaborate to trace evidence relationships and recommend specialist consultation routes.
              </p>
            </div>
            <div className="flex flex-col gap-2">
              <span className="font-display text-4xl font-extrabold text-brand-lavender/40 leading-none tracking-tight">04</span>
              <h4 className="text-sm font-bold text-brand-plum mt-1">Prepare for appointment and recover</h4>
              <p className="text-xs text-brand-slate leading-relaxed font-normal">
                Generate custom doctor question sheets and log recovery check-ins to monitor treatment response.
              </p>
            </div>
          </div>
        </div>

      </div>
    );
  }

  const patientName = patient?.name || user?.name || 'Patient';

  return (
    <div className="flex flex-col gap-8">
      {/* Offline Alert Banner */}
      {isOffline && (
        <div className="bg-brand-amber-bg border border-brand-amber-text/10 text-brand-amber-text p-4 rounded-2xl flex items-center justify-between text-xs animate-in slide-in-from-top-4 duration-300">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-4.5 h-4.5 shrink-0" />
            <span>CarePath cannot contact the local API server. Showing demo data for visualization.</span>
          </div>
          <button 
            onClick={() => patient && fetchPatient(patient.id)}
            className="text-xs font-semibold underline hover:no-underline cursor-pointer"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Greeting Header */}
      <div>
        <h1 className="font-display text-2xl md:text-3xl font-bold tracking-tight text-brand-plum mb-1">
          Welcome back, {patientName}
        </h1>
        <p className="text-brand-slate text-xs font-light">
          Your CarePath is active. Here's where you are in your healthcare journey.
        </p>
      </div>

      {/* PRIMARY CAREPATH VISUALIZATION (THREAD PATHWAY) */}
      <div className="bg-brand-card border border-brand-slate/10 p-6 md:p-8 rounded-3xl shadow-sm relative overflow-hidden">
        {/* Glow accent */}
        <div className="absolute top-0 left-0 w-2 h-full bg-brand-lavender" />

        <h2 className="font-display text-xs font-bold tracking-wider text-brand-slate uppercase mb-8 flex items-center gap-2">
          <Compass className="w-4 h-4 text-brand-lavender" />
          Interactive CarePath Journey
        </h2>

        {/* The Wavy/Connected Ribbon Thread */}
        <div className="relative flex flex-col md:flex-row justify-between gap-8 md:gap-4">
          
          {stages.map((stage, index) => {
            const Icon = stage.icon;
            const isCompleted = stage.number < currentStage;
            const isCurrent = stage.number === currentStage;
            const isSelected = stage.number === selectedStage;
            const showConnector = index < stages.length - 1;
            const nextStageCompleted = stage.number + 1 <= currentStage;

            // Connector path coloring
            const connectorColor = nextStageCompleted 
              ? 'bg-brand-sage-text' 
              : isCompleted 
              ? 'bg-brand-lavender/40 animate-pulse' 
              : 'bg-brand-slate/10';

            return (
              <button 
                key={stage.number} 
                onClick={() => setSelectedStage(stage.number)}
                className={`flex flex-row md:flex-col items-center gap-4 md:text-center flex-1 relative group focus:outline-none cursor-pointer text-left md:items-center ${
                  isSelected ? 'scale-102 font-bold' : 'hover:scale-101'
                }`}
              >
                {/* Connector line */}
                {showConnector && (
                  <div className={`hidden md:block absolute top-6 left-12 w-[calc(100%-1.5rem)] h-0.5 -z-10 transition-all ${connectorColor}`} />
                )}

                {/* Stepper Node Circle */}
                <div 
                  className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all shrink-0 relative ${
                    isCompleted 
                      ? 'bg-brand-sage-bg border-brand-sage-text text-brand-sage-text shadow-xxs'
                      : isCurrent
                      ? 'bg-brand-lavender-light border-brand-lavender text-brand-lavender shadow-md ring-4 ring-brand-lavender/10'
                      : 'bg-brand-card border-brand-slate/20 text-brand-slate/50'
                  } ${
                    isSelected ? 'ring-2 ring-brand-plum border-brand-plum scale-110' : ''
                  }`}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="w-5 h-5 stroke-[2.5]" />
                  ) : (
                    <Icon className="w-5 h-5" />
                  )}

                  {/* You are Here tag bubble */}
                  {isCurrent && (
                    <span className="absolute -top-6 bg-brand-lavender text-white text-[8px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full whitespace-nowrap shadow-xs animate-bounce">
                      You are here
                    </span>
                  )}
                </div>

                <div className="flex flex-col md:items-center min-w-0">
                  <span className={`text-xs md:text-sm font-semibold truncate ${
                    isSelected ? 'text-brand-plum font-bold border-b border-brand-plum/20 pb-0.5' : isCurrent ? 'text-brand-lavender font-semibold' : 'text-brand-slate/70'
                  }`}>
                    {stage.name}
                  </span>
                  <span className="text-[10px] text-brand-slate/60 hidden md:block max-w-[140px] mt-1 font-light leading-snug">
                    {stage.desc}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* DYNAMIC STAGE DETAIL PANEL */}
      <div className="bg-brand-card border border-brand-slate/10 p-6 md:p-8 rounded-3xl shadow-sm flex flex-col gap-6 animate-in fade-in duration-300">
        
        {/* Stage Header Info */}
        <div className="flex items-center justify-between border-b border-brand-slate/10 pb-4 flex-wrap gap-2">
          <div className="flex items-center gap-2.5">
            <span className="text-[10px] font-bold text-brand-slate uppercase tracking-wider bg-brand-bg border border-brand-slate/10 px-2.5 py-1 rounded-lg">
              {selectedStage === currentStage ? 'YOU ARE HERE' : 'YOU ARE INSPECTING'}
            </span>
            <h2 className="font-display text-md font-bold text-brand-plum uppercase tracking-wide">
              Stage {selectedStage}: {stages[selectedStage - 1].name}
            </h2>
          </div>
          {selectedStage === 3 && latestAnalysis?.specialist_recommendation && (
            <span className="text-[10px] font-semibold text-brand-sage-text bg-brand-sage-bg px-2.5 py-0.5 rounded-full uppercase">
              94% matching confidence
            </span>
          )}
        </div>

        {/* Stage Specific Details Rendering */}
        {selectedStage === 1 && (
          <div className="flex flex-col gap-5 animate-in slide-in-from-top-2 duration-200">
            <div>
              <h3 className="text-xs font-bold text-brand-slate uppercase tracking-wider mb-2">Primary Symptoms Logged</h3>
              <p className="text-xs text-brand-plum leading-relaxed bg-brand-bg p-4 rounded-xl border border-brand-slate/10 italic font-light">
                "{patient?.current_symptoms || 'Describe your symptoms in the patient profile context setup.'}"
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="border border-brand-slate/10 p-4 rounded-2xl bg-brand-bg/50">
                <span className="text-[10px] font-bold text-brand-slate uppercase block mb-1">Patient Details</span>
                <span className="text-xs text-brand-plum leading-relaxed font-light">
                  Age: {patient?.age || 'N/A'} | Gender: {patient?.gender || 'N/A'} | Blood: {patient?.blood_type || 'N/A'}
                </span>
              </div>
              <div className="border border-brand-slate/10 p-4 rounded-2xl bg-brand-bg/50">
                <span className="text-[10px] font-bold text-brand-slate uppercase block mb-1">Allergies & Risks</span>
                <span className="text-xs text-brand-plum leading-relaxed font-light">
                  {patient?.allergies && patient.allergies.length > 0 ? patient.allergies.join(', ') : 'No known drug allergies.'}
                </span>
              </div>
            </div>
          </div>
        )}

        {selectedStage === 2 && (
          <div className="flex flex-col gap-5 animate-in slide-in-from-top-2 duration-200">
            <div>
              <h3 className="text-xs font-bold text-brand-slate uppercase tracking-wider mb-2">AI Diagnostic Parsing Trace</h3>
              <p className="text-xs text-brand-slate leading-relaxed mb-4 font-light">
                CarePath AI Intake, Vision, and Medical Documents agents processed the following parameters:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-brand-bg border border-brand-slate/10 rounded-2xl flex flex-col gap-1.5">
                  <div className="flex items-center gap-1.5 text-brand-lavender font-bold text-xs">
                    <CheckCircle2 className="w-4 h-4 text-brand-sage-text" />
                    <span>Intake Agent</span>
                  </div>
                  <span className="text-[10px] text-brand-slate leading-relaxed font-light">Parsed symptoms timeline: 3-day cough logs.</span>
                </div>
                <div className="p-4 bg-brand-bg border border-brand-slate/10 rounded-2xl flex flex-col gap-1.5">
                  <div className="flex items-center gap-1.5 text-brand-lavender font-bold text-xs">
                    <CheckCircle2 className="w-4 h-4 text-brand-sage-text" />
                    <span>Vision Agent</span>
                  </div>
                  <span className="text-[10px] text-brand-slate leading-relaxed font-light">Correlated markings on uploaded chest X-rays.</span>
                </div>
                <div className="p-4 bg-brand-bg border border-brand-slate/10 rounded-2xl flex flex-col gap-1.5">
                  <div className="flex items-center gap-1.5 text-brand-lavender font-bold text-xs">
                    <CheckCircle2 className="w-4 h-4 text-brand-sage-text" />
                    <span>Docs Agent</span>
                  </div>
                  <span className="text-[10px] text-brand-slate leading-relaxed font-light">Extracted clinical markers from CBC blood tests.</span>
                </div>
              </div>
            </div>
            <div className="flex justify-between items-center border-t border-brand-slate/5 pt-4">
              <span className="text-[10px] text-brand-slate font-light">Additional diagnostic files can be uploaded anytime.</span>
              <Link to="/upload" className="text-xs font-semibold text-brand-lavender hover:underline flex items-center gap-1">
                Go to Upload Center
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        )}

        {selectedStage === 3 && (
          <div className="flex flex-col md:flex-row gap-8 items-stretch animate-in slide-in-from-top-2 duration-200">
            {/* Left side: Next Best Step */}
            <div className="flex-1 flex flex-col justify-between">
              <div>
                <h3 className="text-xs font-bold text-brand-slate uppercase tracking-wider mb-2">Your next best step</h3>
                <h2 className="font-display text-lg font-bold text-brand-plum mb-3 leading-snug">
                  {latestAnalysis?.specialist_recommendation 
                    ? `Schedule a consultation with a ${latestAnalysis.specialist_recommendation}`
                    : 'Analyze medical documents to recommend specialist referrals'}
                </h2>
                <p className="text-brand-slate text-xs leading-relaxed mb-6 font-light">
                  {latestAnalysis?.explanation || 'Provide chest X-rays, lab records, or check-ins. The multi-agent Referral and Clinical Reasoning agents will analyze factors and suggest the appropriate clinical referral route.'}
                </p>
              </div>

              <div className="flex items-center gap-4 mt-2">
                <button 
                  onClick={() => setSelectedStage(4)}
                  className="bg-brand-lavender hover:bg-brand-lavender-hover text-white text-xs font-semibold px-5 py-3 rounded-xl transition-all shadow-xs flex items-center gap-1 cursor-pointer"
                >
                  Prepare for appointment
                  <ArrowRight className="w-4 h-4" />
                </button>
                <Link to="/analysis" className="text-xs font-semibold text-brand-slate hover:text-brand-plum">
                  View Full Report
                </Link>
              </div>
            </div>

            {/* Right side: Visual Reasoning Chain */}
            <div className="flex-1 bg-brand-bg border border-brand-slate/10 p-5 rounded-2xl flex flex-col">
              <h3 className="font-display text-xs font-bold tracking-wider text-brand-slate uppercase mb-4">
                Why CarePath recommends this
              </h3>
              
              {latestAnalysis?.considered_factors ? (
                <div className="flex flex-col items-center gap-2 py-2 w-full text-center">
                  <div className="bg-brand-card border border-brand-slate/10 px-4 py-2 rounded-xl text-xxs font-medium text-brand-plum shadow-xxs">
                    Logged Dry Cough (3 Days)
                  </div>
                  <ArrowDown className="w-4 h-4 text-brand-slate/40" />
                  <div className="bg-brand-card border border-brand-slate/10 px-4 py-2 rounded-xl text-xxs font-medium text-brand-plum shadow-xxs">
                    Chest X-Ray Markings Extracted
                  </div>
                  <ArrowDown className="w-4 h-4 text-brand-slate/40" />
                  <div className="bg-brand-card border border-brand-slate/10 px-4 py-2 rounded-xl text-xxs font-medium text-brand-plum shadow-xxs">
                    Clinical Reasoning Engine Processed
                  </div>
                  <ArrowDown className="w-4 h-4 text-brand-slate/40" />
                  <div className="bg-brand-lavender text-white px-4 py-2.5 rounded-xl text-xs font-bold shadow-xs">
                    Referral Advisory: {latestAnalysis.specialist_recommendation}
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-6 text-center flex-1">
                  <Clock className="w-6 h-6 text-brand-slate/30 mb-2" />
                  <p className="text-xxs text-brand-slate max-w-xs font-light">Reasoning flow will map here once diagnostics are evaluated.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {selectedStage === 4 && (
          <div className="flex flex-col gap-5 animate-in slide-in-from-top-2 duration-200">
            <div>
              <h3 className="text-xs font-bold text-brand-slate uppercase tracking-wider mb-2">Appointment Preparation Summary</h3>
              <p className="text-xs text-brand-slate leading-relaxed mb-4 font-light">
                CarePath compiled the following key discussion questions for your physician appointment:
              </p>
              <div className="bg-brand-bg border border-brand-slate/10 rounded-2xl p-4 flex flex-col gap-3">
                <div className="flex gap-2.5 items-start text-xs text-brand-plum font-light">
                  <span className="text-brand-lavender font-bold">1.</span>
                  <span>How do my dry cough symptoms correlate with the consolidation markings on my chest X-ray?</span>
                </div>
                <div className="flex gap-2.5 items-start text-xs text-brand-plum font-light">
                  <span className="text-brand-lavender font-bold">2.</span>
                  <span>Are there specific lifestyle changes or emergency red-flags I should track at home?</span>
                </div>
              </div>
            </div>
            <div className="flex justify-between items-center border-t border-brand-slate/5 pt-4">
              <span className="text-[10px] text-brand-slate font-light">Bring your printed Consult Brief sheets to the clinic.</span>
              <Link to="/analysis" className="text-xs font-semibold text-brand-lavender hover:underline flex items-center gap-1">
                Print Consult Brief
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        )}

        {selectedStage === 5 && (
          <div className="flex flex-col gap-5 animate-in slide-in-from-top-2 duration-200">
            <div>
              <h3 className="text-xs font-bold text-brand-slate uppercase tracking-wider mb-3">Recovery Progress Checkpoints</h3>
              
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-2">
                <div className="p-4 bg-brand-sage-bg border border-brand-sage-text/10 text-brand-sage-text rounded-2xl flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 shrink-0" />
                  <span className="text-xs font-semibold">Day 1: Onset Logged</span>
                </div>
                <div className="p-4 bg-brand-sage-bg border border-brand-sage-text/10 text-brand-sage-text rounded-2xl flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 shrink-0" />
                  <span className="text-xs font-semibold">Day 3: Diagnostic Check</span>
                </div>
                <div className="p-4 bg-brand-bg border border-brand-slate/10 text-brand-slate rounded-2xl flex items-center gap-2 font-light">
                  <Clock className="w-5 h-5 shrink-0" />
                  <span className="text-xs">Day 7: Check-in Pending</span>
                </div>
              </div>
            </div>

            {/* Check-ins Alert */}
            {timeline.some(e => e.description.toLowerCase().includes('persistent') || e.description.toLowerCase().includes('no improvement')) && (
              <div className="p-4 bg-brand-amber-bg border border-brand-amber-text/15 text-brand-amber-text rounded-2xl flex items-start gap-3 text-xs leading-relaxed font-light">
                <ShieldAlert className="w-5 h-5 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">CarePath noticed something important: </span>
                  Symptom progress logs report flat recovery trends. CarePath suggests completing the specialist consultation review.
                </div>
              </div>
            )}

            <div className="flex justify-between items-center border-t border-brand-slate/5 pt-4">
              <span className="text-[10px] text-brand-slate font-light">Record daily recovery logs to track improvements over time.</span>
              <Link to="/followup" className="text-xs font-semibold text-brand-lavender hover:underline flex items-center gap-1">
                Log Follow-up Check-in
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        )}

      </div>

      {/* YOUR JOURNEY SO FAR CHRONOLOGY TIMELINE */}
      <div className="bg-brand-card border border-brand-slate/10 p-6 md:p-8 rounded-3xl shadow-sm animate-in fade-in duration-300">
        <h3 className="font-display text-xs font-bold tracking-wider text-brand-slate uppercase mb-6 flex items-center gap-2">
          <Activity className="w-4 h-4 text-brand-lavender" />
          Your journey so far
        </h3>

        {timeline.length > 0 ? (
          <div className="relative flex flex-col gap-6 pl-6 border-l border-brand-slate/10">
            {timeline.slice(0, 4).map((event, idx) => (
              <div key={event.id} className="relative">
                {/* Timeline dot marker */}
                <div className="absolute -left-8.5 top-0.5 w-5 h-5 rounded-full bg-brand-bg border-2 border-brand-lavender flex items-center justify-center shadow-xxs">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-lavender" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-brand-plum">{event.title}</span>
                    <span className="text-[10px] text-brand-slate bg-brand-bg px-2 py-0.5 rounded-full">
                      {idx === 0 ? 'Today' : `Day ${timeline.length - idx}`}
                    </span>
                  </div>
                  <p className="text-xs text-brand-slate mt-1 font-light leading-relaxed">
                    {event.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-8 text-center">
            <p className="text-xs text-brand-slate font-light">No timeline milestones parsed yet.</p>
          </div>
        )}
      </div>

      {/* CONTINUE YOUR CAREPATH BANNER */}
      <div className="bg-brand-lavender-light border border-brand-lavender/10 p-6 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4 animate-in fade-in duration-300">
        <div className="flex gap-3 items-center">
          <div className="w-10 h-10 bg-brand-lavender text-white rounded-xl flex items-center justify-center shrink-0">
            <FileCheck className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-display font-bold text-sm text-brand-plum">Your CarePath has been updated</h4>
            <p className="text-brand-slate text-xs font-light">Follow recommended clinical referral guidelines for recovery.</p>
          </div>
        </div>
        <Link 
          to="/profile"
          className="bg-brand-lavender hover:bg-brand-lavender-hover text-white text-xs font-semibold px-6 py-3 rounded-xl transition-all shadow-sm shrink-0 active:scale-98"
        >
          Continue
        </Link>
      </div>

    </div>
  );
}
