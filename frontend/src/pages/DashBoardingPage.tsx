import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { usePatient } from '../context/PatientContext';
import { useAuth } from '../context/AuthContext';
import { timelineService } from '../services/timelineService';
import { analysisService } from '../services/analysisService';
import { medicationService } from '../services/medicationService';
import { doctorBridgeService } from '../services/doctorBridgeService';
import { 
  Activity, 
  Calendar, 
  Clock, 
  CheckCircle2, 
  CheckSquare,
  ArrowRight,
  Sparkles,
  Pill,
  Stethoscope,
  Compass,
  FileText,
  AlertCircle,
  TrendingUp,
  PlusCircle,
  Smile,
  ShieldCheck,
  ChevronRight,
  TrendingDown,
  Inbox
} from 'lucide-react';
import type { TimelineEvent, AnalysisResult } from '../types';

export default function DashBoardingPage() {
  const { patient, isLoading: isPatientLoading, fetchPatient } = usePatient();
  const { user } = useAuth();
  
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [latestAnalysis, setLatestAnalysis] = useState<AnalysisResult | null>(null);
  const [doctorReview, setDoctorReview] = useState<any>(null);
  const [medications, setMedications] = useState<any[]>([]);
  const [adherencePercentage, setAdherencePercentage] = useState(0);

  const [isLoadingData, setIsLoadingData] = useState(false);
  const [isOffline, setIsOffline] = useState(false);
  
  // Interactive Follow-up State
  const [feelingLogged, setFeelingLogged] = useState<string | null>(null);
  const [symptomTrend, setSymptomTrend] = useState<'Improving' | 'Stable' | 'Declining'>('Stable');
  const [lastCheckIn, setLastCheckIn] = useState<string>('Yesterday, 6:30 PM');

  // Journey stage selection state
  const [selectedStage, setSelectedStage] = useState<number>(3);

  const loadLocalStates = () => {
    setMedications(medicationService.getMedications());
    setAdherencePercentage(medicationService.getAdherenceSummary().percentage);
    setDoctorReview(doctorBridgeService.getReview());

    const savedTrend = localStorage.getItem('carepath_symptom_trend');
    if (savedTrend) {
      setSymptomTrend(savedTrend as any);
    }
    const savedCheckIn = localStorage.getItem('carepath_last_check_in');
    if (savedCheckIn) {
      setLastCheckIn(savedCheckIn);
    }
  };

  const loadDashboardData = async () => {
    if (!patient) return;
    setIsLoadingData(true);
    setIsOffline(false);
    try {
      if (patient.id === 'demo_patient_id') {
        const timelineData = await timelineService.getTimeline('demo_patient_id');
        setTimeline(timelineData.slice(0, 3));

        // Mock Analysis
        setLatestAnalysis({
          id: 'demo_analysis_1',
          patient_id: 'demo_patient_id',
          status: 'completed',
          specialist_recommendation: 'Pulmonologist / Respirologist',
          explanation: 'Exertional shortness of breath with hyperinflation signs indicates assessment for airway hyperreactivity or occupational exposures.',
          considered_factors: [
            'Persistent dry cough (3 days)',
            'Right lower lobe consolidation on scan',
            'Flat recovery trend with Albuterol'
          ],
          created_at: new Date(Date.now() - 86400000).toISOString()
        });
      } else {
        const [timelineData, analysisHistory] = await Promise.all([
          timelineService.getTimeline(patient.id),
          analysisService.getAnalysisHistory(patient.id)
        ]);
        setTimeline(timelineData.slice(0, 4));
        setLatestAnalysis(analysisHistory.length > 0 ? analysisHistory[0] : null);
      }
    } catch (err: any) {
      console.error(err);
      setIsOffline(true);
      
      // Load fallback local demo states in offline mode
      setLatestAnalysis({
        id: 'demo_analysis_offline',
        patient_id: 'demo_patient',
        status: 'completed',
        specialist_recommendation: 'Pulmonologist / Respirologist',
        explanation: 'Exertional shortness of breath with hyperinflation signs indicates assessment for airway hyperreactivity or occupational exposures.',
        considered_factors: [
          'Persistent dry cough (3 days)',
          'Right lower lobe consolidation on scan',
          'Flat recovery trend with Albuterol'
        ],
        created_at: new Date().toISOString()
      });
    } finally {
      setIsLoadingData(false);
    }
  };

  useEffect(() => {
    loadLocalStates();
    loadDashboardData();

    // Listen to updates from other pages
    window.addEventListener('medication_updated', loadLocalStates);
    window.addEventListener('timeline_updated', loadDashboardData);
    window.addEventListener('doctor_review_updated', () => {
      loadLocalStates();
      // Auto advance to stage 5 (Doctor Approved) when review exists
      setSelectedStage(5);
    });
    return () => {
      window.removeEventListener('medication_updated', loadLocalStates);
      window.removeEventListener('timeline_updated', loadDashboardData);
      window.removeEventListener('doctor_review_updated', loadLocalStates);
    };
  }, [patient]);

  const handleMedicationCheckOff = (medId: string) => {
    medicationService.markAsTaken(medId);
    loadLocalStates();
  };

  const handleSymptomCheckIn = (status: 'Worse' | 'Same' | 'Better') => {
    let trend: 'Improving' | 'Stable' | 'Declining' = 'Stable';
    if (status === 'Better') trend = 'Improving';
    if (status === 'Worse') trend = 'Declining';

    const checkInTime = new Date().toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
    const checkInDateString = `Today, ${checkInTime}`;

    setSymptomTrend(trend);
    setLastCheckIn(checkInDateString);
    setFeelingLogged(status);

    localStorage.setItem('carepath_symptom_trend', trend);
    localStorage.setItem('carepath_last_check_in', checkInDateString);

    // Push log to timeline
    const checkInLog = {
      patient_id: patient?.id || 'demo_patient_id',
      type: 'symptom' as const,
      title: `Daily Check-in: Feeling ${status}`,
      description: `Logged symptom trend is ${trend}.`,
      timestamp: new Date().toISOString()
    };
    
    if (patient?.id === 'demo_patient_id') {
      setTimeline(prev => [checkInLog as any, ...prev]);
    } else {
      timelineService.addTimelineEvent(checkInLog).then(loadDashboardData);
    }
  };

  const patientName = patient?.name || user?.name || 'Jane Doe';
  const careJourneyDay = patient?.id === 'demo_patient_id' ? '4' : '1';

  // Stepper Stages list
  const stages = [
    { num: 1, label: 'Symptoms Logged', desc: 'Initial symptoms recorded' },
    { num: 2, label: 'Documents Uploaded', desc: 'Medical records uploaded' },
    { num: 3, label: 'AI Analyzed', desc: 'Machine learning advisory generated' },
    { num: 4, label: 'Doctor Brief Prepared', desc: 'Sync questions finalized' },
    { num: 5, label: 'Physician Endorsed', desc: 'Doctor reviewed and signed off' },
    { num: 6, label: 'Follow-up Due', desc: 'Verify health parameters' }
  ];

  // Dynamically determine current active stage in the Health Journey
  const currentActiveStage = doctorReview ? 5 : (latestAnalysis ? 3 : 2);

  // Care Plan Tasks Lists
  const carePlanTasks = [
    { id: 't1', text: 'Upload chest X-ray scans', done: true },
    { id: 't2', text: 'Prepare Doctor Brief details', done: true },
    { id: 't3', text: 'Attend Pulmonologist consultation', done: !!doctorReview },
    { id: 't4', text: 'Complete pulmonary spirometry scan', done: false },
    { id: 't5', text: 'Log day-7 recovery check-in', done: false }
  ];

  const completedTasksCount = carePlanTasks.filter(t => t.done).length;
  const carePlanPercentage = Math.round((completedTasksCount / carePlanTasks.length) * 100);

  return (
    <div className="animate-in fade-in duration-300">
      
      {/* Dashboard Hero */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-brand-slate/10 pb-6 mt-2">
        <div>
          <h1 className="font-display text-2xl md:text-3xl font-extrabold tracking-tight text-brand-plum">
            CAREPATH AI
          </h1>
          <p className="text-brand-slate text-sm font-light mt-1">
            Your Healthcare Navigation Journey
          </p>
          <div className="flex items-center gap-2 mt-3">
            <Clock className="w-4 h-4 text-brand-slate" />
            <span className="text-xs text-brand-slate">Your CarePath was updated {patient?.id === 'demo_patient_id' ? '2 minutes ago' : 'recently'}.</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3 w-full md:w-auto">
          <Link
            to="/upload"
            className="flex-1 md:flex-none flex justify-center items-center gap-2 bg-white border border-brand-slate/20 hover:border-brand-lavender/50 text-brand-slate hover:text-brand-plum text-xs font-semibold px-4 py-3 rounded-xl transition-all shadow-sm"
          >
            <FileText className="w-4 h-4" />
            Upload Document
          </Link>
          <Link
            to="/journey"
            className="flex-1 md:flex-none flex justify-center items-center gap-2 bg-brand-plum hover:bg-brand-lavender text-white text-xs font-semibold px-4 py-3 rounded-xl transition-all shadow-md hover:shadow-lg"
          >
            <PlusCircle className="w-4 h-4" />
            Update My Condition
          </Link>
        </div>
      </div>

      {/* Patient Status Card */}
      <div className="bg-brand-card border border-brand-slate/10 p-6 rounded-2xl shadow-sm relative overflow-hidden mt-2">
        <div className="absolute top-0 left-0 w-1 h-full bg-brand-lavender" />
        <h2 className="font-display text-xs font-bold tracking-wider text-brand-slate uppercase mb-5 flex items-center gap-2">
          <Activity className="w-4 h-4 text-brand-lavender" />
          YOUR CAREPATH
        </h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="flex flex-col gap-1">
            <span className="text-[10px] uppercase font-bold text-brand-slate tracking-wider">Current Pathway</span>
            <span className="text-sm font-bold text-brand-plum flex items-center gap-2">
              <Stethoscope className="w-4 h-4 text-brand-lavender" />
              {latestAnalysis?.specialist_recommendation || 'General Physician'}
            </span>
          </div>
          
          <div className="flex flex-col gap-1">
            <span className="text-[10px] uppercase font-bold text-brand-slate tracking-wider">Recommended</span>
            <span className="text-sm font-bold text-brand-sage-text flex items-center gap-1.5">
              <Clock className="w-4 h-4" />
              Soon
            </span>
          </div>

          <div className="flex flex-col gap-1">
            <span className="text-[10px] uppercase font-bold text-brand-slate tracking-wider">Last Updated</span>
            <span className="text-sm font-semibold text-brand-plum">
              {lastCheckIn}
            </span>
          </div>

          <div className="flex flex-col gap-1">
            <span className="text-[10px] uppercase font-bold text-brand-slate tracking-wider">Journey</span>
            <span className="text-sm font-semibold text-brand-plum">
              {timeline.length + 1} updates · {latestAnalysis ? '3 analyses' : '1 analysis'}
            </span>
          </div>
        </div>
        
        <div className="mt-6 flex justify-end">
          <Link
            to="/journey"
            className="text-xs font-semibold text-brand-lavender flex items-center gap-1.5 hover:underline"
          >
            View Full Journey
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* ROW 1: CARE PLAN GOALS & MEDICATION REMINDERS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
        
        {/* Left: Continuous Care Plan Goals (spans 2 columns) */}
        <div className="lg:col-span-2 bg-brand-card border border-brand-slate/10 p-6 md:p-8 rounded-3xl shadow-sm flex flex-col justify-between gap-5">
          <div className="flex justify-between items-center border-b border-brand-slate/5 pb-3.5 flex-wrap gap-2">
            <h3 className="font-display text-xs font-bold tracking-wider text-brand-slate uppercase flex items-center gap-2">
              <CheckSquare className="w-4.5 h-4.5 text-brand-lavender" />
              Continuous Care Plan Goals
            </h3>
            <span className="text-[10px] font-bold text-brand-sage-text bg-brand-sage-bg px-2.5 py-0.5 rounded-full uppercase">
              {carePlanPercentage}% Complete
            </span>
          </div>

          {/* Percentage Bar */}
          <div className="w-full bg-brand-bg rounded-full h-2 overflow-hidden border border-brand-slate/5">
            <div 
              className="bg-brand-sage-text h-full rounded-full transition-all duration-500" 
              style={{ width: `${carePlanPercentage}%` }}
            />
          </div>

          {/* Checklists */}
          <div className="flex flex-col gap-3 mt-1.5 flex-1 justify-center">
            {carePlanTasks.map((task) => (
              <div 
                key={task.id} 
                className={`flex items-center justify-between gap-3 text-xxs p-2.5 rounded-xl border transition-all ${
                  task.done 
                    ? 'bg-brand-sage-bg/5 border-brand-sage-text/15 text-brand-sage-text' 
                    : 'bg-brand-bg/50 border-brand-slate/5 text-brand-slate'
                }`}
              >
                <div className="flex items-center gap-2">
                  <CheckCircle2 className={`w-4 h-4 shrink-0 ${task.done ? 'text-brand-sage-text' : 'text-brand-slate/20'}`} />
                  <span className={task.done ? 'line-through font-light' : 'font-semibold text-brand-plum'}>{task.text}</span>
                </div>
                {task.done ? (
                  <span className="text-[8px] font-bold uppercase tracking-wider text-brand-sage-text/80">Done</span>
                ) : (
                  <span className="text-[8px] font-bold uppercase tracking-wider text-brand-slate/60">Pending</span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Right: Medication Reminders (spans 1 column, h-full/flex-1 to align bottom edge) */}
        <div className="bg-brand-card border border-brand-slate/10 p-6 rounded-3xl shadow-sm flex flex-col justify-between gap-4 h-full">
          <div className="flex justify-between items-center border-b border-brand-slate/5 pb-3">
            <h3 className="font-display text-xs font-bold tracking-wider text-brand-slate uppercase flex items-center gap-2">
              <Pill className="w-4 h-4 text-brand-lavender" />
              Medication Reminders
            </h3>
            <Link 
              to="/medications"
              className="text-xxs font-bold text-brand-lavender hover:underline flex items-center gap-0.5"
            >
              Go to Companion
              <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* Empty States check */}
          {medications.length === 0 ? (
            <div className="py-8 text-center flex flex-col items-center justify-center gap-3 flex-1">
              <Inbox className="w-8 h-8 text-brand-slate/20" />
              <p className="text-xxs text-brand-slate font-light leading-relaxed max-w-xs">
                No active medication logged in system. Register a course in Medications Companion.
              </p>
              <Link
                to="/medications"
                className="text-xxs font-semibold bg-brand-lavender text-white px-3 py-1.5 rounded-lg shadow-xxs"
              >
                Configure Medications
              </Link>
            </div>
          ) : (
            <div className="flex flex-col gap-3 mt-1 flex-1 justify-center">
              {medications.slice(0, 3).map((med) => {
                return (
                  <div key={med.id} className="border border-brand-slate/10 rounded-2xl p-4 flex flex-col justify-between gap-2.5 bg-brand-bg/25">
                    <div className="flex justify-between items-start gap-2">
                      <div>
                        <span className="text-[10px] font-bold text-brand-plum block leading-tight">{med.name}</span>
                        <span className="text-[9px] text-brand-slate font-light">{med.dosage} &bull; {med.frequency}</span>
                      </div>
                      <span className="text-[8px] font-extrabold uppercase tracking-wider bg-brand-lavender-light text-brand-lavender border border-brand-lavender/10 px-1.5 py-0.5 rounded">
                        {med.timing}
                      </span>
                    </div>

                    {/* Log take check-off buttons */}
                    <div className="flex items-center justify-between gap-3 mt-1.5 border-t border-brand-slate/5 pt-2.5">
                      <span className="text-[9px] text-brand-slate/75 font-light">Next Dose: {med.nextDose}</span>
                      {med.status === 'taken' ? (
                        <span className="text-[9px] font-bold text-brand-sage-text bg-brand-sage-bg border border-brand-sage-text/10 px-2.5 py-1 rounded-lg flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Taken
                        </span>
                      ) : med.status === 'missed' ? (
                        <button
                          onClick={() => handleMedicationCheckOff(med.id)}
                          className="text-[9px] font-bold text-brand-rose-text bg-brand-rose-bg border border-brand-rose-text/10 px-2.5 py-1 rounded-lg hover:border-brand-lavender hover:bg-brand-lavender-light/10 transition-all cursor-pointer"
                        >
                          Missed (Log taken)
                        </button>
                      ) : (
                        <button
                          onClick={() => handleMedicationCheckOff(med.id)}
                          className="text-[9px] font-bold text-brand-plum bg-brand-card border border-brand-slate/15 px-2.5 py-1 rounded-lg hover:border-brand-lavender hover:bg-brand-lavender-light/10 transition-all cursor-pointer"
                        >
                          Log Taken
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* ROW 2: SYMPTOM CHECK-IN, LATEST MILESTONE, RECENT ACTIONS LOG */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch">
        
        {/* Box 1: Symptom Follow-up Check-in */}
        <div className="bg-brand-card border border-brand-slate/10 p-6 rounded-3xl shadow-sm flex flex-col justify-between gap-4 h-full">
          <div className="flex flex-col gap-4">
            <h3 className="font-display text-xs font-bold tracking-wider text-brand-slate uppercase border-b border-brand-slate/5 pb-3 flex items-center gap-2">
              <Activity className="w-4 h-4 text-brand-lavender" />
              Symptom Follow-up Check-in
            </h3>

            {/* Follow-up indicators */}
            <div className="grid grid-cols-2 gap-3 mb-2 text-xxs leading-relaxed font-light">
              <div className="bg-brand-bg/50 border border-brand-slate/5 p-3 rounded-2xl">
                <span className="text-[9px] font-bold text-brand-slate uppercase tracking-wider block">Symptom Trend</span>
                <span className="flex items-center gap-1 mt-1 text-brand-plum font-semibold">
                  {symptomTrend === 'Improving' && <Smile className="w-3.5 h-3.5 text-brand-sage-text shrink-0" />}
                  {symptomTrend === 'Stable' && <Smile className="w-3.5 h-3.5 text-brand-slate/40 shrink-0" />}
                  {symptomTrend === 'Declining' && <Smile className="w-3.5 h-3.5 text-brand-rose-text shrink-0" />}
                  {symptomTrend}
                </span>
              </div>
              <div className="bg-brand-bg/50 border border-brand-slate/5 p-3 rounded-2xl">
                <span className="text-[9px] font-bold text-brand-slate uppercase tracking-wider block">Last Check-in</span>
                <span className="block mt-1 font-semibold text-brand-plum truncate">{lastCheckIn}</span>
              </div>
            </div>

            {/* Daily feeling question */}
            <div className="border border-brand-slate/10 rounded-2xl p-4 bg-brand-bg/30 text-center flex flex-col gap-3">
              <span className="text-xxs font-bold text-brand-plum leading-snug block">How are you feeling today?</span>
              
              <div className="flex gap-2">
                {[
                  { state: 'Worse', color: 'bg-brand-rose-bg hover:bg-brand-rose-bg/85 border-brand-rose-text/10 text-brand-rose-text' },
                  { state: 'Same', color: 'bg-brand-bg hover:bg-brand-bg/80 border-brand-slate/15 text-brand-plum' },
                  { state: 'Better', color: 'bg-brand-sage-bg hover:bg-brand-sage-bg/85 border-brand-sage-text/10 text-brand-sage-text' }
                ].map(item => (
                  <button
                    key={item.state}
                    onClick={() => handleSymptomCheckIn(item.state as any)}
                    className={`flex-1 text-[10px] font-bold py-2 rounded-xl border transition-all cursor-pointer ${item.color} ${
                      feelingLogged === item.state ? 'ring-2 ring-brand-plum shadow-xxs scale-95' : ''
                    }`}
                  >
                    {item.state}
                  </button>
                ))}
              </div>
              {feelingLogged && (
                <span className="text-[9px] text-brand-sage-text font-bold uppercase animate-pulse mt-0.5">
                  Check-in Logged!
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Box 2: Latest Milestone */}
        <div className="bg-brand-card border border-brand-slate/10 p-6 rounded-3xl shadow-sm flex flex-col justify-between gap-4 h-full">
          <div className="flex flex-col gap-4">
            <div className="flex justify-between items-center border-b border-brand-slate/5 pb-3">
              <h3 className="font-display text-xs font-bold tracking-wider text-brand-slate uppercase flex items-center gap-2">
                <Clock className="w-4 h-4 text-brand-lavender" />
                Latest Milestones
              </h3>
              <Link 
                to="/journey"
                className="text-xxs font-bold text-brand-lavender hover:underline flex items-center gap-0.5"
              >
                View Full Journey
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {/* Empty check */}
            {timeline.length === 0 ? (
              <div className="py-8 text-center flex flex-col items-center justify-center gap-3">
                <Inbox className="w-8 h-8 text-brand-slate/20" />
                <p className="text-xxs text-brand-slate font-light">No logged milestones found on timeline.</p>
              </div>
            ) : (
              <div className="flex flex-col gap-3 mt-1">
                {timeline.slice(0, 3).map((event) => (
                  <div key={event.id} className="border-l-2 border-brand-slate/15 pl-3.5 py-1.5 flex flex-col gap-0.5">
                    <span className="text-[8px] font-bold text-brand-slate/50">
                      {new Date(event.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                    </span>
                    <span className="text-xxs font-semibold text-brand-plum leading-tight">{event.title}</span>
                    <p className="text-[10px] text-brand-slate leading-relaxed font-light line-clamp-1">{event.description}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Box 3: Recent Actions Log */}
        <div className="bg-brand-card border border-brand-slate/10 p-6 rounded-3xl shadow-sm flex flex-col justify-between gap-4 h-full">
          <div className="flex flex-col gap-4">
            <h3 className="font-display text-xs font-bold tracking-wider text-brand-slate uppercase border-b border-brand-slate/5 pb-3 flex items-center gap-2">
              <Sparkles className="w-4.5 h-4.5 text-brand-lavender" />
              Recent Actions Log
            </h3>

            <div className="flex flex-col gap-3 mt-1.5 text-xxs font-light leading-snug">
              {/* Document upload status */}
              <div className="flex items-start gap-2.5">
                <FileText className="w-4 h-4 text-brand-slate/55 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-brand-plum block">Prescription Uploaded</span>
                  <span className="text-brand-slate">cbc_blood_report.pdf parsed successfully.</span>
                </div>
              </div>

              {/* AI analysis */}
              <div className="flex items-start gap-2.5">
                <Sparkles className="w-4 h-4 text-brand-lavender shrink-0 mt-0.5 animate-pulse" />
                <div>
                  <span className="font-bold text-brand-plum block">AI Analysis Updated</span>
                  <span className="text-brand-slate">Pulmonology consult advisory generated.</span>
                </div>
              </div>

              {/* Doctor feedback review */}
              {doctorReview && (
                <div className="flex items-start gap-2.5 animate-in slide-in-from-top-1 duration-200">
                  <ShieldCheck className="w-4 h-4 text-brand-sage-text shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-brand-plum block">Doctor Feedback Endorsed</span>
                    <span className="text-brand-slate">Signed off by {doctorReview.reviewedBy}.</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
